# Consumidor criptográfico localizado, alcance pendente

Análise estática manual da DLL fixada. A [evidência](evidence/isolated-block-consumer.json) registra sete chamadas diretas e três chamadas por importação conferidas. Nenhum conteúdo de sensor, chave ou IV foi coletado.

## O que a rotina faz

A função **0x85f60** verifica o DWORD do contexto +0x178 e o comprimento de entrada. Se qualquer um for zero, sai sem processamento. No ramo ativo:

1. Define comprimento de chave 32 quando a classe interna é 1; nas demais classes consulta 0x74d60.
2. Guarda os últimos 16 bytes da entrada em um buffer local, antes da transformação.
3. Chama **0xdae20** em 0x86083 com operação interna 5, campo do contexto +0x17c como material de chave e +0x19c como vetor de inicialização.
4. O dispatcher de operação 5 encaminha para **0xe0ce0** em 0xdaf2a.
5. Essa rotina importa o material por 0xe18f0, configura parâmetros com **CryptSetKeyParam** e, no ramo examinado, chama **CryptDecrypt**, IAT RVA 0x1100c8, em 0xe0fad.
6. Com sucesso, 0x85f60 copia os 16 bytes finais preservados para contexto +0x19c e encaminha o resultado a **0x61ff0**. Com erro da transformação, chama 0x62090 para limpar estado.

A documentação oficial descreve o papel do vetor de inicialização e dos parâmetros de modo em [CryptSetKeyParam](https://learn.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptsetkeyparam), e a operação em [CryptDecrypt](https://learn.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptdecrypt). A relação com os campos gerados na etapa anterior vem do fluxo de argumentos observado no binário, não da documentação da API.

O helper 0x61ff0 usa estado em contexto +0x200 e tem destinos diferentes conforme outro seletor. Sua função final, a verificação de integridade e a relação com entrega de imagem ainda não foram estabelecidas. Não classificar o resultado como imagem válida ou autenticada.

## Limites de tamanho

Antes de ler a cauda em `entrada + comprimento - 16`, a função local verifica apenas comprimento não zero. Ela pode depender de um contrato do chamador. Qualquer implementação original futura precisará validar o limite mínimo antes da leitura e os limites exigidos pelo algoritmo; esta análise não demonstra que uma entrada curta alcance a função no driver Windows.

Também não concluir que toda leitura do sensor usa essa transformação. Os campos aleatórios anteriormente localizados são preparados por outro construtor, mas o caminho completo entre construtor, resposta e este consumidor não foi fechado.

## Alcance ainda não demonstrado

A busca no disassembly não encontrou chamada direta para 0x85f60. Uma varredura adicional dos candidatos de instrução E8 na faixa de texto examinada não encontrou destino correspondente, e a busca pelo endereço absoluto de 64 bits no arquivo não encontrou ocorrências. Essas buscas não excluem referências relativas, chamadas indiretas calculadas, tail calls ou código não utilizado.

Portanto, **esta é uma rotina isolada com comportamento delimitado, não um consumidor comprovadamente ativo na captura do 138a:00a6**. Não habilitar aquisição ou implementar descriptografia do sensor com base nela isoladamente. O próximo passo é investigar referências relativas e outros consumidores do estado +0x178/+0x200, priorizando funções alcançáveis a partir do fluxo de captura já identificado.

## Estado do experimento

A investigação ainda não fecha identificação real do tipo, preparação do transporte e inicialização necessárias para um teste de detecção/captura. Não há novo comando a pedir ao participante nesta etapa. Probe inalterado; sem USB ou teste com dedo. Mudança documental, sem repetição da suíte: base de 103 testes aprovados na v0.47.
