# Goldmine Strategy ML Implementation - Complete Project Plan

## Executive Summary

This document outlines the complete pipeline for building a machine learning model that replicates the **Pure Goldmine Contrarian Strategy**. The model will predict ENTRY and EXIT signals based on the strategy's core principle: **trading against retail behavior at RSI extremes without additional filters**.

**Project Status:** ✅ Data Available | 📋 Planning Complete | 🚀 Ready for Implementation

---

## I. Project Objectives

### Primary Goal
Build an ML model that generates trading signals (BUY/SELL) with the same or better performance as the rule-based strategy.

### Success Metrics
1. **Signal Accuracy:** ≥75% precision on entry signals
2. **Strategy Alignment:** ≥80% agreement with rule-based strategy
3. **Profitability:** Positive expectancy per trade in backtesting
4. **Win Rate:** ≥50% (minimum acceptable)
5. **Risk-Reward:** Average win ≥ 1.5x average loss

---

## II. Data Inventory & Analysis

### Available Data (Confirmed)
```
✅ XAUUSDm_M1_202401012305_202607031457.csv  (~59 MB)
✅ XAUUSDm_M3_202401012303_202607031457.csv  (~20 MB)
✅ XAUUSDm_M5_202401012305_202607031500.csv  (~12 MB)
✅ XAUUSDm_H1_202401012300_202607031500.csv  (~1 MB)
```

**Duration:** January 1, 2024 → July 3, 2026 (18 months) ✅ Exceeds minimum requirement
**Symbol:** Gold (XAUUSDm)
**Quality:** To be validated in Notebook 01

### Data Split Strategy
- **Training Set:** Jan 2024 - Dec 2024 (12 months, ~70%)
- **Validation Set:** Jan 2025 - Mar 2025 (3 months, ~15%)
- **Test Set:** Apr 2025 - Jul 2026 (15 months, ~15%)

**Critical:** Chronological split to prevent look-ahead bias

---

## III. Strategy Core Logic Translation

### Rule-Based Strategy (From Theory Doc)

```python
# CONTRARIAN REVERSAL LOGIC
if RSI_M5 crosses_above 35.0:  # Oversold
    → Standard signal: BUY
    → Goldmine signal: SELL (reverse)
    
if RSI_M5 crosses_below 65.0:  # Overbought
    → Standard signal: SELL
    → Goldmine signal: BUY (reverse)

# NO FILTERS (Pure Strategy)
# No trend validation
# No volume confirmation
# No multi-timeframe consensus
# Immediate execution on RSI cross
```

### ML Model Translation Task

The model must learn to:
1. **Detect RSI extremes** (not just calculate them)
2. **Identify trap formations** (retail liquidity accumulation)
3. **Predict optimal entry timing** (RSI cross vs. RSI in zone)
4. **Estimate probability of success** (confidence scoring)

**Key Insight:** The ML model can potentially enhance the rule-based approach by learning:
- Which RSI extremes are high vs. low probability
- Market conditions where reversals are more likely
- Subtle patterns invisible to rule-based systems

---

## IV. Feature Engineering Blueprint

### Category 1: Core RSI Features (Strategy-Aligned)

```python
# M5 Timeframe (Primary)
- rsi_m5_value           # Current RSI(14) value
- rsi_m5_crossed_above_35  # Binary: just crossed oversold threshold
- rsi_m5_crossed_below_65  # Binary: just crossed overbought threshold
- rsi_m5_in_oversold_zone  # Binary: RSI < 35
- rsi_m5_in_overbought_zone  # Binary: RSI > 65
- rsi_m5_momentum        # Change in RSI over last N periods
- rsi_m5_extreme_duration  # How long RSI stayed in extreme zone

# M1 Timeframe (Micro-trend)
- rsi_m1_value
- rsi_m1_in_oversold
- rsi_m1_in_overbought

# M3 Timeframe (Intermediate)
- rsi_m3_value
- rsi_m3_in_oversold
- rsi_m3_in_overbought

# H1 Timeframe (Macro context - informational only)
- rsi_h1_value
- rsi_h1_trend           # Directional bias
```

### Category 2: Price Action Features
```python
- close_m5               # Current close price
- open_m5
- high_m5
- low_m5
- price_change_pct       # % change in last N candles
- candle_body_size       # |close - open|
- candle_wick_ratio      # Upper/lower wick proportions
- price_volatility       # Rolling standard deviation
```

### Category 3: Volume Features
```python
- volume_m5              # Current volume
- volume_ma_ratio        # Volume vs moving average
- volume_surge           # Abnormal volume spike
- cumulative_volume      # Volume accumulation
```

### Category 4: Trend & Momentum

```python
- adx_m5                 # Average Directional Index
- ema_20_m5              # Short-term trend
- ema_50_m5              # Medium-term trend
- price_above_ema        # Position relative to EMAs
- macd_m5                # MACD histogram
- macd_signal            # MACD signal line
```

### Category 5: Temporal Features
```python
- hour_of_day            # 0-23
- day_of_week            # 0-6
- trading_session        # Asian/European/US
- is_high_volatility_hour  # News events typical
```

### Category 6: Multi-Timeframe Alignment
```python
- mtf_rsi_alignment      # All timeframes agree on extreme
- mtf_trend_agreement    # Trend consistency across TFs
- m1_m3_m5_divergence    # RSI divergence detection
```

### Category 7: Trap Detection Features (Advanced)
```python
- false_breakout_indicator  # Price makes new high but RSI doesn't
- liquidity_trap_score   # Proprietary score for trap detection
- retail_sentiment       # Derived from RSI extremes + volume
- smart_money_flow       # Large volume moves vs price action
```

**Total Features:** ~50-80 engineered features

---

## V. Label Generation Strategy

### Binary Classification Approach (Primary)

**Target Variable:** `signal`

```python
# Label generation based on forward-looking outcomes
def generate_labels(df):
    """
    For each candle, look forward and determine outcome
    """
    labels = []
    
    for i in range(len(df)):
        current_price = df.loc[i, 'close']
        
        # Look forward 100-200 pips (adjustable)
        future_high = df.loc[i:i+40, 'high'].max()  # Next 40 candles (200 min)
        future_low = df.loc[i:i+40, 'low'].min()
        
        move_up = future_high - current_price
        move_down = current_price - future_low
        
        # Label logic
        if move_up > 100_pips and move_up > move_down * 1.5:
            label = 1  # BUY signal (profitable long)
        elif move_down > 100_pips and move_down > move_up * 1.5:
            label = 0  # SELL signal (profitable short)
        else:
            label = -1  # NO_TRADE (unclear/choppy)
        
        labels.append(label)
    
    return labels
```

**Alternative: Three-Class Classification**
- `0`: SELL signal
- `1`: NO_TRADE / NEUTRAL
- `2`: BUY signal

### Exit Signal Labels (Secondary Model)

For trades that were entered, predict optimal exit:
```python
exit_reason = {
    'TP_HIT': 0,      # Take profit (100 pips)
    'SL_HIT': 1,      # Stop loss (200 pips)
    'TIME_EXIT': 2,   # Max time in trade
    'RSI_REVERSE': 3  # RSI reverses back to neutral
}
```

---

## VI. Model Architecture & Selection

### Candidate Models (Ranked by Priority)

#### 1. **XGBoost Classifier** ⭐ PRIMARY
**Why:**
- Best performance on tabular data
- Handles non-linear interactions
- Built-in feature importance
- Fast inference (<1ms)

**Configuration:**

```python
xgb_params = {
    'objective': 'binary:logistic',  # or 'multi:softmax'
    'eval_metric': 'auc',
    'max_depth': 6,
    'learning_rate': 0.01,
    'n_estimators': 500,
    'early_stopping_rounds': 50,
    'scale_pos_weight': 1.0,  # Adjust for class imbalance
}
```

#### 2. **LightGBM** ⭐ SECONDARY
**Why:**
- Faster training than XGBoost
- Lower memory usage
- Good for large datasets

#### 3. **Random Forest** (Baseline)
**Why:**
- Robust baseline
- Good for feature importance
- Less prone to overfitting

#### 4. **LSTM (Deep Learning)** 🔬 EXPERIMENTAL
**Why:**
- Captures temporal patterns
- Sequence modeling
- Can learn complex interactions

**Architecture:**
```python
model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(lookback, n_features)),
    Dropout(0.2),
    LSTM(64, return_sequences=False),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(3, activation='softmax')  # 3 classes
])
```

#### 5. **Ensemble Stacking** 🎯 FINAL PRODUCTION
**Strategy:**
- Level 1: XGBoost + LightGBM + Random Forest
- Level 2: Logistic Regression meta-learner
- Combines strengths of multiple models

---

## VII. Training Pipeline

### Step 1: Data Preprocessing
```python
1. Load multi-timeframe data
2. Synchronize timestamps (resample to M5 base)
3. Handle missing values (forward fill, interpolation)
4. Remove outliers (3-sigma rule)
5. Validate OHLC relationships
```

### Step 2: Feature Engineering

```python
1. Calculate all technical indicators
2. Create temporal features
3. Generate multi-timeframe features
4. Create lag features (t-1, t-2, t-3)
5. Normalize/standardize features
```

### Step 3: Label Generation
```python
1. Apply forward-looking outcome analysis
2. Label each candle: BUY/SELL/NO_TRADE
3. Handle class imbalance (SMOTE, class weights)
4. Validate label distribution
```

### Step 4: Feature Selection
```python
1. Remove highly correlated features (>0.95)
2. Remove low-variance features
3. Use feature importance from tree models
4. Select top 30-50 features
```

### Step 5: Model Training
```python
1. Train baseline models
2. Hyperparameter optimization (Optuna)
3. Cross-validation (TimeSeriesSplit, 5 folds)
4. Track metrics: accuracy, precision, recall, F1, AUC
5. Save best model checkpoints
```

### Step 6: Model Evaluation
```python
1. Test on holdout set (Apr 2025 - Jul 2026)
2. Generate confusion matrix
3. Calculate trading-specific metrics
4. Compare with rule-based strategy
5. Analyze misclassifications
```

---

## VIII. Evaluation Metrics

### Classification Metrics
```python
- Accuracy: Overall correctness
- Precision: % of predicted trades that are correct
- Recall: % of actual opportunities captured
- F1-Score: Harmonic mean of precision & recall
- ROC-AUC: Model's discrimination ability
- Confusion Matrix: Detailed error analysis
```

### Trading Metrics (Backtesting)

```python
- Win Rate: % of profitable trades
- Profit Factor: Gross profit / Gross loss
- Sharpe Ratio: Risk-adjusted returns
- Max Drawdown: Largest equity decline
- Average Win/Loss: Mean profit per winning/losing trade
- Expectancy: (Win% × AvgWin) - (Loss% × AvgLoss)
- Total Trades: Number of signals generated
- Risk-Reward Ratio: AvgWin / AvgLoss
```

### Strategy Alignment Metrics
```python
- Signal Agreement Rate: % ML signals matching rule-based
- False Positive Rate: Bad trades ML took
- False Negative Rate: Good trades ML missed
- Profit Improvement: ML profit vs rule-based profit
```

---

## IX. Implementation Roadmap

### Phase 1: Foundation (Week 1) ✅ IN PROGRESS
**Notebook:** `01_data_exploration.ipynb`

**Tasks:**
- [ ] Load all 4 timeframes (M1, M3, M5, H1)
- [ ] Validate data quality (gaps, outliers, duplicates)
- [ ] Visualize price distributions
- [ ] Check data alignment across timeframes
- [ ] Generate data quality report
- [ ] Save cleaned data to `data/processed/`

**Deliverable:** Clean, validated multi-timeframe dataset

---

### Phase 2: Feature Engineering (Week 1-2)
**Notebook:** `02_feature_engineering.ipynb`

**Tasks:**
- [ ] Implement RSI calculation (all timeframes)
- [ ] Create RSI cross detection features
- [ ] Calculate price action features
- [ ] Generate volume features
- [ ] Add temporal features (hour, day, session)
- [ ] Create multi-timeframe alignment features
- [ ] Normalize/standardize features
- [ ] Feature correlation analysis
- [ ] Save feature matrix to `data/features/`

**Deliverable:** Feature-engineered dataset ready for modeling

---

### Phase 3: Label Generation & EDA (Week 2)
**Notebook:** `02_feature_engineering.ipynb` (continued)

**Tasks:**

- [ ] Generate forward-looking labels (BUY/SELL/NO_TRADE)
- [ ] Analyze label distribution
- [ ] Visualize feature-label relationships
- [ ] Identify most predictive features
- [ ] Handle class imbalance
- [ ] Split data: Train/Val/Test (chronological)

**Deliverable:** Labeled dataset with train/val/test splits

---

### Phase 4: Baseline Model Training (Week 2-3)
**Notebook:** `03_model_training.ipynb`

**Tasks:**
- [ ] Train Random Forest (baseline)
- [ ] Train XGBoost (primary model)
- [ ] Train LightGBM (secondary model)
- [ ] Implement time-series cross-validation
- [ ] Track training metrics (loss, accuracy)
- [ ] Compare baseline models
- [ ] Select best baseline
- [ ] Save model checkpoints

**Deliverable:** Trained baseline models

---

### Phase 5: Hyperparameter Optimization (Week 3)
**Notebook:** `03_model_training.ipynb` (continued)

**Tasks:**
- [ ] Define hyperparameter search space
- [ ] Run Optuna optimization (100+ trials)
- [ ] Validate on validation set
- [ ] Select optimal hyperparameters
- [ ] Retrain best model on train+val
- [ ] Final model evaluation on test set
- [ ] Save final production model

**Deliverable:** Optimized production model

---

### Phase 6: Model Evaluation (Week 3-4)
**Notebook:** `04_model_evaluation.ipynb`

**Tasks:**
- [ ] Load best model
- [ ] Predict on test set
- [ ] Generate classification report
- [ ] Confusion matrix analysis
- [ ] Feature importance visualization
- [ ] Error analysis (misclassified samples)
- [ ] SHAP values for interpretability
- [ ] Compare with rule-based strategy

**Deliverable:** Comprehensive model evaluation report

---

### Phase 7: Backtesting & Trading Simulation (Week 4)
**Notebook:** `05_backtesting.ipynb`

**Tasks:**

- [ ] Implement trading simulator
- [ ] Apply 100-pip TP, 200-pip SL rules
- [ ] Simulate trades on test set
- [ ] Calculate win rate, profit factor, Sharpe ratio
- [ ] Generate equity curve
- [ ] Analyze drawdowns
- [ ] Compare ML vs rule-based performance
- [ ] Sensitivity analysis (TP/SL variations)
- [ ] Final performance report

**Deliverable:** Backtest results with trading metrics

---

### Phase 8: Documentation & Deployment (Week 5)
**Tasks:**
- [ ] Document model architecture
- [ ] Create model inference script
- [ ] Build prediction API (optional)
- [ ] Write deployment guide
- [ ] Create monitoring dashboard
- [ ] Final presentation/report

**Deliverable:** Production-ready model with documentation

---

## X. Technical Stack

### Python Libraries
```python
# Data manipulation
pandas >= 2.0.0
numpy >= 1.24.0

# Visualization
matplotlib >= 3.7.0
seaborn >= 0.12.0
plotly >= 5.14.0

# Technical indicators
ta >= 0.11.0  # Technical Analysis library
pandas_ta >= 0.3.14b

# Machine Learning
scikit-learn >= 1.3.0
xgboost >= 2.0.0
lightgbm >= 4.0.0
catboost >= 1.2.0  # Optional

# Deep Learning (optional)
tensorflow >= 2.13.0
keras >= 2.13.0

# Hyperparameter optimization
optuna >= 3.3.0

# Model interpretation
shap >= 0.42.0

# Backtesting
vectorbt >= 0.25.0  # Optional, advanced backtesting

# Utilities
pyyaml >= 6.0
python-dotenv >= 1.0.0
tqdm >= 4.65.0
```

### Development Environment

```
Python: 3.10 or 3.11 (recommended)
Jupyter: Lab or Notebook
IDE: VS Code, PyCharm, or Jupyter Lab
Version Control: Git
```

---

## XI. Risk Management & Validation

### Preventing Overfitting
1. **Time-Series Split:** No shuffling, chronological only
2. **Early Stopping:** Stop training when val loss increases
3. **Regularization:** L1/L2, dropout in neural nets
4. **Feature Selection:** Remove redundant features
5. **Cross-Validation:** Multiple train/val splits

### Preventing Look-Ahead Bias
1. **No Future Data:** Labels only use forward-looking windows
2. **Indicator Lag:** All indicators calculated with historical data only
3. **Strict Temporal Order:** Train always before val/test
4. **No Data Leakage:** Scaling fitted only on train set

### Model Validation Checklist
- [ ] Model performs well on unseen test data
- [ ] No significant performance drop from val to test
- [ ] Feature importance makes logical sense
- [ ] Model predictions explainable (SHAP)
- [ ] Consistent performance across market regimes
- [ ] Backtesting results align with strategy theory

---

## XII. What I Need From You

### ✅ Already Provided
1. ✅ Historical data (M1, M3, M5, H1) - 18 months of XAUUSD
2. ✅ Strategy theory document
3. ✅ Project structure

### 📋 Optional but Valuable
1. **Historical Trade Logs** (if available)
   - CSV with: timestamp, direction, entry_price, exit_price, profit
   - This provides ground truth for model validation
   
2. **Strategy Parameters Clarification**
   - Confirm: TP = 100 pips, SL = 200 pips?
   - Confirm: No filters, pure RSI reversals?
   - Any hidden conditions not in docs?

3. **Preferences**
   - Target deployment: Standalone predictions or MT5 integration?
   - Real-time prediction requirements?
   - Model interpretability vs pure performance?

---

## XIII. Expected Outcomes

### Minimum Viable Model (MVP)

- XGBoost classifier with 75%+ accuracy
- Positive backtesting results
- Clear feature importance insights
- Reproducible training pipeline

### Stretch Goals
- Ensemble model with 80%+ accuracy
- LSTM model for sequence modeling
- Real-time prediction API
- Live trading connector (paper trading)
- Automated retraining pipeline

---

## XIV. Project Timeline

**Total Duration:** 4-5 weeks (assuming part-time work)

```
Week 1: Data exploration + Feature engineering
Week 2: Label generation + Baseline models
Week 3: Optimization + Advanced models
Week 4: Evaluation + Backtesting
Week 5: Documentation + Deployment
```

**Daily Commitment:** 2-3 hours recommended

---

## XV. Next Steps (Immediate Actions)

### Step 1: Environment Setup ⚡ DO FIRST
```bash
# Verify Python version
python --version  # Should be 3.10 or 3.11

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter lab
```

### Step 2: Start with Notebook 01 📊
Open: `notebooks/01_data_exploration.ipynb`

**Tasks for first session:**
1. Load all 4 CSV files
2. Check data shapes and dtypes
3. Verify timestamp alignment
4. Plot sample price charts
5. Identify any data quality issues

---

## XVI. Success Criteria Summary

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Accuracy | 70% | 75% | 80%+ |
| Precision | 65% | 70% | 75%+ |
| Win Rate | 45% | 50% | 55%+ |
| Profit Factor | 1.2 | 1.5 | 2.0+ |
| Sharpe Ratio | 0.5 | 1.0 | 1.5+ |
| Max Drawdown | <30% | <20% | <15% |

---

## XVII. Contact & Support

**Questions During Development:**

- Technical issues: Check notebook error messages
- Strategy questions: Refer to `docs/Goldmine_Strategy_Theory.md`
- Data questions: Refer to `docs/Data_Requirements.md`

---

## XVIII. Appendix: Key Formulas

### RSI Calculation
```python
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

### Label Generation Logic
```python
def generate_label(current_price, future_high, future_low, tp_pips=100, sl_pips=200):
    pip_value = 0.01  # For XAUUSD
    
    move_up = (future_high - current_price) / pip_value
    move_down = (current_price - future_low) / pip_value
    
    if move_up >= tp_pips and move_down < sl_pips:
        return 1  # BUY signal
    elif move_down >= tp_pips and move_up < sl_pips:
        return 0  # SELL signal
    else:
        return -1  # NO_TRADE
```

---

## XIX. Glossary

- **RSI:** Relative Strength Index (momentum oscillator)
- **TP:** Take Profit target (100 pips)
- **SL:** Stop Loss level (200 pips)
- **Pip:** Point in Percentage (0.01 for Gold)
- **Contrarian:** Trading against the crowd
- **Liquidity Trap:** Price level where retail traders get trapped
- **Look-Ahead Bias:** Using future data in training (fatal error)
- **Overfitting:** Model memorizes training data, fails on new data
- **Feature Engineering:** Creating predictive variables from raw data
- **Ensemble:** Combining multiple models for better predictions

---

**Document Version:** 1.0  
**Last Updated:** July 4, 2026  
**Status:** Ready for Implementation ✅

---

# 🚀 LET'S BEGIN! Open `notebooks/01_data_exploration.ipynb` to start.
