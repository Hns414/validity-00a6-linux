# Primeiro teste Linux: E1

Este teste é experimental. Ainda não há driver de autenticação. O participante usa apenas Linux; Windows não é pré-requisito. O agente compilou a ferramenta e verificou o transporte simulado, mas não executou a consulta ativa no sensor.

## Preparação

Use uma sessão com o trabalho salvo e disponibilidade para encerrar a sessão e desligar completamente o laptop se o leitor parar de responder. Uma reinicialização não garante desfazer alterações persistentes de firmware; não temos evidência de que essa consulta as cause, nem garantia formal de ausência de efeitos. Se você não pode interromper o uso do computador agora, faça apenas a compilação e os testes offline.

A consulta 0x01 aparece em um relato público desse USB ID, mas aquele protótipo fazia reset antes. Nosso teste verifica uma consulta isolada, sem esse reset. Não executar o protótipo completo de terceiros, sequências de inicialização ou comandos de cadastro para esse fim.

## Compilar e testar sem acessar o sensor

Dentro do clone atualizado do repositório:

```bash
git pull --ff-only
make test
make probe
./build/probe-rom-info --help
```

Dependências no EndeavourOS/Arch: compilador C (por exemplo gcc), make, pkgconf, libusb e Python 3. Se faltarem, o erro de compilação indicará isso; instale os pacotes de desenvolvimento pelo gerenciador da distribuição antes de continuar. A compilação não instala nada no sistema.

Confira se os 23 testes passam sem skips. O --help não inicializa libusb. Nada nessas etapas executa o teste de hardware.

## Executar uma vez no sensor

Com a preparação acima atendida:

```bash
./build/probe-rom-info --probe-rom-info
```

Comece sem sudo. Não há instalação, PAM, alteração de serviço ou regra udev. A ferramenta recusa alvo ausente/múltiplo, revisão diferente de 1.64, configuração/interface/endpoints inesperados e interface ocupada; não tenta desconectar um driver.

Somente depois dessas verificações, envia um byte 0x01 por bulk OUT e lê no máximo 64 bytes por bulk IN. Não faz reset, troca de configuração, pareamento, flash, captura ou retry automático. Ctrl+C solicita cancelamento da transferência pendente. As transferências têm limite individual de 1 segundo e orçamento conjunto de 3 segundos; preparação/liberação não entram nesse prazo. Drenagem de cancelamento tem até 1 segundo adicional.

## Retorno a compartilhar

Envie somente a linha JSON impressa pela ferramenta. Não envie logs brutos, dados do dispositivo ou saídas completas de outras ferramentas. Exemplo de formato, **sintético**:

```json
{"schema_version":1,"experiment":"E1","status":"reply_received_unvalidated","stage":"read","received_bytes":38,"biometric_support":false}
```

Esse estado significa que houve troca de dados; não confirma identidade dos campos, compatibilidade do protocolo, captura ou reconhecimento. Os bytes recebidos não são impressos, gravados ou decodificados.

| Estado | Interpretação / próximo passo |
| --- | --- |
| reply_received_unvalidated | Informe o JSON; definir uma análise de campos antes de qualquer comando adicional |
| permission_denied | Informe o JSON; preparar acesso pontual ao dispositivo, sem chmod global ou instalação de regras nesta etapa |
| usb_unavailable / target_not_found | Informar o resultado para distinguir acesso do ambiente e presença do dispositivo |
| unexpected_* / ambiguous_target / interface_busy | Parar e investigar a pré-condição; não contornar a verificação |
| timeout / deadline / disconnected / transfer_error | Não repetir em sequência; informar o JSON e o estado do leitor |
| cancelled | A consulta foi interrompida; não interpretar como teste concluído |
| cancel_drain_failed | O callback não pôde ser drenado; processo termina sem liberar memória ainda em uso. O SO fecha recursos; informar resultado antes de repetir |

Uma permissão negada não é falha do protocolo. Em nenhum estado o teste anuncia suporte biométrico. O código de saída 0 significa apenas resposta recebida sem validação semântica; falhas retornam 2. Interface liberada e memória de transporte são verificadas nas simulações; recuperação física do leitor ainda não foi exercitada.
