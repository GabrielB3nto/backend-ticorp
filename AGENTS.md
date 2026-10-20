# Programa de Pontos

Sistema de fidelidade da rede. O documento de negócio está em docs/PRD.md.

## Arquitetura

- **Domínio isolado de infra** (ADR-001): camadas domínio, aplicação, infra, API.
- **Lançamentos imutáveis** (ADR-002): cada operação cria novo lançamento; saldo calculado.
- **Expiração 12 meses** (ADR-003): lazy evaluation em `calcular_saldo()`.
- **Plano de implementação** em `docs/plan.md`: 10 etapas, MVP = etapas 0–4.

## Processo

- Leia docs/PRD.md antes de implementar qualquer feature.
- Antes de implementar, liste os requisitos ambíguos que encontrar.
  Não decida por conta própria o que o PRD deixou em aberto — pergunte.
- Decisões estruturais (modelagem de dados, fronteiras de módulo,
  dependências externas) precisam de um ADR em docs/adr/ antes do código.
- Consulte docs/adr/README.md antes de propor mudanças estruturais.
- Não contrarie uma decisão registrada em ADR sem avisar explicitamente.
  Se você discorda de um ADR, diga por quê e espere — não refatore.

## Qualidade

- Toda regra de negócio tem teste.
- Mudanças pequenas e revisáveis. Uma tarefa por vez.
