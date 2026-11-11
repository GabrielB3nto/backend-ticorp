from src.auth import AuthUnavailable


class ConsultaUnavailable(Exception):
    pass


class PostgresConsultaRepository:
    def __init__(self, connection):
        self.connection = connection

    def equipamentos(self):
        try:
            with self.connection() as conn:
                rows = conn.execute(
                    'SELECT e.id, e.nome, e.patrimonio, c.nome AS categoria, '
                    'CASE WHEN e.status_operacional <> \'DISPONIVEL\' THEN e.status_operacional '
                    'WHEN EXISTS (SELECT 1 FROM public.emprestimos l '
                    'WHERE l.equipamento_id = e.id AND l.devolvido_em IS NULL) '
                    'THEN \'EMPRESTADO\' ELSE \'DISPONIVEL\' END AS status '
                    'FROM public.equipamentos e JOIN public.categorias c ON c.id = e.categoria_id '
                    'ORDER BY e.patrimonio, e.id',
                    (),
                ).fetchall()
        except AuthUnavailable:
            raise ConsultaUnavailable() from None
        return [{**row, 'id': str(row['id'])} for row in rows]

    def emprestimos_meus(self, usuario_id):
        try:
            with self.connection() as conn:
                rows = conn.execute(
                    'SELECT l.id, l.retirado_em, l.previsto_para, e.id AS equipamento_id, '
                    'e.nome, e.patrimonio, c.nome AS categoria '
                    'FROM public.emprestimos l JOIN public.equipamentos e ON e.id = l.equipamento_id '
                    'JOIN public.categorias c ON c.id = e.categoria_id '
                    'WHERE l.usuario_id = %s AND l.devolvido_em IS NULL '
                    'ORDER BY l.previsto_para, l.id',
                    (usuario_id,),
                ).fetchall()
        except AuthUnavailable:
            raise ConsultaUnavailable() from None
        return [
            {'id': str(row['id']), 'retirado_em': row['retirado_em'].isoformat(),
             'previsto_para': row['previsto_para'].isoformat(),
             'equipamento': {'id': str(row['equipamento_id']), 'nome': row['nome'],
                             'patrimonio': row['patrimonio'], 'categoria': row['categoria']}}
            for row in rows
        ]
