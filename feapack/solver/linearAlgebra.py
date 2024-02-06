import numpy as np
import numpy.ctypeslib as npc
import feapack.c.libmkl as mkl
from ctypes import byref
from typing import Literal, overload
from feapack.solver import SparseCSR
from feapack.typing import Real, RealVector, RealMatrix

def determinant(A: RealMatrix) -> float:
    """Computes the determinant of a small matrix (up to 4-by-4)."""
    if A.ndim != 2 or A.shape[0] != A.shape[1]: raise ValueError("a square matrix is required")
    match A.shape[0]:
        case 0:
            return 1.0
        case 1:
            return A[0, 0]
        case 2:
            return A[0, 0]*A[1, 1] - A[0, 1]*A[1, 0]
        case 3:
            return A[0, 0]*A[1, 1]*A[2, 2] - A[0, 0]*A[1, 2]*A[2, 1] - A[0, 1]*A[1, 0]*A[2, 2] + \
                   A[0, 1]*A[1, 2]*A[2, 0] + A[0, 2]*A[1, 0]*A[2, 1] - A[0, 2]*A[1, 1]*A[2, 0]
        case 4:
            return A[0, 0]*A[1, 1]*A[2, 2]*A[3, 3] - A[0, 0]*A[1, 1]*A[2, 3]*A[3, 2] - A[0, 0]*A[1, 2]*A[2, 1]*A[3, 3] + A[0, 0]*A[1, 2]*A[2, 3]*A[3, 1] + \
                   A[0, 0]*A[1, 3]*A[2, 1]*A[3, 2] - A[0, 0]*A[1, 3]*A[2, 2]*A[3, 1] - A[0, 1]*A[1, 0]*A[2, 2]*A[3, 3] + A[0, 1]*A[1, 0]*A[2, 3]*A[3, 2] + \
                   A[0, 1]*A[1, 2]*A[2, 0]*A[3, 3] - A[0, 1]*A[1, 2]*A[2, 3]*A[3, 0] - A[0, 1]*A[1, 3]*A[2, 0]*A[3, 2] + A[0, 1]*A[1, 3]*A[2, 2]*A[3, 0] + \
                   A[0, 2]*A[1, 0]*A[2, 1]*A[3, 3] - A[0, 2]*A[1, 0]*A[2, 3]*A[3, 1] - A[0, 2]*A[1, 1]*A[2, 0]*A[3, 3] + A[0, 2]*A[1, 1]*A[2, 3]*A[3, 0] + \
                   A[0, 2]*A[1, 3]*A[2, 0]*A[3, 1] - A[0, 2]*A[1, 3]*A[2, 1]*A[3, 0] - A[0, 3]*A[1, 0]*A[2, 1]*A[3, 2] + A[0, 3]*A[1, 0]*A[2, 2]*A[3, 1] + \
                   A[0, 3]*A[1, 1]*A[2, 0]*A[3, 2] - A[0, 3]*A[1, 1]*A[2, 2]*A[3, 0] - A[0, 3]*A[1, 2]*A[2, 0]*A[3, 1] + A[0, 3]*A[1, 2]*A[2, 1]*A[3, 0]
        case _:
            raise ValueError("unsupported matrix size")

def inverse(A: RealMatrix) -> tuple[RealMatrix, float]:
    """
    Computes the inverse of a small matrix (up to 4-by-4).
    Also returns the determinant.
    """
    if A.ndim != 2 or A.shape[0] != A.shape[1]: raise ValueError("a square matrix is required")
    if (detA := determinant(A)) == 0.0: raise ValueError("matrix is singular")
    invA: RealMatrix = np.zeros(shape=A.shape, dtype=Real)
    match A.shape[0]:
        case 0:
            pass
        case 1:
            # row 0
            invA[0, 0] = 1.0/detA
        case 2:
            # row 0
            invA[0, 0] =  A[1, 1]/detA
            invA[0, 1] = -A[0, 1]/detA
            # row 1
            invA[1, 0] = -A[1, 0]/detA
            invA[1, 1] =  A[0, 0]/detA
        case 3:
            # row 0
            invA[0, 0] =  (A[1, 1]*A[2, 2] - A[1, 2]*A[2, 1])/detA
            invA[0, 1] = -(A[0, 1]*A[2, 2] - A[0, 2]*A[2, 1])/detA
            invA[0, 2] =  (A[0, 1]*A[1, 2] - A[0, 2]*A[1, 1])/detA
            # row 1
            invA[1, 0] = -(A[1, 0]*A[2, 2] - A[1, 2]*A[2, 0])/detA
            invA[1, 1] =  (A[0, 0]*A[2, 2] - A[0, 2]*A[2, 0])/detA
            invA[1, 2] = -(A[0, 0]*A[1, 2] - A[0, 2]*A[1, 0])/detA
            # row 2
            invA[2, 0] =  (A[1, 0]*A[2, 1] - A[1, 1]*A[2, 0])/detA
            invA[2, 1] = -(A[0, 0]*A[2, 1] - A[0, 1]*A[2, 0])/detA
            invA[2, 2] =  (A[0, 0]*A[1, 1] - A[0, 1]*A[1, 0])/detA
        case 4:
            # row 0
            invA[0, 0] =  (A[1, 1]*A[2, 2]*A[3, 3] - A[1, 1]*A[2, 3]*A[3, 2] - A[1, 2]*A[2, 1]*A[3, 3] + A[1, 2]*A[2, 3]*A[3, 1] + A[1, 3]*A[2, 1]*A[3, 2] - A[1, 3]*A[2, 2]*A[3, 1])/detA
            invA[0, 1] = -(A[0, 1]*A[2, 2]*A[3, 3] - A[0, 1]*A[2, 3]*A[3, 2] - A[0, 2]*A[2, 1]*A[3, 3] + A[0, 2]*A[2, 3]*A[3, 1] + A[0, 3]*A[2, 1]*A[3, 2] - A[0, 3]*A[2, 2]*A[3, 1])/detA
            invA[0, 2] =  (A[0, 1]*A[1, 2]*A[3, 3] - A[0, 1]*A[1, 3]*A[3, 2] - A[0, 2]*A[1, 1]*A[3, 3] + A[0, 2]*A[1, 3]*A[3, 1] + A[0, 3]*A[1, 1]*A[3, 2] - A[0, 3]*A[1, 2]*A[3, 1])/detA
            invA[0, 3] = -(A[0, 1]*A[1, 2]*A[2, 3] - A[0, 1]*A[1, 3]*A[2, 2] - A[0, 2]*A[1, 1]*A[2, 3] + A[0, 2]*A[1, 3]*A[2, 1] + A[0, 3]*A[1, 1]*A[2, 2] - A[0, 3]*A[1, 2]*A[2, 1])/detA
            # row 1
            invA[1, 0] = -(A[1, 0]*A[2, 2]*A[3, 3] - A[1, 0]*A[2, 3]*A[3, 2] - A[1, 2]*A[2, 0]*A[3, 3] + A[1, 2]*A[2, 3]*A[3, 0] + A[1, 3]*A[2, 0]*A[3, 2] - A[1, 3]*A[2, 2]*A[3, 0])/detA
            invA[1, 1] =  (A[0, 0]*A[2, 2]*A[3, 3] - A[0, 0]*A[2, 3]*A[3, 2] - A[0, 2]*A[2, 0]*A[3, 3] + A[0, 2]*A[2, 3]*A[3, 0] + A[0, 3]*A[2, 0]*A[3, 2] - A[0, 3]*A[2, 2]*A[3, 0])/detA
            invA[1, 2] = -(A[0, 0]*A[1, 2]*A[3, 3] - A[0, 0]*A[1, 3]*A[3, 2] - A[0, 2]*A[1, 0]*A[3, 3] + A[0, 2]*A[1, 3]*A[3, 0] + A[0, 3]*A[1, 0]*A[3, 2] - A[0, 3]*A[1, 2]*A[3, 0])/detA
            invA[1, 3] =  (A[0, 0]*A[1, 2]*A[2, 3] - A[0, 0]*A[1, 3]*A[2, 2] - A[0, 2]*A[1, 0]*A[2, 3] + A[0, 2]*A[1, 3]*A[2, 0] + A[0, 3]*A[1, 0]*A[2, 2] - A[0, 3]*A[1, 2]*A[2, 0])/detA
            # row 2
            invA[2, 0] =  (A[1, 0]*A[2, 1]*A[3, 3] - A[1, 0]*A[2, 3]*A[3, 1] - A[1, 1]*A[2, 0]*A[3, 3] + A[1, 1]*A[2, 3]*A[3, 0] + A[1, 3]*A[2, 0]*A[3, 1] - A[1, 3]*A[2, 1]*A[3, 0])/detA
            invA[2, 1] = -(A[0, 0]*A[2, 1]*A[3, 3] - A[0, 0]*A[2, 3]*A[3, 1] - A[0, 1]*A[2, 0]*A[3, 3] + A[0, 1]*A[2, 3]*A[3, 0] + A[0, 3]*A[2, 0]*A[3, 1] - A[0, 3]*A[2, 1]*A[3, 0])/detA
            invA[2, 2] =  (A[0, 0]*A[1, 1]*A[3, 3] - A[0, 0]*A[1, 3]*A[3, 1] - A[0, 1]*A[1, 0]*A[3, 3] + A[0, 1]*A[1, 3]*A[3, 0] + A[0, 3]*A[1, 0]*A[3, 1] - A[0, 3]*A[1, 1]*A[3, 0])/detA
            invA[2, 3] = -(A[0, 0]*A[1, 1]*A[2, 3] - A[0, 0]*A[1, 3]*A[2, 1] - A[0, 1]*A[1, 0]*A[2, 3] + A[0, 1]*A[1, 3]*A[2, 0] + A[0, 3]*A[1, 0]*A[2, 1] - A[0, 3]*A[1, 1]*A[2, 0])/detA
            # row 3
            invA[3, 0] = -(A[1, 0]*A[2, 1]*A[3, 2] - A[1, 0]*A[2, 2]*A[3, 1] - A[1, 1]*A[2, 0]*A[3, 2] + A[1, 1]*A[2, 2]*A[3, 0] + A[1, 2]*A[2, 0]*A[3, 1] - A[1, 2]*A[2, 1]*A[3, 0])/detA
            invA[3, 1] =  (A[0, 0]*A[2, 1]*A[3, 2] - A[0, 0]*A[2, 2]*A[3, 1] - A[0, 1]*A[2, 0]*A[3, 2] + A[0, 1]*A[2, 2]*A[3, 0] + A[0, 2]*A[2, 0]*A[3, 1] - A[0, 2]*A[2, 1]*A[3, 0])/detA
            invA[3, 2] = -(A[0, 0]*A[1, 1]*A[3, 2] - A[0, 0]*A[1, 2]*A[3, 1] - A[0, 1]*A[1, 0]*A[3, 2] + A[0, 1]*A[1, 2]*A[3, 0] + A[0, 2]*A[1, 0]*A[3, 1] - A[0, 2]*A[1, 1]*A[3, 0])/detA
            invA[3, 3] =  (A[0, 0]*A[1, 1]*A[2, 2] - A[0, 0]*A[1, 2]*A[2, 1] - A[0, 1]*A[1, 0]*A[2, 2] + A[0, 1]*A[1, 2]*A[2, 0] + A[0, 2]*A[1, 0]*A[2, 1] - A[0, 2]*A[1, 1]*A[2, 0])/detA
        case _:
            raise ValueError("unsupported matrix size")
    return invA, detA

@overload
def spmatmul(
    A: SparseCSR, x: RealVector, y: RealVector, alpha: float = 1.0, beta: float = 1.0, transposeA: bool = False
) -> None:
    """
    Computes a sparse matrix-vector product. Performed in-place, defined as `y <- alpha*op(A)*x + beta*y`, where `alpha`
    and `beta` are scalars, `x` and `y` are vectors, and `A` is a sparse matrix. Additionally, `op(A) = A` or
    `op(A) = transpose(A)`.
    """
    ...

@overload
def spmatmul(
    A: SparseCSR, x: RealVector, y: None = None, alpha: float = 1.0, beta: None = None, transposeA: bool = False
) -> RealVector:
    """
    Computes a sparse matrix-vector product. Defined as `y <- alpha*op(A)*x`, where `alpha` is a scalar, `x` and `y` are
    vectors, and `A` is a sparse matrix. Additionally, `op(A) = A` or `op(A) = transpose(A)`.
    """
    ...

def spmatmul(
    A: SparseCSR, x: RealVector, y: RealVector | None = None, alpha: float = 1.0, beta: float | None = None,
    transposeA: bool = False
) -> RealVector | None:
    # allocate output vector if necessary
    if y is None:
        y = np.zeros(shape=(A.rowCount if not transposeA else A.columnCount,), dtype=Real)
        spmatmul(A, x, y, alpha, 1.0, transposeA)
        return y

    # check arguments
    m: int = A.rowCount if not transposeA else A.columnCount
    n: int = A.columnCount if not transposeA else A.rowCount
    if x.ndim != 1 or x.shape[0] != n: raise ValueError(f"'x' must be a vector of size {n}")
    if y.ndim != 1 or y.shape[0] != m: raise ValueError(f"'y' must be a vector of size {m}")
    if beta is None: beta = 1.0

    # call external computational routine
    status: int = mkl.mkl_sparse_d_mv(
        mkl.SPARSE_OPERATION_NON_TRANSPOSE if not transposeA else mkl.SPARSE_OPERATION_TRANSPOSE,
        alpha,
        A.internalPointer,
        A.description,
        npc.as_ctypes(x),
        beta,
        npc.as_ctypes(y)
    )
    if status != mkl.SPARSE_STATUS_SUCCESS:
        raise RuntimeError("external computational error")

def spsolve(A: SparseCSR, B: RealVector, _mtype: int = 11) -> RealVector:
    """Calculates the solution of a set of sparse linear equations."""
    # check arguments
    if A.rowCount != A.columnCount: raise ValueError("'A' must be a square sparse matrix")
    if B.ndim != 1 or B.shape[0] != A.rowCount: raise ValueError(f"'B' must be a vector of size {A.rowCount}")

    # allocate solution vector
    X: RealVector = np.zeros(shape=B.shape, dtype=Real)

    # unpack CSR3-type data
    values, columns, rowIndex = A.CSR3

    # solver internal data address pointer
    pt = npc.as_ctypes(np.zeros(shape=(64,), dtype=np.int64))

    # maximal number of factors in memory
    maxfct = mkl.c_int(1)

    # the number of matrix to solve
    mnum = mkl.c_int(1)

    # matrix type
    #  1: real and structurally symmetric
    #  2: real and symmetric positive definite
    # -2: real and symmetric indefinite
    #  3: complex and structurally symmetric
    #  4: complex and Hermitian positive definite
    # -4: complex and Hermitian indefinite
    #  6: complex and symmetric matrix
    # 11: real and non-symmetric matrix
    # 13: complex and non-symmetric matrix
    mtype = mkl.c_int(_mtype)

    # controls the execution of the solver
    #  11: analysis
    #  12: analysis, numerical factorization
    #  13: analysis, numerical factorization, solve, iterative refinement
    #  22: numerical factorization
    #  23: numerical factorization, solve, iterative refinement
    #  33: solve, iterative refinement
    # 331: like phase=33, but only forward substitution
    # 332: like phase=33, but only diagonal substitution
    # 333: like phase=33, but only backward substitution
    #   0: release internal memory for L and U of the matrix number mnum
    #  -1: release all internal memory for all matrices
    phase = mkl.c_int(13)

    # number of equations in the sparse linear system
    n = mkl.c_int(A.rowCount)

    # non-zero elements of the coefficient matrix
    a = npc.as_ctypes(values)

    # rowIndex array in CSR3 format
    ia = npc.as_ctypes(rowIndex)

    # columns array in CSR3 format
    ja = npc.as_ctypes(columns)

    # the permutation vector
    perm = (mkl.c_int*A.rowCount)()

    # number of right-hand sides
    nrhs = mkl.c_int(1)

    # Intel oneMKL PARDISO parameters
    iparm = (mkl.c_int*64)()
    iparm[0]     = 1
    iparm[1]     = 3
    iparm[2]     = 0
    iparm[3]     = 0
    iparm[4]     = 0
    iparm[5]     = 0
    iparm[6]     = 0
    iparm[7]     = 0
    iparm[8]     = 0
    iparm[9]     = 13 if _mtype in (11, 13) else 8 if _mtype in (-2, -4, 6) else 0
    iparm[10]    = 1 if _mtype in (11, 13) else 0
    iparm[11]    = 0
    iparm[12]    = 1 if _mtype in (11, 13) else 0
    iparm[13:17] = 0, 0, 0, 0
    iparm[17]    = -1
    iparm[18]    = 0
    iparm[19]    = 0
    iparm[20]    = 1
    iparm[21:23] = 0, 0
    iparm[23]    = 0
    iparm[24]    = 0
    iparm[25]    = 0
    iparm[26]    = 0
    iparm[27]    = 0
    iparm[28]    = 0
    iparm[29]    = 0
    iparm[30]    = 0
    iparm[31:33] = 0, 0
    iparm[33]    = 0
    iparm[34]    = 1
    iparm[35]    = 0
    iparm[36]    = 0
    iparm[37]    = 0
    iparm[38]    = 0
    iparm[39:42] = 0, 0, 0
    iparm[42]    = 0
    iparm[43:55] = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    iparm[55]    = 0
    iparm[56:59] = 0, 0, 0
    iparm[59]    = 0
    iparm[60:62] = 0, 0
    iparm[62]    = 0
    iparm[63]    = 0

    # message level information
    msglvl = mkl.c_int(0)

    # right-hand side vectors
    b = npc.as_ctypes(B)

    # solution vectors
    x = npc.as_ctypes(X)

    # error indicator
    error = mkl.c_int(1)

    # call computational routine
    mkl.pardiso(
        pt, byref(maxfct), byref(mnum), byref(mtype), byref(phase), byref(n), a, ia, ja, perm, byref(nrhs), iparm,
        byref(msglvl), b, x, byref(error)
    )
    if error.value != 0:
        raise RuntimeError("external computational error")

    # release internal memory
    phase = mkl.c_int(-1)
    mkl.pardiso(
        pt, byref(maxfct), byref(mnum), byref(mtype), byref(phase), byref(n), a, ia, ja, perm, byref(nrhs), iparm,
        byref(msglvl), b, x, byref(error)
    )
    if error.value != 0:
        raise RuntimeError("external computational error")

    # done
    return X

def speigen(A: SparseCSR, B: SparseCSR, k0: int, which: Literal["S", "L"]) -> tuple[RealVector, RealMatrix, RealVector]:
    """
    Computes the largest/smallest eigenvalues and corresponding eigenvectors of a generalized sparse eigenproblem.
    The parameter `k0` specifies the number of eigenpairs to extract.
    The parameter `which` specifies if the largest or smallest eigenvalues are requested.
    """
    # check arguments
    if A.rowCount != A.columnCount: raise ValueError("'A' must be a square sparse matrix")
    if B.rowCount != B.columnCount: raise ValueError("'B' must be a square sparse matrix")
    if A.rowCount != B.rowCount: raise ValueError("'A' and 'B' must have the same shape")
    if k0 < 1 or k0 > A.rowCount: raise ValueError("invalid value for 'k0'")
    if which not in ("S", "L"): raise ValueError("invalid value for 'which'")

    # extended eigensolver input parameters
    pm = (mkl.c_int*128)()
    pm[0] = 0
    pm[1] = 6
    pm[2] = 0
    pm[3] = 0
    pm[4] = 0
    pm[5] = 0
    pm[6] = 1
    pm[7] = 0
    pm[8] = 0
    pm[9] = 0
    # pm[10:128] = 0

    # allocate output
    k = mkl.c_int()                                     # number of eigenvalues found
    E = np.zeros(shape=(k0,), dtype=Real)               # eigenvalue storage
    X = np.zeros(shape=(k0*A.columnCount,), dtype=Real) # eigenvector storage
    res = np.zeros(shape=(k0,), dtype=Real)             # residuals

    # call computational routine
    status: int = mkl.mkl_sparse_d_gv(
        byref(mkl.c_char(ord(which))), pm, A.internalPointer, A.description, B.internalPointer, B.description, k0,
        byref(k), npc.as_ctypes(E), npc.as_ctypes(X), npc.as_ctypes(res)
    )
    if status != mkl.SPARSE_STATUS_SUCCESS:
        raise RuntimeError("external computational error")

    # return results
    return E[:k.value], X.reshape(k0, A.columnCount)[:k.value, :].T, res[:k.value]
