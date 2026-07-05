"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ===== REQUEST MODELS =====

class TerminalConnectRequest(BaseModel):
    """Request to connect to MT5 terminal"""
    terminal_id: str = Field(..., description="Terminal identifier")
    account: int = Field(..., description="MT5 account number")
    password: str = Field(..., description="Account password")
    server: str = Field(..., description="Broker server name")


class SymbolSelectRequest(BaseModel):
    """Request to select trading symbol"""
    symbol: str = Field(..., description="Symbol name (e.g., XAUUSDm)")


class ClosePositionRequest(BaseModel):
    """Request to close position"""
    ticket: int = Field(..., description="Position ticket number")


class ModifyPositionRequest(BaseModel):
    """Request to modify position"""
    ticket: int = Field(..., description="Position ticket number")
    sl: Optional[float] = Field(None, description="New stop loss price")
    tp: Optional[float] = Field(None, description="New take profit price")


class ConfigUpdateRequest(BaseModel):
    """Request to update configuration"""
    auto_trading: Optional[bool] = Field(None, description="Enable/disable auto trading")
    max_positions: Optional[int] = Field(None, description="Maximum concurrent positions")
    max_daily_loss: Optional[float] = Field(None, description="Maximum daily loss in USD")
    min_confidence: Optional[float] = Field(None, description="Minimum signal confidence")
    lot_size: Optional[float] = Field(None, description="Default lot size")


# ===== RESPONSE MODELS =====

class TerminalInfo(BaseModel):
    """MT5 Terminal information"""
    id: str
    name: str
    path: str
    broker: str
    connected: bool
    account: Optional[int] = None
    server: Optional[str] = None


class SymbolInfo(BaseModel):
    """Symbol information"""
    name: str
    description: str
    path: Optional[str] = None
    digits: int
    point: float
    min_volume: float
    max_volume: float


class AccountInfo(BaseModel):
    """Account information"""
    balance: float
    equity: float
    margin: float
    free_margin: float
    profit: float
    account: int
    server: str
    company: str
    currency: Optional[str] = None
    leverage: Optional[int] = None


class PositionInfo(BaseModel):
    """Open position information"""
    ticket: int
    symbol: str
    direction: str  # BUY or SELL
    volume: float
    entry_price: float
    current_price: float
    sl: float
    tp: float
    profit: float
    time: datetime
    comment: Optional[str] = None


class TradeInfo(BaseModel):
    """Closed trade information"""
    ticket: int
    symbol: str
    direction: str
    entry_price: float
    exit_price: float
    tp_price: float
    sl_price: float
    lot_size: float
    entry_time: datetime
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    profit: Optional[float] = None
    confidence: float


class SignalInfo(BaseModel):
    """Signal information"""
    timestamp: datetime
    symbol: str
    signal: str  # BUY, SELL, NO_TRADE
    confidence: float
    was_executed: bool
    reason: Optional[str] = None


class MetricsSummary(BaseModel):
    """Trading metrics summary"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    net_profit: float
    gross_profit: float
    gross_loss: float
    avg_win: float
    avg_loss: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: float
    max_drawdown_pct: float


class DailyStats(BaseModel):
    """Daily statistics"""
    date: str
    pnl: float
    trades: int
    loss_limit: float
    profit_target: float
    remaining_loss_buffer: float
    can_trade: bool


class EquityPoint(BaseModel):
    """Equity curve data point"""
    timestamp: datetime
    equity: float


class ConnectionStatus(BaseModel):
    """Connection status"""
    connected: bool
    terminal: Optional[TerminalInfo] = None
    account: Optional[int] = None
    symbol: Optional[str] = None


class HealthStatus(BaseModel):
    """System health status"""
    status: str  # healthy, degraded, down
    mt5_connected: bool
    database_connected: bool
    model_loaded: bool
    uptime_seconds: float
    last_signal_time: Optional[datetime] = None
    open_positions: int


class APIResponse(BaseModel):
    """Generic API response"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
