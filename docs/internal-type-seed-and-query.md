# Hipótese inicial de tipo interno e consulta 0x75

Análise manual da DLL fixada, com [evidência de chamadas, slot e instruções](evidence/internal-type-seed-and-query.json). Sem execução ou transferência USB.

## Produtor do identificador no contexto

No fluxo de abertura, 0x6575d chama a rotina **0x62eb0**. Ela obtém o contexto, prepara um candidato de identificador, pode consultar informação adicional e guarda um resultado no campo +0x10 do objeto de operação. Ao sair, copia esse campo para **contexto +0x128 em 0x63319**.

Assim, foi localizado um produtor concreto do identificador consumido pelo seletor de programas. Isso não significa que seu resultado final tenha sido observado no leitor do participante.

## Produto 0x30 fornece uma hipótese, não uma medição

A rotina tem alternativas por produto ROM. No ramo de produto **0x30**, a instrução **0x62fed** grava o candidato **0xdb** em uma variável local. Outros produtos seguem regras diferentes.

O produto candidato 0x30 já relatado pelo participante torna esse ramo relevante. Contudo, a rotina prossegue para uma consulta e pode substituir a hipótese antes de armazenar o identificador final. Portanto, **não afirmar que o tipo interno do participante foi identificado como 0xdb** e não selecionar automaticamente um programa público dessa família.

## Requisição interna 0x35 constrói opcode 0x75

Em **0x6301a**, a rotina chama 0x54a40 com locais de saída para dois valores. O wrapper monta **requisição interna 0x35** em 0x54b71 e despacha por 0x5a820 em 0x54ba6.

O slot **0x1164e8** da tabela de handlers aponta para **0x82610**. Esse handler chama o alocador 0x83220 em **0x8266b**, com tamanho 1 e argumento de opcode **0x75**, e passa o buffer ao transporte comum 0x7b110 em **0x826c3**. Sua capacidade inicial de recepção é **10**, não um comprimento real de resposta já observado.

O caminho identifica a construção do comando, mas não comprova operação sem efeitos, disponibilidade antes da inicialização ou formato de retorno válido no 00a6. Não foi acrescentada opção 0x75 ao probe.

## Substituição e normalização

Quando a consulta retorna sucesso e um dos valores de saída não é zero, a rotina pode tratá-lo por um mapeamento adicional: separa partes de 16 bits e chama 0x5f140 em 0x6307f. Esse helper encaminha a 0x63f80, que usa outras estruturas do host.

Há ainda tratamentos especiais de identificadores antes da gravação no objeto. Os significados completos desses valores, sua normalização e o callback que extrai os dois resultados ainda precisam ser reconstruídos. O candidato inicial não pode ser usado como substituto da análise desses passos.

Se o identificador final permanece zero, existe um caminho diferente que tenta obter/usar um descritor e uma operação posterior. Essa alternativa também impede generalizar a atribuição inicial como identificação universal.

## Próximo passo e limites

A descoberta transforma a lacuna “origem desconhecida do campo +0x128” em um fluxo concreto a investigar: callback da consulta 0x75, mapeamento dos resultados e alternativas da rotina. O registro da tabela de programas nas listas do host continua pendente; não foi resolvido nesta etapa.

Sete destinos de chamadas, o slot do handler, o candidato 0xdb e o argumento 0x75 foram conferidos no binário fixado. Ramos e papéis continuam análise manual, sem identificação em runtime. Somente documentos/evidência: mantém a base de **91 testes aprovados na v0.37**, sem nova execução da suíte.

Ainda não há programa final de captura estabelecido, novo teste de hardware ou teste com dedo.

A [continuação do callback](query75-callback-mapping.md) identifica dois DWORDs de corpo e a tabela de normalização/mapeamento, sem habilitar coleta.
