import os
import feapack.resources as res
from typing import Literal, cast
from collections.abc import Iterable
from feapack.model import ODB
from feapack.viewer import CLI, Viewport, ODBView, Views, RenderingModes, Spectrums, InteractionTypes, AboutDialog, \
    AnimateDeformationDialog, AnimateTimeDialog
from PySide6.QtGui import Qt, QColor, QAction
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QSizePolicy, QSplitter, QTreeWidget, QMenuBar, QMenu, \
    QFileDialog, QTreeWidgetItem, QToolBar, QLineEdit, QLabel, QComboBox

class MainWindow(QMainWindow):
    """The main window of the application."""

    __slots__ = ("_odb", "_odbView", "_animateDeformationDialog", "_animateTimeDialog")

    def __init__(self) -> None:
        """Main window constructor."""
        super().__init__()

        # instance variables
        self._odb: ODB | None = None
        self._odbView: ODBView | None = None

        # main window
        self.setWindowIcon(res.icons["feapack"])
        self.setWindowTitle("FEAPACK Viewer")
        self.resize(900, 720)

        # menu bar
        menuBar: QMenuBar = QMenuBar(self)
        menuBar.setObjectName("menuBar")
        self.setMenuBar(menuBar)

        # file menu
        fileMenu: QMenu = QMenu(menuBar)
        fileMenu.setObjectName("fileMenu")
        fileMenu.setTitle("File")
        menuBar.addMenu(fileMenu)

        # file > open action
        fileOpenAction: QAction = QAction(fileMenu)
        fileOpenAction.setObjectName("fileOpenAction")
        fileOpenAction.setIcon(res.graphics["file-open"])
        fileOpenAction.setText("Open...")
        fileOpenAction.triggered.connect(self.onFileOpenActionTriggered)
        fileMenu.addAction(fileOpenAction)

        # file > close action
        fileCloseAction: QAction = QAction(fileMenu)
        fileCloseAction.setObjectName("fileCloseAction")
        fileCloseAction.setIcon(res.graphics["file-close"])
        fileCloseAction.setText("Close")
        fileCloseAction.triggered.connect(self.onFileCloseActionTriggered)
        fileMenu.addAction(fileCloseAction)

        # separator
        fileMenu.addSeparator()

        # file > print action
        filePrintAction: QAction = QAction(fileMenu)
        filePrintAction.setObjectName("filePrintAction")
        filePrintAction.setIcon(res.graphics["file-print"])
        filePrintAction.setText("Print...")
        filePrintAction.triggered.connect(self.onFilePrintActionTriggered)
        fileMenu.addAction(filePrintAction)

        # separator
        fileMenu.addSeparator()

        # file > exit action
        fileExitAction: QAction = QAction(fileMenu)
        fileExitAction.setObjectName("fileExitAction")
        fileExitAction.setIcon(res.graphics["file-exit"])
        fileExitAction.setText("Exit")
        fileExitAction.triggered.connect(self.close)
        fileMenu.addAction(fileExitAction)

        # animate menu
        animateMenu: QMenu = QMenu(menuBar)
        animateMenu.setObjectName("animateMenu")
        animateMenu.setTitle("Animate")
        menuBar.addMenu(animateMenu)

        # animate deformation action
        animateDeformationAction: QAction = QAction(animateMenu)
        animateDeformationAction.setObjectName("animateDeformationAction")
        animateDeformationAction.setIcon(res.graphics["animate"])
        animateDeformationAction.setText("Deformation...")
        animateDeformationAction.triggered.connect(self.onAnimateDeformationActionTriggered)
        animateMenu.addAction(animateDeformationAction)

        # animate time action
        animateTimeAction: QAction = QAction(animateMenu)
        animateTimeAction.setObjectName("animateTimeAction")
        animateTimeAction.setIcon(res.graphics["animate"])
        animateTimeAction.setText("Time...")
        animateTimeAction.triggered.connect(self.onAnimateTimeActionTriggered)
        animateMenu.addAction(animateTimeAction)

        # help menu
        helpMenu: QMenu = QMenu(menuBar)
        helpMenu.setObjectName("helpMenu")
        helpMenu.setTitle("Help")
        menuBar.addMenu(helpMenu)

        # help about action
        helpAboutAction: QAction = QAction(helpMenu)
        helpAboutAction.setObjectName("helpAboutAction")
        helpAboutAction.setIcon(res.graphics["help-about"])
        helpAboutAction.setText("About")
        helpAboutAction.triggered.connect(self.onHelpAboutActionTriggered)
        helpMenu.addAction(helpAboutAction)

        # views tool bar
        viewsToolBar: QToolBar = QToolBar(self)
        viewsToolBar.setObjectName("viewsToolBar")
        self.addToolBar(viewsToolBar)

        # view front action
        viewFrontAction: QAction = QAction(viewsToolBar)
        viewFrontAction.setObjectName("viewFrontAction")
        viewFrontAction.setIcon(res.graphics["view-front"])
        viewFrontAction.setToolTip("View Front")
        viewFrontAction.triggered.connect(self.onViewFrontActionTriggered)
        viewsToolBar.addAction(viewFrontAction)

        # view back action
        viewBackAction: QAction = QAction(viewsToolBar)
        viewBackAction.setObjectName("viewBackAction")
        viewBackAction.setIcon(res.graphics["view-back"])
        viewBackAction.setToolTip("View Back")
        viewBackAction.triggered.connect(self.onViewBackActionTriggered)
        viewsToolBar.addAction(viewBackAction)

        # view top action
        viewTopAction: QAction = QAction(viewsToolBar)
        viewTopAction.setObjectName("viewTopAction")
        viewTopAction.setIcon(res.graphics["view-top"])
        viewTopAction.setToolTip("View Top")
        viewTopAction.triggered.connect(self.onViewTopActionTriggered)
        viewsToolBar.addAction(viewTopAction)

        # view bottom action
        viewBottomAction: QAction = QAction(viewsToolBar)
        viewBottomAction.setObjectName("viewBottomAction")
        viewBottomAction.setIcon(res.graphics["view-bottom"])
        viewBottomAction.setToolTip("View Bottom")
        viewBottomAction.triggered.connect(self.onViewBottomActionTriggered)
        viewsToolBar.addAction(viewBottomAction)

        # view left action
        viewLeftAction: QAction = QAction(viewsToolBar)
        viewLeftAction.setObjectName("viewLeftAction")
        viewLeftAction.setIcon(res.graphics["view-left"])
        viewLeftAction.setToolTip("View Left")
        viewLeftAction.triggered.connect(self.onViewLeftActionTriggered)
        viewsToolBar.addAction(viewLeftAction)

        # view right action
        viewRightAction: QAction = QAction(viewsToolBar)
        viewRightAction.setObjectName("viewRightAction")
        viewRightAction.setIcon(res.graphics["view-right"])
        viewRightAction.setToolTip("View Right")
        viewRightAction.triggered.connect(self.onViewRightActionTriggered)
        viewsToolBar.addAction(viewRightAction)

        # view isometric action
        viewIsometricAction: QAction = QAction(viewsToolBar)
        viewIsometricAction.setObjectName("viewIsometricAction")
        viewIsometricAction.setIcon(res.graphics["view-isometric"])
        viewIsometricAction.setToolTip("View Isometric")
        viewIsometricAction.triggered.connect(self.onViewIsometricActionTriggered)
        viewsToolBar.addAction(viewIsometricAction)

        # view auto-fit action
        viewAutoFitAction: QAction = QAction(viewsToolBar)
        viewAutoFitAction.setObjectName("viewAutoFitAction")
        viewAutoFitAction.setIcon(res.graphics["view-auto-fit"])
        viewAutoFitAction.setToolTip("View Auto-Fit")
        viewAutoFitAction.triggered.connect(self.onViewAutoFitActionTriggered)
        viewsToolBar.addAction(viewAutoFitAction)

        # interaction tool bar
        interactionToolBar: QToolBar = QToolBar(self)
        interactionToolBar.setObjectName("interactionToolBar")
        self.addToolBar(interactionToolBar)

        # rotate action
        rotateAction: QAction = QAction(interactionToolBar)
        rotateAction.setObjectName("rotateAction")
        rotateAction.setIcon(res.graphics["interaction-rotate"])
        rotateAction.setToolTip("Rotate (Hold Shift to Spin)")
        rotateAction.setCheckable(True)
        rotateAction.setChecked(True)
        rotateAction.triggered.connect(self.onRotateActionTriggered)
        interactionToolBar.addAction(rotateAction)

        # pan action
        panAction: QAction = QAction(interactionToolBar)
        panAction.setObjectName("panAction")
        panAction.setIcon(res.graphics["interaction-pan"])
        panAction.setToolTip("Pan")
        panAction.setCheckable(True)
        panAction.setChecked(False)
        panAction.triggered.connect(self.onPanActionTriggered)
        interactionToolBar.addAction(panAction)

        # zoom action
        zoomAction: QAction = QAction(interactionToolBar)
        zoomAction.setObjectName("zoomAction")
        zoomAction.setIcon(res.graphics["interaction-zoom"])
        zoomAction.setToolTip("Zoom")
        zoomAction.setCheckable(True)
        zoomAction.setChecked(False)
        zoomAction.triggered.connect(self.onZoomActionTriggered)
        interactionToolBar.addAction(zoomAction)

        # rendering tool bar
        renderingToolBar: QToolBar = QToolBar(self)
        renderingToolBar.setObjectName("renderingToolBar")
        self.addToolBar(renderingToolBar)

        # render in wireframe action
        renderInWireframeAction: QAction = QAction(renderingToolBar)
        renderInWireframeAction.setObjectName("renderInWireframeAction")
        renderInWireframeAction.setIcon(res.graphics["rendering-wireframe"])
        renderInWireframeAction.setToolTip("Rendering: Wireframe")
        renderInWireframeAction.setCheckable(True)
        renderInWireframeAction.setChecked(False)
        renderInWireframeAction.triggered.connect(self.onRenderInWireframeActionTriggered)
        renderingToolBar.addAction(renderInWireframeAction)

        # render in filled action
        renderInFilledAction: QAction = QAction(renderingToolBar)
        renderInFilledAction.setObjectName("renderInFilledAction")
        renderInFilledAction.setIcon(res.graphics["rendering-filled"])
        renderInFilledAction.setToolTip("Rendering: Filled")
        renderInFilledAction.setCheckable(True)
        renderInFilledAction.setChecked(True)
        renderInFilledAction.triggered.connect(self.onRenderInFilledActionTriggered)
        renderingToolBar.addAction(renderInFilledAction)

        # render in filled (no edges) action
        renderInFilledNoEdgesAction: QAction = QAction(renderingToolBar)
        renderInFilledNoEdgesAction.setObjectName("renderInFilledNoEdgesAction")
        renderInFilledNoEdgesAction.setIcon(res.graphics["rendering-filled-no-edges"])
        renderInFilledNoEdgesAction.setToolTip("Rendering: No Edges")
        renderInFilledNoEdgesAction.setCheckable(True)
        renderInFilledNoEdgesAction.setChecked(False)
        renderInFilledNoEdgesAction.triggered.connect(self.onRenderInFilledNoEdgesActionTriggered)
        renderingToolBar.addAction(renderInFilledNoEdgesAction)

        # projection tool bar
        projectionToolBar: QToolBar = QToolBar(self)
        projectionToolBar.setObjectName("projectionToolBar")
        self.addToolBar(projectionToolBar)

        # project with perspective action
        projectWithPerspectiveAction: QAction = QAction(projectionToolBar)
        projectWithPerspectiveAction.setObjectName("projectWithPerspectiveAction")
        projectWithPerspectiveAction.setIcon(res.graphics["projection-perspective"])
        projectWithPerspectiveAction.setToolTip("Perspective On")
        projectWithPerspectiveAction.setCheckable(True)
        projectWithPerspectiveAction.setChecked(True)
        projectWithPerspectiveAction.triggered.connect(self.onProjectWithPerspectiveActionTriggered)
        projectionToolBar.addAction(projectWithPerspectiveAction)

        # project in parallel action
        projectInParallelAction: QAction = QAction(projectionToolBar)
        projectInParallelAction.setObjectName("projectInParallelAction")
        projectInParallelAction.setIcon(res.graphics["projection-parallel"])
        projectInParallelAction.setToolTip("Perspective Off")
        projectInParallelAction.setCheckable(True)
        projectInParallelAction.setChecked(False)
        projectInParallelAction.triggered.connect(self.onProjectInParallelActionTriggered)
        projectionToolBar.addAction(projectInParallelAction)

        # lighting tool bar
        lightingToolBar: QToolBar = QToolBar(self)
        lightingToolBar.setObjectName("lightingToolBar")
        self.addToolBar(lightingToolBar)

        # lighting on action
        lightingOnAction: QAction = QAction(lightingToolBar)
        lightingOnAction.setObjectName("lightingOnAction")
        lightingOnAction.setIcon(res.graphics["lighting-on"])
        lightingOnAction.setToolTip("Lighting On")
        lightingOnAction.setCheckable(True)
        lightingOnAction.setChecked(True)
        lightingOnAction.triggered.connect(self.onLightingOnActionTriggered)
        lightingToolBar.addAction(lightingOnAction)

        # lighting off action
        lightingOffAction: QAction = QAction(lightingToolBar)
        lightingOffAction.setObjectName("lightingOffAction")
        lightingOffAction.setIcon(res.graphics["lighting-off"])
        lightingOffAction.setToolTip("Lighting Off")
        lightingOffAction.setCheckable(True)
        lightingOffAction.setChecked(False)
        lightingOffAction.triggered.connect(self.onLightingOffActionTriggered)
        lightingToolBar.addAction(lightingOffAction)

        # frame navigation tool bar
        frameNavigationToolBar: QToolBar = QToolBar(self)
        frameNavigationToolBar.setObjectName("frameNavigationToolBar")
        self.addToolBar(frameNavigationToolBar)

        # go to first frame action
        goToFirstFrameAction: QAction = QAction(frameNavigationToolBar)
        goToFirstFrameAction.setObjectName("goToFirstFrameAction")
        goToFirstFrameAction.setIcon(res.graphics["go-to-first"])
        goToFirstFrameAction.setToolTip("First Frame")
        goToFirstFrameAction.triggered.connect(self.onGoToFirstFrameActionTriggered)
        frameNavigationToolBar.addAction(goToFirstFrameAction)

        # go to previous frame action
        goToPreviousFrameAction: QAction = QAction(frameNavigationToolBar)
        goToPreviousFrameAction.setObjectName("goToPreviousFrameAction")
        goToPreviousFrameAction.setIcon(res.graphics["go-to-previous"])
        goToPreviousFrameAction.setToolTip("Previous Frame")
        goToPreviousFrameAction.triggered.connect(self.onGoToPreviousFrameActionTriggered)
        frameNavigationToolBar.addAction(goToPreviousFrameAction)

        # go to next frame action
        goToNextFrameAction: QAction = QAction(frameNavigationToolBar)
        goToNextFrameAction.setObjectName("goToNextFrameAction")
        goToNextFrameAction.setIcon(res.graphics["go-to-next"])
        goToNextFrameAction.setToolTip("Next Frame")
        goToNextFrameAction.triggered.connect(self.onGoToNextFrameActionTriggered)
        frameNavigationToolBar.addAction(goToNextFrameAction)

        # go to last frame action
        goToLastFrameAction: QAction = QAction(frameNavigationToolBar)
        goToLastFrameAction.setObjectName("goToLastFrameAction")
        goToLastFrameAction.setIcon(res.graphics["go-to-last"])
        goToLastFrameAction.setToolTip("Last Frame")
        goToLastFrameAction.triggered.connect(self.onGoToLastFrameActionTriggered)
        frameNavigationToolBar.addAction(goToLastFrameAction)

        # tool bar break
        self.addToolBarBreak()

        # deformation tool bar
        deformationToolBar: QToolBar = QToolBar(self)
        deformationToolBar.setObjectName("deformationToolBar")
        self.addToolBar(deformationToolBar)

        # deformation label
        deformationLabel: QLabel = QLabel(deformationToolBar)
        deformationLabel.setObjectName("deformationLabel")
        deformationLabel.setText("Scale: ")
        deformationLabel.setToolTip("Deformation Scale Factor")
        deformationToolBar.addWidget(deformationLabel)

        # deformation box
        deformationBox: QLineEdit = QLineEdit(deformationToolBar)
        deformationBox.setObjectName("deformationBox")
        deformationBox.setToolTip("Deformation Scale Factor")
        deformationBox.setFixedWidth(80)
        deformationBox.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        deformationBox.setText("1.0")
        deformationBox.editingFinished.connect(self.onDeformationBoxEditingFinished)
        deformationToolBar.addWidget(deformationBox)

        # legend tool bar
        legendToolBar: QToolBar = QToolBar(self)
        legendToolBar.setObjectName("legendToolBar")
        self.addToolBar(legendToolBar)

        # spectrum label
        spectrumLabel: QLabel = QLabel(legendToolBar)
        spectrumLabel.setObjectName("spectrumLabel")
        spectrumLabel.setText("Spectrum: ")
        legendToolBar.addWidget(spectrumLabel)

        # spectrum box
        spectrumBox: QComboBox = QComboBox(legendToolBar)
        spectrumBox.setObjectName("spectrumBox")
        spectrumBox.addItems([spectrum.name for spectrum in Spectrums])
        spectrumBox.addItems(["Reversed " + spectrum.name for spectrum in Spectrums])
        spectrumBox.setCurrentText("Jet")
        spectrumBox.currentTextChanged.connect(self.onSpectrumUpdateRequested)
        legendToolBar.addWidget(spectrumBox)

        # intervals label
        intervalsLabel: QLabel = QLabel(legendToolBar)
        intervalsLabel.setObjectName("intervalsLabel")
        intervalsLabel.setText(" Intervals: ")
        legendToolBar.addWidget(intervalsLabel)

        # intervals box
        intervalsBox: QComboBox = QComboBox(legendToolBar)
        intervalsBox.setObjectName("intervalsBox")
        intervalsBox.addItems(["Continuous"] + [str(i) for i in range(2, 17)])
        intervalsBox.setCurrentText("12")
        intervalsBox.currentTextChanged.connect(self.onSpectrumUpdateRequested)
        legendToolBar.addWidget(intervalsBox)

        # central widget
        centralWidget: QWidget = QWidget(self)
        centralWidget.setObjectName("centralWidget")
        self.setCentralWidget(centralWidget)

        # central widget layout
        centralWidgetLayout: QGridLayout = QGridLayout(centralWidget)
        centralWidgetLayout.setObjectName("centralWidgetLayout")
        centralWidget.setLayout(centralWidgetLayout)

        # vertical splitter
        verticalSplitter: QSplitter = QSplitter(centralWidget)
        verticalSplitter.setObjectName("verticalSplitter")
        verticalSplitter.setOrientation(Qt.Orientation.Vertical)
        verticalSplitter.setHandleWidth(9)
        centralWidgetLayout.addWidget(verticalSplitter, 0, 0, 1, 1)

        # size policy 0
        sizePolicy0: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy0.setVerticalStretch(1)

        # horizontal splitter
        horizontalSplitter: QSplitter = QSplitter(verticalSplitter)
        horizontalSplitter.setObjectName("horizontalSplitter")
        horizontalSplitter.setOrientation(Qt.Orientation.Horizontal)
        horizontalSplitter.setHandleWidth(9)
        horizontalSplitter.setSizePolicy(sizePolicy0)
        verticalSplitter.addWidget(horizontalSplitter)

        # tree widget
        treeWidget: QTreeWidget = QTreeWidget(horizontalSplitter)
        treeWidget.setObjectName("treeWidget")
        treeWidget.setHeaderHidden(True)
        treeWidget.currentItemChanged.connect(self.onCurrentTreeWidgetItemChanged)
        horizontalSplitter.addWidget(treeWidget)

        # size policy 1
        sizePolicy1: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)

        # viewport
        viewport: Viewport = Viewport(horizontalSplitter)
        viewport.setObjectName("viewport")
        viewport.setBackgroundColor1(QColor.fromRgbF(0.0, 0.1, 0.2))
        viewport.setBackgroundColor2(QColor.fromRgbF(0.5, 0.6, 0.7))
        viewport.setSizePolicy(sizePolicy1)
        viewport.renderingModeChanged.connect(self.onViewportRenderingModeChanged)
        viewport.cameraProjectionModeChanged.connect(self.onViewportCameraProjectionModeChanged)
        viewport.lightingModeChanged.connect(self.onViewportLightingModeChanged)
        viewport.deformationScaleFactorChanged.connect(self.onViewportDeformationScaleFactorChanged)
        viewport.interactionTypeChanged.connect(self.onViewportInteractionTypeChanged)
        horizontalSplitter.addWidget(viewport)

        # cli
        cli: CLI = CLI(verticalSplitter, locals={"session": self})
        cli.setObjectName("cli")
        verticalSplitter.addWidget(cli)

        # extension dialogs
        self._animateDeformationDialog: AnimateDeformationDialog = AnimateDeformationDialog(self, viewport)
        self._animateTimeDialog: AnimateTimeDialog = AnimateTimeDialog(self, viewport, treeWidget)

        # initial state
        self.refresh()

    def treeWidget(self) -> QTreeWidget:
        """Returns the tree widget."""
        return cast(QTreeWidget, self.findChild(QTreeWidget, "treeWidget"))

    def viewport(self) -> Viewport:
        """Returns the viewport."""
        return cast(Viewport, self.findChild(Viewport, "viewport"))

    def cli(self) -> CLI:
        """Returns the command-line interface (CLI)."""
        return cast(CLI, self.findChild(CLI, "cli"))

    def show(self) -> None:
        """Shows the main window."""
        super().show()
        self.viewport().start()

    def openODB(self, filePath: str) -> None:
        """Opens the specified output database."""
        # check file extension
        if (ext := os.path.splitext(filePath)[1].lower()) != ".out":
            raise ValueError(f"unexpected file extension: '{ext}'")

        # close previous if necessary
        if self._odb or self._odbView:
            self.closeODB()

        # create ODB and ODBView objects
        self._odb = ODB(filePath, mode="read")
        self._odbView = ODBView(
            self._odb.fileName,
            self._odb,
            self.viewport().legend(),
            self.viewport().renderingMode(),
            self.viewport().deformationScaleFactor()
        )

        # refresh UI
        self.refresh()
        print(f"Output database opened: '{filePath}'")

    def closeODB(self) -> None:
        """Closes the current output database."""
        # get current ODB file path
        filePath: str | None = self._odb.filePath if self._odb else None

        # set ODB and ODBView objects to None
        self._odb = None
        self._odbView = None

        # refresh UI
        if filePath is not None:
            self.refresh()
            print(f"Output database closed: '{filePath}'")

    def refresh(self, *, treeWidget: bool = True, viewport: bool = True, windowTitle: bool = True) -> None:
        """Refreshes the UI."""
        # refresh tree widget
        if treeWidget:
            self.treeWidget().clear()
            if self._odb:
                odbItem: QTreeWidgetItem = QTreeWidgetItem(self.treeWidget().invisibleRootItem(), ("Output Database",))
                nodeOutputItem: QTreeWidgetItem = QTreeWidgetItem(odbItem, ("Node Output",))
                globalOutputItem: QTreeWidgetItem = QTreeWidgetItem(odbItem, ("Global Output",))
                nodeOutputTitles: Iterable[str] = self._odb.getNodeOutputTitles()
                globalOutputTitles: Iterable[str] = self._odb.getGlobalOutputTitles()
                for outputItem, titles in ((nodeOutputItem, nodeOutputTitles), (globalOutputItem, globalOutputTitles)):
                    for title in titles:
                        parent: QTreeWidgetItem = outputItem
                        for section in title.split(">"):
                            child: QTreeWidgetItem
                            for i in range(parent.childCount()):
                                if parent.child(i).text(0) == section:
                                    child = parent.child(i)
                                    break
                            else:
                                child = QTreeWidgetItem(parent, (section,))
                            parent = child
                for item in (odbItem, nodeOutputItem, globalOutputItem): item.setExpanded(True)
            else:
                QTreeWidgetItem(self.treeWidget().invisibleRootItem(), ("Output Database (Empty)",))

        # refresh viewport
        if viewport:
            self.viewport().clear()
            self.viewport().infoBlock().clear()
            self.viewport().legend().setVisible(False)
            if self._odb and self._odbView:
                self.viewport().draw(self._odbView)
                self.viewport().view(Views.Front if self._odbView.dimension == 2 else Views.Isometric)
                self.viewport().infoBlock().setText(1, self._odb.getDescription())
                self.viewport().infoBlock().setText(
                    2, f"Deformation Scale Factor: {self.viewport().deformationScaleFactor()}"
                )
            else:
                self.viewport().view(Views.Front)

        # refresh window title
        if windowTitle:
            title: str = "FEAPACK Viewer"
            if self._odb:
                title += f" - {self._odb.filePath}"
            self.setWindowTitle(title)

    def plotNodeOutput(self, title: str, draw: bool = True) -> None:
        """Plots the specified node output scalar field."""
        if not self._odbView: return
        self._odbView.plotNodeOutput(title)
        self.viewport().legend().setVisible(True)
        self.viewport().infoBlock().setText(0, title.replace(">", ": "))
        if draw: self.viewport().draw()

    def clearNodeOutput(self, draw: bool = True) -> None:
        """Clears the current node output scalar field."""
        if not self._odbView: return
        self._odbView.clearNodeOutput()
        self.viewport().legend().setVisible(False)
        self.viewport().infoBlock().setText(0, "")
        if draw: self.viewport().draw()

    def printGlobalOutput(self, title: str) -> None:
        """Prints the specified global output scalar."""
        if not self._odb: return
        name: str = title.split(">")[-1]
        frame: int = self._odb.currentFrame
        description: str = self._odb.getDescription()
        value: float = self._odb.getGlobalOutputValues(title)
        print(f"{name} at frame {frame} ({description}) is {value}")

    goToFirstFrame = lambda self: self.goToFrame("first")
    goToPreviousFrame = lambda self: self.goToFrame("previous")
    goToNextFrame = lambda self: self.goToFrame("next")
    goToLastFrame = lambda self: self.goToFrame("last")
    def goToFrame(self, move: Literal["first", "previous", "next", "last"]) -> None:
        """Output frame navigation moves."""
        if not self._odb or not self._odbView: return

        # get title of plotted node output (if any) and clear plot
        plotted: str = self.viewport().infoBlock().text(0).replace(": ", ">")
        self.clearNodeOutput(draw=False)

        # move reader pointers
        match move:
            case "first": self._odb.goToFirstFrame()
            case "previous": self._odb.goToPreviousFrame()
            case "next": self._odb.goToNextFrame()
            case "last": self._odb.goToLastFrame()

        # rebuild ODBView data set
        self._odbView.rebuild(self.viewport().deformationScaleFactor())

        # update info block
        self.viewport().infoBlock().setText(1, self._odb.getDescription())

        # refresh tree widget
        self.refresh(treeWidget=True, viewport=False, windowTitle=False)

        # replot if node output available in the current frame
        if plotted and plotted in self._odb.getNodeOutputTitles():
            self.plotNodeOutput(plotted, draw=True)

            # reselect tree widget item
            item: QTreeWidgetItem = self.treeWidget().invisibleRootItem()
            branch: list[str] = ["Output Database", "Node Output"] + plotted.split(">")
            for i in range(len(branch)):
                for j in range(item.childCount()):
                    if item.child(j).text(0) == branch[i]:
                        item = item.child(j)
                        break
            self.treeWidget().currentItemChanged.disconnect(self.onCurrentTreeWidgetItemChanged)
            self.treeWidget().setCurrentItem(item)
            self.treeWidget().currentItemChanged.connect(self.onCurrentTreeWidgetItemChanged)
        else:
            self.viewport().draw()

    def updateDeformationScaleFactor(self, value: float) -> None:
        """Updates the deformation scale factor."""
        # update deformation scale factor
        self.viewport().setDeformationScaleFactor(value, draw=False)

        # replot if necessary
        if plotted := self.viewport().infoBlock().text(0).replace(": ", ">"): self.plotNodeOutput(plotted, draw=True)
        else: self.viewport().draw()

    def onCurrentTreeWidgetItemChanged(self) -> None:
        """On current tree widget item changed."""
        # get selected branch
        branch: list[QTreeWidgetItem] = [item] if (item := self.treeWidget().currentItem()) else []
        if len(branch) > 0:
            while parent := branch[-1].parent():
                branch.append(parent)
            branch.reverse()
        depth: int = len(branch)

        # handle selection
        if depth > 2 and branch[-1].childCount() == 0:
            title: str = ">".join(item.text(0) for item in branch[2:])
            match outputType := branch[1].text(0):
                case "Node Output":
                    self.cli().push(f"session.plotNodeOutput('{title}')")
                case "Global Output":
                    if self.viewport().legend().isVisible(): self.cli().push("session.clearNodeOutput()")
                    self.cli().push(f"session.printGlobalOutput('{title}')")
                case _:
                    raise NotImplementedError(f"cannot handle '{outputType}'")
            return

        # clear any previous plots
        if self._odbView and self.viewport().legend().isVisible():
            self.cli().push("session.clearNodeOutput()")

    def onViewportRenderingModeChanged(self, mode: RenderingModes) -> None:
        """On viewport rendering mode changed."""
        renderInWireframeAction: QAction = cast(QAction, self.findChild(QAction, "renderInWireframeAction"))
        renderInFilledAction: QAction = cast(QAction, self.findChild(QAction, "renderInFilledAction"))
        renderInFilledNoEdgesAction: QAction = cast(QAction, self.findChild(QAction, "renderInFilledNoEdgesAction"))
        renderInWireframeAction.setChecked(mode == RenderingModes.Wireframe)
        renderInFilledAction.setChecked(mode == RenderingModes.Filled)
        renderInFilledNoEdgesAction.setChecked(mode == RenderingModes.FilledNoEdges)

    def onViewportCameraProjectionModeChanged(self, parallel: bool) -> None:
        """On viewport camera projection mode changed."""
        projectWithPerspectiveAction: QAction = cast(QAction, self.findChild(QAction, "projectWithPerspectiveAction"))
        projectInParallelAction: QAction = cast(QAction, self.findChild(QAction, "projectInParallelAction"))
        projectWithPerspectiveAction.setChecked(not parallel)
        projectInParallelAction.setChecked(parallel)

    def onViewportLightingModeChanged(self, lighting: bool) -> None:
        """On viewport lighting mode changed."""
        lightingOnAction: QAction = cast(QAction, self.findChild(QAction, "lightingOnAction"))
        lightingOffAction: QAction = cast(QAction, self.findChild(QAction, "lightingOffAction"))
        lightingOnAction.setChecked(lighting)
        lightingOffAction.setChecked(not lighting)

    def onViewportDeformationScaleFactorChanged(self, value: float) -> None:
        """On viewport deformation scale factor changed."""
        if self._odbView: self.viewport().infoBlock().setText(2, f"Deformation Scale Factor: {value}")
        deformationBox: QLineEdit = cast(QLineEdit, self.findChild(QLineEdit, "deformationBox"))
        deformationBox.setText(str(value))

    def onViewportInteractionTypeChanged(self, interactionType: InteractionTypes) -> None:
        """On viewport interaction type changed."""
        rotateAction: QAction = cast(QAction, self.findChild(QAction, "rotateAction"))
        panAction: QAction = cast(QAction, self.findChild(QAction, "panAction"))
        zoomAction: QAction = cast(QAction, self.findChild(QAction, "zoomAction"))
        rotateAction.setChecked(interactionType == InteractionTypes.Rotate)
        panAction.setChecked(interactionType == InteractionTypes.Pan)
        zoomAction.setChecked(interactionType == InteractionTypes.Zoom)

    def onSpectrumUpdateRequested(self) -> None:
        """On spectrum update requested."""
        spectrumBox: QComboBox = cast(QComboBox, self.findChild(QComboBox, "spectrumBox"))
        intervalsBox: QComboBox = cast(QComboBox, self.findChild(QComboBox, "intervalsBox"))
        spectrum: Spectrums = Spectrums[spectrumBox.currentText().removeprefix("Reversed ")]
        reversed: bool = spectrumBox.currentText().startswith("Reversed ")
        continuous: bool = intervalsBox.currentText() == "Continuous"
        intervals: int = int(intervalsBox.currentText()) if not continuous else 0
        command: str = f"session.viewport().legend().rebuild({spectrum}, {intervals}, {continuous}, {reversed}); " + \
            "session.viewport().draw()"
        self.cli().push(command)

    def onFileOpenActionTriggered(self) -> None:
        """On File > Open..."""
        if filePath := QFileDialog.getOpenFileName(
            parent=self,
            caption="Open Output Database",
            filter="Output Database Files (*.out)",
            options=QFileDialog.Option.DontUseNativeDialog
        )[0]: self.cli().push(f"session.openODB('{filePath}')")

    def onFileCloseActionTriggered(self) -> None:
        """On File > Close."""
        self.cli().push("session.closeODB()")

    def onFilePrintActionTriggered(self) -> None:
        """On File > Print..."""
        if filePath := QFileDialog.getSaveFileName(
            parent=self,
            caption="Print Viewport",
            filter="PNG Image Files (*.png)",
            options=QFileDialog.Option.DontUseNativeDialog
        )[0]:
            filePath = os.path.splitext(filePath)[0] + ".png"
            self.cli().push(f"session.viewport().print('{filePath}')")

    def onGoToFirstFrameActionTriggered(self) -> None:
        """On go to first frame."""
        self.cli().push("session.goToFirstFrame()")

    def onGoToPreviousFrameActionTriggered(self) -> None:
        """On go to previous frame."""
        self.cli().push("session.goToPreviousFrame()")

    def onGoToNextFrameActionTriggered(self) -> None:
        """On go to next frame."""
        self.cli().push("session.goToNextFrame()")

    def onGoToLastFrameActionTriggered(self) -> None:
        """On go to last frame."""
        self.cli().push("session.goToLastFrame()")

    def onViewFrontActionTriggered(self) -> None:
        """On view front."""
        self.cli().push("session.viewport().view(Views.Front)")

    def onViewBackActionTriggered(self) -> None:
        """On view back."""
        self.cli().push("session.viewport().view(Views.Back)")

    def onViewTopActionTriggered(self) -> None:
        """On view top."""
        self.cli().push("session.viewport().view(Views.Top)")

    def onViewBottomActionTriggered(self) -> None:
        """On view bottom."""
        self.cli().push("session.viewport().view(Views.Bottom)")

    def onViewLeftActionTriggered(self) -> None:
        """On view left."""
        self.cli().push("session.viewport().view(Views.Left)")

    def onViewRightActionTriggered(self) -> None:
        """On view right."""
        self.cli().push("session.viewport().view(Views.Right)")

    def onViewIsometricActionTriggered(self) -> None:
        """On view isometric."""
        self.cli().push("session.viewport().view(Views.Isometric)")

    def onViewAutoFitActionTriggered(self) -> None:
        """On view auto-fit."""
        self.cli().push("session.viewport().autoFitView()")

    def onRotateActionTriggered(self) -> None:
        """On rotate."""
        self.cli().push("session.viewport().setInteractionType(InteractionTypes.Rotate)")

    def onPanActionTriggered(self) -> None:
        """On pan."""
        self.cli().push("session.viewport().setInteractionType(InteractionTypes.Pan)")

    def onZoomActionTriggered(self) -> None:
        """On zoom."""
        self.cli().push("session.viewport().setInteractionType(InteractionTypes.Zoom)")

    def onRenderInWireframeActionTriggered(self) -> None:
        """On render in wireframe."""
        self.cli().push("session.viewport().setRenderingMode(RenderingModes.Wireframe)")

    def onRenderInFilledActionTriggered(self) -> None:
        """On render in filled."""
        self.cli().push("session.viewport().setRenderingMode(RenderingModes.Filled)")

    def onRenderInFilledNoEdgesActionTriggered(self) -> None:
        """On render in filled (no edges)."""
        self.cli().push("session.viewport().setRenderingMode(RenderingModes.FilledNoEdges)")

    def onProjectWithPerspectiveActionTriggered(self) -> None:
        """On project with perspective."""
        self.cli().push("session.viewport().setCameraUsingParallelProjection(False)")

    def onProjectInParallelActionTriggered(self) -> None:
        """On project in parallel."""
        self.cli().push("session.viewport().setCameraUsingParallelProjection(True)")

    def onLightingOnActionTriggered(self) -> None:
        """On lighting on."""
        self.cli().push("session.viewport().setLightingActive(True)")

    def onLightingOffActionTriggered(self) -> None:
        """On lighting off."""
        self.cli().push("session.viewport().setLightingActive(False)")

    def onDeformationBoxEditingFinished(self) -> None:
        """On deformation box editing finished."""
        deformationBox: QLineEdit = cast(QLineEdit, self.findChild(QLineEdit, "deformationBox"))
        try:
            dsf: float = float(deformationBox.text())
            if dsf != self.viewport().deformationScaleFactor():
                self.cli().push(f"session.updateDeformationScaleFactor({dsf})")
        except ValueError:
            pass
        finally:
            deformationBox.setText(str(self.viewport().deformationScaleFactor()))

    def onAnimateDeformationActionTriggered(self) -> None:
        """On Animate > Deformation..."""
        self._animateDeformationDialog.show()
        self._animateDeformationDialog.activateWindow()

    def onAnimateTimeActionTriggered(self) -> None:
        """On Animate > Time..."""
        self._animateTimeDialog.show()
        self._animateTimeDialog.activateWindow()

    def onHelpAboutActionTriggered(self) -> None:
        """On Help > About."""
        AboutDialog(self).exec()
