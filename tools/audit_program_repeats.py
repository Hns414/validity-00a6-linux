#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Audit one candidate repeat patch offline; no mutation, payload output or USB."""
import struct
from inspect_capture_chunks import inspect as inspect_chunks


def audit(program, factor, increment_address=False, preserve_counter=False):
    if type(factor) is not int or not 0 <= factor <= 255:
        raise ValueError('Factor outside modeled scope')
    if type(increment_address) is not bool or type(preserve_counter) is not bool:
        raise ValueError('Flags must be booleans')
    inspect_chunks(program)
    selected = {}
    offset = 0
    while offset < len(program):
        kind, size = struct.unpack_from('<HH', program, offset)
        offset += 4
        if kind in (0x2f, 0x34):
            if kind in selected:
                raise ValueError('Ambiguous candidate chunk')
            selected[kind] = program[offset:offset+size]
        offset += size
    if set(selected) != {0x2f, 0x34} or len(selected[0x2f]) != 4:
        raise ValueError('Outside strict candidate scope')
    multiplier = max(1, factor)
    code = selected[0x34]
    cursor = sites = count_overflows = address_overflows = 0
    while len(code)-cursor >= 3:
        opcode = code[cursor]
        if opcode & 0xf8 == 0x10:
            count = code[cursor+2]
            if count > 1:
                sites += 1
                count_overflows += count*multiplier > 255
                address_overflows += increment_address and code[cursor+1] == 255
            cursor += 3
        elif opcode == 0:
            cursor += 1
        elif opcode == 7:
            cursor += 2
        else:
            break
    counter = struct.unpack('<I', selected[0x2f])[0]
    return {'schema_version': 1, 'model': 'candidate-repeat-patch-impact',
            'effective_multiplier': multiplier, 'eligible_repeat_sites': sites,
            'repeat_byte_overflow_sites': count_overflows,
            'address_byte_overflow_sites': address_overflows,
            'counter_u32_overflow': not preserve_counter and counter*multiplier > 0xffffffff,
            'inspected_prefix_bytes': cursor, 'uninspected_bytes': len(code)-cursor,
            'program_modified': False, 'hardware_validated': False}
