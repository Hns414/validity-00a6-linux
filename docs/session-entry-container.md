# Produtores do contêiner de entradas da sessão

Continuação da [preparação local](local-auxiliary-preparation.md). Análise estática da DLL fixada; [evidência sanitizada](evidence/session-entry-container.json) com onze chamadas diretas e onze âncoras de campos/controle conferidas. Sem executar a DLL ou consultar conteúdo do participante.

## O campo +0x228 tem um setter identificado

**0x5e1b0** obtém o contexto por 0x7ade0 e, depois de sucesso, guarda sua segunda entrada em **contexto +0x228**, em **0x5e1f5**. O getter 0x5e140 devolve esse campo. Foram encontrados dois chamadores diretos do setter no texto examinado:

| Chamador | Efeito delimitado |
| --- | --- |
| 0x8d961, dentro de 0x8d810 | Registra a referência do contêiner. |
| 0x8da23, dentro de 0x8d990 | Passa nulo após descarte do contêiner. |

Isso identifica uma rota de escrita, sem excluir aliases ou outros escritores indiretos.

## Criar o contêiner não preenche as entradas

O caminho superior em **0x65476** verifica contexto +0x228; quando ausente, chama **0x65488 → 0x8d810**. Este consulta o getter e, se não houver estrutura, solicita **0x28 (40) bytes** e os inicializa com zero. Há uma condição obtida por 0x5f720 que controla a consulta adicional por 0x5bf40 e o preenchimento de metadados antes de registrar a referência.

Esse inicializador não demonstra que o buffer de entradas em +0x20 já esteja preenchido. As semânticas completas de 0x5f720 e dos metadados consultados não foram fechadas; não atribuir sua origem ao sensor por suposição.

Um produtor separado, **0x8ca30**, aloca um buffer do tamanho recebido e solicita preenchimento com 0xff. Pelo getter, instala na estrutura os campos:

| Campo do contêiner | Operação observada |
| --- | --- |
| +0x18 | Contagem usada inicializada com zero. |
| +0x1c | Tamanho/capacidade recebido do chamador. |
| +0x20 | Ponteiro para o buffer alocado. |

Depois chama **0x8da40**, usado também por **0x8d3e0**, para acrescentar uma entrada. O helper considera prefixo de 0x24 bytes e conteúdo de comprimento WORD. Nos pontos examinados, grava identificador e comprimento nos primeiros quatro bytes, passa a região seguinte a um helper e copia conteúdo após mais 0x20 bytes. Só atualiza a contagem usada no caminho de sucesso. Não foi criado um encoder operacional nem publicada a região intermediária ou o conteúdo.

A existência desse produtor fecha a ligação entre contêiner e buffer consultado por 0x8d550. Ainda falta rastrear os chamadores superiores que escolhem e fornecem os conteúdos: não há prova de que sejam todos respostas USB, constantes locais ou dados persistidos.

## Descarte independente do auxiliar

**0x8d990** consulta a referência, encaminha o buffer +0x20 à rotina de liberação se presente, anula esse campo, solicita zero na região +0x18 de tamanho 0x10, libera a estrutura e chama o setter com nulo. É um ciclo de vida separado do auxiliar de 1320 bytes investigado anteriormente. Descartar o auxiliar não implica, por si só, descartar esse contêiner em contexto +0x228.

A análise não prova recuperação do dispositivo, apagamento seguro de conteúdo ou ausência de referências externas.

## Processamento opcional devolve nova saída

A opção 1 de 0x8d550 chama **0x71b40** com o conteúdo encontrado. O corpo examinado ajusta a posição de entrada conforme seu primeiro byte e contém processamento em duas passagens por **0xe05b0**, com uma chamada intermediária a **0x72450**. Faz alocações e, no caminho de sucesso, copia o resultado para uma nova região e publica seu ponteiro e comprimento em **0x71ed3/0x71ee2**.

Portanto, a saída dessa opção não deve ser tratada como simples referência ao conteúdo original. A semântica dos helpers aninhados, limites e contrato completo de propriedade ainda precisam ser auditados. Não chamar esse processamento de autenticação, decifragem ou descompressão apenas pela forma das chamadas. A opção zero continua podendo devolver uma referência ao conteúdo no contêiner, com duração dependente de seu proprietário.

## Próximo ponto

Rastrear os chamadores de 0x8ca30 e 0x8d3e0 e os helpers de processamento para identificar a origem das entradas e a fronteira real com o transporte. Os contratos de capacidade e duração precisam ser definidos antes de implementar o formato. Probe inalterado; sem USB, captura ou teste com dedo. Etapa documental: base de **121 testes aprovados na v0.72**, sem repetir a suíte.

O [carregador candidato de entradas](candidate-entry-loader.md) tem um ramo ligado ao transporte, mas sua alcançabilidade no fluxo ativo ainda não foi demonstrada.
