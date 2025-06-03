from PyQt6.QtGui import QTextCursor
import sys
from typing import Any

# ---------------------------------------------
# UTILITY CLASSES
# ---------------------------------------------

class OutputStream:
    """
    A custom output stream class that redirects standard output to a QTextEdit widget.
    This class is useful for displaying print statements and other console output directly
    within a PyQt application's GUI, allowing for custom formatting and easy viewing
    of application logs or messages.
    """

    def __init__(self, text_edit_widget: Any) -> None:
        """
        Initializes the OutputStream with a QTextEdit widget.
        Args:
            text_edit_widget (Any): The QTextEdit widget where the output will be displayed.
                                   It's typed as Any because QTextEdit is a PyQt widget
                                   and its specific type might not be directly available
                                   without importing the entire QtWidgets module,
                                   which is already done.
        """
        self.text_edit_widget: Any = text_edit_widget

    def write(self, text: str) -> None:
        """
        Writes the given text to the associated QTextEdit widget.
        The text is formatted with a specific font, size, weight, and color, and
        'white-space: pre;' is applied to preserve formatting (e.g., newlines, spaces).
        Args:
            text (str): The text string to be written to the QTextEdit widget.
        """

        if self.text_edit_widget is None or not text.strip():
            return

        try:
            cursor: QTextCursor = self.text_edit_widget.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            html: str = (
                f"<span style='"
                f"font-family: Consolas, Monaco, monospace;"
                f"font-size: 11pt;"
                f"font-weight: 400;"
                f"color: #83a78c;"
                f"white-space: pre;"
                f"'>{text}</span><br>"
            )
            cursor.insertHtml(html)
            self.text_edit_widget.ensureCursorVisible()

        except Exception as e:
            sys.__stdout__.write(f"Exception occurred in OutputStream: {e}\n")

    def flush(self) -> None:
        """
        This method is required for file-like objects but does nothing in this implementation.
        It's included to satisfy the interface for `sys.stdout` redirection.
        """
        pass
