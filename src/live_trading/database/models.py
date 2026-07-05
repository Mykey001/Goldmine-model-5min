"""
SQLAlchemy models for live trading database
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Trade(Base):
    """Trade records table"""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket = Column(Integer, unique=True, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # BUY, SELL
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    tp_price = Column(Float)
    sl_price = Column(Float)
    lot_size = Column(Float, nullable=False)
    entry_time = Column(DateTime, nullable=False, index=True)
    exit_time = Column(DateTime)
    exit_reason = Column(String(20))  # TP, SL, MANUAL
    profit = Column(Float)
    confidence = Column(Float)
    status = Column(String(20), nullable=False, index=True)  # OPEN, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Trade(ticket={self.ticket}, symbol={self.symbol}, direction={self.direction}, status={self.status})>"


class Signal(Base):
    """ML signal records table"""
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal = Column(String(10), nullable=False)  # BUY, SELL, NO_TRADE
    confidence = Column(Float, nullable=False)
    was_executed = Column(Boolean, default=False)
    reason = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Signal(symbol={self.symbol}, signal={self.signal}, confidence={self.confidence:.2f})>"


class AccountSnapshot(Base):
    """Account balance snapshots table"""
    __tablename__ = 'account_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    balance = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    margin = Column(Float)
    free_margin = Column(Float)
    profit = Column(Float)
    account_number = Column(Integer)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AccountSnapshot(balance={self.balance:.2f}, equity={self.equity:.2f})>"


class DailySummary(Base):
    """Daily trading summary table"""
    __tablename__ = 'daily_summary'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    symbol = Column(String(20))
    trades_count = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    gross_profit = Column(Float, default=0.0)
    gross_loss = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DailySummary(date={self.date}, trades={self.trades_count}, profit={self.net_profit:.2f})>"
