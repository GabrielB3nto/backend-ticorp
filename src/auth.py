import hashlib
import os
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Protocol

from src.passwords import verify_password

SESSION_SECONDS = 3600


class AuthUnavailable(Exception):
    pass


class LoginBusy(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class AuthRepository(Protocol):
    def login(self, email, password, token_hash, now, expires): ...
    def user_for_session(self, token_hash, now): ...
    def revoke(self, token_hash): ...


class PostgresAuthRepository:
    @contextmanager
    def connection(self):
        # Configuração somente servidor; não abre conexão no import ou health.
        url = os.environ.get('DATABASE_URL')
        if not url:
            raise AuthUnavailable() from None
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            raise AuthUnavailable() from None
        try:
            with psycopg.connect(url, connect_timeout=5, row_factory=dict_row,
                                 options='-c statement_timeout=5000 -c lock_timeout=1000 -c search_path=public') as conn:
                yield conn
        except psycopg.Error:
            raise AuthUnavailable() from None

    def login(self, email, password, token_hash, now, expires):
        with self.connection() as conn:
            locked = conn.execute(
                'SELECT pg_try_advisory_xact_lock(hashtextextended(%s, 314159)) AS locked',
                (email,),
            ).fetchone()['locked']
            if not locked:
                raise LoginBusy()
            row = conn.execute(
                'SELECT * FROM app_private.lock_login_user(%s)',
                (email,),
            ).fetchone()
            valid = verify_password(password, row['senha_hash'] if row else None)
            if not valid or not row or not row['ativo']:
                raise InvalidCredentials()
            conn.execute(
                'INSERT INTO public.sessoes_login (token_hash, usuario_id, criado_em, expira_em) VALUES (%s, %s, %s, %s)',
                (token_hash, row['id'], now, expires),
            )
            return {'id': str(row['id']), 'email': row['email']}

    def user_for_session(self, token_hash, now):
        with self.connection() as conn:
            row = conn.execute(
                'SELECT u.id, u.email FROM public.sessoes_login s JOIN public.usuarios u ON u.id = s.usuario_id '
                'WHERE s.token_hash = %s AND s.expira_em > %s AND u.ativo = true',
                (token_hash, now),
            ).fetchone()
            return {'id': str(row['id']), 'email': row['email']} if row else None

    def revoke(self, token_hash):
        with self.connection() as conn:
            conn.execute('DELETE FROM public.sessoes_login WHERE token_hash = %s', (token_hash,))


class AuthService:
    def __init__(self, repository: AuthRepository, clock=None):
        self.repository = repository
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def login(self, email, password):
        token = secrets.token_urlsafe(32)
        now = self.clock()
        user = self.repository.login(email.strip().lower(), password, self.digest(token),
                                     now, now + timedelta(seconds=SESSION_SECONDS))
        return {'user': user, 'expires_in': SESSION_SECONDS, 'access_token': token, 'token_type': 'bearer'}

    def me(self, token):
        user = self.repository.user_for_session(self.digest(token), self.clock())
        if not user:
            raise InvalidCredentials()
        return {'user': user}

    def logout(self, token):
        self.repository.revoke(self.digest(token))

    @staticmethod
    def digest(token):
        return hashlib.sha256(token.encode('ascii')).hexdigest()
