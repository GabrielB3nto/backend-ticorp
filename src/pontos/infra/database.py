"""Configuração e acesso ao PostgreSQL do Programa de Pontos."""

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


def _carregar_env_local() -> None:
    """Carrega variáveis ausentes do .env sem sobrescrever o ambiente."""
    arquivo = Path(__file__).resolve().parents[3] / ".env"
    if not arquivo.exists():
        return

    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip("'\""))


def conectar():
    _carregar_env_local()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL não configurada.")
    return psycopg.connect(url, row_factory=dict_row)
