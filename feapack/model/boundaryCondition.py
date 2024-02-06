from feapack.typing import IntTuple, FloatTuple

class BoundaryCondition:
    """Definition of a boundary condition (prescribed nodal displacements)."""

    __slots__ = ("_region", "_u", "_v", "_w", "_dofs", "_displacements")

    @property
    def region(self) -> str:
        """The name of the region in which the boundary condition is applied (defined by a node set)."""
        return self._region

    @property
    def u(self) -> float | None:
        """The prescribed nodal displacement along the global X-axis."""
        return self._u

    @property
    def v(self) -> float | None:
        """The prescribed nodal displacement along the global Y-axis."""
        return self._v

    @property
    def w(self) -> float | None:
        """The prescribed nodal displacement along the global Z-axis."""
        return self._w

    @property
    def dofs(self) -> IntTuple:
        """The constrained degrees of freedom."""
        return self._dofs

    @property
    def displacements(self) -> FloatTuple:
        """The prescribed nodal displacements."""
        return self._displacements

    def __init__(self, region: str, u: float | None, v: float | None, w: float | None) -> None:
        """
        Creates a new boundary condition (prescribed nodal displacements) applied in the specified region (defined by
        the name of a node set).
        The boundary condition is defined by its individual components along the global axes.
        """
        self._region: str = region
        self._u: float | None = u
        self._v: float | None = v
        self._w: float | None = w
        self._dofs: IntTuple = tuple(dof for dof, displacement in enumerate((u, v, w)) if displacement is not None)
        self._displacements: FloatTuple = tuple(displacement for displacement in (u, v, w) if displacement is not None)
