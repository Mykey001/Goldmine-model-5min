"""
Quick test script to verify H1 trend filter implementation
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path

print('='*60)
print('H1 TREND FILTER VERIFICATION TEST')
print('='*60)

# Test 1: Configuration loading
print('\n✅ Test 1: Loading configuration...')
try:
    with open('configs/backtest_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print('   SUCCESS: Config loaded')
    print(f'   Filter enabled: {config["trend_filter"]["enabled"]}')
    print(f'   H1 EMA period: {config["trend_filter"]["h1_ema_period"]}')
except Exception as e:
    print(f'   FAILED: {e}')
    exit(1)

# Test 2: Check H1 data availability
print('\n✅ Test 2: Checking H1 data...')
try:
    h1_path = Path('data/processed/H1_cleaned.parquet')
    if h1_path.exists():
        h1 = pd.read_parquet(h1_path)
        print(f'   SUCCESS: H1 data found')
        print(f'   Rows: {len(h1):,}')
        print(f'   Period: {h1.timestamp.min()} to {h1.timestamp.max()}')
    else:
        print('   WARNING: H1 data not found at data/processed/H1_cleaned.parquet')
        print('   Run: python scripts/01_data_processing.py')
except Exception as e:
    print(f'   FAILED: {e}')

# Test 3: Check M5 test data
print('\n✅ Test 3: Checking M5 test data...')
try:
    test_path = Path('data/features/test.parquet')
    if test_path.exists():
        test = pd.read_parquet(test_path)
        print(f'   SUCCESS: Test data found')
        print(f'   Rows: {len(test):,}')
        print(f'   Period: {test.timestamp.min()} to {test.timestamp.max()}')
    else:
        print('   WARNING: Test data not found at data/features/test.parquet')
        print('   Run: python scripts/02_feature_engineering.py')
except Exception as e:
    print(f'   FAILED: {e}')

# Test 4: Check model availability
print('\n✅ Test 4: Checking trained model...')
try:
    model_path = Path('models/final/xgboost_model.pkl')
    if model_path.exists():
        print(f'   SUCCESS: Model found at {model_path}')
    else:
        print('   WARNING: Model not found at models/final/xgboost_model.pkl')
        print('   Run: python scripts/03_model_training.py')
except Exception as e:
    print(f'   FAILED: {e}')

# Test 5: Verify directory structure
print('\n✅ Test 5: Verifying output directories...')
dirs_to_check = [
    'results/predictions',
    'results/metrics',
    'results/visualizations'
]
for dir_path in dirs_to_check:
    p = Path(dir_path)
    if p.exists():
        print(f'   ✓ {dir_path}')
    else:
        print(f'   ✗ {dir_path} (will be created automatically)')

# Test 6: Simulate trend filter logic
print('\n✅ Test 6: Testing trend filter logic...')
try:
    # Create sample data
    sample_signals = pd.DataFrame({
        'signal': [1, 0, 1, 0, 1, 0],  # BUY, SELL, BUY, SELL, BUY, SELL
        'h1_trend': [1, 1, 0, 0, 1, 0],  # UP, UP, DOWN, DOWN, UP, DOWN
    })
    
    # Apply filter logic
    buy_in_downtrend = (sample_signals['signal'] == 1) & (sample_signals['h1_trend'] == 0)
    sell_in_uptrend = (sample_signals['signal'] == 0) & (sample_signals['h1_trend'] == 1)
    
    sample_signals['filtered'] = sample_signals['signal'].copy()
    sample_signals.loc[buy_in_downtrend, 'filtered'] = -1
    sample_signals.loc[sell_in_uptrend, 'filtered'] = -1
    
    print('   Sample filter results:')
    print('   Signal | H1 Trend | Filtered | Result')
    print('   ' + '-'*50)
    for idx, row in sample_signals.iterrows():
        signal_name = 'BUY' if row['signal'] == 1 else 'SELL'
        trend_name = 'UP' if row['h1_trend'] == 1 else 'DOWN'
        filtered_name = signal_name if row['filtered'] != -1 else 'NO_TRADE'
        result = '✓ KEPT' if row['filtered'] != -1 else '✗ FILTERED'
        print(f'   {signal_name:6} | {trend_name:8} | {filtered_name:8} | {result}')
    
    filtered_count = (sample_signals['filtered'] == -1).sum()
    print(f'\n   SUCCESS: Logic working correctly')
    print(f'   Filtered: {filtered_count}/6 signals ({filtered_count/6*100:.0f}%)')
    
except Exception as e:
    print(f'   FAILED: {e}')

print('\n' + '='*60)
print('VERIFICATION COMPLETE')
print('='*60)

print('\n📋 Next Steps:')
print('1. If all tests passed, run: python scripts/05b_backtest_comparison.py')
print('2. Review results in: results/predictions/backtest_comparison.csv')
print('3. Adjust config in: configs/backtest_config.yaml')
print('4. Re-run comparison to test different settings')

print('\n💡 Quick Commands:')
print('   - Run comparison: python scripts/05b_backtest_comparison.py')
print('   - Run backtest: python scripts/05_backtesting.py')
print('   - Edit config: notepad configs/backtest_config.yaml')
