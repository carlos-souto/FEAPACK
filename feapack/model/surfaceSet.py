from collections.abc import Iterable
from feapack.typing import Int2D, Tuple

class SurfaceSet:
    """
    Definition of a surface index set.
    The indices are unique and sorted.
    Each index of the set is a tuple that contains:
    1. The global index of the element that contains the surface.
    2. The local index of the element surface.
    """

    __slots__ = ("_indices",)

    @property
    def indices(self) -> Tuple[Int2D]:
        """The indices in the set."""
        return self._indices

    def __init__(self, indices: Iterable[Int2D]) -> None:
        """
        Creates a new surface index set containing the specified indices.
        Duplicate indices are removed and the index set is sorted.
        Each index of the set is a tuple that contains:
        1. The global index of the element that contains the surface.
        2. The local index of the element surface.
        """
        self._indices: Tuple[Int2D] = tuple(sorted(set(indices)))
