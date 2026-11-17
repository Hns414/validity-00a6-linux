# Restauração adiada pela máquina de estados

Continuação da [consulta e dos caminhos de restauração](timeout-query-restoration.md). A nova [evidência sanitizada](evidence/deferred-timeout-restoration.json) confere seis chamadas, doze âncoras, a entrada do estado 6 e um destino IAT. Análise estática da DLL fixada, sem Windows ou USB.

## Erro guardado não é necessariamente retorno imediato

No caminho já examinado, a chamada **0x7a0e2 → 0x75600** grava seu resultado em **auxiliar +0x4ec**. Se falhar, seleciona estado **6** em 0x7a119 e salta ao epílogo. Esse resultado não é copiado ali para a variável local de retorno, em rsp+0x40. No caminho que chega a esse ramo após sucesso das precondições, essa variável permanece zero; a falha da operação fica guardada para outro estado.

O epílogo pode substituir um retorno zero por erro de limpeza, mas o helper **0xd6160** chama o import **LeaveCriticalSection**, IAT **0x1105c0**, e retorna zero no caminho de entrada não nula. Portanto, naquele caminho, a primeira invocação pode retornar zero apesar do erro guardado em auxiliar +0x4ec. Isso distingue retorno de avanço da máquina de estados de resultado final da operação.

## O chamador pode voltar ao estado 6

A função **0x746c0** chama a máquina em **0x74757**. Seu laço volta por **0x747ac → 0x7473f** quando o retorno é zero; só continua se o indicador de conclusão não for 1 e não houver erro. Um retorno não zero deixa esse laço, com tratamento específico para 0xca e mapeamento de outros erros para 0xcc.

A tabela **0x7a770**, indexada pelo estado, associa **6 → 0x7a4e0**. Nesse ramo:

1. Se auxiliar +0x518 for maior que zero, tenta reaplicar esse timeout ao pipe de índice 1 pela chamada **0x7a526**.
2. Uma falha do setter é registrada no caminho de diagnóstico; esse ramo continua até carregar o resultado guardado em **auxiliar +0x4ec**, em 0x7a555, para a variável de retorno.
3. Chama **0x758e0** e marca conclusão 1 em **0x7a578** antes do epílogo.

Assim, existe uma **tentativa adiada de restauração antes da entrega do erro guardado**, quando o laço prossegue com o mesmo contexto e as precondições da próxima invocação são satisfeitas. A v0.70 delimitou corretamente o desvio da primeira passagem; a análise atual mostra por que esse desvio isolado não prova abandono da restauração.

## O que os helpers de limpeza esclarecem

**0x7af60** chama **0x7aa50**. Este decrementa o DWORD do contexto em +0x08 sob proteção de um helper de sincronização. Se o resultado for maior que zero, libera a proteção por 0xd6160 e retorna zero; se não for maior que zero, segue para um ramo extenso de destruição. **0x7ade0**, usado para obter o contexto, incrementa esse mesmo campo antes de devolver a referência.

Isso sustenta a interpretação de retenção/liberação de referência nesses caminhos. O ramo completo de destruição, seus helpers e efeitos indiretos não foram auditados exaustivamente; não atribuir a eles restauração de timeout sem prova.

## Limites e consequência para Linux

Não há garantia universal de restauração: o estado 6 ignora o setter se o valor guardado for zero; uma nova invocação pode falhar antes do despacho; o setter pode falhar; outros chamadores ou concorrência podem alterar o contexto. Nenhuma dessas situações foi observada no participante.

Para a implementação original, o resultado da operação e o progresso da máquina precisam ser campos distintos, e a limpeza deve ter um caminho definido mesmo após erro. Uma falha ao restaurar configuração também precisa continuar observável. Essa arquitetura ainda não foi implementada no transporte ativo.

A investigação de timeout agora tem uma ligação condicional entre ajuste, erro, nova passagem e tentativa de restauração. O próximo trabalho deve voltar ao contrato de recepção e enquadramento, mantendo prazo de transferência separado de fim de mensagem. Probe inalterado, sem teste com dedo. Etapa documental: base anterior de **119 testes aprovados**, sem repetir a suíte.
