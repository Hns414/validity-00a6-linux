# Referência pública de cleanup e tradução de status

Esta etapa compara o fonte público fixado do python-validity com análise estática da DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`. Não executa esses projetos ou novos comandos USB. Endereços são RVAs relativos à ImageBase 0x180000000.

## O que a referência pública mostra

Em [flash.py, commit a6bbc21](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/flash.py), `call_cleanups()` envia 0x1a por `tls.cmd`, lê o status little endian e aceita 0x0491 com o comentário “Nothing to commit”. Outros status seguem para a validação comum. O fonte usa essa função no bloco `finally` de operações de apagar/escrever flash, depois da etapa de habilitação de escrita.

Isso fornece uma pista concreta de finalidade no projeto relacionado. Não demonstra quais operações o comando executa no 00a6, se mudanças são persistentes, se a operação é reversível ou se o caminho Dell usa o mesmo estado de sessão. O nome cleanup e o comentário não autorizam chamar o comando de leitura, reset ou recuperação segura. Nenhuma operação de flash da referência foi executada.

## Tradução na DLL Dell

A rotina 0x7da00 traduz status do dispositivo para retornos internos usados pelos wrappers. Foram conferidos dois casos pertinentes:

| Status do dispositivo | Caminho estático | Retorno interno |
| --- | --- | --- |
| 0x0491 | Subtrai 0x0402, índice 143 na tabela byte em 0x7dca4; índice de case 8; tabela DWORD em 0x7dc68 aponta para 0x7db54 | 0 |
| 0x0401 | Comparações em 0x7da18/0x7da22 e branch para 0x7db47 | 0xd1 |

Os bytes das duas tabelas e os imediatos dos destinos foram lidos diretamente do arquivo fixado por hash. A análise dos branches foi manual. Não se executou o tradutor proprietário.

Portanto, **0xd1 não deve ser confundido com 0x0491**: são espaços de códigos distintos. No fluxo examinado, 0x0491 se traduz em zero e 0x0401 se traduz em 0xd1. O consumidor aceitar zero/0xd1 após a preparação não significa que o sensor sempre retornou zero.

Além disso, como visto na [preparação condicional](pre-init-preparation.md), há conclusão local de sucesso sem transporte. Um futuro port deve preservar a distinção entre erro de transporte, status bruto, status traduzido e conclusão local. O probe atual conserva status como candidato, sem incorporar essa tabela ou converter 0x0491 em sucesso de hardware.

## Origem dos campos que disparam cleanup

Foram ligados ao mesmo contexto os seguintes pontos, sem pretender análise exaustiva de aliases:

- O callback de versão 0x56830 copia conteúdo +0x0f para estrutura interna +0x0f em 0x569d8. Portanto, o campo pode vir de uma resposta, além de ser alterado no host.
- O consumidor 0x62ad0, no caminho gerenciado por cache (classificador zero), armazena máscara em cache DWORD +0, parâmetro do registro em byte +8 e esse parâmetro na estrutura de versão +0x0f, em 0x62de2/0x62e0b/0x62e2b. Para máscara 0x4000 esse caminho é pulado, conforme etapa anterior.
- A rotina local 0x5c480 zera esses campos; o campo de versão é zerado em 0x5c4cb.

A origem mista impede tratar o byte +0x0f como medição atual e exclusiva de estado do sensor. Uma flag local pode persistir até a limpeza sem nova consulta. Não confundir escritas em +0x0f de estruturas de outros offsets/objetos com este contexto apenas porque o deslocamento coincide.

## Consequência e validação

O [registro estruturado](evidence/cleanup-status-analysis.json) guarda referências, tabela de tradução e pontos observados de escrita, sem payload ou disassembly integral. A relação entre 0x1a e cleanup tem suporte no código público; o efeito específico no 00a6 continua hipótese de pesquisa.

Esta etapa altera somente documentos/evidência. A base de 59 testes validada em v0.18 permanece sem nova execução. Nenhum comando adicional foi habilitado ou solicitado ao participante. Próximo trabalho: relacionar o payload de 484 bytes e os estados posteriores do consumidor a funções públicas documentadas, antes de avaliar uma sequência de inicialização executável.
