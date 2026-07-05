# 🎯 GOLDMINE ML TRADING - MASTER GUIDE

Complete guide for configuration, setup, and operation of the live trading system.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Configuration Files](#configuration-files)
3. [Backend Configuration](#backend-configuration)
4. [Frontend Configuration](#frontend-configuration)
5. [Complete Startup Guide](#complete-startup-guide)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [WebSocket Events Reference](#websocket-events-reference)
8. [Trading Flow](#trading-flow)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GOLDMINE ML TRADING SYSTEM                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   MT5 API    │───▶│    BACKEND   │───▶│   FRONTEND   │  │
│  │  (MetaTrader)│    │   (Python)   │    │   (React)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         │                    │                    │          │
│    Live Market          PostgreSQL          User Browser    │
│       Data               Database             Dashboard      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Components:**
1. **MT5 Terminal** - Connects to broker, executes trades
2. **Python Backend** - ML signal generation, trade execution, API server
3. **PostgreSQL Database** - Stores trades, signals, metrics
4. **React Frontend** - Real-time dashboard, monitoring, control
5. **WebSocket** - Real-time communication between backend and frontend

---

## 📁 Configuration Files

### **Backend Configuration**

#### 1. `.env` (Root Directory)
**Location:** `c:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min\.env`

```env
# Database Configuration
DATABASE_URL=postgresql://avnadmin:AVNS_jSaI48VccE8DQV3_Q5q@pg-3eecca93-ramosjeffrey414-2d10.e.aivencloud.com:19738/defaultdb?sslmode=require

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=goldmine_ml_secret_key_change_in_production_2024

# CORS Origins (comma separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Risk Management
MAX_DAILY_LOSS=400
MAX_POSITIONS=1
MIN_CONFIDENCE=0.5
DEFAULT_LOT_SIZE=0.01

# Trading Parameters
TP_PIPS=100
SL_PIPS=50
PIP_VALUE=0.01

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/live_trading.log

# Model Path
MODEL_PATH=models/final/xgboost_model.pkl
```

**What Each Setting Does:**

| Setting | Description | Default | How to Change |
|---------|-------------|---------|---------------|
| `DATABASE_URL` | PostgreSQL connection string | Aiven cloud DB | Update with your DB credentials |
| `API_HOST` | Backend API host | 0.0.0.0 (all interfaces) | Keep as is for local |
| `API_PORT` | Backend API port | 8000 | Change if port conflict |
| `API_SECRET_KEY` | API security key | Auto-generated | Change in production |
| `CORS_ORIGINS` | Allowed frontend URLs | localhost:5173 | Add production URL |
| `MAX_DAILY_LOSS` | Daily loss limit ($) | 400 | Adjust based on risk |
| `MAX_POSITIONS` | Max simultaneous trades | 1 | Increase for multi-position |
| `MIN_CONFIDENCE` | Min ML confidence to trade | 0.5 (50%) | Higher = fewer trades |
| `DEFAULT_LOT_SIZE` | Default trade volume | 0.01 lots | Adjust position size |
| `TP_PIPS` | Take Profit in pips | 100 | Adjust profit target |
| `SL_PIPS` | Stop Loss in pips | 50 | Adjust risk level |
| `LOG_LEVEL` | Logging detail level | INFO | DEBUG for more detail |
| `MODEL_PATH` | Path to XGBoost model | models/final/... | Update if moved |

#### 2. `requirements-live.txt`
**Location:** `src\live_trading\requirements-live.txt`

Contains all Python dependencies:
```txt
fastapi==0.115.12
uvicorn[standard]==0.34.0
python-socketio==5.12.0
sqlalchemy==2.0.37
psycopg2-binary==2.9.10
python-dotenv==1.0.1
MetaTrader5==5.0.4800
pandas==2.2.3
numpy==2.2.5
xgboost==3.0.0
joblib==1.4.2
pydantic==2.10.6
```

### **Frontend Configuration**

#### 1. `.env.development` (Frontend Directory)
**Location:** `frontend\.env.development`

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```

**What Each Setting Does:**

| Setting | Description | Default | When to Change |
|---------|-------------|---------|----------------|
| `VITE_API_URL` | Backend REST API URL | http://localhost:8000 | Production deployment |
| `VITE_WS_URL` | Backend WebSocket URL | http://localhost:8000 | Production deployment |

#### 2. `package.json` (Frontend Directory)
**Location:** `frontend\package.json`

Key dependencies:
- `react` - UI framework
- `socket.io-client` - Real-time communication
- `axios` - HTTP requests
- `@tanstack/react-query` - Data fetching
- `zustand` - State management
- `recharts` - Charts
- `tailwindcss` - Styling

---

## ⚙️ Backend Configuration

### **How the Backend Works**

```
┌─────────────────────────────────────────────────────────┐
│                   BACKEND ARCHITECTURE                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Main.py (Trading Bot Loop)                           │
│     ├─> Detects M5 bar close every 5 minutes            │
│     ├─> Fetches market data from MT5                    │
│     ├─> Calculates 50+ technical indicators             │
│     ├─> Passes to ML model (XGBoost)                    │
│     ├─> Generates BUY/SELL/HOLD signal                  │
│     ├─> Checks risk limits                              │
│     ├─> Executes trade if conditions met                │
│     └─> Saves to database & broadcasts via WebSocket    │
│                                                           │
│  2. REST API (FastAPI)                                   │
│     ├─> Runs on port 8000                               │
│     ├─> 30+ endpoints for frontend                      │
│     └─> Serves account info, positions, trades, etc     │
│                                                           │
│  3. WebSocket Server (Socket.IO)                         │
│     ├─> Real-time event broadcasting                    │
│     ├─> Sends trade opens/closes instantly              │
│     └─> Updates P&L every tick                          │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### **Key Backend Files**

| File | Purpose | Key Functions |
|------|---------|---------------|
| `run.py` | Entry point | Starts API server & trading bot |
| `main.py` | Trading bot main loop | Signal generation, trade execution |
| `mt5_connector.py` | MT5 integration | Connect, get data, place orders |
| `mt5_terminal_manager.py` | Multi-terminal support | Discover, connect, switch terminals |
| `signal_generator.py` | ML signal generation | Calculate features, predict with XGBoost |
| `trade_executor.py` | Trade execution | Open/close positions, set TP/SL |
| `risk_manager.py` | Risk management | Check limits, validate trades |
| `api/rest_api.py` | REST API endpoints | All HTTP endpoints |
| `api/websocket_server.py` | WebSocket server | Real-time events |
| `database/db_manager.py` | Database operations | Save/retrieve trades, signals |

### **Backend Configuration Options**

#### **Risk Management Settings (in `.env`)**

```env
# Conservative (Low Risk)
MAX_DAILY_LOSS=200
MAX_POSITIONS=1
MIN_CONFIDENCE=0.7
DEFAULT_LOT_SIZE=0.01

# Moderate (Medium Risk)
MAX_DAILY_LOSS=400
MAX_POSITIONS=2
MIN_CONFIDENCE=0.5
DEFAULT_LOT_SIZE=0.02

# Aggressive (High Risk) - NOT RECOMMENDED
MAX_DAILY_LOSS=1000
MAX_POSITIONS=5
MIN_CONFIDENCE=0.3
DEFAULT_LOT_SIZE=0.05
```

#### **Trading Parameters**

```env
# Scalping (Quick trades, small profits)
TP_PIPS=30
SL_PIPS=15
PIP_VALUE=0.01

# Day Trading (Medium duration)
TP_PIPS=100
SL_PIPS=50
PIP_VALUE=0.01

# Swing Trading (Longer duration)
TP_PIPS=200
SL_PIPS=100
PIP_VALUE=0.01
```

---

## 🎨 Frontend Configuration

### **How the Frontend Works**

```
┌─────────────────────────────────────────────────────────┐
│                  FRONTEND ARCHITECTURE                   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Data Fetching (TanStack Query)                       │
│     ├─> Polls REST API every 1-5 seconds                │
│     ├─> Caches responses for performance                │
│     └─> Auto-retries on failure                         │
│                                                           │
│  2. Real-time Updates (WebSocket)                        │
│     ├─> Connects to backend WebSocket                   │
│     ├─> Receives instant updates                        │
│     └─> Updates UI without page refresh                 │
│                                                           │
│  3. State Management (Zustand)                           │
│     ├─> accountStore - Account balance, equity          │
│     ├─> tradesStore - Positions, trades, signals        │
│     ├─> metricsStore - Performance metrics              │
│     └─> connectionStore - Connection status             │
│                                                           │
│  4. UI Components (React)                                │
│     ├─> MetricsOverview - 4 metric cards                │
│     ├─> EquityCurve - Interactive chart                 │
│     ├─> OpenPositions - Live position list              │
│     ├─> SignalHistory - Signal log                      │
│     └─> TradeHistory - Completed trades table           │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### **Frontend Customization**

#### **Change Refresh Rates**

Edit `frontend/src/hooks/useDataFetcher.ts`:

```typescript
// Account info - every 2 seconds (default)
refetchInterval: 2000,

// Open positions - every 1 second (real-time)
refetchInterval: 1000,

// Metrics - every 10 seconds (less frequent)
refetchInterval: 10000,
```

#### **Change Colors**

Edit `frontend/tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#0ea5e9',  // Change main color
      },
    },
  },
}
```

#### **Change Dashboard Layout**

Edit `frontend/src/App.tsx` to reorder or remove components.

---

## 🚀 Complete Startup Guide

### **Prerequisites Checklist**

- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] MT5 terminal installed
- [ ] MT5 demo account created
- [ ] PostgreSQL database accessible
- [ ] XGBoost model trained (`models/final/xgboost_model.pkl`)

### **Step-by-Step Startup**

#### **Step 1: Verify Configuration**

```bash
# Check backend .env file
type .env

# Check frontend .env file
type frontend\.env.development
```

Ensure all settings are correct!

#### **Step 2: Install Dependencies**

**Backend:**
```bash
# Activate virtual environment (if using)
venv\Scripts\activate

# Install Python packages
pip install -r requirements-live.txt
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

#### **Step 3: Test Backend Setup**

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

If any test fails, check the error message and fix before continuing.

#### **Step 4: Start Backend**

```bash
# From src\live_trading directory
python run.py
```

Expected output:
```
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Trading bot thread started
INFO: Waiting for MT5 connection...
```

**Keep this terminal open!**

#### **Step 5: Start Frontend**

Open a **new terminal**:

```bash
cd frontend
npm run dev
```

Expected output:
```
VITE v8.1.3 ready in 2567 ms
➜ Local: http://localhost:5173/
```

**Keep this terminal open too!**

#### **Step 6: Open Dashboard**

Open browser and go to: `http://localhost:5173`

You should see:
- Dashboard loaded with dark theme
- "MT5 Disconnected" in header (normal - not connected yet)
- "Offline" WebSocket status (normal - will connect)
- All metrics showing $0.00 (normal - no data yet)

#### **Step 7: Connect MT5**

You have 2 options:

**Option A: Via Frontend (Coming in future update)**
- Terminal selector dropdown
- Connection form
- One-click connect

**Option B: Via API (Current method)**

Use Postman, curl, or Python:

```bash
# 1. Discover terminals
curl http://localhost:8000/api/terminals/discover

# You'll get response with terminal_id like:
# {"terminals": [{"id": "abc123", "name": "MetaTrader 5", ...}]}

# 2. Connect to MT5
curl -X POST http://localhost:8000/api/terminals/connect \
  -H "Content-Type: application/json" \
  -d '{
    "terminal_id": "abc123",
    "account": 12345678,
    "password": "your_mt5_password",
    "server": "YourBroker-Demo"
  }'

# 3. Select trading symbol (optional, default is XAUUSDm from model)
curl -X POST http://localhost:8000/api/symbols/select \
  -H "Content-Type: application/json" \
  -d '{"symbol": "XAUUSDm"}'
```

#### **Step 8: Verify Connection**

Check dashboard:
- Header should show "MT5 Connected" (green pulse)
- "Live" WebSocket status
- Account balance loaded
- Symbol showing

Check backend terminal:
```
INFO: MT5 connected successfully
INFO: Account: 12345678
INFO: Balance: $10000.00
INFO: Symbol: XAUUSDm selected
```

#### **Step 9: Watch it Trade!**

The system is now fully operational:

1. **Every 5 minutes** (on M5 bar close):
   - Bot detects new candle
   - Fetches market data
   - Calculates 50+ indicators
   - ML model predicts BUY/SELL/HOLD
   - If confidence > 0.5 and risk OK → Opens trade
   - Dashboard updates instantly via WebSocket

2. **Real-time monitoring**:
   - Position P&L updates every tick
   - Charts update automatically
   - Signals appear immediately
   - Trades logged to database

3. **Auto risk management**:
   - Stops trading if daily loss > $400
   - Only 1 position open at a time
   - Auto TP/SL on every trade

---

## 📡 API Endpoints Reference

### **Terminal Management**

```http
GET /api/terminals/discover
```
Discovers all MT5 terminals on system.

```http
POST /api/terminals/connect
Body: {
  "terminal_id": "string",
  "account": number,
  "password": "string",
  "server": "string"
}
```
Connects to specific MT5 terminal.

```http
GET /api/terminals/active
```
Gets currently active terminal info.

### **Symbol Management**

```http
GET /api/symbols/available
```
Lists all tradeable symbols from MT5.

```http
GET /api/symbols/search?query=XAU
```
Searches for symbols by name.

```http
POST /api/symbols/select
Body: {"symbol": "XAUUSDm"}
```
Selects symbol for trading.

```http
GET /api/symbols/current
```
Gets currently selected symbol.

### **Account & Connection**

```http
GET /api/account/info
```
Returns account balance, equity, margin, profit.

```http
GET /api/connection/status
```
Returns MT5 connection status.

```http
GET /api/health
```
Health check endpoint.

### **Positions & Trades**

```http
GET /api/positions/open
```
Lists all open positions.

```http
POST /api/positions/close/{ticket}
```
Closes specific position by ticket number.

```http
POST /api/positions/close_all
```
Emergency close all positions.

```http
GET /api/trades/history?limit=50&offset=0
```
Gets trade history with pagination.

### **Signals & Metrics**

```http
GET /api/signals/history?limit=50&offset=0
```
Gets ML signal history.

```http
GET /api/signals/latest
```
Gets most recent signal.

```http
GET /api/metrics/summary
```
Returns overall performance metrics.

```http
GET /api/metrics/daily
```
Returns today's metrics.

```http
GET /api/metrics/equity_curve
```
Returns equity curve data for chart.

### **Configuration**

```http
GET /api/config
```
Gets current configuration.

```http
POST /api/config/update
Body: {
  "max_daily_loss": 500,
  "min_confidence": 0.6
}
```
Updates configuration dynamically.

---

## 📡 WebSocket Events Reference

### **Events Sent by Backend**

#### `trade_opened`
```json
{
  "ticket": 123456,
  "symbol": "XAUUSDm",
  "direction": "BUY",
  "entry_price": 2645.50,
  "tp": 2646.50,
  "sl": 2645.00,
  "volume": 0.01,
  "timestamp": "2026-07-05T15:30:00Z"
}
```

#### `trade_closed`
```json
{
  "ticket": 123456,
  "profit": 7.50,
  "exit_price": 2646.25,
  "timestamp": "2026-07-05T15:45:00Z"
}
```

#### `new_signal`
```json
{
  "symbol": "XAUUSDm",
  "direction": "BUY",
  "confidence": 0.78,
  "entry_price": 2645.50,
  "timestamp": "2026-07-05T15:30:00Z"
}
```

#### `account_update`
```json
{
  "balance": 10007.50,
  "equity": 10007.50,
  "profit": 0.00
}
```

#### `metrics_update`
```json
{
  "daily_pnl": 7.50,
  "daily_pnl_pct": 0.075,
  "win_rate": 65.5,
  "profit_factor": 2.1
}
```

#### `position_update`
```json
{
  "ticket": 123456,
  "current_price": 2646.00,
  "profit": 5.00
}
```

#### `connection_status`
```json
{
  "connected": true,
  "terminal_id": "abc123"
}
```

#### `error`
```json
{
  "message": "Failed to open position",
  "timestamp": "2026-07-05T15:30:00Z"
}
```

---

## 🔄 Trading Flow

### **Complete Trading Cycle**

```
1. BAR CLOSE DETECTION (Every 5 minutes)
   ↓
2. FETCH MARKET DATA
   ├─> Gets last 200 M5 candles
   ├─> Gets M1, M3, H1 data for multi-timeframe
   └─> Validates data quality
   ↓
3. CALCULATE FEATURES (50+ indicators)
   ├─> RSI (14, 21, 28)
   ├─> EMA (9, 21, 50, 200)
   ├─> MACD
   ├─> Bollinger Bands
   ├─> ATR
   ├─> Momentum indicators
   ├─> Volatility measures
   └─> Temporal features (hour, day, etc.)
   ↓
4. ML MODEL PREDICTION
   ├─> XGBoost model loaded
   ├─> Features passed to model
   ├─> Returns: [BUY probability, SELL probability, HOLD probability]
   └─> Direction = argmax(probabilities)
   ↓
5. RISK CHECKS
   ├─> Check daily loss limit (< $400?)
   ├─> Check max positions (< 1?)
   ├─> Check confidence (> 0.5?)
   └─> If ALL pass → Continue, else → Skip trade
   ↓
6. TRADE EXECUTION
   ├─> Calculate position size (0.01 lots)
   ├─> Calculate TP (entry + 100 pips)
   ├─> Calculate SL (entry - 50 pips)
   ├─> Send order to MT5
   └─> Get ticket number
   ↓
7. SAVE TO DATABASE
   ├─> Save trade to 'trades' table
   ├─> Save signal to 'signals' table
   └─> Update daily summary
   ↓
8. BROADCAST VIA WEBSOCKET
   ├─> Send 'trade_opened' event to frontend
   ├─> Send 'new_signal' event
   └─> Send 'metrics_update' event
   ↓
9. FRONTEND UPDATES INSTANTLY
   ├─> New position appears in Open Positions
   ├─> Signal appears in Signal History
   ├─> Metrics update
   └─> Chart updates
   ↓
10. MONITOR UNTIL CLOSE
    ├─> Update P&L every tick
    ├─> Broadcast 'position_update' events
    ├─> Wait for TP/SL hit or manual close
    └─> When closed → Restart cycle
```

---

## 🐛 Troubleshooting

### **Backend Issues**

#### Backend Won't Start
```
Error: Address already in use: port 8000
```
**Solution:** Port 8000 is taken. Either:
1. Stop other process using port 8000
2. Change `API_PORT=8001` in `.env`

#### Database Connection Failed
```
Error: password authentication failed
```
**Solution:**
1. Check `DATABASE_URL` in `.env`
2. Verify password is correct
3. Check database is accessible

#### MT5 Not Found
```
Warning: No MT5 terminals found
```
**Solution:**
1. Install MetaTrader 5
2. Ensure MT5 is in default installation path
3. Check `mt5_terminal_manager.py` for search paths

#### Model Not Found
```
Error: Model file not found
```
**Solution:**
1. Train model: `python scripts/03_model_training.py`
2. Check `MODEL_PATH` in `.env`
3. Verify file exists at specified path

### **Frontend Issues**

#### Frontend Won't Load
```
Error: Cannot connect to backend
```
**Solution:**
1. Ensure backend is running on port 8000
2. Check `VITE_API_URL` in `.env.development`
3. Clear browser cache

#### No Real-time Updates
```
WebSocket shows "Offline"
```
**Solution:**
1. Check WebSocket server is running (backend logs)
2. Verify no firewall blocking WebSocket
3. Check browser console for errors

#### API Errors (403, 404, 500)
```
API request failed
```
**Solution:**
1. Check backend logs for detailed error
2. Verify API endpoint exists
3. Check request payload format

### **Trading Issues**

#### No Trades Opening
**Check:**
1. MT5 connected? (Header shows green)
2. Symbol selected? (Should show in header)
3. Confidence too low? (Check signal history)
4. Daily loss limit hit? (Check today's P&L)
5. Position already open? (Check open positions)

#### Trades Not Executing
**Check:**
1. MT5 account has sufficient margin
2. Symbol is tradeable (not disabled)
3. Lot size is valid (min/max volume)
4. Backend logs for error messages

#### Wrong Prices/Data
**Check:**
1. MT5 symbol matches training data symbol
2. Symbol digits correct (2 for XAUUSD typically)
3. Pip value calculation in `.env`
4. Timezone settings

---

## 📞 Support Resources

- **Backend Docs:** `BACKEND_COMPLETE.md`
- **Frontend Docs:** `frontend/README.md`
- **Implementation Plan:** `docs/LIVE_TRADING_IMPLEMENTATION_PLAN.md`
- **This Guide:** `MASTER_GUIDE.md`

---

## ✅ Quick Reference Card

### **Common Commands**

```bash
# Start backend
cd src\live_trading
python run.py

# Start frontend
cd frontend
npm run dev

# Test setup
cd src\live_trading
python test_setup.py

# Install dependencies
pip install -r requirements-live.txt
cd frontend && npm install
```

### **URLs**

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### **Default Settings**

- Daily Loss Limit: $400
- Max Positions: 1
- Min Confidence: 0.5 (50%)
- Lot Size: 0.01
- TP: 100 pips
- SL: 50 pips
- Database: PostgreSQL (Aiven Cloud)

---

**Last Updated:** July 5, 2026
**Version:** 1.0.0
**Status:** ✅ Production Ready
