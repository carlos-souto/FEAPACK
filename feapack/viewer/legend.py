from feapack.viewer import Spectrums
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import vtkColorTransferFunction
from PySide6.QtGui import QColor

class _Legend_vtk:
    """The VTK API object for the `Legend` class."""

    __slots__ = ("lookupTable", "scalarBarActor")

    def __init__(self) -> None:
        """VTK API object constructor."""
        # lookup table
        self.lookupTable: vtkLookupTable = vtkLookupTable()

        # scalar bar actor
        self.scalarBarActor: vtkScalarBarActor = vtkScalarBarActor()
        self.scalarBarActor.SetLookupTable(self.lookupTable)

class Legend:
    """Viewport legend."""

    __slots__ = ("_vtk",)

    def __init__(self) -> None:
        """Legend constructor."""
        # initialize variables
        self._vtk: _Legend_vtk = _Legend_vtk()

        # scalar bar actor settings
        self._vtk.scalarBarActor.UnconstrainedFontSizeOn()
        self._vtk.scalarBarActor.GetLabelTextProperty().SetFontSize(18)
        self._vtk.scalarBarActor.GetLabelTextProperty().SetFontFamilyToCourier()
        self._vtk.scalarBarActor.GetLabelTextProperty().ItalicOff()
        self._vtk.scalarBarActor.GetLabelTextProperty().ShadowOn()
        self._vtk.scalarBarActor.GetLabelTextProperty().BoldOff()
        self._vtk.scalarBarActor.SetPosition(0.025, 0.45)
        self._vtk.scalarBarActor.SetWidth(0.075)
        self._vtk.scalarBarActor.SetHeight(0.5)
        self._vtk.scalarBarActor.SetLabelFormat("%+0.3e")

        # first build
        self.rebuild(Spectrums.Jet, 12, False, False)

    def rebuild(self, spectrum: Spectrums, intervals: int, continuous: bool, reversed: bool) -> None:
        """Rebuilds the legend."""
        # counts
        colorCount: int = intervals if not continuous else 256
        labelCount: int = (intervals + 1) if not continuous else 10

        # color transfer function
        colorTransferFunction: vtkColorTransferFunction = vtkColorTransferFunction()
        for i, color in enumerate(spectrum.baseColors):
            colorTransferFunction.AddRGBPoint(i, *color)

        # weights
        n: int = len(spectrum.baseColors) - 1
        a, b = (0, n) if not reversed else (n, 0)
        weights: list[float] = [a + i*(b - a)/(colorCount - 1) for i in range(colorCount)]

        # update lookup table
        self._vtk.lookupTable.SetNumberOfTableValues(colorCount)
        for i, weight in enumerate(weights):
            self._vtk.lookupTable.SetTableValue(i, *colorTransferFunction.GetColor(weight))
        self._vtk.lookupTable.Build()

        # update scalar bar actor
        self._vtk.scalarBarActor.SetNumberOfLabels(labelCount)

    def isVisible(self) -> bool:
        """Gets the legend visibility."""
        return bool(self._vtk.scalarBarActor.GetVisibility())

    def setVisible(self, value: bool) -> None:
        """Sets the legend visibility."""
        self._vtk.scalarBarActor.SetVisibility(value)

    def textColor(self) -> QColor:
        """Gets the text color."""
        return QColor.fromRgbF(*self._vtk.scalarBarActor.GetLabelTextProperty().GetColor())

    def setTextColor(self, color: QColor) -> None:
        """Sets the text color."""
        self._vtk.scalarBarActor.GetLabelTextProperty().SetColor(color.redF(), color.greenF(), color.blueF())
