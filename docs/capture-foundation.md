# Base offline para futura captura

## Caminhos candidatos na DLL

A DLL Dell fixada pelo hash registrado na [evidência](evidence/capture-foundation-analysis.json) contém strings de diagnóstico relacionadas à captura. Suas referências foram localizadas e os intervalos de funções conferidos por `.pdata`:

| String | Referência RVA | Intervalo da função, fim exclusivo |
| --- | --- | --- |
| CCaptureImage::Start | 0x125b1 | 0x124c0–0x14bb0 |
| CCaptureImage::WaitForFinger | 0x14d3c | 0x14ce0–0x1569a |
| CCaptureImage::forceFingerUp | 0x1576f | 0x1570c–0x15eb5 |

Esses nomes são pistas de diagnóstico, não símbolos que comprovem a semântica completa ou uma sequência USB já rastreada. As funções ainda precisam ser ligadas aos comandos, eventos e estados do 00a6. A presença de WaitForFinger não significa que o probe atual detecte toque.

## Formato de referência e seus limites

O driver [VFS7552 do libfprint fixado](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/drivers/vfs7552.c) trata blocos com cabeçalho de seis bytes, comprimento little endian em +2 e linhas de 120 bytes: oito de controle e 112 de pixels. A geometria de referência é 112 × 112. Esse driver registra **138a:0091**, não o 00a6.

O formato ainda não foi observado no leitor do participante. A biblioteca original abaixo é um modelo candidato para testar limites com dados sintéticos, não um decoder validado de imagens do 00a6. Não deve ser aplicada a respostas TLS encapsuladas ou a qualquer transferência sem identificar previamente o formato.

## Componente original de inspeção

[capture_chunk.c](../src/capture_chunk.c) não abre USB, não contém comandos de captura e não está ligado ao probe. A função `validity_inspect_reference_chunk()` recebe um frame acessível, seu comprimento e a contagem anterior de linhas. Retorna somente comprimento de payload, linhas do bloco, total e indicador candidato de frame completo.

O contrato é deliberadamente estrito:

- Exige pelo menos seis bytes, status inicial zero e comprimento declarado igual ao conteúdo exato do frame fornecido.
- Exige payload não vazio e múltiplo inteiro de 120; recusa linha parcial, dados truncados ou bytes extras.
- Recusa acumulação acima de 112 linhas e novas linhas depois de completar o frame.
- Usa subtração antes de somar linhas para evitar overflow, inclusive com `rows_seen = SIZE_MAX`.
- Limpa a saída disponível ao recusar entrada. Não copia pixels, bytes de controle ou os campos desconhecidos do cabeçalho.

Essas verificações são mais restritas que alguns caminhos da referência, que calculam linhas por divisão inteira e podem tolerar sobras. São uma escolha do modelo offline: não demonstram que pacotes reais válidos do 00a6 tenham essa forma. O componente não monta ou salva uma imagem e não classifica uma digital.

## Validação

O teste nativo usa somente bytes sintéticos. Percorre blocos de uma a 112 linhas, capacidade acumulada, comprimentos truncados/excedentes, payloads vazios/parciais, status não zero, ponteiros nulos e contadores extremos. Alterações nos bytes de pixels/controle e campos desconhecidos não mudam o resultado, verificando que só contagens são exportadas.

`make test` passou com **68 testes sem skips**. ASan/UBSan do novo componente passou sem diagnóstico com `ASAN_OPTIONS=detect_leaks=0`; detecção de leaks não foi validada. O probe ativo permanece inalterado, sem emissão de comandos novos.

## Quando haverá teste com o dedo

Ainda falta ligar a inicialização ao caminho de captura real: configuração do sensor, armamento, eventos, leitura limitada e parada/cancelamento. Os anchors acima orientam essa investigação. Só então um experimento de toque/captura terá um resultado interpretável.

Nenhuma imagem ou amostra biométrica foi recebida, gerada ou publicada nesta etapa. Não há teste com dedo solicitado agora. O próximo trabalho é rastrear os comandos/eventos a partir de WaitForFinger e Start, mantendo separadas detecção de toque, captura e cadastro/comparação.

## Avanço no caminho de espera

A [análise seguinte](wait-finger-route.md) liga um ramo de consulta a 0x77 e distingue a cadeia de eventos do host. Os estados, endpoints e preparação da detecção ainda não foram validados no 00a6. Nenhum comando de captura foi ativado.
