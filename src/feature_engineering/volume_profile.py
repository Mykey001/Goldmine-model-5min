"""
Volume Profile and Point of Control (POC) Calculation
Critical institutional flow indicator for Goldmine strategy
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_volume_profile_poc(
    df: pd.DataFrame,
    lookback_hours: int = 24,
    bins: int = 100
) -> pd.Series:
    """
    Calculate Volume Profile Point of Control (POC)
    
    POC = Price level with highest trading volume in lookback period
    Represents institutional "fair value" consensus
    
    Parameters:
    -----------
    df : pd.DataFrame
        Must contain: timestamp, high, low, close, volume
    lookback_hours : int
        Lookback period in hours (default: 24)
    bins : int
        Number of price bins for volume distribution
        
    Returns:
    --------
    pd.Series : POC values for each timestamp
    """
    poc_values = []
    
    for i in range(len(df)):
        # Get lookback window
        current_time = df.iloc[i]['timestamp']
        lookback_time = current_time - pd.Timedelta(hours=lookback_hours)
        
        # Filter data within lookback period
        mask = (df['timestamp'] >= lookback_time) & (df['timestamp'] <= current_time)
        window_data = df.loc[mask].copy()
        
        if len(window_data) < 10:  # Not enough data
            poc_values.append(np.nan)
            continue
        
        # Calculate price range
        price_min = window_data['low'].min()
        price_max = window_data['high'].max()
        
        # Create price bins
        price_bins = np.linspace(price_min, price_max, bins + 1)
        
        # Calculate volume at each price level
        volume_at_price = np.zeros(bins)
        
        for _, row in window_data.iterrows():
            # Distribute volume across price range of candle
            candle_low = row['low']
            candle_high = row['high']
            candle_volume = row['volume']
            
            # Find bins that intersect with this candle
            for j in range(bins):
                bin_low = price_bins[j]
                bin_high = price_bins[j + 1]
                
                # Check if candle overlaps with this bin
                if candle_high >= bin_low and candle_low <= bin_high:
                    # Add proportional volume
                    overlap = min(candle_high, bin_high) - max(candle_low, bin_low)
                    candle_range = candle_high - candle_low
                    
                    if candle_range > 0:
                        volume_proportion = overlap / candle_range
                        volume_at_price[j] += candle_volume * volume_proportion
                    else:
                        # Point candle - add all volume to this bin
                        volume_at_price[j] += candle_volume
        
        # Find POC (price level with max volume)
        poc_bin = np.argmax(volume_at_price)
        poc_price = (price_bins[poc_bin] + price_bins[poc_bin + 1]) / 2
        
        poc_values.append(poc_price)
    
    return pd.Series(poc_values, index=df.index, name='poc_24h')


def calculate_value_area(
    df: pd.DataFrame,
    lookback_hours: int = 24,
    value_area_pct: float = 0.70,
    bins: int = 100
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate Value Area High (VAH) and Value Area Low (VAL)
    
    Value Area = Price range containing 70% of volume
    
    Parameters:
    -----------
    df : pd.DataFrame
        Must contain: timestamp, high, low, close, volume
    lookback_hours : int
        Lookback period
    value_area_pct : float
        Percentage of volume for value area (default: 0.70)
    bins : int
        Number of price bins
        
    Returns:
    --------
    Tuple[pd.Series, pd.Series] : VAH and VAL
    """
    vah_values = []
    val_values = []
    
    for i in range(len(df)):
        current_time = df.iloc[i]['timestamp']
        lookback_time = current_time - pd.Timedelta(hours=lookback_hours)
        
        mask = (df['timestamp'] >= lookback_time) & (df['timestamp'] <= current_time)
        window_data = df.loc[mask].copy()
        
        if len(window_data) < 10:
            vah_values.append(np.nan)
            val_values.append(np.nan)
            continue
        
        # Calculate volume distribution (same as POC)
        price_min = window_data['low'].min()
        price_max = window_data['high'].max()
        price_bins = np.linspace(price_min, price_max, bins + 1)
        volume_at_price = np.zeros(bins)
        
        for _, row in window_data.iterrows():
            candle_low = row['low']
            candle_high = row['high']
            candle_volume = row['volume']
            
            for j in range(bins):
                bin_low = price_bins[j]
                bin_high = price_bins[j + 1]
                
                if candle_high >= bin_low and candle_low <= bin_high:
                    overlap = min(candle_high, bin_high) - max(candle_low, bin_low)
                    candle_range = candle_high - candle_low
                    
                    if candle_range > 0:
                        volume_proportion = overlap / candle_range
                        volume_at_price[j] += candle_volume * volume_proportion
                    else:
                        volume_at_price[j] += candle_volume
        
        # Find value area
        total_volume = volume_at_price.sum()
        target_volume = total_volume * value_area_pct
        
        # Start from POC and expand
        poc_bin = np.argmax(volume_at_price)
        accumulated_volume = volume_at_price[poc_bin]
        
        lower_bin = poc_bin
        upper_bin = poc_bin
        
        while accumulated_volume < target_volume:
            # Expand to side with more volume
            lower_vol = volume_at_price[lower_bin - 1] if lower_bin > 0 else 0
            upper_vol = volume_at_price[upper_bin + 1] if upper_bin < bins - 1 else 0
            
            if lower_vol > upper_vol and lower_bin > 0:
                lower_bin -= 1
                accumulated_volume += lower_vol
            elif upper_bin < bins - 1:
                upper_bin += 1
                accumulated_volume += upper_vol
            else:
                break
        
        vah = price_bins[upper_bin + 1]
        val = price_bins[lower_bin]
        
        vah_values.append(vah)
        val_values.append(val)
    
    vah_series = pd.Series(vah_values, index=df.index, name='vah_24h')
    val_series = pd.Series(val_values, index=df.index, name='val_24h')
    
    return vah_series, val_series


def calculate_poc_features(df: pd.DataFrame, poc: pd.Series) -> pd.DataFrame:
    """
    Calculate POC-related features
    
    Parameters:
    -----------
    df : pd.DataFrame
        Must contain: close, high, low
    poc : pd.Series
        POC values
        
    Returns:
    --------
    pd.DataFrame : POC features
    """
    features = pd.DataFrame()
    
    # Price position relative to POC
    features['price_vs_poc'] = df['close'] - poc
    features['price_vs_poc_pct'] = (df['close'] - poc) / poc * 100
    
    # Above or below POC (binary)
    features['above_poc'] = (df['close'] > poc).astype(int)
    features['below_poc'] = (df['close'] < poc).astype(int)
    
    # Distance from POC (absolute)
    features['distance_from_poc'] = np.abs(df['close'] - poc)
    features['distance_from_poc_normalized'] = features['distance_from_poc'] / poc
    
    return features
