# TiCorp — Programa de Pontos

Backend do sistema de fidelidade da rede varejista.

## Executar localmente

1. Execute: python -m pip install -r requirements.txt
2. Defina PYTHONPATH=src.
3. Execute: python -m uvicorn pontos.api.app:app --host 127.0.0.1 --port 5000

A API estará em http://127.0.0.1:5000. A verificação de saúde é GET /health.

## Banco de dados

Configure DATABASE_URL no arquivo .env e aplique
migrations/001_programa_pontos.sql ao PostgreSQL antes de usar os endpoints que
consultam dados.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| docs/PRD.md | Requisitos de negócio |
| docs/adr/ | Decisões de arquitetura |
| migrations/ | Schema do Programa de Pontos |
| src/pontos/ | Domínio, aplicação, infraestrutura e API |
