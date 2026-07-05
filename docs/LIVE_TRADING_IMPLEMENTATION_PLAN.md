# 🚀 Live Trading MT5 Implementation Plan

## 📋 Project Overview

**Objective:** Transform the backtesting system into a live trading application connected to MetaTrader 5 with real-time signal generation and a professional React dashboard.

**Core Components:**
1. **Backend:** Python MT5 integration with live signal generation
2. **Frontend:** React + Vite dashboard with real-time metrics
3. **Communication:** WebSocket/REST API for real-time updates
4. **Database:** Trade logging and performance tracking

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LIVE TRADING SYSTEM                       │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   MT5 API    │ ◄─────► │   Python     │ ◄─────► │   Database   │
│  (Real-Time) │         │   Backend    │         │   (SQLite)   │
└──────────────┘         └──────────────┘         └──────────────┘
       ▲                        │                         │
       │                        │ WebSocket/REST          │
       │                        ▼                         │
       │                 ┌──────────────┐                 │
       └─────────────────│   React      │◄────────────────┘
         (Place Orders)  │   Dashboard  │   (Fetch Metrics)
                         └──────────────┘
```

---

## 🐍 Part 1: Python Backend Architecture

### 1.1 Core Modules Structure

```
src/
├── live_trading/
│   ├── __init__.py
│   ├── mt5_connector.py      # MT5 connection & authentication
│   ├── mt5_terminal_manager.py # Multi-terminal management (NEW)
│   ├── signal_generator.py   # Real-time ML signal generation
│   ├── trade_executor.py     # Order placement & management
│   ├── risk_manager.py       # Position sizing & risk controls
│   ├── market_data_manager.py # Real-time data collection
│   └── performance_tracker.py # Metrics calculation
├── api/
│   ├── __init__.py
│   ├── websocket_server.py   # Real-time updates to frontend
│   ├── rest_api.py           # HTTP endpoints
│   └── models.py             # Pydantic data models
├── database/
│   ├── __init__.py
│   ├── db_manager.py         # Database operations
│   └── models.py             # SQLAlchemy models
└── utils/
    ├── __init__.py
    ├── logger.py             # Logging configuration
    └── config.py             # Configuration management
```

### 1.2 MT5 Terminal Manager Module (`mt5_terminal_manager.py`) **[NEW]**

**Purpose:** Manage multiple MT5 terminals and allow runtime switching

**Key Functions:**
```python
def discover_terminals() -> list[dict]
def initialize_terminal(terminal_path: str) -> bool
def switch_terminal(terminal_id: str) -> bool
def get_active_terminal() -> dict
def get_available_symbols(terminal_id: str) -> list[str]
```

**Example Implementation:**
```python
import MetaTrader5 as mt5
import os
from pathlib import Path
import logging

class MT5TerminalManager:
    def __init__(self):
        self.terminals = {}
        self.active_terminal_id = None
        self.logger = logging.getLogger(__name__)
    
    def discover_terminals(self) -> list[dict]:
        """
        Scan system for installed MT5 terminals
        Returns list of terminal configurations
        """
        terminals = []
        
        # Common MT5 installation paths
        search_paths = [
            r"C:\Program Files\MetaTrader 5",
            r"C:\Program Files (x86)\MetaTrader 5",
            os.path.expanduser(r"~\AppData\Roaming\MetaQuotes\Terminal"),
        ]
        
        # Search for terminal64.exe
        for base_path in search_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    if 'terminal64.exe' in files:
                        terminal_path = os.path.join(root, 'terminal64.exe')
                        
                        # Try to get terminal info
                        terminal_info = {
                            'id': self._generate_terminal_id(terminal_path),
                            'path': terminal_path,
                            'name': self._get_terminal_name(terminal_path),
                            'broker': self._detect_broker(root),
                        }
                        terminals.append(terminal_info)
        
        self.terminals = {t['id']: t for t in terminals}
        return terminals
    
    def _generate_terminal_id(self, path: str) -> str:
        """Generate unique ID for terminal"""
        import hashlib
        return hashlib.md5(path.encode()).hexdigest()[:8]
    
    def _get_terminal_name(self, path: str) -> str:
        """Extract terminal name from path"""
        return Path(path).parent.name
    
    def _detect_broker(self, terminal_root: str) -> str:
        """Try to detect broker from config files"""
        config_path = os.path.join(terminal_root, 'config', 'common.ini')
        if os.path.exists(config_path):
            # Parse config to get broker name
            # This is simplified - actual parsing would be more complex
            return "Detected Broker"
        return "Unknown"
    
    def initialize_terminal(self, terminal_id: str, account: int, 
                           password: str, server: str) -> bool:
        """Initialize specific MT5 terminal"""
        if terminal_id not in self.terminals:
            self.logger.error(f"Terminal {terminal_id} not found")
            return False
        
        terminal = self.terminals[terminal_id]
        
        # Shutdown current connection if exists
        if self.active_terminal_id:
            mt5.shutdown()
        
        # Initialize with specific terminal path
        if not mt5.initialize(terminal['path']):
            self.logger.error(f"Failed to initialize {terminal['name']}")
            return False
        
        # Login to account
        if not mt5.login(account, password=password, server=server):
            self.logger.error(f"Login failed: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        self.active_terminal_id = terminal_id
        self.terminals[terminal_id]['connected'] = True
        self.terminals[terminal_id]['account'] = account
        
        self.logger.info(f"Connected to {terminal['name']} - Account: {account}")
        return True
    
    def get_active_terminal(self) -> dict:
        """Get currently active terminal info"""
        if self.active_terminal_id:
            return self.terminals.get(self.active_terminal_id)
        return None
    
    def get_available_symbols(self) -> list[dict]:
        """Get all available symbols from active terminal"""
        if not self.active_terminal_id:
            return []
        
        symbols = mt5.symbols_get()
        if symbols is None:
            return []
        
        symbol_list = []
        for symbol in symbols:
            symbol_list.append({
                'name': symbol.name,
                'description': symbol.description,
                'path': symbol.path,
                'digits': symbol.digits,
                'trade_mode': symbol.trade_mode,
            })
        
        return symbol_list
    
    def switch_terminal(self, terminal_id: str, account: int,
                       password: str, server: str) -> bool:
        """Switch to different terminal"""
        return self.initialize_terminal(terminal_id, account, password, server)

```

### 1.3 MT5 Connector Module (`mt5_connector.py`)

**Purpose:** Handle connection, authentication, and basic MT5 operations

**Key Functions:**
```python
def initialize_mt5(terminal_path: str = None) -> bool
def login_mt5(account: int, password: str, server: str) -> bool
def shutdown_mt5() -> None
def get_account_info() -> dict
def get_symbol_info(symbol: str) -> dict
def get_latest_rates(symbol: str, timeframe: int, count: int) -> pd.DataFrame
def check_connection() -> bool
```

**Dependencies:**
```python
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import logging
```

**Connection Flow:**
1. Initialize MT5 terminal
2. Authenticate with account credentials
3. Verify connection status
4. Load symbol specifications
5. Subscribe to market data

**Example Implementation:**
```python
import MetaTrader5 as mt5
import logging

class MT5Connector:
    def __init__(self):
        self.connected = False
        self.current_symbol = None
        self.logger = logging.getLogger(__name__)
    
    def initialize(self, terminal_path: str = None):
        """Initialize MT5 with optional terminal path"""
        if terminal_path:
            if not mt5.initialize(terminal_path):
                self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
        else:
            if not mt5.initialize():
                self.logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
        
        self.connected = True
        return True

    
    def login(self, account: int, password: str, server: str):
        if not self.connected:
            self.initialize()
        
        authorized = mt5.login(account, password=password, server=server)
        if not authorized:
            self.logger.error(f"Login failed: {mt5.last_error()}")
            return False
        
        self.logger.info(f"Logged in to account {account}")
        return True
    
    def get_account_info(self):
        account = mt5.account_info()
        if account is None:
            return None
        
        return {
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'free_margin': account.margin_free,
            'profit': account.profit,
        }
```

---

### 1.3 Signal Generator Module (`signal_generator.py`)

**Purpose:** Generate ML predictions every bar close

**Key Functions:**
```python
def load_model() -> xgb.XGBClassifier
def compute_features(df: pd.DataFrame) -> pd.DataFrame
def generate_signal(current_bar: dict) -> tuple[int, float]
def get_confidence() -> float
def validate_signal(signal: int) -> bool
```

**Signal Generation Flow:**
```
1. On new M5 bar close:
   ├─> Fetch last 200 bars (M1, M3, M5, H1)
   ├─> Calculate all features (RSI, EMA, MACD, etc.)
   ├─> Feed features to XGBoost model
   ├─> Get prediction + confidence
   ├─> Apply confidence threshold (>0.5)
   └─> Return signal or NO_TRADE
```

**Features to Calculate (Real-Time):**
- RSI (14) + crosses (above 35, below 65)
- EMA (20, 50)
- MACD + Signal + Histogram
- ADX (trend strength)
- Momentum (1, 3, 5, 10, 20 periods)
- Volatility (10, 20 periods)
- Candle patterns (body, wicks, ratios)
- Temporal features (hour, day, session)

**Example Implementation:**
```python
import joblib
import pandas as pd
import ta

class SignalGenerator:
    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)
        self.feature_cols = self._load_feature_names()
        self.min_confidence = 0.5
    
    def compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all features matching backtest"""
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        df['rsi_oversold'] = (df['rsi'] < 35).astype(int)
        df['rsi_overbought'] = (df['rsi'] > 65).astype(int)
        df['rsi_cross_above_35'] = ((df['rsi'] > 35) & (df['rsi'].shift(1) <= 35)).astype(int)
        df['rsi_cross_below_65'] = ((df['rsi'] < 65) & (df['rsi'].shift(1) >= 65)).astype(int)
        
        # EMAs
        df['ema_20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
        df['ema_50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
        df['price_above_ema20'] = (df['close'] > df['ema_20']).astype(int)
        
        # MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Momentum
        for period in [1, 3, 5, 10, 20]:
            df[f'momentum_{period}'] = df['close'].pct_change(period) * 100
        
        # ... (add all other features from backtest)
        
        return df
    
    def generate_signal(self, bars: pd.DataFrame) -> tuple:
        """Generate signal from latest bar"""
        features_df = self.compute_features(bars)
        latest = features_df.iloc[-1][self.feature_cols]
        
        prediction = self.model.predict([latest])[0]
        confidence = self.model.predict_proba([latest]).max()
        
        if confidence < self.min_confidence:
            return -1, confidence  # NO_TRADE
        
        return prediction, confidence  # 0=SELL, 1=BUY
```

---

### 1.4 Trade Executor Module (`trade_executor.py`)

**Purpose:** Execute trades based on signals

**Key Functions:**
```python
def open_position(symbol: str, signal: int, lot_size: float) -> int
def set_tp_sl(ticket: int, tp_price: float, sl_price: float) -> bool
def close_position(ticket: int) -> bool
def modify_position(ticket: int, new_tp: float, new_sl: float) -> bool
def get_open_positions() -> list
```

**Trade Execution Flow:**
```
1. Signal received (BUY/SELL)
2. Check risk limits (daily loss, max positions)
3. Calculate position size (0.01 lots)
4. Calculate TP/SL prices:
   - BUY:  TP = entry + (100 pips * 0.01)
           SL = entry - (50 pips * 0.01)
   - SELL: TP = entry - (100 pips * 0.01)
           SL = entry + (50 pips * 0.01)
5. Place market order via MT5
6. Set TP/SL levels
7. Log trade to database
8. Emit event to frontend (WebSocket)
```

**Example Implementation:**
```python
import MetaTrader5 as mt5

class TradeExecutor:
    def __init__(self, symbol: str = "XAUUSDm"):
        self.symbol = symbol
        self.pip_value = 0.01  # For XAUUSD
        self.tp_pips = 100
        self.sl_pips = 50
        self.lot_size = 0.01
        self.magic = 123456
    
    def open_position(self, signal: int) -> dict:
        """Open BUY or SELL position"""
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return {'success': False, 'error': 'Symbol not found'}
        
        # Get current price
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return {'success': False, 'error': 'No tick data'}
        
        # Determine order type and prices
        if signal == 1:  # BUY
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
            tp = price + (self.tp_pips * self.pip_value)
            sl = price - (self.sl_pips * self.pip_value)
        else:  # SELL
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
            tp = price - (self.tp_pips * self.pip_value)
            sl = price + (self.sl_pips * self.pip_value)
        
        # Prepare order request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": self.magic,
            "comment": "Goldmine ML",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {
                'success': False,
                'error': f"Order failed: {result.retcode}",
                'result': result
            }
        
        return {
            'success': True,
            'ticket': result.order,
            'price': price,
            'tp': tp,
            'sl': sl,
            'volume': self.lot_size,
        }
    
    def close_position(self, ticket: int) -> dict:
        """Close specific position"""
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return {'success': False, 'error': 'Position not found'}
        
        position = positions[0]
        
        # Determine closing order type (opposite of position)
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(self.symbol).bid if close_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(self.symbol).ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": self.magic,
            "comment": "Close by system",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        return {'success': result.retcode == mt5.TRADE_RETCODE_DONE, 'result': result}
```

---

### 1.5 Risk Manager Module (`risk_manager.py`)

**Purpose:** Enforce risk limits and position sizing

**Key Functions:**
```python
def check_daily_limit() -> bool
def calculate_position_size(account_balance: float, risk_pct: float) -> float
def can_open_trade() -> tuple[bool, str]
def update_daily_pnl(trade_profit: float) -> None
def emergency_close_all() -> None
```

**Risk Parameters:**
```python
RISK_LIMITS = {
    'max_positions': 1,           # One trade at a time
    'max_daily_loss': 400,        # USD
    'max_daily_profit': 1000,     # USD (optional target)
    'max_lot_size': 0.01,         # Standard lot
    'min_confidence': 0.5,        # Model confidence
}
```

**Example Implementation:**
```python
class RiskManager:
    def __init__(self):
        self.max_positions = 1
        self.max_daily_loss = 400
        self.max_lot_size = 0.01
        self.min_confidence = 0.5
        self.daily_pnl = 0
        self.reset_time = None
    
    def can_open_trade(self, confidence: float) -> tuple[bool, str]:
        """Check if trade can be opened"""
        # Check confidence
        if confidence < self.min_confidence:
            return False, f"Low confidence: {confidence:.2f}"
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return False, f"Daily loss limit reached: ${self.daily_pnl:.2f}"
        
        # Check max positions
        open_positions = mt5.positions_total()
        if open_positions >= self.max_positions:
            return False, f"Max positions reached: {open_positions}"
        
        return True, "OK"
    
    def update_daily_pnl(self, profit: float):
        """Update daily P&L tracking"""
        self.daily_pnl += profit
    
    def reset_daily_stats(self):
        """Reset at start of new trading day"""
        self.daily_pnl = 0
```

---

### 1.6 Main Trading Loop (`main.py`)

**Purpose:** Orchestrate the entire live trading system

**Example Implementation:**
```python
import time
import logging
from datetime import datetime
from mt5_connector import MT5Connector
from signal_generator import SignalGenerator
from trade_executor import TradeExecutor
from risk_manager import RiskManager
from database.db_manager import DatabaseManager
from api.websocket_server import WebSocketServer

class LiveTradingBot:
    def __init__(self, config: dict):
        self.config = config
        self.mt5 = MT5Connector()
        self.signal_gen = SignalGenerator('models/final/xgboost_model.pkl')
        self.executor = TradeExecutor()
        self.risk_mgr = RiskManager()
        self.db = DatabaseManager()
        self.ws_server = WebSocketServer()
        
        self.running = False
        self.last_bar_time = None
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("Starting Goldmine ML Live Trading Bot...")
        
        # Connect to MT5
        if not self.mt5.initialize():
            self.logger.error("Failed to initialize MT5")
            return
        
        # Login
        if not self.mt5.login(
            self.config['account'],
            self.config['password'],
            self.config['server']
        ):
            self.logger.error("Failed to login to MT5")
            return
        
        self.logger.info("Connected to MT5 successfully!")
        self.running = True
        
        # Start WebSocket server in separate thread
        self.ws_server.start()
        
        # Main loop
        self.run_loop()
    
    def run_loop(self):
        """Main trading loop"""
        while self.running:
            try:
                # Check for new M5 bar
                current_bar = self.get_latest_m5_bar()
                
                if self.is_new_bar(current_bar):
                    self.logger.info(f"New M5 bar: {current_bar['time']}")
                    self.process_new_bar(current_bar)
                
                # Monitor open positions
                self.monitor_positions()
                
                # Update account info
                self.update_account_metrics()
                
                # Sleep for 1 second
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.logger.info("Shutting down...")
                self.stop()
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(5)

    
    def process_new_bar(self, current_bar: dict):
        """Process new bar and generate signal"""
        # Fetch historical bars for feature calculation
        bars = self.mt5.get_latest_rates('XAUUSDm', mt5.TIMEFRAME_M5, 200)
        
        # Generate signal
        signal, confidence = self.signal_gen.generate_signal(bars)
        
        self.logger.info(f"Signal: {signal} | Confidence: {confidence:.2f}")
        
        # Save signal to database
        self.db.save_signal({
            'timestamp': datetime.now(),
            'signal': 'BUY' if signal == 1 else 'SELL' if signal == 0 else 'NO_TRADE',
            'confidence': confidence,
        })
        
        # Emit signal to frontend
        self.ws_server.emit('new_signal', {
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        # Execute trade if valid signal
        if signal in [0, 1]:
            can_trade, reason = self.risk_mgr.can_open_trade(confidence)
            
            if can_trade:
                result = self.executor.open_position(signal)
                
                if result['success']:
                    self.logger.info(f"Trade opened: {result}")
                    
                    # Save to database
                    self.db.save_trade({
                        'ticket': result['ticket'],
                        'symbol': 'XAUUSDm',
                        'direction': 'BUY' if signal == 1 else 'SELL',
                        'entry_price': result['price'],
                        'tp_price': result['tp'],
                        'sl_price': result['sl'],
                        'lot_size': result['volume'],
                        'entry_time': datetime.now(),
                        'confidence': confidence,
                        'status': 'OPEN'
                    })
                    
                    # Emit to frontend
                    self.ws_server.emit('trade_opened', result)
                else:
                    self.logger.error(f"Trade failed: {result['error']}")
            else:
                self.logger.warning(f"Trade blocked: {reason}")
    
    def monitor_positions(self):
        """Monitor open positions for TP/SL hits"""
        positions = mt5.positions_get(symbol='XAUUSDm')
        
        for position in positions:
            # Check if position closed
            # Update database and emit to frontend
            pass
    
    def is_new_bar(self, bar: dict) -> bool:
        """Check if this is a new bar"""
        bar_time = bar['time']
        if self.last_bar_time is None or bar_time > self.last_bar_time:
            self.last_bar_time = bar_time
            return True
        return False
    
    def stop(self):
        """Stop the bot gracefully"""
        self.running = False
        self.mt5.shutdown()
        self.ws_server.stop()
        self.logger.info("Bot stopped")

if __name__ == "__main__":
    config = {
        'account': 12345678,
        'password': 'your_password',
        'server': 'YourBroker-Demo',
    }
    
    bot = LiveTradingBot(config)
    bot.start()
```

---

## 💾 Part 2: Database Layer

### 2.1 Database Schema (SQLite)

```sql
-- Trades table
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket INTEGER UNIQUE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    entry_price REAL NOT NULL,
    exit_price REAL,
    tp_price REAL,
    sl_price REAL,
    lot_size REAL NOT NULL,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    exit_reason VARCHAR(20),
    profit REAL,
    confidence REAL,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Signals table
CREATE TABLE signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    signal VARCHAR(10) NOT NULL,
    confidence REAL NOT NULL,
    was_executed BOOLEAN DEFAULT 0,
    reason VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Account snapshots
CREATE TABLE account_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    balance REAL NOT NULL,
    equity REAL NOT NULL,
    margin REAL,
    free_margin REAL,
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Daily summary
CREATE TABLE daily_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    trades_count INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    gross_profit REAL DEFAULT 0,
    gross_loss REAL DEFAULT 0,
    net_profit REAL DEFAULT 0,
    win_rate REAL,
    profit_factor REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🌐 Part 3: REST API & WebSocket

### 3.1 REST API Endpoints (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Goldmine ML Trading API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === TERMINAL MANAGEMENT (NEW) ===
@app.get("/api/terminals/discover")
async def discover_terminals():
    """Discover all installed MT5 terminals"""
    terminals = terminal_manager.discover_terminals()
    return {"terminals": terminals}

@app.post("/api/terminals/connect")
async def connect_terminal(request: TerminalConnectRequest):
    """Connect to specific MT5 terminal
    
    Body: {
        "terminal_id": "abc12345",
        "account": 12345678,
        "password": "password",
        "server": "Broker-Demo"
    }
    """
    success = terminal_manager.initialize_terminal(
        request.terminal_id,
        request.account,
        request.password,
        request.server
    )
    
    if success:
        return {
            "success": True,
            "terminal": terminal_manager.get_active_terminal()
        }
    else:
        raise HTTPException(status_code=400, detail="Connection failed")

@app.get("/api/terminals/active")
async def get_active_terminal():
    """Get currently active terminal"""
    terminal = terminal_manager.get_active_terminal()
    if terminal:
        return terminal
    raise HTTPException(status_code=404, detail="No active terminal")

@app.post("/api/terminals/switch")
async def switch_terminal(request: TerminalConnectRequest):
    """Switch to different terminal"""
    success = terminal_manager.switch_terminal(
        request.terminal_id,
        request.account,
        request.password,
        request.server
    )
    
    if success:
        return {"success": True, "message": "Terminal switched"}
    raise HTTPException(status_code=400, detail="Switch failed")

# === SYMBOL MANAGEMENT (NEW) ===
@app.get("/api/symbols/available")
async def get_available_symbols():
    """Get all available symbols from active terminal"""
    symbols = terminal_manager.get_available_symbols()
    return {"symbols": symbols}

@app.get("/api/symbols/search")
async def search_symbols(query: str):
    """Search for symbols by name
    
    Query param: ?query=XAU
    """
    all_symbols = terminal_manager.get_available_symbols()
    filtered = [s for s in all_symbols if query.upper() in s['name'].upper()]
    return {"symbols": filtered}

@app.post("/api/symbols/select")
async def select_symbol(request: SymbolSelectRequest):
    """Select symbol for trading
    
    Body: {
        "symbol": "XAUUSDm"
    }
    """
    symbol_info = mt5.symbol_info(request.symbol)
    
    if symbol_info is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    # Enable symbol in Market Watch if not already
    if not symbol_info.visible:
        if not mt5.symbol_select(request.symbol, True):
            raise HTTPException(status_code=400, detail="Failed to enable symbol")
    
    # Update active symbol in trading bot
    trading_bot.set_symbol(request.symbol)
    
    return {
        "success": True,
        "symbol": request.symbol,
        "info": {
            "name": symbol_info.name,
            "description": symbol_info.description,
            "digits": symbol_info.digits,
            "point": symbol_info.point,
            "min_volume": symbol_info.volume_min,
            "max_volume": symbol_info.volume_max,
        }
    }

@app.get("/api/symbols/current")
async def get_current_symbol():
    """Get currently selected trading symbol"""
    symbol = trading_bot.get_current_symbol()
    if symbol:
        symbol_info = mt5.symbol_info(symbol)
        return {
            "symbol": symbol,
            "info": {
                "name": symbol_info.name,
                "description": symbol_info.description,
                "digits": symbol_info.digits,
            }
        }
    raise HTTPException(status_code=404, detail="No symbol selected")

# === ACCOUNT & CONNECTION ===
@app.get("/api/account/info")
async def get_account_info():
    """Get current account information"""
    account = mt5.account_info()
    if account is None:
        raise HTTPException(status_code=503, detail="Not connected to MT5")
    
    return {
        "balance": account.balance,
        "equity": account.equity,
        "margin": account.margin,
        "free_margin": account.margin_free,
        "profit": account.profit,
        "account": account.login,
        "server": account.server,
        "company": account.company,
    }

@app.get("/api/connection/status")
async def get_connection_status():
    """Check MT5 connection status"""
    terminal = terminal_manager.get_active_terminal()
    is_connected = mt5.terminal_info() is not None
    
    return {
        "connected": is_connected,
        "terminal": terminal,
        "account": mt5.account_info().login if is_connected else None
    }

# === POSITIONS ===
@app.get("/api/positions/open")
async def get_open_positions():
    """List all open positions"""
    return [
        {
            "ticket": 123456,
            "symbol": "XAUUSDm",
            "direction": "BUY",
            "entry_price": 2645.50,
            "current_price": 2646.20,
            "tp": 2646.50,
            "sl": 2645.00,
            "profit": 7.00,
            "volume": 0.01
        }
    ]

@app.post("/api/positions/close/{ticket}")
async def close_position(ticket: int):
    """Close specific position"""
    # Call trade_executor.close_position(ticket)
    return {"success": True, "ticket": ticket}

# === METRICS ===
@app.get("/api/metrics/summary")
async def get_metrics_summary():
    """Get overall performance summary"""
    return {
        "total_trades": 247,
        "winning_trades": 145,
        "losing_trades": 102,
        "win_rate": 58.7,
        "profit_factor": 1.85,
        "net_profit": 1250.50,
        "sharpe_ratio": 1.42,
        "max_drawdown": -450.00,
        "max_drawdown_pct": -4.3
    }

@app.get("/api/metrics/equity_curve")
async def get_equity_curve():
    """Get equity curve data"""
    # Return list of {timestamp, equity} points
    return []

@app.get("/api/trades/history")
async def get_trade_history(limit: int = 50, offset: int = 0):
    """Get trade history with pagination"""
    return []

# === PYDANTIC MODELS ===
class TerminalConnectRequest(BaseModel):
    terminal_id: str
    account: int
    password: str
    server: str

class SymbolSelectRequest(BaseModel):
    symbol: str
```

---

### 3.2 WebSocket Server (Socket.IO)

```python
from socketio import AsyncServer
from fastapi import FastAPI

sio = AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
socket_app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

# Emit events from trading bot
async def emit_trade_opened(trade_data):
    await sio.emit('trade_opened', trade_data)

async def emit_trade_closed(trade_data):
    await sio.emit('trade_closed', trade_data)

async def emit_new_signal(signal_data):
    await sio.emit('new_signal', signal_data)

async def emit_metrics_update(metrics):
    await sio.emit('metrics_update', metrics)
```

---

## ⚛️ Part 4: React Frontend

### 4.1 Technology Stack

- **React 18** + **TypeScript**
- **Vite** (build tool)
- **Tailwind CSS** (styling)
- **Shadcn/ui** (component library)
- **Recharts** (charts)
- **Socket.IO Client** (real-time)
- **TanStack Query** (data fetching)
- **Zustand** (state management)

### 4.2 Project Setup

```bash
# Create Vite project
npm create vite@latest goldmine-dashboard -- --template react-ts

cd goldmine-dashboard

# Install dependencies
npm install

# Install additional packages
npm install @tanstack/react-query axios socket.io-client zustand
npm install recharts lucide-react clsx tailwind-merge
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 4.3 Folder Structure

```
src/
├── components/
│   ├── dashboard/
│   │   ├── MetricCard.tsx
│   │   ├── EquityCurve.tsx
│   │   ├── OpenPositions.tsx
│   │   ├── SignalHistory.tsx
│   │   └── TradeHistory.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Sidebar.tsx
│   └── ui/
│       ├── card.tsx
│       ├── badge.tsx
│       └── button.tsx
├── hooks/
│   ├── useWebSocket.ts
│   └── useAPI.ts
├── store/
│   ├── accountStore.ts
│   ├── tradesStore.ts
│   └── metricsStore.ts
├── services/
│   ├── api.ts
│   └── websocket.ts
├── types/
│   └── index.ts
├── utils/
│   └── formatters.ts
└── App.tsx
```

---

### 4.4 Key Components

#### MetricCard Component
```tsx
interface MetricCardProps {
  label: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
  label, value, change, icon 
}) => {
  const isPositive = change && change > 0;
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-2">
        <span className="text-slate-400 text-sm">{label}</span>
        {icon}
      </div>
      <div className="text-3xl font-bold text-white">{value}</div>
      {change !== undefined && (
        <div className={`text-sm mt-2 ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
          {isPositive ? '↑' : '↓'} {Math.abs(change)}%
        </div>
      )}
    </div>
  );
};
```

#### EquityCurve Component
```tsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const EquityCurve: React.FC = () => {
  const data = useMetricsStore(state => state.equityCurve);
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">Equity Curve</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <XAxis dataKey="timestamp" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1e293b', 
              border: '1px solid #334155' 
            }}
          />
          <Line 
            type="monotone" 
            dataKey="equity" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
```

#### OpenPositions Component
```tsx
export const OpenPositions: React.FC = () => {
  const positions = useTradesStore(state => state.openPositions);
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">Open Positions</h2>
      <div className="space-y-3">
        {positions.map(position => (
          <div key={position.ticket} className="bg-slate-700 p-4 rounded">
            <div className="flex justify-between items-center">
              <div>
                <span className="font-semibold text-white">{position.symbol}</span>
                <span className={`ml-2 px-2 py-1 rounded text-xs ${
                  position.direction === 'BUY' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                }`}>
                  {position.direction}
                </span>
              </div>
              <div className={`text-lg font-bold ${
                position.profit > 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                ${position.profit.toFixed(2)}
              </div>
            </div>
            <div className="mt-2 text-sm text-slate-400">
              Entry: {position.entry_price} | TP: {position.tp} | SL: {position.sl}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

### 4.5 WebSocket Hook

```tsx
import { useEffect } from 'react';
import { io, Socket } from 'socket.io-client';
import { useTradesStore } from '../store/tradesStore';
import { useMetricsStore } from '../store/metricsStore';
import { useAccountStore } from '../store/accountStore';

export const useWebSocket = () => {
  useEffect(() => {
    const socket: Socket = io('http://localhost:8000');
    
    socket.on('connect', () => {
      console.log('Connected to WebSocket');
    });
    
    socket.on('trade_opened', (data) => {
      useTradesStore.getState().addTrade(data);
    });
    
    socket.on('trade_closed', (data) => {
      useTradesStore.getState().closeTrade(data);
    });
    
    socket.on('new_signal', (data) => {
      // Handle new signal
      console.log('New signal:', data);
    });
    
    socket.on('metrics_update', (data) => {
      useMetricsStore.getState().updateMetrics(data);
    });
    
    socket.on('account_update', (data) => {
      useAccountStore.getState().updateAccount(data);
    });
    
    return () => {
      socket.disconnect();
    };
  }, []);
};
```

### 4.6 Zustand Stores

```typescript
// tradesStore.ts
import { create } from 'zustand';

interface Trade {
  ticket: number;
  symbol: string;
  direction: 'BUY' | 'SELL';
  entry_price: number;
  current_price?: number;
  tp: number;
  sl: number;
  profit: number;
  volume: number;
}

interface TradesState {
  openPositions: Trade[];
  closedTrades: Trade[];
  addTrade: (trade: Trade) => void;
  closeTrade: (data: any) => void;
  updatePositionProfit: (ticket: number, profit: number) => void;
}

export const useTradesStore = create<TradesState>((set) => ({
  openPositions: [],
  closedTrades: [],
  
  addTrade: (trade) => set((state) => ({
    openPositions: [...state.openPositions, trade]
  })),
  
  closeTrade: (data) => set((state) => ({
    openPositions: state.openPositions.filter(t => t.ticket !== data.ticket),
    closedTrades: [data, ...state.closedTrades]
  })),
  
  updatePositionProfit: (ticket, profit) => set((state) => ({
    openPositions: state.openPositions.map(t => 
      t.ticket === ticket ? { ...t, profit } : t
    )
  }))
}));
```

---

### 4.7 Dashboard Layout

```tsx
// App.tsx
import { MetricCard } from './components/dashboard/MetricCard';
import { EquityCurve } from './components/dashboard/EquityCurve';
import { OpenPositions } from './components/dashboard/OpenPositions';
import { SignalHistory } from './components/dashboard/SignalHistory';
import { useWebSocket } from './hooks/useWebSocket';
import { useAccountStore } from './store/accountStore';
import { useMetricsStore } from './store/metricsStore';

function App() {
  useWebSocket(); // Initialize WebSocket connection
  
  const account = useAccountStore();
  const metrics = useMetricsStore();
  
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Goldmine ML Trading</h1>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-slate-400">Connected</span>
          </div>
        </div>
      </header>
      
      {/* Main Dashboard */}
      <main className="container mx-auto p-6">
        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <MetricCard 
            label="Account Balance" 
            value={`$${account.balance.toLocaleString()}`} 
          />
          <MetricCard 
            label="Today's P&L" 
            value={`$${metrics.dailyPnl.toFixed(2)}`}
            change={metrics.dailyPnlPct}
          />
          <MetricCard 
            label="Win Rate" 
            value={`${metrics.winRate.toFixed(1)}%`}
          />
          <MetricCard 
            label="Profit Factor" 
            value={metrics.profitFactor.toFixed(2)}
          />
        </div>
        
        {/* Equity Curve */}
        <div className="mb-6">
          <EquityCurve />
        </div>
        
        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <OpenPositions />
          <SignalHistory />
        </div>
      </main>
    </div>
  );
}

export default App;
```

---

## 📝 Part 5: Implementation Timeline

### Week 1: Backend Foundation
- **Day 1-2:** MT5 Integration
  - [ ] Install MetaTrader5 package
  - [ ] Create MT5Connector class
  - [ ] Test connection with demo account
  - [ ] Implement account info retrieval
  
- **Day 3-4:** Signal Generation
  - [ ] Create SignalGenerator class
  - [ ] Load XGBoost model
  - [ ] Implement feature calculation pipeline
  - [ ] Validate against backtest features
  - [ ] Test signal generation
  
- **Day 5-7:** Trading Execution
  - [ ] Create TradeExecutor class
  - [ ] Implement order placement
  - [ ] Test on demo account
  - [ ] Create RiskManager class
  - [ ] Implement position limits

### Week 2: API & Database
- **Day 8-10:** Database Setup
  - [ ] Design database schema
  - [ ] Create SQLite database
  - [ ] Implement DatabaseManager
  - [ ] Test CRUD operations
  
- **Day 11-12:** REST API
  - [ ] Setup FastAPI
  - [ ] Implement all endpoints
  - [ ] Test with Postman
  - [ ] Add CORS configuration
  
- **Day 13-14:** WebSocket
  - [ ] Implement WebSocket server
  - [ ] Create event emitters
  - [ ] Test real-time communication

### Week 3: Main Loop & Frontend
- **Day 15-17:** Trading Bot
  - [ ] Create main trading loop
  - [ ] Implement bar close detection
  - [ ] Integrate all modules
  - [ ] Add comprehensive logging
  - [ ] Test end-to-end on demo
  
- **Day 18-19:** React Setup
  - [ ] Initialize Vite project
  - [ ] Setup Tailwind CSS
  - [ ] Create basic layout
  - [ ] Setup WebSocket client
  
- **Day 20-21:** Dashboard Components
  - [ ] Create MetricCard component
  - [ ] Create EquityCurve chart
  - [ ] Create OpenPositions table
  - [ ] Create SignalHistory list
  - [ ] Implement Zustand stores

### Week 4: Integration & Testing
- **Day 22-24:** Full Integration
  - [ ] Connect frontend to backend
  - [ ] Test WebSocket events
  - [ ] Test all API endpoints
  - [ ] Fix bugs and issues
  
- **Day 25-26:** Polish & Optimization
  - [ ] Improve UI/UX
  - [ ] Add animations
  - [ ] Optimize performance
  - [ ] Add error handling
  
- **Day 27-28:** Documentation & Demo
  - [ ] Write user documentation
  - [ ] Create setup guide
  - [ ] Record demo video
  - [ ] Prepare for deployment

---

## 🔧 Part 6: MT5 Account Setup Guide

### 6.1 Installing MetaTrader 5

1. **Download MT5:**
   - Visit your broker's website
   - Download MT5 terminal for Windows
   - Install and launch

2. **Open Demo Account:**
   - File → Open Account
   - Select your broker's server
   - Choose "Demo Account"
   - Fill in registration form
   - Save login credentials: Account, Password, Server

3. **Test Connection:**
   ```python
   import MetaTrader5 as mt5
   
   if not mt5.initialize():
       print("MT5 initialization failed")
       quit()
   
   print("MT5 version:", mt5.version())
   
   account = 12345678  # Your demo account
   password = "your_password"
   server = "YourBroker-Demo"
   
   if mt5.login(account, password=password, server=server):
       print("Logged in successfully!")
       print(mt5.account_info()._asdict())
   else:
       print("Login failed")
   
   mt5.shutdown()
   ```

### 6.2 Symbol Configuration

**Enable XAUUSDm in Market Watch:**
1. Open MT5
2. View → Market Watch (Ctrl+M)
3. Right-click → Symbols
4. Search for "XAUUSD" or "XAUUSDm"
5. Select and click "Show"
6. Verify symbol appears in Market Watch

**Check Symbol Specifications:**
```python
import MetaTrader5 as mt5

mt5.initialize()
mt5.login(account, password, server)

symbol_info = mt5.symbol_info("XAUUSDm")
if symbol_info is not None:
    print(f"Symbol: {symbol_info.name}")
    print(f"Point: {symbol_info.point}")
    print(f"Digits: {symbol_info.digits}")
    print(f"Min Volume: {symbol_info.volume_min}")
    print(f"Max Volume: {symbol_info.volume_max}")
    print(f"Volume Step: {symbol_info.volume_step}")
```

### 6.3 Configuration File

Create `config.yaml`:
```yaml
# MT5 Connection
mt5:
  account: 12345678
  password: "your_password"
  server: "YourBroker-Demo"
  symbol: "XAUUSDm"

# Trading Parameters
trading:
  lot_size: 0.01
  tp_pips: 100
  sl_pips: 50
  pip_value: 0.01
  magic_number: 123456

# Risk Management
risk:
  max_positions: 1
  max_daily_loss: 400
  max_daily_profit: 1000
  min_confidence: 0.5

# API Configuration
api:
  host: "0.0.0.0"
  port: 8000
  cors_origin: "http://localhost:5173"

# Database
database:
  path: "data/live_trading.db"

# Logging
logging:
  level: "INFO"
  file: "logs/live_trading.log"
```

---

## 📦 Part 7: Dependencies & Requirements

### 7.1 Python Backend Requirements

Create `requirements-live.txt`:
```txt
# MT5 Integration
MetaTrader5>=5.0.45

# ML & Data Processing
xgboost>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
ta>=0.11.0
joblib>=1.3.0

# API & WebSocket
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-socketio>=5.10.0
pydantic>=2.4.0
python-multipart>=0.0.6

# Database
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# Utilities
pyyaml>=6.0
python-dotenv>=1.0.0
```

### 7.2 Frontend Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.2.2",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0",
    "zustand": "^4.4.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.294.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

### 7.3 Installation Commands

**Backend:**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements-live.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

---

## 🚀 Part 8: Running the System

### 8.1 Start Backend

```bash
# Terminal 1: Start FastAPI server
cd src/live_trading
python -m uvicorn api.rest_api:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start trading bot
python main.py
```

### 8.2 Start Frontend

```bash
# Terminal 3: Start Vite dev server
cd frontend
npm run dev
```

### 8.3 Access Dashboard

Open browser: `http://localhost:5173`

---

## ⚠️ Part 9: Safety & Best Practices

### 9.1 Pre-Launch Checklist

- [ ] Test all modules individually
- [ ] Test on demo account first (MANDATORY)
- [ ] Verify feature parity with backtest
- [ ] Test WebSocket reconnection
- [ ] Test database operations
- [ ] Test emergency stop button
- [ ] Verify TP/SL calculations
- [ ] Test with different market conditions
- [ ] Monitor for 1-2 weeks on demo before live

### 9.2 Risk Management Rules

1. **Never skip demo testing**
2. **Start with minimum lot size (0.01)**
3. **Set daily loss limit**
4. **One position at a time (initially)**
5. **Monitor first week 24/7**
6. **Keep detailed logs**
7. **Have kill switch ready**

### 9.3 Monitoring

**Key Metrics to Watch:**
- Slippage (entry vs expected)
- Execution time
- Signal frequency
- Win rate deviation from backtest
- Drawdown patterns
- API latency

**Red Flags:**
- Win rate < 45% (significantly worse than backtest)
- Profit factor < 1.0
- Drawdown > 20%
- Frequent connection errors
- Slippage > 5 pips consistently

---

## 📊 Part 10: Dashboard Design Specifications

### 10.1 Color Palette

```css
/* Dark Theme */
:root {
  /* Primary Colors */
  --primary-blue: #3b82f6;
  --success-green: #10b981;
  --danger-red: #ef4444;
  --warning-orange: #f59e0b;
  
  /* Background Colors */
  --bg-primary: #0f172a;      /* Main background */
  --bg-secondary: #1e293b;    /* Cards background */
  --bg-tertiary: #334155;     /* Hover states */
  
  /* Text Colors */
  --text-primary: #f1f5f9;    /* Main text */
  --text-secondary: #94a3b8;  /* Secondary text */
  --text-muted: #64748b;      /* Muted text */
  
  /* Border Colors */
  --border-default: #334155;
  --border-focus: #3b82f6;
}
```

### 10.2 Typography

```css
/* Font Sizes */
.text-xs { font-size: 0.75rem; }    /* 12px */
.text-sm { font-size: 0.875rem; }   /* 14px */
.text-base { font-size: 1rem; }     /* 16px */
.text-lg { font-size: 1.125rem; }   /* 18px */
.text-xl { font-size: 1.25rem; }    /* 20px */
.text-2xl { font-size: 1.5rem; }    /* 24px */
.text-3xl { font-size: 1.875rem; }  /* 30px */

/* Font Weights */
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
```

### 10.3 Component Spacing

```css
/* Padding */
.p-2  { padding: 0.5rem; }   /* 8px */
.p-4  { padding: 1rem; }     /* 16px */
.p-6  { padding: 1.5rem; }   /* 24px */
.p-8  { padding: 2rem; }     /* 32px */

/* Margin */
.m-2  { margin: 0.5rem; }
.m-4  { margin: 1rem; }
.m-6  { margin: 1.5rem; }

/* Gap */
.gap-2 { gap: 0.5rem; }
.gap-4 { gap: 1rem; }
.gap-6 { gap: 1.5rem; }
```

### 10.4 Responsive Breakpoints

```css
/* Mobile First */
sm: 640px   /* Tablet */
md: 768px   /* Laptop */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large Desktop */
2xl: 1536px /* Extra Large */
```

### 10.5 Key Animations

```css
/* Pulse (for connection indicator) */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Slide In */
@keyframes slideIn {
  from {
    transform: translateY(-10px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

---

## 🎨 Part 11: Advanced Dashboard Features

### 11.1 Real-Time Price Chart

**Component: PriceChart.tsx**
```tsx
import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const PriceChart: React.FC = () => {
  const [priceData, setPriceData] = useState([]);
  
  useEffect(() => {
    // Update price data from WebSocket
    const socket = useWebSocket();
    
    socket.on('price_update', (data) => {
      setPriceData(prev => [...prev.slice(-100), {
        time: data.timestamp,
        price: data.price,
        signal: data.signal // Show signal markers
      }]);
    });
  }, []);
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold mb-4">XAUUSDm - M5</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={priceData}>
          <XAxis dataKey="time" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" domain={['auto', 'auto']} />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#3b82f6" 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
```

### 11.2 Trade Statistics Table

**Component: TradeStatistics.tsx**
```tsx
export const TradeStatistics: React.FC = () => {
  const metrics = useMetricsStore();
  
  const stats = [
    { label: 'Total Trades', value: metrics.totalTrades },
    { label: 'Winning Trades', value: metrics.winningTrades, color: 'text-green-400' },
    { label: 'Losing Trades', value: metrics.losingTrades, color: 'text-red-400' },
    { label: 'Win Rate', value: `${metrics.winRate.toFixed(1)}%` },
    { label: 'Profit Factor', value: metrics.profitFactor.toFixed(2) },
    { label: 'Avg Win', value: `$${metrics.avgWin.toFixed(2)}`, color: 'text-green-400' },
    { label: 'Avg Loss', value: `$${metrics.avgLoss.toFixed(2)}`, color: 'text-red-400' },
    { label: 'R:R Ratio', value: metrics.rrRatio.toFixed(2) },
    { label: 'Max Drawdown', value: `$${metrics.maxDrawdown.toFixed(2)}`, color: 'text-red-400' },
    { label: 'Sharpe Ratio', value: metrics.sharpe.toFixed(2) },
  ];
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold mb-4">Trading Statistics</h2>
      <div className="grid grid-cols-2 gap-4">
        {stats.map((stat, i) => (
          <div key={i} className="flex justify-between items-center py-2 border-b border-slate-700">
            <span className="text-slate-400">{stat.label}</span>
            <span className={`font-semibold ${stat.color || 'text-white'}`}>
              {stat.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 11.3 Signal Confidence Gauge

**Component: ConfidenceGauge.tsx**
```tsx
export const ConfidenceGauge: React.FC<{ confidence: number; signal: string }> = ({
  confidence,
  signal
}) => {
  const getColor = () => {
    if (confidence >= 0.8) return 'text-green-500';
    if (confidence >= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };
  
  const percentage = confidence * 100;
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h3 className="text-lg font-semibold mb-4">Latest Signal</h3>
      
      <div className="flex items-center justify-center mb-4">
        <div className={`text-4xl font-bold ${getColor()}`}>
          {percentage.toFixed(0)}%
        </div>
      </div>
      
      <div className="w-full bg-slate-700 rounded-full h-4 mb-4">
        <div 
          className={`h-4 rounded-full transition-all duration-300 ${
            confidence >= 0.8 ? 'bg-green-500' :
            confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      <div className="text-center">
        <span className={`px-4 py-2 rounded-lg font-semibold ${
          signal === 'BUY' ? 'bg-green-900 text-green-300' :
          signal === 'SELL' ? 'bg-red-900 text-red-300' :
          'bg-slate-700 text-slate-300'
        }`}>
          {signal}
        </span>
      </div>
    </div>
  );
};
```

---

## 🔔 Part 12: Notifications & Alerts

### 12.1 Alert System

**Component: AlertManager.tsx**
```tsx
import { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Info } from 'lucide-react';

interface Alert {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  timestamp: Date;
}

export const AlertManager: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  
  useEffect(() => {
    const socket = useWebSocket();
    
    socket.on('trade_opened', (data) => {
      addAlert('success', `Position opened: ${data.direction} at ${data.price}`);
    });
    
    socket.on('trade_closed', (data) => {
      const profit = data.profit > 0;
      addAlert(
        profit ? 'success' : 'error',
        `Position closed: ${profit ? '+' : ''}$${data.profit.toFixed(2)}`
      );
    });
    
    socket.on('error', (data) => {
      addAlert('error', data.message);
    });
  }, []);
  
  const addAlert = (type: string, message: string) => {
    const newAlert = {
      id: Date.now().toString(),
      type,
      message,
      timestamp: new Date()
    };
    
    setAlerts(prev => [newAlert, ...prev.slice(0, 9)]); // Keep last 10
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setAlerts(prev => prev.filter(a => a.id !== newAlert.id));
    }, 5000);
  };
  
  const getIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'warning': return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default: return <Info className="w-5 h-5 text-blue-500" />;
    }
  };
  
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {alerts.map(alert => (
        <div 
          key={alert.id}
          className={`bg-slate-800 border rounded-lg p-4 shadow-lg animate-slideIn flex items-start gap-3 min-w-[300px] ${
            alert.type === 'success' ? 'border-green-500' :
            alert.type === 'error' ? 'border-red-500' :
            alert.type === 'warning' ? 'border-yellow-500' :
            'border-blue-500'
          }`}
        >
          {getIcon(alert.type)}
          <div className="flex-1">
            <p className="text-white text-sm">{alert.message}</p>
            <p className="text-slate-400 text-xs mt-1">
              {alert.timestamp.toLocaleTimeString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};
```

### 12.2 Sound Notifications

**Utility: soundManager.ts**
```typescript
class SoundManager {
  private enabled: boolean = true;
  
  playTradeOpen() {
    if (this.enabled) {
      const audio = new Audio('/sounds/trade-open.mp3');
      audio.play();
    }
  }
  
  playTradeClose(profit: number) {
    if (this.enabled) {
      const sound = profit > 0 ? '/sounds/profit.mp3' : '/sounds/loss.mp3';
      const audio = new Audio(sound);
      audio.play();
    }
  }
  
  playSignal() {
    if (this.enabled) {
      const audio = new Audio('/sounds/signal.mp3');
      audio.play();
    }
  }
  
  toggle() {
    this.enabled = !this.enabled;
  }
}

export const soundManager = new SoundManager();
```

---

## ⚙️ Part 13: Settings & Configuration Panel

### 13.1 Terminal Selection Component **[NEW]**

**Component: TerminalSelector.tsx**
```tsx
import { useState, useEffect } from 'react';
import { Server, CheckCircle } from 'lucide-react';

interface Terminal {
  id: string;
  name: string;
  path: string;
  broker: string;
  connected?: boolean;
}

export const TerminalSelector: React.FC = () => {
  const [terminals, setTerminals] = useState<Terminal[]>([]);
  const [selectedTerminal, setSelectedTerminal] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [credentials, setCredentials] = useState({
    account: '',
    password: '',
    server: '',
  });
  
  useEffect(() => {
    // Discover terminals on mount
    discoverTerminals();
  }, []);
  
  const discoverTerminals = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/terminals/discover');
      const data = await response.json();
      setTerminals(data.terminals);
    } catch (error) {
      console.error('Failed to discover terminals:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const connectToTerminal = async () => {
    if (!selectedTerminal) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/terminals/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          terminal_id: selectedTerminal,
          account: parseInt(credentials.account),
          password: credentials.password,
          server: credentials.server,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Connected to ${data.terminal.name}`);
        // Update UI to show connected state
      } else {
        alert('Connection failed');
      }
    } catch (error) {
      console.error('Connection error:', error);
      alert('Connection error');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">MT5 Terminal</h2>
        <button
          onClick={discoverTerminals}
          className="text-sm text-blue-400 hover:text-blue-300"
        >
          Refresh
        </button>
      </div>
      
      {/* Terminal List */}
      <div className="space-y-2 mb-4">
        {terminals.map((terminal) => (
          <div
            key={terminal.id}
            onClick={() => setSelectedTerminal(terminal.id)}
            className={`p-4 rounded cursor-pointer transition-colors ${
              selectedTerminal === terminal.id
                ? 'bg-blue-900 border-2 border-blue-500'
                : 'bg-slate-700 border-2 border-transparent hover:bg-slate-600'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Server className="w-5 h-5 text-slate-400" />
                <div>
                  <div className="font-semibold text-white">{terminal.name}</div>
                  <div className="text-sm text-slate-400">{terminal.broker}</div>
                </div>
              </div>
              {terminal.connected && (
                <CheckCircle className="w-5 h-5 text-green-400" />
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* Connection Credentials */}
      {selectedTerminal && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Account Number</label>
            <input
              type="number"
              value={credentials.account}
              onChange={(e) => setCredentials({...credentials, account: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              placeholder="12345678"
            />
          </div>
          
          <div>
            <label className="block text-sm text-slate-400 mb-1">Password</label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              placeholder="••••••••"
            />
          </div>
          
          <div>
            <label className="block text-sm text-slate-400 mb-1">Server</label>
            <input
              type="text"
              value={credentials.server}
              onChange={(e) => setCredentials({...credentials, server: e.target.value})}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              placeholder="Broker-Demo"
            />
          </div>
          
          <button
            onClick={connectToTerminal}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded transition-colors disabled:opacity-50"
          >
            {loading ? 'Connecting...' : 'Connect'}
          </button>
        </div>
      )}
    </div>
  );
};
```

### 13.2 Symbol Selector Component **[NEW]**

**Component: SymbolSelector.tsx**
```tsx
import { useState, useEffect } from 'react';
import { Search, TrendingUp } from 'lucide-react';

interface Symbol {
  name: string;
  description: string;
  path: string;
  digits: number;
}

export const SymbolSelector: React.FC = () => {
  const [symbols, setSymbols] = useState<Symbol[]>([]);
  const [filteredSymbols, setFilteredSymbols] = useState<Symbol[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState<string>('XAUUSDm');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    loadAvailableSymbols();
  }, []);
  
  useEffect(() => {
    // Filter symbols based on search
    if (searchQuery) {
      const filtered = symbols.filter(s => 
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredSymbols(filtered);
    } else {
      setFilteredSymbols(symbols);
    }
  }, [searchQuery, symbols]);
  
  const loadAvailableSymbols = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/symbols/available');
      const data = await response.json();
      setSymbols(data.symbols);
      setFilteredSymbols(data.symbols);
    } catch (error) {
      console.error('Failed to load symbols:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const selectSymbol = async (symbolName: string) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/symbols/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: symbolName }),
      });
      
      if (response.ok) {
        setSelectedSymbol(symbolName);
        alert(`Trading symbol changed to ${symbolName}`);
      } else {
        alert('Failed to select symbol');
      }
    } catch (error) {
      console.error('Symbol selection error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">Trading Symbol</h2>
      
      {/* Current Symbol */}
      <div className="mb-4 p-4 bg-slate-700 rounded">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <div>
              <div className="font-semibold text-white">{selectedSymbol}</div>
              <div className="text-sm text-slate-400">Active Trading Symbol</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Search */}
      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search symbols..."
          className="w-full pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400"
        />
      </div>
      
      {/* Symbol List */}
      <div className="max-h-96 overflow-y-auto space-y-2">
        {loading ? (
          <div className="text-center text-slate-400 py-4">Loading symbols...</div>
        ) : filteredSymbols.length === 0 ? (
          <div className="text-center text-slate-400 py-4">No symbols found</div>
        ) : (
          filteredSymbols.slice(0, 50).map((symbol) => (
            <div
              key={symbol.name}
              onClick={() => selectSymbol(symbol.name)}
              className={`p-3 rounded cursor-pointer transition-colors ${
                selectedSymbol === symbol.name
                  ? 'bg-blue-900 border border-blue-500'
                  : 'bg-slate-700 hover:bg-slate-600'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">{symbol.name}</div>
                  <div className="text-xs text-slate-400">{symbol.description}</div>
                </div>
                <div className="text-xs text-slate-500">{symbol.path}</div>
              </div>
            </div>
          ))
        )}
      </div>
      
      <div className="mt-4 text-xs text-slate-500 text-center">
        Showing {Math.min(50, filteredSymbols.length)} of {filteredSymbols.length} symbols
      </div>
    </div>
  );
};
```

### 13.3 Settings Panel Component

**Component: SettingsPanel.tsx**
```tsx
import { useState } from 'react';

export const SettingsPanel: React.FC = () => {
  const [settings, setSettings] = useState({
    autoTrading: true,
    soundEnabled: true,
    maxPositions: 1,
    dailyLossLimit: 400,
    minConfidence: 0.5,
    lotSize: 0.01,
  });
  
  const handleSave = async () => {
    await fetch('/api/config/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });
  };
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-2xl font-bold mb-6">Trading Settings</h2>
      
      {/* Auto Trading Toggle */}
      <div className="mb-6">
        <label className="flex items-center justify-between">
          <span className="text-white font-medium">Auto Trading</span>
          <button
            className={`w-14 h-7 rounded-full transition-colors ${
              settings.autoTrading ? 'bg-green-500' : 'bg-slate-600'
            }`}
            onClick={() => setSettings({...settings, autoTrading: !settings.autoTrading})}
          >
            <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
              settings.autoTrading ? 'translate-x-8' : 'translate-x-1'
            }`} />
          </button>
        </label>
      </div>
      
      {/* Sound Toggle */}
      <div className="mb-6">
        <label className="flex items-center justify-between">
          <span className="text-white font-medium">Sound Notifications</span>
          <button
            className={`w-14 h-7 rounded-full transition-colors ${
              settings.soundEnabled ? 'bg-green-500' : 'bg-slate-600'
            }`}
            onClick={() => setSettings({...settings, soundEnabled: !settings.soundEnabled})}
          >
            <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
              settings.soundEnabled ? 'translate-x-8' : 'translate-x-1'
            }`} />
          </button>
        </label>
      </div>
      
      {/* Risk Settings */}
      <div className="space-y-4">
        <div>
          <label className="block text-slate-400 mb-2">Max Positions</label>
          <input
            type="number"
            value={settings.maxPositions}
            onChange={(e) => setSettings({...settings, maxPositions: +e.target.value})}
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white"
          />
        </div>
        
        <div>
          <label className="block text-slate-400 mb-2">Daily Loss Limit ($)</label>
          <input
            type="number"
            value={settings.dailyLossLimit}
            onChange={(e) => setSettings({...settings, dailyLossLimit: +e.target.value})}
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white"
          />
        </div>
        
        <div>
          <label className="block text-slate-400 mb-2">Min Confidence</label>
          <input
            type="number"
            step="0.1"
            min="0"
            max="1"
            value={settings.minConfidence}
            onChange={(e) => setSettings({...settings, minConfidence: +e.target.value})}
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white"
          />
        </div>
        
        <div>
          <label className="block text-slate-400 mb-2">Lot Size</label>
          <input
            type="number"
            step="0.01"
            value={settings.lotSize}
            onChange={(e) => setSettings({...settings, lotSize: +e.target.value})}
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white"
          />
        </div>
      </div>
      
      {/* Save Button */}
      <button
        onClick={handleSave}
        className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors"
      >
        Save Settings
      </button>
      
      {/* Emergency Stop */}
      <button
        className="w-full mt-4 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-lg transition-colors"
      >
        🛑 EMERGENCY STOP
      </button>
    </div>
  );
};
```

---

## 📱 Part 14: Mobile Responsiveness

### 14.1 Responsive Grid Layout

```tsx
// Mobile-first responsive design
<div className="container mx-auto p-4 md:p-6">
  {/* Metrics - Stack on mobile, grid on desktop */}
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <MetricCard label="Balance" value="$10,350" />
    <MetricCard label="P&L" value="+$125" />
    <MetricCard label="Win Rate" value="58.5%" />
    <MetricCard label="Profit Factor" value="1.85" />
  </div>
  
  {/* Main content - Stack on mobile */}
  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div className="lg:col-span-2">
      <EquityCurve />
    </div>
    <div>
      <OpenPositions />
    </div>
  </div>
</div>
```

### 14.2 Mobile Navigation

```tsx
export const MobileNav: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      {/* Hamburger Menu */}
      <button 
        className="lg:hidden"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Menu className="w-6 h-6" />
      </button>
      
      {/* Mobile Menu */}
      {isOpen && (
        <div className="fixed inset-0 bg-slate-900 z-50 lg:hidden">
          <div className="p-6">
            <button onClick={() => setIsOpen(false)}>
              <X className="w-6 h-6" />
            </button>
            
            <nav className="mt-8 space-y-4">
              <a href="#dashboard" className="block text-xl">Dashboard</a>
              <a href="#trades" className="block text-xl">Trades</a>
              <a href="#analytics" className="block text-xl">Analytics</a>
              <a href="#settings" className="block text-xl">Settings</a>
            </nav>
          </div>
        </div>
      )}
    </>
  );
};
```

---

## 🧪 Part 15: Testing Strategy

### 15.1 Backend Unit Tests

**test_signal_generator.py**
```python
import pytest
import pandas as pd
from live_trading.signal_generator import SignalGenerator

def test_signal_generator_initialization():
    """Test that model loads correctly"""
    sg = SignalGenerator('models/final/xgboost_model.pkl')
    assert sg.model is not None
    assert sg.min_confidence == 0.5

def test_feature_calculation():
    """Test feature calculation matches backtest"""
    sg = SignalGenerator('models/final/xgboost_model.pkl')
    
    # Create sample data
    data = pd.DataFrame({
        'close': [2645.0, 2645.5, 2646.0, 2645.8, 2646.2],
        'high': [2645.5, 2646.0, 2646.5, 2646.0, 2646.5],
        'low': [2644.5, 2645.0, 2645.5, 2645.5, 2645.8],
        'open': [2644.8, 2645.2, 2645.8, 2645.7, 2646.0],
    })
    
    result = sg.compute_features(data)
    
    # Check that RSI is calculated
    assert 'rsi' in result.columns
    assert not result['rsi'].isna().all()

def test_signal_generation():
    """Test signal output format"""
    sg = SignalGenerator('models/final/xgboost_model.pkl')
    
    # Mock data
    bars = create_sample_bars()
    
    signal, confidence = sg.generate_signal(bars)
    
    assert signal in [-1, 0, 1]
    assert 0 <= confidence <= 1
```

### 15.2 API Integration Tests

**test_api.py**
```python
from fastapi.testclient import TestClient
from api.rest_api import app

client = TestClient(app)

def test_account_info():
    """Test account info endpoint"""
    response = client.get("/api/account/info")
    assert response.status_code == 200
    data = response.json()
    assert 'balance' in data
    assert 'equity' in data

def test_open_positions():
    """Test open positions endpoint"""
    response = client.get("/api/positions/open")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_metrics_summary():
    """Test metrics endpoint"""
    response = client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert 'win_rate' in data
    assert 'profit_factor' in data
```

### 15.3 Frontend Component Tests

**MetricCard.test.tsx**
```tsx
import { render, screen } from '@testing-library/react';
import { MetricCard } from './MetricCard';

describe('MetricCard', () => {
  it('renders label and value', () => {
    render(<MetricCard label="Balance" value="$10,000" />);
    expect(screen.getByText('Balance')).toBeInTheDocument();
    expect(screen.getByText('$10,000')).toBeInTheDocument();
  });
  
  it('shows positive change in green', () => {
    render(<MetricCard label="P&L" value="+$100" change={5} />);
    const changeElement = screen.getByText('↑ 5%');
    expect(changeElement).toHaveClass('text-green-500');
  });
  
  it('shows negative change in red', () => {
    render(<MetricCard label="P&L" value="-$50" change={-2.5} />);
    const changeElement = screen.getByText('↓ 2.5%');
    expect(changeElement).toHaveClass('text-red-500');
  });
});
```

---

## 🚀 Part 16: Deployment Guide

### 16.1 Production Checklist

**Before Going Live:**
- [ ] Complete 2+ weeks of demo trading
- [ ] Verify win rate within 5% of backtest
- [ ] Test all emergency stops
- [ ] Verify TP/SL execution
- [ ] Test reconnection handling
- [ ] Monitor slippage patterns
- [ ] Document all API keys securely
- [ ] Setup backup system
- [ ] Configure logging properly
- [ ] Test with real market conditions

### 16.2 Environment Variables

**Backend (.env)**
```env
# MT5 Connection
MT5_ACCOUNT=12345678
MT5_PASSWORD=your_secure_password
MT5_SERVER=YourBroker-Live

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your_secret_key_here

# Database
DATABASE_URL=sqlite:///data/live_trading.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/live_trading.log

# Risk Management
MAX_DAILY_LOSS=400
MAX_POSITIONS=1
MIN_CONFIDENCE=0.5

# Notifications (optional)
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
```

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### 16.3 Docker Deployment (Optional)

**Dockerfile (Backend)**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements-live.txt .
RUN pip install --no-cache-dir -r requirements-live.txt

# Copy application
COPY src/ ./src/
COPY models/ ./models/
COPY configs/ ./configs/

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "src/live_trading/main.py"]
```

**Dockerfile (Frontend)**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - .env
    restart: unless-stopped
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### 16.4 Running in Production

```bash
# Using Docker Compose
docker-compose up -d

# Or manually
# Terminal 1: Backend
cd src/live_trading
python main.py

# Terminal 2: Frontend (production build)
cd frontend
npm run build
npm run preview
```

---

## 📊 Part 17: Performance Monitoring

### 17.1 System Health Dashboard

**Component: SystemHealth.tsx**
```tsx
export const SystemHealth: React.FC = () => {
  const [health, setHealth] = useState({
    mt5Connected: true,
    apiLatency: 45,
    wsConnected: true,
    lastSignal: new Date(),
    cpuUsage: 25,
    memoryUsage: 340,
  });
  
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold mb-4">System Health</h2>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">MT5 Connection</span>
          <span className={`flex items-center gap-2 ${
            health.mt5Connected ? 'text-green-400' : 'text-red-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              health.mt5Connected ? 'bg-green-400' : 'bg-red-400'
            }`} />
            {health.mt5Connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-slate-400">API Latency</span>
          <span className="text-white">{health.apiLatency}ms</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-slate-400">WebSocket</span>
          <span className={`flex items-center gap-2 ${
            health.wsConnected ? 'text-green-400' : 'text-red-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              health.wsConnected ? 'bg-green-400' : 'bg-red-400'
            }`} />
            {health.wsConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Last Signal</span>
          <span className="text-white">
            {formatDistanceToNow(health.lastSignal)} ago
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-slate-400">CPU Usage</span>
          <span className="text-white">{health.cpuUsage}%</span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Memory</span>
          <span className="text-white">{health.memoryUsage} MB</span>
        </div>
      </div>
    </div>
  );
};
```

### 17.2 Trade Analytics Page

```tsx
export const AnalyticsPage: React.FC = () => {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Analytics</h1>
      
      {/* Time Period Selector */}
      <div className="flex gap-2">
        <button className="px-4 py-2 bg-blue-600 rounded">Today</button>
        <button className="px-4 py-2 bg-slate-700 rounded">Week</button>
        <button className="px-4 py-2 bg-slate-700 rounded">Month</button>
        <button className="px-4 py-2 bg-slate-700 rounded">All Time</button>
      </div>
      
      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <WinRateChart />
        <ProfitDistribution />
        <TradesByHour />
        <TradesByDay />
      </div>
      
      {/* Detailed Statistics */}
      <TradeStatistics />
    </div>
  );
};
```

---

## 🔐 Part 18: Security Best Practices

### 18.1 API Security

**Implement JWT Authentication:**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

@app.get("/api/account/info")
async def get_account_info(user = Depends(verify_token)):
    # Protected endpoint
    return account_info
```

### 18.2 Secure Configuration Storage

**Use environment variables and encrypted storage:**
```python
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

class SecureConfig:
    def __init__(self):
        self.cipher = Fernet(os.getenv('ENCRYPTION_KEY'))
    
    def encrypt_password(self, password: str) -> bytes:
        return self.cipher.encrypt(password.encode())
    
    def decrypt_password(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode()
    
    @property
    def mt5_credentials(self):
        return {
            'account': int(os.getenv('MT5_ACCOUNT')),
            'password': self.decrypt_password(os.getenv('MT5_PASSWORD_ENCRYPTED')),
            'server': os.getenv('MT5_SERVER')
        }
```

### 18.3 Rate Limiting

```python
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/account/info")
@limiter.limit("30/minute")
async def get_account_info(request: Request):
    return account_data
```

### 18.4 Input Validation

```python
from pydantic import BaseModel, validator

class TradeRequest(BaseModel):
    symbol: str
    lot_size: float
    
    @validator('symbol')
    def validate_symbol(cls, v):
        allowed_symbols = ['XAUUSDm', 'EURUSD', 'GBPUSD']
        if v not in allowed_symbols:
            raise ValueError('Invalid symbol')
        return v
    
    @validator('lot_size')
    def validate_lot_size(cls, v):
        if v < 0.01 or v > 1.0:
            raise ValueError('Lot size must be between 0.01 and 1.0')
        return v
```

---

## 📚 Part 19: Documentation & User Guide

### 19.1 Quick Start Guide

**QUICK_START_LIVE.md**
```markdown
# Goldmine ML Live Trading - Quick Start

## Prerequisites
- Python 3.10+
- Node.js 18+
- MetaTrader 5 installed
- Demo account credentials

## Installation

### 1. Backend Setup
```bash
# Clone repository
cd Profitable5min

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements-live.txt
```

### 2. Configure MT5
1. Open MetaTrader 5
2. Create demo account (File → Open Account)
3. Note your: Account, Password, Server
4. Enable XAUUSDm in Market Watch

### 3. Configure Application
```bash
# Copy example config
cp config.example.yaml config.yaml

# Edit config.yaml with your MT5 credentials
```

### 4. Start Backend
```bash
cd src/live_trading
python main.py
```

### 5. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 6. Access Dashboard
Open browser: http://localhost:5173

## First Run
1. Check "Connected" indicator (green)
2. Verify account balance displays
3. Wait for first M5 bar close
4. Monitor signals in dashboard
5. Check logs for any errors

## Safety Tips
- Always start with demo account
- Monitor first 24 hours continuously
- Verify signals match expectations
- Test emergency stop button
- Keep daily loss limit conservative
```

### 19.2 Troubleshooting Guide

**Common Issues:**

**Issue: MT5 Connection Failed**
```
Solution:
1. Verify MT5 is running
2. Check credentials in config.yaml
3. Ensure symbol is enabled in Market Watch
4. Check firewall settings
```

**Issue: No Signals Generated**
```
Solution:
1. Wait for M5 bar close (every 5 minutes)
2. Check model file exists in models/final/
3. Verify sufficient historical data available
4. Check logs for feature calculation errors
```

**Issue: WebSocket Disconnects**
```
Solution:
1. Check network stability
2. Verify frontend API_URL in .env
3. Check backend is running
4. Look for CORS errors in browser console
```

---

## 🎯 Part 20: Project Summary & Next Steps

### 20.1 What You'll Build

**Backend (Python):**
- ✅ MT5 connector with authentication
- ✅ Real-time signal generator using trained XGBoost model
- ✅ Trade executor with TP/SL management
- ✅ Risk manager with position limits
- ✅ SQLite database for trade logging
- ✅ FastAPI REST endpoints
- ✅ WebSocket server for real-time updates
- ✅ Comprehensive logging system

**Frontend (React):**
- ✅ Modern dark-themed dashboard
- ✅ Real-time metrics display
- ✅ Interactive equity curve chart
- ✅ Live position monitoring
- ✅ Signal history tracker
- ✅ Settings panel with controls
- ✅ Alert/notification system
- ✅ Mobile-responsive design

### 20.2 Expected Features

**Real-Time Functionality:**
- Signal generation every M5 bar close
- Automatic trade execution based on signals
- Live P&L tracking
- WebSocket push notifications
- Account balance updates
- Connection status monitoring

**Safety Features:**
- Daily loss limit enforcement
- Maximum position limits
- Confidence threshold filtering
- Emergency stop button
- Automatic position monitoring
- Trade logging for audit

**Analytics:**
- Win rate calculation
- Profit factor tracking
- Equity curve visualization
- Drawdown monitoring
- Trade history with filtering
- Performance metrics dashboard

### 20.3 Development Roadmap

**Phase 1 (Week 1): Core Backend**
- Days 1-2: MT5 integration
- Days 3-4: Signal generation
- Days 5-7: Trade execution & risk management

**Phase 2 (Week 2): API & Database**
- Days 8-10: Database setup
- Days 11-12: REST API implementation
- Days 13-14: WebSocket server

**Phase 3 (Week 3): Frontend**
- Days 15-17: Main trading loop integration
- Days 18-19: React setup & basic layout
- Days 20-21: Dashboard components

**Phase 4 (Week 4): Testing & Deployment**
- Days 22-24: Full integration testing
- Days 25-26: UI/UX polish
- Days 27-28: Documentation & demo preparation

### 20.4 Success Criteria

**Technical:**
- [ ] MT5 connects successfully
- [ ] Signals generate every M5 bar
- [ ] Trades execute automatically
- [ ] TP/SL hits are detected
- [ ] Database logs all trades
- [ ] WebSocket updates in real-time
- [ ] Frontend displays live data

**Trading:**
- [ ] Win rate within 5% of backtest (58.5%)
- [ ] Profit factor > 1.5
- [ ] Max drawdown < 20%
- [ ] Slippage < 5 pips average
- [ ] No missed signals
- [ ] Risk limits enforced

**User Experience:**
- [ ] Dashboard loads < 2 seconds
- [ ] Real-time updates < 1 second delay
- [ ] Mobile responsive
- [ ] No UI crashes
- [ ] Clear error messages
- [ ] Intuitive navigation

### 20.5 Cost Estimate

**Development Time:** 4 weeks (part-time) or 2 weeks (full-time)

**Infrastructure Costs:**
- Demo account: Free
- Domain (optional): $10-15/year
- VPS hosting (optional): $5-20/month
- No additional costs for local deployment

**Tools (All Free):**
- VS Code
- Python + packages
- Node.js + npm
- MetaTrader 5
- SQLite

### 20.6 Immediate Next Steps

**To Start Today:**

1. **Review this plan thoroughly**
2. **Setup MT5 demo account**
3. **Create project structure:**
   ```bash
   mkdir -p src/live_trading/{api,database,utils}
   mkdir -p frontend/src/{components,hooks,store,services}
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements-live.txt
   cd frontend && npm install
   ```

5. **Start with MT5 connector:**
   - Create `src/live_trading/mt5_connector.py`
   - Test connection
   - Verify account info retrieval

6. **Build incrementally:**
   - Don't try to build everything at once
   - Test each module independently
   - Integrate step by step

---

## 📞 Support & Resources

### Learning Resources
- **MT5 Python Docs:** https://www.mql5.com/en/docs/integration/python_metatrader5
- **FastAPI Tutorial:** https://fastapi.tiangolo.com/tutorial/
- **React Docs:** https://react.dev/learn
- **Recharts Examples:** https://recharts.org/en-US/examples

### Community
- **MQL5 Forum:** https://www.mql5.com/en/forum
- **FastAPI Discord:** https://discord.gg/fastapi
- **React Community:** https://react.dev/community

---

## ✅ Final Checklist

Before starting development:
- [ ] Read entire implementation plan
- [ ] MT5 demo account created and tested
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Trained XGBoost model available
- [ ] Understand backtest logic
- [ ] Development environment ready
- [ ] Time allocated (4 weeks part-time)

**Ready? Let's build this! 🚀**

---

**Document Version:** 1.0  
**Created:** July 5, 2026  
**Last Updated:** July 5, 2026  
**Status:** Complete Implementation Plan  
**Estimated Development Time:** 4 weeks (part-time) / 2 weeks (full-time)



---

## 🔄 Part 13A: Backend Integration for Multi-Terminal/Symbol **[NEW SECTION]**

### 13A.1 Updated Main Trading Loop with Dynamic Terminal/Symbol

**main.py with terminal and symbol management:**
```python
import time
import logging
from datetime import datetime
from mt5_terminal_manager import MT5TerminalManager
from mt5_connector import MT5Connector
from signal_generator import SignalGenerator
from trade_executor import TradeExecutor
from risk_manager import RiskManager

class LiveTradingBot:
    def __init__(self):
        self.terminal_manager = MT5TerminalManager()
        self.mt5 = MT5Connector()
        self.signal_gen = None  # Will be initialized after symbol selection
        self.executor = None
        self.risk_mgr = RiskManager()
        
        self.running = False
        self.current_symbol = 'XAUUSDm'  # Default
        self.last_bar_time = {}  # Track per symbol
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def set_symbol(self, symbol: str):
        """Change trading symbol at runtime"""
        self.logger.info(f"Switching to symbol: {symbol}")
        
        # Verify symbol exists
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            self.logger.error(f"Symbol {symbol} not found")
            return False
        
        # Enable in Market Watch
        if not symbol_info.visible:
            mt5.symbol_select(symbol, True)
        
        # Update current symbol
        self.current_symbol = symbol
        
        # Reinitialize executor with new symbol
        self.executor = TradeExecutor(symbol=symbol)
        
        # Reset bar tracking for new symbol
        self.last_bar_time[symbol] = None
        
        self.logger.info(f"Symbol changed to {symbol}")
        return True
    
    def get_current_symbol(self) -> str:
        """Get currently active symbol"""
        return self.current_symbol
    
    def connect_terminal(self, terminal_id: str, account: int, 
                        password: str, server: str) -> bool:
        """Connect to specific MT5 terminal"""
        success = self.terminal_manager.initialize_terminal(
            terminal_id, account, password, server
        )
        
        if success:
            # Reinitialize signal generator after terminal switch
            self.signal_gen = SignalGenerator('models/final/xgboost_model.pkl')
            self.executor = TradeExecutor(symbol=self.current_symbol)
        
        return success
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("Starting Goldmine ML Live Trading Bot...")
        
        # Check if terminal is connected
        if not self.terminal_manager.get_active_terminal():
            self.logger.warning("No terminal connected. Waiting for connection via API...")
            # Don't return - keep bot running to accept API connections
        
        self.running = True
        
        # Main loop
        self.run_loop()
    
    def run_loop(self):
        """Main trading loop"""
        while self.running:
            try:
                # Check if connected
                if not self.terminal_manager.get_active_terminal():
                    time.sleep(5)  # Wait for connection
                    continue
                
                # Initialize components if not done
                if self.signal_gen is None:
                    self.signal_gen = SignalGenerator('models/final/xgboost_model.pkl')
                    self.executor = TradeExecutor(symbol=self.current_symbol)
                
                # Check for new bar on current symbol
                current_bar = self.get_latest_bar(self.current_symbol)
                
                if current_bar and self.is_new_bar(current_bar):
                    self.logger.info(f"New bar: {self.current_symbol} - {current_bar['time']}")
                    self.process_new_bar(current_bar)
                
                # Monitor open positions
                self.monitor_positions()
                
                # Sleep
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.logger.info("Shutting down...")
                self.stop()
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(5)
    
    def get_latest_bar(self, symbol: str) -> dict:
        """Get latest bar for symbol"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 1)
            if rates is not None and len(rates) > 0:
                return {
                    'time': rates[0]['time'],
                    'open': rates[0]['open'],
                    'high': rates[0]['high'],
                    'low': rates[0]['low'],
                    'close': rates[0]['close'],
                }
        except Exception as e:
            self.logger.error(f"Error getting bar data: {e}")
        return None
    
    def is_new_bar(self, bar: dict) -> bool:
        """Check if this is a new bar"""
        symbol = self.current_symbol
        bar_time = bar['time']
        
        if symbol not in self.last_bar_time or self.last_bar_time[symbol] is None:
            self.last_bar_time[symbol] = bar_time
            return True
        
        if bar_time > self.last_bar_time[symbol]:
            self.last_bar_time[symbol] = bar_time
            return True
        
        return False
    
    def stop(self):
        """Stop the bot gracefully"""
        self.running = False
        mt5.shutdown()
        self.logger.info("Bot stopped")

# Global instance for API access
trading_bot = LiveTradingBot()
terminal_manager = trading_bot.terminal_manager

# Start bot in background thread when API starts
import threading
bot_thread = threading.Thread(target=trading_bot.start, daemon=True)
bot_thread.start()
```

### 13A.2 Complete Settings Page Integration

**Page: Settings.tsx (Complete)**
```tsx
import { TerminalSelector } from '../components/settings/TerminalSelector';
import { SymbolSelector } from '../components/settings/SymbolSelector';
import { SettingsPanel } from '../components/settings/SettingsPanel';
import { AlertCircle } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-slate-400">
          Configure your MT5 connection, trading symbol, and risk parameters
        </p>
      </div>
      
      {/* Info Banner */}
      <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4 mb-6 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-200">
          <strong>Multi-Terminal Support:</strong> You can switch between different MT5 
          installations and trade any available symbol. Changes take effect immediately.
        </div>
      </div>
      
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Terminal Selection */}
        <div>
          <TerminalSelector />
        </div>
        
        {/* Symbol Selection */}
        <div>
          <SymbolSelector />
        </div>
        
        {/* Trading Settings */}
        <div>
          <SettingsPanel />
        </div>
      </div>
    </div>
  );
};
```

### 13A.3 Updated TypeScript Types

**types/index.ts:**
```typescript
export interface Terminal {
  id: string;
  name: string;
  path: string;
  broker: string;
  connected?: boolean;
  account?: number;
}

export interface Symbol {
  name: string;
  description: string;
  path: string;
  digits: number;
  trade_mode?: number;
  point?: number;
  min_volume?: number;
  max_volume?: number;
}

export interface TerminalConnectRequest {
  terminal_id: string;
  account: number;
  password: string;
  server: string;
}

export interface SymbolSelectRequest {
  symbol: string;
}

export interface ConnectionStatus {
  connected: boolean;
  terminal: Terminal | null;
  account: number | null;
  symbol: string;
}
```

---
