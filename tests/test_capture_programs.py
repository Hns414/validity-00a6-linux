# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from compare_capture_programs import assemble, public_programs

BASE = 0x180000000
SECTIONS = [{'rva': 0x1000, 'raw_offset': 0, 'raw_size': 4096}]


def fixture():
    data = bytearray(4096)
    struct.pack_into('<Q', data, 0x134, BASE+0x1200)
    struct.pack_into('<HQ', data, 0x200, 3, BASE+0x1800)
    struct.pack_into('<HQ', data, 0x20a, 2, BASE+0x1900)
    data[0x800:0x803] = b'abc'
    data[0x900:0x902] = b'de'
    return data


class CaptureProgramsTests(unittest.TestCase):
    def test_packed_fragments_preserve_order(self):
        self.assertEqual(assemble(bytes(fixture()), 0x1100, BASE, SECTIONS), (b'abcde', 2))

    def test_out_of_section_pointer_and_truncated_input_rejected(self):
        data = fixture()
        struct.pack_into('<Q', data, 0x202, BASE+0x3000)
        with self.assertRaises(ValueError):
            assemble(bytes(data), 0x1100, BASE, SECTIONS)
        with self.assertRaises(ValueError):
            assemble(bytes(fixture()[:0x802]), 0x1100, BASE, SECTIONS)

    def test_zero_size_and_inconsistent_terminator_rejected(self):
        for offset, size, address in ((0x200, 0, BASE+0x1800), (0x214, 1, 0), (0x200, 0, 0)):
            data = fixture()
            struct.pack_into('<HQ', data, offset, size, address)
            with self.assertRaises(ValueError):
                assemble(bytes(data), 0x1100, BASE, SECTIONS)

    def test_missing_terminator_is_bounded(self):
        data = fixture()
        for i in range(64):
            struct.pack_into('<HQ', data, 0x200+10*i, 1, BASE+0x1800)
        with self.assertRaises(ValueError):
            assemble(bytes(data), 0x1100, BASE, SECTIONS)

    def test_public_literal_extraction_without_importing(self):
        source = "SensorCaptureProg(major=6, minor=7, build=0, u1=0, dev_type=219, a0=24, a1=25, blobs=['6162', '63'])"
        self.assertEqual(public_programs(source), [b'abc'])

    def test_public_dynamic_duplicate_and_bad_fields_rejected(self):
        prefix = 'SensorCaptureProg(major=6, minor=7, build=0, u1=0, dev_type=219, a0=24, a1=25, '
        for source in (prefix+"blobs=[str(1)])", prefix+"blobs=['zz'])", prefix+"blobs=[], a0=2)", prefix+"blobs=make())", 'pass'):
            with self.assertRaises((ValueError, SyntaxError)):
                public_programs(source)
