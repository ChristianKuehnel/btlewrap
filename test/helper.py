"""Helpers for test cases."""
from btlewrap.base import AbstractBackend


class MockBackend(AbstractBackend):
    """Mockup of a Backend and Sensor.

    The behaviour of this Sensors is based on the knowledge there
    is so far on the behaviour of the sensor. So if our knowledge
    is wrong, so is the behaviour of this sensor! Thus is always
    makes sensor to also test against a real sensor.
    """

    def __init__(self, adapter='hci0', address_type=None):
        super(MockBackend, self).__init__(adapter, address_type)
        self.written_handles = []
        self.expected_write_handles = set()
        self.override_read_handles = dict()
        self.is_available = True
        self.address_type = address_type

    def check_backend(self):
        """This backend is available when the field is set accordingly."""
        return self.is_available

    def read_handle(self, handle):
        """Read one of the handles that are implemented."""
        if handle in self.override_read_handles:
            return self.override_read_handles[handle]
        raise ValueError('handle not implemented in mockup')

    def write_handle(self, handle, value):
        """Writing handles just stores the results in a list."""
        self.written_handles.append((handle, value))
        return handle in self.expected_write_handles

    def wait_for_notification(self, handle, delegate, notification_timeout):
        """same as write_handle. Delegate is not used, yet."""
        delegate.handleNotification(bytes([int(x, 16) for x in "54 3d 32 37 2e 33 20 48 3d 32 37 2e 30 00".split()]))
        return self.write_handle(handle, self._DATA_MODE_LISTEN)
