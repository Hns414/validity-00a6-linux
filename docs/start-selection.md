# Seleção condicional da preparação de Start

Continuação da [preparação](start-preparation.md), com análise manual da DLL fixada e filtragem da tabela. A [evidência estruturada](evidence/start-conditional-selection.json) registra premissas e resultados. Sem execução da DLL ou transferência USB.

## Papéis dos argumentos

A chamada 0x5ea7e passa máscara requerida 0x400000 e valor 0x22020 ao wrapper 0x5ed80. Esse wrapper move 0x22020 para o quinto argumento de 0x5ede0 e zera o quarto em 0x5edb2. O segundo wrapper preserva esses argumentos ao chamar o seletor 0x8fb20 em 0x5ef20.

No seletor, o quarto argumento é comparado ao campo de registro +0x30 (com curinga 0xffff), e o quinto é usado como **máscara excluída**: se sua interseção com +0x2c não é zero, o registro é rejeitado em 0x8fc57. Portanto, neste caminho:

- Máscara requerida: 0x400000.
- Parâmetro comparado a +0x30: zero.
- Máscara excluída: 0x22020.

A etapa anterior chamava 0x22020 genericamente de parâmetro; esta análise delimita seu papel na seleção. Nenhum desses números é um opcode USB.

## Resultado sob as premissas do participante

Aplicando os filtros sobre os 75 registros:

| Filtro acumulado | Índices restantes |
| --- | --- |
| Máscara requerida 0x400000 | 15, 24, 28, 32, 39, 46, 52, 59, 62, 66, 72 |
| Máscara excluída 0x22020 | Os mesmos 11 |
| Major 6, minor 7, build 164 ou curinga | 15, 52 |
| Parâmetro +0x30 igual a zero ou curinga | 15, 52 |
| Discriminante +0x34 igual a 2 | **52** |

A entrada 15 requer discriminante 3; a 52 requer 2. O discriminante 2 vem do resumo E1 já relatado pelo participante. Versão/build e discriminante foram medidos em momentos separados; não são snapshot atômico do estado usado pelo driver Windows.

A entrada **52 / RVA 0x13d3a0** possui 12100 bytes de argumentos, máscara 0x400080, campo +0x20 igual a 18, campos +0x1c/+0x38/+0x40 curinga e exige campo interno +0x0a igual a 1 por +0x3c. Assim, **se** os valores relatados correspondem ao contexto do seletor e esse campo interno vale 1, só a entrada 52 passa pelos filtros descritos. Isso não demonstra que Start alcança esse ramo ou que o campo ainda tenha o valor necessário nessa ocasião.

Os dois blocos de 12100 bytes foram comparados localmente e **não são iguais**. Nenhum byte de payload foi incorporado ao repositório. Tamanho e versão, isoladamente, não autorizam a substituição entre eles.

## Comportamento do consumidor e cache

Em 0x5f002, o consumidor 0x62ad0 recebe a máscara **do registro** (+0x2c), neste caso 0x400080, e o campo +0x20, além dos argumentos. O classificador 0x63f00 só retorna 1 para valores exatos 0x800, 0x1000, 0x4000 e 0x40000; retorna zero para 0x400080. Portanto, esse ramo pode consultar o cache local +0x220 e retornar sucesso **sem enviar**, conforme máscara armazenada, parâmetro e máscara excluída. A presença da chamada no caminho estático não comprova uma transferência.

Quando prossegue, o caminho comum passa pela preparação 0x537b0 e pelo envio interno 0x53560. Após sucesso, para classificador zero, grava máscara/parâmetro/campo +0x20 no cache e copia o último para o byte +0x0f da estrutura de versão, se presente. São atualizações de memória do host. Isso difere da máscara de inicialização 0x4000, que pula esse gerenciamento; não demonstra efeito persistente do conteúdo no sensor.

## Validação e pendências

Quatro destinos adicionais de chamadas foram conferidos no binário fixado; campos de descritores e comparação dos blocos foram calculados com mapeamento de seções PE. Ramos e significado de estruturas continuam análise manual. Somente documentação/evidência: permanece a base de 73 testes aprovados na v0.27, sem nova execução necessária.

Precisamos agora investigar o conteúdo por referências públicas e os demais caminhos de preparação, além de definir recuperação e observação de eventos. A seleção condicional não estabelece que o bloco seja apenas armamento de dedo ou que possa ser enviado com segurança. Probe e encoder offline não foram ampliados para esse comprimento; não há teste com dedo nesta etapa.

A [análise das alternativas](start-public-comparison.md) delimita o campo de contexto que escolhe 0x400000 ou 0x80 e compara os blocos com referências públicas.
