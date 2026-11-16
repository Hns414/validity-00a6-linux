# Worker de eventos, pipe 3 e cancelamento

Análise estática da DLL Dell fixada pelo hash da [evidência](evidence/event-worker-analysis.json), complementada por leitura dos descritores já armazenados no sysfs. Nenhuma DLL foi executada e nenhuma transferência USB foi iniciada. RVAs relativos à ImageBase 0x180000000.

## Registro e worker

O wrapper 0xe7520 alcança 0xedcb0, que monta requisição interna **0x938ae060**. A tabela de dispatch leva ao case 0xee616, instala o adaptador 0xeedb0 e encaminha para 0xef310. A segunda tabela leva ao case 0xef531 e à rotina 0xf1970.

Essa rotina guarda callback/contexto/tipo nos offsets +0x48/+0x50/+0x58 da estrutura inferior, marca +0x5c e sinaliza um objeto do host. O worker 0xf1aa0 aguarda esse objeto e, quando habilitado, chama 0xf1760 com buffer local e capacidade **7** em 0xf1b66. Após a operação prepara um descritor com tipo, status, tamanho e ponteiro, limpa o registro local de callback e o chama em 0xf1c1c. Isso delimita entrega assíncrona, não uma sequência de polling 0x77.

## Caminho WinUSB e vínculo ao endpoint

Quando o campo inferior +0x60 está ausente, 0xf1760 usa o ramo 0xf18dd: chama 0xf0f50 em 0xf191b com alternate setting 0 e índice de pipe **3**. O wrapper consulta WinUsb_QueryPipe em 0xf0fe9 e usa o PipeID retornado ao chamar WinUsb_ReadPipe em 0xf104d.

A [documentação primária de WinUsb_QueryPipe](https://learn.microsoft.com/en-us/windows/win32/api/winusb/nf-winusb-winusb_querypipe) define PipeIndex como posição ordinal dos endpoints da interface, começando em zero; ele não é bEndpointAddress. A consulta interpreta os descritores da configuração.

Nesta sessão, a ferramenta original leu **somente** o arquivo `descriptors` já em cache no sysfs, após selecionar exatamente um 138a:00a6. O [resultado sanitizado](evidence/target-endpoint-order-2026-11-16.json) preserva a ordem original:

| Índice | Endpoint | Tipo | Máximo por pacote |
| --- | --- | --- | --- |
| 0 | 0x01 | bulk OUT | 64 |
| 1 | 0x81 | bulk IN | 64 |
| 2 | 0x82 | bulk IN | 64 |
| 3 | 0x83 | interrupt IN | 8 |
| 4 | 0x84 | interrupt IN | 16 |

**Inferência delimitada:** para essa configuração e interface, o ramo WinUSB de índice 3 corresponde ao endpoint 0x83. Não houve execução Windows para observar o PipeID em runtime. A ordem foi lida do fluxo binário de descritores, não deduzida da ordenação alfabética das entradas sysfs.

A capacidade de sete bytes é compatível com pacote máximo de oito, mas não demonstra comprimento real ou semântica dos eventos. Tamanho máximo de pacote não exige que a aplicação receba sempre oito bytes.

## Fonte alternativa e cache

Quando +0x60 está presente, a rotina usa uma fonte alternativa via 0xefeb0 e trata um tipo local 0x12. Essa fonte ainda não foi identificada; não atribuir o mesmo endpoint a esse ramo.

O adaptador 0xeedb0 copia até sete bytes para cache local em contexto +0x20 antes de subir pela cadeia de callbacks. A leitura de estado por requisição interna **0x938ae038** chega a 0xeed10 e copia sete bytes desse cache; não é necessariamente uma nova leitura USB. A cadeia superior ainda traduz campos conforme tipo solicitado.

O status do descritor de conclusão, o tipo registrado e os bytes do cache são entidades distintas. Não foi comprovado qual campo significa toque, retirada ou captura concluída. As estruturas intermediárias não devem ser confundidas com um frame bruto só porque têm sete bytes.

## Cancelamento

A requisição interna **0x938ae064** passa pelo case 0xee521, depois 0xef579 e 0xf1a00. A rotina limpa habilitação e campos de callback. Quando recebe argumento 1 e há registro ativo, chama 0xf1250 com índice de pipe 3.

Esse helper consulta o pipe e chama o slot +0x38 do mesmo objeto WinUSB. A resolução em 0xf02cf liga o slot a **WinUsb_AbortPipe**, chamado em 0xf1300. É uma operação de cancelamento de pipe nesse ramo, não factory reset ou reversão de efeitos persistentes. A interação completa entre cancelamento, leitura em andamento e duração da espera ainda precisa ser reimplementada com orçamento finito e buffers válidos.

## Coleta reproduzível e validação

```sh
python3 tools/collect_endpoint_order.py
```

O coletor original só lê atributos numéricos de seleção e descritores em cache. Não abre `/dev/bus/usb`, não solicita novos descritores ao sensor e não publica serial, nomes, índices de strings ou topologia. Seu parser é restrito a uma configuração, interface 0 e alt 0; recusa formatos fora desse escopo, truncamentos, contagens divergentes e endpoints duplicados. A leitura tem limite de tamanho.

Cinco testes novos verificam preservação de ordem, comprimentos, identidade, interface, duplicatas, privacidade e seleção única. `make test` passou com **73 testes sem skips**. Sete destinos de chamadas e duas tabelas de dispatch foram conferidos no binário. Os papéis e branches continuam análise manual.

O probe ativo permanece inalterado. Não é necessário repetir testes ou colocar o dedo agora. A próxima questão é interpretar os bytes do cache e ligar a preparação de Start ao armamento desse worker, antes de propor detecção real de toque.
