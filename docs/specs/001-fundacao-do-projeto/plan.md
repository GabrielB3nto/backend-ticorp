# Plano — Spec 001: Fundação do projeto

1. Confirmar que PRD, plano, ADRs e `AGENTS.md` já descrevem o contexto
   mínimo da implementação.
2. Completar os pacotes vazios de `aplicacao`, `infra` e `api`, além do pacote
   raiz `pontos`, sem adicionar dependências nem comportamento.
3. Registrar esta spec e verificar os critérios CA-01 a CA-05.

## Verificação

```powershell
$env:PYTHONPATH = 'src'
python -c "import pontos, pontos.aplicacao, pontos.infra, pontos.api"
python -m pytest -q  # depois de instalar requirements.txt
```
