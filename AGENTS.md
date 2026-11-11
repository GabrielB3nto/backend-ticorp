# EMPREST.AI

Sistema de empréstimo de equipamentos, com frontend e backend separados.
O documento de negócio está em docs/PRD.md. Consulte também rules/.

## Arquitetura e estado documental

- ADR-004 define entry point FastAPI e health check sem acesso ao banco.
- ADR-001 e ADR-002 estão vazios: o índice não comprova decisões implementáveis.
- ADR-003 trata do Programa de Pontos, não do prazo de empréstimos.
- Não remova nem reescreva ADRs históricos ou código legado automaticamente.
- docs/PRD.md registra EMPREST.AI e preserva pontos como histórico.
- As decisões de negócio e os recortes implementados do EMPREST.AI estão
  registrados em docs/PRD.md, docs/plan.md e docs/adr/. Não trate aprovações
  específicas como autorização para escrita em produção ou deploy.
- Pixabay substitui Pexels por orientação do professor relatada por Gabriel.
  Consulte o contrato atualizado no PRD; não reutilize licença/atribuição Pexels.
- Limite confirmado: 3 empréstimos em aberto. Manutenção confirmada:
  TI-0004, TI-0007 e TI-0010.
- Prazo confirmado: 14 dias de segunda a sexta, excluindo o dia inicial,
  sem descontar feriados, America/Sao_Paulo; atraso no dia após o vencimento.

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
