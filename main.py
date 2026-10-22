"""Ponto de entrada HTTP da aplicacao no Vercel."""

from fastapi import FastAPI


app = FastAPI(title="EMPREST.AI API")


@app.get("/health", tags=["operacao"])
def health() -> dict[str, str]:
    """Informa que a API esta disponivel."""
    return {"status": "ok"}
