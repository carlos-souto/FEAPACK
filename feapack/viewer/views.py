from enum import Enum, unique

@unique
class Views(Enum):
    """Available viewport camera views."""
    Front     = 0
    Back      = 1
    Top       = 2
    Bottom    = 3
    Left      = 4
    Right     = 5
    Isometric = 6
