from enum import Enum, unique

@unique
class SectionTypes(Enum):
    """Available section types."""

    PlaneStress = 201
    """Two-dimensional plane stress section."""

    PlaneStrain = 202
    """Two-dimensional plane strain section."""

    Axisymmetric = 203
    """Two-dimensional axisymmetric section."""

    General = 301
    """General three-dimensional section."""
