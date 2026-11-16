# SPDX-License-Identifier: LGPL-2.1-or-later
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('cc') or not shutil.which('pkg-config'):
            raise unittest.SkipTest('C compiler and libusb headers needed for transport simulation')
        flags = subprocess.run(['pkg-config', '--cflags', 'libusb-1.0'], capture_output=True, text=True)
        if flags.returncode:
            raise unittest.SkipTest('libusb development headers unavailable')
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.binary = Path(cls.tmp.name) / 'probe-simulated'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-Dclock_gettime=fake_clock_gettime', *flags.stdout.split(),
                        str(ROOT / 'src/probe_rom_info.c'), str(ROOT / 'src/rom_info.c'), str(ROOT / 'src/status_reply.c'),
                        str(ROOT / 'tests/fake_libusb.c'),
                        '-o', str(cls.binary)], check=True, capture_output=True)

    def run_probe(self, scenario='normal', flag='--probe-rom-info'):
        trace = Path(self.tmp.name) / 'trace'
        trace.unlink(missing_ok=True)
        env = {**os.environ, 'FAKE_SCENARIO': scenario, 'FAKE_TRACE': str(trace),
               'FAKE_EXPECT_QUERY': '19' if flag == '--probe-cmd19' else '01'}
        proc = subprocess.run([str(self.binary), flag], env=env, capture_output=True, text=True, timeout=3)
        calls = trace.read_text().splitlines() if trace.exists() else []
        self.assertEqual(proc.stderr, '')
        if flag == '--help':
            return proc, calls
        result = json.loads(proc.stdout)
        self.assertEqual(proc.returncode, 0 if result['status'] == 'reply_received_unvalidated' else 2)
        keys = {'schema_version', 'experiment', 'status', 'stage', 'received_bytes', 'biometric_support'}
        if flag == '--summarize-rom-info':
            keys |= {'decode_status', 'rom_info_candidate'}
        if flag == '--probe-cmd19':
            keys |= {'command', 'candidate_status_zero', 'reference_length_bytes', 'reference_length_match'}
        self.assertEqual(set(result), keys)
        self.assertFalse(result['biometric_support'])
        self.assertNotIn('a5a5', proc.stdout.lower())
        return result, calls

    def test_cmd19_is_one_isolated_query_with_bounded_reply(self):
        result, calls = self.run_probe(flag='--probe-cmd19')
        self.assertEqual(result['schema_version'], 3)
        self.assertEqual(result['experiment'], 'E2')
        self.assertEqual(result['command'], '0x19')
        self.assertEqual(result['received_bytes'], 68)
        self.assertTrue(result['candidate_status_zero'])
        self.assertTrue(result['reference_length_match'])
        self.assertEqual(result['reference_length_bytes'], 68)
        self.assertEqual(calls.count('write_19'), 1)
        self.assertEqual(calls.count('read_128'), 1)
        self.assertNotIn('write_01', calls)
        self.assertNotIn('read_64', calls)
        self.assertIn('release', calls)

    def test_cmd19_short_status_different_size_and_nonzero_status(self):
        for scenario, zero, match in [('cmd19_short', None, False),
                                      ('cmd19_different_length', True, False),
                                      ('cmd19_error', False, True),
                                      ('empty_read', None, False)]:
            with self.subTest(scenario=scenario):
                result, calls = self.run_probe(scenario, flag='--probe-cmd19')
                self.assertIs(result['candidate_status_zero'], zero)
                self.assertIs(result['reference_length_match'], match)
                self.assertEqual(calls.count('read_128'), 1)
                self.assertNotIn('write_01', calls)

    def test_cmd19_transport_failures_do_not_invent_status_or_length_match(self):
        for scenario in ['permission', 'write_timeout', 'read_timeout', 'disconnect',
                         'cancel_read', 'overflow', 'release_error', 'stuck']:
            with self.subTest(scenario=scenario):
                result, _ = self.run_probe(scenario, flag='--probe-cmd19')
                self.assertIsNone(result['candidate_status_zero'])
                self.assertIsNone(result['reference_length_match'])

    def test_offline_init_frame_bounds_aliasing_and_failure_atomicity(self):
        binary = Path(self.tmp.name) / 'init-frame-test'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-I', str(ROOT / 'src'), str(ROOT / 'src/init_frame.c'),
                        str(ROOT / 'tests/test_init_frame.c'), '-o', str(binary)],
                       check=True, capture_output=True)
        subprocess.run([str(binary)], check=True, capture_output=True, timeout=3)

    def test_cleartext_status_header_bounds_endianness_and_payload_omission(self):
        binary = Path(self.tmp.name) / 'status-reply-test'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-I', str(ROOT / 'src'), str(ROOT / 'src/status_reply.c'),
                        str(ROOT / 'tests/test_status_reply.c'), '-o', str(binary)],
                       check=True, capture_output=True)
        subprocess.run([str(binary)], check=True, capture_output=True, timeout=3)

    def test_decoder_bounds_endianness_and_omitted_byte_independence(self):
        binary = Path(self.tmp.name) / 'decoder-test'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-I', str(ROOT / 'src'), str(ROOT / 'src/rom_info.c'), str(ROOT / 'src/status_reply.c'),
                        str(ROOT / 'tests/test_rom_info.c'), '-o', str(binary)],
                       check=True, capture_output=True)
        subprocess.run([str(binary)], check=True, capture_output=True, timeout=3)

    def test_summary_exports_only_allowlisted_candidate_fields(self):
        result, calls = self.run_probe(flag='--summarize-rom-info')
        self.assertEqual(result['schema_version'], 2)
        self.assertEqual(result['decode_status'], 'candidate_layout_unverified')
        self.assertEqual(result['rom_info_candidate'], {
            'firmware_build': 0x12345678, 'firmware_major': 6,
            'firmware_minor': 7, 'product_code': 0x30})
        self.assertEqual(calls.count('write_01'), 1)
        self.assertEqual(calls.count('read_64'), 1)

    def test_summary_rejects_unexpected_length_and_device_status(self):
        for scenario, expected in [('summary_short', 'unexpected_length'),
                                   ('summary_long', 'unexpected_length'),
                                   ('summary_error', 'device_status_nonzero')]:
            with self.subTest(scenario=scenario):
                result, calls = self.run_probe(scenario, flag='--summarize-rom-info')
                self.assertEqual(result['decode_status'], expected)
                self.assertIsNone(result['rom_info_candidate'])
                self.assertEqual(calls.count('read_64'), 1)

    def test_summary_does_not_decode_transport_or_cleanup_failures(self):
        for scenario in ['read_timeout', 'disconnect', 'permission', 'release_error']:
            with self.subTest(scenario=scenario):
                result, _ = self.run_probe(scenario, flag='--summarize-rom-info')
                self.assertEqual(result['decode_status'], 'not_attempted')
                self.assertIsNone(result['rom_info_candidate'])

    def test_help_does_not_initialize_usb(self):
        proc, calls = self.run_probe(flag='--help')
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(calls, [])

    def test_single_query_then_bounded_read_and_cleanup(self):
        result, calls = self.run_probe()
        self.assertEqual(result['status'], 'reply_received_unvalidated')
        self.assertEqual(result['received_bytes'], 38)
        self.assertEqual(calls.count('write_01'), 1)
        self.assertEqual(calls.count('read_64'), 1)
        self.assertLess(calls.index('write_01'), calls.index('read_64'))
        self.assertEqual(calls.count('release'), 1)
        self.assertLess(calls.index('release'), calls.index('close'))
        self.assertEqual(calls[-1], 'exit')

    def test_preflight_failures_send_nothing(self):
        scenarios = {'no_target': 'target_not_found', 'multiple': 'ambiguous_target',
                     'wrong_revision': 'unexpected_device_descriptor',
                     'wrong_endpoint': 'unexpected_configuration', 'wrong_type': 'unexpected_configuration',
                     'duplicate_endpoint': 'unexpected_configuration',
                     'permission': 'permission_denied', 'busy': 'interface_busy', 'claim_busy': 'interface_busy'}
        for scenario, expected in scenarios.items():
            with self.subTest(scenario=scenario):
                result, calls = self.run_probe(scenario)
                self.assertEqual(result['status'], expected)
                self.assertNotIn('write_01', calls)
                self.assertNotIn('read_64', calls)
                self.assertNotIn('release', calls)
                self.assertEqual(calls[-1], 'exit')

    def test_write_failures_never_read_or_retry(self):
        for scenario, status in [('short_write', 'short_write'), ('write_timeout', 'timeout'),
                                 ('submit_error', 'submit_error'), ('hang_write', 'timeout')]:
            with self.subTest(scenario=scenario):
                result, calls = self.run_probe(scenario)
                self.assertEqual(result['status'], status)
                self.assertEqual(calls.count('write_01'), 1)
                self.assertNotIn('read_64', calls)
                self.assertEqual(calls.count('release'), 1)

    def test_read_failures_stop_and_cleanup(self):
        for scenario, status in [('read_timeout', 'timeout'), ('disconnect', 'disconnected'),
                                 ('empty_read', 'empty_reply'), ('overflow', 'invalid_length')]:
            with self.subTest(scenario=scenario):
                result, calls = self.run_probe(scenario)
                self.assertEqual(result['status'], status)
                self.assertEqual(calls.count('read_64'), 1)
                self.assertEqual(calls.count('release'), 1)

    def test_sigint_cancels_inflight_transfer_before_cleanup(self):
        for scenario in ['cancel_write', 'cancel_read']:
            with self.subTest(scenario=scenario):
                result, calls = self.run_probe(scenario)
                self.assertEqual(result['status'], 'cancelled')
                self.assertIn('cancel', calls)
                self.assertLess(calls.index('cancel'), len(calls) - 1 - calls[::-1].index('free_transfer'))
                self.assertEqual(calls.count('release'), 1)
                if scenario == 'cancel_write':
                    self.assertNotIn('read_64', calls)

    def test_event_error_is_cancelled_and_drained(self):
        result, calls = self.run_probe('event_error')
        self.assertEqual(result['status'], 'event_error')
        self.assertIn('cancel', calls)
        self.assertLess(calls.index('cancel'), calls.index('free_transfer'))
        self.assertEqual(calls.count('release'), 1)

    def test_late_completion_is_not_accepted(self):
        result, calls = self.run_probe('late_completion')
        self.assertEqual(result['status'], 'deadline')
        self.assertNotIn('read_64', calls)
        self.assertIn('release', calls)

    def test_undrainable_transfer_exits_without_freeing_live_buffers(self):
        result, calls = self.run_probe('stuck')
        self.assertEqual(result['status'], 'cancel_drain_failed')
        self.assertIn('cancel', calls)
        self.assertNotIn('free_transfer', calls)
        self.assertNotIn('release', calls)
        self.assertNotIn('close', calls)


if __name__ == '__main__':
    unittest.main()
