# Preparação local do contexto auxiliar

Continuação do [descarte e nova alocação](auxiliary-context-discard.md). Análise estática da DLL fixada; [evidência sanitizada](evidence/local-auxiliary-preparation.json) com dez chamadas, quinze âncoras e destino IAT conferidos. Nenhum recurso criptográfico ou comando USB foi criado/executado nesta investigação.

## Preparação de contadores e flags

A função 0x753f0 seleciona primeiro um descritor por 0x78df0 e o guarda em auxiliar +0xf8. Em seguida chama dois helpers:

| Helper | Operação local delimitada |
| --- | --- |
| 0x78cf0, chamado em 0x7554a | Solicita zero em oito bytes de auxiliar +0xf0; se o primeiro WORD do descritor +0xf8 não for zero, acrescenta bit 1 ao DWORD auxiliar +0x128. |
| 0x78d70, chamado em 0x75567 | Solicita zero em oito bytes de auxiliar +0xe8; sob a mesma condição do descritor, acrescenta bit 2 ao DWORD auxiliar +0x128. |

Na preparação examinada, a seleção inicial usa entrada zero. O helper 0x78df0 procura um identificador WORD numa tabela de quatro descritores de tamanho 0x18, retornando ponteiro correspondente ou nulo. Não atribuir nomes de algoritmos ou invariantes de sessão a todos os descritores sem auditar seus campos e os demais usos.

## Criação de hash no host

**0x7559d → 0x76050 → 0xdf8a0**, com seletor zero e endereço de saída auxiliar +0x120, chega à chamada importada **CryptCreateHash**, IAT **0x1100d0**, em **0xdf9be**. O seletor zero determina ALG_ID **0x800c**, identificado como **CALG_SHA_256** na [documentação oficial de ALG_ID](https://learn.microsoft.com/en-us/windows/win32/seccrypto/alg-id).

O helper exige o contexto de provedor global e uma saída não nula, inicializa essa saída com nulo e verifica o retorno da API. Depois prepara um objeto local que guarda o handle e só publica sua referência no caminho de sucesso. Falha de API ou alocação pode encerrar a preparação. O ciclo completo de descarte em todas as falhas desse helper permanece fora do que foi demonstrado aqui.

Criar esse hash é preparação local. Isso não demonstra que dados tenham sido autenticados, que uma negociação tenha sido concluída ou que o sensor compartilhe o mesmo estado. O hash também não identifica sozinho o protocolo completo.

## Identificadores iniciais consultam dados em memória

Na máquina 0x79500, as chamadas **0x79778** e **0x798e2** chegam a **0x8d550** com identificadores WORD 7 e 5, respectivamente. A rotina obtém, por 0x5e140, a referência guardada em **contexto +0x228**; consulta comprimento em +0x1c e ponteiro em +0x20 dessa referência.

O corpo percorre entradas em memória: lê identificador WORD no deslocamento 0 e comprimento WORD no deslocamento 2; considera um prefixo de **0x24 bytes** para localizar o conteúdo e avançar à próxima entrada. Esses identificadores são seletores dessa busca, **não opcodes USB nesses pontos**. A origem e o preenchimento do conjunto de dados ainda precisam ser rastreados.

A opção de processamento fornecida ao helper também importa: a chamada com identificador 7 passa opção 1 e pode alcançar **0x8d723 → 0x71b40** antes de devolver a saída. A chamada com identificador 5 passa opção zero e pode devolver referência ao conteúdo encontrado. O helper 0x71b40 não foi integralmente auditado nesta etapa; não presumir que todo o processamento posterior à busca seja uma simples cópia ou estritamente local.

O percurso de memória acima também não constitui prova completa de limites do parser proprietário. Não foi criado um parser operacional para esse formato nem publicado seu conteúdo.

## Consequência e próximo ponto

A criação do auxiliar reúne alocação, inicialização de campos e criação de hash local. Os estados iniciais ainda dependem de dados já disponíveis no contexto e de processamento adicional. Portanto, nova alocação não basta para definir uma sequência de recuperação do sensor.

Próximo trabalho: rastrear o produtor de contexto +0x228 e a opção de processamento, para então localizar com precisão as operações de transporte exigidas pelo início da sessão. Probe inalterado; sem USB, captura ou teste com dedo. Etapa documental: base de **121 testes aprovados na v0.72**, sem repetir a suíte.

Os [produtores do contêiner de sessão](session-entry-container.md) separam criação, preenchimento e descarte; a opção processada devolve nova saída, com origem e semântica ainda pendentes.
