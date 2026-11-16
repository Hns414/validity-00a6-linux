# Seleção condicional e consumidor do ramo de 484 bytes

Análise estática da DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`. RVAs relativos à ImageBase 0x180000000. Sem executar DLL ou operação de inicialização.

## Varredura dos 75 registros

Foi percorrida a tabela em 0x13dad0, com leituras limitadas às seções mapeadas e terminador nulo conferido após 75 ponteiros. Aplicando máscara requerida 0x4000, versão candidata 6.7/build 164, argumento zero em +0x30 e discriminante 2 em +0x34, resta somente a entrada **55 / RVA 0x13d490 / 484 argumentos**.

A versão/build vem do relato E1 anterior; o discriminante vem do resumo schema 4. São observações separadas do participante, não um snapshot atômico de todos os campos. A conclusão abaixo é condicionada a esses valores continuarem correspondendo ao mesmo estado.

No registro restante, +0x1c, +0x38 e +0x40 são wildcards 0xffff. Não exigem novos valores concretos para seus respectivos filtros. A máscara excluída no caminho examinado é zero. O teste obrigatório restante é +0x3c igual ao byte +0x0a da estrutura interna: a entrada exige 1.

## Gate anterior à seleção

No mesmo fluxo externo de abertura, após preencher a estrutura de versão, a DLL lê o byte interno +0x0a em 0x64d7a e compara com 1 em 0x64d7e. Quando diferente, prepara erro e sai da rotina pelo desvio em 0x64d9f, antes da chamada de seleção em 0x65411.

**Conclusão condicional:** no caminho de abertura examinado, se os valores candidatos 6.7/build 164/discriminante 2 se mantêm e o gate anterior foi ultrapassado, a entrada 55 é a única que passa pelos filtros descritos. Com uma única candidata, a lógica posterior de preferência entre múltiplos registros não precisa decidir entre este par. Isso não é observação de execução do seletor no dispositivo: a DLL não foi executada, e o probe não mede o byte do gate ou os estados do driver Windows.

Não é necessário solicitar outro teste ao participante para documentar essa implicação lógica. Se o gate real falhar, o fluxo pode simplesmente não alcançar a seleção; não presumir sucesso.

## O parâmetro +0x20 não é opcode neste caminho

O consumidor 0x62ad0 recebe máscara, argumentos e o byte do campo +0x20 do registro. A rotina 0x63f00 retorna 1 para máscara exatamente 0x4000 (também para alguns outros valores exatos). Isso leva ao branch 0x62ba7 para 0x62cb2, pulando a sequência de consulta do cache local que poderia encerrar sem enviar.

No caminho que prossegue, o consumidor:

1. Recupera tamanho/ponteiro dos argumentos.
2. Chama 0x537b0 em 0x62d27. Seu retorno zero ou 0xd1 permite prosseguir; outros retornos interrompem. Os efeitos dessa preparação ainda precisam ser analisados.
3. Monta descritor de tamanho/ponteiro e chama 0x53560 em 0x62da5, passando zero no argumento de comando interno usado por esse wrapper.
4. Para o classificador não zero, pula as atualizações posteriores do cache e do byte interno +0x0f que usariam +0x20.

Assim, não foi observada incorporação do valor 1 de +0x20 ao frame nesse caminho. O handler já rastreado da requisição 7 constrói opcode 0x06 seguido dos argumentos. Essa conclusão é específica da máscara 0x4000, não uma descrição universal do parâmetro.

O cache citado é uma estrutura na memória do host, em contexto +0x220. Pular esse cache não demonstra escrita persistente, reset ou ausência de efeitos no sensor. A chamada preparatória e as transformações do transporte ainda impedem equiparar automaticamente o frame interno ao tráfego final.

## Encoder offline atualizado

O encoder original agora aceita somente os dois comprimentos investigados: 484 ou 500 argumentos. Produz respectivamente 485 ou 501 bytes, com opcode 0x06. Continua sem payload embutido, sem seleção automática e sem link no probe USB. Não houve alteração do executável ativo nesta etapa.

O teste nativo cobre ambos os tamanhos, rejeição dos demais comprimentos de 0–600 e SIZE_MAX, capacidades insuficientes sem alteração da saída, capacidade exata, sentinelas e sobreposição. `make test` passou com 59 testes sem skips; o teste existente foi ampliado. ASan/UBSan do encoder passou sem diagnóstico com detecção de leaks desabilitada, conforme limitação já registrada.

O [registro estruturado](evidence/init-484-conditional-selection.json) contém premissas, índices após cada filtro e coordenadas. O filtro de tabela foi calculado sobre dados; os branches e papéis foram interpretados manualmente, sem prova automática de equivalência completa. Próximo passo: analisar 0x537b0 e os efeitos do conteúdo, sem enviar inicialização ao leitor.
