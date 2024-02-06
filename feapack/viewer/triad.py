from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from PySide6.QtGui import QColor

class _Triad_vtk:
    """The VTK API object for the `Triad` class."""

    __slots__ = ("axesActor", "orientationMarkerWidget")

    def __init__(self) -> None:
        """VTK API object constructor."""
        # axes actor
        self.axesActor: vtkAxesActor = vtkAxesActor()

        # orientation marker widget
        self.orientationMarkerWidget: vtkOrientationMarkerWidget = vtkOrientationMarkerWidget()
        self.orientationMarkerWidget.SetOrientationMarker(self.axesActor)

class Triad:
    """Viewport triad."""

    __slots__ = ("_vtk",)

    def __init__(self) -> None:
        """Triad constructor."""
        # initialize VTK API object
        self._vtk: _Triad_vtk = _Triad_vtk()

        # axes actor settings
        self._vtk.axesActor.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        self._vtk.axesActor.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        self._vtk.axesActor.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        self._vtk.axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(18)
        self._vtk.axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(18)
        self._vtk.axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(18)
        self._vtk.axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontFamilyToCourier()
        self._vtk.axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontFamilyToCourier()
        self._vtk.axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontFamilyToCourier()
        self._vtk.axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
        self._vtk.axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
        self._vtk.axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
        self._vtk.axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().ShadowOn()
        self._vtk.axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty().ShadowOn()
        self._vtk.axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty().ShadowOn()
        self._vtk.axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
        self._vtk.axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
        self._vtk.axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
        self._vtk.axesActor.SetTipTypeToCone()
        self._vtk.axesActor.SetShaftTypeToCylinder()
        self._vtk.axesActor.SetConeResolution(64)
        self._vtk.axesActor.SetCylinderResolution(64)
        self._vtk.axesActor.SetConeRadius(0.5)
        self._vtk.axesActor.SetCylinderRadius(0.08)
        self._vtk.axesActor.SetNormalizedTipLength(0.3, 0.3, 0.3)
        self._vtk.axesActor.SetNormalizedShaftLength(0.7, 0.7, 0.7)
        self._vtk.axesActor.SetNormalizedLabelPosition(1.25, 1.25, 1.25)

        # orientation marker widget settings
        self._vtk.orientationMarkerWidget.SetViewport(0.75, 0.0, 1.0, 0.25)

    def textColor(self) -> QColor:
        """Gets the text color."""
        return QColor.fromRgbF(*self._vtk.axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().GetColor())

    def setTextColor(self, color: QColor) -> None:
        """Sets the text color."""
        r, g, b = color.redF(), color.greenF(), color.blueF()
        self._vtk.axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(r, g, b)
        self._vtk.axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetColor(r, g, b)
        self._vtk.axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetColor(r, g, b)
