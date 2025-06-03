# ---------------------------------------------
# TRADE CONTROLLER
# ---------------------------------------------
from typing import Optional
from datetime import datetime
import pandas as pd
from src.core.models import TradeModel
from src.core.utils import find_peaks_and_valleys


class TradeController:
    """Controller for managing trade operations."""

    def __init__(self) -> None:
        """Initialize the trade controller with a trade model."""
        self.model = TradeModel()

    def set_current_date(self, date: str) -> None:
        """
        Set the current date in the model.

        Args:
            date (str): The current date in 'YYYY-MM-DD HH:MM' format.
        """
        try:
            self.model.current_date = date
        except Exception as e:
            print(f"Error setting current date: {e}")

    def buy_trade(self) -> None:
        """Open a new buy trade."""
        try:
            if not self.model.current_trade.empty:
                print("Closing current trade before opening a new one.")
                self.close_trade()
            entry_price = self.model.get_close_price(self.model.current_date)
            if entry_price is None:
                raise ValueError("Cannot open buy trade: No valid close price.")
            self.model.current_trade = pd.DataFrame([{
                'type': 'buy',
                'entry_date': self.model.current_date,
                'entry_price': entry_price,
                'status': 'open'
            }])
            print(f"Buy trade opened at {entry_price} on {self.model.current_date}")
        except Exception as e:
            print(f"Error opening buy trade: {e}")

    def sell_trade(self) -> None:
        """Open a new sell trade."""
        try:
            if not self.model.current_trade.empty:
                print("Closing current trade before opening a new one.")
                self.close_trade()
            entry_price = self.model.get_close_price(self.model.current_date)
            if entry_price is None:
                raise ValueError("Cannot open sell trade: No valid close price.")
            self.model.current_trade = pd.DataFrame([{
                'type': 'sell',
                'entry_date': self.model.current_date,
                'entry_price': entry_price,
                'status': 'open'
            }])
            print(f"Sell trade opened at {entry_price} on {self.model.current_date}")
        except Exception as e:
            print(f"Error opening sell trade: {e}")

    def close_trade(self) -> None:
        """Close the current trade and calculate profit/loss."""
        try:
            if not self.model.current_trade.empty and self.model.current_trade.iloc[0]['status'] == 'open':
                exit_price = self.model.get_close_price(self.model.current_date)
                if exit_price is None:
                    raise ValueError("Cannot close trade: No valid close price.")
                trade_type = self.model.current_trade.iloc[0]['type']
                entry_price = self.model.current_trade.iloc[0]['entry_price']
                profit = exit_price - entry_price if trade_type == 'buy' else entry_price - exit_price
                self.model.current_trade.loc[0, 'exit_date'] = self.model.current_date
                self.model.current_trade.loc[0, 'exit_price'] = exit_price
                self.model.current_trade.loc[0, 'profit'] = profit
                self.model.current_trade.loc[0, 'status'] = 'closed'
                self.model.current_trade = self.model.current_trade.dropna(how='all', axis=1)
                self.model.trades = self.model.trades.dropna(how='all', axis=1)
                self.model.trades = pd.concat([self.model.trades, self.model.current_trade], ignore_index=True)
                print(f"Trade closed with a profit/loss of {profit}.")
                print(f"Trade details: {self.model.current_trade.iloc[0].to_dict()}")
                self.model.current_trade = pd.DataFrame(columns=['type', 'entry_date', 'entry_price', 'status'])
            else:
                print("No open trade to close.")
        except Exception as e:
            print(f"Error closing trade: {e}")

    def auto_trade(self, df: pd.DataFrame, current_datetime: datetime, 
                  furthest_index: int = 100, peaks_distance: int = 5, peaks_prominence: float = 0.1) -> None:
        """
        Process a new data point and manage trades based on signals.

        Args:
            df (pd.DataFrame): The financial data dataframe.
            current_datetime (datetime): The current datetime.
            furthest_index (int): Maximum index distance for valid signals.
            peaks_distance (int): Distance parameter for peak detection.
            peaks_prominence (float): Prominence parameter for peak detection.
        """
        try:
            self.model.set_data(df)
            new_data_point = df.tail(1)
            if new_data_point.empty:
                print("No new data point available for auto trading.")
                return
            current_signal = find_peaks_and_valleys(df, distance=peaks_distance, prominence=peaks_prominence, rolling=True)
            df.loc[len(df) - 1, 'Signal'] = current_signal
            current_date = new_data_point.iloc[0]['Time']
            latest_trade_date = self.model.current_trade.iloc[-1]['entry_date'] if not self.model.current_trade.empty else None

            signals_since_last_trade = df[(df['Time'] > latest_trade_date) & (df['Time'] <= current_date)] if latest_trade_date else df[df['Time'] <= current_date]
            valid_signals = signals_since_last_trade.loc[signals_since_last_trade['Signal'].isin([0.0, 2.0])]

            if valid_signals.empty:
                return
            signal_index = valid_signals.index[-1]
            new_signal = valid_signals.iloc[-1]['Signal']
            index_difference = df.index[-1] - signal_index
            recent_signal_condition = index_difference <= furthest_index

            if pd.isna(new_signal) or new_signal == 1.0:
                return

            if not self.model.current_trade.empty:
                current_trade_type = self.model.current_trade.iloc[-1]['type']
                if (new_signal == 0.0 and current_trade_type == 'buy') or (new_signal == 2.0 and current_trade_type == 'sell'):
                    return
                self.close_trade()
                if new_signal == 0.0 and recent_signal_condition:
                    self.buy_trade()
                elif new_signal == 2.0 and recent_signal_condition:
                    self.sell_trade()
            else:
                if new_signal == 0.0 and recent_signal_condition:
                    self.buy_trade()
                elif new_signal == 2.0 and recent_signal_condition:
                    self.sell_trade()
        except Exception as e:
            print(f"Error in auto_trade: {e}")

    def export_to_excel(self) -> None:
        """Export the trade history to an Excel file."""
        try:
            if self.model.trades.empty:
                print("No trades to export.")
                return
            self.model.trades.to_excel('trades_history.xlsx', index=False)
            print(self.model.trades)
            print("Trades exported to 'trades_history.xlsx'.")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")