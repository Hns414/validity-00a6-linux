# Consulta e caminhos de restauração do timeout

Continuação do [ajuste durante a sessão](runtime-pipe-timeout.md). Análise estática manual da DLL fixada, com [evidência sanitizada](evidence/timeout-query-restoration.json): associação da API, tabela de despacho, sete chamadas diretas, treze âncoras e um salto de erro conferidos. Sem execução Windows ou USB.

## Consulta ligada à API

O helper **0xee160** seleciona o pedido interno **0x938ae050**, com entrada DWORD contendo índice do pipe e saída DWORD. O dispatcher exige buffers não nulos e comprimentos exatamente 4; a tabela leva ao caso **0xef5c3**, cuja chamada **0xef622** chega a **0xf1540**.

Este último consulta alternate setting 0 pelo slot QueryPipe +0x20 em **0xf1605**, usando a entrada truncada a um byte como índice. Após sucesso, usa o endereço do endpoint retornado para consultar **política 3**, com capacidade de valor **4 bytes**, em **0xf165c**, pelo slot **+0x68**. A associação dinâmica desse slot vem do nome **WinUsb_GetPipePolicy**, RVA **0x21c8b0**, referenciado em 0xf0369 e armazenado em 0xf0383.

A [documentação oficial de WinUsb_GetPipePolicy](https://learn.microsoft.com/en-us/windows/win32/api/winusb/nf-winusb-winusb_getpipepolicy) define a consulta como síncrona, com tamanho de buffer por referência e resultado booleano. No helper examinado, falhas das duas APIs retornam erro interno 0xca; a saída do chamador só recebe o DWORD local depois do sucesso da segunda API, em **0xf168d**. Não foi identificada uma comparação posterior do tamanho devolvido com 4 nesse helper.

Assim fica fechada a ligação da consulta superior 0xe7370 à política de timeout: índice 0 pela chamada 0xe73c0 e índice 1 por 0xe73f8. No caminho anterior, auxiliar +0x518 é destino do valor consultado para índice 1. Nenhum valor efetivo de política foi observado no hardware.

## Restauração depende do caminho

Foram distinguidos três trechos da função 0x79500:

| Trecho | Condição e consequência |
| --- | --- |
| 0x7a4f9–0x7a526 | Só tenta reaplicar auxiliar +0x518 ao índice 1 se o DWORD guardado for maior que zero. |
| 0x7a61d–0x7a636 | Outro ramo tenta reaplicar esse valor ao índice 1, sem aquela comparação local com zero. |
| 0x7a0e2–0x7a120 | Depois do setter de 8000 ms ter retornado sucesso, uma falha de 0x75600 leva a gravar estado 6 e saltar a 0x7a6d6, sem passar pelos dois pontos explícitos acima nessa invocação. |

Não é correto concluir que toda saída restaura o timeout. Também **não é correto concluir que o timeout fica permanentemente alterado**: o epílogo comum libera recursos, pode chamar 0xd6160 conforme um indicador e chama 0x7af60; efeitos indiretos desses helpers e invocações posteriores da máquina de estados ainda não foram fechados. O significado operacional completo de 0x75600 não é necessário para identificar esse desvio e não foi presumido.

O caminho que ignora um valor guardado igual a zero merece distinção do caminho que o reaplica; isso é uma diferença estática de controle, sem diagnóstico de defeito no hardware ou no driver Windows.

## Requisito para a implementação original

O futuro transporte Linux precisa manter separados: prazo da operação, timeout de cada transferência e encerramento da resposta. Se introduzir configurações temporárias, deve definir quem as possui, quando são restauradas e como reportar falha de restauração sem apagar o erro principal. Esse é um requisito de projeto; nenhuma implementação ativa foi acrescentada nesta etapa.

A prova de enquadramento/tamanho da resposta continua aberta. Próximo passo: seguir os efeitos de limpeza e a transição para estado 6 antes de decidir se uma nova operação de hardware é justificável. Probe e seus prazos inalterados. Mudança documental, com base anterior de **119 testes aprovados**, sem repetir a suíte e sem teste com dedo.

A [restauração adiada pela máquina de estados](deferred-timeout-restoration.md) liga o laço superior ao estado 6: uma nova passagem pode tentar restaurar o timeout antes de devolver o erro guardado.
