# Componente original em C para corpo candidato 0x78

Esta etapa transforma o contrato do [inspetor offline](read78-origin.md) em um componente C independente: `src/read78_body.c` e `src/read78_body.h`. O componente não está ligado ao probe e não contém transporte.

## Contrato

`validity_parse_read78_body(data, length, capacity, result)` aceita somente o corpo candidato de quatro bytes de contagem little-endian seguido de exatamente essa quantidade de bytes. A entrada deve ter sido separada de status e normalizada/autenticada conforme o protocolo exigir por outra camada. Este componente não faz essas operações nem estabelece que elas ocorreram.

A função valida:

- Entrada e resultado não nulos; pelo menos quatro bytes acessíveis.
- Corpo dentro do orçamento local de 65536 bytes.
- Capacidade de destino no escopo local de 0 a 65532 bytes.
- Contagem igual ao comprimento disponível após o prefixo e menor ou igual à capacidade informada.

As comparações usam o comprimento disponível antes de formar a referência ao conteúdo, sem somar a contagem não confiável ao tamanho do cabeçalho. Contagem zero é aceita somente estruturalmente e produz ponteiro nulo/comprimento zero. Em rejeição, o resultado é limpo quando disponível.

## Referência e duração

Com conteúdo não vazio, a saída aponta para `data + 4` e informa o comprimento. Não há alocação ou cópia do conteúdo. O chamador precisa manter o buffer vivo e inalterado enquanto usar a referência, fornecer o comprimento realmente acessível e manter o resultado fora da região de entrada. A interface documenta essas responsabilidades.

A função não lê registros encapsulados, valida status, descriptografa, autentica ou decide sucesso biométrico. Não imprime dados nem hashes. Não basta chamar esse parser para tornar a leitura 0x78 segura: os contratos anteriores do transporte e multirregistro continuam abertos.

## Verificação

O teste nativo percorre centenas de tamanhos sintéticos e diferentes truncamentos, verifica capacidade insuficiente, cauda adicional, comprimento máximo, contagem excessiva, endianness, ponteiros nulos, limpeza da saída, referência correta e ausência de mutação da entrada. É compilado com C11, `-Wall -Wextra -Werror`, por um teste Python independente de libusb.

`make test` passou com **119 testes sem skips**, incluindo o novo teste nativo. O mesmo executável de teste passou com **AddressSanitizer e UndefinedBehaviorSanitizer**, usando `ASAN_OPTIONS=detect_leaks=0`; detecção de leaks não foi validada. O componente não aloca memória; as alocações presentes são apenas do teste.

## Estado da integração

O Makefile e o código do probe permanecem inalterados. O novo parser é compilado somente pelo teste, sem possibilidade nova de emitir 0x78. Nenhuma consulta USB, captura ou teste com dedo foi realizado.

O caminho inferior de troca de buffers anteriormente identificado continua sem prova de resposta única: uma chamada de leitura não implica um único registro no buffer. A associação entre os registros e seus comprimentos deve ser resolvida na camada de normalização, antes de ligar este componente a uma leitura ativa.
