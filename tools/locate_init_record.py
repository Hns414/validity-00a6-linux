#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Locate one known init descriptor in the pinned Dell DLL without executing it."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

from analyze_vfs7552 import parse_arrays, read_pinned, HEADER
from survey_vendor_dll import pe_sections, locations

DELL_SHA256 = '6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7'


def rva_at(offset, size, sections):
    matches = [s for s in sections if s['raw_offset'] <= offset
               and offset+size <= s['raw_offset']+s['raw_size']]
    if len(matches) != 1:
        raise ValueError('Ambiguous or unmapped range')
    section = matches[0]
    return section['rva']+offset-section['raw_offset']


def locate(data, arguments, base, sections):
    if len(arguments) != 500:
        raise ValueError('Expected the known 500-byte reference arguments')
    matches = locations(data, arguments)
    if len(matches) != 1:
        raise ValueError('Expected unique arguments')
    payload_offset = matches[0]
    payload_rva = rva_at(payload_offset, len(arguments), sections)
    refs = locations(data, struct.pack('<Q', base+payload_rva))
    if len(refs) != 1:
        raise ValueError('Expected unique pointer to arguments')
    pointer_offset = refs[0]
    # Offsets come from static inspection of the hash-pinned selector/consumer.
    record_offset = pointer_offset-0x48
    if record_offset < 0 or record_offset+0x50 > len(data):
        raise ValueError('Truncated descriptor')
    record_rva = rva_at(record_offset, 0x50, sections)
    def word(offset):
        return struct.unpack_from('<I', data, record_offset+offset)[0]
    if word(0x44) != len(arguments):
        raise ValueError('Descriptor size does not match reference')
    record_refs = locations(data, struct.pack('<Q', base+record_rva))
    if not record_refs:
        raise ValueError('Descriptor has no static pointer reference')
    return {
        'record_rva': hex(record_rva), 'record_size_bytes': 0x50,
        'payload_rva': hex(payload_rva), 'payload_size_bytes': word(0x44),
        'payload_pointer_field_offset': '0x48',
        'candidate_metadata_keys': {'major': word(0x10), 'minor': word(0x14), 'build': word(0x18)},
        'required_mask_field_2c': hex(word(0x2c)),
        'unresolved_selector_field_3c': word(0x3c),
        'unresolved_parameter_field_20': word(0x20),
        'record_pointer_reference_rvas': [hex(rva_at(o, 8, sections)) for o in record_refs],
        'selection_evaluated': False, 'hardware_execution_allowed': False,
    }


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
        arrays = parse_arrays(read_pinned(args.libfprint_checkout, HEADER).decode())
        base, sections = pe_sections(data)
        result = locate(data, arrays['vfs7552_init_00'][1:], base, sections)
        print(json.dumps({'schema_version': 1, 'method': 'static-known-descriptor-location',
                          'dll_sha256': DELL_SHA256, 'descriptor': result,
                          'limit': 'Keys matching E1 do not establish all selector conditions or payload effects.'},
                         sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError, KeyError):
        print('Unable to locate the pinned init descriptor.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
