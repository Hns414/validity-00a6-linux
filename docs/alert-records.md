# Buffer interno: candidato a alerta TLS

A investigação segue o buffer enviado pela rotina 0x75700, separado do payload opaco de init_00. Foi inspecionada somente a DLL Dell com SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`. Endereços são RVAs relativos à ImageBase 0x180000000. Não houve execução da DLL ou acesso ao sensor.

## Produção dos dados

Em 0x757af, o chamador passa o contexto auxiliar, seu buffer +0x130 e argumento de um byte igual a zero para 0x771e0. Essa rotina:

1. Zera a contagem auxiliar +0x12c em 0x77205.
2. Escolhe nível 1 por padrão e 2 para argumentos 10, 20, 40 ou 47.
3. Escreve nível e argumento nos offsets +0x15 e +0x16 do buffer, em 0x77245/0x77252; também os guarda nos campos auxiliares +0x4e6/+0x4e7.
4. Chama 0x763f0 em 0x7728b, com tipo 0x15 e comprimento 7. A rotina de registro desconta cinco do comprimento para tipos diferentes de 0x16: neste caso, sobram dois bytes de conteúdo antes de eventual proteção.
5. Quando o bit 0x02 de +0x128 está zerado, há um caminho que copia o conteúdo de +0x15 para +5 após a construção do cabeçalho. O helper de cópia não foi auditado integralmente nesta etapa.

A rotina 0x763f0 escreve tipo no offset 0, versão 03 03 nos offsets 1/2 e comprimento de dois bytes em +3. A chamada 0x76739 usa 0x794a0, cuja sequência de shifts escreve primeiro o byte mais significativo. A contagem +0x12c é incrementada pelo comprimento final mais cinco.

## Comparação com o padrão

Na [RFC 5246, seção 6.2.1](https://www.rfc-editor.org/rfc/rfc5246.html#section-6.2.1), os tipos 21/22/23 correspondem a alert/handshake/application_data; a versão 3,3 identifica TLS 1.2 e o cabeçalho contém comprimento de dois bytes. A [seção 7.2](https://www.rfc-editor.org/rfc/rfc5246.html#section-7.2) define nível 1 como warning, 2 como fatal e descrição zero como close_notify. As descrições 10/20/40/47 também existem nessa enumeração.

**Inferência:** o conjunto de campos, constantes e encaminhamento é consistente com construção de alertas TLS, incluindo warning/close_notify no caminho com argumento zero. Esta é uma interpretação estática sustentada por vários campos; não uma observação de negociação TLS bem-sucedida no 00a6 ou demonstração de conformidade completa com a RFC. O formato do cabeçalho também coincide com o construtor de registros no [python-validity fixado](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/tls.py), sem executar esse projeto ou transferir sua compatibilidade para o 00a6.

O registro final pode ter conteúdo protegido conforme estado: os dois bytes não são necessariamente transmitidos em claro. A flag +0x4e0 marcada antes do transporte evita aplicar novamente o transformador analisado, mas ainda não é uma interface pública de controle de sessão.

## Chamadores e ciclo de vida

Foram observados dois chamadores diretos de 0x75700 nos trechos pesquisados:

| Chamador | Condições observadas | Operação posterior |
| --- | --- | --- |
| 0x74bb0, chamada em 0x74c56 | Contexto auxiliar presente, flag +0x4e0 zerada e segundo argumento igual a 1 | Chama 0x758e0 com endereço do ponteiro auxiliar em 0x74c6b |
| 0x74e90, chamada em 0x74ec7 | Helper 0x74c90 indica campo +0x100 igual a 0xff; segundo argumento não zero | No caminho de lock bem-sucedido, chama reinicialização do contexto em 0x74f17 |

Há chamadas a 0x74bb0 em caminhos que também liberam recursos do contexto externo, por exemplo após 0x5ab10. Isso reforça a hipótese de encerramento, sem provar todos os efeitos dos chamadores ou da limpeza. As rotinas podem preservar códigos de erro de formas diferentes; não foram reimplementadas.

## Condição adicional para dados de aplicação

Os predicados publicados em [transport-context](transport-context.md) delimitam a chegada à chamada de 0x773a0; eles não bastam para garantir seu sucesso. Dentro dessa rotina, o modo +0x100 deve continuar igual a 0xff e o bit 0x02 do campo +0x128 deve estar ativo, ou o caminho retorna 0xcc. Há também limite de entrada de 0x10000 bytes. O construtor recebe tipo 0x17, compatível com application_data na RFC. Isso explica uma recusa adicional, sem estabelecer cifra, chaves ou estado atual do dispositivo.

## Consequência para init_00

O buffer seguido nesta etapa pertence ao caminho candidato de alertas; não é a origem dos 500 bytes do registro de inicialização. Identificar um cabeçalho TLS de cinco bytes não decodifica o prefixo ou corpo de init_00. A coincidência de tamanho de prefixo e o alinhamento por 16 continuam insuficientes para igualar esses formatos.

O [registro estruturado](evidence/alert-record-analysis.json) contém somente coordenadas, constantes e conclusões selecionadas. Esta etapa altera documentação/evidência; o código e a base de 52 testes validada em v0.11 permanecem iguais, sem nova execução da suíte. Nenhum teste adicional de hardware é necessário. A próxima análise deve voltar ao produtor/consumidor da inicialização e localizar sua posição em relação ao estabelecimento do contexto, evitando confundir alerta, registro externo e payload interno.
