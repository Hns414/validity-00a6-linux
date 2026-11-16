# Origem imediata e modificações do programa de 0x02

Análise manual da DLL Dell fixada, com [evidência](evidence/capture-program-origin.json). Nenhum driver proprietário foi executado, e não houve USB.

## Buffer associado a descritor do host

O builder 0x7c4e0 chama 0x709e0 em 0x7c877, passando um descritor e locais de saída para ponteiro/tamanho. O helper retorna o ponteiro do campo **+0x38** e o comprimento DWORD de **+0x34** desse descritor. Quando o descritor é nulo ou -1, retorna ponteiro nulo e tamanho zero nesse caminho.

Quando há ponteiro, o builder o copia para um nó por 0x877f0 em **0x7c8ba** e insere esse nó na lista que será concatenada. Depois passa a usar a cópia armazenada em nó +0x18, não apenas o ponteiro original.

Isso estabelece a origem **imediata** do buffer. Ainda não identifica quem selecionou e preencheu o descritor, nem demonstra que seja um literal embutido, dado persistente lido do sensor ou programa gerado em memória. A rotina 0x70ae0 pode alocar/copiar um buffer para os campos +0x34/+0x38, mas nenhum chamador alcançável foi identificado nesta etapa; não apresentá-la como proveniência resolvida apenas por sua forma de setter.

## A cópia pode ser modificada

Após a cópia, 0x7c960 consulta 0x5b840. Quando esse caminho retorna 1, o builder avalia flags internas para escolher um argumento e chama **0x82eb0** em 0x7ca38, passando o buffer copiado e seu comprimento.

O helper busca blocos 0x2f e 0x34 pelo [lookup de tipo/tamanho](capture-chunk-nodes.md), consulta metadados e modifica bytes em um ramo condicionado. A interpretação completa dos campos e efeitos não foi reconstruída. Assim, mesmo que o buffer original seja localizado integralmente em uma fonte pública, isso não prova que deva ser enviado sem as transformações locais.

Não confundir esse programa de blocos usado em 0x02 com os argumentos opacos de 0x06 selecionados pelas máscaras de preparação. São pontos diferentes do fluxo; a semelhança de nomes ou de papel aparente não permite substituí-los.

## O que a referência pública acrescenta

No commit fixado a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920, [sensor.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/sensor.py) consulta `SensorCaptureProg.get` com ROM, **tipo interno do sensor** e parâmetros 0x18/0x19. Depois transforma os blocos antes de montar o comando.

A classe em [table_types.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/table_types.py) filtra major, tipo interno e dois parâmetros (com curingas), usa uma métrica de preferência da versão e concatena os blobs da entrada escolhida. A métrica completa e suas relações com o seletor Dell não foram equiparadas nesta etapa.

Os dois arquivos foram lidos localmente e conferidos contra o commit fixado, sem importar ou executar módulos upstream. Isso mostra dependências da implementação pública, não uma seleção validada para 00a6. O tipo interno do sensor do participante não foi medido/identificado pelas ferramentas atuais. **PID USB 0x00a6, produto candidato da ROM 0x30 e tipo interno são identificadores distintos.** Não preencher um com o valor de outro.

## Consequência e próximo passo

Ainda não há um programa final de captura estabelecido para o participante. O trabalho seguinte é ligar o descritor ao seu produtor e determinar como identificar o tipo interno sem expor conteúdo desconhecido. Uma nova consulta de hardware só será proposta com comando, formato de resposta e campos permitidos delimitados; não é necessário repetir E1/E2 agora.

Quatro destinos de chamadas foram conferidos no binário; o fluxo e os papéis são análise manual. Esta etapa altera somente documentos/evidência. Mantém a base de **91 testes aprovados na v0.37**, sem nova execução da suíte. Probe inalterado, sem captura ou teste com dedo.
