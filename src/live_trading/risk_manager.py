"""
Risk Manager - Enforce risk limits and position sizing
"""
import logging
from typing import Tuple
from datetime import datetime, date
import os


class RiskManager:
    """Manage trading risk and enforce limits"""
    
    def __init__(self):
        """Initialize risk manager"""
        self.logger = logging.getLogger(__name__)
        
        # Load risk parameters from environment
        self.max_positions = int(os.getenv('MAX_POSITIONS', 1))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', 400))
        self.max_daily_profit = float(os.getenv('MAX_DAILY_PROFIT', 1000))  # Optional target
        self.min_confidence = float(os.getenv('MIN_CONFIDENCE', 0.5))
        self.default_lot_size = float(os.getenv('DEFAULT_LOT_SIZE', 0.01))
        
        # Daily tracking
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.current_date = date.today()
        
        self.logger.info("Risk Manager initialized")
        self.logger.info(f"Max positions: {self.max_positions}")
        self.logger.info(f"Max daily loss: ${self.max_daily_loss}")
        self.logger.info(f"Min confidence: {self.min_confidence}")
    
    def can_open_trade(self, confidence: float, open_positions_count: int) -> Tuple[bool, str]:
        """
        Check if a new trade can be opened
        
        Args:
            confidence: Model confidence score
            open_positions_count: Current number of open positions
        
        Returns:
            Tuple of (can_trade, reason)
        """
        # Check if new day - reset daily stats
        self._check_new_day()
        
        # Check confidence
        if confidence < self.min_confidence:
            return False, f"Low confidence: {confidence:.3f} < {self.min_confidence}"
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return False, f"Daily loss limit reached: ${self.daily_pnl:.2f} <= -${self.max_daily_loss}"
        
        # Check daily profit target (optional stop)
        if self.max_daily_profit > 0 and self.daily_pnl >= self.max_daily_profit:
            return False, f"Daily profit target reached: ${self.daily_pnl:.2f} >= ${self.max_daily_profit}"
        
        # Check max positions
        if open_positions_count >= self.max_positions:
            return False, f"Max positions reached: {open_positions_count} >= {self.max_positions}"
        
        return True, "OK"
    
    def update_daily_pnl(self, profit: float):
        """
        Update daily P&L tracking
        
        Args:
            profit: Trade profit/loss amount
        """
        self._check_new_day()
        
        self.daily_pnl += profit
        self.daily_trades += 1
        
        self.logger.info(f"Daily P&L updated: ${self.daily_pnl:.2f} ({self.daily_trades} trades)")
        
        # Warning if approaching limit
        if self.daily_pnl < -self.max_daily_loss * 0.8:
            self.logger.warning(f"⚠️ Approaching daily loss limit: ${self.daily_pnl:.2f}")
    
    def _check_new_day(self):
        """Check if it's a new trading day and reset stats"""
        today = date.today()
        
        if today != self.current_date:
            self.logger.info(f"New trading day - Resetting daily stats")
            self.logger.info(f"Previous day P&L: ${self.daily_pnl:.2f} ({self.daily_trades} trades)")
            
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.current_date = today
    
    def calculate_position_size(self, account_balance: float, risk_percent: float = 1.0) -> float:
        """
        Calculate position size based on account balance and risk
        
        Args:
            account_balance: Current account balance
            risk_percent: Risk percentage per trade (default: 1%)
        
        Returns:
            Lot size
        """
        # For now, use default lot size
        # TODO: Implement dynamic position sizing based on account balance
        return self.default_lot_size
    
    def get_daily_stats(self) -> dict:
        """
        Get current daily statistics
        
        Returns:
            Dictionary with daily stats
        """
        self._check_new_day()
        
        return {
            'date': self.current_date.isoformat(),
            'pnl': self.daily_pnl,
            'trades': self.daily_trades,
            'loss_limit': self.max_daily_loss,
            'profit_target': self.max_daily_profit,
            'remaining_loss_buffer': self.max_daily_loss + self.daily_pnl,
            'can_trade': self.daily_pnl > -self.max_daily_loss,
        }
    
    def reset_daily_stats(self):
        """Manually reset daily statistics"""
        self.logger.info("Manually resetting daily stats")
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.current_date = date.today()
    
    def emergency_check(self) -> Tuple[bool, str]:
        """
        Emergency risk check
        
        Returns:
            Tuple of (is_emergency, reason)
        """
        self._check_new_day()
        
        # Check if daily loss limit exceeded
        if self.daily_pnl <= -self.max_daily_loss:
            return True, f"Daily loss limit exceeded: ${self.daily_pnl:.2f}"
        
        # Check if approaching limit (90%)
        if self.daily_pnl <= -self.max_daily_loss * 0.9:
            return True, f"Approaching daily loss limit: ${self.daily_pnl:.2f}"
        
        return False, "No emergency"
    
    def validate_trade_parameters(self, symbol: str, lot_size: float, 
                                  tp_pips: float, sl_pips: float) -> Tuple[bool, str]:
        """
        Validate trade parameters
        
        Args:
            symbol: Trading symbol
            lot_size: Position size
            tp_pips: Take profit in pips
            sl_pips: Stop loss in pips
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check lot size
        if lot_size <= 0 or lot_size > 1.0:
            return False, f"Invalid lot size: {lot_size}"
        
        # Check TP/SL ratio
        if tp_pips <= 0 or sl_pips <= 0:
            return False, "TP and SL must be positive"
        
        risk_reward_ratio = tp_pips / sl_pips
        if risk_reward_ratio < 0.5:  # Minimum 1:2 risk-reward
            return False, f"Poor risk-reward ratio: {risk_reward_ratio:.2f}"
        
        return True, "Valid parameters"
