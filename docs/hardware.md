# Hardware e evidências

Data inicial: 2026-11-16.

## Relato herdado dos documentos fornecidos

| Campo | Valor relatado | Verificação nesta etapa |
| --- | --- | --- |
| Computador | Dell Latitude 3490 | Não repetida |
| Dispositivo | 138a:00a6, Validity | Acesso USB indisponível |
| bcdDevice | 1.64 | Descritor pendente |
| USB | 2.0, full speed, 12 Mbps | Descritor pendente |
| Interface | vendor-specific, cinco endpoints | Endereços/tipos pendentes |
| Ambiente | EndeavourOS, GNOME, Wayland, x86_64 | Relato inicial |
| Cadastro | fprintd-enroll: No devices available | Não repetido |

## Observação local desta sessão

Consultas somente leitura retornaram libfprint 1.94.100-2, fprintd 1.94.5-2 e kernel 7.3.4-arch1-1. `lsusb -d 138a:00a6` falhou com `unable to initialize libusb: -99`; isso não prova ausência do sensor. Nenhum comando de protocolo foi enviado.

## Próxima coleta

No host com acesso ao sensor, executar `lsusb -d 138a:00a6`, `pacman -Q libfprint fprintd` e `uname -r`. Inspecionar localmente `lsusb -v -d 138a:00a6`; registrar somente campos selecionados: VID/PID, bcdDevice, bcdUSB, classe/subclasse/protocolo, configurações/interfaces, quantidade e endereços/tipos/tamanhos dos endpoints. Não publicar iSerial, service tag ou a saída completa.

Não assumir que os cinco endpoints têm os mesmos endereços ou funções de outro sensor. Modelo comercial, protocolo, versão de firmware, mecanismo de matching e necessidade de pareamento seguem desconhecidos.

## Verificação independente por sysfs — 2026-11-16

A limitação anterior de libusb foi contornada por leitura dos metadados já expostos pelo kernel. Nenhum dispositivo USB foi aberto, reinicializado ou recebeu comandos. O [JSON sanitizado](evidence/usb-138a-00a6-2026-11-16.json) registra somente campos permitidos; inteiros hexadecimais dos descritores são serializados em decimal (por exemplo bcdDevice 356 = 0x0164, revisão BCD 1.64).

Confirmados: VID:PID 138a:00a6; USB 2.00, 12 Mbps; classe/subclasse/protocolo de dispositivo ff/10/ff; uma configuração e uma interface; interface 0, alternate 0, classe ff/00/00.

| Endpoint | Tipo/direção | MaxPacketSize | bInterval bruto |
| --- | --- | --- | --- |
| 0x01 | Bulk OUT | 64 | 0 |
| 0x81 | Bulk IN | 64 | 0 |
| 0x82 | Bulk IN | 64 | 0 |
| 0x83 | Interrupt IN | 8 | 4 |
| 0x84 | Interrupt IN | 16 | 10 |

O INF Dell identifica o nome comercial VFS7552; o silício interno, firmware, funções específicas dos endpoints e mecanismo biométrico desta variante continuam sem verificação. As seções anteriores preservam o histórico do diagnóstico inicial.
