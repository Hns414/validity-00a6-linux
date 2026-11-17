# Carregador candidato de entradas e sua alcançabilidade

Continuação dos [produtores do contêiner](session-entry-container.md). Análise estática da DLL fixada; [evidência sanitizada](evidence/candidate-entry-loader.json) com sete chamadas, nove âncoras e uma entrada de despacho conferidas. Nenhum comando USB foi enviado.

## O produtor direto encontrado prepara uma entrada inicial

A busca no texto encontrou **0x666ec → 0x8ca30**, com capacidade obtida de uma referência global e terceira entrada zero. O produtor instala o buffer no contêiner e chama 0x8da40 com identificador zero, comprimento 1 e endereço dessa entrada local. Esse caminho demonstra preparação de buffer e entrada inicial; **não demonstra presença das entradas 5 e 7** usadas pelos estados posteriores.

Não foram encontrados chamadores diretos de 0x8d3e0 no disassembly textual examinado. Isso não exclui chamadas indiretas, código não reconhecido ou referências construídas em execução.

## Outro corpo carrega e instala um buffer

A função **0x8cb40** contém um caminho que consulta metadados por 0x4eeb0, procura uma entrada de categoria 1 e obtém um tamanho. Aloca um buffer e chama **0x8cccc → 0x4f2c0** com os campos de seleção examinados. Se esse percurso e a verificação posterior **0x8cf2a → 0x8dc00** retornam sucesso, instala no contêiner:

| Campo | Valor de origem |
| --- | --- |
| +0x1c | Tamanho de buffer obtido no carregador. |
| +0x20 | Ponteiro para o buffer alocado e preenchido. |
| +0x18 | Quantidade usada devolvida pela verificação. |

Há outro ramo condicionado por 0x5f720; ele não foi integralmente fechado nesta etapa. Os limites e a semântica completa de 0x8dc00 também permanecem pendentes. Instalar o buffer depois de uma verificação não prova, por si só, validação completa de seu formato ou autenticação.

## Ligação estática com o transporte

O wrapper **0x4f2c0** seleciona pedido interno **0x16** em 0x4f405 e o despacha em **0x4f468 → 0x5a820**, com callback 0x57620. A tabela de handlers resolve a entrada **0x1163f0** para **0x7f730**.

Esse handler solicita em **0x7f7ae → 0x83220** uma estrutura de pedido de **13 bytes** com opcode candidato **0x40**, preenche seus campos a partir do pedido interno e chama **0x7f866 → 0x7b110**, o transporte já investigado. Isso liga estaticamente um ramo do carregador a uma operação de transporte. Pedido interno 0x16 e opcode candidato 0x40 são identificadores de camadas distintas.

O callback extrai uma contagem e copia conteúdo para o destino no caminho de sucesso. O contrato completo dessa cópia, da capacidade e da resposta ainda precisa ser auditado antes de produzir qualquer implementação ativa. Nenhum conteúdo, payload de pedido ou dados de sessão são publicados.

## Lacuna decisiva: quem chama o carregador

Não foram encontrados chamadores diretos de **0x8cb40** no texto examinado, nem ponteiros absolutos de 64 bits com seu endereço exato no arquivo. A mesma busca limitada não encontrou ponteiro absoluto para 0x8d3e0. Essas buscas **não provam código morto**: referências relativas, aliases, tabelas compactadas ou despacho indireto podem escapar desse critério.

Portanto, encontrar esse corpo não demonstra que o fluxo ativo do participante o execute. Também não demonstra que suas entradas 5 e 7 venham dessa operação ou que a operação esteja disponível no firmware relatado.

## Consequência e próximo passo

A origem das entradas ainda não está fechada: há preparação inicial diretamente chamada e um carregador com caminho de transporte, cuja alcançabilidade não foi demonstrada. Não adicionar consulta 0x40 ao probe com base apenas nessa descoberta.

Próximo trabalho: investigar referências relativas/indiretas do carregador e auditar o contrato de resposta antes de propor experimento no hardware. Probe inalterado; sem USB, captura ou teste com dedo. Etapa documental: base de **121 testes aprovados na v0.72**, sem repetir a suíte.
