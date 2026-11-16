# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_capture_chunks import inspect


def chunk(kind, data):
    return struct.pack('<HH', kind, len(data))+data


class CaptureChunksTests(unittest.TestCase):
    def test_multiple_chunks_and_output_omits_types_and_contents(self):
        a = inspect(chunk(0x29, b'secret')+chunk(0x2f, b'ab'))
        b = inspect(chunk(0xffff, b'xxxxxx')+chunk(0, b'yz'))
        self.assertEqual(a, b)
        self.assertEqual((a['chunk_count'], a['content_bytes'], a['total_bytes']), (2, 8, 16))

    def test_zero_length_and_duplicate_types_preserved_as_counts(self):
        out = inspect(chunk(0, b'')+chunk(0, b'')+chunk(0, b'x'))
        self.assertEqual((out['chunk_count'], out['zero_length_chunks']), (3, 2))

    def test_truncated_single_chunk_rejected_at_every_position(self):
        data = chunk(1, b'12345678')
        for size in range(len(data)):
            with self.assertRaises(ValueError):
                inspect(data[:size])

    def test_incomplete_header_after_valid_chunk_rejected(self):
        for size in (1, 2, 3):
            with self.assertRaises(ValueError):
                inspect(chunk(1, b'x')+bytes(size))

    def test_little_endian_size_and_oversized_declaration(self):
        self.assertEqual(inspect(chunk(1, bytes(256)))['content_bytes'], 256)
        with self.assertRaises(ValueError):
            inspect(struct.pack('<HH', 1, 65535)+b'x')

    def test_budget_and_input_types(self):
        self.assertEqual(inspect(chunk(1, bytes(65532)))['total_bytes'], 65536)
        for data in (chunk(1, bytes(65533)), bytearray(4), None, ''):
            with self.assertRaises(ValueError):
                inspect(data)
