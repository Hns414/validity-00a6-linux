# Layout candidato de 0x02 e modelo offline

Continuação do [handler da requisição interna 9](post-preparation-request9.md), com [coordenadas e evidência](evidence/command02-layout.json) na DLL fixada. Sem execução do driver ou transferência USB.

## Cabeçalho e concatenação

O builder 0x7d660 lê um WORD de sua estrutura de entrada +0x0c e outro de +0x00. As chamadas 0x7d874/0x7d883 a 0xd6530 preservam esses WORDs; o helper retorna o valor sem trocar bytes. A cópia de quatro bytes para buffer +1 em 0x7d8a3 mantém a representação little-endian do PE x86-64:

| Offset no buffer | Tamanho | Origem |
| --- | --- | --- |
| 0 | 1 | Opcode 0x02 |
| 1 | 2 | WORD da entrada +0x0c, little-endian |
| 3 | 2 | WORD da entrada +0x00, little-endian |
| 5 | variável | Buffers concatenados em ordem da lista |

O primeiro percurso da lista soma os comprimentos WORD dos nós em +0x12. O segundo copia cada buffer apontado por +0x18 para a posição corrente e avança pelo tamanho desse nó. Isso descreve a concatenação externa; ainda não identifica a sintaxe interna ou os efeitos dos blocos.

## Caso especial de tamanho múltiplo de 64

O total inicial é cinco mais a soma dos comprimentos. Em 0x7d7f8–0x7d803, o builder calcula o resto da divisão por 64. Se zero, acrescenta **quatro bytes**, e não um pacote inteiro. Depois de copiar os nós, grava esses quatro bytes como zero em 0x7d9a1.

Exemplos sintéticos: soma 58 → total 63; soma 59 → total inicial 64, total final **68**; soma 60 → total 65. Não foi determinado por que o driver aplica essa regra; não chamá-la de padding criptográfico, alinhamento universal ou substituto de ZLP USB. Transformações posteriores do transporte permanecem possíveis.

## Referência pública e limites semânticos

O [python-validity fixado](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/sensor.py), função `build_cmd_02`, constrói um cabeçalho `<BHH` com valor 2 seguido de campos nomeados `bytes_per_line` e `req_lines`, mais blocos de programa. O arquivo foi lido localmente e conferido contra esse commit, sem executar seus módulos.

Há correspondência de **forma do cabeçalho**, não confirmação dos nomes desses campos no 00a6 ou da equivalência de seus programas. O fluxo público também inclui dependências de calibração e contexto; não foi usado para capturar ou provisionar o sensor. O modelo original mantém nomes neutros `field_0c` e `field_00`.

## Ferramenta original

```sh
python3 tools/model_capture_request.py 1 2 59
```

Os números são exemplo sintético, não parâmetros recomendados para hardware. A ferramenta recebe dois inteiros de 16 bits e uma soma de comprimentos; retorna somente metadados de layout. Não aceita payload, não abre arquivos de dispositivo, não monta frame binário e não acessa USB.

O limite de 65536 bytes é um **orçamento de análise do projeto**, não um limite descoberto do protocolo. A ferramenta recusa totais que o ultrapassem, incluindo cabeçalho e bytes adicionais. Não reproduz possíveis overflows ou cópias sem limites do código proprietário. Sua validação não demonstra que um comprimento aceito corresponda a um pedido válido no sensor.

## Validação e próximo passo

Cinco destinos de chamadas foram conferidos no binário fixado. O fluxo do builder continua interpretação manual. Seis novos testes cobrem fronteiras dos campos, tipos inválidos, orçamento total, todos os múltiplos de 64 dentro do escopo e saída da CLI. `make test` passou com **79 testes sem skips**.

Ainda faltam formato e origem dos nós, resolução dos campos semânticos e parser de resposta. O probe ativo permanece com os experimentos anteriores; não há novo comando habilitado nem teste com dedo nesta etapa.
