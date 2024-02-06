from feapack import __version__
from PySide6.QtGui import Qt, QFont
from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QLabel

class AboutDialog(QDialog):
    """The About dialog."""

    __slots__ = ()

    def __init__(self, parent: QWidget) -> None:
        """Dialog constructor."""
        super().__init__(parent)

        # self
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)
        self.setWindowTitle("About FEAPACK")
        self.resize(0, 0)

        # font 0
        font0: QFont = QFont()
        font0.setBold(True)
        font0.setPointSize(14)

        # font 1
        font1: QFont = QFont()
        font1.setBold(True)
        font1.setPointSize(10)

        # layout
        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setObjectName("layout")
        self.setLayout(layout)

        # title
        title: QLabel = QLabel(self)
        title.setObjectName("title")
        title.setFont(font0)
        title.setText(f"About FEAPACK v{__version__}")
        layout.addWidget(title)

        # subtitle
        subtitle: QLabel = QLabel(self)
        subtitle.setObjectName("subtitle")
        subtitle.setFont(font1)
        subtitle.setText("A finite element analysis package for solids using Python.")
        layout.addWidget(subtitle)

        # copyright
        copyright: QLabel = QLabel(self)
        copyright.setObjectName("copyright")
        copyright.setText("Copyright © 2024 Carlos Souto.\nAll rights reserved.")
        layout.addWidget(copyright)

        # license
        license: QLabel = QLabel(self)
        license.setObjectName("license")
        license.setText("<b>License:</b> <a href='https://www.gnu.org/licenses/gpl-3.0.en.html'>GNU General Public License v3.0</a>")
        license.setTextFormat(Qt.TextFormat.RichText)
        license.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        license.setOpenExternalLinks(True)
        layout.addWidget(license)

        # repository
        repository: QLabel = QLabel(self)
        repository.setObjectName("repository")
        repository.setText("<b>Repository:</b> <a href='https://github.com/carlos-souto/FEAPACK'>github.com/carlos-souto/FEAPACK</a>")
        repository.setTextFormat(Qt.TextFormat.RichText)
        repository.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        repository.setOpenExternalLinks(True)
        layout.addWidget(repository)
