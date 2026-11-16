# Ordem parcial da inicialização e ambiguidade de seleção

Análise estática da DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`, sem execução. RVAs relativos à ImageBase 0x180000000. A entrada `.pdata` delimita a rotina externa em [0x64b00, 0x6588c).

## Ordem no caminho examinado

A inspeção de branches e chamadas nesse fluxo encontrou a sequência abaixo. Falhas podem sair antes das etapas seguintes, e algumas chamadas são condicionais.

| Chamada | Destino / papel observado | Condição relevante |
| --- | --- | --- |
| 0x653e0 | 0x633e0 prepara referência armazenada no contexto +0x248 | Falha desvia para saída |
| 0x65411 | 0x5eac0 solicita seleção de máscara 0x4000 | Falha desvia para saída |
| 0x65442 | 0x5eb60 solicita seleção de máscara 0x1 | Só alcançada após retorno zero da anterior; falha desvia para saída |
| 0x65488 | 0x8d810, função ainda sem semântica completa | Chamada quando ponteiro externo +0x228 está ausente |
| 0x65536 | 0x8d290, função ainda sem semântica completa | Dependente dos testes de família e resultado de 0x8d7c0 |
| 0x65579 | 0x746c0, coordenação do contexto auxiliar | Caminho de família 3/5/7/8 e variável local em rsp+0x90 igual a zero |

A rotina 0x5eac0 é a entrada já ligada ao registro de 500 bytes e à montagem do comando 0x06. Em 0x5eb60, a máscara muda para 0x1, mas o fluxo volta ao mesmo wrapper/consumidor de seleção. **Não foi demonstrado que essa segunda solicitação corresponda a init_04**, nem que obrigatoriamente produza um pacote: a seleção completa e os casos sem registro ainda precisam ser avaliados.

A ordem mostra que, neste caminho, a solicitação 0x4000 antecede a chamada posterior de coordenação do contexto. Não prova ausência de contexto no envio: ele pode existir antes da entrada da rotina, ser alterado por chamadas anteriores ou participar de outro fluxo. Também não mede a ordem de transferências reais ou a conclusão de operações assíncronas.

## Criação condicional do contexto

A rotina 0x746c0 consulta 0x74c90 e pode retornar sem chamar a máquina de estados. Quando necessário, chama 0x79500 em 0x74757, repetindo conforme retorno e indicador de conclusão. Não reimplementar esse loop sem compreender limites e cancelamento.

Dentro de 0x79500:

- Obtém o contexto externo e seu lock.
- Testa o ponteiro auxiliar +0x50 em 0x7962f/0x79634.
- Quando ausente, calcula um parâmetro a partir do resultado de 0x63e20 e chama 0x753f0 em 0x7968a com endereço do campo +0x50.
- Após a criação, chama 0x7a7a0 em 0x796c6. Se o contexto já existia, esse bloco de criação é pulado.
- Carrega o estado auxiliar +0x4e8 e usa tabela de dispatch em RVA 0x7a770, com teste de limite 7. Os casos completos ainda não foram decodificados nesta etapa.

Esses pontos ligam a alocação/reinicialização do contexto à infraestrutura que alimenta os predicados do transformador. Não estabelecem sessão autenticada, cifra escolhida ou estado atual do participante.

## Duas entradas compartilham versão e máscara

Uma varredura limitada aos 75 ponteiros da tabela em 0x13dad0 encontrou **duas** entradas com major 6, minor 7, build 164 e máscara 0x4000:

| Índice | Registro RVA | Comprimento de argumentos | Campo ainda não resolvido +0x20 | Campo +0x3c |
| --- | --- | --- | --- | --- |
| 19 | 0x13c950 | 500 | 3 | 1 |
| 55 | 0x13d490 | 484 | 1 | 1 |

A primeira contém os argumentos já comparados integralmente a init_00. A segunda demonstra concretamente que versão/build/máscara não identificam uma única entrada. A tabela acima não lista todos os campos do seletor e não afirma que ambas passem por ele no mesmo contexto. O significado do campo +0x20 não foi atribuído apenas por seus valores. O resultado E1 não permite resolver essa escolha.

Esta descoberta reforça o limite das versões anteriores: a identidade dos 500 bytes com a referência upstream é comprovada, mas a seleção desse registro para o estado real do 00a6 continua pendente. A entrada de 484 bytes não foi exportada, executada ou adicionada ao projeto.

## Verificação e próximos passos

O [registro de evidência](evidence/open-order-analysis.json) contém as duas entradas e cinco ligações de chamadas. Seus destinos foram conferidos independentemente decodificando o deslocamento assinado de instruções CALL rel32 e verificando o hash do arquivo; os campos vieram de intervalos mapeados e limitados às seções PE. Essa conferência valida coordenadas específicas, não toda a interpretação de fluxo, alcance ou equivalência ao driver.

Somente documentação/evidência foi alterada. Código e base de 52 testes de v0.11 permanecem inalterados, sem nova execução da suíte. Não há novo teste de hardware. A próxima prioridade é resolver os demais campos do seletor e a origem de seus valores, antes de escolher qualquer payload; a ordem parcial não autoriza inferir efeitos internos ou recuperação do sensor.
