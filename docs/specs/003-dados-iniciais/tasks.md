# Tarefas — Spec 003: Dados iniciais

**Status:** planejamento; nenhuma tarefa de implementação concluída. Uma tarefa aprovada por vez, seguida dos checks.

- [ ] T1 · CA-05/06/08: receber decisões técnicas/ADRs, aprovação da spec/plano e mecanismo de isolamento demonstrável. Termina com aprovação explícita registrada.
- [ ] T2 · CA-08: configurar verificador obrigatório, somente leitura, contexto limpo e tabela comparável. Depende T1; termina com teste de escrita bloqueada e erro plantado reprovado/revertido.
- [ ] T3 · CA-01/02: preparar lista exata e formato de manifesto com teste dos 12 patrimônios. Depende T1.
- [ ] T4a · CA-02/03/06/07: criar a skill imagens-equipamentos com SKILL.md, referências da API/licença e separação de preparo local e publicação humana. Depende T1/T3; termina com contrato rastreável e sem upload de produção disponível ao agente.
- [ ] T4 · CA-02/07: implementar scripts de preparo Pixabay/cache/download limitado usados pela skill, com ferramenta aprovada. Depende T4a; termina com testes de repetição, tamanho e falhas.
- [ ] T5 · CA-03: usuário revisa visualmente as 12 fotos; registrar aprovadas/reprovadas e motivos. Depende T4; sem aprovação visual não há seed final.
- [ ] T6 · CA-01/04: implementar seed local idempotente e preservação de estado existente. Depende T3/T5; termina com segunda execução e teste de item emprestado preservado.
- [ ] T7 · CA-05/06: preparar fluxo humano da conta e upload sem segredos versionados nem escrita remota pelo agente. Depende T1/T6.
- [ ] T8 · CA-01 a CA-08: rodar checks e verificação local; principal corrige falhas locais. Depende T2/T7. Evidências remotas ficam não verificadas; esta rodada não conclui a spec.
- [ ] T9 · CA-05/06/08: usuário valida licença e publica; coletar evidência segura de URLs e conta intacta. Depende T8 sem falhas locais; itens sem evidência permanecem pendentes.
- [ ] T9a · CA-01 a CA-08: verificador reavalia a versão final com evidências humanas remotas, sem escrever em produção. Depende T9; só permite conclusão com cobertura integral, sem itens não verificados.
- [ ] T10 · CA-08: registrar rodadas e decisões no ENTREGA.md dos dois repositórios. Depende T9a; não inventar hash, revisão ou sucesso de produção.
