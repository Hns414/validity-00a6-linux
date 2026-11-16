# Roadmap por marcos

Cada marco exige evidência registrada; versões experimentais não indicam aptidão para login.

| Marco | Entregas e critério de saída | Estado |
| --- | --- | --- |
| M0 — v0.1.0-research | Estrutura, documentação, fontes, limites e plano de testes; commit inicial | Publicado: 1476b11 |
| M1 — identidade | Descritores sanitizados, INF com ID exato, hashes e fontes fixadas por commit | Concluído: v0.2.0-research |
| M2 — arquitetura | Comparação upstream, licença definida, estratégia libfprint e ambiente recuperável | Parcial: matriz e relato específico investigados; recuperação e semântica da consulta isolada pendentes |
| M3 — transporte | Operações mínimas compreendidas, timeouts/cancelamento e testes offline; experimento de hardware revisado | Parcial: E1/resumo e E2 relatados pelo participante; v0.14.0-research delimita ordem parcial e revela dois registros com mesma versão/máscara; seleção completa, contexto real, semântica interna e recuperação pendentes |
| M4 — biometria | Cadastro e verificação legítimos no hardware, rejeição e erros validados sem publicar dados biométricos | Pendente |
| M5 — integração | Revisão de segurança, integração fprintd/GNOME, proposta upstream e limitações documentadas | Pendente |

M0 não inclui driver. Não alterar PAM durante M0–M4. Antes de integração de login, definir recuperação, manter senha e registrar resultados positivos e negativos. Não prometer datas sem conhecer o protocolo.
