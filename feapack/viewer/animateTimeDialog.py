import os
from typing import Literal, cast
from feapack.typing import Float2D
from feapack.viewer import Viewport
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QDialog, QGridLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, QCheckBox, \
    QSlider, QSpacerItem, QSizePolicy, QPushButton, QSpinBox, QFileDialog, QTreeWidget, QTreeWidgetItem

class AnimateTimeDialog(QDialog):
    """Animate time dialog."""

    __slots__ = ("_viewport", "_treeWidget", "_limits")

    def __init__(self, parent: QWidget, viewport: Viewport, treeWidget: QTreeWidget) -> None:
        """Constructor."""
        super().__init__(parent)

        # instance variables
        self._viewport: Viewport = viewport
        self._treeWidget: QTreeWidget = treeWidget
        self._limits: Float2D = 0.0, 1.0

        # self
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)
        self.setWindowTitle("Animate Time (Experimental)")
        self.resize(0, 0)

        # layout
        layout: QGridLayout = QGridLayout(self)
        layout.setObjectName("layout")
        self.setLayout(layout)

        # animation mode group box
        animationModeGroupBox: QGroupBox = QGroupBox(self)
        animationModeGroupBox.setObjectName("animationModeGroupBox")
        animationModeGroupBox.setTitle("Animation Mode")
        layout.addWidget(animationModeGroupBox, 0, 0, 1, 2)

        # animation mode group box layout
        animationModeGroupBoxLayout: QGridLayout = QGridLayout(animationModeGroupBox)
        animationModeGroupBoxLayout.setObjectName("animationModeGroupBoxLayout")
        animationModeGroupBox.setLayout(animationModeGroupBoxLayout)

        # loop button
        loopButton: QRadioButton = QRadioButton(animationModeGroupBox)
        loopButton.setObjectName("loopButton")
        loopButton.setText("Loop")
        loopButton.setChecked(True)
        animationModeGroupBoxLayout.addWidget(loopButton, 0, 0, 1, 1)

        # swing button
        swingButton: QRadioButton = QRadioButton(animationModeGroupBox)
        swingButton.setObjectName("swingButton")
        swingButton.setText("Swing")
        swingButton.setChecked(False)
        animationModeGroupBoxLayout.addWidget(swingButton, 1, 0, 1, 1)

        # legend limits group box
        legendLimitsGroupBox: QGroupBox = QGroupBox(self)
        legendLimitsGroupBox.setObjectName("legendLimitsGroupBox")
        legendLimitsGroupBox.setTitle("Legend Limits")
        layout.addWidget(legendLimitsGroupBox, 0, 2, 1, 2)

        # legend limits group box layout
        legendLimitsGroupBoxLayout: QGridLayout = QGridLayout(legendLimitsGroupBox)
        legendLimitsGroupBoxLayout.setObjectName("legendLimitsGroupBoxLayout")
        legendLimitsGroupBox.setLayout(legendLimitsGroupBoxLayout)

        # auto-compute button
        autoComputeButton: QRadioButton = QRadioButton(legendLimitsGroupBox)
        autoComputeButton.setObjectName("autoComputeButton")
        autoComputeButton.setText("Auto-compute")
        autoComputeButton.setChecked(True)
        legendLimitsGroupBoxLayout.addWidget(autoComputeButton, 0, 0, 1, 2)

        # specify button
        specifyButton: QRadioButton = QRadioButton(legendLimitsGroupBox)
        specifyButton.setObjectName("specifyButton")
        specifyButton.setText("Specify:")
        specifyButton.setChecked(False)
        legendLimitsGroupBoxLayout.addWidget(specifyButton, 1, 0, 1, 1)

        # legend limits box
        legendLimitsBox: QLineEdit = QLineEdit(legendLimitsGroupBox)
        legendLimitsBox.setObjectName("legendLimitsBox")
        legendLimitsBox.setFixedWidth(100)
        legendLimitsBox.setText(f"{self._limits[0]}, {self._limits[1]}")
        legendLimitsBox.setEnabled(False)
        legendLimitsBox.editingFinished.connect(self.onLegendLimitsBoxEditingFinished)
        legendLimitsGroupBoxLayout.addWidget(legendLimitsBox, 1, 1, 1, 1)

        # specify button -> legend limits box connection
        specifyButton.toggled.connect(legendLimitsBox.setEnabled)

        # frame rate group box
        frameRateGroupBox: QGroupBox = QGroupBox(self)
        frameRateGroupBox.setObjectName("frameRateGroupBox")
        frameRateGroupBox.setTitle("Frame Rate")
        layout.addWidget(frameRateGroupBox, 1, 0, 1, 4)

        # frame rate group box layout
        frameRateGroupBoxLayout: QGridLayout = QGridLayout(frameRateGroupBox)
        frameRateGroupBoxLayout.setObjectName("frameRateGroupBoxLayout")
        frameRateGroupBox.setLayout(frameRateGroupBoxLayout)

        # frame rate label
        frameRateLabel: QLabel = QLabel(frameRateGroupBox)
        frameRateLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frameRateLabel.setObjectName("frameRateLabel")
        frameRateLabel.setText("0 ms delay")
        frameRateGroupBoxLayout.addWidget(frameRateLabel, 0, 0, 1, 3)

        # frame rate slider
        frameRateSlider: QSlider = QSlider(frameRateGroupBox)
        frameRateSlider.setObjectName("frameRateSlider")
        frameRateSlider.setOrientation(Qt.Orientation.Horizontal)
        frameRateSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        frameRateSlider.setTracking(True)
        frameRateSlider.setRange(0, 500)
        frameRateSlider.setTickInterval(50)
        frameRateSlider.setSingleStep(10)
        frameRateSlider.setValue(0)
        frameRateSlider.valueChanged.connect(self.onFrameRateSliderValueChanged)
        frameRateGroupBoxLayout.addWidget(frameRateSlider, 1, 0, 1, 3)

        # slow label
        slowLabel: QLabel = QLabel(frameRateGroupBox)
        slowLabel.setObjectName("slowLabel")
        slowLabel.setText("Slow")
        frameRateGroupBoxLayout.addWidget(slowLabel, 2, 2, 1, 1)

        # slow fast spacer
        slowFastSpacer: QSpacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        frameRateGroupBoxLayout.addItem(slowFastSpacer, 2, 1, 1, 1)

        # fast label
        fastLabel: QLabel = QLabel(frameRateGroupBox)
        fastLabel.setObjectName("fastLabel")
        fastLabel.setText("Fast")
        frameRateGroupBoxLayout.addWidget(fastLabel, 2, 0, 1, 1)

        # save box
        saveBox: QCheckBox = QCheckBox(self)
        saveBox.setObjectName("saveBox")
        saveBox.setText("Save Animation")
        saveBox.setChecked(False)
        layout.addWidget(saveBox, 2, 0, 1, 1)

        # button spacer
        buttonSpacer: QSpacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addItem(buttonSpacer, 2, 1, 1, 1)

        # play button
        playButton: QPushButton = QPushButton(self)
        playButton.setObjectName("playButton")
        playButton.setText("Play")
        playButton.setDefault(False)
        playButton.setAutoDefault(False)
        playButton.clicked.connect(self.onPlayButtonClicked)
        layout.addWidget(playButton, 2, 2, 1, 1)

        # repetitions box
        repetitionsBox: QSpinBox = QSpinBox(self)
        repetitionsBox.setObjectName("repetitionsBox")
        repetitionsBox.setMinimum(1)
        repetitionsBox.setMaximum(10)
        repetitionsBox.setValue(2)
        layout.addWidget(repetitionsBox, 2, 3, 1, 1)

        # save box -> repetitions box connection
        saveBox.stateChanged.connect(lambda state: repetitionsBox.setEnabled(not state))

    def onFrameRateSliderValueChanged(self) -> None:
        """On frame rate slider value changed."""
        frameRateLabel: QLabel = cast(QLabel, self.findChild(QLabel, "frameRateLabel"))
        frameRateSlider: QSlider = cast(QSlider, self.findChild(QSlider, "frameRateSlider"))
        frameRateLabel.setText(f"{frameRateSlider.value()} ms delay")

    def onLegendLimitsBoxEditingFinished(self) -> None:
        """On legend limits box editing finished."""
        legendLimitsBox: QLineEdit = cast(QLineEdit, self.findChild(QLineEdit, "legendLimitsBox"))
        try:
            if len(split := legendLimitsBox.text().split(",")) != 2:
                raise ValueError("expected two comma-separated values")
            k0: float = float(split[0].strip())
            k1: float = float(split[1].strip())
            self._limits = min(k0, k1), max(k0, k1)
        except ValueError:
            pass
        finally:
            legendLimitsBox.setText(f"{self._limits[0]}, {self._limits[1]}")

    def onPlayButtonClicked(self) -> None:
        """On play button clicked."""
        # get widgets
        saveBox: QCheckBox = cast(QCheckBox, self.findChild(QCheckBox, "saveBox"))
        autoComputeButton: QRadioButton = cast(QRadioButton, self.findChild(QRadioButton, "autoComputeButton"))
        loopButton: QRadioButton = cast(QRadioButton, self.findChild(QRadioButton, "loopButton"))
        frameRateSlider: QSlider = cast(QSlider, self.findChild(QSlider, "frameRateSlider"))
        repetitionsBox: QSpinBox = cast(QSpinBox, self.findChild(QSpinBox, "repetitionsBox"))

        # get user input
        limits: Float2D | None = None if autoComputeButton.isChecked() else self._limits
        animationMode: Literal["loop", "swing"] = "loop" if loopButton.isChecked() else "swing"
        frameDelay: int = frameRateSlider.value()
        repetitions: int = repetitionsBox.value()
        saveAnimation: bool = saveBox.isChecked()

        # get file path
        filePath: str | None = None
        if saveAnimation:
            repetitions = 1
            if filePath := QFileDialog.getSaveFileName(
                parent=self,
                caption="Save Animation",
                filter="GIF Image Files (*.gif)",
                options=QFileDialog.Option.DontUseNativeDialog
            )[0]:
                filePath = os.path.splitext(filePath)[0] + ".gif"
            else:
                return

        # get selected branch
        branch: list[QTreeWidgetItem] = [item] if (item := self._treeWidget.currentItem()) else []
        if len(branch) > 0:
            while parent := branch[-1].parent():
                branch.append(parent)
            branch.reverse()
        depth: int = len(branch)

        # get node output title
        nodeOutputTitle: str = ""
        if depth > 2 and branch[1].text(0) == "Node Output" and branch[-1].childCount() == 0:
            nodeOutputTitle = ">".join(item.text(0) for item in branch[2:])

        # animate
        self._viewport.animateTime(limits, animationMode, frameDelay, repetitions, nodeOutputTitle, filePath)
