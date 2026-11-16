# Callback e mapeamento da consulta candidata 0x75

Continuação da [origem do tipo interno](internal-type-seed-and-query.md), por análise manual da DLL fixada. A [evidência](evidence/query75-callback-mapping.json) registra coordenadas e leituras de metadados. Sem execução ou USB.

## Dois DWORDs após tratamento comum

O wrapper 0x54a40 instala **0x5a710** como callback em 0x54b79. Esse callback guarda o status recebido, verifica ponteiros e, quando o status é zero, lê dois DWORDs do conteúdo em offsets **0 e 4**. Os guarda nos campos +0x14/+0x18 de sua estrutura de conclusão.

Isso exige pelo menos oito bytes acessíveis de corpo nesse caminho. A capacidade inicial de dez bytes do handler é coerente com dois bytes de status comum mais oito de corpo, mas **não comprova comprimento exato em hardware**. O callback não apresenta uma verificação visível de comprimento antes dessas leituras; podem existir validações anteriores, ainda não auditadas integralmente.

Um decoder original futuro precisará validar tamanho antes de acessar campos e separar o status do corpo. Nenhum dado dessa consulta foi coletado no participante. A interpretação dos campos foi refinada na [conferência pública posterior](query75-public-crosscheck.md); não publicar dados reais desconhecidos por suposição.

## O segundo DWORD é interpretado, não usado diretamente

Na rotina 0x62eb0, sucesso da consulta e segundo DWORD de corpo não zero permitem um caminho de substituição. Há uma regra explícita em 0x63031–0x63056:

`0x0049000c` → `0x00830003`

Em seguida, a rotina separa as metades de 16 bits: metade alta para o primeiro identificador do mapper e metade baixa para outro critério. Em 0x6307f chama 0x5f140, que passa a tabela estática **RVA 0x116800** e contagem **0x17b (379)** a **0x63f80**.

Não é correto interpretar o DWORD recebido como se já fosse o tipo interno usado no seletor. Há normalização, consulta de tabela e tratamentos adicionais posteriores, descritos na etapa anterior.

## Tabela de mapeamento

O mapper percorre registros de **0x1c (28) bytes**. Nos campos iniciais observados:

| Offset do registro | Tamanho | Uso no trecho examinado |
| --- | --- | --- |
| +0 | 2 | Chave comparada à metade alta |
| +2 | 2 | Resultado candidato retornado |
| +4 | 2 | Valor de comparação |
| +6 | 2 | Máscara usada na comparação |
| +8 | restante | Metadados também referenciados pelo contexto |

Para a chave 0x83, a leitura local encontrou três registros:

| Índice | Resultado | Valor | Máscara |
| --- | --- | --- | --- |
| 138 | 0xed | 1 | 0xff |
| 139 | 0xed | 2 | 0xff |
| 140 | 0xed | 3 | 0xff |

No ramo com critérios não zero, o mapper compara partes mascaradas do argumento e do valor do registro. Esses registros ajudam a conferir a lógica do exemplo normalizado; **não são dados medidos no participante**. O restante da tabela e seus metadados não foram transformados em uma especificação pública de todas as famílias.

A rotina também obtém um snapshot de contexto por 0x5dfd0 e pode guardar referência a metadados do registro em +0x2c8. A semântica completa desse estado e dos consumidores ainda não foi resolvida. Não implementar uma identificação ativa copiando apenas as duas primeiras colunas.

## Validação e próximos passos

Foram conferidos o vínculo do callback, as duas leituras DWORD, duas chamadas e os três registros da tabela fixada. O fluxo de interpretação permanece análise manual. O tipo interno real do participante e o registro da tabela de programas nas listas do host continuam pendentes.

Esta etapa altera somente documentos/evidência. Mantém a base de **91 testes aprovados na v0.37**, sem nova execução da suíte. Não há decoder ativo de 0x75, novo comando no probe ou teste com dedo.

A v0.43 corrigiu a fonte do mapper para o segundo DWORD, seguindo os ponteiros de saída até o chamador; veja a [conferência detalhada](query75-public-crosscheck.md).
