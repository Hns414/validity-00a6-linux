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
