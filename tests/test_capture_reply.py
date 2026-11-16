# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import json
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_capture_reply import inspect


def body(count, tail):
    return struct.pack('<II', 0x30000288, count)+tail


class CaptureReplyTests(unittest.TestCase):
    def test_counts_without_exposing_words(self):
        a = inspect(body(2, b'PRIVATE!'))
        b = inspect(body(2, b'OTHER123'))
        self.assertEqual(a, b)
        self.assertEqual((a['word_count'], a['word_bytes'], a['body_bytes']), (2, 8, 16))
        self.assertFalse(a['hardware_validated'])
        self.assertNotIn('PRIVATE', json.dumps(a))

    def test_zero_count_is_structurally_accepted_without_semantic_claim(self):
        self.assertEqual(inspect(body(0, b''))['word_bytes'], 0)

    def test_all_truncations_and_partial_word_rejected(self):
        valid = body(3, bytes(12))
        for size in range(len(valid)):
            with self.assertRaises(ValueError):
                inspect(valid[:size])
        with self.assertRaises(ValueError):
            inspect(body(1, bytes(3)))

    def test_overflow_sized_count_and_extra_tail_rejected(self):
        for count, tail in ((0xffffffff, b''), (0x40000000, b''), (1, bytes(8)), (0, b'x')):
            with self.assertRaises(ValueError):
                inspect(body(count, tail))

    def test_signature_endianness_and_input_type_rejected(self):
        for data in (struct.pack('>II', 0x30000288, 0), bytes(8), bytearray(body(0, b'')), None):
            with self.assertRaises(ValueError):
                inspect(data)

    def test_analysis_budget_boundary(self):
        self.assertEqual(inspect(body(16382, bytes(65528)))['body_bytes'], 65536)
        with self.assertRaises(ValueError):
            inspect(body(16383, bytes(65532)))
