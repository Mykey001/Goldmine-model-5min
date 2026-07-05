# Multi-Terminal & Symbol Selection Feature

## 🎯 Overview

Added comprehensive support for:
- **Multiple MT5 Terminals**: Switch between different MT5 installations
- **Any Symbol Trading**: Select and trade any available symbol
- **Frontend Controls**: User-friendly interface for terminal and symbol management

---

## 🔧 Backend Changes

### 1. New Module: `mt5_terminal_manager.py`

**Purpose:** Discover and manage multiple MT5 terminals

**Key Features:**
- Auto-discover all MT5 installations on system
- Store terminal configurations (path, broker, name)
- Switch between terminals at runtime
- Manage terminal connections

**Core Methods:**
```python
discover_terminals()          # Find all MT5 installations
initialize_terminal()         # Connect to specific terminal
switch_terminal()             # Change active terminal
get_active_terminal()         # Get current terminal info
get_available_symbols()       # List all symbols from active terminal
```

### 2. Updated: `mt5_connector.py`

**Changes:**
- Added `terminal_path` parameter to `initialize()`
- Support for dynamic terminal switching
- Symbol-agnostic connection handling

### 3. New API Endpoints

**Terminal Management:**
```
GET  /api/terminals/discover     # Discover all MT5 installations
POST /api/terminals/connect      # Connect to specific terminal
GET  /api/terminals/active       # Get active terminal info
POST /api/terminals/switch       # Switch terminals
```

**Symbol Management:**
```
GET  /api/symbols/available      # List all symbols
GET  /api/symbols/search?query=  # Search symbols
POST /api/symbols/select         # Select trading symbol
GET  /api/symbols/current        # Get current symbol
```

### 4. Updated: `main.py`

**Changes:**
- Added `set_symbol(symbol)` method
- Added `get_current_symbol()` method
- Added `connect_terminal()` method
- Per-symbol bar tracking
- Dynamic component reinitialization on symbol change

---

## 🎨 Frontend Changes

### 1. New Component: `TerminalSelector.tsx`

**Features:**
- Display all discovered MT5 terminals
- Visual indication of active terminal
- Connection form (account, password, server)
- One-click terminal switching

**UI Elements:**
- Terminal cards with broker info
- Connection status indicators
- Credential input fields
- Connect/Switch buttons

### 2. New Component: `SymbolSelector.tsx`

**Features:**
- Display all available symbols
- Real-time search/filter
- Current symbol indicator
- One-click symbol selection

**UI Elements:**
- Search bar with live filtering
- Scrollable symbol list
- Symbol descriptions and paths
- Active symbol highlighting

### 3. New Page: `Settings.tsx`

**Layout:**
```
┌─────────────────────────────────────────────┐
│  Settings                                    │
├─────────────────┬─────────────────┬─────────┤
│  Terminal       │  Symbol         │  Risk   │
│  Selector       │  Selector       │  Config │
│                 │                 │         │
│  [Terminals]    │  [Search]       │  [Auto] │
│  • Terminal 1   │  XAUUSDm       │  Trading│
│  • Terminal 2   │  EURUSD        │         │
│                 │  GBPUSD        │  [Lots] │
│  [Connect]      │  ...           │  [Stop] │
└─────────────────┴─────────────────┴─────────┘
```

### 4. Updated: `App.tsx`

**Changes:**
- Added Settings navigation link
- Page routing (Dashboard ↔ Settings)
- Header with navigation tabs

---

## 📋 Usage Workflow

### Terminal Setup

1. **Discover Terminals**
   - Frontend calls `/api/terminals/discover`
   - Backend scans system for MT5 installations
   - Returns list of found terminals

2. **Connect to Terminal**
   - User selects terminal from list
   - Enters account credentials
   - Clicks "Connect"
   - Backend initializes selected terminal

3. **Switch Terminals** (Optional)
   - Select different terminal
   - Enter credentials
   - Click "Switch"
   - System reconnects to new terminal

### Symbol Selection

1. **Load Available Symbols**
   - Frontend calls `/api/symbols/available`
   - Backend returns all symbols from active terminal
   - Displayed in searchable list

2. **Search Symbols**
   - User types in search box
   - Frontend filters list in real-time
   - Shows matching symbols

3. **Select Symbol**
   - User clicks on symbol
   - Frontend calls `/api/symbols/select`
   - Backend updates active symbol
   - Trading bot starts monitoring new symbol

---

## 🔄 Data Flow

```
User Action (Frontend)
    │
    ├─ Discover Terminals
    │   └─> GET /api/terminals/discover
    │       └─> MT5TerminalManager.discover_terminals()
    │           └─> Returns: [Terminal list]
    │
    ├─ Connect Terminal
    │   └─> POST /api/terminals/connect
    │       └─> MT5TerminalManager.initialize_terminal()
    │           └─> mt5.initialize(path)
    │           └─> mt5.login(account, password, server)
    │
    ├─ Load Symbols
    │   └─> GET /api/symbols/available
    │       └─> mt5.symbols_get()
    │           └─> Returns: [Symbol list]
    │
    └─ Select Symbol
        └─> POST /api/symbols/select
            └─> LiveTradingBot.set_symbol(symbol)
                └─> mt5.symbol_select(symbol, True)
                └─> Reinitialize TradeExecutor
                └─> Reset bar tracking
```

---

## 🛠️ Configuration Example

**Multiple Terminals Setup:**
```python
# Terminal 1: Demo Account
{
    'id': 'abc12345',
    'path': 'C:/Program Files/MetaTrader 5/terminal64.exe',
    'name': 'MetaTrader 5',
    'broker': 'Broker A'
}

# Terminal 2: Live Account  
{
    'id': 'def67890',
    'path': 'C:/Program Files/MT5-Broker/terminal64.exe',
    'name': 'MT5-Broker',
    'broker': 'Broker B'
}
```

**Symbol Selection Examples:**
- Gold: `XAUUSDm`, `XAUUSD`
- Forex: `EURUSD`, `GBPUSD`, `USDJPY`
- Indices: `US30`, `NAS100`, `SPX500`
- Crypto: `BTCUSD`, `ETHUSD`

---

## ✅ Testing Checklist

**Terminal Management:**
- [ ] Discover terminals successfully
- [ ] Connect to first terminal
- [ ] Switch to second terminal
- [ ] Verify connection status updates
- [ ] Test with invalid credentials

**Symbol Management:**
- [ ] Load all symbols
- [ ] Search for specific symbol
- [ ] Select different symbol
- [ ] Verify symbol enables in Market Watch
- [ ] Test signal generation on new symbol

**Integration:**
- [ ] Settings page loads correctly
- [ ] Terminal selector shows all terminals
- [ ] Symbol selector shows all symbols
- [ ] Connection status updates in real-time
- [ ] Bot continues running after symbol change

---

## 🚀 Benefits

1. **Flexibility**: Trade any symbol without code changes
2. **Multi-Account**: Switch between demo and live accounts
3. **Multi-Broker**: Use different brokers simultaneously
4. **User-Friendly**: No config file editing required
5. **Real-Time**: Changes apply immediately

---

## 📝 Next Steps

1. Implement terminal discovery on backend
2. Create frontend components
3. Test with multiple MT5 installations
4. Add error handling for failed connections
5. Implement symbol validation
6. Add connection timeout handling
7. Store last-used terminal/symbol preferences

---

**Feature Status:** ✅ Complete Design  
**Implementation Time:** 2-3 days  
**Priority:** High (enables multi-strategy trading)
