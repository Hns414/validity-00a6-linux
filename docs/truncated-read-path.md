# Leituras truncadas no caminho examinado

Continuação da [fronteira entre leitura e registros](readpipe-record-boundary.md), após a investigação de políticas e timeouts. Análise estática manual da DLL fixada; a [evidência sanitizada](evidence/truncated-read-path.json) confere seis chamadas diretas, dezesseis âncoras e o destino IAT de GetLastError. Sem leitura USB ou resposta truncada real observada.

## Ramo síncrono e propagação da falha da API

A troca 0xeea70 chama 0xef750 em 0xeead9. Esse wrapper fornece **Overlapped nulo**, embora o helper inferior 0xf0f50 também suporte outros chamadores assíncronos. O helper chama WinUsb_ReadPipe em 0xf104d e, quando a API falha, consulta GetLastError pelo IAT 0x1105d8 em 0xf1054.

No helper genérico, erro numérico 0x3e5 só é aceito como progresso se Overlapped não for nulo. Portanto, essa exceção não vale para a rota síncrona examinada. Erro 0x79 vira status interno 0x75; outras falhas desse ramo viram 0xca. A troca superior converte 0x75 em 0xca em 0xeeae2–0xeeae9. Não há nova chamada de leitura nesse corpo após falha.

A [documentação de WinUsb_ReadPipe](https://learn.microsoft.com/en-us/windows/win32/api/winusb/nf-winusb-winusb_readpipe) distingue chamada síncrona com Overlapped nulo de operação assíncrona pendente. Numa operação assíncrona, o comprimento não deve ser tratado como final antes da conclusão. Aqui a passagem síncrona é demonstrada pelos argumentos, sem generalizar esse contrato para todos os chamadores.

O wrapper só publica a quantidade transferida depois do retorno interno de sucesso. Uma falha da API não é transformada neste caminho em resposta parcial válida para o normalizador.

## Sucesso de leitura não significa estrutura completa

Em 0x7b260, falha da troca desvia para a saída antes da normalização. Se a troca retorna sucesso mas o comprimento é zero, o ramo também pula o normalizador; isso não deve ser descrito como aceitação de envelope vazio pelo parser. Se o comprimento é positivo, **0x7b4fb → 0x749e0** recebe o buffer e o descritor de comprimento.

Quando as condições de contexto, estado 7 e modo 0xff selecionam a normalização, **0x74b3f → 0x774e0** passa esse comprimento ao parser. Os pontos examinados mostram:

| Condição | Ação |
| --- | --- |
| Menos de 5 bytes restantes ao alcançar a verificação 0x775f7 | Define erro local 0xd3 em 0x77616. |
| Conteúdo declarado maior que os bytes restantes após o cabeçalho, em 0x776f2 | Define erro local 0xd3 em 0x77710. |
| Saída com erro do parser | Marca auxiliar +0x4dc e converte o resultado em 0xca em 0x77d7d. |
| Normalizador recebe erro do parser | Salta a cópia e a atualização de comprimento que só ocorreriam após sucesso. |

**Ressalva de escopo:** a consulta de marcador 0x00/0xff pode ocorrer antes da verificação de cinco bytes, sob o predicado já documentado. Portanto, esta tabela descreve os ramos alcançados; não prova que todo buffer curto passe pela mesma verificação nem é uma prova de segurança de memória da DLL. O componente C original verifica os bytes acessíveis antes de qualquer acesso correspondente e rejeita marcadores fora de seu escopo estrito.

## Sem remontagem local demonstrada

Após erro 0xca do normalizador, 0x7b260 chama **0x74bb0** com segunda entrada zero em 0x7b51c e sai com erro. O helper, quando supera suas precondições, chama 0x758e0 para o campo de contexto +0x50. A operação condicional 0x75700 exige segunda entrada igual a 1 e não é selecionada por essa chamada com zero. Não presumir reset USB ou recuperação do sensor a partir do nome informal de limpeza.

O wrapper 0x7b110 só alcança seu callback de conclusão depois de sucesso de 0x7b260; o caminho de erro pula esse callback e libera buffers locais. Nos corpos examinados não há preservação de fragmento seguida de nova leitura para completar um cabeçalho ou conteúdo. Isso não exclui buffering interno do WinUSB, outra rota de transporte ou uma nova operação iniciada acima desses wrappers.

## Consequência para o projeto

O comportamento delimitado é rejeitar truncamento nos ramos examinados, sem remontagem local demonstrada. Ele não prova que as respostas reais sempre cheguem completas, nem autoriza concatenar leituras arbitrárias. O [componente C de envelopes](record-envelope-c-component.md) continua recebendo exclusivamente buffers completos para análise estrutural, sem conduzir novas leituras.

Próximo ponto: seguir a invalidação/liberação do contexto em 0x758e0 e determinar o requisito de nova sessão após erro de normalização. Probe inalterado; sem USB, captura ou teste com dedo. Etapa documental: base de **121 testes aprovados na v0.72**, sem repetir a suíte.

O [descarte do contexto auxiliar](auxiliary-context-discard.md) liga a falha à anulação do estado local; nova alocação foi delimitada, sem demonstrar recuperação do sensor.
