# Plano de validação

Ainda não há driver nem testes de hardware aprovados. Não interpretar a existência desta pasta como validação funcional.

## Etapa atual: somente leitura

- Conferir versões e presença do dispositivo no host; falha de acesso USB deve ser registrada como limitação.
- Revisar descritores por campos permitidos, removendo identificadores únicos.
- Verificar a procedência das fontes e a consistência entre fato, hipótese e pendência.

## Etapas futuras

Após documentar o protocolo e preparar recuperação: testar parsing com fixtures sintéticas, mensagens truncadas, comprimentos inválidos, códigos de erro, timeout, cancelamento e desconexão. Só depois testar enumeração/inicialização e recuperação no hardware de propriedade do participante.

Para biometria: cadastro, verificação com dedo cadastrado, rejeição de dedo não cadastrado, cancelamento, reconexão e suspend/resume. Medições isoladas não estabelecem taxa estatística de falso aceite/rejeição. Publicar apenas resultado agregado e contexto sanitizado.

Cada relatório deve conter: data, commit, ambiente sem identificadores, operação, expectativa, resultado observado, limitações e recuperação. Não armazenar imagens, templates, chaves, traces brutos ou credenciais. Não há testes executáveis porque ainda não existe implementação a validar.
