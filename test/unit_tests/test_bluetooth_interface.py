"""Tests for the BluetoothInterface class."""
import unittest
from test.helper import MockBackend
from btlewrap.base import BluetoothInterface


class TestBluetoothInterface(unittest.TestCase):
    """Tests for the BluetoothInterface class."""

    def test_context_manager_locking(self):
        """Test the usage of the with statement."""
        bluetooth_if = BluetoothInterface(MockBackend)
        self.assertFalse(bluetooth_if.is_connected())

        with bluetooth_if.connect("abc"):  # as connection:
            self.assertTrue(bluetooth_if.is_connected())

        self.assertFalse(bluetooth_if.is_connected())

    def test_exception_in_with(self):
        """Test clean exit after exception."""
        bluetooth_if = BluetoothInterface(MockBackend)
        self.assertFalse(bluetooth_if.is_connected())
        with self.assertRaises(ValueError):
            with bluetooth_if.connect("abc"):
                raise ValueError("some test exception")
        self.assertFalse(bluetooth_if.is_connected())
