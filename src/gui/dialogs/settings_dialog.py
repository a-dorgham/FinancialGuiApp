# ---------------------------------------------
# SETTINGS DIALOG
# ---------------------------------------------
from typing import Optional
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the settings dialog.

        Args:
            parent (Optional[QWidget]): The parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the settings dialog UI."""
        try:
            layout = QVBoxLayout(self)
            self.data_path_edit = QLineEdit("src/data/GBP_USD_M15.pkl")
            layout.addWidget(QLabel("Data File Path:"))
            layout.addWidget(self.data_path_edit)
            save_button = QPushButton("Save")
            save_button.clicked.connect(self.accept)
            layout.addWidget(save_button)
        except Exception as e:
            print(f"Error setting up settings dialog: {e}")

    def get_settings(self) -> dict:
        """
        Get the current settings.

        Returns:
            dict: The settings dictionary.
        """
        try:
            return {"data_path": self.data_path_edit.text()}
        except Exception as e:
            print(f"Error getting settings: {e}")
            return {}