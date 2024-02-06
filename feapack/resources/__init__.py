import os
from collections.abc import Mapping, Iterable
from PySide6.QtGui import QIcon

graphics: Mapping[str, QIcon] = {}
icons: Mapping[str, QIcon] = {}

def _getFiles(subdirName: str) -> Iterable[tuple[str, str]]:
    """Returns an iterable over the file paths and corresponding file names found in the specified subdirectory."""
    subdir: str = os.path.join(os.path.dirname(__file__), subdirName)
    for entry in os.listdir(subdir):
        if os.path.isfile(filePath := os.path.join(subdir, entry)):
            fileName: str = os.path.splitext(entry)[0]
            yield filePath, fileName

def load(darkMode: bool = False) -> None:
    """
    Loads the application resources into memory.
    This function must be called after creating the application object.
    """
    badSuffix: str = "-light" if darkMode else "-dark"
    goodSuffix: str = "-dark" if darkMode else "-light"
    for dir, dict in ( ("svg", graphics), ("ico", icons) ):
        for path, name in _getFiles(dir):
            if name.endswith(badSuffix): continue
            elif name.endswith(goodSuffix): name = name.removesuffix(goodSuffix)
            dict[name] = QIcon(path)
