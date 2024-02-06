from feapack.viewer import InteractionTypes
from vtkmodules.vtkCommonCore import vtkCommand, vtkObject
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera

class _Interaction_vtk:
    """The VTK API object for the `Interaction` class."""

    __slots__ = ("interactorStyle",)

    def __init__(self) -> None:
        """VTK API object constructor."""
        self.interactorStyle: vtkInteractorStyleTrackballCamera = vtkInteractorStyleTrackballCamera()

class Interaction:
    """View manipulation style object."""

    __slots__ = ("_vtk", "_interactionType")

    def __init__(self) -> None:
        """Constructor."""
        self._vtk: _Interaction_vtk = _Interaction_vtk()
        self._vtk.interactorStyle.AddObserver(vtkCommand.LeftButtonPressEvent, self.leftButtonPressObserver)
        self._vtk.interactorStyle.AddObserver(vtkCommand.LeftButtonReleaseEvent, self.leftButtonReleaseObserver)
        self._interactionType: InteractionTypes = InteractionTypes.Rotate

    def leftButtonPressObserver(self, sender: vtkObject, event: str) -> None:
        """Left button press observer."""
        match self._interactionType:
            case InteractionTypes.Rotate:
                if self._vtk.interactorStyle.GetInteractor().GetShiftKey():
                    self._vtk.interactorStyle.StartSpin()
                else:
                    self._vtk.interactorStyle.StartRotate()
            case InteractionTypes.Pan:
                self._vtk.interactorStyle.StartPan()
            case InteractionTypes.Zoom:
                self._vtk.interactorStyle.StartDolly()

    def leftButtonReleaseObserver(self, sender: vtkObject, event: str) -> None:
        """Left button release observer."""
        self._vtk.interactorStyle.EndPan()
        self._vtk.interactorStyle.EndSpin()
        self._vtk.interactorStyle.EndDolly()
        self._vtk.interactorStyle.EndRotate()

    def interactionType(self) -> InteractionTypes:
        """Gets the interaction type."""
        return self._interactionType

    def setInteractionType(self, interactionType: InteractionTypes) -> None:
        """Sets the interaction type."""
        self._interactionType = interactionType
