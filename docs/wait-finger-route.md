# Caminhos de consulta e eventos em WaitForFinger

Análise estática da DLL Dell fixada pelo hash na [evidência](evidence/wait-finger-route-analysis.json). RVAs relativos à ImageBase 0x180000000. Não houve execução do driver ou novo teste no leitor.

## Do diagnóstico ao comando candidato 0x77

A função associada ao diagnóstico WaitForFinger tem ramos distintos. Em um deles, a chamada 0x15324 alcança o helper 0x11318, associado à string GetWOFStatus. A cadeia observada é:

| Ponto | Papel |
| --- | --- |
| 0x1136f → 0x46b70 | Consulta por wrapper de estado |
| 0x46c36 → 0x55620 | Wrapper de solicitação interna |
| 0x55751 | Seleciona requisição interna 0x30 |
| 0x55759 | Instala conclusão 0x5a4a0 |
| 0x55786 → 0x5a820 | Dispatcher já conhecido |
| Tabela 0x1164c0 | Slot 0x30 aponta para 0x81dc0 |
| 0x81e17 / 0x81e1b | Handler constrói comando 0x77 de um byte |
| 0x81e37 | Capacidade inicial de recepção 10 |
| 0x81e73 → 0x7b110 | Encaminhamento ao transporte comum |

O índice 0x30 não é o opcode USB. O valor 0x77 é observado na construção interna; transformações de contexto continuam aplicáveis. Não foi demonstrado que a consulta funcione antes da inicialização ou que seja sem efeitos no 00a6.

## Campos de resposta e tradução

Após o tratamento comum de status, o callback 0x5a4a0 lê bytes +1 e +2 do descritor de conteúdo e os guarda em contexto de conclusão +0x14/+0x15. O wrapper 0x55620 os entrega ao chamador quando o status é zero.

Em 0x46b70, o primeiro byte é remapeado: 0 → 0, 1 → 2 e 2 → 1. O segundo integra a pequena estrutura repassada. O código examinado não fornece nomes semânticos comprovados para esses estados. Não atribuir “dedo ausente/presente” apenas pelo nome da função. Também não publicar o segundo byte desconhecido sem entender sua finalidade.

A capacidade 10 não demonstra comprimento exato. Uma futura implementação original terá de verificar o comprimento acessível antes de ler os campos e distinguir estado desconhecido de ausência de dedo; esta análise não incorpora o callback proprietário como decoder ativo.

O helper 0x11318 tem um ramo de repetição para retorno interno 0xd1, compara diferença de contador com 500 e usa uma pausa com argumento 5. As unidades desses wrappers ainda não foram ligadas integralmente às APIs, portanto não anunciar frequência de polling ou timeout total só por esses números. O mapeamento anteriormente observado 0x0401 → 0xd1 também impede chamar qualquer retorno desse ramo de “sensor ocupado” sem evidência adicional.

## Caminho separado de eventos do host

Em outro ramo, WaitForFinger chama 0x44e10 em 0x15105. Essa função chega a 0x5f7e0, que solicita **0x938ae038** pela infraestrutura interna do fornecedor em 0x5f878. O resultado sofre tradução local de estados. Esse código de requisição não é um byte de protocolo USB.

A preparação de callback observada passa por 0x48c00 e 0x5c3a0. O primeiro instala 0x48dd0 e contexto; o segundo guarda callback/contexto/tipo e passa um callback inferior 0x64a90 a 0xe7520. A função 0x48dd0 encaminha os argumentos para o callback registrado. O caminho inferior até recebimento USB e endpoint ainda não foi resolvido.

Na espera em 0x14f2a, o slot importado 0x1102e0 foi identificado como `WaitForSingleObject`; o argumento de espera é 0xffffffff. Isso é uma espera de objeto do host, não leitura direta de endpoint. Flags e caminhos de interrupção influenciam a saída. Um futuro port deverá ter espera limitada e cancelamento explícito, em vez de transplantar esse comportamento literalmente.

## O que falta para o teste com dedo

Agora há um comando candidato de consulta ligado a um ramo e uma cadeia separada de eventos. Ainda faltam a semântica dos estados, o vínculo do callback inferior ao endpoint, a configuração que arma a detecção e sua relação com a inicialização do participante. O início de captura e a obtenção da imagem não foram demonstrados por este rastreamento.

Onze destinos de chamadas diretas e o slot de dispatcher foram conferidos no binário fixado; as interpretações de branches continuam manuais. Nenhum comando 0x77 foi habilitado e nenhum estado foi observado no hardware. A etapa altera somente documentação/evidência; mantém a base de 68 testes validada em v0.25, sem nova execução da suíte.

Não há novo teste com dedo nesta etapa. O próximo passo é rastrear 0xe7520/0x64a90 e identificar de onde chegam os eventos antes de preparar um experimento de detecção.

## Avanço no caminho inferior

A [análise do worker](event-worker.md) ligou um ramo de recepção ao pipe índice 3, correspondente a 0x83 na configuração lida do cache do alvo. O ramo alternativo e os significados dos eventos permanecem pendentes. Nenhum evento foi lido no sensor.
