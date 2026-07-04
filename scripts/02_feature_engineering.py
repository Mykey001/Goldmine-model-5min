"""
Goldmine ML - Script 02: Feature Engineering
Create all predictive features and labels
"""

# ============================================================================
# IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ta  # Technical Analysis library
from sklearn.preprocessing import StandardScaler
import warnings
import os

warnings.filterwarnings('ignore')
print('✅ Imports complete!')

# ============================================================================
# 1. LOAD PROCESSED DATA
# ============================================================================
print('\n' + '='*60)
print('LOADING PROCESSED DATA')
print('='*60)

m5 = pd.read_parquet('data/processed/M5_cleaned.parquet')
print(f'M5 data loaded: {m5.shape}')
print(f'Date range: {m5.timestamp.min()} to {m5.timestamp.max()}')

# ============================================================================
# 2. RSI FEATURES (CORE STRATEGY)
# ============================================================================
print('\n' + '='*60)
print('CREATING RSI FEATURES')
print('='*60)

# Calculate RSI(14)
m5['rsi'] = ta.momentum.RSIIndicator(m5['close'], window=14).rsi()

# RSI zones
m5['rsi_oversold'] = (m5['rsi'] < 35).astype(int)
m5['rsi_overbought'] = (m5['rsi'] > 65).astype(int)

# RSI crosses (KEY SIGNALS for Goldmine strategy)
m5['rsi_cross_above_35'] = ((m5['rsi'] > 35) & (m5['rsi'].shift(1) <= 35)).astype(int)
m5['rsi_cross_below_65'] = ((m5['rsi'] < 65) & (m5['rsi'].shift(1) >= 65)).astype(int)

# RSI momentum
m5['rsi_momentum'] = m5['rsi'].diff()
m5['rsi_slope'] = m5['rsi'].diff(3)

print(f'RSI range: {m5.rsi.min():.2f} - {m5.rsi.max():.2f}')
print(f'Oversold periods: {m5.rsi_oversold.sum():,}')
print(f'Overbought periods: {m5.rsi_overbought.sum():,}')
print(f'Cross above 35: {m5.rsi_cross_above_35.sum():,}')
print(f'Cross below 65: {m5.rsi_cross_below_65.sum():,}')
print('✅ RSI features created')

# ============================================================================
# 3. PRICE ACTION FEATURES
# ============================================================================
print('\n' + '='*60)
print('CREATING PRICE ACTION FEATURES')
print('='*60)

# Momentum (multiple periods)
for period in [1, 3, 5, 10, 20]:
    m5[f'momentum_{period}'] = m5['close'].pct_change(period) * 100

# Volatility
m5['volatility_10'] = m5['close'].rolling(10).std()
m5['volatility_20'] = m5['close'].rolling(20).std()

# Candle patterns
m5['candle_body'] = abs(m5['close'] - m5['open'])
m5['candle_range'] = m5['high'] - m5['low']
m5['upper_wick'] = m5['high'] - m5[['open', 'close']].max(axis=1)
m5['lower_wick'] = m5[['open', 'close']].min(axis=1) - m5['low']

# Body ratio
m5['body_ratio'] = m5['candle_body'] / (m5['candle_range'] + 0.0001)

print('✅ Price action features created')

# ============================================================================
# 4. TREND INDICATORS
# ============================================================================
print('\n' + '='*60)
print('CREATING TREND INDICATORS')
print('='*60)

# EMAs
m5['ema_20'] = ta.trend.EMAIndicator(m5['close'], window=20).ema_indicator()
m5['ema_50'] = ta.trend.EMAIndicator(m5['close'], window=50).ema_indicator()
m5['price_above_ema20'] = (m5['close'] > m5['ema_20']).astype(int)
m5['price_above_ema50'] = (m5['close'] > m5['ema_50']).astype(int)
m5['ema_distance'] = (m5['close'] - m5['ema_20']) / m5['close'] * 100

# MACD
macd = ta.trend.MACD(m5['close'])
m5['macd'] = macd.macd()
m5['macd_signal'] = macd.macd_signal()
m5['macd_diff'] = macd.macd_diff()

# ADX (trend strength)
m5['adx'] = ta.trend.ADXIndicator(m5['high'], m5['low'], m5['close'], window=14).adx()

print('✅ Trend indicators created')

# ============================================================================
# 5. VOLUME FEATURES
# ============================================================================
print('\n' + '='*60)
print('CREATING VOLUME FEATURES')
print('='*60)

if 'volume' in m5.columns:
    m5['volume_ma'] = m5['volume'].rolling(20).mean()
    m5['volume_ratio'] = m5['volume'] / (m5['volume_ma'] + 1)
    m5['volume_surge'] = (m5['volume_ratio'] > 2).astype(int)
    print('✅ Volume features created')
else:
    print('⚠️  No volume column found - skipping volume features')

# ============================================================================
# 6. TEMPORAL FEATURES
# ============================================================================
print('\n' + '='*60)
print('CREATING TEMPORAL FEATURES')
print('='*60)

# Time components
m5['hour'] = m5['timestamp'].dt.hour
m5['day_of_week'] = m5['timestamp'].dt.dayofweek
m5['day_of_month'] = m5['timestamp'].dt.day
m5['week_of_year'] = m5['timestamp'].dt.isocalendar().week

# Trading sessions (UTC time)
m5['session_asian'] = ((m5['hour'] >= 0) & (m5['hour'] < 8)).astype(int)
m5['session_european'] = ((m5['hour'] >= 8) & (m5['hour'] < 13)).astype(int)
m5['session_us'] = ((m5['hour'] >= 13) & (m5['hour'] < 21)).astype(int)

print('✅ Temporal features created')

# ============================================================================
# 7. GENERATE LABELS (BUY/SELL/NO_TRADE)
# ============================================================================
print('\n' + '='*60)
print('GENERATING LABELS')
print('='*60)
print('This may take a few minutes...')

lookforward = 40  # 40 candles = 200 minutes on M5
tp_pips = 100
sl_pips = 200
pip_value = 0.01  # For XAUUSD

def generate_label(row_idx):
    """
    Generate label based on forward-looking outcome
    Returns: 1 (BUY), 0 (SELL), -1 (NO_TRADE)
    """
    if row_idx >= len(m5) - lookforward:
        return -1  # Not enough future data
    
    current_price = m5.loc[row_idx, 'close']
    future_slice = m5.loc[row_idx+1:row_idx+lookforward]
    
    future_high = future_slice['high'].max()
    future_low = future_slice['low'].min()
    
    move_up_pips = (future_high - current_price) / pip_value
    move_down_pips = (current_price - future_low) / pip_value
    
    # BUY: significant upward move
    if move_up_pips >= tp_pips and move_up_pips > move_down_pips * 1.5:
        return 1
    
    # SELL: significant downward move
    elif move_down_pips >= tp_pips and move_down_pips > move_up_pips * 1.5:
        return 0
    
    # NO_TRADE: unclear/choppy
    else:
        return -1

# Generate labels
m5['label'] = [generate_label(i) for i in range(len(m5))]

print('\n✅ Labels generated!')
print(f'\nLabel distribution:')
print(m5['label'].value_counts().sort_index())
print(f'\nPercentages:')
print((m5['label'].value_counts(normalize=True) * 100).sort_index())

# ============================================================================
# 8. CLEAN DATA & PREPARE FOR MODELING
# ============================================================================
print('\n' + '='*60)
print('CLEANING & PREPARING DATA')
print('='*60)

# Remove NaN rows (from indicators with lag)
print(f'Rows before cleaning: {len(m5):,}')
m5_clean = m5.dropna().reset_index(drop=True)
print(f'Rows after cleaning: {len(m5_clean):,}')
print(f'Rows removed: {len(m5) - len(m5_clean):,}')

# ============================================================================
# 9. TRAIN/VAL/TEST SPLIT (CHRONOLOGICAL)
# ============================================================================
print('\n' + '='*60)
print('SPLITTING DATA')
print('='*60)

# Define split dates
train_end = '2024-12-31'
val_end = '2025-03-31'

train = m5_clean[m5_clean['timestamp'] <= train_end].copy()
val = m5_clean[(m5_clean['timestamp'] > train_end) & 
               (m5_clean['timestamp'] <= val_end)].copy()
test = m5_clean[m5_clean['timestamp'] > val_end].copy()

print(f'\nTrain: {len(train):,} rows')
print(f'  {train.timestamp.min().date()} to {train.timestamp.max().date()}')
print(f'  Labels: SELL={sum(train.label==0)}, BUY={sum(train.label==1)}, NO_TRADE={sum(train.label==-1)}')

print(f'\nVal:   {len(val):,} rows')
print(f'  {val.timestamp.min().date()} to {val.timestamp.max().date()}')
print(f'  Labels: SELL={sum(val.label==0)}, BUY={sum(val.label==1)}, NO_TRADE={sum(val.label==-1)}')

print(f'\nTest:  {len(test):,} rows')
print(f'  {test.timestamp.min().date()} to {test.timestamp.max().date()}')
print(f'  Labels: SELL={sum(test.label==0)}, BUY={sum(test.label==1)}, NO_TRADE={sum(test.label==-1)}')

# ============================================================================
# 10. SAVE FEATURE MATRIX
# ============================================================================
print('\n' + '='*60)
print('SAVING FEATURE MATRIX')
print('='*60)

os.makedirs('data/features', exist_ok=True)

train.to_parquet('data/features/train.parquet', index=False)
val.to_parquet('data/features/val.parquet', index=False)
test.to_parquet('data/features/test.parquet', index=False)

print('✅ Train set saved: data/features/train.parquet')
print('✅ Val set saved: data/features/val.parquet')
print('✅ Test set saved: data/features/test.parquet')

# Save feature names for reference
feature_cols = [c for c in m5_clean.columns if c not in ['timestamp', 'timeframe', 'label']]
import json
with open('data/features/feature_names.json', 'w') as f:
    json.dump(feature_cols, f, indent=2)
print('✅ Feature names saved')

print('\n🎉 SCRIPT 02 COMPLETE!')
print(f'Total features created: {len(feature_cols)}')
print('Next: Run 03_model_training.py')

