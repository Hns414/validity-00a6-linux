# Documentação primária e mecanismos de proteção distintos

## Pista documentada em uma família relacionada

O [whitepaper técnico HP Client Security](https://h10032.www1.hp.com/ctg/Manual/c04016447.pdf), página impressa 18, descreve patches de firmware VFS-RSA no contexto do VFS495: cifra AES-CBC-256 e assinatura RSA-2048, com verificação da assinatura pelo firmware antes da aceitação.

Isso é uma fonte primária para aquela família. Não identifica o algoritmo do bloco de 484 argumentos do VFS7552, seu cabeçalho, chave, assinatura ou instruções internas. O prefixo compartilhado e o comprimento alinhado não estabelecem que o esquema descrito pela HP se aplique ao 138a:00a6. Não foi localizado nessa documentação um parser do corpo investigado.

## Boletim VFS75xx: partições, não decoder do init

O [boletim da Synaptics de 14/07/2020](https://www.synaptics.com/sites/default/files/fingerprint-sensor-VFS7500-security-brief-2020-07-14.pdf), páginas 1–2, trata de sensores VFS75xx com flash externa e da CVE-2019-18618. Descreve uma falha na aceitação de tabelas de partição e uma correção distribuída por drivers que exige tabelas assinadas. Apresenta versões afetadas/corrigidas e condições de recuperação para o cenário abordado.

O aviso não fornece formato do payload de inicialização, nem valida o ramo de 484 bytes. Não foi comprovada a presença de flash externa no participante ou a incidência da falha no seu leitor. A versão Dell 5.5.4.1032 inspecionada não aparece como ramo exato na tabela publicada; comparar apenas “5.5” ou idade do pacote não basta para atribuir vulnerabilidade, correção ou compatibilidade. O pacote continua material de análise estática, sem instalação.

## Separação necessária na implementação

| Mecanismo | Evidência disponível | Lacuna para o 00a6 |
| --- | --- | --- |
| Proteção de registros do transporte | Caminhos estáticos de construção de registros e código público TLS | Estado real, negociação e integração ainda não validados |
| Proteção interna de patch/init | Blocos opacos, seleção condicional, igualdade com fonte público; HP descreve proteção para outra família | Algoritmo, formato autenticado e operações internas não demonstrados |
| Assinatura de tabela de partição | Boletim primário VFS75xx e ramo de provisionamento em fonte relacionado | Aplicabilidade ao hardware/firmware do participante não estabelecida |

Uma assinatura de partição não valida automaticamente um patch. Um registro TLS corretamente montado não prova que o payload seja aceitável. Uma identidade de bytes não demonstra ausência de alterações persistentes.

O fonte relacionado contém rotinas de provisionamento, mas o projeto não as executa. Este trabalho não usa a falha descrita para extrair dados, alterar partições ou contornar validações. O propósito da consulta aos documentos é estabelecer quais hipóteses têm suporte e quais ainda precisam de evidência.

## Estado da investigação e continuidade

A busca não produziu um consumidor público que decodifique o bloco de 484 argumentos. A conclusão permanece aberta; não foi inferida criptografia por entropia, prefixo ou tentativa de usar chaves do transporte.

O [registro da revisão](evidence/vendor-security-document-review.json) inclui fontes, páginas, escopo e limites. Não contém cópias integrais dos documentos. Esta etapa altera somente documentação/evidência; a base de 67 testes validada em v0.22 permanece sem nova execução. Probe e comandos permitidos continuam iguais.

Para avançar de forma verificável, a próxima análise deve localizar referências ao formato de patch no código do fornecedor ou em documentação específica, preservando a distinção entre bytes montados pelo host e interpretação pelo sensor. Não há captura pronta, novo teste USB ou solicitação de colocar o dedo nesta etapa.
