"""
REST API for live trading system using FastAPI
"""
import os
import logging
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import (
    TerminalConnectRequest, SymbolSelectRequest, ClosePositionRequest,
    ModifyPositionRequest, ConfigUpdateRequest, TerminalInfo, SymbolInfo,
    AccountInfo, PositionInfo, TradeInfo, SignalInfo, MetricsSummary,
    DailyStats, EquityPoint, ConnectionStatus, HealthStatus, APIResponse,
    ErrorResponse
)

# Import trading modules (will be injected by main.py)
trading_bot = None
terminal_manager = None
db_manager = None

# Initialize FastAPI app
app = FastAPI(
    title="Goldmine ML Live Trading API",
    description="REST API for live trading with ML signals",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)


# ===== DEPENDENCY INJECTION =====

def get_trading_bot():
    """Dependency to get trading bot instance"""
    if trading_bot is None:
        raise HTTPException(status_code=503, detail="Trading bot not initialized")
    return trading_bot


def get_terminal_manager():
    """Dependency to get terminal manager instance"""
    if terminal_manager is None:
        raise HTTPException(status_code=503, detail="Terminal manager not initialized")
    return terminal_manager


def get_db_manager():
    """Dependency to get database manager instance"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return db_manager


# ===== EXCEPTION HANDLERS =====

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# ===== HEALTH & STATUS =====

@app.get("/api/health", response_model=HealthStatus, tags=["System"])
async def health_check(bot=Depends(get_trading_bot)):
    """System health check"""
    import time
    import MetaTrader5 as mt5
    
    mt5_connected = mt5.terminal_info() is not None if mt5 else False
    
    return HealthStatus(
        status="healthy" if mt5_connected else "degraded",
        mt5_connected=mt5_connected,
        database_connected=db_manager is not None,
        model_loaded=bot.signal_gen is not None if bot else False,
        uptime_seconds=time.time() - bot.start_time if hasattr(bot, 'start_time') else 0,
        last_signal_time=None,  # TODO: Track last signal time
        open_positions=len(bot.executor.get_open_positions()) if bot.executor else 0
    )


@app.get("/api/connection/status", response_model=ConnectionStatus, tags=["Connection"])
async def get_connection_status(bot=Depends(get_trading_bot), tm=Depends(get_terminal_manager)):
    """Get MT5 connection status"""
    import MetaTrader5 as mt5
    
    terminal = tm.get_active_terminal()
    is_connected = mt5.terminal_info() is not None
    
    return ConnectionStatus(
        connected=is_connected,
        terminal=TerminalInfo(**terminal) if terminal else None,
        account=terminal.get('account') if terminal else None,
        symbol=bot.current_symbol if bot else None
    )


# ===== TERMINAL MANAGEMENT =====

@app.get("/api/terminals/discover", response_model=dict, tags=["Terminals"])
async def discover_terminals(tm=Depends(get_terminal_manager)):
    """Discover all installed MT5 terminals"""
    terminals = tm.discover_terminals()
    return {"terminals": [TerminalInfo(**t).dict() for t in terminals]}


@app.post("/api/terminals/connect", response_model=APIResponse, tags=["Terminals"])
async def connect_terminal(
    request: TerminalConnectRequest,
    bot=Depends(get_trading_bot),
    tm=Depends(get_terminal_manager)
):
    """Connect to specific MT5 terminal"""
    success = bot.connect_terminal(
        request.terminal_id,
        request.account,
        request.password,
        request.server
    )
    
    if success:
        terminal = tm.get_active_terminal()
        return APIResponse(
            success=True,
            message=f"Connected to {terminal['name']}",
            data=terminal
        )
    else:
        raise HTTPException(status_code=400, detail="Connection failed")


@app.get("/api/terminals/active", response_model=Optional[TerminalInfo], tags=["Terminals"])
async def get_active_terminal(tm=Depends(get_terminal_manager)):
    """Get currently active terminal"""
    terminal = tm.get_active_terminal()
    if terminal:
        return TerminalInfo(**terminal)
    raise HTTPException(status_code=404, detail="No active terminal")


# ===== SYMBOL MANAGEMENT =====

@app.get("/api/symbols/available", response_model=List[SymbolInfo], tags=["Symbols"])
async def get_available_symbols(tm=Depends(get_terminal_manager)):
    """Get all available symbols from active terminal"""
    symbols = tm.get_available_symbols()
    return [SymbolInfo(**s) for s in symbols]


@app.get("/api/symbols/search", response_model=List[SymbolInfo], tags=["Symbols"])
async def search_symbols(query: str, tm=Depends(get_terminal_manager)):
    """Search for symbols by name"""
    all_symbols = tm.get_available_symbols()
    filtered = [s for s in all_symbols if query.upper() in s['name'].upper()]
    return [SymbolInfo(**s) for s in filtered]


@app.post("/api/symbols/select", response_model=APIResponse, tags=["Symbols"])
async def select_symbol(request: SymbolSelectRequest, bot=Depends(get_trading_bot)):
    """Select trading symbol"""
    success = bot.set_symbol(request.symbol)
    
    if success:
        return APIResponse(
            success=True,
            message=f"Symbol changed to {request.symbol}",
            data={"symbol": request.symbol}
        )
    else:
        raise HTTPException(status_code=400, detail="Failed to select symbol")


@app.get("/api/symbols/current", response_model=dict, tags=["Symbols"])
async def get_current_symbol(bot=Depends(get_trading_bot)):
    """Get currently selected trading symbol"""
    return {"symbol": bot.current_symbol}


# ===== ACCOUNT =====

@app.get("/api/account/info", response_model=AccountInfo, tags=["Account"])
async def get_account_info(bot=Depends(get_trading_bot)):
    """Get account information"""
    account_info = bot.mt5.get_account_info()
    
    if account_info:
        return AccountInfo(**account_info)
    raise HTTPException(status_code=503, detail="Failed to get account info")


# ===== POSITIONS =====

@app.get("/api/positions/open", response_model=List[PositionInfo], tags=["Positions"])
async def get_open_positions(bot=Depends(get_trading_bot)):
    """Get all open positions"""
    if bot.executor is None:
        return []  # Return empty list if executor not initialized yet
    positions = bot.executor.get_open_positions()
    return [PositionInfo(**p) for p in positions]


@app.post("/api/positions/close", response_model=APIResponse, tags=["Positions"])
async def close_position(request: ClosePositionRequest, bot=Depends(get_trading_bot)):
    """Close specific position"""
    if bot.executor is None:
        raise HTTPException(status_code=503, detail="Trading system not fully initialized yet")
    
    result = bot.executor.close_position(request.ticket)
    
    if result['success']:
        return APIResponse(
            success=True,
            message=f"Position {request.ticket} closed",
            data=result
        )
    else:
        raise HTTPException(status_code=400, detail=result.get('error', 'Close failed'))


@app.post("/api/positions/modify", response_model=APIResponse, tags=["Positions"])
async def modify_position(request: ModifyPositionRequest, bot=Depends(get_trading_bot)):
    """Modify position TP/SL"""
    if bot.executor is None:
        raise HTTPException(status_code=503, detail="Trading system not fully initialized yet")
    
    result = bot.executor.modify_position(request.ticket, request.sl, request.tp)
    
    if result['success']:
        return APIResponse(
            success=True,
            message=f"Position {request.ticket} modified",
            data=result
        )
    else:
        raise HTTPException(status_code=400, detail=result.get('error', 'Modification failed'))


@app.post("/api/positions/close_all", response_model=APIResponse, tags=["Positions"])
async def close_all_positions(bot=Depends(get_trading_bot)):
    """Emergency: Close all open positions"""
    if bot.executor is None:
        raise HTTPException(status_code=503, detail="Trading system not fully initialized yet")
    
    result = bot.executor.close_all_positions()
    
    return APIResponse(
        success=result['success'],
        message=f"Closed {result['closed']} position(s)",
        data=result
    )


# ===== TRADES =====

@app.get("/api/trades/history", response_model=List[TradeInfo], tags=["Trades"])
async def get_trade_history(
    limit: int = 50,
    offset: int = 0,
    symbol: Optional[str] = None,
    db=Depends(get_db_manager)
):
    """Get trade history with pagination"""
    trades = db.get_trade_history(limit=limit, offset=offset, symbol=symbol)
    return [TradeInfo(**t.__dict__) for t in trades]


# ===== SIGNALS =====

@app.get("/api/signals/history", response_model=List[SignalInfo], tags=["Signals"])
async def get_signal_history(
    limit: int = 50,
    symbol: Optional[str] = None,
    db=Depends(get_db_manager)
):
    """Get signal history"""
    signals = db.get_signal_history(limit=limit, symbol=symbol)
    return [SignalInfo(**s.__dict__) for s in signals]


@app.get("/api/signals/latest", response_model=Optional[SignalInfo], tags=["Signals"])
async def get_latest_signal(db=Depends(get_db_manager)):
    """Get latest signal"""
    signals = db.get_signal_history(limit=1)
    if signals:
        return SignalInfo(**signals[0].__dict__)
    return None


# ===== METRICS =====

@app.get("/api/metrics/summary", response_model=MetricsSummary, tags=["Metrics"])
async def get_metrics_summary(db=Depends(get_db_manager)):
    """Get overall performance metrics"""
    # Get all closed trades
    trades = db.get_trade_history(limit=10000)
    
    if not trades:
        return MetricsSummary(
            total_trades=0, winning_trades=0, losing_trades=0,
            win_rate=0.0, profit_factor=0.0, net_profit=0.0,
            gross_profit=0.0, gross_loss=0.0, avg_win=0.0,
            avg_loss=0.0, max_drawdown=0.0, max_drawdown_pct=0.0
        )
    
    winning = [t for t in trades if t.profit > 0]
    losing = [t for t in trades if t.profit < 0]
    
    gross_profit = sum(t.profit for t in winning)
    gross_loss = abs(sum(t.profit for t in losing))
    net_profit = gross_profit - gross_loss
    
    return MetricsSummary(
        total_trades=len(trades),
        winning_trades=len(winning),
        losing_trades=len(losing),
        win_rate=(len(winning) / len(trades)) * 100 if trades else 0,
        profit_factor=gross_profit / gross_loss if gross_loss > 0 else 0,
        net_profit=net_profit,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        avg_win=gross_profit / len(winning) if winning else 0,
        avg_loss=gross_loss / len(losing) if losing else 0,
        max_drawdown=0.0,  # TODO: Calculate from equity curve
        max_drawdown_pct=0.0
    )


@app.get("/api/metrics/daily", response_model=DailyStats, tags=["Metrics"])
async def get_daily_metrics(bot=Depends(get_trading_bot)):
    """Get today's performance"""
    stats = bot.risk_mgr.get_daily_stats()
    return DailyStats(**stats)


@app.get("/api/metrics/equity_curve", response_model=List[EquityPoint], tags=["Metrics"])
async def get_equity_curve(days: int = 30, db=Depends(get_db_manager)):
    """Get equity curve data"""
    curve_data = db.get_equity_curve(days=days)
    return [EquityPoint(**point) for point in curve_data]


# ===== CONFIGURATION =====

@app.get("/api/config", response_model=dict, tags=["Config"])
async def get_config(bot=Depends(get_trading_bot)):
    """Get current configuration"""
    from utils.config import config
    
    return {
        "auto_trading": getattr(bot, 'running', False),
        "max_positions": bot.risk_mgr.max_positions if bot.risk_mgr else config.MAX_POSITIONS,
        "max_daily_loss": bot.risk_mgr.max_daily_loss if bot.risk_mgr else config.MAX_DAILY_LOSS,
        "min_confidence": bot.risk_mgr.min_confidence if bot.risk_mgr else config.MIN_CONFIDENCE,
        "lot_size": bot.executor.lot_size if bot.executor else config.DEFAULT_LOT_SIZE,
        "tp_pips": bot.executor.tp_pips if bot.executor else config.TP_PIPS,
        "sl_pips": bot.executor.sl_pips if bot.executor else config.SL_PIPS,
    }


@app.post("/api/config/update", response_model=APIResponse, tags=["Config"])
async def update_config(request: ConfigUpdateRequest, bot=Depends(get_trading_bot)):
    """Update configuration"""
    updated = []
    
    if request.max_positions is not None:
        if bot.risk_mgr:
            bot.risk_mgr.max_positions = request.max_positions
            updated.append("max_positions")
    
    if request.max_daily_loss is not None:
        if bot.risk_mgr:
            bot.risk_mgr.max_daily_loss = request.max_daily_loss
            updated.append("max_daily_loss")
    
    if request.min_confidence is not None:
        if bot.risk_mgr:
            bot.risk_mgr.min_confidence = request.min_confidence
            updated.append("min_confidence")
    
    if request.lot_size is not None:
        if bot.executor:
            bot.executor.lot_size = request.lot_size
            updated.append("lot_size")
    
    if not updated:
        return APIResponse(
            success=False,
            message="Cannot update config: MT5 not connected yet",
            data={}
        )
    
    return APIResponse(
        success=True,
        message=f"Updated: {', '.join(updated)}",
        data={"updated_fields": updated}
    )


# ===== ROOT =====

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "name": "Goldmine ML Live Trading API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


# Initialize function (called from main.py)
def init_api(bot, tm, db):
    """Initialize API with trading bot instances"""
    global trading_bot, terminal_manager, db_manager
    trading_bot = bot
    terminal_manager = tm
    db_manager = db
    logger.info("API initialized with trading bot instances")
