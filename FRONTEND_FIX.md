# Frontend Blank Page Fix

## Problems Fixed

### 1. Backend `/api/config` Crash (FIXED ✅)
The `/api/config` endpoint was crashing when accessed before MT5 connection was established.

**Error:**
```
AttributeError: 'NoneType' object has no attribute 'lot_size'
```

**Solution:** Added null checks with fallback to default config values in `src/live_trading/api/rest_api.py`

### 2. Frontend ConnectionPanel Crash (FIXED ✅)
The `ConnectionPanel` component was crashing because the API response format didn't match.

**Error:**
```
TypeError: Cannot read properties of undefined (reading 'length')
at ConnectionPanel (ConnectionPanel.tsx:146:26)
```

**Root Causes:**
- Backend returned `[...]` but frontend expected `{ terminals: [...] }`
- No error handling for failed API calls

**Solutions:**
- Updated backend `/api/terminals/discover` to return `{ terminals: [...] }`
- Added null-safe checks: `discoveredTerminals || []`
- Set `terminals` to empty array on error: `setTerminals([])`

### 3. SignalHistory Component Crash (FIXED ✅)
The `SignalHistory` component was crashing when displaying signals with missing price data.

**Error:**
```
TypeError: Cannot read properties of undefined (reading 'toFixed')
at formatPrice (formatters.ts:77:16)
at SignalHistory.tsx:74:22
```

**Root Causes:**
- Backend returning signals with undefined `entry_price` fields
- No null safety in formatPrice and other formatting functions
- Components not handling missing data gracefully

**Solutions:**
- Added null checks to all formatting functions in `formatters.ts`:
  - `formatPrice()` - returns '0.00' for null/undefined
  - `formatCurrency()` - defaults to 0
  - `formatPercentage()` - returns '0.00%' for null/undefined
  - `formatNumber()` - returns '0.00' for null/undefined
  - `getProfitColor()` - returns gray for null/undefined
  - `getProfitBgColor()` - returns gray for null/undefined
- Added fallback values in components:
  - `SignalHistory.tsx` - `signal.entry_price || 0`
  - `OpenPositions.tsx` - `position.entry_price || 0`, etc.

## Files Modified
1. `src/live_trading/api/rest_api.py`:
   - Line ~353: Fixed `/api/config` endpoint with null checks
   - Line ~368: Fixed `/api/config/update` endpoint with null checks  
   - Line ~120: Fixed `/api/terminals/discover` response format
2. `frontend/src/components/controls/ConnectionPanel.tsx`:
   - Line ~30: Added null-safe terminal array handling
3. `frontend/src/utils/formatters.ts`:
   - All formatting functions now handle null/undefined values
4. `frontend/src/components/dashboard/SignalHistory.tsx`:
   - Added fallback values for undefined prices
5. `frontend/src/components/dashboard/OpenPositions.tsx`:
   - Added fallback values for undefined prices and profits

## Next Steps
1. **Refresh the frontend:**
   - Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Or clear cache and refresh

2. **You should now see:**
   - Full UI with collapsible sidebar
   - ConnectionPanel with "Discover" button
   - SettingsPanel with risk management controls
   - Dashboard with metrics and charts
   - No more crashes when viewing signals or positions

3. **To connect MT5:**
   - Click "Discover" to find MT5 terminals
   - Select terminal from dropdown
   - Enter account, password, server
   - Enter trading symbol (e.g., XAUUSDm)
   - Click "Connect to MT5"

## Known Issue: MT5 Terminal Discovery
If no terminals are showing up after clicking "Discover":
- Ensure MetaTrader 5 is installed
- Check that `terminal64.exe` exists in your MT5 installation
- Backend logs will show discovery process
- The system searches these locations:
  - `C:\Program Files\MetaTrader 5`
  - `C:\Program Files (x86)\MetaTrader 5`
  - User AppData folders

