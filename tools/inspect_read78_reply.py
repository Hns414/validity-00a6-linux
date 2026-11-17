#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Inspect sizes of a candidate command-78 body offline; never USB."""
import argparse
import json
from pathlib import Path
import struct
import sys

ANALYSIS_LIMIT = 65536


def inspect(data, *, capacity=None):
    """Strict local scope: LE length followed by exactly that many bytes."""
    if capacity is not None and (type(capacity) is not int or not 0 <= capacity <= ANALYSIS_LIMIT-4):
        raise ValueError('Invalid destination capacity')
    if not isinstance(data, bytes) or not 4 <= len(data) <= ANALYSIS_LIMIT:
        raise ValueError('Invalid candidate size')
    count = struct.unpack_from('<I', data)[0]
    if count != len(data)-4 or (capacity is not None and count > capacity):
        raise ValueError('Invalid candidate structure')
    return {'schema_version': 1, 'model': 'candidate-command-78-body',
            'body_bytes': len(data), 'content_bytes': count,
            'hardware_validated': False, 'content_semantics_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('body_file', type=Path)
    parser.add_argument('--capacity', type=int, help='Explicit destination capacity in bytes')
    args = parser.parse_args()
    try:
        with args.body_file.open('rb') as stream:
            data = stream.read(ANALYSIS_LIMIT+1)
        print(json.dumps(inspect(data, capacity=args.capacity), sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError):
        print('Unable to inspect a body within the strict candidate scope.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
