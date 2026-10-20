# Cadastro de equipamento

**Status:** aprovado pelo solicitante em 19/10/2026

## Objetivo

Disponibilizar a primeira tela administrativa do EMPREST.AI para preparar o cadastro de itens de TI no catálogo interno.

## Escopo desta tarefa

- Exibir a identidade fixa de **Gabriel Bento** no papel de **Operações**.
- Criar a tela de cadastro com os campos definidos no modelo `equipamentos`: nome, patrimônio, categoria, situação operacional e observação.
- Usar as categorias iniciais previstas na migração: Notebook, Monitor, Cabo, Câmera e Acessório.
- Validar no navegador que o nome é obrigatório.
- Informar explicitamente que os dados ainda não foram enviados ao banco.

## Fora do escopo

- Autenticação e troca de usuário.
- Criação ou alteração de tabelas no Supabase.
- Persistência do formulário e listagem do catálogo.

## Critérios de aceite

- CA-01: a tela se identifica como EMPREST.AI e mostra Gabriel Bento como Operações.
- CA-02: o formulário contém todos os campos de cadastro previstos no modelo.
- CA-03: patrimônio é opcional e a interface explica a exibição `TI-—` quando ausente.
- CA-04: o envio sem nome apresenta uma validação.
- CA-05: nenhum sucesso de gravação é informado sem integração com a API.
