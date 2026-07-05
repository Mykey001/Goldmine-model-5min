"""
Database manager for PostgreSQL operations
"""
import os
import logging
from datetime import datetime, date
from typing import List, Optional, Dict
from sqlalchemy import create_engine, desc, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, Trade, Signal, AccountSnapshot, DailySummary


class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize database connection
        
        Args:
            database_url: PostgreSQL connection string
        """
        self.logger = logging.getLogger(__name__)
        
        # Get database URL from env or parameter
        self.database_url = database_url or os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL not provided")
        
        # Create engine
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,  # Test connections before using
            pool_size=5,
            max_overflow=10
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        self.logger.info("Database manager initialized")
    
    def init_database(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(self.engine)
            self.logger.info("Database tables created successfully")
            return True
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to create tables: {e}")
            return False
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    # ===== TRADE OPERATIONS =====
    
    def save_trade(self, trade_data: Dict) -> Optional[Trade]:
        """
        Save or update trade record
        
        Args:
            trade_data: Dictionary with trade information
        
        Returns:
            Trade object if successful, None otherwise
        """
        session = self.get_session()
        try:
            # Check if trade exists
            existing_trade = session.query(Trade).filter_by(
                ticket=trade_data['ticket']
            ).first()
            
            if existing_trade:
                # Update existing trade
                for key, value in trade_data.items():
                    setattr(existing_trade, key, value)
                trade = existing_trade
            else:
                # Create new trade
                trade = Trade(**trade_data)
                session.add(trade)
            
            session.commit()
            session.refresh(trade)
            self.logger.info(f"Trade saved: {trade.ticket}")
            return trade
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Failed to save trade: {e}")
            return None
        finally:
            session.close()
    
    def get_open_trades(self, symbol: str = None) -> List[Trade]:
        """Get all open trades"""
        session = self.get_session()
        try:
            query = session.query(Trade).filter(Trade.status == 'OPEN')
            
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            
            trades = query.order_by(desc(Trade.entry_time)).all()
            return trades
            
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get open trades: {e}")
            return []
        finally:
            session.close()
    
    def get_trade_history(self, limit: int = 100, offset: int = 0, 
                         symbol: str = None) -> List[Trade]:
        """Get closed trades with pagination"""
        session = self.get_session()
        try:
            query = session.query(Trade).filter(Trade.status == 'CLOSED')
            
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            
            trades = query.order_by(desc(Trade.exit_time)).limit(limit).offset(offset).all()
            return trades
            
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get trade history: {e}")
            return []
        finally:
            session.close()
    
    def close_trade(self, ticket: int, exit_data: Dict) -> bool:
        """
        Close a trade
        
        Args:
            ticket: Trade ticket number
            exit_data: Dictionary with exit information
        """
        session = self.get_session()
        try:
            trade = session.query(Trade).filter_by(ticket=ticket).first()
            
            if not trade:
                self.logger.error(f"Trade {ticket} not found")
                return False
            
            # Update trade with exit data
            trade.exit_price = exit_data.get('exit_price')
            trade.exit_time = exit_data.get('exit_time', datetime.utcnow())
            trade.exit_reason = exit_data.get('exit_reason')
            trade.profit = exit_data.get('profit')
            trade.status = 'CLOSED'
            
            session.commit()
            self.logger.info(f"Trade {ticket} closed with profit: {trade.profit}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Failed to close trade: {e}")
            return False
        finally:
            session.close()
    
    # ===== SIGNAL OPERATIONS =====
    
    def save_signal(self, signal_data: Dict) -> Optional[Signal]:
        """Save signal record"""
        session = self.get_session()
        try:
            signal = Signal(**signal_data)
            session.add(signal)
            session.commit()
            session.refresh(signal)
            return signal
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Failed to save signal: {e}")
            return None
        finally:
            session.close()
    
    def get_signal_history(self, limit: int = 50, symbol: str = None) -> List[Signal]:
        """Get recent signals"""
        session = self.get_session()
        try:
            query = session.query(Signal)
            
            if symbol:
                query = query.filter(Signal.symbol == symbol)
            
            signals = query.order_by(desc(Signal.timestamp)).limit(limit).all()
            return signals
            
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get signal history: {e}")
            return []
        finally:
            session.close()
    
    # ===== ACCOUNT SNAPSHOT OPERATIONS =====
    
    def save_account_snapshot(self, snapshot_data: Dict) -> Optional[AccountSnapshot]:
        """Save account snapshot"""
        session = self.get_session()
        try:
            snapshot = AccountSnapshot(**snapshot_data)
            session.add(snapshot)
            session.commit()
            session.refresh(snapshot)
            return snapshot
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Failed to save snapshot: {e}")
            return None
        finally:
            session.close()
    
    def get_equity_curve(self, days: int = 30) -> List[Dict]:
        """Get equity curve data"""
        session = self.get_session()
        try:
            snapshots = session.query(AccountSnapshot).order_by(
                AccountSnapshot.timestamp
            ).limit(days * 288).all()  # 288 = 5-minute intervals per day
            
            return [
                {'timestamp': s.timestamp, 'equity': s.equity}
                for s in snapshots
            ]
            
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get equity curve: {e}")
            return []
        finally:
            session.close()
    
    # ===== DAILY SUMMARY OPERATIONS =====
    
    def calculate_daily_summary(self, target_date: date = None) -> Optional[DailySummary]:
        """Calculate and save daily summary"""
        if target_date is None:
            target_date = date.today()
        
        session = self.get_session()
        try:
            # Get all closed trades for the day
            trades = session.query(Trade).filter(
                and_(
                    Trade.status == 'CLOSED',
                    Trade.exit_time >= datetime.combine(target_date, datetime.min.time()),
                    Trade.exit_time < datetime.combine(target_date, datetime.max.time())
                )
            ).all()
            
            if not trades:
                return None
            
            # Calculate metrics
            winning_trades = [t for t in trades if t.profit > 0]
            losing_trades = [t for t in trades if t.profit < 0]
            
            gross_profit = sum(t.profit for t in winning_trades)
            gross_loss = abs(sum(t.profit for t in losing_trades))
            net_profit = gross_profit - gross_loss
            win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            # Get or create summary
            summary = session.query(DailySummary).filter_by(date=target_date).first()
            
            if summary:
                # Update existing
                summary.trades_count = len(trades)
                summary.winning_trades = len(winning_trades)
                summary.losing_trades = len(losing_trades)
                summary.gross_profit = gross_profit
                summary.gross_loss = gross_loss
                summary.net_profit = net_profit
                summary.win_rate = win_rate
                summary.profit_factor = profit_factor
                summary.updated_at = datetime.utcnow()
            else:
                # Create new
                summary = DailySummary(
                    date=target_date,
                    trades_count=len(trades),
                    winning_trades=len(winning_trades),
                    losing_trades=len(losing_trades),
                    gross_profit=gross_profit,
                    gross_loss=gross_loss,
                    net_profit=net_profit,
                    win_rate=win_rate,
                    profit_factor=profit_factor
                )
                session.add(summary)
            
            session.commit()
            session.refresh(summary)
            return summary
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Failed to calculate daily summary: {e}")
            return None
        finally:
            session.close()
