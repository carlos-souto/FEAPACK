from typing import Protocol
from collections.abc import Iterable
from feapack.typing import Float3D, IntTuple

class MeshReader(Protocol):
    """Mesh reader protocol."""

    @property
    def software(self) -> str:
        """The third-party software."""
        ...

    def getNodes(self) -> Iterable[Float3D]:
        """Gets the nodal coordinates from file."""
        ...

    def getElements(self) -> Iterable[tuple[str, IntTuple]]:
        """
        Gets the element types and corresponding nodal connectivity from file.
        Note: 1-based indexing is automatically converted into 0-based indexing when applicable.
        """
        ...

    def getNodeSets(self) -> Iterable[tuple[str, IntTuple]]:
        """
        Gets the node sets from file (names and corresponding node indices).
        Note: 1-based indexing is automatically converted into 0-based indexing when applicable.
        """
        ...

    def getElementSets(self) -> Iterable[tuple[str, IntTuple]]:
        """
        Gets the element sets from file (names and corresponding element indices).
        Note: 1-based indexing is automatically converted into 0-based indexing when applicable.
        """
        ...
