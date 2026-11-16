#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Count bounded candidate type/length chunks offline without exposing contents."""
import argparse
import json
from pathlib import Path
import struct
import sys

ANALYSIS_LIMIT = 65536


def inspect(data):
    if not isinstance(data, bytes) or not 4 <= len(data) <= ANALYSIS_LIMIT:
        raise ValueError('Invalid candidate size')
    offset = count = payload = zero_length = 0
    while offset < len(data):
        if len(data)-offset < 4:
            raise ValueError('Incomplete header')
        _, size = struct.unpack_from('<HH', data, offset)
        offset += 4
        if size > len(data)-offset:
            raise ValueError('Incomplete content')
        offset += size
        count += 1
        payload += size
        zero_length += size == 0
    return {'schema_version': 1, 'model': 'candidate-type-length-chunks',
            'total_bytes': len(data), 'chunk_count': count,
            'content_bytes': payload, 'zero_length_chunks': zero_length,
            'hardware_validated': False, 'content_semantics_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('chunks_file', type=Path)
    args = parser.parse_args()
    try:
        with args.chunks_file.open('rb') as stream:
            data = stream.read(ANALYSIS_LIMIT+1)
        print(json.dumps(inspect(data), sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError):
        print('Unable to inspect chunks within the strict candidate scope.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
