from enum import Enum, unique

@unique
class InteractionTypes(Enum):
    """Available interaction types."""
    Rotate = 0
    Pan    = 1
    Zoom   = 2
