# Task 5: Volatility Filter & CSV Export - COMPLETE

**Date**: 2026-07-07  
**Status**: ✅ Implementation Complete - Ready for Testing

---

## Summary

Successfully implemented volatility filter parameter and CSV export functionality for the backtest system. All code changes are complete and the system is ready for testing.

---

## Implementation Details

### 1. Backend API Endpoints (`src/live_trading/api/rest_api.py`)

#### `/api/backtest/run` Endpoint
Added three new parameters:
- `use_volatility_filter: bool = False` - Enable/disable volatility filtering
- `min_atr: float = 0.5` - Minimum ATR threshold
- `max_atr: float = 5.0` - Maximum ATR threshold

These parameters are passed through to the backtest engine in the config dictionary.

#### `/api/backtest/export/csv` Endpoint
**New endpoint** that:
- Accepts backtest results as JSON
- Converts trades to pandas DataFrame
- Saves to `results/exports/` directory
- Returns filename, filepath, and trade count
- Filename format: `backtest_{symbol}_{timestamp}.csv`
- Handles errors gracefully

---

### 2. Backend Backtest Engine (`src/live_trading/backtest_engine.py`)

#### Volatility Filter in `generate_signals()` Method
```python
# Apply volatility filter if enabled (from config)
use_volatility_filter = config.get('use_volatility_filter', False) if config else False
if use_volatility_filter and 'adx' in data.columns:
    min_atr = config.get('min_atr', 0.5)
    max_atr = config.get('max_atr', 5.0)
    
    # Calculate ATR if not present
    if 'atr' not in data.columns:
        from ta.volatility import AverageTrueRange
        atr_indicator = AverageTrueRange(data['high'], data['low'], data['close'], window=14)
        data['atr'] = atr_indicator.average_true_range()
    
    signals_before_vol = (data['signal'] != -1).sum()
    
    # Filter out signals where ATR is outside acceptable range
    low_volatility = data['atr'] < min_atr
    high_volatility = data['atr'] > max_atr
    
    data.loc[low_volatility, 'signal'] = -1
    data.loc[high_volatility, 'signal'] = -1
    
    signals_after_vol = (data['signal'] != -1).sum()
    filtered_vol = signals_before_vol - signals_after_vol
    logger.info(f"Volatility filter applied: {signals_before_vol} -> {signals_after_vol} signals ({filtered_vol} filtered)")
```

**Behavior**:
- Calculates ATR(14) using ta-lib
- Filters out signals when ATR < min_atr (low volatility)
- Filters out signals when ATR > max_atr (high volatility)
- Logs number of signals filtered
- Only activates when `use_volatility_filter=True` in config

---

### 3. Frontend UI (`frontend/src/components/dashboard/BacktestPanel.tsx`)

#### New State Variables
```typescript
useVolatilityFilter: boolean;  // Default: false
minAtr: number;                 // Default: 0.5
maxAtr: number;                 // Default: 5.0
```

#### Volatility Filter UI (in Advanced Settings)
- Checkbox to enable/disable volatility filter
- Two input fields for Min ATR and Max ATR
- Conditional rendering (only shows inputs when checkbox is checked)
- Proper styling matching existing design

#### Export to CSV Button
```typescript
const exportToCSV = async () => {
  if (!results) return;
  
  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/backtest/export/csv`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(results),
    });

    if (response.ok) {
      const data = await response.json();
      alert(`✅ Exported ${data.trades_count} trades to ${data.filename}`);
    } else {
      alert('❌ Export failed');
    }
  } catch (err) {
    console.error('Export error:', err);
    alert('❌ Export failed');
  }
};
```

**Features**:
- Button displayed above results (only when results exist)
- Green styling to differentiate from backtest run button
- Sends entire results object to backend
- Shows success/failure alert with filename
- Error handling included

---

## Testing Checklist

### Prerequisites
- [x] MT5 connected via Live Trading tab
- [ ] Backend server running (`python src/live_trading/run.py`)
- [ ] Frontend running (`npm run dev` in frontend folder)
- [ ] Model loaded (`models/final/xgboost_model.pkl` exists)

### Test 1: Volatility Filter OFF (Baseline)
1. [ ] Run backtest with default settings
2. [ ] Note total trades generated
3. [ ] Verify results match previous runs

### Test 2: Volatility Filter ON - Low ATR Filter
1. [ ] Enable volatility filter
2. [ ] Set min_atr = 1.0, max_atr = 10.0
3. [ ] Run backtest
4. [ ] Check logs for: "Volatility filter applied: X -> Y signals (Z filtered)"
5. [ ] Verify fewer trades than baseline (signals filtered in low volatility)

### Test 3: Volatility Filter ON - High ATR Filter
1. [ ] Enable volatility filter
2. [ ] Set min_atr = 0.1, max_atr = 2.0
3. [ ] Run backtest
4. [ ] Check logs for filtered signal count
5. [ ] Verify fewer trades than baseline (signals filtered in high volatility)

### Test 4: CSV Export
1. [ ] Run successful backtest (any configuration)
2. [ ] Click "Export to CSV" button
3. [ ] Verify success alert shows filename
4. [ ] Check `results/exports/` directory exists
5. [ ] Verify CSV file created with correct naming: `backtest_XAUUSDm_YYYYMMDD_HHMMSS.csv`
6. [ ] Open CSV file and verify:
   - [ ] All trade fields present (direction, entry_time, entry_price, exit_time, exit_price, profit, exit_reason, confidence)
   - [ ] Data is properly formatted
   - [ ] Number of rows matches trade count in metrics

### Test 5: Export Error Handling
1. [ ] Try to export with no results
2. [ ] Verify appropriate error handling

---

## File Locations

### Backend Files
- `src/live_trading/api/rest_api.py` - API endpoints
- `src/live_trading/backtest_engine.py` - Backtest logic

### Frontend Files
- `frontend/src/components/dashboard/BacktestPanel.tsx` - Main UI component

### Export Directory
- `results/exports/` - CSV files saved here (created automatically)

---

## Expected Behavior

### Volatility Filter
**Purpose**: Filter out trading signals during periods of extreme market conditions

**How it works**:
1. Calculates ATR(14) for all M5 candles
2. For each signal generated by the model:
   - If ATR < min_atr: Signal rejected (market too quiet)
   - If ATR > max_atr: Signal rejected (market too volatile)
   - Otherwise: Signal accepted

**Use cases**:
- Avoid trading during low liquidity periods
- Avoid trading during news events or high volatility
- Optimize for specific market conditions

**Default values**:
- min_atr = 0.5
- max_atr = 5.0
- Filter disabled by default

### CSV Export

**Purpose**: Export all trade details for further analysis in Excel, Python, or other tools

**Export includes**:
- Trade direction (BUY/SELL)
- Entry time and price
- Exit time and price
- Profit/loss
- Exit reason (TP/SL)
- Model confidence score

**File format**:
```
direction,entry_time,entry_price,tp,sl,confidence,exit_price,exit_time,profit,exit_reason
BUY,2025-05-01T08:00:00,2345.60,2356.60,2340.60,0.78,2356.60,2025-05-01T10:30:00,110.0,TP
SELL,2025-05-01T14:00:00,2352.40,2342.40,2357.40,0.65,2342.40,2025-05-01T16:15:00,100.0,TP
...
```

---

## Next Steps

1. **Start Backend** (if not running):
   ```bash
   cd c:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min
   python src/live_trading/run.py
   ```

2. **Start Frontend** (if not running):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Connect MT5**:
   - Open frontend in browser
   - Go to "Live Trading" tab
   - Connect to MT5 terminal
   - Select XAUUSDm symbol

4. **Test Backtest Tab**:
   - Go to "Backtest" tab
   - Configure date range and parameters
   - Enable/disable volatility filter
   - Run backtest
   - Review results
   - Export to CSV

---

## Known Issues & Limitations

### Volatility Filter
- Uses ATR(14) as volatility measure
- ATR thresholds need to be tuned for specific symbols and timeframes
- Gold (XAUUSD) typical ATR range: 0.5 - 5.0
- Other symbols may require different ranges

### CSV Export
- Exports to server-side directory (`results/exports/`)
- Does not trigger browser download (file stays on server)
- For browser download, would need to return file as response

### General
- Model expects exactly 38 features (tickvol, vol, spread included)
- MT5 must be connected before running backtest
- Historical data availability depends on broker

---

## Success Criteria

✅ **Task 5 Complete When**:
1. [ ] Volatility filter can be enabled/disabled via UI
2. [ ] ATR min/max thresholds can be adjusted via UI
3. [ ] Volatility filter correctly filters signals based on ATR
4. [ ] Filter statistics logged in backend
5. [ ] CSV export button visible after backtest completes
6. [ ] CSV file created in `results/exports/` directory
7. [ ] CSV contains all trade details
8. [ ] All tests pass successfully

---

## Documentation Created

- `TASK5_VOLATILITY_CSV_COMPLETE.md` - This file
- All previous backtest documentation still valid:
  - `BACKTEST_FEATURE_SUMMARY.md`
  - `BACKTEST_INTERFACE_GUIDE.md`
  - `BACKTEST_QUICK_START.md`
  - `BACKTEST_FIXES_APPLIED.md`

---

**READY FOR TESTING** 🚀
