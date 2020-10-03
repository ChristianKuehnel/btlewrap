"""Test btlewrap by connecting to a real device."""

import unittest
from btlewrap import GatttoolBackend
from . import CommonTests


class TestGatttool(unittest.TestCase, CommonTests):
    """Test btlewrap by connecting to a real device."""
    # pylint does not understand pytest fixtures, so we have to disable the warning
    # pylint: disable=no-member

    def setUp(self):
        """Set up the test environment."""
        self.backend = GatttoolBackend()

    def test_scan_with_adapter(self):
        """Scan for devices with specific adapter."""

        devices = self.backend.scan_for_devices(timeout=7, adapter='hci0')
        self.assertGreater(len(devices), 0)
