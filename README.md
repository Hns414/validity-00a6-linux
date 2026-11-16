# Validity 00A6 Linux

Open-source research toward Linux support for the Validity USB fingerprint reader **138a:00a6**, found in the Dell Latitude 3490.

**Research only: no functional driver, enrollment or authentication support yet.**

## Scope

Identify the hardware and protocol, evaluate existing drivers, then pursue a userspace libfprint implementation and fprintd integration. A kernel module is not an established requirement. Dell’s inspected INF identifies 138a:00a6 as a Synaptics VFS7552 Touch Fingerprint Sensor. Compatibility with other VFS7552 USB IDs remains unverified.

## Current findings

- Cached Linux sysfs metadata confirms revision 1.64, USB 2.00 at 12 Mbps, one vendor-specific interface and five endpoints.
- Dell NKXR6 was downloaded, its SHA-256 verified and its INF inspected without executing the installer. It maps 138a:00a6 to the VFS7552 commercial name.
- The pinned libfprint source explicitly lists 138a:00a6 as known unsupported. Its VFS7552 driver registers 138a:0091 only.
- Endpoint addresses overlap with that driver, but no protocol compatibility or functional support has been established.

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

The upstream open path resets USB and sends opaque initialization blocks. Its receive macros, endpoint transfer types and cancellation behavior need review before porting. No active probe has been implemented or run.

Run offline checks with `python3 -m unittest discover -s tests -v`. The current suite has 14 tests for metadata privacy and source inventory parsing; it does not validate biometric support.

## Licensing

Project-authored code and documentation are licensed under **LGPL-2.1-or-later**; see [LICENSE](LICENSE). This matches the inspected upstream VFS7552 driver's license. Third-party materials retain their own terms. The Dell package and its INF are not redistributed. No upstream driver code has been copied into this project.

Independent project, unaffiliated with Dell, Validity or Synaptics.
