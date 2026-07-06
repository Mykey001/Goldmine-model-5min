"""
Goldmine ML - Script 05D: Realistic Backtest
Enhanced backtest with spread costs, slippage, and first-touch logic
More accurately represents live trading conditions
"""

# ============================================================================
# IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import warnings
import ta
import yaml
from pathlib import Path
import os

warnings.filterwarnings('ignore')
print('✅ Imports complete!')

# ============================================================================
# SET WORKING DIRECTORY
# ============================================================================
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

# ============================================================================
# CONFIGURATION
# ============================================================================
print('\n' + '='*60)
print('REALISTIC BACKTEST CONFIGURATION')
print('='*60)

# Load config
try:
    with open('configs/backtest_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except:
    config = {
        'trend_filter': {'enabled': False, 'h1_ema_period': 200},
        'signals': {'min_confidence': 0.5},
        'risk_management': {
            'tp_pips': 100, 'sl_pips': 50, 'lot_size': 0.01,
            'pip_value': 0.01, 'starting_capital': 10000
        }
    }

# Realistic trading costs
SPREAD_PIPS = 2  # Typical Gold spread during normal hours
ENTRY_SLIPPAGE_PIPS = 1  # Expected entry slippage
EXIT_SLIPPAGE_PIPS = 0.5  # Expected exit slippage
COMMISSION_PER_LOT = 0  # If your broker charges commission

TP_PIPS = config['risk_management']['tp_pips']
SL_PIPS = config['risk_management']['sl_pips']
LOT_SIZE = config['risk_management']['lot_size']
PIP_VALUE = config['risk_management']['pip_value']
STARTING_CAPITAL = config['risk_management']['starting_capital']
DOLLARS_PER_PIP = 10 * LOT_SIZE

print('\n📋 Trading Costs Configuration:')
print(f'  Spread: {SPREAD_PIPS} pips')
print(f'  Entry Slippage: {ENTRY_SLIPPAGE_PIPS} pips')
print(f'  Exit Slippage: {EXIT_SLIPPAGE_PIPS} pips')
print(f'  Commission: ${COMMISSION_PER_LOT} per lot')
print(f'  Total Cost per Trade: ~{SPREAD_PIPS + ENTRY_SLIPPAGE_PIPS + EXIT_SLIPPAGE_PIPS:.1f} pips')
print('='*60)

# ============================================================================
# LOAD DATA
# ============================================================================
print('\n' + '='*60)
print('LOADING DATA')
print('='*60)

model = joblib.load('models/final/xgboost_model.pkl')
test = pd.read_parquet('data/features/test.parquet')

print(f'✅ Model and test data loaded')
print(f'Test period: {test.timestamp.min().date()} to {test.timestamp.max().date()}')

# Prepare features
exclude_cols = ['timestamp', 'timeframe', 'label', 'open', 'high', 'low', 'close', 'date', 'time']
feature_cols = [c for c in test.columns if c not in exclude_cols]

# Generate predictions
X_test = test[feature_cols]
test['prediction'] = model.predict(X_test)
test['confidence'] = np.max(model.predict_proba(X_test), axis=1)

# Filter signals
MIN_CONFIDENCE = config['signals']['min_confidence']
test['signal'] = test['prediction'].where(test['confidence'] >= MIN_CONFIDENCE, -1)

print(f'✅ Predictions generated')
print(f'Total signals: {(test.signal != -1).sum():,}')

# ============================================================================
# ENHANCED BACKTEST SIMULATOR
# ============================================================================
print('\n' + '='*60)
print('RUNNING REALISTIC BACKTEST')
print('='*60)

def determine_first_touch(row, tp_price, sl_price, direction):
    """
    Determine which level was hit first when both are touched in same candle.
    Uses candle close position as indicator.
    """
    if direction == 'BUY':
        tp_touched = row['high'] >= tp_price
        sl_touched = row['low'] <= sl_price
    else:  # SELL
        tp_touched = row['low'] <= tp_price
        sl_touched = row['high'] >= sl_price
    
    if not (tp_touched and sl_touched):
        # Only one or neither touched
        if tp_touched:
            return 'TP'
        elif sl_touched:
            return 'SL'
        else:
            return None
    
    # Both touched - determine which came first
    candle_range = row['high'] - row['low']
    if candle_range == 0:
        return 'TP'  # Default to TP if no range
    
    close_position = (row['close'] - row['low']) / candle_range
    
    if direction == 'BUY':
        # If close near high, price likely went up first (TP first)
        # If close near low, price likely went down first (SL first)
        if close_position > 0.5:
            return 'TP'
        else:
            return 'SL'
    else:  # SELL
        # If close near low, price likely went down first (TP first)
        # If close near high, price likely went up first (SL first)
        if close_position < 0.5:
            return 'TP'
        else:
            return 'SL'

# Initialize tracking
trades = []
equity = STARTING_CAPITAL
equity_curve = [equity]
active_trade = None

# Statistics
first_touch_cases = 0
tp_first_count = 0
sl_first_count = 0

print('Simulating trades with realistic execution...')

for idx in range(len(test)):
    row = test.iloc[idx]
    
    # Check active trade
    if active_trade is not None:
        direction = active_trade['direction']
        tp = active_trade['tp']
        sl = active_trade['sl']
        
        # Determine what happened
        result = determine_first_touch(row, tp, sl, direction)
        
        if result == 'TP':
            # Take profit hit
            # Account for spread and slippage
            actual_tp_pips = TP_PIPS - SPREAD_PIPS - EXIT_SLIPPAGE_PIPS
            profit = actual_tp_pips * DOLLARS_PER_PIP - (COMMISSION_PER_LOT * LOT_SIZE)
            
            active_trade['exit_price'] = active_trade['tp']
            active_trade['exit_time'] = row['timestamp']
            active_trade['profit'] = profit
            active_trade['exit_reason'] = 'TP'
            active_trade['spread_cost'] = SPREAD_PIPS * DOLLARS_PER_PIP
            active_trade['slippage_cost'] = (ENTRY_SLIPPAGE_PIPS + EXIT_SLIPPAGE_PIPS) * DOLLARS_PER_PIP
            
            trades.append(active_trade)
            equity += profit
            equity_curve.append(equity)
            active_trade = None
            
            # Check if both were touched
            if direction == 'BUY':
                if row['high'] >= tp and row['low'] <= sl:
                    first_touch_cases += 1
                    tp_first_count += 1
            else:
                if row['low'] <= tp and row['high'] >= sl:
                    first_touch_cases += 1
                    tp_first_count += 1
        
        elif result == 'SL':
            # Stop loss hit
            # Account for spread and slippage (both work against you)
            actual_sl_pips = SL_PIPS + SPREAD_PIPS + EXIT_SLIPPAGE_PIPS
            loss = -actual_sl_pips * DOLLARS_PER_PIP - (COMMISSION_PER_LOT * LOT_SIZE)
            
            active_trade['exit_price'] = active_trade['sl']
            active_trade['exit_time'] = row['timestamp']
            active_trade['profit'] = loss
            active_trade['exit_reason'] = 'SL'
            active_trade['spread_cost'] = SPREAD_PIPS * DOLLARS_PER_PIP
            active_trade['slippage_cost'] = (ENTRY_SLIPPAGE_PIPS + EXIT_SLIPPAGE_PIPS) * DOLLARS_PER_PIP
            
            trades.append(active_trade)
            equity += loss
            equity_curve.append(equity)
            active_trade = None
            
            # Check if both were touched
            if direction == 'BUY':
                if row['high'] >= tp and row['low'] <= sl:
                    first_touch_cases += 1
                    sl_first_count += 1
            else:
                if row['low'] <= tp and row['high'] >= sl:
                    first_touch_cases += 1
                    sl_first_count += 1
    
    # Open new trade
    if active_trade is None and row['signal'] in [0, 1]:
        # Entry with slippage
        entry_price = row['close']
        if row['signal'] == 1:  # BUY
            entry_price += ENTRY_SLIPPAGE_PIPS * PIP_VALUE
            active_trade = {
                'direction': 'BUY',
                'entry_time': row['timestamp'],
                'entry_price': entry_price,
                'tp': entry_price + (TP_PIPS * PIP_VALUE),
                'sl': entry_price - (SL_PIPS * PIP_VALUE),
                'confidence': row['confidence']
            }
        else:  # SELL
            entry_price -= ENTRY_SLIPPAGE_PIPS * PIP_VALUE
            active_trade = {
                'direction': 'SELL',
                'entry_time': row['timestamp'],
                'entry_price': entry_price,
                'tp': entry_price - (TP_PIPS * PIP_VALUE),
                'sl': entry_price + (SL_PIPS * PIP_VALUE),
                'confidence': row['confidence']
            }

trades_df = pd.DataFrame(trades)

print(f'\n✅ Realistic backtest complete!')
print(f'Total trades: {len(trades_df):,}')
print(f'\n📊 First-Touch Analysis:')
print(f'Both TP & SL touched in same candle: {first_touch_cases:,}')
print(f'  TP hit first: {tp_first_count:,} ({tp_first_count/first_touch_cases*100:.1f}%)')
print(f'  SL hit first: {sl_first_count:,} ({sl_first_count/first_touch_cases*100:.1f}%)')

# ============================================================================
# CALCULATE METRICS
# ============================================================================
print('\n' + '='*60)
print('PERFORMANCE METRICS (REALISTIC)')
print('='*60)

if len(trades_df) > 0:
    winning_trades = trades_df[trades_df['profit'] > 0]
    losing_trades = trades_df[trades_df['profit'] < 0]
    
    total_trades = len(trades_df)
    wins = len(winning_trades)
    losses = len(losing_trades)
    win_rate = wins / total_trades * 100
    
    gross_profit = winning_trades['profit'].sum()
    gross_loss = abs(losing_trades['profit'].sum())
    net_profit = gross_profit - gross_loss
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
    
    avg_win = winning_trades['profit'].mean() if wins > 0 else 0
    avg_loss = losing_trades['profit'].mean() if losses > 0 else 0
    
    # Total costs
    total_spread_cost = trades_df['spread_cost'].sum()
    total_slippage_cost = trades_df['slippage_cost'].sum()
    total_costs = total_spread_cost + total_slippage_cost
    
    # Drawdown
    equity_series = pd.Series(equity_curve)
    rolling_max = equity_series.expanding().max()
    drawdown = equity_series - rolling_max
    max_drawdown = drawdown.min()
    max_drawdown_pct = (max_drawdown / rolling_max.max()) * 100
    
    # Sharpe
    returns = equity_series.pct_change().dropna()
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
    
    print(f'\n📊 REALISTIC PERFORMANCE:')
    print(f'='*50)
    print(f'Total Trades:        {total_trades:,}')
    print(f'Winning Trades:      {wins:,} ({win_rate:.2f}%)')
    print(f'Losing Trades:       {losses:,} ({(losses/total_trades)*100:.2f}%)')
    print(f'')
    print(f'Gross Profit:        ${gross_profit:,.2f}')
    print(f'Gross Loss:          ${gross_loss:,.2f}')
    print(f'Net Profit:          ${net_profit:,.2f}')
    print(f'')
    print(f'💰 COSTS BREAKDOWN:')
    print(f'Total Spread Cost:   ${total_spread_cost:,.2f}')
    print(f'Total Slippage Cost: ${total_slippage_cost:,.2f}')
    print(f'Total Costs:         ${total_costs:,.2f}')
    print(f'Cost per Trade:      ${total_costs/total_trades:.2f}')
    print(f'')
    print(f'Profit Factor:       {profit_factor:.2f}')
    print(f'Average Win:         ${avg_win:.2f}')
    print(f'Average Loss:        ${avg_loss:.2f}')
    print(f'Risk-Reward Ratio:   {abs(avg_win/avg_loss):.2f}' if avg_loss != 0 else '')
    print(f'')
    print(f'Max Drawdown:        ${max_drawdown:,.2f} ({max_drawdown_pct:.2f}%)')
    print(f'Sharpe Ratio:        {sharpe:.2f}')
    print(f'')
    print(f'Final Equity:        ${equity:,.2f}')
    print(f'Return:              {((equity/STARTING_CAPITAL)-1)*100:.2f}%')

# ============================================================================
# SAVE RESULTS
# ============================================================================
print('\n' + '='*60)
print('SAVING RESULTS')
print('='*60)

os.makedirs('results/realistic', exist_ok=True)

trades_df.to_csv('results/realistic/realistic_trade_log.csv', index=False)
print('✅ Realistic trade log saved')

realistic_metrics = {
    'configuration': {
        'spread_pips': SPREAD_PIPS,
        'entry_slippage_pips': ENTRY_SLIPPAGE_PIPS,
        'exit_slippage_pips': EXIT_SLIPPAGE_PIPS,
        'commission_per_lot': COMMISSION_PER_LOT
    },
    'total_trades': int(total_trades),
    'winning_trades': int(wins),
    'losing_trades': int(losses),
    'win_rate': float(win_rate),
    'gross_profit': float(gross_profit),
    'gross_loss': float(gross_loss),
    'net_profit': float(net_profit),
    'profit_factor': float(profit_factor),
    'total_spread_cost': float(total_spread_cost),
    'total_slippage_cost': float(total_slippage_cost),
    'total_costs': float(total_costs),
    'first_touch_cases': int(first_touch_cases),
    'tp_first_count': int(tp_first_count),
    'sl_first_count': int(sl_first_count),
    'max_drawdown': float(max_drawdown),
    'max_drawdown_pct': float(max_drawdown_pct),
    'sharpe_ratio': float(sharpe),
    'final_equity': float(equity),
    'return_pct': float(((equity/STARTING_CAPITAL)-1)*100)
}

with open('results/realistic/realistic_metrics.json', 'w') as f:
    json.dump(realistic_metrics, f, indent=2)
print('✅ Realistic metrics saved')

# Equity curve
plt.figure(figsize=(14, 6))
plt.plot(equity_curve, linewidth=2, label='Realistic')
plt.axhline(y=STARTING_CAPITAL, color='r', linestyle='--', alpha=0.5, label='Starting Capital')
plt.title('Realistic Equity Curve (with spread + slippage)', fontweight='bold')
plt.xlabel('Trade Number')
plt.ylabel('Equity ($)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/realistic/realistic_equity_curve.png', dpi=150)
plt.close()
print('✅ Equity curve saved')

print('\n🎉 REALISTIC BACKTEST COMPLETE!')
print(f'\nℹ️  This represents more accurate live trading performance')
print(f'📁 Results saved in: results/realistic/')
