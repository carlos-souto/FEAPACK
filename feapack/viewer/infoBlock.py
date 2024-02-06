from vtkmodules.vtkRenderingCore import vtkTextActor
from PySide6.QtGui import QColor

class _InfoBlock_vtk:
    """The VTK API object for the `InfoBlock` class."""

    __slots__ = ("textActor",)

    def __init__(self) -> None:
        """VTK API object constructor."""
        self.textActor: vtkTextActor = vtkTextActor()

class InfoBlock:
    """Viewport information text block."""

    __slots__ = ("_vtk", "_textLines")

    def __init__(self) -> None:
        """Info block constructor."""
        # initialize variables
        self._vtk: _InfoBlock_vtk = _InfoBlock_vtk()
        self._textLines: list[str] = []

        # text actor settings
        self._vtk.textActor.SetTextScaleModeToNone()
        self._vtk.textActor.GetTextProperty().SetFontSize(18)
        self._vtk.textActor.GetTextProperty().SetFontFamilyToCourier()
        self._vtk.textActor.GetTextProperty().ItalicOff()
        self._vtk.textActor.GetTextProperty().ShadowOn()
        self._vtk.textActor.GetTextProperty().BoldOff()
        self._vtk.textActor.GetTextProperty().SetJustificationToLeft()
        self._vtk.textActor.GetTextProperty().SetVerticalJustificationToBottom()
        self._vtk.textActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        self._vtk.textActor.GetPositionCoordinate().SetValue(0.01, 0.01)

    def clear(self) -> None:
        """Clears all text."""
        self._textLines.clear()
        self._vtk.textActor.SetInput("")

    def text(self, row: int) -> str:
        """Gets the text at the specified row."""
        if row >= len(self._textLines): return ""
        return self._textLines[row]

    def setText(self, row: int, text: str) -> None:
        """Sets the text at the specified row."""
        while len(self._textLines) < row + 1:
            self._textLines.append("")
        self._textLines[row] = text
        self._vtk.textActor.SetInput("\n".join(self._textLines))

    def textColor(self) -> QColor:
        """Gets the text color."""
        return QColor.fromRgbF(*self._vtk.textActor.GetTextProperty().GetColor())

    def setTextColor(self, color: QColor) -> None:
        """Sets the text color."""
        self._vtk.textActor.GetTextProperty().SetColor(color.redF(), color.greenF(), color.blueF())
