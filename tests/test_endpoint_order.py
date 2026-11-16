# SPDX-License-Identifier: LGPL-2.1-or-later
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import collect_endpoint_order as collector


def descriptors(addresses=(1, 0x81, 0x82, 0x83, 0x84)):
    device = bytearray(18)
    device[:2] = bytes([18, 1])
    device[8:12] = bytes.fromhex('8a13a600')
    device[14:18] = bytes([99, 98, 97, 1])  # Private string indices never exported.
    interface = bytes([9, 4, 0, 0, len(addresses), 255, 0, 0, 96])
    eps = b''.join(bytes([7, 5, a, 3 if a >= 0x83 else 2, 8, 0, 4]) for a in addresses)
    total = 9+len(interface)+len(eps)
    config = bytes([9, 2, total & 255, total >> 8, 1, 1, 95, 128, 50])
    return bytes(device)+config+interface+eps


class EndpointOrderTests(unittest.TestCase):
    def test_preserves_order_instead_of_sorting_addresses(self):
        addresses = (0x84, 1, 0x81, 0x82, 0x83)
        output = collector.parse_order(descriptors(addresses))
        items = output['endpoints_in_descriptor_order']
        self.assertEqual([x['bEndpointAddress'] for x in items], list(addresses))
        self.assertEqual([x['pipe_index'] for x in items], list(range(5)))
        self.assertNotIn('serial', json.dumps(output))

    def test_truncation_length_and_zero_size_rejected(self):
        data = descriptors()
        for end in range(len(data)):
            with self.subTest(end=end), self.assertRaises(ValueError):
                collector.parse_order(data[:end])
        for offset, value in [(20, 1), (27, 0), (36, 0)]:
            changed = bytearray(data)
            changed[offset] = value
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                collector.parse_order(changed)

    def test_unexpected_identity_interface_and_duplicate_endpoint_rejected(self):
        data = descriptors()
        for offset, value in [(10, 0x91), (17, 2), (22, 2), (29, 1), (30, 1), (31, 4)]:
            changed = bytearray(data)
            changed[offset] = value
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                collector.parse_order(changed)
        with self.assertRaises(ValueError):
            collector.parse_order(descriptors((1, 1)))
        with self.assertRaises(ValueError):
            collector.parse_order(descriptors((0x80,)))

    def test_cached_collection_does_not_emit_paths_or_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/'PRIVATE-TOPOLOGY'
            target.mkdir()
            (target/'idVendor').write_text('138a')
            (target/'idProduct').write_text('00a6')
            (target/'serial').write_text('PRIVATE-SERIAL')
            (target/'descriptors').write_bytes(descriptors())
            output = collector.collect(Path(tmp))
            self.assertFalse(output['usb_transfer_performed'])
            self.assertNotIn('PRIVATE', json.dumps(output))
            self.assertNotIn(tmp, json.dumps(output))

    def test_missing_or_multiple_targets_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                collector.collect(root)
            for name in ('first', 'second'):
                target = root/name
                target.mkdir()
                (target/'idVendor').write_text('138a')
                (target/'idProduct').write_text('00a6')
                (target/'descriptors').write_bytes(descriptors())
            with self.assertRaises(ValueError):
                collector.collect(root)
