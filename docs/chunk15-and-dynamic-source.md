# Layout de 0x15 e callbacks da fonte dinâmica

Análise manual da DLL fixada. A [evidência](evidence/chunk15-and-dynamic-source.json) contém condições e campos decodificados, sem programa completo ou dados de sensor. Nenhuma execução ou USB.

## Quando o nó 0x15 existe

Na função **0x87b70**, o campo DWORD +4 do descritor é guardado como valor de modo e a máscara **0x20** do DWORD +8 vira uma condição local. As variáveis de tamanho começam em zero. Somente quando o modo vale zero e essa flag está desativada, a rotina define tamanho de **12 bytes** em 0x87c35.

O total calculado é testado em 0x87c4d; com zero, o caminho pula a alocação. Com 12, aloca o nó, escreve o cabeçalho de tipo 0x15 e conteúdo de tamanho 8 e chama **0x8c050 em 0x87cd3** para preencher o conteúdo.

Portanto, no ramo examinado, o nó inteiro fica delimitado:

| Offset no nó transmitido | Tamanho | Campo |
| --- | --- | --- |
| 0 | 2 | Tipo 0x15, little-endian |
| 2 | 2 | Tamanho de conteúdo 8, little-endian |
| 4 | 4 | DWORD zero |
| 8 | 4 | DWORD 0x2820, little-endian |

Esses campos não identificam por si só registrador, endereço, dimensões ou função do comando. Não interpretar 0x2820 como constante operacional reutilizável sem compreender o consumidor no sensor.

## Helper de conteúdo e argumentos

A função 0x8c050 termina em **0x8c08a**. Ela testa seu terceiro argumento, mas ambos os ramos escrevem o mesmo DWORD **0x2820** no conteúdo +4. Depois escreve zero em +0. O segundo argumento é recebido, mas não influencia essas escritas no trecho examinado.

Isso delimita os oito bytes e evita atribuir a esse helper as rotinas vizinhas a partir de 0x8c0a0, que tratam outros dados. Não equivale a dizer que os argumentos possam ser removidos dos chamadores: outros construtores ou versões podem usá-los, e o objetivo atual é compreender este caminho fixado.

## Fonte dinâmica: tamanho e cópia de estado do host

O helper 0x736c0 mantém a separação entre consulta de tamanho e preenchimento já documentada. Na classe de objeto examinada, valor 1 no campo +8 seleciona callbacks locais:

- **0x922b0** usa a função **0x92be0** para calcular comprimentos durante seu percurso.
- **0x923d0** instala **0x92be0** para tamanhos e **0x92c20** para copiar conteúdo.
- A chamada indireta do percurso chega ao callback de cópia, que usa memcpy em **0x92ca8**, com origem calculada a partir da estrutura do host.

Isso confirma que a fase de preenchimento copia campos de objetos já existentes no host; não é, nesse trecho, uma nova leitura USB. A origem anterior e o significado desses objetos continuam pendentes. Eles podem depender de passos anteriores do fluxo e não foram classificados como dados fixos, calibração ou biometria.

Os callbacks e as estruturas não foram executados, e nenhum conteúdo dinâmico foi coletado. Ainda é necessário reconstruir o percurso completo e seus limites antes de portar essa parte da montagem.

## Resultado e pendências

O layout completo e a condição de inclusão de um nó adicional foram delimitados, e a fonte dinâmica foi ligada a callbacks de tamanho/cópia. Isso reduz as lacunas de montagem, mas não completa o pedido de captura: há outros construtores, flags e estados, além da identificação real do tipo do participante.

Cinco destinos de chamadas e as três escritas do helper de conteúdo foram conferidos no binário fixado. A análise de condições continua manual, sem validação em runtime. Somente documentos/evidência: mantém a base de **103 testes aprovados na v0.47**, sem nova execução da suíte.

O próximo passo é rastrear quem produz os objetos copiados e delimitar os demais construtores condicionais. Probe inalterado, sem novo comando ou teste com dedo.
