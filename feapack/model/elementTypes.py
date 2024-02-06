from enum import Enum, unique
from feapack.model import ModelingSpaces
from feapack.typing import IntTuple, Tuple

@unique
class ElementTypes(Enum):
    """Available finite element types."""

    Line2 = 102
    """One-dimensional first-order interpolation element with 2 nodes."""

    Line3 = 103
    """One-dimensional second-order interpolation element with 3 nodes."""

    Plane3 = 203
    """Two-dimensional first-order interpolation element with 3 nodes."""

    Plane4 = 204
    """Two-dimensional first-order interpolation element with 4 nodes."""

    Plane6 = 206
    """Two-dimensional second-order interpolation element with 6 nodes."""

    Plane8 = 208
    """Two-dimensional second-order interpolation element with 8 nodes."""

    Volume4 = 304
    """Three-dimensional first-order interpolation element with 4 nodes."""

    Volume6 = 306
    """Three-dimensional first-order interpolation element with 6 nodes."""

    Volume8 = 308
    """Three-dimensional first-order interpolation element with 8 nodes."""

    Volume10 = 310
    """Three-dimensional second-order interpolation element with 10 nodes."""

    Volume15 = 315
    """Three-dimensional second-order interpolation element with 15 nodes."""

    Volume20 = 320
    """Three-dimensional second-order interpolation element with 20 nodes."""

    @staticmethod
    def from3rdParty(software: str, elementType: str) -> "ElementTypes | None":
        """
        Returns the corresponding finite element type given a type from a third-party software.
        If the specified third-party software or its finite element type are unsupported, returns `None`.
        """
        match software.upper():
            case "ABAQUS":
                match elementType.upper():
                    case "CPS3" | "CPE3" | "CAX3":
                        return ElementTypes.Plane3
                    case "CPS4" | "CPE4" | "CAX4" | "CPS4R" | "CPE4R" | "CAX4R":
                        return ElementTypes.Plane4
                    case "CPS6" | "CPE6" | "CAX6":
                        return ElementTypes.Plane6
                    case "CPS8" | "CPE8" | "CAX8" | "CPS8R" | "CPE8R" | "CAX8R":
                        return ElementTypes.Plane8
                    case "C3D4":
                        return ElementTypes.Volume4
                    case "C3D6":
                        return ElementTypes.Volume6
                    case "C3D8" | "C3D8R":
                        return ElementTypes.Volume8
                    case "C3D10":
                        return ElementTypes.Volume10
                    case "C3D15":
                        return ElementTypes.Volume15
                    case "C3D20" | "C3D20R":
                        return ElementTypes.Volume20
                    case _:
                        return None
            case _:
                return None

    @property
    def cellType(self) -> int:
        """The corresponding VTK cell type."""
        match self:
            case ElementTypes.Line2:    return  3 # VTK_LINE
            case ElementTypes.Line3:    return 21 # VTK_QUADRATIC_EDGE
            case ElementTypes.Plane3:   return  5 # VTK_TRIANGLE
            case ElementTypes.Plane4:   return  9 # VTK_QUAD
            case ElementTypes.Plane6:   return 22 # VTK_QUADRATIC_TRIANGLE
            case ElementTypes.Plane8:   return 23 # VTK_QUADRATIC_QUAD
            case ElementTypes.Volume4:  return 10 # VTK_TETRA
            case ElementTypes.Volume6:  return 13 # VTK_WEDGE
            case ElementTypes.Volume8:  return 12 # VTK_HEXAHEDRON
            case ElementTypes.Volume10: return 24 # VTK_QUADRATIC_TETRA
            case ElementTypes.Volume15: return 26 # VTK_QUADRATIC_WEDGE
            case ElementTypes.Volume20: return 25 # VTK_QUADRATIC_HEXAHEDRON

    @property
    def nodeCount(self) -> int:
        """The number of element nodes."""
        match self:
            case ElementTypes.Line2:    return  2
            case ElementTypes.Line3:    return  3
            case ElementTypes.Plane3:   return  3
            case ElementTypes.Plane4:   return  4
            case ElementTypes.Plane6:   return  6
            case ElementTypes.Plane8:   return  8
            case ElementTypes.Volume4:  return  4
            case ElementTypes.Volume6:  return  6
            case ElementTypes.Volume8:  return  8
            case ElementTypes.Volume10: return 10
            case ElementTypes.Volume15: return 15
            case ElementTypes.Volume20: return 20

    @property
    def dofCount(self) -> int:
        """The total number of element degrees of freedom."""
        match self:
            case ElementTypes.Line2:    return  2
            case ElementTypes.Line3:    return  3
            case ElementTypes.Plane3:   return  6
            case ElementTypes.Plane4:   return  8
            case ElementTypes.Plane6:   return 12
            case ElementTypes.Plane8:   return 16
            case ElementTypes.Volume4:  return 12
            case ElementTypes.Volume6:  return 18
            case ElementTypes.Volume8:  return 24
            case ElementTypes.Volume10: return 30
            case ElementTypes.Volume15: return 45
            case ElementTypes.Volume20: return 60

    @property
    def modelingSpace(self) -> ModelingSpaces:
        """The modeling space in which the element resides."""
        match self:
            case ElementTypes.Line2:    return ModelingSpaces.OneDimensional
            case ElementTypes.Line3:    return ModelingSpaces.OneDimensional
            case ElementTypes.Plane3:   return ModelingSpaces.TwoDimensional
            case ElementTypes.Plane4:   return ModelingSpaces.TwoDimensional
            case ElementTypes.Plane6:   return ModelingSpaces.TwoDimensional
            case ElementTypes.Plane8:   return ModelingSpaces.TwoDimensional
            case ElementTypes.Volume4:  return ModelingSpaces.ThreeDimensional
            case ElementTypes.Volume6:  return ModelingSpaces.ThreeDimensional
            case ElementTypes.Volume8:  return ModelingSpaces.ThreeDimensional
            case ElementTypes.Volume10: return ModelingSpaces.ThreeDimensional
            case ElementTypes.Volume15: return ModelingSpaces.ThreeDimensional
            case ElementTypes.Volume20: return ModelingSpaces.ThreeDimensional

    @property
    def surfaces(self) -> "Tuple[tuple[ElementTypes, IntTuple]]":
        """The surfaces of the element (surface types and corresponding local nodal connectivity)."""
        match self:
            case ElementTypes.Line2 | ElementTypes.Line3:
                raise NotImplementedError("0D surface in 1D space")
            case ElementTypes.Plane3:
                return (
                    (ElementTypes.Line2, (0, 1)),
                    (ElementTypes.Line2, (1, 2)),
                    (ElementTypes.Line2, (2, 0)),
                )
            case ElementTypes.Plane4:
                return (
                    (ElementTypes.Line2, (0, 1)),
                    (ElementTypes.Line2, (1, 2)),
                    (ElementTypes.Line2, (2, 3)),
                    (ElementTypes.Line2, (3, 0)),
                )
            case ElementTypes.Plane6:
                return (
                    (ElementTypes.Line3, (0, 1, 3)),
                    (ElementTypes.Line3, (1, 2, 4)),
                    (ElementTypes.Line3, (2, 0, 5)),
                )
            case ElementTypes.Plane8:
                return (
                    (ElementTypes.Line3, (0, 1, 4)),
                    (ElementTypes.Line3, (1, 2, 5)),
                    (ElementTypes.Line3, (2, 3, 6)),
                    (ElementTypes.Line3, (3, 0, 7)),
                )
            case ElementTypes.Volume4:
                return (
                    (ElementTypes.Plane3, (0, 2, 1)),
                    (ElementTypes.Plane3, (0, 3, 2)),
                    (ElementTypes.Plane3, (0, 1, 3)),
                    (ElementTypes.Plane3, (1, 2, 3)),
                )
            case ElementTypes.Volume6:
                return (
                    (ElementTypes.Plane3, (0, 2, 1)),
                    (ElementTypes.Plane3, (3, 4, 5)),
                    (ElementTypes.Plane4, (0, 3, 5, 2)),
                    (ElementTypes.Plane4, (0, 1, 4, 3)),
                    (ElementTypes.Plane4, (1, 2, 5, 4)),
                )
            case ElementTypes.Volume8:
                return (
                    (ElementTypes.Plane4, (0, 1, 5, 4)),
                    (ElementTypes.Plane4, (1, 2, 6, 5)),
                    (ElementTypes.Plane4, (2, 3, 7, 6)),
                    (ElementTypes.Plane4, (3, 0, 4, 7)),
                    (ElementTypes.Plane4, (3, 2, 1, 0)),
                    (ElementTypes.Plane4, (4, 5, 6, 7)),
                )
            case ElementTypes.Volume10:
                return (
                    (ElementTypes.Plane6, (0, 2, 1, 6, 5, 4)),
                    (ElementTypes.Plane6, (0, 3, 2, 7, 9, 6)),
                    (ElementTypes.Plane6, (0, 1, 3, 4, 8, 7)),
                    (ElementTypes.Plane6, (1, 2, 3, 5, 9, 8)),
                )
            case ElementTypes.Volume15:
                return (
                    (ElementTypes.Plane6, (0, 2, 1, 8,  7,  6)),
                    (ElementTypes.Plane6, (3, 4, 5, 9, 10, 11)),
                    (ElementTypes.Plane8, (0, 3, 5, 2, 12, 11, 14,  8)),
                    (ElementTypes.Plane8, (0, 1, 4, 3,  6, 13,  9, 12)),
                    (ElementTypes.Plane8, (1, 2, 5, 4,  7, 14, 10, 13)),
                )
            case ElementTypes.Volume20:
                return (
                    (ElementTypes.Plane8, (0, 1, 5, 4,  8, 17, 12, 16)),
                    (ElementTypes.Plane8, (1, 2, 6, 5,  9, 18, 13, 17)),
                    (ElementTypes.Plane8, (2, 3, 7, 6, 10, 19, 14, 18)),
                    (ElementTypes.Plane8, (3, 0, 4, 7, 11, 16, 15, 19)),
                    (ElementTypes.Plane8, (3, 2, 1, 0, 10,  9,  8, 11)),
                    (ElementTypes.Plane8, (4, 5, 6, 7, 12, 13, 14, 15)),
                )
