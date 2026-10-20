# ADR-004 — PostgreSQL para a persistência do Programa de Pontos

**Status:** aceito  
**Data:** 2026-10-19

## Contexto

O Programa de Pontos precisa de consultas rápidas de saldo, histórico
auditável e dados persistentes para o painel administrativo.

## Decisão

O sistema usará PostgreSQL com as tabelas clientes e lancamentos. A primeira
migration do projeto cria o schema, seus índices e uma proteção contra alteração
ou remoção de lançamentos.

A camada de infraestrutura concentra o acesso ao banco; a API apenas traduz
HTTP e a camada de domínio permanece independente de detalhes de persistência.

## Consequências

- DATABASE_URL é obrigatória para consultas e lançamentos.
- O dashboard retorna dados reais ou uma resposta 503 quando o banco não puder
  ser alcançado.
- Lançamentos respeitam a imutabilidade do ADR-002 também no banco.
