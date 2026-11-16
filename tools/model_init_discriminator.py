#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Model one static selector predicate; never select or send an init payload."""
import argparse
import json


def discriminator(major, internal_flag_byte):
    """RVA 0x8feb0 model; inputs are internal fields, NOT USB reply offsets."""
    for value in (major, internal_flag_byte):
        if type(value) is not int or not 0 <= value <= 255:
            raise ValueError('Expected integer bytes')
    if major != 6:
        return 0
    return 2 if internal_flag_byte & 0x20 else 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--major', required=True, type=lambda v: int(v, 0))
    parser.add_argument('--internal-flag-byte', required=True,
                        type=lambda v: int(v, 0),
                        help='Synthetic internal structure field; not a raw USB byte offset')
    args = parser.parse_args()
    try:
        value = discriminator(args.major, args.internal_flag_byte)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({'schema_version': 1, 'method': 'offline-single-predicate-model',
                      'discriminator': value, 'full_selection_evaluated': False,
                      'hardware_execution_enabled': False}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
