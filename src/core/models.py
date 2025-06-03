# ---------------------------------------------
# DATA MODELS
# ---------------------------------------------
from typing import Optional
import pandas as pd


class TradeModel:
    """Model for managing trade data."""

    def __init__(self) -> None:
        """Initialize the trade model with empty dataframes."""
        self.trades = pd.DataFrame(columns=['type', 'entry_date', 'entry_price', 'status', 
                                           'exit_date', 'exit_price', 'profit'])
        self.current_trade = pd.DataFrame(columns=['type', 'entry_date', 'entry_price', 'status'])
        self.current_date: Optional[str] = None
        self.data: Optional[pd.DataFrame] = None

    def set_data(self, data: pd.DataFrame) -> None:
        """
        Set the financial data dataframe.

        Args:
            data (pd.DataFrame): The financial data.
        """
        try:
            self.data = data.copy()
        except Exception as e:
            print(f"Error setting data: {e}")

    def get_close_price(self, date: str) -> Optional[float]:
        """
        Get the close price for a specific date.

        Args:
            date (str): The date in 'YYYY-MM-DD HH:MM' format.

        Returns:
            Optional[float]: The close price, or None if not found.
        """
        try:
            return float(self.data.loc[self.data['Time'] == date, 'Close'].iloc[0])
        except (IndexError, KeyError) as e:
            print(f"Error retrieving close price for {date}: {e}")
            return None