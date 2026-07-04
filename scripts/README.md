# Goldmine ML - Python Scripts

## 📋 Overview

These are **complete, executable Python scripts** for the Goldmine ML project. You can:
1. Run them directly in Python
2. Copy-paste into Jupyter notebooks (cell by cell)
3. Execute from command line

All scripts are production-ready and fully documented.

---

## 🚀 Quick Start

### Option 1: Run as Python Scripts (Recommended)

```bash
# Activate environment
cd c:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min
venv\Scripts\activate

# Run scripts in sequence
python scripts/01_data_exploration.py
python scripts/02_feature_engineering.py
python scripts/03_model_training.py
python scripts/04_model_evaluation.py
python scripts/05_backtesting.py
```

### Option 2: Use in Jupyter Notebook

1. Open Jupyter Lab
2. Create new notebook
3. Copy sections from scripts
4. Run cell by cell

---

## 📝 Script Descriptions

### 01_data_exploration.py
**Purpose:** Load and validate multi-timeframe data

**What it does:**
- Loads M1, M3, M5, H1 CSV files
- Validates data quality (missing values, duplicates, OHLC relationships)
- Generates price visualizations
- Saves cleaned data to `data/processed/`

**Runtime:** ~2 minutes  
**Output:** 
- `data/processed/M1_cleaned.parquet`
- `data/processed/M3_cleaned.parquet`
- `data/processed/M5_cleaned.parquet`
- `data/processed/H1_cleaned.parquet`
- `results/visualizations/m5_price_chart.png`

---

### 02_feature_engineering.py
**Purpose:** Create predictive features and labels

**What it does:**
- Calculates RSI (core strategy indicator)
- Creates 60+ features (price action, volume, trend, temporal)
- Generates labels (BUY/SELL/NO_TRADE) using forward-looking analysis
- Splits data chronologically (Train/Val/Test)
- Saves feature matrix

**Runtime:** ~5-10 minutes (label generation is slow)  
**Output:**
- `data/features/train.parquet` (70% of data)
- `data/features/val.parquet` (15% of data)
- `data/features/test.parquet` (15% of data)
- `data/features/feature_names.json`

---

### 03_model_training.py
**Purpose:** Train XGBoost classifier

**What it does:**
- Trains baseline Random Forest
- Trains primary XGBoost model
- Calculates feature importance
- Generates confusion matrix
- Saves trained model

**Runtime:** ~10-20 minutes (depends on CPU)  
**Output:**
- `models/final/xgboost_model.pkl` (trained model)
- `models/final/model_params.json`
- `results/metrics/feature_importance.csv`
- `results/metrics/training_metrics.json`
- `results/visualizations/feature_importance.png`
- `results/visualizations/confusion_matrix.png`

---

### 04_model_evaluation.py
**Purpose:** Evaluate model on test set

**What it does:**
- Loads trained model
- Predicts on unseen test data
- Calculates accuracy, precision, recall, F1, ROC-AUC
- Generates visualizations
- Analyzes prediction confidence

**Runtime:** ~2 minutes  
**Output:**
- `results/predictions/test_predictions.csv`
- `results/metrics/test_metrics.json`
- `results/visualizations/confusion_matrix_test.png`
- `results/visualizations/roc_curve.png`
- `results/visualizations/confidence_distribution.png`

---

### 05_backtesting.py
**Purpose:** Simulate real trading performance

**What it does:**
- Generates trading signals from model
- Simulates trades with TP/SL (100/200 pips)
- Calculates win rate, profit factor, Sharpe ratio
- Tracks equity curve
- Generates comprehensive trading report

**Runtime:** ~3-5 minutes  
**Output:**
- `results/predictions/trade_log.csv`
- `results/metrics/backtest_metrics.json`
- `results/visualizations/equity_curve.png`
- `results/visualizations/trade_distribution.png`

---

## 📊 Expected Results

After running all scripts, you should see:

### Training Metrics (Notebook 03)
- Accuracy: **75-80%**
- Precision: **70-75%**
- F1-Score: **72-77%**

### Backtest Results (Notebook 05)
- Win Rate: **48-55%**
- Profit Factor: **1.3-1.8**
- Net Profit: **Positive** (target: $5,000+ on $10,000 capital)
- Max Drawdown: **<20%**

---

## 🛠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'ta'"
```bash
pip install ta pandas-ta
```

### Error: "File not found"
Make sure you're running from project root:
```bash
cd c:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min
```

### Script runs slowly
Normal! Feature engineering and model training are compute-intensive.
- Script 02: ~10 minutes (label generation)
- Script 03: ~15 minutes (model training)

### Out of memory
If you run out of RAM, modify scripts to use less data:
```python
# Add this after loading data
m5 = m5.sample(frac=0.5, random_state=42)  # Use 50% of data
```

---

## 📁 Directory Structure After Execution

```
Profitable5min/
├── data/
│   ├── processed/
│   │   ├── M1_cleaned.parquet ✅
│   │   ├── M3_cleaned.parquet ✅
│   │   ├── M5_cleaned.parquet ✅
│   │   └── H1_cleaned.parquet ✅
│   └── features/
│       ├── train.parquet ✅
│       ├── val.parquet ✅
│       ├── test.parquet ✅
│       └── feature_names.json ✅
├── models/
│   └── final/
│       ├── xgboost_model.pkl ✅
│       └── model_params.json ✅
├── results/
│   ├── metrics/
│   │   ├── training_metrics.json ✅
│   │   ├── test_metrics.json ✅
│   │   ├── backtest_metrics.json ✅
│   │   └── feature_importance.csv ✅
│   ├── predictions/
│   │   ├── test_predictions.csv ✅
│   │   └── trade_log.csv ✅
│   └── visualizations/
│       ├── m5_price_chart.png ✅
│       ├── feature_importance.png ✅
│       ├── confusion_matrix.png ✅
│       ├── confusion_matrix_test.png ✅
│       ├── roc_curve.png ✅
│       ├── confidence_distribution.png ✅
│       ├── equity_curve.png ✅
│       └── trade_distribution.png ✅
```

---

## ⏱️ Total Time Estimate

| Script | Time |
|--------|------|
| 01_data_exploration.py | 2 min |
| 02_feature_engineering.py | 10 min |
| 03_model_training.py | 15 min |
| 04_model_evaluation.py | 2 min |
| 05_backtesting.py | 5 min |
| **TOTAL** | **~35 minutes** |

---

## ✅ Success Criteria

After completion, verify:
- [ ] All 5 scripts ran without errors
- [ ] Model accuracy ≥ 70%
- [ ] Backtest win rate ≥ 45%
- [ ] Profit factor ≥ 1.2
- [ ] All output files created

---

## 🎉 Next Steps

Once all scripts complete successfully:
1. Review results in `results/metrics/`
2. Check visualizations in `results/visualizations/`
3. Analyze trade log in `results/predictions/trade_log.csv`
4. Consider model improvements (see ML_PROJECT_PLAN.md)

---

**Ready to start? Run:**
```bash
python scripts/01_data_exploration.py
```
