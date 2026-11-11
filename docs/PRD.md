# PRD — EMPREST.AI

**Status:** regras de negócio confirmadas; login, catálogo, empréstimos próprios
e solicitação estão implementados. Migrations 001–003 foram aplicadas ao
Supabase sob aprovações específicas. O reset local limpo, o uso da role
restrita, seed/imagens, verificador independente e produção ainda não estão
validados; consulte `docs/plan.md` e as tarefas das specs.

## Contexto

Sistema de empréstimo de equipamentos com backend REST e frontend separados.
Esta prática acrescenta verificador independente, skill de imagens, dados iniciais,
catálogo e solicitação. O Programa de Pontos ao final é referência histórica;
seus requisitos e aprovação antigos não autorizam esta prática.

## Decisões humanas confirmadas

Gabriel confirmou nesta conversa:

- Limite de **3 empréstimos em aberto** por colaborador, não os 5 do briefing.
- **TI-0004** (Notebook 15 polegadas), **TI-0007** (Monitor 22 polegadas)
  e **TI-0010** (Cabo de rede 3 m) em manutenção, conforme a lista exata.
  Os outros 9 equipamentos começam disponíveis.
- Devolução prevista **14 dias de segunda a sexta depois da solicitação**,
  excluindo o dia inicial e sem descontar feriados, no fuso **America/Sao_Paulo**.
  Atraso começa no dia seguinte ao vencimento, pela data nesse fuso.
- Gabriel aprovou os recortes de autenticação, leituras, solicitação
  transacional e integração frontend registrados nos ADRs 005–007 e na Spec
  004. A ferramenta de imagens e o isolamento do harness ainda não foram
  implementados/aprovados.
- Exceção específica aprovada por Gabriel: chave Pixabay apenas no preparo local
  não versionado, com nome/valor vazio em .env.example, sem Vercel. Não altera
  a regra de ambientes para as demais variáveis. Nenhuma chave no frontend.
- Após perda de resposta de solicitação, não reenviar automaticamente. Consultar
  próprios empréstimos e catálogo; só confirmar empréstimo demonstrado para o
  titular. Se não puder confirmar, mostrar "Não foi possível confirmar a solicitação".
  Item indisponível sozinho não comprova sucesso do pedido desse usuário.
- Por orientação do professor relatada por Gabriel, **Pixabay substitui Pexels**
  como única fonte de fotos de equipamentos nesta prática. Registrar essa exceção
  ao enunciado original no ENTREGA.md; não altera os demais requisitos de imagens.

## Requisitos da prática

### Dados iniciais e imagens

- Usar os 12 equipamentos exatos do enunciado (TI-0001 a TI-0012), com
  patrimônio único, nome, categoria, situação e imagem. Nenhum empréstimo no seed.
- Repetição não duplica equipamentos, usuários ou arquivos. Não redefinir
  empréstimos existentes ou liberar equipamentos emprestados ao repetir o seed.
- Preparar conta obrigatória do professor conforme enunciado, com zero empréstimos.
  Testes de solicitação usam outra conta. Nenhuma senha em código ou git;
  valores sensíveis fornecidos pelo usuário fora dos arquivos versionados.
- Toda foto de equipamento vem exclusivamente da API Pixabay pela skill
  imagens-equipamentos; substituir origens anteriores. Landing/logo fora do escopo.
- Fotos únicas, verificadas em 800×600, com origem, fotógrafo e licença registrados.
  Revisão visual reprova pessoas, marcas/logos legíveis, texto e telas com conteúdo.
- Imagens em bucket público Supabase Storage com upload idempotente. Agente
  prepara localmente; somente usuário grava no banco/Storage de produção.
- Exibir "Fotos: Pixabay" com link https://pixabay.com/pt/ onde houver fotos.
  A licença não exige atribuição em geral; a API pede indicação da origem ao
  exibir resultados. Manter o crédito como requisito do projeto e rastreabilidade,
  sem apresentar a exigência anterior do Pexels como se fosse do Pixabay.
- Respeitar cache de resultados da API por 24 horas, limites de requisições e
  ausência de downloads em massa. Sem hotlink permanente: baixar fotos escolhidas
  e preparar armazenamento próprio, sem usar URLs Pixabay como fonte final.
- Registrar Pixabay Content License, URL da licença e data de obtenção; não
  presumir CC0. Apenas redimensionar/cortar não resolve a proibição de distribuição
  standalone. Antes de publicação humana, validar uso das fotos integrado ao
  catálogo e compatibilidade do bucket público, sem criar galeria para redistribuir
  imagens ou um pacote de fotos para download. Essa validação continua pendente.
- Fontes consultadas: https://pixabay.com/api/docs/,
  https://pixabay.com/service/license-summary/ e https://pixabay.com/service/terms/.

### Solicitar empréstimo

- Colaborador autenticado vê os 12 equipamentos com foto, nome, categoria e situação.
- Conforme decisão declarada para a turma, solicitação cria empréstimo imediato;
  não existe aprovação de Operações nem fila de espera nesta versão.
- Servidor valida identidade, disponibilidade, limite de 3 e ausência de atraso;
  recusas mostram o motivo. Identidade fixa e validação apenas na interface não valem.
- Manutenção e empréstimo impedem solicitação. Criar empréstimo e alterar
  disponibilidade são uma única operação atômica. Pedidos simultâneos não podem
  emprestar o mesmo item duas vezes nem exceder o limite de um usuário.
- Colaborador vê apenas seus empréstimos em aberto e respectivas datas previstas.
- Prazo e atraso obedecem às decisões acima; testar fins de semana, virada de mês
  e ano, dia do vencimento e dia seguinte, com relógio controlado.

### Processo e evidências

- Toda funcionalidade passa por spec, plano e tarefas aprovadas antes de código.
- Verificador em contexto limpo confere cada critério e evidencia o resultado;
  não corrige código/testes, não publica, migra ou escreve no deploy.
- Conclusão de spec depende obrigatoriamente do verificador, não de lembrança.
  Rodadas comparáveis e prova real com erro plantado/revertido são exigidas.
- Prompt somente leitura não garante isolamento: capabilities do harness precisam
  ser verificadas antes de declarar o verificador seguro.
- ENTREGA.md em ambos os repositórios registra decisões, alternativas e evidências
  reais. Não inventar commits, rodadas, fotos revisadas ou validações de produção.
- Agente não escreve em banco/Storage de produção, não faz deploy e não cria
  tags sem autorização específica. Em 2026-11-11 Gabriel autorizou push dos
  repositórios para o GitHub quando prontos; isso não autoriza deploy automático
  ou alteração na configuração da Vercel.

## Pendências técnicas

- Validar a API como `emprestai_runtime`; a conexão administrativa não comprova
  as permissões efetivas da role restrita.
- Executar reset/replay local limpo e reconciliar o histórico de migrations.
- Preparar/revisar as 12 imagens Pixabay 800×600, manifesto/licenças e seed
  idempotente; completar a conta do professor sem senha no código.
- Implementar verificador independente com isolamento demonstrado, validar o
  frontend com API real e obter evidências de produção fornecidas pelo usuário.
- Repetir checks após mudanças finais e registrar ENTREGA.md nos dois projetos.

## Fora de escopo

Devolução, Operações, reserva futura, renovação, e-mail, cadastro por interface,
importação de planilha e mudanças de landing/logo. Não remover código histórico
fora do escopo nem usar a conta do professor para testes de empréstimo.

---

# Referência histórica — Programa de Pontos (não rege o EMPREST.AI)

**Solicitante:** Diretoria de Marketing
**Time responsável:** Engenharia
**Status:** aprovado para desenvolvimento

## Contexto

Somos uma rede varejista com 40 lojas físicas e um e-commerce. Hoje o programa de
fidelidade é operado por uma planilha mantida pelo time de Marketing, atualizada
manualmente uma vez por semana. O processo não escala e já gerou reclamações de
clientes por saldo divergente.

Queremos um sistema próprio para operar o programa.

## O que o sistema precisa fazer

**Acúmulo.** O cliente ganha 1 ponto a cada R$ 1,00 gasto em compras. Em datas de
campanha definidas pelo Marketing, a pontuação da compra é dobrada.

**Expiração.** Pontos expiram 12 meses após a compra que os originou.

**Resgate.** O cliente troca pontos por produtos de um catálogo. Cada produto do
catálogo tem um custo em pontos definido pelo Marketing.

**Estorno.** Se uma compra é cancelada ou devolvida, os pontos gerados por ela
são desfeitos.

**Atendimento.** O atendente da loja precisa conseguir explicar ao cliente por que
o saldo dele é o que é. Hoje a pergunta mais comum no balcão é "eu tinha 500
pontos, por que agora tenho 320?" — e o atendente não sabe responder.

**Fechamento contábil.** No fim de cada mês, o Financeiro precisa do total de
pontos emitidos e ainda não resgatados. Esse número entra no balanço como passivo
e é auditado.

**Disputas.** Um cliente pode contestar seu saldo meses depois do fato. Precisamos
conseguir reconstruir o que aconteceu na conta dele em qualquer data passada.

## Restrições

- A consulta de saldo acontece no PDV, com o cliente esperando no caixa. Precisa
  ser rápida.
- Nenhum registro do programa pode ser apagado ou alterado depois de criado —
  exigência da auditoria.
- Volume atual: cerca de 180 mil clientes ativos, 25 mil compras por dia.

## Fora de escopo nesta versão

- App do cliente (a consulta é feita pelo atendente)
- Níveis de fidelidade (bronze/prata/ouro)
- Transferência de pontos entre clientes

---

*Este documento descreve o que o negócio precisa. Decisões de tecnologia,
modelagem e arquitetura são responsabilidade do time de engenharia.*
