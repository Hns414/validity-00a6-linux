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
