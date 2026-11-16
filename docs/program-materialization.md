# Reconstrução dos programas e comparação pública

Análise offline da DLL fixada. A [evidência do materializador](evidence/program-materialization.json) e o [resultado reproduzível da comparação](evidence/capture-program-comparison.json) não contêm buffers de programa. Nenhuma DLL ou módulo upstream foi executado e não houve USB.

## Dois layouts diferentes

Após escolher um registro, o seletor 0x906e0 cria uma estrutura de **0x40 bytes** e copia os primeiros **0x34 bytes** de metadados. O campo estático +0x34 é um **ponteiro de oito bytes para uma lista de fragmentos**, não o comprimento final do programa.

Cada item dessa lista tem **dez bytes**, sem padding entre seus campos: tamanho uint16 em +0 e ponteiro de oito bytes em +2. O percurso avança por dez bytes e termina quando o ponteiro é nulo. O primeiro percurso soma os tamanhos; o segundo concatena os conteúdos na ordem indicada.

Na estrutura criada em memória, +0x34 passa a ser **comprimento DWORD**, e +0x38 passa a ser **ponteiro para o programa concatenado**. Essa é a estrutura depois consumida por 0x709e0. A distinção resolve por que ler o registro estático como descritor mutável produzia uma interpretação incorreta dos campos posteriores.

## Preferência entre registros

Os filtros iniciais incluem tipo, major e parâmetros, com curingas em campos previstos. A preferência posterior calcula pontuação a partir de major, minor, build e byte interno +0x0f, com pesos **64, 16, 4 e 1**. Nesses componentes, correspondência, curinga e divergência têm tratamentos distintos; a pontuação não substitui os filtros anteriores.

Em 0x90a0b–0x90a23, uma candidata só substitui a atual se sua pontuação é maior; empate preserva a primeira. Isso difere da regra de menor comprimento na tabela de preparação opaca. Não usar a lógica de um seletor para o outro.

A implementação completa dessa seleção ainda não foi portada ou validada com o estado do participante. A ferramenta desta etapa reconstrói **todas as entradas**, sem escolher uma para o hardware.

## Comparação com programas públicos

A ferramenta original extraiu 42 programas de inicializadores literais `SensorCaptureProg` do arquivo [generated_tables.py fixado](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/generated_tables.py). Usa AST para ler constantes; não importa o módulo nem executa seus inicializadores.

Resultado: **17 das 21 entradas Dell coincidem integralmente com pelo menos um dos 42 programas públicos**. As quatro restantes não coincidem nesse inventário; isso não estabelece ausência de referência em outras versões/projetos.

Duas correspondências relevantes para hipóteses já estudadas:

| Entrada Dell | Tipo no registro | Fragmentos | Programa concatenado | Índice público com igualdade integral |
| --- | --- | --- | --- | --- |
| 2 / RVA 0x1be170 | 0xdb | 2 | 1044 bytes | 41 |
| 4 / RVA 0x1be230 | 0xed | 2 | 644 bytes | 15 |

A igualdade é comparação byte a byte, além dos hashes registrados. Esses tipos continuam hipóteses de análise; o tipo real do participante não foi confirmado. A correspondência de origem também não demonstra que um programa possa ser enviado sem as modificações posteriores, sem preparação ou em qualquer revisão do sensor.

## Reproduzir sem USB

```sh
python3 tools/compare_capture_programs.py /caminho/python-validity /caminho/synaWudfBioUsb.dll
```

A CLI exige tamanho e SHA-256 da DLL fixada, lê o objeto Git público pelo commit fixado e usa mapeamento de seções PE. Recusa ponteiros fora do arquivo, fragmentos vazios, terminadores inconsistentes, ausência de terminador em até 64 itens e total acima de 65536 bytes. São limites do inspetor, não limites descobertos do sensor. Também confere as 21 entradas e o terminador da tabela conhecida.

A saída contém comprimentos, contagens, hashes, RVAs e índices de igualdade; não contém payload ou disassembly. O pacote proprietário não deve ser adicionado ao repositório para reproduzir a análise.

## Validação e próximo passo

Três destinos de chamadas do materializador foram conferidos no binário. Seis novos testes cobrem ordem dos fragmentos, mapeamento/truncamento, terminador, limite de percurso e rejeição de inicializadores públicos dinâmicos ou ambíguos. `make test` passou com **97 testes sem skips**.

A próxima investigação é delimitar as modificações aplicadas aos programas já identificados e o tipo efetivo necessário para selecioná-los. O probe ativo permanece inalterado; não houve novo comando, captura ou teste com dedo.

A [análise dos nós adicionais](additional-capture-nodes.md) delimita outras fontes e condições de montagem, além dos programas-base comparados.
