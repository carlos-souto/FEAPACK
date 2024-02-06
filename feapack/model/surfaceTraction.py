import math

class SurfaceTraction:
    """Definition of a surface traction."""

    __slots__ = ("_region", "_x", "_y", "_z", "_magnitude")

    @property
    def region(self) -> str:
        """The name of the region in which the load is applied (defined by a surface set)."""
        return self._region

    @property
    def x(self) -> float:
        """The load component along the global X-axis."""
        return self._x

    @property
    def y(self) -> float:
        """The load component along the global Y-axis."""
        return self._y

    @property
    def z(self) -> float:
        """The load component along the global Z-axis."""
        return self._z

    @property
    def magnitude(self) -> float:
        """The load magnitude."""
        return self._magnitude

    def __init__(self, region: str, x: float, y: float, z: float) -> None:
        """
        Creates a new surface traction applied in the specified region (defined by the name of a surface set).
        The load is defined by its individual components along the global axes.
        """
        self._region: str = region
        self._x: float = x
        self._y: float = y
        self._z: float = z
        self._magnitude: float = math.sqrt(x*x + y*y + z*z)
