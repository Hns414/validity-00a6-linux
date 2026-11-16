# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from model_capture_request import layout


class CaptureRequestModelTests(unittest.TestCase):
    def test_header_field_order_and_boundaries(self):
        out = layout(65535, 0, 0)
        self.assertEqual((out['field_0c'], out['field_00']), (65535, 0))
        self.assertEqual(out['total_bytes'], 5)
        self.assertEqual(out['field_encoding'], 'little-endian-uint16')
        self.assertFalse(out['hardware_validated'])

    def test_padding_at_exact_boundary_not_adjacent_sizes(self):
        self.assertEqual([(layout(1, 2, n)['total_bytes'],
                           layout(1, 2, n)['trailing_zero_bytes'])
                          for n in (58, 59, 60)], [(63, 0), (68, 4), (65, 0)])

    def test_every_boundary_in_analysis_budget(self):
        for total in range(64, 65536, 64):
            self.assertEqual(layout(0, 0, total-5)['total_bytes'], total+4)
            self.assertEqual(layout(0, 0, total-6)['trailing_zero_bytes'], 0)
            self.assertEqual(layout(0, 0, total-4)['trailing_zero_bytes'], 0)

    def test_budget_includes_header_and_padding(self):
        self.assertEqual(layout(0, 0, 65530)['total_bytes'], 65535)
        for count in (65531, 65532, 65536, 65537, 2**100):
            with self.assertRaises(ValueError):
                layout(0, 0, count)

    def test_invalid_types_and_ranges_rejected(self):
        for position in range(3):
            for value in (-1, True, False, 1.0, '1', None):
                args = [0, 0, 0]
                args[position] = value
                with self.assertRaises(ValueError):
                    layout(*args)
        for args in ((65536, 0, 0), (0, 65536, 0)):
            with self.assertRaises(ValueError):
                layout(*args)

    def test_cli_reports_only_metadata_and_rejects_out_of_scope(self):
        command = [sys.executable, str(ROOT/'tools/model_capture_request.py')]
        result = subprocess.run(command+['1', '2', '59'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['total_bytes'], 68)
        bad = subprocess.run(command+['1', '2', '65531'], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, '')
