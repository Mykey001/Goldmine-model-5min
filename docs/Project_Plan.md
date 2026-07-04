# Goldmine ML Strategy - Project Plan & Pipeline

## Project Overview

This project aims to develop a machine learning model that replicates and potentially enhances the Goldmine Contrarian trading strategy through predictive modeling of entry and exit signals.

---

## Project Structure

```
Profitable5min/
│
├── data/                           # Data storage
│   ├── raw/                        # Raw market data from MT5/broker
│   ├── processed/                  # Cleaned and preprocessed data
│   └── features/                   # Engineered features ready for ML
│
├── src/                            # Source code modules
│   ├── data_processing/            # Data loading, cleaning, validation
│   ├── feature_engineering/        # Feature creation and selection
│   ├── models/                     # ML model architectures
│   ├── evaluation/                 # Performance metrics and backtesting
│   └── utils/                      # Helper functions and utilities
│
├── notebooks/                      # Jupyter notebooks for experimentation
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_evaluation.ipynb
│   └── 05_backtesting.ipynb
│
├── models/                         # Saved models
│   ├── checkpoints/                # Training checkpoints
│   └── final/                      # Production-ready models
│
├── results/                        # Output and results
│   ├── metrics/                    # Performance metrics
│   ├── visualizations/             # Charts and plots
│   └── predictions/                # Model predictions
│
├── configs/                        # Configuration files
│
├── docs/                           # Documentation
│   ├── Goldmine_Strategy_Theory.md
│   └── Project_Plan.md (this file)
│
├── SimplifiedGoldmine_v1.mq5      # Original MQL5 strategy
└── requirements.txt                # Python dependencies

```

---

## ML Pipeline Architecture

### Phase 1: Data Collection & Preparation

#### 1.1 Data Requirements

**Required Timeframes:**
- **M1 (1-minute):** For immediate micro-trend analysis
- **M3 (3-minute):** For swing high/low detection
- **M5 (5-minute):** Primary execution timeframe
- **H1 (1-hour):** For macro-trend EMA filter

**Required Data Points per Timeframe:**
- OHLCV (Open, High, Low, Close, Volume)
- Tick volume (if real volume unavailable)
- Timestamp with timezone

**Historical Data Depth:**
- Minimum: 6 months of continuous data
- Recommended: 12-24 months for robust training
- Include various market conditions (trending, ranging, volatile)

**Data Format:**
- CSV or Parquet format
- Columns: `timestamp, open, high, low, close, volume, timeframe`
- No gaps in data (continuous)

#### 1.2 Data Processing Tasks
- Load multi-timeframe data
- Handle missing values and gaps
- Synchronize timestamps across timeframes
- Validate data quality (no duplicates, correct OHLCV relationships)
- Split data: 70% train, 15% validation, 15% test (chronological split)

---

### Phase 2: Feature Engineering

#### 2.1 Technical Indicators (As per Strategy)

**RSI-Based Features:**
- RSI(14) on M5
- RSI oversold crossover (crosses above 35.0)
- RSI overbought crossover (crosses below 65.0)
- RSI momentum (rate of change)

**Trend Indicators:**
- EMA(50) on H1
- Price position relative to H1 EMA (above/below)
- EMA slope (uptrend/downtrend strength)

**Multi-Timeframe Swing Analysis:**
- M1 swing high/low
- M3 swing high/low
- M5 swing high/low
- Swing alignment score (all three agreeing)

**Volume Profile:**
- 24-hour Volume Profile POC
- Current price relative to POC (above/below)
- Distance from POC (normalized)
- Volume at price levels

#### 2.2 Additional ML-Specific Features

**Price Action:**
- Price momentum (multiple periods)
- Volatility (ATR, standard deviation)
- Candlestick patterns
- Support/resistance levels

**Market Microstructure:**
- Bid-ask spread (if available)
- Order flow imbalance
- Volume spikes

**Temporal Features:**
- Hour of day
- Day of week
- Trading session (Asian, European, US)
- Time since last trade

**Risk Metrics:**
- Current daily P&L
- Number of trades today
- Win/loss streak
- Drawdown level

---

### Phase 3: Label Generation (Target Variable)

#### 3.1 Entry Signal Labels

**Binary Classification:**
- `1`: Valid SELL entry (reverse of standard BUY signal)
- `0`: Valid BUY entry (reverse of standard SELL signal)
- `-1`: No trade (filters not met)

**Multi-Class Classification (Alternative):**
- `STRONG_SELL`: All filters aligned for aggressive short
- `WEAK_SELL`: Partial confirmation
- `NEUTRAL`: No clear signal
- `WEAK_BUY`: Partial confirmation
- `STRONG_BUY`: All filters aligned for aggressive long

#### 3.2 Exit Signal Labels

**For Each Entry:**
- Actual exit price (from historical strategy execution)
- Time to exit
- Profit/loss in pips
- Exit reason (TP hit, SL hit, daily limit, manual close)

---

### Phase 4: Model Selection & Training

#### 4.1 Candidate Models

**Tree-Based Models:**
1. **XGBoost** (Primary candidate)
   - Excellent for tabular data
   - Handles non-linear relationships
   - Built-in feature importance
   
2. **LightGBM**
   - Faster training
   - Good for large datasets
   
3. **Random Forest**
   - Robust baseline
   - Less prone to overfitting

**Deep Learning Models:**
4. **LSTM (Long Short-Term Memory)**
   - Sequential time-series data
   - Captures temporal dependencies
   
5. **Transformer-based**
   - Attention mechanisms
   - Multi-timeframe fusion

**Ensemble Approaches:**
6. **Stacking Ensemble**
   - Combine multiple model predictions
   - Meta-learner for final decision

#### 4.2 Training Strategy

**Cross-Validation:**
- Time-series cross-validation (walk-forward)
- No look-ahead bias
- Expanding window approach

**Hyperparameter Optimization:**
- Optuna or Ray Tune for automated search
- Focus on precision and recall balance
- Custom loss function (profit-weighted)

**Training Metrics:**
- Accuracy
- Precision/Recall/F1 for each class
- ROC-AUC
- **Custom Metric:** Expected profit per trade

---

### Phase 5: Model Evaluation

#### 5.1 Performance Metrics

**Classification Metrics:**
- Confusion matrix
- Precision, Recall, F1-score per class
- ROC-AUC and Precision-Recall curves

**Trading-Specific Metrics:**
- Win rate
- Profit factor
- Sharpe ratio
- Maximum drawdown
- Average profit per trade
- Risk-reward ratio

**Strategy Alignment:**
- Signal agreement rate (ML vs original strategy)
- False positive rate (bad trades)
- Miss rate (missed good trades)

#### 5.2 Backtesting

**Walk-Forward Testing:**
- Test on unseen future data
- Simulate real trading conditions
- Include slippage and commissions

**Stress Testing:**
- Test on different market regimes
- Worst-case scenario analysis
- Sensitivity to parameter changes

---

### Phase 6: Deployment & Monitoring

#### 6.1 Model Deployment
- Export model to production format
- Create inference pipeline
- Integration with MT5 (if desired)

#### 6.2 Monitoring
- Track live performance vs backtest
- Detect model drift
- Automated retraining triggers

---

## Data Requirements Summary

### What I Need From You:

1. **Historical Market Data:**
   - **Symbol:** Gold (XAUUSD) or other traded instrument
   - **Timeframes:** M1, M3, M5, H1
   - **Period:** Minimum 6 months, preferably 12-24 months
   - **Format:** CSV files with columns: `timestamp, open, high, low, close, volume`
   - **Source:** MT5 export, broker API, or data provider

2. **Strategy Performance Data (Optional but Highly Valuable):**
   - Historical trade log from the MQL5 EA
   - Entry/exit timestamps
   - Entry/exit prices
   - Profit/loss per trade
   - Trade direction
   - This will be used as ground truth labels

3. **Clarifications:**
   - Specific symbol(s) this strategy trades
   - Broker spread and commission structure
   - Any additional filters or conditions not evident in the code
   - Preferred risk-reward targets if different from code

---

## Implementation Timeline

### Week 1-2: Data Collection & Exploration
- Gather historical data
- Exploratory data analysis
- Data quality validation
- Initial visualization

### Week 3-4: Feature Engineering
- Implement all technical indicators
- Create multi-timeframe features
- Generate labels from strategy logic
- Feature selection and importance analysis

### Week 5-6: Model Training
- Train baseline models
- Hyperparameter optimization
- Ensemble model development
- Cross-validation

### Week 7-8: Evaluation & Refinement
- Comprehensive backtesting
- Strategy comparison
- Model interpretation
- Performance optimization

### Week 9-10: Documentation & Deployment
- Final model selection
- Create deployment pipeline
- Write comprehensive documentation
- Prepare for live testing (paper trading)

---

## Success Criteria

1. **Model Accuracy:** >70% on test set for entry signals
2. **Profit Factor:** >1.5 in backtesting
3. **Sharpe Ratio:** >1.0
4. **Max Drawdown:** <20% of account
5. **Signal Agreement:** >80% alignment with original strategy on valid setups
6. **Latency:** <1 second for prediction generation

---

## Risk Considerations

1. **Overfitting:** Model learns noise instead of signal
2. **Look-Ahead Bias:** Using future information in training
3. **Market Regime Change:** Model trained on one regime fails in another
4. **Data Quality:** Garbage in, garbage out
5. **Slippage & Costs:** Real trading differs from backtest

---

## Next Steps

1. **Data Collection:** Provide historical data as specified above
2. **Environment Setup:** Install required Python libraries
3. **Notebook 01:** Begin with data exploration and validation
4. **Iterative Development:** Build pipeline step-by-step with validation at each stage

---

## Questions for You

1. What is the specific trading symbol? (XAUUSD, EURUSD, etc.)
2. What broker/data source will you use?
3. Do you have existing trade logs from the EA for ground truth labels?
4. What is your preferred Python environment? (Anaconda, venv, etc.)
5. Any specific ML frameworks you prefer? (TensorFlow, PyTorch, scikit-learn)
6. Target deployment: Standalone predictions or MT5 integration?

---

**Let's build this systematically and professionally. No guesswork—only data-driven decisions.**
