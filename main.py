"""Ponto de entrada HTTP da aplicacao no Vercel."""

import os
import re
from urllib.parse import urlsplit
from uuid import UUID

from fastapi import Depends, FastAPI, Header, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, SecretStr

from src.auth import AuthService, AuthUnavailable, InvalidCredentials, LoginBusy, PostgresAuthRepository
from src.consultas import ConsultaUnavailable, PostgresConsultaRepository
from src.emprestimos import EmprestimoRecusado, EmprestimoUnavailable, PostgresEmprestimoRepository


class EmprestimoInput(BaseModel):
    model_config = {'extra': 'forbid'}
    equipamento_id: UUID


def get_emprestimo_repository():
    return PostgresEmprestimoRepository(PostgresAuthRepository().connection)


app = FastAPI(title="EMPREST.AI API")


def cors_origins():
    origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    result = []
    for value in origins:
        origin = value.strip()
        parsed = urlsplit(origin)
        if (parsed.scheme in ('http', 'https') and parsed.hostname and not parsed.username
                and not parsed.password and not parsed.path and not parsed.query
                and not parsed.fragment and '*' not in origin):
            result.append(origin)
    return result


app.add_middleware(CORSMiddleware, allow_origins=cors_origins(),
                   allow_methods=['GET', 'POST'], allow_headers=['Authorization', 'Content-Type'])


class LoginInput(BaseModel):
    email: str = Field(strict=True, min_length=1, max_length=254)
    password: SecretStr = Field(min_length=1, max_length=1024)


def get_auth_service():
    return AuthService(PostgresAuthRepository())


def bearer_token(authorization):
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer' and re.fullmatch(r'[A-Za-z0-9_-]{43}', parts[1]):
        return parts[1]
    return None


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    # Nunca serializar exc.errors()/body: podem conter a senha ou JSON inteiro.
    return JSONResponse(status_code=422, content={'detail': 'Dados inválidos.'},
                        headers={'Cache-Control': 'no-store'})


@app.exception_handler(AuthUnavailable)
async def auth_unavailable(request, exc):
    return JSONResponse(status_code=503, content={'detail': 'Autenticação indisponível.'},
                        headers={'Cache-Control': 'no-store'})


@app.exception_handler(InvalidCredentials)
async def invalid_credentials(request, exc):
    return JSONResponse(status_code=401, content={'detail': 'Credenciais inválidas.'},
                        headers={'Cache-Control': 'no-store', 'WWW-Authenticate': 'Bearer'})


@app.exception_handler(LoginBusy)
async def login_busy(request, exc):
    return JSONResponse(status_code=429, content={'detail': 'Tente novamente.'},
                        headers={'Cache-Control': 'no-store', 'Retry-After': '1'})


@app.post('/api/login')
def login(body: LoginInput, response: Response, service=Depends(get_auth_service)):
    response.headers['Cache-Control'] = 'no-store'
    return service.login(body.email, body.password.get_secret_value())


@app.get('/api/me')
def me(response: Response, authorization: str | None = Header(default=None), service=Depends(get_auth_service)):
    token = bearer_token(authorization)
    if not token:
        raise InvalidCredentials()
    response.headers['Cache-Control'] = 'no-store'
    return service.me(token)


@app.post('/api/logout', status_code=204)
def logout(authorization: str | None = Header(default=None), service=Depends(get_auth_service)):
    token = bearer_token(authorization)
    if token:
        service.logout(token)
    return Response(status_code=204, headers={'Cache-Control': 'no-store'})


def get_consulta_repository():
    return PostgresConsultaRepository(PostgresAuthRepository().connection)


def authenticated_user(authorization: str | None = Header(default=None), service=Depends(get_auth_service)):
    token = bearer_token(authorization)
    if not token:
        raise InvalidCredentials()
    return service.me(token)['user']


@app.exception_handler(ConsultaUnavailable)
async def consulta_unavailable(request, exc):
    return JSONResponse(status_code=503, content={'detail': 'Consulta indisponível.'},
                        headers={'Cache-Control': 'no-store'})


@app.get('/api/equipamentos')
def equipamentos(response: Response, user=Depends(authenticated_user), repository=Depends(get_consulta_repository)):
    response.headers['Cache-Control'] = 'no-store'
    return {'equipamentos': repository.equipamentos()}


@app.get('/api/emprestimos/meus')
def emprestimos_meus(response: Response, user=Depends(authenticated_user), repository=Depends(get_consulta_repository)):
    response.headers['Cache-Control'] = 'no-store'
    return {'emprestimos': repository.emprestimos_meus(user['id'])}


@app.exception_handler(EmprestimoUnavailable)
async def emprestimo_unavailable(request, exc):
    return JSONResponse(status_code=503, content={'detail': 'Solicitação indisponível.'},
                        headers={'Cache-Control': 'no-store'})


@app.exception_handler(EmprestimoRecusado)
async def emprestimo_recusado(request, exc):
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail, 'reason': exc.reason},
                        headers={'Cache-Control': 'no-store'})


@app.post('/api/emprestimos', status_code=201)
def solicitar_emprestimo(body: EmprestimoInput, response: Response,
                        authorization: str | None = Header(default=None),
                        repository=Depends(get_emprestimo_repository)):
    token = bearer_token(authorization)
    if not token:
        raise InvalidCredentials()
    response.headers['Cache-Control'] = 'no-store'
    return {'emprestimo': repository.solicitar(token, body.equipamento_id)}


@app.get("/health", tags=["operacao"])
def health() -> dict[str, str]:
    """Informa que a API esta disponivel."""
    return {"status": "ok"}
