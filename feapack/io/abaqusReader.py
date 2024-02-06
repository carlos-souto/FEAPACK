from io import TextIOWrapper
from collections.abc import Iterable
from feapack.typing import Float3D, IntTuple

class AbaqusReader:
    """I/O class for reading an Abaqus input file."""

    __slots__ = ("_filePath",)

    @staticmethod
    def cleanLines(file: TextIOWrapper) -> Iterable[str]:
        """
        For iterating over the specified file while ignoring empty lines and comments.
        The lines are also processed: they are converted to uppercase and whitespaces are removed.
        """
        for line in file:
            line = line.strip().replace(" ", "").upper()   # remove whitespaces and convert to uppercase
            if not line or line.startswith("**"): continue # ignore empty lines and comments
            yield line

    @property
    def software(self) -> str:
        """The third-party software."""
        return "Abaqus"

    def __init__(self, filePath: str) -> None:
        """Creates a new reader for the specified Abaqus input file."""
        self._filePath: str = filePath

    def _getSets(self, keyword: str) -> Iterable[tuple[str, IntTuple]]:
        """
        Gets the node or element sets from file (names and corresponding indices).
        Note: 1-based indexing is automatically converted into 0-based indexing.
        """
        readData: bool = False
        generate: bool = False
        setName: str = ""
        partName: str = ""
        instanceName: str = ""
        indices: list[int] = []
        with open(self._filePath, "r") as file:
            for line in self.cleanLines(file):
                if readData and line[0] == "*":
                    readData = False
                    yield setName, tuple(indices)
                if readData:
                    if generate:
                        params: list[int] = [int(x) for x in line.split(",") if x]
                        first: int = params[0] - 1
                        last:  int = params[1] - 1
                        inc:   int = params[2] if len(params) >= 3 else 1
                        indices.extend(range(first, last + inc, inc))
                    else:
                        indices.extend(int(x) - 1 for x in line.split(",") if x)
                elif line.split(",")[0] == keyword:
                    readData = True
                    generate = ",GENERATE" in line
                    instanceName = line.split("INSTANCE=")[1].split(",")[0] if ",INSTANCE" in line else ""
                    setName = (instanceName + "." if instanceName else partName + "." if partName else "") + \
                        line.split("SET=")[1].split(",")[0]
                    indices = []
                elif line.split(",")[0] == "*PART":
                    partName = line.split("NAME=")[1].split(",")[0]
                elif line.split(",")[0] == "*ENDPART":
                    partName = ""
            if readData:
                yield setName, tuple(indices)

    def getNodeSets(self) -> Iterable[tuple[str, IntTuple]]:
        """
        Gets the node sets from file (names and corresponding node indices).
        Note: 1-based indexing is automatically converted into 0-based indexing.
        """
        return self._getSets("*NSET")

    def getElementSets(self) -> Iterable[tuple[str, IntTuple]]:
        """
        Gets the element sets from file (names and corresponding element indices).
        Note: 1-based indexing is automatically converted into 0-based indexing.
        """
        return self._getSets("*ELSET")

    def getNodes(self) -> Iterable[Float3D]:
        """Gets the nodal coordinates from file."""
        readData: bool = False
        with open(self._filePath, "r") as file:
            for line in self.cleanLines(file):
                if readData and line[0] == "*":
                    readData = False
                if readData:
                    coordinates: list[float] = [float(x) for x in line.split(",")[1:] if x]
                    while len(coordinates) < 3: coordinates.append(0.0)
                    yield coordinates[0], coordinates[1], coordinates[2]
                elif line.split(",")[0] == "*NODE":
                    readData = True

    def getElements(self) -> Iterable[tuple[str, IntTuple]]:
        """
        Gets the element types and corresponding nodal connectivity from file.
        Note: 1-based indexing is automatically converted into 0-based indexing.
        """
        readData: bool = False
        elementType: str = ""
        with open(self._filePath, "r") as file:
            for line in (lines := self.cleanLines(file)):
                if readData and line[0] == "*":
                    readData = False
                if readData:
                    skipIndex: bool = True
                    connectivity: list[int] = []
                    while True:
                        connectivity.extend(int(x) - 1 for x in line.split(",")[skipIndex:] if x)
                        if line[-1] == ",":
                            line = next(iter(lines))
                            skipIndex = False
                        else:
                            break
                    yield elementType, tuple(connectivity)
                elif line.split(",")[0] == "*ELEMENT":
                    readData = True
                    elementType = line.split("TYPE=")[1].split(",")[0]
