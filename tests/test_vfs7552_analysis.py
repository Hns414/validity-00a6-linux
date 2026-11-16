# SPDX-License-Identifier: LGPL-2.1-or-later
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    'analyzer', Path(__file__).resolve().parents[1] / 'tools/analyze_vfs7552.py')
analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer)


class InventoryTests(unittest.TestCase):
    def test_comments_are_not_bytes_and_lengths_are_computed(self):
        source = '''// static unsigned char fake[] = {0xff};
        static unsigned char packet[] = { /* 999 bytes? */ 0x01, 2, // 0xff
        255, };'''
        self.assertEqual(analyzer.parse_arrays(source), {'packet': bytes([1, 2, 255])})

    def test_expressions_cannot_be_executed_or_silently_accepted(self):
        for body in ('1 << 2', 'get_byte()', '__import__("os")', '0x01 + 1'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                analyzer.parse_arrays('static unsigned char a[] = {' + body + '};')

    def test_unsupported_array_cannot_be_silently_skipped(self):
        for extra in ('static unsigned char b[2] = {1, 2};',
                      'static unsigned char b[] = {{1}};'):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                analyzer.parse_arrays('static unsigned char a[] = {1};' + extra)

    def test_byte_range_and_ambiguous_literals_rejected(self):
        for body in ('256', '-1', '010', '0x100', '1,,2'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                analyzer.parse_arrays('static unsigned char a[] = {' + body + '};')

    def test_empty_and_duplicate_arrays_rejected(self):
        for source in ('', 'static unsigned char a[] = {};',
                       'static unsigned char a[] = {1}; static unsigned char a[] = {2};'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                analyzer.parse_arrays(source)

    def test_sequences_preserve_order_and_declared_not_validated_sizes(self):
        source = '''struct usb_action seq[] = {
            SEND(VFS7552_OUT_ENDPOINT, command)
            // RECV(VFS7552_IN_ENDPOINT, 999)
            RECV_CHECK_SIZE(VFS7552_IN_ENDPOINT, 64, reply)
            RECV_CHECK(VFS7552_IN_ENDPOINT, 64, reply)
        };'''
        seq = analyzer.parse_sequences(source, {'command': b'\x01', 'reply': b'\0\0'})['seq']
        self.assertEqual([item['macro'] for item in seq], ['SEND', 'RECV_CHECK_SIZE', 'RECV_CHECK'])
        self.assertEqual(seq[1]['declared_expected_bytes'], 2)
        self.assertEqual(seq[1]['receive_capacity'], 64)
        self.assertNotIn('validated_bytes', seq[1])

    def test_unknown_macro_and_wrong_argument_count_rejected(self):
        for action in ('EXEC(VFS7552_OUT_ENDPOINT, command)',
                       'SEND(VFS7552_OUT_ENDPOINT, command, 1)',
                       'RECV(VFS7552_IN_ENDPOINT, 1+2)'):
            with self.subTest(action=action), self.assertRaises(ValueError):
                analyzer.parse_sequences('struct usb_action seq[] = {' + action + '};', {'command': b'1'})

    def test_unknown_array_rejected(self):
        with self.assertRaises(KeyError):
            analyzer.parse_sequences('struct usb_action seq[] = { SEND(VFS7552_OUT_ENDPOINT, missing) };', {})

    def test_reply_larger_than_buffer_rejected(self):
        with self.assertRaises(ValueError):
            analyzer.parse_sequences('struct usb_action seq[] = { RECV_CHECK(VFS7552_IN_ENDPOINT, 1, reply) };',
                                     {'reply': b'12'})

    def test_duplicate_sequences_rejected(self):
        block = 'struct usb_action seq[] = { RECV(VFS7552_IN_ENDPOINT, 1) };'
        with self.assertRaises(ValueError):
            analyzer.parse_sequences(block + block, {})


if __name__ == '__main__':
    unittest.main()
