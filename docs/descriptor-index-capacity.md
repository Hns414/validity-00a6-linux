# Capacidade da tabela de índices e limite ainda aberto da leitura

Análise estática da DLL fixada. A [evidência](evidence/descriptor-index-capacity.json) registra quatro chamadas de alocação/limpeza conferidas e o resultado agregado da auditoria de 29 metadados, sem publicar registros completos.

## Alocação do descritor

A função 0xa5030 verifica se estado de processamento +0x168 está nulo. Nesse caso, pede **0x4f4 bytes** ao alocador em **0xa54bd** e zera esse espaço em 0xa5519. O ponteiro fica no estado +0x168, usado posteriormente pelo preparador 0xa3510 e pela reordenação 0xa2510.

A tabela começa em **+0x1ac**, com elementos de dois bytes. Portanto, o espaço restante comporta `(0x4f4 - 0x1ac) / 2 = 420` elementos. Se um descritor já estiver presente, esse ramo pula a alocação; sua origem e capacidade anteriores não ficam demonstradas apenas por esse teste.

## Auditoria dos metadados fixados

O lookup 0x4ee00 percorre **29 registros**, stride 0xa8, na tabela RVA 0x115030. Todos têm DWORD +0x28 igual a 3, valor aceito pelo preparador 0xa2470. Para cada registro foi calculada a contagem usada por 0xa3510: soma dos WORDs +0x32 e +0x42.

| Propriedade da tabela fixada | Resultado |
| --- | --- |
| Menor contagem | 78 |
| Maior contagem | 144 |
| Capacidade disponível | 420 índices |
| Contagens positivas representáveis como int16 | 29/29 |
| Região escrita pela identidade cabe na alocação | 29/29 |
| Exemplo de tipo candidato 0xdb | 144 índices |
| Exemplo de tipo candidato 0xed | 112 índices |

No maior caso, a escrita da identidade termina no offset exclusivo **0x2cc**, dentro de 0x4f4. Os índices escritos vão de 0 até contagem-1 e permanecem não negativos sob a leitura signed de 16 bits observada. O helper 0xa6040 também lê os dois primeiros índices para uma comparação; todas as contagens da tabela examinada são maiores que um.

Isso resolve a compatibilidade da inicialização identidade com os metadados estáticos examinados. Não prova seleção real de 0xdb/0xed no participante, não cobre alterações posteriores da tabela e não valida os acessos do decoder inteiro. Os campos continuam sem classificação como dimensões de imagem.

## Buffer da leitura 0x78

No caminho superior, os ramos de alocação em **0x47d2e** e **0x47dcf** usam o tamanho guardado em estado +0x20 e mantêm o ponteiro em +0x28. Esse tamanho vem de um argumento do chamador. O callback de leitura preenche o descritor associado a esse buffer, como documentado na [origem 0x78](read78-origin.md).

Ainda falta fechar o limite permitido para esse argumento e a relação entre capacidade original, tamanho solicitado e comprimento efetivo da resposta. O callback limita a cópia pelo corpo disponível, mas isso sozinho não demonstra compatibilidade com a capacidade do destino. O cálculo DWORD de capacidade inicial `pedido + 6` também precisa de limite explícito em qualquer implementação original futura.

Não foi feita chamada USB, e nenhum resultado desta auditoria habilita o opcode 0x78. O probe permanece inalterado.

## Verificação e próximo passo

Quatro chamadas e a constante de alocação foram conferidas; 29 contagens foram recalculadas no binário fixado. Mudança documental: base atual de **109 testes aprovados na v0.59**, sem repetir a suíte nesta etapa.

Próximo passo: rastrear o chamador que fornece a capacidade de leitura e conferir as condições do laço que alimenta o método +0x18. A auditoria de capacidade de entrada e saída permanece requisito antes de um experimento ativo de aquisição.
