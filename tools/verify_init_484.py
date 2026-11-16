#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Verify the pinned 484-byte descriptor against a public literal; no USB or execution."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

from compare_init_blobs import PYTHON_VALIDITY, unhex_assignments, pinned
from locate_init_record import DELL_SHA256
from survey_vendor_dll import pe_sections
from verify_init_frame import file_at


def inspect(data, reference, base, sections):
    def mapped(rva, size):
        offset = file_at(rva, size, sections)
        if offset < 0 or offset+size > len(data):
            raise ValueError('Truncated mapped range')
        return offset

    if len(reference) != 485 or reference[0] != 6:
        raise ValueError('Unexpected public frame')
    record = 0x13d490
    offset = mapped(record, 0x50)
    for field, expected in [(0x10, 6), (0x14, 7), (0x18, 164),
                            (0x2c, 0x4000), (0x34, 2), (0x3c, 1), (0x44, 484)]:
        if struct.unpack_from('<I', data, offset+field)[0] != expected:
            raise ValueError('Unexpected descriptor field')
    pointer = struct.unpack_from('<Q', data, mapped(0x13dad0+55*8, 8))[0]
    if pointer != base+record:
        raise ValueError('Unexpected table entry')
    handler = struct.unpack_from('<Q', data, mapped(0x116340+7*8, 8))[0]
    if handler != base+0x7e540:
        raise ValueError('Unexpected dispatch target')
    payload = struct.unpack_from('<Q', data, offset+0x48)[0]-base
    start = mapped(payload, 484)
    arguments = data[start:start+484]
    frame = b'\x06'+arguments
    if frame != reference:
        raise ValueError('Public reference mismatch')
    return {'record_rva': hex(record), 'table_index': 55, 'arguments_length': 484,
            'frame_length': len(frame), 'frame_sha256': hashlib.sha256(frame).hexdigest(),
            'arguments_sha256': hashlib.sha256(arguments).hexdigest(),
            'equals_public_init_hardcoded': True, 'full_selection_evaluated': False,
            'hardware_execution_enabled': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('python_validity_checkout', type=Path)
    parser.add_argument('dll', type=Path)
    args = parser.parse_args()
    try:
        if args.dll.stat().st_size != 2296920:
            raise ValueError('Unexpected DLL size')
        data = args.dll.read_bytes()
        if hashlib.sha256(data).hexdigest() != DELL_SHA256:
            raise ValueError('Unexpected DLL hash')
        source = pinned(args.python_validity_checkout, PYTHON_VALIDITY,
                            'validitysensor/blobs_90.py').decode('utf-8')
        reference = unhex_assignments(source)['init_hardcoded']
        base, sections = pe_sections(data)
        result = inspect(data, reference, base, sections)
        result.update(schema_version=1, method='offline-known-484-byte-descriptor-comparison',
                      dll_sha256=DELL_SHA256, public_reference_commit=PYTHON_VALIDITY)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, struct.error, subprocess.CalledProcessError, UnicodeError):
        print('Unable to verify the pinned 484-byte init reference.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
