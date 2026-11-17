# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Read78NativeTests(unittest.TestCase):
    def test_native_bounds_capacity_borrowing_and_no_input_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp)/'read78-body-test'
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                            '-I', str(ROOT/'src'), str(ROOT/'src/read78_body.c'),
                            str(ROOT/'tests/test_read78_body.c'), '-o', str(binary)],
                           check=True, capture_output=True, timeout=30)
            result = subprocess.run([str(binary)], check=True, capture_output=True, timeout=5)
            self.assertEqual((result.stdout, result.stderr), (b'', b''))
