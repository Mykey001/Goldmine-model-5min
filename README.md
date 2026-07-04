# Goldmine ML Trading Strategy

A machine learning implementation of the Goldmine Contrarian trading strategy for predicting entry and exit signals based on retail liquidity traps and institutional flow.

## Project Overview

This project transforms the rule-based Goldmine trading strategy into a predictive ML model that identifies optimal entry and exit points by learning from historical market patterns and the strategy's psychological principles.

## Strategy Philosophy

The Goldmine Contrarian Principle is based on:
- **Retail Exhaustion:** Trading against predictable retail behavior at RSI extremes
- **Institutional Alignment:** Following volume profile POC and macro trends
- **Multi-Timeframe Consensus:** M1, M3, M5 micro-trends validated by H1 macro-trend
- **Asymmetric Execution:** Triple position entries on high-conviction setups

See [docs/Goldmine_Strategy_Theory.md](docs/Goldmine_Strategy_Theory.md) for detailed theory.

## Project Structure

```
├── data/                    # Raw, processed, and feature datasets
├── src/                     # Source code modules
├── notebooks/               # Jupyter notebooks for experimentation
├── models/                  # Saved ML models
├── results/                 # Metrics, visualizations, predictions
├── configs/                 # Configuration files
├── docs/                    # Documentation
└── SimplifiedGoldmine_v1.mq5  # Original MQL5 strategy
```

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Data Requirements

To train the model, you need:
- **Timeframes:** M1, M3, M5, H1 OHLCV data
- **Duration:** Minimum 6 months (12-24 months recommended)
- **Format:** CSV with columns: `timestamp, open, high, low, close, volume`
- **Symbol:** Gold (XAUUSD) or your traded instrument

Place raw data files in `data/raw/` directory.

## Usage

Follow the numbered notebooks in sequence:

1. **01_data_exploration.ipynb** - Load and explore market data
2. **02_feature_engineering.ipynb** - Create technical indicators and features
3. **03_model_training.ipynb** - Train ML models
4. **04_model_evaluation.ipynb** - Evaluate performance
5. **05_backtesting.ipynb** - Backtest on unseen data

## Key Features

- Multi-timeframe feature engineering (M1, M3, M5, H1)
- RSI-based liquidity trap detection
- Volume Profile POC calculation
- Ensemble ML models (XGBoost, LightGBM, LSTM)
- Walk-forward backtesting
- Trading-specific performance metrics

## Model Architecture

- **Primary Model:** XGBoost classifier for entry/exit signals
- **Features:** 50+ engineered features including RSI, EMA, swing points, POC
- **Labels:** Binary classification (BUY/SELL/NO_TRADE)
- **Validation:** Time-series cross-validation with walk-forward testing

## Performance Metrics

- Classification: Accuracy, Precision, Recall, F1, ROC-AUC
- Trading: Win Rate, Profit Factor, Sharpe Ratio, Max Drawdown
- Strategy Alignment: Signal agreement with original EA

## Documentation

- [Strategy Theory](docs/Goldmine_Strategy_Theory.md) - Psychological foundation
- [Project Plan](docs/Project_Plan.md) - Complete pipeline and timeline

## Contributing

This is a professional research project. All changes should be:
1. Data-driven and validated
2. Properly documented
3. Tested on out-of-sample data

## License

Proprietary - All Rights Reserved

## Contact

For questions about data requirements or implementation, refer to [docs/Project_Plan.md](docs/Project_Plan.md).

---

**Status:** Development Phase - Data Collection
**Last Updated:** July 3, 2026
# Goldmine-model-5min
