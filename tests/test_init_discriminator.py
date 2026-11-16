# SPDX-License-Identifier: LGPL-2.1-or-later
import importlib.util
from pathlib import Path
import subprocess
import sys
import json
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'tools/model_init_discriminator.py'
spec = importlib.util.spec_from_file_location('model_init_discriminator', TOOL)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class DiscriminatorTests(unittest.TestCase):
    def test_documented_branch_vectors(self):
        for major, flags, expected in [(6, 0, 3), (6, 0x20, 2),
                                       (6, 0xff, 2), (5, 0x20, 0),
                                       (0, 0, 0), (255, 255, 0)]:
            with self.subTest(major=major, flags=flags):
                self.assertEqual(model.discriminator(major, flags), expected)

    def test_unrelated_bits_do_not_change_branch(self):
        for flags in range(256):
            baseline = flags & 0x20
            self.assertEqual(model.discriminator(6, flags),
                             model.discriminator(6, baseline))
            self.assertNotEqual(model.discriminator(6, flags),
                                model.discriminator(6, flags ^ 0x20))

    def test_other_major_versions_ignore_flag(self):
        for major in range(256):
            if major == 6:
                continue
            for flags in (0, 0x20, 0xff):
                self.assertEqual(model.discriminator(major, flags), 0)

    def test_reject_non_bytes_in_either_input(self):
        for invalid in (-1, 256, None, True, 6.0, '6'):
            for args in ((invalid, 0), (6, invalid)):
                with self.subTest(args=args), self.assertRaises(ValueError):
                    model.discriminator(*args)

    def test_cli_limits_and_metadata(self):
        result = subprocess.run([sys.executable, str(TOOL), '--major', '6',
                                 '--internal-flag-byte', '0x20'],
                                capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        self.assertEqual(output['discriminator'], 2)
        self.assertFalse(output['full_selection_evaluated'])
        self.assertFalse(output['hardware_execution_enabled'])
        invalid = subprocess.run([sys.executable, str(TOOL), '--major', '6',
                                  '--internal-flag-byte', '256'],
                                 capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, '')
