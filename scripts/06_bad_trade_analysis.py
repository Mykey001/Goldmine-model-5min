"""
Goldmine ML - Script 06: Bad Trade Analysis
Deep analysis of losing trades to identify patterns and optimal filters
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
from pathlib import Path
import os
from datetime import datetime

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
print('✅ Imports complete!')

# ============================================================================
# SET WORKING DIRECTORY
# ============================================================================
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

# ============================================================================
# LOAD DATA
# ============================================================================
print('\n' + '='*60)
print('LOADING DATA FOR ANALYSIS')
print('='*60)

# Load test data
test = pd.read_parquet('data/features/test.parquet')
print(f'✅ Test data loaded: {len(test):,} rows')

# Load H1 data
h1 = pd.read_parquet('data/processed/H1_cleaned.parquet')
print(f'✅ H1 data loaded: {len(h1):,} rows')

# Load model
model = joblib.load('models/final/xgboost_model.pkl')
print(f'✅ Model loaded')

# ============================================================================
# PREPARE DATA WITH ALL INDICATORS
# ============================================================================
print('\n' + '='*60)
print('CALCULATING ADDITIONAL INDICATORS')
print('='*60)

# Calculate H1 EMA and trend
h1['h1_ema_200'] = ta.trend.EMAIndicator(h1['close'], window=200).ema_indicator()
h1['h1_ema_50'] = ta.trend.EMAIndicator(h1['close'], window=50).ema_indicator()
h1['h1_trend'] = np.where(h1['close'] > h1['h1_ema_200'], 1, 0)

# Calculate H1 ADX for trend strength
h1['h1_adx'] = ta.trend.ADXIndicator(h1['high'], h1['low'], h1['close'], window=14).adx()

# Keep only necessary H1 columns
h1_data = h1[['timestamp', 'h1_trend', 'h1_ema_200', 'h1_ema_50', 'h1_adx', 'close']].copy()
h1_data.rename(columns={'close': 'h1_close'}, inplace=True)

# Merge with test data
test = test.sort_values('timestamp')
h1_data = h1_data.sort_values('timestamp')
test = pd.merge_asof(test, h1_data, on='timestamp', direction='backward')

print('✅ H1 data merged with M5 data')

# ============================================================================
# GENERATE PREDICTIONS
# ============================================================================
print('\n' + '='*60)
print('GENERATING PREDICTIONS')
print('='*60)

exclude_cols = ['timestamp', 'timeframe', 'label', 'open', 'high', 'low', 'close', 
               'date', 'time', 'h1_trend', 'h1_ema_200', 'h1_ema_50', 'h1_adx', 'h1_close']
feature_cols = [c for c in test.columns if c not in exclude_cols]

X_test = test[feature_cols]
test['prediction'] = model.predict(X_test)
test['confidence'] = np.max(model.predict_proba(X_test), axis=1)

# Get prediction probabilities for both classes
proba = model.predict_proba(X_test)
test['prob_sell'] = proba[:, 0]
test['prob_buy'] = proba[:, 1]

print('✅ Predictions generated')

# ============================================================================
# SIMULATE TRADES AND TRACK OUTCOMES
# ============================================================================
print('\n' + '='*60)
print('SIMULATING TRADES AND ANALYZING OUTCOMES')
print('='*60)

# Trading parameters
TP_PIPS = 100
SL_PIPS = 50
PIP_VALUE = 0.01
MIN_CONFIDENCE = 0.5

# Generate signals
test['signal'] = test['prediction'].where(test['confidence'] >= MIN_CONFIDENCE, -1)

# Simulate trades with detailed tracking
trades = []
active_trade = None

for idx in range(len(test)):
    row = test.iloc[idx]
    
    # Check active trade for TP/SL
    if active_trade is not None:
        if active_trade['direction'] == 'BUY':
            if row['high'] >= active_trade['tp']:
                active_trade['exit_price'] = active_trade['tp']
                active_trade['exit_time'] = row['timestamp']
                active_trade['exit_reason'] = 'TP'
                active_trade['outcome'] = 'WIN'
                active_trade['profit'] = 10.0  # $10 per TP
                trades.append(active_trade)
                active_trade = None
                continue
            elif row['low'] <= active_trade['sl']:
                active_trade['exit_price'] = active_trade['sl']
                active_trade['exit_time'] = row['timestamp']
                active_trade['exit_reason'] = 'SL'
                active_trade['outcome'] = 'LOSS'
                active_trade['profit'] = -5.0  # $5 per SL
                trades.append(active_trade)
                active_trade = None
                continue
        
        elif active_trade['direction'] == 'SELL':
            if row['low'] <= active_trade['tp']:
                active_trade['exit_price'] = active_trade['tp']
                active_trade['exit_time'] = row['timestamp']
                active_trade['exit_reason'] = 'TP'
                active_trade['outcome'] = 'WIN'
                active_trade['profit'] = 10.0
                trades.append(active_trade)
                active_trade = None
                continue
            elif row['high'] >= active_trade['sl']:
                active_trade['exit_price'] = active_trade['sl']
                active_trade['exit_time'] = row['timestamp']
                active_trade['exit_reason'] = 'SL'
                active_trade['outcome'] = 'LOSS'
                active_trade['profit'] = -5.0
                trades.append(active_trade)
                active_trade = None
                continue
    
    # Open new trade if signal present
    if active_trade is None and row['signal'] in [0, 1]:
        entry_price = row['close']
        
        # Collect entry context
        trade_context = {
            'direction': 'BUY' if row['signal'] == 1 else 'SELL',
            'entry_time': row['timestamp'],
            'entry_price': entry_price,
            'confidence': row['confidence'],
            'prob_buy': row['prob_buy'],
            'prob_sell': row['prob_sell'],
            # M5 indicators
            'rsi': row['rsi'],
            'adx': row['adx'],
            'macd': row['macd'],
            'macd_diff': row['macd_diff'],
            'ema_distance': row['ema_distance'],
            'volatility_10': row['volatility_10'],
            'momentum_5': row['momentum_5'],
            'hour': row['hour'],
            'day_of_week': row['day_of_week'],
            # H1 context
            'h1_trend': row['h1_trend'],
            'h1_adx': row['h1_adx'],
            'aligned_with_h1': (row['signal'] == 1 and row['h1_trend'] == 1) or 
                               (row['signal'] == 0 and row['h1_trend'] == 0),
            # Volume indicators
            'volume_ratio': row.get('volume_ratio', 1.0),
        }
        
        if row['signal'] == 1:  # BUY
            trade_context['tp'] = entry_price + (TP_PIPS * PIP_VALUE)
            trade_context['sl'] = entry_price - (SL_PIPS * PIP_VALUE)
        else:  # SELL
            trade_context['tp'] = entry_price - (TP_PIPS * PIP_VALUE)
            trade_context['sl'] = entry_price + (SL_PIPS * PIP_VALUE)
        
        active_trade = trade_context

trades_df = pd.DataFrame(trades)
print(f'\n✅ Simulated {len(trades_df):,} trades')
print(f'Winning trades: {len(trades_df[trades_df["outcome"]=="WIN"]):,}')
print(f'Losing trades: {len(trades_df[trades_df["outcome"]=="LOSS"]):,}')

# ============================================================================
# ANALYZE LOSING TRADES
# ============================================================================
print('\n' + '='*60)
print('ANALYZING LOSING TRADES')
print('='*60)

winning_trades = trades_df[trades_df['outcome'] == 'WIN']
losing_trades = trades_df[trades_df['outcome'] == 'LOSS']

print(f'\n📊 BASIC STATISTICS:')
print(f'Total Trades: {len(trades_df):,}')
print(f'Winners: {len(winning_trades):,} ({len(winning_trades)/len(trades_df)*100:.2f}%)')
print(f'Losers: {len(losing_trades):,} ({len(losing_trades)/len(trades_df)*100:.2f}%)')

# ============================================================================
# PATTERN ANALYSIS
# ============================================================================
print('\n' + '='*60)
print('IDENTIFYING LOSING TRADE PATTERNS')
print('='*60)

def analyze_pattern(df, column, name):
    """Analyze a specific pattern in losing vs winning trades"""
    if column not in df.columns:
        return
    
    losing_mean = losing_trades[column].mean()
    winning_mean = winning_trades[column].mean()
    difference = losing_mean - winning_mean
    
    print(f'\n{name}:')
    print(f'  Losing trades: {losing_mean:.2f}')
    print(f'  Winning trades: {winning_mean:.2f}')
    print(f'  Difference: {difference:.2f}')
    
    return {'metric': name, 'losing': losing_mean, 'winning': winning_mean, 'diff': difference}

patterns = []

# Confidence analysis
patterns.append(analyze_pattern(trades_df, 'confidence', 'Model Confidence'))

# RSI analysis
patterns.append(analyze_pattern(trades_df, 'rsi', 'RSI'))

# ADX (trend strength)
patterns.append(analyze_pattern(trades_df, 'adx', 'ADX (M5)'))
patterns.append(analyze_pattern(trades_df, 'h1_adx', 'ADX (H1)'))

# MACD
patterns.append(analyze_pattern(trades_df, 'macd_diff', 'MACD Diff'))

# Volatility
patterns.append(analyze_pattern(trades_df, 'volatility_10', 'Volatility'))

# Momentum
patterns.append(analyze_pattern(trades_df, 'momentum_5', 'Momentum'))

# EMA distance
patterns.append(analyze_pattern(trades_df, 'ema_distance', 'EMA Distance'))

# Volume
patterns.append(analyze_pattern(trades_df, 'volume_ratio', 'Volume Ratio'))

# ============================================================================
# H1 TREND ALIGNMENT ANALYSIS
# ============================================================================
print('\n' + '='*60)
print('H1 TREND ALIGNMENT ANALYSIS')
print('='*60)

aligned_trades = trades_df[trades_df['aligned_with_h1'] == True]
counter_trades = trades_df[trades_df['aligned_with_h1'] == False]

print(f'\nAligned with H1 Trend:')
print(f'  Total: {len(aligned_trades):,}')
print(f'  Winners: {len(aligned_trades[aligned_trades["outcome"]=="WIN"]):,}')
print(f'  Win Rate: {len(aligned_trades[aligned_trades["outcome"]=="WIN"])/len(aligned_trades)*100:.2f}%')

print(f'\nCounter H1 Trend:')
print(f'  Total: {len(counter_trades):,}')
print(f'  Winners: {len(counter_trades[counter_trades["outcome"]=="WIN"]):,}')
print(f'  Win Rate: {len(counter_trades[counter_trades["outcome"]=="WIN"])/len(counter_trades)*100:.2f}%')

# ============================================================================
# TIME-BASED ANALYSIS
# ============================================================================
print('\n' + '='*60)
print('TIME-BASED ANALYSIS')
print('='*60)

# Hour analysis
hour_analysis = trades_df.groupby('hour').agg({
    'outcome': lambda x: (x == 'WIN').sum() / len(x) * 100 if len(x) > 0 else 0,
    'profit': 'sum'
}).round(2)
hour_analysis.columns = ['Win_Rate_%', 'Total_Profit']
hour_analysis['Trade_Count'] = trades_df.groupby('hour').size()

print('\n📊 Win Rate by Hour:')
worst_hours = hour_analysis.nsmallest(5, 'Win_Rate_%')
print('Worst performing hours:')
print(worst_hours)

# Day of week analysis
dow_analysis = trades_df.groupby('day_of_week').agg({
    'outcome': lambda x: (x == 'WIN').sum() / len(x) * 100 if len(x) > 0 else 0,
    'profit': 'sum'
}).round(2)
dow_analysis.columns = ['Win_Rate_%', 'Total_Profit']
dow_analysis['Trade_Count'] = trades_df.groupby('day_of_week').size()

print('\n📊 Win Rate by Day of Week:')
print(dow_analysis)

# ============================================================================
# CONFIDENCE THRESHOLD ANALYSIS
# ============================================================================
print('\n' + '='*60)
print('CONFIDENCE THRESHOLD ANALYSIS')
print('='*60)

confidence_thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
threshold_results = []

for threshold in confidence_thresholds:
    filtered = trades_df[trades_df['confidence'] >= threshold]
    if len(filtered) > 0:
        win_rate = len(filtered[filtered['outcome'] == 'WIN']) / len(filtered) * 100
        total_profit = filtered['profit'].sum()
        threshold_results.append({
            'threshold': threshold,
            'trade_count': len(filtered),
            'win_rate': win_rate,
            'total_profit': total_profit
        })

threshold_df = pd.DataFrame(threshold_results)
print('\n📊 Performance by Confidence Threshold:')
print(threshold_df.to_string(index=False))

# ============================================================================
# COMBINED FILTER ANALYSIS
# ============================================================================
print('\n' + '='*60)
print('TESTING COMBINED FILTER STRATEGIES')
print('='*60)

filter_strategies = []

# Strategy 1: H1 Trend Filter Only
strategy1 = trades_df[trades_df['aligned_with_h1'] == True]
filter_strategies.append({
    'name': 'H1 Trend Filter Only',
    'trades': len(strategy1),
    'win_rate': len(strategy1[strategy1['outcome']=='WIN'])/len(strategy1)*100 if len(strategy1)>0 else 0,
    'total_profit': strategy1['profit'].sum() if len(strategy1)>0 else 0
})

# Strategy 2: Confidence > 0.60
strategy2 = trades_df[trades_df['confidence'] > 0.60]
filter_strategies.append({
    'name': 'Confidence > 0.60',
    'trades': len(strategy2),
    'win_rate': len(strategy2[strategy2['outcome']=='WIN'])/len(strategy2)*100 if len(strategy2)>0 else 0,
    'total_profit': strategy2['profit'].sum() if len(strategy2)>0 else 0
})

# Strategy 3: H1 Aligned + Confidence > 0.55
strategy3 = trades_df[(trades_df['aligned_with_h1'] == True) & (trades_df['confidence'] > 0.55)]
filter_strategies.append({
    'name': 'H1 Aligned + Conf > 0.55',
    'trades': len(strategy3),
    'win_rate': len(strategy3[strategy3['outcome']=='WIN'])/len(strategy3)*100 if len(strategy3)>0 else 0,
    'total_profit': strategy3['profit'].sum() if len(strategy3)>0 else 0
})

# Strategy 4: H1 Aligned + ADX > 25
strategy4 = trades_df[(trades_df['aligned_with_h1'] == True) & (trades_df['h1_adx'] > 25)]
filter_strategies.append({
    'name': 'H1 Aligned + H1 ADX > 25',
    'trades': len(strategy4),
    'win_rate': len(strategy4[strategy4['outcome']=='WIN'])/len(strategy4)*100 if len(strategy4)>0 else 0,
    'total_profit': strategy4['profit'].sum() if len(strategy4)>0 else 0
})

# Strategy 5: H1 Aligned + Strong Momentum
strategy5 = trades_df[(trades_df['aligned_with_h1'] == True) & (abs(trades_df['momentum_5']) > 0.1)]
filter_strategies.append({
    'name': 'H1 Aligned + Strong Momentum',
    'trades': len(strategy5),
    'win_rate': len(strategy5[strategy5['outcome']=='WIN'])/len(strategy5)*100 if len(strategy5)>0 else 0,
    'total_profit': strategy5['profit'].sum() if len(strategy5)>0 else 0
})

# Strategy 6: Multi-factor filter
strategy6 = trades_df[
    (trades_df['aligned_with_h1'] == True) &
    (trades_df['confidence'] > 0.55) &
    (trades_df['h1_adx'] > 20)
]
filter_strategies.append({
    'name': 'Multi: H1+Conf+ADX',
    'trades': len(strategy6),
    'win_rate': len(strategy6[strategy6['outcome']=='WIN'])/len(strategy6)*100 if len(strategy6)>0 else 0,
    'total_profit': strategy6['profit'].sum() if len(strategy6)>0 else 0
})

# Strategy 7: Avoid weak trends
strategy7 = trades_df[(trades_df['adx'] > 20) & (trades_df['h1_adx'] > 20)]
filter_strategies.append({
    'name': 'ADX M5>20 & H1>20',
    'trades': len(strategy7),
    'win_rate': len(strategy7[strategy7['outcome']=='WIN'])/len(strategy7)*100 if len(strategy7)>0 else 0,
    'total_profit': strategy7['profit'].sum() if len(strategy7)>0 else 0
})

# Baseline (no filter)
filter_strategies.append({
    'name': 'BASELINE (No Filter)',
    'trades': len(trades_df),
    'win_rate': len(trades_df[trades_df['outcome']=='WIN'])/len(trades_df)*100,
    'total_profit': trades_df['profit'].sum()
})

strategies_df = pd.DataFrame(filter_strategies)
strategies_df['profit_per_trade'] = strategies_df['total_profit'] / strategies_df['trades']
strategies_df = strategies_df.sort_values('total_profit', ascending=False)

print('\n📊 FILTER STRATEGY COMPARISON:')
print(strategies_df.to_string(index=False))

# ============================================================================
# SAVE RESULTS
# ============================================================================
print('\n' + '='*60)
print('SAVING ANALYSIS RESULTS')
print('='*60)

os.makedirs('results/analysis', exist_ok=True)

# Save trade data with outcomes
trades_df.to_csv('results/analysis/trades_with_outcomes.csv', index=False)
print('✅ Trade outcomes saved')

# Save filter strategies
strategies_df.to_csv('results/analysis/filter_strategies.csv', index=False)
print('✅ Filter strategies saved')

# Save hour analysis
hour_analysis.to_csv('results/analysis/hour_analysis.csv')
print('✅ Hour analysis saved')

# Save threshold analysis
threshold_df.to_csv('results/analysis/confidence_threshold_analysis.csv', index=False)
print('✅ Confidence analysis saved')

# ============================================================================
# VISUALIZATIONS
# ============================================================================
print('\n' + '='*60)
print('GENERATING VISUALIZATIONS')
print('='*60)

# 1. Win Rate by Confidence
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

ax = axes[0, 0]
ax.plot(threshold_df['threshold'], threshold_df['win_rate'], marker='o', linewidth=2)
ax.set_title('Win Rate vs Confidence Threshold', fontweight='bold', fontsize=12)
ax.set_xlabel('Confidence Threshold')
ax.set_ylabel('Win Rate (%)')
ax.grid(True, alpha=0.3)
ax.axhline(y=strategies_df[strategies_df['name']=='BASELINE (No Filter)']['win_rate'].values[0], 
           color='r', linestyle='--', label='Baseline')
ax.legend()

# 2. Total Profit by Strategy
ax = axes[0, 1]
strategies_sorted = strategies_df.sort_values('total_profit')
colors = ['green' if x > 0 else 'red' for x in strategies_sorted['total_profit']]
ax.barh(strategies_sorted['name'], strategies_sorted['total_profit'], color=colors, alpha=0.7)
ax.set_title('Total Profit by Filter Strategy', fontweight='bold', fontsize=12)
ax.set_xlabel('Total Profit ($)')
ax.grid(True, alpha=0.3, axis='x')

# 3. Win Rate by Hour
ax = axes[1, 0]
hour_analysis_sorted = hour_analysis.sort_values('Win_Rate_%')
ax.bar(hour_analysis_sorted.index, hour_analysis_sorted['Win_Rate_%'], alpha=0.7)
ax.set_title('Win Rate by Hour of Day', fontweight='bold', fontsize=12)
ax.set_xlabel('Hour (UTC)')
ax.set_ylabel('Win Rate (%)')
ax.axhline(y=strategies_df[strategies_df['name']=='BASELINE (No Filter)']['win_rate'].values[0],
           color='r', linestyle='--', label='Baseline')
ax.grid(True, alpha=0.3)
ax.legend()

# 4. Trade Count vs Win Rate for strategies
ax = axes[1, 1]
baseline_profit = strategies_df[strategies_df['name']=='BASELINE (No Filter)']['total_profit'].values[0]
strategies_df['profit_ratio'] = strategies_df['total_profit'] / baseline_profit
scatter = ax.scatter(strategies_df['trades'], strategies_df['win_rate'], 
                    s=strategies_df['profit_ratio']*500, alpha=0.6, c=strategies_df['total_profit'],
                    cmap='RdYlGn')
for idx, row in strategies_df.iterrows():
    if row['name'] != 'BASELINE (No Filter)':
        ax.annotate(row['name'], (row['trades'], row['win_rate']), 
                   fontsize=8, ha='right')
ax.set_title('Trade Count vs Win Rate (size=profit ratio)', fontweight='bold', fontsize=12)
ax.set_xlabel('Trade Count')
ax.set_ylabel('Win Rate (%)')
ax.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax, label='Total Profit ($)')

plt.tight_layout()
plt.savefig('results/analysis/bad_trade_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print('✅ Analysis visualization saved')

# ============================================================================
# GENERATE RECOMMENDATION
# ============================================================================
print('\n' + '='*60)
print('RECOMMENDATIONS')
print('='*60)

# Find best strategy based on balance of profit and win rate
strategies_df['score'] = (strategies_df['total_profit'] / baseline_profit) * (strategies_df['win_rate'] / 100)
best_strategy = strategies_df.loc[strategies_df['score'].idxmax()]

print(f'\n🎯 RECOMMENDED FILTER STRATEGY:')
print(f'Strategy: {best_strategy["name"]}')
print(f'Trade Count: {best_strategy["trades"]:.0f}')
print(f'Win Rate: {best_strategy["win_rate"]:.2f}%')
print(f'Total Profit: ${best_strategy["total_profit"]:,.2f}')
print(f'Profit vs Baseline: {best_strategy["total_profit"]/baseline_profit*100:.1f}%')
print(f'Score: {best_strategy["score"]:.3f}')

print('\n🎉 ANALYSIS COMPLETE!')
print('Check results/analysis/ folder for detailed outputs')
