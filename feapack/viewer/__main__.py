import sys
import feapack.resources as res
from feapack.viewer import MainWindow
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":

    # create application object
    app: QApplication = QApplication(sys.argv)
    app.setStyle("Fusion")

    # load resources
    res.load(QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark)

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
