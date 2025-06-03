# ---------------------------------------------
# MESSAGE BOX WIDGET
# ---------------------------------------------
from typing import Optional
from PyQt6.QtWidgets import QDockWidget, QTextEdit, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from src.utils.output_stream import OutputStream

class MessageBox(QDockWidget):
    """Dock widget for displaying redirected stdout messages."""

    def __init__(self, parent: Optional[QWidget]) -> None:
        """
        Initialize the message box dock.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__("Console", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the message box UI."""
        try:
            self.text_edit = QTextEdit(self)
            self.text_edit.setReadOnly(True)
            dock_widget = QWidget()
            layout = QVBoxLayout(dock_widget)
            layout.addWidget(self.text_edit)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setWidget(dock_widget)
        except Exception as e:
            print(f"Error setting up message box: {e}")

    def write(self, text: str) -> None:
        """
        Write text to the QTextEdit widget.

        Args:
            text (str): The text to append.
        """
        try:
            self.text_edit.append(text.strip())
        except Exception as e:
            print(f"Error writing to message box: {e}")

    def flush(self) -> None:
        """No-op flush method for stdout compatibility."""
        pass