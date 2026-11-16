# Registros do host na montagem dinâmica

Análise estática manual da DLL fixada, sem executar o driver ou transferir USB. A [evidência](evidence/dynamic-host-records.json) registra metadados, quatro destinos de chamadas e cinco âncoras de instruções conferidos. Não contém os registros nem seus conteúdos.

## Busca e origem imediata

Os percursos 0x922b0 e 0x923d0 chamam 0xe5c00, que consulta 0xe6580. Este último percorre uma lista encadeada do host e compara o índice solicitado com o WORD do nó em +0x14. Sem correspondência, retorna ponteiro nulo; o wrapper traduz isso para status 0x76, que os percursos ignoram antes de continuar.

Com correspondência, o wrapper devolve o DWORD do nó +0x18 e o ponteiro +0x20. Esses campos são compatíveis com comprimento e conteúdo de um registro armazenado no host. O comprimento retornado não é usado como limite de cópia nos percursos examinados. Quem cria a lista, quem preenche o conteúdo e seu significado ainda não foram identificados.

## Assimetria que impede uma tradução direta

| Etapa | Comportamento estático observado |
| --- | --- |
| Consulta de tamanho, 0x922b0 | Consulta índices 1 a 6, inclusive |
| Preenchimento, 0x923d0 | Consulta índices 1 a 5, inclusive |
| Tamanho, callback 0x92be0 | Índice 1: 16 bytes; índice 2: 20; demais: zero |
| Cópia, callback 0x92c20 | Somente índice 1 chega à cópia; demais seguem caminho de diagnóstico |

O callback de cópia inicializa uma variável local com 1. No caminho examinado ela não muda, portanto a origem selecionada é o ponteiro do registro +8. As alternativas +0x18 e +0x28 existem no código, mas não são alcançadas por essa variável local constante nesta função.

O preenchimento soma o tamanho de cada índice e compara o acumulado com o tamanho total fornecido pelo chamador. Porém, ao invocar a cópia em 0x9253c, passa esse **tamanho total**, não o tamanho retornado para o índice atual. O callback encaminha esse WORD à função de cópia em 0x92ca8. Assim, não é correto concluir que a cópia do índice 1 sempre tem 16 bytes: isso depende do total calculado e dos registros presentes.

Essas diferenças são observações do binário, não demonstração de falha explorável nem de execução desse ramo no 138a:00a6. Faltam as invariantes impostas pelos produtores dos registros. Não implementar um encoder baseado em uma suposta concatenação uniforme de 16 e 20 bytes.

## Próximas lacunas

Rastrear inserção/preenchimento da lista e seus tamanhos reais; conferir quais índices podem coexistir; continuar o construtor condicional 0x87d90. Identificação real do tipo, inicialização, detecção de dedo e captura continuam sem validação no hardware.

Mudança somente documental. Base de 103 testes aprovados na v0.47, sem nova execução da suíte nesta etapa; probe inalterado e nenhum teste com dedo solicitado.
