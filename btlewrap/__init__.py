"""Public interface for btlewrap."""
import sys
from btlewrap.version import __version__  # noqa: F401

# This check must be run first, so that it fails before loading the other modules.
# Otherwise we do not get a clean error message.
if sys.version_info < (3, 4):
    raise ValueError(
        "this library requires at least Python 3.4. "
        + "You're running version {}.{} from {}.".format(
            sys.version_info.major, sys.version_info.minor, sys.executable
        )
    )

# pylint: disable=wrong-import-position
from btlewrap.base import (  # noqa: F401,E402
    BluetoothBackendException,
)

from btlewrap.bluepy import (
    BluepyBackend,
)
from btlewrap.gatttool import (
    GatttoolBackend,
)
from btlewrap.pygatt import (
    PygattBackend,
)


_ALL_BACKENDS = [BluepyBackend, GatttoolBackend, PygattBackend]


def available_backends():
    """Returns a list of all available backends."""
    return [b for b in _ALL_BACKENDS if b.check_backend()]
