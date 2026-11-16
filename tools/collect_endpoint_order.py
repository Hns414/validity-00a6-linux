#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Inspect cached descriptors for target endpoint order; no USB transfers."""
import json
from pathlib import Path
import sys

from collect_usb_metadata import number


def parse_order(data):
    """Strict scope: USB device descriptor + one config, interface 0/alt 0 only."""
    if len(data) < 27 or len(data) > 65553 or data[:2] != bytes([18, 1]):
        raise ValueError('Unexpected descriptor stream')
    if data[8:12] != bytes.fromhex('8a13a600') or data[17] != 1:
        raise ValueError('Unexpected device')
    if data[18:20] != bytes([9, 2]) or data[22:24] != bytes([1, 1]):
        raise ValueError('Unexpected configuration')
    if int.from_bytes(data[20:22], 'little') != len(data)-18:
        raise ValueError('Configuration length mismatch')
    offset = 27
    interface_seen = False
    expected = None
    endpoints = []
    addresses = set()
    while offset < len(data):
        if offset+2 > len(data):
            raise ValueError('Truncated descriptor header')
        size, kind = data[offset:offset+2]
        if size < 2 or offset+size > len(data):
            raise ValueError('Truncated descriptor')
        item = data[offset:offset+size]
        if kind == 4:
            if size != 9 or interface_seen or item[2:4] != bytes([0, 0]):
                raise ValueError('Unexpected interface')
            interface_seen = True
            expected = item[4]
        elif kind == 5:
            if not interface_seen or size != 7 or item[2] in addresses:
                raise ValueError('Unexpected endpoint')
            address = item[2]
            if address & 0x70 or address & 0x0f == 0:
                raise ValueError('Invalid endpoint address')
            addresses.add(address)
            endpoints.append({'pipe_index': len(endpoints), 'bEndpointAddress': address,
                              'transfer_type': item[3] & 3,
                              'wMaxPacketSize': int.from_bytes(item[4:6], 'little'),
                              'bInterval': item[6]})
        elif kind in (1, 2, 3):
            raise ValueError('Unexpected device/configuration/string descriptor')
        offset += size
    if not interface_seen or len(endpoints) != expected or not endpoints:
        raise ValueError('Endpoint count mismatch')
    return {'configuration_value': 1, 'interface_number': 0,
            'alternate_setting': 0, 'endpoints_in_descriptor_order': endpoints}


def collect(root=Path('/sys/bus/usb/devices')):
    targets = []
    for path in root.iterdir():
        if not (path/'idVendor').exists() or not (path/'idProduct').exists():
            continue
        if (number(path/'idVendor', 16), number(path/'idProduct', 16)) == (0x138a, 0x00a6):
            targets.append(path)
    if len(targets) != 1:
        raise ValueError('Expected one target')
    with (targets[0]/'descriptors').open('rb') as stream:
        data = stream.read(65554)
    return {'schema_version': 1, 'source': 'linux-sysfs-cached-descriptor-order',
            'vendor_id': 0x138a, 'product_id': 0x00a6, 'usb_transfer_performed': False,
            **parse_order(data)}


def main():
    try:
        print(json.dumps(collect(), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, UnicodeError):
        print('Unable to inspect one valid target cached configuration.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
