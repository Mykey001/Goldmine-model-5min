"""
Technical Indicators for Goldmine Strategy
Implements RSI, EMA, ATR, MACD, and other indicators
"""

import pandas as pd
import numpy as np
from typing import Optional


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index
    
    Parameters:
    -----------
    data : pd.Series
        Price data (typically close prices)
    period : int
        RSI period (default: 14)
        
    Returns:
    --------
    pd.Series : RSI values (0-100)
    """
    # Calculate price changes
    delta = data.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average gains and losses
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average
    
    Parameters:
    -----------
    data : pd.Series
        Price data
    period : int
        EMA period
        
    Returns:
    --------
    pd.Series : EMA values
    """
    return data.ewm(span=period, adjust=False).mean()


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range
    
    Parameters:
    -----------
    high : pd.Series
        High prices
    low : pd.Series
        Low prices
    close : pd.Series
        Close prices
    period : int
        ATR period (default: 14)
        
    Returns:
    --------
    pd.Series : ATR values
    """
    # Calculate True Range
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calculate ATR as EMA of True Range
    atr = true_range.rolling(window=period, min_periods=period).mean()
    
    return atr


def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Parameters:
    -----------
    data : pd.Series
        Price data
    fast : int
        Fast EMA period
    slow : int
        Slow EMA period
    signal : int
        Signal line period
        
    Returns:
    --------
    pd.DataFrame : MACD, Signal, and Histogram
    """
    ema_fast = calculate_ema(data, fast)
    ema_slow = calculate_ema(data, slow)
    
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return pd.DataFrame({
        'macd': macd_line,
        'macd_signal': signal_line,
        'macd_hist': histogram
    })


def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Calculate Bollinger Bands
    
    Parameters:
    -----------
    data : pd.Series
        Price data
    period : int
        Moving average period
    std_dev : float
        Number of standard deviations
        
    Returns:
    --------
    pd.DataFrame : Upper, Middle, Lower bands
    """
    middle_band = data.rolling(window=period, min_periods=period).mean()
    std = data.rolling(window=period, min_periods=period).std()
    
    upper_band = middle_band + (std_dev * std)
    lower_band = middle_band - (std_dev * std)
    
    return pd.DataFrame({
        'bb_upper': upper_band,
        'bb_middle': middle_band,
        'bb_lower': lower_band,
        'bb_width': upper_band - lower_band
    })


def detect_rsi_crossover(rsi: pd.Series, oversold: float = 35.0, overbought: float = 65.0) -> pd.DataFrame:
    """
    Detect RSI crossovers (Goldmine strategy core)
    
    Parameters:
    -----------
    rsi : pd.Series
        RSI values
    oversold : float
        Oversold threshold (default: 35.0)
    overbought : float
        Overbought threshold (default: 65.0)
        
    Returns:
    --------
    pd.DataFrame : Crossover signals
    """
    df = pd.DataFrame()
    
    # Detect crossover above oversold (BUY signal → reverse to SELL)
    df['rsi_cross_above_oversold'] = (
        (rsi.shift(1) < oversold) & (rsi >= oversold)
    ).astype(int)
    
    # Detect crossover below overbought (SELL signal → reverse to BUY)
    df['rsi_cross_below_overbought'] = (
        (rsi.shift(1) > overbought) & (rsi <= overbought)
    ).astype(int)
    
    return df


def calculate_momentum(data: pd.Series, period: int = 10) -> pd.Series:
    """Calculate price momentum"""
    return data.diff(period)


def calculate_roc(data: pd.Series, period: int = 10) -> pd.Series:
    """Calculate Rate of Change"""
    return ((data - data.shift(period)) / data.shift(period)) * 100
