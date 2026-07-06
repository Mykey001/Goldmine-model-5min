# Fixes Applied - Feature Mismatch & Frontend Crash

## Date: 2026-07-06

## Issues Fixed

### 1. Feature Shape Mismatch (Backend)

**Problem:**
- Model expected 38 features but only 34 were being generated
- Error: `Feature shape mismatch, expected: 38, got 34`
- Missing features: `volume_ma`, `volume_ratio`, `volume_surge`, and temporal features (`hour`, `day_of_week`, `day_of_month`, `week_of_year`)

**Root Cause:**
- The `data/features/feature_names.json` file incorrectly included raw OHLCV columns (date, time, open, high, low, close, tickvol, vol, spread)
- The `signal_generator.py` was filtering these out, creating a mismatch
- The file was missing the volume features that are generated in live trading
- **CRITICAL**: The bot runs from `src/live_trading/` directory but was looking for `data/features/feature_names.json` with a relative path, which doesn't exist in that location

**Solution:**
1. Updated `data/features/feature_names.json` to include only the actual 38 feature columns:
   - Removed raw OHLCV columns
   - Added volume features (volume_ma, volume_ratio, volume_surge)
   - Confirmed all temporal features are present
   
2. Updated `signal_generator.py` `_load_feature_names()` method:
   - Removed the filtering logic (no longer needed)
   - **Fixed the file path to use absolute path relative to project root**
   - Now correctly finds the file from `src/live_trading/` execution context

**Verification:**
```python
# Total features: 38
Features include:
- RSI features (7): rsi, rsi_oversold, rsi_overbought, rsi_cross_above_35, rsi_cross_below_65, rsi_momentum, rsi_slope
- Momentum features (5): momentum_1, momentum_3, momentum_5, momentum_10, momentum_20
- Volatility features (2): volatility_10, volatility_20
- Candle patterns (5): candle_body, candle_range, upper_wick, lower_wick, body_ratio
- Trend indicators (9): ema_20, ema_50, price_above_ema20, price_above_ema50, ema_distance, macd, macd_signal, macd_diff, adx
- Volume features (3): volume_ma, volume_ratio, volume_surge
- Temporal features (4): hour, day_of_week, day_of_month, week_of_year
- Session features (3): session_asian, session_european, session_us
```

### 2. Frontend Crash (OpenPositions Component)

**Problem:**
- Frontend crashed with error: "An error occurred in the <OpenPositions> component"
- React error boundary triggered
- WebSocket connection issues visible in console

**Root Cause:**
- The `OpenPositions.tsx` component was accessing position fields without null checks
- When position data was incomplete or undefined, it caused runtime errors
- Fields like `profit`, `entry_price`, `current_price`, `tp`, `sl`, `volume`, `open_time` could be undefined

**Solution:**
Updated `OpenPositions.tsx` to add null coalescing operators (`??`) for all position fields:
- Changed `position.profit || 0` to `position.profit ?? 0`
- Changed `position.entry_price || 0` to `position.entry_price ?? 0`
- Changed `position.current_price || 0` to `position.current_price ?? 0`
- Changed `position.tp || 0` to `position.tp ?? 0`
- Changed `position.sl || 0` to `position.sl ?? 0`
- Changed `position.volume` to `position.volume ?? 0`
- Changed `formatRelativeTime(position.open_time)` to `position.open_time ? formatRelativeTime(position.open_time) : 'N/A'`
- Added `?? 'N/A'` fallbacks for string fields

**Why `??` instead of `||`:**
- `||` treats 0, empty string, and false as falsy (incorrect for prices that could be 0)
- `??` only treats null and undefined as falsy (correct behavior)

### 3. API Crash (AttributeError on bot.executor)

**Problem:**
- Backend API crashed with: `AttributeError: 'NoneType' object has no attribute 'get_open_positions'`
- Error occurred when frontend tried to fetch open positions before bot was fully initialized
- `bot.executor` is None until MT5 connection is established

**Root Cause:**
- The REST API endpoints assumed `bot.executor` would always be initialized
- The frontend queries the API immediately on load, before MT5 is connected
- No null checks on executor before calling methods

**Solution:**
Updated `rest_api.py` to handle uninitialized executor gracefully:
1. `get_open_positions()`: Returns empty list `[]` if executor is None
2. `close_position()`: Raises HTTP 503 with clear message if executor is None
3. `modify_position()`: Raises HTTP 503 with clear message if executor is None
4. `close_all_positions()`: Raises HTTP 503 with clear message if executor is None

This allows the frontend to safely query the API during startup without crashes.

## Files Modified

1. `data/features/feature_names.json` - Corrected feature list (38 features, no OHLCV columns)
2. `src/live_trading/signal_generator.py` - Fixed file path resolution and simplified feature loading
3. `frontend/src/components/dashboard/OpenPositions.tsx` - Added null safety
4. `src/live_trading/api/rest_api.py` - Added executor null checks

## Testing

After applying these fixes:
1. Backend should correctly generate 38 features matching the model
2. Feature names file is correctly located regardless of working directory
3. Frontend should handle incomplete position data gracefully
4. API endpoints handle uninitialized executor without crashing
5. No more "Feature shape mismatch" errors
6. No more React component crashes
7. No more AttributeError crashes

## Next Steps

1. **IMPORTANT**: Restart the trading bot backend to pick up the changes
2. Refresh the frontend browser to reload the component
3. Monitor logs to confirm features are now correctly aligned (should see 38 features loaded)
4. Test with actual position data to verify frontend stability
5. Verify API returns empty positions array before MT5 connection

## Technical Details

### Path Resolution Issue
The bot is started from `src/live_trading/` directory via the startup script:
```powershell
cd src\live_trading; python run.py
```

This means relative paths like `data/features/feature_names.json` resolve to:
- ❌ `src/live_trading/data/features/feature_names.json` (doesn't exist)
- ✅ `<project_root>/data/features/feature_names.json` (correct location)

The fix uses `__file__` to get the script location and navigates up to project root:
```python
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
feature_file = os.path.join(project_root, 'data', 'features', 'feature_names.json')
```
