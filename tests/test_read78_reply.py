# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import json
import struct
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_read78_reply import inspect, ANALYSIS_LIMIT


def body(count, tail=b''):
    return struct.pack('<I', count)+tail


class Read78ReplyTests(unittest.TestCase):
    def test_output_independent_of_content(self):
        a = inspect(body(8, b'PRIVATE!'))
        self.assertEqual(a, inspect(body(8, b'OTHER123')))
        self.assertEqual((a['body_bytes'], a['content_bytes']), (12, 8))
        self.assertFalse(a['hardware_validated'])
        self.assertNotIn('PRIVATE', json.dumps(a))

    def test_zero_is_structural_only(self):
        a = inspect(body(0))
        self.assertEqual(a['content_bytes'], 0)
        self.assertFalse(a['content_semantics_verified'])

    def test_all_truncations_rejected(self):
        valid = body(12, bytes(12))
        for size in range(len(valid)):
            with self.assertRaises(ValueError):
                inspect(valid[:size])

    def test_inconsistent_counts_and_endianness(self):
        for data in (body(0xffffffff), body(1, b'xx'), body(0, b'x'), struct.pack('>I', 1)+b'x'):
            with self.assertRaises(ValueError):
                inspect(data)

    def test_input_type_and_budget(self):
        self.assertEqual(inspect(body(ANALYSIS_LIMIT-4, bytes(ANALYSIS_LIMIT-4)))['body_bytes'], ANALYSIS_LIMIT)
        for data in (None, bytearray(body(0)), body(ANALYSIS_LIMIT-3, bytes(ANALYSIS_LIMIT-3))):
            with self.assertRaises(ValueError):
                inspect(data)

    def test_cli_bounded_and_sanitized(self):
        script = Path(__file__).resolve().parents[1]/'tools/inspect_read78_reply.py'
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'PRIVATE.bin'
            p.write_bytes(body(1, b'x'))
            result = subprocess.run([sys.executable, str(script), str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout), inspect(p.read_bytes()))
            p.write_bytes(bytes(ANALYSIS_LIMIT+1))
            for path in (p, Path(tmp)/'MISSING_PRIVATE.bin'):
                result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertNotIn('PRIVATE', result.stderr)
