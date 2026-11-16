# Nós condicionais com material aleatório do host

Análise estática manual da DLL fixada. A [evidência](evidence/conditional-transport-nodes.json) registra doze destinos de chamadas e seis âncoras de tamanho/cabeçalho conferidos. Nenhum buffer de execução foi coletado ou publicado.

## Inclusão e formatos

O montador chama **0x87d90 em 0x7cb22**. O construtor consulta 0x74c90 e a classe interna DWORD do contexto +0x23c. Assumindo que os predicados permaneçam estáveis entre as consultas repetidas na função:

| Condição | Tipo do nó | Conteúdo | Total com cabeçalho |
| --- | --- | --- | --- |
| Helper 0x74c90 positivo e classe 1 | 0x36 | 108 bytes | 112 bytes |
| Helper positivo, outra classe e 0x8bb30 positivo | 0x06 | 106 bytes | 110 bytes |
| Demais condições | Nenhum nó alocado | — | 0 |

O helper **0x8bb30** calcula `(version[8] << 8) + version[9]`, compara com 0x0414 e retorna positivo somente se o resultado for pelo menos esse valor e a classe diferir de 1. Esse predicado é distinto de identificação de tipo por 0x75. A condição de 0x74c90 já foi [delimitada no transporte](query75-transport-order.md): seu resultado positivo não prova sozinho que todos os requisitos de transformação estejam satisfeitos.

O tipo de nó 0x06 é um campo de cabeçalho interno ao pedido; não equivale ao opcode USB 0x06 de inicialização.

## Conteúdo gerado no host

Ambos os formatos zeram inicialmente seu conteúdo e chamam **0x61e30**, que prepara dois campos de 32 bytes do contexto. Cada campo passa por **0xd9f90**, cujo destino indireto na IAT, RVA **0x1100a8**, é **CryptGenRandom**, conforme a tabela de importações PE. Isso identifica a geração aleatória; não estabelece sozinho o papel criptográfico posterior de cada campo.

| Offset no conteúdo do nó | Tamanho | Origem |
| --- | --- | --- |
| 0x00 | 32 | Contexto +0x17c, preenchido por CryptGenRandom |
| 0x20 | 32 | Contexto +0x19c, preenchido por CryptGenRandom |
| 0x40 | 32 | Contexto +0x1c0 se flag 0x08 do descritor estiver ativa; zeros caso contrário |
| 0x64 | 4 | Valor fixo 0x300 |
| 0x68 | 1 | 4 no formato 0x36; seleção adicional no formato 0x06 |
| 0x69 | 1 | Valor 1 |

Com flag 0x08 ativa, **0x61ed0** também preenche o campo +0x1c0 com 32 bytes via CryptGenRandom, antes de preparar estado adicional. Essa preparação adicional possui ramos próprios e não foi inteiramente auditada nesta etapa.

No formato 0x06, o helper 0x74d60 fornece um byte: valores 0x10, 0x18 e 0x20 selecionam respectivamente 1, 2 e 4 no conteúdo +0x68. Outros valores seguem diagnóstico e saída, sem inserção do nó. No formato 0x36, os dois bytes finais do conteúdo de 108 bytes permanecem zerados pelo memset inicial.

## Consequência para o driver aberto

A montagem não depende apenas de copiar um programa fixo: esse ramo acrescenta material novo do host e depende de estado anterior. Ainda faltam o consumidor desses campos, sua relação com a proteção do fluxo e a confirmação das condições no participante. Não foi implementado encoder ou replay desses nós.

O rastreio dos registros dinâmicos continua aberto: foram localizados chamadores que criam os registros sob demanda e escrevem em seu conteúdo, mas a sequência de chamadas que efetivamente preenche a lista usada na captura ainda não foi fechada.

Etapa documental, sem novos comandos USB ou testes com dedo. A suíte não foi repetida: permanece a base de 103 testes aprovados na v0.47. A verificação desta etapa foi estática, incluindo chamadas, cabeçalhos e tabela de importações.
