# Entrega da resposta ao processamento do host

Análise estática manual da DLL fixada. A [evidência](evidence/host-processing-handoff.json) registra seis chamadas diretas, uma associação de método e seu slot indireto conferidos. Não contém programas, respostas, imagens ou material criptográfico de execução.

## Consumidor alcançável após a resposta

Depois do sucesso de 0x54d30, a função 0x47430 volta a processar o descritor local de resposta por **0x47ae1 → 0x5e3d0**. Esse processamento é adicional ao callback examinado na etapa anterior. Com sucesso, verifica o WORD de modo +0x0c:

- Modos 1 ou 3 chegam à chamada **0x47b68 → 0x46fd0**.
- Nos demais modos, essa chamada depende de 0x5f720 retornar 1.

O buffer local opcional devolvido pela requisição é liberado na saída por **0x47bbf → 0xd5410**. A cópia mantida pelo parser no contexto é distinta desse buffer local. Essa separação importa para não usar um ponteiro já liberado em uma futura implementação.

## Estrutura entregue à interface

A função 0x46fd0 prepara estado dentro do segundo argumento +0x78 e reúne campos do contexto interno. Entre eles:

| Origem no contexto interno | Destino relativo ao estado preparado | Tratamento |
| --- | --- | --- |
| +0x88 | +0x20 | DWORD da referência às palavras |
| +0x90 | +0x28 | Ponteiro da referência às palavras |
| +0x78 | +0x30 | DWORD do corpo armazenado |
| +0x80 | +0x38 | Ponteiro do corpo armazenado |

As atribuições de ponteiros nesses quatro campos não fazem cópia profunda. O estado também recebe metadados e outros ponteiros do contexto, além de cópias de regiões fixas. O contrato completo de propriedade e duração desses dados ainda precisa ser auditado.

## Destino da chamada indireta resolvido

A função aloca uma interface de **0x60 bytes** e a inicializa por **0x47087 → 0xa35d0**. Nesse inicializador, a instrução em **0xa3643** obtém o endereço de **0xa3780**, armazenado no slot +0x10.

Em **0x47383**, a chamada indireta usa exatamente esse slot +0x10, recebendo uma saída local e o descritor preparado. Assim, o destino estático dessa chamada fica resolvido, sem depender de adivinhar a função pela proximidade no binário.

Com sucesso, o objeto de interface e a saída obtida são armazenados nos campos +0x58 e +0x50 do argumento superior. No caminho de erro, quando há saída, usa-se o slot +0x20, associado pelo mesmo inicializador a outra função. Esses campos não foram classificados como imagem pronta ou resultado biométrico.

## Limite e próximo passo

A função 0xa3780 começa validando argumentos e alocando seu próprio estado, mas a transformação completa ainda não foi reconstruída. O avanço desta etapa é fechar a ligação alcançável da resposta até esse método. Ainda não há ligação demonstrada com o consumidor criptográfico isolado 0x85f60.

Próximo passo: seguir o uso dos descritores dentro de 0xa3780 e as saídas da interface, incluindo duração dos ponteiros. Isso deve distinguir configuração recebida, dados de aquisição e processamento posterior sem atribuir semântica de pixels antes de haver evidência.

Mudança documental: seis chamadas diretas e a associação do método conferidas, sem USB ou teste com dedo. Base de 103 testes aprovados na v0.47; suíte não repetida nesta etapa. Nenhum novo comando no probe.
