# Changelog

## 0.21.0-research — 2026-11-16

- Fluxo público do bloco de 484 argumentos documentado: consultas, seleção por ID e caminho clean-slate vazio da família 90.
- Ordem nominal de TLS separada do ramo prévio de provisionamento; diferenças com preparação Dell explícitas.
- Verificador offline restrito ao hash da DLL reproduz comparação integral sem exportar payload.
- Seis testes novos; 65 aprovados. Probe ativo inalterado, sem nova operação de hardware.

## 0.20.0-research — 2026-11-16

- Referência pública associa 0x1a a call_cleanups após operações de flash; efeitos no 00a6 não demonstrados.
- Tradução Dell conferida: status 0x0491 para retorno interno zero; 0x0401 para 0xd1.
- Origens observadas dos campos de gatilho ligadas à resposta de versão e ao cache do host.
- Conclusão local, status bruto e status traduzido distinguidos; probe sem alterações.
- Somente documentos/evidência; base anterior de 59 testes sem nova execução ou comando USB.

## 0.19.0-research — 2026-11-16

- Preparação 0x537b0 ligada à requisição interna 8 e handler 0x7ed80.
- Caminho local de sucesso separado do caminho que monta comando 0x1a sob gatilhos do contexto.
- Limpeza de campos do host documentada sem atribuir reset/recuperação do sensor.
- Cinco destinos de chamadas e ponteiro de dispatch conferidos; semântica de 0x1a e 0xd1 pendente.
- Somente documentação/evidência; base anterior de 59 testes, sem nova execução ou operação USB.

## 0.18.0-research — 2026-11-16

- Varredura dos 75 registros deixa somente entrada 55 sob valores candidatos e gate de abertura explícitos.
- Consumidor de máscara 0x4000 pula cache local; papel de +0x20 delimitado e chamada preparatória 0x537b0 pendente.
- Encoder offline ampliado para 484/500 argumentos, sem link no probe; teste de limites/sobreposição ampliado.
- 59 testes aprovados; ASan/UBSan do encoder sem diagnóstico, sem detecção de leaks.
- Nenhuma inicialização USB ou novo teste de hardware.

## 0.17.0-research — 2026-11-16

- Participante relatou E1 schema 4: 38 bytes, major 6, bit ativo e discriminante 2, após 59 testes aprovados.
- Resultado exclui entrada de 500 bytes e admite a de 484 apenas no filtro +0x34; seleção completa pendente.
- Argumentos da entrada 55 comparados integralmente ao init_hardcoded público de blobs_90.py; frame reconstruído de 485 bytes idêntico.
- Somente documentação/evidência; nenhum novo executor ou teste de hardware solicitado.

## 0.16.0-research — 2026-11-16

- Origem do byte interno rastreada pelo handler 0x01 e callback de normalização até o offset candidato 0x19 da resposta completa.
- Nova opção explícita --summarize-init-discriminator: mesma consulta E1, schema 4, major/um bit/valor derivado, sem seleção de payload.
- Testes de privacidade, ramos, comprimentos e falhas; 59 testes aprovados e build concluído.
- ASan/UBSan do decoder sem diagnóstico, com detecção de leaks desabilitada.
- Resultado real do novo resumo pendente; nenhum bloco de inicialização habilitado.

## 0.15.0-research — 2026-11-16

- Campo +0x34 ligado ao discriminante derivado do bit 0x20 de uma estrutura interna; distingue os registros de 500/484 bytes para major 6.
- Campo +0x20 identificado como parâmetro passado ao consumidor, sem atribuir semântica completa.
- Modelo offline original do predicado, sem seleção de payload, e cinco testes novos; 57 testes aprovados.
- Correspondência com offset USB ainda não estabelecida; probe ativo inalterado e nenhum novo teste de hardware.

## 0.14.0-research — 2026-11-16

- Ordem parcial das solicitações 0x4000/0x1 e coordenação posterior do contexto documentada.
- Criação condicional do contexto auxiliar ligada à máquina de estados.
- Segunda entrada com versão 6.7/build 164 e máscara 0x4000 encontrada: 484 argumentos, contra 500 da referência.
- Cinco destinos CALL rel32 e campos das duas entradas conferidos no binário fixado por hash.
- Somente documentos/evidência; nenhuma nova execução de testes ou comando USB.

## 0.13.0-research — 2026-11-16

- Buffer interno rastreado a construtor compatível com alertas TLS; comparação explícita com RFC 5246.
- Cabeçalho tipo/03 03/comprimento big endian e dois chamadores documentados.
- Condição adicional do bit 0x02 em +0x128 delimita sucesso da transformação de dados de aplicação.
- Caminho de alertas separado do conteúdo opaco de init_00; sem negociação ou cifra validada no 00a6.
- Somente documentação/evidência; base anterior de 52 testes, sem nova execução ou operação USB.

## 0.12.0-research — 2026-11-16

- Predicados estáticos da transformação delimitados por contexto, estado, modo e flag interna.
- Aumento de capacidade de recepção separado de substituição do buffer de envio.
- Duas escritas na flag e encaminhamento de buffer interno documentados, sem atribuir semântica de sessão.
- Alinhamento dos 13 blobs públicos não vazios registrado como aritmética, sem identificar cifra ou efeitos.
- Somente documentação/evidência; base de 52 testes de v0.11 mantida, sem nova execução. Nenhum comando adicional habilitado.

## 0.11.0-research — 2026-11-16

- Cadeia estática da requisição do fornecedor ligada aos wrappers WinUsb_WritePipe/ReadPipe.
- Callback +0x20 identificado como pós-processamento de resposta; condições de contexto e transformações seguem em análise.
- Parser C original de status cleartext centralizado em E1/E2, preservando consultas e schemas.
- 52 testes aprovados e ASan/UBSan do parser sem diagnóstico, com detecção de leaks desabilitada.
- Nenhuma nova operação de hardware ou inicialização habilitada.

## 0.10.0-research — 2026-11-16

- Dispatcher e handler da solicitação interna 7 identificados: montagem de opcode 0x06 e argumentos.
- Frame de 501 bytes reconstruído em memória e comparado integralmente ao init_00 upstream.
- Codificador C original e offline, sem payload embutido e sem link no executável USB; teste de limites/sobreposição e ASan/UBSan.
- 51 testes aprovados. Callback USB final, transformações e efeitos do conteúdo continuam pendentes; nenhum novo comando ativo.

## 0.9.0-research — 2026-11-16

- Tabela e registro dos 500 bytes localizados; chaves candidatas 6.7/build 164 e máscara 0x4000 documentadas.
- Caminho estático de solicitação, seleção e cópia do payload rastreado, com limites explícitos sobre contexto e operações internas.
- Extrator de metadados restrito ao hash da DLL, sem executar o seletor ou exportar payloads.
- Seis testes adicionais; 50 no total. Nenhuma nova operação de hardware habilitada.

## 0.8.0-research — 2026-11-16

- Análise estática Dell: init_00 sem opcode (500 bytes) encontrado integralmente na DLL principal; blocos completos ausentes na busca contígua e três anchors candidatos localizados.
- Survey PE reproduzível sem carregar DLLs, extrair payloads ou acessar USB.
- Avaliação do mantenedor sobre a natureza dos blobs e limites do sandbox de terceiros documentados com fontes.
- Sete testes adicionais; 43 no total. Envelope ainda não decodificado e nenhum novo teste de hardware.

## 0.7.0-research — 2026-11-16

- Resultado E2 do participante registrado: 68 bytes, prefixo candidato zero e tamanho coincidente com referência.
- Proveniência de init_00/init_04 comparada com Validity91 e famílias de blobs python-validity, em commits fixados.
- Comparador estático reproduzível, sem execução de Python upstream e sem redistribuir payloads.
- Sete testes adicionais; 37 no total. Nenhum executor de blocos ou novo teste ativo de hardware.

## 0.6.0-research — 2026-11-16

- Resumo E1 do participante registrado: versão candidata 6.7, build 164, produto 48; quatro campos coincidem com o exemplo upstream.
- Consulta 0x19 investigada sem atribuir semântica não demonstrada; referência de 68 bytes e limites documentados.
- E2 experimental --probe-cmd19 implementado: envio isolado, leitura até 128 bytes, schema 3 com indicadores mínimos, sem dump/hash.
- Três testes adicionais; 30 no total. Treze cenários E2 simulados passaram com ASan/UBSan, sem validação de leaks.
- E2 real pendente; sem inicialização completa ou suporte biométrico.

## 0.5.0-research — 2026-11-16

- Primeiro resultado E1 do participante registrado: resposta de 38 bytes após execução elevada; conteúdo não validado.
- Nova opção --summarize-rom-info para a mesma consulta única, com schema 2 e somente quatro campos candidatos.
- Decoder com comprimento exato/status inicial zero, endian explícito e exclusão de bytes desconhecidos.
- Quatro testes adicionais; 27 no total. Verificações ASan/UBSan com LeakSanitizer desabilitado por limitação do ambiente.
- Sem execução do novo resumo no hardware pelo agente e sem suporte biométrico confirmado.

## 0.4.0-research — 2026-11-16

- Probe C experimental para consulta isolada 0x01, sem reset/configuração/retry e sem publicar resposta bruta.
- Verificação de ID/revisão/descritores; timeouts, cancelamento por sinal e tratamento de recursos.
- Simulador linkado no lugar da libusb e nove testes adicionais; 23 testes no total.
- 23 cenários simulados verificados com AddressSanitizer e UndefinedBehaviorSanitizer.
- Relato público específico do Latitude 3490/00a6 investigado, com limites documentados.
- Instruções para primeiro teste Linux pelo participante; execução real e suporte biométrico continuam pendentes.

## 0.3.0-research — 2026-11-16

- Matriz das sequências de abertura, captura e parada do VFS7552 upstream.
- Inventário offline reproduzível de 24 arrays e seis sequências, com comprimentos e hashes; sem redistribuir blocos binários.
- Comportamentos de transporte, validação de respostas e cancelamento documentados para revisão antes de um port.
- Experimento mínimo E1 especificado; ambiente recuperável e semântica do 00a6 continuam pendentes.
- Dez testes offline adicionados; 14 testes no total. Sem transferências USB ou driver funcional.

## 0.2.0-research — 2026-11-16

- Identificação comercial VFS7552 confirmada pelo INF oficial para 138a:00a6.
- Hashes do pacote e INF, fontes fixadas por commit e estado da MR 626 documentados.
- Coletor sysfs com campos numéricos permitidos, evidência real sanitizada e quatro testes offline.
- Licença LGPL-2.1-or-later adotada para código e documentação próprios.
- Sem comandos de protocolo ou validação biométrica.

## 0.1.0-research — 2026-11-16

- Estrutura inicial de pesquisa e documentação bilíngue.
- Evidências herdadas separadas das verificações locais e fontes atuais.
- Roadmap com critérios de saída e plano de validação.
- Sem implementação de driver ou validação de autenticação.
