# Corpo candidato de resposta e inspeção offline

Continuação da [requisição 9](post-preparation-request9.md), baseada na DLL Dell fixada. A [evidência](evidence/capture-reply-layout.json) registra coordenadas e limites. Nenhum comando foi enviado ao sensor.

## Estrutura observada no parser

O helper 0x91020 recebe descritor de tamanho/ponteiro, verifica o DWORD inicial do conteúdo contra **0x30000288**, copia o buffer para armazenamento do host e chama 0x91170 em 0x91156. Este segundo helper repete a verificação em 0x911a2 e produz uma referência ao conteúdo:

| Offset no corpo | Tamanho | Tratamento observado |
| --- | --- | --- |
| 0 | 4 | Assinatura 0x30000288, little-endian |
| 4 | 4 | Contagem uint32 de palavras |
| 8 | contagem × 4 | Região apontada pelo descritor resultante |

Em 0x911dd, o valor da contagem é deslocado dois bits à esquerda; o resultado é gravado em um campo DWORD. O trecho não apresenta uma verificação visível contra o tamanho disponível antes de criar a referência. Isso descreve a rotina examinada, não uma auditoria completa de todas as validações anteriores nem uma afirmação de vulnerabilidade explorável.

Não foram identificados os significados das palavras. Não há evidência para chamá-las de pixels, eventos de dedo, dimensões ou registros. O corpo é recebido após o tratamento comum do transporte/status; o inspetor abaixo não aceita uma transcrição USB inteira com prefixos arbitrários.

## Inspetor original restrito

```sh
python3 tools/inspect_capture_reply.py /caminho/corpo-sintetico.bin
```

A ferramenta é offline: lê um arquivo de corpo e retorna **somente contagens e tamanhos**, sem hex dump, hash ou conteúdo das palavras. Não contém transporte ou comando USB. O exemplo não é pedido para coletar uma resposta real agora.

Regras do escopo de análise:

- Assinatura exata e pelo menos oito bytes.
- Contagem compatível com o buffer, sem multiplicação com wraparound.
- Comprimento **exatamente** igual a 8 + contagem × 4; bytes extras são rejeitados.
- Orçamento de 65536 bytes, incluindo o cabeçalho; leitura limitada a esse orçamento mais um byte para detectar excesso.

Comprimento exato é uma política conservadora do inspetor, não uma prova de que o sensor nunca devolva extensões ou padding. O orçamento também é local, não limite descoberto do protocolo. Contagem zero é aceita estruturalmente, sem concluir sucesso operacional ou resposta válida no hardware.

A ferramenta não reconstrói estruturas proprietárias com ponteiros nem copia a lógica de alocação da DLL. Um corpo que passe nessas verificações continua sendo apenas uma correspondência com o formato candidato.

## Blocos de requisição: referência pública ainda separada

No commit fixado a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920, [timeslot.py do python-validity](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/timeslot.py) define `merge_chunks` como concatenação de cabeçalhos `<HH` (tipo e tamanho do conteúdo), seguidos dos conteúdos. A função inversa lê esse mesmo formato.

O builder Dell previamente examinado concatena buffers de nós; ainda não foi demonstrado nesta etapa que cada buffer de nó contenha exatamente esse cabeçalho público. Portanto, a referência delimita uma hipótese de comparação, sem habilitar um decoder de chunks do 00a6. O próximo passo é rastrear onde os buffers dos nós são construídos e confrontar seus comprimentos/campos.

## Validação

Duas chamadas, a assinatura e a instrução de multiplicação foram conferidas no binário fixado. A interpretação do formato continua manual e não foi validada em runtime. Seis novos testes verificam limites, endianness, assinatura, contagens excessivas, todos os truncamentos de um exemplo e independência da saída em relação ao conteúdo das palavras.

`make test` passou com **85 testes sem skips**. O probe ativo não foi alterado; não houve leitura de evento, captura ou teste com dedo.
