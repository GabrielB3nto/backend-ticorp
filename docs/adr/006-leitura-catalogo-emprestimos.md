# ADR-006 — Leitura autenticada de catálogo e próprios empréstimos

**Status:** aceito por aprovação específica de Gabriel para o recorte T5a. O recorte original usou fakes; em validação posterior, as leituras passaram contra PostgreSQL remoto pela conexão administrativa. A role dedicada ainda aguarda teste autenticado.
**Data:** 2026-11-11

## Autoridade e escopo

Gabriel aprovou explicitamente registrar este ADR e implementar somente as duas consultas abaixo. A exceção à restrição de escrita de ADR não autoriza outros ADRs, POST de empréstimos, frontend, imagens, seed, migrations, novas bibliotecas ou conexão com banco nesta tarefa. A Spec 004 integral continua proposta e não verificada.

## Contrato

- GET /api/equipamentos, autenticado, retorna {equipamentos:[{id,nome,patrimonio,categoria,status}]}. Categoria é o nome; IDs são strings; patrimônio nullable mantém null. Retorna todos os registros existentes, inclusive INATIVO, sem inventar os 12 itens ou imagem. MANUTENCAO e INATIVO são preservados mesmo com empréstimo aberto. DISPONIVEL com empréstimo cujo devolvido_em é null é apresentado como EMPRESTADO; sem aberto fica DISPONIVEL. Nenhuma escrita ou reparo de status.
- GET /api/emprestimos/meus, autenticado, retorna {emprestimos:[{id,retirado_em,previsto_para,equipamento:{id,nome,patrimonio,categoria}}]}. Apenas abertos (devolvido_em null) do id retornado por AuthService.me, nunca titular fornecido pelo cliente. retirado_em é ISO 8601 com offset, previsto_para é data ISO sem horário, ambos persistidos, sem recalcular prazo. Lista vazia é resultado válido.
- Token ausente, inválido, expirado/revogado ou usuário inativo: 401 genérico existente. Falhas de autenticação usam 503 existente; falhas de leitura usam 503 'Consulta indisponível.', sem SQL, credenciais ou detalhes do driver. Todas as respostas destes endpoints usam Cache-Control: no-store.

## Composição e SQL

Repositório de leitura separado em src/consultas.py, recebendo a factory PostgresAuthRepository.connection por composição. Mantém conexão lazy, timeouts e tradução de falhas existentes, sem herança ou segunda configuração. FastAPI injeta autenticação e repositório; valida AuthService.me antes de consultar. SELECTs com nomes public qualificados, JOIN de categoria e EXISTS para aberto no catálogo; filtro de titular parametrizado na consulta de empréstimos. Ordem estável por patrimônio/id no catálogo e previsto_para/id nos empréstimos. Não assume que o seed foi aplicado.

## Alternativas e limites

Catálogo fixo ou imagens provisórias foram recusados: escondem falha/dados ausentes. Status persistido isolado não indica empréstimo aberto; JOIN direto com empréstimos pode duplicar itens, por isso EXISTS. Ocultar INATIVO mudaria o contrato sem decisão: incluí-lo não autoriza solicitação. Acrescentar leituras ao repositório de login misturaria responsabilidades; composição reutiliza conexão sem novo pacote. Não há garantia de snapshot entre chamadas separadas nem autorização de escrita.

## Validação

Pytest existente e testes com conexões falsas para SQL parametrizado, filtro de titular/abertos, classificação, formato/datas, vazio, credenciais e erros sanitizados. Import/compilação sem conectar; diff sem normalizar CRLF. Em validação posterior, as leituras passaram pela API com fixtures sintéticas no PostgreSQL remoto e os registros de teste foram removidos. Essa execução usou `postgres`/`BYPASSRLS`; não comprova RLS sob `emprestai_runtime` nem produção. ADR-004/005 preservados; divergência pré-existente sessoes/sessoes_login não é corrigida por este recorte.
