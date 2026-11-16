# init_00: proveniência, comparações e lacunas

Escopo desta etapa: análise offline de fontes públicas. O participante já relatou respostas às consultas 0x01 e 0x19; nenhum bloco de inicialização foi enviado por uma ferramenta deste projeto. Tamanho e status de consultas iniciais não permitem concluir a segurança do passo seguinte.

## Fontes fixadas

| Projeto | Commit | Arquivo relevante |
| --- | --- | --- |
| [libfprint](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/drivers/vfs7552_proto.h) | 8b6e4e39bee58de2774222e3730269def470b157 | vfs7552_proto.h e vfs7552.c |
| [Validity91](https://github.com/hmaarrfk/Validity91/blob/75f38a615ef1560829f9cd8aa07459d10f0962ae/validity91.py) | 75f38a615ef1560829f9cd8aa07459d10f0962ae | validity91.py |
| [python-validity](https://github.com/uunicorn/python-validity/tree/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor) | a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920 | blobs.py, blobs_90/97/9a/9d.py, usb.py |

Esses arquivos descrevem outros USB IDs; não constituem uma especificação validada do 00a6. Nenhum conteúdo da DLL Dell foi incorporado ou executado.

## O que foi confirmado por comparação de bytes

- init_00 tem 501 bytes e SHA-256 c0ce06740d8c9b836b0d52de2167404ba0b117d0423a278d9fce4b3742e686ee. Coincide integralmente com a terceira mensagem de inicialização do Validity91 (índice 2).
- init_04 tem 6.677 bytes e SHA-256 477d0e7dd70db24b71b2902ed56029f296f9dd318ee3e2a03f44416d5d671789. Coincide integralmente com a sétima mensagem daquele arquivo (índice 6).
- No Validity91, a terceira mensagem declara optional=True; a sétima usa o padrão False da dataclass. O construtor do sensor define skip_optional=False; portanto a terceira mensagem é enviada no caminho padrão. Ser opcional naquele protótipo não demonstra que omiti-la ou enviá-la seja válido no 00a6.
- O código libfprint inclui ambos os blocos incondicionalmente na sequência de abertura, após reset USB. Os comentários de origem usam nomes de outras famílias; nomes de variáveis/comentários não identificam sozinhos a função do payload.

## Comparação com python-validity

Valores calculados sem importar o código analisado:

| Família de blob | init_hardcoded | clean_slate | reset_blob | Prefixo comum com init_00 |
| --- | ---: | ---: | ---: | --- |
| 90 | 485 bytes | vazio | 11.493 bytes | 5 bytes em init/reset |
| 97 | 581 bytes | 741 bytes | 12.037 bytes | 5 bytes em cada bloco não vazio |
| 9a | 581 bytes | 741 bytes | 12.037 bytes | 5 bytes em cada bloco não vazio |
| 9d | 581 bytes | 741 bytes | 12.037 bytes | 5 bytes em cada bloco não vazio |

Nenhum desses blocos coincide integralmente com init_00. Os cinco bytes iniciais compartilhados são 06 02 00 00 01, mas os reset_blob também usam esse prefixo. Logo, interpretar apenas o primeiro byte 0x06 ou esse prefixo como uma operação específica é insuficiente. Isso não prova que init_00 faça reset; prova apenas que a comparação de prefixo não resolve sua semântica.

Não há, nesta etapa, evidência suficiente para classificar o restante como código executável, firmware persistente, mensagem cifrada ou configuração temporária. Aparência e distribuição de bytes não bastam para essas conclusões. Uma resposta de sucesso de dois bytes também não demonstra ausência de alteração de estado.

## Reproduzir a comparação

Com clones locais contendo os commits fixados:

```bash
python3 tools/compare_init_blobs.py /caminho/libfprint /caminho/Validity91 /caminho/python-validity
python3 -m unittest discover -s tests -v
```

O script lê objetos Git, extrai somente literais e flags declaradas com ast, calcula comprimentos/hashes e compara bytes em memória. Não importa/roda módulos upstream, não abre USB, não executa DLLs e não publica o payload. Falha em sintaxe de blob/query que não compreende. O [manifesto resultante](evidence/init-blob-comparison.json) não atribui semântica aos comandos.

## Decisão e próximo trabalho

Não implementar execução de init_00/init_04 nesta etapa. Para avançar, ainda precisamos determinar:

1. Estrutura do envelope e dos dados internos, a partir de documentação ou análise estática rastreável.
2. Operações efetivas: registradores, memória volátil, flash, chaves ou outro estado; quais delas dependem de hardware/revisão.
3. Pré-condições que diferenciam 0091 de 00a6 e comportamento caso o bloco seja rejeitado ou interrompido.
4. Evidência de recuperação aplicável às operações identificadas.

O trabalho pode continuar offline nas fontes do driver e na documentação do protocolo. Não é necessário repetir E1/E2, instalar Windows ou coletar impressões digitais para concluir essa análise. Um trace compatível só será considerado se houver procedimento específico que evite captura biométrica e mantenha dados brutos privados; não é uma solicitação para capturar tráfego agora.

## Continuação: envelope e driver Dell

A [análise estática Dell](dell-static-analysis.md) acrescenta uma declaração do mantenedor sobre provável código executado no sensor, busca de correspondência literal nos arquivos do pacote e pontos candidatos para seguir o fluxo de dados da DLL. A hipótese de código não é uma especificação confirmada do envelope. Nenhum bloco foi executado e o formato interno permanece em aberto.

A investigação ampliada encontrou também os 500 bytes de init_00 sem opcode no driver Dell do 00a6, integralmente. Isso avança a proveniência além da comparação entre projetos, mas não resolve a semântica do envelope nem permite supor que o bloco seja seguro para qualquer estado do sensor. As coordenadas e os limites estão em dell-static-analysis.md.
