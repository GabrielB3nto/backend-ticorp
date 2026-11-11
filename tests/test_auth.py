from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from main import app, get_auth_service, cors_origins
from src.auth import AuthService, AuthUnavailable, InvalidCredentials, LoginBusy, PostgresAuthRepository
from src.passwords import hash_password, verify_password

NOW = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
USER = {'id': '00000000-0000-0000-0000-000000000001', 'email': 'teste@example.test'}
PASSWORD = 'synthetic-password'


class FakeRepository:
    def __init__(self):
        self.password_hash = hash_password(PASSWORD)
        self.active = True
        self.exists = True
        self.sessions = {}
        self.failure = None

    def check(self):
        if self.failure:
            raise self.failure()

    def login(self, email, password, token_hash, now, expires):
        self.check()
        valid = verify_password(password, self.password_hash if self.exists else None)
        if not valid or not self.active or email != USER['email'] or not self.exists:
            raise InvalidCredentials()
        self.sessions[token_hash] = expires
        return dict(USER)

    def user_for_session(self, token_hash, now):
        self.check()
        if self.active and self.sessions.get(token_hash, now) > now:
            return dict(USER)
        return None

    def revoke(self, token_hash):
        self.check()
        self.sessions.pop(token_hash, None)


@pytest.fixture
def auth_client():
    repo = FakeRepository()
    time = [NOW]
    service = AuthService(repo, clock=lambda: time[0])
    app.dependency_overrides[get_auth_service] = lambda: service
    with TestClient(app) as client:
        yield client, repo, time
    app.dependency_overrides.clear()


def login_token(client):
    return client.post('/api/login', json={'email': USER['email'], 'password': PASSWORD}).json()['access_token']


def test_login_me_logout_cycle(auth_client):
    client, repo, _ = auth_client
    result = client.post('/api/login', json={'email': ' TESTE@example.test ', 'password': PASSWORD})
    payload = result.json()
    assert result.status_code == 200
    assert payload == {'user': USER, 'expires_in': 3600, 'access_token': payload['access_token'], 'token_type': 'bearer'}
    token = payload['access_token']
    assert token not in repo.sessions
    assert len(next(iter(repo.sessions))) == 64
    headers = {'Authorization': f'Bearer {token}'}
    assert client.get('/api/me', headers=headers).json() == {'user': USER}
    response = client.post('/api/logout', headers=headers)
    assert (response.status_code, response.content) == (204, b'')
    assert client.get('/api/me', headers=headers).status_code == 401
    assert client.post('/api/logout', headers=headers).status_code == 204


@pytest.mark.parametrize('state', ['wrong', 'absent', 'inactive', 'null_hash'])
def test_credentials_rejected_generically(auth_client, state):
    client, repo, _ = auth_client
    password = PASSWORD
    if state == 'wrong':
        password = 'wrong'
    elif state == 'absent':
        repo.exists = False
    elif state == 'inactive':
        repo.active = False
    else:
        repo.password_hash = None
    response = client.post('/api/login', json={'email': USER['email'], 'password': password})
    assert (response.status_code, response.json()) == (401, {'detail': 'Credenciais inválidas.'})
    assert not repo.sessions


@pytest.mark.parametrize('password', [None, '', 123, ['secret'], 'x' * 1025])
def test_invalid_password_input_sanitized(auth_client, password):
    client, _, _ = auth_client
    response = client.post('/api/login', json={'email': USER['email'], 'password': password})
    assert (response.status_code, response.json()) == (422, {'detail': 'Dados inválidos.'})


def test_invalid_json_does_not_echo_password(auth_client):
    client, _, _ = auth_client
    response = client.post('/api/login', content='{"password":"sensitive-synthetic",', headers={'Content-Type': 'application/json'})
    assert (response.status_code, response.json()) == (422, {'detail': 'Dados inválidos.'})


@pytest.mark.parametrize('header', [None, 'Basic abc', 'Bearer xyz', 'Bearer ' + 'a' * 43, 'Bearer ' + 'é' * 43])
def test_invalid_session_rejected(auth_client, header):
    client, _, _ = auth_client
    # HTTP headers transport ASCII; non-ASCII parser is checked directly.
    if header and 'é' in header:
        from main import bearer_token
        assert bearer_token(header) is None
    else:
        assert client.get('/api/me', headers={'Authorization': header} if header else {}).status_code == 401


@pytest.mark.parametrize('offset', [3600, 3601])
def test_expired_session_rejected(auth_client, offset):
    client, _, time = auth_client
    token = login_token(client)
    time[0] = NOW + timedelta(seconds=offset)
    assert client.get('/api/me', headers={'Authorization': f'Bearer {token}'}).status_code == 401


def test_deactivated_user_rejected_each_me(auth_client):
    client, repo, _ = auth_client
    token = login_token(client)
    repo.active = False
    assert client.get('/api/me', headers={'Authorization': f'Bearer {token}'}).status_code == 401


@pytest.mark.parametrize('path', ['/api/login', '/api/me', '/api/logout'])
def test_database_failure_is_generic_and_health_survives(auth_client, path):
    client, repo, _ = auth_client
    token = login_token(client)
    repo.failure = AuthUnavailable
    headers = {'Authorization': f'Bearer {token}'}
    if path == '/api/me':
        response = client.get(path, headers=headers)
    else:
        response = client.post(path, headers=headers, json={'email': USER['email'], 'password': PASSWORD})
    assert (response.status_code, response.json()) == (503, {'detail': 'Autenticação indisponível.'})
    assert client.get('/health').json() == {'status': 'ok'}


def test_busy_account_returns_429(auth_client):
    client, repo, _ = auth_client
    repo.failure = LoginBusy
    assert client.post('/api/login', json={'email': USER['email'], 'password': PASSWORD}).status_code == 429


def test_cors_exact_origin(auth_client):
    client, _, _ = auth_client
    allowed = client.options('/api/login', headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST'})
    denied = client.options('/api/login', headers={'Origin': 'https://evil.example.test', 'Access-Control-Request-Method': 'POST'})
    assert allowed.headers['access-control-allow-origin'] == 'http://localhost:5173'
    assert 'access-control-allow-origin' not in denied.headers


def test_cors_filters_wildcards_and_paths(monkeypatch):
    monkeypatch.setenv('CORS_ORIGINS', '*,https://*.example.test,https://example.test/path,http://localhost:5173')
    assert cors_origins() == ['http://localhost:5173']


@pytest.mark.parametrize('encoded', [None, '', 'abc', 'sha256$600000$a$b', 'pbkdf2_sha256$999999999$a$b', 'pbkdf2_sha256$600000$invalid!$invalid!', 'pbkdf2_sha256$600000$YQ==$Yg=='])
def test_invalid_hash_rejected(encoded):
    assert not verify_password(PASSWORD, encoded)


def test_password_unicode_and_unique_salts():
    first = hash_password('senha-sintética')
    assert verify_password('senha-sintética', first)
    assert first != hash_password('senha-sintética')


def test_postgres_missing_config_without_connection(monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    with pytest.raises(AuthUnavailable):
        PostgresAuthRepository().user_for_session('a' * 64, NOW)


class FakeConnection:
    def __init__(self, row=None, locked=True):
        self.row = row
        self.locked = locked
        self.calls = []

    def execute(self, sql, params):
        self.calls.append((sql, params))
        return self

    def fetchone(self):
        if 'pg_try_advisory' in self.calls[-1][0]:
            return {'locked': self.locked}
        return self.row


def repository_with_connection(conn):
    repo = PostgresAuthRepository()
    @contextmanager
    def connection():
        yield conn
    repo.connection = connection
    return repo


@pytest.mark.parametrize('state', ['ok', 'wrong', 'absent', 'inactive', 'null_hash', 'busy'])
def test_actual_repository_login_with_fake_connection(state):
    row = {**USER, 'ativo': state != 'inactive', 'senha_hash': None if state == 'null_hash' else hash_password(PASSWORD)}
    conn = FakeConnection(None if state == 'absent' else row, state != 'busy')
    repo = repository_with_connection(conn)
    args = (USER['email'], 'wrong' if state == 'wrong' else PASSWORD, 'a' * 64, NOW, NOW + timedelta(hours=1))
    if state == 'ok':
        assert repo.login(*args) == USER
        assert conn.calls[-1][1] == ('a' * 64, USER['id'], NOW, NOW + timedelta(hours=1))
        assert conn.calls[-2] == ('SELECT * FROM app_private.lock_login_user(%s)', (USER['email'],))
    else:
        with pytest.raises(LoginBusy if state == 'busy' else InvalidCredentials):
            repo.login(*args)
        assert not any('INSERT' in sql for sql, _ in conn.calls)


def test_actual_repository_queries_are_parameterized():
    conn = FakeConnection(USER)
    repo = repository_with_connection(conn)
    suspicious = "' OR 1=1 --"
    assert repo.user_for_session(suspicious, NOW) == USER
    sql, params = conn.calls[-1]
    assert suspicious not in sql
    assert params == (suspicious, NOW)
    assert 's.expira_em > %s' in sql and 'u.ativo = true' in sql
    repo.revoke(suspicious)
    assert conn.calls[-1] == ('DELETE FROM public.sessoes_login WHERE token_hash = %s', (suspicious,))


def test_login_uses_locked_security_definer_query():
    conn = FakeConnection({**USER, 'ativo': True, 'senha_hash': hash_password(PASSWORD)})
    repo = repository_with_connection(conn)
    assert repo.login(USER['email'], PASSWORD, 'a' * 64, NOW, NOW + timedelta(hours=1)) == USER
    sql, params = conn.calls[-2]
    assert sql == 'SELECT * FROM app_private.lock_login_user(%s)'
    assert params == (USER['email'],)
