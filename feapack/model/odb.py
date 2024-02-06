import os
from typing import Literal
from collections.abc import Mapping, Iterable, Sequence
from feapack.model import MissingFrameError, ElementTypes, Mesh
from feapack.typing import Float3D, IntTuple

class ODB:
    """Definition of an output database (ODB)."""

    __slots__ = ("_filePath", "_mode", "_frameCount", "_currentFrame", "_linePointers")

    @property
    def filePath(self) -> str:
        """The ODB file path."""
        return self._filePath

    @property
    def fileName(self) -> str:
        """The ODB file name."""
        return os.path.splitext(os.path.basename(self._filePath))[0]

    @property
    def currentFrame(self) -> int:
        """The current output frame."""
        return self._currentFrame

    @property
    def frameCount(self) -> int:
        """The number of output frames"""
        return self._frameCount

    def __init__(self, filePath: str, mode: Literal["read", "write"], replace: bool = False) -> None:
        """Creates a new output database object associated with the specified file."""
        # instance variables
        self._filePath: str = filePath
        self._mode: Literal["r", "a"] = "a" if mode == "write" else "r"
        self._frameCount: int = 0
        self._currentFrame: int = -1
        self._linePointers: list[dict[str, tuple[str, int]]] = []

        # if replacing is intended, check for read-only mode
        if replace and os.path.isfile(filePath):
            if mode == "read": raise RuntimeError("cannot replace existing output database in read-only mode")
            else: os.remove(filePath)

        # if write mode and file does not exist, create one to append data to
        if mode == "write" and not os.path.isfile(filePath):
            open(filePath, "x").close()

        # if read-only mode, check if the file exists
        if mode == "read" and not os.path.isfile(filePath):
            raise ValueError(f"output database not found: '{filePath}'")

        # if read-only mode, count number of frames
        if mode == "read":
            with open(self._filePath, self._mode) as file:
                for line in file:
                    if line.strip() == "$FRAME":
                        self._frameCount += 1
            if self._frameCount == 0: raise MissingFrameError(f"output database has no frames: '{filePath}'")
            self._currentFrame = self._frameCount - 1

        # if read-only mode, determine pointers pointing to command lines, e.g., $NODES
        # these pointers are used for jumping to specific lines in the file
        if mode == "read":
            self._linePointers = [{} for _ in range(self._frameCount)]
            d: dict[str, tuple[str, int]] | None = None
            with open(self._filePath, self._mode) as file:
                while line := file.readline():
                    if not line.startswith("$"): continue
                    line = line.strip()
                    if line == "$FRAME":
                        frame: int = int(file.readline())
                        d = self._linePointers[frame]
                        continue
                    elif line == "$END_FRAME":
                        d = None
                        continue
                    if d is not None:
                        command: str = line.split(" ", maxsplit=1)[0]
                        d[command] = line, file.tell()

    def writeNextFrame(
        self, description: str, mesh: Mesh, nodeOutput: Mapping[str, Iterable[float]] = {},
        globalOutput: Mapping[str, float] = {}
    ) -> None:
        """Writes the next output frame to file."""
        self._frameCount += 1
        self._currentFrame += 1
        with open(self._filePath, self._mode) as file:

            # frame
            file.write(f"$FRAME\n{self._currentFrame}\n\n")

            # description
            file.write(f"$DESCRIPTION\n{description}\n\n")

            # nodes
            file.write(f"$NODES {mesh.nodeCount}\n")
            for node in mesh.nodes:
                file.write(f"{node.x}, {node.y}, {node.z}\n")
            file.write("\n")

            # elements
            file.write(f"$ELEMENTS {mesh.elementCount}\n")
            for element in mesh.elements:
                file.write(f"{element.type.name}, {", ".join(map(str, element.nodeIndices))}\n")
            file.write("\n")

            # node output titles
            file.write(f"$NODE_OUTPUT_TITLES {len(nodeOutput)}\n")
            for title in nodeOutput.keys():
                file.write(f"{title}\n")
            file.write("\n")

            # node output values
            file.write(f"$NODE_OUTPUT_VALUES {mesh.nodeCount if len(nodeOutput) > 0 else 0}\n")
            for row in zip(*nodeOutput.values()):
                file.write(f"{", ".join(map(str, row))}\n")
            file.write("\n")

            # global output titles
            file.write(f"$GLOBAL_OUTPUT_TITLES {len(globalOutput)}\n")
            for title in globalOutput.keys():
                file.write(f"{title}\n")
            file.write("\n")

            # global output values
            file.write(f"$GLOBAL_OUTPUT_VALUES {len(globalOutput)}\n")
            for value in globalOutput.values():
                file.write(f"{value}\n")
            file.write("\n")

            # end frame
            file.write("$END_FRAME\n\n")

    def getDescription(self) -> str:
        """Gets the description from file for the current output frame."""
        pointer = self._linePointers[self._currentFrame]["$DESCRIPTION"][1]
        with open(self._filePath, self._mode) as file:
            file.seek(pointer)
            return file.readline().strip()

    def getNodes(self) -> Iterable[Float3D]:
        """Gets the nodal coordinates from file for the current output frame."""
        line, pointer = self._linePointers[self._currentFrame]["$NODES"]
        nodeCount: int = int(line.split(" ")[1])
        with open(self._filePath, self._mode) as file:
            file.seek(pointer)
            for _ in range(nodeCount):
                line = file.readline()
                coordinates: list[float] = [float(x) for x in line.split(",")]
                yield (coordinates[0], coordinates[1], coordinates[2])

    def getElements(self) -> Iterable[tuple[ElementTypes, IntTuple]]:
        """Gets the element types and corresponding nodal connectivity from file for the current output frame."""
        line, pointer = self._linePointers[self._currentFrame]["$ELEMENTS"]
        elementCount: int = int(line.split(" ")[1])
        with open(self._filePath, self._mode) as file:
            file.seek(pointer)
            for _ in range(elementCount):
                line = file.readline()
                type, connectivity = line.split(",", maxsplit=1)
                yield ElementTypes[type], tuple(int(x) for x in connectivity.split(","))

    def getNodeOutputTitles(self) -> Iterable[str]:
        """Gets the node output titles from file for the current output frame."""
        line, pointer = self._linePointers[self._currentFrame]["$NODE_OUTPUT_TITLES"]
        count: int = int(line.split(" ")[1])
        with open(self._filePath, self._mode) as file:
            file.seek(pointer)
            for _ in range(count):
                yield file.readline().strip()

    def getGlobalOutputTitles(self) -> Iterable[str]:
        """Gets the global output titles from file for the current output frame."""
        line, pointer = self._linePointers[self._currentFrame]["$GLOBAL_OUTPUT_TITLES"]
        count: int = int(line.split(" ")[1])
        with open(self._filePath, self._mode) as file:
            file.seek(pointer)
            for _ in range(count):
                yield file.readline().strip()

    def getNodeOutputValues(self, title: str) -> Iterable[float]:
        """Gets the node output values from file for the current output frame."""
        index: int = [*self.getNodeOutputTitles()].index(title)
        line, pointer = self._linePointers[self._currentFrame]["$NODE_OUTPUT_VALUES"]
        count: int = int(line.split(" ")[1])
        with open(self._filePath, self._mode) as file:
            file.seek(pointer)
            for _ in range(count):
                yield float(file.readline().split(",", maxsplit=index + 1)[index])

    def getGlobalOutputValues(self, title: str) -> float:
        """Gets the global output values from file for the current output frame."""
        index: int = [*self.getGlobalOutputTitles()].index(title)
        line, pointer = self._linePointers[self._currentFrame]["$GLOBAL_OUTPUT_VALUES"]
        count: int = int(line.split(" ")[1])
        with open(self._filePath, self._mode) as file:
            file.seek(pointer)
            for i in range(count):
                line = file.readline()
                if i == index: return float(line)
        return float("nan")

    def goToFirstFrame(self) -> None:
        """Points to the first frame in the output file."""
        self._currentFrame = 0

    def goToPreviousFrame(self) -> None:
        """Points to the previous frame in the output file."""
        if self._currentFrame == 0: return
        self._currentFrame -= 1

    def goToNextFrame(self) -> None:
        """Points to the next frame in the output file."""
        if self._currentFrame == self._frameCount - 1: return
        self._currentFrame += 1

    def goToLastFrame(self) -> None:
        """Points to the last frame in the output file."""
        self._currentFrame = self._frameCount - 1

    def goToFrame(self, frame: int) -> None:
        """Points to the specified frame in the output file."""
        if frame < 0 or frame >= self._frameCount: raise ValueError("invalid frame")
        self._currentFrame = frame

    @staticmethod
    def merge(filePath: str, selection: Iterable[tuple[str, Iterable[int]]], descriptions: Sequence[str] = (), deleteExisting: bool = False) -> None:
        """
        Merges multiple frames from multiple ODBs into a single ODB file. The parameter `filePath` specifies the file
        path for the new ODB file. If an ODB already exists, it will be replaced. The parameter `selection` specifies
        the existing ODBs and corresponding frames, e.g.,
        `selection=(('my_odb_1.out', (1, 2, 3)), ('my_odb_2.out', (4, 5)))` will merge frames 1, 2, and 3 from
        'my_odb_1.out' and frames 4 and 5 from 'my_odb_2.out' into a single ODB file. The `descriptions` parameter
        (optional) specifies a sequence of descriptions that override the descriptions of the frames. The
        `deleteExisting` parameter (optional) specifies if the existing ODB files should be deleted. By default, they
        are not deleted.
        """
        # delete previous ODB file
        if os.path.isfile(filePath): os.remove(filePath)

        # create new ODB
        new: ODB = ODB(filePath, mode="write")

        # append frames from existing ODBs
        count: int = 0
        for oldFilePath, frames in selection:
            old: ODB = ODB(oldFilePath, mode="read")
            for frame in frames:
                old.goToFrame(frame)
                new.writeNextFrame(
                    description=old.getDescription() if not descriptions else descriptions[count],
                    mesh=Mesh(nodes=old.getNodes(), elements=old.getElements()),
                    nodeOutput={title: old.getNodeOutputValues(title) for title in old.getNodeOutputTitles()},
                    globalOutput={title: old.getGlobalOutputValues(title) for title in old.getGlobalOutputTitles()}
                )
                count += 1

        # delete old ODB files if requested
        if deleteExisting:
            for oldFilePath, _ in selection:
                os.remove(oldFilePath)
