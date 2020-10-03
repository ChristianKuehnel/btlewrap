"""Unit tests for the bluepy backend."""

import unittest
from unittest import mock
from test import TEST_MAC
from bluepy.btle import BTLEException
from btlewrap.bluepy import BluepyBackend
from btlewrap import BluetoothBackendException


class TestBluepy(unittest.TestCase):
    """Unit tests for the bluepy backend."""

    # pylint: disable=no-self-use

    @mock.patch('bluepy.btle.Peripheral')
    def test_configuration_default(self, mock_peripheral):
        """Test adapter name pattern parsing."""
        backend = BluepyBackend()
        backend.connect(TEST_MAC)
        mock_peripheral.assert_called_with(TEST_MAC, addrType='public', iface=0)

    @mock.patch('bluepy.btle.Peripheral')
    def test_configuration_hci12(self, mock_peripheral):
        """Test adapter name pattern parsing."""
        backend = BluepyBackend(adapter='hci12')
        backend.connect(TEST_MAC)
        mock_peripheral.assert_called_with(TEST_MAC, addrType='public', iface=12)

    @mock.patch('bluepy.btle.Peripheral')
    def test_configuration_invalid(self, _):
        """Test adapter name pattern parsing."""
        backend = BluepyBackend(adapter='somestring')
        with self.assertRaises(BluetoothBackendException):
            backend.connect(TEST_MAC)

    def test_check_backend_ok(self):
        """Test check_backend successfully."""
        self.assertTrue(BluepyBackend.check_backend())

    @mock.patch('bluepy.btle.Peripheral')
    def test_connect_exception(self, mock_peripheral):
        """Test exception wrapping."""
        mock_peripheral.side_effect = BTLEException('Test')
        backend = BluepyBackend()
        with self.assertRaises(BluetoothBackendException):
            backend.connect(TEST_MAC)

    @mock.patch('bluepy.btle.Peripheral')
    def test_wait_for_notification(self, mock_peripheral):
        """Test writing to a handle successfully."""
        backend = BluepyBackend()
        backend.connect(TEST_MAC)
        self.assertTrue(backend.wait_for_notification(0xFF, None, 10))
        mock_peripheral.assert_called_with(TEST_MAC, addrType='public', iface=0)

    def test_supports_scanning(self):
        """Check if scanning is set correctly."""
        backend = BluepyBackend()
        self.assertTrue(backend.supports_scanning())
