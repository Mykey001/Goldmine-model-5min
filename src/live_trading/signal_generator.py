"""
Signal Generator - ML-based trading signal generation
"""
import logging
from typing import Tuple, Optional
import pandas as pd
import numpy as np
import joblib
import ta
import json
import os


class SignalGenerator:
    """Generate trading signals using trained XGBoost model"""
    
    def __init__(self, model_path: str):
        """
        Initialize signal generator
        
        Args:
            model_path: Path to trained XGBoost model (.pkl file)
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.model = None
        self.feature_cols = []
        self.min_confidence = float(os.getenv('MIN_CONFIDENCE', 0.5))
        
        self._load_model()
        self._load_feature_names()
    
    def _load_model(self):
        """Load trained model from file"""
        try:
            self.model = joblib.load(self.model_path)
            self.logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_feature_names(self):
        """Load feature names for prediction"""
        feature_file = 'data/features/feature_names.json'
        
        # Define the exact features used in training (exclude raw OHLCV columns)
        exclude_cols = ['date', 'time', 'open', 'high', 'low', 'close', 
                       'tickvol', 'vol', 'spread', 'real_volume', 'timestamp']
        
        if os.path.exists(feature_file):
            try:
                with open(feature_file, 'r') as f:
                    all_cols = json.load(f)
                # Filter out excluded columns
                self.feature_cols = [c for c in all_cols if c not in exclude_cols]
                self.logger.info(f"Loaded {len(self.feature_cols)} feature names (filtered from {len(all_cols)} total)")
            except Exception as e:
                self.logger.warning(f"Failed to load feature names: {e}")
                self.feature_cols = []
        else:
            self.logger.warning(f"Feature names file not found: {feature_file}")
    
    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all features matching backtest
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with calculated features
        """
        df = df.copy()
        
        try:
            # ===== RSI FEATURES (CORE STRATEGY) =====
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
            df['rsi_oversold'] = (df['rsi'] < 35).astype(int)
            df['rsi_overbought'] = (df['rsi'] > 65).astype(int)
            df['rsi_cross_above_35'] = ((df['rsi'] > 35) & (df['rsi'].shift(1) <= 35)).astype(int)
            df['rsi_cross_below_65'] = ((df['rsi'] < 65) & (df['rsi'].shift(1) >= 65)).astype(int)
            df['rsi_momentum'] = df['rsi'].diff()
            df['rsi_slope'] = df['rsi'].diff(3)
            
            # ===== PRICE ACTION FEATURES =====
            for period in [1, 3, 5, 10, 20]:
                df[f'momentum_{period}'] = df['close'].pct_change(period) * 100
            
            df['volatility_10'] = df['close'].rolling(10).std()
            df['volatility_20'] = df['close'].rolling(20).std()
            
            # Candle patterns
            df['candle_body'] = abs(df['close'] - df['open'])
            df['candle_range'] = df['high'] - df['low']
            df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
            df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
            df['body_ratio'] = df['candle_body'] / (df['candle_range'] + 0.0001)
            
            # ===== TREND INDICATORS =====
            df['ema_20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
            df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
            df['price_above_ema20'] = (df['close'] > df['ema_20']).astype(int)
            df['price_above_ema50'] = (df['close'] > df['ema_50']).astype(int)
            df['ema_distance'] = (df['close'] - df['ema_20']) / df['close'] * 100
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_diff'] = macd.macd_diff()
            
            # ADX
            df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=14).adx()
            
            # ===== VOLUME FEATURES =====
            if 'volume' in df.columns:
                df['volume_ma'] = df['volume'].rolling(20).mean()
                df['volume_ratio'] = df['volume'] / (df['volume_ma'] + 1)
                df['volume_surge'] = (df['volume_ratio'] > 2).astype(int)
            
            # ===== TEMPORAL FEATURES =====
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day_of_month'] = df['timestamp'].dt.day
            df['week_of_year'] = df['timestamp'].dt.isocalendar().week
            
            # Trading sessions (UTC)
            df['session_asian'] = ((df['hour'] >= 0) & (df['hour'] < 8)).astype(int)
            df['session_european'] = ((df['hour'] >= 8) & (df['hour'] < 13)).astype(int)
            df['session_us'] = ((df['hour'] >= 13) & (df['hour'] < 21)).astype(int)
            
            self.logger.debug("Features calculated successfully")
            return df
            
        except Exception as e:
            self.logger.error(f"Error computing features: {e}")
            raise
    
    def generate_signal(self, bars: pd.DataFrame) -> Tuple[int, float]:
        """
        Generate trading signal from latest bar
        
        Args:
            bars: DataFrame with recent OHLCV data (minimum 200 bars recommended)
        
        Returns:
            Tuple of (signal, confidence)
            signal: -1 (NO_TRADE), 0 (SELL), 1 (BUY)
            confidence: Model confidence score (0-1)
        """
        try:
            # Compute features
            features_df = self.compute_features(bars)
            
            # Get latest bar features
            latest = features_df.iloc[-1]
            
            # Check if we have feature columns defined
            if not self.feature_cols:
                # Use all numeric columns except excluded ones
                exclude_cols = ['timestamp', 'timeframe', 'label', 'open', 'high', 
                              'low', 'close', 'time', 'date', 'spread', 'real_volume']
                self.feature_cols = [c for c in features_df.columns 
                                    if c not in exclude_cols and features_df[c].dtype in ['float64', 'int64']]
            
            # Extract feature values
            feature_values = latest[self.feature_cols].values.reshape(1, -1)
            
            # Handle NaN values
            feature_values = np.nan_to_num(feature_values, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Validate feature count
            expected_features = self.model.n_features_in_ if hasattr(self.model, 'n_features_in_') else len(self.feature_cols)
            if feature_values.shape[1] != expected_features:
                self.logger.error(f"Feature shape mismatch, expected: {expected_features}, got {feature_values.shape[1]}")
                self.logger.error(f"Available features: {list(self.feature_cols)}")
                return -1, 0.0
            
            # Make prediction
            prediction = self.model.predict(feature_values)[0]
            confidence = np.max(self.model.predict_proba(feature_values))
            
            # Apply confidence threshold
            if confidence < self.min_confidence:
                self.logger.debug(f"Low confidence: {confidence:.3f} < {self.min_confidence}")
                return -1, confidence  # NO_TRADE
            
            self.logger.info(f"Signal generated: {prediction} (confidence: {confidence:.3f})")
            return int(prediction), float(confidence)
            
        except Exception as e:
            self.logger.error(f"Error generating signal: {e}")
            return -1, 0.0
    
    def validate_signal(self, signal: int, confidence: float) -> Tuple[bool, str]:
        """
        Validate signal before execution
        
        Args:
            signal: Signal value (-1, 0, 1)
            confidence: Confidence score
        
        Returns:
            Tuple of (is_valid, reason)
        """
        if signal not in [0, 1]:
            return False, "Invalid signal value (not BUY or SELL)"
        
        if confidence < self.min_confidence:
            return False, f"Confidence too low: {confidence:.3f} < {self.min_confidence}"
        
        return True, "Valid signal"
    
    def get_signal_name(self, signal: int) -> str:
        """
        Convert signal number to name
        
        Args:
            signal: Signal value
        
        Returns:
            Signal name string
        """
        if signal == 1:
            return "BUY"
        elif signal == 0:
            return "SELL"
        else:
            return "NO_TRADE"
