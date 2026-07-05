# 🚀 Quick Start Guide - Goldmine ML Live Trading

## Prerequisites

- ✅ Python 3.10+
- ✅ MetaTrader 5 installed (at least one terminal)
- ✅ MT5 Demo account (for testing)
- ✅ Trained XGBoost model (`models/final/xgboost_model.pkl`)

---

## Step 1: Install Dependencies (2 minutes)

```bash
# Option A: Use batch script (Windows)
install_dependencies.bat

# Option B: Manual installation
pip install -r requirements-live.txt
```

---

## Step 2: Test Setup (1 minute)

```bash
cd src\live_trading
python test_setup.py
```

**Expected Output:**
```
✓ PASS - Package Imports
✓ PASS - Database Connection  
✓ PASS - MT5 Terminal Discovery (found 3 terminals)
✓ PASS - Model File
```

If any test fails, check `SETUP_INSTRUCTIONS.md`

---

## Step 3: Start the System (30 seconds)

```bash
cd src\live_trading
python run.py
```

**You should see:**
```
============================================================
GOLDMINE ML LIVE TRADING SYSTEM
============================================================
Configuration loaded:
  API: 0.0.0.0:8000
  Database: postgres://avnadmin...
  Model: models/final/xgboost_model.pkl
  Max Daily Loss: $400.0
  Min Confidence: 0.5

Starting trading bot thread...
Starting API server on 0.0.0.0:8000...
API Docs: http://localhost:8000/docs
WebSocket: ws://localhost:8000/ws

============================================================
SYSTEM READY - Waiting for connections...
============================================================
```

---

## Step 4: Open API Documentation

Open browser: **http://localhost:8000/docs**

You'll see interactive API documentation with all endpoints!

---

## Step 5: Connect to MT5

### Option A: Using API Docs (Browser)

1. Go to http://localhost:8000/docs
2. Find `POST /api/terminals/connect`
3. Click "Try it out"
4. Fill in:
   ```json
   {
     "terminal_id": "your_terminal_id",
     "account": 12345678,
     "password": "your_password",
     "server": "YourBroker-Demo"
   }
   ```
5. Click "Execute"

### Option B: Using curl

```bash
# 1. Discover terminals
curl http://localhost:8000/api/terminals/discover

# Copy a terminal_id from response

# 2. Connect
curl -X POST http://localhost:8000/api/terminals/connect \
  -H "Content-Type: application/json" \
  -d '{
    "terminal_id": "abc12345",
    "account": 12345678,
    "password": "your_password",
    "server": "YourBroker-Demo"
  }'
```

---

## Step 6: Test the System

### Check Connection Status

```bash
curl http://localhost:8000/api/connection/status
```

### Get Account Info

```bash
curl http://localhost:8000/api/account/info
```

### Get Available Symbols

```bash
curl http://localhost:8000/api/symbols/available
```

### Select Trading Symbol

```bash
curl -X POST http://localhost:8000/api/symbols/select \
  -H "Content-Type: application/json" \
  -d '{"symbol": "XAUUSDm"}'
```

---

## Step 7: Monitor Trading

The system will now:
1. ✅ Detect new M5 bars
2. ✅ Generate ML signals
3. ✅ Execute trades (if signal is strong)
4. ✅ Monitor positions
5. ✅ Save to database
6. ✅ Broadcast via WebSocket

### View Open Positions

```bash
curl http://localhost:8000/api/positions/open
```

### View Recent Signals

```bash
curl http://localhost:8000/api/signals/history
```

### View Performance Metrics

```bash
curl http://localhost:8000/api/metrics/summary
```

---

## 🔍 Monitoring & Logs

### View Live Logs

The system logs everything to:
- **Console** (real-time)
- **File**: `logs/live_trading.log`

### Check System Health

```bash
curl http://localhost:8000/api/health
```

---

## 🛑 Emergency Stop

### Close All Positions

```bash
curl -X POST http://localhost:8000/api/positions/close_all
```

### Stop the System

Press `Ctrl+C` in the terminal running `run.py`

---

## 🎮 WebSocket Connection (For Frontend)

### JavaScript Example

```javascript
const socket = new WebSocket('ws://localhost:8000/ws');

socket.onopen = () => {
  console.log('Connected to trading system');
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  // Handle different event types
  if (data.type === 'new_signal') {
    console.log('New signal:', data.data);
  } else if (data.type === 'trade_opened') {
    console.log('Trade opened:', data.data);
  } else if (data.type === 'trade_closed') {
    console.log('Trade closed:', data.data);
  }
};
```

---

## ⚙️ Configuration

Edit `.env` file to change:

```env
# Risk limits
MAX_DAILY_LOSS=400
MAX_POSITIONS=1
MIN_CONFIDENCE=0.5

# Trading parameters
TP_PIPS=100
SL_PIPS=50
DEFAULT_LOT_SIZE=0.01
```

Changes take effect on restart.

---

## 🐛 Troubleshooting

### "Database connection failed"
- Check internet connection
- Verify DATABASE_URL in `.env`

### "MT5 initialization failed"
- Make sure MT5 is installed
- Try running MT5 manually first

### "Model file not found"
- Train model first: `python scripts/03_model_training.py`
- Or check path in `.env`: `MODEL_PATH=models/final/xgboost_model.pkl`

### "No signals generated"
- Wait for M5 bar close (every 5 minutes)
- Check logs: `logs/live_trading.log`
- Verify symbol is enabled in MT5

---

## 📚 Next Steps

1. **Test on Demo**: Run for a day to verify everything works
2. **Build Frontend**: Create React dashboard (Phase 3)
3. **Monitor Performance**: Check metrics daily
4. **Adjust Risk**: Fine-tune based on results

---

## ⚠️ Important Reminders

- ❗ **ALWAYS test on DEMO account first**
- ❗ **Never run untested code on live account**
- ❗ **Monitor the system continuously for first 24 hours**
- ❗ **Keep daily loss limits conservative**
- ❗ **Have emergency stop procedure ready**

---

## 📞 Support

Check these files for more info:
- `BACKEND_COMPLETE.md` - Full backend documentation
- `IMPLEMENTATION_STATUS.md` - Progress tracker
- `docs/LIVE_TRADING_IMPLEMENTATION_PLAN.md` - Complete plan
- `SETUP_INSTRUCTIONS.md` - Detailed setup

---

## 🎉 You're Ready!

Your live trading system is now operational. 

**System Status:** ✅ Backend 100% Complete

**What You Can Do:**
- Connect to any MT5 terminal
- Trade any symbol
- Generate ML signals
- Execute trades automatically
- Monitor performance
- Access via REST API
- Get real-time updates via WebSocket

**Next:** Build the React frontend for a beautiful UI! 🚀
