# Goldmine ML Project - Progress Checklist

## 📋 Project Status Tracker

**Project Start Date:** July 4, 2026  
**Expected Completion:** August 8, 2026 (5 weeks)

---

## ✅ Phase 0: Project Setup (Pre-Work)

### Environment Setup
- [ ] Python 3.10+ installed and verified
- [ ] Virtual environment created (`venv`)
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Jupyter Lab/Notebook tested and working
- [ ] Git repository initialized (optional but recommended)

### Documentation Review
- [ ] Read `docs/Goldmine_Strategy_Theory.md` completely
- [ ] Read `docs/ML_PROJECT_PLAN.md` completely
- [ ] Read `docs/QUICK_START_GUIDE.md`
- [ ] Understand PIPELINE_VISUAL.md
- [ ] Reviewed project structure

### Data Verification
- [x] Data files present in `data/raw/` ✅
- [x] XAUUSDm_M1 file (59 MB) ✅
- [x] XAUUSDm_M3 file (20 MB) ✅
- [x] XAUUSDm_M5 file (12 MB) ✅
- [x] XAUUSDm_H1 file (1 MB) ✅

**Status:** ⏳ READY TO START  
**Completion:** ▓▓▓▓▓▓░░░░░░░░░░░░░░ 30%

---

## 📊 Phase 1: Data Exploration (Notebook 01)

**Notebook:** `notebooks/01_data_exploration.ipynb`  
**Estimated Time:** 1-2 hours  
**Goal:** Validate data quality and understand structure

### Data Loading
- [ ] Load M1 data successfully
- [ ] Load M3 data successfully
- [ ] Load M5 data successfully
- [ ] Load H1 data successfully
- [ ] Verify column names match requirements
- [ ] Check data types (datetime, float, etc.)

### Data Quality Analysis
- [ ] Check for missing values (NaN)
- [ ] Check for duplicate timestamps
- [ ] Validate OHLC relationships (low ≤ open/close ≤ high)
- [ ] Check for unrealistic price jumps (>10%)
- [ ] Verify volume values are positive
- [ ] Count total rows per timeframe
- [ ] Identify any gaps in data (>5 consecutive missing candles)

### Data Visualization
- [ ] Plot M5 closing price over time
- [ ] Plot H1 closing price with EMA overlay
- [ ] Visualize volume distribution
- [ ] Check price volatility over time
- [ ] Identify major price trends and regimes

### Data Synchronization
- [ ] Align timestamps across all timeframes
- [ ] Resample to M5 base timeframe
- [ ] Handle any timezone issues (ensure UTC)
- [ ] Create unified DataFrame

### Save Processed Data
- [ ] Clean and preprocess all data
- [ ] Save to `data/processed/cleaned_multiTF.parquet`
- [ ] Verify saved file loads correctly
- [ ] Document any data issues found

**Status:** ⏳ NOT STARTED  
**Completion:** ░░░░░░░░░░░░░░░░░░░░ 0%

---

## 🔧 Phase 2: Feature Engineering (Notebook 02)

**Notebook:** `notebooks/02_feature_engineering.ipynb`  
**Estimated Time:** 2-3 hours  
**Goal:** Create all predictive features

### RSI Features (Core Strategy)
- [ ] Calculate RSI(14) for M5
- [ ] Calculate RSI(14) for M1
- [ ] Calculate RSI(14) for M3
- [ ] Calculate RSI(14) for H1
- [ ] Create RSI cross above 35 indicator (M5)
- [ ] Create RSI cross below 65 indicator (M5)
- [ ] Create RSI zone features (in_oversold, in_overbought)
- [ ] Calculate RSI momentum (rate of change)
- [ ] Calculate duration in extreme zones

### Price Action Features
- [ ] Price momentum (1, 3, 5, 10 periods)
- [ ] Rolling volatility (standard deviation)
- [ ] Candle body size (|close - open|)
- [ ] Upper wick size (high - max(open, close))
- [ ] Lower wick size (min(open, close) - low)
- [ ] Price change percentage
- [ ] High/Low ratios

### Volume Features
- [ ] Volume moving average (20 periods)
- [ ] Volume ratio (current / MA)
- [ ] Volume surge detection (>2x MA)
- [ ] Cumulative volume
- [ ] Volume momentum

### Trend & Momentum Indicators
- [ ] EMA(20) on M5
- [ ] EMA(50) on M5
- [ ] EMA(50) on H1
- [ ] Price above/below EMA flags
- [ ] MACD (12, 26, 9)
- [ ] MACD histogram
- [ ] ADX (Average Directional Index)
- [ ] +DI / -DI indicators

### Temporal Features
- [ ] Hour of day (0-23)
- [ ] Day of week (0-6)
- [ ] Trading session (0=Asian, 1=European, 2=US)
- [ ] Is high volatility hour (news times)
- [ ] Day of month

### Multi-Timeframe Features
- [ ] M1-M3-M5 RSI alignment score
- [ ] Cross-timeframe trend agreement
- [ ] RSI divergence detection
- [ ] Multi-TF momentum consensus

### Feature Quality
- [ ] Handle NaN values (forward fill, drop, etc.)
- [ ] Normalize/standardize features (StandardScaler)
- [ ] Check feature distributions
- [ ] Remove highly correlated features (>0.95)
- [ ] Remove low-variance features

### Label Generation
- [ ] Implement forward-looking outcome analysis
- [ ] Calculate future high/low for each candle
- [ ] Generate BUY/SELL/NO_TRADE labels
- [ ] Validate label distribution (class balance)
- [ ] Visualize label distribution
- [ ] Handle class imbalance (SMOTE, class weights)

### Data Splitting
- [ ] Split data chronologically (no shuffling!)
- [ ] Training set: Jan 2024 - Dec 2024 (70%)
- [ ] Validation set: Jan 2025 - Mar 2025 (15%)
- [ ] Test set: Apr 2025 - Jul 2026 (15%)
- [ ] Verify no data leakage between sets
- [ ] Save splits separately

### Save Feature Matrix
- [ ] Save feature-engineered data to `data/features/`
- [ ] Save train set: `features_train.parquet`
- [ ] Save validation set: `features_val.parquet`
- [ ] Save test set: `features_test.parquet`
- [ ] Save feature names list: `feature_names.json`
- [ ] Save scaler object: `scaler.pkl`

**Status:** ⏳ NOT STARTED  
**Completion:** ░░░░░░░░░░░░░░░░░░░░ 0%

---

## 🤖 Phase 3: Model Training (Notebook 03)

**Notebook:** `notebooks/03_model_training.ipynb`  
**Estimated Time:** 2-4 hours (includes compute time)  
**Goal:** Train and optimize ML models

### Baseline Model: Random Forest
- [ ] Import RandomForestClassifier
- [ ] Train with default parameters
- [ ] Predict on validation set
- [ ] Calculate accuracy, precision, recall, F1
- [ ] Save model to `models/checkpoints/rf_baseline.pkl`
- [ ] Document baseline performance

### Primary Model: XGBoost
- [ ] Import XGBoost
- [ ] Define initial hyperparameters
- [ ] Train XGBoost classifier
- [ ] Implement early stopping (50 rounds)
- [ ] Predict on validation set
- [ ] Calculate all metrics
- [ ] Plot training vs validation loss
- [ ] Save model checkpoint

### Secondary Model: LightGBM
- [ ] Import LightGBM
- [ ] Train with similar config to XGBoost
- [ ] Evaluate on validation set
- [ ] Compare with XGBoost performance
- [ ] Save model checkpoint

### Hyperparameter Optimization (Optuna)
- [ ] Install and import Optuna
- [ ] Define search space (max_depth, learning_rate, etc.)
- [ ] Define optimization objective (F1 or custom)
- [ ] Run 100+ trials
- [ ] Track best parameters
- [ ] Save optimization history
- [ ] Visualize optimization process

### Cross-Validation
- [ ] Implement TimeSeriesSplit (5 folds)
- [ ] Train model on each fold
- [ ] Calculate average metrics
- [ ] Check consistency across folds
- [ ] Identify overfitting (train vs val gap)

### Final Model Training
- [ ] Retrain with best hyperparameters
- [ ] Use train + validation sets (full data before test)
- [ ] Train until convergence
- [ ] Save final production model
- [ ] Document final configuration

### Model Comparison
- [ ] Create comparison table (RF vs XGBoost vs LightGBM)
- [ ] Compare accuracy, precision, recall, F1, AUC
- [ ] Compare training time
- [ ] Select best model for production

### Save Artifacts
- [ ] Save best model: `models/final/xgboost_best.pkl`
- [ ] Save hyperparameters: `models/final/best_params.json`
- [ ] Save training history: `results/metrics/training_history.csv`
- [ ] Save feature importance: `results/metrics/feature_importance.csv`

**Status:** ⏳ NOT STARTED  
**Completion:** ░░░░░░░░░░░░░░░░░░░░ 0%

---

## 📈 Phase 4: Model Evaluation (Notebook 04)

**Notebook:** `notebooks/04_model_evaluation.ipynb`  
**Estimated Time:** 1-2 hours  
**Goal:** Comprehensive model assessment

### Load Model & Data
- [ ] Load best model from `models/final/`
- [ ] Load test set (never seen before!)
- [ ] Verify test set has no data leakage

### Generate Predictions
- [ ] Predict on test set
- [ ] Get predicted classes (0, 1, -1)
- [ ] Get prediction probabilities
- [ ] Calculate confidence scores

### Classification Metrics
- [ ] Calculate accuracy
- [ ] Calculate precision (per class)
- [ ] Calculate recall (per class)
- [ ] Calculate F1-score (per class)
- [ ] Calculate macro/micro averages
- [ ] Generate classification report
- [ ] Save metrics to JSON

### Confusion Matrix
- [ ] Create confusion matrix
- [ ] Visualize with heatmap
- [ ] Analyze misclassifications
- [ ] Identify systematic errors
- [ ] Save confusion matrix plot

### ROC & Precision-Recall Curves
- [ ] Calculate ROC-AUC for each class
- [ ] Plot ROC curves
- [ ] Calculate Precision-Recall AUC
- [ ] Plot PR curves
- [ ] Compare BUY vs SELL performance

### Feature Importance
- [ ] Extract feature importance from model
- [ ] Sort features by importance
- [ ] Plot top 20 features
- [ ] Validate importance makes sense
- [ ] Save feature importance chart

### SHAP Values (Interpretability)
- [ ] Install and import SHAP
- [ ] Calculate SHAP values for test set
- [ ] Create summary plot
- [ ] Create force plots for sample predictions
- [ ] Analyze feature contributions
- [ ] Save SHAP visualizations

### Error Analysis
- [ ] Identify most confident wrong predictions
- [ ] Identify least confident correct predictions
- [ ] Analyze feature patterns in errors
- [ ] Look for systematic biases
- [ ] Document findings

### Compare with Rule-Based Strategy
- [ ] Implement rule-based strategy signals
- [ ] Compare ML vs rule-based on same data
- [ ] Calculate signal agreement rate
- [ ] Identify where ML differs
- [ ] Analyze if differences are improvements

### Save Results
- [ ] Save all metrics to `results/metrics/evaluation_report.json`
- [ ] Save visualizations to `results/visualizations/`
- [ ] Create summary report document
- [ ] Document key findings

**Status:** ⏳ NOT STARTED  
**Completion:** ░░░░░░░░░░░░░░░░░░░░ 0%

---

## 💰 Phase 5: Backtesting (Notebook 05)

**Notebook:** `notebooks/05_backtesting.ipynb`  
**Estimated Time:** 1-2 hours  
**Goal:** Simulate real trading performance

### Trading Simulator Setup
- [ ] Define trading rules (entry, TP, SL)
- [ ] Set position size (e.g., 0.3 lots)
- [ ] Define pip value for XAUUSD (0.01)
- [ ] TP = 100 pips
- [ ] SL = 200 pips
- [ ] One trade at a time rule

### Signal Generation
- [ ] Use model predictions on test set
- [ ] Filter for BUY and SELL signals only (ignore NO_TRADE)
- [ ] Optionally: Apply confidence threshold (e.g., >70%)
- [ ] Create trade entry signals

### Trade Simulation
- [ ] For each signal, simulate trade:
  - [ ] Record entry timestamp
  - [ ] Record entry price
  - [ ] Calculate TP and SL levels
  - [ ] Track price movement
  - [ ] Determine exit (TP hit or SL hit)
  - [ ] Record exit timestamp
  - [ ] Calculate profit/loss
- [ ] Ensure no overlapping positions

### Calculate Trading Metrics
- [ ] Total number of trades
- [ ] Number of winning trades
- [ ] Number of losing trades
- [ ] Win rate (%)
- [ ] Gross profit
- [ ] Gross loss
- [ ] Net profit
- [ ] Profit factor (gross profit / gross loss)
- [ ] Average win
- [ ] Average loss
- [ ] Risk-reward ratio
- [ ] Expectancy per trade

### Risk Metrics
- [ ] Calculate equity curve
- [ ] Identify maximum drawdown
- [ ] Calculate drawdown duration
- [ ] Calculate Sharpe ratio
- [ ] Calculate Sortino ratio (optional)
- [ ] Calculate Calmar ratio (optional)

### Visualizations
- [ ] Plot equity curve
- [ ] Plot drawdown over time
- [ ] Plot win/loss distribution
- [ ] Plot trade duration distribution
- [ ] Plot hourly/daily trade distribution

### Sensitivity Analysis
- [ ] Test with different TP values (80, 100, 120 pips)
- [ ] Test with different SL values (150, 200, 250 pips)
- [ ] Test with confidence thresholds (60%, 70%, 80%)
- [ ] Compare results
- [ ] Find optimal parameters

### Compare Strategies
- [ ] Backtest rule-based strategy (pure RSI)
- [ ] Backtest ML model
- [ ] Create side-by-side comparison
- [ ] Analyze profit improvement
- [ ] Identify ML edge

### Save Results
- [ ] Save trade log to `results/predictions/trade_log.csv`
- [ ] Save metrics to `results/metrics/backtest_metrics.json`
- [ ] Save equity curve plot
- [ ] Save drawdown plot
- [ ] Create comprehensive backtest report

**Status:** ⏳ NOT STARTED  
**Completion:** ░░░░░░░░░░░░░░░░░░░░ 0%

---

## 📝 Phase 6: Documentation & Deployment

**Estimated Time:** 2-3 hours  
**Goal:** Finalize documentation and prepare for deployment

### Model Documentation
- [ ] Document final model architecture
- [ ] List all hyperparameters used
- [ ] Describe feature engineering process
- [ ] Document model performance metrics
- [ ] Create model card (summary sheet)

### Code Documentation
- [ ] Add docstrings to all functions
- [ ] Add comments to complex logic
- [ ] Create README for each module
- [ ] Document any assumptions made

### Inference Pipeline
- [ ] Create standalone prediction script
- [ ] Test script on new data
- [ ] Measure prediction latency (<1s requirement)
- [ ] Document usage instructions

### Deployment Options
- [ ] Option 1: Standalone Python script (manual execution)
- [ ] Option 2: REST API (Flask/FastAPI)
- [ ] Option 3: MT5 integration script
- [ ] Document chosen deployment method

### Monitoring & Maintenance
- [ ] Create performance monitoring dashboard (optional)
- [ ] Document retraining procedure
- [ ] Define model drift detection criteria
- [ ] Create retraining trigger rules

### Final Presentation
- [ ] Create summary presentation slides
- [ ] Include key visualizations
- [ ] Summarize model performance
- [ ] Present business impact

### Repository Cleanup
- [ ] Remove unused notebooks
- [ ] Clean up temporary files
- [ ] Organize all results
- [ ] Final commit to Git (if using)

**Status:** ⏳ NOT STARTED  
**Completion:** ░░░░░░░░░░░░░░░░░░░░ 0%

---

## 🎯 Overall Project Progress

```
Project Milestone Tracker:

[✅] Phase 0: Setup (30% complete)
[⏳] Phase 1: Data Exploration (0% complete)
[⏳] Phase 2: Feature Engineering (0% complete)
[⏳] Phase 3: Model Training (0% complete)
[⏳] Phase 4: Model Evaluation (0% complete)
[⏳] Phase 5: Backtesting (0% complete)
[⏳] Phase 6: Documentation (0% complete)

Overall: ▓▓░░░░░░░░░░░░░░░░░░ 5%
```

---

## 📊 Success Criteria Tracking

### Minimum Requirements
- [ ] Model accuracy ≥ 70%
- [ ] Win rate ≥ 45%
- [ ] Profit factor ≥ 1.2
- [ ] Max drawdown ≤ 30%

### Target Requirements
- [ ] Model accuracy ≥ 75%
- [ ] Win rate ≥ 50%
- [ ] Profit factor ≥ 1.5
- [ ] Max drawdown ≤ 20%
- [ ] Sharpe ratio ≥ 1.0

### Stretch Goals
- [ ] Model accuracy ≥ 80%
- [ ] Win rate ≥ 55%
- [ ] Profit factor ≥ 2.0
- [ ] Max drawdown ≤ 15%
- [ ] Sharpe ratio ≥ 1.5

**Current Status:** Not yet evaluated

---

## 🚨 Issues & Blockers Log

| Date | Issue | Resolution | Status |
|------|-------|------------|--------|
| - | - | - | - |

---

## 📝 Notes & Insights

### Key Learnings
- *(Add as you progress)*

### Challenges Faced
- *(Add as you encounter them)*

### Improvements for Future
- *(Add ideas as they come)*

---

## ⏰ Time Tracking

| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 0: Setup | 1h | - | - |
| Phase 1: Data Exploration | 2h | - | - |
| Phase 2: Feature Engineering | 3h | - | - |
| Phase 3: Model Training | 4h | - | - |
| Phase 4: Model Evaluation | 2h | - | - |
| Phase 5: Backtesting | 2h | - | - |
| Phase 6: Documentation | 2h | - | - |
| **Total** | **16h** | **-** | **-** |

---

**Checklist Version:** 1.0  
**Last Updated:** July 4, 2026  
**Next Review:** After completing each phase

---

## 🎉 Completion Celebration

Once all phases are ✅, you will have:
- A production-ready ML trading model
- Comprehensive documentation
- Validated backtest results
- Deployment-ready codebase
- Professional portfolio project

**Let's get started! 🚀**
