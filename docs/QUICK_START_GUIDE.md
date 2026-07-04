# Quick Start Guide - Goldmine ML Project

## 🎯 Goal
Build an ML model that predicts BUY/SELL signals for the Goldmine Contrarian Strategy.

---

## ✅ Pre-Flight Checklist

### 1. Data Available
- ✅ XAUUSDm_M1_202401012305_202607031457.csv (59 MB)
- ✅ XAUUSDm_M3_202401012303_202607031457.csv (20 MB)
- ✅ XAUUSDm_M5_202401012305_202607031500.csv (12 MB)
- ✅ XAUUSDm_H1_202401012300_202607031500.csv (1 MB)

**Location:** `data/raw/`  
**Duration:** Jan 2024 - Jul 2026 (18 months) ✅

### 2. Environment Setup

```bash
# Check Python version (must be 3.10+)
python --version

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pandas, numpy, xgboost; print('All good!')"
```

### 3. Launch Jupyter

```bash
# Start Jupyter Lab (recommended)
jupyter lab

# OR Jupyter Notebook
jupyter notebook
```

---

## 📓 Notebook Execution Order

### Phase 1: Foundation
**Notebook:** `01_data_exploration.ipynb`
- Load 4 timeframes
- Validate data quality
- Visualize price action
- Check for gaps/outliers
- **Time:** 1-2 hours

### Phase 2: Features
**Notebook:** `02_feature_engineering.ipynb`
- Calculate RSI (all timeframes)
- Create price action features
- Add volume features
- Generate labels (BUY/SELL/NO_TRADE)
- **Time:** 2-3 hours

### Phase 3: Training
**Notebook:** `03_model_training.ipynb`
- Train baseline models
- Optimize hyperparameters
- Cross-validation
- Save best model
- **Time:** 2-4 hours (includes compute)

### Phase 4: Evaluation
**Notebook:** `04_model_evaluation.ipynb`
- Test on holdout data
- Classification metrics
- Feature importance
- Error analysis
- **Time:** 1-2 hours

### Phase 5: Backtest
**Notebook:** `05_backtesting.ipynb`
- Simulate trading
- Calculate win rate, profit factor
- Generate equity curve
- Compare with rule-based strategy
- **Time:** 1-2 hours

---

## 🎓 Key Concepts

### Strategy Core Logic
```
RSI crosses ABOVE 35 (oversold)
→ Retail thinks: BUY
→ Goldmine does: SELL (reverse)

RSI crosses BELOW 65 (overbought)
→ Retail thinks: SELL
→ Goldmine does: BUY (reverse)
```

### Risk Parameters
- **Take Profit:** 100 pips
- **Stop Loss:** 200 pips
- **Risk-Reward:** 1:2 (asymmetric)
- **Position:** 1 trade at a time

### ML Task
- **Type:** Binary or 3-class classification
- **Input:** ~50-80 engineered features
- **Output:** BUY (1) / SELL (0) / NO_TRADE (-1)
- **Model:** XGBoost (primary)

---

## 📊 Expected Results

### Minimum Viable
- Accuracy: 70%+
- Win Rate: 45%+
- Profit Factor: 1.2+

### Target
- Accuracy: 75%+
- Win Rate: 50%+
- Profit Factor: 1.5+

### Excellent
- Accuracy: 80%+
- Win Rate: 55%+
- Profit Factor: 2.0+

---

## 🚨 Common Pitfalls to Avoid

1. **Look-Ahead Bias:** Never use future data in features
2. **Data Shuffling:** Always use chronological splits
3. **Overfitting:** Validate on truly unseen data
4. **Ignoring Slippage:** Real trading has costs
5. **Over-Optimization:** Don't chase 99% backtest accuracy

---

## 📁 Project Structure

```
Profitable5min/
├── data/
│   ├── raw/              ← Your CSV files (✅ done)
│   ├── processed/        ← Cleaned data (created in notebook 01)
│   └── features/         ← Feature matrix (created in notebook 02)
├── notebooks/
│   ├── 01_data_exploration.ipynb      ← START HERE
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_evaluation.ipynb
│   └── 05_backtesting.ipynb
├── models/
│   ├── checkpoints/      ← Training checkpoints
│   └── final/            ← Production model
├── results/
│   ├── metrics/          ← Performance reports
│   ├── visualizations/   ← Charts, plots
│   └── predictions/      ← Model outputs
└── docs/
    ├── Goldmine_Strategy_Theory.md    ← Strategy explanation
    ├── ML_PROJECT_PLAN.md             ← Complete plan (you are here)
    └── QUICK_START_GUIDE.md           ← This file
```

---

## 🔧 Troubleshooting

### Error: Module not found
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

### Error: Data file not found
```bash
# Check files exist
dir data\raw

# Verify path in notebook matches actual location
```

### Kernel crashes during training
```python
# Reduce data size for testing
df = df.sample(frac=0.1)  # Use 10% of data

# Or reduce model complexity
n_estimators = 100  # Instead of 1000
```

### Jupyter won't start
```bash
# Install/reinstall Jupyter
pip install jupyter jupyterlab --upgrade

# Try classic notebook
jupyter notebook
```

---

## 💡 Pro Tips

1. **Start Small:** Run notebooks on subset of data first
2. **Save Often:** Save intermediate results to avoid recomputation
3. **Document Assumptions:** Comment your code extensively
4. **Version Models:** Save models with timestamps
5. **Track Experiments:** Keep notes on what works/doesn't work

---

## 📞 Need Help?

1. **Strategy Questions:** Read `docs/Goldmine_Strategy_Theory.md`
2. **Technical Errors:** Check error messages, Google stack traces
3. **Data Issues:** Verify CSV format and column names
4. **Model Performance:** Review `docs/ML_PROJECT_PLAN.md` Section VIII

---

## ✨ Next Action

**Right now, do this:**

1. Open terminal/command prompt
2. Navigate to project folder:
   ```bash
   cd c:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min
   ```
3. Activate environment:
   ```bash
   venv\Scripts\activate
   ```
4. Launch Jupyter:
   ```bash
   jupyter lab
   ```
5. Open: `notebooks/01_data_exploration.ipynb`
6. Run first cell: Load data

---

**🚀 You're ready! Let's build this model.**
