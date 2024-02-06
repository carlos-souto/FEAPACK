import sys
import feapack.resources as res
from feapack.viewer import MainWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":

    # determine light or dark mode (experimental)
    darkMode: bool = "-dark" in sys.argv
    argv: list[str] = [sys.argv[0], "-platform", f"windows:darkmode={1 if not darkMode else 2}"]

    # create application object
    app: QApplication = QApplication(argv)
    app.setStyle("Fusion")

    # load resources
    res.load(darkMode)

    # create main window
    mainWindow: MainWindow = MainWindow()
    mainWindow.show()

    # redirect standard streams
    sys.stdin = mainWindow.cli().stdin()
    sys.stdout = mainWindow.cli().stdout()
    sys.stderr = mainWindow.cli().stderr()

    # make stuff available for CLI
    mainWindow.cli().push("from feapack.viewer import *")

    # launch application
    exitCode: int = app.exec()

    # restore streams
    sys.stdin = sys.__stdin__
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    # exit application
    sys.exit(exitCode)
