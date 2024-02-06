from itertools import repeat
from collections.abc import Iterable
from feapack.model import ODB
from feapack.typing import Float3D, Tuple
from feapack.viewer import RenderingModes, Legend
from vtkmodules.vtkCommonCore import vtkPoints, vtkUnsignedCharArray, vtkDoubleArray
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, vtkCellArray
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor
from vtkmodules.vtkFiltersCore import vtkExtractEdges

class _ODBView_vtk:
    """The VTK API object for the `ODBView` class."""

    __slots__ = ("dataSet", "mapper", "actor", "edgeFilter", "edgeMapper", "edgeActor")

    def __init__(self) -> None:
        """VTK API object constructor."""
        # data set
        self.dataSet: vtkUnstructuredGrid = vtkUnstructuredGrid()

        # mapper
        self.mapper: vtkDataSetMapper = vtkDataSetMapper()
        self.mapper.SetInputData(self.dataSet)

        # actor
        self.actor: vtkActor = vtkActor()
        self.actor.SetMapper(self.mapper)

        # edge filter
        self.edgeFilter: vtkExtractEdges = vtkExtractEdges()
        self.edgeFilter.SetInputData(self.dataSet)

        # edge mapper
        self.edgeMapper: vtkDataSetMapper = vtkDataSetMapper()
        self.edgeMapper.SetInputConnection(self.edgeFilter.GetOutputPort())

        # edge actor
        self.edgeActor: vtkActor = vtkActor()
        self.edgeActor.SetMapper(self.edgeMapper)

class ODBView:
    """A VTK-based renderable object for visualizing an output database."""

    __slots__ = ("_name", "_odb", "_vtk", "_legend")

    @property
    def name(self) -> str:
        """The name of this object."""
        return self._name

    @property
    def dimension(self) -> int:
        """The dimension (1D, 2D, or 3D) of the rendered mesh."""
        xmin, xmax, ymin, ymax, zmin, zmax = self._vtk.actor.GetBounds()
        x: int = (xmax - xmin) > 0.0
        y: int = (ymax - ymin) > 0.0
        z: int = (zmax - zmin) > 0.0
        return x + y + z

    @property
    def odb(self) -> ODB:
        """The underlying ODB."""
        return self._odb

    def __init__(self, name: str, odb: ODB, legend: Legend, renderingMode: RenderingModes, k: float) -> None:
        """
        Creates a new visualization object for the specified ODB.
        The parameter `k` sets the initial deformation scale factor.
        """
        # initialize variables
        self._name: str = name
        self._odb: ODB = odb
        self._legend: Legend = legend
        self._vtk: _ODBView_vtk = _ODBView_vtk()

        # mapper settings
        self._vtk.mapper.SetLookupTable(legend._vtk.lookupTable)
        self._vtk.mapper.InterpolateScalarsBeforeMappingOn()
        self._vtk.mapper.ScalarVisibilityOff()

        # edge mapper settings
        self._vtk.edgeMapper.SetLookupTable(legend._vtk.lookupTable)
        self._vtk.edgeMapper.InterpolateScalarsBeforeMappingOn()
        self._vtk.edgeMapper.ScalarVisibilityOff()

        # edge actor settings
        self._vtk.edgeActor.GetProperty().SetColor(0.0, 0.0, 0.0)

        # first build
        self.rebuild(k)
        self.renderIn(renderingMode)

    def _actors_vtk(self) -> Tuple[vtkActor]:
        """Returns the renderable VTK actors."""
        return (self._vtk.actor, self._vtk.edgeActor)

    def rebuild(self, k: float) -> None:
        """
        Rebuilds the internal data set.
        The parameter `k` updates the current deformation scale factor.
        """
        # reset
        self._vtk.dataSet.Initialize()

        # nodal displacements
        getValues = self._odb.getNodeOutputValues
        getTitles = self._odb.getNodeOutputTitles
        nodalDisplacements: zip[Float3D] = zip(
            getValues(title) if (title := "Displacement>Displacement in X") in getTitles() else repeat(0.0), # u
            getValues(title) if (title := "Displacement>Displacement in Y") in getTitles() else repeat(0.0), # v
            getValues(title) if (title := "Displacement>Displacement in Z") in getTitles() else repeat(0.0), # v
        )

        # nodal coordinates
        self._vtk.dataSet.SetPoints(vtkPoints())
        for (x, y, z), (u, v, w) in zip(self._odb.getNodes(), nodalDisplacements):
            self._vtk.dataSet.GetPoints().InsertNextPoint(x + k*u, y + k*v, z + k*w)
        self._vtk.dataSet.GetPoints().Squeeze()

        # element connectivity
        self._vtk.dataSet.SetCells(vtkUnsignedCharArray(), vtkCellArray())
        for type, connectivity in self._odb.getElements():
            self._vtk.dataSet.InsertNextCell(type.cellType, len(connectivity), connectivity)
        self._vtk.dataSet.Squeeze()

        # node scalars
        self._vtk.dataSet.GetPointData().SetScalars(vtkDoubleArray())
        self._vtk.dataSet.GetPointData().GetScalars().SetNumberOfValues(self._vtk.dataSet.GetNumberOfPoints())

    def plotNodeOutput(self, title: str) -> None:
        """Plots the specified node output scalar field."""
        # check if output is available
        values: Iterable[float]
        if title in self._odb.getNodeOutputTitles():
            values = self._odb.getNodeOutputValues(title)
        else:
            values = (0.0 for _ in range(self._vtk.dataSet.GetNumberOfPoints()))

        # update node scalars
        for index, value in enumerate(values):
            self._vtk.dataSet.GetPointData().GetScalars().SetValue(index, value)
        self._vtk.dataSet.GetPointData().GetScalars().Modified()

        # update mappers
        self._vtk.mapper.SetScalarRange(self._vtk.dataSet.GetPointData().GetScalars().GetRange())
        self._vtk.edgeMapper.SetScalarRange(self._vtk.dataSet.GetPointData().GetScalars().GetRange())
        if self._vtk.actor.GetVisibility(): self._vtk.mapper.ScalarVisibilityOn()
        elif self._vtk.edgeActor.GetVisibility(): self._vtk.edgeMapper.ScalarVisibilityOn()

    def clearNodeOutput(self) -> None:
        """Clears the current node output scalar field."""
        self._vtk.mapper.ScalarVisibilityOff()
        self._vtk.edgeMapper.ScalarVisibilityOff()

    def renderIn(self, mode: RenderingModes) -> None:
        """Renders the mesh in the specified rendering mode."""
        self._vtk.actor.SetVisibility(mode in (RenderingModes.Filled, RenderingModes.FilledNoEdges))
        self._vtk.edgeActor.SetVisibility(mode in (RenderingModes.Wireframe, RenderingModes.Filled))
        if not self._vtk.actor.GetVisibility() and self._vtk.mapper.GetScalarVisibility():
            self._vtk.mapper.ScalarVisibilityOff()
            self._vtk.edgeMapper.ScalarVisibilityOn()
        elif self._vtk.actor.GetVisibility() and self._vtk.edgeMapper.GetScalarVisibility():
            self._vtk.edgeMapper.ScalarVisibilityOff()
            self._vtk.mapper.ScalarVisibilityOn()
