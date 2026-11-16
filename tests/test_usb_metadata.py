# SPDX-License-Identifier: LGPL-2.1-or-later
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    'collector', Path(__file__).resolve().parents[1] / 'tools/collect_usb_metadata.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, path, **values):
        path.mkdir(parents=True, exist_ok=True)
        for key, value in values.items():
            (path / key).write_text(value)
        return path

    def test_target_metadata_excludes_sensitive_strings_and_topology(self):
        dev = self.write(self.root / 'private-topology', idVendor='138a', idProduct='00a6',
                         bcdDevice='0164', serial='PRIVATE-SERIAL', product='PRIVATE-NAME',
                         speed='12', version=' 2.00')
        interface = self.write(dev / 'private:1.0', bInterfaceNumber='00', bNumEndpoints='0a')
        self.write(interface / 'ep_83', bEndpointAddress='83', bmAttributes='03',
                   wMaxPacketSize='0008', bInterval='04')
        result = collector.collect(self.root)
        text = json.dumps(result)
        self.assertNotIn('PRIVATE', text)
        self.assertNotIn('private', text)
        self.assertEqual(result['devices'][0]['bcdDevice'], 0x0164)
        item = result['devices'][0]['interfaces'][0]
        self.assertEqual(item['bNumEndpoints'], 10)
        self.assertEqual(item['endpoints'][0]['bEndpointAddress'], 0x83)

    def test_unrelated_device_ignored(self):
        self.write(self.root / 'other', idVendor='138a', idProduct='0091', serial='PRIVATE')
        self.assertEqual(collector.collect(self.root)['devices'], [])

    def test_malformed_value_rejected(self):
        self.write(self.root / 'target', idVendor='138a', idProduct='00a6',
                   bcdDevice='0164 PRIVATE')
        with self.assertRaises(ValueError):
            collector.collect(self.root)

    def test_disappearing_or_unreadable_root_fails(self):
        with self.assertRaises(OSError):
            collector.collect(self.root / 'missing')


if __name__ == '__main__':
    unittest.main()
