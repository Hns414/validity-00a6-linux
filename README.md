# Validity 00A6 Linux

Open-source research toward Linux support for the Validity USB fingerprint reader **138a:00a6**, found in the Dell Latitude 3490.

**Research only: no functional driver, enrollment or authentication support yet.**

## Scope

Identify the hardware and protocol, evaluate existing drivers, then pursue a userspace libfprint implementation and fprintd integration. A kernel module is not an established requirement. Dell’s inspected INF identifies 138a:00a6 as a Synaptics VFS7552 Touch Fingerprint Sensor. Compatibility with other VFS7552 USB IDs remains unverified.

## Current findings

- Cached Linux sysfs metadata confirms revision 1.64, USB 2.00 at 12 Mbps, one vendor-specific interface and five endpoints.
- Dell NKXR6 was downloaded, its SHA-256 verified and its INF inspected without executing the installer. It maps 138a:00a6 to the VFS7552 commercial name.
- The pinned libfprint source explicitly lists 138a:00a6 as known unsupported. Its VFS7552 driver registers 138a:0091 only.
- Endpoint addresses overlap with that driver. A participant-run single 0x01 query returned 38 bytes. Its candidate version 6.7, build 164 and product code 48 match selected fields of the upstream example; the full reply and biometric capability remain unvalidated.

See [hardware](docs/hardware.md), [research and sources](docs/research.md), [protocol analysis](docs/protocol.md), [lab and proposed experiment](docs/lab.md), [milestones](docs/roadmap.md), and [test plan](tests/README.md). Working documentation is in Portuguese; this public overview is in English.

## Getting started

There is nothing to install yet. Read the research log and contribute sanitized hardware metadata or source-backed findings. Do not add this USB ID to another driver's table as a substitute for protocol validation.

## Development and versioning

Small, reviewable commits on main; experimental work on topic branches. The initial research baseline is tagged `v0.1.0-research`; this denotes documentation maturity, not driver capability. Future versions will state exactly which hardware operations were tested.

## Contributions and security

Read [CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md). Keep biometric samples, unique identifiers, keys, proprietary firmware and binaries out of Git. Do not change PAM or use experiments for login.

## Metadata collection

Run `python3 tools/collect_usb_metadata.py` without sudo. It reads cached sysfs fields and emits JSON to stdout; it does not open USB devices, reset them or send protocol commands. Output excludes serials, string descriptors and topology paths. Review it before sharing. No device returns status 1; inaccessible or malformed metadata returns status 2.

## Offline protocol research

`python3 tools/analyze_vfs7552.py /path/to/libfprint` inventories arrays and action sequences from a pinned Git commit in an existing local upstream checkout. It outputs lengths, hashes and sequence metadata; it never executes C or communicates with the sensor. See the [reproducible inventory](docs/evidence/vfs7552-static-inventory.json) and [limitations](docs/protocol.md).

The upstream open path resets USB and sends opaque initialization blocks. Its receive macros, endpoint transfer types and cancellation behavior need review before porting. An experimental single-query probe is now implemented and tested against a USB simulator. The participant reported a 38-byte reply from the target sensor; four candidate metadata fields have since been reported and match the selected upstream example fields; no raw reply has been inspected. See the [first hardware test](docs/first-hardware-test.md) before running it.

Run offline checks with `python3 -m unittest discover -s tests -v`. The current suite has 73 tests for metadata privacy, source inventory parsing and a simulated libusb transport. Probe simulation requires a C compiler, pkg-config and libusb development headers; those tests are explicitly skipped if unavailable. No tests validate biometric support.

## Experimental hardware probe

Build with `make probe` (C compiler, make, pkg-config and libusb-1.0 development files required). `build/probe-rom-info --help` does not access USB. The explicit `--probe-rom-info` flag sends a single 0x01 query and receives at most 64 bytes, after descriptor checks. No reset, configuration change, retry or raw reply logging is performed. A received reply is reported as **unvalidated**, never as working biometric support. The new `--summarize-rom-info` option repeats the same single query and emits only candidate build/version/product fields under a tentative layout; see the [field map](docs/rom-info.md). Read the [Linux test instructions](docs/first-hardware-test.md) before active use.

## Experimental command 0x19 probe

`build/probe-rom-info --probe-cmd19` runs E2: a single 0x19 command and a receive capped at 128 bytes. It neither runs 0x01 first nor continues initialization. Its semantics and persistence effects remain unknown; do not call it a proven read-only operation. Only byte count and candidate status/length booleans are exported. Read [E2 instructions and limitations](docs/cmd19.md) before hardware use. The participant reported a 68-byte E2 reply with a zero candidate status prefix. The payload and internal effects remain unvalidated; see the [sanitized result](docs/evidence/e2-participant-report-2026-11-16.json).

## Initialization research

The [init_00 analysis](docs/init-blobs.md) traces the 501-byte upstream block to an identical Validity91 literal. Its short prefix also occurs in unrelated initialization and reset blobs; that prefix does not establish safe semantics. No tool sends init_00 or init_04 in this project. A [reproducible offline comparator](tools/compare_init_blobs.py) exports only public-source hashes, lengths and comparison metadata, not payloads.

## Vendor driver analysis

A [read-only PE survey](docs/dell-static-analysis.md) now records hashes, exact-match searches and selected diagnostic anchors in the Dell DLLs. It found the exact 500-byte init_00 arguments in the official Dell DLL, stored without the leading opcode. It does not execute vendor code or access USB. The internal init envelope remains unresolved; the published Windows-driver sandbox can alter sensor provisioning and has not been run. No new hardware test is requested for this stage.

## Init descriptor selection

The [descriptor analysis](docs/init-selection.md) traces the known 500-byte arguments to a pointer table and selector/consumer routines in the pinned Dell DLL. Candidate keys 6.7/build 164 match E1, while masks and other selector conditions remain unresolved. A hash-restricted offline extractor reproduces the record metadata without exporting payloads or running the selector. No init command is enabled.

## Offline init framing

The [framing analysis](docs/init-framing.md) traced internal request 7 to a handler that constructs opcode 0x06 followed by the selected arguments. Reconstructing the 500 known argument bytes in memory produces the exact 501-byte upstream init_00 frame. An original offline encoder is tested with synthetic data and is not linked into the USB probe. Transport transformations, device-side effects and recovery remain unresolved; no new active command is enabled.

## Transport and response status

The [static transport analysis](docs/transport-and-status.md) now connects a vendor request to the WinUSB write/read wrappers and identifies the response callback. Context-dependent transformations and payload effects remain unresolved. An original status-header parser is shared by E1/E2 without changing their public schemas or adding commands. The init frame encoder is still offline-only.

## Transport context conditions

The [context analysis](docs/transport-context.md) documents the observed guards before buffer transformation, two internal flag writes and a separate receive-capacity adjustment. These static conditions do not establish the runtime state of the 00a6 or the effects of init_00. This documentation-only stage adds no hardware operation.

## Internal alert record path

The [internal buffer analysis](docs/alert-records.md) finds a path consistent with TLS alerts, including close_notify, and documents an additional application-record guard. This separates a connection-signaling buffer from the opaque init payload; it does not establish a working TLS session on the 00a6.

## Partial initialization order

The [opening-path analysis](docs/open-order.md) places the 0x4000 and 0x1 selection requests before later context coordination in one static path. Two records share version 6.7/build 164 and mask 0x4000 but have different argument lengths (500/484). Matching E1 fields therefore does not uniquely select the known init_00 record. Runtime selection remains unresolved.

## Initialization discriminator model

The [selector refinement](docs/init-discriminator.md) identifies an internal bit-derived discriminator that separates the 500-byte and 484-byte records. An original offline model tests this predicate with synthetic inputs. The internal-to-USB field mapping and full runtime selection remain unverified; no hardware probe field or command was added.

## E1 discriminator summary

`--summarize-init-discriminator` repeats the isolated 0x01 E1 query and exports only candidate major, one flag bit and its derived discriminator under schema 4. The [static dataflow analysis and Linux instructions](docs/rom-discriminator.md) document the candidate raw-reply mapping. It does not select or send an init payload. The participant reported major 6, the bit set and discriminator 2; earlier schemas remain unchanged.

## Participant discriminator result

The [participant result and 484-byte comparison](docs/init-484.md) show discriminator 2, which excludes the known 500-byte record under this predicate and admits the 484-byte record at this filter. The latter exactly matches the public python-validity `blobs_90.py` init arguments. Full selection, payload effects and biometric support remain unverified; no init executor is enabled.

## Conditional 484-byte selection

The [table and consumer analysis](docs/init-484-selection.md) leaves only record 55 under the reported candidate values and the opening path’s mandatory gate. This is a conditional static result, not observed runtime selection. The offline encoder now accepts 484 or 500 arguments and remains disconnected from USB; the preparatory call and payload effects are unresolved.

## Pre-initialization preparation

The [preparation analysis](docs/pre-init-preparation.md) separates local completion from a context-dependent path that constructs command 0x1a. Host cache cleanup does not establish device reset or recovery. Neither this command nor an init executor is enabled; command semantics remain unresolved.

## Cleanup reference and status translation

The [cleanup/status analysis](docs/cleanup-status.md) links public 0x1a usage to cleanup after flash operations and checks two Dell status translations. Device status 0x0491 maps to internal zero; 0x0401 maps to internal 0xd1. These references do not establish 00a6 command effects or recovery, and the probe behavior is unchanged.

## Public initialization flow and verification

The [public-flow analysis](docs/public-init-flow.md) places the matching 484-byte arguments within upstream initialization and distinguishes that sequence from Dell preparation. A hash-restricted offline verifier now reproduces the exact 485-byte frame comparison without exporting payloads. The public project does not register 00a6, and payload effects remain unresolved.

## Distinct payload roles

The [payload-role analysis](docs/payload-roles.md) distinguishes the 485-byte init frame from a 1765-byte public write-enable frame also found in a separate Dell descriptor. They share a prefix and block alignment, which do not establish purpose or cryptography. An optional offline inventory includes the write-enable literals; internal payload protection remains unverified.

## Vendor documentation scope

The [primary-document review](docs/vendor-security-context.md) separates transport protection, opaque initialization payloads and partition-table signatures. HP documents patch protection for the related VFS495 family; a Synaptics VFS75xx advisory concerns external-flash partition tables. Neither establishes the 00a6 payload format or confirms a vulnerability on the participant’s hardware.

## Initialization completion contract

The [handler/completion analysis](docs/init-completion.md) distinguishes copied patch arguments, an initial receive capacity of 34 bytes and a callback that stores translated status without parsing the reply body. These facts do not establish exact reply length, patch effects or capture readiness.

## Offline capture groundwork

The [capture groundwork](docs/capture-foundation.md) locates Dell diagnostic anchors for starting capture and waiting for a finger. An original offline inspector validates a strict candidate chunk shape from the 0091 reference and returns only counts, without copying pixels. The format is unverified on 00a6 and no capture command is enabled.

## Finger-wait route research

The [WaitForFinger analysis](docs/wait-finger-route.md) connects one status-query branch to an internal handler that constructs 0x77 and separates it from host event registration/waiting. State meanings and event endpoint mapping remain unverified; no query or finger-detection experiment was enabled.

## Event worker and endpoint order

The [event-worker analysis](docs/event-worker.md) traces a direct WinUSB branch to pipe index 3 and relates it to interrupt endpoint 0x83 using cached target descriptor order. Registration, local event cache and conditional AbortPipe cancellation are documented separately. A metadata-only cached-descriptor collector makes the mapping reproducible; event meanings and live detection remain unverified.

## Licensing

Project-authored code and documentation are licensed under **LGPL-2.1-or-later**; see [LICENSE](LICENSE). This matches the inspected upstream VFS7552 driver's license. Third-party materials retain their own terms. The Dell package and its INF are not redistributed. No upstream driver code has been copied into this project.

Independent project, unaffiliated with Dell, Validity or Synaptics.

O [rastreamento do registro de eventos](docs/event-registration.md) distingue tipos do host, conclusão e seletores do cache; armamento do sensor ainda pendente.

A [preparação de Start](docs/start-preparation.md) alcança o seletor com máscara 0x400000; seleção e efeitos ainda pendentes.

A [seleção condicional de Start](docs/start-selection.md) deixa a entrada 52 sob premissas explícitas; inclui máscara excluída e limitações do cache.

A [comparação pública da preparação](docs/start-public-comparison.md) não encontrou igualdade com 47 literais conhecidos e delimita os ramos alternativos 0x400000/0x80.

A [origem do parâmetro de preparação](docs/start-parameter-origin.md) foi ligada ao contexto do host; não é o discriminante medido por E1.

A [atribuição de modo e seleção no ramo 0x80](docs/start-mode-assignment.md) revela sobrescrita local para 3 e preferência condicional pela entrada 53 de 6676 argumentos.

O [caminho posterior à preparação](docs/post-preparation-request9.md) alcança a requisição interna 9 e um builder de opcode 0x02; argumentos e resposta ainda pendentes.

O [layout candidato de 0x02](docs/command02-layout.md) possui modelo original offline de tamanhos; suíte ampliada para 79 testes. Sem captura habilitada.

O [inspetor de corpo candidato de resposta](docs/capture-reply-layout.md) valida assinatura e contagens offline sem expor palavras; suíte ampliada para 85 testes.

A [análise dos nós e blocos](docs/capture-chunk-nodes.md) confirma caminhos tipo/tamanho e acrescenta inspetor offline sem conteúdo; suíte com 91 testes.

A [origem imediata do programa de captura](docs/capture-program-origin.md) foi ligada a descritor e cópia modificável; o tipo interno do sensor ainda não foi identificado.

O [produtor do descritor de programa](docs/program-descriptor-selection.md) foi ligado ao seletor da abertura e ao contexto +0x250; origem final da tabela ainda pendente.

A [classificação de produto da ROM](docs/product-context-class.md) liga condicionalmente o produto relatado 0x30 à classe de contexto 1; tipo interno ainda pendente.

O [produtor do tipo interno](docs/internal-type-seed-and-query.md) foi ligado a uma hipótese por produto e à consulta candidata 0x75; valor real ainda não confirmado.

O [callback e mapeamento de 0x75](docs/query75-callback-mapping.md) separa corpo, normalização e consulta de tabela; tipo real ainda não confirmado.

A [conferência pública de 0x75](docs/query75-public-crosscheck.md) corrige o mapper para o segundo DWORD e delimita o contexto TLS do fluxo público.

A [ordem do transporte de 0x75](docs/query75-transport-order.md) separa preparação, reaproveitamento de contexto e decisão de transformar o buffer.

O [registro da tabela de programas](docs/program-table-registration.md) corrige a categoria para 1 e inventaria 21 entradas estáticas, sem publicar payloads.

A [reconstrução dos programas](docs/program-materialization.md) encontrou igualdade integral pública em 17/21 entradas e acrescentou comparador offline; suíte com 97 testes.

A [análise de repetição dos programas](docs/program-repeat-patch.md) liga fatores ao tipo e acrescenta auditor offline sem mutação; suíte com 103 testes.

Os [nós adicionais de captura](docs/additional-capture-nodes.md) incluem caminhos condicionais e dinâmicos além do programa-base; montagem final ainda não validada.

O [layout de 0x15 e a fonte dinâmica](docs/chunk15-and-dynamic-source.md) delimita um nó de 12 bytes e callbacks que copiam estado do host, sem captura habilitada.

A [auditoria dos registros dinâmicos](docs/dynamic-host-records.md) identifica a busca na lista do host e diferenças entre cálculo de tamanho e cópia que ainda precisam ser explicadas.

Os [produtores dos registros dinâmicos](docs/dynamic-record-producers.md) delimitam alocação, criação sob demanda e uma entrada alternativa de importação; seleção real ainda pendente.

Os [nós condicionais de transporte](docs/conditional-transport-nodes.md) acrescentam campos aleatórios gerados no host; formatos e condições delimitados, sem captura habilitada.

Um [consumidor criptográfico isolado](docs/isolated-block-consumer.md) usa os campos anteriores; seu alcance pelo fluxo de captura permanece sem demonstração.

A [conclusão da requisição 9](docs/request9-completion.md) liga o parser ao callback e distingue corpo devolvido de referência interna, ainda sem semântica de imagem.
