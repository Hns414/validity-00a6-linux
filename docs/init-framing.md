# Montagem interna de init_00 e encaminhamento ao transporte

Aplica-se à DLL Dell com SHA-256 6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7. A investigação foi somente estática. O pacote não foi enviado ao sensor e código Windows não foi executado.

## A solicitação interna e seu handler

A rotina em RVA 0x53560 prepara uma solicitação com identificador interno 7. O dispatcher em 0x5a820 lê esse identificador e consulta uma tabela de ponteiros em **RVA 0x116340**. A entrada de índice 7, em **RVA 0x116378**, aponta para o handler **RVA 0x7e540**.

No handler:

| RVA | Comportamento observado na análise manual |
| --- | --- |
| 0x7e580 | Define valor de comando 0x06 |
| 0x7e5a9 | Lê o tamanho dos argumentos da solicitação, no offset +0x24 |
| 0x7e5b5 | Lê o ponteiro dos argumentos, no offset +0x28 |
| 0x7e5c2 | Soma um byte ao tamanho |
| 0x7e5d2 | Chama o alocador/construtor em 0x83220 |
| 0x7e603 | Copia os argumentos para o buffer a partir da posição 1 |
| 0x7e64e | Encaminha buffer e comprimento à rotina 0x7b110 |

O construtor em 0x83220 aloca e zera o buffer e escreve um único byte do comando no início, em 0x83294. Portanto, para os 500 argumentos que coincidem com o registro investigado, o frame interno tem 501 bytes:

```text
posição 0       : opcode 0x06
posições 1–500  : argumentos armazenados na DLL
```

O índice interno 7 seleciona um handler que constrói opcode 0x06. O próprio handler também calcula um valor 34 e o passa ao caminho de transporte; o papel completo desse argumento e da recepção continua em análise.

## Verificação reproduzível em memória

A ferramenta [verify_init_frame.py](../tools/verify_init_frame.py) verifica tamanho/hash da DLL, a entrada de dispatch e o descritor conhecido. Reconstrói o frame em memória, usando opcode 0x06 determinado na análise manual, e compara-o com o init_00 do libfprint fixado.

Resultado: 501 bytes, igualdade integral e SHA-256 **c0ce06740d8c9b836b0d52de2167404ba0b117d0423a278d9fce4b3742e686ee**. O [manifesto](evidence/init-frame-verification.json) não contém bytes do payload. A igualdade confirma a composição do frame com os dados encontrados; não valida os efeitos das instruções do sensor.

```bash
python3 tools/verify_init_frame.py /caminho/libfprint /local/privado/synaWudfBioUsb.dll
```

O script lê dados e tabelas; não executa nem emula as instruções da DLL. A interpretação das instruções nas coordenadas da tabela acima é análise manual, explicitamente separada dos checks automatizados.

## Codificador original, exclusivamente offline

[src/init_frame.c](../src/init_frame.c) implementa a composição de um byte 0x06 e exatamente 500 argumentos. Aceita buffers sobrepostos e recusa ponteiros nulos, comprimento diferente de 500 ou capacidade menor que 501, mantendo a saída intacta na recusa.

Não contém o payload da DLL e não interpreta seu conteúdo. O Makefile do probe não o inclui; o arquivo é compilado apenas no teste offline. Nenhuma opção CLI foi adicionada para emitir init_00. Uma inspeção dos símbolos do executável ativo confirmou ausência de validity_encode_init_frame.

O teste C usa dados inteiramente sintéticos: percorre comprimentos 0–600 e capacidades inferiores a 501, verifica sentinelas de memória, conteúdo, sobreposição, ponteiros nulos e SIZE_MAX. Também passou com ASan/UBSan e detecção de leaks desabilitada pela limitação de ptrace do ambiente. Total atual da suíte: 51 testes aprovados.

## O trecho de transporte ainda não resolvido

A rotina 0x7b110 chama 0x7b260, que inspeciona o comando e encaminha descritores para outras funções. Há caminhos que manipulam buffers e estado antes de chamar indiretamente uma função no offset +0x20 do contexto, em 0x7b213.

Não foi demonstrado qual callback está instalado nesse contexto, quais transformações ocorreriam no caminho escolhido para o participante ou a chegada do frame completo a WinUsb_WritePipe. A DLL resolve esse símbolo dinamicamente em outro objeto: a referência à string aparece em 0xf0297, e o ponteiro resolvido é guardado no offset +0x30 daquele objeto. A ligação entre esses dois objetos ainda precisa ser estabelecida; coincidência de offsets de membros em objetos distintos não prova identidade de callbacks.

Por isso esta etapa comprova a **montagem interna** e o encaminhamento para uma camada de transporte, sem afirmar equivalência dos bytes no barramento em qualquer estado do sensor.

## Próxima investigação

Seguir a instalação do callback do contexto e a transformação dos descritores até o wrapper USB. Em paralelo, determinar a função e os efeitos do conteúdo carregado no sensor. Compor corretamente um frame não torna seguro enviá-lo: as condições de seleção, os efeitos internos e a recuperação continuam pendentes. Nenhum teste adicional é solicitado ao participante nesta etapa.
