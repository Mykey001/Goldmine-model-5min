"""
Goldmine ML - Script 05B: Backtest Comparison
Compare performance with and without H1 trend filter
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
from typing import Dict, List, Tuple
from pathlib import Path
import os
import sys

warnings.filterwarnings('ignore')
print('✅ Imports complete!')

# ============================================================================
# SET WORKING DIRECTORY TO PROJECT ROOT
# ============================================================================
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)
print(f'Working directory: {os.getcwd()}')

# ============================================================================
# BACKTEST FUNCTION
# ============================================================================

def run_backtest(test_data: pd.DataFrame, use_trend_filter: bool = False, 
                 h1_ema_period: int = 200) -> Tuple[pd.DataFrame, Dict]:
    """
    Run backtest with or without H1 trend filter
    
    Parameters:
    -----------
    test_data : pd.DataFrame
        Test dataset with features
    use_trend_filter : bool
        Whether to apply H1 trend filter
    h1_ema_period : int
        H1 EMA period for trend determination
        
    Returns:
    --------
    trades_df : pd.DataFrame
        Trade log
    metrics : Dict
        Performance metrics
    """
    
    test = test_data.copy()
    
    # Load model
    model = joblib.load('models/final/xgboost_model.pkl')
    
    # Apply H1 trend filter if enabled
    if use_trend_filter:
        print(f'\n🔍 Loading H1 data for trend filter (EMA-{h1_ema_period})...')
        try:
            h1 = pd.read_parquet('data/processed/H1_cleaned.parquet')
            
            # Calculate H1 EMA and trend
            h1['h1_ema'] = ta.trend.EMAIndicator(h1['close'], window=h1_ema_period).ema_indicator()
            h1['h1_trend'] = np.where(h1['close'] > h1['h1_ema'], 1, 0)
            
            h1_trend = h1[['timestamp', 'h1_trend', 'h1_ema', 'close']].copy()
            h1_trend.rename(columns={'close': 'h1_close'}, inplace=True)
            
            # Merge with test data
            test = test.sort_values('timestamp')
            h1_trend = h1_trend.sort_values('timestamp')
            
            test = pd.merge_asof(test, h1_trend, on='timestamp', direction='backward')
            print('✅ H1 trend filter applied')
            
        except Exception as e:
            print(f'⚠️  Error loading H1 data: {e}')
            use_trend_filter = False
    
    # Prepare features
    exclude_cols = ['timestamp', 'timeframe', 'label', 'open', 'high', 'low', 'close', 
                   'date', 'time', 'h1_trend', 'h1_ema', 'h1_close']
    feature_cols = [c for c in test.columns if c not in exclude_cols]
    
    # Generate predictions
    X_test = test[feature_cols]
    test['prediction'] = model.predict(X_test)
    test['confidence'] = np.max(model.predict_proba(X_test), axis=1)
    
    # Filter by confidence
    min_confidence = 0.5
    test['signal'] = test['prediction'].where(test['confidence'] >= min_confidence, -1)
    
    # Apply trend filter
    if use_trend_filter and 'h1_trend' in test.columns:
        # Filter out BUY signals in downtrend
        buy_in_downtrend = (test['signal'] == 1) & (test['h1_trend'] == 0)
        test.loc[buy_in_downtrend, 'signal'] = -1
        
        # Filter out SELL signals in uptrend
        sell_in_uptrend = (test['signal'] == 0) & (test['h1_trend'] == 1)
        test.loc[sell_in_uptrend, 'signal'] = -1
    
    # Trading parameters
    TP_PIPS = 100
    SL_PIPS = 50
    PIP_VALUE = 0.01
    LOT_SIZE = 0.01
    DOLLARS_PER_PIP = 10 * LOT_SIZE
    
    # Initialize tracking
    trades = []
    equity = 10000
    equity_curve = [equity]
    active_trade = None
    
    # Simulate trades
    for idx in range(len(test)):
        row = test.iloc[idx]
        
        # Check active trade for TP/SL
        if active_trade is not None:
            if active_trade['direction'] == 'BUY':
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
        
        # Open new trade
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
    
    # Calculate metrics
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
        
        # Sharpe Ratio
        returns = equity_series.pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        metrics = {
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
            'return_pct': float(((equity/10000)-1)*100),
            'equity_curve': equity_curve
        }
    else:
        metrics = None
    
    return trades_df, metrics


# ============================================================================
# MAIN COMPARISON
# ============================================================================
print('\n' + '='*60)
print('BACKTEST COMPARISON: WITH vs WITHOUT H1 TREND FILTER')
print('='*60)

# Load test data
print('\nLoading test data...')
test = pd.read_parquet('data/features/test.parquet')
print(f'✅ Test period: {test.timestamp.min().date()} to {test.timestamp.max().date()}')

# Run backtest WITHOUT filter
print('\n' + '='*60)
print('BACKTEST 1: NO FILTER (All Signals)')
print('='*60)
trades_no_filter, metrics_no_filter = run_backtest(test, use_trend_filter=False)

if metrics_no_filter:
    print(f'\n📊 Results WITHOUT Filter:')
    print(f'Total Trades: {metrics_no_filter["total_trades"]}')
    print(f'Win Rate: {metrics_no_filter["win_rate"]:.2f}%')
    print(f'Profit Factor: {metrics_no_filter["profit_factor"]:.2f}')
    print(f'Net Profit: ${metrics_no_filter["net_profit"]:,.2f}')
    print(f'Return: {metrics_no_filter["return_pct"]:.2f}%')
    print(f'Sharpe Ratio: {metrics_no_filter["sharpe_ratio"]:.2f}')
    print(f'Max Drawdown: {metrics_no_filter["max_drawdown_pct"]:.2f}%')

# Run backtest WITH filter
print('\n' + '='*60)
print('BACKTEST 2: WITH H1 TREND FILTER (EMA-200)')
print('='*60)
trades_with_filter, metrics_with_filter = run_backtest(test, use_trend_filter=True, h1_ema_period=200)

if metrics_with_filter:
    print(f'\n📊 Results WITH Filter:')
    print(f'Total Trades: {metrics_with_filter["total_trades"]}')
    print(f'Win Rate: {metrics_with_filter["win_rate"]:.2f}%')
    print(f'Profit Factor: {metrics_with_filter["profit_factor"]:.2f}')
    print(f'Net Profit: ${metrics_with_filter["net_profit"]:,.2f}')
    print(f'Return: {metrics_with_filter["return_pct"]:.2f}%')
    print(f'Sharpe Ratio: {metrics_with_filter["sharpe_ratio"]:.2f}')
    print(f'Max Drawdown: {metrics_with_filter["max_drawdown_pct"]:.2f}%')

# ============================================================================
# COMPARISON ANALYSIS
# ============================================================================
if metrics_no_filter and metrics_with_filter:
    print('\n' + '='*60)
    print('COMPARISON SUMMARY')
    print('='*60)
    
    comparison = pd.DataFrame({
        'No Filter': [
            metrics_no_filter['total_trades'],
            f"{metrics_no_filter['win_rate']:.2f}%",
            f"{metrics_no_filter['profit_factor']:.2f}",
            f"${metrics_no_filter['net_profit']:,.2f}",
            f"{metrics_no_filter['return_pct']:.2f}%",
            f"{metrics_no_filter['sharpe_ratio']:.2f}",
            f"{metrics_no_filter['max_drawdown_pct']:.2f}%"
        ],
        'With H1 Filter': [
            metrics_with_filter['total_trades'],
            f"{metrics_with_filter['win_rate']:.2f}%",
            f"{metrics_with_filter['profit_factor']:.2f}",
            f"${metrics_with_filter['net_profit']:,.2f}",
            f"{metrics_with_filter['return_pct']:.2f}%",
            f"{metrics_with_filter['sharpe_ratio']:.2f}",
            f"{metrics_with_filter['max_drawdown_pct']:.2f}%"
        ],
        'Difference': [
            metrics_with_filter['total_trades'] - metrics_no_filter['total_trades'],
            f"{metrics_with_filter['win_rate'] - metrics_no_filter['win_rate']:+.2f}%",
            f"{metrics_with_filter['profit_factor'] - metrics_no_filter['profit_factor']:+.2f}",
            f"${metrics_with_filter['net_profit'] - metrics_no_filter['net_profit']:+,.2f}",
            f"{metrics_with_filter['return_pct'] - metrics_no_filter['return_pct']:+.2f}%",
            f"{metrics_with_filter['sharpe_ratio'] - metrics_no_filter['sharpe_ratio']:+.2f}",
            f"{metrics_with_filter['max_drawdown_pct'] - metrics_no_filter['max_drawdown_pct']:+.2f}%"
        ]
    }, index=['Total Trades', 'Win Rate', 'Profit Factor', 'Net Profit', 
              'Return %', 'Sharpe Ratio', 'Max DD %'])
    
    print('\n')
    print(comparison.to_string())
    
    # Save comparison
    comparison.to_csv('results/predictions/backtest_comparison.csv')
    print('\n✅ Comparison saved: results/predictions/backtest_comparison.csv')
    
    # ============================================================================
    # VISUALIZATIONS
    # ============================================================================
    print('\n' + '='*60)
    print('GENERATING COMPARISON VISUALIZATIONS')
    print('='*60)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # Equity curves
    ax = axes[0, 0]
    ax.plot(metrics_no_filter['equity_curve'], label='No Filter', linewidth=2, alpha=0.8)
    ax.plot(metrics_with_filter['equity_curve'], label='With H1 Filter', linewidth=2, alpha=0.8)
    ax.axhline(y=10000, color='gray', linestyle='--', alpha=0.5)
    ax.set_title('Equity Curve Comparison', fontsize=12, fontweight='bold')
    ax.set_xlabel('Trade Number')
    ax.set_ylabel('Equity ($)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Win rate comparison
    ax = axes[0, 1]
    win_rates = [metrics_no_filter['win_rate'], metrics_with_filter['win_rate']]
    colors = ['#3498db', '#2ecc71']
    bars = ax.bar(['No Filter', 'With H1 Filter'], win_rates, color=colors, alpha=0.7)
    ax.set_title('Win Rate Comparison', fontsize=12, fontweight='bold')
    ax.set_ylabel('Win Rate (%)')
    ax.set_ylim(0, 100)
    for bar, val in zip(bars, win_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Profit factor comparison
    ax = axes[1, 0]
    pf_values = [metrics_no_filter['profit_factor'], metrics_with_filter['profit_factor']]
    bars = ax.bar(['No Filter', 'With H1 Filter'], pf_values, color=colors, alpha=0.7)
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Break-even')
    ax.set_title('Profit Factor Comparison', fontsize=12, fontweight='bold')
    ax.set_ylabel('Profit Factor')
    for bar, val in zip(bars, pf_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Trade count comparison
    ax = axes[1, 1]
    trade_counts = [metrics_no_filter['total_trades'], metrics_with_filter['total_trades']]
    bars = ax.bar(['No Filter', 'With H1 Filter'], trade_counts, color=colors, alpha=0.7)
    ax.set_title('Total Trades Comparison', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Trades')
    for bar, val in zip(bars, trade_counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(val)}', ha='center', va='bottom', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('results/visualizations/backtest_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print('✅ Comparison chart saved')
    
    # Save detailed comparison metrics
    comparison_metrics = {
        'no_filter': metrics_no_filter,
        'with_h1_filter': metrics_with_filter,
        'improvements': {
            'trade_reduction': metrics_no_filter['total_trades'] - metrics_with_filter['total_trades'],
            'win_rate_change': metrics_with_filter['win_rate'] - metrics_no_filter['win_rate'],
            'profit_factor_change': metrics_with_filter['profit_factor'] - metrics_no_filter['profit_factor'],
            'net_profit_change': metrics_with_filter['net_profit'] - metrics_no_filter['net_profit'],
            'return_change': metrics_with_filter['return_pct'] - metrics_no_filter['return_pct'],
            'sharpe_change': metrics_with_filter['sharpe_ratio'] - metrics_no_filter['sharpe_ratio']
        }
    }
    
    # Remove equity curves before saving (too large for JSON)
    comparison_metrics['no_filter'].pop('equity_curve', None)
    comparison_metrics['with_h1_filter'].pop('equity_curve', None)
    
    with open('results/metrics/backtest_comparison.json', 'w') as f:
        json.dump(comparison_metrics, f, indent=2)
    print('✅ Comparison metrics saved')
    
    print('\n🎉 COMPARISON COMPLETE!')
    print('\nKey Findings:')
    print(f"📉 Trades filtered out: {comparison_metrics['improvements']['trade_reduction']}")
    print(f"📈 Win rate change: {comparison_metrics['improvements']['win_rate_change']:+.2f}%")
    print(f"💰 Net profit change: ${comparison_metrics['improvements']['net_profit_change']:+,.2f}")
    print(f"📊 Profit factor change: {comparison_metrics['improvements']['profit_factor_change']:+.2f}")

else:
    print('\n⚠️  Could not complete comparison - insufficient data')

print('\n✅ All analysis complete!')
