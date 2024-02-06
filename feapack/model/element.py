from collections.abc import Iterable
from feapack.typing import IntTuple, Tuple
from feapack.model import ModelingSpaces, ElementTypes, Node, Section, Material

class Element:
    """Definition of a finite element."""

    __slots__ = (
        "_index", "_type", "_nodeIndices", "_nodes", "_section", "_material", "_activeLocalDOFs", "_activeGlobalDOFs",
        "_inactiveLocalDOFs", "_inactiveGlobalDOFs"
    )

    @property
    def index(self) -> int:
        """The element index."""
        return self._index

    @property
    def type(self) -> ElementTypes:
        """The finite element type."""
        return self._type

    @property
    def nodeIndices(self) -> IntTuple:
        """The nodal connectivity."""
        return self._nodeIndices

    @property
    def nodeCount(self) -> int:
        """The number of element nodes."""
        return self._type.nodeCount

    @property
    def dofCount(self) -> int:
        """The total number of element degrees of freedom."""
        return self._type.dofCount

    @property
    def modelingSpace(self) -> ModelingSpaces:
        """The modeling space in which the element resides."""
        return self._type.modelingSpace

    @property
    def surfaces(self) -> Tuple[tuple[ElementTypes, IntTuple]]:
        """The surfaces of the element (surface types and corresponding local nodal connectivity)."""
        return self._type.surfaces

    @property
    def nodes(self) -> Tuple[Node]:
        """The element nodes."""
        if self._nodes is None: raise RuntimeError("accessing unset property")
        return self._nodes

    @property
    def section(self) -> Section:
        """The element section."""
        if self._section is None: raise RuntimeError("accessing unset property")
        return self._section

    @property
    def material(self) -> Material:
        """The element material."""
        if self._material is None: raise RuntimeError("accessing unset property")
        return self._material

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

    def __init__(self, index: int, type: ElementTypes | str | int, nodeIndices: Iterable[int]) -> None:
        """Creates a new element based on its type and nodal connectivity."""
        # convert str or int to enum if necessary
        if isinstance(type, str): type = ElementTypes[type]
        elif isinstance(type, int): type = ElementTypes(type)

        # instance variables
        self._index: int = index
        self._type: ElementTypes = type
        self._nodeIndices: IntTuple = tuple(nodeIndices)

        # instance variables assigned by the MDB
        self._nodes: Tuple[Node] | None = None
        self._material: Material | None = None
        self._section: Section | None = None
        self._activeLocalDOFs: IntTuple | None = None
        self._activeGlobalDOFs: IntTuple | None = None
        self._inactiveLocalDOFs: IntTuple | None = None
        self._inactiveGlobalDOFs: IntTuple | None = None

        # check if the required number of node indices was given
        if (count := len(self._nodeIndices)) != self.nodeCount:
            raise ValueError(
                f"element of type '{self._type.name}' requires exactly {self.nodeCount} nodes for construction, " +
                f"but {count} were given"
            )
