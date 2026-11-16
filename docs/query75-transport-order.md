# Ordem e condições de transporte antes de 0x75

Análise manual da DLL fixada, com [evidência de chamadas e dispatch](evidence/query75-transport-order.json). Sem executar driver ou acessar USB.

## A abertura prepara contexto antes da identificação

No caminho externo 0x64b00, uma condição em 0x65567–0x6556f controla a chamada **0x65579 → 0x746c0**, anteriormente associada à preparação de contexto de transporte. Se a chamada retorna erro, o caminho chama **0x74bb0 com argumento zero em 0x65596** e sai antes da identificação. Mais adiante, **0x6575d → 0x62eb0** alcança a consulta candidata 0x75.

A presença da condição externa impede concluir que uma nova negociação ocorra sempre. Também não foi reconstruído nesta etapa o valor dessa condição no participante. O caminho estabelece ordem e dependência condicional, não uma sessão observada no hardware.

## Retorno de sucesso pode reaproveitar contexto

Dentro de 0x746c0, **0x7472f → 0x74c90** consulta a situação do contexto. Esse helper obtém o ponteiro auxiliar em +0x50 e retorna indicação positiva quando seu DWORD **+0x100 vale 0xff**. Nesse caso, o chamador pode sair com sucesso sem avançar a máquina de estados.

O helper não testa o byte +0x4e8 contra 7 nesse trecho. Logo, seu retorno positivo não comprova sozinho todos os predicados usados para transformar o próximo buffer. Não interpretar esse atalho como “comando em claro”, “sessão autenticada” ou “TLS obrigatório” sem os demais campos.

Quando precisa avançar, o wrapper chama **0x79500 em 0x74757** repetidamente até indicação de conclusão ou erro. A máquina despacha pelo byte auxiliar +0x4e8 por uma tabela em 0x7a770; o estado numérico 7 aponta para 0x7a583. Esse ramo limpa buffers temporários e pode sinalizar conclusão pelo parâmetro de saída em 0x7a67e, dependendo do caminho de status intermediário. A equivalência de cada estado a uma etapa pública de TLS ainda não foi estabelecida.

## Transformação do comando é outra decisão

O handler de 0x75 continua passando o buffer interno ao transporte comum em **0x826c3 → 0x7b110**. Conforme a [análise de contexto de transporte](transport-context.md), o helper inferior só tenta transformar o buffer quando seus predicados locais permitem: contexto auxiliar presente, estado +0x4e8 igual a 7, DWORD +0x100 igual a 0xff e flag +0x4e0 zerada. A rotina de transformação ainda exige o bit 0x02 no DWORD auxiliar +0x128.

Os offsets +0x128 aqui pertencem à estrutura **auxiliar de transporte**. Não confundir com o +0x128 do contexto de identificação do sensor estudado nas etapas anteriores. Igualdade de offset entre objetos não implica igualdade de campo.

Sucesso de preparação, capacidade inicial de dez bytes e opcode interno 0x75 não demonstram os bytes finais no USB. A presença do auxiliar também pode aumentar a capacidade de recepção antes de decidir transformar, como já documentado. Não usar esse tamanho como prova isolada de resposta em claro.

## Relação com a referência pública e limite atual

A [conferência pública](query75-public-crosscheck.md) mostra identificação depois da abertura TLS no fluxo normal do python-validity. A análise Dell acrescenta dependências condicionais de contexto antes da identificação. Esses fatos são compatíveis com transporte contextual, mas não provam equivalência integral entre as implementações.

Ainda não foi demonstrado que 0x75 funcione diretamente antes da inicialização no 00a6. Tampouco foi demonstrado que todas as execuções Dell necessariamente o transformem. Nenhum dos dois extremos deve orientar um novo experimento sem identificar o estado aplicável.

## Validação e pendências

Seis destinos de chamadas e o destino do estado 7 foram conferidos no binário fixado. O ciclo de vida, a ordem e o significado dos branches permanecem interpretação manual, sem observação de sessão real. O registro/origem final da tabela de programas também continua pendente; esta etapa não resolveu esse segundo objetivo.

Somente documentos/evidência: mantém a base de **91 testes aprovados na v0.37**, sem nova execução da suíte. O próximo trabalho é ligar a condição externa e os produtores da tabela às estruturas de abertura, sem ampliar o probe com 0x75 ainda. Nenhum teste com dedo foi realizado.
