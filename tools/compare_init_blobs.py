#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Compare pinned public init literals offline. Never import upstream Python or use USB."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

# Sibling module is original project tooling, not code from the source being analyzed.
from analyze_vfs7552 import parse_arrays

LIBFPRINT = '8b6e4e39bee58de2774222e3730269def470b157'
VALIDITY91 = '75f38a615ef1560829f9cd8aa07459d10f0962ae'
PYTHON_VALIDITY = 'a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920'


def literal_hex(node):
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        raise ValueError('Hex data must be a literal string')
    if not re.fullmatch(r'[0-9a-fA-F\s]*', node.value):
        raise ValueError('Invalid hex literal')
    return bytes.fromhex(''.join(node.value.split()))


def unhex_assignments(source, include_write_enable=False):
    result = {}
    selected = {'init_hardcoded', 'init_hardcoded_clean_slate', 'reset_blob'}
    if include_write_enable:
        selected.add('db_write_enable')
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name) and t.id in selected]
        if not names:
            continue
        if len(node.targets) != 1 or len(names) != 1 or names[0] in result:
            raise ValueError('Unsupported or duplicate blob assignment')
        call = node.value
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                and call.func.id == 'unhex' and len(call.args) == 1 and not call.keywords):
            raise ValueError('Unsupported blob initializer')
        result[names[0]] = literal_hex(call.args[0])
    if not result:
        raise ValueError('No selected blob assignments')
    return result


def message_bytes(node):
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == 'array' and len(node.args) == 2 and not node.keywords
            and isinstance(node.args[0], ast.Constant) and node.args[0].value == 'B'):
        raise ValueError('Unsupported query array')
    data = node.args[1]
    if isinstance(data, ast.List):
        values = []
        for item in data.elts:
            if not isinstance(item, ast.Constant) or type(item.value) is not int or not 0 <= item.value <= 255:
                raise ValueError('Query byte is not a literal')
            values.append(item.value)
        return bytes(values)
    if (isinstance(data, ast.Call) and isinstance(data.func, ast.Attribute)
            and isinstance(data.func.value, ast.Name) and data.func.value.id == 'bytes'
            and data.func.attr == 'fromhex' and len(data.args) == 1 and not data.keywords):
        return literal_hex(data.args[0])
    raise ValueError('Unsupported query data')


def validity91_messages(source):
    messages = []
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            continue
        append = node.value
        if not (isinstance(append.func, ast.Attribute) and append.func.attr == 'append'
                and isinstance(append.func.value, ast.Name) and append.func.value.id == 'init_messages'):
            continue
        if len(append.args) != 1 or append.keywords:
            raise ValueError('Unsupported message append')
        call = append.args[0]
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                and call.func.id == 'Validity_Messages' and not call.args):
            raise ValueError('Unsupported message constructor')
        keywords = {}
        for kw in call.keywords:
            if kw.arg is None or kw.arg in keywords:
                raise ValueError('Unsupported keyword')
            keywords[kw.arg] = kw.value
        optional = keywords.get('optional', ast.Constant(False))
        if not isinstance(optional, ast.Constant) or type(optional.value) is not bool:
            raise ValueError('Optional flag is not literal')
        messages.append({'data': message_bytes(keywords['query']), 'optional_declared': optional.value})
    if not messages:
        raise ValueError('No init messages')
    return messages


def common_prefix(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def metadata(data):
    return {'length': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def pinned(repo, commit, path):
    return subprocess.run(['git', '-C', str(repo), 'show', f'{commit}:{path}'],
                          check=True, capture_output=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('libfprint', type=Path)
    parser.add_argument('validity91', type=Path)
    parser.add_argument('python_validity', type=Path)
    parser.add_argument('--include-write-enable', action='store_true',
                        help='Include a distinct opaque write-enable literal; does not execute it')
    args = parser.parse_args()
    try:
        header = pinned(args.libfprint, LIBFPRINT, 'libfprint/drivers/vfs7552_proto.h')
        v91 = pinned(args.validity91, VALIDITY91, 'validity91.py')
        arrays = parse_arrays(header.decode())
        target = arrays['vfs7552_init_00']
        report = {'schema_version': 1, 'scope': 'offline-byte-comparison-not-command-semantics',
                  'libfprint': {'commit': LIBFPRINT, 'init_00': metadata(target),
                               'init_04': metadata(arrays['vfs7552_init_04'])},
                  'validity91': {'commit': VALIDITY91, 'messages': []},
                  'python_validity': {'commit': PYTHON_VALIDITY, 'device_blobs': {}}}
        for i, item in enumerate(validity91_messages(v91.decode())):
            data = item['data']
            report['validity91']['messages'].append({
                'index': i, **metadata(data), 'optional_declared': item['optional_declared'],
                'equals_init_00': data == target, 'equals_init_04': data == arrays['vfs7552_init_04']})
        if args.include_write_enable:
            report['schema_version'] = 2
            report['init_vs_write_enable'] = {}
        for model in ['90', '97', '9a', '9d']:
            source = pinned(args.python_validity, PYTHON_VALIDITY, f'validitysensor/blobs_{model}.py')
            result = {}
            blobs = unhex_assignments(source.decode(), args.include_write_enable)
            for name, data in blobs.items():
                result[name] = {**metadata(data), 'equals_init_00': data == target,
                                'common_prefix_bytes_with_init_00': common_prefix(target, data)}
            report['python_validity']['device_blobs'][model] = result
            if args.include_write_enable:
                init, write = blobs['init_hardcoded'], blobs['db_write_enable']
                report['init_vs_write_enable'][model] = {
                    'identical': init == write,
                    'common_prefix_bytes': common_prefix(init, write),
                    'same_five_byte_prefix': len(init) >= 5 and len(write) >= 5 and init[:5] == write[:5],
                    'write_enable_body_after_five_bytes_multiple_of_16':
                        len(write) >= 5 and (len(write)-5) % 16 == 0}
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.CalledProcessError):
        print('Unable to compare pinned init literals.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
