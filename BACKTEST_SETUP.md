# Backtest Feature Setup Guide

## Quick Setup

The backtest feature is now integrated into your live trading system. Follow these steps to start using it.

## Prerequisites

✅ All required dependencies are already installed:
- Backend: pandas, numpy, MetaTrader5, ta, joblib, FastAPI
- Frontend: React, Recharts, TypeScript, Tailwind CSS

✅ Trained ML model exists at: `models/final/xgboost_model.pkl`

✅ MT5 connection configured and working

## Installation Steps

### No Installation Required! 🎉

The backtest feature has been integrated into your existing codebase. All new files have been created:

**Backend:**
- `src/live_trading/backtest_engine.py` ✅
- Updated `src/live_trading/api/rest_api.py` ✅
- Updated `src/live_trading/run.py` ✅

**Frontend:**
- `frontend/src/components/dashboard/BacktestPanel.tsx` ✅
- `frontend/src/components/dashboard/BacktestResults.tsx` ✅
- `frontend/src/components/dashboard/BacktestChart.tsx` ✅
- Updated `frontend/src/App.tsx` ✅

**Documentation:**
- `docs/BACKTEST_INTERFACE_GUIDE.md` ✅
- `BACKTEST_FEATURE_IMPLEMENTATION.md` ✅

## Starting the System

### Option 1: Using Batch File (Recommended for Windows)

```cmd
START_SYSTEM.bat
```

This will:
1. Start the backend API server
2. Start the frontend development server
3. Open browser to http://localhost:5173

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd src/live_trading
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Accessing the Backtest Interface

1. Open browser to: `http://localhost:5173`
2. Click the **"Backtest"** tab in the navigation bar
3. You'll see the Backtest Configuration panel

## Running Your First Backtest

### Step-by-Step Guide

1. **Configure Basic Settings:**
   - Symbol: `XAUUSDm` (default)
   - Start Date: `2025-05-01`
   - End Date: `2025-07-03`

2. **Set Risk Parameters:**
   - Take Profit: `100` pips
   - Stop Loss: `50` pips
   - Lot Size: `0.01`
   - Starting Capital: `$10,000`

3. **Advanced Settings (Optional):**
   - Min Confidence: `0.5` (50%)
   - ☑️ Use H1 Trend Filter
   - H1 EMA Period: `200`

4. **Run the Backtest:**
   - Click the **"Run Backtest"** button
   - Wait 30-60 seconds for processing
   - View results below

## What to Expect

### Processing Time
- **Short backtest** (1-2 months): 20-30 seconds
- **Medium backtest** (3-4 months): 40-60 seconds
- **Long backtest** (6+ months): 60-120 seconds

### Results Display

After processing completes, you'll see:

1. **Performance Summary Card**
   - Performance badge (Excellent/Good/Fair/Poor)
   - Net profit and return %
   - Win rate
   - Profit factor
   - Final equity

2. **Detailed Metrics**
   - Trading performance breakdown
   - Risk metrics
   - Configuration summary

3. **Visualizations**
   - Equity curve chart
   - Drawdown chart
   - Profit/loss distribution
   - Trade log table

## Verifying Installation

### Backend Check

Test the API endpoint:
```bash
curl http://localhost:8000/api/backtest/status
```

Expected response:
```json
{
  "available": true,
  "model_loaded": true
}
```

### Frontend Check

1. Open browser dev tools (F12)
2. Go to Console tab
3. Should see no errors
4. Network tab should show successful API calls

### MT5 Connection Check

1. Ensure MT5 is running
2. Check connection in "Live Trading" tab
3. Verify symbol `XAUUSDm` is in Market Watch

## Troubleshooting

### "Model not loaded" Error

**Solution:**
```bash
# Verify model file exists
ls models/final/xgboost_model.pkl

# If missing, train the model:
python scripts/03_model_training.py
```

### "No data returned" Error

**Possible causes:**
1. MT5 not connected
2. Symbol not in Market Watch
3. No historical data for date range

**Solution:**
1. Open MT5
2. Add `XAUUSDm` to Market Watch
3. Ensure broker provides historical data
4. Try a different date range

### "Connection refused" Error

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/api/health

# If not running, start it:
cd src/live_trading
python run.py
```

### Charts Not Displaying

**Solution:**
1. Check browser console for errors
2. Verify Recharts is installed:
   ```bash
   cd frontend
   npm list recharts
   ```
3. If missing, install:
   ```bash
   npm install recharts@^2.15.0
   ```

## Testing the Feature

### Test 1: Basic Backtest
```
Symbol: XAUUSDm
Date: 2025-06-01 to 2025-06-30
TP: 100, SL: 50
Expected: Results in ~30 seconds
```

### Test 2: With H1 Filter
```
Same as Test 1, but:
☑️ Use H1 Trend Filter
H1 EMA: 200
Expected: Fewer signals, possibly higher win rate
```

### Test 3: Different Parameters
```
TP: 50, SL: 30
Confidence: 0.7
Expected: More conservative, fewer trades
```

## Configuration Tips

### For Better Performance
- Use shorter date ranges
- Start with 1-2 months
- Gradually increase range

### For Better Accuracy
- Enable H1 trend filter
- Increase min confidence (0.6-0.7)
- Test multiple time periods

### For More Trades
- Lower min confidence (0.4-0.5)
- Disable H1 filter
- Use wider date range

## API Integration Example

If you want to call the API programmatically:

```python
import requests
from datetime import datetime

url = "http://localhost:8000/api/backtest/run"
params = {
    "symbol": "XAUUSDm",
    "start_date": "2025-05-01T00:00:00Z",
    "end_date": "2025-07-03T00:00:00Z",
    "use_h1_filter": True,
    "h1_ema_period": 200,
    "min_confidence": 0.5,
    "tp_pips": 100,
    "sl_pips": 50,
    "lot_size": 0.01,
    "starting_capital": 10000
}

response = requests.post(url, params=params)
results = response.json()

print(f"Net Profit: ${results['metrics']['net_profit']:.2f}")
print(f"Win Rate: {results['metrics']['win_rate']:.1f}%")
```

## Next Steps

1. ✅ Run your first backtest
2. ✅ Compare with offline backtest script results
3. ✅ Experiment with different parameters
4. ✅ Test different time periods
5. ✅ Analyze performance metrics
6. ✅ Use insights to optimize live trading

## Additional Resources

- **User Guide**: `docs/BACKTEST_INTERFACE_GUIDE.md`
- **Implementation Details**: `BACKTEST_FEATURE_IMPLEMENTATION.md`
- **Backtest Analysis**: `docs/BACKTEST_RESULTS_ANALYSIS.md`
- **Master Guide**: `MASTER_GUIDE.md`

## Support

If you encounter issues:

1. **Check Logs:**
   ```bash
   tail -f src/live_trading/logs/live_trading.log
   ```

2. **Check Browser Console:**
   - Open Dev Tools (F12)
   - Look for errors in Console tab

3. **Verify Services:**
   ```bash
   # Backend
   curl http://localhost:8000/api/health
   
   # Frontend
   curl http://localhost:5173
   ```

4. **Restart System:**
   ```bash
   # Stop all services (Ctrl+C)
   # Then restart with START_SYSTEM.bat
   ```

## Feature Status

✅ **Implemented**: Full backtest pipeline
✅ **Tested**: Backend engine verified
✅ **Documented**: Comprehensive guides available
✅ **Ready**: Production-ready for use

## Summary

The backtest feature is fully integrated and ready to use. No additional installation is required. Simply start the system and click the "Backtest" tab to begin testing strategies!

**Happy Backtesting! 🚀📈**
