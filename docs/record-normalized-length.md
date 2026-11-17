# Comprimento normalizado de um registro de aplicação

Continuação dos [limites do transporte](response-transport-bounds.md). Análise estática manual da DLL fixada. A [evidência](evidence/record-normalized-length.json) registra cinco chamadas e seis âncoras de comprimento/offset conferidas. Nenhum registro do sensor foi coletado ou processado.

## Cabeçalho e disponibilidade

O parser 0x774e0 percorre registros com cabeçalho de **cinco bytes**. Confere os bytes de versão +1/+2 contra 3/3. O comprimento L é lido nos bytes +3/+4 como inteiro big-endian por **0x77656 → 0x79430**. Há teste de cabeçalho disponível e comparação entre L e os bytes restantes após o cabeçalho.

O código também compara a variável de comprimento, carregada como WORD sem sinal, com 0x10060. Esse valor é maior que o máximo de uint16, portanto esse teste superior não deve ser citado como limite efetivo para L; o teste separado de zero e a disponibilidade do buffer são condições distintas.

## Ramo protegido e comprimento final

O bit 0 do campo auxiliar +0x128 seleciona um ramo de transformação para os registros pertinentes. Nesse ramo, o código passa uma região que começa 16 bytes depois do início do conteúdo ao helper **0x78b50 em 0x777b1**. A semântica e todos os limites desse helper ainda não foram auditados nesta etapa.

Depois da chamada e de outros passos, há verificações de comprimento e leitura do último byte p:

- p deve ser menor que 16.
- O teste posterior exige `L >= p + 33`.
- Um ponteiro final é calculado em `início do conteúdo + L - 32 - p - 1`.
- O início útil avança 16 bytes.
- Uma região de 32 bytes é comparada com um resultado calculado por outro helper; com sucesso, essa região é zerada.

Para o registro de aplicação **tipo 0x17**, aceito sob modo auxiliar 0xff e bit 0 ativo, o comprimento guardado em **auxiliar +0x12c**, em 0x77cfb, é a diferença desses ponteiros:

`comprimento normalizado = L - 49 - p`

Essa fórmula descreve o caminho após seus passos bem-sucedidos. Não é autorização para implementar criptografia ou assumir que os campos sejam um IV/MAC sem acompanhar os helpers. Algumas verificações de tamanho aparecem depois da transformação; a segurança de chamadas com comprimentos pequenos ainda depende da auditoria desses helpers e de contratos anteriores.

## O que a fórmula permite concluir

Para um único registro, ela explica a remoção de regiões do conteúdo e relaciona o comprimento normalizado com L. Com o cabeçalho de cinco bytes, o total recebido desse registro é `5 + L`.

Isso ainda não demonstra que a saída caiba na capacidade original N da leitura 0x78. Se usarmos somente o teto ampliado `N + 75` localizado anteriormente, a desigualdade fornece no máximo `normalizado <= N + 21 - p`. Esse limite isolado não basta para provar `normalizado <= N + 6`, necessário à conta que desconta status e prefixo de comprimento antes da cópia de dados. Outras invariantes podem impor um limite menor; não foram demonstradas ainda.

Essa é uma limitação da prova atual, não demonstração de resposta excedente real, falha explorável ou comportamento do participante.

## Múltiplos registros

O loop avança para `início do registro + 5 + L` e pode continuar enquanto houver entrada. O normalizador superior 0x749e0 usa um offset fixo de 21 bytes ao copiar o conteúdo e o campo auxiliar +0x12c como comprimento. Ainda falta verificar o contrato entre esse offset, registros anteriores, múltiplos registros de aplicação e eventuais sentinelas de encerramento. A fórmula de um registro não deve ser aplicada automaticamente à transcrição inteira.

## Resultado e próximo passo

O cálculo do comprimento final deixou de ser opaco, mas a prova de capacidade permanece aberta. Próximos pontos: contratos de 0x78b50 e 0x75a90, mínimo validado antes da transformação e relação entre saída normalizada e limite solicitado ao dispositivo.

Mudança documental: cinco chamadas e seis âncoras conferidas. Base atual de **112 testes aprovados na v0.62**, sem repetir a suíte nesta etapa. Probe inalterado; sem USB, captura ou teste com dedo.
