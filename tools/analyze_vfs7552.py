#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Inventory pinned upstream C literals offline. Never access USB or execute C."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

UPSTREAM_COMMIT = '8b6e4e39bee58de2774222e3730269def470b157'
DRIVER = 'libfprint/drivers/vfs7552.c'
HEADER = 'libfprint/drivers/vfs7552_proto.h'


def uncomment(source):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', source, flags=re.S)


def parse_arrays(source):
    """Accept only explicit byte literals, rejecting expressions and duplicates."""
    clean = uncomment(source)
    declarations = re.findall(r'static\s+unsigned\s+char\s+(\w+)\s*\[\s*\]\s*=\s*\{([^{}]*)\}\s*;', clean, re.S)
    candidates = re.findall(r'static\s+unsigned\s+char\s+\w+\s*\[', clean)
    if not declarations or len(declarations) != len(candidates):
        raise ValueError('Missing or unsupported byte array declaration')
    arrays = {}
    for name, body in declarations:
        if name in arrays:
            raise ValueError('Duplicate array')
        parts = body.strip().split(',')
        if parts[-1].strip() == '':
            parts.pop()
        data = []
        for part in parts:
            token = part.strip()
            if not re.fullmatch(r'(?:0[xX][0-9a-fA-F]+|0|[1-9][0-9]*)', token):
                raise ValueError('Unsupported byte initializer')
            value = int(token, 16 if token.lower().startswith('0x') else 10)
            if not 0 <= value <= 255:
                raise ValueError('Byte out of range')
            data.append(value)
        if not data:
            raise ValueError('Empty byte array')
        arrays[name] = bytes(data)
    return arrays


def parse_sequences(source, arrays):
    clean = uncomment(source)
    blocks = re.findall(r'struct\s+usb_action\s+(\w+)\s*\[\s*\]\s*=\s*\{([^{}]*)\}\s*;', clean, re.S)
    sequences = {}
    for name, body in blocks:
        if name in sequences:
            raise ValueError('Duplicate sequence')
        actions = []
        pos = 0
        while body[pos:].strip():
            match = re.match(r'\s*(SEND|RECV|RECV_CHECK|RECV_CHECK_SIZE)\s*\(([^()]*)\)\s*', body[pos:])
            if not match:
                raise ValueError('Unsupported sequence action')
            macro, arguments = match.groups()
            args = [arg.strip() for arg in arguments.split(',')]
            expected_count = {'SEND': 2, 'RECV': 2, 'RECV_CHECK': 3, 'RECV_CHECK_SIZE': 3}[macro]
            if len(args) != expected_count or not re.fullmatch(r'VFS7552_[A-Z0-9_]+', args[0]):
                raise ValueError('Invalid action arguments')
            action = {'macro': macro, 'endpoint_symbol': args[0]}
            if macro == 'SEND':
                action['array'] = args[1]
                action['send_bytes'] = len(arrays[args[1]])
            else:
                if not re.fullmatch(r'[1-9][0-9]*', args[1]):
                    raise ValueError('Unsupported receive size')
                action['receive_capacity'] = int(args[1])
                if len(args) == 3:
                    action['expected_array'] = args[2]
                    action['declared_expected_bytes'] = len(arrays[args[2]])
                    if action['declared_expected_bytes'] > action['receive_capacity']:
                        raise ValueError('Expected reply exceeds receive capacity')
            actions.append(action)
            pos += match.end()
        sequences[name] = actions
    if not sequences:
        raise ValueError('No action sequences found')
    return sequences


def analyze(header, driver):
    arrays = parse_arrays(header)
    return {
        'schema_version': 1,
        'scope': 'offline-static-inventory-not-device-validation',
        'arrays': {name: {'length': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                   for name, data in sorted(arrays.items())},
        'sequences': parse_sequences(driver, arrays),
        'notice': 'Macro names and declared sizes do not prove runtime validation; see docs/protocol.md.',
    }


def read_pinned(repository, relative):
    result = subprocess.run(['git', '-C', str(repository), 'show', f'{UPSTREAM_COMMIT}:{relative}'],
                            check=True, capture_output=True)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('upstream_checkout', type=Path, help='Existing libfprint Git checkout containing the pinned commit')
    args = parser.parse_args()
    try:
        header = read_pinned(args.upstream_checkout, HEADER)
        driver = read_pinned(args.upstream_checkout, DRIVER)
        result = analyze(header.decode('utf-8'), driver.decode('utf-8'))
        result['upstream'] = {
            'url': 'https://gitlab.freedesktop.org/libfprint/libfprint',
            'commit': UPSTREAM_COMMIT,
            'files': {HEADER: hashlib.sha256(header).hexdigest(), DRIVER: hashlib.sha256(driver).hexdigest()},
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
        print('Unable to inventory the pinned upstream source.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
