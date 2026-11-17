# Ajuste de timeout durante a sessão

Continuação das [políticas iniciais](pipe-policy-setup.md). Análise estática da mesma DLL fixada; [evidência sanitizada](evidence/runtime-pipe-timeout.json). Foram conferidas sete chamadas diretas, doze âncoras de argumentos e a entrada da tabela de despacho. Nenhuma execução Windows ou transferência USB foi realizada.

## Pedido interno de configuração

O wrapper **0xe7430** encaminha índice de pipe e timeout DWORD para **0xee0a0**, pela chamada **0xe7481**. Este último monta uma entrada de **8 bytes**, com dois DWORDs: índice no primeiro e timeout no segundo. Em **0xee12b** seleciona o pedido interno **0x938ae054** e em **0xee13e** chama o dispatcher pelo slot +0x10.

A tabela do dispatcher resolve esse pedido para **0xef62d**. O caso exige entrada não nula com comprimento exatamente 8, recupera os dois campos e chama **0xf1400** em **0xef67c**. O setter já identificado consulta o pipe e aplica política 3, PIPE_TRANSFER_TIMEOUT, pelo slot WinUSB +0x60.

Esse pedido é uma interface interna do driver Windows; **não é opcode USB nem comando para enviar ao sensor**. O significado em milissegundos vem da [documentação da política WinUSB](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/winusb-functions-for-pipe-policy-modification).

## Valor temporário no caminho de estados

No caminho da função **0x79500** examinado:

| Ponto | Comportamento estático |
| --- | --- |
| 0x7a03e–0x7a05c | Fornece o endereço auxiliar +0x518 como uma das saídas do helper 0xe7370. |
| 0x7a093–0x7a0a6 | Solicita timeout de **8000 ms** para pipe de índice **1**, após verificar sucesso do helper anterior. |
| 0x7a61d–0x7a636 | Em um caminho posterior de saída, solicita novamente índice 1 com o DWORD guardado em auxiliar +0x518. |

O helper **0xe7370** consulta índice 0 primeiro, pela chamada 0xe73c0, usando sua terceira entrada como destino; depois consulta índice 1 em 0xe73f8 usando a segunda entrada. Isso associa o campo auxiliar +0x518 à saída referente ao índice 1. A ligação completa dessa consulta à API inferior ainda deve ser auditada; não presumir que toda consulta ou restauração teve sucesso.

A ordem de endpoints do participante associa índice 1 a 0x81 IN somente se o Windows consultar a mesma configuração e ordem. O caminho mostra intenção de guardar, alterar e reaplicar um valor; **não prova restauração em todas as saídas**, execução no participante ou prazo total de uma operação.

## Wrapper que ajusta dois pipes

A função **0x63a70** recebe valor para índice 0 na segunda entrada e para índice 1 na terceira. Consulta os valores pelo helper 0xe7370, compara e só chama o setter quando há diferença: índice 1 em **0x63b1e**, depois índice 0 em **0x63b5d**. Uma falha pode interromper a sequência; não há rollback demonstrado nesse wrapper. As saídas opcionais recebem os valores consultados apenas no caminho que alcança esse trecho.

## Consequência para o driver Linux

Os 2000 ms iniciais não são constantes de toda a sessão. O caminho de 8000 ms é uma configuração de transferência, sem demonstrar término de mensagem ou garantia de registro único. Não copiar esses prazos para o probe nem ampliar suas operações com base apenas nessa análise.

Próximos pontos: auditar a consulta inferior, as saídas que deixam de reaplicar o valor e os chamadores superiores de 0x63a70. O contrato de tamanho e enquadramento da resposta continua pendente. Etapa documental; base anterior de **119 testes aprovados**, sem repetir a suíte e sem teste com dedo.

A [consulta e os caminhos de restauração do timeout](timeout-query-restoration.md) foram ligados à API; um desvio de erro evita os setters explícitos, com efeitos indiretos de limpeza ainda pendentes.
