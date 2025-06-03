# ---------------------------------------------
# HTTP SERVER CLASS
# ---------------------------------------------
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import Optional

class HTTPServerThread(threading.Thread):
    """
    A multi-threaded HTTP server class that serves files from a specified directory.
    This class extends `threading.Thread` to run the HTTP server in a separate thread,
    preventing it from blocking the main program execution.
    """

    def __init__(self, host: str = "localhost", port: int = 8000, directory: str = ".") -> None:
        """
        Initializes the HTTPServerThread with the specified host, port, and directory.

        Args:
            host (str): The hostname or IP address on which the server will listen.
                        Defaults to "localhost".
            port (int): The port number on which the server will listen.
                        Defaults to 8000.
            directory (str): The root directory from which files will be served.
                             Defaults to ".", meaning the current working directory.
        """
        super().__init__()
        self.host: str = host
        self.port: int = port
        self.directory: str = os.path.abspath(directory)  # Convert to absolute path
        self.server: Optional[HTTPServer] = None

    # ---------------------------------------------
    # SERVER CONTROL METHODS
    # ---------------------------------------------

    def run(self) -> None:
        """
        Starts the HTTP server.
        This method sets up the HTTP server to serve files from the specified directory
        without changing the process's working directory.
        """
        # Create a custom handler class with access to the directory
        def create_handler(directory):
            class CustomHandler(SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    # Pass the directory to the parent class
                    super().__init__(*args, directory=directory, **kwargs)

            return CustomHandler

        self.server = HTTPServer((self.host, self.port), create_handler(self.directory))
        print(f"Serving HTTP on {self.host}:{self.port} from directory: {self.directory}")
        self.server.serve_forever()

    def stop(self) -> None:
        """
        Stops the HTTP server.
        If the server is running, this method shuts it down gracefully.
        """
        if self.server:
            self.server.shutdown()
            print("HTTP Server stopped")