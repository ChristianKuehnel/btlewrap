"""Test pygatt backend."""

import unittest
from btlewrap import PygattBackend


class TestGatttool(unittest.TestCase):
    """Test gatttool by mocking gatttool.

    These tests do NOT require hardware!
    time.sleep is mocked in some cases to speed up the retry-feature."""

    def test_supports_scanning(self):
        """Check if scanning is set correctly."""
        self.assertFalse(PygattBackend.supports_scanning())
