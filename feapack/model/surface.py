from operator import itemgetter
from collections.abc import Iterable
from feapack.typing import Int2D, IntTuple, Tuple
from feapack.model import ModelingSpaces, ElementTypes, Node, Material, Section, Element

class Surface:
    """Definition of a finite element surface."""

    __slots__ = (
        "_parent", "_index", "_type", "_localNodeIndices", "_globalNodeIndices", "_nodes", "_section", "_material"
    )

    @property
    def parent(self) -> Element:
        """The parent element containing the surface."""
        return self._parent

    @property
    def index(self) -> Int2D:
        """
        The element surface index.
        A tuple that contains:
        1. The global index of the element that contains the surface.
        2. The local index of the element surface.
        """
        return self._index

    @property
    def type(self) -> ElementTypes:
        """The finite element surface type."""
        return self._type

    @property
    def localNodeIndices(self) -> IntTuple:
        """The local nodal connectivity."""
        return self._localNodeIndices

    @property
    def globalNodeIndices(self) -> IntTuple:
        """The global nodal connectivity."""
        return self._globalNodeIndices

    @property
    def nodeCount(self) -> int:
        """The number of surface nodes."""
        return self._type.nodeCount

    @property
    def dofCount(self) -> int:
        """The total number of surface degrees of freedom."""
        return self._type.dofCount

    @property
    def modelingSpace(self) -> ModelingSpaces:
        """The modeling space in which the surface resides."""
        return self._type.modelingSpace

    @property
    def nodes(self) -> Tuple[Node]:
        """The surface nodes."""
        return itemgetter(*self._localNodeIndices)(self._parent.nodes)

    @property
    def section(self) -> Section:
        """The surface section."""
        return self._parent.section

    @property
    def material(self) -> Material:
        """The surface material."""
        return self._parent.material

    def __init__(
        self, localIndex: int, type: ElementTypes | str | int, localNodeIndices: Iterable[int], parent: Element
    ) -> None:
        """Creates a new element surface based on its type, local nodal connectivity, and parent element."""
        # convert str or int to enum if necessary
        if isinstance(type, str): type = ElementTypes[type]
        elif isinstance(type, int): type = ElementTypes(type)

        # instance variables
        self._parent: Element = parent
        self._index: Int2D = (parent.index, localIndex)
        self._type: ElementTypes = type
        self._localNodeIndices: IntTuple = tuple(localNodeIndices)
        self._globalNodeIndices: IntTuple = itemgetter(*localNodeIndices)(parent.nodeIndices)

        # check if the required number of node indices was given
        if (count := len(self._localNodeIndices)) != self.nodeCount:
            raise ValueError(
                f"surface of type '{self._type.name}' requires exactly {self.nodeCount} nodes for construction, " +
                f"but {count} were given"
            )
