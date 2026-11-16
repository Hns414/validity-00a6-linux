# Registro do host não é armamento do sensor

Análise manual da DLL fixada pelo hash na [evidência](evidence/event-registration-analysis.json). RVAs relativos à ImageBase 0x180000000; sem execução da DLL ou transferência USB.

## Tipos em camadas distintas

O wrapper 0x48c00 aceita tipos superiores 1, 2 e 3. Preserva callback/contexto e encaminha o tipo a 0x5c3a0 em 0x48cf7. Esse segundo wrapper guarda o tipo original em contexto +0x20, mas transforma **todos os três em tipo inferior 1**, antes de chamar 0xe7520 em 0x5c427. É esse tipo inferior que chega ao [worker](event-worker.md).

Assim, o número usado para selecionar o caminho inferior não distingue três eventos físicos. O callback 0x64a90 recupera o tipo superior guardado, entrega o status do descritor de conclusão e passa terceiro argumento zero. Não entrega os sete bytes brutos diretamente ao callback superior. O intermediário 0x48dd0 também preserva essa distinção entre tipo e status.

## Espera e notificação

No caminho WaitForFinger, 0x14ea7 registra tipo superior 1, callback 0x11278 e contexto da operação. Depois chama 0x112c0 com argumento 1 em 0x14eb9; esse helper atualiza estado **do host** (+0x40) sob sincronização. Esse trecho não constrói comando USB.

Quando recebe tipo 1, o callback 0x11278 guarda o segundo argumento em contexto +0x30 e sinaliza o handle em +0x28. O slot importado 0x1105a8, chamado em 0x112b4, é SetEvent, conforme tabela de imports do PE. É o mesmo campo de handle usado pela espera em 0x14f2a. Portanto, o despertar observado nessa cadeia indica conclusão/notificação; isoladamente, não comprova toque válido ou presença de dedo.

O caminho Start 0x124c0 chama WaitForFinger em 0x138ea em um de seus ramos. Não há chamada direta de Start a 0x48c00 nesse intervalo examinado. Isso não exclui registro indireto ou outros ramos; delimita apenas o trecho conferido.

## Consulta posterior do cache

Em 0x44e10, os tipos superiores 1, 2 e 3 viram seletores locais 2, 3 e 4, respectivamente, antes da chamada 0x5f7e0 em 0x44f18. Esses seletores escolhem interpretação **depois** da requisição interna 0x938ae038, que copia sete bytes do cache; não são opcodes enviados ao USB. O wrapper também extrai posições 5 e 6 do cache para campos auxiliares. Sua semântica permanece desconhecida e seus valores não foram coletados.

Não confundir três numerações: tipo superior registrado, tipo inferior do worker e seletor de interpretação do cache. Nenhuma delas, sozinha, documenta uma ordem de armamento do sensor.

## Limite e próximo passo

Seis destinos de chamadas foram conferidos diretamente no binário fixado. Tipos, argumentos e fluxo são interpretação manual das instruções; não há equivalência automática ou validação em runtime. Esta etapa altera apenas documentos/evidência. A base continua com 73 testes aprovados na v0.27, sem nova execução necessária.

Ainda precisamos localizar o comando que prepara o sensor para produzir eventos, sua dependência da inicialização e os significados dos campos recebidos. Nenhum comando novo foi habilitado no probe; ainda não há teste com dedo.
