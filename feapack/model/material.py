class Material:
    """Definition of a linear-elastic (Hookean) and isotropic-homogeneous material."""

    __slots__ = ("_young", "_poisson", "_density")

    @property
    def young(self) -> float:
        """The Young's modulus."""
        return self._young

    @property
    def poisson(self) -> float:
        """The Poisson's ratio."""
        return self._poisson

    @property
    def density(self) -> float:
        """The mass density."""
        return self._density

    def __init__(self, young: float, poisson: float, density: float) -> None:
        """
        Creates a new linear-elastic (Hookean) and isotropic-homogeneous material with the specified Young's modulus,
        Poisson's ratio, and mass density.
        """
        self._young: float = young
        self._poisson: float = poisson
        self._density: float = density
