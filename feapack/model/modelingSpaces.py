from enum import Enum, unique
from collections.abc import Iterable
from feapack.typing import Float3D

@unique
class ModelingSpaces(Enum):
    """Available modeling spaces."""

    OneDimensional = 1
    "One-dimensional modeling space."

    TwoDimensional = 2
    "Two-dimensional modeling space."

    ThreeDimensional = 3
    "Three-dimensional modeling space."

    @staticmethod
    def fromCoordinates(coordinates: Iterable[Float3D]) -> "ModelingSpaces":
        """Determines the modeling space from an iterable of nodal coordinates."""
        count: int = 0
        for dim in range(3):
            for xyz in coordinates:
                if xyz[dim] != 0.0:
                    count += 1
                    break
        if count not in (1, 2, 3): raise ValueError("unexpected modeling space")
        return ModelingSpaces(count)
