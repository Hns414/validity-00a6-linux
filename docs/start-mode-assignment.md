# Atribuição do modo e preferência no ramo 0x80

Análise manual da DLL Dell fixada, com [evidência de campos, chamadas e comparação](evidence/start-mode-assignment.json). Sem execução da DLL ou transferência USB. RVAs relativos à ImageBase 0x180000000.

## Uma escrita posterior substitui o cálculo anterior

Antes de construir o objeto de captura, o chamador passa o objeto externo +0x1d0 à rotina 0x16998 em 0x1b033. Quando o DWORD +4 desse objeto vale 1, a rotina executa um cálculo que pode inicialmente gravar 1, 2 ou 3 no DWORD +0x18.

Entretanto, todas essas alternativas convergem em 0x16ac1. A instrução em **0x16ac9 grava incondicionalmente 3 no mesmo campo** nesse ramo. Portanto, o cálculo anterior não determina seu valor final. Os bytes dessa instrução foram conferidos no binário fixado; não é inferência baseada apenas em nomes de função.

Se +4 não vale 1, o desvio em 0x169cd pula esse bloco. Não foi demonstrado nesta etapa qual valor anterior permanece nesse caso. Não generalizar a escrita de 3 para todo contexto de operação.

O getter 0x2bc20, chamado em 0x1b128, lê +0x18 posteriormente. Pela [cadeia de cópia já rastreada](start-parameter-origin.md), esse valor chega ao construtor, ao objeto de captura +0x80 e ao WORD +0x0c da preparação. Se não houver outra escrita ou mudança de caminho, o valor 3 pode permanecer ou ser ajustado localmente para 1. Ambos são diferentes de 2 e, quando não há o desvio que pula a preparação, escolhem **máscara 0x80**, não 0x400000.

Essa é uma implicação de fluxo sob condições explícitas; a DLL não foi executada para observar o ramo real do participante. Também não atribui nomes como autenticação ou cadastro aos valores da enumeração.

## Duas candidatas e regra de comprimento

Para máscara requerida 0x80, excluída 0x22020, parâmetro zero, versão candidata 6.7/build 164, discriminante 2 e gate interno +0x0a igual a 1, os filtros da tabela deixam:

| Índice | Registro | Máscara do registro | Argumentos | Campo +0x20 |
| --- | --- | --- | --- | --- |
| 52 | 0x13d3a0 | 0x400080 | 12100 | 18 |
| 53 | 0x13d3f0 | 0x80 | 6676 | 17 |

Ambas têm +0x1c/+0x38/+0x40 curinga 0xffff e os mesmos requisitos restantes. O seletor não encerra na primeira candidata. Na preferência entre elas, compara comprimentos em 0x8fe1b/0x8fe1e e, pelo desvio em 0x8fe21, só considera substituir pela menor. As condições de especificidade examinadas não diferenciam esse par, cujos campos são iguais. Assim, sob essas premissas, a entrada posterior **53**, menor, substitui a 52 em 0x8fe59.

Isso difere do ramo 0x400000, no qual a entrada 53 nem passa pelo filtro de máscara. Logo, a conclusão anterior sobre entrada 52 continua específica daquele ramo. Não usar a primeira entrada compatível nem o maior bloco como seleção automática.

## Mesmo comprimento do bloco público, conteúdo diferente

O frame interno candidato da entrada 53 teria opcode 0x06 seguido de 6676 argumentos, totalizando **6677 bytes**. Foi comparado byte a byte ao literal público `vfs7552_init_04` do libfprint no commit 8b6e4e39bee58de2774222e3730269def470b157.

Os comprimentos são iguais, mas os conteúdos **não são iguais**. A evidência registra os hashes e o resultado, sem publicar o payload proprietário. Isso não prova que exerçam funções diferentes ou equivalentes; a semântica continua desconhecida. Não substituir um pelo outro com base no nome ou tamanho.

A máscara 0x80 também leva ao caminho de gerenciamento de cache do consumidor. Mesmo uma seleção correta pode concluir localmente sem envio, conforme estado do host. O frame candidato não foi habilitado no encoder nem no probe.

## Validação e pendências

Dois destinos de chamadas e a escrita final de modo foram conferidos no binário; a filtragem e comparação foram calculadas sobre dados mapeados pelas seções PE. A preferência e o fluxo de sobrescrita foram interpretados manualmente, sem prova automática de equivalência ou observação em runtime.

Somente documentos/evidência: mantém a base de 73 testes aprovados na v0.27, sem nova execução da suíte. Ainda faltam identificar o significado de +4 e do modo, os consumidores posteriores e os efeitos dos argumentos. Nenhum novo comando foi enviado e não há teste com dedo nesta etapa.
