# Limites entre transporte, normalização e cópia

Análise estática manual da DLL fixada. A [evidência](evidence/response-transport-bounds.json) registra cinco chamadas e três âncoras de comprimento/offset conferidas. Sem execução do driver ou USB.

## A capacidade inicial pode mudar

0x7b260 chama **0x747e0 em 0x7b35b**, antes de alocar a recepção em 0x7b377. Dentro do helper, havendo contexto auxiliar e ponteiro do comprimento, a instrução **0x748a2** soma **0x45 = 69 bytes** à capacidade, com armazenamento DWORD. Esse ajuste ocorre antes dos testes posteriores de estado 7, modo 0xff e flag de transformação.

Portanto, não é correto tratar `N + 6` do handler 0x78 como capacidade final em todos os estados. Para os literais examinados, o ajuste produziria 4.875 ou 32.843 bytes, mas o estado efetivo do participante não foi observado. Não interpretar o acréscimo como especificação universal de overhead do protocolo.

## Normalização de resposta

Após a troca, para descritor com comprimento não zero, **0x7b4fb → 0x749e0** pode processar a resposta. O helper examina contexto auxiliar, estado e modo. Quando chega ao ramo de transformação:

1. Chama **0x74b3f → 0x774e0**, passando o buffer e o comprimento recebido.
2. Com sucesso, usa conteúdo a partir do offset **0x15 (21)** e o comprimento do campo auxiliar **+0x12c** em 0x74b79 → 0xe79f0.
3. Substitui o comprimento do descritor pelo campo auxiliar +0x12c.

O parser 0x774e0 zera inicialmente esse campo e possui verificações de cabeçalho e caminhos de extração. Sua auditoria integral, incluindo todos os cálculos e limites, ainda não foi concluída. Logo, a normalização localizada não prova que o corpo final sempre caiba na capacidade original N do destino da leitura 0x78.

O callback comum 0x7dd60 trata status e, fora do caso especial de opcode 0x44, separa dois bytes iniciais do corpo. No caminho 0x78 esse tratamento ainda depende dos contratos anteriores: a análise local não deve assumir que uma resposta menor que dois bytes é automaticamente recusada em toda a cadeia. Uma implementação nova precisa verificar o mínimo antes de subtrair o prefixo.

## Checagem original no inspetor offline

O inspetor agora aceita capacidade explícita:

```sh
python3 tools/inspect_read78_reply.py /caminho/corpo-sintetico.bin --capacity 4800
```

Além das verificações estruturais existentes, rejeita conteúdo declarado maior que a capacidade informada. A capacidade deve ser inteiro de 0 a 65532, dentro do orçamento local do corpo; booleanos e tipos ambíguos são recusados pela API Python. A saída continua contendo apenas tamanhos, sem payload ou hash.

Sem `--capacity`, permanece a inspeção estrutural anterior; isso não verifica um destino específico. A opção não determina qual tamanho o sensor usa e não valida a cadeia da DLL. Nenhum frame USB ou decoder de imagem foi adicionado.

## Respostas parciais e pendências

A existência de capacidade maior, retorno menor ou comprimento normalizado não identifica por si só fim de captura. O chamador inferior altera estados e devolve flags conforme os resultados de leitura e processamento; seus significados completos ainda precisam ser rastreados antes de definir repetição, encerramento e cancelamento no driver aberto.

O próximo passo é auditar os caminhos de comprimento do parser 0x774e0 e os retornos de entrega parcial. A prova do limite de cópia no caminho real permanece explicitamente aberta.

## Validação

Três testes novos cobrem capacidade exata/maior/zero, recusa de capacidade insuficiente, tipos e limites inválidos e recusa pela CLI sem expor conteúdo ou caminhos. `make test` passou com **112 testes sem skips**. Cinco chamadas e três âncoras do binário foram conferidas separadamente; os testes não validam a interpretação do driver Windows.

Probe inalterado, sem USB, captura ou teste com dedo nesta etapa.
