# SPDX-License-Identifier: LGPL-2.1-or-later
import struct
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
try:
    import survey_vendor_dll as survey
finally:
    sys.path.pop(0)


def synthetic_pe():
    data = bytearray(1024)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 0x3c, 0x80)
    data[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HH', data, 0x84, 0x8664, 1)
    struct.pack_into('<H', data, 0x94, 112)
    struct.pack_into('<H', data, 0x98, 0x20b)
    struct.pack_into('<Q', data, 0x98+24, 0x180000000)
    struct.pack_into('<IIII', data, 0x98+112+8, 512, 0x2000, 512, 512)
    return data


class VendorSurveyTests(unittest.TestCase):
    def test_pe_section_mapping_and_known_anchor(self):
        data = synthetic_pe()
        label = survey.LABELS[0].encode()+b'\0'
        data[544:544+len(label)] = label
        result = survey.survey(bytes(data), {'absent': b'no-such-capsule'})
        self.assertEqual(result['format'], 'PE32+ AMD64')
        self.assertEqual(result['exact_literal_occurrences']['absent'], 0)
        self.assertEqual(result['diagnostic_string_anchors'][0]['string_rva'], '0x2020')
        self.assertNotIn('strings', result)

    def test_separately_stored_payload_matches_without_opcode(self):
        data = synthetic_pe()
        body = b'\x02\0\0\1' + b'x'*100
        data[544:544+len(body)] = body
        result = survey.survey(bytes(data), {'whole_command': b'\x06'+body, 'without_opcode': body})
        self.assertEqual(result['exact_literal_occurrences'], {'whole_command': 0, 'without_opcode': 1})
        self.assertEqual(result['matched_literal_locations'], [{
            'reference_name': 'without_opcode', 'length': len(body),
            'file_offset': '0x220', 'rva': '0x2020'}])

    def test_truncated_and_non_pe_inputs_rejected(self):
        for data in [b'', b'MZ', bytes(1024), bytes(synthetic_pe()[:300])]:
            with self.subTest(length=len(data)), self.assertRaises(ValueError):
                survey.pe_sections(data)

    def test_wrong_architecture_and_magic_rejected(self):
        for offset, value in [(0x84, 0x14c), (0x98, 0x10b)]:
            data = synthetic_pe()
            struct.pack_into('<H', data, offset, value)
            with self.assertRaises(ValueError):
                survey.pe_sections(data)

    def test_out_of_file_section_rejected(self):
        data = synthetic_pe()
        struct.pack_into('<I', data, 0x98+112+8+8, 100000)
        with self.assertRaises(ValueError):
            survey.pe_sections(data)

    def test_exact_contiguous_search_is_not_prefix_or_semantic_match(self):
        self.assertEqual(survey.locations(b'abcabc', b'abcd'), [])
        self.assertEqual(survey.locations(b'abcabc', b'abc'), [0, 3])
        self.assertEqual(survey.locations(b'aaa', b'aa'), [0, 1])
        with self.assertRaises(ValueError):
            survey.locations(b'abc', b'')

    def test_anchor_outside_sections_not_mislabeled_as_virtual_address(self):
        data = synthetic_pe()
        label = survey.LABELS[0].encode()+b'\0'
        data[32:32+len(label)] = label
        with self.assertRaises(ValueError):
            survey.survey(bytes(data), {})


if __name__ == '__main__':
    unittest.main()
