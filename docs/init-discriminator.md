# Predicado que distingue os argumentos de 500/484 bytes

A análise é estática e limitada à DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`. RVAs relativos à ImageBase 0x180000000. Não houve execução de DLL nem nova operação USB.

## Distinção encontrada

As duas entradas da [etapa anterior](open-order.md) diferem também no campo +0x34. O seletor 0x8fb20 calcula um discriminante pela chamada a 0x8feb0 em 0x8fbd2 e o compara com esse campo em 0x8fd67:

| Entrada | Argumentos | Campo +0x20 | Discriminante exigido em +0x34 |
| --- | --- | --- | --- |
| 19 / RVA 0x13c950 | 500 bytes | 3 | 3 |
| 55 / RVA 0x13d490 | 484 bytes | 1 | 2 |

O helper lê o ponteiro no offset +0x28 do contexto do seletor. Dentro da estrutura apontada, lê major em +0x08; se major é 6, testa o bit 0x20 do byte em +0x17. Bit zerado resulta em 3; bit ativo, em 2. Para outras versões major, o retorno observado é zero. A indireção `[base + 1 + 0x16]` em 0x8feea corresponde a +0x17, não +0x16.

Portanto, **para major 6 essas duas entradas não passam simultaneamente pelo predicado +0x34**. A análise anterior comprovou ambiguidade com os campos então disponíveis; agora há um critério adicional concreto que as distingue. Não é necessário escolher pelo menor comprimento para resolver este par quando o discriminante é conhecido.

O campo +0x20 não é o comparador que decide esse ramo: o consumidor o carrega em 0x5efdd e o passa adiante na chamada 0x5f002 para 0x62ad0. Seu papel completo continua pendente.

## Outros filtros continuam necessários

| Campo do registro | Fonte comparada no caminho examinado |
| --- | --- |
| +0x3c | Byte +0x0a da estrutura interna apontada por contexto +0x28; igualdade obrigatória |
| +0x2c | Inclusão da máscara solicitada e ausência da máscara excluída |
| +0x10 / +0x14 / +0x18 | Major/minor/build internos, com wildcard 0xffff no registro |
| +0x1c | Byte interno +0x0f, com wildcard no registro |
| +0x40 | WORD interno +0x19, com wildcard no registro |
| +0x38 | DWORD do contexto do seletor +0x128, com wildcard no registro |
| +0x30 | Argumento do chamador, com wildcard no registro |
| +0x34 | Resultado de 0x8feb0; comparação pulada somente quando o resultado do helper é 0xffff |

Os registros 19/55 compartilham os valores desses filtros publicados, exceto +0x34; o [JSON](evidence/init-discriminator-analysis.json) registra os campos pertinentes. Após os filtros há lógica de preferência/ambiguidade que considera especificidade e comprimento; ela ainda não foi reimplementada integralmente. Outros registros da tabela podem ser relevantes. Não confundir o campo +0x128 deste contexto com um campo de mesmo offset na estrutura auxiliar do transporte: são objetos distintos.

## Modelo offline original

[model_init_discriminator.py](../tools/model_init_discriminator.py) modela somente o helper, com dois inteiros de 0 a 255. Não abre arquivos de captura, importa código upstream, acessa USB ou escolhe payloads. Exemplo inteiramente sintético:

```sh
python3 tools/model_init_discriminator.py --major 6 --internal-flag-byte 0x20
```

A saída indica discriminante 2, `full_selection_evaluated: false` e `hardware_execution_enabled: false`. Os argumentos representam campos internos já identificados no driver; **não são instrução para extrair um byte de um offset presumido na resposta USB**.

Cinco testes novos verificam vetores de referência, irrelevância dos outros sete bits, efeito de alternar o bit 0x20, versões major distintas, entradas inválidas e limites/saída da CLI. `make test` passou com 57 testes sem skips. Isso valida o modelo sob o contrato documentado, não prova equivalência do seletor completo ou compatibilidade biométrica.

## Dado ainda ausente e próximo passo

A origem e a cópia da estrutura interna apontada por +0x28 ainda precisam ser rastreadas até o tratamento da resposta. Não foi comprovada nesta etapa uma correspondência entre seu +0x17 e um offset do frame USB E1. O resumo E1 publicado não contém esse campo; não se pode inferir seu valor a partir de build, produto, bcdDevice ou tamanho da resposta.

Nenhum novo campo foi adicionado ao probe ativo e não se solicita repetir E1. O próximo trabalho é verificar a origem e a normalização dessa estrutura; só então avaliar se uma observação mínima adicional é necessária. Efeitos do payload e recuperação permanecem pendentes.

## Rastreio posterior até E1

A [análise de origem](rom-discriminator.md) ligou o campo interno à resposta cleartext do handler 0x01. A opção schema 4 foi preparada para observar somente o bit candidato; sua execução no participante ainda está pendente. Isso refina a lacuna de mapeamento desta etapa sem resolver os demais filtros.
