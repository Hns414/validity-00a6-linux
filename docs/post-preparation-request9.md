# Requisição posterior à preparação e construção de 0x02

Análise manual da DLL Dell fixada, com [evidência estruturada](evidence/post-preparation-request9.json). RVAs relativos à ImageBase 0x180000000. Sem execução ou transferência USB.

## Encadeamento após os blocos selecionados

No caminho 0x47430, depois dos ramos de preparação e de outras verificações/montagem de flags, a chamada **0x47aa8 → 0x54d30** prepara uma solicitação adicional. Um teste anterior de contexto pode saltar para a saída em 0x47a63; portanto, essa chamada não é incondicional.

O wrapper chama 0x7c4e0 em 0x54ea9 para preparar estruturas, instala callback de conclusão 0x56ab0 e grava **requisição interna 9** em 0x54e2b. Em seguida despacha por 0x5a820 em 0x54ec8. O slot da tabela 0x116340 + 9×8, em 0x116388, aponta para **0x7dfe0**. O número 9 é índice de dispatch do host, não opcode USB.

## Construção do buffer

O handler 0x7dfe0 chama o builder 0x7d660 em 0x7e0e2 e 0x7e16f, com alocação entre essas chamadas. O builder recebe estruturas e calcula comprimentos; o formato integral de seus campos ainda precisa ser decodificado.

Em **0x7d84c**, o builder passa valor 2 ao helper 0x83220. Esse helper aloca e zera o buffer e grava o byte baixo do primeiro argumento em seu primeiro byte, em **0x83294**. Assim, há evidência de construção de **opcode 0x02** neste caminho, além da seleção dos blocos opacos de preparação.

Essa conclusão não fornece um frame mínimo válido. Não se deve enviar apenas o byte 0x02 ou inventar o restante: o tamanho, campos variáveis e dependências de contexto ainda não foram completamente reconstruídos.

## Transporte e capacidade de resposta

O handler passa o buffer e comprimento ao transporte comum 0x7b110 em **0x7e32c**. A capacidade inicial de recepção é **0x1002 (4098)** em 0x7e2d2. Um ramo que testa valores internos muda essa capacidade para **2** em 0x7e2ee. Os significados desses testes ainda não foram estabelecidos.

Capacidade não é comprimento real, tamanho de imagem ou formato confirmado do retorno. Transformações do transporte podem se aplicar, como já documentado em etapas anteriores. Nenhum tráfego desse comando foi observado no sensor.

## Processamento posterior no host

Após o wrapper retornar sucesso, 0x47430 chama 0x5e3d0 em 0x47ae1. O callback 0x56ab0 também pode encaminhar um descritor de resposta para esse helper em 0x56bbb. Há, portanto, processamento de conteúdo além de guardar o status de conclusão, diferentemente do callback de init anteriormente analisado.

O helper consulta o contexto interno +0x23c e, no ramo de valor 1, encaminha para 0x91020. Esse parser ainda não foi reconstruído. Não publicar o conteúdo desconhecido como imagem, evento de dedo ou configuração, nem assumir que a resposta seja apenas status.

Há também caminhos de erro com chamadas de limpeza, que precisam ser analisados antes de propor um experimento ativo. Nenhuma delas foi estabelecida como recuperação de alterações persistentes.

## Limites e próxima implementação

Nove destinos de chamadas, o slot de dispatch, o índice e a construção do primeiro byte foram conferidos no binário fixado. Os papéis e ramos são interpretação manual; não há validação de captura em runtime. O significado do campo +4 da operação do host permanece pendente: a investigação não resolveu esse ponto nesta etapa.

O próximo passo é reconstruir a estrutura de argumentos e o parser de resposta por comparação com referências públicas, mantendo separados comando interno, frame e dados retornados. Só depois será possível avaliar um encoder/decoder original offline para esse caminho.

Esta etapa altera somente documentos/evidência e mantém a base de 73 testes aprovados na v0.27, sem nova execução da suíte. Não há novo comando no probe ou teste com dedo.
