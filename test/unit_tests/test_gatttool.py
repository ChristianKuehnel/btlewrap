"""Test gatttool backend."""

import unittest
from unittest import mock
from test import TEST_MAC
from subprocess import TimeoutExpired
from btlewrap import GatttoolBackend, BluetoothBackendException


class TestGatttool(unittest.TestCase):
    """Test gatttool by mocking gatttool.

    These tests do NOT require hardware!
    time.sleep is mocked in some cases to speed up the retry-feature.
    """
    # access to protected members is fine in testing
    # pylint: disable = protected-access

    # arguments of mock.patch are not always used
    # tests have more methos that usual
    # pylint: disable = unused-argument, too-many-public-methods

    handle_notification_called = False

    @mock.patch('btlewrap.gatttool.Popen')
    def test_read_handle_ok(self, popen_mock):
        """Test reading handle successfully."""
        gattoutput = bytes([0x00, 0x11, 0xAA, 0xFF])
        _configure_popenmock(popen_mock, 'Characteristic value/descriptor: 00 11 AA FF')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        result = backend.read_handle(0xFF)
        self.assertEqual(gattoutput, result)

    def test_run_connect_disconnect(self):
        """Just run connect and disconnect"""
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        self.assertEqual(TEST_MAC, backend._mac)
        backend.disconnect()
        self.assertEqual(None, backend._mac)

    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_read_handle_empty_output(self, _, popen_mock):
        """Test reading handle where no result is returned."""
        _configure_popenmock(popen_mock, '')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.read_handle(0xFF)

    @mock.patch('btlewrap.gatttool.Popen')
    def test_read_handle_wrong_handle(self, popen_mock):
        """Test reading invalid handle."""
        _configure_popenmock(popen_mock, 'Characteristic value/descriptor read failed: Invalid handle')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.read_handle(0xFF)

    def test_read_not_connected(self):
        """Test reading data when not connected."""
        backend = GatttoolBackend()
        with self.assertRaises(BluetoothBackendException):
            backend.read_handle(0xFF)

    @mock.patch('os.killpg')
    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_read_handle_timeout(self, time_mock, popen_mock, os_mock):
        """Test notification when timeout"""
        _configure_popenmock_timeout(popen_mock, "Characteristic")
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.read_handle(0xFF)

    def test_write_not_connected(self):
        """Test writing data when not connected."""
        backend = GatttoolBackend()
        with self.assertRaises(BluetoothBackendException):
            backend.write_handle(0xFF, [0x00])

    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_write_handle_ok(self, time_mock, popen_mock):
        """Test writing to a handle successfully."""
        _configure_popenmock(popen_mock, 'Characteristic value was written successfully')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        self.assertTrue(backend.write_handle(0xFF, b'\x00\x10\xFF'))

    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_write_handle_wrong_handle(self, time_mock, popen_mock):
        """Test writing to a non-writable handle."""
        _configure_popenmock(popen_mock, "Characteristic Write Request failed: Attribute can't be written")
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.write_handle(0xFF, b'\x00\x10\xFF')

    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_write_handle_no_answer(self, time_mock, popen_mock):
        """Test writing to a handle when no result is returned."""
        _configure_popenmock(popen_mock, '')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.write_handle(0xFF, b'\x00\x10\xFF')

    @mock.patch('os.killpg')
    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_write_handle_timeout(self, time_mock, popen_mock, os_mock):
        """Test notification when timeout"""
        _configure_popenmock_timeout(popen_mock, "Characteristic")
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.write_handle(0xFF, b'\x00\x10\xFF')

    def test_notification_not_connected(self):
        """Test writing data when not connected."""
        backend = GatttoolBackend()
        with self.assertRaises(BluetoothBackendException):
            backend.wait_for_notification(0xFF, self, 10)

    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_wait_for_notification(self, time_mock, popen_mock):
        """Test notification successfully."""
        _configure_popenmock(popen_mock, (
            "Characteristic value was written successfully\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 33 20 48 3d 32 37 2e 30 00\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 32 20 48 3d 32 37 2e 32 00\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 31 20 48 3d 32 37 2e 34 00")
                            )
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        self.handle_notification_called = False
        self.assertTrue(backend.wait_for_notification(0xFF, self, 10))
        self.assertTrue(self.handle_notification_called)

    def handleNotification(self, handle, raw_data):  # pylint: disable=unused-argument,invalid-name,no-self-use
        """ gets called by the backend when using wait_for_notification
        """
        if raw_data is None:
            raise Exception('no data given')
        self.assertTrue(len(raw_data) == 14)
        self.handle_notification_called = True

    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_notification_wrong_handle(self, time_mock, popen_mock):
        """Test notification when wrong handle"""
        _configure_popenmock(popen_mock, "Characteristic Write Request failed: Attribute can't be written")
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.wait_for_notification(0xFF, self, 10)

    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_notification_no_answer(self, time_mock, popen_mock):
        """Test notification when no result is returned."""
        _configure_popenmock(popen_mock, '')
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        with self.assertRaises(BluetoothBackendException):
            backend.wait_for_notification(0xFF, self, 10)

    @mock.patch('os.killpg')
    @mock.patch('btlewrap.gatttool.Popen')
    @mock.patch('time.sleep', return_value=None)
    def test_notification_timeout(self, time_mock, popen_mock, os_mock):
        """Test notification when timeout"""
        _configure_popenmock_timeout(popen_mock, (
            "Characteristic value was written successfully\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 33 20 48 3d 32 37 2e 30 00\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 32 20 48 3d 32 37 2e 32 00\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 31 20 48 3d 32 37 2e 34 00"))
        backend = GatttoolBackend()
        backend.connect(TEST_MAC)
        self.handle_notification_called = False
        self.assertTrue(backend.wait_for_notification(0xFF, self, 10))
        self.assertTrue(self.handle_notification_called)

    @mock.patch('btlewrap.gatttool.run', return_value=None)
    def test_check_backend_ok(self, call_mock):
        """Test check_backend successfully."""
        self.assertTrue(GatttoolBackend().check_backend())

    @mock.patch('btlewrap.gatttool.run', **{'side_effect': IOError()})
    def test_check_backend_fail(self, call_mock):
        """Test check_backend with IOError being risen."""
        self.assertFalse(GatttoolBackend().check_backend())

    def test_notification_payload_ok(self):
        """ testing data processing"""

        notification_response = (
            "Characteristic value was written successfully\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 33 20 48 3d 32 37 2e 30 00\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 32 20 48 3d 32 37 2e 32 00\n"
            "Notification handle = 0x000e value: 54 3d 32 37 2e 31 20 48 3d 32 37 2e 34 00")
        data = GatttoolBackend().extract_notification_payload(notification_response)
        self.assertTrue(len(data) == 3)
        self.assertTrue(data[0] == "54 3d 32 37 2e 33 20 48 3d 32 37 2e 30 00")
        self.assertTrue(data[2] == "54 3d 32 37 2e 31 20 48 3d 32 37 2e 34 00")

    def test_supports_scanning(self):
        """Check if scanning is set correctly."""
        backend = GatttoolBackend()
        self.assertTrue(backend.supports_scanning())


def _configure_popenmock(popen_mock, output_string):
    """Helper function to create a mock for Popen."""
    match_result = mock.Mock()
    match_result.communicate.return_value = [
        bytes(output_string, encoding='UTF-8'),
        bytes('random text', encoding='UTF-8')]
    popen_mock.return_value.__enter__.return_value = match_result


def _configure_popenmock_timeout(popen_mock, output_string):
    """Helper function to create a mock for Popen."""
    match_result = mock.Mock()
    match_result.communicate = POpenHelper(output_string).communicate_timeout
    popen_mock.return_value.__enter__.return_value = match_result


class POpenHelper:
    """Helper class to configure Popen mock behavior for timeout"""
    partial_response = ''

    def __init__(self, output_string=None):
        self.set_partial_response(output_string)

    def set_partial_response(self, response):
        """set response on timeout"""
        self.partial_response = response

    def communicate_timeout(self, timeout=None):  # pylint: disable=no-self-use,unused-argument
        """pass this method as a replacement to themocked Popen.communicate method"""
        process = mock.Mock()
        process.pid = 0
        if timeout:
            raise TimeoutExpired(process, timeout)
        return [bytes(self.partial_response, 'utf-8')]
