import os
import time
import vtkmodules.vtkRenderingContextOpenGL2 # type: ignore (initialize VTK)
from glob import glob
from PIL import Image
from itertools import chain
from typing import Literal, Protocol, overload
from feapack.typing import Float2D, Float3D, FloatTuple, Tuple
from feapack.viewer import Views, RenderingModes, Triad, Legend, InfoBlock, ODBView, Interaction, InteractionTypes
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QFrame
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingCore import vtkRenderWindow, vtkRenderer, vtkRenderWindowInteractor, vtkActor, vtkCamera, \
    vtkInteractorStyle, vtkWindowToImageFilter

class _Renderable(Protocol):
    """A protocol for renderable objects."""

    @property
    def name(self) -> str:
        """The name of the renderable object."""
        ...

    def _actors_vtk(self) -> Tuple[vtkActor]:
        """Returns the renderable VTK actors."""
        ...

class _Viewport_vtk:
    """The VTK API object for the `Viewport` class."""

    __slots__ = ("renderWindow", "renderer", "interactor", "interactorStyle", "camera")

    def __init__(self, renderWindow: vtkRenderWindow, interactorStyle: vtkInteractorStyle) -> None:
        """VTK API object constructor."""
        # renderer
        self.renderer: vtkRenderer = vtkRenderer()

        # render window
        self.renderWindow: vtkRenderWindow = renderWindow
        self.renderWindow.AddRenderer(self.renderer)

        # interactor style
        self.interactorStyle: vtkInteractorStyle = interactorStyle

        # interactor
        self.interactor: vtkRenderWindowInteractor = self.renderWindow.GetInteractor()
        self.interactor.SetInteractorStyle(self.interactorStyle)

        # camera
        self.camera: vtkCamera = self.renderer.GetActiveCamera()

class Viewport(QWidget):
    """A VTK-based viewport widget."""

    __slots__ = ("_vtk", "_triad", "_legend", "_infoBlock", "_interaction", "_rendered")

    # persistent settings
    _renderingMode: RenderingModes = RenderingModes.Filled
    _isLightingActive: bool = True
    _deformationScaleFactor: float = 1.0

    # custom signals
    renderingModeChanged: Signal = Signal(RenderingModes)
    cameraProjectionModeChanged: Signal = Signal(bool)
    lightingModeChanged: Signal = Signal(bool)
    deformationScaleFactorChanged: Signal = Signal(float)
    interactionTypeChanged: Signal = Signal(InteractionTypes)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Viewport constructor."""
        super().__init__(parent)

        # layout
        layout: QGridLayout = QGridLayout(self)
        layout.setObjectName("layout")
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # frame
        frame: QFrame = QFrame(self)
        frame.setObjectName("frame")
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(frame, 0, 0, 1, 1)

        # frame layout
        frameLayout: QGridLayout = QGridLayout(frame)
        frameLayout.setObjectName("frameLayout")
        frameLayout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(frameLayout)

        # VTK widget
        vtkWidget: QVTKRenderWindowInteractor = QVTKRenderWindowInteractor(frame)
        vtkWidget.setObjectName("vtkWidget")
        frameLayout.addWidget(vtkWidget, 0, 0, 1, 1)

        # interaction
        self._interaction: Interaction = Interaction()

        # VTK API object
        self._vtk: _Viewport_vtk = _Viewport_vtk(vtkWidget.GetRenderWindow(), self._interaction._vtk.interactorStyle)
        self._vtk.interactor.RemoveObservers("CharEvent")

        # triad
        self._triad: Triad = Triad()
        self._triad._vtk.orientationMarkerWidget.SetInteractor(self._vtk.interactor)
        self._triad._vtk.orientationMarkerWidget.EnabledOn()
        self._triad._vtk.orientationMarkerWidget.InteractiveOff()

        # legend
        self._legend: Legend = Legend()
        self._vtk.renderer.AddActor2D(self._legend._vtk.scalarBarActor)

        # info block
        self._infoBlock: InfoBlock = InfoBlock()
        self._vtk.renderer.AddActor2D(self._infoBlock._vtk.textActor)

        # rendered objects
        self._rendered: list[_Renderable] = []

    def start(self) -> None:
        """Starts the viewport."""
        self._vtk.interactor.Start()

    def triad(self) -> Triad:
        """The viewport triad."""
        return self._triad

    def legend(self) -> Legend:
        """The viewport legend."""
        return self._legend

    def infoBlock(self) -> InfoBlock:
        """The viewport information text block."""
        return self._infoBlock

    def interactionType(self) -> InteractionTypes:
        """Gets the interaction type."""
        return self._interaction.interactionType()

    def setInteractionType(self, interactionType: InteractionTypes) -> None:
        """Sets the interaction type."""
        self._interaction.setInteractionType(interactionType)
        self.interactionTypeChanged.emit(interactionType)

    def renderingMode(self) -> RenderingModes:
        """Gets the rendering mode."""
        return self._renderingMode

    def setRenderingMode(self, mode: RenderingModes, draw: bool = True) -> None:
        """Sets the rendering mode."""
        self._renderingMode = mode
        for renderable in self._rendered:
            if isinstance(renderable, ODBView):
                renderable.renderIn(mode)
        if draw: self._vtk.renderWindow.Render()
        self.renderingModeChanged.emit(mode)

    def isCameraUsingParallelProjection(self) -> bool:
        """Gets if camera is using parallel projection."""
        return bool(self._vtk.camera.GetParallelProjection())

    def setCameraUsingParallelProjection(self, value: bool, draw: bool = True) -> None:
        """Sets if camera is using parallel projection."""
        self._vtk.camera.SetParallelProjection(value)
        if draw: self._vtk.renderWindow.Render()
        self.cameraProjectionModeChanged.emit(value)

    def isLightingActive(self) -> bool:
        """Gets if lighting is active."""
        return self._isLightingActive

    def setLightingActive(self, value: bool, draw: bool = True) -> None:
        """Sets if lighting is active."""
        self._isLightingActive = value
        for renderable in self._rendered:
            for actor in renderable._actors_vtk():
                actor.GetProperty().SetLighting(value)
        if draw: self._vtk.renderWindow.Render()
        self.lightingModeChanged.emit(value)

    def deformationScaleFactor(self) -> float:
        """Gets the deformation scale factor."""
        return self._deformationScaleFactor

    def setDeformationScaleFactor(self, value: float, draw: bool = True) -> None:
        """Sets the deformation scale factor."""
        self._deformationScaleFactor = value
        for renderable in self._rendered:
            if isinstance(renderable, ODBView):
                renderable.rebuild(value)
        if draw: self._vtk.renderWindow.Render()
        self.deformationScaleFactorChanged.emit(value)

    def backgroundColor1(self) -> QColor:
        """Gets the background color 1."""
        return QColor.fromRgbF(*self._vtk.renderer.GetBackground2())

    def setBackgroundColor1(self, color: QColor, draw: bool = True) -> None:
        """Sets the background color 1."""
        self._vtk.renderer.GradientBackgroundOn()
        self._vtk.renderer.SetBackground2(color.redF(), color.greenF(), color.blueF())
        if draw: self._vtk.renderWindow.Render()

    def backgroundColor2(self) -> QColor:
        """Gets the background color 2."""
        return QColor.fromRgbF(*self._vtk.renderer.GetBackground())

    def setBackgroundColor2(self, color: QColor, draw: bool = True) -> None:
        """Sets the background color 2."""
        self._vtk.renderer.GradientBackgroundOn()
        self._vtk.renderer.SetBackground(color.redF(), color.greenF(), color.blueF())
        if draw: self._vtk.renderWindow.Render()

    def textColor(self) -> QColor:
        """Gets the text color."""
        return self._infoBlock.textColor()

    def setTextColor(self, color: QColor, draw: bool = True) -> None:
        """Sets the text color."""
        self._triad.setTextColor(color)
        self._legend.setTextColor(color)
        self._infoBlock.setTextColor(color)
        if draw: self._vtk.renderWindow.Render()

    def view(self, view: Views, draw: bool = True) -> None:
        """Updates the viewport camera view."""
        focalPoint: Float3D
        position: Float3D
        viewUp: Float3D
        match view:
            case Views.Front:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +0.0, +1.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Back:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +0.0, -1.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Top:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +1.0, +0.0)
                viewUp     = (+0.0, +0.0, -1.0)
            case Views.Bottom:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, -1.0, +0.0)
                viewUp     = (+0.0, +0.0, +1.0)
            case Views.Left:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (-1.0, +0.0, +0.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Right:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+1.0, +0.0, +0.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Isometric:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+1.0, +1.0, +1.0)
                viewUp     = (+0.0, +1.0, +0.0)
        self._vtk.camera.SetFocalPoint(focalPoint)
        self._vtk.camera.SetPosition(position)
        self._vtk.camera.SetViewUp(viewUp)
        self._vtk.renderer.ResetCamera()
        if draw: self._vtk.renderWindow.Render()

    def autoFitView(self, draw: bool = True) -> None:
        """Auto-fits the current view."""
        self._vtk.renderer.ResetCamera()
        if draw: self._vtk.renderWindow.Render()

    def print(self, filePath: str) -> None:
        """Prints the current viewport scene to the specified file."""
        # save current background and text colors
        backgroundColor1: QColor = self.backgroundColor1()
        backgroundColor2: QColor = self.backgroundColor2()
        textColor: QColor = self.textColor()

        # set white background and black text
        self.setBackgroundColor1(QColor(255, 255, 255), draw=False)
        self.setBackgroundColor2(QColor(255, 255, 255), draw=False)
        self.setTextColor(QColor(0, 0, 0), draw=True)

        # create image filter
        filter: vtkWindowToImageFilter = vtkWindowToImageFilter()
        filter.SetInput(self._vtk.renderWindow)
        filter.SetInputBufferTypeToRGB()

        # create writer
        writer: vtkPNGWriter = vtkPNGWriter()
        writer.SetInputConnection(filter.GetOutputPort())
        writer.SetFileName(filePath)

        # write
        writer.Write()

        # reset background and text colors
        self.setBackgroundColor1(backgroundColor1, draw=False)
        self.setBackgroundColor2(backgroundColor2, draw=False)
        self.setTextColor(textColor, draw=True)

    @overload
    def get(self, name: str) -> _Renderable:
        """Returns the rendered object with the specified name as a generic renderable object."""
        ...

    @overload
    def get[T](self, name: str, type: type[T]) -> T:
        """Returns the rendered object with the specified name and of the specified type."""
        ...

    def get[T](self, name: str, type: type[T] | None = None) -> T | _Renderable:
        for renderable in self._rendered:
            if renderable.name == name and (type is None or isinstance(renderable, type)):
                return renderable
        raise ValueError(f"renderable object not found in the current scene: '{name}'")

    def draw(self, renderable: _Renderable | None = None) -> None:
        """
        Draws/renders the current scene.
        If a renderable object is specified, it is added to the scene before the scene is rendered.
        """
        if renderable is not None and renderable not in self._rendered:
            for actor in renderable._actors_vtk():
                actor.GetProperty().SetLighting(self._isLightingActive)
                self._vtk.renderer.AddActor(actor)
            self._rendered.append(renderable)
        self._vtk.renderWindow.Render()

    def clear(self, renderable: _Renderable | None = None) -> None:
        """
        Clears the current scene.
        If a renderable object is specified, only that object is removed from the scene before the scene is rendered;
        otherwise, all objects are removed from the scene.
        """
        if renderable is not None and renderable in self._rendered:
            for actor in renderable._actors_vtk(): self._vtk.renderer.RemoveActor(actor)
            self._rendered.remove(renderable)
        elif renderable is None:
            for renderable in self._rendered:
                for actor in renderable._actors_vtk():
                    self._vtk.renderer.RemoveActor(actor)
            self._rendered.clear()
        self._vtk.renderWindow.Render()

    def animateDeformation(
        self, dsf: float, limits: Float2D | None, animationMode: Literal["loop", "swing"],
        scalingMode: Literal["half", "full", "full+scalars"], frameCount: int, frameDelay: int, repetitions: int,
        filePath: str | None = None
    ) -> None:
        """Animate deformation."""
        # check k = 0
        if dsf == 0.0: raise ValueError("non-zero deformation scale factor required for animation")

        # get ODBView object
        odbView: ODBView
        for renderable in self._rendered:
            if isinstance(renderable, ODBView):
                odbView = renderable
                break
        else:
            raise RuntimeError("no ODBView object found in the current scene")

        # deformation scale factors
        start: float = 0.0 if scalingMode == "half" else -dsf
        stop: float = dsf
        dsfVector: list[float] = [start + i*(stop - start)/(frameCount - 1) for i in range(frameCount)]

        # get limits
        scalarRange: Float2D = odbView._vtk.dataSet.GetPointData().GetScalars().GetRange()
        globalMax: float
        globalMin: float
        if limits is None:
            if scalingMode == "full+scalars":
                globalAbs: float = max(abs(scalarRange[0]), abs(scalarRange[1]))
                globalMin, globalMax = -globalAbs, +globalAbs
            else:
                globalMin, globalMax = scalarRange
        else:
            globalMin, globalMax = limits

        # get scalars
        scalars: FloatTuple = tuple(
            odbView._vtk.dataSet.GetPointData().GetScalars().GetValue(i)
            for i in range(odbView._vtk.dataSet.GetNumberOfPoints())
        )

        # set limits
        odbView._vtk.mapper.SetScalarRange((globalMin, globalMax))
        odbView._vtk.edgeMapper.SetScalarRange((globalMin, globalMax))

        # update colors if save animation
        backgroundColor1: QColor = self.backgroundColor1()
        backgroundColor2: QColor = self.backgroundColor2()
        textColor: QColor = self.textColor()
        if filePath:
            self.setBackgroundColor1(QColor(255, 255, 255), draw=False)
            self.setBackgroundColor2(QColor(255, 255, 255), draw=False)
            self.setTextColor(QColor(0, 0, 0), draw=False)

        # render animation
        for rep in range(repetitions if not filePath else 1):
            for i, k in enumerate(dsfVector if animationMode == "loop" else chain(dsfVector, reversed(dsfVector))):

                # update deformation scale factor
                odbView.rebuild(k)

                # update node scalars
                weight: float = k/dsf
                if scalingMode != "full+scalars": weight = abs(weight)
                for index, value in enumerate(scalars):
                    odbView._vtk.dataSet.GetPointData().GetScalars().SetValue(index, weight*value)
                odbView._vtk.dataSet.GetPointData().GetScalars().Modified()

                # update dsf info
                self.infoBlock().setText(2, f"Deformation Scale Factor: {round(k, 4)}")

                # render
                self._vtk.renderWindow.Render()
                if not filePath: time.sleep(frameDelay/1000.0)

                # save gif frames
                if rep == 0 and filePath:

                    # create image filter
                    imageFilter: vtkWindowToImageFilter = vtkWindowToImageFilter()
                    imageFilter.SetInput(self._vtk.renderWindow)
                    imageFilter.SetInputBufferTypeToRGB()

                    # create image writer
                    pngWriter: vtkPNGWriter = vtkPNGWriter()
                    pngWriter.SetInputConnection(imageFilter.GetOutputPort())
                    pngWriter.SetFileName(os.path.splitext(filePath)[0] + f"__gif_frame_{i:06}.png")

                    # print frame
                    pngWriter.Write()

        # finalize gif animation
        if filePath:
            imageFiles: list[str] = [*sorted(glob(os.path.splitext(filePath)[0] + "__gif_frame_*.png"))]
            animation: Image.Image = Image.open(imageFiles[0])
            animation.save(
                filePath, "GIF", save_all=True, loop=0, duration=frameDelay,
                append_images=[Image.open(imageFile) for imageFile in imageFiles[1:]]
            )
            for imageFile in imageFiles:
                os.remove(imageFile)

        # reset background and text colors
        if filePath:
            self.setBackgroundColor1(backgroundColor1, draw=False)
            self.setBackgroundColor2(backgroundColor2, draw=False)
            self.setTextColor(textColor, draw=False)

        # reset deformation scale factor, limits, and scalars
        self.infoBlock().setText(2, f"Deformation Scale Factor: {self.deformationScaleFactor()}")
        odbView.rebuild(self.deformationScaleFactor())
        for index, value in enumerate(scalars):
            odbView._vtk.dataSet.GetPointData().GetScalars().SetValue(index, value)
        odbView._vtk.dataSet.GetPointData().GetScalars().Modified()
        odbView._vtk.mapper.SetScalarRange(scalarRange)
        odbView._vtk.edgeMapper.SetScalarRange(scalarRange)
        self._vtk.renderWindow.Render()

    def animateTime(
        self, limits: Float2D | None, animationMode: Literal["loop", "swing"], frameDelay: int, repetitions: int,
        nodeOutputTitle: str = "", filePath: str | None = None
    ) -> None:
        """Animate time (ODB frames)."""
        # get ODBView object
        odbView: ODBView
        for renderable in self._rendered:
            if isinstance(renderable, ODBView):
                odbView = renderable
                break
        else:
            raise RuntimeError("no ODBView object found in the current scene")

        # print gif frame function
        currentFrame: list[int] = [0]
        def printFrame() -> None:
            if not filePath: return

            # create image filter
            imageFilter: vtkWindowToImageFilter = vtkWindowToImageFilter()
            imageFilter.SetInput(self._vtk.renderWindow)
            imageFilter.SetInputBufferTypeToRGB()

            # create image writer
            pngWriter: vtkPNGWriter = vtkPNGWriter()
            pngWriter.SetInputConnection(imageFilter.GetOutputPort())
            pngWriter.SetFileName(os.path.splitext(filePath)[0] + f"__gif_frame_{currentFrame[0]:06}.png")

            # print frame
            pngWriter.Write()
            currentFrame[0] += 1

        # update colors if save animation
        backgroundColor1: QColor = self.backgroundColor1()
        backgroundColor2: QColor = self.backgroundColor2()
        textColor: QColor = self.textColor()
        if filePath:
            self.setBackgroundColor1(QColor(255, 255, 255), draw=False)
            self.setBackgroundColor2(QColor(255, 255, 255), draw=False)
            self.setTextColor(QColor(0, 0, 0), draw=False)

        # render animation
        if filePath: repetitions = 1
        for rep in range(repetitions):

            # render initial state
            odbView.odb.goToFirstFrame()
            odbView.rebuild(self.deformationScaleFactor())
            if nodeOutputTitle: odbView.plotNodeOutput(nodeOutputTitle)
            if limits:
                odbView._vtk.mapper.SetScalarRange(limits)
                odbView._vtk.edgeMapper.SetScalarRange(limits)
            self.infoBlock().setText(1, odbView.odb.getDescription())
            self._vtk.renderWindow.Render()
            if rep == 0 and filePath: printFrame()
            if not filePath: time.sleep(frameDelay/1000.0)

            # forward
            for _ in range(odbView.odb.frameCount - 1):
                odbView.odb.goToNextFrame()
                odbView.rebuild(self.deformationScaleFactor())
                if nodeOutputTitle: odbView.plotNodeOutput(nodeOutputTitle)
                if limits:
                    odbView._vtk.mapper.SetScalarRange(limits)
                    odbView._vtk.edgeMapper.SetScalarRange(limits)
                self.infoBlock().setText(1, odbView.odb.getDescription())
                self._vtk.renderWindow.Render()
                if rep == 0 and filePath: printFrame()
                if not filePath: time.sleep(frameDelay/1000.0)

            # backward
            if animationMode == "swing":
                for _ in range(odbView.odb.frameCount - (1 if rep == repetitions - 1 else 2)):
                    odbView.odb.goToPreviousFrame()
                    odbView.rebuild(self.deformationScaleFactor())
                    if nodeOutputTitle: odbView.plotNodeOutput(nodeOutputTitle)
                    if limits:
                        odbView._vtk.mapper.SetScalarRange(limits)
                        odbView._vtk.edgeMapper.SetScalarRange(limits)
                    self.infoBlock().setText(1, odbView.odb.getDescription())
                    self._vtk.renderWindow.Render()
                    if rep == 0 and filePath: printFrame()
                    if not filePath: time.sleep(frameDelay/1000.0)

        # finalize gif animation
        if filePath:
            imageFiles: list[str] = [*sorted(glob(os.path.splitext(filePath)[0] + "__gif_frame_*.png"))]
            animation: Image.Image = Image.open(imageFiles[0])
            animation.save(
                filePath, "GIF", save_all=True, loop=0, duration=frameDelay,
                append_images=[Image.open(imageFile) for imageFile in imageFiles[1:]]
            )
            for imageFile in imageFiles:
                os.remove(imageFile)

        # reset background and text colors
        if filePath:
            self.setBackgroundColor1(backgroundColor1, draw=False)
            self.setBackgroundColor2(backgroundColor2, draw=False)
            self.setTextColor(textColor, draw=False)
            self._vtk.renderWindow.Render() # or reset below
