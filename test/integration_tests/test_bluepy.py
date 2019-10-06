"""Test btlewrap by connecting to a real device."""

import unittest
import pytest
from btlewrap import BluepyBackend


class TestBluepy(unittest.TestCase):
    """Test btlewrap by connecting to a real device."""
    # pylint does not understand pytest fixtures, so we have to disable the warning
    # pylint: disable=no-member

    def setUp(self):
        """Set up the test environment."""
        self.backend = BluepyBackend()

    @pytest.mark.usefixtures("mac")
    def test_connect(self):
        """Try connecting to a device."""
        self.backend.connect(self.mac)
        self.backend.disconnect()
