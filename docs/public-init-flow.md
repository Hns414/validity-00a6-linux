# Posição do bloco de 484 bytes no fluxo público

Inspeção somente do fonte no commit `a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920` do python-validity. Não foram importados módulos, abertos dispositivos ou executadas rotinas do projeto relacionado.

## Sequência observada

Em [usb.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/usb.py), `Usb.send_init()` faz:

1. Consulta 0x01 e valida status.
2. Consulta 0x19 e valida status.
3. Consulta 0x43 0x02 e guarda a resposta, comentada como informação de firmware/partição fwext.
4. Envia `init_hardcoded` e valida status.
5. Examina o status guardado da consulta de partição; se não zero, tenta o bloco `init_hardcoded_clean_slate`.

A decisão do passo 5 usa a resposta anterior da consulta 0x43 0x02, não a resposta do bloco de inicialização. Não transforma qualquer status não zero em prova de ausência de firmware no 00a6; esse é o comportamento do fonte relacionado, com seus limites.

A função não chama 0x1a nessa sequência explícita. Isso difere da preparação condicional Dell já [documentada](pre-init-preparation.md). Não atribuir equivalência entre as duas aberturas apenas porque um payload coincide.

Em [blobs.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/blobs.py), a escolha é por USB ID: 138a:0090 leva a blobs_90, outras entradas a suas famílias. **138a:00a6 não está nesse dispatcher.** Para a família 90, o bloco clean-slate é vazio. `Usb.cmd()` resolve a função fornecida e retorna localmente quando o resultado é vazio; nesse caso não escreve um segundo bloco. O sucesso de um literal igual não estabelece suporte ao novo ID no projeto público.

## Relação com TLS e provisionamento

Em [init.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/init.py), o fluxo `open_common()` chama `init_flash()`, depois `usb.send_init()`, leitura/parsing da área TLS, `tls.open()`, upload de extensão, abertura do sensor e banco de dados.

Logo, a chamada explícita de abertura TLS em `open_common()` vem depois de `send_init()`. Isso não prova ausência de toda sessão anterior: [init_flash.py](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/init_flash.py) possui um ramo de provisionamento próprio que abre TLS, cria partições, apaga/escreve dados e reinicia o dispositivo. Quando já há partições, a função retorna cedo. O ramo depende de estado não medido aqui.

`send_init()` usa diretamente `Usb.cmd()` para o bloco, não o wrapper condicional `Tls.cmd()`. Isso é uma propriedade do código público. Não elimina as transformações condicionais da DLL Dell nem decodifica a estrutura interna do payload.

A abertura completa upstream também chama `set_configuration()` ao abrir e reset ao fechar, além de outras operações. Ela não é equivalente ao probe restrito deste projeto e não foi usada como experimento. A existência de rotinas que alteram flash é motivo concreto para estudar o caminho, não inferência de que o bloco de 484 bytes sozinho execute essas operações.

## Comparação reproduzível dos 484 bytes

A ferramenta original [verify_init_484.py](../tools/verify_init_484.py) reproduz a correspondência já encontrada sem executar driver ou publicar payload:

```sh
python3 tools/verify_init_484.py /path/to/python-validity /path/to/synaWudfBioUsb.dll
```

Ela exige tamanho/hash exatos da DLL, lê o fonte público via `git show` no commit fixado e usa parsing de literal por AST. Confere campos do registro em 0x13d490, vínculo com entrada 55 e handler da requisição 7; mapeia todos os intervalos consultados para as seções PE e para o tamanho real do arquivo. Rejeita referência de tamanho/opcode inesperados, divergência integral, ponteiros não mapeados ou arquivo truncado. A saída é somente JSON de metadados e hashes, sem bytes de payload. A API interna de inspeção é testável com dados sintéticos; a CLI é quem aplica a restrição de hash antes dela.

A execução offline sobre as referências fixadas confirmou frame de 485 bytes e SHA-256 `854b90943a8b865ca237b686112381d15460f715c88147ff6d83d7b8d264b1db`; veja o [resultado reproduzido](evidence/init-484-verification.json). `full_selection_evaluated` e `hardware_execution_enabled` permanecem false. O verificador não executa seletor ou valida automaticamente as instruções de montagem do fornecedor.

Seis testes novos cobrem identidade exata sem exportação, divergência no último byte apesar do prefixo comum, referência inválida, campos alterados, ligações tabela/dispatcher, ponteiro fora da seção e truncamento. `make test` passou com 65 testes sem skips. Nenhuma alteração no probe ativo ou novo teste de hardware.

## Próxima lacuna

A referência pública localiza a etapa de envio e comprova a identidade do bloco, mas seus autores o tratam como literal opaco. Ainda falta decodificar as operações internas e os efeitos do payload no 00a6. A consulta de partição 0x43 0x02 é uma pista para compreender o fluxo; não foi habilitada nem executada aqui. Não há sequência de inicialização validada para uso biométrico.
