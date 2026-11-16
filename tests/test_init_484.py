# SPDX-License-Identifier: LGPL-2.1-or-later
import hashlib
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import verify_init_484 as verifier


class Init484Tests(unittest.TestCase):
    def setUp(self):
        self.base = 0x180000000
        self.sections = [{'rva': 0x110000, 'raw_offset': 0,
                          'raw_size': 0x60000}]
        self.data = bytearray(0x60000)
        self.reference = b'\x06'+bytes(i % 251 for i in range(484))
        self.record = 0x13d490-0x110000
        for field, value in [(0x10, 6), (0x14, 7), (0x18, 164), (0x2c, 0x4000),
                             (0x34, 2), (0x3c, 1), (0x44, 484)]:
            struct.pack_into('<I', self.data, self.record+field, value)
        struct.pack_into('<Q', self.data, self.record+0x48, self.base+0x15f000)
        struct.pack_into('<Q', self.data, 0x13dad0+55*8-0x110000, self.base+0x13d490)
        struct.pack_into('<Q', self.data, 0x116340+7*8-0x110000, self.base+0x7e540)
        self.data[0x4f000:0x4f000+484] = self.reference[1:]

    def inspect(self):
        return verifier.inspect(bytes(self.data), self.reference, self.base, self.sections)

    def test_exact_identity_exports_only_metadata(self):
        result = self.inspect()
        self.assertEqual(result['frame_sha256'], hashlib.sha256(self.reference).hexdigest())
        self.assertEqual(result['frame_length'], 485)
        self.assertFalse(result['full_selection_evaluated'])
        self.assertFalse(result['hardware_execution_enabled'])
        self.assertTrue(all(type(v) in (str, int, bool) for v in result.values()))
        self.assertNotIn('payload', result)

    def test_common_prefix_does_not_hide_tail_mismatch(self):
        self.data[0x4f000+483] ^= 1
        with self.assertRaises(ValueError):
            self.inspect()

    def test_malformed_public_reference_rejected(self):
        for reference in (b'', b'\x06'+bytes(500), b'\x07'+self.reference[1:]):
            with self.subTest(length=len(reference)), self.assertRaises(ValueError):
                verifier.inspect(bytes(self.data), reference, self.base, self.sections)

    def test_changed_descriptor_fields_rejected(self):
        for field in (0x10, 0x14, 0x18, 0x2c, 0x34, 0x3c, 0x44):
            old = self.data[self.record+field]
            self.data[self.record+field] ^= 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.inspect()
            self.data[self.record+field] = old

    def test_table_and_dispatch_binding_checked(self):
        for rva in (0x13dad0+55*8, 0x116340+7*8):
            offset = rva-0x110000
            self.data[offset] ^= 1
            with self.subTest(rva=rva), self.assertRaises(ValueError):
                self.inspect()
            self.data[offset] ^= 1

    def test_pointer_outside_section_and_truncated_file_rejected(self):
        struct.pack_into('<Q', self.data, self.record+0x48, self.base+0x16ffff)
        with self.assertRaises(ValueError):
            self.inspect()
        struct.pack_into('<Q', self.data, self.record+0x48, self.base+0x15f000)
        self.data = self.data[:0x4f100]
        with self.assertRaises(ValueError):
            self.inspect()
