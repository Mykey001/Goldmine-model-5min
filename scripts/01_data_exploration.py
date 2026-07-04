"""
Goldmine ML - Script 01: Data Exploration
Execute this in Jupyter or run directly
"""

# ============================================================================
# IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (15, 8)

print('✅ Imports complete!')
print(f'📅 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print('\n' + '='*60)
print('LOADING DATA')
print('='*60)

data_files = {
    'M1': 'data/raw/XAUUSDm_M1_202401012305_202607031457.csv',
    'M3': 'data/raw/XAUUSDm_M3_202401012303_202607031457.csv',
    'M5': 'data/raw/XAUUSDm_M5_202401012305_202607031500.csv',
    'H1': 'data/raw/XAUUSDm_H1_202401012300_202607031500.csv'
}

def load_data(path, tf):
    """Load and parse market data"""
    # Read CSV (tab-delimited)
    df = pd.read_csv(path, sep='\t')
    
    # Remove < > from column names
    df.columns = [c.strip('<>') for c in df.columns]
    
    # Create timestamp from DATE and TIME
    df['timestamp'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'])
    
    # Standardize column names (lowercase)
    df.columns = [c.lower() for c in df.columns]
    df['timeframe'] = tf
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    print(f'{tf}: {len(df):,} rows | {df.timestamp.min().date()} to {df.timestamp.max().date()}')
    return df

# Load all timeframes
data = {}
for tf, path in data_files.items():
    data[tf] = load_data(path, tf)

print('\n✅ All data loaded successfully!')

# ============================================================================
# 2. DATA QUALITY CHECK
# ============================================================================
print('\n' + '='*60)
print('DATA QUALITY VALIDATION')
print('='*60)

m5 = data['M5']  # Primary timeframe

print(f'\n📊 M5 DATA:')
print(f'Shape: {m5.shape}')
print(f'Columns: {list(m5.columns)}')
print(f'\nFirst 5 rows:')
print(m5.head())

print(f'\n🔍 QUALITY CHECKS:')
print(f'Missing values:\n{m5.isnull().sum()}')
print(f'\nDuplicates: {m5.timestamp.duplicated().sum()}')

# OHLC validation
invalid = ((m5.low > m5.high) | 
           (m5.low > m5.close) | 
           (m5.high < m5.close) |
           (m5.low > m5.open) |
           (m5.high < m5.open)).sum()
print(f'Invalid OHLC: {invalid}')

# Price statistics
print(f'\n💰 PRICE STATISTICS:')
print(f'Range: ${m5.close.min():.2f} - ${m5.close.max():.2f}')
print(f'Mean: ${m5.close.mean():.2f}')
print(f'Std Dev: ${m5.close.std():.2f}')

print('\n✅ Quality check complete!')

# ============================================================================
# 3. VISUALIZATIONS
# ============================================================================
print('\n' + '='*60)
print('GENERATING VISUALIZATIONS')
print('='*60)

# Plot closing price
plt.figure(figsize=(16, 6))
plt.plot(m5.timestamp, m5.close, linewidth=0.5, alpha=0.8)
plt.title('XAUUSDm M5 Closing Price', fontsize=14, fontweight='bold')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/visualizations/m5_price_chart.png', dpi=150)
plt.close()  # Close instead of show

print('✅ Chart saved to results/visualizations/')

# ============================================================================
# 4. SAVE CLEANED DATA
# ============================================================================
print('\n' + '='*60)
print('SAVING PROCESSED DATA')
print('='*60)

os.makedirs('data/processed', exist_ok=True)

for tf, df in data.items():
    output_path = f'data/processed/{tf}_cleaned.parquet'
    df.to_parquet(output_path, index=False)
    print(f'✅ Saved {tf}: {output_path}')

print('\n🎉 SCRIPT 01 COMPLETE!')
print('Next: Run 02_feature_engineering.py')
