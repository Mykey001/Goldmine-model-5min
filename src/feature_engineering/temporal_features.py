"""
Temporal Features - Time-based patterns
Trading sessions, day of week, hour patterns
"""

import pandas as pd
import numpy as np


def extract_temporal_features(timestamps: pd.Series) -> pd.DataFrame:
    """
    Extract time-based features from timestamps
    
    Parameters:
    -----------
    timestamps : pd.Series
        Datetime timestamps
        
    Returns:
    --------
    pd.DataFrame : Temporal features
    """
    df = pd.DataFrame()
    
    # Basic time features
    df['hour'] = timestamps.dt.hour
    df['day_of_week'] = timestamps.dt.dayofweek  # 0=Monday, 6=Sunday
    df['day_of_month'] = timestamps.dt.day
    df['month'] = timestamps.dt.month
    
    # Trading sessions (UTC/GMT time)
    # Asian: 00:00-09:00, European: 07:00-16:00, US: 13:00-22:00
    df['session_asian'] = ((df['hour'] >= 0) & (df['hour'] < 9)).astype(int)
    df['session_european'] = ((df['hour'] >= 7) & (df['hour'] < 16)).astype(int)
    df['session_us'] = ((df['hour'] >= 13) & (df['hour'] < 22)).astype(int)
    
    # Session overlaps (higher volatility)
    df['session_asian_european'] = ((df['hour'] >= 7) & (df['hour'] < 9)).astype(int)
    df['session_european_us'] = ((df['hour'] >= 13) & (df['hour'] < 16)).astype(int)
    
    # Market open/close hours (high activity)
    df['market_open_hour'] = df['hour'].isin([0, 7, 8, 13, 14]).astype(int)
    df['market_close_hour'] = df['hour'].isin([8, 9, 15, 16, 21, 22]).astype(int)
    
    # Weekend proximity (Friday/Monday effects)
    df['is_monday'] = (df['day_of_week'] == 0).astype(int)
    df['is_friday'] = (df['day_of_week'] == 4).astype(int)
    
    # Time of day categories
    df['time_category'] = pd.cut(
        df['hour'],
        bins=[0, 6, 12, 18, 24],
        labels=['night', 'morning', 'afternoon', 'evening'],
        include_lowest=True
    )
    
    # Cyclical encoding (preserves circular nature of time)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    return df
