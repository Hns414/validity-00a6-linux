# Montagem, capacidade de resposta e conclusão do init

Análise estática da DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`. Endereços são RVAs relativos à ImageBase 0x180000000. Nenhuma execução de DLL, patch ou nova operação USB.

## O que o handler interpreta

O handler 0x7e540 da requisição 7 lê tamanho e ponteiro de argumentos, soma um byte, aloca o frame, copia os argumentos para a posição 1 em 0x7e603 e usa opcode 0x06. O tamanho dos argumentos vem do registro selecionado; a rotina não exige especificamente 484 ou 500 nesse trecho.

Não há parser do corpo do patch nas instruções deste handler. Elas tratam os argumentos como sequência de bytes. Isso explica por que reconstruir o frame foi possível sem decodificar o conteúdo. Não demonstra que toda a DLL jamais interprete dados de patch; a conclusão é restrita ao caminho inspecionado.

## Significado do valor 34

O handler inicializa uma variável com 2 em 0x7e608 e adiciona 0x20 em 0x7e614. Seu valor, **0x22 / 34 decimal**, é passado como quarto argumento na chamada 0x7e64e para 0x7b110.

Em 0x7b110, o argumento é colocado no comprimento do descritor de recepção, acompanhado de ponteiro inicialmente nulo, e o descritor é passado por referência para 0x7b260. Isso liga o valor à capacidade inicial de recepção, em vez de um código de operação ou tamanho declarado do payload de envio.

O [transformador de contexto](transport-context.md) pode ajustar essa capacidade antes da troca. Portanto, 34 não é tamanho exato de resposta validado no sensor, nem prova de 32 bytes de conteúdo significativo depois do status. Também não é motivo para substituir automaticamente o limite do probe atual.

## Callback de conclusão

O wrapper da requisição instala 0x56cd0. A rotina valida seu contexto de saída, guarda o status recebido em 0x56d23 e sinaliza o objeto de espera em 0x56d36. Não lê o descritor de dados da resposta nesse callback.

O status recebido já passou pelo processamento comum e pode ter sido traduzido conforme a [análise de códigos](cleanup-status.md). Assim, sucesso do callback não implica resposta bruta igual a dois bytes zero, conteúdo validado ou captura pronta. O payload de resposta não fornece evidência adicional através desse callback.

## Contrato para uma implementação futura

A implementação futura precisará distinguir:

- Tamanho do frame construído, capacidade do buffer e comprimento efetivamente recebido.
- Falha de transporte, status bruto e retorno traduzido do fornecedor.
- Conclusão de uma solicitação e comprovação dos efeitos do patch.

Respostas menores que dois bytes não permitem parsing de status. Bytes adicionais desconhecidos não devem virar confirmação de compatibilidade ou ser publicados como dump. O parser original de status já separa status e comprimento sem copiar o corpo; não foi criado outro decoder para supor semântica de init.

O encode offline continua limitado aos dois tamanhos investigados e não está ligado ao probe USB. A ausência de um parser no handler do host não justifica enviar o patch sem compreender o estado escolhido e a recuperação.

## Resultado e próxima questão

O [registro de evidência](evidence/init-completion-analysis.json) contém chamadas e imediatos selecionados, conferidos no binário fixado. A interpretação de fluxo permanece manual. Não foi encontrado um consumidor do lado do sensor que decodifique o corpo.

Esta etapa altera apenas documentação/evidência. A base de 67 testes aprovada em v0.22 permanece sem nova execução da suíte. Nenhum novo teste de hardware ou com dedo foi solicitado.

A próxima investigação deve buscar identificação de operações e estado após o envio em fontes específicas do firmware. O caminho de conclusão do host agora está delimitado, mas não resolve os efeitos do payload e não estabelece captura funcional.
