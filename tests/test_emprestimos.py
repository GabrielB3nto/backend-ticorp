from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

import psycopg
import pytest
from fastapi.testclient import TestClient

from main import app, get_auth_service, get_consulta_repository, get_emprestimo_repository
from src.auth import AuthService, AuthUnavailable, InvalidCredentials
from src.consultas import PostgresConsultaRepository
from src.emprestimos import EmprestimoRecusado, EmprestimoUnavailable, PostgresEmprestimoRepository, validar_solicitacao

NOW = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
USER = UUID(int=1)
ITEM = UUID(int=10)
LOAN = UUID(int=20)
TOKEN = 'a' * 43
HEADERS = {'Authorization': f'Bearer {TOKEN}'}


class FakeConnection:
    def __init__(self):
        self.calls = []
        self.session = {'usuario_id': USER, 'expira_em': NOW + timedelta(hours=1)}
        self.user = {'id': USER, 'ativo': True}
        self.item = {'id': ITEM, 'nome': 'Sintético', 'patrimonio': None,
                     'categoria': 'Notebook', 'status_operacional': 'DISPONIVEL'}
        self.open_dates = []
        self.occupied = False
        self.created = None
        self.pending = None
        self.committed = False
        self.rolled_back = False
        self.failure = None
        self.commit_failure = False
        self.after_lock = None

    def execute(self, sql, params):
        self.calls.append((sql, params))
        if 'INSERT' in sql:
            if self.failure:
                raise self.failure
            self.pending = {'id': LOAN, 'retirado_em': params[2], 'previsto_para': params[3]}
        if 'lock_session_for_loan' in sql and self.after_lock:
            self.after_lock()
        return self

    def fetchone(self):
        sql, _ = self.calls[-1]
        if 'lock_session_for_loan' in sql or 'public.sessoes_login' in sql:
            return self.session
        if 'lock_user_for_loan' in sql:
            return self.user
        if 'lock_equipment_for_loan' in sql:
            return self.item
        if 'INSERT' in sql:
            return self.pending
        if 'SELECT id FROM public.emprestimos' in sql:
            return {'id': UUID(int=21)} if self.occupied else None
        raise AssertionError(sql)

    def fetchall(self):
        sql, params = self.calls[-1]
        if 'CASE WHEN' in sql:
            return [{**self.item, 'status': 'EMPRESTADO' if self.created else 'DISPONIVEL'}]
        if 'SELECT previsto_para' in sql:
            return [{'previsto_para': value} for value in self.open_dates]
        assert 'WHERE l.usuario_id = %s AND l.devolvido_em IS NULL' in sql
        if self.created and params == (str(USER),):
            return [{**self.created, 'equipamento_id': ITEM, **{key: self.item[key] for key in ('nome', 'patrimonio', 'categoria')}}]
        return []

    @contextmanager
    def connection(self):
        try:
            yield self
            if self.commit_failure:
                raise AuthUnavailable('synthetic commit secret')
            self.created = self.pending
            self.committed = True
        except Exception:
            self.pending = None
            self.rolled_back = True
            raise


@pytest.fixture
def loan_client():
    conn = FakeConnection()
    time = [NOW]
    repo = PostgresEmprestimoRepository(conn.connection, clock=lambda: time[0])
    class ReadAuth:
        def me(self, token):
            return {'user': {'id': str(USER)}}
    app.dependency_overrides[get_emprestimo_repository] = lambda: repo
    app.dependency_overrides[get_consulta_repository] = lambda: PostgresConsultaRepository(conn.connection)
    app.dependency_overrides[get_auth_service] = lambda: ReadAuth()
    try:
        with TestClient(app) as client:
            yield client, conn, time
    finally:
        app.dependency_overrides.clear()


def request(client, **body):
    return client.post('/api/emprestimos', json={'equipamento_id': str(ITEM), **body}, headers=HEADERS)


@pytest.mark.parametrize('count', [0, 2])
def test_dominio_permite_ate_dois_abertos(count):
    assert validar_solicitacao('DISPONIVEL', False, [date(2026, 11, 9)] * count, NOW) is None


@pytest.mark.parametrize('status', [None, 'MANUTENCAO', 'INATIVO'])
def test_dominio_recusa_equipamento_indisponivel(status):
    with pytest.raises(EmprestimoRecusado, match='Equipamento indisponível'):
        validar_solicitacao(status, False, [], NOW)


def test_dominio_recusa_equipamento_ocupado():
    with pytest.raises(EmprestimoRecusado, match='Equipamento indisponível'):
        validar_solicitacao('DISPONIVEL', True, [], NOW)


def test_dominio_recusa_tres_abertos():
    with pytest.raises(EmprestimoRecusado, match='Limite de 3'):
        validar_solicitacao('DISPONIVEL', False, [date(2026, 11, 27)] * 3, NOW)


def test_dominio_recusa_atraso():
    with pytest.raises(EmprestimoRecusado, match='Existe empréstimo em atraso'):
        validar_solicitacao('DISPONIVEL', False, [date(2026, 11, 8)], NOW)


def test_post_retorna_contrato_201_apos_commit(loan_client):
    client, conn, _ = loan_client
    response = request(client)
    assert (response.status_code, response.json(), response.headers['cache-control'], conn.committed) == (
        201, {'emprestimo': {'id': str(LOAN), 'retirado_em': NOW.isoformat(), 'previsto_para': '2026-11-27',
                            'equipamento': {'id': str(ITEM), 'nome': 'Sintético', 'patrimonio': None, 'categoria': 'Notebook'}}},
        'no-store', True)


def test_post_sucesso_aparece_na_leitura_propria(loan_client):
    client, _, _ = loan_client
    created = request(client).json()['emprestimo']
    assert client.get('/api/emprestimos/meus', headers=HEADERS).json() == {'emprestimos': [created]}


def test_post_sucesso_indisponibiliza_catalogo_sem_update(loan_client):
    client, conn, _ = loan_client
    request(client)
    assert client.get('/api/equipamentos', headers=HEADERS).json()['equipamentos'][0]['status'] == 'EMPRESTADO'
    assert not any('UPDATE public.' in sql for sql, _ in conn.calls)


@pytest.mark.parametrize('extra', ['usuario_id', 'retirado_em', 'previsto_para', 'id'])
def test_post_proibe_titular_e_campos_extras(loan_client, extra):
    client, conn, _ = loan_client
    response = request(client, **{extra: str(USER)})
    assert (response.status_code, response.json(), response.headers['cache-control'], conn.calls) == (
        422, {'detail': 'Dados inválidos.'}, 'no-store', [])


@pytest.mark.parametrize('body', [{}, {'equipamento_id': None}, {'equipamento_id': 'x'}, {'equipamento_id': 123}, []])
def test_post_valida_uuid_sem_eco(loan_client, body):
    client, conn, _ = loan_client
    response = client.post('/api/emprestimos', json=body, headers=HEADERS)
    assert (response.status_code, response.json(), conn.calls) == (422, {'detail': 'Dados inválidos.'}, [])


@pytest.mark.parametrize('header', [None, 'Basic abc', 'Bearer xyz'])
def test_post_rejeita_token_sem_consultar_banco(loan_client, header):
    client, conn, _ = loan_client
    response = client.post('/api/emprestimos', json={'equipamento_id': str(ITEM)},
                           headers={'Authorization': header} if header else {})
    assert (response.status_code, response.json(), response.headers['cache-control'], conn.calls) == (
        401, {'detail': 'Credenciais inválidas.'}, 'no-store', [])


@pytest.mark.parametrize('state', ['absent', 'expired', 'inactive', 'revoked_after_lock', 'changed_after_lock'])
def test_post_revalida_sessao_e_usuario_sem_insert(loan_client, state):
    client, conn, _ = loan_client
    if state == 'absent':
        conn.session = None
    elif state == 'expired':
        conn.session['expira_em'] = NOW
    elif state == 'inactive':
        conn.user['ativo'] = False
    elif state == 'revoked_after_lock':
        conn.after_lock = lambda: setattr(conn, 'session', None)
    else:
        conn.after_lock = lambda: setattr(conn, 'session', {**conn.session, 'usuario_id': UUID(int=2)})
    response = request(client)
    assert (response.status_code, response.json(), conn.rolled_back) == (401, {'detail': 'Credenciais inválidas.'}, True)
    assert not any('INSERT' in sql for sql, _ in conn.calls)


@pytest.mark.parametrize('state,status,reason', [
    ('missing', 409, 'equipamento_indisponivel'), ('maintenance', 409, 'equipamento_indisponivel'),
    ('inactive', 409, 'equipamento_indisponivel'), ('occupied', 409, 'equipamento_indisponivel'),
    ('limit', 409, 'limite_emprestimos'), ('overdue', 403, 'emprestimo_atrasado')])
def test_post_recusa_sem_insert(loan_client, state, status, reason):
    client, conn, _ = loan_client
    if state == 'missing':
        conn.item = None
    elif state in ('maintenance', 'inactive'):
        conn.item['status_operacional'] = 'MANUTENCAO' if state == 'maintenance' else 'INATIVO'
    elif state == 'occupied':
        conn.occupied = True
    else:
        conn.open_dates = [date(2026, 11, 27)] * 3 if state == 'limit' else [date(2026, 11, 8)]
    response = request(client)
    assert (response.status_code, response.json()['reason'], response.headers['cache-control'], conn.rolled_back) == (
        status, reason, 'no-store', True)
    assert not any('INSERT' in sql for sql, _ in conn.calls)


def test_post_vencendo_hoje_permitido(loan_client):
    client, conn, _ = loan_client
    conn.open_dates = [date(2026, 11, 9)]
    assert request(client).status_code == 201


def test_repositorio_ordem_locks_e_selects_apos_espera(loan_client):
    client, conn, _ = loan_client
    request(client)
    sqls = [sql for sql, _ in conn.calls]
    assert sqls[0] == 'SET TRANSACTION ISOLATION LEVEL READ COMMITTED'
    assert conn.calls[1][1] == (AuthService.digest(TOKEN),)
    assert conn.calls[2:4] == [
        ('SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))', (str(ITEM),)),
        ('SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))', (str(USER),))]
    assert sqls[4] == 'SELECT * FROM app_private.lock_equipment_for_loan(%s)'
    assert sqls[5] == 'SELECT * FROM app_private.lock_user_for_loan(%s)'
    assert sqls[6] == 'SELECT * FROM app_private.lock_session_for_loan(%s)'
    assert 'equipamento_id = %s AND devolvido_em IS NULL' in sqls[7]
    assert 'usuario_id = %s AND devolvido_em IS NULL' in sqls[8]
    assert conn.calls[9][1] == (ITEM, USER, NOW, date(2026, 11, 27))


@pytest.mark.parametrize('change,reason', [('occupied', 'equipamento_indisponivel'), ('limit', 'limite_emprestimos')])
def test_post_rele_estado_alterado_durante_espera_sem_insert(loan_client, change, reason):
    client, conn, _ = loan_client
    if change == 'occupied':
        conn.after_lock = lambda: setattr(conn, 'occupied', True)
    else:
        conn.open_dates = [date(2026, 11, 27)] * 2
        conn.after_lock = lambda: conn.open_dates.append(date(2026, 11, 27))
    response = request(client)
    assert (response.status_code, response.json()['reason']) == (409, reason)
    assert not any('INSERT' in sql for sql, _ in conn.calls)


def test_post_expira_durante_espera_dos_locks(loan_client):
    client, conn, time = loan_client
    conn.after_lock = lambda: time.__setitem__(0, NOW + timedelta(hours=1))
    assert request(client).status_code == 401
    assert not any('INSERT' in sql for sql, _ in conn.calls)


def test_post_data_local_apos_espera_vira_atraso(loan_client):
    client, conn, time = loan_client
    time[0] = datetime(2026, 11, 10, 2, 59, tzinfo=timezone.utc)
    conn.session['expira_em'] = time[0] + timedelta(hours=1)
    conn.open_dates = [date(2026, 11, 9)]
    conn.after_lock = lambda: time.__setitem__(0, datetime(2026, 11, 10, 3, tzinfo=timezone.utc))
    assert request(client).json()['reason'] == 'emprestimo_atrasado'


def test_post_prazo_usa_relogio_apos_espera(loan_client):
    client, conn, time = loan_client
    conn.session['expira_em'] = datetime(2026, 11, 14, 12, tzinfo=timezone.utc)
    conn.after_lock = lambda: time.__setitem__(0, datetime(2026, 11, 13, 12, tzinfo=timezone.utc))
    assert request(client).json()['emprestimo']['previsto_para'] == '2026-12-03'


class UniqueWithConstraint(psycopg.errors.UniqueViolation):
    def __init__(self, name):
        self.name = name
        super().__init__('synthetic sensitive SQL')

    @property
    def diag(self):
        class Diagnostic:
            constraint_name = self.name
        return Diagnostic()


@pytest.mark.parametrize('name,status', [('ux_emprestimos_equipamento_ativo', 409), ('other_unique', 503)])
def test_post_traduz_somente_unique_conhecido(loan_client, name, status):
    client, conn, _ = loan_client
    conn.failure = UniqueWithConstraint(name)
    response = request(client)
    assert (response.status_code, conn.rolled_back, conn.created) == (status, True, None)
    assert 'synthetic' not in response.text


@pytest.mark.parametrize('error', [psycopg.errors.DeadlockDetected, psycopg.errors.LockNotAvailable,
                                    psycopg.errors.CheckViolation, psycopg.OperationalError])
def test_post_erro_driver_sanitizado_com_rollback(loan_client, error):
    client, conn, _ = loan_client
    conn.failure = error('synthetic SQL password')
    response = request(client)
    assert (response.status_code, response.json(), response.headers['cache-control'], conn.rolled_back) == (
        503, {'detail': 'Solicitação indisponível.'}, 'no-store', True)


def test_post_falha_commit_nao_retorna_sucesso(loan_client):
    client, conn, _ = loan_client
    conn.commit_failure = True
    response = request(client)
    assert (response.status_code, conn.created, conn.rolled_back) == (503, None, True)


def test_repositorio_falha_configuracao_sanitizada(monkeypatch):
    from src.auth import PostgresAuthRepository
    monkeypatch.delenv('DATABASE_URL', raising=False)
    repo = PostgresEmprestimoRepository(PostgresAuthRepository().connection, clock=lambda: NOW)
    with pytest.raises(EmprestimoUnavailable):
        repo.solicitar(TOKEN, ITEM)
