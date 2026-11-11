# EMPREST.AI — Backend

API REST em FastAPI para autenticação, catálogo, empréstimos próprios e
solicitação transacional. O histórico do Programa de Pontos permanece no
repositório, mas não representa o fluxo atual do EMPREST.AI.

## Executar localmente

Use Python e as dependências já disponíveis no ambiente. Não instale pacotes
sem aprovação. No PowerShell, a partir desta pasta:

```powershell
$env:DATABASE_URL = "postgresql://<usuario>:<senha>@<host>:5432/<database>"
$env:PGSSLMODE = "verify-full"
$env:PGSSLROOTCERT = "C:\caminho\para\o\CA-oficial.crt"
$env:CORS_ORIGINS = "http://localhost:5173"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Mantenha a URL e a senha fora do Git, do frontend e do chat. Use o CA oficial
com `sslmode=verify-full`; não desative a verificação TLS. O endpoint
`http://127.0.0.1:8000/health` não acessa o banco. As rotas autenticadas
precisam de PostgreSQL e das migrations aplicadas.

## Testes

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m pytest -p no:cacheprovider -q
```

Os testes que usam repositórios falsos são simulados; eles não comprovam
permissões/RLS ou integração PostgreSQL. As evidências de PostgreSQL remoto
estão em `docs/specs/004-solicitar-emprestimo/tasks.md` e distinguem a conexão
administrativa da role `emprestai_runtime`.

## Estado e documentação

- `docs/PRD.md`: contrato de negócio e critérios gerais.
- `docs/adr/`: decisões de autenticação, leituras e transação.
- `docs/specs/003-dados-iniciais/`: seed, imagens e conta obrigatória ainda
  pendentes de implementação e evidência.
- `docs/specs/004-solicitar-emprestimo/tasks.md`: implementação, testes e
  bloqueios atuais.
- `migrations/001_emprestai_schema.sql` a `003_runtime_role.sql`: schema e
  permissões. A migration 003 já foi aplicada remotamente; o replay limpo
  local e a conexão da API como `emprestai_runtime` continuam pendentes.

Não execute seed, upload, reset remoto, deploy ou operações na conta do
professor sem aprovação específica e credenciais fornecidas em canal seguro.
