# Consumidor alcançável da região de palavras

Continuação da [entrega ao processamento do host](host-processing-handoff.md), por análise estática manual da DLL fixada. A [evidência](evidence/word-region-consumer.json) registra oito destinos de chamadas conferidos. Sem execução do driver ou USB.

## Três estruturas distintas

A função 0xa3780 recebe um descritor de chamada. O campo +0x40 desse descritor aponta para o estado preparado pela função 0x46fd0; o método o guarda em seu novo estado de processamento +0x160. O campo +0 do descritor contém o contexto, guardado no estado de processamento +0x10.

Portanto, offsets iguais em estruturas diferentes não representam os mesmos dados. Em particular, os campos +0x28/+0x30 do descritor de chamada não são os campos de resposta +0x28/+0x30 do estado da captura. Esta etapa explicita a indireção sem alterar a associação do método demonstrada anteriormente.

## Metadados e preparação do host

A chamada **0xa39cf → 0xa57b0** consulta **0xa5810 → 0x4ee00**, usando o DWORD inicial do estado de processamento como chave. É o mesmo lookup de metadados por tipo [já usado no ajuste de repetição](program-repeat-patch.md). O ponteiro fica em +0x170; o WORD de metadados +6 é copiado para o DWORD +0x2e8.

Depois, **0xa3a01 → 0xa5030** prepara buffers e propriedades do host, usando metadados e argumentos do descritor. Seus tamanhos não foram classificados como dimensões de uma imagem. Em seguida, **0xa3a2f → 0xa5880** inicia o consumo dos dados armazenados.

## Ligação ao conteúdo da resposta

No ramo com contexto não nulo, 0xa5880 chama **0xa5a5a → 0x5e220**. Este helper obtém o contexto interno por 0x7ade0 e devolve:

| Saída | Origem no contexto interno |
| --- | --- |
| Ponteiro | +0x90 |
| Comprimento DWORD | +0x88 |

São os campos preenchidos pelo parser da resposta 0x30000288. O getter não lê USB nem copia o conteúdo: entrega uma referência aos dados existentes no host. O contrato de duração dessa referência continua pendente de auditoria completa.

Quando existe ponteiro de conteúdo, **0xa5ae8 → 0xa2470** recebe a região de palavras, seu comprimento em bytes, o DWORD do estado de processamento +0x188, o ponteiro dos metadados e o buffer de saída do host em +0x168. Essa chamada fecha um consumidor alcançável da resposta; a transformação dentro de 0xa2470 ainda precisa ser reconstruída.

A função também possui ramo sem contexto, que obtém dados diretamente do estado da captura. Esse ramo alternativo não deve ser confundido com o caminho do chamador 0x46fd0 que fornece contexto.

## Outro bloco, ainda sem semântica

Após o consumidor, se o estado +0x190 contiver outro buffer, há busca de nó **0x2d** por **0xa5b4d → 0x70db0**, pulando quatro bytes iniciais desse buffer. Quando encontrado, o código exige tipo 0x2d e comprimento de conteúdo 0x1c (28 bytes) antes de copiar seus campos. A origem completa desse buffer e o significado do bloco ainda não foram estabelecidos. Não concluir que se trate de imagem ou de configuração universal do sensor.

## Resultado e pendências

Agora há ligação demonstrada da resposta até 0xa2470, passando por contexto, getter e metadados. Ainda não há ligação demonstrada com a rotina criptográfica isolada 0x85f60, nem semântica de pixels, evento de dedo ou autenticação.

Próximo passo: delimitar a transformação 0xa2470 e a origem do buffer adicional. Somente documentação/evidência: oito chamadas conferidas, sem novo código de transporte, USB ou teste com dedo. A base permanece em 103 testes aprovados na v0.47; suíte não repetida nesta etapa.
