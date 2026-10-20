# Plano de implementação — Programa de Pontos

**Status:** aprovado  
**Data:** 2026-08-17  
**MVP:** Etapas 0–4

## Arquitetura

- **Domínio isolado de infra** (ADR-001): camadas domínio, aplicação, infra, API.
- **Lançamentos vs. saldo** (ADR-002): imutabilidade de lançamentos, saldo calculado.
- **Expiração 12 meses** (ADR-003): lazy evaluation no `calcular_saldo`.

## Etapas

### Etapa 0: Setup de pasta e índice de decisões
- Criar `src/pontos/{dominio,aplicacao,infra,api}/`
- Criar `tests/dominio/`
- Indexar ADR-001 e ADR-002 em `docs/adr/README.md`
- Adicionar seção Arquitetura em `AGENTS.md`

### Etapa 1: Modelo de domínio (Cliente, Lançamento, Saldo)
- Classe `Cliente` (id, nome)
- Classe `Lançamento` (id, cliente_id, tipo, pontos, data_criacao, expira_em)
- Valor-objeto `Saldo` (pontos_vigentes, histórico de lotes)
- Testes: inserção, expiração lazy, cálculo de saldo

### Etapa 2: Regras de negócio (conversão R$ → pontos)
- Função `converter_reais_para_pontos(valor: float) -> int`
  - Arredonda para baixo (`floor`) até Marketing definir arredondamento final
- Função `calcular_saldo(cliente_id)` → `Saldo`
  - Filtra lançamentos expirados, soma os vigentes
- Testes: conversão com valores típicos (R$ 0,99, R$ 49,99, R$ 100,00)

### Etapa 3: Repositório e persistência (banco em memória, depois SQLite)
- Interface `RepositorioCliente`
- Implementação em memória para testes
- Implementação SQLite com schema:
  - `clientes (id, nome)`
  - `lancamentos (id, cliente_id, tipo, pontos, data_criacao, expira_em)`
- Testes: CRUD, múltiplos clientes

### Etapa 4: API HTTP (GET /clientes/{id}/saldo, POST /compras)
- Framework: Flask (Python) ou FastAPI
- Endpoints:
  - `GET /clientes/{id}/saldo` → JSON com pontos_vigentes
  - `POST /compras` → JSON (cliente_id, valor_reais) → registra lançamento, retorna novo saldo
- Remover banner de demo em `static/index.html`
- Testes: integração com repositório SQLite

### Etapa 5: Resgate básico (FIFO por expira_em)
- Endpoint `POST /resgates` → (cliente_id, pontos) → deduz saldo em ordem FIFO
- ADR-004: protocolo de resgate e ambiguidades
- Testes: múltiplos lotes, expiração durante resgate

### Etapa 6: Devoluções (reversa de compra)
- Tipo de lançamento `DEVOLUCAO`
- Endpoint `POST /devolucoes` → reverte lançamento de compra
- Testes: lançamento reverso, saldo correto

### Etapa 7: Resgate com preferência de saldo expirado
- Opção de priorizar pontos próximos de expiração
- Endpoint `POST /resgates/prioridade-expiracao`
- Testes: seleção de lotes

### Etapa 8: Job noturno de materialização de EXPIRACAO
- Se Financeiro exigir lançamentos `EXPIRACAO` imutáveis
- Scheduler asyncio ou APScheduler
- Revisitar necessidade com Financeiro

### Etapa 9: Auditoria e relatórios
- Tabela de auditoria de operações
- Endpoints de relatório (extrato do cliente, auditoria global)
- Dashboard de métricas (pontos em circulação, taxa de resgate)

---

**Decisões pendentes:**
- ADR-004: protocolo de resgate e ordem FIFO (Etapa 5)
- Arredondamento: `floor()` é provisório até Marketing definir (Etapa 2)
- Materialização de EXPIRACAO: agenda noturna só se Financeiro exigir (Etapa 8)
