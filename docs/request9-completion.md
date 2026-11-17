# Conclusão da requisição 9 e entrega do corpo

Análise estática manual da DLL fixada, continuando a [requisição 9](post-preparation-request9.md) e o [formato candidato de resposta](capture-reply-layout.md). A [evidência](evidence/request9-completion.json) contém sete destinos de chamadas conferidos. Não houve execução no sensor.

## Caminho demonstrado

O callback **0x56ab0**, instalado pelo wrapper da requisição 9, recebe status e um descritor de corpo: DWORD de comprimento em +0 e ponteiro em +8. Ele grava o status recebido no objeto de conclusão e, quando esse status é zero:

- Com comprimento positivo, exige ponteiro de conteúdo não nulo, cria um descritor local e chama **0x5e3d0 em 0x56bbb**.
- O wrapper obtém o contexto por 0x7ade0. Para descritor não nulo, aceita classe interna 1 e chama **0x91020 em 0x5e49d**. Outras classes seguem erro nesse wrapper.
- O parser 0x91020 verifica a assinatura 0x30000288, armazena uma cópia no contexto e chama **0x91170 em 0x91156**, que constrói a referência à região de palavras já documentada.

Isso liga o parser ao caminho de conclusão da requisição, além da descrição isolada de seu formato. Não identifica o significado das palavras nem estabelece que a resposta seja uma imagem.

## Saída opcional ao chamador

Depois de sucesso do wrapper, se o campo +0x20 do objeto de conclusão apontar para um descritor de saída, o callback grava nele o comprimento, aloca um buffer desse tamanho e copia **o corpo recebido inteiro**, incluindo seu cabeçalho. Não entrega apenas a região de palavras do parser.

O parser mantém sua própria cópia no contexto. Portanto, a cópia opcional para o chamador e a referência interna às palavras são objetos distintos. Uma implementação original deverá especificar propriedade e limites dessas saídas; não deve reproduzir automaticamente os ponteiros da DLL.

Com comprimento recebido igual a zero, o callback pula o processamento do corpo e, quando há saída opcional, grava comprimento zero e ponteiro nulo. Isso é um ramo do callback, não evidência de sucesso operacional de captura com resposta vazia. O status do transporte recebido e o retorno local do callback também são campos distintos.

Ao sair, o callback chama 0xd5990 com o campo +8 do objeto de conclusão. A primitiva por trás desse helper não foi classificada nesta etapa.

## O que essa ligação não resolve

Na cadeia aqui delimitada, não apareceu ligação com **0x85f60**, o [consumidor criptográfico isolado](isolated-block-consumer.md). Isso não exclui transformação anterior no transporte ou outro processamento posterior. A posição exata de qualquer descriptografia de dados de aquisição continua pendente.

O inspetor offline existente aceita o corpo candidato com seus limites conservadores. Ele continua sem USB e sem interpretação de pixels, dimensões ou eventos de dedo. Não há novo comando para o participante executar.

Próximo trabalho: seguir os consumidores da saída opcional e da referência interna no contexto a partir dos chamadores do wrapper. Priorizar esses caminhos alcançáveis antes de atribuir função de captura a rotinas sem referências demonstradas.

Somente documentação/evidência: sete chamadas conferidas e diff revisado. Probe inalterado; base de 103 testes aprovados na v0.47, sem repetição nesta etapa. Nenhuma inicialização, captura ou teste com dedo realizado.
