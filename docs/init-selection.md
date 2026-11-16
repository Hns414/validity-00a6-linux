# Seleção do registro de init_00 no driver Dell

Esta etapa aprofunda a [análise estática da DLL](dell-static-analysis.md). Aplica-se exclusivamente a synaWudfBioUsb.dll com SHA-256 6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7. Nenhuma DLL foi carregada e nenhum comando adicional foi enviado ao sensor.

## Do payload para a tabela

A coincidência dos 500 bytes sem opcode levou ao ponteiro armazenado em RVA 0x13c998. O consumidor usa offsets +0x44 para tamanho e +0x48 para ponteiro, situando o começo do registro em **RVA 0x13c950**, e não no começo de seus campos de versão em 0x13c960.

Uma referência ao registro aparece em RVA 0x13db68. Ela pertence a uma tabela de ponteiros iniciada em **RVA 0x13dad0**, com 75 entradas antes de um terminador nulo; o registro investigado é a entrada de índice 19. A estrutura candidata ocupa 0x50 (80) bytes. Não se publica a tabela completa ou os payloads.

## Campos observados no registro

| Offset relativo ao registro | Valor | Interpretação sustentada até agora |
| --- | --- | --- |
| +0x10 | 6 | Chave comparada a um byte no objeto de informações; candidata a major |
| +0x14 | 7 | Chave comparada ao byte seguinte; candidata a minor |
| +0x18 | 164 | Chave comparada a um inteiro de 32 bits; candidata a build |
| +0x20 | 3 | Parâmetro passado adiante; significado ainda não resolvido |
| +0x2c | 0x4000 | Campo usado em testes de máscara de inclusão/exclusão |
| +0x3c | 1 | Outra condição de seleção, ainda sem nome confiável |
| +0x44 | 500 | Quantidade de bytes copiados do payload |
| +0x48 | VA 0x18015f550 | Ponteiro para os 500 bytes que coincidem com init_00 sem opcode |

As três chaves candidatas coincidem com os valores 6.7/build 164 informados pelo participante em E1. Isso não satisfaz automaticamente as outras condições da rotina. Um campo isolado, como produto 48, tampouco estabelece o resultado da seleção completa.

## Cadeia de chamadas observada

Coordenadas RVA; nomes abaixo são descrições de análise, não símbolos originais recuperados:

| Ponto | Papel observado |
| --- | --- |
| 0x5eac0 | Caminho que obtém contexto e solicita máscara 0x4000; chamada em 0x5eb19 |
| 0x5ed80 | Wrapper que encaminha argumentos para 0x5ede0 |
| 0x5ede0 | Obtém contexto, chama o seletor, lê tamanho/ponteiro do registro, aloca/copia o conteúdo e passa o buffer para 0x62ad0 |
| 0x8fb20 | Seletor que percorre uma lista terminada em nulo; compara atributos, curingas 0xffff e máscaras; pode escolher/rejeitar candidatos conforme critérios adicionais |
| 0x62ad0 | Consulta/altera estado de contexto e encaminha um descritor de buffer ao caminho 0x53560, além de outras chamadas de preparação |
| 0x53560 | Encaminha a solicitação para infraestrutura assíncrona em 0x5a820; ainda não foi ligado integralmente à formação do pacote USB |
| 0x716f0 | Rotina que pode atribuir a tabela 0x13dad0 a um objeto, conforme um seletor; não é a prova isolada de que esse objeto esteja ativo no teste do participante |

A leitura de tamanho e ponteiro ocorre em 0x5ef71 e 0x5efc0. A chamada de seleção ocorre em 0x5ef20. O consumidor não trata somente um byte de comando: ele trabalha com um registro de atributos e um buffer de tamanho escolhido.

A inspeção encontrou também três referências diretas à mesma tabela em outros caminhos que pedem máscara 0x4. O registro investigado tem máscara 0x4000; portanto referências à mesma tabela não significam que todas essas chamadas escolham o mesmo registro. O caminho de 0x5eac0 mostra que existe uma solicitação compatível com a máscara específica, ainda condicionada ao contexto.

Strings de diagnóstico apontam para os basenames scsSensorConfig.c (seletor) e scs.c (consumidor) no build original. Isso orienta a investigação, sem recuperar símbolos ou fornecer a fonte do fabricante. Caminhos internos completos e disassembly não são redistribuídos.

## Reprodução e testes

A ferramenta [locate_init_record.py](../tools/locate_init_record.py) exige a DLL com tamanho e hash conhecidos e uma referência init_00 do libfprint fixado. Busca os 500 bytes, um ponteiro único para eles, verifica tamanho no registro e localiza referências estáticas ao registro.

```bash
python3 tools/locate_init_record.py /caminho/libfprint /local/privado/synaWudfBioUsb.dll
```

Saída: [init-descriptor-location.json](evidence/init-descriptor-location.json). Não contém payload ou dados do sensor. A ferramenta não executa o seletor, não escolhe um registro para o hardware, não gera comandos e não autoriza sua emissão. Os offsets são hipóteses estruturais sustentadas pela análise desta DLL; a ferramenta recusa outro hash, em vez de generalizá-los silenciosamente.

Seis testes novos usam somente bytes sintéticos para verificar campos/coordenadas, ambiguidade, ponteiros duplicados, tamanho incompatível e intervalos inválidos. Total da suíte: 50 testes aprovados. A extração real foi regenerada e comparada ao JSON versionado. A cadeia de chamadas e os critérios completos são análise manual de disassembly; o extrator não valida essa semântica automaticamente.

## O que falta antes de um teste ativo

- Ligar o caminho assíncrono à montagem do pacote que começa com 0x06 e verificar as transformações do buffer.
- Identificar o significado dos parâmetros e das condições restantes, sem solicitar dump bruto ou ampliar exposição de identificadores do participante.
- Determinar as operações do conteúdo carregado e suas consequências sobre memória, persistência e estado do leitor.
- Definir recuperação aplicável ao que essas operações efetivamente fizerem.

Esta etapa confirma a ligação estática entre registro, seleção e encaminhamento do payload. Ainda não prova que o registro seria selecionado no estado atual do sensor, nem que executá-lo seria adequado. Não há novo comando de hardware para o participante.

## Continuação: montagem do frame

A [análise de framing](init-framing.md) relacionou a solicitação interna 7 ao handler 0x7e540, que constrói 0x06 seguido dos argumentos. A reprodução offline resultou no frame de 501 bytes idêntico ao upstream. A ligação final entre a camada de transporte e o wrapper USB ainda não foi completada, e os efeitos do payload no sensor continuam desconhecidos.
