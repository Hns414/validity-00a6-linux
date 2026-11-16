# Preparação anterior ao frame de inicialização

Análise estática da DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`. RVAs relativos à ImageBase 0x180000000. Complementa o [consumidor de 484 bytes](init-484-selection.md); nenhuma DLL foi executada ou nova operação enviada ao sensor.

## Solicitação interna 8

A chamada preparatória 0x537b0 cria a solicitação interna **8** em 0x5387f, instala conclusão 0x61dd0 e usa o dispatcher em 0x538b4. O slot da tabela em 0x116380 aponta para **0x7ed80**. O número 8 é índice interno do driver, não opcode USB.

O handler valida o contexto e examina duas estruturas do host: cache em contexto +0x220 e estrutura de versão em +0x28. Há dois caminhos de conclusão.

| Condição observada no handler | Caminho |
| --- | --- |
| Cache presente com DWORD +0 ou byte +8 não zero | Montagem e encaminhamento ao transporte |
| Sem o gatilho acima, estrutura de versão presente com byte +0x0f não zero | Montagem e encaminhamento ao transporte |
| Nenhum desses gatilhos | Conclusão local de status zero, sem transporte neste handler |

A presença do cache, sozinha, não basta para disparar envio. DWORD +4 do cache não é gatilho nesse handler. Esses são campos de memória do host; não foram medidos pelo probe do participante.

## Caminho que pode enviar 0x1a

Em 0x7ee67 o handler prepara comando **0x1a**; em 0x7ee6b chama o construtor 0x83220 com tamanho total de um byte. O argumento de capacidade de recepção é 2 em 0x7ee87. A chamada de transporte ocorre em 0x7eec3 para 0x7b110.

É uma construção interna de frame de um byte e capacidade indicada ao transporte, não uma captura de barramento nem prova de comprimento real da resposta. Transformações e estado do transporte continuam relevantes. O significado e os efeitos do comando 0x1a não foram estabelecidos; não o chamar de reset seguro, unload comprovado ou consulta sem efeitos.

No outro ramo, 0x7ee5d chama diretamente a conclusão com descritor nulo e status zero. Assim, retorno zero do wrapper pode representar conclusão local, sem qualquer resposta de dispositivo. Não se deve registrar esse sucesso como evidência de troca USB.

## Conclusão e limpeza local

A conclusão 0x61dd0 guarda o status recebido no contexto de espera e sinaliza seu objeto de sincronização. Ela não decodifica conteúdo de resposta nesse trecho.

Se a chamada de dispatcher retorna zero, o wrapper lê o status de conclusão e chama 0x5c480 em 0x538d6. Essa chamada ocorre mesmo quando o status de conclusão lido é não zero. A rotina de limpeza:

- Zera byte +0x0f da estrutura de versão quando o ponteiro existe.
- Zera DWORD +0, DWORD +4 e byte +8 do cache quando presente.
- Não faz troca USB nos trechos examinados dessa rotina.

Não interpretar essa alteração local como confirmação de alteração, reset ou recuperação do dispositivo. No consumidor externo 0x62ad0, retorno zero ou 0xd1 da preparação permite seguir para a requisição 7; outros retornos interrompem. O significado de 0xd1 e sua relação com status de dispositivo ainda não foram demonstrados.

Há também chamada ao mesmo wrapper antes do preenchimento da estrutura de versão, em 0x64c9d, no fluxo externo já analisado. A ordem parcial é insuficiente para decidir os gatilhos: estruturas preexistentes podem mudar qual caminho executa. Não foi provado que a abertura sempre omita ou sempre envie 0x1a.

## Implicação para o projeto

Reproduzir somente `0x06 + argumentos` não reproduz a preparação do fornecedor. Também seria incorreto adicionar 0x1a incondicionalmente com base nesta descoberta. A próxima investigação deve ligar os campos de estado aos comandos e retornos que os atualizam, e compreender os efeitos de 0x1a e do payload antes de propor execução.

O [registro estruturado](evidence/pre-init-preparation-analysis.json) inclui cinco destinos de CALL rel32 conferidos e o ponteiro de dispatcher lido diretamente no binário fixado. A interpretação dos branches é manual, não prova automática de equivalência completa.

Esta etapa altera somente documentação/evidência. A base de 59 testes validada em v0.18 permanece, sem nova execução da suíte. Não há novo comando ativo ou teste de hardware solicitado ao participante.
