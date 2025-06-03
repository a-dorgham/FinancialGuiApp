# ---------------------------------------------
# MAIN WINDOW
# ---------------------------------------------
from typing import Optional
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QToolBar, QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
from src.gui.widgets.control_panel import ControlPanel
from src.gui.widgets.message_box import MessageBox
from src.gui.widgets.plot_view import PlotView
from src.core.controllers import TradeController
from src.core.services import HTTPServerService
from typing import Tuple, Optional, Dict, Any



class MainWindow(QMainWindow):
    """Main application window for the financial strategy testing GUI."""

    def __init__(self, server_service: HTTPServerService) -> None:
        """
        Initialize the main window with UI components and controllers.

        Args:
            server_service (HTTPServerService): The HTTP server service for Plotly JS.
        """
        super().__init__()
        self.server_service = server_service
        self.trade_controller = TradeController()
        self.setWindowTitle("Strategy Visualizer")
        self.resize(1200, 800)

        self._setup_ui()
        self._redirect_stdout()

    # ---------------------------------------------
    # UI SETUP
    # ---------------------------------------------
    def _setup_ui(self) -> None:
        """Set up the main window's UI components."""
        try:
            #self._create_menu_bar()
            #self._create_toolbar()
            self._create_central_widget()
            self._create_docks()
        except Exception as e:
            print(f"Error setting up UI: {e}")

    def _create_menu_bar(self) -> None:
        """Create and configure the menu bar."""
        try:
            menu_bar = self.menuBar()
            menu_bar.addMenu("&File")
            menu_bar.addMenu("&Edit")
            menu_bar.addMenu(QIcon("src/assets/images/plus_icon.png"), "&Help")
            self.setMenuBar(menu_bar)
        except Exception as e:
            print(f"Error creating menu bar: {e}")

    def _create_toolbar(self) -> None:
        """Create and configure the toolbar."""
        try:
            toolbar = QToolBar("Main Toolbar", self)
            actions = [
                ("src/assets/images/new_icon.png", "New", "Create a new file", 32),
                ("src/assets/images/open_icon.png", "Open", "Open an existing file", 32),
                ("src/assets/images/save_icon.png", "Save", "Save the current file", 27),
                ("src/assets/images/export_icon.png", "Export", "Export the current file", 29),
                ("src/assets/images/exit_icon.png", "Exit", "Close the current file", 32)
            ]
            for icon_path, text, tooltip, icon_size in actions:
                action = QAction(QIcon(icon_path), text, self)
                action.setToolTip(tooltip)
                toolbar.addAction(action)
            toolbar.addWidget(QWidget().setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred))
            self.addToolBar(toolbar)
        except Exception as e:
            print(f"Error creating toolbar: {e}")

    def _create_central_widget(self) -> None:
        """Create the central widget with the plot view."""
        try:
            self.central_widget = QWidget()
            layout = QVBoxLayout(self.central_widget)
            # Initialize PlotView without control_panel (set later)
            self.plot_view = PlotView(self, self.trade_controller)
            layout.addWidget(self.plot_view)
            self.setCentralWidget(self.central_widget)
        except Exception as e:
            print(f"Error creating central widget: {e}")

    def _create_docks(self) -> None:
        """Create the right and bottom docks."""
        try:
            self.control_panel = ControlPanel(self, self.trade_controller, self.plot_view)
            # Set control_panel in PlotView after creation
            self.plot_view.control_panel = self.control_panel
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.control_panel)

            self.message_box = MessageBox(self)
            self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.message_box)
            self.resizeDocks([self.message_box], [100], Qt.Orientation.Vertical)
        except Exception as e:
            print(f"Error creating docks: {e}")

    def _redirect_stdout(self) -> None:
        """Redirect stdout to the message box."""
        try:
            import sys
            sys.stdout = self.message_box
        except Exception as e:
            print(f"Error redirecting stdout: {e}")

    # ---------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------
    def closeEvent(self, event: Any) -> None:
        """
        Handle the window close event, stopping the HTTP server.

        Args:
            event (Any): The close event.
        """
        try:
            self.server_service.stop()
            event.accept()
        except Exception as e:
            print(f"Error closing application: {e}")
            event.accept()            