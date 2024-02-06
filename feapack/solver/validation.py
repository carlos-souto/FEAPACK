from typing import Literal
from collections.abc import Collection
from feapack.model import MDB, ModelingSpaces, SectionTypes

def _checkMesh(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """
    Performs basic checks on the finite element mesh.
    Note: some checks are performed during the initialization of the mesh object.
    """
    # check for undefined or over-defined section assignments
    counts: list[int] = [0]*mdb.mesh.elementCount
    for section in mdb.sections.values():
        if section.region in mdb.elementSets.keys():
            for elementIndex in mdb.elementSets[section.region].indices:
                if 0 <= elementIndex < mdb.mesh.elementCount:
                    counts[elementIndex] += 1
    if counts.count(1) != len(counts):
        errors.append("elements with undefined or over-defined section assignments detected")

def _checkNodeSets(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the node sets."""
    # check for empty sets and invalid indices
    for name, nodeSet in mdb.nodeSets.items():
        if len(nodeSet.indices) == 0:
            warnings.append(f"node set '{name}' is empty")
        elif min(nodeSet.indices) < 0 or max(nodeSet.indices) >= mdb.mesh.nodeCount:
            errors.append(f"node set '{name}' contains invalid indices")

def _checkElementSets(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the element sets."""
    # check for empty sets and invalid indices
    for name, elementSet in mdb.elementSets.items():
        if len(elementSet.indices) == 0:
            warnings.append(f"element set '{name}' is empty")
        elif min(elementSet.indices) < 0 or max(elementSet.indices) >= mdb.mesh.elementCount:
            errors.append(f"element set '{name}' contains invalid indices")

def _checkSurfaceSets(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the surface sets."""
    # check for empty sets and invalid indices
    for name, surfaceSet in mdb.surfaceSets.items():
        if len(surfaceSet.indices) == 0:
            warnings.append(f"surface set '{name}' is empty")
        else:
            for elementIndex, surfaceIndex in surfaceSet.indices:
                if (
                    elementIndex < 0 or elementIndex >= mdb.mesh.elementCount or
                    surfaceIndex < 0 or surfaceIndex >= len(mdb.mesh.elements[elementIndex].surfaces)
                ):
                    errors.append(f"surface set '{name}' contains invalid indices")
                    break

def _checkMaterials(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the materials."""
    # check for invalid material properties
    for name, material in mdb.materials.items():
        if material.young <= 0.0:
            errors.append(f"material '{name}' has a Young's modulus that is less than or equal to zero")
        if material.poisson <= -1.0 or material.poisson >= 0.5:
            errors.append(f"material '{name}' has a Poisson's ratio that lies outside the open interval of (-1.0, 0.5)")
        if material.density < 0.0:
            errors.append(f"material '{name}' has a mass density that is less than zero")

def _checkSections(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the sections."""
    # check for invalid references and properties
    sectionTypes2D = SectionTypes.PlaneStress, SectionTypes.PlaneStrain, SectionTypes.Axisymmetric
    sectionTypes3D = SectionTypes.General,
    for name, section in mdb.sections.items():
        if section.region not in mdb.elementSets.keys():
            errors.append(f"section '{name}' references a non-existent element set '{section.region}'")
        if section.material not in mdb.materials.keys():
            errors.append(f"section '{name}' references a non-existent material '{section.material}'")
        if (
            (mdb.mesh.modelingSpace == ModelingSpaces.TwoDimensional and section.type not in sectionTypes2D) or
            (mdb.mesh.modelingSpace == ModelingSpaces.ThreeDimensional and section.type not in sectionTypes3D)
        ):
            errors.append(f"section '{name}' of type '{section.type.name}' is invalid for the current modeling space")
        if section.type in (SectionTypes.PlaneStress, SectionTypes.PlaneStrain) and section.thickness <= 0.0:
            errors.append(f"section '{name}' of type '{section.type.name}' has negative or no thickness")

def _checkConcentratedLoads(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the concentrated loads."""
    # check for invalid references and null loads
    for name, load in mdb.concentratedLoads.items():
        if load.region not in mdb.nodeSets.keys():
            errors.append(f"concentrated load '{name}' references a non-existent node set '{load.region}'")
        if load.magnitude == 0.0:
            warnings.append(f"concentrated load '{name}' has a magnitude of zero")
        elif load.z != 0.0 and mdb.mesh.modelingSpace == ModelingSpaces.TwoDimensional:
            warnings.append(f"concentrated load '{name}' has a nonzero component along the Z-axis that will be ignored")

def _checkSurfaceTractions(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the surface tractions."""
    # check for invalid references and null loads
    for name, load in mdb.surfaceTractions.items():
        if load.region not in mdb.surfaceSets.keys():
            errors.append(f"surface traction '{name}' references a non-existent surface set '{load.region}'")
        if load.magnitude == 0.0:
            warnings.append(f"surface traction '{name}' has a magnitude of zero")
        elif load.z != 0.0 and mdb.mesh.modelingSpace == ModelingSpaces.TwoDimensional:
            warnings.append(f"surface traction '{name}' has a nonzero component along the Z-axis that will be ignored")

def _checkPressures(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the pressures."""
    # check for invalid references and null loads
    for name, load in mdb.pressures.items():
        if load.region not in mdb.surfaceSets.keys():
            errors.append(f"pressure '{name}' references a non-existent surface set '{load.region}'")
        if load.magnitude == 0.0:
            warnings.append(f"pressure '{name}' has a magnitude of zero")

def _checkBodyLoads(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the body loads."""
    # check for invalid references and null loads
    for name, load in mdb.bodyLoads.items():
        if load.region not in mdb.elementSets.keys():
            errors.append(f"body load '{name}' references a non-existent element set '{load.region}'")
        if load.magnitude == 0.0:
            warnings.append(f"body load '{name}' has a magnitude of zero")
        elif load.z != 0.0 and mdb.mesh.modelingSpace == ModelingSpaces.TwoDimensional:
            warnings.append(f"body load '{name}' has a nonzero component along the Z-axis that will be ignored")

def _checkAccelerations(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the accelerations."""
    # check for invalid references and null loads
    for name, load in mdb.accelerations.items():
        if load.region not in mdb.elementSets.keys():
            errors.append(f"acceleration '{name}' references a non-existent element set '{load.region}'")
        if load.magnitude == 0.0:
            warnings.append(f"acceleration '{name}' has a magnitude of zero")
        elif load.z != 0.0 and mdb.mesh.modelingSpace == ModelingSpaces.TwoDimensional:
            warnings.append(f"acceleration '{name}' has a nonzero component along the Z-axis that will be ignored")

def _checkBoundaryConditions(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks on the boundary conditions."""
    # check for invalid references and null boundary conditions
    for name, boundary in mdb.boundaryConditions.items():
        if boundary.region not in mdb.nodeSets.keys():
            errors.append(f"boundary condition '{name}' references a non-existent node set '{boundary.region}'")
        if len(boundary.dofs) == 0:
            warnings.append(f"boundary condition '{name}' has no constrained degrees of freedom")
        elif max(boundary.dofs) == 2 and mdb.mesh.modelingSpace == ModelingSpaces.TwoDimensional:
            warnings.append(f"boundary condition '{name}' has constraints along the Z-axis that will be ignored")

def _checkFrequencyAnalysis(mdb: MDB, errors: list[str], warnings: list[str]) -> None:
    """Performs basic checks for a frequency analysis."""
    # check mass density
    for material in mdb.materials.values():
        if material.density == 0.0:
            errors.append("the mass density must be specified for a frequency analysis")
            break

    # check loads
    for x in (mdb.concentratedLoads, mdb.surfaceTractions, mdb.pressures, mdb.accelerations, mdb.bodyLoads):
        if len(x) > 0:
            warnings.append("any type of loading is ignored during a frequency analysis")
            break

    # check boundary conditions
    for boundaryCondition in mdb.boundaryConditions.values():
        if any(x != 0.0 for x in boundaryCondition.displacements):
            warnings.append("any prescribed nodal displacement is assumed to be zero during a frequency analysis")
            break

def checkMDB(mdb: MDB, analysis: Literal["static", "frequency", "buckling"]) -> tuple[Collection[str], Collection[str]]:
    """Performs basic checks on the specified model database and returns error and warning messages."""
    # error and warning messages
    errors: list[str] = []
    warnings: list[str] = []

    # common checks
    for check in (
        _checkMesh, _checkNodeSets, _checkElementSets, _checkSurfaceSets, _checkMaterials, _checkSections,
        _checkConcentratedLoads, _checkSurfaceTractions, _checkPressures, _checkBodyLoads, _checkAccelerations,
        _checkBoundaryConditions
    ): check(mdb, errors, warnings)
    if analysis == "frequency": _checkFrequencyAnalysis(mdb, errors, warnings)

    # done
    return errors, warnings
