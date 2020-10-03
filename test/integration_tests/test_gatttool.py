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
