import os
from typing import Literal
from feapack.typing import Float3D
from feapack.io import AbaqusReader
from itertools import chain

SUPPORTED_ELEMENT_TYPES = (
    "CPS3", "CPE3", "CAX3", "CPS4", "CPE4", "CAX4", "CPS4R", "CPE4R", "CAX4R", "CPS6", "CPE6", "CAX6", "CPS8", "CPE8",
    "CAX8", "CPS8R", "CPE8R", "CAX8R", "C3D4", "C3D6", "C3D8", "C3D8R", "C3D10", "C3D15", "C3D20", "C3D20R"
)

def clean(filePath: str) -> None:
    """Cleans an Abaqus input file (*.inp) generated by Gmsh, making it compatible with FEAPACK."""
    # check extension
    match ext := os.path.splitext(filePath)[1].lower():
        case ".inp": pass
        case _: raise ValueError(f"unsupported file extension: '{ext}'")

    # initialize variables
    setType: str = ""
    setName: str = ""
    elementType: str = ""
    nodes: list[tuple[list[int], Float3D]] = []
    elements: dict[str, list[tuple[list[int], list[int]]]] = {type: [] for type in SUPPORTED_ELEMENT_TYPES}
    sets: dict[str, dict[str, list[int]]] = {"node-set": {}, "element-set": {}}
    action: Literal["read-command", "read-node", "read-element", "read-set", "pass"] = "pass"

    # read data
    with open(filePath, "r") as file:
        for line in (lines := AbaqusReader.cleanLines(file)):
            if line.startswith("*"):
                action = "read-command"
            match action:
                case "read-command":
                    match line.split(",")[0]:
                        case "*NODE":
                            action = "read-node"
                        case "*ELEMENT":
                            elementType = line.split("TYPE=")[1].split(",")[0]
                            action = "read-element" if elementType in SUPPORTED_ELEMENT_TYPES else "pass"
                        case "*NSET" | "*ELSET":
                            setType = "node-set" if line.startswith("*NSET") else "element-set"
                            setName = line.split("SET=")[1].split(",")[0]
                            action = "read-set"
                        case _:
                            action = "pass"
                case "read-node":
                    newIndex: int = -1
                    oldIndex: int = int((lineSplit := line.split(","))[0])
                    coordinates: list[float] = [float(x) for x in lineSplit[1:] if x]
                    while len(coordinates) < 3: coordinates.append(0.0)
                    nodes.append(([oldIndex, newIndex], (coordinates[0], coordinates[1], coordinates[2])))
                case "read-element":
                    newIndex: int = -1
                    oldIndex: int = int(line.split(",")[0])
                    connectivity: list[int] = []
                    skipIndex: bool = True
                    while True:
                        connectivity.extend(int(x) for x in line.split(",")[skipIndex:] if x)
                        if line[-1] == ",":
                            line = next(iter(lines))
                            skipIndex = False
                        else:
                            break
                    elements[elementType].append(([oldIndex, newIndex], connectivity))
                case "read-set":
                    if setName not in sets[setType].keys(): sets[setType][setName] = []
                    sets[setType][setName].extend(int(x) for x in line.split(",") if x)
                case "pass":
                    pass

    # sort nodes by their old indices
    nodes.sort(key=lambda x: x[0][0])

    # determine unconnected/unused nodes
    for elementType in elements.keys():
        for _, connectivity in elements[elementType]:
            for nodeIndex in connectivity:
                if nodes[nodeIndex - 1][0][0] != nodeIndex: raise RuntimeError("bad node numbering: missing nodes")
                nodes[nodeIndex - 1][0][1] = -2

    # new node numbering
    nodeCount: int = 0
    for node in nodes:
        if node[0][1] == -2:
            node[0][1] = nodeCount + 1
            nodeCount += 1

    # new element numbering
    elementCount: int = 0
    for elementType in elements.keys():
        for element in elements[elementType]:
            element[0][1] = elementCount + 1
            elementCount += 1

    # create mappings
    nodeMapping: dict[int, int] = {node[0][0]: node[0][1] for node in nodes}
    elementMapping: dict[int, int] = {element[0][0]: element[0][1] for element in chain(*elements.values())}

    # fix element connectivity
    for elementType in elements.keys():
        for element in elements[elementType]:
            for i in range(len(element[1])):
                element[1][i] = nodeMapping[element[1][i]]

    # fix node sets
    for setName, nodeSet in sets["node-set"].items():
        for i in range(len(nodeSet)):
            if nodeSet[i] in nodeMapping.keys(): nodeSet[i] = nodeMapping[nodeSet[i]]
            else: nodeSet[i] = -1
        sets["node-set"][setName] = list(filter(lambda x: x != -1, nodeSet))

    # fix element sets
    for setName, elementSet in sets["element-set"].items():
        for i in range(len(elementSet)):
            if elementSet[i] in elementMapping.keys(): elementSet[i] = elementMapping[elementSet[i]]
            else: elementSet[i] = -1
        sets["element-set"][setName] = list(filter(lambda x: x != -1, elementSet))

    # write to file
    with open(filePath, "w") as file:

        # nodes
        file.write("*Node\n")
        for node in nodes:
            if node[0][1] > 0:
                file.write(f"{node[0][1]}, {node[1][0]}, {node[1][1]}, {node[1][2]}\n")

        # elements
        for elementType in elements.keys():
            if len(elements[elementType]) == 0: continue
            file.write(f"*Element, type={elementType}\n")
            for element in elements[elementType]:
                if element[0][1] > 0:
                    file.write(f"{element[0][1]}, {", ".join(map(str, element[1]))}\n")

        # node sets
        k: int = 10 # max number of indices per line
        for setName, nodeSet in sets["node-set"].items():
            if len(nodeSet) == 0: continue
            file.write(f"*Nset, nset={setName}\n")
            for i in range(0, len(nodeSet), k):
                file.write(", ".join(map(str, nodeSet[i:i+k])) + "\n")

        # element sets
        for setName, elementSet in sets["element-set"].items():
            if len(elementSet) == 0: continue
            file.write(f"*Elset, elset={setName}\n")
            for i in range(0, len(elementSet), k):
                file.write(", ".join(map(str, elementSet[i:i+k])) + "\n")