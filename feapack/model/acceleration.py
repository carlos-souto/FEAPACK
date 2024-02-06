import math

class Acceleration:
    """Definition of an acceleration (e.g., due to gravity)."""

    __slots__ = ("_region", "_x", "_y", "_z", "_magnitude")

    @property
    def region(self) -> str:
        """The name of the region in which the load is applied (defined by an element set)."""
        return self._region

    @property
    def x(self) -> float:
        """The acceleration component along the global X-axis."""
        return self._x

    @property
    def y(self) -> float:
        """The acceleration component along the global Y-axis."""
        return self._y

    @property
    def z(self) -> float:
        """The acceleration component along the global Z-axis."""
        return self._z

    @property
    def magnitude(self) -> float:
        """The acceleration magnitude."""
        return self._magnitude

    def __init__(self, region: str, x: float, y: float, z: float) -> None:
        """
        Creates a new acceleration (e.g., due to gravity) applied in the specified region (defined by the name of an
        element set).
        The acceleration is defined by its individual components along the global axes.
        """
        self._region: str = region
        self._x: float = x
        self._y: float = y
        self._z: float = z
        self._magnitude: float = math.sqrt(x*x + y*y + z*z)
