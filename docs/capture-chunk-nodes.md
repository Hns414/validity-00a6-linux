# Nós do host e blocos tipo/tamanho

Análise manual da DLL fixada, com [evidência e chamadas conferidas](evidence/capture-chunk-nodes.json). Sem execução da DLL ou transferência USB.

## Busca estrutural de blocos

Na preparação da requisição 9, 0x7ca38 chama 0x82eb0. Esse helper busca tipos 0x2f e 0x34 usando 0x70db0 em 0x82f90 e 0x8303f. A rotina de busca:

- Exige pelo menos quatro bytes antes de ler o cabeçalho.
- Lê dois WORDs little-endian: tipo em +0 e tamanho do conteúdo em +2.
- Confere a disponibilidade de `4 + tamanho` em 0x70e6d.
- Compara o tipo procurado e, quando não corresponde, avança por `4 + tamanho` em 0x70ea4.

Isso confirma uso do formato estrutural tipo/tamanho/conteúdo em um caminho da DLL, coerente com o formato público documentado na [etapa anterior](capture-reply-layout.md). Não fornece semântica para os conteúdos nem prova identidade dos programas entre sensores.

## Construção de um bloco vazio

O builder também chama 0x87910 em 0x7ca64. Esse construtor monta um cabeçalho de quatro bytes com o tipo recebido e tamanho zero, depois chama 0x877f0 em 0x8797e para criar um nó. A rotina insere o nó em uma lista do host.

Portanto, blocos de tamanho zero existem no caminho examinado. Não os tratar automaticamente como fim de sequência. Um cabeçalho de quatro zeros pode ser consumido estruturalmente como tipo zero/tamanho zero, mas isso não determina seu significado: não generalizar a regra de quatro zeros do builder para toda sequência de blocos.

## O nó não é o frame

O helper 0x877f0 aloca 0x20 bytes de metadados do host mais espaço para o buffer. Guarda o comprimento em WORD +0x12 e um ponteiro para o buffer em +0x18. Quando recebe origem não nula, copia o buffer em 0x878d0; com origem nula, zera esse espaço.

O builder final de 0x02 usa esse comprimento e ponteiro, não a estrutura inteira de nó. Os links da lista e outros campos do host não pertencem ao frame. A forma de um construtor vazio e do lookup não prova que todos os outros construtores de nós tenham sido compreendidos; seus consumidores e modificações de conteúdo continuam pendentes.

O comprimento de entrada do alocador é DWORD, enquanto o campo armazenado no nó é WORD. Não foi feita auditoria completa das restrições impostas pelos chamadores. O projeto não reproduz truncamentos implícitos nem presume que isso aceite qualquer tamanho no sensor.

## Inspetor original offline

```sh
python3 tools/inspect_capture_chunks.py /caminho/blocos-sinteticos.bin
```

A entrada é uma sequência de blocos sem o cabeçalho de cinco bytes de 0x02. O inspetor exige cabeçalhos completos, conteúdo integralmente disponível e consumo de todo o arquivo, com orçamento de análise de 65536 bytes. A leitura é limitada ao orçamento mais um byte para detectar excesso.

A saída contém apenas total de bytes, número de blocos, soma dos conteúdos e número de blocos vazios. Não exporta tipos, conteúdo, hashes ou dumps. Tipos repetidos e desconhecidos são aceitos estruturalmente; essa aceitação não constitui validação semântica. O orçamento é do projeto, não um limite confirmado do sensor.

A ferramenta não constrói nem envia pedidos e não interpreta registradores, programas ou dados biométricos. Ainda não há um conjunto completo de parâmetros de captura validado para o 00a6.

## Validação

Sete destinos de chamadas foram conferidos no binário fixado. Cabeçalhos, limites e papéis das estruturas foram interpretados manualmente. Seis novos testes cobrem contagens independentes de conteúdo/tipo, blocos vazios e repetidos, truncamentos, cabeçalho parcial, endianness e orçamento.

`make test` passou com **91 testes sem skips**. O probe ativo permanece inalterado. O próximo passo é identificar a proveniência dos buffers de programa e as modificações aplicadas pelos outros construtores; não há teste com dedo nesta etapa.
