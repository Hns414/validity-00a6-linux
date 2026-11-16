# ROM info: campos candidatos e limites

A consulta 0x01 já retornou 38 bytes no teste do participante. Nenhum byte da resposta foi publicado ou analisado. O passo seguinte é extrair poucos campos sob uma hipótese explícita de layout, sem despejar o buffer.

Fonte primária: [RomInfo em sensor.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/sensor.py), commit a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920. Essa implementação usa status de dois bytes, seguido de timestamp/build/version/produto e campos ainda não identificados, em little endian. O suporte ao 00a6 não consta na tabela daquele projeto: a correspondência é uma hipótese, não uma especificação validada para nosso dispositivo. Nenhum código daquele decoder foi incorporado.

## Campos exportados

Offsets absolutos a partir do começo da resposta recebida; não a partir do payload após status.

| Bytes | Campo candidato | Tratamento |
| --- | --- | --- |
| 0–1 | Status | Exigir ambos zero; não exportar o valor bruto |
| 2–5 | Timestamp suposto | Omitir |
| 6–9 | firmware_build | Inteiro little endian de 32 bits |
| 10 | firmware_major | Inteiro de 8 bits |
| 11 | firmware_minor | Inteiro de 8 bits |
| 12 | Padding suposto | Omitir |
| 13 | product_code | Inteiro de 8 bits; não mapear para modelo comercial |
| 14–37 | Desconhecidos/padding/outros dados | Omitir integralmente |

Versão/build/produto são tratados como metadados compartilhados sob essa interpretação. A hipótese ainda pode estar errada; os valores não devem receber significado adicional sem outra evidência. Não exportar timestamp, campo u1, serial, hexdump, hash da resposta ou bytes finais. Um hash da resposta inteira também poderia se tornar identificador estável e não é necessário aqui.

O decoder exige exatamente 38 bytes e status zero. Em tamanho diferente ou status não zero, limpa o resultado e retorna erro de interpretação; o transporte ainda pode ter recebido uma resposta, portanto status de transporte continua reply_received_unvalidated. decode_status explica a interpretação e rom_info_candidate fica null.

## Formato e execução

A opção --probe-rom-info conserva schema_version 1. A nova opção --summarize-rom-info usa schema_version 2 e acrescenta decode_status e rom_info_candidate. Não existe autodetecção nem escalada para outra consulta em caso de falha.

Exemplo **sintético, usado nos testes**, não leitura do hardware:

```json
{"schema_version":2,"experiment":"E1","status":"reply_received_unvalidated","stage":"read","received_bytes":38,"biometric_support":false,"decode_status":"candidate_layout_unverified","rom_info_candidate":{"firmware_build":305419896,"firmware_major":6,"firmware_minor":7,"product_code":48}}
```

A nova opção usa exatamente o mesmo transporte da consulta anterior: um byte OUT, leitura de até 64 bytes, sem reset, troca de configuração, inicialização ou retry. Nenhuma execução dessa opção ativa foi feita pelo agente. Veja o [passo a passo do participante](first-hardware-test.md).

Uma resposta coerente pode orientar comparação com fontes existentes. Não valida transporte de captura, pareamento, matching ou login. O código de saída 0 continua indicando somente resposta recebida; não é aprovação semântica do layout.
