from operator import itemgetter
from collections.abc import Iterable
from feapack.typing import Float3D, IntTuple, Tuple
from feapack.model import ModelingSpaces, ElementTypes, Node, Element
from feapack.io import MeshReader

class Mesh:
    """Definition of a finite element mesh."""

    __slots__ = ("_modelingSpace", "_nodes", "_elements", "_nodeToElementsMap", "_activeDOFCount", "_inactiveDOFCount")

    @classmethod
    def fromReader(cls, reader: MeshReader) -> "Mesh":
        """
        Creates a new finite element mesh based on the specified mesh reader for third-party mesh formats.
        Element types from third-party software are automatically converted using `ElementTypes.from3rdParty`.
        Unsupported third-party element types are ignored.
        """
        # map element types from third-party software to supported types, filtering out unsupported element types
        def mapAndFilterElementTypes() -> Iterable[tuple[ElementTypes, IntTuple]]:
            for thirdPartyType, nodeIndices in reader.getElements():
                elementType: ElementTypes | None = ElementTypes.from3rdParty(reader.software, thirdPartyType)
                if elementType is not None: yield elementType, nodeIndices

        # return new mesh object
        return cls(reader.getNodes(), mapAndFilterElementTypes())

    @property
    def modelingSpace(self) -> ModelingSpaces:
        """The modeling space in which the mesh resides."""
        return self._modelingSpace

    @property
    def nodeCount(self) -> int:
        """The number of mesh nodes."""
        return len(self._nodes)

    @property
    def elementCount(self) -> int:
        """The number of mesh elements."""
        return len(self._elements)

    @property
    def nodes(self) -> Tuple[Node]:
        """The mesh nodes."""
        return self._nodes

    @property
    def elements(self) -> Tuple[Element]:
        """The mesh elements."""
        return self._elements

    @property
    def nodeToElementsMap(self) -> Tuple[IntTuple]:
        """A container that maps a node index to the indices of the elements connected to that node."""
        return self._nodeToElementsMap

    @property
    def activeDOFCount(self) -> int:
        """The total number of active DOFs."""
        if self._activeDOFCount is None: raise RuntimeError("accessing unset property")
        return self._activeDOFCount

    @property
    def inactiveDOFCount(self) -> int:
        """The total number of inactive DOFs."""
        if self._inactiveDOFCount is None: raise RuntimeError("accessing unset property")
        return self._inactiveDOFCount

    def __init__(self, nodes: Iterable[Float3D], elements: Iterable[tuple[ElementTypes | str | int, IntTuple]]) -> None:
        """
        Creates a new finite element mesh based on an iterable of nodal coordinates and an iterable of element types and
        corresponding nodal connectivity.
        """
        # convert str or int to enum if necessary
        elements = ((
            ElementTypes[type] if isinstance(type, str) else ElementTypes(type) if isinstance(type, int) else type,
            nodeIndices
        ) for type, nodeIndices in elements)

        # build node array
        self._nodes: Tuple[Node] = tuple(Node(index, x, y, z) for index, (x, y, z) in enumerate(nodes))

        # check for no nodes
        if self.nodeCount == 0:
            raise ValueError("mesh contains no nodes")

        # get modeling space based on nodal coordinates
        self._modelingSpace: ModelingSpaces = ModelingSpaces.fromCoordinates(node.coordinates for node in self._nodes)
        if self._modelingSpace not in (ModelingSpaces.TwoDimensional, ModelingSpaces.ThreeDimensional):
            raise ValueError("a 2D or 3D mesh is required")

        # build element array, filtering out elements with a mismatched modeling space
        self._elements: Tuple[Element] = tuple(
            Element(index, type, nodeIndices) for index, (type, nodeIndices) in enumerate(
                filter(lambda tup: tup[0].modelingSpace == self._modelingSpace, elements)
            )
        )

        # check for no elements
        if self.elementCount == 0:
            raise ValueError("mesh contains no elements")

        # get element indices connected to each mesh node
        nodeToElementsMap: list[list[int]] = [[] for _ in range(self.nodeCount)]
        for element in self._elements:
            for nodeIndex in element.nodeIndices:
                if 0 <= nodeIndex < self.nodeCount: nodeToElementsMap[nodeIndex].append(element.index)
                else: raise ValueError("element referencing non-existent node detected")
        self._nodeToElementsMap: Tuple[IntTuple] = tuple(tuple(list) for list in nodeToElementsMap)

        # check for unconnected nodes
        for nodeIndex, elementIndices in enumerate(self._nodeToElementsMap):
            if len(elementIndices) == 0:
                raise ValueError(f"unconnected node detected: node {nodeIndex} at {self._nodes[nodeIndex].coordinates}")

        # instance variables assigned by the MDB
        self._activeDOFCount: int | None = None
        self._inactiveDOFCount: int | None = None

    def getNodes(self, indices: Iterable[int]) -> Tuple[Node]:
        """Returns the nodes associated with the given indices."""
        return itemgetter(*indices)(self.nodes)

    def getElements(self, indices: Iterable[int]) -> Tuple[Element]:
        """Returns the elements associated with the given indices."""
        return itemgetter(*indices)(self.elements)
