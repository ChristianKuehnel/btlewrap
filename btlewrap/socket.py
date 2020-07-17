"""Backend using L2CAP and HCI sockets, primarily intended for FreeBSD.
"""

import ctypes
import ctypes.util
import logging
import socket
import struct
import time
from typing import List, Tuple, Callable
from btlewrap.base import AbstractBackend, BluetoothBackendException


_LOGGER = logging.getLogger(__name__)
SOL_HCI_RAW = 0x0802
SOL_HCI_RAW_FILTER = 1
NG_HCI_EVENT_MASK_LE = 0x2000000000000000
LE_META_EVENT = 0x3e
EVT_LE_ADVERTISING_REPORT = 0x02
OGF_LE_CTL = 0x8
OCF_LE_SET_EVENT_MASK = 0x1
OCF_LE_SET_SCAN_PARAMETERS = 0xB
OCF_LE_SET_SCAN_ENABLE = 0xC


class SockaddrL2cap(ctypes.Structure):
    _fields_ = [
        ('l2cap_len', ctypes.c_char),
        ('l2cap_family', ctypes.c_char),
        ('l2cap_psm', ctypes.c_int16),
        ('l2cap_bdaddr', ctypes.c_int8 * 6),
        ('l2cap_cid', ctypes.c_int16),
        ('l2cap_bdaddr_type', ctypes.c_int8),
    ]


class SockaddrHci(ctypes.Structure):
    _fields_ = [
        ('hci_len', ctypes.c_char),
        ('hci_family', ctypes.c_char),
        ('hci_node', ctypes.c_char * 32),
    ]


class HciRawFilter(ctypes.Structure):
    _fields_ = [
        ('packet_mask', ctypes.c_uint32),
        ('event_mask', ctypes.c_uint64),
    ]


def hci_connect(libc, adapter: str):
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
    adr = SockaddrHci(ctypes.sizeof(SockaddrHci), socket.AF_BLUETOOTH,
        (adapter + 'hci').ljust(32, '\0').encode('utf-8'))
    if libc.bind(sock.fileno(), ctypes.pointer(adr), ctypes.sizeof(SockaddrHci)) != 0:
        raise BluetoothBackendException('Error {}'.format(ctypes.get_errno()))
    if libc.connect(sock.fileno(), ctypes.pointer(adr), ctypes.sizeof(SockaddrHci)) != 0:
        raise BluetoothBackendException('Error {}'.format(ctypes.get_errno()))
    filter = HciRawFilter(0, NG_HCI_EVENT_MASK_LE)
    if libc.setsockopt(sock.fileno(),
                       SOL_HCI_RAW, SOL_HCI_RAW_FILTER,
                       ctypes.pointer(filter), ctypes.sizeof(HciRawFilter)) != 0:
        raise BluetoothBackendException('Error {}'.format(ctypes.get_errno()))
    return sock


def hci_send_cmd(sock, gf: int, cf: int, data: bytes):
    opcode = (((gf & 0x3f) << 10) | (cf & 0x3ff))
    sock.send(struct.pack('<BHB', 1, opcode, len(data)) + data)


def hci_set_ble_mask(sock):
    try:
        hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_EVENT_MASK,
            struct.pack('<Q', 0x1f))
    except PermissionError:
        _LOGGER.debug('No permission to set LE mask, set LE_Enable using hccontrol as root')


class SocketBackend(AbstractBackend):
    """Backend for btlewrap using L2CAP and HCI sockets."""

    def __init__(self, adapter: str = 'ubt0', address_type: str = 'public'):
        """Create new instance of the backend."""
        super(SocketBackend, self).__init__(adapter, address_type)
        self._libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
        self._sock = None
        self._hci = hci_connect(self._libc, adapter)
        hci_set_ble_mask(self._hci)

    def connect(self, mac: str):
        """Connect to a device."""
        bdaddr = bytearray(map(lambda x: int(x, 16), reversed(mac.split(':'))))
        adr = SockaddrL2cap(ctypes.sizeof(SockaddrL2cap), socket.AF_BLUETOOTH,
            0, (ctypes.c_int8 * 6).from_buffer(bdaddr), 4, 1)
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
        res = self._libc.connect(sock.fileno(), ctypes.pointer(adr),
            ctypes.sizeof(SockaddrL2cap))
        if res != 0:
            raise BluetoothBackendException('Error {}'.format(ctypes.get_errno()))
        self._sock = sock

    def disconnect(self):
        """Disconnect from a device if connected."""
        if self._sock is None:
            return

        self._sock.close()
        self._sock = None

    def read_handle(self, handle: int) -> bytes:
        """Read a handle from the device.

        You must be connected to do this.
        """
        if self._sock is None:
            raise BluetoothBackendException('not connected to backend')

        self._sock.send(struct.pack('<BH', 0x0a, handle))

        reply = self._sock.recv(255)
        if reply[0] == 0x0b:
            return reply[1:]

        raise BluetoothBackendException(
            'ATT code {:02X}, expected 0x0b'.format(reply[0]))

    def write_handle(self, handle: int, value: bytes):
        """Write a handle from the device.

        You must be connected to do this.
        """
        if self._sock is None:
            raise BluetoothBackendException('not connected to backend')

        self._sock.send(struct.pack('<BH', 0x12, handle) + value)

        reply = self._sock.recv(255)
        if reply != b'\x13':
            raise BluetoothBackendException(
                'ATT code 0x{:02X}, expected 0x13'.format(reply[0]))

    def wait_for_notification(self, handle: int, delegate, notification_timeout: float):
        """Wait for a notification from the device.

        You must be connected to do this.
        """
        if self._sock is None:
            raise BluetoothBackendException('not connected to backend')
        raise BluetoothBackendException('TODO')

    @staticmethod
    def check_backend() -> bool:
        """Check if the backend is available."""
        if not 'AF_BLUETOOTH' in dir(socket):
            return False
        if not 'SOCK_SEQPACKET' in dir(socket) or not 'SOCK_RAW' in dir(socket):
            return False
        if not 'BTPROTO_L2CAP' in dir(socket) or not 'BTPROTO_HCI' in dir(socket):
            return False
        return True

    @staticmethod
    def scan_for_devices(timeout: float, adapter='ubt0') -> List[Tuple[str, str]]:
        """Scan for Bluetooth Low Energy devices.

        Note: this needs to run as root!"""
        libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
        hci = hci_connect(libc, adapter)
        hci_set_ble_mask(hci)
        hci_send_cmd(hci, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE,
            struct.pack('BB', False, False))
        params = struct.pack(
            "<BHHBB",
            1, # active
            0x10, # interval
            0x10, # window
            0, # public address
            0) # filter parameters
        hci_send_cmd(hci, OGF_LE_CTL, OCF_LE_SET_SCAN_PARAMETERS,
            params)
        hci_send_cmd(hci, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE,
            struct.pack('BB', True, False))
        result = {}
        read_time = time.monotonic()
        while timeout > 0:
            print(timeout)
            hci.settimeout(timeout)
            data = None
            try:
                data = hci.recv(255)
            except socket.timeout:
                continue
            timeout -= time.monotonic() - read_time
            read_time = time.monotonic()
            if data[1] != LE_META_EVENT or data[3] != EVT_LE_ADVERTISING_REPORT:
                continue
            mac = ':'.join(map(lambda x: '{:02X}'.format(x), reversed(data[7:13])))
            name = None
            attrs = data[14:]
            while len(attrs) > 2:
                length = attrs[0]
                if attrs[1] == 9:
                    name = str(attrs[2:length + 1])
                attrs = attrs[length + 1:]
            result[mac] = name
        hci_send_cmd(hci, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE,
            struct.pack('BB', False, False))
        return [(k, v) for k, v in result.items()]
