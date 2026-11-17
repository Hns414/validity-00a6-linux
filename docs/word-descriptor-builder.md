# Correção: preparação de descritor, sem leitura das palavras

A [etapa anterior](word-region-consumer.md) demonstrou que a região de palavras é passada a 0xa2470, mas chamou essa função de consumidor antes de reconstruir seu corpo. **A leitura completa mostra que o ramo suportado não lê essa região.** A ligação de argumentos continua correta; a interpretação como transformação dos dados deve ser retirada.

Análise estática manual da DLL fixada. A [evidência](evidence/word-descriptor-builder.json) registra duas chamadas e seis âncoras de instruções conferidas, sem conteúdo proprietário ou execução USB.

## Wrapper e condição

A função **0xa2470** exige ponteiro de metadados não nulo e testa o DWORD de metadados **+0x28 contra 3**. Somente esse valor chama **0xa3510 em 0xa24e7**. Os demais retornam status 0x6f. Não extrapolar esse ramo para todos os tipos de sensor.

O wrapper encaminha cinco argumentos: ponteiro de região, comprimento, um DWORD de estado, metadados e saída. A função **0xa3510**, delimitada de 0xa3510 até o retorno em 0xa35ca, utiliza os três últimos para preparar a saída. Os argumentos de região e comprimento são guardados no prólogo, mas não são lidos no corpo dessa função.

## Layout preparado

| Offset na saída | Preenchimento observado |
| --- | --- |
| +0x00 | DWORD recebido no terceiro argumento |
| +0x04 | Soma dos WORDs de metadados +0x32 e +0x42, armazenada como DWORD |
| +0x08 até +0x1ab | 0x1a4 bytes preenchidos com o byte baixo do terceiro argumento |
| +0x1ac em diante | Array de WORDs com índices 0, 1, 2… |

O loop usa comparação **signed de 16 bits** para o índice e para a parte baixa do campo +4, embora a soma tenha sido armazenada como DWORD. Não substituir isso por uma contagem uint32 sem reconhecer a diferença. Também não assumir que os campos de metadados sejam dimensões de imagem: ainda não foi demonstrado.

A função não recebe capacidade da saída nem valida localmente o limite do array. A rotina superior precisa garantir espaço e valores compatíveis; essa invariante ainda deve ser rastreada. Isso não demonstra entrada malformada alcançável no driver nem autoriza copiar o padrão de memória para uma implementação nova.

## Rotina vizinha separada

A função seguinte a 0xa2470 no arquivo, **0xa2510**, contém operações de bytes e bits. Ela é uma função distinta e não é chamada por 0xa2470 ou 0xa3510 nos corpos examinados. Sua proximidade não constitui ligação com a resposta do sensor. Esta etapa não a classifica como decoder ativo.

## Impacto na investigação

Ainda precisamos localizar quem efetivamente lê a região de palavras. O descritor preparado pode fornecer parâmetros para processamento posterior, mas seu papel operacional completo permanece pendente. A existência de uma saída preenchida não é evidência de imagem decodificada.

O próximo passo é seguir o uso desse descritor e os métodos posteriores da interface a partir de chamadas demonstradas. O probe permanece inalterado, sem novo comando USB, captura ou teste com dedo. Mudança documental: base de 103 testes aprovados na v0.47, sem repetição da suíte nesta etapa.
