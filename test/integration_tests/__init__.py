"""Common functionality for integration tests"""
import pytest
from btlewrap import BluepyBackend


class CommonTests():
    """Base class for integration tests"""
    # pylint does not understand pytest fixtures, so we have to disable the warning
    # pylint: disable=no-member

    def setUp(self):  # pylint: disable=invalid-name
        """Just create type definition for self.backend."""
        self.backend = None  # type: BluepyBackend
        raise NotImplementedError()

    def test_check_backend(self):
        """Ensure backend is available."""
        self.assertTrue(self.backend.check_backend())

    @pytest.mark.usefixtures("mac")
    def test_scan(self):
        """Scan for devices, if supported by backend."""
        if not self.backend.supports_scanning():
            return

        devices = self.backend.scan_for_devices(timeout=7)
        mac_list = [d[0].lower() for d in devices]
        self.assertIn(self.mac.lower(), mac_list)

    @pytest.mark.usefixtures("mac")
    def test_connect(self):
        """Try connecting to a device."""
        self.backend.connect(self.mac)
        self.backend.disconnect()

    @pytest.mark.usefixtures("mac")
    def test_read_0x38(self):
        """Read from handle 0x38.

        On the miflora devices this get the battery and version info."""
        self.backend.connect(self.mac)
        result = self.backend.read_handle(0x38)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 5)
