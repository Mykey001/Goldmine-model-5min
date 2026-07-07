# Backtest Interface Guide

## Overview
The Backtest Interface provides a comprehensive on-demand backtesting system integrated into the live trading frontend. It allows you to fetch fresh data, calculate features, generate ML signals, and run complete backtest simulations with full visualization and metrics.

## Features

### 1. **Data Fetching**
- Fetches fresh historical data directly from MT5
- Supports multiple timeframes (M1, M3, M5, M15, M30, H1, H4, D1)
- Custom date range selection
- Automatic data validation

### 2. **Feature Engineering**
- Real-time calculation of 50+ technical indicators
- RSI-based features (core strategy)
- Price action patterns
- Trend indicators (EMA, MACD, ADX)
- Volume features
- Temporal features (sessions, day of week)

### 3. **Signal Generation**
- ML model predictions with confidence scores
- Configurable confidence threshold
- Optional H1 trend filter
- Alignment with live trading logic

### 4. **Backtest Simulation**
- Realistic trade execution simulation
- TP/SL order management
- Equity curve tracking
- Comprehensive trade logging

### 5. **Performance Metrics**
- **Trading Performance:**
  - Total trades
  - Winning/losing trades
  - Win rate
  - Gross profit/loss
  - Average win/loss
  - Profit factor

- **Risk Metrics:**
  - Maximum drawdown ($ and %)
  - Sharpe ratio
  - Risk/reward ratio

### 6. **Visualizations**
- **Equity Curve:** Real-time equity progression
- **Drawdown Chart:** Visual risk assessment
- **Profit Distribution:** Trade outcome histogram
- **Trade Log Table:** Detailed trade-by-trade analysis

## How to Use

### Step 1: Access Backtest Tab
1. Open the frontend application
2. Click on the "Backtest" tab in the navigation bar
3. The Backtest Configuration panel will appear

### Step 2: Configure Backtest Parameters

#### Basic Configuration
- **Symbol:** Trading symbol (default: XAUUSDm)
- **Start Date:** Beginning of backtest period
- **End Date:** End of backtest period

#### Risk Management
- **Take Profit (pips):** Target profit level (default: 100)
- **Stop Loss (pips):** Maximum loss level (default: 50)
- **Lot Size:** Position size (default: 0.01)
- **Starting Capital:** Initial account balance (default: $10,000)

#### Advanced Settings
- **Min Confidence:** Minimum ML confidence to take trade (0.0-1.0)
- **Use H1 Trend Filter:** Enable/disable H1 trend alignment
- **H1 EMA Period:** EMA period for trend determination (default: 200)

### Step 3: Run Backtest
1. Click "Run Backtest" button
2. Wait for data fetching and processing (may take 30-60 seconds)
3. View results in real-time

### Step 4: Analyze Results

#### Performance Summary
- Overall performance badge (Excellent/Good/Fair/Poor)
- Key metrics at a glance
- Net profit and return percentage

#### Detailed Analysis
- Trading performance breakdown
- Risk metrics evaluation
- Visual charts for trends
- Trade-by-trade review

## Configuration Examples

### Conservative Strategy
```yaml
TP: 50 pips
SL: 30 pips
Lot Size: 0.01
Min Confidence: 0.7
H1 Filter: Enabled
```

### Aggressive Strategy
```yaml
TP: 150 pips
SL: 75 pips
Lot Size: 0.05
Min Confidence: 0.5
H1 Filter: Disabled
```

### Balanced Strategy (Default)
```yaml
TP: 100 pips
SL: 50 pips
Lot Size: 0.01
Min Confidence: 0.5
H1 Filter: Enabled (EMA200)
```

## API Endpoint

### POST `/api/backtest/run`

**Query Parameters:**
- `symbol` (string): Trading symbol
- `start_date` (ISO datetime): Start date
- `end_date` (ISO datetime): End date
- `use_h1_filter` (boolean): Enable H1 filter
- `h1_ema_period` (int): H1 EMA period
- `min_confidence` (float): Min confidence threshold
- `tp_pips` (int): Take profit in pips
- `sl_pips` (int): Stop loss in pips
- `lot_size` (float): Position size
- `starting_capital` (float): Starting capital

**Response:**
```json
{
  "success": true,
  "metrics": {
    "total_trades": 150,
    "winning_trades": 85,
    "losing_trades": 65,
    "win_rate": 56.67,
    "profit_factor": 1.85,
    "net_profit": 2500.50,
    "gross_profit": 5200.00,
    "gross_loss": 2699.50,
    "avg_win": 61.18,
    "avg_loss": -41.53,
    "max_drawdown": -850.00,
    "max_drawdown_pct": -7.5,
    "sharpe_ratio": 1.45,
    "final_equity": 12500.50,
    "return_pct": 25.01
  },
  "trades": [...],
  "equity_curve": [...],
  "config": {...},
  "symbol": "XAUUSDm",
  "start_date": "2025-05-01T00:00:00",
  "end_date": "2025-07-03T00:00:00",
  "total_candles": 15000
}
```

## Backend Architecture

### BacktestEngine Class
Location: `src/live_trading/backtest_engine.py`

**Key Methods:**
- `fetch_data()`: Fetch historical data from MT5
- `calculate_features()`: Calculate technical indicators
- `calculate_h1_trend()`: Calculate H1 trend filter
- `generate_signals()`: Generate ML predictions
- `run_backtest()`: Execute backtest simulation
- `full_backtest()`: Complete pipeline execution

### Integration
The backtest engine is initialized in `run.py` and injected into the FastAPI application:

```python
backtest_engine = BacktestEngine(config.MODEL_PATH)
init_api(bot, bot.terminal_manager, bot.db, backtest_engine)
```

## Frontend Components

### BacktestPanel
Main component for configuration and orchestration.
Location: `frontend/src/components/dashboard/BacktestPanel.tsx`

### BacktestResults
Displays performance metrics and configuration summary.
Location: `frontend/src/components/dashboard/BacktestResults.tsx`

### BacktestChart
Renders equity curve, drawdown, and trade distribution charts.
Location: `frontend/src/components/dashboard/BacktestChart.tsx`

## Performance Tips

### Data Fetching
- Shorter date ranges load faster
- M5 timeframe is optimal for the strategy
- Consider MT5 data availability limits

### Processing Time
- Typical backtest: 30-60 seconds
- Factors: date range, number of candles, feature complexity

### Browser Performance
- Large trade lists (1000+) may slow rendering
- Charts are optimized with React memoization
- Consider pagination for very long backtests

## Interpreting Results

### Good Backtest Indicators
- ✅ Win rate > 50%
- ✅ Profit factor > 1.5
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 20%
- ✅ Consistent equity curve growth

### Warning Signs
- ⚠️ Win rate < 40%
- ⚠️ Profit factor < 1.2
- ⚠️ Max drawdown > 30%
- ⚠️ Irregular equity curve
- ⚠️ Very few trades (< 30)

### Red Flags
- 🚫 Negative net profit
- 🚫 Profit factor < 1.0
- 🚫 Max drawdown > 50%
- 🚫 Negative Sharpe ratio
- 🚫 Win rate < 30%

## Troubleshooting

### "No data returned" Error
- Check MT5 connection
- Verify symbol name is correct
- Ensure date range has trading data
- Check MT5 market watch has symbol enabled

### "Model not loaded" Error
- Ensure model file exists at `models/final/xgboost_model.pkl`
- Check file permissions
- Verify model was trained successfully

### "Backtest failed" Error
- Check backend logs for details
- Verify all dependencies installed
- Ensure sufficient system resources
- Check data quality and completeness

### Slow Performance
- Reduce date range
- Use more recent data
- Check system resource usage
- Optimize MT5 data access

## Best Practices

1. **Start Small:** Test with 1-2 months before running longer periods
2. **Compare Periods:** Test different market conditions
3. **Validate Settings:** Ensure parameters match live trading
4. **Cross-Validate:** Compare with offline backtest script
5. **Document Results:** Save configurations that perform well
6. **Consider Slippage:** Real trading may have additional costs
7. **Market Conditions:** Past performance ≠ future results

## Future Enhancements

### Planned Features
- [ ] Multi-symbol backtesting
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] Parameter optimization grid search
- [ ] Export results to PDF/CSV
- [ ] Comparison mode (multiple configs)
- [ ] Real-time progress updates
- [ ] Saved configuration presets

## Related Documentation
- [Backtest Results Analysis](BACKTEST_RESULTS_ANALYSIS.md)
- [Trend Filter Guide](TREND_FILTER_GUIDE.md)
- [Live Trading Implementation](LIVE_TRADING_IMPLEMENTATION_PLAN.md)
- [ML Project Plan](ML_PROJECT_PLAN.md)

## Support

For issues or questions:
1. Check backend logs: `src/live_trading/logs/live_trading.log`
2. Review browser console for frontend errors
3. Verify API connectivity: `http://localhost:8000/api/backtest/status`
4. Consult main documentation: `MASTER_GUIDE.md`
