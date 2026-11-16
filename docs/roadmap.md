# Roadmap por marcos

Cada marco exige evidência registrada; versões experimentais não indicam aptidão para login.

| Marco | Entregas e critério de saída | Estado |
| --- | --- | --- |
| M0 — v0.1.0-research | Estrutura, documentação, fontes, limites e plano de testes; commit inicial | Preparado |
| M1 — identidade | Descritores sanitizados, INF com ID exato, hashes e fontes fixadas por commit | Pendente |
| M2 — arquitetura | Comparação upstream, licença definida, estratégia libfprint e ambiente recuperável | Pendente |
| M3 — transporte | Operações mínimas compreendidas, timeouts/cancelamento e testes offline; experimento de hardware revisado | Pendente |
| M4 — biometria | Cadastro e verificação legítimos no hardware, rejeição e erros validados sem publicar dados biométricos | Pendente |
| M5 — integração | Revisão de segurança, integração fprintd/GNOME, proposta upstream e limitações documentadas | Pendente |

M0 não inclui driver. Não alterar PAM durante M0–M4. Antes de integração de login, definir recuperação, manter senha e registrar resultados positivos e negativos. Não prometer datas sem conhecer o protocolo.
