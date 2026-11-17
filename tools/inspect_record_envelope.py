#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Count candidate 3/3 record envelopes offline; no decryption or USB."""
import argparse
import json
from pathlib import Path
import sys

ANALYSIS_LIMIT = 65536


def inspect(data):
    """Strict scope: complete nonempty records, known types, no tail markers."""
    if not isinstance(data, bytes) or not 6 <= len(data) <= ANALYSIS_LIMIT:
        raise ValueError('Invalid envelope size')
    pos = records = applications = content_bytes = 0
    while pos < len(data):
        if len(data)-pos < 5:
            raise ValueError('Truncated envelope')
        kind = data[pos]
        count = int.from_bytes(data[pos+3:pos+5], 'big')
        if kind not in (0x14, 0x15, 0x16, 0x17) or data[pos+1:pos+3] != b'\x03\x03':
            raise ValueError('Unsupported envelope')
        if not count or count > len(data)-pos-5:
            raise ValueError('Invalid envelope length')
        records += 1
        applications += kind == 0x17
        content_bytes += count
        pos += 5+count
    return {'schema_version': 1, 'model': 'candidate-3-3-record-envelopes',
            'envelope_bytes': len(data), 'record_count': records,
            'application_record_count': applications, 'content_bytes': content_bytes,
            'single_application_envelope': records == applications == 1,
            'cryptographically_validated': False, 'hardware_validated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('envelope_file', type=Path)
    args = parser.parse_args()
    try:
        with args.envelope_file.open('rb') as stream:
            data = stream.read(ANALYSIS_LIMIT+1)
        print(json.dumps(inspect(data), sort_keys=True, indent=2))
        return 0
    except (ValueError, OSError):
        print('Unable to inspect an envelope within the strict candidate scope.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
