# ---------------------------------------------
# SERVICES
# ---------------------------------------------
from src.utils.http_server_thread import HTTPServerThread


class HTTPServerService:
    """Service for managing the HTTP server for serving Plotly JS."""

    def __init__(self, directory: str) -> None:
        """
        Initialize the HTTP server service.

        Args:
            directory (str): The directory to serve files from.
        """
        self.http_thread = HTTPServerThread(directory=directory)

    def start(self) -> None:
        """Start the HTTP server."""
        try:
            self.http_thread.start()
        except Exception as e:
            print(f"Error starting HTTP server: {e}")

    def stop(self) -> None:
        """Stop the HTTP server and wait for it to terminate."""
        try:
            self.http_thread.stop()
            self.http_thread.join()
        except Exception as e:
            print(f"Error stopping HTTP server: {e}")