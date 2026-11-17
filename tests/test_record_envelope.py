# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from inspect_record_envelope import inspect, ANALYSIS_LIMIT


def record(data, kind=0x17):
    return bytes((kind, 3, 3))+len(data).to_bytes(2, 'big')+data


class RecordEnvelopeTests(unittest.TestCase):
    def test_single_and_multiple_application_records(self):
        a = inspect(record(b'x'))
        self.assertTrue(a['single_application_envelope'])
        b = inspect(record(b'x')+record(b'yy'))
        self.assertEqual((b['record_count'], b['application_record_count'], b['content_bytes']), (2, 2, 3))
        self.assertFalse(b['single_application_envelope'])
        self.assertFalse(b['cryptographically_validated'])

    def test_output_ignores_content(self):
        a = inspect(record(b'PRIVATE!'))
        self.assertEqual(a, inspect(record(b'OTHER123')))
        self.assertNotIn('PRIVATE', json.dumps(a))
        self.assertEqual(inspect(record(b'x', 0x16))['application_record_count'], 0)

    def test_truncation_and_declared_length(self):
        valid = record(bytes(19))
        for size in range(len(valid)):
            with self.assertRaises(ValueError):
                inspect(valid[:size])
        with self.assertRaises(ValueError):
            inspect(b'\x17\x03\x03\x01\x00x')

    def test_zero_unknown_version_and_tail_markers(self):
        for data in (record(b''), record(b'x', 0x18), b'\x17\x03\x01\x00\x01x', record(b'x')+b'\0', record(b'x')+b'\xff'):
            with self.assertRaises(ValueError):
                inspect(data)

    def test_budget_and_input_type(self):
        self.assertEqual(inspect(record(bytes(ANALYSIS_LIMIT-5)))['envelope_bytes'], ANALYSIS_LIMIT)
        for data in (None, bytearray(record(b'x')), record(bytes(ANALYSIS_LIMIT-4))):
            with self.assertRaises(ValueError):
                inspect(data)

    def test_cli_bounded_and_sanitized(self):
        script = Path(__file__).resolve().parents[1]/'tools/inspect_record_envelope.py'
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'PRIVATE.bin'
            p.write_bytes(record(b'x')+record(b'yy'))
            result = subprocess.run([sys.executable, str(script), str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout), inspect(p.read_bytes()))
            p.write_bytes(bytes(ANALYSIS_LIMIT+1))
            for path in (p, Path(tmp)/'PRIVATE_MISSING.bin'):
                result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertNotIn('PRIVATE', result.stderr)
