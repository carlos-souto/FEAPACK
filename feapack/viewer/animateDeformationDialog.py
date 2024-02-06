import os
from typing import Literal, cast
from feapack.typing import Float2D
from feapack.viewer import Viewport
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QDialog, QGridLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, QCheckBox, \
    QSlider, QSpacerItem, QSizePolicy, QPushButton, QSpinBox, QFileDialog

class AnimateDeformationDialog(QDialog):
    """Animate deformation dialog."""

    __slots__ = ("_viewport", "_dsf", "_limits")

    def __init__(self, parent: QWidget, viewport: Viewport) -> None:
        """Constructor."""
        super().__init__(parent)

        # instance variables
        self._viewport: Viewport = viewport
        self._dsf: float = 1.0
        self._limits: Float2D = 0.0, 1.0

        # self
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setWindowFlag(Qt.WindowType.WindowMinMaxButtonsHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)
        self.setWindowTitle("Animate Deformation (Experimental)")
        self.resize(0, 0)

        # layout
        layout: QGridLayout = QGridLayout(self)
        layout.setObjectName("layout")
        self.setLayout(layout)

        # deformation group box
        deformationGroupBox: QGroupBox = QGroupBox(self)
        deformationGroupBox.setObjectName("deformationGroupBox")
        deformationGroupBox.setTitle("Deformation Scale Factor")
        layout.addWidget(deformationGroupBox, 0, 0, 1, 2)

        # deformation group box layout
        deformationGroupBoxLayout: QGridLayout = QGridLayout(deformationGroupBox)
        deformationGroupBoxLayout.setObjectName("deformationGroupBoxLayout")
        deformationGroupBox.setLayout(deformationGroupBoxLayout)

        # dsf label
        dsfLabel: QLabel = QLabel(deformationGroupBox)
        dsfLabel.setObjectName("dsfLabel")
        dsfLabel.setText("Specify:")
        deformationGroupBoxLayout.addWidget(dsfLabel, 0, 0, 1, 1)

        # dsf box
        dsfBox: QLineEdit = QLineEdit(deformationGroupBox)
        dsfBox.setObjectName("dsfBox")
        dsfBox.setFixedWidth(100)
        dsfBox.setText(str(self._dsf))
        dsfBox.editingFinished.connect(self.onDSFBoxEditingFinished)
        deformationGroupBoxLayout.addWidget(dsfBox, 0, 1, 1, 1)

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

        # animation mode group box
        animationModeGroupBox: QGroupBox = QGroupBox(self)
        animationModeGroupBox.setObjectName("animationModeGroupBox")
        animationModeGroupBox.setTitle("Animation Mode")
        layout.addWidget(animationModeGroupBox, 1, 0, 1, 2)

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

        # scaling mode group box
        scalingModeGroupBox: QGroupBox = QGroupBox(self)
        scalingModeGroupBox.setObjectName("scalingModeGroupBox")
        scalingModeGroupBox.setTitle("Scaling Mode")
        layout.addWidget(scalingModeGroupBox, 1, 2, 1, 2)

        # scaling mode group box layout
        scalingModeGroupBoxLayout: QGridLayout = QGridLayout(scalingModeGroupBox)
        scalingModeGroupBoxLayout.setObjectName("scalingModeGroupBoxLayout")
        scalingModeGroupBox.setLayout(scalingModeGroupBoxLayout)

        # half cycle button
        halfCycleButton: QRadioButton = QRadioButton(scalingModeGroupBox)
        halfCycleButton.setObjectName("halfCycleButton")
        halfCycleButton.setText("Half Cycle")
        halfCycleButton.setChecked(True)
        scalingModeGroupBoxLayout.addWidget(halfCycleButton, 0, 0, 1, 2)

        # full cycle button
        fullCycleButton: QRadioButton = QRadioButton(scalingModeGroupBox)
        fullCycleButton.setObjectName("fullCycleButton")
        fullCycleButton.setText("Full Cycle")
        fullCycleButton.setChecked(False)
        scalingModeGroupBoxLayout.addWidget(fullCycleButton, 1, 0, 1, 1)

        # mirror scalars box
        mirrorScalarsBox: QCheckBox = QCheckBox(scalingModeGroupBox)
        mirrorScalarsBox.setObjectName("mirrorScalarsBox")
        mirrorScalarsBox.setText("Mirror Scalars")
        mirrorScalarsBox.setChecked(False)
        mirrorScalarsBox.setEnabled(False)
        scalingModeGroupBoxLayout.addWidget(mirrorScalarsBox, 1, 1, 1, 1)

        # full cycle button -> mirror scalars box connection
        fullCycleButton.toggled.connect(mirrorScalarsBox.setEnabled)

        # frame rate group box
        frameRateGroupBox: QGroupBox = QGroupBox(self)
        frameRateGroupBox.setObjectName("frameRateGroupBox")
        frameRateGroupBox.setTitle("Frame Rate")
        layout.addWidget(frameRateGroupBox, 2, 0, 1, 2)

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

        # frame count group box
        frameCountGroupBox: QGroupBox = QGroupBox(self)
        frameCountGroupBox.setObjectName("frameCountGroupBox")
        frameCountGroupBox.setTitle("Frame Count")
        layout.addWidget(frameCountGroupBox, 2, 2, 1, 2)

        # frame count group box layout
        frameCountGroupBoxLayout: QGridLayout = QGridLayout(frameCountGroupBox)
        frameCountGroupBoxLayout.setObjectName("frameCountGroupBoxLayout")
        frameCountGroupBox.setLayout(frameCountGroupBoxLayout)

        # frame count label
        frameCountLabel: QLabel = QLabel(frameCountGroupBox)
        frameCountLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frameCountLabel.setObjectName("frameCountLabel")
        frameCountLabel.setText("30 frames")
        frameCountGroupBoxLayout.addWidget(frameCountLabel, 0, 0, 1, 3)

        # frame count slider
        frameCountSlider: QSlider = QSlider(frameCountGroupBox)
        frameCountSlider.setObjectName("frameCountSlider")
        frameCountSlider.setOrientation(Qt.Orientation.Horizontal)
        frameCountSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        frameCountSlider.setTracking(True)
        frameCountSlider.setRange(10, 60)
        frameCountSlider.setTickInterval(10)
        frameCountSlider.setSingleStep(1)
        frameCountSlider.setValue(30)
        frameCountSlider.valueChanged.connect(self.onFrameCountSliderValueChanged)
        frameCountGroupBoxLayout.addWidget(frameCountSlider, 1, 0, 1, 3)

        # min label
        minLabel: QLabel = QLabel(frameCountGroupBox)
        minLabel.setObjectName("minLabel")
        minLabel.setText("10")
        frameCountGroupBoxLayout.addWidget(minLabel, 2, 0, 1, 1)

        # min max spacer
        minMaxSpacer: QSpacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        frameCountGroupBoxLayout.addItem(minMaxSpacer, 2, 1, 1, 1)

        # max label
        maxLabel: QLabel = QLabel(frameCountGroupBox)
        maxLabel.setObjectName("maxLabel")
        maxLabel.setText("60")
        frameCountGroupBoxLayout.addWidget(maxLabel, 2, 2, 1, 1)

        # save box
        saveBox: QCheckBox = QCheckBox(self)
        saveBox.setObjectName("saveBox")
        saveBox.setText("Save Animation")
        saveBox.setChecked(False)
        layout.addWidget(saveBox, 3, 0, 1, 1)

        # button spacer
        buttonSpacer: QSpacerItem = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addItem(buttonSpacer, 3, 1, 1, 1)

        # play button
        playButton: QPushButton = QPushButton(self)
        playButton.setObjectName("playButton")
        playButton.setText("Play")
        playButton.setDefault(False)
        playButton.setAutoDefault(False)
        playButton.clicked.connect(self.onPlayButtonClicked)
        layout.addWidget(playButton, 3, 2, 1, 1)

        # repetitions box
        repetitionsBox: QSpinBox = QSpinBox(self)
        repetitionsBox.setObjectName("repetitionsBox")
        repetitionsBox.setMinimum(1)
        repetitionsBox.setMaximum(10)
        repetitionsBox.setValue(2)
        layout.addWidget(repetitionsBox, 3, 3, 1, 1)

        # save box -> repetitions box connection
        saveBox.stateChanged.connect(lambda state: repetitionsBox.setEnabled(not state))

    def onFrameRateSliderValueChanged(self) -> None:
        """On frame rate slider value changed."""
        frameRateLabel: QLabel = cast(QLabel, self.findChild(QLabel, "frameRateLabel"))
        frameRateSlider: QSlider = cast(QSlider, self.findChild(QSlider, "frameRateSlider"))
        frameRateLabel.setText(f"{frameRateSlider.value()} ms delay")

    def onFrameCountSliderValueChanged(self) -> None:
        """On frame count slider value changed."""
        frameCountLabel: QLabel = cast(QLabel, self.findChild(QLabel, "frameCountLabel"))
        frameCountSlider: QSlider = cast(QSlider, self.findChild(QSlider, "frameCountSlider"))
        frameCountLabel.setText(f"{frameCountSlider.value()} frames")

    def onDSFBoxEditingFinished(self) -> None:
        """On DSF box editing finished."""
        dsfBox: QLineEdit = cast(QLineEdit, self.findChild(QLineEdit, "dsfBox"))
        try:
            self._dsf = float(dsfBox.text())
        except ValueError:
            pass
        finally:
            dsfBox.setText(str(self._dsf))

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
        mirrorScalarsBox: QCheckBox = cast(QCheckBox, self.findChild(QCheckBox, "mirrorScalarsBox"))
        halfCycleButton: QRadioButton = cast(QRadioButton, self.findChild(QRadioButton, "halfCycleButton"))
        frameRateSlider: QSlider = cast(QSlider, self.findChild(QSlider, "frameRateSlider"))
        frameCountSlider: QSlider = cast(QSlider, self.findChild(QSlider, "frameCountSlider"))
        repetitionsBox: QSpinBox = cast(QSpinBox, self.findChild(QSpinBox, "repetitionsBox"))

        # get user input
        dsf: float = self._dsf
        limits: Float2D | None = None if autoComputeButton.isChecked() else self._limits
        animationMode: Literal["loop", "swing"] = "loop" if loopButton.isChecked() else "swing"
        scalingMode: Literal["half", "full", "full+scalars"] = \
            "half" if halfCycleButton.isChecked() else "full+scalars" if mirrorScalarsBox.isChecked() else "full"
        frameDelay: int = frameRateSlider.value()
        frameCount: int = frameCountSlider.value()
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

        # animate
        self._viewport.animateDeformation(
            dsf, limits, animationMode, scalingMode, frameCount, frameDelay, repetitions, filePath
        )
