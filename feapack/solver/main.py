import os
import sys
import time
import traceback
import numpy as np
import feapack.solver.validation as val
import feapack.solver.procedures as pro
import feapack.solver.linearAlgebra as linalg
from typing import Literal
from datetime import datetime
from collections.abc import Sequence
from feapack import __version__
from feapack.model import MDB, ODB
from feapack.typing import Real, RealVector, RealMatrix

_printFlag: bool = False
"""Determines if log messages should be printed."""

_writeFlag: bool = False
"""Determines if log messages should be written to file."""

_logFilePath: str = ""
"""Current .log file path."""

_outFilePath: str = ""
"""Current .out file path."""

def _log(message: str = "", append: bool = True) -> None:
    """Logs the specified message."""
    if _printFlag: print(message, flush=True)
    if _writeFlag:
        with open(_logFilePath, "a" if append else "w") as logFile:
            logFile.write(message + "\n")

def _staticAnalysis(mdb: MDB, processes: int) -> None:
    """Performs a linear-elastic static analysis."""
    # log
    _log("Building algebraic system...")

    # compute stiffness matrix
    Kaa, Kab, Kba, Kbb = pro.assembleStiffnessMatrix(mdb, processes)

    # compute equivalent nodal load vector
    Pa: RealVector = np.zeros(shape=(mdb.mesh.activeDOFCount,), dtype=Real)
    Pa += pro.assembleConcentratedLoadVector(mdb)       # add concentrated loads (Pc)
    Pa += pro.assembleSurfaceLoadVector(mdb, processes) # add surface loads (Ps)
    Pa += pro.assembleBodyLoadVector(mdb, processes)    # add body loads (Pb)

    # compute prescribed nodal displacement vector
    Ub: RealVector = pro.assemblePrescribedDisplacementVector(mdb)

    # log
    _log("Solving algebraic system...")

    # compute unknown nodal displacement vector (solution)
    rhs: RealVector = Pa - linalg.spmatmul(Kab, Ub)
    Ua: RealVector = linalg.spsolve(Kaa, rhs)

    # log
    _log("General post-processing...")

    # compute strain energy
    U: float = 0.5*np.dot(Ua, rhs)

    # compute unknown nodal load vector (reaction forces)
    Pb: RealVector = linalg.spmatmul(Kba, Ua) + linalg.spmatmul(Kbb, Ub)

    # compute internal nodal force vector
    # also computes the basic components of strain and stress at the integration points
    Fa, _, ε_ips, σ_ips = pro.assembleInternalForceVector(mdb, Ua, Ub, processes)

    # compute force residual (infinity norm of the out-of-balance forces)
    R: float = np.max(np.abs(rhs - Fa))

    # compute additional strain and stress measures (principal strains, principal stresses, and equivalent stresses)
    ε_ips = pro.extendStrain(mdb, ε_ips, processes)
    σ_ips = pro.extendStress(mdb, σ_ips, processes)

    # extrapolate strain and stress from the element integration points to the element nodes
    ε_nds: Sequence[RealMatrix] = pro.extrapolate(mdb, ε_ips, processes)
    σ_nds: Sequence[RealMatrix] = pro.extrapolate(mdb, σ_ips, processes)

    # compute values at mesh nodes (final smoothing)
    ε_msh: RealMatrix = pro.smoothing(mdb, ε_nds)
    σ_msh: RealMatrix = pro.smoothing(mdb, σ_nds)

    # convert global vectors to result matrices
    disp: RealMatrix = pro.unshuffleVector(mdb, Ua, Ub)
    reac: RealMatrix = pro.unshuffleVector(mdb, None, Pb)
    forc: RealMatrix = pro.unshuffleVector(mdb, Pa, None)

    # log
    _log("Writing output frame 0 to file...")

    # write to file: initial state
    odb: ODB = ODB(_outFilePath, mode="write", replace=True)
    odb.writeNextFrame(description="Increment 0: Time = 0.0", mesh=mdb.mesh)

    # log
    _log("Writing output frame 1 to file...")

    # write to file: deformed state
    odb.writeNextFrame(
        description="Increment 1: Time = 1.0",
        mesh=mdb.mesh,
        nodeOutput={
            "Displacement>Displacement in X":             disp[:,  0],
            "Displacement>Displacement in Y":             disp[:,  1],
            "Displacement>Displacement in Z":             disp[:,  2],
            "Displacement>Magnitude of Displacement":     disp[:,  3],
            "Reaction Force>Reaction Force in X":         reac[:,  0],
            "Reaction Force>Reaction Force in Y":         reac[:,  1],
            "Reaction Force>Reaction Force in Z":         reac[:,  2],
            "Reaction Force>Magnitude of Reaction Force": reac[:,  3],
            "Nodal Force>Nodal Force in X":               forc[:,  0],
            "Nodal Force>Nodal Force in Y":               forc[:,  1],
            "Nodal Force>Nodal Force in Z":               forc[:,  2],
            "Nodal Force>Magnitude of Nodal Force":       forc[:,  3],
            "Strain>Component XX of Strain":             ε_msh[:,  0],
            "Strain>Component YY of Strain":             ε_msh[:,  1],
            "Strain>Component ZZ of Strain":             ε_msh[:,  2],
            "Strain>Component YZ of Strain":             ε_msh[:,  3],
            "Strain>Component ZX of Strain":             ε_msh[:,  4],
            "Strain>Component XY of Strain":             ε_msh[:,  5],
            "Strain>Max. Principal Value of Strain":     ε_msh[:,  6],
            "Strain>Mid. Principal Value of Strain":     ε_msh[:,  7],
            "Strain>Min. Principal Value of Strain":     ε_msh[:,  8],
            "Strain>Major Principal Value of Strain":    ε_msh[:,  9],
            "Stress>Component XX of Stress":             σ_msh[:,  0],
            "Stress>Component YY of Stress":             σ_msh[:,  1],
            "Stress>Component ZZ of Stress":             σ_msh[:,  2],
            "Stress>Component YZ of Stress":             σ_msh[:,  3],
            "Stress>Component ZX of Stress":             σ_msh[:,  4],
            "Stress>Component XY of Stress":             σ_msh[:,  5],
            "Stress>Max. Principal Value of Stress":     σ_msh[:,  6],
            "Stress>Mid. Principal Value of Stress":     σ_msh[:,  7],
            "Stress>Min. Principal Value of Stress":     σ_msh[:,  8],
            "Stress>Major Principal Value of Stress":    σ_msh[:,  9],
            "Stress>Equivalent Tresca Stress":           σ_msh[:, 10],
            "Stress>Equivalent Mises Stress":            σ_msh[:, 11],
            "Stress>Equivalent Pressure Stress":         σ_msh[:, 12],
        },
        globalOutput={
            "General>Time":        1.0,
            "General>Residual":      R,
            "General>Strain Energy": U,
        }
    )

def _frequencyAnalysis(mdb: MDB, k0: int, processes: int) -> None:
    """
    Performs a frequency analysis (extraction of undamped natural frequencies and corresponding mode shapes).
    The input parameter `k0: int` corresponds to the requested number of eigenvalues and eigenvectors.
    """
    # log
    _log("Building algebraic system...")

    # compute stiffness matrix
    Kaa, _, _, _ = pro.assembleStiffnessMatrix(mdb, processes)

    # compute mass matrix
    Maa, _, _, _ = pro.assembleMassMatrix(mdb, processes)

    # log
    _log("Solving eigenproblem...")

    # solve generalized sparse eigenproblem
    eigenvalues, eigenvectors, residuals = linalg.speigen(Kaa, Maa, k0, which="S")

    # log
    _log("General post-processing...")

    # compute frequencies
    frequencies: RealVector = np.sqrt(eigenvalues)/(2.0*np.pi)

    # normalize eigenvectors with respect to the mass matrix
    for i in range(eigenvalues.size):
        φi: RealVector = eigenvectors[:, i]
        norm: float = np.sqrt(np.dot(φi, linalg.spmatmul(Maa, φi)))
        eigenvectors[:, i] = φi/norm

    # write to file
    odb: ODB = ODB(_outFilePath, mode="write", replace=True)
    for i in range(eigenvalues.size):

        # log
        _log(f"Writing output frame {i} to file...")

        # write frame
        disp: RealMatrix = pro.unshuffleVector(mdb, eigenvectors[:, i], None)
        odb.writeNextFrame(
            description=f"Mode {i + 1}: Frequency = {frequencies[i]:+.3E}",
            mesh=mdb.mesh,
            nodeOutput={
                "Displacement>Displacement in X":         disp[:,  0],
                "Displacement>Displacement in Y":         disp[:,  1],
                "Displacement>Displacement in Z":         disp[:,  2],
                "Displacement>Magnitude of Displacement": disp[:,  3],
            },
            globalOutput={
                "General>Eigenvalue": eigenvalues[i],
                "General>Frequency":  frequencies[i],
                "General>Residual":     residuals[i],
            }
        )

def _bucklingAnalysis(mdb: MDB, k0: int, processes: int) -> None:
    """
    Performs an eigenvalue buckling analysis (extraction of critical loads and corresponding mode shapes).
    The input parameter `k0: int` corresponds to the requested number of eigenvalues and eigenvectors.
    """
    # log
    _log("Building algebraic system for static analysis...")

    # compute stiffness matrix
    Kaa, Kab, _, _ = pro.assembleStiffnessMatrix(mdb, processes)

    # compute equivalent nodal load vector
    Pa: RealVector = np.zeros(shape=(mdb.mesh.activeDOFCount,), dtype=Real)
    Pa += pro.assembleConcentratedLoadVector(mdb)       # add concentrated loads (Pc)
    Pa += pro.assembleSurfaceLoadVector(mdb, processes) # add surface loads (Ps)
    Pa += pro.assembleBodyLoadVector(mdb, processes)    # add body loads (Pb)

    # compute prescribed nodal displacement vector
    Ub: RealVector = pro.assemblePrescribedDisplacementVector(mdb)

    # log
    _log("Solving algebraic system (static analysis)...")

    # compute unknown nodal displacement vector (solution of static analysis)
    rhs: RealVector = Pa - linalg.spmatmul(Kab, Ub)
    Ua: RealVector = linalg.spsolve(Kaa, rhs)

    # log
    _log("Building algebraic system for buckling analysis...")

    # compute stress-stiffness matrix
    Saa, _, _, _ = pro.assembleStressStiffnessMatrix(mdb, Ua, Ub, processes)

    # log
    _log("Solving eigenproblem...")

    # solve generalized sparse eigenproblem
    eigenvalues, eigenvectors, residuals = linalg.speigen(Saa, Kaa, k0, which="S")
    eigenvalues = -1.0/eigenvalues

    # log
    _log("General post-processing...")

    # normalize eigenvectors
    for i in range(eigenvalues.size):
        φi: RealVector = eigenvectors[:, i]
        norm: float = np.max(np.abs(φi))
        eigenvectors[:, i] = φi/norm

    # write to file
    odb: ODB = ODB(_outFilePath, mode="write", replace=True)
    for i in range(eigenvalues.size):

        # log
        _log(f"Writing output frame {i} to file...")

        # write frame
        disp: RealMatrix = pro.unshuffleVector(mdb, eigenvectors[:, i], None)
        odb.writeNextFrame(
            description=f"Mode {i + 1}: Eigenvalue = {eigenvalues[i]:+.3E}",
            mesh=mdb.mesh,
            nodeOutput={
                "Displacement>Displacement in X":         disp[:,  0],
                "Displacement>Displacement in Y":         disp[:,  1],
                "Displacement>Displacement in Z":         disp[:,  2],
                "Displacement>Magnitude of Displacement": disp[:,  3],
            },
            globalOutput={
                "General>Eigenvalue": eigenvalues[i],
                "General>Residual":     residuals[i],
            }
        )

def solve(
    mdb: MDB, analysis: Literal["static", "frequency", "buckling"], k0: int = 10, jobName: str = "", processes: int = 1,
    printLog: bool = True, writeLog: bool = True
) -> None:
    """
    Performs the specified finite element analysis.

    Input parameters:
    * `mdb: MDB` specifies the finite element model database for the analysis.

    * `analysis: Literal["static", "frequency", "buckling"]` specifies the type of analysis to perform: "static",
    "frequency" or "buckling".

    * `k0: int = 10` (optional) specifies the number of eigenvalues and corresponding eigenvectors to extract during a
    "frequency" or "buckling" analysis (by default, 10); ignored for a "static" analysis.

    * `jobName: str = ""` (optional) specifies the name for the .log and .out files; by default, the calling script file
    name is used.

    * `processes: int = 1` (optional) specifies the number of processes to use; by default, 1 process is used
    (sequential mode). If a value greater than 1 is specified, parallel loops are used when possible. In parallel mode,
    a main guard is required in the calling script (e.g., `if __name__ == '__main__': ...`).

    * `printLog: bool = True` (optional) determines if log messages are to be printed; by default, log messages are
    printed.

    * `writeLog: bool = True` (optional) determines if log messages are to be written to the log file; by default, a log
    file is created, replacing any existing.
    """
    # log and output files
    global _logFilePath, _outFilePath, _printFlag, _writeFlag
    if not jobName: jobName = sys.argv[0]
    _logFilePath = os.path.splitext(jobName)[0] + ".log"
    _outFilePath = os.path.splitext(jobName)[0] + ".out"
    _printFlag = printLog
    _writeFlag = writeLog

    # start timer
    timerStart: float = time.perf_counter()

    try:
        # general info
        _date: str = datetime.now().date().isoformat()
        _time: str = datetime.now().time().isoformat("seconds")
        _log("+-------------------------------------+", append=False)
        _log("|                                     |")
        _log("|   F E A P A C K   -   S O L V E R   |")
        _log("|  ---------------------------------  |")
        _log(f"|{"VERSION " + __version__:^37}|")
        _log("|                                     |")
        _log(f"|   DATE {_date}   TIME {_time}   |")
        _log("|                                     |")
        _log("|                                     |")
        _log(f"|{"--- START OF RUN ---":^37}|")
        _log("|                                     |")
        _log("+-------------------------------------+")
        _log()
        _log("GENERAL INFO")
        _log("------------")
        _log(f"* Analysis    {analysis.strip().lower()}")
        _log(f"* Mode        {"parallel" if processes > 1 else "sequential"}")
        _log(f"* Processes   {max(processes, 1)}")
        _log()

        # check the model database
        _log("MODEL DATABASE CHECKS")
        _log("---------------------")
        errors, warnings = val.checkMDB(mdb, analysis)
        errorCount: int = len(errors)
        warningCount: int = len(warnings)
        for warning in warnings: _log("[Warning] " + warning)
        for error in errors: _log("[Error] " + error)
        if errorCount == 0 and warningCount == 0:
            _log("Basic checks found no warnings nor errors")
        else:
            message: str = "Basic checks found "
            if warningCount > 0: message += f"{warningCount} warning(s)"
            if warningCount > 0 and errorCount > 0: message += " and "
            if errorCount > 0: message += f"{errorCount} error(s)"
            _log(message)
        _log()

        # abort on errors
        if errorCount > 0:
            _log("Solver has stopped prematurely due to errors (see above)")
            return

        # general pre-processing
        _log("PRE-PROCESSING")
        _log("--------------")
        mdb._buildDOFs()
        mdb._assignElementProperties()
        _log(f"Number of nodes: {mdb.mesh.nodeCount}")
        _log(f"Number of elements: {mdb.mesh.elementCount}")
        _log(f"Number of active degrees of freedom: {mdb.mesh.activeDOFCount}")
        _log(f"Number of inactive degrees of freedom: {mdb.mesh.inactiveDOFCount}")
        _log()

        # perform analysis
        match analysis.strip().lower():
            case "static":
                _log("STATIC ANALYSIS")
                _log("---------------")
                _staticAnalysis(mdb, processes)
            case "frequency":
                _log("FREQUENCY ANALYSIS")
                _log("------------------")
                _frequencyAnalysis(mdb, k0, processes)
            case "buckling":
                _log("BUCKLING ANALYSIS")
                _log("-----------------")
                _bucklingAnalysis(mdb, k0, processes)
            case _:
                raise ValueError(f"undefined analysis type: '{analysis}'")
        _log()
        _log("Successful run")

    # log exceptions
    except:
        _log()
        _log(traceback.format_exc())
        _log("Solver has stopped prematurely due to an exception (see above)")
        raise

    # log final messages
    finally:
        timerStop: float = time.perf_counter()
        _log(f"Elapsed time is {round(timerStop - timerStart, 3)} seconds")
        _log("--- END OF RUN ---")
