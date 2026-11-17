# Laço de registros e contrato da cópia final

Continuação dos [contratos de transformação](transform-helper-contracts.md). Análise estática manual da DLL fixada; a [evidência](evidence/multirecord-copy-contract.json) registra sete âncoras e a chamada de cópia final conferidas. Sem tráfego ou conteúdo do participante.

## Comprimento e condição de parada

Na entrada de 0x774e0, o campo auxiliar +0x12c é zerado. Cada passagem pelo ramo de aplicação 0x17 grava a diferença de ponteiros nesse campo em 0x77cfb. A operação é **atribuição**, não soma; o campo não representa automaticamente o total de vários registros.

No início de uma iteração, o parser verifica um byte de parada quando:

`comprimento auxiliar != 0 OU modo auxiliar == 0xff`

A condição é OR, não AND. Se o byte corrente for zero ou 0xff, segue para a saída comum sem criar erro naquele teste. Isso é um comportamento do parser fixado; não demonstra que qualquer byte zero/0xff ao final seja padding universal do protocolo.

Após processar um registro sem erro, o ponteiro corrente avança para `início do registro + 5 + L`. Se ainda estiver antes do fim da entrada, o laço pode continuar. O teste de parada não proíbe por si só um segundo registro cujo tipo seja 0x17; a aceitação ainda depende dos estados e verificações internas.

## Cópia final sem concatenação demonstrada

Depois do parser, 0x749e0 chama **0x74b79 → 0xe79f0** com origem em **buffer recebido original +21** e comprimento obtido de auxiliar +0x12c. O início usado nessa chamada não é atualizado para o início do último registro de aplicação pelo laço examinado.

Assim, não há concatenação demonstrada nesse nível. Em entrada com vários registros de aplicação, simplesmente usar o último comprimento como tamanho da região no primeiro endereço não equivale a entregar o conjunto dos conteúdos. Ainda falta estabelecer quais combinações são permitidas pelos chamadores e pelo transporte no fluxo real.

Isso impede adotar esse contrato diretamente em um driver novo. Não demonstra falha explorável, aceitação de registros criptograficamente inválidos ou existência de respostas multirregistro no 00a6.

## Inspetor original de envelopes

```sh
python3 tools/inspect_record_envelope.py /caminho/envelope-sintetico.bin
```

A ferramenta conta registros com cabeçalhos de cinco bytes, versão 3/3 e comprimento big-endian. Aceita estruturalmente os tipos 0x14 a 0x17 e retorna somente totais de bytes, quantidade de registros, quantidade de registros de aplicação e um indicador de envelope com exatamente um registro de aplicação.

Sua política é deliberadamente estrita: registros completos, comprimento declarado não zero, ausência de cauda ou marcadores extras e orçamento de **65536 bytes**. Essas regras são o escopo local do inspetor, não uma reprodução de todas as aceitações da DLL. A leitura de arquivo é limitada ao orçamento mais um byte para detectar excesso.

O conteúdo não é impresso, armazenado em outro arquivo, descriptografado ou autenticado. Um envelope com estrutura aceita pode conter dados arbitrários; os indicadores de validação criptográfica e de hardware permanecem falsos. O indicador de um único registro também não prova que ele seja uma resposta válida para leitura 0x78.

Este inspetor recebe envelopes candidatos; o inspetor `inspect_read78_reply.py` recebe um corpo posterior ao tratamento de transporte/status. Não intercambiar essas camadas nem remover prefixos por tentativa.

## Resultado e próximos pontos

O comprimento auxiliar foi delimitado como uma seleção/sobrescrita por ramo de aplicação, e a cópia superior foi distinguida de concatenação. Para um futuro experimento delimitado, ainda precisamos demonstrar o contrato de resposta única ou implementar uma normalização original que preserve a associação entre cada conteúdo e seu comprimento, além dos limites e verificações criptográficas.

Seis testes novos cobrem registro único/múltiplos, contagem por classe, independência do conteúdo, truncamentos, comprimentos, versão/tipo, caudas, orçamento e CLI sanitizada. `make test` passou com **118 testes sem skips**. Sete âncoras e uma chamada foram verificadas no binário separadamente; os testes não executam a DLL.

Probe inalterado, sem USB, captura ou teste com dedo nesta etapa.
