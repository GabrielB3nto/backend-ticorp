# Spec 001 — Fundação do projeto

**Status:** implementada; regressão pendente de dependências locais  
**Vínculo:** Etapa 0 de `docs/plan.md`  
**Data:** 2026-09-28

## Objetivo

Preparar a estrutura mínima do backend para que as próximas fatias possam
implementar o Programa de Pontos respeitando as camadas já decididas, sem
introduzir regra de negócio, persistência ou API antes da hora.

## Regras

- O código do backend vive em `src/pontos/` e é separado nas camadas
  `dominio`, `aplicacao`, `infra` e `api`.
- As decisões registradas em `docs/adr/` são consultadas pelo índice
  `docs/adr/README.md` antes de alterações estruturais.
- `AGENTS.md` permanece como ponto de entrada para a arquitetura e o processo
  do repositório.
- Esta fatia não cria endpoint, tabela, migration ou regra de pontuação.

## Critérios de aceitação

- **CA-01:** existem os pacotes `src/pontos/dominio/`,
  `src/pontos/aplicacao/`, `src/pontos/infra/` e `src/pontos/api/`.
- **CA-02:** `import pontos`, `import pontos.aplicacao`, `import pontos.infra`
  e `import pontos.api` funcionam com `src/` no caminho de importação.
- **CA-03:** `docs/adr/README.md` lista os ADRs 001, 002 e 003 como aceitos.
- **CA-04:** `AGENTS.md` identifica domínio isolado de infraestrutura e aponta
  para o PRD, os ADRs e o plano de implementação.
- **CA-05:** não há alteração de comportamento de negócio, banco de dados ou
  contrato HTTP nesta fatia.

## Fora de escopo

- Entidades de domínio e cálculo de saldo (Etapas 1 e 2).
- Repositório, SQLite e schema (Etapa 3).
- Endpoints HTTP e integração com a tela (Etapa 4).
- Resgate, estorno, campanhas e relatórios.

## Contrato afetado

Nenhum contrato HTTP, schema ou tela é alterado. O único contrato introduzido
é interno: as próximas implementações devem usar a estrutura de pacotes em
`src/pontos/`.
