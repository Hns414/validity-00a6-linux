# Fronteira entre leitura WinUSB e registros

Continuação do [contrato multirregistro](multirecord-copy-contract.md). Análise estática manual da DLL fixada; a [evidência](evidence/readpipe-record-boundary.json) registra três chamadas, três âncoras e a associação à API conferidas. Nenhuma leitura USB foi executada.

## O caminho inferior demonstrado

No ramo de troca 0xeea70, a chamada de escrita **0xeeaa5 → 0xef7d0** é seguida, somente após sucesso, por **0xeead9 → 0xef750**. Nesse corpo há uma chamada de leitura no caminho examinado; não há laço que delimite registros de aplicação por seus cabeçalhos.

O wrapper **0xef750** chama **0xef7a3 → 0xf0f50**. Quando o resultado dessa chamada é sucesso, copia para a saída o número de bytes transferidos em **0xef7bf**. Ele não converte essa quantidade em contagem de registros nem inspeciona tipo/versão/comprimento dos envelopes.

A função 0xf0f50 consulta o pipe pelo slot +0x20 em 0xf0fe9 e chama o slot **+0x28 em 0xf104d**. Esse slot foi associado a **WinUsb_ReadPipe** pelo inicializador, com nome referenciado em 0xf0279. A associação foi reconferida no arquivo, incluindo o nome da API na seção mapeada.

## O que a API garante — e o que ainda precisa de evidência

A documentação oficial de [WinUsb_ReadPipe](https://learn.microsoft.com/en-us/windows/win32/api/winusb/nf-winusb-winusb_readpipe) descreve buffers, comprimento solicitado e bytes transferidos, além de comportamentos dependentes das políticas do pipe. A [documentação das políticas](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/winusb-functions-for-pipe-policy-modification) permite alterar aspectos de conclusão e tratamento de transferências.

A inferência relevante é limitada: uma chamada dessa API, isoladamente, não demonstra enquadramento nos registros de cinco bytes examinados em 0x774e0. Não assumir que um pacote USB, uma chamada de leitura e um registro de aplicação tenham a mesma fronteira.

As políticas efetivamente configuradas no pipe dessa DLL ainda não foram integralmente auditadas, e o comportamento real do 00a6 não foi observado nesse estado. Portanto, esta etapa não afirma se uma resposta real vem sempre inteira, fragmentada ou com vários registros. Apenas retira a suposição de que a chamada inferior provaria resposta única.

## Consequência para a arquitetura original

O projeto passa a separar explicitamente três contratos:

| Camada | Responsabilidade |
| --- | --- |
| Transporte | Informar bytes realmente acessíveis, capacidade e resultado da operação; gerir prazo e cancelamento |
| Enquadramento/normalização | Validar envelopes e associar cada conteúdo ao seu comprimento, preservando estado quando o contrato exigir; aplicar autenticação e transformação necessárias |
| Corpo 0x78 | Validar status na camada apropriada e então contagem/capacidade do corpo antes de usar seu conteúdo |

O [parser C recém-adicionado](read78-c-component.md) implementa somente o último contrato estrutural, depois de os requisitos anteriores terem sido estabelecidos. O inspetor de envelopes continua sendo análise offline de entrada completa; não é remontador de fluxo nem substitui validação criptográfica.

Não se deve escolher um único registro ignorando os demais nem concatenar conteúdos antes de confirmar se pertencem à mesma resposta. Essa associação ainda precisa de evidência do protocolo e do estado da requisição.

## Resultado e próximo passo

O retorno inferior foi delimitado como quantidade de bytes da leitura, sem regra demonstrada de registro único. Próximo passo: auditar as políticas efetivamente instaladas e o contrato de encerramento da resposta, mantendo separados os dados observados e a política conservadora de uma implementação nova.

Mudança documental, com três chamadas, três âncoras e associação de API conferidas. Base de **119 testes aprovados na v0.66**, sem repetir a suíte nesta etapa. Probe inalterado; sem USB, captura ou teste com dedo.
