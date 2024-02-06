from collections.abc import Iterable
from feapack.typing import IntTuple

class ElementSet:
    """
    Definition of an element index set.
    The indices are unique and sorted.
    """

    __slots__ = ("_indices",)

    @property
    def indices(self) -> IntTuple:
        """The indices in the set."""
        return self._indices

    def __init__(self, indices: Iterable[int]) -> None:
        """
        Creates a new element index set containing the specified indices.
        Duplicate indices are removed and the index set is sorted.
        """
        self._indices: IntTuple = tuple(sorted(set(indices)))
