"""
Goldmine ML - Script 05: Backtesting
Simulate real trading performance with optional 1H trend filter
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
import sys

warnings.filterwarnings('ignore')
print('✅ Imports complete!')

# ============================================================================
# SET WORKING DIRECTORY TO PROJECT ROOT
# ============================================================================
# Get the project root directory (parent of scripts folder)
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)
print(f'Working directory: {os.getcwd()}')

# ============================================================================
# LOAD CONFIGURATION
# ============================================================================
print('\n' + '='*60)
print('LOADING BACKTEST CONFIGURATION')
print('='*60)

config_path = project_root / 'configs' / 'backtest_config.yaml'

try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    print(f'✅ Configuration loaded from {config_path}')
except FileNotFoundError:
    print(f'⚠️  Config file not found at {config_path}')
    print('Using default settings.')
    config = {
        'trend_filter': {'enabled': True, 'h1_ema_period': 200},
        'signals': {'min_confidence': 0.5},
        'risk_management': {
            'tp_pips': 100, 'sl_pips': 50, 'lot_size': 0.01,
            'pip_value': 0.01, 'starting_capital': 10000
        }
    }

# Extract settings
USE_H1_TREND_FILTER = config['trend_filter']['enabled']
H1_EMA_PERIOD = config['trend_filter']['h1_ema_period']
MIN_CONFIDENCE = config['signals']['min_confidence']
TP_PIPS = config['risk_management']['tp_pips']
SL_PIPS = config['risk_management']['sl_pips']
LOT_SIZE = config['risk_management']['lot_size']
PIP_VALUE = config['risk_management']['pip_value']
STARTING_CAPITAL = config['risk_management']['starting_capital']

print('\n📋 Configuration:')
print(f'  1H Trend Filter: {"ENABLED" if USE_H1_TREND_FILTER else "DISABLED"}')
if USE_H1_TREND_FILTER:
    print(f'  H1 EMA Period: {H1_EMA_PERIOD}')
print(f'  Min Confidence: {MIN_CONFIDENCE}')
print(f'  Take Profit: {TP_PIPS} pips')
print(f'  Stop Loss: {SL_PIPS} pips')
print(f'  Position Size: {LOT_SIZE} lots')
print(f'  Starting Capital: ${STARTING_CAPITAL:,}')
print('='*60)

# ============================================================================
# 1. LOAD MODEL & DATA
# ============================================================================
print('\n' + '='*60)
print('LOADING MODEL & DATA')
print('='*60)

model = joblib.load('models/final/xgboost_model.pkl')
test = pd.read_parquet('data/features/test.parquet')

print('✅ Model and data loaded')
print(f'Test period: {test.timestamp.min().date()} to {test.timestamp.max().date()}')

# ============================================================================
# 1B. LOAD H1 DATA AND CALCULATE TREND (IF ENABLED)
# ============================================================================
if USE_H1_TREND_FILTER:
    print('\n' + '='*60)
    print('LOADING H1 DATA FOR TREND FILTER')
    print('='*60)
    
    try:
        h1 = pd.read_parquet('data/processed/H1_cleaned.parquet')
        print(f'✅ H1 data loaded: {h1.shape}')
        print(f'H1 period: {h1.timestamp.min().date()} to {h1.timestamp.max().date()}')
        
        # Calculate H1 EMA for trend determination
        h1['h1_ema'] = ta.trend.EMAIndicator(h1['close'], window=H1_EMA_PERIOD).ema_indicator()
        h1['h1_trend'] = np.where(h1['close'] > h1['h1_ema'], 1, 0)  # 1 = uptrend, 0 = downtrend
        
        # Keep only necessary columns
        h1_trend = h1[['timestamp', 'h1_trend', 'h1_ema', 'close']].copy()
        h1_trend.rename(columns={'close': 'h1_close'}, inplace=True)
        
        # Merge H1 trend data to M5 test data
        # Use merge_asof to align H1 data with M5 timestamps
        test = test.sort_values('timestamp')
        h1_trend = h1_trend.sort_values('timestamp')
        
        test = pd.merge_asof(
            test,
            h1_trend,
            on='timestamp',
            direction='backward'
        )
        
        print(f'✅ H1 trend filter applied')
        print(f'Uptrend periods: {test.h1_trend.sum():,} ({test.h1_trend.sum()/len(test)*100:.1f}%)')
        print(f'Downtrend periods: {(1-test.h1_trend).sum():,} ({(1-test.h1_trend).sum()/len(test)*100:.1f}%)')
        
    except FileNotFoundError:
        print('⚠️  H1 data not found. Disabling trend filter.')
        USE_H1_TREND_FILTER = False
    except Exception as e:
        print(f'⚠️  Error loading H1 data: {e}')
        print('Disabling trend filter.')
        USE_H1_TREND_FILTER = False

# Prepare features
exclude_cols = ['timestamp', 'timeframe', 'label', 'open', 'high', 'low', 'close', 'date', 'time', 'h1_trend', 'h1_ema', 'h1_close']
feature_cols = [c for c in test.columns if c not in exclude_cols]

# ============================================================================
# 2. GENERATE TRADING SIGNALS
# ============================================================================
print('\n' + '='*60)
print('GENERATING TRADING SIGNALS')
print('='*60)

# Predict
X_test = test[feature_cols]
test['prediction'] = model.predict(X_test)
test['confidence'] = np.max(model.predict_proba(X_test), axis=1)

# Filter for tradeable signals (confidence > min_confidence)
min_confidence = MIN_CONFIDENCE
test['signal'] = test['prediction'].where(test['confidence'] >= min_confidence, -1)

# Apply H1 trend filter if enabled
if USE_H1_TREND_FILTER:
    print('\n' + '-'*60)
    print('APPLYING H1 TREND FILTER')
    print('-'*60)
    
    signals_before = (test['signal'] != -1).sum()
    
    # Filter logic:
    # - Only take BUY signals (prediction=1) when H1 trend is UP (h1_trend=1)
    # - Only take SELL signals (prediction=0) when H1 trend is DOWN (h1_trend=0)
    test['signal_filtered'] = test['signal'].copy()
    
    # Filter out BUY signals in downtrend
    buy_in_downtrend = (test['signal'] == 1) & (test['h1_trend'] == 0)
    test.loc[buy_in_downtrend, 'signal_filtered'] = -1
    
    # Filter out SELL signals in uptrend
    sell_in_uptrend = (test['signal'] == 0) & (test['h1_trend'] == 1)
    test.loc[sell_in_uptrend, 'signal_filtered'] = -1
    
    # Use filtered signals
    test['signal'] = test['signal_filtered']
    
    signals_after = (test['signal'] != -1).sum()
    filtered_out = signals_before - signals_after
    
    print(f'Signals before filter: {signals_before:,}')
    print(f'Signals after filter: {signals_after:,}')
    print(f'Filtered out: {filtered_out:,} ({filtered_out/signals_before*100:.1f}%)')
    print(f'  - BUY signals filtered (in downtrend): {buy_in_downtrend.sum():,}')
    print(f'  - SELL signals filtered (in uptrend): {sell_in_uptrend.sum():,}')
    print('-'*60)

print(f'Total candles: {len(test):,}')
print(f'\nFinal signals:')
print(f'SELL: {sum(test.signal==0):,}')
print(f'BUY:  {sum(test.signal==1):,}')
print(f'NO_TRADE: {sum(test.signal==-1):,}')

# ============================================================================
# 3. BACKTEST SIMULATOR
# ============================================================================
print('\n' + '='*60)
print('RUNNING BACKTEST')
print('='*60)

# Trading parameters
DOLLARS_PER_PIP = 10 * LOT_SIZE  # Standard lot calculation

# Initialize tracking
trades = []
equity = STARTING_CAPITAL  # Starting capital
equity_curve = [equity]

# Simulate trades
print('Simulating trades...')

active_trade = None

for idx in range(len(test)):
    row = test.iloc[idx]
    
    # Skip if no signal or already in trade
    if active_trade is not None:
        # Check if TP or SL hit
        if active_trade['direction'] == 'BUY':
            # Check TP
            if row['high'] >= active_trade['tp']:
                profit = TP_PIPS * DOLLARS_PER_PIP
                active_trade['exit_price'] = active_trade['tp']
                active_trade['exit_time'] = row['timestamp']
                active_trade['profit'] = profit
                active_trade['exit_reason'] = 'TP'
                trades.append(active_trade)
                equity += profit
                equity_curve.append(equity)
                active_trade = None
                continue
            # Check SL
            elif row['low'] <= active_trade['sl']:
                loss = -SL_PIPS * DOLLARS_PER_PIP
                active_trade['exit_price'] = active_trade['sl']
                active_trade['exit_time'] = row['timestamp']
                active_trade['profit'] = loss
                active_trade['exit_reason'] = 'SL'
                trades.append(active_trade)
                equity += loss
                equity_curve.append(equity)
                active_trade = None
                continue
                
        elif active_trade['direction'] == 'SELL':
            # Check TP
            if row['low'] <= active_trade['tp']:
                profit = TP_PIPS * DOLLARS_PER_PIP
                active_trade['exit_price'] = active_trade['tp']
                active_trade['exit_time'] = row['timestamp']
                active_trade['profit'] = profit
                active_trade['exit_reason'] = 'TP'
                trades.append(active_trade)
                equity += profit
                equity_curve.append(equity)
                active_trade = None
                continue
            # Check SL
            elif row['high'] >= active_trade['sl']:
                loss = -SL_PIPS * DOLLARS_PER_PIP
                active_trade['exit_price'] = active_trade['sl']
                active_trade['exit_time'] = row['timestamp']
                active_trade['profit'] = loss
                active_trade['exit_reason'] = 'SL'
                trades.append(active_trade)
                equity += loss
                equity_curve.append(equity)
                active_trade = None
                continue
    
    # Open new trade if signal present
    if active_trade is None and row['signal'] in [0, 1]:
        entry_price = row['close']
        
        if row['signal'] == 1:  # BUY
            active_trade = {
                'direction': 'BUY',
                'entry_time': row['timestamp'],
                'entry_price': entry_price,
                'tp': entry_price + (TP_PIPS * PIP_VALUE),
                'sl': entry_price - (SL_PIPS * PIP_VALUE),
                'confidence': row['confidence']
            }
        elif row['signal'] == 0:  # SELL
            active_trade = {
                'direction': 'SELL',
                'entry_time': row['timestamp'],
                'entry_price': entry_price,
                'tp': entry_price - (TP_PIPS * PIP_VALUE),
                'sl': entry_price + (SL_PIPS * PIP_VALUE),
                'confidence': row['confidence']
            }

trades_df = pd.DataFrame(trades)

print(f'\n✅ Backtest complete!')
print(f'Total trades executed: {len(trades_df)}')

# ============================================================================
# 4. CALCULATE METRICS
# ============================================================================
print('\n' + '='*60)
print('TRADING METRICS')
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
    
    # Drawdown
    equity_series = pd.Series(equity_curve)
    rolling_max = equity_series.expanding().max()
    drawdown = equity_series - rolling_max
    max_drawdown = drawdown.min()
    max_drawdown_pct = (max_drawdown / rolling_max.max()) * 100
    
    # Sharpe Ratio (simplified)
    returns = equity_series.pct_change().dropna()
    sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
    
    print(f'\n📊 PERFORMANCE SUMMARY:')
    print(f'='*50)
    print(f'Total Trades:        {total_trades}')
    print(f'Winning Trades:      {wins} ({win_rate:.2f}%)')
    print(f'Losing Trades:       {losses} ({(losses/total_trades)*100:.2f}%)')
    print(f'')
    print(f'Gross Profit:        ${gross_profit:,.2f}')
    print(f'Gross Loss:          ${gross_loss:,.2f}')
    print(f'Net Profit:          ${net_profit:,.2f}')
    print(f'')
    print(f'Profit Factor:       {profit_factor:.2f}')
    print(f'')
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
    # 5. VISUALIZATIONS
    # ============================================================================
    print('\n' + '='*60)
    print('GENERATING VISUALIZATIONS')
    print('='*60)
    
    # Equity curve
    plt.figure(figsize=(14, 6))
    plt.plot(equity_curve, linewidth=2)
    plt.title('Equity Curve', fontsize=14, fontweight='bold')
    plt.xlabel('Trade Number')
    plt.ylabel('Equity ($)')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=STARTING_CAPITAL, color='r', linestyle='--', alpha=0.5, label='Starting Capital')
    plt.legend()
    plt.tight_layout()
    plt.savefig('results/visualizations/equity_curve.png', dpi=150)
    plt.close()
    print('✅ Equity curve saved')
    
    # Win/Loss distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Profit distribution
    axes[0].hist(trades_df['profit'], bins=30, edgecolor='black', alpha=0.7)
    axes[0].axvline(x=0, color='r', linestyle='--', linewidth=2)
    axes[0].set_title('Profit/Loss Distribution', fontweight='bold')
    axes[0].set_xlabel('Profit/Loss ($)')
    axes[0].set_ylabel('Frequency')
    axes[0].grid(True, alpha=0.3)
    
    # Direction breakdown
    direction_counts = trades_df.groupby('direction')['profit'].agg(['count', 'sum'])
    axes[1].bar(direction_counts.index, direction_counts['count'], alpha=0.7)
    axes[1].set_title('Trades by Direction', fontweight='bold')
    axes[1].set_xlabel('Direction')
    axes[1].set_ylabel('Number of Trades')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/visualizations/trade_distribution.png', dpi=150)
    plt.close()
    print('✅ Trade distribution saved')
    
    # ============================================================================
    # 6. SAVE RESULTS
    # ============================================================================
    print('\n' + '='*60)
    print('SAVING RESULTS')
    print('='*60)
    
    # Save trade log
    trades_df.to_csv('results/predictions/trade_log.csv', index=False)
    print('✅ Trade log saved')
    
    # Save metrics
    backtest_metrics = {
        'configuration': {
            'h1_trend_filter_enabled': USE_H1_TREND_FILTER,
            'h1_ema_period': H1_EMA_PERIOD if USE_H1_TREND_FILTER else None,
            'min_confidence': min_confidence,
            'tp_pips': TP_PIPS,
            'sl_pips': SL_PIPS,
            'lot_size': LOT_SIZE
        },
        'total_trades': int(total_trades),
        'winning_trades': int(wins),
        'losing_trades': int(losses),
        'win_rate': float(win_rate),
        'gross_profit': float(gross_profit),
        'gross_loss': float(gross_loss),
        'net_profit': float(net_profit),
        'profit_factor': float(profit_factor),
        'average_win': float(avg_win),
        'average_loss': float(avg_loss),
        'max_drawdown': float(max_drawdown),
        'max_drawdown_pct': float(max_drawdown_pct),
        'sharpe_ratio': float(sharpe),
        'final_equity': float(equity),
        'return_pct': float(((equity/STARTING_CAPITAL)-1)*100)
    }
    
    with open('results/metrics/backtest_metrics.json', 'w') as f:
        json.dump(backtest_metrics, f, indent=2)
    print('✅ Backtest metrics saved')
    
    print('\n🎉 BACKTESTING COMPLETE!')
    print(f'\n📊 KEY RESULTS:')
    print(f'Win Rate: {win_rate:.2f}%')
    print(f'Profit Factor: {profit_factor:.2f}')
    print(f'Net Profit: ${net_profit:,.2f}')
    print(f'Sharpe Ratio: {sharpe:.2f}')

else:
    print('⚠️  No trades were executed in the backtest.')

print('\n✅ All notebooks complete! Check results/ folder for outputs.')

