# ADR-007 — Solicitação transacional de empréstimo

**Status:** aceito no recorte específico aprovado por Gabriel. Migrations 001/002/003 foram aplicadas; a versão atual passou pelos fluxos PostgreSQL através da conexão administrativa. A autenticação/execução com a role dedicada segue pendente.

## Autoridade e escopo

Aprovação original permite registrar este contrato e implementar UMA tarefa backend reutilizando schema, psycopg e conexão do ADR-005, leituras do ADR-006 e prazo existente. Naquele recorte, não autorizava DDL, migration, banco remoto, permissões, frontend, seed ou deploy. Autorizações posteriores e separadas permitiram aplicar as migrations 002 e 003. ADRs históricos preservados. Não há nova ambiguidade de negócio neste recorte.

## Contrato HTTP

POST /api/emprestimos recebe somente {equipamento_id: UUID}; campos extras, inclusive usuario_id, são proibidos (422 sanitizado). Authorization Bearer usa sessão opaca existente; titular vem exclusivamente do banco. Retorna 201 {emprestimo:{id,retirado_em,previsto_para,equipamento:{id,nome,patrimonio,categoria}}}, no mesmo formato das leituras. Datas persistidas, retirada com offset e vencimento como data ISO. Patrimônio nullable é preservado.

Token ausente/inválido/expirado/revogado ou usuário inativo: 401 genérico existente. Equipamento ausente, manutenção/inativo ou já aberto: 409, reason equipamento_indisponivel; 3 abertos: 409, reason limite_emprestimos; atraso: 403, reason emprestimo_atrasado. Respostas de recusa incluem detail legível e reason estável; prioridade disponibilidade, limite, atraso. Infraestrutura: 503 'Solicitação indisponível.', sem detalhes SQL/driver. Todas as respostas usam Cache-Control: no-store. Não há retry automático nem chave de idempotência; perda da resposta exige reconciliação pelas leituras do ADR-006, conforme PRD.

## Transação e composição

Repositório em src/emprestimos.py composto com PostgresAuthRepository.connection, lazy e sem nova configuração. Uma transação READ COMMITTED explícita: localizar sessão/titular; advisory xact lock hashtextextended(equipamento UUID canônico em texto, 0), depois hashtextextended(usuario UUID canônico em texto, 0); chamar `app_private.lock_equipment_for_loan`, `lock_user_for_loan` e `lock_session_for_loan`, nessa ordem. Esses helpers encapsulam `FOR UPDATE`/`FOR SHARE` como `SECURITY DEFINER`, para que a role de runtime não receba UPDATE direto. Login usa `app_private.lock_login_user` para preservar o bloqueio `FOR SHARE` durante verificação da senha. Os helpers estão definidos na migration 003, já aplicada. Relógio UTC aware do servidor é consultado após aquisição dos locks, não do cliente. Locks da sessão e usuário permanecem até commit, impedindo revogação/desativação intercalada com criação. Sessão inválida desfaz a transação.

Depois dos locks, SELECTs separados em READ COMMITTED reavaliam empréstimo aberto do equipamento e todos os abertos do titular (incluindo os que venceram hoje). Validar disponibilidade, quantidade < 3 e ausência de previsto_para estritamente anterior à data local America/Sao_Paulo. Calcular 14 dias de segunda a sexta pela função existente. Um único INSERT, com retirado_em explícito, retorna id e datas persistidos. Disponibilidade deriva do empréstimo aberto: nenhuma escrita no status do equipamento. Commit acontece antes de devolver sucesso; exceções desfazem tudo.

O trigger `validar_novo_emprestimo` da migration 001 continua ativo, com a mesma ordem equipamento advisory → usuário advisory → equipamento FOR UPDATE, reentrante na transação. A migration 003 o configura como `SECURITY DEFINER` com `search_path` fixo, para validar o INSERT sem ampliar UPDATE da role runtime. A aplicação adquire os advisory locks em statements anteriores ao snapshot de validação/INSERT; dois itens do mesmo titular serializam no advisory do usuário antes da contagem. O índice `ux_emprestimos_equipamento_ativo` permanece defesa final: somente UniqueViolation com esse constraint_name vira 409 equipamento_indisponivel; outras violações e erros ficam 503. Não classificar erros por mensagem textual.

## Revisão de outros caminhos e limites

Migration 001 também contém trigger de status (consulta abertos durante UPDATE do equipamento) e atualização de timestamps; nenhum adquire advisory em ordem inversa. Código atual não oferece outras escritas de empréstimo/status. Login adquire advisory por email com seed 314159 e usuário FOR SHARE; /logout apaga sessão; leituras não adquirem locks de escrita. Nenhum desses caminhos exige lock de equipamento depois de usuário/sessão. Futuras operações devem revisar essa ordem e não adquirir row lock de equipamento antes de advisory.

Seed 0 e namespace compartilhado entre UUID de equipamento/usuário são mantidos por compatibilidade com trigger: colisões de hash ou IDs cruzados podem causar contenção/deadlock; timeouts existentes/erros de deadlock retornam 503 com rollback, não sucesso nem retry. Não há promessa de ausência absoluta de deadlocks. Escritas SQL externas não cooperativas e alterações de status concorrentes precisam de validação real; este recorte não certifica os triggers globais nem RLS. Não corrigir SQL histórico ou schema de sessões implicitamente.

## Alternativas e validação

Bloqueio só na UI não protege integridade; contagem sem lock por usuário excede limite; mudar namespace/ordem só na aplicação conflita com trigger; serializable exigiria política de retry não aprovada; mudar schema/idempotência fica fora do recorte. Manter READ COMMITTED com consultas após locks é a alteração mínima compatível.

pytest completo e fakes para contrato, autenticação, SQL parametrizado, ordem de locks, horário após espera, recusas sem INSERT, sucesso seguido de leitura e rollback/commit falhando. Domínio testado diretamente sem banco.

Validação posterior: migrations 001 e 002 foram aplicadas atomicamente e 003 em transação separada, sob aprovações explícitas e TLS `verify-full`. A versão anterior e o código atual passaram login, /me, catálogo, empréstimos próprios, concorrência no mesmo item, atraso, limite, manutenção e logout; com dois empréstimos abertos, dois POSTs simultâneos em itens distintos resultaram em um 201 e um 409 `limite_emprestimos`. A validação atual executou pela conexão `postgres` privilegiada, exercitando as funções `SECURITY DEFINER` e o trigger, mas não aplicou as permissões RLS da role runtime. Uma tentativa read-only de `SET ROLE emprestai_runtime` foi negada por falta de membership; nenhum grant temporário foi feito. A role foi criada sem senha, portanto o teste com `current_user=emprestai_runtime` aguarda provisionamento seguro. As policies `runtime_*` permitem acesso do servidor às linhas das tabelas necessárias; segregação por titular continua sendo feita pela camada da API, não por policy por usuário final. Reset local limpo e produção seguem pendentes.
