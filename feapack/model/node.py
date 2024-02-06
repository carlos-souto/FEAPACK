from feapack.typing import Float3D, IntTuple

class Node:
    """Definition of a finite element node."""

    __slots__ = (
        "_index", "_coordinates", "_activeLocalDOFs", "_activeGlobalDOFs", "_inactiveLocalDOFs", "_inactiveGlobalDOFs"
    )

    @property
    def index(self) -> int:
        """The node index."""
        return self._index

    @property
    def x(self) -> float:
        """The X-coordinate."""
        return self._coordinates[0]

    @property
    def y(self) -> float:
        """The Y-coordinate."""
        return self._coordinates[1]

    @property
    def z(self) -> float:
        """The Z-coordinate."""
        return self._coordinates[2]

    @property
    def coordinates(self) -> Float3D:
        """The nodal coordinates."""
        return self._coordinates

    @property
    def activeLocalDOFs(self) -> IntTuple:
        """The active local DOFs."""
        if self._activeLocalDOFs is None: raise RuntimeError("accessing unset property")
        return self._activeLocalDOFs

    @property
    def activeGlobalDOFs(self) -> IntTuple:
        """The active global DOFs."""
        if self._activeGlobalDOFs is None: raise RuntimeError("accessing unset property")
        return self._activeGlobalDOFs

    @property
    def inactiveLocalDOFs(self) -> IntTuple:
        """The inactive local DOFs."""
        if self._inactiveLocalDOFs is None: raise RuntimeError("accessing unset property")
        return self._inactiveLocalDOFs

    @property
    def inactiveGlobalDOFs(self) -> IntTuple:
        """The inactive global DOFs."""
        if self._inactiveGlobalDOFs is None: raise RuntimeError("accessing unset property")
        return self._inactiveGlobalDOFs

    def __init__(self, index: int, x: float, y: float, z: float) -> None:
        """Creates a new node based on its nodal coordinates."""
        # instance variables
        self._index: int = index
        self._coordinates: Float3D = (x, y, z)

        # instance variables assigned by the MDB
        self._activeLocalDOFs: IntTuple | None = None
        self._activeGlobalDOFs: IntTuple | None = None
        self._inactiveLocalDOFs: IntTuple | None = None
        self._inactiveGlobalDOFs: IntTuple | None = None
