from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from main import app, get_auth_service, get_consulta_repository
from src.auth import AuthService, AuthUnavailable, PostgresAuthRepository
from src.consultas import ConsultaUnavailable, PostgresConsultaRepository

NOW = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
USER_A = '00000000-0000-0000-0000-000000000001'
USER_B = '00000000-0000-0000-0000-000000000002'
TOKEN_A = 'a' * 43
TOKEN_B = 'b' * 43
EQUIPMENT_ID = UUID('00000000-0000-0000-0000-000000000010')
LOAN_ID = UUID('00000000-0000-0000-0000-000000000020')
PATHS = ['/api/equipamentos', '/api/emprestimos/meus']


def equipment(status='DISPONIVEL'):
    return {'id': EQUIPMENT_ID, 'nome': 'Equipamento sintético', 'patrimonio': None,
            'categoria': 'Notebook', 'status': status}


def loan(user=USER_A, returned=None, identifier=LOAN_ID):
    return {'id': identifier, 'usuario_id': user, 'devolvido_em': returned,
            'retirado_em': NOW.astimezone(timezone(timedelta(hours=-3))),
            'previsto_para': date(2026, 11, 27), 'equipamento_id': EQUIPMENT_ID,
            'nome': 'Equipamento sintético', 'patrimonio': None, 'categoria': 'Notebook'}


class FakeConnection:
    def __init__(self):
        self.calls = []
        self.equipment_rows = []
        self.loans = []
        self.sessions = {
            AuthService.digest(TOKEN_A): (USER_A, NOW + timedelta(hours=1), True),
            AuthService.digest(TOKEN_B): (USER_B, NOW + timedelta(hours=1), True),
        }
        self.failure = False

    def execute(self, sql, params):
        self.calls.append((sql, params))
        if self.failure:
            raise AuthUnavailable('synthetic driver SQL credential detail')
        return self

    def fetchone(self):
        sql, params = self.calls[-1]
        assert 's.expira_em > %s AND u.ativo = true' in sql
        session = self.sessions.get(params[0])
        if session and session[1] > params[1] and session[2]:
            return {'id': session[0], 'email': 'synthetic@example.test'}
        return None

    def fetchall(self):
        sql, params = self.calls[-1]
        if 'CASE WHEN' in sql:
            return self.equipment_rows
        assert 'WHERE l.usuario_id = %s AND l.devolvido_em IS NULL' in sql
        return [row for row in self.loans if row['usuario_id'] == params[0] and row['devolvido_em'] is None]


@contextmanager
def fake_connection(conn):
    yield conn


@pytest.fixture
def read_client():
    auth_conn = FakeConnection()
    read_conn = FakeConnection()
    auth_repo = PostgresAuthRepository()
    auth_repo.connection = lambda: fake_connection(auth_conn)
    app.dependency_overrides[get_auth_service] = lambda: AuthService(auth_repo, clock=lambda: NOW)
    app.dependency_overrides[get_consulta_repository] = lambda: PostgresConsultaRepository(lambda: fake_connection(read_conn))
    try:
        with TestClient(app) as client:
            yield client, auth_conn, read_conn
    finally:
        app.dependency_overrides.clear()


def headers(token=TOKEN_A):
    return {'Authorization': f'Bearer {token}'}


@pytest.mark.parametrize('path,key', zip(PATHS, ['equipamentos', 'emprestimos']))
def test_leitura_vazia_autenticada(read_client, path, key):
    client, _, _ = read_client
    response = client.get(path, headers=headers())
    assert (response.status_code, response.json(), response.headers['cache-control']) == (200, {key: []}, 'no-store')


@pytest.mark.parametrize('path', PATHS)
@pytest.mark.parametrize('header', [None, 'Basic abc', 'Bearer xyz', 'Bearer ' + 'c' * 43])
def test_leitura_rejeita_token_ausente_ou_invalido(read_client, path, header):
    client, _, read_conn = read_client
    response = client.get(path, headers={'Authorization': header} if header else {})
    assert (response.status_code, response.json(), response.headers['cache-control']) == (
        401, {'detail': 'Credenciais inválidas.'}, 'no-store')
    assert not read_conn.calls


@pytest.mark.parametrize('path', PATHS)
@pytest.mark.parametrize('state', ['expired', 'inactive', 'revoked'])
def test_leitura_rejeita_sessao_sem_validade(read_client, path, state):
    client, auth_conn, read_conn = read_client
    digest = AuthService.digest(TOKEN_A)
    if state == 'revoked':
        auth_conn.sessions.pop(digest)
    else:
        auth_conn.sessions[digest] = (USER_A, NOW if state == 'expired' else NOW + timedelta(hours=1), state != 'inactive')
    assert client.get(path, headers=headers()).status_code == 401
    assert not read_conn.calls


@pytest.mark.parametrize('user,token', [(USER_A, TOKEN_A), (USER_B, TOKEN_B)])
def test_meus_emprestimos_segrega_titular_e_exclui_devolvidos(read_client, user, token):
    client, _, read_conn = read_client
    read_conn.loans = [loan(), loan(USER_B, identifier=UUID(int=21)), loan(user, returned=NOW, identifier=UUID(int=22))]
    other = USER_B if user == USER_A else USER_A
    response = client.get('/api/emprestimos/meus', params={'usuario_id': other, 'id': other}, headers=headers(token))
    result = response.json()['emprestimos']
    assert [row['id'] for row in result] == [str(LOAN_ID if user == USER_A else UUID(int=21))]
    assert read_conn.calls[-1][1] == (user,)


def test_meus_emprestimos_formato_datas_e_campos(read_client):
    client, _, read_conn = read_client
    read_conn.loans = [loan()]
    result = client.get('/api/emprestimos/meus', headers=headers()).json()
    assert result == {'emprestimos': [{'id': str(LOAN_ID), 'retirado_em': '2026-11-09T09:00:00-03:00',
        'previsto_para': '2026-11-27', 'equipamento': {'id': str(EQUIPMENT_ID), 'nome': 'Equipamento sintético',
        'patrimonio': None, 'categoria': 'Notebook'}}]}


@pytest.mark.parametrize('status', ['DISPONIVEL', 'EMPRESTADO', 'MANUTENCAO', 'INATIVO'])
def test_catalogo_preserva_resultado_sql_sem_imagem_falsa(read_client, status):
    client, _, read_conn = read_client
    read_conn.equipment_rows = [equipment(status)]
    result = client.get('/api/equipamentos', headers=headers()).json()
    assert result == {'equipamentos': [{**equipment(status), 'id': str(EQUIPMENT_ID)}]}


def test_catalogo_sql_classifica_sem_duplicar_e_preserva_status_operacional():
    conn = FakeConnection()
    PostgresConsultaRepository(lambda: fake_connection(conn)).equipamentos()
    sql, params = conn.calls[-1]
    assert "CASE WHEN e.status_operacional <> 'DISPONIVEL' THEN e.status_operacional" in sql
    assert 'WHEN EXISTS (SELECT 1 FROM public.emprestimos l WHERE l.equipamento_id = e.id AND l.devolvido_em IS NULL)' in sql
    assert "THEN 'EMPRESTADO' ELSE 'DISPONIVEL' END AS status" in sql
    assert 'JOIN public.emprestimos' not in sql
    assert 'WHERE e.status_operacional' not in sql
    assert params == ()


def test_meus_emprestimos_sql_parametriza_titular():
    conn = FakeConnection()
    suspicious = "' OR 1=1 --"
    PostgresConsultaRepository(lambda: fake_connection(conn)).emprestimos_meus(suspicious)
    sql, params = conn.calls[-1]
    assert suspicious not in sql
    assert params == (suspicious,)
    assert 'WHERE l.usuario_id = %s AND l.devolvido_em IS NULL' in sql


@pytest.mark.parametrize('path', PATHS)
@pytest.mark.parametrize('source,detail', [('auth', 'Autenticação indisponível.'), ('read', 'Consulta indisponível.')])
def test_leitura_falha_sanitizada_sem_cache_e_health_independente(read_client, path, source, detail):
    client, auth_conn, read_conn = read_client
    (auth_conn if source == 'auth' else read_conn).failure = True
    response = client.get(path, headers=headers())
    assert (response.status_code, response.json(), response.headers['cache-control']) == (503, {'detail': detail}, 'no-store')
    assert client.get('/health').json() == {'status': 'ok'}


@pytest.mark.parametrize('method,args', [('equipamentos', ()), ('emprestimos_meus', (USER_A,))])
def test_repositorio_reutiliza_conexao_sem_configuracao(method, args, monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    repository = PostgresConsultaRepository(PostgresAuthRepository().connection)
    with pytest.raises(ConsultaUnavailable):
        getattr(repository, method)(*args)


@pytest.mark.parametrize('path', PATHS)
def test_recorte_nao_adiciona_post(read_client, path):
    client, _, _ = read_client
    assert client.post(path, headers=headers()).status_code == 405
