# Descarte do contexto auxiliar após erro

Continuação do [tratamento de leituras truncadas](truncated-read-path.md). Análise estática da DLL fixada; [evidência sanitizada](evidence/auxiliary-context-discard.json) com onze chamadas diretas e onze âncoras conferidas. Nenhum código proprietário, conteúdo de sessão ou dado biométrico é publicado.

## Contexto do host é invalidado

Após erro 0xca da normalização, o caminho já delimitado chama 0x74bb0 com segunda entrada zero. Se o helper supera a validação e a aquisição de sincronização, chama **0x758e0** com o endereço do campo **contexto +0x50**. A rotina não recebe um handle USB diretamente: recebe um endereço que contém o ponteiro auxiliar.

Se esse ponteiro já for nulo, 0x758e0 sai. Caso contrário, o corpo examinado:

| Região/recurso auxiliar | Operação observada |
| --- | --- |
| Ponteiros +0x108, +0x110, +0x00 e +0x38 | Quando não nulos, encaminha à rotina 0xd5410 e anula os campos. |
| Região +0x4f0 | Encaminha ao helper 0xdb200. |
| Recurso +0x120, se não nulo | Chama 0xdfbe0 com saída local e capacidade inicial 32; sem atribuir aqui significado criptográfico completo. |
| Região +0x08, tamanho 0x30 | Solicita preenchimento com zero por 0xd5430. |
| Região +0x48, tamanho 0x80 | Solicita preenchimento com zero por 0xd5430. |
| Estrutura inteira, tamanho **0x528 (1320 bytes)** | Solicita preenchimento com zero em **0x75a4a**. |
| Ponteiro auxiliar | Encaminha à rotina de liberação 0xd5410 em **0x75a62** e anula o ponteiro do chamador em **0x75a6c**. |

O resultado relevante é o campo contexto +0x50 nulo depois desse caminho. Isso impede reutilizar a mesma estrutura por esse campo, mas não prova ausência de aliases em outros pontos, limpeza segura de todos os recursos ou apagamento resistente a otimizações. O ciclo de vida dos recursos internos ainda não foi auditado por completo.

## Consulta posterior e nova alocação

O predicado **0x74c90**, sob suas precondições de sincronização, consulta contexto +0x50. Se nulo, retorna zero. Se não nulo, retorna 1 somente quando auxiliar +0x100 é 0xff. Esse predicado verifica presença/modo; não deve ser chamado de prova de autenticação ou de sessão válida sem fechar os demais invariantes.

O chamador **0x746c0** usa esse predicado antes de executar seu laço de estados. Quando chega a 0x79500 com auxiliar ausente, o ramo já examinado chama **0x753f0** para preparar a estrutura. No caminho de ponteiro nulo, essa função solicita **0x528 bytes** em **0x7543d**, verifica a alocação e solicita preenchimento inicial com zero em **0x75486**. Não se trata de ressuscitar a estrutura descartada.

A preparação inclui outros helpers que podem falhar. Só no caminho que os supera são definidos parâmetros posteriores e o estado inicial: valor 0 quando a segunda entrada é 2, ou valor 1 para as demais entradas, em 0x755d0/0x755e1. Esses valores são estados internos; não demonstram que o sensor esteja pronto nem autorizam enviar qualquer sequência nova.

## O que permanece aberto

Descarte do estado do host não equivale a reset USB, encerramento confirmado da sessão remota ou recuperação do leitor. Não foi demonstrado que os recursos internos e o sensor retornem juntos a um estado inicial conhecido. Portanto, **não implementar retry automático, nova negociação ou replay** como consequência dessa análise.

Para o driver original, uma falha de normalização deve invalidar o contexto associado; uma operação posterior só poderá prosseguir após um procedimento de recuperação estabelecido e validado. A criação de uma nova estrutura em memória é apenas uma parte desse requisito.

Próximo ponto: auditar o início da preparação e os efeitos observáveis dos estados iniciais, distinguindo alocação local de negociação com o dispositivo. Probe inalterado, sem USB e sem teste com dedo. Etapa documental: base de **121 testes aprovados na v0.72**, sem repetir a suíte.

A [preparação local do auxiliar](local-auxiliary-preparation.md) liga a criação de hash à CryptoAPI e separa seletores de busca em memória de comandos USB.
