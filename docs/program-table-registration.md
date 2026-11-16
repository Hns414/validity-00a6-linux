# Registro das tabelas e inventário de programas

Análise manual da DLL fixada, com [evidência de argumentos, vínculos e inventário](evidence/program-table-registration.json). Nenhuma execução ou transferência USB.

## Correção da categoria

A v0.39 descreveu o lookup usado pelo seletor de programas como categoria 2. A conferência da instrução **0x634d2** mostra argumento **1**, passado a 0x64750 em 0x634dc. O wrapper vizinho usa categoria 2; ele não é o wrapper 0x63470 chamado por esse seletor.

A documentação e a evidência anteriores foram corrigidas. Essa interpretação não estava em código ativo do probe. A correção permite localizar a tabela correta sem confundir programas com outra categoria.

## Produtor dos nós de categoria

No caminho examinado, um loop chama **0x71540 em 0x712c3**, passando categorias de 0 a 3. A rotina cria o nó, guarda a categoria em +0x10 e, quando a classe do objeto pai é 1, chama **0x716f0 em 0x71611** para atribuir seu ponteiro de tabela.

O inicializador contém os seguintes vínculos estáticos:

| Categoria | Ponteiro de tabela |
| --- | --- |
| 0 | RVA 0x13dad0 — tabela opaca estudada anteriormente |
| **1** | **RVA 0x1be890 — tabela usada pelo seletor de programas** |
| 2 | RVA 0x1be940 — outra tabela, fora do escopo desta seleção |
| 3 | Nulo nesse inicializador |

Quando há ponteiro de tabela, o nó é inserido na lista de categorias do objeto pai. O lookup 0x64750 percorre a lista externa pela classe e a lista interna pela categoria, retornando o ponteiro armazenado. Isso estabelece o produtor do nó e o vínculo estático da tabela para a classe 1. O percurso completo que publica o objeto pai na lista externa ainda não foi auditado em todos os branches; não afirmar que toda execução o registre com sucesso.

## Inventário da tabela correta

A leitura limitada a 64 ponteiros encontrou **21 entradas e um terminador nulo no índice 21** em 0x1be890. A evidência publica apenas RVA de cada registro e seus primeiros sete DWORDs, sem buffers de programa ou disassembly.

Esses campos iniciais incluem os critérios examinados pelo seletor, como major/tipo e parâmetros. Por exemplo, há registros com tipos 0xdb e 0xed e parâmetros 0x18/0x19. Isso não determina qual corresponde ao participante: o tipo real permanece sem medição validada e a lógica integral de preferência ainda precisa ser conferida.

Os registros estáticos não devem ser interpretados diretamente como a estrutura de buffer mutável usada por todos os helpers do host. Campos posteriores contêm ponteiros e ainda precisam ser rastreados; um DWORD que faz parte de ponteiro não é um comprimento de payload. Por isso o inventário não anuncia tamanhos de programas nem usa os offsets +0x34/+0x38 como se o layout estivesse resolvido para qualquer objeto.

## Resultado e próximo passo

Foi localizado o vínculo da categoria correta à tabela estática e inventariadas suas entradas. A lacuna seguinte é reconstruir os campos posteriores dos registros, a montagem/obtenção dos buffers e a preferência do seletor para tipos candidatos. Não usar a hipótese 0xdb como seleção real do participante.

Três destinos de chamadas, o argumento de categoria, o endereço da tabela e seu terminador foram conferidos no binário fixado. O registro nas listas continua análise manual, sem observação em runtime. Somente documentos/evidência: mantém a base de **91 testes aprovados na v0.37**, sem nova execução da suíte. Nenhum novo comando no probe ou teste com dedo.
