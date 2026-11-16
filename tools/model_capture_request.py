#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Model candidate command-02 framing sizes offline; no payload or USB access."""
import argparse
import json
import sys

# Project analysis budget, not a discovered sensor protocol limit.
ANALYSIS_LIMIT = 65536


def layout(field_0c, field_00, concatenated_bytes):
    """Model DLL builder fields without assigning biometric semantics."""
    for value, maximum in ((field_0c, 65535), (field_00, 65535),
                           (concatenated_bytes, ANALYSIS_LIMIT)):
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError('Out of analysis scope')
    initial = 5 + concatenated_bytes
    padding = 4 if initial % 64 == 0 else 0
    total = initial + padding
    if total > ANALYSIS_LIMIT:
        raise ValueError('Out of analysis scope')
    return {'schema_version': 1, 'model': 'candidate-command-02-layout',
            'opcode': 2, 'header_bytes': 5, 'field_encoding': 'little-endian-uint16',
            'field_0c': field_0c, 'field_00': field_00,
            'concatenated_bytes': concatenated_bytes,
            'trailing_zero_bytes': padding, 'total_bytes': total,
            'analysis_limit_bytes': ANALYSIS_LIMIT,
            'sensor_limit_verified': False, 'hardware_validated': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('field_0c', type=int)
    parser.add_argument('field_00', type=int)
    parser.add_argument('concatenated_bytes', type=int)
    args = parser.parse_args()
    try:
        print(json.dumps(layout(args.field_0c, args.field_00, args.concatenated_bytes),
                         indent=2, sort_keys=True))
        return 0
    except ValueError:
        print('Values exceed the offline analysis scope.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
