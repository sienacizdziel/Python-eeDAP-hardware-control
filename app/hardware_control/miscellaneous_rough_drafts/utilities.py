# from openflexure microscope utilities

import base64
import copy
import logging
import sys
import time
from contextlib import contextmanager
from typing import Dict, List, Optional, Sequence, Tuple, Type, Union

import numpy as np

# TypedDict was added to typing in 3.8. Use typing_extensions for <3.8
if sys.version_info >= (3, 8):
    from typing import TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import TypedDict

def axes_to_array(
    coordinate_dictionary: Dict[str, Optional[int]],
    # axis_keys: Sequence[str] = ("x", "y", "z"),
    axis_keys: Sequence[str] = ("x", "y"),
    base_array: Optional[List[int]] = None,
    asint: bool = True,
) -> List[int]:
    """Takes key-value pairs of a JSON value, and maps onto an array
    
    This is designed to take a dictionary like `{"x": 1, "y":2}`
    and return a list like `[1, 2]` to convert between the argument
    format expected by most of our stages, and the usual argument
    format in JSON.
    
    `axis_keys` is an ordered sequence of key names to extract from
    the input dictionary.

    `base_array` specifies a default value for each axis.  It must 
    have the same length as `axis_keys`.
    
    `asint` casts values to integers if it is `True` (default).
    
    Missing keys, or keys that have a `None` value will be left
    at the specified default value, or zero if none is specified.
    """
    # If no base array is given
    if not base_array:
        # Create an array of zeros
        base_array = [0] * len(axis_keys)
    else:
        # Create a copy of the passed base_array
        base_array = copy.copy(base_array)

    # Do the mapping
    for axis, key in enumerate(axis_keys):
        if key in coordinate_dictionary:
            value = coordinate_dictionary[key]
            if value is None:
                # Values set to None should be treated as if they
                # are missing
                # i.e. we leave the default value in place.
                break
            if asint:
                value = int(value)
            base_array[axis] = value

    return base_array
