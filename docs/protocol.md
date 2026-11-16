# Protocolo VFS7552: análise estática

Data: 2026-11-16. Escopo: driver upstream para **138a:0091**, comparado aos descritores observados do **138a:00a6**. Nenhuma mensagem abaixo foi enviada ao 00a6. Tamanhos, nomes e respostas descrevem o código do 0091; não são contratos confirmados do nosso sensor.

Fontes oficiais fixadas em `8b6e4e39bee58de2774222e3730269def470b157`:

- [vfs7552.c](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/drivers/vfs7552.c)
- [vfs7552_proto.h](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/drivers/vfs7552_proto.h)
- [fpi-usb-transfer.c](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/fpi-usb-transfer.c)

## Sequência ao abrir

`dev_open` executa reset USB, reivindica interface 0 e inicia a sequência abaixo, antes da captura. Cada transferência dessa sequência usa timeout de 3.000 ms, não um prazo global de 3.000 ms para a abertura inteira.

Envios: endpoint 0x01, bulk OUT. Respostas: 0x81, bulk IN. Capacidade solicitada e comprimento do array de exemplo são grandezas distintas.

| Etapa/array enviado | Bytes OUT | Capacidade IN | Bytes do exemplo IN | Verificação implementada no callback | Efeito no 00a6 |
| --- | ---: | ---: | ---: | --- | --- |
| cmd_01 | 1 | 64 | 38 | Sem comparação de tamanho/conteúdo nesse caminho | Desconhecido; candidato a consulta de informações |
| cmd_19 | 1 | 128 | 68 | Sem comparação de tamanho/conteúdo nesse caminho | Desconhecido |
| init_00 | 501 | 64 | 2 | Tamanho exato e conteúdo | Bloco opaco; persistência não determinada |
| init_01 | 10 | 64 | 2 | Tamanho exato e conteúdo | Possível escrita de registro, por comparação com outro projeto; não validada |
| init_02 | 6 | 64 | 6 | Tamanho exato e conteúdo | Possível leitura de registro; não validada |
| init_03 | 1 | 64 | 10 | Sem comparação de tamanho/conteúdo nesse caminho | Possível identificação de silício; não validada |
| init_04 | 6.677 | 64 | 2 | Tamanho exato e conteúdo | Bloco opaco; persistência não determinada |

A inferência sobre registros e identificação vem dos comandos 0x08, 0x07 e 0x75 em [sensor.py do python-validity](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/sensor.py). O comando 0x01 é usado ali como RomInfo e na inicialização de [usb.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/usb.py). São analogias entre implementações; não estabelecem semântica ou ausência de efeitos persistentes no 00a6.

## Captura e parada no upstream

| Operação | Envio/recepção | Timeout por transferência | Observação |
| --- | --- | --- | --- |
| Preparar captura | image_start, 13.725 bytes OUT; capacidade IN 2.048, exemplo 1.962 | 3.000 ms | Bloco opaco; resposta passa por RECV_CHECK_SIZE |
| Esperar evento | endpoint 0x83; capacidade 8, exemplos de 5 bytes | 0, sem timeout | Macro de recepção usa o caminho bulk; descritor do nosso 0x83 é interrupt |
| Consultar disponibilidade | is_image_ready, 5 bytes OUT; capacidade IN 64, exemplo de 6 | 0, sem timeout | Estado avalia o primeiro byte da resposta |
| Solicitar chunk | read_image_chunk, 5 bytes OUT | 1.000 ms | Não é consulta de identidade; faz parte da captura |
| Receber chunk | capacidade 4.806 em 0x81 | 1.000 ms | Parser verifica cabeçalho mínimo e comprimento declarado |
| Parar captura | cmd_04 e cmd_52, cada um com 1 byte OUT e resposta esperada de 2 bytes | 1.000 ms | Nomes vêm do uso no driver; efeito independente no 00a6 desconhecido |

O driver cria imagens de 112 × 112 pixels, remove oito bytes de controle por linha e usa processamento no host via FpImageDevice. Isso descreve o caminho do 0091; não demonstra a arquitetura biométrica do 00a6. Os endpoints 0x82 e 0x84 do nosso dispositivo não têm função estabelecida por esta comparação.

## Comportamentos a revisar antes de portar

1. `RECV_CHECK_SIZE` preenche `correct_reply_size`, mas deixa `data` nulo. `async_recv_cb` só verifica comprimento quando `data` não é nulo; portanto o nome da macro não corresponde a uma verificação efetiva de tamanho nesse callback. Um parser próprio deve validar comprimento antes de acessar qualquer campo. Esta é uma observação estática, sem teste de impacto no hardware.
2. O executor de sequências chama `fill_bulk` para toda recepção, inclusive para o símbolo INTERRUPT_ENDPOINT. A API de transferência possui caminho interrupt separado. Para nosso 0x83, o tipo observado é interrupt; não assumir que o uso bulk funcionará.
3. As submissões analisadas passam cancellable nulo; há esperas sem timeout e a desativação sinaliza uma flag consultada nas transições. Não há, nesse caminho, interrupção explícita da transferência pendente pela flag. Validar limites de espera e cancelamento antes de tentar usar uma adaptação.
4. O parser de chunks já verifica mínimo de seis bytes, tamanho declarado e limite de linhas. Não confundir isso com validação completa: alinhamento da carga em linhas, ausência de progresso e prazo global também precisam de requisitos explícitos em um port.

Esses pontos orientam o projeto e não constituem uma declaração de vulnerabilidade explorável, nem um patch testado para upstream. Nenhuma issue ou mensagem externa foi enviada.

## Inventário reproduzível

O [inventário JSON](evidence/vfs7552-static-inventory.json) contém 24 arrays e seis sequências: comprimentos calculados dos literais, hashes SHA-256 e ordem das macros. Não contém os blocos binários nem capturas do usuário. O arquivo identifica o commit e os hashes dos dois arquivos de entrada.

Na raiz deste projeto, passando um clone local do libfprint que contenha o commit fixado:

```bash
python3 tools/analyze_vfs7552.py /caminho/para/libfprint
python3 -m unittest discover -s tests -v
```

A ferramenta lê os arquivos pelo objeto Git fixado, não pelo conteúdo possivelmente modificado do checkout. Não clona, compila, importa ou executa o código analisado. O parser aceita apenas o subconjunto de literais e macros usado nessa revisão, não é um compilador C ou analisador geral. Expressões, valores fora de byte, referências desconhecidas e sintaxe não suportada resultam em falha. Os comprimentos declarados no JSON não atestam validação em runtime.

## Decisão técnica

Não adicionar 00a6 à tabela do driver para realizar uma simples detecção: abrir esse caminho já resetaria e inicializaria o hardware. Manter como base candidata o driver de imagem VFS7552, condicionado à comparação de protocolo. A MR VCSFW continua uma referência distinta.

O próximo experimento candidato é uma única consulta de informações, isolada da inicialização e com deadline/cancelamento; sua especificação está em [lab.md](lab.md). Foi localizado um relato específico do 00a6 com resposta à consulta 0x01, mas com reset prévio. O protótipo de consulta isolada foi implementado e testado em simulação; sua execução no hardware e recuperação continuam pendentes. Não enviar blocos opacos, escrever registros, parear, capturar biometria ou modificar armazenamento nesta fase.
