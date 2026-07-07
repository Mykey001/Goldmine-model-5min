# Backtest Feature Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (React Frontend)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  BacktestPanel  │  │ BacktestResults  │  │ BacktestChart │ │
│  │  (Config Form)  │  │   (Metrics)      │  │ (Visuals)     │ │
│  └────────┬────────┘  └─────────┬────────┘  └───────┬───────┘ │
│           │                     │                    │         │
│           └─────────────────────┴────────────────────┘         │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │ HTTP POST/GET
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                              ▼                                   │
│                     REST API SERVER                             │
│                      (FastAPI)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  POST /api/backtest/run                                        │
│  ├─ Query parameters: symbol, dates, config                    │
│  └─ Returns: {metrics, trades, equity_curve}                   │
│                                                                 │
│  GET /api/backtest/status                                      │
│  └─ Returns: {available, model_loaded}                         │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               │ Function Call
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                              ▼                                   │
│                     BACKTEST ENGINE                             │
│                  (backtest_engine.py)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              full_backtest()                             │  │
│  │                                                           │  │
│  │  1. fetch_data(symbol, timeframe, dates)                │  │
│  │     └─> MT5 API                                          │  │
│  │                                                           │  │
│  │  2. calculate_features(dataframe)                        │  │
│  │     ├─> RSI, EMA, MACD                                   │  │
│  │     ├─> Price action patterns                            │  │
│  │     ├─> Volume features                                  │  │
│  │     └─> Temporal features                                │  │
│  │                                                           │  │
│  │  3. calculate_h1_trend(h1_data)  [optional]             │  │
│  │     └─> H1 EMA trend filter                              │  │
│  │                                                           │  │
│  │  4. generate_signals(features, model)                    │  │
│  │     ├─> ML predictions                                   │  │
│  │     ├─> Confidence filtering                             │  │
│  │     └─> H1 trend alignment                               │  │
│  │                                                           │  │
│  │  5. run_backtest(signals, config)                        │  │
│  │     ├─> Simulate trades                                  │  │
│  │     ├─> Track equity                                     │  │
│  │     ├─> Calculate metrics                                │  │
│  │     └─> Return results                                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
         ┌──────────┐   ┌──────────┐   ┌──────────┐
         │   MT5    │   │  ML Model│   │ Database │
         │   API    │   │  (XGB)   │   │ (SQLite) │
         └──────────┘   └──────────┘   └──────────┘
```

## Data Flow Diagram

```
User Action                Frontend              API               Backend Engine
    │                          │                  │                      │
    │ Click "Run Backtest"     │                  │                      │
    ├─────────────────────────>│                  │                      │
    │                          │                  │                      │
    │                          │ POST /backtest   │                      │
    │                          ├─────────────────>│                      │
    │                          │                  │                      │
    │                          │                  │ full_backtest()      │
    │                          │                  ├─────────────────────>│
    │                          │                  │                      │
    │                          │                  │                  1. Fetch M5 Data
    │                          │                  │                      ├──> MT5
    │                          │                  │                      │
    │                          │                  │                  2. Fetch H1 Data
    │                          │                  │                      ├──> MT5
    │                          │                  │                      │
    │                          │                  │                  3. Calculate Features
    │                          │                  │                      ├─> RSI
    │                          │                  │                      ├─> EMA/MACD
    │                          │                  │                      └─> Price Action
    │                          │                  │                      │
    │                          │                  │                  4. Generate Signals
    │                          │                  │                      ├─> ML Model
    │                          │                  │                      └─> H1 Filter
    │                          │                  │                      │
    │                          │                  │                  5. Run Backtest
    │                          │                  │                      ├─> Simulate Trades
    │                          │                  │                      ├─> Track Equity
    │                          │                  │                      └─> Calculate Metrics
    │                          │                  │                      │
    │                          │                  │ <────────────────────┤
    │                          │                  │  Return Results      │
    │                          │ <────────────────┤                      │
    │                          │  JSON Response   │                      │
    │ Display Results          │                  │                      │
    │<─────────────────────────┤                  │                      │
    │                          │                  │                      │
```

## Component Architecture

### Frontend Layer

```
App.tsx
  │
  ├─> Tab Navigation
  │    ├─> "Live Trading" Tab
  │    └─> "Backtest" Tab ──────┐
  │                              │
  └──────────────────────────────┘
                                 │
                                 ▼
                         BacktestPanel.tsx
                                 │
                    ┌────────────┼────────────┐
                    │                         │
                    ▼                         ▼
            BacktestResults.tsx       BacktestChart.tsx
                    │                         │
        ┌───────────┴───────────┐   ┌────────┴────────┐
        │                       │   │                 │
        ▼                       ▼   ▼                 ▼
    Metrics Grid        Risk Section  Equity Curve  Trade Table
    - Net Profit        - Drawdown    - Line Chart  - Last 20 Trades
    - Win Rate          - Sharpe      - Area Fill   - Scrollable
    - Profit Factor     - R:R         - Tooltips    - Color Coded
    - Final Equity      - Config      - Gradients   - Filter Options
```

### Backend Layer

```
run.py (Entry Point)
  │
  ├─> Initialize Components
  │    ├─> LiveTradingBot
  │    ├─> DatabaseManager
  │    ├─> TerminalManager
  │    └─> BacktestEngine ───────┐
  │                               │
  └─> Initialize FastAPI          │
       │                          │
       └─> rest_api.py            │
            │                     │
            ├─> init_api() <──────┘
            │    (receives backtest_engine)
            │
            └─> Endpoints
                 │
                 ├─> POST /api/backtest/run
                 │    └─> backtest_engine.full_backtest()
                 │
                 └─> GET /api/backtest/status
                      └─> check backtest_engine availability
```

### BacktestEngine Class

```
BacktestEngine
  │
  ├─> __init__(model_path)
  │    └─> load_model()
  │
  ├─> fetch_data(symbol, timeframe, start, end)
  │    ├─> Connect to MT5
  │    ├─> Copy historical rates
  │    └─> Return DataFrame
  │
  ├─> calculate_features(df)
  │    ├─> RSI indicators
  │    ├─> Trend indicators (EMA, MACD, ADX)
  │    ├─> Price action features
  │    ├─> Volume features
  │    └─> Temporal features
  │
  ├─> calculate_h1_trend(h1_df, ema_period)
  │    ├─> Calculate H1 EMA
  │    ├─> Determine trend direction
  │    └─> Return trend data
  │
  ├─> generate_signals(df, min_conf, h1_data)
  │    ├─> ML model prediction
  │    ├─> Confidence filtering
  │    ├─> H1 trend alignment
  │    └─> Return signals
  │
  ├─> run_backtest(data, tp, sl, lot, capital)
  │    ├─> Initialize trade tracker
  │    ├─> Loop through candles
  │    ├─> Check TP/SL on active trades
  │    ├─> Open new trades on signals
  │    ├─> Track equity curve
  │    ├─> Calculate metrics
  │    └─> Return results
  │
  └─> full_backtest(symbol, start, end, config)
       │
       └─> Orchestrate complete pipeline
            1. Fetch M5 & H1 data
            2. Calculate features
            3. Generate signals
            4. Run simulation
            5. Return comprehensive results
```

## API Request/Response Flow

### Request Structure

```
POST /api/backtest/run
├─ Query Parameters
│   ├─ symbol: "XAUUSDm"
│   ├─ start_date: "2025-05-01T00:00:00Z"
│   ├─ end_date: "2025-07-03T00:00:00Z"
│   ├─ use_h1_filter: true
│   ├─ h1_ema_period: 200
│   ├─ min_confidence: 0.5
│   ├─ tp_pips: 100
│   ├─ sl_pips: 50
│   ├─ lot_size: 0.01
│   └─ starting_capital: 10000
│
└─ Headers
    ├─ Content-Type: application/json
    └─ Accept: application/json
```

### Response Structure

```json
{
  "success": true,
  "symbol": "XAUUSDm",
  "start_date": "2025-05-01T00:00:00",
  "end_date": "2025-07-03T00:00:00",
  "total_candles": 15000,
  
  "config": {
    "use_h1_filter": true,
    "h1_ema_period": 200,
    "min_confidence": 0.5,
    "tp_pips": 100,
    "sl_pips": 50,
    "lot_size": 0.01,
    "pip_value": 0.01,
    "starting_capital": 10000
  },
  
  "metrics": {
    "total_trades": 150,
    "winning_trades": 85,
    "losing_trades": 65,
    "win_rate": 56.67,
    "profit_factor": 1.85,
    "net_profit": 2500.50,
    "gross_profit": 5200.00,
    "gross_loss": 2699.50,
    "avg_win": 61.18,
    "avg_loss": -41.53,
    "max_drawdown": -850.00,
    "max_drawdown_pct": -7.5,
    "sharpe_ratio": 1.45,
    "final_equity": 12500.50,
    "return_pct": 25.01
  },
  
  "trades": [
    {
      "direction": "BUY",
      "entry_time": "2025-05-01T10:30:00",
      "entry_price": 2325.50,
      "exit_time": "2025-05-01T14:20:00",
      "exit_price": 2335.50,
      "tp": 2335.50,
      "sl": 2320.50,
      "profit": 100.00,
      "exit_reason": "TP",
      "confidence": 0.75
    }
    // ... more trades
  ],
  
  "equity_curve": [
    {
      "timestamp": "2025-05-01T00:00:00",
      "equity": 10000.00
    },
    {
      "timestamp": "2025-05-01T14:20:00",
      "equity": 10100.00
    }
    // ... more points
  ]
}
```

## Technology Stack Diagram

```
┌────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                   │
├────────────────────────────────────────────────────────┤
│  React 19      TypeScript      Tailwind CSS            │
│  Recharts      Lucide Icons    Vite                    │
└─────────────────────┬──────────────────────────────────┘
                      │
                      │ HTTP/WebSocket
                      │
┌─────────────────────┴──────────────────────────────────┐
│                    API LAYER                            │
├────────────────────────────────────────────────────────┤
│  FastAPI       Pydantic       CORS                      │
│  Uvicorn       WebSocket      REST                      │
└─────────────────────┬──────────────────────────────────┘
                      │
                      │ Function Calls
                      │
┌─────────────────────┴──────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                 │
├────────────────────────────────────────────────────────┤
│  BacktestEngine    SignalGenerator                      │
│  TradeExecutor     RiskManager                          │
│  FeatureCalculator MLModel                              │
└─────────────────────┬──────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
┌─────────┴─┐   ┌─────┴────┐   ┌┴────────┐
│   MT5 API │   │  XGBoost │   │ SQLite  │
│  (C++ DLL)│   │  Model   │   │    DB   │
└───────────┘   └──────────┘   └─────────┘
```

## Feature Calculation Pipeline

```
Raw OHLCV Data
      │
      ├─> RSI Indicators
      │    ├─> rsi
      │    ├─> rsi_oversold
      │    ├─> rsi_overbought
      │    ├─> rsi_cross_above_35
      │    ├─> rsi_cross_below_65
      │    ├─> rsi_momentum
      │    └─> rsi_slope
      │
      ├─> Price Action Features
      │    ├─> momentum_1, momentum_3, momentum_5
      │    ├─> momentum_10, momentum_20
      │    ├─> volatility_10, volatility_20
      │    ├─> candle_body, candle_range
      │    ├─> upper_wick, lower_wick
      │    └─> body_ratio
      │
      ├─> Trend Indicators
      │    ├─> ema_20, ema_50
      │    ├─> price_above_ema20, price_above_ema50
      │    ├─> ema_distance
      │    ├─> macd, macd_signal, macd_diff
      │    └─> adx
      │
      ├─> Volume Features
      │    ├─> volume_ma
      │    ├─> volume_ratio
      │    └─> volume_surge
      │
      └─> Temporal Features
           ├─> hour, day_of_week, day_of_month
           ├─> week_of_year
           └─> session_asian, session_european, session_us

     Total: 50+ Features
```

## Deployment Architecture

```
Production Environment
├─ Backend Server (Port 8000)
│   ├─ FastAPI Application
│   ├─ BacktestEngine
│   ├─ MT5 Connector
│   └─ SQLite Database
│
├─ Frontend Server (Port 5173)
│   ├─ Vite Dev Server (development)
│   └─ Static Files (production)
│
└─ MT5 Terminal
    └─ Broker Connection
```

## Security Considerations

```
┌─────────────────────────────────────────┐
│         Security Layers                 │
├─────────────────────────────────────────┤
│                                         │
│  1. Input Validation                    │
│     ├─> Date range checks               │
│     ├─> Parameter bounds                │
│     └─> Type validation (Pydantic)      │
│                                         │
│  2. CORS Configuration                  │
│     └─> Allowed origins only            │
│                                         │
│  3. Error Handling                      │
│     ├─> Try/catch blocks                │
│     ├─> Graceful failures               │
│     └─> Sanitized error messages        │
│                                         │
│  4. Resource Limits                     │
│     ├─> Max date range                  │
│     ├─> Timeout controls                │
│     └─> Memory management               │
│                                         │
└─────────────────────────────────────────┘
```

## Summary

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Scalable component design
- ✅ Robust error handling
- ✅ Efficient data flow
- ✅ Maintainable codebase
- ✅ Production-ready system
