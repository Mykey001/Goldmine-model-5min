# Goldmine ML Strategy - Project Summary

## 📋 Project Overview

**Objective:** Transform the rule-based Goldmine Contrarian trading strategy into a predictive machine learning model.

**Strategy Core Principle:**  
Trade **against** retail behavior at RSI extremes (oversold/overbought) without additional filters.

---

## ✅ Current Status

### Data Availability: ✅ COMPLETE
- **Symbol:** XAUUSD (Gold)
- **Timeframes:** M1, M3, M5, H1
- **Duration:** Jan 2024 - Jul 2026 (18 months)
- **Size:** ~93 MB total
- **Location:** `data/raw/`

### Documentation: ✅ COMPLETE
- ✅ Strategy theory explained
- ✅ Complete ML pipeline documented
- ✅ Data requirements specified
- ✅ Quick start guide created

### Environment: 🔄 READY TO SETUP
- Python 3.10+ required
- All dependencies listed in requirements.txt
- Jupyter Lab/Notebook for development

### Implementation: ⏳ READY TO START
- Notebooks 01-05 created
- Source code structure ready
- Next step: Begin with `01_data_exploration.ipynb`

---

## 🎯 Project Goals

### Primary Objectives
1. **Build ML Model:** XGBoost classifier for entry signals
2. **Match/Beat Strategy:** ≥80% signal alignment with rule-based approach
3. **Validate Performance:** Positive expectancy in backtesting
4. **Professional Quality:** Reproducible, documented, production-ready

### Success Metrics
| Metric | Target | Stretch |
|--------|--------|---------|
| Accuracy | 75% | 80% |
| Win Rate | 50% | 55% |
| Profit Factor | 1.5 | 2.0 |
| Sharpe Ratio | 1.0 | 1.5 |

---

## 🔄 ML Pipeline Architecture

### Phase 1: Data Foundation
```
Raw CSV Files (M1, M3, M5, H1)
    ↓
Data Validation & Cleaning
    ↓
Multi-Timeframe Synchronization
    ↓
Processed Dataset
```

### Phase 2: Feature Engineering
```
Processed Data
    ↓
Technical Indicators (RSI, EMA, MACD, ADX)
    ↓
Price Action Features (momentum, volatility)
    ↓
Volume Features (surge, accumulation)
    ↓
Temporal Features (hour, day, session)
    ↓
Multi-Timeframe Features (alignment)
    ↓
Feature Matrix (~50-80 features)
```

### Phase 3: Label Generation
```
Feature Matrix
    ↓
Forward-Looking Outcome Analysis
    ↓
Binary Labels: BUY (1) / SELL (0) / NO_TRADE (-1)
    ↓
Handle Class Imbalance
    ↓
Labeled Dataset
```

### Phase 4: Model Training
```
Labeled Dataset
    ↓
Train/Val/Test Split (Chronological)
    ↓
Baseline Models (RF, XGBoost, LightGBM)
    ↓
Hyperparameter Optimization (Optuna)
    ↓
Cross-Validation (Time-Series)
    ↓
Best Model Selection
    ↓
Production Model
```

### Phase 5: Evaluation & Deployment
```
Production Model
    ↓
Test Set Predictions
    ↓
Classification Metrics (Accuracy, Precision, Recall)
    ↓
Backtesting (Trading Simulation)
    ↓
Performance Report
    ↓
Model Deployment
```

---

## 🧠 Strategy Translation

### Rule-Based Logic
```python
if RSI_M5 > 35 (crosses up):
    # Retail: BUY
    goldmine_signal = SELL  # Reverse
    
if RSI_M5 < 65 (crosses down):
    # Retail: SELL
    goldmine_signal = BUY  # Reverse
```

### ML Enhancement
```python
# Model learns:
- Which RSI extremes are high probability
- Market microstructure patterns
- Optimal entry timing
- Hidden correlations in features

# Output:
signal = model.predict(features)
confidence = model.predict_proba(features)
```

---

## 📊 Data Specifications

### Input Data
- **Primary Timeframe:** M5 (5-minute)
- **Supporting Timeframes:** M1, M3, H1
- **Features per Candle:**
  - OHLCV (Open, High, Low, Close, Volume)
  - Timestamp (UTC)

### Feature Categories
1. **RSI Features** (14 features)
   - RSI values across timeframes
   - Cross detection
   - Momentum, duration in zones

2. **Price Action** (12 features)
   - Price changes, volatility
   - Candle patterns
   - Support/resistance

3. **Volume** (6 features)
   - Volume ratios
   - Surge detection
   - Accumulation

4. **Trend** (10 features)
   - EMA indicators
   - MACD, ADX
   - Trend strength

5. **Temporal** (8 features)
   - Hour, day, session
   - Market timing

6. **Multi-Timeframe** (10+ features)
   - Alignment scores
   - Divergences
   - Cross-TF patterns

**Total:** ~60-80 engineered features

---

## 🛠️ Technology Stack

### Core Libraries
- **Data:** pandas, numpy
- **ML:** scikit-learn, xgboost, lightgbm
- **Deep Learning:** tensorflow/keras (optional)
- **Optimization:** optuna
- **Indicators:** ta, pandas_ta
- **Visualization:** matplotlib, seaborn, plotly
- **Interpretation:** shap

### Development Tools
- **Environment:** Python 3.10+, venv
- **Notebooks:** Jupyter Lab
- **Version Control:** Git
- **IDE:** VS Code (recommended)

---

## 📅 Timeline

### Week 1: Foundation
- Data exploration & validation
- Feature engineering
- Label generation
- **Deliverable:** Feature matrix ready

### Week 2: Training
- Baseline model training
- Hyperparameter optimization
- Cross-validation
- **Deliverable:** Trained models

### Week 3-4: Evaluation
- Model evaluation
- Backtesting simulation
- Performance analysis
- **Deliverable:** Final model & report

### Week 5: Polish
- Documentation
- Code cleanup
- Deployment preparation
- **Deliverable:** Production-ready system

**Total Duration:** 4-5 weeks (part-time)

---

## 🎓 Key Learning Points

### Strategy Insights
1. **Contrarian Edge:** Profit from retail traps at RSI extremes
2. **Simplicity:** No complex filters, pure RSI reversals
3. **Risk Management:** Asymmetric 1:2 risk-reward (200 SL, 100 TP)
4. **Patience:** One trade at a time, wait for clear signals

### ML Insights
1. **Time-Series Rules:** No shuffling, chronological splits only
2. **Look-Ahead Bias:** Most critical error to avoid
3. **Overfitting:** Simple models often outperform complex ones
4. **Imbalance:** Handle NO_TRADE class carefully
5. **Backtesting:** Simulate real trading conditions (slippage, costs)

---

## ⚠️ Risk Considerations

### Technical Risks
- **Overfitting:** Model memorizes, doesn't generalize
- **Look-Ahead Bias:** Accidentally using future data
- **Data Quality:** Gaps, outliers, incorrect timestamps
- **Class Imbalance:** Too many NO_TRADE labels

### Trading Risks
- **Slippage:** Real execution differs from backtest
- **Market Regime Change:** Model trained on one regime, tested on another
- **Black Swan Events:** Unprecedented market conditions
- **Execution Delays:** Latency in signal generation

### Mitigation Strategies
- Strict time-series validation
- Out-of-sample testing
- Multiple market regime testing
- Conservative position sizing
- Paper trading before live deployment

---

## 📈 Expected Deliverables

### Code Artifacts
1. ✅ 5 Jupyter notebooks (01-05)
2. ✅ Feature engineering pipeline
3. ⏳ Trained XGBoost model
4. ⏳ Model evaluation report
5. ⏳ Backtesting simulator
6. ⏳ Prediction script

### Documentation
1. ✅ Strategy theory document
2. ✅ Complete project plan
3. ✅ Quick start guide
4. ✅ Data requirements spec
5. ⏳ Model architecture doc
6. ⏳ Performance report

### Visualizations
1. ⏳ Equity curves
2. ⏳ Feature importance charts
3. ⏳ Confusion matrices
4. ⏳ SHAP value plots
5. ⏳ Prediction distributions

---

## 🚀 Next Actions

### Immediate (Today)
1. **Setup Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Launch Jupyter**
   ```bash
   jupyter lab
   ```

3. **Open First Notebook**
   - Navigate to `notebooks/01_data_exploration.ipynb`
   - Run cells sequentially
   - Validate data quality

### This Week
- Complete data exploration
- Engineer all features
- Generate labels
- Begin baseline training

### This Month
- Optimize models
- Full evaluation
- Comprehensive backtesting
- Document findings

---

## 📞 Resources

### Documentation
- **Strategy:** `docs/Goldmine_Strategy_Theory.md`
- **Plan:** `docs/ML_PROJECT_PLAN.md`
- **Quick Start:** `docs/QUICK_START_GUIDE.md`
- **Data Specs:** `docs/Data_Requirements.md`

### Code
- **Notebooks:** `notebooks/` (01-05)
- **Source:** `src/` (data_processing, feature_engineering, models)
- **Configs:** `configs/config.yaml`

### External Links
- XGBoost Docs: https://xgboost.readthedocs.io/
- Optuna Tutorial: https://optuna.readthedocs.io/
- SHAP Examples: https://shap.readthedocs.io/

---

## ✅ Pre-Flight Checklist

Before starting development:

- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Data files in `data/raw/` (✅ already done)
- [ ] Jupyter Lab/Notebook working
- [ ] Read strategy theory document
- [ ] Reviewed project plan
- [ ] Understood ML pipeline

**All green? → Open Notebook 01 and begin! 🚀**

---

**Document Version:** 1.0  
**Last Updated:** July 4, 2026  
**Status:** Ready for Implementation
