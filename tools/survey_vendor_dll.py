#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Read-only PE32+ survey. Never load DLLs, extract payloads or access USB."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

from analyze_vfs7552 import parse_arrays, read_pinned, HEADER, UPSTREAM_COMMIT

LABELS = ('CBiometricDevice::deviceInit', 'CeivMode::SetPayloadData', 'CeivMode::GetPayloadData')


def pe_sections(data):
    def read(fmt, offset):
        if offset < 0 or offset + struct.calcsize(fmt) > len(data):
            raise ValueError('Truncated PE')
        return struct.unpack_from(fmt, data, offset)
    if data[:2] != b'MZ':
        raise ValueError('Not PE')
    pe, = read('<I', 0x3c)
    if data[pe:pe+4] != b'PE\0\0':
        raise ValueError('Not PE')
    machine, count = read('<HH', pe+4)
    optional_size, = read('<H', pe+20)
    optional = pe+24
    if machine != 0x8664 or not 1 <= count <= 96 or optional_size < 112:
        raise ValueError('Unsupported PE')
    magic, = read('<H', optional)
    image_base, = read('<Q', optional+24)
    table = optional+optional_size
    if magic != 0x20b or table+40*count > len(data):
        raise ValueError('Unsupported PE32+ header')
    sections = []
    for i in range(count):
        offset = table+40*i
        virtual_size, rva, size, raw = read('<IIII', offset+8)
        if raw+size > len(data):
            raise ValueError('Section beyond file')
        sections.append({'rva': rva, 'virtual_size': virtual_size, 'raw_offset': raw, 'raw_size': size})
    return image_base, sections


def locations(data, needle):
    if not needle:
        raise ValueError('Empty needle')
    result = []
    pos = 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            return result
        result.append(pos)
        pos += 1


def survey(data, needles):
    base, sections = pe_sections(data)
    result = {'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
              'format': 'PE32+ AMD64', 'image_base': hex(base),
              'exact_literal_occurrences': {name: len(locations(data, value)) for name, value in needles.items()},
              'diagnostic_string_anchors': [], 'matched_literal_locations': []}
    for name, needle in needles.items():
        for offset in locations(data, needle):
            covering = [s for s in sections if s['raw_offset'] <= offset
                        and offset+len(needle) <= s['raw_offset']+s['raw_size']]
            if len(covering) != 1:
                raise ValueError('Ambiguous or unmapped literal')
            result['matched_literal_locations'].append({
                'reference_name': name, 'length': len(needle), 'file_offset': hex(offset),
                'rva': hex(covering[0]['rva']+offset-covering[0]['raw_offset'])})
    for label in LABELS:
        for offset in locations(data, label.encode('ascii')+b'\0'):
            covering = [s for s in sections if s['raw_offset'] <= offset < s['raw_offset']+s['raw_size']]
            if len(covering) != 1:
                raise ValueError('Ambiguous or unmapped anchor')
            rva = covering[0]['rva']+offset-covering[0]['raw_offset']
            result['diagnostic_string_anchors'].append({'label': label, 'string_rva': hex(rva),
                                                         'string_va': hex(base+rva)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('libfprint_checkout', type=Path)
    parser.add_argument('dll', type=Path, nargs='+')
    args = parser.parse_args()
    try:
        arrays = parse_arrays(read_pinned(args.libfprint_checkout, HEADER).decode())
        needles = {n: arrays[n] for n in ['vfs7552_init_00', 'vfs7552_init_04']}
        for name in ['vfs7552_init_00', 'vfs7552_init_04']:
            needles[name+'_without_opcode'] = arrays[name][1:]
            needles[name+'_after_five_byte_prefix'] = arrays[name][5:]
        needles['shared_envelope_prefix'] = bytes.fromhex('0602000001')
        results = []
        for path in args.dll:
            if path.stat().st_size > 64 * 1024 * 1024:
                raise ValueError('File too large')
            results.append({'file_name': path.name, **survey(path.read_bytes(), needles)})
        print(json.dumps({'schema_version': 1, 'method': 'static-read-only-no-code-execution',
                          'upstream_reference_commit': UPSTREAM_COMMIT, 'files': results,
                          'limit': 'No exact contiguous match does not prove absence of generated or transformed payloads.'},
                         indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError):
        print('Unable to survey PE files.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
