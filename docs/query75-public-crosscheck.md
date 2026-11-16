# Conferência pública de 0x75 e correção da ordem dos campos

Revisão manual da DLL fixada e dos fontes públicos no commit fixado. A [evidência](evidence/query75-public-crosscheck.json) registra o fluxo dos ponteiros de saída. Nenhuma execução de driver, TLS, provisionamento ou USB.

## Correção necessária na interpretação anterior

A v0.42 descreveu incorretamente o primeiro DWORD do corpo como fonte do mapper. O callback lê os dois DWORDs, mas é preciso seguir seus ponteiros de saída até o chamador para identificar qual é usado:

| Corpo após status | Campo da conclusão | Local no wrapper | Argumento de saída | Local no chamador |
| --- | --- | --- | --- | --- |
| DWORD em +0 | +0x14 | rsp+0x3c | rdx | rsp+0x50 |
| DWORD em +4 | +0x18 | rsp+0x40 | r8 | rsp+0x48 |

Em 0x63005, o chamador passa `rsp+0x48` em **r8**; em 0x6300a passa `rsp+0x50` em **rdx**. O wrapper grava os resultados nesses ponteiros em 0x54bd3/0x54be1. A comparação e normalização posteriores usam `rsp+0x48`.

Portanto, o valor normalizado e dividido para o mapper é o **segundo DWORD do corpo, offset +4**. A tabela e a normalização previamente identificadas permanecem, mas sua fonte foi corrigida. Os documentos anteriores foram atualizados; nenhum decoder ou comando ativo continha essa interpretação.

## Correspondência com a referência pública

No commit a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920, [sensor.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/sensor.py), função `identify_sensor`, envia 0x75 por `tls.cmd`, verifica status, remove seus dois bytes e interpreta o corpo como `<LHH`.

Nesse perfil público, o primeiro DWORD deve ser zero. Os dois WORDs seguintes são chamados `minor` e `major` e passados a `dev_info_lookup`. São nomes dessa identificação, não a versão 6.7 da ROM. A posição dos WORDs coincide com o segundo DWORD usado pela DLL: metade baixa e metade alta do corpo +4.

Isso corrobora a forma de oito bytes de corpo e resolve a inversão na análise. Ainda não comprova que o 00a6 responda nesse formato em qualquer estado. O campo inicial deve continuar omitido de relatórios reais até ser validado no escopo do experimento.

## O fluxo normal público já abriu TLS

Em [init.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/init.py), `open_common` passa por inicialização, abertura de TLS e upload de extensão antes de `sensor.open`, que chama a identificação.

Em [tls.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/tls.py), `cmd` usa aplicação TLS quando as flags de transmissão e recepção seguras estão ativas; caso contrário, chama o transporte USB direto. A existência desse fallback não demonstra que cada comando funcione antes de inicialização/TLS. No fluxo normal examinado, a identificação ocorre depois da abertura TLS.

Não executar `open_common` como teste de identificação: seus passos anteriores incluem gerenciamento de flash e outras operações já delimitadas em etapas anteriores. Também não concluir que a DLL Dell sempre cifra 0x75; seu transporte é condicionado ao contexto e precisa ser avaliado no ponto de envio.

## Resultado prático e validação

Agora há concordância estrutural entre a DLL e o perfil público para o par de identificadores no segundo DWORD. Falta confirmar o estado de transporte aplicável ao participante, a resposta real e a seleção completa do programa. Isso ainda não habilita uma consulta ativa nova.

Foram conferidas as instruções dos argumentos de saída e das leituras no wrapper. Os três fontes públicos foram conferidos localmente contra o commit fixado, sem importar módulos. Somente documentos/evidência; mantém a base de **91 testes aprovados na v0.37**, sem nova execução necessária. Não houve teste com dedo ou envio USB.

A [continuação do transporte Dell](query75-transport-order.md) delimita a preparação anterior à identificação e o atalho por contexto existente, sem concluir transporte universal.
