# Preparação de Start e máscara 0x400000

Análise estática da DLL Dell fixada pelo hash na [evidência](evidence/start-preparation-analysis.json). Nenhuma execução do driver, extração pública de payload ou transferência USB. RVAs relativos à ImageBase 0x180000000.

## Ramo anterior à espera

O caminho associado a Start contém a chamada 0x1368d → 0x45bd0. Esse helper prepara estruturas e copia 0x1c bytes de parâmetros para contexto. Em 0x45d66 consulta 0x5b840 e, somente quando retorna 1, chama 0x47430 em 0x45d75. O helper de condição obtém um contexto por 0x7ade0 e testa seu DWORD +0x23c contra 1; o significado desse campo ainda não foi identificado. Não supor que o ramo foi percorrido no equipamento do participante.

Dentro de 0x47430 há várias consultas, verificações e saídas por erro antes de 0x476e7 → 0x5e9f0. Esse último helper monta máscara **0x400000** e parâmetro **0x22020** (bits 17, 13 e 5), recupera contexto +0x248 e chama 0x5ed80 em 0x5ea7e.

Esse é o wrapper do seletor/consumidor já estudado na [inicialização](init-selection.md), mas a máscara difere de **0x4000**. Não confundir o número da máscara, o parâmetro do consumidor e um opcode USB. O caminho comum pode selecionar argumentos para o handler de comando 0x06; não foi demonstrado que esse ramo apenas habilite interrupções ou seja suficiente para iniciar captura.

## Descritores candidatos

Uma varredura da tabela fixada de 75 entradas encontrou 11 registros cujo campo +0x2c inclui 0x400000. Isso é filtragem de metadados, **não avaliação completa do seletor**. Entre eles, dois têm major/minor 6.7:

| Índice | RVA | Máscara | Campo build | Argumentos | Campo +0x20 |
| --- | --- | --- | --- | --- | --- |
| 15 | 0x13c810 | 0x400080 | 0xffff | 12100 bytes | 18 |
| 52 | 0x13d3a0 | 0x400080 | 0xffff | 12100 bytes | 18 |

O build 0xffff é curinga no seletor conhecido. As demais condições, incluindo discriminação e contexto, precisam ser avaliadas antes de apontar um registro. Mesmo tamanho não demonstra igualdade dos conteúdos. Os bytes desses blocos não foram publicados e seus efeitos não foram determinados.

A versão 6.7 previamente informada pelo participante torna esses registros relevantes para investigação; não comprova seleção ou execução. Também não autoriza reutilizar o bloco de inicialização de 484 bytes como substituto: ele pertence à máscara 0x4000.

## Limites práticos

Quatro destinos de chamadas foram verificados diretamente no binário fixado; a tabela foi lida usando o mapeamento de seções PE. A interpretação dos ramos permanece manual. Esta etapa altera somente documentação e evidência; mantém a base de 73 testes aprovados na v0.27, sem nova execução da suíte.

O ramo mostra uma preparação dependente de contexto além do registro de eventos no host. Ainda faltam a seleção integral, o papel dos blocos, os demais caminhos de 0x47430 e a ligação com eventos reais. Não há novo comando habilitado nem teste com dedo nesta etapa.
