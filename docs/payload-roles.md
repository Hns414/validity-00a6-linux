# Payload de inicialização, habilitação de escrita e proteção

## Dois blocos diferentes com o mesmo prefixo

A comparação foi ampliada para o literal público `db_write_enable`, separadamente de `init_hardcoded`. No commit [a6bbc21 do python-validity](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/blobs_90.py), a família 90 contém:

| Literal | Comprimento do frame | Bytes após prefixo de cinco bytes |
| --- | --- | --- |
| init_hardcoded | 485 | 480 |
| db_write_enable | 1765 | 1760 |

Ambos começam com o mesmo prefixo de cinco bytes e ambos os corpos têm comprimento múltiplo de 16, mas a correspondência acaba exatamente no byte 5. Os blocos completos são diferentes. Nas famílias 97/9a/9d ocorre a mesma distinção: init com 581 bytes e write-enable com 3621; os três write-enable dessas famílias são iguais entre si no commit examinado.

O [inventário ampliado](evidence/init-write-enable-comparison.json) registra comprimentos, hashes, igualdade e prefixos sem publicar payload. Isso fornece um contraexemplo concreto à atribuição de finalidade ou de proteção apenas pelo prefixo/alinhamento.

## Correspondência adicional na DLL Dell

Na DLL Dell fixada por SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`, a entrada **57**, registro RVA **0x13d530**, tem 1764 argumentos. Eles coincidem integralmente com `blobs_90.py:db_write_enable` sem seu opcode inicial. Recolocar 0x06 produz o frame público de 1765 bytes com SHA-256 `fd5a68c1d323974f6cef2ab5a5cd5f1fd0a52d6bd520b806141327057a161263`.

O registro compartilha versão 6.7/build 164 com o ramo de inicialização investigado, mas tem máscara **0x10008**, distinta de **0x4000**. Não foi executado o seletor para esse registro, nem rastreada sua solicitação até uma operação do 00a6. A [evidência](evidence/write-enable-dell-comparison.json) registra os campos e a comparação em memória, sem exportar os argumentos.

Portanto, a identidade anterior da entrada 55 com init_hardcoded não deve ser confundida com a entrada 57 de write-enable. Isso também não prova que init_hardcoded seja incapaz de modificar estado: apenas separa duas sequências de bytes e seus usos públicos.

## Finalidade observável e proteção não demonstrada

Em [flash.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/flash.py), o literal write-enable é enviado antes de operações de alteração de flash. Isso sustenta seu papel no fluxo público, sem decodificar as operações internas. O nome do símbolo não é especificação do 00a6.

O projeto [Metallica MIS, revisão fixada](https://github.com/wdes/Synaptics-Metallica-MIS-rs/blob/9014965cd6f524b92290cf55ff7210c7ef7690cb/src/blobs.rs), descreve cápsulas opacas para 06cb:009a e atribui validação de assinatura/habilitação de escrita ao respectivo bloco. Essa descrição é uma afirmação do projeto relacionado, não verificação independente do mecanismo no 00a6. Não se usa essa descrição para anunciar assinatura validada, cifra identificada ou persistência compreendida aqui.

As rotinas AES/HMAC do python-validity examinadas pertencem ao transporte TLS e ao armazenamento de chaves. Não foi encontrada nesses trechos uma rotina que descriptografe e valide o corpo de init_hardcoded. Aplicar o decoder TLS a esse corpo só porque há alinhamento seria uma hipótese sem suporte de fluxo de dados.

**Estado da investigação:** proteção interna, conteúdo executável e efeitos do bloco de 484 argumentos ainda não foram demonstrados. Não foram tentadas chaves do host, lidas áreas privadas do sensor ou executados blobs para resolver essa lacuna.

## Reprodução e validação

A ferramenta original mantém o comportamento anterior por padrão. A opção explícita abaixo inclui write-enable e usa schema 2 para o inventário ampliado:

```sh
python3 tools/compare_init_blobs.py /path/to/libfprint /path/to/Validity91 /path/to/python-validity --include-write-enable
```

O código só seleciona atribuições literais permitidas, rejeitando expressões dinâmicas e duplicação. Não importa módulos upstream, não escreve payloads e não acessa USB. A execução padrão foi novamente comparada ao inventário schema 1 publicado e permaneceu idêntica.

Dois testes adicionais verificam inclusão somente por opção e rejeição de inicializadores inválidos/dinâmicos/duplicados. `make test` passou com 67 testes sem skips. O probe ativo não mudou. Não há teste de hardware ou com dedo nesta etapa; a próxima análise deve buscar uma interpretação do formato ancorada no consumidor do dispositivo ou em documentação primária, distinguindo isso da criptografia do transporte.

## Documentação primária complementar

A [revisão de documentos dos fabricantes](vendor-security-context.md) registra proteção de patches para VFS495 e assinatura de partições para o escopo VFS75xx com flash externa, sem transferir essas conclusões ao formato do 00a6. A proteção interna continua pendente.
