# Políticas configuradas no caminho WinUSB

Continuação da [fronteira entre leitura e registros](readpipe-record-boundary.md). Análise estática manual da DLL fixada. A [evidência](evidence/pipe-policy-setup.json) registra associação da API, quatro chamadas indiretas, seis âncoras de argumentos e um chamador adicional conferidos. Nenhuma política foi aplicada ao hardware.

## Associação da API

O inicializador obtém **WinUsb_SetPipePolicy** pelo nome em RVA 0x21c898, referenciado em **0xf034b**, e guarda o resultado no slot **+0x60** do objeto WinUSB. Esse slot é usado pelas chamadas de política abaixo. Não confundir com +0x50/+0x58, associados a políticas de energia.

## Inicialização examinada

A função **0xf04f0** define localmente o DWORD **0x7d0 (2000)** e, no caminho que supera as consultas e operações anteriores, faz:

| Chamada | Seleção do pipe por QueryPipe | Política | Comprimento do valor | Valor |
| --- | --- | --- | --- | --- |
| 0xf07e7 | Alternate setting 0, índice 1 | 3 | 4 bytes | 2000 |
| 0xf088e | Alternate setting 0, índice 0 | 1 | 1 byte | 1 |
| 0xf08e8 | Alternate setting 0, índice 0 | 3 | 4 bytes | 2000 |

A documentação oficial identifica **política 3 como PIPE_TRANSFER_TIMEOUT, em milissegundos**, e **política 1 como SHORT_PACKET_TERMINATE**, aplicável a transferências OUT. Esta última permite terminação por pacote de comprimento zero nas condições descritas pela API. Fonte: [políticas WinUSB](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/winusb-functions-for-pipe-policy-modification).

Portanto, o valor 2000 configura timeout inicial de dois segundos nesse caminho; não é prazo global de captura, cancelamento do programa inteiro ou timeout obrigatório para o futuro driver Linux.

Conforme a [ordem de endpoints coletada do sysfs](evidence/target-endpoint-order-2026-11-16.json), os índices 0 e 1 correspondem respectivamente a 0x01 OUT e 0x81 IN, **se** a consulta Windows usar essa mesma configuração e ordem. A correspondência é estática/condicional; nenhuma chamada Windows foi observada no participante.

Falhas das consultas e das chamadas de política levam a saídas de erro no inicializador. Encontrar os argumentos no código não demonstra que as políticas estejam ativas no estado real do leitor.

## Timeout pode ser alterado depois

O helper **0xf1400**, chamado em **0xef67c**, recebe índice de pipe e valor DWORD do chamador, consulta o pipe e aplica novamente política 3 em **0xf14e9**. Logo, 2000 não deve ser tratado como valor fixo durante toda a sessão. A seleção de todos os chamadores superiores desse ajuste permanece pendente.

## Leituras curtas e excedentes

Nas quatro chamadas diretas ao slot +0x60 examinadas foram observados apenas IDs 1 e 3. Não foram encontrados nesses pontos ajustes de IDs 4, 5 ou 6, associados na documentação a políticas de leituras curtas e tratamento de excedentes. Isso não prova ausência de ajustes por aliases indiretos ou em outro componente, nem autoriza assumir os defaults como estado observado do hardware.

A política 1 identificada no pipe de índice 0 controla terminação de **escritas OUT**. Ela não estabelece enquadramento de leituras IN em registros de aplicação. Timeout também não associa cada resposta a um único registro. Portanto, o contrato multirregistro continua aberto.

## Impacto na implementação

Nenhuma política ou timeout do probe foi alterado. O Linux usa um transporte diferente, e os limites de prazo/cancelamento precisam continuar explícitos nesse transporte; não copiar números da DLL como garantia de comportamento equivalente.

Próximo passo: seguir o ajuste de timeout até os chamadores superiores e separar prazo de operação, tamanho recebido e critério de fim de resposta. Mudança documental, sem repetir a suíte: base de **119 testes aprovados na v0.66**. Sem USB, captura ou teste com dedo.
