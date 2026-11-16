#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Read allowlisted numeric metadata from cached Linux sysfs; no USB I/O."""
import json
from pathlib import Path
import re
import sys

DEVICE_HEX = ('idVendor', 'idProduct', 'bcdDevice', 'bDeviceClass',
              'bDeviceSubClass', 'bDeviceProtocol')
DEVICE_DEC = ('bNumConfigurations', 'bNumInterfaces')
INTERFACE_HEX = ('bInterfaceNumber', 'bInterfaceClass',
                 'bInterfaceSubClass', 'bInterfaceProtocol')
INTERFACE_DEC = ('bAlternateSetting',)
ENDPOINT_HEX = ('bEndpointAddress', 'bmAttributes', 'wMaxPacketSize', 'bInterval')


def number(path, base):
    text = path.read_text(encoding='ascii').strip()
    pattern = r'[0-9a-fA-F]{1,8}' if base == 16 else r'[0-9]{1,8}'
    if not re.fullmatch(pattern, text):
        raise ValueError('Invalid numeric metadata')
    return int(text, base)


def fields(path, hex_keys=(), dec_keys=()):
    result = {}
    for keys, base in ((hex_keys, 16), (dec_keys, 10)):
        for key in keys:
            if (path / key).exists():
                result[key] = number(path / key, base)
    return result


def collect(root=Path('/sys/bus/usb/devices')):
    """Never emit topology paths, string descriptors, serials or environment data."""
    devices = []
    for path in sorted(root.iterdir()):
        if not (path / 'idVendor').exists() or not (path / 'idProduct').exists():
            continue
        if (number(path / 'idVendor', 16), number(path / 'idProduct', 16)) != (0x138a, 0x00a6):
            continue
        device = fields(path, DEVICE_HEX, DEVICE_DEC)
        if (path / 'speed').exists():
            device['speed_mbps'] = number(path / 'speed', 10)
        if (path / 'version').exists():
            version = (path / 'version').read_text(encoding='ascii').strip()
            if not re.fullmatch(r'[0-9]\.[0-9]{2}', version):
                raise ValueError('Invalid USB version')
            device['usb_version'] = version
        device['interfaces'] = []
        for interface in sorted(path.glob('*:*')):
            if not (interface / 'bInterfaceNumber').exists():
                continue
            # Linux exposes bNumEndpoints as hexadecimal (e.g. 0a).
            item = fields(interface, INTERFACE_HEX + ('bNumEndpoints',), INTERFACE_DEC)
            item['endpoints'] = [fields(ep, ENDPOINT_HEX)
                                 for ep in sorted(interface.glob('ep_*'))]
            device['interfaces'].append(item)
        devices.append(device)
    return {'schema_version': 1, 'source': 'linux-sysfs-cached-metadata', 'devices': devices}


def main():
    try:
        result = collect()
        if not result['devices']:
            print('Target 138a:00a6 not found in sysfs.', file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, UnicodeError):
        # Exceptions may contain local paths or source contents; suppress them.
        print('Unable to read valid target metadata from sysfs.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
