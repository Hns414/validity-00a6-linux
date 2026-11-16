# Investigação técnica

Consulta inicial: 2026-11-16. Os dois documentos entregues pelo usuário foram lidos integralmente como contexto histórico; comandos sugeridos neles não equivalem a resultados executados.

Estado atual: identidade e descritores em M1 confirmados; análise estática do protocolo em M2 disponível em [protocol.md](protocol.md). O [plano do próximo experimento](lab.md) ainda não foi executado. As seções iniciais abaixo preservam o histórico de M0; as atualizações posteriores registram o que foi resolvido.

## Registro de fontes — histórico de M0

| Fonte | Resultado | Limite |
| --- | --- | --- |
| [libfprint: dispositivos](https://fprint.freedesktop.org/supported-devices.html) | Lista de desenvolvimento consultada por busca: 138a:0091 associado a VFS7552; 138a:00a6 não encontrado | Acesso direto sofreu timeout; lista não equivale à versão instalada |
| [libfprint upstream](https://gitlab.freedesktop.org/libfprint/libfprint) | Destino pretendido para integração | Inspeção do código/commit e licença pendentes |
| [MR 626](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/626) | Acesso negado por Anubis | Estado, conteúdo e dispositivos não verificados; não é evidência de suporte |
| [python-validity USB](https://github.com/uunicorn/python-validity/blob/master/validitysensor/usb.py) | Tabela enumera 138a:0090, 138a:0097, 138a:009d e 06cb:009a | Branch mutável; fixar commit na próxima comparação; 00a6 ausente da tabela |
| [python-validity](https://github.com/uunicorn/python-validity) | Projeto usa serviço D-Bus com open-fprintd e sessões TLS; repositório indica licença MIT | Arquitetura de referência; protocolo do 00a6 não demonstrado |
| [Dell NKXR6](https://www.dell.com/support/home/en-us/drivers/driversdetails?driverid=nkxr6) | Latitude 3490 consta entre sistemas compatíveis | INF e vínculo exato ao USB ID ainda pendentes |
| [Catálogo comunitário](https://github.com/jedbillyb/linux-fingerprint-drivers/blob/master/docs/unsupported-devices.md) | Referência do handoff | Não validado nesta etapa; não substitui fonte upstream |

## Pacote Dell candidato

Metadados conferidos na página oficial: versão 5.5.4.1032, A00; data 2018-01-10; Windows 10 64-bit. Esses dados tornam o pacote candidato, mas não identificam o chip. O download por HTTPS retornou HTTP 403; nada foi executado ou extraído.

Próximo procedimento: obter o pacote oficial localmente, registrar hash e termos aplicáveis, extrair sem executar o instalador e localizar no INF `USB\VID_138A&PID_00A6`. Registrar seção, nome comercial e DriverVer com contexto mínimo. Conferir arquitetura e correspondência com a revisão do hardware. Não versionar o pacote, firmware ou binários. Um nome em INF também não prova equivalência de protocolo com 0091.

## Decisão de arquitetura

Preferir avaliar um driver userspace integrado ao libfprint, aproveitando fprintd como serviço de autenticação. Isso é uma direção de pesquisa, não uma implementação aprovada. Comparar tabela de IDs, transporte, inicialização, endpoints, modelo de captura/matching e dependências de firmware antes de escolher um driver base. GNOME/Wayland são camadas posteriores à enumeração e ao suporte do sensor.

Não instalar python-validity nem executar seus exemplos de reset/pareamento nesta etapa. Apenas adicionar 00a6 à tabela de IDs não implementa o protocolo.

## Questões abertas e próximos experimentos

1. Identidade: INF oficial e descritores sanitizados concordam?
2. Upstream: qual commit/versão e licença dos drivers candidatos? Qual estado real da MR 626?
3. Transporte: quais endpoints e mensagens são necessários? Começar por documentação e análise offline; nenhuma transferência vendor-specific foi autorizada pelo plano atual.
4. Segurança: matching ocorre no host ou sensor? Há chaves, templates persistentes ou inicialização que altera flash?
5. Testabilidade: construir fixtures sintéticas de mensagens documentadas antes de testes ativos; não inventar um driver funcional.

## Atualização M1 — evidências verificadas em 2026-11-16

Esta seção substitui as pendências anteriores sobre obtenção do pacote, INF e acesso à MR. Nenhum binário foi executado.

### Identificação Dell

O download oficial funcionou na nova tentativa com User-Agent de navegador. SHA-256 do EXE: `91980fd65adaa40b3f97b82ae547e4e7c9626f3d694bcf9d34083afb2720367d`, igual ao divulgado pela Dell.

Extração somente do INF com bsdtar; caminho interno: `drivers/production/Windows10-x64/synaWudfBioUsbDellProd.inf`. SHA-256 dos bytes originais extraídos: `0abecbe2fe25320e36c81a4eb8c3473b91b7787bf5eaac56e436eee3a4e8d803`.

Metadados factuais mínimos, sem redistribuir o arquivo:

- DriverVer: 09/29/2017,5.5.4.1032 (data do INF, distinta da publicação Dell).
- Seções Synaptics.NTamd64.6.1 e Synaptics.NTamd64.6.2 associam USB\VID_138A&PID_00A6 ao token WBDIUsbDeviceName.
- Nome resolvido: Synaptics VFS7552 Touch Fingerprint Sensor.
- Não há filtro REV nessa associação: ela não demonstra suporte específico à revisão 1.64 nem equivalência com 0091.

Pacote proprietário mantido fora do repositório; inspeção de metadados não concede direitos de redistribuição ou de reutilização de seu código.

### Fontes fixadas e comparação

libfprint: commit `8b6e4e39bee58de2774222e3730269def470b157`, obtido do repositório oficial.

- [Catálogo upstream](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/fprint-list-udev-hwdb.c): 138a:00a6 está na lista de dispositivos conhecidos e não suportados. Sua presença nesse arquivo não é registro de driver.
- [Driver vfs7552.c](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/drivers/vfs7552.c): tabela registra somente 138a:0091. Implementa FpImageDevice; abrir o dispositivo já executa reset USB e inicialização. Não executar apenas para descobrir compatibilidade.
- [Protocolo](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/drivers/vfs7552_proto.h): usa OUT 0x01, IN 0x81 e interrupt 0x83, endereços também presentes no 00a6. Isso é indício de transporte semelhante, não equivalência de mensagens. As sequências incluem grandes blocos de inicialização cuja aplicabilidade ainda exige análise.
- Cabeçalho do driver e meson.build indicam LGPL-2.1-or-later. Adotada a mesma licença para nosso material original; preservação de atribuições continua obrigatória se houver incorporação futura.

python-validity: commit `a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920`, [tabela USB](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/usb.py). Não registra 00a6; continua referência secundária, sem teste neste sensor.

### MR 626

Consultada pela API oficial GitLab: estado opened, merged_at nulo, SHA `5db7da904f74f7fb912d4a18f700a9671d8ab4ac`. Título: validity: 0x969/0xd51 sensor support, robustness and security hardening. Trata de dispositivos VCSFW com TLS e matching no sensor. A descrição e seus IDs relatados não incluem 138a:00a6. As alegações de validação pertencem ao autor da MR e não foram reproduzidas por este projeto. Não confundir o protocolo dela com o de nosso sensor apenas pelo fabricante.

### Próximo marco

Preparar uma matriz de mensagens do VFS7552 upstream (efeito, entradas, respostas, timeout, cancelamento e possível persistência), avaliar os blocos de inicialização e procurar evidências públicas específicas do 00a6. Somente depois definir um experimento ativo mínimo com plano de recuperação. M1 estabelece identidade comercial e descritores; não comprova protocolo nem reconhecimento biométrico.

## Atualização M2 — análise offline em 2026-11-16

Inventário reproduzível implementado: 24 arrays e seis sequências do driver upstream, com tamanhos calculados e hashes. A [matriz do protocolo](protocol.md) separa capacidade de recepção, tamanho de exemplo e validação realmente executada. Foram examinados o executor de transferências, inicialização, captura, parada e cancelamento no commit fixado.

A análise confirma que simplesmente adicionar o ID do 00a6 já acionaria reset e envio de blocos cuja aplicabilidade não conhecemos. O [experimento E1](lab.md) foi especificado como consulta isolada candidata, sem implementação ou execução ativa nesta etapa. O ambiente recuperável e a semântica específica do 00a6 permanecem pendentes; M2 continua parcial.

Validação desta etapa: 14 testes offline aprovados; inventário regenerado a partir dos objetos Git e comparado com o arquivo versionado. Não houve instalação de driver, alteração de PAM, acesso a dados biométricos ou transferências USB.

## Atualização E1 — fonte específica e transporte experimental

Localizado o relato [Validity90 #110](https://github.com/nmikhailov/Validity90/issues/110), aberto em 2023-02-05, com título identificando Latitude 3490 e 138a:00a6. O anexo público foi consultado localmente: 46.038 bytes; SHA-256 `30614818a28e1015f47931cf9e051cabb6e3f7df0d483837168f4c476c198133`. Não foi copiado para este repositório, pois contém respostas brutas que não precisamos redistribuir.

O início do registro mostra envio de 0x01 e resposta de 38 bytes, seguido de divergência do valor esperado pelo protótipo. O resto do registro contém outras divergências; não é validação de captura ou autenticação. A tabela do [prototype/main.c](https://github.com/nmikhailov/Validity90/blob/8b80cfeae15487d5e13ff5ff3ab4f282eac765be/prototype/main.c), no commit inspecionado `8b80cfeae15487d5e13ff5ff3ab4f282eac765be`, não registra 00a6. Não sabemos quais alterações locais o autor do relato utilizou. Além disso, esse caminho de main faz reset e set_configuration antes de init; o relato não comprova a consulta isolada que propomos.

Foi feito apenas inventário local dos imports PE da DLL Dell: isso não identificou o fluxo de consulta nem provou a semântica de 0x01. Nenhum código da DLL foi executado, incorporado ou redistribuído.

Implementado um probe C original com libusb, condicionado à opção explícita --probe-rom-info. O teste real depende do participante e está documentado em [first-hardware-test.md](first-hardware-test.md). As simulações exercitam uma consulta, uma leitura limitada, falhas de pré-condição, permissão, interface ocupada, timeout, cancelamento por sinal, desconexão, erro de event loop, resposta vazia e conclusão tardia. A biblioteca real foi usada para compilar e exibir somente --help; a opção ativa não foi executada nesta sessão.

## Resultado E1 e análise candidata da resposta

O [relato do participante](evidence/e1-participant-report-2026-11-16.json) confirma uma resposta de 38 bytes à consulta isolada, segundo o resultado da ferramenta. Isso acrescenta evidência específica além do relato Validity90, mas sem resposta bruta nem validação semântica. O fluxo implementado não exige reset ou blocos de inicialização.

Próximo passo preparado: --summarize-rom-info, com layout candidato baseado no RomInfo de python-validity, commit a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920. O [mapa de campos](rom-info.md) documenta offsets, little endian, status zero, tamanho exato e exclusões de privacidade. A análise não assume que o layout esteja confirmado para 00a6. Nenhum comando adicional foi implementado ou enviado ao sensor nesta etapa pelo agente.

## Investigação de 0x19 — 2026-11-16

- libfprint fixado: vfs7552_initialization envia 0x19 depois de 0x01 e antes de init_00; capacidade de leitura 128, array de exemplo com 68 bytes. A macro RECV_CHECK_SIZE nesse callback não garante validação de comprimento.
- python-validity fixado: send_init envia 0x19 e verifica status, sem documentar o significado do payload.
- Validity90 fixado: init_sequence_msg2 é 0x19, resposta-modelo tem 68 bytes e campos marcados variáveis. A existência de bytes variáveis motiva não publicar dump ou hash.
- No [relato público #110](https://github.com/nmikhailov/Validity90/issues/110), a primeira resposta registrada após 0x19 tem 68 bytes. O log repete a impressão do mesmo bloco; essa duplicação não é uma segunda leitura USB. O protocolo e as alterações locais do autor não estão integralmente estabelecidos.
- A [MR 626](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/626), no head 5db7da904f74f7fb912d4a18f700a9671d8ab4ac, define VCSFW_CMD_UNKNOWN_INIT como 0x19. Isso reforça a ausência de uma semântica plenamente documentada; não prova equivalência entre suas famílias de sensores.

Decisão: manter nome cmd19, sem chamar o resultado de capacidades, sessão TLS ou identidade. O [experimento E2](cmd19.md) foi implementado como uma emissão isolada, sem reset, 0x01 ou continuação. A emissão pode alterar estado interno; não há garantia formal de ausência de persistência. Seu resultado será apenas contagem e dois indicadores mínimos; nenhum payload é decodificado. Execução no hardware continua pendente e deverá ser explícita pelo participante.

O [resumo E1 do participante](evidence/e1-summary-participant-2026-11-16.json) foi registrado nesta etapa: os campos selecionados coincidem com a referência upstream; o conteúdo integral não foi comparado.

## Resultado E2 e proveniência de init_00

O [resultado do participante](evidence/e2-participant-report-2026-11-16.json) registra 68 bytes, prefixo candidato zero e correspondência do tamanho após 30 testes e compilação em f174d7a. Isso não equivale a comparar o payload integral.

A análise seguinte está em [init-blobs.md](init-blobs.md), acompanhada de [comparação reproduzível](evidence/init-blob-comparison.json). O bloco de 501 bytes é idêntico ao do Validity91 fixado em 75f38a615ef1560829f9cd8aa07459d10f0962ae, onde é declarado opcional mas enviado por padrão. O bloco de 6.677 bytes também coincide integralmente com o dessa origem. Já os blobs init_hardcoded de python-validity têm tamanhos e hashes distintos; compartilham somente os cinco bytes iniciais com init_00, assim como seus reset_blob. Não extrapolar semântica por esse prefixo.

Decisão desta etapa: nenhum executor para init_00/init_04; continuar com análise de formato, operações e persistência, antes de propor envio ao hardware. A ausência de documentação de efeitos é uma lacuna técnica, não prova de que o bloco seja destrutivo. O E2 não precisa ser repetido para esse trabalho offline.

## Investigação do envelope e do produtor de payload

A [análise estática do pacote Dell](dell-static-analysis.md) foi realizada sem executar os binários. Os dois arquivos PE não contêm os blocos upstream ou seu prefixo completo em forma contígua idêntica. Isso não exclui montagem ou transformação em runtime. Foram localizadas três strings de diagnóstico e suas referências em código como pontos candidatos para rastrear a produção dos comandos; não se atribuiu semântica aos métodos apenas pelos nomes.

Uma [avaliação do mantenedor do python-validity](https://github.com/uunicorn/python-validity/issues/3#issuecomment-645873155) descreve os blobs como provável código carregado e executado no dispositivo. É uma pista de pesquisa, não prova específica do 00a6. O sandbox referido nessa conversa foi revisado estaticamente: pode provocar reprovisionamento/recalibração e não foi executado.

O [relatório PE](evidence/dell-static-survey.json) foi produzido por ferramenta somente leitura e reproduzido integralmente. Sete testes adicionais verificam casos PE sintéticos válidos, limites de arquivo, arquitetura, mapeamento de anchors e busca literal. Total: 44 testes aprovados. O envelope e seus efeitos ainda não foram decodificados; o próximo trabalho é rastrear argumentos e chamadas nos pontos candidatos. Não há operação adicional de hardware nesta etapa.

Na busca ampliada da mesma etapa, init_00 sem o opcode inicial 0x06 (500 bytes) foi encontrado integralmente uma vez na DLL principal Dell, em RVA 0x15f550. Seu corpo após o prefixo de cinco bytes (496 bytes) também coincide. O bloco completo de 501 bytes permanece ausente como uma única sequência contígua. Isso sugere armazenamento separado de opcode e argumentos, sem demonstrar ainda a rotina que os reúne. init_04 e seus recortes pesquisados não foram encontrados. O relatório e o teste de busca foram atualizados; total final da etapa: 44 testes.

## Rastreio do consumidor e da seleção

A [análise de init-selection](init-selection.md) encontrou uma tabela de 75 ponteiros em RVA 0x13dad0; a entrada 19 aponta para o registro em RVA 0x13c950. Campos candidatos de versão/build (6, 7, 164) coincidem com E1. O campo +0x2c é 0x4000 e participa de testes de máscara; outro campo exigido e atributos/contexto continuam sem semântica completa.

O caminho de 0x5eac0 solicita 0x4000 por 0x5ed80/0x5ede0. Este último chama o seletor em 0x8fb20, lê tamanho +0x44 e ponteiro +0x48, copia o conteúdo e o passa adiante via 0x62ad0. O caminho 0x53560 usa infraestrutura assíncrona. Ainda falta provar a formação do pacote USB e as operações executadas no sensor. Não se enviou o bloco.

O [extrator de metadados do registro](../tools/locate_init_record.py) é limitado ao hash da DLL inspecionada; o [resultado](evidence/init-descriptor-location.json) indica explicitamente que a seleção não foi avaliada e a execução não foi habilitada. Seis testes adicionais, apenas sintéticos; 50 testes aprovados no total. Nenhum novo dado do participante foi necessário.

## Montagem interna e limite do rastreamento USB

O [rastreio de framing](init-framing.md) confirmou o dispatcher em RVA 0x5a820, tabela 0x116340 e entrada 7 em 0x116378 para o handler 0x7e540. Esse handler usa comando 0x06, soma um byte ao tamanho e copia os argumentos na posição 1. Com os 500 bytes encontrados na DLL, o frame reconstruído coincide integralmente com init_00 upstream; o [manifesto](evidence/init-frame-verification.json) registra comprimento/hash sem reproduzir o payload.

Implementado um codificador C original apenas para uso offline e teste sintético; não está ligado ao probe USB. O teste verifica falhas sem alteração de saída, limites, sentinelas e sobreposição de buffers. A suíte tem 51 testes aprovados; ASan/UBSan do encoder também passou, com detecção de leaks desabilitada pela limitação já registrada.

O caminho de transporte chama rotinas que podem manipular descritores antes de um callback indireto. O vínculo desse callback ao wrapper WinUsb_WritePipe e as transformações relevantes ao contexto do 00a6 não foram comprovados. Não afirmar captura de tráfego nem equivalência final de bytes no barramento. Nenhuma DLL ou nova operação de hardware foi executada nesta etapa.

## Transporte WinUSB e callback de resposta

A [análise estática](transport-and-status.md) localizou a instalação do callback +0x20 em 0x65919, com destino 0x7dd60. Seu papel é tratamento da resposta. O caminho de envio usa a requisição 0x938ae058, o handler 0xee420 e o case 0xee721, chegando a 0xeea70, que encaminha escrita e leitura aos wrappers WinUSB. A resolução dinâmica dos símbolos e as chamadas pelos slots +0x30/+0x28 foram ligadas ao mesmo objeto global.

Essa cadeia é um caminho implementado na DLL, sem trace ou avaliação do contexto real do participante. PipeID é consultado dinamicamente e há transformações condicionais anteriores. O efeito do payload permanece desconhecido. O [registro de análise](evidence/transport-route-analysis.json) é manual e não é validado pela suíte como prova de equivalência de disassembly.

Foi implementado um parser C original de status cleartext, compartilhado por E1/E2, mantendo schemas e comandos anteriores. Respostas curtas são recusadas; status não zero não é confundido com erro de parsing ou sucesso biométrico. O novo teste e ASan/UBSan passaram; 52 testes no total. Nenhuma operação ativa foi adicionada ou executada nesta etapa.

## Condições do contexto de transporte

A [análise dos predicados](transport-context.md) delimita a tentativa de transformação em 0x747e0: contexto auxiliar presente, byte +0x4e8 igual a 7, DWORD +0x100 igual a 0xff e DWORD +0x4e0 zerado, além de ponteiros válidos. O aumento de 69 na capacidade de recepção precede parte desses testes e não prova transformação do envio.

A flag é zerada em 0x754dd no contexto do host e marcada em 0x75891 após a cópia de um buffer interno, antes da chamada de transporte em 0x758c2. Isso não estabelece semântica de sessão ou reset do dispositivo. Os 13 blobs públicos não vazios inventariados têm comprimento menos cinco divisível por 16; o alinhamento não identifica cifra nem efeitos internos.

Etapa somente documental, com evidência estática manual; código e base de 52 testes de v0.11 inalterados, sem nova execução da suíte. Próximo trabalho: chamadores e produção do buffer interno, ainda offline.

## Buffer interno e candidato a alerta TLS

O [rastreio de 0x771e0](alert-records.md) encontrou nível/descrição de dois bytes, tipo 0x15 e cabeçalho 03 03 com comprimento big endian. A comparação com a RFC 5246 sustenta a interpretação de alerta, incluindo close_notify quando o argumento é zero. Os chamadores aparecem em caminhos de liberação/reinicialização do contexto do host. Esta interpretação não decodifica init_00 nem comprova sessão TLS no leitor.

Dentro de 0x773a0, o modo 0xff e o bit 0x02 de +0x128 são requisitos adicionais; os predicados da etapa anterior delimitavam somente a tentativa. O registro de evidência permanece manual. Nenhuma alteração de código, execução adicional da suíte ou operação USB nesta etapa.

## Ordem de abertura e segundo registro candidato

A [ordem parcial](open-order.md) liga chamadas de seleção 0x4000 e 0x1 à coordenação posterior do contexto em uma rotina externa delimitada por `.pdata`. Contexto preexistente e branches impedem concluir que init_00 sempre trafega em claro. A segunda solicitação não foi identificada como init_04.

Uma varredura da tabela revelou duas entradas com 6.7/build 164 e máscara 0x4000: índices 19/55, tamanhos 500/484. Os valores do E1 não selecionam unicamente a primeira. Cinco destinos de chamadas diretas e os campos publicados foram conferidos no binário fixado por hash; a análise de alcance continua manual. Etapa somente documental, sem novos testes ou operações no sensor.

## Discriminante das entradas 19/55

O [novo rastreamento](init-discriminator.md) liga o campo +0x34 ao helper 0x8feb0. Major 6 e bit 0x20 zerado no byte interno +0x17 resultam em 3 (entrada de 500 bytes); bit ativo resulta em 2 (484 bytes). Os registros não passam simultaneamente por esse predicado. +0x20 é carregado pelo consumidor, não é o filtro que distingue o par.

O modelo offline original recebeu cinco testes; make test passou com 57 testes sem skips. Não há mapeamento confirmado do byte interno até o frame USB nem novo campo no probe. Próxima etapa: origem/normalização da estrutura interna; nenhum teste de hardware adicional nesta versão.

## Origem do campo e resumo E1 específico

O [rastreio de normalização](rom-discriminator.md) ligou solicitação interna 1, handler 0x7df10, remoção do status e callback 0x56830 ao buffer armazenado em contexto +0x28. O byte interno +0x17 é preservado a partir do conteúdo da resposta +0x17, correspondente ao offset candidato bruto 0x19.

Preparada opção --summarize-init-discriminator com schema 4 e apenas major/bit/valor derivado. Consultas E1 e schemas anteriores mantidos; nenhuma emissão de init. 59 testes passaram sem skips, build concluído e ASan/UBSan do decoder passou sem detecção de leaks. Próxima evidência necessária: resultado mínimo do participante para esse campo, sem dump.

## Resultado real do discriminante e ramo de 484 bytes

O [relato sanitizado e a comparação](init-484.md) registram o E1 schema 4 do participante em 9d429de: major 6, bit 0x20 ativo, valor derivado 2 e 38 bytes. Isso exclui a entrada 19 pelo filtro +0x34 e admite a 55 por esse filtro, sem concluir seleção global. Os 59 testes passaram no host conforme relato.

Os 484 argumentos da entrada 55 coincidem integralmente com o init_hardcoded público de blobs_90.py sem opcode; acrescentar 0x06 produz o frame público de 485 bytes e mesmo hash. A localização em família 90 não implica compatibilidade do restante do protocolo. Etapa somente documental; próximo trabalho offline nos filtros e consumidor, sem repetir hardware.

## Seleção condicional única e consumidor

A [varredura completa da tabela](init-484-selection.md) deixa somente entrada 55 sob máscara 0x4000, versão 6.7/build 164, argumento zero e discriminante 2. Os outros filtros são wildcards ou exigem byte interno +0x0a igual a 1, valor já exigido pelo gate anterior no mesmo fluxo de abertura. As premissas vêm de relatos separados, sem snapshot atômico; a seleção runtime não foi observada.

O consumidor classifica máscara 0x4000 com retorno 1 e pula consulta/atualização de cache do host. Não foi observada incorporação de +0x20 ao frame nesse caminho. A chamada 0x537b0 antes da requisição 7 permanece por investigar. Encoder offline aceita agora 484/500 argumentos; 59 testes e ASan/UBSan passaram, com detecção de leaks desabilitada. Nenhum novo comando ativo ou teste de hardware.
