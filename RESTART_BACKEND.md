# Restart Backend to Fix CSV Export

## What Changed
- Added detailed logging to CSV export endpoint
- Improved error handling (no longer throws HTTPException, returns error in JSON)
- Better error messages showing what went wrong
- Frontend now displays actual error messages instead of generic "Export failed"

## Steps to Apply the Fix

### 1. Stop the Backend Server
Find the terminal/command prompt running the backend and press `Ctrl+C` to stop it.

### 2. Restart the Backend
```bash
cd c:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min
python src/live_trading/run.py
```

### 3. Test the Export Again
1. Keep the frontend open (no need to restart)
2. Click "Export to CSV" button again
3. This time you'll see a detailed error message if it fails
4. Check the backend logs for detailed export information

## What to Look For

### In Frontend Alert
You should now see either:
- ✅ Success message with filename and full path
- ❌ Specific error message (not just "Export failed")

### In Backend Logs
You should see:
```
Export request received with keys: ['success', 'trades', 'equity_curve', 'metrics', 'config', 'symbol', 'start_date', 'end_date', 'total_candles']
Export directory: C:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min\results\exports
Number of trades to export: 3375
DataFrame created with columns: ['direction', 'entry_time', 'entry_price', 'tp', 'sl', 'confidence', 'exit_price', 'exit_time', 'profit', 'exit_reason']
Backtest exported successfully to C:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min\results\exports\backtest_XAUUSDm_20260707_HHMMSS.csv
```

## Common Issues

### Issue: "No trades to export"
**Cause**: The results object doesn't have trades or trades array is empty
**Fix**: Make sure the backtest ran successfully and generated trades before exporting

### Issue: Permission denied / File access error
**Cause**: Windows file permissions or antivirus blocking file creation
**Fix**: 
- Check if `results/exports/` directory can be created
- Try running as administrator
- Add exception in antivirus

### Issue: DataFrame error
**Cause**: Trade data format incompatible with pandas
**Solution**: The logs will show exactly which column/data caused the issue

## After Restart

Once backend is restarted:
1. Frontend will automatically reconnect
2. Try the export again
3. Check for the detailed error message or success confirmation
4. Verify the CSV file was created in `results/exports/` directory
