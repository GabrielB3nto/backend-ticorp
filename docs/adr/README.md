# Decisões de arquitetura

Índice das decisões deste projeto. Leia este arquivo antes de propor
mudanças estruturais. Abra o ADR completo só quando precisar do
raciocínio por trás da decisão.

| #   | Decisão                             | Status |
|-----|-------------------------------------|--------|
| 001 | Domínio isolado de infra            | aceito |
| 002 | Lançamentos imutáveis vs. saldo     | aceito |
| 003 | Expiração de pontos em 12 meses     | aceito |
| 004 | Entry point e health check HTTP      | aceito |
| 005 | [Login tradicional](005-login-tradicional.md) | aceito; fluxo validado via conexão administrativa, role restrita pendente |
| 006 | [Leitura de catálogo e próprios empréstimos](006-leitura-catalogo-emprestimos.md) | aceito; PostgreSQL remoto validado via conexão administrativa |
| 007 | [Solicitação transacional](007-solicitacao-transacional.md) | aceito; PostgreSQL remoto validado via conexão administrativa |
