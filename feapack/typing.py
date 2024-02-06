import numpy as np
import numpy.typing as npt
from typing import Annotated

type Int2D = tuple[int, int]
"""A type alias for `tuple[int, int]`."""

type Float2D = tuple[float, float]
"""A type alias for `tuple[float, float]`."""

type Float3D = tuple[float, float, float]
"""A type alias for `tuple[float, float, float]`."""

type IntTuple = tuple[int, ...]
"""A type alias for `tuple[int, ...]`."""

type FloatTuple = tuple[float, ...]
"""A type alias for `tuple[float, ...]`."""

type Tuple[T] = tuple[T, ...]
"""A type alias for `tuple[T, ...]`."""

Int = np.int32
"""Represents an integer number (32-bit)."""

Real = np.float64
"""Represents a real number (64-bit)."""

type IntVector = Annotated[npt.NDArray[Int], ["N"]]
"""A type alias representing a vector of integer numbers."""

type RealVector = Annotated[npt.NDArray[Real], ["N"]]
"""A type alias representing a vector of real numbers."""

type IntMatrix = Annotated[npt.NDArray[Int], ["M", "N"]]
"""A type alias representing a matrix of integer numbers."""

type RealMatrix = Annotated[npt.NDArray[Real], ["M", "N"]]
"""A type alias representing a matrix of real numbers."""
