# Spec 003 — Dados iniciais

Preparar os 12 equipamentos com fotos e a conta do professor sem criar empréstimos. A spec cobre backend e integração futura com frontend; produção é executada somente por Gabriel.

**Status:** proposta para revisão; não implementada nem verificada.
**Fontes:** ../../PRD.md, ../../plan.md, ../../../rules/spec-flow 1.md e ../../../rules/restrictions 1.md.
**Enunciado transcrito:** ../../../../pratica-sdd-subagentes.html, seções #skill (lista dos 12 equipamentos) e #spec002 (conta obrigatória). As exceções de manutenção e provedor foram decididas por Gabriel nesta conversa; o HTML não é alterado.

## Decisões e conflitos resolvidos

- Gabriel escolheu TI-0004, TI-0007 e TI-0010 em manutenção: a lista prevalece sobre o briefing que omite TI-0010.
- Pixabay substitui Pexels por orientação do professor relatada por Gabriel. O HTML original permanece intacto como evidência do conflito.
- Senha no seed é rejeitada; usuário fornece segredo fora do código/git. Não pedir senha no chat.
- Gabriel rejeitou sharp e sips: buscar fotos já em 800×600, sem redimensionar, cortar ou completar bordas. Medir o arquivo obtido antes de aceitar; CSS ou dimensão mínima da busca não comprovam 800×600. Se faltar foto adequada, registrar pendência, sem mudar tamanho ou origem automaticamente.
- Reexecução não deve restaurar disponibilidade de item emprestado nem alterar empréstimos. Registro existente divergente deve ser reportado para revisão, não sobrescrito automaticamente.
- Esta spec é 003 porque 002-cadastro-equipamento já existe; nenhuma spec anterior é sobrescrita.

## Dados obrigatórios

| Patrimônio | Nome | Categoria | Situação inicial | Busca do enunciado |
|---|---|---|---|---|
| TI-0001 | Notebook 14 polegadas | notebook | disponivel | laptop on white desk |
| TI-0002 | Notebook 15 polegadas | notebook | disponivel | open laptop minimal desk |
| TI-0003 | Notebook 13 polegadas | notebook | disponivel | laptop closeup keyboard |
| TI-0004 | Notebook 15 polegadas | notebook | manutencao | closed laptop on table |
| TI-0005 | Monitor 24 polegadas | monitor | disponivel | computer monitor on desk |
| TI-0006 | Monitor 27 polegadas | monitor | disponivel | monitor screen office desk |
| TI-0007 | Monitor 22 polegadas | monitor | manutencao | black computer screen |
| TI-0008 | Cabo HDMI 2 m | cabo | disponivel | hdmi cable |
| TI-0009 | Cabo USB-C 1 m | cabo | disponivel | usb cable white background |
| TI-0010 | Cabo de rede 3 m | cabo | manutencao | ethernet cable |
| TI-0011 | Webcam Full HD | camera | disponivel | webcam |
| TI-0012 | Câmera compacta | camera | disponivel | compact camera on table |

Conta obrigatória: marcelo.grilo@institutojef.org.br, credencial definida no enunciado e fornecida pelo usuário fora do repositório. A conta chega à correção com zero empréstimos; testes usam identidade diferente. Conta existente não tem senha redefinida automaticamente.

## Critérios de aceite

| ID | Resultado observável | Evidência exigida |
|---|---|---|
| CA-01 | Primeiro seed contém exatamente os 12 patrimônios acima, 3 em manutenção e 9 disponíveis, sem empréstimos criados | Teste local que compara os 12 registros com a tabela e contagem antes/depois |
| CA-02 | Uma foto Pixabay distinta por equipamento; cada arquivo mede 800×600 de fato | Manifesto com ID, patrimônio, origem, autor, licença/data, checksum e leitura das dimensões dos 12 arquivos |
| CA-03 | Nenhuma pessoa, marca/logo legível, texto ou tela com conteúdo nas fotos finais | Registro de revisão visual humana por arquivo, incluindo reprovações e motivos; safesearch sozinho não prova isso |
| CA-04 | Reexecução não duplica equipamentos, usuário nem objetos; não altera item emprestado ou empréstimos | Duas execuções locais, comparação de contagens/checksums e cenário de item já emprestado e registro divergente |
| CA-05 | Professor autentica e tem zero empréstimos; testes não usam sua conta; segredo não está no código/git | Teste local de identidade isolada e evidência de login/contagem remota fornecida pelo usuário, sem senha/token |
| CA-06 | Preparo local não pode escrever no Supabase do deploy; arquivos finais ficam públicos após upload humano idempotente | Inspeção das capacidades do preparo, teste de bloqueio e URLs/dimensões verificadas após publicação humana |
| CA-07 | API Pixabay usa cache 24h, não faz download em massa nem hotlink permanente; falhas de API não produzem manifesto aprovado | Testes locais simulando cache, chave ausente, 429, resultado vazio, download inválido e imagem repetida |
| CA-08 | Cada CA passa pelo verificador independente antes de conclusão | Relatório por rodada com critério, status e evidência; itens de produção sem evidência permanecem não verificados |

## Limites e pendências

Antes de implementação: registrar decisões estruturais em ADRs pelo time, aprovar mecanismo de isolamento do harness e plano desta spec. Não instalar processador de imagens: a seleção deve aceitar somente arquivos já em 800×600. API Pixabay tem filtros de dimensões mínimas, não filtro de dimensão exata; selecionar candidatos e verificar os bytes baixados, sem prometer disponibilidade de 12 fotos elegíveis. Chave Pixabay não entra em logs/manifestos nem no frontend.

Decisão humana aprovada: exceção específica à regra dos três ambientes em rules/secrets 1.md para a chave Pixabay. Ela fica exclusivamente no ambiente local não versionado da ferramenta de preparo, com nome e valor vazio no .env.example, sem cadastro na Vercel. A aplicação publicada não consulta essa API. Nenhum valor real é versionado, exibido em logs ou entregue ao frontend. A exceção vale apenas nesta prática e para essa chave.

A licença Pixabay Content License proíbe redistribuição standalone; redimensionar/cortar não muda isso. Validar compatibilidade do catálogo e bucket público antes da publicação humana. Não tratar fotos como CC0 nem criar pacote de distribuição.

## Fora de escopo

Catálogo UI (spec 004), cadastro administrativo persistente, importação de planilha, empréstimos no seed, alteração de landing/logo e escrita remota pelo agente.
