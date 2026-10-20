"""API HTTP do Programa de Pontos."""

from datetime import date
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..infra.repositorio_postgres import RepositorioPontosPostgres

app = FastAPI(title="TiCorp — Programa de Pontos")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
repositorio = RepositorioPontosPostgres()


class CompraEntrada(BaseModel):
    cliente_id: UUID
    valor: float = Field(gt=0)
    data: date


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/dashboard/resumo")
def dashboard_resumo():
    return repositorio.resumo_dashboard()


@app.get("/clientes/{cliente_id}/saldo")
def saldo_cliente(cliente_id: UUID, em: date | None = None):
    saldo = repositorio.saldo_cliente(cliente_id, em or date.today())
    if saldo is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return saldo


@app.post("/compras", status_code=201)
def registrar_compra(compra: CompraEntrada):
    try:
        pontos = repositorio.registrar_compra(compra.cliente_id, compra.valor, compra.data)
    except LookupError as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    return {"pontos_gerados": pontos}
