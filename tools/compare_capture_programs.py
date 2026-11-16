#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Compare pinned capture program fragments offline; export metadata only."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from compare_init_blobs import pinned, PYTHON_VALIDITY, literal_hex
from locate_init_record import DELL_SHA256
from survey_vendor_dll import pe_sections
from verify_init_frame import file_at


def assemble(data, record, base, sections):
    def read(rva, size):
        offset = file_at(rva, size, sections)
        if offset+size > len(data):
            raise ValueError('Truncated mapped data')
        return data[offset:offset+size]
    pointer = struct.unpack('<Q', read(record+0x34, 8))[0]-base
    chunks = []
    total = 0
    for index in range(64):
        size, address = struct.unpack('<HQ', read(pointer+10*index, 10))
        if address == 0:
            if size != 0 or not chunks:
                raise ValueError('Unexpected fragment terminator')
            return b''.join(chunks), len(chunks)
        if not size or total+size > 65536:
            raise ValueError('Fragment exceeds analysis scope')
        chunks.append(read(address-base, size))
        total += size
    raise ValueError('Missing bounded fragment terminator')


def public_programs(source):
    output = []
    names = {'major', 'minor', 'build', 'u1', 'dev_type', 'a0', 'a1', 'blobs'}
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != 'SensorCaptureProg':
            continue
        fields = {kw.arg: kw.value for kw in node.keywords}
        if node.args or len(fields) != len(node.keywords) or set(fields) != names:
            raise ValueError('Unexpected public program initializer')
        for key in names-{'blobs'}:
            value = fields[key]
            if not isinstance(value, ast.Constant) or type(value.value) is not int or not 0 <= value.value <= 0xffff:
                raise ValueError('Nonliteral program field')
        blobs = fields['blobs']
        if not isinstance(blobs, ast.List):
            raise ValueError('Nonliteral fragment list')
        content = b''.join(literal_hex(item) for item in blobs.elts)
        if len(content) > 65536:
            raise ValueError('Public program exceeds analysis budget')
        output.append(content)
    if not output:
        raise ValueError('Missing public programs')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('python_validity_checkout', type=Path)
    parser.add_argument('dll', type=Path)
    args = parser.parse_args()
    try:
        with args.dll.open('rb') as stream:
            data = stream.read(2296921)
        if len(data) != 2296920 or hashlib.sha256(data).hexdigest() != DELL_SHA256:
            raise ValueError('Unexpected DLL')
        base, sections = pe_sections(data)
        source = pinned(args.python_validity_checkout, PYTHON_VALIDITY, 'validitysensor/generated_tables.py')
        references = public_programs(source.decode('utf-8'))
        records = []
        for index in range(22):
            offset = file_at(0x1be890+index*8, 8, sections)
            address = struct.unpack_from('<Q', data, offset)[0]
            if index == 21:
                if address:
                    raise ValueError('Missing expected table terminator')
                break
            if not address:
                raise ValueError('Premature table terminator')
            content, count = assemble(data, address-base, base, sections)
            records.append({'table_index': index, 'record_rva': hex(address-base),
                            'fragment_count': count, 'program_bytes': len(content),
                            'program_sha256': hashlib.sha256(content).hexdigest(),
                            'exact_public_program_indices': [i for i, ref in enumerate(references) if ref == content]})
        print(json.dumps({'schema_version': 1, 'dll_sha256': DELL_SHA256,
                          'public_commit': PYTHON_VALIDITY, 'public_program_count': len(references),
                          'records': records, 'participant_selection_verified': False,
                          'usb_transfer_performed': False}, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, SyntaxError, UnicodeError, struct.error, subprocess.CalledProcessError):
        print('Unable to compare the pinned capture programs.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
