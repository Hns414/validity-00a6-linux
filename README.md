# Validity 00A6 Linux

Open-source research toward Linux support for the Validity USB fingerprint reader **138a:00a6**, found in the Dell Latitude 3490.

**Research only: no functional driver, enrollment or authentication support yet.**

## Scope

Identify the hardware and protocol, evaluate existing drivers, then pursue a userspace libfprint implementation and fprintd integration. A kernel module is not an established requirement. The commercial sensor model remains unverified; VFS7552 is a hypothesis, not a compatibility claim.

## Current findings

- The supplied hardware report describes revision 1.64, USB full speed, a vendor-specific interface and five endpoints. Descriptors have not been independently captured here.
- The official libfprint development device list consulted on 2026-11-16 does not list 138a:00a6; it associates VFS7552 with 138a:0091.
- python-validity's inspected USB device table does not contain 138a:00a6.
- Dell package NKXR6 lists Latitude 3490 compatibility, but its INF has not been inspected.

See [hardware](docs/hardware.md), [research and sources](docs/research.md), [milestones](docs/roadmap.md), and [test plan](tests/README.md). Working documentation is in Portuguese; this public overview is in English.

## Getting started

There is nothing to install yet. Read the research log and contribute sanitized hardware metadata or source-backed findings. Do not add this USB ID to another driver's table as a substitute for protocol validation.

## Development and versioning

Small, reviewable commits on main; experimental work on topic branches. The initial research baseline is tagged `v0.1.0-research`; this denotes documentation maturity, not driver capability. Future versions will state exactly which hardware operations were tested.

## Contributions and security

Read [CONTRIBUTING](CONTRIBUTING.md) and [SECURITY](SECURITY.md). Keep biometric samples, unique identifiers, keys, proprietary firmware and binaries out of Git. Do not change PAM or use experiments for login.

## Licensing

No license has been selected yet. Public visibility alone does not grant an open-source license. This is intended to become an open-source driver project; select and publish an upstream-compatible license before accepting code contributions. No third-party code is included in this baseline.

Independent project, unaffiliated with Dell, Validity or Synaptics.
