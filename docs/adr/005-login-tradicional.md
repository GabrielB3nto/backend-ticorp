# ADR-005 — Login tradicional no backend

**Status:** aceito. Migrations 001/002/003 aplicadas sob aprovações explícitas. Os helpers e o fluxo atual foram exercitados contra PostgreSQL remoto pela conexão administrativa; a autenticação da role dedicada continua pendente porque sua senha não foi provisionada.
**Data:** 2026-11-11

## Contexto e autoridade

A aprovação original permitiu registrar este ADR e implementar somente login. Substitui a direção temporária Supabase Auth/auth_user_id, ainda não aplicada; não altera Storage nem ADRs históricos. Uma autorização posterior e específica permitiu criar a migration versionada complementar sem CLI e aplicá-la em transação controlada; não autorizou seed, conta do professor, deploy ou reset remoto.

## Decisão

POST /api/login recebe email/password e retorna user {id,email}, expires_in, access_token e token_type bearer. GET /api/me retorna {user}; POST /api/logout revoga a sessão e retorna 204, inclusive para token desconhecido. Token ausente/inválido/expirado e usuário inativo não autenticam.

Senhas usam PBKDF2-HMAC-SHA256, 600000 iterações, salt aleatório de 16 bytes e compare_digest. Formato pbkdf2_sha256$600000$base64(salt)$base64(hash32). Sem senha em seed/código/log; conta sem senha_hash não entra. Hash inválido não causa erro nem trabalho descontrolado. Verificação fictícia equivalente reduz diferença de tempo para conta ausente/inativa.

Sessão opaca aleatória de 32 bytes, somente SHA-256 hexadecimal persistido. Validade técnica inicial de 3600 segundos, sem refresh; relógio UTC injetável em testes. /me verifica expiração e ativo no banco em cada chamada. Repositório coeso injetável para testes, implementação psycopg síncrona por operação, SQL parametrizado e transações. DATABASE_URL somente no servidor; conexão 5s, statement_timeout 5s, lock_timeout 1s; nenhuma conexão no import/health. Erros de infraestrutura viram 503 genérico, validação 422 sem payload nem password em detalhes. Respostas de autenticação não são cacheadas.

Dependência aprovada: psycopg[binary]==3.3.7, incluindo psycopg-binary==3.3.7. PyPI público informa release não retirada em 2026-11-03 (mais de 7 dias na consulta de 2026-11-11); 3.3.8 ainda abaixo de 7 dias. Extra binary necessário porque libpq local não foi encontrada; evita instalar compilador/libpq/pool. https://pypi.org/pypi/psycopg/json e https://pypi.org/pypi/psycopg-binary/3.3.7/json. Nenhum outro pacote novo autorizado.

CORS lê CORS_ORIGINS já existente, lista exata de origens HTTP(S) sem caminho/wildcard. Padrão apenas http://localhost:5173. Produção precisa de origem real configurada pelo usuário; nenhuma origem inventada. Credenciais via Authorization bearer, não cookies.

## Schema aprovado e aplicação posterior

Adicionar senha_hash text nullable em usuarios: linhas existentes permanecem sem senha e não autenticam; provisionamento seguro separado, sem reset automático. Sessões: token_hash varchar(64) PK, usuario_id FK usuarios(id), criado_em timestamptz default now(), expira_em timestamptz com check expira_em > criado_em; índice usuario_id; RLS, revoke PUBLIC/anon/authenticated e policy deny anon/authenticated. Nome técnico aprovado: sessoes_login. Acesso do servidor exige papel apropriado e privilégios mínimos, não chave no frontend.

`backend/migrations/002_auth_sessions_and_rls.sql` implementa esse delta sem editar `001_emprestai_schema.sql`. Como a CLI Supabase não estava disponível, Gabriel autorizou explicitamente a exceção: criar o arquivo versionado manualmente e aplicar 001+002 atomicamente, com TLS `verify-full` e precondição de schema remoto vazio. A transação confirmou ambas as migrations. A inspeção posterior confirmou as seis tabelas com RLS, 12 policies negadas, grants de tabela removidos para `anon`/`authenticated`, triggers e categorias.

Não existiam `supabase_migrations.schema_migrations` nem `public.schema_migrations`; a aplicação não ficou registrada no histórico padrão da CLI. Não foi feito `supabase db reset` local, pois a CLI não está disponível. O schema remoto foi validado por endpoints reais usando fixtures sintéticas, posteriormente removidas.

O papel observado para conexão e testes é `postgres`, com privilégios elevados e `BYPASSRLS`. As policies negam acesso direto a `anon`/`authenticated`, mas isso não comprova isolamento para a conexão da aplicação. A role dedicada `emprestai_runtime` foi criada sem senha, sem `BYPASSRLS`, `CREATE` ou `UPDATE`; os grants e policies foram verificados por catálogo.

`backend/migrations/003_runtime_role.sql` foi aplicada após aprovação específica. O backend usa o helper `app_private.lock_login_user`; os fluxos atuais foram repetidos no PostgreSQL pela conexão administrativa e passaram. A role runtime ainda não autenticou uma conexão: sua senha precisa ser provisionada fora do repositório, e o teste real sob essa role permanece pendente.

## Alternativas e limites

Supabase Auth foi substituído por escolha humana; JWT não permite revogação imediata sem estado; sessão em memória não serve em serverless. Advisory try-lock transacional por email normalizado limita tentativas simultâneas na mesma conta e retorna 429 sem fila, mas NÃO limita tentativas sequenciais nem ataque distribuído a várias contas. Não tratar como rate limit completo ou liberar produção como segura.

Proteção persistente exige aprovação adicional: proposta de tabela de tentativas por chave de conta, janela, contador e bloqueado_ate, com RLS/policy explícita, atualização atômica sob lock e expiração; política de limites e proteção por origem precisam de decisão humana. Nenhum DDL extra ou contador process-local introduzido nesta tarefa.
