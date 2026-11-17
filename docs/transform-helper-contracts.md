# Contratos de tamanho dos helpers de transformação

Continuação do [comprimento normalizado](record-normalized-length.md). Análise estática manual da DLL fixada. A [evidência](evidence/transform-helper-contracts.json) registra sete chamadas e quatro âncoras conferidas. Nenhum buffer, chave, IV ou resposta real foi coletado.

## Helper 0x78b50

O parser chama 0x78b50 com origem/destino após os 16 bytes iniciais do conteúdo e comprimento DWORD calculado como L -16. Seu sexto argumento seleciona o ramo; no caminho examinado vale zero.

Nesse ramo, o helper preserva 16 bytes a partir de `origem + uint32(comprimento - 16)` antes da transformação, em **0x78c5f → 0xd54b0**. Não há teste local de comprimento mínimo antes dessa cópia. Isso exige um contrato anterior; não se pode contar com uma recusa posterior da API para proteger uma leitura que já ocorreu.

Depois encaminha os argumentos para **0x78cb1 → 0xdae20**, com operação interna **5**. O dispatcher usa **0xdaf2a → 0xe0ce0**, que contém a chamada de importação CryptDecrypt já delimitada no projeto. A chave e o vetor vêm de campos do contexto auxiliar; seus valores não foram extraídos. Após o dispatcher, o helper copia a cauda preservada para o campo indicado pelo chamador e retorna o status obtido.

Assim, existe um dispatcher compartilhado com o [consumidor isolado anteriormente localizado](isolated-block-consumer.md). Isso não estabelece uma chamada a 0x85f60 nem torna essa rotina isolada parte da captura: compartilhar um helper é diferente de chamar o mesmo consumidor superior.

## Helper 0x75a90

Esse helper prepara uma saída de 32 bytes por operações sobre um estado, um cabeçalho construído de cinco bytes e o conteúdo fornecido pelo chamador. Também recebe uma sequência de oito bytes que incrementa após sucesso; esta etapa não demonstra incorporação dessa sequência ao cálculo. As chamadas encadeadas são:

- 0x75b11 → 0xdfef0: cria o estado usado pelo cálculo.
- 0x75b36 → 0xe0250: incorpora o cabeçalho de cinco bytes.
- 0x75b5d → 0xe0250: incorpora o conteúdo com o comprimento DWORD fornecido.
- 0x75b81 → 0xe0330: produz os 32 bytes de saída.

O cabeçalho incorpora tipo, bytes 3/3 e uma codificação de comprimento em dois bytes. Após sucesso, o código incrementa a sequência de oito bytes com propagação de carry. A atribuição formal do algoritmo e todos os contratos internos dessas operações permanecem fora desta etapa; o papel demonstrado é preparar o valor comparado pelo parser.

Não há validação local que compare o comprimento do conteúdo com o espaço acessível antes de encaminhá-lo. Portanto, esse helper também não fornece a prova de limites que falta ao chamador.

## Condições conservadoras para uma implementação original

Para um único registro de aplicação do formato examinado, uma implementação nova precisa validar os intervalos antes de formar ponteiros ou subtrair comprimentos. A sequência de validação deve considerar:

| Operação | Condição necessária ou política conservadora |
| --- | --- |
| Ler cabeçalho | Pelo menos cinco bytes acessíveis |
| Selecionar conteúdo | L cabe nos bytes disponíveis após o cabeçalho |
| Transformar/preservar cauda | Comprimento passado satisfaz o mínimo e alinhamento do algoritmo antes de qualquer cópia |
| Calcular diferença não negativa | p em 0…15 e L >= 49 + p |
| Interpretar resposta 0x78 após transformação | Pelo menos seis bytes para status e prefixo de comprimento |
| Aceitar corpo no destino N | Verificar comprimento declarado e disponível contra N; limitar também a saída normalizada conforme o contrato escolhido |

A política estrita de corpo sem cauda adicional permite exigir `L - 49 - p <= N + 6` depois da transformação válida, junto das verificações de status e contagem. Essa é uma condição conservadora proposta, não um teste identificado na DLL nem prova de um contrato universal do sensor. Os testes criptográficos e de integridade não podem ser substituídos apenas por essas contas.

## Limites restantes

Os helpers examinados não fecham a garantia de capacidade. Também permanece aberto o contrato multirregistro: o parser pode avançar por mais de um registro, enquanto a normalização superior usa um offset fixo e um comprimento auxiliar. Precisamos rastrear quais sequências o transporte entrega e como o comprimento corresponde ao conteúdo efetivamente copiado.

Nada nesta análise demonstra entrada malformada alcançável, falha explorável ou comportamento observado do participante. O resultado é uma especificação mais precisa dos contratos que o código original futuro deverá aplicar.

Sete chamadas e quatro âncoras conferidas. Mudança documental, sem repetir a suíte: base de **112 testes aprovados na v0.62**. Probe inalterado; sem USB, captura ou teste com dedo.
