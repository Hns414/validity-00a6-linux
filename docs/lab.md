# Ambiente e próximo experimento

Estado em 2026-11-16: coleta sysfs e análise offline concluídas. Não foi preparado nem validado um ambiente de execução ativa do protocolo. Os metadados do kernel estão acessíveis, mas libusb falhou na primeira sessão; uma ferramenta de transporte ainda precisará diagnosticar separadamente permissões e visibilidade.

## Ambiente definido para desenvolvimento

- Ferramentas de pesquisa em Python 3, biblioteca padrão; testes offline não precisam de sudo ou sensor.
- Fonte upstream mantida em checkout separado, fixada por commit; sem instalação por cima do libfprint/fprintd da distribuição.
- Pacote Dell e arquivos extraídos ficam fora do Git público. A análise atual não executa DLLs ou instaladores.
- Um futuro teste ativo deverá usar acesso ao dispositivo concedido ao processo de teste, com seleção exata do ID e sem desconectar drivers automaticamente. Nenhuma regra udev foi instalada.

Para testes com USB, usar host de teste ou sistema live com senha disponível e procedimento de desligamento completo conhecido. Snapshot de VM protege o sistema convidado, mas não desfaz mudanças persistentes no leitor físico. Esse ambiente ainda não foi exercitado; não marcar recuperação como validada.

## Experimento E1 proposto: consulta mínima de identidade

Objetivo: verificar se a consulta 0x01, usada como informação de ROM em projetos relacionados, é reconhecida pelo 00a6. Essa finalidade ainda é hipótese para este ID; emissão de um byte por bulk OUT já é operação ativa, mesmo quando o objetivo é ler informação.

**Estado: protótipo C implementado, compilado e testado com libusb simulada; não executado no hardware.**

Evidência específica localizada: a issue Validity90 #110 contém um relato do Latitude 3490 com 138a:00a6, envio de 0x01 e resposta de 38 bytes. O protótipo relacionado fazia reset antes; por isso o relato não valida a consulta isolada nem garante ausência de efeitos persistentes. Confirmar o ambiente de recuperação antes de testar. Não coletar cadastro ou autenticação biométrica para essa finalidade; traces brutos ficam privados.

Contrato implementado pelo protótipo (com limites abaixo):

1. Confirmar 138a:00a6 e os descritores esperados; recusar múltiplos alvos, interface ocupada, configuração inesperada ou falta de permissão. Não trocar configuração, fazer reset ou repetir automaticamente.
2. Reivindicar somente a interface necessária, sem detach automático. Interromper se não for possível.
3. Enviar uma única consulta de 1 byte e fazer uma leitura limitada a 64 bytes no endpoint correspondente. Usar timeout por transferência de 1.000 ms e orçamento de 3.000 ms para a fase de troca USB, com cancelamento efetivo. Preparação e liberação ficam fora desse orçamento; drenagem de cancelamento tem limite adicional de 1.000 ms. Não executar cmd_19 nem os passos seguintes em cascata.
4. Registrar somente a contagem de uma resposta de 1 a 64 bytes, sempre como reply_received_unvalidated. Não decodificar nem aceitar a estrutura como válida para o 00a6. Os 38 bytes dos relatos são referência, não critério de compatibilidade estabelecido.
5. Em resposta desconhecida, timeout, cancelamento ou desconexão: parar, liberar recursos e registrar apenas operação, comprimento, duração e classe de erro. Não salvar bytes de resposta por padrão. Não tentar recuperação por escrita ou reset.

Saída pública desejada: resultado sanitizado associado ao commit do protótipo, sem identificadores únicos. Um retorno bem-sucedido só comprovará essa consulta; não comprovará captura, matching ou autenticação.

Se o dispositivo deixar de responder, o procedimento de recuperação deverá seguir o plano previamente exercitado no host de teste. Sem esse plano, E1 permanece pendente. Não existe ainda promessa de reversão de estado persistente por software.

## Execução pelo participante

O ambiente do participante é Linux somente. Não é preciso instalar Windows para E1. O [primeiro teste de hardware](first-hardware-test.md) traz compilação, comando, pré-condições e interpretação. O agente não executou a opção ativa no sensor.

O protótipo não chama reset, set_configuration, detach, pareamento, escrita em flash ou comandos de captura. Encerrar uma transferência que não retorna seu callback dentro do limite exige terminar o processo sem liberar buffers ainda em uso; o sistema operacional fecha seus recursos. Isso não deve ser apresentado como recuperação comprovada do dispositivo.
