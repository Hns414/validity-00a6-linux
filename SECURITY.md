# Segurança

Este projeto não oferece autenticação utilizável. Preserve a senha como método de acesso e não altere PAM durante a pesquisa.

Não publique impressões digitais, templates, chaves, credenciais, seriais ou capturas brutas. Investigue protocolo em máquina de teste com recuperação disponível; uma VM com USB passthrough ainda pode alterar o dispositivo físico.

## Relatos sensíveis

Não abra issue pública com detalhes sensíveis. No GitHub, use Security → Report a vulnerability se o canal privado estiver habilitado. Caso não esteja, solicite um canal privado em uma issue sem incluir detalhes técnicos sensíveis. Ainda não há endereço privado dedicado nem SLA de resposta.

Antes de qualquer integração de login: revisar armazenamento de templates, fronteiras de confiança, rejeição de entradas inválidas, cancelamento, falhas e recuperação. Não registrar dados biométricos em logs de testes.
