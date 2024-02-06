from feapack.model import SectionTypes

class Section:
    """Definition of a solid section."""

    __slots__ = ("_region", "_material", "_type", "_thickness", "_reducedIntegration")

    @property
    def region(self) -> str:
        """The name of the associated region (defined by an element set)."""
        return self._region

    @property
    def material(self) -> str:
        """The name of the associated material."""
        return self._material

    @property
    def type(self) -> SectionTypes:
        """The section type."""
        return self._type

    @property
    def thickness(self) -> float:
        """The section thickness (valid for planar sections)."""
        return self._thickness

    @property
    def reducedIntegration(self) -> bool:
        """A boolean flag that determines if reduced integration should be used when available."""
        return self._reducedIntegration

    def __init__(
        self, region: str, material: str, type: SectionTypes | str | int, thickness: float, reducedIntegration: bool
    ) -> None:
        """
        Creates a new solid section associated with the specified region (defined by the name of an element set).
        A material name must also be linked to the section, and the section type must also be specified.
        For plane stress and plane strain type sections, the section thickness should be defined.
        A reduced integration flag can also be set to determine if reduced integration should be used when available.
        """
        if isinstance(type, str): type = SectionTypes[type]
        elif isinstance(type, int): type = SectionTypes(type)
        self._region: str = region
        self._material: str = material
        self._type: SectionTypes = type
        self._thickness: float = thickness
        self._reducedIntegration: bool = reducedIntegration
