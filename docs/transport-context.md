# Condições de transformação do transporte

Análise manual e estática da DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`. Todos os endereços abaixo são RVAs, relativos à ImageBase 0x180000000. Nenhuma DLL foi carregada ou executada, e nenhum novo comando foi enviado ao sensor. Esta etapa complementa o [caminho WinUSB](transport-and-status.md).

## Predicados observados

A rotina 0x747e0 recebe descritores que podem ser alterados antes da troca USB. Após validar o contexto externo e obter seu lock, carrega um ponteiro auxiliar do offset +0x50. Para chegar à tentativa de transformação em 0x74962, os testes observados exigem:

| Campo / condição | Instrução de referência | Efeito quando não atendida |
| --- | --- | --- |
| Contexto auxiliar presente | 0x74869 / 0x74878 | Não tenta transformar |
| Byte auxiliar +0x4e8 igual a 7 | 0x748b9 | Não tenta transformar |
| DWORD auxiliar +0x100 igual a 0xff | 0x748dc | Não tenta transformar |
| DWORD auxiliar +0x4e0 igual a zero | 0x74906 | Não tenta transformar |
| Ponteiros de buffer, buffer referenciado e comprimento presentes | 0x74914–0x7492d | Retorna erro neste caminho |

Contexto externo inválido e falha de lock também produzem erro. Já os desvios por estado podem retornar sucesso sem substituir o buffer de envio. Portanto, sucesso da função não significa que a transformação ocorreu. Os nomes semânticos dos campos ainda não foram demonstrados; os números não devem ser tratados como estados públicos de um protocolo.

No caminho de transformação, 0x74962 chama 0x773a0. Esta prepara dados em buffer interno e chama 0x763f0 em 0x774c2, com argumento de tipo 0x17 preparado em 0x774ae. Após sucesso, o chamador libera o buffer anterior e substitui ponteiro/comprimento pelos resultados do contexto auxiliar. Isso delimita uma transformação possível; não demonstra o estado do leitor nem estabelece o algoritmo criptográfico.

## Capacidade de recepção é uma variável distinta

Quando há contexto auxiliar e ponteiro para a capacidade de recepção, a rotina soma 0x45 (69) em 0x748a2. A operação ocorre **antes** dos testes de estado, modo e flag listados acima. Pode haver aumento de capacidade mesmo quando o buffer de envio não é transformado. Esse número não deve ser usado como comprimento obrigatório de resposta, overhead comprovado de todo frame ou evidência isolada de criptografia.

O teste de opcode 0x17 observado anteriormente em 0x7b260 desvia de uma parte do processamento inicial; ele não pula a chamada posterior ao helper 0x747e0. Não foi estabelecida uma regra geral “opcode 0x17 sempre passa inalterado”.

## Escritas na flag e encaminhamento

Dois pontos de escrita direta no campo auxiliar +0x4e0 foram observados nos trechos examinados:

- Em 0x754dd, a rotina 0x753f0 escreve zero ao inicializar/reinicializar campos da estrutura auxiliar do host. Isso não prova reset, limpeza de cadastro ou restauração do dispositivo.
- A rotina 0x75700 testa a flag em 0x75790; no caminho em que está zerada, chama 0x771e0. Depois lê o comprimento em +0x12c, aloca e copia dados de +0x130; após alocação bem-sucedida, escreve 1 na flag em 0x75891 e chama 0x7b110 em 0x758c2. Quando encontra a flag já não zero, o caminho examinado termina com código 0xca.

A segunda sequência liga a flag ao envio de um buffer interno. Como o helper recusa a transformação quando ela é não zero, existe uma relação estática entre essas rotinas. Não foram avaliados todos os chamadores, concorrência, ciclo de vida do contexto ou a seleção desse caminho para init_00. “Flag de segurança”, “sessão autenticada” e “bypass criptográfico disponível” seriam atribuições prematuras.

## Forma dos blobs públicos

Revisando os comprimentos do [comparativo de blobs](evidence/init-blob-comparison.json), os 13 blocos públicos não vazios inventariados têm comprimento menos cinco divisível por 16. Por exemplo, init_00 tem 501 bytes e corpo de 496; init_04 tem 6677 e corpo de 6672. O bloco vazio de clean-slate da família 90 não entra nessa contagem.

A observação é somente aritmética. As entradas vêm de famílias relacionadas, não de 13 amostras independentes do 00a6. Alinhamento de bloco não identifica cifra, assinatura, compressão, arquitetura de CPU, destino de memória ou operações persistentes. O corpo continua opaco.

## Evidência, validação e próximo trabalho

O [registro estruturado](evidence/transport-context-analysis.json) publica coordenadas, condições e comprimentos, sem bytes proprietários ou disassembly integral. As condições foram conferidas manualmente nas instruções; o JSON não é prova automática de equivalência. Esta versão altera apenas documentação e evidência. O código e a suíte permanecem na base de 52 testes validada em v0.11.0-research; não houve nova execução da suíte nesta etapa.

A próxima investigação deve seguir os chamadores das rotinas de contexto e a origem dos dados produzidos por 0x771e0, distinguindo construção no host de operações executadas pelo sensor. Continuam pendentes o contexto efetivamente selecionado para o 00a6, os efeitos internos de init_00 e um procedimento de recuperação validado. Nenhum novo teste de hardware é solicitado; E1/E2 não precisam ser repetidos para esta análise.
