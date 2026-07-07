# Backtest MT5 Connection Issue - Solution

## Issue

```
No data returned for XAUUSDm M5
Backtest failed: Failed to fetch M5 data
```

## Root Cause

The backtest engine cannot fetch data from MT5 because:

1. **MT5 Terminal State**: The MT5 terminal connection is managed by the live trading bot
2. **Symbol Selection**: The symbol must be properly selected in MT5 Market Watch
3. **Connection Timing**: The backtest tries to fetch data before MT5 is fully initialized
4. **Broker Data**: The broker may not have data for the requested date range

## Solution

### Prerequisites Before Running Backtest

**You MUST do these steps FIRST:**

1. **Connect to MT5 Terminal** (via Live Trading tab):
   - Go to "Live Trading" tab
   - Click "Discover Terminals"
   - Connect to your MT5 terminal
   - Select your symbol (XAUUSDm)
   - ✅ Wait for "Connected" status

2. **Verify Symbol is Active**:
   - Check that the symbol appears in MT5 Market Watch
   - Ensure historical data is available

3. **Then Use Backtest Tab**:
   - Now switch to "Backtest" tab
   - Configure your backtest
   - Run backtest

## Updated Workflow

### Correct Order:

```
Step 1: Start System
   ↓
Step 2: Open Frontend (http://localhost:5173)
   ↓
Step 3: Go to "Live Trading" Tab
   ↓
Step 4: Connect to MT5 Terminal
   ↓
Step 5: Select Symbol (XAUUSDm)
   ↓
Step 6: Wait for Connection Confirmation
   ↓
Step 7: Switch to "Backtest" Tab
   ↓
Step 8: Run Backtest
```

### Why This Order Matters:

- **MT5 Initialization**: The live trading bot handles MT5 connection
- **Symbol Selection**: Live trading ensures the symbol is enabled
- **Data Access**: Once connected, historical data becomes available
- **State Sharing**: Backtest engine uses the same MT5 connection

## Fixes Applied

### 1. Enhanced Error Messages

**In `backtest_engine.py`:**
```python
# Check if MT5 is initialized
if not mt5.terminal_info():
    logger.error("MT5 not initialized. Please connect to MT5 terminal first.")
    return None

# Ensure symbol is selected
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    logger.error(f"Symbol {symbol} not found")
    return None

if not symbol_info.visible:
    logger.info(f"Enabling symbol {symbol} in Market Watch...")
    if not mt5.symbol_select(symbol, True):
        logger.error(f"Failed to select symbol {symbol}")
        return None
```

### 2. Better User Guidance

**In `BacktestPanel.tsx`:**
```typescript
if (errorMessage.includes('No data returned') || errorMessage.includes('Failed to fetch')) {
  errorMessage = 'Failed to fetch data from MT5. Please ensure:\n' +
                '1. MT5 is running and connected\n' +
                '2. You are connected to a terminal (use Live Trading tab first)\n' +
                '3. The symbol exists and has historical data\n' +
                '4. The date range is valid for your broker';
}
```

### 3. MT5 State Checks

The backtest engine now:
- ✅ Checks if MT5 is initialized
- ✅ Verifies symbol exists
- ✅ Enables symbol in Market Watch if needed
- ✅ Provides detailed error messages with MT5 error codes

## Step-by-Step Fix

### Option 1: Use Live Trading First (Recommended)

1. **Open Live Trading Tab**
   ```
   http://localhost:5173 → "Live Trading" tab
   ```

2. **Connect to Terminal**
   - Click "Discover Terminals"
   - Select your terminal
   - Enter credentials
   - Click "Connect"

3. **Verify Connection**
   - Look for "Connected" status
   - Symbol should show in dashboard

4. **Now Use Backtest**
   - Switch to "Backtest" tab
   - Configure and run

### Option 2: Check MT5 Directly

1. **Open MT5 Application**
   - Ensure it's running
   - Check that you're logged in
   - Verify symbol in Market Watch

2. **Add Symbol if Missing**
   - Right-click Market Watch
   - Select "Symbols"
   - Find XAUUSDm
   - Click "Show"

3. **Verify Data Available**
   - Open chart for XAUUSDm
   - Check historical data exists
   - Try scrolling back to your date range

## Testing

### Test 1: Verify MT5 Connection

```python
import MetaTrader5 as mt5

# Test connection
if mt5.initialize():
    print("✅ MT5 initialized")
    
    # Test symbol
    symbol_info = mt5.symbol_info("XAUUSDm")
    if symbol_info:
        print(f"✅ Symbol found: {symbol_info.name}")
    else:
        print("❌ Symbol not found")
    
    mt5.shutdown()
else:
    print("❌ MT5 not initialized")
```

### Test 2: Verify Data Available

```python
import MetaTrader5 as mt5
from datetime import datetime

mt5.initialize()

# Try fetching data
rates = mt5.copy_rates_range(
    "XAUUSDm", 
    mt5.TIMEFRAME_M5,
    datetime(2025, 6, 1),
    datetime(2025, 6, 30)
)

if rates is not None and len(rates) > 0:
    print(f"✅ Data available: {len(rates)} candles")
else:
    error = mt5.last_error()
    print(f"❌ No data: {error}")

mt5.shutdown()
```

## Common Issues

### Issue 1: "MT5 not initialized"

**Cause:** MT5 connection not established

**Solution:**
1. Go to Live Trading tab first
2. Connect to terminal
3. Then use Backtest

### Issue 2: "Symbol not found"

**Cause:** Symbol not in Market Watch

**Solution:**
1. Open MT5
2. Add XAUUSDm to Market Watch
3. Restart backend

### Issue 3: "No data for date range"

**Cause:** Broker doesn't have historical data

**Solution:**
1. Check your broker's data availability
2. Try a more recent date range
3. Or download historical data in MT5

### Issue 4: Different symbol name

**Cause:** Your broker uses different naming

**Solution:**
1. Check exact symbol name in MT5
2. Use that exact name in backtest
3. Common variations:
   - XAUUSDm (micro lot)
   - XAUUSD (standard)
   - XAUUSD.a (alpha suffix)
   - Gold (some brokers)

## Quick Checklist

Before running backtest, verify:

- [ ] Backend is running (`python run.py`)
- [ ] Frontend is open (`http://localhost:5173`)
- [ ] MT5 terminal is running
- [ ] Connected via Live Trading tab
- [ ] Symbol is visible in Market Watch
- [ ] Symbol shows in dashboard
- [ ] "Connected" status is green
- [ ] Now switch to Backtest tab

## Updated Documentation

See these files for more details:
- `docs/BACKTEST_INTERFACE_GUIDE.md` - Updated with connection requirements
- `BACKTEST_SETUP.md` - Updated workflow
- `BACKTEST_FIXES_APPLIED.md` - Technical fixes

## Summary

The backtest feature requires an active MT5 connection. **Always connect via the Live Trading tab first**, then switch to the Backtest tab. This ensures MT5 is properly initialized and can provide historical data.

---

**Key Takeaway:** 
```
Live Trading Tab (Connect) → Backtest Tab (Use)
```

**Status:** ✅ Issue Identified and Documented  
**Solution:** Connection workflow clarified  
**User Action Required:** Connect to MT5 via Live Trading tab first
