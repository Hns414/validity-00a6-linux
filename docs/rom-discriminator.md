# Origem do discriminante e resumo E1 schema 4

Análise estática limitada à DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`. RVAs relativos à ImageBase 0x180000000. Não foi executado código proprietário ou novo experimento no sensor pelo agente.

## Origem da estrutura interna

Na rotina externa 0x64b00, o buffer que alimenta contexto +0x28 é reutilizado quando presente ou alocado com 0x1b bytes em 0x64cf1. A chamada em 0x64d38 passa esse destino para 0x533a0. Após sucesso, 0x64d71 armazena o ponteiro no contexto +0x28.

A rotina 0x533a0 prepara a solicitação interna 1, guarda o destino em +0x18 do contexto de conclusão e instala callback 0x56830. O slot 1 da tabela de dispatcher, RVA 0x116348, aponta para 0x7df10. Esse handler monta comando 0x01, usa capacidade 0x26 (38) e chama o transporte em 0x7dfc3.

No caminho comum de resposta em 0x7dd60, o status inicial ocupa dois bytes e o descritor de conteúdo avança para resposta +2 em 0x7dea8. O callback 0x56830 preenche a estrutura interna com campos do conteúdo. Não é uma cópia integral: há conversões de inteiros e alguns offsets finais mudam. Para o campo que interessa, porém, a instrução 0x56a49 lê conteúdo +0x17 e 0x56a4f escreve destino +0x17, sem transformar esse byte.

Assim, **no caminho cleartext examinado, o bit interno +0x17/0x20 vem do bit 0x20 no offset 0x19 (25 decimal, base zero) da resposta completa**. O helper de seleção em 0x8feb0 usa esse campo. Esse rastreamento também preserva major no corpo +8, resposta +10, coerente com o resumo candidato anterior.

O [registro estruturado](evidence/rom-discriminator-mapping.json) contém coordenadas e essa relação. A conclusão é estática e específica do caminho; não mede a DLL em runtime nem demonstra que os demais filtros do seletor passam no 00a6.

## Nova opção explícita

```sh
./build/probe-rom-info --summarize-init-discriminator
```

A opção executa a mesma consulta E1 isolada: um byte 0x01 e uma leitura de até 64 bytes. Mantém seleção exata do hardware, descritores, limites de tempo e cancelamento já implementados. O decoder exige exatamente 38 bytes e status inicial zero. Não altera configuração USB ou executa inicialização/captura.

O schema 4 mantém os campos básicos de E1 e acrescenta:

- `decode_status`: `candidate_layout_unverified`, erro de layout/status ou `not_attempted`.
- `discriminator_candidate`: major, booleano `flag_0x20_set` e `derived_value`; nulo quando a análise não foi concluída ou houve falha de liberação.
- `full_selection_evaluated`: sempre false.

Para major 6, bit zerado deriva 3; bit ativo deriva 2. Para outro major, o helper modelado retorna zero. Nenhum desses valores significa suporte biométrico ou seleção completa. O byte de flags inteiro, timestamps, identificadores e conteúdo da resposta não são exportados. Os schemas anteriores 1/2/3 permanecem inalterados.

## Validação

`make test` passou com 59 testes sem skips e `make probe` compilou com os warnings tratados como erros. O teste nativo percorre os 256 valores do byte, comprimentos 0–64, status não zero e ponteiros nulos; verifica também que bytes não permitidos não alteram a saída. A simulação verifica ambos os ramos, outro major, envio único 0x01, limite de leitura, respostas malformadas e falhas de transporte/permissão/liberação.

ASan/UBSan do decoder passou sem diagnóstico com `ASAN_OPTIONS=detect_leaks=0`; detecção de leaks não foi validada. Os testes usam dados sintéticos e não provam o layout no hardware.

## Teste mínimo pelo participante

Este teste é útil agora para obter o bit que o resumo anterior não publicou. Aplicam-se as condições do [teste Linux E1](first-hardware-test.md), inclusive manter senha disponível e considerar que a recuperação física ainda não foi validada. Não há necessidade de Windows. A consulta continua uma operação ativa de protocolo, com efeitos internos não demonstrados integralmente.

Na cópia já clonada:

```sh
cd ~/validity-00a6-linux
git pull --ff-only
make test
make probe
sudo ./build/probe-rom-info --summarize-init-discriminator
```

Compartilhar somente a linha JSON. Se houver erro, parar e compartilhar essa saída, sem repetir automaticamente. Não executar o driver upstream com ID alterado ou enviar os blocos de inicialização.

O resultado permitirá avaliar esse predicado para o participante. Ainda faltam os demais filtros, contexto do transporte, efeitos dos payloads e recuperação antes de preparar qualquer executor de inicialização. Resultado real desta opção permanece pendente.
