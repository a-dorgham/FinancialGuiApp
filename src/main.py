# ---------------------------------------------
# MAIN APPLICATION ENTRY POINT
# ---------------------------------------------
import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.core.services import HTTPServerService


def main() -> int:
    """
    Initialize and run the financial GUI application.

    Returns:
        int: The application exit code.
    """
    try:
        app = QApplication(sys.argv)
        server_service = HTTPServerService(directory="src/utils")
        server_service.start()
        window = MainWindow(server_service)
        window.show()
        return_code = app.exec()
        server_service.stop()
        return return_code
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())