# Produtor do descritor de programa

Continuação da [origem imediata do programa](capture-program-origin.md). Análise manual da DLL fixada, com [evidência de chamadas e armazenamento](evidence/program-descriptor-selection.json). Sem executar driver ou acessar USB.

## Da abertura ao campo +0x250

No caminho externo de abertura já examinado, **0x6584b chama 0x5f430**. Essa rotina obtém o contexto e prepara parâmetros. Quando contexto +0x250 está nulo, chama **0x63620 em 0x5f598**. Se o resultado contém um descritor não nulo, guarda esse ponteiro em **contexto +0x250, em 0x5f5d0**. Quando o campo já está preenchido, pula a seleção nesse trecho.

O getter 0x700d0 retorna exatamente esse campo, como visto na chamada 0x475c1 da preparação. O descritor passa como argumento ao wrapper da requisição 9 e chega a 0x709e0 em 0x7c877, que extrai comprimento +0x34 e ponteiro +0x38. Isso fecha a ligação entre um produtor de seleção e o descritor consumido pelo builder; não resolve ainda a origem final dos bytes da tabela.

O armazenamento é um ponteiro em memória do host. Não é escrita de programa na flash do sensor, e reaproveitar esse ponteiro não demonstra ausência de outros efeitos nos passos de abertura.

## Parâmetros de seleção observados

A rotina 0x5f430 lê contexto +0x23c. Para valor 1, escolhe primeiro parâmetro **0x0c** quando o campo +0x128 vale 0xe2 ou 0xfd; nos demais casos desse ramo usa **0x18**. Para outros valores de +0x23c, prepara 0x12, mas isso não demonstra que o wrapper seguinte suporte esse contexto.

O segundo parâmetro é **0x19** e há ainda valor **0x08** passado ao wrapper. O campo contexto +0x128 é usado como identificador na seleção. Sua correspondência exata com o tipo interno do sensor continua a exigir rastreamento de origem; não identificá-lo com o PID USB.

O wrapper 0x63620 só chega ao seletor **0x906e0** quando contexto +0x23c vale 1. Outros valores seguem para erro nesse wrapper. Portanto, preparar 0x12 em um ramo anterior não comprova uma seleção funcional com esse valor.

A proximidade do par 0x18/0x19 com a referência pública `SensorCaptureProg.get` é evidência de estrutura comparável, não prova de que qualquer entrada pública seja a correta para 00a6. Os parâmetros dependem de contexto e tipo, e o valor adicional 0x08 ainda não teve seu papel completo reconstruído.

## Tabela fornecida ao seletor

Antes da seleção, 0x63620 chama 0x63470 em 0x636a7 para obter a tabela. Esse wrapper consulta **0x64750 com categoria 1**. A rotina percorre listas do host, compara um campo de categoria e outro associado ao contexto +0x23c e retorna um objeto encontrado.

O seletor 0x906e0 recebe uma tabela de ponteiros e a percorre até ponteiro nulo. Examina campos com curingas 0xffff e atributos do contexto. A classificação completa, a preferência e o produtor das listas ainda não foram reconstruídos nesta etapa. Não publicar um índice escolhido para o participante sem resolver essas dependências.

A tabela de programas não foi equiparada à tabela de 75 descritores de preparação opaca anteriormente estudada. São caminhos e formatos diferentes; compartilhar versão do firmware não torna suas entradas intercambiáveis.

## O que ficou resolvido e o que permanece

Ficou identificado um produtor concreto do descritor consumido no builder, seu armazenamento e reaproveitamento no host e o seletor que o fornece. Permanecem a proveniência final da tabela/programas, a identificação do campo +0x128 no participante e os demais critérios de seleção. Também continuam pendentes os efeitos dos programas e a recuperação de operações ativas.

Seis destinos de chamadas e a instrução de armazenamento foram conferidos no binário fixado. O fluxo e os papéis continuam análise manual, sem seleção observada em runtime. Somente documentos/evidência: mantém a base de **91 testes aprovados na v0.37**, sem nova execução da suíte. Probe inalterado, sem teste com dedo.

A [origem da classe de contexto](product-context-class.md) foi ligada à tabela de produtos da ROM; isso não identifica o tipo interno nem o registro da tabela de programas.

A [análise do registro das tabelas](program-table-registration.md) corrige a categoria para 1 e localiza a tabela estática de 21 entradas.
