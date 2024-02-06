import numpy as np
import feapack.solver.isoparametric as iso
from typing import Any
from multiprocessing import Pool
from collections.abc import Iterable, Sequence, Callable
from feapack.model import MDB, Node, Element, Surface, SectionTypes
from feapack.typing import Float3D, IntTuple, Tuple, Int, IntVector, Real, RealVector, RealMatrix
from feapack.solver import SparseCSR

#-----------------------------------------------------------------------------------------------------------------------
# LOCAL MATRICES AND VECTORS
#-----------------------------------------------------------------------------------------------------------------------

def coordinateMatrix(element: Element | Surface) -> RealMatrix:
    """Returns the matrix of element nodal coordinates."""
    X: RealMatrix = np.zeros(shape=(element.nodeCount, 3), dtype=Real)
    for i, node in enumerate(element.nodes): X[i, :] = node.coordinates
    return X

def displacementVector(element: Element, Ua: RealVector, Ub: RealVector) -> RealVector:
    """Returns the element nodal displacement vector."""
    U: RealVector = np.zeros(shape=(element.dofCount,), dtype=Real)
    U[element.activeLocalDOFs,] = Ua[element.activeGlobalDOFs,]
    U[element.inactiveLocalDOFs,] = Ub[element.inactiveGlobalDOFs,]
    return U

def displacementMatrix(element: Element, vecU: RealVector) -> RealMatrix:
    """Returns the element nodal displacement matrix."""
    matU: RealMatrix = np.zeros(shape=(element.nodeCount, 3), dtype=Real)
    count: int = int(element.dofCount/element.nodeCount)
    for i in range(element.nodeCount):
        for j in range(count):
            k: int = i*count + j
            matU[i, j] = vecU[k]
    return matU

def stressStrainMatrix(element: Element) -> RealMatrix:
    """
    Returns the stress-strain matrix.
    Note: working with engineering shear strain.
    """
    # material constants
    E: float = element.material.young    # Young's modulus
    ν: float = element.material.poisson  # Poisson's ratio
    λ: float = (E*ν)/((1 + ν)*(1 - 2*ν)) # Lamé's 1st modulus
    μ: float = E/(2*(1 + ν))             # Lamé's 2nd modulus (shear modulus)
    α: float = E/(1 - ν*ν)               # constants for convenience...
    β: float = α*ν
    γ: float = 2*μ + λ

    # build stress-strain matrix
    D: RealMatrix
    match element.section.type:
        case SectionTypes.PlaneStress:
            D = np.array((
                (α, β, 0),
                (β, α, 0),
                (0, 0, μ),
            ), dtype=Real)
        case SectionTypes.PlaneStrain | SectionTypes.Axisymmetric:
            D = np.array((
                (γ, λ, λ, 0),
                (λ, γ, λ, 0),
                (λ, λ, γ, 0),
                (0, 0, 0, μ),
            ), dtype=Real)
        case SectionTypes.General:
            D = np.array((
                (γ, λ, λ, 0, 0, 0),
                (λ, γ, λ, 0, 0, 0),
                (λ, λ, γ, 0, 0, 0),
                (0, 0, 0, μ, 0, 0),
                (0, 0, 0, 0, μ, 0),
                (0, 0, 0, 0, 0, μ),
            ), dtype=Real)
    return D

def strainDisplacementMatrix(element: Element, coord: RealVector, N: RealVector, Nx: RealMatrix) -> RealMatrix:
    """Returns the strain-displacement matrix."""
    B: RealMatrix
    match element.section.type:
        case SectionTypes.PlaneStress:
            B = np.zeros(shape=(3, element.dofCount), dtype=Real)
            for i in range(element.nodeCount):
                j: int = i*2
                B[:, j:j+2] = (
                    (Nx[0, i],      0.0),
                    (     0.0, Nx[1, i]),
                    (Nx[1, i], Nx[0, i]),
                )
        case SectionTypes.PlaneStrain:
            B = np.zeros(shape=(4, element.dofCount), dtype=Real)
            for i in range(element.nodeCount):
                j: int = i*2
                B[:, j:j+2] = (
                    (Nx[0, i],      0.0),
                    (     0.0, Nx[1, i]),
                    (     0.0,      0.0),
                    (Nx[1, i], Nx[0, i]),
                )
        case SectionTypes.Axisymmetric:
            B = np.zeros(shape=(4, element.dofCount), dtype=Real)
            for i in range(element.nodeCount):
                j: int = i*2
                B[:, j:j+2] = (
                    (     Nx[0, i],      0.0),
                    (          0.0, Nx[1, i]),
                    (N[i]/coord[0],      0.0),
                    (     Nx[1, i], Nx[0, i]),
                )
        case SectionTypes.General:
            B = np.zeros(shape=(6, element.dofCount), dtype=Real)
            for i in range(element.nodeCount):
                j: int = i*3
                B[:, j:j+3] = (
                    (Nx[0, i],      0.0,      0.0),
                    (     0.0, Nx[1, i],      0.0),
                    (     0.0,      0.0, Nx[2, i]),
                    (     0.0, Nx[2, i], Nx[1, i]),
                    (Nx[2, i],      0.0, Nx[0, i]),
                    (Nx[1, i], Nx[0, i],      0.0),
                )
    return B

def interpolationMatrix(element: Element | Surface, N: RealVector) -> RealMatrix:
    """Returns the element/surface interpolation matrix."""
    indices: Iterable[int] = element.localNodeIndices if isinstance(element, Surface) else range(element.nodeCount)
    m: int = element.parent.modelingSpace.value if isinstance(element, Surface) else element.modelingSpace.value
    n: int = element.parent.dofCount if isinstance(element, Surface) else element.dofCount
    I: RealMatrix = np.eye(m, dtype=Real)
    H: RealMatrix = np.zeros(shape=(m, n), dtype=Real)
    for k, i in enumerate(indices):
        j: int = i*m
        H[:, j:j+m] = I*N[k]
    return H

def stiffnessMatrix(element: Element) -> RealMatrix:
    """Returns the element stiffness matrix."""
    K: RealMatrix = np.zeros(shape=(element.dofCount, element.dofCount), dtype=Real)
    D: RealMatrix = stressStrainMatrix(element)
    X: RealMatrix = coordinateMatrix(element)
    for intPt, weight in zip(*iso.integrationPoints(element)):
        coord, N, Nx, vol = iso.evaluateElement(element, X, intPt, weight)
        B: RealMatrix = strainDisplacementMatrix(element, coord, N, Nx)
        K += np.matmul(B.T, np.matmul(D, B))*vol
    return K

def massMatrix(element: Element) -> RealMatrix:
    """Returns the element mass matrix."""
    M: RealMatrix = np.zeros(shape=(element.dofCount, element.dofCount), dtype=Real)
    X: RealMatrix = coordinateMatrix(element)
    ρ: float = element.material.density
    for intPt, weight in zip(*iso.integrationPoints(element)):
        _, N, _, vol = iso.evaluateElement(element, X, intPt, weight)
        H: RealMatrix = interpolationMatrix(element, N)
        M += np.matmul(H.T, H)*(ρ*vol)
    return M

def stressStiffnessMatrix(element: Element, Ua: RealVector, Ub: RealVector) -> RealMatrix:
    """Returns the element stress-stiffness matrix."""
    S: RealMatrix = np.zeros(shape=(element.dofCount, element.dofCount), dtype=Real)
    D: RealMatrix = stressStrainMatrix(element)
    X: RealMatrix = coordinateMatrix(element)
    vecU: RealVector = displacementVector(element, Ua, Ub)
    matU: RealMatrix = displacementMatrix(element, vecU)
    X += matU # updated lagrange approach
    for intPt, weight in zip(*iso.integrationPoints(element)):
        coord, N, Nx, vol = iso.evaluateElement(element, X, intPt, weight)
        B: RealMatrix = strainDisplacementMatrix(element, coord, N, Nx)
        ε: RealVector = np.matmul(B, vecU)
        σ: RealVector = np.matmul(D, ε)
        # build G
        G: RealMatrix = np.zeros(shape=(9, element.dofCount), dtype=Real)
        count: int = int(element.dofCount/element.nodeCount)
        for i in range(element.nodeCount):
            for j in range(count):
                for k in range(count):
                    G[k*3 + j, i*count + j] = Nx[k, i]
        # build Σ
        match element.section.type:
            case SectionTypes.PlaneStress:
                σ11, σ22, σ12 = σ
                σ33 = σ23 = σ31 = 0.0
            case SectionTypes.PlaneStrain | SectionTypes.Axisymmetric:
                σ11, σ22, σ33, σ12 = σ
                σ23 = σ31 = 0.0
            case SectionTypes.General:
                σ11, σ22, σ33, σ23, σ31, σ12 = σ
        Σ: RealMatrix = np.array((
            (σ11, 0.0, 0.0, σ12, 0.0, 0.0, σ31, 0.0, 0.0),
            (0.0, σ11, 0.0, 0.0, σ12, 0.0, 0.0, σ31, 0.0),
            (0.0, 0.0, σ11, 0.0, 0.0, σ12, 0.0, 0.0, σ31),
            (σ12, 0.0, 0.0, σ22, 0.0, 0.0, σ23, 0.0, 0.0),
            (0.0, σ12, 0.0, 0.0, σ22, 0.0, 0.0, σ23, 0.0),
            (0.0, 0.0, σ12, 0.0, 0.0, σ22, 0.0, 0.0, σ23),
            (σ31, 0.0, 0.0, σ23, 0.0, 0.0, σ33, 0.0, 0.0),
            (0.0, σ31, 0.0, 0.0, σ23, 0.0, 0.0, σ33, 0.0),
            (0.0, 0.0, σ31, 0.0, 0.0, σ23, 0.0, 0.0, σ33),
        ), dtype=Real)
        # integration
        S += np.matmul(G.T, np.matmul(Σ, G))*vol
    return S

def surfaceLoadVector(surface: Surface, magnitude: float = 0.0, components: Float3D = (0.0, 0.0, 0.0)) -> RealVector:
    """
    Returns the element surface load vector.
    Notes:
    * For a pressure, specify the optional `magnitude` parameter only.
    * For a surface traction, specify the optional `components` parameter only.
    """
    Ps: RealVector = np.zeros(shape=(surface.parent.dofCount,), dtype=Real)
    Xs: RealMatrix = coordinateMatrix(surface)
    for intPt, weight in zip(*iso.integrationPoints(surface)):
        _, N, n, area = iso.evaluateSurface(surface, Xs, intPt, weight)
        Hs: RealMatrix = interpolationMatrix(surface, N)
        Fs: RealVector = (-n*magnitude + np.array(components, dtype=Real))[:surface.parent.modelingSpace.value]
        Ps += np.matmul(Hs.T, Fs)*area
    return Ps

def bodyLoadVector(element: Element, components: Float3D) -> RealVector:
    """Returns the element body load vector."""
    Fb: RealVector = np.array(components, dtype=Real)[:element.modelingSpace.value]
    Pb: RealVector = np.zeros(shape=(element.dofCount,), dtype=Real)
    X: RealMatrix = coordinateMatrix(element)
    for intPt, weight in zip(*iso.integrationPoints(element)):
        _, N, _, vol = iso.evaluateElement(element, X, intPt, weight)
        H: RealMatrix = interpolationMatrix(element, N)
        Pb += np.matmul(H.T, Fb)*vol
    return Pb

def internalForceVector(element: Element, Ua: RealVector, Ub: RealVector) -> tuple[RealVector, RealMatrix, RealMatrix]:
    """
    Returns the element internal force vector.
    Also computes the basic components of strain and stress at the element integration points.
    """
    intPts, weights = iso.integrationPoints(element)
    F: RealVector = np.zeros(shape=(element.dofCount,), dtype=Real)
    D: RealMatrix = stressStrainMatrix(element)
    X: RealMatrix = coordinateMatrix(element)
    U: RealVector = displacementVector(element, Ua, Ub)
    ε: RealMatrix = np.zeros(shape=(D.shape[1], intPts.shape[0]), dtype=Real)
    σ: RealMatrix = np.zeros(shape=(D.shape[0], intPts.shape[0]), dtype=Real)
    for i, (intPt, weight) in enumerate(zip(intPts, weights)):
        coord, N, Nx, vol = iso.evaluateElement(element, X, intPt, weight)
        B: RealMatrix = strainDisplacementMatrix(element, coord, N, Nx)
        ε[:, i] = np.matmul(B, U)
        σ[:, i] = np.matmul(D, ε[:, i])
        F += np.matmul(B.T, σ[:, i])*vol
    return F, ε, σ

#-----------------------------------------------------------------------------------------------------------------------
# ASSEMBLAGE
#-----------------------------------------------------------------------------------------------------------------------

def loop[T](procedure: Callable[..., T], arguments: Iterable[Tuple[Any]], processes: int) -> Sequence[T]:
    """
    Executes the specified procedure once for each entry in the sequence of arguments and returns the sequence of
    results. This may be performed in parallel by using multiple processes.
    """
    if processes > 1:
        with Pool(processes) as pool:
            return pool.starmap(procedure, arguments)
    else:
        return [*map(lambda x: procedure(*x), arguments)]

def assembleMatrix(
    elements: Sequence[Element], matrices: Sequence[RealMatrix], activeDOFCount: int, inactiveDOFCount: int
) -> tuple[SparseCSR, SparseCSR, SparseCSR, SparseCSR]:
    """Assembles dense element matrices into a sparse system matrix."""
    # with static condensation (Guyan reduction), a system matrix has the following format:
    # M = | Maa Mab |
    #     | Mba Mbb |
    # where Maa, Mab, Mba, and Mbb are sub-matrices
    # moreover, the subscripts a and b are related to the active and inactive DOFs, respectively

    # determine the size of the COO-type data arrays
    size_aa: int = 0
    size_ab: int = 0
    size_ba: int = 0
    size_bb: int = 0
    for element in elements:
        size_aa += len(element.activeLocalDOFs  )*len(element.activeLocalDOFs  )
        size_ab += len(element.activeLocalDOFs  )*len(element.inactiveLocalDOFs)
        size_ba += len(element.inactiveLocalDOFs)*len(element.activeLocalDOFs  )
        size_bb += len(element.inactiveLocalDOFs)*len(element.inactiveLocalDOFs)

    # allocate COO-type storage (Maa)
    rows_aa: IntVector = np.zeros(shape=(size_aa,), dtype=Int)
    cols_aa: IntVector = np.zeros(shape=(size_aa,), dtype=Int)
    vals_aa: RealVector = np.zeros(shape=(size_aa,), dtype=Real)

    # allocate COO-type storage (Mab)
    rows_ab: IntVector = np.zeros(shape=(size_ab,), dtype=Int)
    cols_ab: IntVector = np.zeros(shape=(size_ab,), dtype=Int)
    vals_ab: RealVector = np.zeros(shape=(size_ab,), dtype=Real)

    # allocate COO-type storage (Mba)
    rows_ba: IntVector = np.zeros(shape=(size_ba,), dtype=Int)
    cols_ba: IntVector = np.zeros(shape=(size_ba,), dtype=Int)
    vals_ba: RealVector = np.zeros(shape=(size_ba,), dtype=Real)

    # allocate COO-type storage (Mbb)
    rows_bb: IntVector = np.zeros(shape=(size_bb,), dtype=Int)
    cols_bb: IntVector = np.zeros(shape=(size_bb,), dtype=Int)
    vals_bb: RealVector = np.zeros(shape=(size_bb,), dtype=Real)

    # fill COO-type arrays (includes repeated matrix entries, which are then added in the COO to CSR conversion)
    i_aa: int = 0
    i_ab: int = 0
    i_ba: int = 0
    i_bb: int = 0
    for element, A in zip(elements, matrices):
        alDOFs: IntTuple = element.activeLocalDOFs
        agDOFs: IntTuple = element.activeGlobalDOFs
        ilDOFs: IntTuple = element.inactiveLocalDOFs
        igDOFs: IntTuple = element.inactiveGlobalDOFs
        j_aa: int = i_aa + len(alDOFs)*len(alDOFs)
        j_ab: int = i_ab + len(alDOFs)*len(ilDOFs)
        j_ba: int = i_ba + len(ilDOFs)*len(alDOFs)
        j_bb: int = i_bb + len(ilDOFs)*len(ilDOFs)
        (r_aa, c_aa), v_aa = np.meshgrid(agDOFs, agDOFs), A[np.ix_(alDOFs, alDOFs)]
        (r_ab, c_ab), v_ab = np.meshgrid(agDOFs, igDOFs), A[np.ix_(alDOFs, ilDOFs)]
        (r_ba, c_ba), v_ba = np.meshgrid(igDOFs, agDOFs), A[np.ix_(ilDOFs, alDOFs)]
        (r_bb, c_bb), v_bb = np.meshgrid(igDOFs, igDOFs), A[np.ix_(ilDOFs, ilDOFs)]
        rows_aa[i_aa:j_aa] = r_aa.T.flat; cols_aa[i_aa:j_aa] = c_aa.T.flat; vals_aa[i_aa:j_aa] = v_aa.flat
        rows_ab[i_ab:j_ab] = r_ab.T.flat; cols_ab[i_ab:j_ab] = c_ab.T.flat; vals_ab[i_ab:j_ab] = v_ab.flat
        rows_ba[i_ba:j_ba] = r_ba.T.flat; cols_ba[i_ba:j_ba] = c_ba.T.flat; vals_ba[i_ba:j_ba] = v_ba.flat
        rows_bb[i_bb:j_bb] = r_bb.T.flat; cols_bb[i_bb:j_bb] = c_bb.T.flat; vals_bb[i_bb:j_bb] = v_bb.flat
        i_aa = j_aa
        i_ab = j_ab
        i_ba = j_ba
        i_bb = j_bb

    # convert COO to CSR and return
    Maa: SparseCSR = SparseCSR(activeDOFCount,   activeDOFCount,   rows_aa, cols_aa, vals_aa)
    Mab: SparseCSR = SparseCSR(activeDOFCount,   inactiveDOFCount, rows_ab, cols_ab, vals_ab)
    Mba: SparseCSR = SparseCSR(inactiveDOFCount, activeDOFCount,   rows_ba, cols_ba, vals_ba)
    Mbb: SparseCSR = SparseCSR(inactiveDOFCount, inactiveDOFCount, rows_bb, cols_bb, vals_bb)
    return Maa, Mab, Mba, Mbb

def assembleVector(
    elements: Sequence[Element], vectors: Sequence[RealVector], activeDOFCount: int, inactiveDOFCount: int
) -> tuple[RealVector, RealVector]:
    """Assembles element vectors into a system vector."""
    # with static condensation (Guyan reduction), a system vector has the following format:
    # V = | Va |
    #     | Vb |
    # where Va and Vb are sub-vectors
    # moreover, the subscripts a and b are related to the active and inactive DOFs, respectively
    Va: RealVector = np.zeros(shape=(activeDOFCount,), dtype=Real)
    Vb: RealVector = np.zeros(shape=(inactiveDOFCount,), dtype=Real)
    for element, V in zip(elements, vectors):
        Va[element.activeGlobalDOFs,] += V[element.activeLocalDOFs,]
        Vb[element.inactiveGlobalDOFs,] += V[element.inactiveLocalDOFs,]
    return Va, Vb

def assembleStiffnessMatrix(mdb: MDB, processes: int) -> tuple[SparseCSR, SparseCSR, SparseCSR, SparseCSR]:
    """
    Assembles the system's global stiffness matrix via the direct stiffness method.
    Assembly may be performed in parallel for each element by using multiple processes.
    """
    # compute each element matrix and assemble them into a global system matrix
    matrices: Sequence[RealMatrix] = loop(stiffnessMatrix, zip(mdb.mesh.elements), processes)
    Kaa, Kab, Kba, Kbb = assembleMatrix(mdb.mesh.elements, matrices, mdb.mesh.activeDOFCount, mdb.mesh.inactiveDOFCount)
    return Kaa, Kab, Kba, Kbb

def assembleMassMatrix(mdb: MDB, processes: int) -> tuple[SparseCSR, SparseCSR, SparseCSR, SparseCSR]:
    """
    Assembles the system's global mass matrix via the direct stiffness method.
    Assembly may be performed in parallel for each element by using multiple processes.
    """
    # compute each element matrix and assemble them into a global system matrix
    matrices: Sequence[RealMatrix] = loop(massMatrix, zip(mdb.mesh.elements), processes)
    Maa, Mab, Mba, Mbb = assembleMatrix(mdb.mesh.elements, matrices, mdb.mesh.activeDOFCount, mdb.mesh.inactiveDOFCount)
    return Maa, Mab, Mba, Mbb

def assembleStressStiffnessMatrix(mdb: MDB, Ua: RealVector, Ub: RealVector, processes: int) -> \
    tuple[SparseCSR, SparseCSR, SparseCSR, SparseCSR]:
    """
    Assembles the system's global stress-stiffness matrix via the direct stiffness method.
    Assembly may be performed in parallel for each element by using multiple processes.
    """
    # create the sequence of procedure arguments for the element loop:
    # join each element with the nodal displacements
    arguments: list[tuple[Element, RealVector, RealVector]] = [(element, Ua, Ub) for element in mdb.mesh.elements]

    # compute each element matrix and assemble them into a global system matrix
    matrices: Sequence[RealMatrix] = loop(stressStiffnessMatrix, arguments, processes)
    Saa, Sab, Sba, Sbb = assembleMatrix(mdb.mesh.elements, matrices, mdb.mesh.activeDOFCount, mdb.mesh.inactiveDOFCount)
    return Saa, Sab, Sba, Sbb

def assembleConcentratedLoadVector(mdb: MDB) -> RealVector:
    """Assembles the system's global concentrated load vector."""
    Pc: RealVector = np.zeros(shape=(mdb.mesh.activeDOFCount,), dtype=Real)
    for load in mdb.concentratedLoads.values():
        F: RealVector = np.array((load.x, load.y, load.z), dtype=Real)
        for nodeIndex in mdb.nodeSets[load.region].indices:
            node: Node = mdb.mesh.nodes[nodeIndex]
            Pc[node.activeGlobalDOFs,] += F[node.activeLocalDOFs,]
    return Pc

def assembleSurfaceLoadVector(mdb: MDB, processes: int) -> RealVector:
    """
    Assembles the system's global surface load vector via the direct stiffness method.
    Assembly may be performed in parallel for each element surface by using multiple processes.
    """
    # create the sequence of procedure arguments for the element surface loop:
    # join each surface with the corresponding load parameters (magnitude or components)
    arguments: list[tuple[Surface, float, Float3D]] = []
    for pressure in mdb.pressures.values():
        for elementIndex, surfaceIndex in mdb.surfaceSets[pressure.region].indices:
            element: Element = mdb.mesh.elements[elementIndex]
            surfaceType, connectivity = element.surfaces[surfaceIndex]
            surface: Surface = Surface(surfaceIndex, surfaceType, connectivity, element)
            arguments.append((surface, pressure.magnitude, (0.0, 0.0, 0.0)))
    for surfaceTraction in mdb.surfaceTractions.values():
        for elementIndex, surfaceIndex in mdb.surfaceSets[surfaceTraction.region].indices:
            element: Element = mdb.mesh.elements[elementIndex]
            surfaceType, connectivity = element.surfaces[surfaceIndex]
            surface: Surface = Surface(surfaceIndex, surfaceType, connectivity, element)
            arguments.append((surface, 0.0, (surfaceTraction.x, surfaceTraction.y, surfaceTraction.z)))

    # compute each element vector and assemble them into a global system vector
    elements: Sequence[Element] = [tup[0].parent for tup in arguments]
    vectors: Sequence[RealVector] = loop(surfaceLoadVector, arguments, processes)
    Ps: RealVector = assembleVector(elements, vectors, mdb.mesh.activeDOFCount, mdb.mesh.inactiveDOFCount)[0]
    return Ps

def assembleBodyLoadVector(mdb: MDB, processes: int) -> RealVector:
    """
    Assembles the system's global body load vector via the direct stiffness method.
    Assembly may be performed in parallel for each element by using multiple processes.
    """
    # create the sequence of procedure arguments for the element loop:
    # join each element with the corresponding load components
    arguments: list[tuple[Element, Float3D]] = []
    for acceleration in mdb.accelerations.values():
        for elementIndex in mdb.elementSets[acceleration.region].indices:
            element: Element = mdb.mesh.elements[elementIndex]
            ρ: float = element.material.density
            arguments.append((element, (ρ*acceleration.x, ρ*acceleration.y, ρ*acceleration.z)))
    for bodyLoad in mdb.bodyLoads.values():
        for elementIndex in mdb.elementSets[bodyLoad.region].indices:
            element: Element = mdb.mesh.elements[elementIndex]
            arguments.append((element, (bodyLoad.x, bodyLoad.y, bodyLoad.z)))

    # compute each element vector and assemble them into a global system vector
    elements: Sequence[Element] = [tup[0] for tup in arguments]
    vectors: Sequence[RealVector] = loop(bodyLoadVector, arguments, processes)
    Pb: RealVector = assembleVector(elements, vectors, mdb.mesh.activeDOFCount, mdb.mesh.inactiveDOFCount)[0]
    return Pb

def assembleInternalForceVector(mdb: MDB, Ua: RealVector, Ub: RealVector, processes: int) -> \
    tuple[RealVector, RealVector, Sequence[RealMatrix], Sequence[RealMatrix]]:
    """
    Assembles the system's global internal force vector via the direct stiffness method.
    Also returns the basic components of strain and stress at the integration points.
    Assembly may be performed in parallel for each element by using multiple processes.
    """
    # create the sequence of procedure arguments for the element loop:
    # join each element with the nodal displacements
    arguments: list[tuple[Element, RealVector, RealVector]] = [(element, Ua, Ub) for element in mdb.mesh.elements]

    # compute each element vector and assemble them into a global system vector
    x: Sequence[tuple[RealVector, RealMatrix, RealMatrix]] = loop(internalForceVector, arguments, processes)
    elements: Sequence[Element] = [tup[0] for tup in arguments]
    vectors: Sequence[RealVector] = [tup[0] for tup in x]
    ε_ips  : Sequence[RealMatrix] = [tup[1] for tup in x]
    σ_ips  : Sequence[RealMatrix] = [tup[2] for tup in x]
    Fa, Fb = assembleVector(elements, vectors, mdb.mesh.activeDOFCount, mdb.mesh.inactiveDOFCount)
    return Fa, Fb, ε_ips, σ_ips

def assemblePrescribedDisplacementVector(mdb: MDB) -> RealVector:
    """Assembles the system's global prescribed displacement vector."""
    Ub: RealVector = np.zeros(shape=(mdb.mesh.inactiveDOFCount,), dtype=Real)
    for boundaryCondition in mdb.boundaryConditions.values():
        U: RealVector = np.zeros(shape=(3,), dtype=Real)
        U[boundaryCondition.dofs,] = boundaryCondition.displacements
        for nodeIndex in mdb.nodeSets[boundaryCondition.region].indices:
            node: Node = mdb.mesh.nodes[nodeIndex]
            Ub[node.inactiveGlobalDOFs,] = U[node.inactiveLocalDOFs,]
    return Ub

#-----------------------------------------------------------------------------------------------------------------------
# POST-PROCESSING
#-----------------------------------------------------------------------------------------------------------------------

def extendElementStrain(element: Element, ε_old: RealMatrix) -> RealMatrix:
    """Computes additional strain measures (principal strains)."""
    # create extra storage for new strain measures
    # 10 rows: ε11, ε22, ε33, ε23, ε31, ε12, ε1, ε2, ε3, εMajor
    ε_new: RealMatrix = np.zeros(shape=(10, ε_old.shape[1]), dtype=Real)

    # for each location (i.e., integration point or element node)
    for i in range(ε_old.shape[1]):

        # get basic components
        match element.section.type:
            case SectionTypes.PlaneStress:
                ε11, ε22, ε12 = ε_old[:, i]
                ε33 = ε23 = ε31 = 0.0
            case SectionTypes.PlaneStrain | SectionTypes.Axisymmetric:
                ε11, ε22, ε33, ε12 = ε_old[:, i]
                ε23 = ε31 = 0.0
            case SectionTypes.General:
                ε11, ε22, ε33, ε23, ε31, ε12 = ε_old[:, i]

        # build matrix
        ε: RealMatrix = np.array((
            (    ε11, 0.5*ε12, 0.5*ε31),
            (0.5*ε12,     ε22, 0.5*ε23),
            (0.5*ε31, 0.5*ε23,     ε33),
        ), dtype=Real)

        # compute principal strains
        eigenvalues: RealVector = np.linalg.eigvalsh(ε)
        ε3, ε2, ε1 = eigenvalues
        εMajor = eigenvalues[np.argmax(np.abs(eigenvalues))]

        # store results
        ε_new[:, i] = ε11, ε22, ε33, ε23, ε31, ε12, ε1, ε2, ε3, εMajor

    # done
    return ε_new

def extendElementStress(element: Element, σ_old: RealMatrix) -> RealMatrix:
    """Computes additional stress measures (principal stresses and equivalent stresses)."""
    # create extra storage for new stress measures
    # 13 rows: σ11, σ22, σ33, σ23, σ31, σ12, σ1, σ2, σ3, σMajor, σTresca, σMises, σPressure
    σ_new: RealMatrix = np.zeros(shape=(13, σ_old.shape[1]), dtype=Real)

    # for each location (i.e., integration point or element node)
    for i in range(σ_old.shape[1]):

        # get basic components
        match element.section.type:
            case SectionTypes.PlaneStress:
                σ11, σ22, σ12 = σ_old[:, i]
                σ33 = σ23 = σ31 = 0.0
            case SectionTypes.PlaneStrain | SectionTypes.Axisymmetric:
                σ11, σ22, σ33, σ12 = σ_old[:, i]
                σ23 = σ31 = 0.0
            case SectionTypes.General:
                σ11, σ22, σ33, σ23, σ31, σ12 = σ_old[:, i]

        # build matrix
        σ: RealMatrix = np.array((
            (σ11, σ12, σ31),
            (σ12, σ22, σ23),
            (σ31, σ23, σ33),
        ), dtype=Real)

        # compute principal stresses
        eigenvalues: RealVector = np.linalg.eigvalsh(σ)
        σ3, σ2, σ1 = eigenvalues
        σMajor = eigenvalues[np.argmax(np.abs(eigenvalues))]

        # compute equivalent stresses
        σTresca = abs(σ1 - σ3)
        σMises = np.sqrt(0.5*((σ1 - σ2)**2 + (σ2 - σ3)**2 + (σ3 - σ1)**2))
        σPressure = -(σ11 + σ22 + σ33)/3.0

        # store results
        σ_new[:, i] = σ11, σ22, σ33, σ23, σ31, σ12, σ1, σ2, σ3, σMajor, σTresca, σMises, σPressure

    # done
    return σ_new

def extendStrain(mdb: MDB, ε: Sequence[RealMatrix], processes: int) -> Sequence[RealMatrix]:
    """
    Computes additional strain measures.
    May be performed in parallel for each matrix by using multiple processes.
    """
    return loop(extendElementStrain, zip(mdb.mesh.elements, ε), processes)

def extendStress(mdb: MDB, σ: Sequence[RealMatrix], processes: int) -> Sequence[RealMatrix]:
    """
    Computes additional stress measures.
    May be performed in parallel for each matrix by using multiple processes.
    """
    return loop(extendElementStress, zip(mdb.mesh.elements, σ), processes)

def extrapolateWithinElement(element: Element, φi: RealMatrix) -> RealMatrix:
    """Extrapolation from integration points to element nodes."""
    # notes:
    # subscript i relates to variables at the element integration points
    # subscript j relates to variables at the element nodes

    # get natural coordinates
    Ci: RealMatrix = iso.integrationPoints(element)[0]
    Cj: RealMatrix = iso.nodes(element)
    ri, rj = Ci[:, 0], Cj[:, 0]
    si, sj = Ci[:, 1], Cj[:, 1]
    ti, tj = Ci[:, 2], Cj[:, 2]
    ni: int = Ci.shape[0] # number of element integration points
    nj: int = Cj.shape[0] # number of element nodes

    # extrapolation approaches
    A: RealMatrix
    p: RealMatrix
    φj: RealMatrix
    _1i: RealVector = np.ones(shape=(ni,), dtype=Real)
    _1j: RealVector = np.ones(shape=(nj,), dtype=Real)
    match iso.extrapolationApproach(element):

        case "constant":
            # no extrapolation
            φj = np.outer(φi, _1j)

        case "linear in r":
            # fit polynomial coefficients
            A = np.column_stack((_1i, ri))
            p = np.linalg.lstsq(A, φi.T, rcond=None)[0]

            # extrapolation
            φj = np.outer(p[0, :], _1j) + np.outer(p[1, :], rj)

        case "linear in t":
            # fit polynomial coefficients
            A = np.column_stack((_1i, ti))
            p = np.linalg.lstsq(A, φi.T, rcond=None)[0]

            # extrapolation
            φj = np.outer(p[0, :], _1j) + np.outer(p[1, :], tj)

        case "bilinear in r, s":
            # fit polynomial coefficients
            A = np.column_stack((_1i, ri, si, ri*si))
            p = np.linalg.lstsq(A, φi.T, rcond=None)[0]

            # extrapolation
            φj = np.outer(p[0, :], _1j) + np.outer(p[1, :], rj) + np.outer(p[2, :], sj) + np.outer(p[3, :], rj*sj)

        case "trilinear in r, s, t":
            # fit polynomial coefficients
            A = np.column_stack((_1i, ri, si, ti, ri*si, si*ti, ti*ri, ri*si*ti))
            p = np.linalg.lstsq(A, φi.T, rcond=None)[0]

            # extrapolation
            φj = np.outer(p[0, :], _1j) + np.outer(p[1, :], rj) + np.outer(p[2, :], sj) + np.outer(p[3, :], tj) + \
                np.outer(p[4, :], rj*sj) + np.outer(p[5, :], sj*tj) + np.outer(p[6, :], tj*rj) + \
                np.outer(p[7, :], rj*sj*tj)

    # done
    return φj

def extrapolate(mdb: MDB, φ_ips: Sequence[RealMatrix], processes: int) -> Sequence[RealMatrix]:
    """
    Extrapolates results from the integration points to the element nodes.
    May be performed in parallel for each element by using multiple processes.
    """
    return loop(extrapolateWithinElement, zip(mdb.mesh.elements, φ_ips), processes)

def smoothing(mdb: MDB, φ_nds: Sequence[RealMatrix]) -> RealMatrix:
    """Final nodal average."""
    n: int = φ_nds[0].shape[0] # number of strain or stress components/measures
    φ_msh: RealMatrix = np.zeros(shape=(mdb.mesh.nodeCount, n), dtype=Real)
    for element in mdb.mesh.elements: φ_msh[element.nodeIndices, :] += φ_nds[element.index].T
    for node in mdb.mesh.nodes: φ_msh[node.index, :] /= len(mdb.mesh.nodeToElementsMap[node.index])
    return φ_msh

def unshuffleVector(mdb: MDB, Va: RealVector | None, Vb: RealVector | None) -> RealMatrix:
    """
    Converts a global vector into a matrix of values per node.
    Also computes the magnitude at each node.
    """
    if Va is None: Va = np.zeros(shape=(mdb.mesh.activeDOFCount,), dtype=Real)
    if Vb is None: Vb = np.zeros(shape=(mdb.mesh.inactiveDOFCount,), dtype=Real)
    matrix: RealMatrix = np.zeros(shape=(mdb.mesh.nodeCount, 4), dtype=Real)
    for node in mdb.mesh.nodes:
        matrix[node.index, node.activeLocalDOFs] = Va[node.activeGlobalDOFs,]
        matrix[node.index, node.inactiveLocalDOFs] = Vb[node.inactiveGlobalDOFs,]
    matrix[:, 3] = np.sqrt(matrix[:, 0]*matrix[:, 0] + matrix[:, 1]*matrix[:, 1] + matrix[:, 2]*matrix[:, 2])
    return matrix
