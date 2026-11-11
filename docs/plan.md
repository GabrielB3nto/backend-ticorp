# Proposta de plano — prática EMPREST.AI

**Status:** direção e plano aprovados por Gabriel. O fluxo básico de login,
catálogo, empréstimos próprios e solicitação foi implementado. As migrations
001–003 foram aplicadas ao Supabase sob aprovações específicas; a API atual foi
validada pela conexão administrativa, mas a role restrita ainda não autenticou.
Seed/imagens, verificador independente, reset local limpo e validação de
produção continuam pendentes.

## Regras confirmadas

Limite 3; TI-0004, TI-0007 e TI-0010 em manutenção; 14 dias de segunda a sexta,
excluindo dia inicial, sem feriados, America/Sao_Paulo; atraso no dia seguinte
à data de vencimento. Referência de negócio: docs/PRD.md.

## Decisões técnicas e situação atual

| Tema | Alternativas | Decisão/implementação | Situação e pendências |
|---|---|---|---|
| Auth e REST | Supabase Auth (direção anterior não aplicada); login tradicional no backend | Login tradicional implementado conforme ADR-005 e Spec 004; frontend chama API REST e servidor valida sessão opaca e titularidade | Migrations 001–003 aplicadas. API atual exercitada contra PostgreSQL remoto usando `postgres`; role `emprestai_runtime` sem senha ainda não foi autenticada. CORS e produção seguem pendentes |
| Concorrência | Bloqueios só na interface; transação no PostgreSQL | Operação transacional protege equipamento e usuário, verifica disponibilidade, atraso e limite 3 antes de inserir | Código atual passou testes PostgreSQL de concorrência pela conexão administrativa. Reset local limpo e validação sob role dedicada ainda pendentes |
| Imagens | Redimensionar; selecionar fotos já no tamanho | Gabriel escolheu buscar arquivos já em 800×600, sem sharp nem sips; medir bytes do arquivo e revisar visualmente | API não tem filtro exato; sem candidato adequado, requisito fica pendente, sem transformar ou trocar origem |
| Verificador | Prompt somente leitura; isolamento real do processo | Checkout somente leitura, ambiente sem segredos, sem rede e ferramentas de publicação; execução local isolada e relatório por CA | Confirmar harness disponível e demonstrar impossibilidade de escrita; instrução textual sozinha não basta |
| Histórico | Apagar documentos de pontos; preservar e separar | Preservar conteúdo existente como histórico e usar novo PRD como contrato | Não remover código/ADRs antigos nem pressupor ADR-001/002 preenchidos |

Conforme rules/restrictions 1.md, decisões estruturais exigem ADR do time antes
do código. Esta tabela resume o estado atual e não substitui ADR aprovado.
ADR-004 rege o entry point/health check. ADR-003 é de pontos e não define prazos.

## Próximas etapas para conclusão

1. Provisionar a senha de `emprestai_runtime` em canal seguro, sem enviá-la no
   chat/repositório; atualizar o DSN local e validar a API com `current_user` igual
   à role dedicada. Nenhum grant temporário deve ser criado.
2. Executar reset local limpo e replay de todas as migrations no ambiente isolado
   aprovado. A CLI não está disponível; não instalar ferramentas sem autorização.
   Reconciliar também a ausência do histórico padrão de migrations antes de novas.
3. Concluir dados iniciais: 12 equipamentos, imagens 800×600 com licença/crédito,
   revisão visual e conta do professor. Imagens estão adiadas; usuário executa
   gravações em produção e nenhuma conta existente pode ser usada como fixture.
4. Confirmar CORS/origem real e validar o frontend com API integrada. Não alterar
   Vercel, publicar ou fazer deploy sem autorização; produção ainda não foi testada.
5. Implementar e executar verificador independente sob isolamento demonstrável,
   com evidências por CA e sem escrita remota; instrução textual não basta.
6. Repetir checks após a última correção, registrar limitações de lint e risco de
   rate limit persistente de login, e então produzir ENTREGA.md nos dois projetos.
   O usuário valida produção; publicações exigem autorização específica.

Uma tarefa de código por vez, seguida dos checks do projeto. As specs seguintes
definem critérios globais; aprovações específicas documentadas nos ADRs e tarefas
autorizaram recortes já implementados, mas não concluem nem aprovam integralmente
as specs.

## Spec proposta — dados iniciais

Registrada como proposta em specs/003-dados-iniciais/{spec,plan,tasks}.md.
002-cadastro-equipamento preservada, sem reutilizar seu número.

- D-CA01: exatamente 12 patrimônios distintos com os dados do enunciado e
  TI-0004/TI-0007/TI-0010 em manutenção; demais 9 disponíveis no primeiro seed.
- D-CA02: 12 fotos Pixabay distintas, 800×600 verificadas, revisão visual aprovada
  e proveniência/licença completas; público acessa sem login após upload humano.
- D-CA03: reexecução não duplica nem redefine item emprestado ou empréstimos.
- D-CA04: professor entra com credenciais fornecidas pelo usuário e tem zero
  empréstimos; scripts não contêm senha e não redefinem conta existente sem revisão.
- D-CA05: apenas usuário escreve no deploy; preparo local não possui upload remoto.
- D-CA06: verificador independente apresenta evidência por critério; resultado
  de produção não observado é marcado não verificado, nunca aprovado por inferência.

Fora de escopo: empréstimos no seed, catálogo nesta spec e cadastro/importação UI.

## Spec proposta — solicitar empréstimo

Registrada como proposta em specs/004-solicitar-emprestimo/{spec,plan,tasks}.md.

- E-CA01: login real; catálogo exibe 12 itens com fotos, dados e crédito Pixabay.
- E-CA02: só disponível pode ser solicitado; manutenção/emprestado recusados.
- E-CA03: solicitação cria um empréstimo imediato e indisponibiliza item
  atomicamente; erro no meio da operação não deixa estado parcial.
- E-CA04: usuário com 3 abertos ou atraso recebe recusa com motivo, sem criação.
- E-CA05: prazo segue PRD; exemplos com relógio controlado cobrem sexta-feira,
  fim de semana, mês/ano, vencimento e primeiro dia de atraso no fuso aprovado.
- E-CA06: concorrência no mesmo equipamento cria apenas um empréstimo; pedidos
  a itens distintos pelo usuário com 2 abertos não elevam total acima de 3.
- E-CA07: meus empréstimos mostra apenas os próprios abertos e datas previstas;
  token inválido e tentativa de consultar/solicitar como outro usuário são recusados.
- E-CA08: verificador reavalia backend e frontend após correções; evidências
  locais separadas de produção; conta do professor não usada em testes de pedido.

Fora de escopo: devolução, Operações, reserva futura, renovação e e-mail.

## Validação documental

Regras humanas explícitas, critérios observáveis, ordem de dependências e limites
de produção registrados. Este plano não certifica revisão de imagens, verificação
independente nem validação de produção.

---

# Plano histórico — Programa de Pontos (não autoriza EMPREST.AI)

**Status:** aprovado

**Data:** 2026-08-17

**MVP:** Etapas 0–4

## Arquitetura

- **Domínio isolado de infra** (ADR-001): camadas domínio, aplicação, infra, API.
- **Lançamentos vs. saldo** (ADR-002): imutabilidade de lançamentos, saldo calculado.
- **Expiração 12 meses** (ADR-003): lazy evaluation no `calcular_saldo`.

## Etapas

### Etapa 0: Setup de pasta e índice de decisões
- Criar `src/pontos/{dominio,aplicacao,infra,api}/`
- Criar `tests/dominio/`
- Indexar ADR-001 e ADR-002 em `docs/adr/README.md`
- Adicionar seção Arquitetura em `AGENTS.md`

### Etapa 1: Modelo de domínio (Cliente, Lançamento, Saldo)
- Classe `Cliente` (id, nome)
- Classe `Lançamento` (id, cliente_id, tipo, pontos, data_criacao, expira_em)
- Valor-objeto `Saldo` (pontos_vigentes, histórico de lotes)
- Testes: inserção, expiração lazy, cálculo de saldo

### Etapa 2: Regras de negócio (conversão R$ → pontos)
- Função `converter_reais_para_pontos(valor: float) -> int`
  - Arredonda para baixo (`floor`) até Marketing definir arredondamento final
- Função `calcular_saldo(cliente_id)` → `Saldo`
  - Filtra lançamentos expirados, soma os vigentes
- Testes: conversão com valores típicos (R$ 0,99, R$ 49,99, R$ 100,00)

### Etapa 3: Repositório e persistência (banco em memória, depois SQLite)
- Interface `RepositorioCliente`
- Implementação em memória para testes
- Implementação SQLite com schema:
  - `clientes (id, nome)`
  - `lancamentos (id, cliente_id, tipo, pontos, data_criacao, expira_em)`
- Testes: CRUD, múltiplos clientes

### Etapa 4: API HTTP (GET /clientes/{id}/saldo, POST /compras)
- Framework: Flask (Python) ou FastAPI
- Endpoints:
  - `GET /clientes/{id}/saldo` → JSON com pontos_vigentes
  - `POST /compras` → JSON (cliente_id, valor_reais) → registra lançamento, retorna novo saldo
- Remover banner de demo em `static/index.html`
- Testes: integração com repositório SQLite

### Etapa 5: Resgate básico (FIFO por expira_em)
- Endpoint `POST /resgates` → (cliente_id, pontos) → deduz saldo em ordem FIFO
- ADR-004: protocolo de resgate e ambiguidades
- Testes: múltiplos lotes, expiração durante resgate

### Etapa 6: Devoluções (reversa de compra)
- Tipo de lançamento `DEVOLUCAO`
- Endpoint `POST /devolucoes` → reverte lançamento de compra
- Testes: lançamento reverso, saldo correto

### Etapa 7: Resgate com preferência de saldo expirado
- Opção de priorizar pontos próximos de expiração
- Endpoint `POST /resgates/prioridade-expiracao`
- Testes: seleção de lotes

### Etapa 8: Job noturno de materialização de EXPIRACAO
- Se Financeiro exigir lançamentos `EXPIRACAO` imutáveis
- Scheduler asyncio ou APScheduler
- Revisitar necessidade com Financeiro

### Etapa 9: Auditoria e relatórios
- Tabela de auditoria de operações
- Endpoints de relatório (extrato do cliente, auditoria global)
- Dashboard de métricas (pontos em circulação, taxa de resgate)

---

**Decisões pendentes:**
- ADR-004: protocolo de resgate e ordem FIFO (Etapa 5)
- Arredondamento: `floor()` é provisório até Marketing definir (Etapa 2)
- Materialização de EXPIRACAO: agenda noturna só se Financeiro exigir (Etapa 8)
