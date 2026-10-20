# ADR-004 — PostgreSQL para a persistência do Programa de Pontos

**Status:** aceito  
**Data:** 2026-10-19

## Contexto

O ambiente configurado expõe um PostgreSQL e já contém tabelas de outro domínio
(empréstimos de equipamentos). O Programa de Pontos precisa persistir clientes e
lançamentos imutáveis sem afetar esse domínio.

## Decisão

O Programa de Pontos usará novas tabelas PostgreSQL, com prefixo lógico próprio:
clientes e lancamentos. A API acessará o banco por um repositório na camada de
infraestrutura; a camada de aplicação permanece responsável por orquestrar as
consultas e a API só traduz HTTP.

As migrations serão aditivas. Os lançamentos terão bloqueio de atualização e
remoção no banco para reforçar a imutabilidade definida no ADR-002.

## Consequências

- O banco existente de empréstimos permanece intacto.
- O dashboard consulta agregações reais; quando não houver dados, retorna zero e
  listas vazias.
- A aplicação requer DATABASE_URL e o driver psycopg.
