# E2: comando 0x19 isolado

Estado: implementado e simulado; não executado no hardware do participante. O objetivo é observar uma resposta a 0x19, sem reproduzir a inicialização inteira. Este é um novo experimento, distinto de E1.

## Evidência e incerteza

No [driver upstream fixado](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/drivers/vfs7552.c), 0x19 vem depois de 0x01, com leitura até 128 bytes. O [header de referência](https://gitlab.freedesktop.org/libfprint/libfprint/-/blob/8b6e4e39bee58de2774222e3730269def470b157/libfprint/drivers/vfs7552_proto.h) contém exemplo de 68 bytes. O [relato público do 00a6](https://github.com/nmikhailov/Validity90/issues/110) também contém resposta desse tamanho, dentro de uma sequência maior que incluía reset.

A função e os efeitos internos continuam desconhecidos. Não se garante que o comando seja somente leitura nem que não altere estado persistente. Não chamar sua resposta de capacidades, sessão TLS ou dados de identidade sem evidência adicional. A resposta pode conter campos variáveis ou identificadores; não publicar bytes, hash ou comparação byte a byte do payload.

E2 deliberadamente não envia 0x01 antes. Uma resposta diferente da sequência upstream é resultado a investigar, não motivo para repetir comandos ou iniciar automaticamente o sensor.

## Implementação

A opção --probe-cmd19 reutiliza o transporte verificado em E1 e realiza apenas:

1. Verificação do dispositivo 138a:00a6/revisão 1.64 e descritores esperados; interface livre.
2. Claim da interface 0, sem detach, troca de configuração ou reset.
3. Uma emissão de um byte 0x19 em bulk OUT 0x01.
4. Uma leitura de até 128 bytes em bulk IN 0x81.
5. Liberação de recursos e JSON sanitizado.

Timeout individual de 1.000 ms e orçamento de troca de 3.000 ms; preparação/liberação fora desse prazo. Cancelamento por sinal e drenagem limitada seguem E1. Sem retry, 0x01, blocos de inicialização, captura, cadastro ou comandos de armazenamento. O agente executou apenas simulações e --help.

## Executar no Linux do participante

Use as mesmas condições de E1: trabalho salvo, disponibilidade para encerrar a sessão/desligar o laptop se necessário e sem depender do leitor para autenticação. A recuperação física ainda não foi exercitada pelo projeto. Se não puder interromper o computador agora, limite-se a atualizar, compilar e executar os testes offline.

```bash
cd ~/validity-00a6-linux
git pull --ff-only
make test
make probe
```

Se os 30 testes passarem sem skips e a compilação concluir, a opção ativa é:

```bash
sudo ./build/probe-rom-info --probe-cmd19
```

Execute uma vez. Envie somente a linha JSON. Não executar consultas posteriores para contornar erro ou divergência.

## Interpretar a saída

Exemplo **sintético de simulação**, não resultado do seu sensor:

```json
{"schema_version":3,"experiment":"E2","status":"reply_received_unvalidated","stage":"read","received_bytes":68,"biometric_support":false,"command":"0x19","candidate_status_zero":true,"reference_length_bytes":68,"reference_length_match":true}
```

- candidate_status_zero: true somente se a resposta tiver pelo menos dois bytes e ambos forem zero, sob a interpretação candidata de status. false significa que algum deles não é zero; null significa que não houve status completo utilizável. Não decodifica o restante.
- reference_length_match: compara apenas o tamanho recebido a 68. Tamanhos diferentes são registrados, não rejeitados por semelhança forçada. null indica ausência de resultado confiável da troca ou falha de liberação.
- reply_received_unvalidated: transporte recebeu dados; não indica comando semanticamente validado. O código de saída 0 tem esse mesmo limite.
- Em falha de transporte, cancelamento ou liberação, os indicadores não afirmam validade nem correspondência.

Mesmo true/true não valida o conteúdo integral, a inicialização, captura ou matching. O próximo passo dependerá do resultado observado e da análise das sequências seguintes.
