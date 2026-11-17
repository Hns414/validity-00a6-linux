# Componente C de inspeção estrutural de envelopes

O projeto agora tem um segundo componente original em C, independente de libusb: `src/record_envelope.c` e seu contrato em `src/record_envelope.h`. Implementa o escopo estrito do [inspetor Python](../tools/inspect_record_envelope.py), com testes de concordância, sem copiar implementação da DLL. Está separado do probe.

## Entrada e resultado

`validity_inspect_record_envelope(data, length, result)` recebe um buffer completo e devolve 1 se a estrutura estiver dentro do escopo candidato, ou 0 em caso de rejeição. O resultado contém apenas número de registros, número de registros de tipo 0x17 e soma dos comprimentos de conteúdo. Não devolve conteúdo nem referências a ele.

O escopo exige entre 6 e 65536 bytes, cabeçalhos completos de cinco bytes, tipo entre 0x14 e 0x17, versão 3/3 e comprimento big-endian de dois bytes maior que zero. Cada conteúdo deve caber nos bytes restantes. Todos os bytes precisam pertencer a registros completos; caudas e marcadores de parada não fazem parte deste contrato conservador.

A implementação verifica comprimentos por subtração antes de avançar. Acumula o resultado localmente e só o publica após validar toda a entrada: uma falha depois de registros válidos deixa todos os campos zerados. Não aloca memória, não modifica a entrada e não faz cópia de conteúdo, criptografia, logging ou USB. O chamador deve fornecer comprimento realmente acessível e resultado sem sobreposição ao buffer.

## Limites de interpretação

Aceitar a estrutura **não demonstra que uma resposta do sensor terminou**. Um buffer com registros completos pode ser apenas parte de uma resposta maior. O componente também não associa registros a uma requisição, não autentica, não decifra, não concatena conteúdos e não remonta leituras fragmentadas. Uma entrada truncada é rejeitada, sem pedir novas leituras.

Não aplicar diretamente o [parser de corpo 0x78](read78-c-component.md) ao conteúdo contado: ainda faltam as provas e operações de normalização, autenticação e separação de status. Os tipos de registro não conferem significado biométrico aos bytes.

## Validação

A suíte tem **121 testes aprovados, sem skips**. Os dois novos testes incluem:

- Teste nativo com todos os truncamentos do envelope de tamanho máximo, limite excedido, ponteiros nulos, entrada inalterada e maior quantidade de registros mínimos no orçamento.
- Comparação do C com o inspetor Python em 503 entradas sintéticas determinísticas, incluindo múltiplos registros, truncamentos, caudas e mutações de cabeçalho; comparação das contagens e limpeza do resultado em rejeições.

O teste nativo também passou compilado com AddressSanitizer e UndefinedBehaviorSanitizer, com detecção de leaks desativada. Compilações usam C11, Wall, Wextra e Werror. Não houve execução do probe ou leitura USB.

O próximo passo continua sendo estabelecer o contrato de encerramento/associação da resposta antes de implementar remontagem ou ligar os componentes ao transporte ativo.
