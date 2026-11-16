# Comparação pública e alternativas da preparação

Análise offline da DLL Dell fixada, sem execução ou operação USB. A [evidência](evidence/start-public-comparison.json) registra commits, nomes e comprimentos dos literais e resultados da comparação; não contém payloads.

## Comparação delimitada a referências conhecidas

Os argumentos das entradas 15 e 52 têm 12100 bytes cada. Para comparação, foi construído em memória o frame candidato com opcode 0x06, totalizando 12101 bytes, conforme o handler comum já estudado. Isso não demonstra o tráfego final: preparação prévia, cache e transformações continuam aplicáveis.

Foram comparados 47 literais extraídos dos objetos Git locais nos commits fixados:

- Arrays do header `libfprint/drivers/vfs7552_proto.h` do libfprint 8b6e4e39bee58de2774222e3730269def470b157.
- Mensagens do arquivo `validity91.py` do Validity91 75f38a615ef1560829f9cd8aa07459d10f0962ae.
- Literais init/clean_slate/reset/db_write_enable das famílias 90, 97, 9a e 9d do python-validity a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920.

Os parsers originais do projeto extraíram dados literais, sem importar ou executar os módulos analisados. Para ambas as entradas, **nenhum literal coincide integralmente com os argumentos ou com o frame candidato**. Também não há literal de comprimento 12101 nesse inventário.

Essa é uma conclusão sobre esse conjunto de referências, não uma busca exaustiva em projetos públicos. Não foram comparadas todas as possíveis sub-regiões, descompressões, decifrações ou versões históricas. A ausência de igualdade não identifica um novo formato nem estabelece incompatibilidade operacional. Não chamar o bloco de firmware, captura ou reset com base nesse resultado.

## Dois ramos alternativos

Em 0x47430, após as verificações anteriores:

1. Se existe o ponteiro de contexto +0x20 e seu DWORD +4 vale 5, o desvio 0x476cc pula ambos os helpers e segue para 0x47746.
2. Caso contrário, o WORD +0x0c da estrutura local referida por `[rsp+0x48]` é comparado com 2 em 0x476d7.
3. Se igual, chama 0x5e9f0 em 0x476e7, usando máscara requerida 0x400000. Após sucesso, o salto 0x47710 vai a 0x47746.
4. Se diferente, chama 0x5e7b0 em 0x4771d. Esse helper usa máscara requerida **0x80**, máscara excluída 0x22020 e o mesmo wrapper 0x5ed80 em 0x5e83e.

Portanto, **0x400000 e 0x80 são alternativas**, não uma sequência de dois comandos. Os nomes semânticos dos campos de contexto ainda não foram determinados. Não afirmar que o participante segue o ramo 0x400000 apenas por sua versão 6.7 ou discriminante 2. A [seleção da entrada 52](start-selection.md) continua uma implicação condicionada a alcançar aquele ramo e satisfazer o gate.

A entrada 52 tem máscara 0x400080, que inclui ambos os bits. Isso, sozinho, não basta para provar que o ramo 0x80 seleciona a mesma entrada: sua seleção completa ainda não foi avaliada nesta etapa.

## Validação e próximo passo

As comparações foram feitas byte a byte em memória; dois destinos adicionais de chamadas foram conferidos no binário fixado. A análise de branches é manual. Não foi incorporado conteúdo proprietário ao código público.

A etapa altera somente documentos/evidência. Continua a base de 73 testes aprovados na v0.27, sem nova execução da suíte. O probe ativo não recebeu opções novas e o encoder offline continua restrito aos comprimentos anteriormente estudados.

O próximo trabalho é rastrear a origem do WORD +0x0c e do estado que permite pular a preparação, além de investigar os ramos posteriores até o início efetivo de aquisição. Nenhum teste com dedo está disponível ainda.
