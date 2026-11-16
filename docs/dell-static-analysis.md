# Envelope de inicialização: análise estática do driver Dell

Data: 2026-11-16. Nenhuma DLL, instalador ou executável Windows foi executado; nenhum comando USB novo foi enviado. A análise usa os arquivos do pacote NKXR6 já identificado para Latitude 3490 e 138a:00a6. Os binários permanecem fora do repositório.

## Pista primária sobre a natureza dos blocos

Em [comentário de 2020-06-18](https://github.com/uunicorn/python-validity/issues/3#issuecomment-645873155), o mantenedor do python-validity descreve os blobs como provável código carregado e executado no sensor pelo driver Windows. A fala é uma avaliação do autor: não demonstra o formato do nosso bloco de 501 bytes, suas instruções ou seus efeitos no 00a6.

Isso reforça a necessidade de tratar o envelope 06 02 00 00 01 como estrutura ainda não resolvida, sem classificá-lo como consulta simples. O prefixo também aparece em blocos usados em reset; o significado não está estabelecido apenas pela igualdade parcial.

## Arquivos inspecionados

| Arquivo | Bytes | SHA-256 |
| --- | ---: | --- |
| synaWudfBioUsb.dll | 2.296.920 | 6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7 |
| synaBscAdapter.dll | 358.504 | 6a78cf2370219beb9115c32720a856d3c9089e6fdd66a19430ca1711f2dca53f |

Ambos são PE32+ AMD64, com ImageBase 0x180000000. A busca exata, nos bytes integrais de cada arquivo, encontrou zero ocorrências contíguas de init_00, init_04 e do prefixo completo de cinco bytes. Os blocos de referência vieram do libfprint no commit 8b6e4e39bee58de2774222e3730269def470b157.

A busca ampliada encontrou **os 500 bytes de init_00 após o opcode 0x06**, integralmente e uma única vez em synaWudfBioUsb.dll. O recorte de 496 bytes após o prefixo completo também coincide, no mesmo local lógico:

| Referência | File offset | RVA | Bytes |
| --- | --- | --- | ---: |
| init_00 sem opcode | 0x15e550 | 0x15f550 | 500 |
| init_00 após prefixo de cinco bytes | 0x15e554 | 0x15f554 | 496 |

Há ainda um ponteiro absoluto para o começo dos 500 bytes em RVA 0x13c998, precedido por um inteiro de 32 bits com valor 500 em RVA 0x13c994. Isso é compatível com um registro de tamanho/ponteiro, mas o formato da tabela e sua seleção ainda precisam ser demonstrados. O inteiro inicial dos 500 bytes é 0x01000002 em little endian; seu significado não foi determinado.

A coincidência torna plausível que o opcode seja anexado separadamente ao buffer. Não prova que esse caminho seja efetivamente escolhido para a revisão 1.64, nem quais operações o bloco executa. Nenhum recorte pesquisado de init_04 foi encontrado, e o adapter não contém os recortes pesquisados de init_00.

A ausência de correspondência do comando completo não prova ausência de seu conteúdo no driver: ele pode ser montado em runtime, transformado ou obtido de outra fonte. Tampouco demonstra criptografia ou compressão. Imports como CryptDecrypt não vinculam, por si sós, uma operação criptográfica ao bloco em questão.

## Pontos candidatos para a próxima análise

A DLL principal contém strings de diagnóstico selecionadas. Uma busca em disassembly local encontrou uma referência RIP-relative para cada uma; a tabela de runtime functions (.pdata) delimita o código que contém essa referência.

| Rótulo do log | RVA da string | RVA da referência | Intervalo RVA do código contendo a referência, fim exclusivo |
| --- | --- | --- | --- |
| CBiometricDevice::deviceInit | 0x111600 | 0x25b21 | 0x25aec–0x2611f |
| CeivMode::SetPayloadData | 0x112d80 | 0x3d958 | 0x3d928–0x3daee |
| CeivMode::GetPayloadData | 0x112da0 | 0x3bde8 | 0x3bdb8–0x3bf7e |

Esses são pontos de investigação associados a logs, não nomes de funções confirmados por símbolos de debug. Os endereços só são aplicáveis à DLL com o hash acima. A associação não prova que essas rotinas gerem init_00, nem que payload se refira ao envelope investigado.

Próxima tarefa concreta: identificar o consumidor do registro candidato em RVA 0x13c998 e seguir o fluxo de chamadas e dados desses intervalos até a montagem de comandos ou a camada USB, identificar origem e transformações do buffer e produzir uma descrição independente dos campos/efeitos. Uma cadeia de chamadas e argumentos ainda precisa ser demonstrada antes de atribuir significado aos bytes do envelope.

## Reproduzir sem executar o driver

A ferramenta [survey_vendor_dll.py](../tools/survey_vendor_dll.py) lê os arquivos como dados. Requer somente Python padrão e um clone local do libfprint contendo o commit fixado.

```bash
python3 tools/survey_vendor_dll.py /caminho/libfprint /local/privado/synaWudfBioUsb.dll /local/privado/synaBscAdapter.dll
```

Ela valida cabeçalhos/limites de seções PE32+, calcula hashes dos arquivos distribuídos pelo fabricante, conta ocorrências do comando e de recortes sem opcode/prefixo, mapeia as localizações de coincidências e somente três strings de diagnóstico permitidas para RVA/VA. Não imprime strings arbitrárias, código, payloads ou caminhos completos. O [relatório reproduzido](evidence/dell-static-survey.json) contém esses metadados. Os hashes são de arquivos públicos do driver, não de respostas potencialmente identificadoras do sensor.

Os intervalos de código da tabela foram obtidos separadamente, por objdump e leitura local da .pdata; o script não faz disassembly nem prova a semântica dessas rotinas. Não versionar DLL, disassembly completo, firmware ou dumps para reproduzir este passo.

## Por que o sandbox existente não foi executado

O [synaWudfBioUsb-sandbox](https://github.com/uunicorn/synaWudfBioUsb-sandbox/tree/f7b31df6670ca15172053653fa49c1171c5df038), commit f7b31df6670ca15172053653fa49c1171c5df038, imita o framework Windows e carrega o driver sob Wine modificado. Seu README informa que mudanças de ownership podem levar o driver a regravar e recalibrar o sensor.

O nome sandbox não significa execução sem efeitos no hardware. Nenhum executável desse projeto foi usado, nem mesmo seu modo nop. Uma eventual emulação futura precisaria de USB inteiramente simulado, ausência comprovada de passthrough e isolamento de arquivos/rede; este ambiente ainda não foi construído. Não é uma instrução para instalar Wine, executar o driver ou repetir E1/E2.

## Estado da conclusão

Confirmados: hashes/estrutura PE, correspondência integral de init_00 sem opcode na DLL principal, ausência do comando completo contíguo nos dois arquivos, três strings candidatas e coordenadas de análise. Não resolvidos: formato do envelope, função geradora, instruções/operações internas, memória-alvo, persistência e recuperação aplicável. Não há novo teste solicitado ao participante nesta etapa.

## Continuação: consumidor do registro

A [análise de seleção](init-selection.md) localizou o começo do registro em RVA 0x13c950 e sua entrada em uma tabela de ponteiros a partir de 0x13dad0. Há cadeia estática até um seletor e consumidor, com solicitação de máscara 0x4000 e cópia dos 500 bytes. O encaminhamento até a montagem USB e os efeitos do conteúdo ainda precisam ser resolvidos. Não foi executado código da DLL.
