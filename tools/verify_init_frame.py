#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Reconstruct one known frame in memory and emit only comparison metadata. No USB."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

from analyze_vfs7552 import parse_arrays, read_pinned, HEADER, UPSTREAM_COMMIT
from locate_init_record import DELL_SHA256, locate
from survey_vendor_dll import pe_sections


def file_at(rva, size, sections):
    matches = [s for s in sections if s['rva'] <= rva and rva+size <= s['rva']+s['raw_size']]
    if len(matches) != 1:
        raise ValueError('Unmapped RVA')
    return matches[0]['raw_offset']+rva-matches[0]['rva']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('libfprint_checkout', type=Path)
    parser.add_argument('dll', type=Path)
    args = parser.parse_args()
    try:
        if args.dll.stat().st_size != 2296920:
            raise ValueError('Unexpected DLL size')
        data = args.dll.read_bytes()
        if hashlib.sha256(data).hexdigest() != DELL_SHA256:
            raise ValueError('Unexpected DLL hash')
        base, sections = pe_sections(data)
        arrays = parse_arrays(read_pinned(args.libfprint_checkout, HEADER).decode())
        reference = arrays['vfs7552_init_00']
        descriptor = locate(data, reference[1:], base, sections)
        # Static analysis established dispatch index 7 -> handler RVA 0x7e540.
        dispatch_slot_rva = 0x116340+7*8
        handler, = struct.unpack_from('<Q', data, file_at(dispatch_slot_rva, 8, sections))
        if handler != base+0x7e540:
            raise ValueError('Unexpected dispatch target')
        arguments_offset = file_at(int(descriptor['payload_rva'], 16), 500, sections)
        frame = b'\x06'+data[arguments_offset:arguments_offset+500]
        print(json.dumps({
            'schema_version': 1, 'method': 'offline-reconstruction-not-vendor-code-execution',
            'dll_sha256': DELL_SHA256, 'upstream_reference_commit': UPSTREAM_COMMIT,
            'request_index': 7, 'dispatch_slot_rva': hex(dispatch_slot_rva),
            'handler_rva': hex(handler-base), 'opcode': '0x06',
            'arguments_length': 500, 'frame_length': len(frame),
            'frame_sha256': hashlib.sha256(frame).hexdigest(),
            'equals_upstream_init_00': frame == reference,
            'vendor_instruction_semantics_automatically_verified': False,
            'payload_effects_known': False, 'hardware_execution_enabled': False,
        }, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError):
        print('Unable to verify the pinned init frame.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
