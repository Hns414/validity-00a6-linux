# Capacidades fornecidas pelos chamadores da leitura

Continuação da [auditoria de capacidade](descriptor-index-capacity.md). Análise estática manual da DLL fixada. A [evidência](evidence/read78-capacity-callers.json) registra cinco chamadas e seis âncoras de tamanho/modo conferidas. Sem execução do driver ou USB.

## Origem dos tamanhos

Foram localizados dois chamadores diretos de 0x11c0c no disassembly examinado:

| Chamada | Origem do segundo argumento DWORD |
| --- | --- |
| 0x13e45 → 0x11c0c | Local inicializado com 0x8000 em 0x12571, alterado para 0x12c0 em 0x127c8 quando DWORD do objeto +0x80 vale 3 |
| 0x15d64 → 0x11c0c | Local selecionado entre 0x12c0 e 0x8000 em 0x157d7/0x157e1, conforme o mesmo teste de campo |

Os valores são **4.800 e 32.768 bytes**. Não foram interpretados como tamanho de imagem, resolução ou quantidade de pixels. O DWORD de modo do objeto superior e o WORD +0x0c do estado inferior pertencem a estruturas diferentes; não presumir equivalência sem rastrear a atribuição.

O wrapper 0x11c0c encaminha o tamanho como terceiro argumento a **0x11d4b → 0x45db0**. Esse wrapper o preserva para **0x45e4f → 0x47c00**, sob teste de classe por 0x5b840. Assim, fica rastreada a origem do argumento que alimenta a capacidade do buffer inferior.

## Crescimento e reutilização

Em 0x47c00, se o buffer em estado +0x28 já existe, o código compara a capacidade guardada em +0x20 com o tamanho solicitado. Se a capacidade for suficiente, mantém o buffer. Se for menor, libera e aloca novamente, guardando o novo tamanho. Com ponteiro nulo, também aloca usando o argumento recebido.

Logo, a capacidade armazenada pode ser maior que o tamanho nominal da chamada atual. A requisição 0x78 usa o tamanho do descritor preparado a partir dessa capacidade, e não necessariamente o literal 4.800/32.768 selecionado naquela iteração. Esta etapa não prova limite universal para todo estado preexistente.

## Condição do caminho 0x78

O bloco que chama **0x4817a → 0x53010** é precedido pelo teste do **WORD de estado +0x0c igual a 3**, em 0x4810e. Há condições adicionais de estado que controlam o preenchimento do descritor e a entrega posterior ao método +0x18. Outros modos chegam a outro ramo de aquisição no mesmo corpo; não classificar toda aquisição como opcode 0x78.

Com sucesso da requisição e estado de entrega ativo, o código prepara ponteiro e comprimento para o método +0x18. Também compara o comprimento efetivo com a capacidade guardada, podendo alterar flags do estado. O significado de todos esses estados e flags ainda não foi reconstruído. Não interpretar resposta menor automaticamente como fim de digital ou erro.

## Limite aritmético condicionado

Para os dois tamanhos literais, o cálculo de capacidade inicial `N + 6` do handler 0x78 resulta em **4.806 e 32.774**, sem wraparound de DWORD.

O callback copia `min(declarado, corpo disponível - 4)`. Portanto, **se** o corpo entregue após o transporte/status estiver limitado a `N + 4`, essa cópia fica limitada a N bytes. Isso é uma implicação aritmética; ainda falta demonstrar que todas as transformações do transporte preservam esse limite no caminho real. A existência dos literais e do teste de crescimento, isoladamente, não fecha essa prova.

## Resultado e próximos passos

A capacidade deixou de ser um argumento sem origem conhecida: há dois chamadores com seleção de tamanhos delimitada, preservação do argumento e regra de reutilização identificadas. Faltam a associação entre os modos das estruturas, os limites após transformação do transporte e o contrato completo de respostas parciais.

Etapa somente documental: cinco chamadas e seis âncoras conferidas. Base de **109 testes aprovados na v0.59**, sem repetir a suíte. Probe inalterado; sem opcode 0x78 ativo, captura ou teste com dedo.
