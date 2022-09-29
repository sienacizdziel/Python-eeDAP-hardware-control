from abc import ABCMeta, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
# from labthings import StrictLock
import threading
from typing_extensions import Literal

CoordinateType = Tuple[int, int, int]

class AxisLimits(typing.NamedTuple):
    """ Limits of a StageAxis, based on Python-Microscope """

    # TODO: do these need to be floats
    lower: float
    upper: float

class StageAxis(metaclass=ABCMeta):
    """ Single dimension axis for a Stage Device """

# based on Openflexure base stage and Python-Microscope stage classes
class BaseStage(metaclass=ABCMeta):
    """
    Attributes:

        lock (:py:class:`labthings.StrictLock`): Strict lock controlling thread
            access to stage hardware

            TODO change this
    """

    def __init__(self):
        self.lock = threading.RLock()#name="Stage", timeout=None)

    # @abstractmethod
    # def update_settings(self, config: dict):
    #     """Update settings from a config dictionary"""

    # @abstractmethod
    # def read_settings(self):
    #     """Return the current settings as a dictionary"""

    @property
    @abstractmethod
    def state(self):
        """The general state dictionary of the board."""

    @property
    @abstractmethod
    def configuration(self):
        """The general stage configuration."""

    @property
    @abstractmethod
    def n_axes(self):
        """The number of axes this stage has. Should be 2, x,y for Prior stage"""

    @property
    @abstractmethod
    def position(self) -> CoordinateType:
        """The current position, as a list"""

    @property
    def position_map(self) -> Dict[str, int]:
        # return {"x": self.position[0], "y": self.position[1], "z": self.position[2]}
        return {"x": self.position[0], "y": self.position[1]}

    @abstractmethod
    def move_rel(
        self,
        displacement: Union[int, CoordinateType],
        # axis: Optional[Literal["x", "y", "z"]] = None,
        axis: Optional[Literal["x", "y"]] = None,
        # backlash: bool = True,
    ):
        """Make a relative move, optionally correcting for backlash.
        displacement: integer or array/list of 3 integers
        backlash: (default: True) whether to correct for backlash.
        """

    @abstractmethod
    def move_abs(self, final: CoordinateType, **kwargs):
        """Make an absolute move to a position"""

    @abstractmethod
    def zero_position(self):
        """Set the current position to zero"""

    @abstractmethod
    def close(self):
        """Cleanly close communication with the stage"""

    def scan_linear(
        self,
        rel_positions: List[CoordinateType],
        # backlash: bool = True,
        return_to_start: bool = True,
    ):
        """
        Scan through a list of (relative) positions (generator fn)
        rel_positions should be an nx3-element array (or list of 3 element arrays).
        Positions should be relative to the starting position - not a list of relative moves.
        backlash argument is passed to move_rel
        if return_to_start is True (default) we return to the starting position after a
        successful scan.  NB we always attempt to return to the starting position if an
        exception occurs during the scan..
        """
        starting_position = self.position
        rel_positions_array: np.ndarray = np.array(rel_positions)
        # assert rel_positions_array.shape[1] == 3, ValueError(
        #     "Positions should be 3 elements long."
        # )
        assert rel_positions_array.shape[1] == 2, ValueError(
            "Positions should be 2 elements long."
        )
        try:
            self.move_rel(rel_positions_array[0]) #, backlash=backlash)
            yield 0

            for i, step in enumerate(np.diff(rel_positions_array, axis=0)):
                self.move_rel(step) #, backlash=backlash)
                yield i + 1
        except Exception as e:
            return_to_start = True  # always return to start if it went wrong.
            raise e
        finally:
            if return_to_start:
                self.move_abs(starting_position) #, backlash=backlash)

    # def scan_z(self, dz: List[int], **kwargs):
    #     """Scan through a list of (relative) z positions (generator fn)
    #     This function takes a 1D numpy array of Z positions, relative to
    #     the position at the start of the scan, and converts it into an
    #     array of 3D positions with x=y=0.  This, along with all the
    #     keyword arguments, is then passed to ``scan_linear``.
    #     """
    #     return self.scan_linear([(0, 0, z) for z in dz], **kwargs)
