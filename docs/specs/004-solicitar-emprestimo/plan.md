# Plano — Spec 004: Solicitar empréstimo

**Status atual:** T3/login, T5a/leitura, T6a/solicitação e recortes frontend foram aprovados e implementados. Migrations 001–003 foram aplicadas; a versão atual passou por testes PostgreSQL remotos através da conexão administrativa, mas a role restrita ainda não autenticou. Seed/imagens, reset local limpo, verificador independente e produção seguem pendentes. Deriva de spec.md.

As restrições abaixo descrevem os limites das aprovações originais. Aprovações posteriores e específicas autorizaram a migration 002, a migration 003, os testes remotos com fixtures sintéticas e a integração do frontend; elas não autorizam seed, conta do professor, reset remoto, deploy ou publicação.

## Recorte aprovado T6a

1. Registrar ADR-007, contrato e tarefa estreita antes de código (CA-02/03/04/05/06/07). Aprovação específica dispensa DDL neste recorte: reutilizar schema/trigger existentes, sem declarar T4 integral concluída.
2. Implementar POST em main e repositório composto com conexão existente; sessão/titular revalidados na transação READ COMMITTED, ordem de locks idêntica ao trigger, SELECTs pós-locks, regras sem banco e prazo existente; um INSERT, sem escrita de status.
3. Testar contrato, fakes de transação, recusas sem INSERT, relógio após locks, erro/rollback, unique conhecido, sucesso seguido das leituras e regressões. Executar pytest global existente com PYTHONPATH do ambiente disponível, AST/import e diff --check com cr-at-eol.
4. Parar após esta tarefa. Sem DDL, migration, instalação, permissões ou acesso remoto. Descoberta de PostgreSQL cabe à sessão principal; concorrência/SQL/RLS reais permanecem não verificados, sem concluir CA-06 ou spec integral.

## Recorte aprovado T5a

1. Registrar ADR-006 e contrato de leitura nesta spec antes do código (CA-01/07).
2. Implementar apenas GET catálogo e próprios abertos; repositório de leitura por composição com PostgresAuthRepository.connection e DI, identidade AuthService.me, SQL parametrizado; preservar health e login.
3. Testar classificação, datas, titularidade/abertos, vazio, token ausente/inválido/expirado/inativo, erros e no-store usando conexões falsas. Executar pytest completo existente, import/compilação sem conexão e git diff --check com cr-at-eol.
4. Parar após o recorte. Não acessar banco, criar schema/dependências, POST, frontend, seed ou imagens. PostgreSQL/RLS/dados reais continuam não validados; T5 integral e Spec 004 não concluídas.

## Recorte aprovado T3

1. Registrar ADR-005 e índice antes do código; substituir apenas direção temporária de autenticação.
2. Implementar hashing, repositório injetável/psycopg, login/me/logout e CORS exato no entry point preservando health sem banco.
3. Testar com fake o ciclo, erros, null/inativo/expiração, token/revogação, validação sem vazamento e regressões; compilar/importar após última edição. psycopg[binary]==3.3.7; testes disponíveis sem instalar extras.
4. CLI ausente impede gerar migration; PostgreSQL local ausente impede integração e RLS. Não contornar com SQL manual/remoto/reset. Registrar bloqueio e parar após esta tarefa. Advisory try-lock não substitui rate limit persistente; apresentar proposta adicional sem implementar schema.

ADR-005 é a aprovação específica de arquitetura/dependência de login; não autoriza transação de empréstimos nem demais tarefas.

## Restrições técnicas

ADR-004 mantém entry point e health check sem banco. ADR-001/002 vazios e ADR-003 de pontos não aprovam domínio de empréstimos. O time precisa registrar contratos Auth/REST/transação e aprovar migration/dependências antes do código, conforme rules/restrictions 1.md. Alternativas estão em ../../plan.md, não são ADRs aprovados.

## Ordem e integração

1. Aprovar spec/plano e contratos de Auth/API/persistência com o time; confirmar dados da 003 e verificador (CA-01/03/06/07/09).
2. Implementar/testar prazo com relógio controlado e biblioteca padrão, sem extrapolar decisão de feriados (CA-05).
3. Implementar autenticação no backend; não confiar em identidade enviada pelo cliente. Frontend usa login real e não recebe credenciais administrativas (CA-01/07).
4. Preparar migration/operacão transacional local aprovada para proteção de item e usuário; criação/indisponibilidade, limite e atraso na mesma transação (CA-02/03/04/06).
5. API oferece catálogo, solicitação e próprios empréstimos; validar erros sem divulgar dados de outro usuário (CA-01/02/04/07).
6. Frontend integra catálogo da 003 com crédito Pixabay e solicitação; exibe falhas/restrições reais e meus empréstimos (CA-01/02/04/07/08).
7. Rodar regressões, testes de fronteira/erros, concorrência em PostgreSQL local e verificador limpo por critério. Principal corrige; verificador não edita (CA-01 a CA-09).
8. Usuário valida produção com conta própria; preservar professor. Documentar evidências reais no ENTREGA.md dos dois projetos (CA-09).

## Validação

Backend: pytest existente mais testes de domínio/API/concorrência. Frontend: build existente e testes de interação aprovados pelo time, sem instalar framework de teste automaticamente. Falha de API, token inválido, manutenção, limite, atraso e rollback obrigatórios. Mock não prova atomicidade real; sem PostgreSQL local, CA-06 fica não verificado.

O catálogo integrado usa fotos no Storage, não URLs Pixabay permanentes. Apenas o usuário grava remotamente. Não ampliar para devolução, Operações ou e-mail.
