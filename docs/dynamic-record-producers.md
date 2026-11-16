# Produtores dos registros dinâmicos

Continuação da [auditoria dos registros](dynamic-host-records.md), por análise estática manual da mesma DLL fixada. A [evidência](evidence/dynamic-record-producers.json) contém metadados e nove chamadas conferidas, sem conteúdo de registros, execução do driver ou transferências USB.

## Alocação e propriedade do conteúdo

A função **0xe6640** aloca um nó de 0x30 bytes. Seus argumentos fornecem a chave WORD, gravada em +0x14, o comprimento DWORD, em +0x18, e o conteúdo, cujo ponteiro fica em +0x20. A função insere o nó na lista duplamente encadeada e incrementa o contador agregado do objeto em comprimento +6.

Para comprimento zero, o conteúdo fica nulo. Para comprimento não zero e quarto argumento igual a 1, aloca um buffer e copia o conteúdo fornecido; nos demais valores, guarda o ponteiro fornecido. Isso distingue cópia de retenção de ponteiro nesse produtor; não completa a auditoria de destruição ou de tempo de vida da lista.

O wrapper **0xe5560** encaminha chave, comprimento e conteúdo com modo de cópia 1. O campo de tipo recebido pelo alocador é distinto da chave usada na busca. Não confundir nenhum deles com o tipo interno de sensor identificado por 0x75.

## Criação sob demanda

A função **0x91530** começa buscando a chave solicitada. Quando recebe status de ausência 0x76, há ramos específicos para índices 1, 2, 4 e 5. Dois deles foram acompanhados até a inserção:

| Índice | Comprimento do registro criado | Inserção por 0xe5560 |
| --- | --- | --- |
| 1 | 62 bytes | Chamada em 0x91649 |
| 2 | 14 bytes | Chamada em 0x916c3 |

Os buffers locais são zerados; um ponteiro opcional no objeto +0x20 permite copiar campos para eles antes da inserção. A origem anterior desses campos não foi classificada. Portanto, esses registros não são constantes universais, e seus conteúdos não devem ser publicados nem reutilizados como configuração pronta.

Isso dá contexto à assimetria anterior: **se** ambos esses registros existirem e forem usados pelo percurso dinâmico examinado, o callback de tamanho soma 16+20=36 bytes. A cópia suportada do índice 1 começa em +8; o intervalo termina em +44 e cabe no registro de 62 bytes criado por esse ramo. O índice 2 continua sem cópia nesse callback. O cálculo não demonstra concatenação de ambos nem explica a intenção do formato.

A presença simultânea, a seleção desse produtor no caminho real e a semântica do conteúdo continuam sem confirmação. Outros produtores podem fornecer comprimentos diferentes.

## Outra entrada: importação de registros

O wrapper **0x72e50** encaminha um buffer para **0xe5e50**, que chega ao parser **0xe6880**. Ele interpreta cabeçalhos de seis bytes: chave WORD em +0 e comprimento DWORD em +2, seguidos do conteúdo. Depois encaminha cada registro ao mesmo alocador 0xe6640. A função inclui um teste de comprimento acumulado contra o total, mas esta etapa não auditou todas as leituras prévias, conversões e condições de erro; não considerar esse parser validado para entrada não confiável.

Essa entrada alternativa impede concluir que a lista contenha sempre os registros padrão acima. Falta rastrear os chamadores superiores e identificar qual fonte está ativa na montagem de captura do participante.

## Estado da etapa

Nove destinos de chamadas e seis âncoras de argumentos/escritas foram conferidos no binário fixado. Somente documentação e evidência: a base continua sendo os 103 testes aprovados na v0.47, sem nova execução nesta etapa. O probe não mudou. Inicialização, identificação real do tipo e captura ainda não foram executadas; nenhum teste com dedo solicitado.
