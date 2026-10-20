# Handoff — sessão 2026-08-17

## Onde parei

Projeto ainda sem código (`src/` não existe). Nesta sessão foram produzidas a proposta de arquitetura técnica (no chat) e o plano de implementação em 10 etapas (0–9), aprovado no modo Plan mas **não persistido** em `docs/plan.md`. ADR-001 e ADR-002 existem como arquivos; ADR-003 já estava no índice. A tela `static/index.html` continua em modo demonstração porque os endpoints ainda não existem.

## Decisões não óbvias

- **MVP = Etapas 0–4.** Entrega mínima quando `GET /clientes/{id}/saldo` e `POST /compras` funcionarem e a tela parar de exibir o banner de demo. Etapas 5–9 cobrem o PRD completo.
- **Arredondamento provisório:** usar `floor(valor)` na Etapa 2 até Marketing definir R$ 49,99 → 49 ou 50.
- **Expiração lazy na v1:** calcular lotes expirados em `calcular_saldo` sem job noturno; revisitar na Etapa 8 se o Financeiro exigir lançamentos `EXPIRACAO` materializados.
- **Resgate (Etapa 7):** recomendado FIFO por `expira_em`, mas precisa virar ADR-004 antes de codar — ver ambiguidades no plano.
- **`rules/` fica em `turnover/rules/`**, não dentro de `programa-pontos/`. O AGENTS.md referencia caminhos relativos à raiz do monorepo de aula.

Decisões já registradas em ADR — não repetir aqui: domínio isolado (ADR-001), lançamentos imutáveis (ADR-002), expiração 12 meses (ADR-003).

## O que tentei e não funcionou

- O plano foi gerado no modo Plan e ficou apenas em `.cursor/plans/plano_programa_pontos_16063952.plan.md`. Não foi copiado para `programa-pontos/docs/plan.md` durante a sessão.

## Próximo passo exato

Salvar o conteúdo do plano aprovado em `programa-pontos/docs/plan.md` e, em seguida, executar a **Etapa 0** do plano: atualizar `docs/adr/README.md` (indexar ADR-001 e ADR-002), acrescentar seção Arquitetura ao `AGENTS.md` e criar o esqueleto `src/pontos/{dominio,aplicacao,infra,api}/` + `tests/dominio/`.

## Arquivos relevantes

- `programa-pontos/docs/PRD.md`
- `programa-pontos/docs/adr/001-dominio-isolado-de-infra.md`
- `programa-pontos/docs/adr/002-lancamentos-vs-saldo.md`
- `programa-pontos/docs/adr/003-expiracao-de-pontos.md`
- `programa-pontos/docs/adr/README.md` (pendente: indexar 001 e 002)
- `programa-pontos/static/index.html` (contrato fixo da API)
- `programa-pontos/AGENTS.md`
- `rules/handoff.md`
- `rules/tests.md`
- `rules/checks.md`
- `.cursor/plans/plano_programa_pontos_16063952.plan.md` (plano aprovado, ainda não commitado em `docs/plan.md`)
