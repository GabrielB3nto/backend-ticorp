# ADR-004 - Entry point e health check HTTP

**Status:** aceito
**Data:** 2026-10-22

## Contexto

O backend sera publicado no Vercel, que requer uma aplicacao FastAPI exportada
por um arquivo de entrada reconhecivel. A primeira tela do EMPREST.AI ainda nao
faz chamadas a API nem persiste dados, mas a operacao precisa de uma forma de
verificar se o servico esta disponivel.

## Decisao

Manter `main.py` na raiz como entry point do FastAPI e expor `GET /health`,
retornando `{ "status": "ok" }`. O endpoint nao acessa banco de dados.

## Alternativas consideradas

Restaurar a API antiga do Programa de Pontos foi descartado porque seus
endpoints e dominio nao correspondem ao EMPREST.AI. Tambem foi descartado
adiar todo o deploy ate existir persistencia, pois isso impediria validar a
infraestrutura de publicacao.

## Consequencias

O health check so confirma que o processo HTTP iniciou; ele nao verifica a
conectividade com o banco nem oferece operacoes de equipamentos ou emprestimos.
