# ---------------------------------------------
# CONTROL PANEL WIDGET
# ---------------------------------------------
import os
import pandas as pd
from typing import Optional
from PyQt6.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, 
                             QCheckBox, QLabel, QFrame, 
                             QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from src.core.controllers import TradeController
from src.gui.widgets.plot_view import PlotView
from src.data.config_manager import ConfigManager


class ControlPanel(QDockWidget):
    """Dock widget for controlling plot and trade settings."""

    def __init__(self, parent: Optional[QWidget], trade_controller: TradeController, plot_view: PlotView) -> None:
        """
        Initialize the control panel with input fields and buttons.

        Args:
            parent (Optional[QWidget]): The parent widget.
            trade_controller (TradeController): Controller for trade operations.
            plot_view (PlotView): The plot view widget for updating plots.
        """
        super().__init__("Control Panel", parent)
        self.trade_controller = trade_controller
        self.config_manager = ConfigManager()
        self.plot_view = plot_view
        self.setFloating(False)
        self.auto_incrementing = False
        self.timer = QTimer(self)  
        self.timer.timeout.connect(self._auto_increment_step)
        self._setup_ui()
        self._increment_plot()
        #self._import_data(file_path= 'local')

    # ---------------------------------------------
    # UI SETUP
    # ---------------------------------------------
    def _setup_ui(self) -> None:
        """Set up the control panel's UI components."""
        try:
            dock_widget = QWidget()
            dock_layout = QVBoxLayout(dock_widget)

            # Import Data Button
            self.import_data_button = QPushButton("Import Data")
            self.import_data_button.clicked.connect(self._import_data)
            dock_layout.addWidget(self.import_data_button)
            self.import_data_button.setMinimumHeight(70)
            self.import_data_button.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Preferred
            )
            
            self.file_path = self.config_manager.get_data_path()
            self.file_path_edit = QLabel(self.file_path)
            dock_layout.addWidget(self.file_path_edit)
            self.file_path_edit.setEnabled(False)

            dock_layout.addWidget(self._create_horizontal_line())
            dock_layout.addWidget(self._create_horizontal_line())
            dock_layout.addStretch()
                        
            self.start_date_edit = self._create_label_edit(dock_layout, "Start Date:", "2024-11-12 07:30")
            self.end_date_edit = self._create_label_edit(dock_layout, "End Date:", "2024-11-26 06:30")
            self.current_date_edit = self._create_label_edit(dock_layout, "Current Date:", "2024-11-20 06:45")
            
            dock_layout.addWidget(self._create_horizontal_line())
            dock_layout.addWidget(self._create_horizontal_line())
            dock_layout.addStretch()
            
            self.increment_edit = self._create_label_edit(dock_layout, "Increment (mins):", "15")
            self.increment_plot_button = QPushButton("Increment/Plot")
            self.increment_plot_button.clicked.connect(self._handle_increment_plot)
            dock_layout.addWidget(self.increment_plot_button)

            self.increment_checkbox = QCheckBox("Apply increment to x-limits")
            dock_layout.addWidget(self.increment_checkbox)
            
            self.auto_increment_checkbox = QCheckBox("Auto Increment")
            self.auto_increment_checkbox.stateChanged.connect(self._update_auto_increment_state)
            dock_layout.addWidget(self.auto_increment_checkbox)

            dock_layout.addWidget(self._create_horizontal_line())
            dock_layout.addWidget(self._create_horizontal_line())
            dock_layout.addStretch()

            self.get_limits_button = QPushButton("Get limits from figure")
            self.get_limits_button.clicked.connect(self.plot_view.set_limits_from_figure)
            dock_layout.addWidget(self.get_limits_button)

            xlim_layout = QHBoxLayout()
            xlim_layout.addWidget(QLabel("X Min:"))
            self.xlim_min_edit = QLineEdit("2024-11-18 07:15")
            xlim_layout.addWidget(self.xlim_min_edit)
            xlim_layout.addWidget(QLabel("X Max:"))
            self.xlim_max_edit = QLineEdit("2024-11-26 06:30")
            xlim_layout.addWidget(self.xlim_max_edit)
            dock_layout.addLayout(xlim_layout)

            ylim_layout = QHBoxLayout()
            ylim_layout.addWidget(QLabel("Y Min:"))
            self.ylim_min_edit = QLineEdit("1.23")
            ylim_layout.addWidget(self.ylim_min_edit)
            ylim_layout.addWidget(QLabel("Y Max:"))
            self.ylim_max_edit = QLineEdit("1.275")
            ylim_layout.addWidget(self.ylim_max_edit)
            dock_layout.addLayout(ylim_layout)

            set_limits_button = QPushButton("Apply Limits")
            set_limits_button.clicked.connect(self.plot_view.set_limits)
            dock_layout.addWidget(set_limits_button)

            dock_layout.addWidget(self._create_horizontal_line())
            dock_layout.addWidget(self._create_horizontal_line())
            dock_layout.addStretch()

            self.auto_trade_checkbox = QCheckBox("Auto trade")
            self.auto_trade_checkbox.setChecked(True)
            self.auto_trade_checkbox.stateChanged.connect(self._increment_plot)
            dock_layout.addWidget(self.auto_trade_checkbox)

            button_layout = QHBoxLayout()
            self.buy_button = QPushButton("Buy")
            self.sell_button = QPushButton("Sell")
            self.close_trade_button = QPushButton("Close Trade")
            button_layout.addWidget(self.buy_button)
            button_layout.addWidget(self.sell_button)
            button_layout.addWidget(self.close_trade_button)
            self.buy_button.clicked.connect(self.trade_controller.buy_trade)
            self.sell_button.clicked.connect(self.trade_controller.sell_trade)
            self.close_trade_button.clicked.connect(self.trade_controller.close_trade)
            dock_layout.addLayout(button_layout)

            self.export_button = QPushButton("Export to Excel")
            self.export_button.clicked.connect(self.trade_controller.export_to_excel)
            dock_layout.addWidget(self.export_button)

            self.setWidget(dock_widget)
        except Exception as e:
            print(f"Error setting up control panel: {e}")

    def _create_label_edit(self, layout: QVBoxLayout, label_text: str, default_value: str) -> QLineEdit:
        """
        Create a label and QLineEdit pair.

        Args:
            layout (QVBoxLayout): The layout to add the widgets to.
            label_text (str): The text for the label.
            default_value (str): The default value for the QLineEdit.

        Returns:
            QLineEdit: The created QLineEdit widget.
        """
        try:
            label = QLabel(label_text)
            edit = QLineEdit(default_value)
            layout.addWidget(label)
            layout.addWidget(edit)
            return edit
        except Exception as e:
            print(f"Error creating label/edit for '{label_text}': {e}")
            return QLineEdit(default_value)

    def _create_horizontal_line(self) -> QFrame:
        """
        Create a horizontal line separator.

        Returns:
            QFrame: The horizontal line widget.
        """
        try:
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            return line
        except Exception as e:
            print(f"Error creating horizontal line: {e}")
            return QFrame()

    # ---------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------
    def _increment_plot(self) -> None:
        """Handle the increment/plot action."""
        try:
            self.plot_view.increment_plot(
                start_date=self.start_date_edit.text(),
                end_date=self.end_date_edit.text(),
                current_date=self.current_date_edit.text(),
                increment=self.increment_edit.text(),
                x_limits=(self.xlim_min_edit.text(), self.xlim_max_edit.text()),
                y_limits=(self.ylim_min_edit.text(), self.ylim_max_edit.text()),
                auto_trade=self.auto_trade_checkbox.isChecked(),
                increment_x_limits=self.increment_checkbox.isChecked()
            )
            self.trade_controller.set_current_date(self.current_date_edit.text())
        except Exception as e:
            print(f"Error incrementing plot: {e}")
            

    def _handle_increment_plot(self) -> None:
        """Handle the Increment/Plot button click, toggling auto-increment if enabled."""
        try:
            if self.auto_increment_checkbox.isChecked() and not self.auto_incrementing:
                # Start auto-increment
                self.auto_incrementing = True
                self.increment_plot_button.setText("Stop Auto-Increment")
                self._auto_increment_step()  
            elif self.auto_incrementing:
                # Stop auto-increment
                self._stop_auto_increment()
            else:
                # Single increment
                self._increment_plot()
        except Exception as e:
            print(f"Error handling increment plot: {e}")

    def _auto_increment_step(self) -> None:
        """Perform one step of auto-increment and schedule the next if needed."""
        try:
            if not self.auto_incrementing:
                return

            end_reached = self._increment_plot()
            if end_reached:
                QMessageBox.information(self, "Info", "Reached end of data.")
                self._stop_auto_increment()
                return

            # Schedule next increment
            self.timer.start(100)
        except Exception as e:
            print(f"Error in auto-increment step: {e}")
            self._stop_auto_increment()

    def _stop_auto_increment(self) -> None:
        """Stop the auto-increment process."""
        self.auto_incrementing = False
        self.timer.stop()
        self.increment_plot_button.setText("Increment/Plot")
        self.auto_increment_checkbox.setChecked(False)

    def _update_auto_increment_state(self, state: int) -> None:
        """Handle changes to the auto-increment checkbox state."""
        if state == Qt.CheckState.Unchecked.value and self.auto_incrementing:
            self._stop_auto_increment()
        elif state == Qt.CheckState.Checked.value and not self.auto_incrementing:
            # Start auto-increment if button is already in "Stop" mode
            if self.increment_plot_button.text() == "Stop Auto-Increment":
                self.auto_incrementing = True
                self._auto_increment_step()
                    
    def _import_data(self, file_path:str=None) -> None:
        """Handle the import data action."""
        try:
            if not file_path:
                # Open file dialog
                initial_dir = os.path.join("src", "data")
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select Data File",
                    initial_dir,
                    "Data Files (*.pkl)"
                )
                if not file_path:
                    return  
            else:
                file_path = self.config_manager.get_data_path()

            # Read the file
            df = None
            file_ext = os.path.splitext(file_path)[1].lower()
            try:
                if file_ext in (".csv", ".txt", ".dat"):
                    delimiter = "," if file_ext == ".csv" else "\t"
                    df = pd.read_csv(file_path, delimiter=delimiter)
                elif file_ext in [".xls", ".xlsx"]:
                    df = pd.read_excel(file_path)
                elif file_ext == ".pkl":
                    df = pd.read_pickle(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read file: {e}")
                return

            if df is None or df.empty:
                QMessageBox.critical(self, "Error", "File is empty or invalid.")
                return

            # Check required columns
            required_columns = ["time", "volume", 
                                "mid_o", "mid_h", "mid_l", "mid_c", 
                                "bid_o", "bid_h", "bid_l", "bid_c", 
                                "ask_o", "ask_h", "ask_l", "ask_c"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                QMessageBox.critical(
                    self,
                    "Missing Columns",
                    f"The following required columns are missing: {', '.join(missing_columns)}"
                )
                return

            # Update config.json
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            relative_path = os.path.relpath(file_path, project_root).replace(os.sep, "/")
            self.config_manager.save_config(relative_path)

            # Plot the data
            self.plot_view.load_and_plot_data(file_path, self.start_date_edit.text(), self.end_date_edit.text())
            self.file_path_edit.setText(str(relative_path))
            QMessageBox.information(self, "Success", "Data imported and plotted successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error importing data: {e}")    
            