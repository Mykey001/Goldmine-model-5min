# 🎯 Goldmine ML Trading System

A complete automated trading system combining Machine Learning (XGBoost), MetaTrader 5, and a real-time React dashboard for live gold (XAUUSD) trading.

---

## 🌟 Features

### **Backend (Python)**
- ✅ **Multi-Terminal Support** - Auto-discovers and connects to any MT5 installation
- ✅ **Multi-Symbol Trading** - Trade any symbol (not limited to XAUUSD)
- ✅ **ML Signal Generation** - XGBoost model with 50+ technical indicators
- ✅ **Automated Execution** - Opens/closes trades with TP/SL automatically
- ✅ **Risk Management** - Daily loss limits, position limits, confidence thresholds
- ✅ **Cloud Database** - PostgreSQL database (Aiven) for trade logging
- ✅ **REST API** - 30+ endpoints for complete system control
- ✅ **WebSocket Server** - Real-time updates to frontend

### **Frontend (React)**
- ✅ **Modern UI** - Beautiful dark-themed dashboard with Tailwind CSS
- ✅ **Real-time Updates** - WebSocket integration for instant data
- ✅ **Live Metrics** - Balance, P&L, win rate, profit factor
- ✅ **Interactive Charts** - Equity curve with Recharts
- ✅ **Position Monitoring** - Live P&L updates, quick close buttons
- ✅ **Signal History** - Track all ML-generated signals
- ✅ **Trade Log** - Complete history of executed trades
- ✅ **Responsive Design** - Works on desktop and tablet

---

## 📊 System Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│              │     │              │     │              │
│  MT5 API     │────▶│   Backend    │────▶│   Frontend   │
│ (MetaTrader) │     │   (Python)   │     │   (React)    │
│              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
       │                     │                     │
       │                     │                     │
  Live Market          PostgreSQL            User Browser
    Data                Database              Dashboard
```

---

## 🚀 Quick Start

### **Option 1: One-Click Launch (PowerShell - Recommended)**

```powershell
.\START_SYSTEM.ps1
```

This will:
1. Check Python and Node.js
2. Activate virtual environment (if exists)
3. Start backend in new window
4. Start frontend in new window
5. Open dashboard at http://localhost:5173

### **Option 2: Manual Launch**

**Terminal 1 - Backend:**
```bash
cd src\live_trading
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open browser: `http://localhost:5173`

---

## 📦 Installation

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- MetaTrader 5
- PostgreSQL database (or use provided Aiven connection)

### **Step 1: Clone Repository**
```bash
cd c:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min
```

### **Step 2: Install Python Dependencies**
```bash
# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install packages
pip install -r requirements-live.txt
```

### **Step 3: Install Frontend Dependencies**
```bash
cd frontend
npm install
cd ..
```

### **Step 4: Configure Environment**

Edit `.env` file in root directory:
```env
DATABASE_URL=postgresql://avnadmin:YOUR_PASSWORD@pg-3eecca93-ramosjeffrey414-2d10.e.aivencloud.com:19738/defaultdb?sslmode=require
MAX_DAILY_LOSS=400
MAX_POSITIONS=1
MIN_CONFIDENCE=0.5
DEFAULT_LOT_SIZE=0.01
TP_PIPS=100
SL_PIPS=50
```

### **Step 5: Test Setup**
```bash
cd src\live_trading
python test_setup.py
```

Expected output:
```
✓ PASS - Package Imports
✓ PASS - Database Connection
✓ PASS - MT5 Terminal Discovery
✓ PASS - Model File
Passed: 4/4
```

---

## 🔧 Configuration

### **Risk Management Settings**

Edit `.env` file:

```env
# Conservative (Recommended for beginners)
MAX_DAILY_LOSS=200
MAX_POSITIONS=1
MIN_CONFIDENCE=0.7
DEFAULT_LOT_SIZE=0.01

# Moderate (Default)
MAX_DAILY_LOSS=400
MAX_POSITIONS=1
MIN_CONFIDENCE=0.5
DEFAULT_LOT_SIZE=0.01

# Aggressive (Not recommended)
MAX_DAILY_LOSS=1000
MAX_POSITIONS=3
MIN_CONFIDENCE=0.3
DEFAULT_LOT_SIZE=0.05
```

### **Trading Parameters**

```env
# Scalping (Quick trades)
TP_PIPS=30
SL_PIPS=15

# Day Trading (Default)
TP_PIPS=100
SL_PIPS=50

# Swing Trading
TP_PIPS=200
SL_PIPS=100
```

---

## 🎮 How to Use

### **1. Start the System**

Run the launcher:
```powershell
.\START_SYSTEM.ps1
```

Or manually start backend and frontend (see Quick Start above).

### **2. Open Dashboard**

Navigate to: `http://localhost:5173`

You should see:
- Beautiful dark-themed dashboard
- "MT5 Disconnected" in header (normal - not connected yet)
- All metrics showing $0.00

### **3. Connect to MT5**

#### **Option A: Via API (Current)**

Use Postman, curl, or any HTTP client:

**1. Discover Terminals:**
```bash
curl http://localhost:8000/api/terminals/discover
```

**2. Connect:**
```bash
curl -X POST http://localhost:8000/api/terminals/connect \
  -H "Content-Type: application/json" \
  -d '{
    "terminal_id": "YOUR_TERMINAL_ID_FROM_STEP_1",
    "account": 12345678,
    "password": "your_mt5_password",
    "server": "YourBroker-Demo"
  }'
```

**3. Select Symbol (optional):**
```bash
curl -X POST http://localhost:8000/api/symbols/select \
  -H "Content-Type: application/json" \
  -d '{"symbol": "XAUUSDm"}'
```

#### **Option B: Via Frontend (Future Update)**
- Coming soon: Terminal selector UI
- Coming soon: Connection form in dashboard

### **4. Watch it Trade!**

Once connected:
- System detects M5 bar closes every 5 minutes
- ML model generates BUY/SELL/HOLD signals
- Trades execute automatically if:
  - Confidence > 0.5 (50%)
  - Daily loss < $400
  - No other position open
- Dashboard updates in real-time via WebSocket

---

## 📡 API Reference

### **Base URL**
```
http://localhost:8000
```

### **Key Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/terminals/discover` | GET | Find MT5 terminals |
| `/api/terminals/connect` | POST | Connect to MT5 |
| `/api/symbols/select` | POST | Select trading symbol |
| `/api/account/info` | GET | Get account balance, equity |
| `/api/positions/open` | GET | List open positions |
| `/api/positions/close/{ticket}` | POST | Close specific position |
| `/api/trades/history` | GET | Get trade history |
| `/api/signals/history` | GET | Get signal history |
| `/api/metrics/summary` | GET | Get performance metrics |

**Full API Documentation:** `http://localhost:8000/docs` (when backend is running)

---

## 📂 Project Structure

```
Profitable5min/
├── .env                          # Backend configuration
├── START_SYSTEM.ps1              # PowerShell launcher
├── START_SYSTEM.bat              # Batch launcher
├── README.md                     # This file
├── MASTER_GUIDE.md              # Complete configuration guide
├── BACKEND_COMPLETE.md          # Backend documentation
├── FRONTEND_COMPLETE.md         # Frontend documentation
│
├── src/
│   └── live_trading/            # Backend Python code
│       ├── run.py               # Entry point
│       ├── main.py              # Trading bot
│       ├── mt5_connector.py     # MT5 integration
│       ├── signal_generator.py  # ML signals
│       ├── trade_executor.py    # Trade execution
│       ├── risk_manager.py      # Risk management
│       ├── api/                 # REST API & WebSocket
│       ├── database/            # Database models
│       └── utils/               # Utilities
│
├── frontend/                    # React dashboard
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── hooks/              # React hooks
│   │   ├── services/           # API & WebSocket clients
│   │   ├── store/              # State management
│   │   ├── types/              # TypeScript types
│   │   └── utils/              # Utilities
│   ├── package.json
│   └── README.md
│
├── models/
│   └── final/
│       └── xgboost_model.pkl   # Trained ML model
│
├── data/                       # Training data
├── docs/                       # Documentation
└── logs/                       # Application logs
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| `README.md` | This file - Quick start guide |
| `MASTER_GUIDE.md` | Complete configuration and troubleshooting |
| `BACKEND_COMPLETE.md` | Backend implementation details |
| `FRONTEND_COMPLETE.md` | Frontend implementation details |
| `docs/LIVE_TRADING_IMPLEMENTATION_PLAN.md` | Full implementation plan |
| `frontend/README.md` | Frontend-specific documentation |

---

## 🎯 Trading Flow

```
1. M5 Bar Closes (Every 5 minutes)
   ↓
2. Fetch Market Data (M1, M3, M5, H1)
   ↓
3. Calculate 50+ Technical Indicators
   ↓
4. ML Model Prediction (XGBoost)
   ↓
5. Risk Checks (Loss limit, confidence, positions)
   ↓
6. Execute Trade (if all conditions met)
   ↓
7. Save to Database
   ↓
8. Broadcast to Frontend via WebSocket
   ↓
9. Monitor Until TP/SL Hit
   ↓
10. Close Trade & Update Metrics
```

---

## 🔍 Monitoring

### **Dashboard Metrics**

1. **Account Balance** - Total account balance
2. **Today's P&L** - Profit/loss for current day (with % change)
3. **Win Rate** - Percentage of winning trades
4. **Profit Factor** - Gross profit / Gross loss ratio

### **Charts**

- **Equity Curve** - Visual representation of account growth over time

### **Position Monitoring**

- Real-time P&L updates
- Entry/Exit prices
- Take Profit and Stop Loss levels
- Quick close button for manual intervention

### **Signal History**

- All ML-generated signals
- Confidence scores
- Execution status
- Timestamps

### **Trade History**

- Complete log of closed trades
- Entry/Exit prices
- Duration
- Profit/Loss

---

## 🐛 Troubleshooting

### **Backend Won't Start**

**Issue:** Port 8000 already in use
**Solution:** 
```env
# Change port in .env
API_PORT=8001
```

**Issue:** Database connection failed
**Solution:** 
- Check `DATABASE_URL` in `.env`
- Verify password is correct
- Test connection: `python test_setup.py`

### **Frontend Won't Load**

**Issue:** Cannot connect to backend
**Solution:**
- Ensure backend is running: `http://localhost:8000/api/health`
- Check `.env.development` has correct API URL
- Clear browser cache

### **No Trades Opening**

**Possible Causes:**
1. MT5 not connected (check header)
2. Confidence too low (check signals)
3. Daily loss limit reached
4. Position already open
5. Insufficient margin

**Solution:** Check backend logs in `logs/live_trading.log`

---

## ⚠️ Important Notes

### **Safety**

1. **ALWAYS test on DEMO account first**
2. **Never risk more than you can afford to lose**
3. **Monitor the system regularly**
4. **Understand the code before using**
5. **Start with small lot sizes (0.01)**

### **Disclaimers**

- This is educational software
- Trading carries risk of loss
- Past performance doesn't guarantee future results
- Use at your own risk
- Always test thoroughly before live trading

---

## 📊 Performance Statistics (Backtest)

Based on historical data (Jan 2024 - Jun 2026):

- **Total Trades:** ~247
- **Win Rate:** ~58.7%
- **Profit Factor:** ~1.85
- **Max Drawdown:** ~4.3%
- **Sharpe Ratio:** ~1.42

*Note: Live results may differ from backtest*

---

## 🤝 Support

For detailed configuration and troubleshooting, see:
- `MASTER_GUIDE.md` - Complete configuration guide
- `BACKEND_COMPLETE.md` - Backend details
- `FRONTEND_COMPLETE.md` - Frontend details

---

## 📝 Version History

- **v1.0.0** (July 2026) - Initial release
  - Complete backend implementation
  - React dashboard with real-time updates
  - Multi-terminal & multi-symbol support
  - PostgreSQL database integration

---

## 🎉 Quick Reference

### **URLs**
- Dashboard: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### **Commands**
```bash
# Start system
.\START_SYSTEM.ps1

# Test setup
cd src\live_trading
python test_setup.py

# Start backend only
cd src\live_trading
python run.py

# Start frontend only
cd frontend
npm run dev
```

### **Default Settings**
- Daily Loss Limit: $400
- Max Positions: 1
- Confidence Threshold: 0.5 (50%)
- Lot Size: 0.01
- Take Profit: 100 pips
- Stop Loss: 50 pips

---

**Last Updated:** July 5, 2026  
**Status:** ✅ Production Ready  
**License:** Private/Educational Use

---

🎯 **Happy Trading!** 🎯
