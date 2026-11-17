# Método posterior da interface e reordenação de bytes

Continuação do [descritor preparado](word-descriptor-builder.md). Análise estática manual da DLL fixada; a [evidência](evidence/processing-method18.json) registra três chamadas diretas, a associação do método e um slot indireto conferidos. Sem execução do driver ou USB.

## Slot +0x18 alcançável

O inicializador 0xa35d0 associa **0xa47c0** ao slot **+0x18** da interface, por endereço calculado em 0xa3663. A chamada indireta em **0x48379** usa esse slot, buscando a interface no campo +0x58 e passando o estado do campo +0x50 — os mesmos campos preenchidos após a criação da interface já documentada.

Isso demonstra outro método usado pelo fluxo do host. A origem integral do descritor de entrada preparado nesse chamador ainda não foi rastreada até uma leitura USB; não confundir o bloco de entrada com a resposta de configuração 0x30000288 apenas porque ambos passam pela mesma interface.

## Dois ramos no método

A função 0xa47c0 testa o bit 0 do byte de estado +0x6b8:

- Com bit ativo, exige pelo menos 12 bytes de entrada, copia a região depois desse prefixo para um buffer do host e chama **0xa8960**.
- Com bit desativado, encaminha o descritor para **0xaa660 em 0xa49a9**, junto de campos de saída e um argumento opcional preparado a partir do estado.

O teste de 12 bytes delimita o prefixo desse ramo, mas não constitui auditoria completa da capacidade de destino ou das demais leituras do método.

## A rotina vizinha agora tem chamada demonstrada

Dentro de 0xaa660 há uma bifurcação posterior:

| Condição | Operação observada |
| --- | --- |
| DWORD de metadados +0x28 igual a 3 e DWORD inicial do descritor preparado igual a 8 | Cópia direta de um trecho limitado por valores locais |
| Caso contrário | Chamada **0xaab18 → 0xa2510** |

Essa chamada passa o buffer de entrada local, seu comprimento, um destino do host e o descritor preparado em estado +0x168. Portanto, a função 0xa2510 deixou de ser apenas uma rotina próxima no arquivo: existe ligação por chamadas a um método identificado da interface. Isso ainda não prova a execução desse ramo no participante.

## Operações delimitadas em 0xa2510

No ramo que supera suas verificações iniciais, a rotina copia os primeiros **oito bytes** para a saída. Em seguida usa uma tabela de índices WORD em **descritor +0x1ac**, com extensão signed de 16 bits, para posicionar bytes no destino.

Ela contém ramos especializados para valores internos 8 e 4. No ramo de valor 8, lê bytes e os escreve nos offsets da tabela. No de valor 4, separa os dois nibbles de cada byte e os desloca para a parte alta dos bytes de saída; um argumento adicional pode alterar os valores por deslocamento e soma. Outro ramo extrai grupos de bits conforme campos do descritor. O comprimento retornado inclui o prefixo de oito bytes e é arredondado para múltiplo de 16.

Essas operações são compatíveis com reorganização de amostras compactadas, mas **isso é uma hipótese funcional**, não confirmação de pixels, resolução ou formato biométrico do 00a6. Os valores 4/8 não foram tratados como especificação de profundidade do sensor. A origem da tabela e os limites de acesso precisam ser auditados antes de criar um decoder.

## Próximas lacunas

Rastrear a origem do descritor recebido pelo método +0x18 até a entrada real, delimitar a construção da tabela de índices e auditar capacidades e comprimentos. A relação com o consumidor criptográfico isolado continua não demonstrada.

Somente documentação/evidência: três chamadas diretas e a associação do método conferidas. Base de 103 testes aprovados na v0.47; suíte não repetida. Probe inalterado, sem USB ou teste com dedo nesta etapa.
