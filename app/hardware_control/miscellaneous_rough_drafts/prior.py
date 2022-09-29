# from msilib.schema import Error
import threading
import serial
# import logging

# based on openflexure mock.py
import logging
import time
from collections.abc import Iterable
from typing import Optional, Tuple, Union

import numpy as np
from typing_extensions import Literal

from base import BaseStage
from utilities import axes_to_array

class _PriorConnection:
    """Wraps serial connection with a reentrant lock
    
    This class wraps serial.Serial, for the stage's connection via Serial Port
    
    On Dr. Blenman's computer, use port COM4"""
    def __init__(self, port: str) -> None: #, baudrate: int, timeout: float) -> None:
        self._serial = serial.Serial(
            port=port,
            baudrate=9600, # based on eeDAP source code
            timeout=3, # also based on eeDAP source code
            # bytesize=serial.EIGHTBITS, # --> because not included in eeDAP source code
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )
        self._lock = threading.RLock()
        with self._lock:
            # The command / does nothing other than getting a response
            # from all devices in the chain.  This seems to be the
            # most innocent command we can use.
            self._serial.write(b"/\n")
            lines = self._serial.readlines()
        if not all([l.startswith(b"@") for l in lines]):
            raise RuntimeError(
                "'%s' does not respond like a Prior device" % port
            )

    @property
    def lock(self) -> threading.RLock:
        return self._lock

    def write(self, data: bytes) -> int:
        with self.lock:
            return self._serial.write(data)

    def readline(self, size: int = -1) -> bytes:
        with self.lock:
            return self._serial.readline(size)

class PriorStage(BaseStage):
    # def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
    def __init__(self, port=None, **kwargs):
        BaseStage.__init__(self)

        self.port=port

        # self._position = [0, 0, 0]
        self._position = [0, 0]
        # self._n_axis = 3
        self._n_axis = 2
        # self._backlash = None

    @property
    def state(self):
        """The general state dictionary of the board."""
        state = {"position": self.position_map}
        return state

    @property
    def configuration(self):
        return {}

    # def update_settings(self, config: dict):
    #     """Update settings from a config dictionary"""
        # Set backlash. Expects a dictionary with axis labels
        # if "backlash" in config:
        #     # Construct backlash array
        #     # backlash = axes_to_array(config["backlash"], ["x", "y", "z"], [0, 0, 0])
        #     backlash = axes_to_array(config["backlash"], ["x", "y"], [0, 0])
        #     self.backlash = backlash

    # TODO fix this
    # def read_settings(self) -> dict:
    #     """Return the current settings as a dictionary"""
    #     # blsh = self.backlash.tolist()
    #     # config = {"backlash": {"x": blsh[0], "y": blsh[1], "z": blsh[2]}}
    #     # config = {"backlash": {"x": blsh[0], "y": blsh[1]}}
    #     config = {"x": blsh[0], "y": blsh[1]}
    #     return config

    @property
    def n_axes(self):
        return self._n_axis

    @property
    def position(self):
        print(self._position)
        return self._position

    # @property
    # def backlash(self):
    #     if self._backlash is not None:
    #         return self._backlash
    #     else:
    #         return np.array([0] * self.n_axes)

    # @backlash.setter
    # def backlash(self, blsh):
    #     if blsh is None:
    #         self._backlash = None
    #     elif isinstance(blsh, Iterable):
    #         assert len(blsh) == self.n_axes
    #         self._backlash = np.array(blsh)
    #     else:
    #         self._backlash = np.array([int(blsh)] * self.n_axes, dtype=np.int)

    def move_rel(
        self,
        # displacement: Union[int, Tuple[int, int, int]],
        displacement: Union[int, Tuple[int, int]],
        # axis: Optional[Literal["x", "y", "z"]] = None,
        axis: Optional[Literal["x", "y"]] = None,
        # backlash: bool = True,
    ):
        time.sleep(0.5)
        if axis:
            # Displacement MUST be an integer if axis name is specified
            if not isinstance(displacement, int):
                raise TypeError(
                    "Displacement must be an integer when axis is specified"
                )
            # Axis name MUST be x, y
            # if axis not in ("x", "y", "z"):
            #     raise ValueError("axis must be one of x, y, or z")
            if axis not in ("x", "y"):
                raise ValueError("axis must be one of x or y")
            move = (
                displacement if axis == "x" else 0,
                displacement if axis == "y" else 0,
                # displacement if axis == "z" else 0,
            )
            displacement = move

        initial_move = np.array(displacement, dtype=np.integer)

        self._position = list(np.array(self._position) + np.array(initial_move))
        logging.debug(np.array(self._position) + np.array(initial_move))
        logging.debug("New position: %s", self._position)

    def move_abs(self, final, **kwargs):
        time.sleep(0.5)

        self._position = list(final)
        logging.debug("New position: %s", self._position)

    def zero_position(self):
        """Set the current position to zero"""
        # self._position = [0, 0, 0]
        self._position = [0, 0]

    def close(self):
        pass


# based on https://www.micron.ox.ac.uk/software/microscope/_modules/microscope/controllers/zaber.html#ZaberDeviceType
# _logger = logging.getLogger(__name__)

# _AT_CODE = ord(b"@")
# _SPACE_CODE = ord(b" ")


# class _PriorReply:
#     """Wraps a Prior reply to easily index its multiple fields. """

#     def __init__(self, data: bytes) -> None:
#         self._data = data
#         if (
#             data[0] != _AT_CODE
#             or data[-2:] != b"\r\n"
#             or any([data[i] != _SPACE_CODE for i in (3, 5, 8, 13, 16)])
#         ):
#             raise ValueError("Not a valid reply from a Zaber device")

#     @property
#     def address(self) -> bytes:
#         """The start of reply with device address and space."""
#         return self._data[1:3]

#     @property
#     def flag(self) -> bytes:
#         """The reply flag indicates if the message was accepted or rejected.

#         Can be `b"OK"` (accepted) or `b"RJ"` (rejected).  If rejected,
#         the response property will be one word with the reason why.
#         """
#         return self._data[6:8]

#     @property
#     def status(self) -> bytes:
#         """``b"BUSY"`` when the axis is moving and ``b"IDLE"`` otherwise.

#         If the reply message applies to the whole device, the status
#         is `b"BUSY"` if any axis is busy and `b"IDLE"` if all axes are
#         idle.
#         """
#         return self._data[9:13]

#     @property
#     def warning(self) -> bytes:
#         """The highest priority warning currently active.

#         This will be `b'--'` under normal conditions.  Anything else
#         is a warning.
#         """
#         return self._data[14:16]

#     @property
#     def response(self) -> bytes:
#         # Assumes no checksum
#         return self._data[17:-2]

# class _PriorConnection:
#     """Wraps serial connection with a reentrant lock
    
#     This class wraps serial.Serial, for the stage's connection via Serial Port
    
#     On Dr. Blenman's computer, use port COM4"""
#     def __init__(self, port: str) -> None: #, baudrate: int, timeout: float) -> None:
#         self._serial = serial.Serial(
#             port=port,
#             # baudrate=baudrate,
#             # timeout=timeout,
#             bytesize=serial.EIGHTBITS,
#             stopbits=serial.STOPBITS_ONE,
#             parity=serial.PARITY_NONE,
#             xonxoff=False,
#             rtscts=False,
#             dsrdtr=False,
#         )
#         self._lock = threading.RLock()
#         with self._lock:
#             # The command / does nothing other than getting a response
#             # from all devices in the chain.  This seems to be the
#             # most innocent command we can use.
#             self._serial.write(b"/\n")
#             lines = self._serial.readlines()
#         if not all([l.startswith(b"@") for l in lines]):
#             raise RuntimeError(
#                 "'%s' does not respond like a Zaber device" % port
#             )

#     @property
#     def lock(self) -> threading.RLock:
#         return self._lock

#     def write(self, data: bytes) -> int:
#         with self.lock:
#             return self._serial.write(data)

#     def readline(self, size: int = -1) -> bytes:
#         with self.lock:
#             return self._serial.readline(size)

# class _PriorDeviceConnection:
#     """A Prior connection to control a single device.

#     Only one is needed because we are only using the Prior ProScan III stage atm

#     This class provides a Python interface to the Prior commands.  It
#     also does the routing of commands to the correct device in the
#     chain.

#     Args:
#         conn: the :class:`_PriorConnection` instance for this device.
#         device_address: the device address for the specific device.
#             This is the number used at the start of all Zaber
#             commands.
#     """

#     def __init__(self, conn: _PriorConnection, device_address: int) -> None:
#         self._conn = conn
#         self._address_bytes = b"%02d" % device_address

#     def _validate_reply(self, reply: _PriorReply) -> None:
#         if reply.address != self._address_bytes:
#             raise RuntimeError(
#                 "received reply from a device with different"
#                 " address (%s instead of %s)"
#                 % (reply.address.decode(), self._address_bytes.decode())
#             )
#         if reply.flag != b"OK":
#             raise RuntimeError(
#                 "command rejected because '%s'" % reply.response.decode()
#             )

#     def command(self, command: bytes, axis: int = 0) -> _PriorReply:
#         """Send command and return reply.

#         Args:
#             command: a bytes array with the command and its
#                 parameters.
#             axis: the axis number to send the command.  If zero, the
#                 command is executed by all axis in the device.
#         """
#         # We do not need to check whether axis number is valid because
#         # the device will reject the command with BADAXIS if so.
#         with self._conn.lock:
#             self._conn.write(
#                 b"/%s %1d %s\n" % (self._address_bytes, axis, command)
#             )
#             data = self._conn.readline()
#         reply = _PriorReply(data)
#         self._validate_reply(reply)
#         return reply

#     def is_busy(self) -> bool:
#         return self.command(b"").status == b"BUSY"

#     def wait_until_idle(self, timeout: float = 10.0) -> None:
#         """Wait, or error, until device is idle.

#         A device is busy if *any* of its axis is busy.
#         """
#         sleep_interval = 0.1
#         for _ in range(int(timeout / sleep_interval)):
#             if not self.is_busy():
#                 break
#             time.sleep(sleep_interval)
#         else:
#             raise Error("device still busy after %f seconds" % timeout)
#             # raise microscope.DeviceError(
#             #     "device still busy after %f seconds" % timeout
#             # )

#     def get_number_axes(self) -> int:
#         """Reports the number of axes in the device."""
#         return int(self.command(b"get system.axiscount").response)

#     def been_homed(self, axis: int = 0) -> bool:
#         """True if all axes, or selected axis, has been homed."""
#         reply = self.command(b"get limit.home.triggered", axis)
#         return all([int(x) for x in reply.response.split()])

#     def home(self, axis: int = 0) -> None:
#         """Move the axis to the home position."""
#         self.command(b"home", axis)

#     def get_rotation_length(self, axis: int) -> int:
#         """Number of microsteps needed to complete one full rotation.

#         This is only valid on controllers and rotary devices including
#         filter wheels and filter cube turrets.
#         """
#         return int(self.command(b"get limit.cycle.dist", axis).response)

#     def get_index_distance(self, axis: int) -> int:
#         """The distance between consecutive index positions."""
#         return int(self.command(b"get motion.index.dist", axis).response)

#     def get_current_index(self, axis: int) -> int:
#         """The current index number or zero if between index positions."""
#         return int(self.command(b"get motion.index.num", axis).response)

#     def move_to_index(self, axis: int, index: int) -> None:
#         self.command(b"move index %d" % index, axis)

#     def move_to_absolute_position(self, axis: int, position: int) -> None:
#         self.command(b"move abs %d" % position, axis)

#     def move_by_relative_position(self, axis: int, position: int) -> None:
#         self.command(b"move rel %d" % position, axis)

#     def get_absolute_position(self, axis: int) -> int:
#         """Current absolute position of an axis, in microsteps."""
#         return int(self.command(b"get pos", axis).response)

#     def get_limit_max(self, axis: int) -> int:
#         """The maximum position the device can move to, in microsteps."""
#         return int(self.command(b"get limit.max", axis).response)

#     def get_limit_min(self, axis: int) -> int:
#         """The minimum position the device can move to, in microsteps."""
#         return int(self.command(b"get limit.min", axis).response)


