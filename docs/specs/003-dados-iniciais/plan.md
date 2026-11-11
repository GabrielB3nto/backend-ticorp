# Plano — Spec 003: Dados iniciais

**Status:** proposta, aguardando aprovação e decisões técnicas. Deriva de spec.md.

## Restrições

ADR-004 mantém entry point/health check sem banco. ADR-001/002 estão vazios; ADR-003 trata de pontos. Não usar esses documentos como autorização para novas dependências ou modelagem. Conforme rules/restrictions 1.md, o time registra ADRs antes do código; agente só propõe alternativas em ../../plan.md.

## Ordem

1. Aprovar spec/plano e resolver ferramenta de imagens, isolamento efetivo do verificador e persistência/Auth com ADRs do time (CA-05/06/08).
2. Criar verificador e skill antes do seed; preservar contexto limpo, restrições reais e tabelas comparáveis (CA-02/03/06/07/08).
3. Preparar manifesto e dados exatos sem dependência externa não autorizada (CA-01/02).
4. Obter candidatos pela API Pixabay com cache 24h e verificar arquivo já em 800×600, sem sharp/sips ou qualquer transformação. Filtros min_width/min_height não garantem tamanho exato; recusar arquivos divergentes e registrar equipamentos sem foto elegível. Tratar erros sem expor chave; revisão humana bloqueia imagens reprovadas (CA-02/03/07).
5. Preparar seed idempotente para ambiente local e execução humana no deploy; preservar registros já emprestados e contas existentes (CA-01/04/05/06).
6. Testar localmente, executar verificador e corrigir no agente principal; registrar evidências reais (CA-01 a CA-08).
7. Gabriel valida licença/uso, executa upload/seed remoto e fornece evidências de URLs/login/zero empréstimos; verificador reavalia sem escrever no deploy.

## Cobertura dos projetos

Backend mantém preparo, manifesto e seed. Frontend não recebe chave Pixabay ou credencial administrativa; a integração do catálogo e crédito fica na 004. Referenciar esta spec no frontend, sem duplicar contrato divergente.

## Validação

Tests existentes do backend e build do frontend para regressão. Testes da spec devem provar dados exatos, duas execuções, estado emprestado preservado, imagem repetida/reprovada, tamanho real e falhas externas. Produção não observada fica não verificada. Nenhuma spec pronta só porque um script terminou sem erro.
