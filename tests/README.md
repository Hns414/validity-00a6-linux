# Plano de validação

Ainda não há driver nem testes de hardware aprovados. Não interpretar a existência desta pasta como validação funcional.

## Etapa atual: somente leitura

- Conferir versões e presença do dispositivo no host; falha de acesso USB deve ser registrada como limitação.
- Revisar descritores por campos permitidos, removendo identificadores únicos.
- Verificar a procedência das fontes e a consistência entre fato, hipótese e pendência.

## Etapas futuras

Após documentar o protocolo e preparar recuperação: testar parsing com fixtures sintéticas, mensagens truncadas, comprimentos inválidos, códigos de erro, timeout, cancelamento e desconexão. Só depois testar enumeração/inicialização e recuperação no hardware de propriedade do participante.

Para biometria: cadastro, verificação com dedo cadastrado, rejeição de dedo não cadastrado, cancelamento, reconexão e suspend/resume. Medições isoladas não estabelecem taxa estatística de falso aceite/rejeição. Publicar apenas resultado agregado e contexto sanitizado.

Cada relatório deve conter: data, commit, ambiente sem identificadores, operação, expectativa, resultado observado, limitações e recuperação. Não armazenar imagens, templates, chaves, traces brutos ou credenciais. O driver ainda não tem implementação a validar. O coletor de metadados possui testes offline executáveis, descritos abaixo.

## Coletor sysfs

`python3 -m unittest discover -s tests -v`: quatro testes com sysfs sintético verificam exclusão de strings sensíveis e topologia, rejeição de valores malformados, seleção do ID exato e erro de raiz indisponível. Não enviam comandos USB. Coleta real realizada com sucesso em 2026-11-16; saída em docs/evidence. Esses testes não validam o protocolo biométrico.

## Inventário estático upstream

O analisador possui dez testes offline adicionais para cálculo de comprimentos sem contar comentários, preservação da ordem, distinção entre tamanhos declarados e verificados, rejeição de expressões/valores inválidos, declarações não suportadas, arrays/sequências duplicados, referências ausentes, macros inválidas e resposta maior que o buffer solicitado. Total atual: 14 testes.

O inventário real também foi regenerado do commit fixado e comparado ao JSON versionado. Isso verifica a reprodução da análise de fonte, não a compatibilidade do 00a6. O parser aceita um subconjunto restrito de C e falha diante de sintaxe que não compreende.

## Transporte C com USB simulada

Nove testes adicionais, com vários cenários por teste, compilam src/probe_rom_info.c contra tests/fake_libusb.c, sem link com a libusb real. O simulador implementa somente as funções necessárias; adicionar chamadas não previstas, como reset ou troca de configuração, quebra esse link de teste. O relógio também é simulado para exercitar deadlines sem esperas reais.

Verificados: consulta única, leitura limitada, ordem e liberação de recursos, recusa de descritores incompatíveis/múltiplos alvos/permissão/interface ocupada, short write, timeout, desconexão, cancelamento SIGINT, event loop com erro, conclusão tardia e saída controlada quando o callback de cancelamento não é entregue. A saída não contém bytes de resposta. Total: 23 testes, sem skips no ambiente usado nesta etapa.

Também foram compilados os mesmos arquivos com -fsanitize=address,undefined e executados 23 cenários simulados, sem diagnósticos desses sanitizadores. Isso não verifica o comportamento do driver USB real, latência real, firmware ou recuperação do sensor.

Dependências adicionais: compilador C, pkg-config e headers de libusb-1.0. Se faltarem, os nove testes de transporte mostram skip explícito; os demais continuam disponíveis com Python padrão. O teste de hardware é manual e separado, nunca executado pelo comando make test.

## Decodificação candidata de ROM info

Quatro testes adicionais (27 no total) verificam a seleção de campos, recusa de tamanho/status inesperados, ausência de campos em falhas de transporte/liberação e um programa C específico de limites e privacidade. Esse programa percorre todos os comprimentos entre 0 e 64, verifica little endian e modifica cada byte omitido para demonstrar que não afeta a saída dos campos candidatos. Testa também ponteiros nulos e limpeza do resultado ao rejeitar entrada.

Verificação extra desta etapa: decoder e oito cenários simulados de resumo passaram com ASan/UBSan. LeakSanitizer falhou por limitação de ptrace do ambiente; a execução foi repetida com ASAN_OPTIONS=detect_leaks=0. Portanto não se declara validação de leaks por esse sanitizador nesta etapa. O resumo ainda não foi executado no sensor pelo participante.

## E2: isolamento do comando e privacidade

Três testes adicionais (30 no total) verificam emissão única de 0x19, nenhuma emissão de 0x01, leitura limitada a 128 bytes, formato schema 3, status incompleto/não zero, tamanho diferente da referência e ausência de conclusões em erros de transporte/liberação. O simulador exige que o byte do comando coincida com a operação esperada pelo teste; qualquer outro envio falha.

Treze cenários E2 simulados foram executados com ASan/UBSan e ASAN_OPTIONS=detect_leaks=0, sem diagnósticos. A detecção de leaks permanece indisponível por limitação de ptrace do ambiente. Não houve execução ativa de E2 no sensor nesta etapa.

## Comparação estática dos blocos de inicialização

Sete testes adicionais (37 no total) verificam extração de literais sem executar o Python upstream, tratamento de whitespace inclusive entre nibbles usado por unhex, rejeição de expressões/dados inválidos/definições duplicadas, ordem e flag optional das mensagens e distinção entre prefixo comum e igualdade integral. O comparador usa ast para ler sintaxe; não usa eval nem importa módulos de terceiros.

A comparação real foi regenerada dos objetos Git fixados de três repositórios e coincide com o JSON versionado. O resultado só descreve igualdade, tamanhos, hashes e flags declaradas. Não valida semântica de comandos ou segurança de sua execução. Nenhuma nova transferência USB foi realizada nesta etapa.

## Survey PE somente leitura

Sete testes adicionais (43 no total) usam arquivos PE32+ inteiramente sintéticos para verificar estrutura/seção, mapeamento de RVA, recusa de cabeçalhos truncados, arquitetura incorreta, seções fora do arquivo e anchors sem mapeamento inequívoco. A busca literal verifica correspondência contígua e não infere semântica a partir de um prefixo. Um teste adicional verifica que o payload armazenado sem o opcode é encontrado mesmo quando o comando completo não está presente. Nenhum teste carrega DLL ou utiliza binário proprietário como fixture.

O relatório real foi regenerado a partir das duas DLLs privadas do pacote Dell e comparado ao JSON versionado; são idênticos. Não houve execução de código Windows ou acesso ao sensor.

## Localização do descritor de inicialização

Seis testes adicionais (50 no total) verificam metadados/coordenadas de um registro sintético, conteúdo ausente/duplicado, ponteiro duplicado, tamanho inconsistente e regiões ambíguas/não mapeadas. A ferramenta real verifica o hash exato da DLL antes de aplicar offsets de análise. O manifesto foi reproduzido por leitura estática, sem executar código do fabricante ou acessar USB. Esses testes não provam os critérios completos do seletor nem os efeitos do payload.

## Framing offline de init_00

Um novo teste automatizado compila src/init_frame.c com um programa C de dados sintéticos. Verifica comprimentos entre 0 e 600, todas as capacidades menores que 501, saída intacta em falhas, sentinelas, ponteiros nulos, SIZE_MAX e argumentos sobrepostos à saída. Total: 51 testes aprovados. O programa também passou com ASan/UBSan, ASAN_OPTIONS=detect_leaks=0; não se declara teste de leaks.

A composição real em memória a partir da DLL privada foi comparada ao init_00 upstream e registrada somente como metadados. A ferramenta de verificação não interpreta automaticamente o disassembly nem executa instruções do fabricante. O encoder não é ligado ao probe ativo; nenhum teste unitário envia o bloco ao USB.

## Parser comum de status cleartext

Um novo teste C percorre tamanhos 0–128, verifica little endian, status não zero, payload vazio e comprimento dos dados, recusa cabeçalhos truncados/ponteiros nulos e confirma limpeza de saída e independência dos bytes do payload. Total: 52 testes aprovados, incluindo integração de E1/E2 com o helper comum e schemas preservados. ASan/UBSan do parser passou com detect_leaks=0; LeakSanitizer continua fora da validação por limitação do ambiente.

Esses testes verificam nosso parser e simulações de transporte. Não verificam a semântica completa da DLL, o contexto do participante ou seus callbacks em runtime.

## Discriminante offline de inicialização

`test_init_discriminator.py` usa somente entradas sintéticas para o helper modelado em `tools/model_init_discriminator.py`. Verifica fronteiras da CLI e isolamento do bit relevante. Não valida o seletor inteiro, offsets USB ou escolha de payload no dispositivo.

## Resumo de discriminante E1

O teste nativo de ROM verifica o decoder de um bit para todos os valores possíveis, dados não permitidos, comprimentos e erros. A libusb simulada cobre schema 4, ambos os ramos e outro major, envio único E1 e recusa de respostas/falhas. Não há sensor na suíte.

## Verificador do frame de 485 bytes

`test_init_484.py` usa arquivo/intervalos sintéticos para verificar correspondência integral, divergência no último byte, campos e ligações, limites PE e truncamento. Não carrega DLL ou acessa USB. O verificador da CLI exige hash e tamanho conhecidos antes da inspeção; o resultado real da comparação é somente metadado.

## Inventário opcional de write-enable

O parser de literais inclui db_write_enable somente quando solicitado. Os testes verificam separação do init apesar de prefixo comum e recusa de expressões dinâmicas/duplicadas. Nenhum bloco é executado.

## Inspetor offline de bloco candidato de captura

`test_capture_chunk.c` usa somente dados sintéticos do formato de referência 0091. Verifica limites de comprimento, linhas inteiras, acumulação sem overflow e saída sem pixels. O componente não está ligado ao probe e não valida o formato do 00a6.

## Ordem de endpoints em cache

`test_endpoint_order.py` usa descritores sintéticos e sysfs temporário. Verifica ordem original em vez de ordenação por endereço, recusa truncamentos/duplicatas/configurações fora do escopo e ausência de strings/topologia na saída. Não envia requisições USB.

`test_capture_request_model.py` cobre o modelo offline de tamanhos de 0x02: fronteiras, orçamento de análise e caso especial dos múltiplos de 64. A suíte completa tem 79 testes. Não usa sensor nem payload.

`test_capture_reply.py` cobre o corpo candidato de resposta: assinatura, contagens excessivas, truncamento, orçamento e omissão do conteúdo. A suíte completa tem 85 testes; não realiza USB.

`test_capture_chunks.py` verifica o inspetor offline de sequências tipo/tamanho: truncamentos, cabeçalhos, limites e omissão de conteúdo. A suíte completa tem 91 testes.

`test_capture_programs.py` cobre fragmentos empacotados, limites de leitura e extração de literais públicos sem execução. A suíte completa tem 97 testes.

`test_program_repeats.py` verifica fronteiras e possíveis truncamentos do auditor de repetição, sem alterar programas ou acessar USB. A suíte completa tem 103 testes.

O inspetor offline de corpo candidato 0x78 é coberto por seis testes de limites, contagens e privacidade da saída. Suíte completa: 109 testes aprovados na v0.59.

Na v0.62, três testes adicionais verificam a capacidade explícita do destino no inspetor offline 0x78. Suíte completa: 112 testes aprovados.

Na v0.65, seis testes cobrem o inspetor offline de envelopes de registros. Suíte completa: 118 testes aprovados.
