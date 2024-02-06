import numpy as np
import numpy.ctypeslib as npc
import feapack.c.libmkl as mkl
from ctypes import byref
from feapack.typing import Int, IntVector, RealVector

class SparseCSR:
    """Sparse matrix storage in CSR format."""

    __slots__ = (
        "_handle", "_rowCount", "_columnCount", "_nonZeroCount", "_pointerB", "_pointerE", "_rowIndex", "_columns",
        "_values", "_description"
    )

    @property
    def rowCount(self) -> int:
        """The number of rows."""
        return self._rowCount

    @property
    def columnCount(self) -> int:
        """The number of columns."""
        return self._columnCount

    @property
    def internalPointer(self) -> mkl.sparse_matrix_t:
        """Internal pointer to data structure."""
        return self._handle

    @property
    def description(self) -> mkl.matrix_descr:
        """Matrix descriptor object."""
        return self._description

    @property
    def CSR(self) -> tuple[RealVector, IntVector, IntVector, IntVector]:
        """A view of the values, columns, pointerB, and pointerE arrays of the CSR format."""
        return (self._values, self._columns, self._pointerB, self._pointerE)

    @property
    def CSR3(self) -> tuple[RealVector, IntVector, IntVector]:
        """A view of the values, columns, and rowIndex arrays of the CSR3 format."""
        return (self._values, self._columns, self._rowIndex)

    def __init__(
        self, rowCount: int, columnCount: int, rowIndices: IntVector, columnIndices: IntVector, values: RealVector,
        matrixType: int = mkl.SPARSE_MATRIX_TYPE_GENERAL, fillMode: int = mkl.SPARSE_FILL_MODE_FULL,
        unitDiagonal: int = mkl.SPARSE_DIAG_NON_UNIT
    ) -> None:
        """Creates a new sparse matrix storage in CSR format from COO-type data."""
        # basic checks
        if values.size != rowIndices.size or values.size != columnIndices.size: raise ValueError("array size mismatch")
        if np.min(columnIndices) < 0 or np.max(columnIndices) >= columnCount: raise ValueError("index out of bounds")   # type: ignore
        if np.min(rowIndices) < 0 or np.max(rowIndices) >= rowCount: raise ValueError("index out of bounds")            # type: ignore

        # create COO handle
        cooHandle: mkl.sparse_matrix_t = mkl.sparse_matrix_t()
        status: int = mkl.mkl_sparse_d_create_coo(
            byref(cooHandle),
            mkl.SPARSE_INDEX_BASE_ZERO,
            rowCount,
            columnCount,
            values.size,
            npc.as_ctypes(rowIndices),
            npc.as_ctypes(columnIndices),
            npc.as_ctypes(values),
        )
        if status != mkl.SPARSE_STATUS_SUCCESS:
            raise RuntimeError("could not create COO handle")

        # convert to CSR
        csrHandle: mkl.sparse_matrix_t = mkl.sparse_matrix_t()
        status = mkl.mkl_sparse_convert_csr(
            cooHandle,
            mkl.SPARSE_OPERATION_NON_TRANSPOSE,
            byref(csrHandle),
        )
        if status != mkl.SPARSE_STATUS_SUCCESS:
            raise RuntimeError("could not create CSR handle")

        # free COO handle
        status = mkl.mkl_sparse_destroy(cooHandle)
        if status != mkl.SPARSE_STATUS_SUCCESS:
            raise RuntimeError("could not destroy COO handle")

        # order CSR column indices
        status = mkl.mkl_sparse_order(csrHandle)
        if status != mkl.SPARSE_STATUS_SUCCESS:
            raise RuntimeError("could not order CSR handle")

        # export CSR data
        _base = mkl.c_int()
        _rowCount = mkl.c_int()
        _columnCount = mkl.c_int()
        _pointerB = mkl.c_int_p()
        _pointerE = mkl.c_int_p()
        _columns = mkl.c_int_p()
        _values = mkl.c_double_p()
        status = mkl.mkl_sparse_d_export_csr(
            csrHandle,
            byref(_base),
            byref(_rowCount),
            byref(_columnCount),
            byref(_pointerB),
            byref(_pointerE),
            byref(_columns),
            byref(_values),
        )
        if status != mkl.SPARSE_STATUS_SUCCESS:
            raise RuntimeError("could not export CSR handle")

        # build self
        self._handle: mkl.sparse_matrix_t = csrHandle
        self._rowCount: int = _rowCount.value
        self._columnCount: int = _columnCount.value
        self._pointerB: IntVector = npc.as_array(_pointerB, shape=(self._rowCount,))
        self._pointerE: IntVector = npc.as_array(_pointerE, shape=(self._rowCount,))
        self._rowIndex: IntVector = np.zeros(shape=(self._rowCount + 1,), dtype=Int)
        self._rowIndex[0] = self._pointerB[0]
        self._rowIndex[1:] = self._pointerE[:]
        self._columns: IntVector = npc.as_array(_columns, shape=(self._pointerE[self._rowCount - 1],))
        self._values: RealVector = npc.as_array(_values, shape=self._columns.shape)
        self._nonZeroCount: int = self._values.size
        self._description: mkl.matrix_descr = mkl.matrix_descr()
        self._description.type = matrixType
        self._description.mode = fillMode
        self._description.diag = unitDiagonal

    def __del__(self) -> None:
        """Frees externally allocated memory."""
        status: int = mkl.mkl_sparse_destroy(self._handle)
        if status != mkl.SPARSE_STATUS_SUCCESS:
            raise RuntimeError("could not destroy CSR handle")
