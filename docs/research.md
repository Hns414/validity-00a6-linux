# Investigação técnica

Consulta inicial: 2026-11-16. Os dois documentos entregues pelo usuário foram lidos integralmente como contexto histórico; comandos sugeridos neles não equivalem a resultados executados.

## Registro de fontes

| Fonte | Resultado | Limite |
| --- | --- | --- |
| [libfprint: dispositivos](https://fprint.freedesktop.org/supported-devices.html) | Lista de desenvolvimento consultada por busca: 138a:0091 associado a VFS7552; 138a:00a6 não encontrado | Acesso direto sofreu timeout; lista não equivale à versão instalada |
| [libfprint upstream](https://gitlab.freedesktop.org/libfprint/libfprint) | Destino pretendido para integração | Inspeção do código/commit e licença pendentes |
| [MR 626](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/626) | Acesso negado por Anubis | Estado, conteúdo e dispositivos não verificados; não é evidência de suporte |
| [python-validity USB](https://github.com/uunicorn/python-validity/blob/master/validitysensor/usb.py) | Tabela enumera 138a:0090, 138a:0097, 138a:009d e 06cb:009a | Branch mutável; fixar commit na próxima comparação; 00a6 ausente da tabela |
| [python-validity](https://github.com/uunicorn/python-validity) | Projeto usa serviço D-Bus com open-fprintd e sessões TLS; repositório indica licença MIT | Arquitetura de referência; protocolo do 00a6 não demonstrado |
| [Dell NKXR6](https://www.dell.com/support/home/en-us/drivers/driversdetails?driverid=nkxr6) | Latitude 3490 consta entre sistemas compatíveis | INF e vínculo exato ao USB ID ainda pendentes |
| [Catálogo comunitário](https://github.com/jedbillyb/linux-fingerprint-drivers/blob/master/docs/unsupported-devices.md) | Referência do handoff | Não validado nesta etapa; não substitui fonte upstream |

## Pacote Dell candidato

Metadados conferidos na página oficial: versão 5.5.4.1032, A00; data 2018-01-10; Windows 10 64-bit. Esses dados tornam o pacote candidato, mas não identificam o chip. O download por HTTPS retornou HTTP 403; nada foi executado ou extraído.

Próximo procedimento: obter o pacote oficial localmente, registrar hash e termos aplicáveis, extrair sem executar o instalador e localizar no INF `USB\VID_138A&PID_00A6`. Registrar seção, nome comercial e DriverVer com contexto mínimo. Conferir arquitetura e correspondência com a revisão do hardware. Não versionar o pacote, firmware ou binários. Um nome em INF também não prova equivalência de protocolo com 0091.

## Decisão de arquitetura

Preferir avaliar um driver userspace integrado ao libfprint, aproveitando fprintd como serviço de autenticação. Isso é uma direção de pesquisa, não uma implementação aprovada. Comparar tabela de IDs, transporte, inicialização, endpoints, modelo de captura/matching e dependências de firmware antes de escolher um driver base. GNOME/Wayland são camadas posteriores à enumeração e ao suporte do sensor.

Não instalar python-validity nem executar seus exemplos de reset/pareamento nesta etapa. Apenas adicionar 00a6 à tabela de IDs não implementa o protocolo.

## Questões abertas e próximos experimentos

1. Identidade: INF oficial e descritores sanitizados concordam?
2. Upstream: qual commit/versão e licença dos drivers candidatos? Qual estado real da MR 626?
3. Transporte: quais endpoints e mensagens são necessários? Começar por documentação e análise offline; nenhuma transferência vendor-specific foi autorizada pelo plano atual.
4. Segurança: matching ocorre no host ou sensor? Há chaves, templates persistentes ou inicialização que altera flash?
5. Testabilidade: construir fixtures sintéticas de mensagens documentadas antes de testes ativos; não inventar um driver funcional.
