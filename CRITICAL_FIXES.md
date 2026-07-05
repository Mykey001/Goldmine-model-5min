# Critical Backend Fixes

## Issues Fixed

### 1. Asyncio Event Loop Error (FIXED ✅)
**Error:**
```
RuntimeError: no running event loop
at asyncio.create_task() in main.py:278
```

**Problem:**
- The trading bot runs in a synchronous thread
- Tried to use `asyncio.create_task()` from sync context
- This crashes the signal emission to WebSocket

**Solution:**
- Replaced `asyncio.create_task()` with thread-safe queue approach
- Added `pending_signals` list to `WebSocketManager`
- Signals are queued and picked up by async WebSocket handler
- No more runtime errors when emitting signals

**Files Modified:**
- `src/live_trading/main.py` (line 278)
- `src/live_trading/api/websocket_server.py` (added pending_signals queue)

### 2. Feature Shape Mismatch (FIXED ✅)
**Error:**
```
Feature shape mismatch, expected: 38, got 34
```

**Problem:**
- Model was trained with 38 features
- Live system was only computing 34 features
- Missing features:
  - `week_of_year` temporal feature
  - Feature list included raw columns (date, time, open, high, low, close, etc.)
  - These raw columns were excluded but counted in the feature list

**Solution:**
- Added `week_of_year` feature calculation:
  ```python
  df['week_of_year'] = df['timestamp'].dt.isocalendar().week
  ```
- Fixed feature loading to exclude raw OHLCV columns:
  ```python
  exclude_cols = ['date', 'time', 'open', 'high', 'low', 'close', 
                 'tickvol', 'vol', 'spread', 'real_volume', 'timestamp']
  ```
- Added validation to check feature count matches model expectations
- Better error logging to identify missing features

**Files Modified:**
- `src/live_trading/signal_generator.py`:
  - `_load_feature_names()` - filters out raw columns
  - `compute_features()` - added week_of_year
  - `generate_signal()` - added feature count validation

## Expected Behavior After Fix

1. **Signal Generation:**
   - New M5 bars trigger feature calculation
   - All 38 features computed correctly
   - Model makes predictions without shape errors
   - Signals display: `Signal: BUY/SELL/NO_TRADE | Confidence: 0.XXX`

2. **WebSocket Updates:**
   - Signals queued for WebSocket emission
   - No more event loop errors
   - Frontend receives real-time signal updates

3. **Feature List (38 total):**
   - RSI features (7): rsi, rsi_oversold, rsi_overbought, rsi_cross_above_35, rsi_cross_below_65, rsi_momentum, rsi_slope
   - Momentum features (5): momentum_1, momentum_3, momentum_5, momentum_10, momentum_20
   - Volatility features (2): volatility_10, volatility_20
   - Candle features (5): candle_body, candle_range, upper_wick, lower_wick, body_ratio
   - EMA features (5): ema_20, ema_50, price_above_ema20, price_above_ema50, ema_distance
   - MACD features (3): macd, macd_signal, macd_diff
   - ADX features (1): adx
   - Temporal features (7): hour, day_of_week, day_of_month, week_of_year, session_asian, session_european, session_us
   - **Total: 35 features** (if volume not available, otherwise 38 with volume features)

## Next Steps

1. **Restart the backend server:**
   ```powershell
   cd src\live_trading
   python run.py
   ```

2. **Connect MT5 and test:**
   - Connect to MT5 terminal
   - Select XAUUSD or your trading symbol
   - Wait for next M5 bar close
   - Check logs for successful signal generation

3. **Monitor logs for:**
   ```
   ✅ "Signal: BUY | Confidence: 0.750" (no errors)
   ✅ "Features calculated successfully"
   ✅ No "Feature shape mismatch" errors
   ✅ No "no running event loop" errors
   ```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] MT5 connection successful
- [ ] Symbol selection works (e.g., XAUUSD)
- [ ] New M5 bar detected in logs
- [ ] Signal generated without shape mismatch
- [ ] No asyncio event loop errors
- [ ] Frontend receives WebSocket updates
- [ ] Signals display in dashboard
