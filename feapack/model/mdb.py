import os
from collections.abc import Iterable
from feapack.typing import Int2D
from feapack.io import MeshReader, AbaqusReader
from feapack.model import SectionTypes, Element, Mesh, NodeSet, ElementSet, SurfaceSet, Material, Section, \
    ConcentratedLoad, SurfaceTraction, Pressure, BodyLoad, Acceleration, BoundaryCondition

class MDB:
    """Definition of a model database (MDB)."""

    __slots__ = (
        "_mesh", "_nodeSets", "_elementSets", "_surfaceSets", "_materials", "_sections", "_concentratedLoads",
        "_surfaceTractions", "_pressures", "_bodyLoads", "_accelerations", "_boundaryConditions"
    )

    @classmethod
    def fromFile(cls, filePath: str) -> "MDB":
        """
        Returns a new model database by reading the specified file.
        Notes on MDBs based on third-party software formats:
        * Currently, only Abaqus input files (*.inp) are accepted.
        * The file must define the mesh of a single part, i.e., multiple parts or assemblies are not supported.
        * Only the mesh and node/element sets are imported.
        * 1-based indexing is automatically converted into 0-based indexing when applicable.
        """
        # determine reader based on file extension
        reader: MeshReader
        match ext := os.path.splitext(filePath)[1].lower():
            case ".inp": reader = AbaqusReader(filePath)
            case _: raise ValueError(f"unsupported file extension: '{ext}'")

        # read from file and build MDB
        mdb: MDB = MDB(Mesh.fromReader(reader))
        for name, indices in reader.getNodeSets(): mdb._nodeSets[name] = NodeSet(indices)
        for name, indices in reader.getElementSets(): mdb._elementSets[name] = ElementSet(indices)
        return mdb

    @property
    def mesh(self) -> Mesh:
        """The finite element mesh."""
        return self._mesh

    @property
    def nodeSets(self) -> dict[str, NodeSet]:
        """The node sets."""
        return self._nodeSets

    @property
    def elementSets(self) -> dict[str, ElementSet]:
        """The element sets."""
        return self._elementSets

    @property
    def surfaceSets(self) -> dict[str, SurfaceSet]:
        """The surface sets."""
        return self._surfaceSets

    @property
    def materials(self) -> dict[str, Material]:
        """The materials."""
        return self._materials

    @property
    def sections(self) -> dict[str, Section]:
        """The sections."""
        return self._sections

    @property
    def concentratedLoads(self) -> dict[str, ConcentratedLoad]:
        """The concentrated (nodal) loads."""
        return self._concentratedLoads

    @property
    def surfaceTractions(self) -> dict[str, SurfaceTraction]:
        """The surface tractions."""
        return self._surfaceTractions

    @property
    def pressures(self) -> dict[str, Pressure]:
        """The pressures."""
        return self._pressures

    @property
    def bodyLoads(self) -> dict[str, BodyLoad]:
        """The body loads."""
        return self._bodyLoads

    @property
    def accelerations(self) -> dict[str, Acceleration]:
        """The accelerations."""
        return self._accelerations

    @property
    def boundaryConditions(self) -> dict[str, BoundaryCondition]:
        """The boundary conditions."""
        return self._boundaryConditions

    def __init__(self, mesh: Mesh) -> None:
        """Creates a new model database based on the specified finite element mesh."""
        self._mesh: Mesh = mesh
        self._nodeSets: dict[str, NodeSet] = {}
        self._elementSets: dict[str, ElementSet] = {}
        self._surfaceSets: dict[str, SurfaceSet] = {}
        self._materials: dict[str, Material] = {}
        self._sections: dict[str, Section] = {}
        self._concentratedLoads: dict[str, ConcentratedLoad] = {}
        self._surfaceTractions: dict[str, SurfaceTraction] = {}
        self._pressures: dict[str, Pressure] = {}
        self._bodyLoads: dict[str, BodyLoad] = {}
        self._accelerations: dict[str, Acceleration] = {}
        self._boundaryConditions: dict[str, BoundaryCondition] = {}

    def nodeSet(self, name: str, indices: Iterable[int]) -> None:
        """
        Adds a new node index set to the model database.
        The set is linked to the specified name and contains the specified indices.
        Duplicate indices are removed and the set is sorted.
        """
        if name in self._nodeSets.keys(): raise ValueError(f"name '{name}' is already in use")
        self._nodeSets[name] = NodeSet(indices)

    def elementSet(self, name: str, indices: Iterable[int]) -> None:
        """
        Adds a new element index set to the model database.
        The set is linked to the specified name and contains the specified indices.
        Duplicate indices are removed and the set is sorted.
        """
        if name in self._elementSets.keys(): raise ValueError(f"name '{name}' is already in use")
        self._elementSets[name] = ElementSet(indices)

    def surfaceSet(self, name: str, surfaceNodes: NodeSet | str | Iterable[int]) -> None:
        """
        Adds a new surface index set to the model database.
        The set is linked to the specified name and is built using the indices of the nodes that lie on the surface.
        The nodes that lie on the surface may be specified as a node set, the name of an existing node set, or as any
        iterable of node indices.
        """
        # build index set of nodes that lie on the surface
        nodeIndexSet: set[int]
        if isinstance(surfaceNodes, NodeSet): nodeIndexSet = set(surfaceNodes.indices)
        elif isinstance(surfaceNodes, str): nodeIndexSet = set(self._nodeSets[surfaceNodes].indices)
        else: nodeIndexSet = set(surfaceNodes)

        # build index set of elements connected to the surface nodes
        elementIndexSet: set[int] = set()
        for nodeIndex in nodeIndexSet:
            elementIndexSet.update(self._mesh.nodeToElementsMap[nodeIndex])

        # build index set of element surfaces that make up the whole surface
        surfaceIndexSet: set[Int2D] = set()
        for elementIndex in elementIndexSet:
            element: Element = self._mesh.elements[elementIndex]
            for surfaceIndex, (_, localConnectivity) in enumerate(element.surfaces):
                globalConnectivity: list[int] = [element.nodeIndices[i] for i in localConnectivity]
                if all(nodeIndex in nodeIndexSet for nodeIndex in globalConnectivity):
                    surfaceIndexSet.add((elementIndex, surfaceIndex))

        # save surface index set
        if name in self._surfaceSets.keys(): raise ValueError(f"name '{name}' is already in use")
        self._surfaceSets[name] = SurfaceSet(surfaceIndexSet)

    def material(self, name: str, young: float, poisson: float, density: float = 0.0) -> None:
        """
        Adds a new linear-elastic (Hookean) and isotropic-homogeneous material to the model database.
        The material is linked to the specified name and defined by the specified Young's modulus, Poisson's ratio, and
        mass density.
        """
        if name in self._materials.keys(): raise ValueError(f"name '{name}' is already in use")
        self._materials[name] = Material(young, poisson, density)

    def section(
        self, name: str, region: str, material: str, type: SectionTypes | str | int, thickness: float = 1.0,
        reducedIntegration: bool = False
    ) -> None:
        """
        Adds a new solid section to the model database, linking it to the specified name.
        The section is associated with the specified region, which is defined by the name of an element set.
        A material name must be linked to the section, and the section type must also be specified.
        For plane stress and plane strain type sections, the section thickness can also be defined (by default, a unit
        thickness is assumed).
        A reduced integration flag can also be set to determine if a reduced integration scheme should be used when
        available (by default, full integration is used).
        """
        if name in self._sections.keys(): raise ValueError(f"name '{name}' is already in use")
        self._sections[name] = Section(region, material, type, thickness, reducedIntegration)

    def concentratedLoad(self, name: str, region: str, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """
        Adds a new concentrated (nodal) load to the model database, linking it to the specified name.
        The load is applied to the specified region, which is defined by the name of a node set.
        The load is defined by its individual components along the global axes.
        """
        if name in self._concentratedLoads.keys(): raise ValueError(f"name '{name}' is already in use")
        self._concentratedLoads[name] = ConcentratedLoad(region, x, y, z)

    def surfaceTraction(self, name: str, region: str, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """
        Adds a new surface traction to the model database, linking it to the specified name.
        The load is applied to the specified region, which is defined by the name of a surface set.
        The load is defined by its individual components along the global axes.
        """
        if name in self._surfaceTractions.keys(): raise ValueError(f"name '{name}' is already in use")
        self._surfaceTractions[name] = SurfaceTraction(region, x, y, z)

    def pressure(self, name: str, region: str, magnitude: float) -> None:
        """
        Adds a new pressure to the model database, linking it to the specified name.
        The load is applied to the specified region, which is defined by the name of a surface set.
        The load is defined by its magnitude.
        """
        if name in self._pressures.keys(): raise ValueError(f"name '{name}' is already in use")
        self._pressures[name] = Pressure(region, magnitude)

    def bodyLoad(self, name: str, region: str, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """
        Adds a new body load to the model database, linking it to the specified name.
        The load is applied to the specified region, which is defined by the name of an element set.
        The load is defined by its individual components along the global axes.
        """
        if name in self._bodyLoads.keys(): raise ValueError(f"name '{name}' is already in use")
        self._bodyLoads[name] = BodyLoad(region, x, y, z)

    def acceleration(self, name: str, region: str, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        """
        Adds a new acceleration (e.g., due to gravity) to the model database, linking it to the specified name.
        The acceleration is applied to the specified region, which is defined by the name of an element set.
        The acceleration is defined by its individual components along the global axes.
        """
        if name in self._accelerations.keys(): raise ValueError(f"name '{name}' is already in use")
        self._accelerations[name] = Acceleration(region, x, y, z)

    def boundaryCondition(
        self, name: str, region: str, u: float | None = None, v: float | None = None, w: float | None = None
    ) -> None:
        """
        Adds a new boundary condition (prescribed nodal displacements) to the model database, linking it to the
        specified name.
        The boundary condition is applied to the specified region, which is defined by the name of a node set.
        The boundary condition is defined by its individual components along the global axes.
        """
        if name in self._boundaryConditions.keys(): raise ValueError(f"name '{name}' is already in use")
        self._boundaryConditions[name] = BoundaryCondition(region, u, v, w)

    def _buildDOFs(self) -> None:
        """
        Assigns active and inactive local and global degrees of freedom (DOFs) to each element and node.
        Having the DOFs allows for the reduction of the number of DOFs in the solver phase via static condensation.
        After calling this function, the element/node DOFs may be accessed via, e.g., `element.activeLocalDOFs`.
        Attempting to get such properties before calling this functions results in a runtime error.
        The MDB should be checked/validated before calling this function.
        """
        # build table of active/inactive DOFs
        # each row corresponds to a mesh node
        # each column corresponds to a nodal DOF
        # False: DOF is inactive (due to a prescribed boundary condition)
        # True: DOF is active
        m: int = self.mesh.nodeCount
        n: int = self.mesh.modelingSpace.value
        tableActive: list[list[bool]] = [[True for _ in range(n)] for _ in range(m)]
        for boundaryCondition in self.boundaryConditions.values():
            for dof in boundaryCondition.dofs:
                if 0 <= dof < n:
                    for nodeIndex in self.nodeSets[boundaryCondition.region].indices:
                        tableActive[nodeIndex][dof] = False

        # enumerate each active and inactive DOF
        activeDOFCount: int = 0
        inactiveDOFCount: int = 0
        tableDOFs: list[list[int]] = [[0 for _ in range(n)] for _ in range(m)]
        for i in range(m):
            for j in range(n):
                if tableActive[i][j]:
                    tableDOFs[i][j] = activeDOFCount
                    activeDOFCount += 1
                else:
                    tableDOFs[i][j] = inactiveDOFCount
                    inactiveDOFCount += 1

        # assign to each element
        k: int = self.mesh.elementCount
        elementWiseActiveLocalDOFs: list[list[int]] = [[] for _ in range(k)]
        elementWiseActiveGlobalDOFs: list[list[int]] = [[] for _ in range(k)]
        elementWiseInactiveLocalDOFs: list[list[int]] = [[] for _ in range(k)]
        elementWiseInactiveGlobalDOFs: list[list[int]] = [[] for _ in range(k)]
        for element in self.mesh.elements:
            for localNodeIndex, globalNodeIndex in enumerate(element.nodeIndices):
                for dof in range(n):
                    localDOF: int = localNodeIndex*n + dof
                    globalDOF: int = tableDOFs[globalNodeIndex][dof]
                    if tableActive[globalNodeIndex][dof]:
                        elementWiseActiveLocalDOFs[element.index].append(localDOF)
                        elementWiseActiveGlobalDOFs[element.index].append(globalDOF)
                    else:
                        elementWiseInactiveLocalDOFs[element.index].append(localDOF)
                        elementWiseInactiveGlobalDOFs[element.index].append(globalDOF)

        # assign to each node
        nodeWiseActiveLocalDOFs: list[list[int]] = [[] for _ in range(m)]
        nodeWiseActiveGlobalDOFs: list[list[int]] = [[] for _ in range(m)]
        nodeWiseInactiveLocalDOFs: list[list[int]] = [[] for _ in range(m)]
        nodeWiseInactiveGlobalDOFs: list[list[int]] = [[] for _ in range(m)]
        for node in self.mesh.nodes:
            for dof in range(n):
                localDOF: int = dof
                globalDOF: int = tableDOFs[node.index][dof]
                if tableActive[node.index][dof]:
                    nodeWiseActiveLocalDOFs[node.index].append(localDOF)
                    nodeWiseActiveGlobalDOFs[node.index].append(globalDOF)
                else:
                    nodeWiseInactiveLocalDOFs[node.index].append(localDOF)
                    nodeWiseInactiveGlobalDOFs[node.index].append(globalDOF)

        # store results
        self.mesh._activeDOFCount = activeDOFCount
        self.mesh._inactiveDOFCount = inactiveDOFCount
        for element in self.mesh.elements:
            element._activeLocalDOFs = tuple(elementWiseActiveLocalDOFs[element.index])
            element._activeGlobalDOFs = tuple(elementWiseActiveGlobalDOFs[element.index])
            element._inactiveLocalDOFs = tuple(elementWiseInactiveLocalDOFs[element.index])
            element._inactiveGlobalDOFs = tuple(elementWiseInactiveGlobalDOFs[element.index])
        for node in self.mesh.nodes:
            node._activeLocalDOFs = tuple(nodeWiseActiveLocalDOFs[node.index])
            node._activeGlobalDOFs = tuple(nodeWiseActiveGlobalDOFs[node.index])
            node._inactiveLocalDOFs = tuple(nodeWiseInactiveLocalDOFs[node.index])
            node._inactiveGlobalDOFs = tuple(nodeWiseInactiveGlobalDOFs[node.index])

    def _assignElementProperties(self) -> None:
        """
        Assigns element properties (e.g., materials and sections) to their corresponding elements.
        After calling this function, the element material property, for example, may be accessed via `element.material`.
        Attempting to get such properties before calling this functions results in a runtime error.
        The MDB should be checked/validated before calling this function.
        """
        # nodes
        for element in self.mesh.elements:
            element._nodes = self.mesh.getNodes(element.nodeIndices)

        # materials and sections
        for section in self.sections.values():
            material: Material = self.materials[section.material]
            for elementIndex in self.elementSets[section.region].indices:
                element: Element = self.mesh.elements[elementIndex]
                element._section = section
                element._material = material
