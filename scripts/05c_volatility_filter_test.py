"""
Goldmine ML - Script 05C: Volatility Filter Testing
Test different volatility thresholds to find optimal balance
"""

# ============================================================================
# IMPORTS
# ============================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

print('✅ Imports complete!')

# ============================================================================
# SET WORKING DIRECTORY
# ============================================================================
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

# ============================================================================
# LOAD TRADE DATA
# ============================================================================
print('\n' + '='*60)
print('LOADING TRADE OUTCOME DATA')
print('='*60)

trades = pd.read_csv('results/analysis/trades_with_outcomes.csv')
print(f'✅ Loaded {len(trades):,} trades')
print(f'Winners: {len(trades[trades["outcome"]=="WIN"]):,}')
print(f'Losers: {len(trades[trades["outcome"]=="LOSS"]):,}')

# ============================================================================
# TEST VOLATILITY THRESHOLDS
# ============================================================================
print('\n' + '='*60)
print('TESTING VOLATILITY THRESHOLDS')
print('='*60)

volatility_thresholds = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]

results = []
for threshold in volatility_thresholds:
    filtered = trades[trades['volatility_10'] >= threshold]
    
    if len(filtered) > 0:
        win_rate = len(filtered[filtered['outcome'] == 'WIN']) / len(filtered) * 100
        total_profit = filtered['profit'].sum()
        trade_reduction = (1 - len(filtered)/len(trades)) * 100
        
        results.append({
            'threshold': threshold,
            'trades': len(filtered),
            'trade_reduction_%': trade_reduction,
            'win_rate_%': win_rate,
            'total_profit': total_profit,
            'profit_per_trade': total_profit / len(filtered),
            'profit_vs_baseline_%': (total_profit / trades['profit'].sum()) * 100
        })

results_df = pd.DataFrame(results)

print('\n📊 VOLATILITY FILTER RESULTS:')
print(results_df.to_string(index=False))

# Find optimal threshold
baseline_profit = trades['profit'].sum()
results_df['score'] = results_df['win_rate_%'] * (results_df['profit_vs_baseline_%'] / 100)
optimal_idx = results_df['score'].idxmax()
optimal = results_df.loc[optimal_idx]

print('\n🎯 OPTIMAL VOLATILITY THRESHOLD:')
print(f'Threshold: {optimal["threshold"]:.1f}')
print(f'Trades: {optimal["trades"]:.0f} ({100-optimal["trade_reduction_%"]:.1f}% kept)')
print(f'Win Rate: {optimal["win_rate_%"]:.2f}%')
print(f'Total Profit: ${optimal["total_profit"]:,.2f}')
print(f'Profit vs Baseline: {optimal["profit_vs_baseline_%"]:.1f}%')

# ============================================================================
# TEST COMBINED FILTERS
# ============================================================================
print('\n' + '='*60)
print('TESTING COMBINED FILTER STRATEGIES')
print('='*60)

combined_results = []

# Baseline
combined_results.append({
    'strategy': 'Baseline (No Filter)',
    'trades': len(trades),
    'win_rate_%': len(trades[trades['outcome']=='WIN'])/len(trades)*100,
    'total_profit': trades['profit'].sum(),
    'profit_per_trade': trades['profit'].sum() / len(trades)
})

# Volatility only (optimal)
vol_filtered = trades[trades['volatility_10'] >= optimal['threshold']]
combined_results.append({
    'strategy': f'Volatility > {optimal["threshold"]:.1f}',
    'trades': len(vol_filtered),
    'win_rate_%': len(vol_filtered[vol_filtered['outcome']=='WIN'])/len(vol_filtered)*100,
    'total_profit': vol_filtered['profit'].sum(),
    'profit_per_trade': vol_filtered['profit'].sum() / len(vol_filtered)
})

# H1 Trend only
h1_filtered = trades[trades['aligned_with_h1'] == True]
combined_results.append({
    'strategy': 'H1 Trend Aligned',
    'trades': len(h1_filtered),
    'win_rate_%': len(h1_filtered[h1_filtered['outcome']=='WIN'])/len(h1_filtered)*100,
    'total_profit': h1_filtered['profit'].sum(),
    'profit_per_trade': h1_filtered['profit'].sum() / len(h1_filtered)
})

# Volatility + H1 Trend
vol_h1_filtered = trades[(trades['volatility_10'] >= optimal['threshold']) & 
                         (trades['aligned_with_h1'] == True)]
combined_results.append({
    'strategy': f'Volatility > {optimal["threshold"]:.1f} + H1 Trend',
    'trades': len(vol_h1_filtered),
    'win_rate_%': len(vol_h1_filtered[vol_h1_filtered['outcome']=='WIN'])/len(vol_h1_filtered)*100 if len(vol_h1_filtered)>0 else 0,
    'total_profit': vol_h1_filtered['profit'].sum() if len(vol_h1_filtered)>0 else 0,
    'profit_per_trade': vol_h1_filtered['profit'].sum() / len(vol_h1_filtered) if len(vol_h1_filtered)>0 else 0
})

# Volatility + H1 + ADX
vol_h1_adx_filtered = trades[(trades['volatility_10'] >= optimal['threshold']) & 
                              (trades['aligned_with_h1'] == True) &
                              (trades['h1_adx'] > 20)]
combined_results.append({
    'strategy': f'Vol + H1 + ADX>20',
    'trades': len(vol_h1_adx_filtered),
    'win_rate_%': len(vol_h1_adx_filtered[vol_h1_adx_filtered['outcome']=='WIN'])/len(vol_h1_adx_filtered)*100 if len(vol_h1_adx_filtered)>0 else 0,
    'total_profit': vol_h1_adx_filtered['profit'].sum() if len(vol_h1_adx_filtered)>0 else 0,
    'profit_per_trade': vol_h1_adx_filtered['profit'].sum() / len(vol_h1_adx_filtered) if len(vol_h1_adx_filtered)>0 else 0
})

combined_df = pd.DataFrame(combined_results)
combined_df['profit_vs_baseline_%'] = (combined_df['total_profit'] / baseline_profit) * 100

print('\n📊 COMBINED FILTER COMPARISON:')
print(combined_df.to_string(index=False))

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print('\n' + '='*60)
print('GENERATING VISUALIZATIONS')
print('='*60)

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

# 1. Win Rate vs Volatility Threshold
ax = axes[0, 0]
ax.plot(results_df['threshold'], results_df['win_rate_%'], marker='o', linewidth=2, color='green')
ax.axvline(x=optimal['threshold'], color='red', linestyle='--', label=f'Optimal: {optimal["threshold"]:.1f}')
ax.axhline(y=combined_results[0]['win_rate_%'], color='gray', linestyle='--', alpha=0.5, label='Baseline')
ax.set_title('Win Rate vs Volatility Threshold', fontweight='bold', fontsize=12)
ax.set_xlabel('Volatility Threshold')
ax.set_ylabel('Win Rate (%)')
ax.grid(True, alpha=0.3)
ax.legend()

# 2. Total Profit vs Volatility Threshold
ax = axes[0, 1]
ax.plot(results_df['threshold'], results_df['total_profit'], marker='o', linewidth=2, color='blue')
ax.axvline(x=optimal['threshold'], color='red', linestyle='--', label=f'Optimal: {optimal["threshold"]:.1f}')
ax.axhline(y=baseline_profit, color='gray', linestyle='--', alpha=0.5, label='Baseline')
ax.set_title('Total Profit vs Volatility Threshold', fontweight='bold', fontsize=12)
ax.set_xlabel('Volatility Threshold')
ax.set_ylabel('Total Profit ($)')
ax.grid(True, alpha=0.3)
ax.legend()

# 3. Combined Strategy Comparison - Win Rate
ax = axes[1, 0]
strategies = combined_df['strategy']
win_rates = combined_df['win_rate_%']
colors = ['gray' if i == 0 else ('green' if x > combined_results[0]['win_rate_%'] else 'orange') 
          for i, x in enumerate(win_rates)]
bars = ax.barh(strategies, win_rates, color=colors, alpha=0.7)
ax.set_title('Win Rate by Strategy', fontweight='bold', fontsize=12)
ax.set_xlabel('Win Rate (%)')
ax.grid(True, alpha=0.3, axis='x')

# 4. Combined Strategy Comparison - Total Profit
ax = axes[1, 1]
profits = combined_df['total_profit']
colors = ['gray' if i == 0 else ('green' if x > baseline_profit*0.7 else 'orange') 
          for i, x in enumerate(profits)]
bars = ax.barh(strategies, profits, color=colors, alpha=0.7)
ax.set_title('Total Profit by Strategy', fontweight='bold', fontsize=12)
ax.set_xlabel('Total Profit ($)')
ax.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig('results/analysis/volatility_filter_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print('✅ Visualization saved: results/analysis/volatility_filter_analysis.png')

# ============================================================================
# SAVE RESULTS
# ============================================================================
results_df.to_csv('results/analysis/volatility_threshold_test.csv', index=False)
combined_df.to_csv('results/analysis/combined_filter_comparison.csv', index=False)
print('✅ Results saved to CSV files')

# ============================================================================
# GENERATE RECOMMENDATION
# ============================================================================
print('\n' + '='*60)
print('RECOMMENDATION')
print('='*60)

# Find best combined strategy
combined_df['score'] = combined_df['win_rate_%'] * (combined_df['profit_vs_baseline_%'] / 100)
best_combined = combined_df.loc[combined_df['score'].idxmax()]

print(f'\n🎯 RECOMMENDED STRATEGY:')
print(f'Strategy: {best_combined["strategy"]}')
print(f'Trades: {best_combined["trades"]:.0f} ({best_combined["trades"]/len(trades)*100:.1f}% of baseline)')
print(f'Win Rate: {best_combined["win_rate_%"]:.2f}% (+{best_combined["win_rate_%"]-combined_results[0]["win_rate_%"]:.2f}%)')
print(f'Total Profit: ${best_combined["total_profit"]:,.2f} ({best_combined["profit_vs_baseline_%"]:.1f}% of baseline)')
print(f'Profit/Trade: ${best_combined["profit_per_trade"]:.2f}')

print(f'\n📋 IMPLEMENTATION:')
print(f'1. Edit configs/backtest_config.yaml:')
print(f'   trend_filter:')
print(f'     enabled: true')
print(f'     h1_ema_period: 200')
print(f'   advanced_filters:')
print(f'     use_volatility_filter: true')
print(f'     min_volatility: {optimal["threshold"]:.1f}')

print(f'\n2. Run backtest:')
print(f'   python scripts\\05_backtesting.py')

print('\n🎉 ANALYSIS COMPLETE!')
