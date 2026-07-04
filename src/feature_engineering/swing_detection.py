"""
Multi-Timeframe Swing High/Low Detection
Critical for Goldmine strategy trend alignment
"""

import pandas as pd
import numpy as np
from typing import Tuple


def detect_swing_highs_lows(high: pd.Series, low: pd.Series, window: int = 5) -> pd.DataFrame:
    """
    Detect swing highs and lows
    
    A swing high is when the high is the highest within a window
    A swing low is when the low is the lowest within a window
    
    Parameters:
    -----------
    high : pd.Series
        High prices
    low : pd.Series
        Low prices
    window : int
        Lookback window for swing detection
        
    Returns:
    --------
    pd.DataFrame : Swing high/low indicators
    """
    df = pd.DataFrame()
    
    # Rolling max/min for swing detection
    rolling_max = high.rolling(window=window*2+1, center=True).max()
    rolling_min = low.rolling(window=window*2+1, center=True).min()
    
    # Swing high: when current high equals rolling max
    df['swing_high'] = (high == rolling_max).astype(int)
    df['swing_high_value'] = high.where(df['swing_high'] == 1)
    
    # Swing low: when current low equals rolling min
    df['swing_low'] = (low == rolling_min).astype(int)
    df['swing_low_value'] = low.where(df['swing_low'] == 1)
    
    # Last swing high/low values (forward fill)
    df['last_swing_high'] = df['swing_high_value'].ffill()
    df['last_swing_low'] = df['swing_low_value'].ffill()
    
    return df


def calculate_swing_trend(df: pd.DataFrame, close: pd.Series) -> pd.Series:
    """
    Calculate swing-based trend
    
    Uptrend: Price above last swing high
    Downtrend: Price below last swing low
    Range: Between swing high and low
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with swing high/low values
    close : pd.Series
        Close prices
        
    Returns:
    --------
    pd.Series : Trend indicator (-1: down, 0: range, 1: up)
    """
    trend = pd.Series(0, index=close.index)
    
    # Uptrend: close above last swing high
    trend[close > df['last_swing_high']] = 1
    
    # Downtrend: close below last swing low
    trend[close < df['last_swing_low']] = -1
    
    return trend


def calculate_multi_timeframe_alignment(
    swing_m1: pd.Series,
    swing_m3: pd.Series,
    swing_m5: pd.Series
) -> pd.Series:
    """
    Calculate multi-timeframe swing alignment
    
    All timeframes must agree on trend direction
    
    Parameters:
    -----------
    swing_m1 : pd.Series
        M1 swing trend
    swing_m3 : pd.Series
        M3 swing trend
    swing_m5 : pd.Series
        M5 swing trend
        
    Returns:
    --------
    pd.Series : Alignment score (-3 to +3)
    """
    # Sum all swing trends (aligned if all same sign)
    alignment = swing_m1 + swing_m3 + swing_m5
    
    return alignment
