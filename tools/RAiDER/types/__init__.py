"""Types specific to RAiDER."""

from typing import Literal, Union

import numpy as np
from pyproj import CRS


LookDir = Literal['right', 'left']
TimeInterpolationMethod = Literal['none', 'center_time', 'azimuth_time_grid']
CRSLike = Union[CRS, str, int]


# Helpers for type annotating the dimensions of a numpy array.
# When you use these, your type checker will alert you when an annotated array
# is used in a way inconsistent with its dimensions.
FloatArray1D = np.ndarray[tuple[int], np.dtype[np.floating]]
FloatArray2D = np.ndarray[tuple[int, int], np.dtype[np.floating]]
FloatArray3D = np.ndarray[tuple[int, int, int], np.dtype[np.floating]]
# ... (repeat the pattern as needed for higher dimensions)

# Any number of dimensions -- when ndim is not able to be known ahead of time
FloatArrayND = np.ndarray[tuple[int, ...], np.dtype[np.floating]]
