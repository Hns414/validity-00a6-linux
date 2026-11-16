#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Inspect only sizes of a candidate command-02 body offline; never USB."""
import argparse
import json
from pathlib import Path
import struct
import sys

ANALYSIS_LIMIT = 65536


def inspect(data):
    """Strict candidate scope: signature, word count, exactly count*4 bytes."""
    if not isinstance(data, bytes) or not 8 <= len(data) <= ANALYSIS_LIMIT:
        raise ValueError('Invalid candidate size')
    signature, count = struct.unpack_from('<II', data)
    if signature != 0x30000288 or count > (len(data)-8)//4 or 8+count*4 != len(data):
        raise ValueError('Invalid candidate structure')
    return {'schema_version': 1, 'model': 'candidate-command-02-body',
            'body_bytes': len(data), 'word_count': count, 'word_bytes': count*4,
            'hardware_validated': False, 'content_semantics_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('body_file', type=Path)
    args = parser.parse_args()
    try:
        with args.body_file.open('rb') as stream:
            data = stream.read(ANALYSIS_LIMIT+1)
        print(json.dumps(inspect(data), sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError):
        print('Unable to inspect a body within the strict candidate scope.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
