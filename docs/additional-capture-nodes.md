# Nós adicionais na montagem de 0x02

Análise manual da DLL fixada, com [evidência e chamadas conferidas](evidence/additional-capture-nodes.json). Sem executar driver, ler dados privados do sensor ou iniciar USB.

## Bloco vazio 0x17 condicionado por flag

O builder 0x7c4e0 testa a máscara **0x10** em seu argumento de flags em 0x7c544. A indicação resultante controla o ramo que chama **0x87910 em 0x7ca64**, passando tipo **0x17**.

O construtor já estudado cria um cabeçalho de quatro bytes com conteúdo de tamanho zero e insere o nó na lista. Assim, a presença de 0x17 não é propriedade universal do programa-base: depende desse argumento de montagem. O significado operacional completo da flag ainda não foi reconstruído desde os chamadores.

A referência pública inclui um bloco vazio 0x17 e o comenta como configuração de resposta. Isso é contexto de comparação, não confirmação isolada desse significado no 00a6. O tipo de chunk e o opcode do comando pertencem a camadas diferentes.

## Nó obtido de um objeto do host

Outro argumento controla **0x7caa4 → 0x87a20**. Esse construtor usa o objeto referenciado por contexto +0x108 e chama o helper **0x736c0** em duas fases:

1. Em 0x87a83, passa saída de comprimento inicializada com zero e ponteiro de conteúdo nulo.
2. Se o comprimento retornado é positivo, aloca nó/buffer por 0x877f0 em 0x87aa7.
3. Em 0x87ad6, chama novamente o helper com o comprimento e o buffer alocado; depois insere o nó na lista.

Em 0x736c0, comprimento zero encaminha para **0x922b0 em 0x73740**; comprimento não zero e destino disponível encaminham para **0x923d0 em 0x73783**. Portanto, o builder não obtém todos os bytes exclusivamente da tabela estática de programas.

O conteúdo e a origem final desse objeto ainda não foram identificados. Não classificá-lo como calibração, imagem, chave ou cadastro com base apenas no padrão de consulta de tamanho/preenchimento. Não foi coletado ou publicado conteúdo desse caminho.

O fluxo proprietário mostrado não constitui um contrato de alocação seguro para copiar literalmente. Uma implementação original precisará conferir os retornos e a capacidade entre as duas fases, preservar a validade dos buffers e limitar tamanhos. Não foi implementada essa operação ativa nesta etapa.

## Construtor com cabeçalho 0x15

Em **0x7cae2**, o builder chama **0x87b70**, passando estruturas e um parâmetro adicional. Esse construtor decide comprimentos a partir de campos do contexto, pode alocar um nó e, no ramo examinado, escreve:

| Campo | Valor observado |
| --- | --- |
| Tipo do cabeçalho | 0x15, em 0x87ca2 |
| Tamanho declarado de conteúdo | 8, em 0x87caf |

A chamada **0x87cd3 → 0x8c050** recebe o endereço depois do cabeçalho. A composição completa, comprimentos anteriores e alternativas desse nó ainda não foram reconstruídos. Não anunciar que todo nó gerado tenha exatamente 12 bytes apenas porque esse cabeçalho declara oito de conteúdo; o construtor usa outras variáveis de tamanho e precisa de análise adicional.

## Consequência para a reutilização dos programas

A [igualdade de 17 programas-base com referências públicas](program-materialization.md) estabelece proveniência dos conteúdos concatenados das entradas estáticas. Ela não torna o programa-base um pedido completo de captura: há alterações de repetição e inclusão de nós dependentes de flags, contexto e dados obtidos de outros objetos do host.

A tabela de programas, o descritor mutável, os nós adicionais e o cabeçalho final de 0x02 precisam permanecer distintos na implementação. Ainda não há uma montagem completa validada para o participante.

## Validação e próximos passos

Nove destinos de chamadas e a máscara da flag foram conferidos no binário fixado. A análise foi limitada às rotinas indicadas: a função 0x736c0 termina em 0x73794; rotinas vizinhas de outros objetos não foram atribuídas a esse helper só por proximidade no disassembly.

O próximo passo é reconstruir 0x8c050 e os produtores do objeto dinâmico, além da origem das flags de inclusão. Somente documentos/evidência: mantém a base de **103 testes aprovados na v0.47**, sem nova execução da suíte. Probe inalterado, sem novo comando ou teste com dedo.
