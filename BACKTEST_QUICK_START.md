# Backtest Feature - Quick Start Guide

## ⚠️ IMPORTANT: Connection Required

The backtest feature requires an **active MT5 connection**. Follow these steps in order:

## 🚀 Step-by-Step (First Time)

### Step 1: Start the System
```bash
START_SYSTEM.bat
```
Or manually:
```bash
# Terminal 1
cd src/live_trading
python run.py

# Terminal 2
cd frontend
npm run dev
```

### Step 2: Open Frontend
```
http://localhost:5173
```

### Step 3: Connect to MT5 (REQUIRED FIRST!)

**🔴 DO THIS FIRST - Very Important!**

1. Click **"Live Trading"** tab (not Backtest!)
2. Click **"Discover Terminals"** button
3. Select your MT5 terminal from the list
4. Enter your MT5 credentials
5. Click **"Connect"** button
6. Select symbol: **XAUUSDm**
7. ✅ Wait for **"Connected"** status (green)

### Step 4: Now Use Backtest

**✅ After connection is established:**

1. Click **"Backtest"** tab
2. Configure your backtest:
   - Symbol: XAUUSDm (already selected)
   - Start Date: 2025-06-01
   - End Date: 2025-06-30
   - Keep other defaults
3. Click **"Run Backtest"**
4. Wait 30-60 seconds
5. View results!

## 📊 Visual Workflow

```
┌─────────────────────────────────────────────────────────┐
│                    START SYSTEM                         │
│                 START_SYSTEM.bat                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              OPEN BROWSER                               │
│          http://localhost:5173                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│         🔴 CLICK "LIVE TRADING" TAB FIRST               │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │ 1. Discover Terminals                          │    │
│  │ 2. Select MT5 Terminal                         │    │
│  │ 3. Enter Credentials                           │    │
│  │ 4. Click "Connect"                             │    │
│  │ 5. Select Symbol (XAUUSDm)                     │    │
│  │ 6. ✅ Wait for "Connected" status              │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│         ✅ NOW CLICK "BACKTEST" TAB                      │
│                                                         │
│  ┌───────────────────────────────────────────────┐    │
│  │ 1. Configure parameters                        │    │
│  │ 2. Click "Run Backtest"                        │    │
│  │ 3. Wait for results                            │    │
│  │ 4. View metrics and charts                     │    │
│  └───────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## ❌ Common Mistake

**DON'T DO THIS:**
```
❌ Open Backtest tab immediately
❌ Try to run backtest without connecting
❌ Skip the Live Trading connection step
```

**Result:** "No data returned" error

## ✅ Correct Approach

**DO THIS:**
```
✅ Open Live Trading tab first
✅ Connect to MT5 terminal
✅ Wait for connection confirmation
✅ Then switch to Backtest tab
✅ Run backtest
```

**Result:** Backtest runs successfully!

## 🔧 Troubleshooting

### Error: "Failed to fetch M5 data"

**Solution:** You skipped the connection step!

1. Go back to "Live Trading" tab
2. Connect to MT5 terminal
3. Wait for "Connected" status
4. Return to "Backtest" tab
5. Try again

### Error: "MT5 not initialized"

**Solution:** Backend can't reach MT5

1. Check MT5 application is running
2. Ensure you're logged in to MT5
3. Restart backend if needed
4. Connect via Live Trading tab
5. Try backtest again

### Error: "Symbol not found"

**Solution:** Symbol not in Market Watch

1. Open MT5 application
2. Right-click Market Watch
3. Select "Symbols"
4. Find and enable XAUUSDm
5. Restart backend
6. Connect again

### Backtest is Slow

**Normal:** First backtest takes 30-60 seconds
- Fetching data from MT5
- Calculating 50+ features
- Running ML predictions
- Simulating trades

**If longer than 2 minutes:**
- Check date range (shorter = faster)
- Check system resources
- Check MT5 connection stability

## 📝 Quick Reference

### Minimum Date Range
- **Start:** At least 3 months of data recommended
- **End:** Not future dates
- **Typical:** 1-2 months for quick test

### Typical Configuration
```yaml
Symbol: XAUUSDm
Start Date: 2025-06-01
End Date: 2025-06-30
TP: 100 pips
SL: 50 pips
Lot Size: 0.01
Starting Capital: $10,000
Min Confidence: 0.5 (50%)
H1 Filter: ✓ Enabled
H1 EMA: 200
```

### Expected Results
- Processing Time: 30-60 seconds
- Total Trades: ~50-150 (depends on period)
- Metrics: Win rate, profit factor, etc.
- Charts: Equity curve, drawdown, distribution

## 🎯 Success Checklist

Complete this checklist for successful backtest:

- [ ] System started (backend + frontend)
- [ ] Browser open (http://localhost:5173)
- [ ] MT5 terminal running
- [ ] **"Live Trading" tab opened FIRST**
- [ ] Terminal discovered and connected
- [ ] Symbol selected (XAUUSDm)
- [ ] "Connected" status showing (green)
- [ ] **NOW switched to "Backtest" tab**
- [ ] Parameters configured
- [ ] "Run Backtest" clicked
- [ ] Results displayed successfully

## 💡 Pro Tips

1. **Always connect first** - Make it a habit to open Live Trading tab before Backtest

2. **Use recent dates** - More recent data is more reliable and faster to fetch

3. **Start small** - Test with 1 month before running longer periods

4. **Check logs** - If issues occur, check backend logs for details

5. **Verify in MT5** - If backtest fails, open MT5 and verify:
   - You're logged in
   - Symbol is in Market Watch
   - Historical data is available (open a chart)

## 📚 More Documentation

- **Full Guide**: `docs/BACKTEST_INTERFACE_GUIDE.md`
- **Setup**: `BACKTEST_SETUP.md`
- **Connection Issues**: `BACKTEST_MT5_CONNECTION_ISSUE.md`
- **Fixes Applied**: `BACKTEST_FIXES_APPLIED.md`

## 🎉 Summary

```
1. Start System
2. Open Browser
3. Live Trading Tab → Connect to MT5
4. Backtest Tab → Run Backtest
5. View Results!
```

**Remember**: Live Trading tab connection is **required** before using Backtest!

---

**Quick Command:**
```bash
START_SYSTEM.bat
# Then: Live Trading → Connect → Backtest → Run
```

**Status:** Ready to use! 🚀
