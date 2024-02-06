import os
import sys
from glob import glob
from ctypes import CDLL, POINTER, Structure, c_int, c_double, c_char, c_void_p

# load Intel MKL runtime library
_matches: list[str] = glob(os.path.join(os.path.dirname(sys.executable), "Library", "bin", "mkl_rt.*.dll"))
if len(_matches) == 0: raise RuntimeError("could not load Intel MKL runtime library")
if len(_matches) > 0: _matches.sort(key=lambda x: int(x.split(".")[-2]), reverse=True)
_LIB: CDLL = CDLL(_matches[0]); del _matches

# status of the routines
SPARSE_STATUS_SUCCESS          = 0 # the operation was successful
SPARSE_STATUS_NOT_INITIALIZED  = 1 # empty handle or matrix arrays
SPARSE_STATUS_ALLOC_FAILED     = 2 # internal error: memory allocation failed
SPARSE_STATUS_INVALID_VALUE    = 3 # invalid input value
SPARSE_STATUS_EXECUTION_FAILED = 4 # e.g. 0-diagonal element for triangular solver
SPARSE_STATUS_INTERNAL_ERROR   = 5 # internal error
SPARSE_STATUS_NOT_SUPPORTED    = 6 # e.g. operation for double precision doesn't support other types

# sparse matrix indexing
SPARSE_INDEX_BASE_ZERO = 0 # C-style
SPARSE_INDEX_BASE_ONE  = 1 # Fortran-style

# sparse matrix operations
SPARSE_OPERATION_NON_TRANSPOSE       = 10
SPARSE_OPERATION_TRANSPOSE           = 11
SPARSE_OPERATION_CONJUGATE_TRANSPOSE = 12

# supported matrix types
SPARSE_MATRIX_TYPE_GENERAL          = 20
SPARSE_MATRIX_TYPE_SYMMETRIC        = 21
SPARSE_MATRIX_TYPE_HERMITIAN        = 22
SPARSE_MATRIX_TYPE_TRIANGULAR       = 23
SPARSE_MATRIX_TYPE_DIAGONAL         = 24
SPARSE_MATRIX_TYPE_BLOCK_TRIANGULAR = 25
SPARSE_MATRIX_TYPE_BLOCK_DIAGONAL   = 26

# applies to triangular matrices only
SPARSE_FILL_MODE_LOWER = 40 # lower triangular part of the matrix is stored
SPARSE_FILL_MODE_UPPER = 41 # upper triangular part of the matrix is stored
SPARSE_FILL_MODE_FULL  = 42 # upper triangular part of the matrix is stored

# applies to triangular matrices only
SPARSE_DIAG_NON_UNIT = 50 # triangular matrix with non-unit diagonal
SPARSE_DIAG_UNIT     = 51 # triangular matrix with unit diagonal

# basic pointer types
c_int_p = POINTER(c_int)
c_int_pp = POINTER(c_int_p)
c_double_p = POINTER(c_double)
c_double_pp = POINTER(c_double_p)
c_char_p = POINTER(c_char)

# opaque structure for sparse matrix in internal format
class sparse_matrix(Structure): pass
sparse_matrix_t = POINTER(sparse_matrix)
sparse_matrix_t_p = POINTER(sparse_matrix_t)

class matrix_descr(Structure):
    """Descriptor of main sparse matrix properties."""
    _fields_ = (
        ("type", c_int), # matrix type: general, diagonal or triangular / symmetric / hermitian
        ("mode", c_int), # upper or lower triangular part of the matrix ( for triangular / symmetric / hermitian case)
        ("diag", c_int), # unit or non-unit diagonal ( for triangular / symmetric / hermitian case)
    )

# creates a handle for a matrix in COO format
mkl_sparse_d_create_coo = _LIB.mkl_sparse_d_create_coo
mkl_sparse_d_create_coo.restype = c_int # status
mkl_sparse_d_create_coo.argtypes = (    #
    sparse_matrix_t_p,                  # A
    c_int,                              # indexing
    c_int,                              # rows
    c_int,                              # cols
    c_int,                              # nnz
    c_int_p,                            # row_indx
    c_int_p,                            # col_indx
    c_double_p,                         # values
)

# converts internal matrix representation to CSR format
mkl_sparse_convert_csr = _LIB.mkl_sparse_convert_csr
mkl_sparse_convert_csr.restype = c_int # status
mkl_sparse_convert_csr.argtypes = (    #
    sparse_matrix_t,                   # source
    c_int,                             # operation
    sparse_matrix_t_p,                 # dest
)

# frees memory allocated for matrix handle
mkl_sparse_destroy = _LIB.mkl_sparse_destroy
mkl_sparse_destroy.restype = c_int # status
mkl_sparse_destroy.argtypes = (    #
    sparse_matrix_t,               # A
)

# performs ordering of column indices of the matrix in CSR format
mkl_sparse_order = _LIB.mkl_sparse_order
mkl_sparse_order.restype = c_int # status
mkl_sparse_order.argtypes = (    #
    sparse_matrix_t,             # A
)

# exports CSR matrix from internal representation
mkl_sparse_d_export_csr = _LIB.mkl_sparse_d_export_csr
mkl_sparse_d_export_csr.restype = c_int # status
mkl_sparse_d_export_csr.argtypes = (    #
    sparse_matrix_t,                    # source
    c_int_p,                            # indexing
    c_int_p,                            # rows
    c_int_p,                            # cols
    c_int_pp,                           # rows_start
    c_int_pp,                           # rows_end
    c_int_pp,                           # col_indx
    c_double_pp,                        # values
)

# computes a sparse matrix-vector product
mkl_sparse_d_mv = _LIB.mkl_sparse_d_mv
mkl_sparse_d_mv.restype = c_int # status
mkl_sparse_d_mv.argtypes = (    #
    c_int,                      # operation
    c_double,                   # alpha
    sparse_matrix_t,            # A
    matrix_descr,               # descr
    c_double_p,                 # x
    c_double,                   # beta
    c_double_p,                 # y
)

# calculates the solution of a set of sparse linear equations with single or multiple right-hand sides
pardiso = _LIB.pardiso
pardiso.restype = None
pardiso.argtypes = (
    c_void_p, # pt
    c_int_p,  # maxfct
    c_int_p,  # mnum
    c_int_p,  # mtype
    c_int_p,  # phase
    c_int_p,  # n
    c_void_p, # a
    c_int_p,  # ia
    c_int_p,  # ja
    c_int_p,  # perm
    c_int_p,  # nrhs
    c_int_p,  # iparm
    c_int_p,  # msglvl
    c_void_p, # b
    c_void_p, # x
    c_int_p,  # error
)

# computes the largest/smallest eigenvalues and corresponding eigenvectors of a generalized sparse eigenproblem
mkl_sparse_d_gv = _LIB.mkl_sparse_d_gv
mkl_sparse_d_gv.restype = c_int # status
mkl_sparse_d_gv.argtypes = (    #
    c_char_p,                   # which
    c_int_p,                    # pm
    sparse_matrix_t,            # A
    matrix_descr,               # descrA
    sparse_matrix_t,            # B
    matrix_descr,               # descrB
    c_int,                      # k0
    c_int_p,                    # k
    c_double_p,                 # E
    c_double_p,                 # X
    c_double_p,                 # res
)
