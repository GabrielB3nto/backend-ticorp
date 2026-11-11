# Spec 004 — Solicitar empréstimo

Colaborador autenticado consulta catálogo, solicita item disponível e vê seus empréstimos abertos. Backend garante as regras; frontend mostra resultados reais, sem identidade fixa.

**Status:** proposta para revisão; não implementada nem verificada.
**Fontes:** ../../PRD.md, spec 003, ../../../rules/ e ../../adr/.

## Decisões e conflitos

- Gabriel escolheu limite **3**, em vez dos 5 do briefing. A autoridade é a decisão humana registrada no PRD, não a implementação existente.
- Enunciado de referência: ../../../../pratica-sdd-subagentes.html, seção #spec003; dados exatos em ../003-dados-iniciais/spec.md.
- TI-0004/TI-0007/TI-0010 permanecem em manutenção; 9 itens inicialmente disponíveis.
- Prazo aprovado: 14 dias de segunda a sexta, excluindo dia inicial, sem descontar feriados; data calculada em America/Sao_Paulo. Atraso começa no dia seguinte à data prevista nesse fuso.
- Solicitação imediata, sem aprovação/fila, conforme decisão declarada para a turma no briefing.
- Pixabay substitui Pexels por orientação do professor relatada por Gabriel; catálogo mantém "Fotos: Pixabay" com link https://pixabay.com/pt/ como requisito de origem do projeto.
- A identidade fixa da spec 002 pertence ao escopo administrativo anterior; não atende à autenticação desta spec. Preservar a 002 e não removê-la automaticamente.

## Critérios de aceite

| ID | Resultado observável | Evidência exigida |
|---|---|---|
| CA-01 | Login real; catálogo mostra os 12 itens da 003 com imagem, nome, categoria, situação e crédito Pixabay | Teste de integração back/front com conta de teste e imagens aprovadas; falha de carregamento não simula catálogo real |
| CA-02 | Somente disponível pode ser solicitado; manutenção/emprestado são recusados no servidor e na UI | Testes diretos da API e UI, incluindo os três itens em manutenção e item solicitado previamente |
| CA-03 | Solicitar cria empréstimo imediato e torna item indisponível em operação atômica | Teste de sucesso e falha intermediária com rollback, sem estado parcial |
| CA-04 | Quem tem 3 abertos não cria quarto; quem tem atraso não cria novo; motivo visível | Cenários com 0/2/3 abertos, atraso e vencimento hoje; recusa não altera contagens |
| CA-05 | Prazo e atraso seguem regra aprovada no fuso especificado | Relógio controlado e tabela de datas; fins de semana, mês/ano e limite da meia-noite local |
| CA-06 | Dois pedidos simultâneos ao mesmo item criam só um empréstimo; usuário com 2 abertos solicitando dois itens simultaneamente não passa de 3 | Testes concorrentes em PostgreSQL local real, não apenas mocks sequenciais |
| CA-07 | Usuário vê só seus empréstimos em aberto com data prevista; token inválido/acesso cruzado são recusados | Dois usuários e testes de identidade, expiração/invalidez do token e tentativa de mudar titular no pedido |
| CA-08 | Interface não inventa sucesso; exibe recusa/erro e só atualiza estado após confirmação do servidor | Testes de timeout, API indisponível, resposta de recusa, clique repetido e retorno ao catálogo |
| CA-09 | Backend/front passam no verificador independente por critério antes de conclusão; professor fica intacto | Rodadas comparáveis com causa/evidência; teste isolado de erro plantado revertido e evidência humana de zero empréstimos do professor |

## Exemplos de prazo para os testes

| Solicitação (data local) | Vencimento | Primeiro dia em atraso |
|---|---|---|
| 2026-11-09, segunda | 2026-11-27, sexta | 2026-11-28 |
| 2026-11-13, sexta | 2026-12-03, quinta | 2026-12-04 |
| 2026-11-14, sábado | 2026-12-03, quinta | 2026-12-04 |
| 2026-12-18, sexta | 2027-01-07, quinta | 2027-01-08 |

Feriados como 25/12 e 01/01 contam se caírem de segunda a sexta, conforme decisão humana. Vencimento é data, não horário inventado de devolução.

## Dependências e pendências

Spec 003 para dados/imagens; verificador real e demais aprovações permanecem pendentes. Gabriel aprovou especificamente T3 (login tradicional no backend), plano correspondente, psycopg e DDL senha_hash/sessões; exceção de escrita de ADR restrita a login (ADR-005). Supabase Auth/auth_user_id temporário não foi aplicado e foi substituído. Não autoriza implementar outras tarefas.

### Contrato aprovado de leitura — CA-01/CA-07, recorte T5a

Aprovação específica de Gabriel permite registrar ADR-006 e implementar somente GET /api/equipamentos e GET /api/emprestimos/meus. Não conclui CA-01/CA-07 integrais nem autoriza outras tarefas; a restrição anterior refere-se à aprovação de login isoladamente.

- Catálogo autenticado: {equipamentos:[{id,nome,patrimonio,categoria,status}]}; categoria é nome, id string e patrimônio pode ser null. Inclui INATIVO; preserva MANUTENCAO/INATIVO; DISPONIVEL com aberto vira EMPRESTADO, sem aberto permanece DISPONIVEL. Não inventa registros/imagens nem altera banco.
- Próprios abertos: {emprestimos:[{id,retirado_em,previsto_para,equipamento:{id,nome,patrimonio,categoria}}]}; titular exclusivamente do id de AuthService.me, devolvido_em null, retirada ISO com offset e vencimento data ISO persistida. Parâmetros enviados pelo cliente não trocam titular.
- Vazio é lista vazia. Token inválido/ausente/expirado/inativo: 401; infraestrutura: 503 sanitizado; Cache-Control no-store inclusive erros. SQL parametrizado e conexão existente por composição/DI.
- No recorte T5a original não houve POST, schema, novas dependências, imagem, seed, frontend ou conexão real. Testes fake não validavam SQL real/RLS; em etapa posterior, leituras foram exercitadas contra PostgreSQL remoto usando a conexão administrativa. Isso não valida a role runtime nem a produção.

### Contrato aprovado de login — CA-01/CA-07, recorte T3

- POST /api/login {email,password} -> {user:{id,email},expires_in,access_token,token_type:'bearer'}; credenciais incorretas, conta ausente/inativa ou senha_hash nulo -> 401 genérico.
- GET /api/me com Authorization bearer -> {user:{id,email}}; sessão inválida, expirada/revogada ou conta inativa -> 401. POST /api/logout revoga e retorna 204, idempotente para token desconhecido.
- PBKDF2-HMAC-SHA256 600000, salt16, compare_digest; tokens aleatórios opacos só digest SHA-256 no banco. Validade técnica inicial 3600s (ADR-005), sem refresh. SQL parametrizado, timeouts, DI/fake em testes e falhas do banco 503 sem segredo; validação não ecoa password.
- CORS exato local 5173 ou origens reais configuradas em CORS_ORIGINS no servidor, nunca wildcard. DATABASE_URL exclusivamente servidor, sem acesso remoto nesta tarefa.
- Advisory try-lock por conta protege apenas concorrência, não tentativas sequenciais. Rate limit/lockout persistente precisa de DDL e política adicionais aprovados; segurança de produção não concluída.
- CLI e PostgreSQL local indisponíveis: migration não pode ser gerada manualmente nem aplicada por SQL avulso; integração, RLS e login com banco real ficam bloqueados. Usuários existentes sem senha_hash não são redefinidos. Nenhuma credencial fixa ou conta do professor criada.

Decisão humana aprovada para CA-08: após timeout ou perda da resposta, não reenviar automaticamente a solicitação, pois o servidor pode ter criado o empréstimo. Consultar próprios empréstimos e catálogo para atualizar o estado observado. Só confirmar existência de empréstimo quando a consulta do titular o demonstrar; item indisponível no catálogo, sozinho, não prova que o pedido desse usuário teve sucesso. Se não for possível confirmar, mostrar "Não foi possível confirmar a solicitação", sem inventar sucesso ou recusa. Testar resposta perdida depois de commit, consulta falhando e item emprestado a outro usuário. Alternativa de chave de idempotência no servidor não foi escolhida nesta decisão.

Produção não é escrita pelo agente; solicitação remota para validação é executada pelo usuário com conta de teste. A conta do professor não é usada em pedidos. Registro existente divergente não é corrigido silenciosamente pelo seed.

### Contrato aprovado de solicitação — recorte T6a

Aprovação específica de Gabriel autoriza ADR-007 e uma tarefa backend reutilizando schema/trigger existentes, sem migration ou DDL. POST /api/emprestimos recebe somente {equipamento_id: UUID}, extras proibidos (422); titular derivado da sessão no servidor e revalidado com usuário ativo dentro da transação. Retorna 201 {emprestimo:{id,retirado_em,previsto_para,equipamento:{id,nome,patrimonio,categoria}}}, compatível com as leituras.

READ COMMITTED, advisory equipamento depois usuário (hashtextextended UUID texto canônico, seed 0, igual ao trigger), equipamento FOR UPDATE, usuário/sessão FOR SHARE; consultas de abertos e relógio após locks. Disponibilidade deriva de único INSERT sem alterar status. Ausente/manutenção/inativo/aberto: 409 reason equipamento_indisponivel; 3 abertos: 409 reason limite_emprestimos; atraso: 403 reason emprestimo_atrasado. Prioridade disponibilidade, limite, atraso. Autenticação inválida/inativa: 401 existente; infraestrutura: 503 sanitizado 'Solicitação indisponível.'. Tudo no-store. Somente unique conhecido ux_emprestimos_equipamento_ativo vira recusa; demais erros não expõem detalhes.

Prazo/atraso reutilizam src/prazo.py com relógio aware do servidor após espera de locks; vencendo hoje permitido. Rollback em qualquer erro, sem retry automático. Testes fake não certificam CA-06 nem integração PostgreSQL/RLS; schema de sessões e banco real pendentes. Não autoriza frontend, seed, imagens, instalação, remoto, permissões ou deploy. T4/T6 integrais e Spec 004 permanecem não concluídas.

## Fora de escopo

Devolução, Operações, reserva futura, renovação, e-mail, alteração de landing/logo e cadastro administrativo persistente.
