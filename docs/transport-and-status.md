# Caminho WinUSB e tratamento de status

Esta análise é estática, limitada à DLL Dell de SHA-256 6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7. Não é um trace de hardware, execução do driver ou prova de qual caminho estaria ativo no estado atual do leitor.

## Correção de papel do callback

O callback no offset +0x20 do contexto usado por 0x7b110 é instalado em RVA **0x65919**, com destino **0x7dd60**. A inspeção desse destino mostra tratamento de resposta: leitura de status, separação dos dados e chamada da conclusão.

Portanto, a chamada indireta em **0x7b213** é pós-processamento da resposta. Ela não é o ponto de escrita USB que a etapa anterior ainda tentava localizar. Os offsets +0x20 e +0x30 em outros objetos pertencem a estruturas diferentes e não devem ser confundidos.

## Cadeia até a troca de buffers

| RVA / valor | Papel observado |
| --- | --- |
| 0x7e540 | Handler monta frame interno com opcode 0x06 e argumentos |
| 0x7b110 → 0x7b260 | Prepara/processa descritores de envio e recepção; há transformação condicional conforme contexto |
| 0x7b4c9 | Caminho que chama 0xe6f50 com descritores; outro caminho em 0x7b491 adiciona metadados para comandos específicos |
| 0xe6f50 → 0xede20 | Encaminhamento para uma requisição do fornecedor |
| 0x938ae058 | Código da requisição interna; não é byte de protocolo USB |
| 0xed60b | Instala handler 0xee420 no offset +0x10 de um objeto de dispatch |
| 0xedefa | Chamada indireta desse objeto, com a requisição acima |
| 0xee9dc / 0xee9ac | Tabelas de seleção de case; offset 0x58 seleciona índice 6 e destino 0xee721 |
| 0xee7c3 | O case encaminha a troca para 0xeea70 |
| 0xeea70 | Chama escrita por 0xef7d0 e, se essa etapa retornar sucesso, leitura por 0xef750 |
| 0xef7d0 → 0xf10d0 | Wrapper de escrita |
| 0xef750 → 0xf0f50 | Wrapper de leitura |

A resolução do case foi conferida lendo os dados das tabelas, além da análise das instruções. Essa cadeia mostra um caminho implementado na DLL; ainda não mede seus argumentos em runtime no participante.

## Ligação aos símbolos WinUSB

O objeto global em VA 0x180223900 é alocado em 0xeef64 e inicializado por chamada a 0xf01b0 em 0xeefb5. O inicializador resolve funções dinamicamente:

- A string WinUsb_ReadPipe é usada perto de 0xf0279; o ponteiro resolvido é armazenado no offset +0x28 do objeto em 0xf0293.
- A string WinUsb_WritePipe é usada em 0xf0297; o ponteiro resolvido é armazenado no offset +0x30 em 0xf02b1.

Os wrappers consultam pipes e chamam esses slots do mesmo objeto global:

| Operação | Consulta de pipe | Chamada da API resolvida |
| --- | --- | --- |
| Escrita | 0xf1174 | 0xf11d8, slot +0x30 |
| Leitura | 0xf0fe9 | 0xf104d, slot +0x28 |

O PipeID vem do resultado da consulta, não de um literal fixo 0x01/0x81 nesses pontos. Os endereços dos endpoints do participante já estão documentados no sysfs, mas o vínculo entre índice de pipe e endpoint deve ser validado no contexto escolhido; não foi observado por trace do driver Windows.

## Transformações e limite da conclusão

Antes da troca, 0x7b260 chama 0x747e0 e outras funções que podem alterar ponteiro/comprimento conforme estado interno. Em um caminho, comandos específicos recebem metadados adicionais; os testes observados incluem 0x50, 0x80 e 0x82. A identificação de uma cadeia até WinUSB não demonstra que todo contexto enviaria o frame interno inalterado.

As instruções de construção do frame 0x06 são conhecidas, mas ainda não foi avaliada a seleção completa de contexto para o estado atual do 00a6. Esta etapa não afirma que a inicialização possa ser executada sem consequências, nem resolve os efeitos do payload no sensor.

## Tratamento da resposta e componente original

O callback 0x7dd60 usa o status inicial de dois bytes no caminho comum. A conversão em 0xd6560 mantém o valor no host x86-64 little endian. O caminho para comando 0x44 tem tratamento especial; respostas encapsuladas não devem receber parsing de status cleartext por suposição.

O novo componente [status_reply.c](../src/status_reply.c) é original e tem contrato restrito:

- O chamador identifica previamente uma resposta como candidata a status cleartext e fornece seu comprimento real acessível.
- Menos de dois bytes, ponteiro nulo ou saída nula resultam em recusa; a estrutura de saída é limpa quando disponível.
- O status é lido explicitamente em little endian, junto da contagem de bytes restantes. Nenhum payload é copiado, interpretado ou armazenado.
- Parsing concluído também pode conter status não zero; o retorno da função não é sucesso de comando ou de biometria.

A função centraliza as verificações já usadas pelo resumo E1 e pelo indicador candidato de E2. Os schemas 1/2/3 e as consultas USB permanecem os mesmos. Não foi reproduzida automaticamente toda a semântica do SDK ou seu mapeamento de códigos de erro.

## Validação e próximo passo

A suíte de 52 testes passou sem skips no ambiente de desenvolvimento. O teste nativo percorre comprimentos 0–128, verifica little endian, recusa truncamentos e ponteiros nulos, limpa a saída ao rejeitar entrada e garante independência em relação aos bytes de payload. ASan/UBSan também passou com ASAN_OPTIONS=detect_leaks=0; detecção de leaks não foi validada por esse sanitizador.

O [registro da análise](evidence/transport-route-analysis.json) contém somente coordenadas e conclusões selecionadas. A cadeia de chamadas foi examinada manualmente; a suíte de testes não é verificador de disassembly. Nenhuma nova operação USB foi executada para essa análise.

A próxima questão é quais condições de contexto escolhem transformação/passthrough para init_00 e quais operações o conteúdo carregado executa. Compor e encaminhar um pacote corretamente não resolve sua persistência ou a recuperação. Não há novo teste solicitado ao participante.
