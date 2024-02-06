from code import InteractiveConsole
from collections.abc import Mapping
from typing import Protocol, TextIO, Any, cast
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import Qt, QColor, QFont, QKeyEvent, QTextCursor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit

class _WriteProtocol(Protocol):
    """A protocol for objects that implement a write method."""

    def write(self, text: str = "", color: QColor | None = None) -> None:
        """Called on write."""
        ...

class _OutputRedirect(TextIO):
    """
    Class used for redirecting standard output streams.
    Output streams are line-buffered.
    """

    __slots__ = ("_fileno", "_buffer", "_writer", "_color")

    def __init__(self, fileno: int, writer: _WriteProtocol, color: QColor | None = None) -> None:
        """Output redirect constructor."""
        super().__init__()
        self._fileno: int = fileno
        self._buffer: list[str] = []
        self._writer: _WriteProtocol = writer
        self._color: QColor | None = color

    def flush(self) -> None:
        """Flushes the line buffer."""
        text: str = "".join(self._buffer).rstrip()
        self._writer.write(text, self._color)
        self._buffer.clear()

    def write(self, text: str) -> int:
        """On write."""
        for char in text:
            if char == "\n": self.flush()
            else: self._buffer.append(char)
        return len(text)

    def fileno(self) -> int:
        """Returns the integer file descriptor."""
        return self._fileno

class _InputRedirect(TextIO):
    """
    Class used for redirecting standard input streams.
    Input streams are currently not allowed.
    """

    __slots__ = ("_fileno",)

    def __init__(self, fileno: int) -> None:
        """Input redirect constructor."""
        super().__init__()
        self._fileno: int = fileno

    def readline(self, limit: int = -1) -> str:
        """On read line."""
        raise RuntimeError("standard input is not allowed")

    def fileno(self) -> int:
        """Returns the integer file descriptor."""
        return self._fileno

class CLI(QWidget):
    """A command-line interface (CLI) for Python-based interaction."""

    __slots__ = ("_stdin", "_stdout", "_stderr", "_console", "_history", "_historyIndex", "_inputRequired")

    def __init__(self, parent: QWidget | None = None, locals: Mapping[str, Any] | None = None) -> None:
        """CLI widget constructor."""
        super().__init__(parent)

        # stream redirection
        self._stdin: TextIO = _InputRedirect(0)
        self._stdout: TextIO = _OutputRedirect(1, self)
        self._stderr: TextIO = _OutputRedirect(2, self, QColor(255, 0, 0))

        # interactive console and history
        self._console: InteractiveConsole = InteractiveConsole(locals)
        self._history: list[str] = [""]
        self._historyIndex: int = 0
        self._inputRequired: bool = False

        # font
        font: QFont = QFont("Courier", 10)

        # layout
        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setObjectName("layout")
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # output box
        outputBox: QTextEdit = QTextEdit(self)
        outputBox.setObjectName("outputBox")
        outputBox.setCursor(Qt.CursorShape.IBeamCursor)
        outputBox.setFont(font)
        outputBox.setReadOnly(True)
        layout.addWidget(outputBox)

        # input box
        inputBox: QLineEdit = QLineEdit(self)
        inputBox.setObjectName("inputBox")
        inputBox.setCursor(Qt.CursorShape.IBeamCursor)
        inputBox.setFont(font)
        inputBox.installEventFilter(self)
        layout.addWidget(inputBox)

    def stdin(self) -> TextIO:
        """Returns the stdin stream redirect."""
        return self._stdin

    def stdout(self) -> TextIO:
        """Returns the stdout stream redirect."""
        return self._stdout

    def stderr(self) -> TextIO:
        """Returns the stderr stream redirect."""
        return self._stderr

    def outputBox(self) -> QTextEdit:
        """The CLI output box."""
        return cast(QTextEdit, self.findChild(QTextEdit, "outputBox"))

    def inputBox(self) -> QLineEdit:
        """The CLI input box."""
        return cast(QLineEdit, self.findChild(QLineEdit, "inputBox"))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """The event filter."""
        if watched.objectName() == "inputBox" and event.type() == QEvent.Type.KeyPress:
            inputBox: QLineEdit = cast(QLineEdit, watched)
            keyEvent: QKeyEvent = cast(QKeyEvent, event)
            match keyEvent.key():
                case Qt.Key.Key_Return:
                    self.push(inputBox.text())
                    inputBox.clear()
                case Qt.Key.Key_Up:
                    inputBox.setText(self.inputHistory(moveUp=True))
                case Qt.Key.Key_Down:
                    inputBox.setText(self.inputHistory(moveUp=False))
                case _:
                    pass
        return super().eventFilter(watched, event)

    def inputHistory(self, moveUp: bool = True) -> str:
        """Navigate the user input history."""
        # update history index
        if moveUp: self._historyIndex -= 1
        else: self._historyIndex += 1

        # fix out-of-bounds index
        self._historyIndex = max(self._historyIndex, 0)
        self._historyIndex = min(self._historyIndex, len(self._history) - 1)

        # return the next or previous user input in the history
        return self._history[self._historyIndex]

    def write(self, text: str = "", color: QColor | None = None) -> None:
        """Writes the specified text to the output box."""
        # deselect any text
        textCursor: QTextCursor = self.outputBox().textCursor()
        textCursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
        self.outputBox().setTextCursor(textCursor)

        # write with color
        self.outputBox().setTextColor(color or self.outputBox().palette().text().color())
        if text: self.outputBox().append(text)
        self.outputBox().ensureCursorVisible()

    def push(self, line: str) -> None:
        """
        Pushes the specified line of source text to the interpreter.
        The line is written to the output box and added to the user input history.
        """
        # update history
        if line != "":
            if line in self._history: self._history.remove(line)
            self._history[-1] = line
            self._history.append("")
        self._historyIndex = len(self._history) - 1

        # write and interpret
        self.write((">>> " if not self._inputRequired else "... ") + line)
        self._inputRequired = self._console.push(line)
