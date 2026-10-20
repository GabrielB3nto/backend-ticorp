# PRD — Programa de Pontos

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
