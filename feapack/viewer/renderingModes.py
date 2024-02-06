from enum import Enum, unique

@unique
class RenderingModes(Enum):
    """Available rendering modes."""
    Wireframe     = 0
    Filled        = 1
    FilledNoEdges = 2
