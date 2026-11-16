# Modificações de repetição nos blocos 0x2f e 0x34

Análise manual da DLL fixada, complementada por auditor original offline. A [evidência](evidence/program-repeat-patch.json) contém coordenadas, fatores e contagens, sem programas ou bytes modificados. Nenhuma execução do driver ou transferência USB.

## Multiplicador depende do tipo

O helper 0x4ee00 procura o tipo numa tabela de **29 registros**, com stride 0xa8, em RVA 0x115030. Na abertura, 0x657c7 chama esse helper; o byte de metadados +0x14 é copiado para contexto +0x294 em **0x65809**.

A rotina modificadora 0x82eb0 lê esse campo e usa pelo menos 1. A leitura da tabela fixada encontrou fator **1 para tipo 0xdb** e **2 para tipo 0xed**. São exemplos condicionais dos programas já comparados com referências públicas, não identificação do participante.

## O que o trecho modifica

A rotina localiza o bloco 0x2f e aponta para seu conteúdo após o cabeçalho de quatro bytes. Guarda seu DWORD inicial para possível ajuste posterior. Em seguida localiza o bloco 0x34 e percorre um prefixo de suas instruções.

Nesse percurso:

- Se `(opcode & 0xf8) == 0x10`, trata uma instrução de três bytes. Quando o terceiro byte é maior que 1, multiplica-o pelo fator e grava o byte baixo em 0x8313d. Se o argumento de incremento está ativo, incrementa também o segundo byte em 0x8316c.
- Opcode zero avança um byte; opcode 7 avança dois.
- Outro opcode encerra esse percurso. O loop só continua enquanto restam pelo menos três bytes.

Essas operações não representam uma interpretação completa do programa. O byte baixo pode truncar o produto ou o incremento; reproduzir silenciosamente wraparound em uma implementação nova exigiria justificativa específica.

## Contador 0x2f tem uma condição separada

O DWORD do conteúdo de 0x2f só é multiplicado e regravado em 0x83207 quando uma flag local de preservação está zerada. Essa flag depende dos bytes da estrutura de versão: no caminho examinado, major 6 e minor pelo menos 5 já a ativam; existe também uma alternativa para minor 3 condicionada a outro campo.

Portanto, sob a interpretação candidata **6.7** já relatada pelo participante, esse ramo preserva o contador de 0x2f. Isso não impede os ajustes do prefixo de 0x34 e não demonstra que a rotina inteira seja chamada naquele estado. Identificação do tipo, flags de modo e preparação continuam pré-condições.

## Auditor original, sem modificar o programa

O módulo `tools/audit_program_repeats.py` fornece `audit(program, factor, increment_address=False, preserve_counter=False)` para uso offline com dados sintéticos ou referências locais. Ele valida a sequência de chunks e exige um único 0x2f com quatro bytes e um único 0x34. Duplicatas e formatos fora desse escopo são recusados.

Retorna contagens de posições elegíveis, riscos de truncamento em byte/DWORD e quantidade de prefixo examinada. **Não altera a entrada nem retorna um programa modificado**, valores de instruções ou conteúdo dos blocos. Os fatores aceitos de 0 a 255 são escopo do modelo; zero vira 1, como no caminho observado. Flags são booleanas explícitas, não inferidas do equipamento.

Aplicado localmente aos programas candidatos de entradas 2/4, com fatores 1/2 e preservação do contador, encontrou **cinco posições de repetição elegíveis em cada um**. Elegível não significa necessariamente byte alterado: fator 1 pode manter a contagem, enquanto o argumento de incremento pode alterar outro byte. Os resultados de ambos os valores desse argumento estão na evidência.

## Comparação pública e limite de percurso

A função `patch_timeslot_table` em [sensor.py fixado](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/sensor.py) contém operações estruturalmente semelhantes. Contudo, seu loop usa `i + 3 < len(b)`, enquanto o trecho Dell examinado continua com **pelo menos três bytes** restantes. A diferença afeta o caso de uma instrução final de exatamente três bytes; não declarar equivalência de fronteiras entre as implementações.

O auditor modela o limite da DLL e aponta possíveis excessos sem imitar a mutação de bytearray da implementação pública. Não é encoder de programa de captura nem validação dos efeitos no sensor.

## Validação e próxima etapa

Quatro destinos de chamadas foram conferidos no binário; o fluxo dos campos e instruções continua análise manual. Seis novos testes cobrem instrução final de três bytes, ausência de mutação, limiares de contagem, excesso em byte/DWORD, parada em opcode desconhecido e entrada fora do escopo.

`make test` passou com **103 testes sem skips**. Ainda faltam as demais modificações aplicadas ao programa, os parâmetros de modo e a identificação efetiva do participante. O probe permanece inalterado, sem novo comando ou teste com dedo.
