from datetime import datetime, timezone

from src.auth import AuthService, AuthUnavailable, InvalidCredentials
from src.prazo import calcular_vencimento, esta_atrasado


class EmprestimoUnavailable(Exception):
    pass


class EmprestimoRecusado(Exception):
    def __init__(self, reason, detail, status_code=409):
        self.reason = reason
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


def validar_solicitacao(status, ocupado, vencimentos, referencia):
    if status != 'DISPONIVEL' or ocupado:
        raise EmprestimoRecusado('equipamento_indisponivel', 'Equipamento indisponível para empréstimo.')
    if len(vencimentos) >= 3:
        raise EmprestimoRecusado('limite_emprestimos', 'Limite de 3 empréstimos em aberto atingido.')
    if any(esta_atrasado(vencimento, referencia) for vencimento in vencimentos):
        raise EmprestimoRecusado('emprestimo_atrasado', 'Existe empréstimo em atraso.', 403)


class PostgresEmprestimoRepository:
    def __init__(self, connection, clock=None):
        self.connection = connection
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def solicitar(self, token, equipamento_id):
        try:
            import psycopg
        except ImportError:
            raise EmprestimoUnavailable() from None
        try:
            with self.connection() as conn:
                try:
                    return self._solicitar(conn, AuthService.digest(token), equipamento_id)
                except psycopg.errors.UniqueViolation as exc:
                    if exc.diag.constraint_name == 'ux_emprestimos_equipamento_ativo':
                        raise EmprestimoRecusado(
                            'equipamento_indisponivel', 'Equipamento indisponível para empréstimo.') from None
                    raise
        except AuthUnavailable:
            raise EmprestimoUnavailable() from None
        except psycopg.Error:
            raise EmprestimoUnavailable() from None

    def _solicitar(self, conn, token_hash, equipamento_id):
        conn.execute('SET TRANSACTION ISOLATION LEVEL READ COMMITTED', ())
        session = conn.execute(
            'SELECT usuario_id FROM public.sessoes_login WHERE token_hash = %s',
            (token_hash,),
        ).fetchone()
        if not session:
            raise InvalidCredentials()
        usuario_id = session['usuario_id']
        # Mesma ordem e namespace do trigger da migration 001, antes dos SELECTs de validação.
        for identifier in (equipamento_id, usuario_id):
            conn.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))', (str(identifier),))
        equipamento = conn.execute(
            'SELECT * FROM app_private.lock_equipment_for_loan(%s)',
            (equipamento_id,),
        ).fetchone()
        usuario = conn.execute(
            'SELECT * FROM app_private.lock_user_for_loan(%s)',
            (usuario_id,),
        ).fetchone()
        session = conn.execute(
            'SELECT * FROM app_private.lock_session_for_loan(%s)',
            (token_hash,),
        ).fetchone()
        now = self.clock()
        if (not usuario or not usuario['ativo'] or not session
                or session['usuario_id'] != usuario_id or session['expira_em'] <= now):
            raise InvalidCredentials()
        ocupado = conn.execute(
            'SELECT id FROM public.emprestimos WHERE equipamento_id = %s AND devolvido_em IS NULL',
            (equipamento_id,),
        ).fetchone()
        abertos = conn.execute(
            'SELECT previsto_para FROM public.emprestimos WHERE usuario_id = %s AND devolvido_em IS NULL',
            (usuario_id,),
        ).fetchall()
        validar_solicitacao(equipamento['status_operacional'] if equipamento else None,
                           ocupado is not None, [row['previsto_para'] for row in abertos], now)
        previsto_para = calcular_vencimento(now)
        row = conn.execute(
            'INSERT INTO public.emprestimos (equipamento_id, usuario_id, retirado_em, previsto_para) '
            'VALUES (%s, %s, %s, %s) RETURNING id, retirado_em, previsto_para',
            (equipamento_id, usuario_id, now, previsto_para),
        ).fetchone()
        return {'id': str(row['id']), 'retirado_em': row['retirado_em'].isoformat(),
                'previsto_para': row['previsto_para'].isoformat(),
                'equipamento': {'id': str(equipamento['id']), 'nome': equipamento['nome'],
                                'patrimonio': equipamento['patrimonio'], 'categoria': equipamento['categoria']}}
