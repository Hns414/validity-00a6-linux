# Origem do campo que escolhe a preparação

Análise manual da DLL Dell fixada pelo hash na [evidência](evidence/start-parameter-origin.json). RVAs relativos à ImageBase 0x180000000; nenhuma execução ou transferência USB.

## Do parâmetro do host ao campo +0x0c

O ponteiro local `[rsp+0x48]` de 0x47430 aponta para o contexto de preparação obtido do argumento +0x28 em 0x474c1/0x474c5. Seu WORD +0x0c não vem de uma resposta USB recém-recebida nesse trecho. A origem rastreada é:

| Ponto | Movimento observado |
| --- | --- |
| 0x1b128 → 0x2bc20 | Getter lê DWORD +0x18 de objeto do host cujo endereço é objeto externo +0x1d0 |
| 0x1b185 / 0x1b1a2 | Retorno é passado como quarto argumento ao construtor 0x10e08 |
| 0x10ea6 | Construtor guarda esse argumento em objeto de captura +0x80 |
| 0x12de1 / 0x12de8 | Start lê o WORD baixo de +0x80 e o guarda em `[rsp+0x284]` |
| 0x13679 / 0x1368d | Start passa o bloco de parâmetros começando em `[rsp+0x278]`; o WORD está no offset +0x0c |
| 0x45d5c | Wrapper copia 0x1c bytes desse bloco para o novo contexto de preparação |

O campo completo no objeto de captura é DWORD, mas este caminho copia apenas seus 16 bits baixos. O trecho não estabelece o nome semântico da enumeração nem permite tratá-la como versão do firmware, presença de dedo ou discriminante do resumo E1. A atribuição original do objeto acessado pelo getter ainda precisa ser rastreada.

O contexto novo foi alocado com tamanho 0x170 e zerado antes da cópia. O memset posterior em 0x474de cobre +0x78 até +0x16f; não apaga o WORD +0x0c. Não confundir esse bloco com a estrutura de versão usada pelo seletor: há dois contextos com offsets diferentes e papéis distintos.

## Ajuste local antes da escolha

Antes dos ramos alternativos, 0x47430 chama 0x5da20 em 0x47623, obtendo um valor usado por 0x4ee00 em 0x47650 para recuperar metadados. O significado desses metadados não foi completamente identificado.

Se o WORD +0x12 dos metadados vale 1 e o WORD +0x0c da preparação vale 3, a rotina grava **1** no campo da preparação em 0x476a9. Caso contrário, preserva o valor. Logo, a decisão posterior usa o valor após esse ajuste, não necessariamente o parâmetro original do construtor.

No ramo examinado, esse ajuste troca 3 por 1; não cria o valor 2. A escolha da máscara 0x400000 exige +0x0c igual a 2 depois desse ponto. Outros valores seguem para 0x80, salvo o ramo anterior que pula ambas as preparações. Essa conclusão vale para as instruções examinadas, não para toda escrita possível nesses objetos em outros fluxos.

## Consequência para o participante

A versão 6.7/build 164 e o discriminante 2 já medidos no leitor ajudam a filtrar **qual bloco** seria escolhido quando o seletor é chamado. Eles não determinam **qual ramo do host** chega ao seletor. O valor 2 deste WORD e o discriminante 2 têm origens e usos distintos; igualdade numérica não estabelece vínculo entre eles.

Não há motivo para pedir outra leitura E1 para resolver um parâmetro do driver Windows. O próximo passo útil é identificar sua atribuição e o significado dos metadados, junto aos consumidores posteriores da preparação.

## Validação

Seis destinos de chamadas foram conferidos diretamente no binário fixado; os movimentos de argumentos e a reescrita condicional foram interpretados manualmente. Não foram executados o construtor ou os caminhos de captura.

Esta etapa modifica somente documentos/evidência. Mantém a base de 73 testes aprovados na v0.27, sem nova execução da suíte. Nenhuma opção foi adicionada ao probe e não há teste com dedo nesta etapa.

A [continuação da atribuição](start-mode-assignment.md) identifica uma escrita final de modo 3 em um ramo anterior ao construtor e avalia a preferência entre candidatas de 0x80.
