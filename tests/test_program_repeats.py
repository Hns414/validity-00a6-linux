# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_program_repeats import audit


def program(code, counter=1):
    return struct.pack('<HHI', 0x2f, 4, counter)+struct.pack('<HH', 0x34, len(code))+code


class RepeatAuditTests(unittest.TestCase):
    def test_exact_three_byte_instruction_and_no_mutation(self):
        data = program(bytes([0x10, 255, 128]))
        before = bytes(data)
        out = audit(data, 2, True)
        self.assertEqual((out['eligible_repeat_sites'], out['repeat_byte_overflow_sites'], out['address_byte_overflow_sites']), (1, 1, 1))
        self.assertEqual(out['uninspected_bytes'], 0)
        self.assertEqual(data, before)
        self.assertFalse(out['program_modified'])

    def test_repeat_threshold_and_factor_clamp(self):
        data = program(bytes([0x17, 0, 0, 0x10, 0, 1, 0x10, 0, 2]))
        self.assertEqual(audit(data, 0)['eligible_repeat_sites'], 1)
        self.assertEqual(audit(data, 0)['effective_multiplier'], 1)

    def test_boundary_255_and_counter_overflow(self):
        self.assertEqual(audit(program(bytes([0x10, 0, 85])), 3)['repeat_byte_overflow_sites'], 0)
        self.assertEqual(audit(program(bytes([0x10, 0, 86])), 3)['repeat_byte_overflow_sites'], 1)
        self.assertTrue(audit(program(b'', 0xffffffff), 2)['counter_u32_overflow'])
        self.assertFalse(audit(program(b'', 0xffffffff), 2, preserve_counter=True)['counter_u32_overflow'])

    def test_unknown_instruction_stops_prefix_scan(self):
        out = audit(program(bytes([0, 7, 9, 0x10, 0, 2, 1, 0, 0])), 1)
        self.assertEqual((out['inspected_prefix_bytes'], out['uninspected_bytes']), (6, 3))

    def test_missing_duplicate_and_wrong_size_chunks_rejected(self):
        data = program(bytes([0x10, 0, 2]))
        for bad in (b'', data[8:], data+data, struct.pack('<HH', 0x2f, 0)+data[8:]):
            with self.assertRaises(ValueError):
                audit(bad, 1)

    def test_invalid_factor_and_flags_rejected(self):
        for value in (-1, 256, True, 1.5, '2'):
            with self.assertRaises(ValueError):
                audit(program(b''), value)
        with self.assertRaises(ValueError):
            audit(program(b''), 1, increment_address=1)
