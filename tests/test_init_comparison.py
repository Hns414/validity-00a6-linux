# SPDX-License-Identifier: LGPL-2.1-or-later
import sys
from pathlib import Path
import ast
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
try:
    import compare_init_blobs as compare
finally:
    sys.path.pop(0)


class InitComparisonTests(unittest.TestCase):
    def test_whitespace_between_hex_nibbles_matches_upstream_unhex(self):
        result = compare.unhex_assignments("init_hardcoded = unhex('0 6\\n02')")
        self.assertEqual(result['init_hardcoded'], b'\x06\x02')

    def test_source_is_parsed_without_execution(self):
        source = "raise RuntimeError('must not run')\ninit_hardcoded = unhex('0602')"
        self.assertEqual(compare.unhex_assignments(source)['init_hardcoded'], b'\x06\x02')

    def test_dynamic_invalid_and_duplicate_blob_definitions_rejected(self):
        for source in ["init_hardcoded=unhex(get_hex())", "init_hardcoded=unhex('xx')",
                       "init_hardcoded=unhex('abc')", "init_hardcoded=unhex('00')\ninit_hardcoded=unhex('01')"]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                compare.unhex_assignments(source)

    def test_messages_preserve_order_and_declared_optional_flag(self):
        source = '''
init_messages.append(Validity_Messages(query=array('B', [1]), optional=True))
init_messages.append(Validity_Messages(query=array('B', bytes.fromhex('0602'))))
'''
        result = compare.validity91_messages(source)
        self.assertEqual([x['data'] for x in result], [b'\x01', b'\x06\x02'])
        self.assertEqual([x['optional_declared'] for x in result], [True, False])

    def test_dynamic_message_bytes_and_flags_rejected(self):
        for query, flag in [("array('B', [get_byte()])", 'True'),
                            ("array('B', [256])", 'True'),
                            ("array('B', [True])", 'True'),
                            ("array('B', [1])", 'get_optional()')]:
            source = f'init_messages.append(Validity_Messages(query={query}, optional={flag}))'
            with self.subTest(source=source), self.assertRaises(ValueError):
                compare.validity91_messages(source)

    def test_common_prefix_is_not_equality(self):
        self.assertEqual(compare.common_prefix(b'\x06\x02\0\0\x01aaa', b'\x06\x02\0\0\x01bbb'), 5)
        self.assertEqual(compare.common_prefix(b'', b'abc'), 0)
        self.assertEqual(compare.common_prefix(b'abc', b'ab'), 2)
        self.assertEqual(compare.common_prefix(b'abc', b'abc'), 3)

    def test_hex_parser_rejects_expressions(self):
        for source in ["'00' + '01'", "f'{value}'", "bytes([1])"]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                compare.literal_hex(ast.parse(source, mode='eval').body)


if __name__ == '__main__':
    unittest.main()
