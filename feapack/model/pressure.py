class Pressure:
    """Definition of a pressure."""

    __slots__ = ("_region", "_magnitude")

    @property
    def region(self) -> str:
        """The name of the region in which the load is applied (defined by a surface set)."""
        return self._region

    @property
    def magnitude(self) -> float:
        """The load magnitude."""
        return self._magnitude

    def __init__(self, region: str, magnitude: float) -> None:
        """
        Creates a new pressure applied in the specified region (defined by the name of a surface set).
        The load is defined by its magnitude.
        """
        self._region: str = region
        self._magnitude: float = magnitude
