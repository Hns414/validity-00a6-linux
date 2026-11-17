# SPDX-License-Identifier: LGPL-2.1-or-later
import ctypes
from pathlib import Path
import random
import subprocess
import tempfile
import unittest
from tools.inspect_record_envelope import inspect

ROOT = Path(__file__).resolve().parents[1]


class Summary(ctypes.Structure):
    _fields_ = [('record_count', ctypes.c_size_t),
                ('application_record_count', ctypes.c_size_t),
                ('content_bytes', ctypes.c_size_t)]


class RecordEnvelopeNativeTests(unittest.TestCase):
    def test_native_boundaries_and_unchanged_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = str(Path(tmp)/'envelope-test')
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            '-I', str(ROOT/'src'), str(ROOT/'src/record_envelope.c'),
                            str(ROOT/'tests/test_record_envelope_native.c'), '-o', binary],
                           check=True, capture_output=True, timeout=30)
            result = subprocess.run([binary], check=True, capture_output=True, timeout=10)
            self.assertEqual((result.stdout, result.stderr), (b'', b''))

    def test_matches_python_scope_on_synthetic_envelopes_and_mutations(self):
        rng = random.Random(7552)
        samples = [b'', b'\x00', bytes(65537)]
        for _ in range(100):
            records = []
            for _ in range(rng.randrange(1, 8)):
                body = rng.randbytes(rng.randrange(1, 400))
                records.append(bytes([rng.randrange(0x14, 0x18), 3, 3]) +
                               len(body).to_bytes(2, 'big') + body)
            data = b''.join(records)
            samples.extend([data, data[:-1], data+b'\x00', data[:rng.randrange(len(data))]])
            changed = bytearray(data)
            changed[rng.randrange(5)] ^= 0xff
            samples.append(bytes(changed))
        with tempfile.TemporaryDirectory() as tmp:
            library = str(Path(tmp)/'envelope.so')
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            '-shared', '-fPIC', str(ROOT/'src/record_envelope.c'),
                            '-o', library], check=True, capture_output=True, timeout=30)
            function = ctypes.CDLL(library).validity_inspect_record_envelope
            function.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(Summary)]
            function.restype = ctypes.c_int
            for data in samples:
                with self.subTest(length=len(data)):
                    buffer = ctypes.create_string_buffer(data)
                    summary = Summary(9, 9, 9)
                    accepted = function(buffer, len(data), ctypes.byref(summary))
                    try:
                        expected = inspect(data)
                    except ValueError:
                        self.assertEqual(accepted, 0)
                        self.assertEqual(tuple(getattr(summary, k) for k, _ in Summary._fields_), (0, 0, 0))
                    else:
                        self.assertEqual(accepted, 1)
                        for key, _ in Summary._fields_:
                            self.assertEqual(getattr(summary, key), expected[key])
                    self.assertEqual(buffer.raw[:len(data)], data)
