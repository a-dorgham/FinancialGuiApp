# ---------------------------------------------
# FINANCIAL DATA PROCESSING MODULE
# ---------------------------------------------
"""
Module for processing financial data, including date manipulation, feature engineering,
data scaling, and visualization with peaks and valleys.

This module provides utilities for loading financial data, calculating technical indicators
(e.g., RSI, MACD, Stochastic Oscillator), identifying peaks and valleys, and plotting
results using Plotly.

Dependencies:
    - pandas
    - numpy
    - plotly
    - scipy
    - sklearn
"""

import os
from typing import Optional, Tuple, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks
from sklearn.preprocessing import MinMaxScaler


# ---------------------------------------------
# DATE UTILITIES
# ---------------------------------------------

def increment_date(date_str: str, increment_minutes: int) -> Optional[str]:
    """
    Increment a date string by a specified number of minutes.

    Args:
        date_str (str): Date string in 'YYYY-MM-DD HH:MM' format.
        increment_minutes (int): Number of minutes to increment the date by.

    Returns:
        Optional[str]: Incremented date string in 'YYYY-MM-DD HH:MM' format, or None if parsing fails.
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        new_date = date + timedelta(minutes=increment_minutes)
        return new_date.strftime("%Y-%m-%d %H:%M")
    except ValueError as e:
        print(f"Error incrementing date: {e}")
        return None


# ---------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------

def find_peaks_and_valleys(
    df_window: pd.DataFrame,
    distance: int = 5,
    prominence: float = 0.1,
    rolling: bool = False
) -> Union[np.ndarray, float]:
    """
    Identify peaks and valleys in financial data based on close prices.

    Peaks are marked as 2 (sell signal), valleys as 0 (buy signal), and neutral points as 1.

    Args:
        df_window (pd.DataFrame): DataFrame with 'Time' and 'Close' columns.
        distance (int, optional): Minimum number of points between peaks/valleys. Defaults to 5.
        prominence (float, optional): Minimum prominence for peaks/valleys. Defaults to 0.1.
        rolling (bool, optional): If True, return the last signal; otherwise, return all signals. Defaults to False.

    Returns:
        Union[np.ndarray, float]: Array of signals (2 for peaks, 0 for valleys, 1 for neutral) or single float if rolling=True.
    """
    df = df_window.copy()
    close = df['Close']
    time = df['Time']

    # Scale close prices
    scaler = MinMaxScaler(feature_range=(0, 1))
    close_scaled = scaler.fit_transform(close.values.reshape(-1, 1)).flatten()

    # Convert time to datetime
    time_data = pd.to_datetime(time)

    # Identify peaks
    peak_indices, _ = find_peaks(close_scaled, distance=distance, prominence=prominence)
    
    # Identify valleys (negative peaks)
    valley_indices, _ = find_peaks(-close_scaled, distance=distance, prominence=prominence)

    # Initialize signal array
    signal = np.ones_like(close_scaled)  # Neutral (1)
    signal[peak_indices] = 2  # Peak (sell, 2)
    signal[valley_indices] = 0  # Valley (buy, 0)

    return signal[-1] if rolling else signal


def add_features(
    df: pd.DataFrame,
    features: Optional[Union[list, tuple]] = None
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Add technical indicators and signals to a financial DataFrame.

    Features include moving averages, RSI, Stochastic Oscillator, MACD, and peak/valley signals.

    Args:
        df (pd.DataFrame): DataFrame with columns 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'.
        features (Optional[Union[list, tuple]], optional): List of feature columns to include in X. 
            Defaults to ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MACD'].

    Returns:
        Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
            - DataFrame with added features.
            - Time series.
            - Feature matrix (X).
            - Target variable (y, signals).
    """
    df = df.copy()

    # Add moving average
    df['MA_50'] = df['Close'].rolling(window=50).mean()

    # Add RSI
    df['RSI'] = rsi_features(df['Close'])

    # Handle NaN values
    df = handle_nan(df)

    # Add Stochastic features
    stoch_features = stochastic_features(df[['High', 'Low', 'Close']])
    df = pd.concat([df, stoch_features], axis=1)

    # Add MACD
    df['MACD'] = macd_features(df[['Close']])

    # Add peak/valley signals
    df['Signal'] = find_peaks_and_valleys(df_window=df[['Time', 'Close']], distance=5, prominence=0.1)

    # Handle NaN values again
    df = handle_nan(df)

    # Prepare features and target
    time = df['Time']
    if features is None:
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MACD']
    if isinstance(features, tuple):
        features = list(features)

    X = df[features]
    y = df['Signal']

    return df, time, X, y


def rsi_features(price_data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI) for a price series.

    Args:
        price_data (pd.Series): Series of closing prices.
        period (int, optional): Lookback period for RSI calculation. Defaults to 14.

    Returns:
        pd.Series: RSI values.
    """
    delta = price_data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.ewm(com=period - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=period - 1, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def stochastic_features(
    df: pd.DataFrame,
    k_length: int = 20,
    k_period: int = 3,
    d_period: int = 3
) -> pd.DataFrame:
    """
    Calculate Stochastic Oscillator features (%K, %D, crossover/under signals).

    Args:
        df (pd.DataFrame): DataFrame with 'High', 'Low', 'Close' columns.
        k_length (int, optional): Lookback period for high/low calculation. Defaults to 20.
        k_period (int, optional): Smoothing period for %K. Defaults to 3.
        d_period (int, optional): Smoothing period for %D. Defaults to 3.

    Returns:
        pd.DataFrame: DataFrame with columns '%K', 'CO' (crossover), 'CU' (crossunder), 'STC_SIGNAL'.
    """
    df = df.copy()
    df['L14'] = df['Low'].rolling(window=k_length).min()
    df['H14'] = df['High'].rolling(window=k_length).max()
    df['%K0'] = 100 * ((df['Close'] - df['L14']) / (df['H14'] - df['L14']))
    df['%K'] = df['%K0'].rolling(window=k_period).mean()
    df['%D'] = df['%K'].rolling(window=d_period).mean()
    df['CO'] = crossover(df['%K'], df['%D'])
    df['CU'] = crossunder(df['%K'], df['%D'])
    df['STC_SIGNAL'] = df.apply(get_stochastic_signal, axis=1)
    df.drop(['L14', 'H14', '%K0'], axis=1, inplace=True)
    return df[['%K', 'CO', 'CU', 'STC_SIGNAL']]


def macd_features(
    df: pd.DataFrame,
    short_window: int = 12,
    long_window: int = 26,
    signal_window: int = 9
) -> pd.Series:
    """
    Calculate the Moving Average Convergence Divergence (MACD) for financial data.

    Args:
        df (pd.DataFrame): DataFrame with 'Close' column.
        short_window (int, optional): Window for short-term EMA. Defaults to 12.
        long_window (int, optional): Window for long-term EMA. Defaults to 26.
        signal_window (int, optional): Window for signal line EMA. Defaults to 9.

    Returns:
        pd.Series: MACD signal line values.
    """
    df = df.copy()
    df['Short_EMA'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['Long_EMA'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    df['MACD_'] = df['Short_EMA'] - df['Long_EMA']
    df['MACD'] = df['MACD_'].ewm(span=signal_window, adjust=False).mean()
    df.drop(['Short_EMA', 'Long_EMA', 'MACD_'], axis=1, inplace=True)
    return df['MACD']


def crossover(
    x: pd.Series,
    y: pd.Series,
    cross_distance: Optional[int] = None
) -> pd.Series:
    """
    Detect crossover events where series x crosses above series y.

    Args:
        x (pd.Series): First series.
        y (pd.Series): Second series.
        cross_distance (Optional[int], optional): Shift distance for comparison. Defaults to 1'.

    Returns:
        pd.Series: Boolean series indicating crossover points.
    """
    shift_value = 1 if cross_distance is None else cross_distance
    return (x > y) & (x.shift(shift_value) < y.shift(shift_value))


def crossunder(
    x: pd.Series,
    y: pd.Series,
    cross_distance: Optional[int] = None
) -> pd.Series:
    """
    Detect crossunder events where series x crosses below series y.

    Args:
        x (pd.Series): First series.
        y (pd.Series): Second series.
        cross_distance (Optional[int], optional): Shift distance for comparison. Defaults to 1'.

    Returns:
        pd.Series: Boolean series indicating crossunder points.
    """
    shift_value = 1 if cross_distance is None else cross_distance
    return (x < y) & (x.shift(shift_value) > y.shift(shift_value))


def get_stochastic_signal(row: pd.Series) -> float:
    """
    Generate stochastic oscillator signals based on %K and crossover/crossunder events.

    Args:
        row (pd.Series): DataFrame row with '%K', 'CO', 'CU' columns.

    Returns:
        float: Signal value (1.27 for buy, 1.3 for sell, 1.25 for neutral).
    """
    if row['%K'] < 10 and row['CO']:
        return 1.27
    elif row['%K'] > 90 and row['CU']:
        return 1.3
    return 1.25


# ---------------------------------------------
# DATA HANDLING
# ---------------------------------------------

import pandas as pd
import os
from typing import Union


def load_data(
    df_raw: Union[str, pd.DataFrame] = None,
    start_date: str = "2024-7-1",
    end_date: str = "2024-7-23"
) -> pd.DataFrame:
    """
    Load and filter financial data from a pickle file or DataFrame.

    Args:
        df_raw (Union[str, pd.DataFrame], optional): Path to pickle file or DataFrame. Defaults to None.
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. Defaults to "2024-7-1".
        end_date (str, optional): End date in 'YYYY-MM-DD' format. Defaults to "2024-7-23".

    Returns:
        pd.DataFrame: Filtered DataFrame with columns 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'.
    """
    if isinstance(df_raw, str):
        df = pd.read_pickle(df_raw)
        df_raw = df.copy()

    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)

    df_raw['time'] = df_raw['time'].dt.tz_localize(None)
    mask = (df_raw['time'] >= start_datetime) & (df_raw['time'] <= end_datetime)
    df_reduced = df_raw.loc[mask].copy()

    df = pd.DataFrame()
    df['Time'] = df_reduced['time']
    df['Open'] = df_reduced['mid_o']
    df['High'] = df_reduced['mid_h']
    df['Low'] = df_reduced['mid_l']
    df['Close'] = df_reduced['mid_c']
    df['Volume'] = df_reduced['volume']

    df.sort_values(by='Time', ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def scale_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scale numerical columns in a DataFrame using MinMaxScaler, preserving the 'Time' column.

    Args:
        df (pd.DataFrame): DataFrame to scale.

    Returns:
        pd.DataFrame: Scaled DataFrame with same columns and index.
    """
    data = df.copy()

    if not isinstance(data, pd.DataFrame):
        raise ValueError("Invalid data type. Expected a pandas DataFrame.")

    # Handle 'Time' column
    time_col = data['Time'] if 'Time' in data.columns else None
    columns_to_scale = data.columns.drop('Time') if time_col is not None else data.columns

    # Scale numerical columns
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[columns_to_scale])

    # Create scaled DataFrame
    scaled_df = pd.DataFrame(scaled_data, columns=columns_to_scale, index=data.index)

    # Restore 'Time' column
    if time_col is not None:
        scaled_df['Time'] = time_col

    return scaled_df


def check_nan(X: pd.DataFrame, y: pd.Series) -> None:
    """
    Check for NaN values in feature matrix and target series, printing a warning if found.

    Args:
        X (pd.DataFrame): Feature matrix.
        y (pd.Series): Target series.
    """
    if X.isnull().values.any() or y.isnull().values.any():
        print("Warning: NaN values detected in the dataset.")


def handle_nan(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle NaN values in a DataFrame by forward-filling and dropping remaining NaNs.

    Args:
        df (pd.DataFrame): DataFrame to process.

    Returns:
        pd.DataFrame: DataFrame with NaN values handled.
    """
    df = df.copy()
    df.ffill(inplace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# ---------------------------------------------
# PLOTTING
# ---------------------------------------------

def plot_with_peaks(
    df: pd.DataFrame,
    fig: go.Figure = go.Figure(),
    plotData: bool = True,
    plotMA: bool = False,
    plotPeaks: bool = False,
    figShow: bool = False,
    plot_stoch: bool = False
) -> go.Figure:
    """
    Create a Plotly figure visualizing financial data with optional candlesticks, moving averages,
    peaks/valleys, and stochastic signals.

    Args:
        df (pd.DataFrame): DataFrame with 'Time', 'Open', 'High', 'Low', 'Close', 'Signal', and optional 'STC_SIGNAL'.
        fig (go.Figure, optional): Existing Plotly figure to add traces to. Defaults to new figure.
        plotData (bool, optional): Plot candlestick data. Defaults to True.
        plotMA (bool, optional): Plot moving average line. Defaults to False.
        plotPeaks (bool, optional): Plot peaks and valleys. Defaults to False.
        figShow (bool, optional): Display the figure. Defaults to False.
        plot_stoch (bool, optional): Plot stochastic signal. Defaults to False.

    Returns:
        go.Figure: Updated Plotly figure.
    """
    time = df['Time']
    close = df['Close']

    if plotData:
        candlestick_trace = go.Candlestick(
            x=df['Time'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Testing Data',
            increasing_line_color='green',
            decreasing_line_color='red'
        )
        fig.add_trace(candlestick_trace)

    if plotMA:
        price_trace = go.Scatter(
            x=time,
            y=close,
            name="Scaled Close Prices",
            mode='lines',
            line=dict(color='orange', width=1.5)
        )
        fig.add_trace(price_trace)

    if plot_stoch and 'STC_SIGNAL' in df.columns:
        stoch_trace = go.Scatter(
            x=time,
            y=df['STC_SIGNAL'],
            mode='lines',
            line=dict(color='red', width=1.5),
            name='Stochastic'
        )
        fig.add_trace(stoch_trace)

    if plotPeaks:
        # Identify peaks and valleys
        peak_indices = df['Signal'] > 1.9
        peak_times = time[peak_indices].reset_index(drop=True)
        peak_values = close[peak_indices].reset_index(drop=True)

        valley_indices = df['Signal'] < 0.1
        valley_times = time[valley_indices].reset_index(drop=True)
        valley_values = close[valley_indices].reset_index(drop=True)

        # Create DataFrames
        peaks = pd.DataFrame({'Time': peak_times, 'Value (Scaled)': peak_values})
        valleys = pd.DataFrame({'Time': valley_times, 'Value (Scaled)': valley_values})

        # Add peak and valley traces
        peak_trace = go.Scatter(
            x=peaks['Time'],
            y=peaks['Value (Scaled)'],
            mode='markers',
            marker=dict(color='white', symbol='triangle-down', size=10),
            name='Peaks'
        )
        valley_trace = go.Scatter(
            x=valleys['Time'],
            y=valleys['Value (Scaled)'],
            mode='markers',
            marker=dict(color='yellow', symbol='triangle-up', size=10),
            name='Valleys'
        )
        fig.add_trace(peak_trace)
        fig.add_trace(valley_trace)

    # Update layout
    fig.update_layout(
        title='Data Visualization with Predictions and Forecast',
        xaxis_title='Time',
        yaxis_title='Price',
        xaxis_rangeslider_visible=True,
        template='plotly_white',
        font=dict(size=10, color="#e1e1e1"),
        paper_bgcolor="#1e1e1e",
        plot_bgcolor="#1e1e1e",
        legend_title_text="Elements",
        showlegend=False,
        xaxis_showgrid=True,
        yaxis_showgrid=True
    )

    fig.update_xaxes(
        gridcolor="#1f292f",
        showgrid=True,
        fixedrange=False,
        rangeslider=dict(visible=False),
        rangebreaks=[dict(bounds=["sat", "mon"])]
    )

    if figShow:
        fig.show()

    return fig