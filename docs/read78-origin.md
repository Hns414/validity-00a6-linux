# Origem do bloco: requisição de leitura 0x78

Continuação do [método posterior da interface](processing-method18.md). Análise estática manual da DLL fixada; a [evidência](evidence/read78-origin.json) registra cinco chamadas, slot de dispatch, opcode e associação de callback conferidos. Nenhum comando foi enviado ao sensor.

## Ligação ao buffer processado

Antes da chamada ao método +0x18 em 0x48379, o chamador passa um descritor de buffer para **0x4817a → 0x53010**. Sob condições de estado já testadas pelo chamador, seu comprimento e ponteiro vêm do estado superior +0x20/+0x28. Após sucesso, esse mesmo buffer fornece a entrada ao método de processamento. Isso liga a entrada a uma requisição específica, sem confundi-la com a resposta 0x30000288 da requisição 9.

O wrapper 0x53010 prepara a **requisição interna 0x31**, instala o callback **0x58de0** e despacha por 0x53134 → 0x5a820. O slot **0x1164c8** da tabela aponta para **0x82010**. O índice 0x31 é do host, não opcode USB.

## Frame e resposta

O handler 0x82010 aloca cinco bytes por **0x8204f → 0x83220**, passando opcode **0x78**, e copia um DWORD do pedido para os quatro bytes seguintes. A capacidade inicial de resposta é calculada como esse DWORD +6 e armazenada como DWORD. Em **0x820cd**, chama o transporte comum 0x7b110.

O cálculo descreve o binário; não é validação de tamanho, limite máximo descoberto ou autorização para emitir esse frame. Transformações e status do transporte continuam aplicáveis. Ainda não foram auditados todos os limites da alocação/destino e as condições anteriores necessárias ao pedido real.

No callback, com status recebido zero e corpo de pelo menos quatro bytes:

| Offset no corpo após tratamento comum | Campo |
| --- | --- |
| 0 | Comprimento DWORD little-endian |
| 4 | Conteúdo declarado |

O callback limita a cópia a `min(comprimento declarado, tamanho disponível - 4)`, grava o comprimento efetivo no descritor do chamador e copia o conteúdo a partir de +4. Depois zera o buffer temporário de resposta. Não foi identificada nesta função uma comparação completa com a capacidade original do destino; o contrato superior continua pendente.

Com corpo menor que quatro bytes ou status recebido diferente de zero, esse ramo de cópia não ocorre. O retorno local do callback e o status recebido são distintos; não interpretar retorno local zero como aquisição válida.

## Inspetor offline original

```sh
python3 tools/inspect_read78_reply.py /caminho/corpo-sintetico.bin
```

A ferramenta lê somente um arquivo local e devolve contagens/tamanhos. Não imprime bytes, hashes, conteúdo ou caminhos de erro. Não contém USB, extração de imagens ou encoder do pedido. O exemplo é para dados sintéticos, não uma solicitação de coleta real.

Sua política é mais estrita que a cópia da DLL: exige exatamente quatro bytes de cabeçalho mais o comprimento declarado. Rejeita truncamentos e caudas adicionais em vez de truncar silenciosamente. Aceita comprimento zero apenas estruturalmente e limita o corpo a **65536 bytes**; esse orçamento é local, não limite confirmado do protocolo.

Não fornecer uma transcrição USB inteira ou assumir que o prefixo de status faz parte desse corpo. Passar no inspetor não prova semântica biométrica nem validade operacional.

## Verificação e pendências

Seis testes novos cobrem independência do conteúdo, comprimento zero, todos os truncamentos de um exemplo, contagens inconsistentes, endianness, tipos de entrada, orçamento e CLI com saída sanitizada. `make test` passou com **109 testes sem skips**.

A origem imediata do bloco ficou ligada ao caminho 0x78. A tabela de índices tem inicialização identidade já documentada, mas sua capacidade completa e possíveis alterações posteriores ainda precisam de auditoria. Também faltam confirmação no hardware, dependências de inicialização, limites do destino e semântica da saída. Probe inalterado, sem teste com dedo nesta etapa.
