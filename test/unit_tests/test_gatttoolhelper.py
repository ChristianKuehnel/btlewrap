"""Test helper functions."""

import unittest
from btlewrap import GatttoolBackend


class TestGatttoolHelper(unittest.TestCase):
    """Test helper functions."""

    # allow testsing protected member functions
    # pylint: disable = protected-access

    def test_byte_to_handle(self):
        """Test conversion of handles."""
        self.assertEqual('0x0B', GatttoolBackend.byte_to_handle(0x0B))
        self.assertEqual('0xAF', GatttoolBackend.byte_to_handle(0xAF))
        self.assertEqual('0xAABB', GatttoolBackend.byte_to_handle(0xAABB))

    def test_bytes_to_string(self):
        """Test conversion of byte arrays."""
        self.assertEqual('0A0B', GatttoolBackend.bytes_to_string(bytes([0x0A, 0x0B])))
        self.assertEqual('0x0C0D', GatttoolBackend.bytes_to_string(bytes([0x0C, 0x0D]), True))

    def test_parse_scan_output_deduplicate(self):
        """Check if parsed lists are de-duplicated."""
        test_data = '''
            LE Scan ...
            65:B8:8C:38:D5:77 (MyDevice)
            78:24:AC:37:21:3D (unknown)
            78:24:AC:37:21:3D (unknown)
            78:24:AC:37:21:3D (unknown)
            63:82:9D:D1:B3:A2 (unknown)
            63:82:9D:D1:B3:A2 (unknown)
            '''
        expected = [
            ('65:B8:8C:38:D5:77', 'MyDevice'),
            ('78:24:AC:37:21:3D', 'unknown'),
            ('63:82:9D:D1:B3:A2', 'unknown'),
        ]
        self.assertCountEqual(
            expected,
            GatttoolBackend._parse_scan_output(test_data))

    def test_parse_scan_output_update_names(self):
        """Check if "unknown" names are updated later on."""
        test_data = '''
            LE Scan ...
            78:24:AC:37:21:3D (SomeDevice)
            78:24:AC:37:21:3D (unknown)
            63:82:9D:D1:B3:A2 (unknown)
            63:82:9D:D1:B3:A2 (OtherDevice)
            '''
        expected = [
            ('78:24:AC:37:21:3D', 'SomeDevice'),
            ('63:82:9D:D1:B3:A2', 'OtherDevice'),
        ]
        self.assertCountEqual(
            expected,
            GatttoolBackend._parse_scan_output(test_data))

    def test_parse_scan_output_partial_data(self):
        """Check if the parser can handle partial data"""
        test_data = '''
            LE Scan ...
            78:24:AC:37:21:3D (SomeDevice)
            65:B8:8C:38:D5:77 (unknown)
            78:24:AC:37:21:3D (unknown)
            63:82:9D:D1:B3:A2 (unknown)
            63:82:9D:D1:B3:A2 (OtherDevice)
            65:B8:8C:38:D5:77 (unknown)
            65:B8:8C:38:D5:77 (MyDevice)
            65:B8:8C:38:D5:77 (unknown)
            '''
        for length in range(0, len(test_data)):
            result = GatttoolBackend._parse_scan_output(test_data[0:length])
            self.assertEqual(len(result) > 0, length > 66)
