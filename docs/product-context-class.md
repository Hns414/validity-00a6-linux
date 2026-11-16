# Produto da ROM e classe do contexto

Análise manual da DLL Dell fixada, com [leitura limitada da tabela e evidência](evidence/product-context-class.json). Nenhuma execução ou transferência USB.

## Origem do campo +0x23c

No caminho de abertura 0x64b00, a DLL lê o byte **+0x0b da estrutura interna de versão** em 0x64da9, chama **0x5bab0 em 0x64dad** e guarda seu retorno em **contexto +0x23c em 0x64dbd**.

O helper percorre registros de oito bytes a partir de **RVA 0x119188**, comparando um byte de produto e retornando um DWORD associado. O percurso termina com chave ou valor zero. A leitura local da tabela fixada encontrou:

| Produto | Classe retornada |
| --- | --- |
| 0x2b | 1 |
| 0x2d | 1 |
| 0x30 | 1 |
| 0x32 | 1 |
| 0x33 | 1 |

O registro terminador zero foi conferido. No trecho, produtos sem correspondência mantêm resultado inicial zero. Não interpretar esses números como classes padronizadas USB, níveis de segurança ou tipos internos de sensor.

## Consequência condicional para o participante

A interpretação candidata de E1 já relatada pelo participante contém produto **0x30**. Pela cadeia de resposta/estrutura de versão estudada anteriormente, ele corresponde ao byte interno +0x0b usado por esse helper. **Se essa interpretação e o estado persistem**, o caminho examinado grava classe **1** em +0x23c.

Essa classe é exigida pelo [wrapper do seletor de programas](program-descriptor-selection.md). Assim, há uma justificativa condicional para essa pré-condição a partir do relato existente; não é necessário repetir E1 para descobrir a tabela estática.

Isso não demonstra execução completa da abertura, presença da tabela de programas, sucesso dos passos intermediários ou seleção de uma entrada concreta. A classificação não foi observada em runtime Windows.

## Identificadores que continuam distintos

- **138a:00a6:** VID/PID USB do equipamento.
- **Produto candidato 0x30:** campo da estrutura de versão/ROM.
- **Classe de contexto 1:** resultado desta tabela de mapeamento.
- **Campo +0x128:** identificador usado na seleção de programas, ainda sem valor identificado para o participante.

O mapeamento 0x30 → 1 não fornece +0x128. Nos trechos examinados, esse último recebe um valor armazenado por outra operação em 0x63319. A origem completa dessa operação, suas alternativas e o valor final continuam pendentes. Também não foi resolvido quem registra a tabela recuperada por categoria 2 nas listas do host.

## Validação e próximo passo

A chamada ao helper e a instrução de armazenamento foram verificadas no binário fixado; a tabela foi lida usando o mapeamento de seções PE, com limite de 32 registros e terminador encontrado após cinco entradas. A interpretação dos papéis é manual, sem executar o driver.

Somente documentação/evidência: mantém a base de **91 testes aprovados na v0.37**, sem nova execução da suíte. O próximo passo continua sendo identificar o produtor/registro da tabela e o valor de +0x128 antes de escolher o programa final. Nenhum novo comando USB ou teste com dedo foi realizado.
