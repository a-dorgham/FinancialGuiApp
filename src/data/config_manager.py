# ---------------------------------------------
# CONFIGURATION MANAGER
# ---------------------------------------------
from typing import Optional
import json
import os


class ConfigManager:
    """Manages application configuration settings."""
    
    def __init__(self, config_path: str = "config.json") -> None:
        """
        Initialize the configuration manager.

        Args:
            config_path (str): Path to the configuration file.
        """
        data_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(data_path, config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """
        Load the configuration from a JSON file.

        Returns:
            dict: The configuration dictionary.
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {"data_path": "src/data/GBP_USD_M15.pkl"}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"data_path": "src/data/GBP_USD_M15.pkl"}

    def get_data_path(self) -> str:
        """
        Get the data file path from the configuration.

        Returns:
            str: The data file path.
        """
        return self.config.get("data_path", "src/data/GBP_USD_M15.pkl")

    def save_config(self, data_path: str) -> None:
        """
        Save the configuration to the JSON file.

        Args:
            data_path (str): The data file path to save.
        """
        try:
            with open(self.config_path, 'w') as f:
                if not data_path.startswith(("src", "..")):
                    data_path = os.path.join("src", data_path)
                self.config["data_path"] = data_path
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")