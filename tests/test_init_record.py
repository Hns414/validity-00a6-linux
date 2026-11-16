# SPDX-License-Identifier: LGPL-2.1-or-later
import struct
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
try:
    import locate_init_record as locator
finally:
    sys.path.pop(0)


class InitRecordTests(unittest.TestCase):
    def setUp(self):
        self.data = bytearray(2048)
        self.base = 0x180000000
        self.sections = [{'raw_offset': 512, 'raw_size': 1536, 'rva': 0x2000}]
        self.arguments = bytes(range(250))*2
        self.data[800:1300] = self.arguments
        for offset, value in [(0x10, 6), (0x14, 7), (0x18, 164), (0x20, 3),
                              (0x2c, 0x4000), (0x3c, 1), (0x44, 500)]:
            struct.pack_into('<I', self.data, 600+offset, value)
        struct.pack_into('<Q', self.data, 600+0x48, self.base+0x2120)
        struct.pack_into('<Q', self.data, 1480, self.base+0x2058)

    def locate(self):
        return locator.locate(bytes(self.data), self.arguments, self.base, self.sections)

    def test_descriptor_fields_and_reference_coordinates(self):
        result = self.locate()
        self.assertEqual(result['candidate_metadata_keys'], {'major': 6, 'minor': 7, 'build': 164})
        self.assertEqual(result['record_rva'], '0x2058')
        self.assertEqual(result['payload_rva'], '0x2120')
        self.assertEqual(result['record_pointer_reference_rvas'], ['0x23c8'])
        self.assertFalse(result['selection_evaluated'])
        self.assertFalse(result['hardware_execution_allowed'])
        self.assertNotIn('payload', result)

    def test_missing_or_duplicate_arguments_rejected(self):
        for target in (b'x'*500, self.arguments):
            if target == self.arguments:
                self.data[1500:2000] = self.arguments
            with self.assertRaises(ValueError):
                locator.locate(bytes(self.data), target, self.base, self.sections)

    def test_duplicate_payload_pointer_rejected(self):
        struct.pack_into('<Q', self.data, 1400, self.base+0x2120)
        with self.assertRaises(ValueError):
            self.locate()

    def test_wrong_descriptor_size_rejected(self):
        struct.pack_into('<I', self.data, 600+0x44, 499)
        with self.assertRaises(ValueError):
            self.locate()

    def test_missing_descriptor_reference_rejected(self):
        self.data[1480:1488] = bytes(8)
        with self.assertRaises(ValueError):
            self.locate()

    def test_invalid_ranges_and_reference_length_rejected(self):
        with self.assertRaises(ValueError):
            locator.locate(bytes(self.data), self.arguments[:499], self.base, self.sections)
        with self.assertRaises(ValueError):
            locator.locate(bytes(self.data), self.arguments, self.base, [])
        with self.assertRaises(ValueError):
            locator.locate(bytes(self.data), self.arguments, self.base, self.sections*2)


if __name__ == '__main__':
    unittest.main()
