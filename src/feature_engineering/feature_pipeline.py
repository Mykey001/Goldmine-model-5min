"""
Main Feature Engineering Pipeline
Orchestrates all feature calculations for Goldmine ML Strategy
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path
from typing import Dict, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from feature_engineering.technical_indicators import (
    calculate_rsi, calculate_ema, calculate_atr, calculate_macd,
    calculate_bollinger_bands, detect_rsi_crossover, calculate_momentum, calculate_roc
)
from feature_engineering.swing_detection import (
    detect_swing_highs_lows, calculate_swing_trend
)
from feature_engineering.volume_profile import (
    calculate_volume_profile_poc, calculate_value_area, calculate_poc_features
)
from feature_engineering.temporal_features import extract_temporal_features


class GoldmineFeatureEngineer:
    """
    Feature engineering pipeline for Goldmine strategy
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize feature engineer
        
        Parameters:
        -----------
        config : Dict, optional
            Configuration dictionary with strategy parameters
        """
        self.config = config or self._default_config()
        
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'rsi_period': 14,
            'rsi_oversold': 35.0,
            'rsi_overbought': 65.0,
            'ema_period': 50,
            'atr_period': 14,
            'poc_lookback_hours': 24,
            'swing_window': 5
        }
    
    def engineer_features_m5(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features for M5 timeframe (primary execution timeframe)
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw M5 OHLCV data
            
        Returns:
        --------
        pd.DataFrame : Data with engineered features
        """
        print("Engineering M5 features...")
        df = df.copy()
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 1. Technical Indicators
        print("  - Calculating RSI...")
        df['rsi'] = calculate_rsi(df['close'], self.config['rsi_period'])
        
        print("  - Detecting RSI crossovers...")
        crossovers = detect_rsi_crossover(
            df['rsi'],
            self.config['rsi_oversold'],
            self.config['rsi_overbought']
        )
        df = pd.concat([df, crossovers], axis=1)
        
        print("  - Calculating ATR...")
        df['atr'] = calculate_atr(df['high'], df['low'], df['close'], self.config['atr_period'])
        
        print("  - Calculating MACD...")
        macd = calculate_macd(df['close'])
        df = pd.concat([df, macd], axis=1)
        
        print("  - Calculating Bollinger Bands...")
        bb = calculate_bollinger_bands(df['close'])
        df = pd.concat([df, bb], axis=1)
        
        print("  - Calculating momentum indicators...")
        df['momentum_10'] = calculate_momentum(df['close'], 10)
        df['momentum_20'] = calculate_momentum(df['close'], 20)
        df['roc_10'] = calculate_roc(df['close'], 10)
        
        # 2. Swing Detection
        print("  - Detecting swing highs/lows...")
        swings = detect_swing_highs_lows(df['high'], df['low'], self.config['swing_window'])
        df = pd.concat([df, swings], axis=1)
        
        df['swing_trend'] = calculate_swing_trend(swings, df['close'])
        
        # 3. Volume Profile POC
        print("  - Calculating Volume Profile POC (this may take a few minutes)...")
        df['poc_24h'] = calculate_volume_profile_poc(
            df,
            lookback_hours=self.config['poc_lookback_hours']
        )
        
        print("  - Calculating Value Area...")
        df['vah_24h'], df['val_24h'] = calculate_value_area(
            df,
            lookback_hours=self.config['poc_lookback_hours']
        )
        
        print("  - Calculating POC features...")
        poc_features = calculate_poc_features(df, df['poc_24h'])
        df = pd.concat([df, poc_features], axis=1)
        
        # 4. Price Action Features
        print("  - Calculating price action features...")
        df['price_change'] = df['close'].diff()
        df['price_change_pct'] = df['close'].pct_change() * 100
        df['high_low_range'] = df['high'] - df['low']
        df['close_open_diff'] = df['close'] - df['open']
        
        # Body and wick sizes
        df['body_size'] = np.abs(df['close'] - df['open'])
        df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
        
        # 5. Volume Features
        print("  - Calculating volume features...")
        df['volume_change'] = df['volume'].diff()
        df['volume_ma_20'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma_20']
        
        # 6. Temporal Features
        print("  - Extracting temporal features...")
        temporal = extract_temporal_features(df['timestamp'])
        df = pd.concat([df, temporal], axis=1)
        
        print(f"✓ M5 feature engineering complete! Total features: {len(df.columns)}")
        return df
    
    def engineer_features_h1(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features for H1 timeframe (macro trend filter)
        
        Parameters:
        -----------
        df : pd.DataFrame
            Raw H1 OHLCV data
            
        Returns:
        --------
        pd.DataFrame : Data with H1 EMA
        """
        print("Engineering H1 features...")
        df = df.copy()
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate EMA(50) - the macro gatekeeper
        print(f"  - Calculating EMA({self.config['ema_period']})...")
        df['ema_50'] = calculate_ema(df['close'], self.config['ema_period'])
        
        # Price vs EMA
        df['price_vs_ema'] = df['close'] - df['ema_50']
        df['above_ema'] = (df['close'] > df['ema_50']).astype(int)
        df['below_ema'] = (df['close'] < df['ema_50']).astype(int)
        
        # EMA slope (trend strength)
        df['ema_slope'] = df['ema_50'].diff(5)
        
        print(f"✓ H1 feature engineering complete!")
        return df
    
    def merge_timeframes(
        self,
        m5_df: pd.DataFrame,
        h1_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge H1 features into M5 dataframe
        
        Parameters:
        -----------
        m5_df : pd.DataFrame
            M5 data with features
        h1_df : pd.DataFrame
            H1 data with EMA
            
        Returns:
        --------
        pd.DataFrame : M5 data with H1 features merged
        """
        print("Merging H1 features into M5 timeframe...")
        
        # Select H1 features to merge
        h1_features = h1_df[['timestamp', 'ema_50', 'price_vs_ema', 'above_ema', 'ema_slope']].copy()
        h1_features.columns = ['timestamp', 'h1_ema_50', 'h1_price_vs_ema', 'h1_above_ema', 'h1_ema_slope']
        
        # Merge using asof (forward fill H1 values to M5)
        m5_df = m5_df.sort_values('timestamp')
        h1_features = h1_features.sort_values('timestamp')
        
        merged = pd.merge_asof(
            m5_df,
            h1_features,
            on='timestamp',
            direction='backward'
        )
        
        print(f"✓ Timeframe merge complete!")
        return merged
