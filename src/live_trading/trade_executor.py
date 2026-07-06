"""
Trade Executor - Execute and manage trades on MT5
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
import MetaTrader5 as mt5
import os


class TradeExecutor:
    """Execute and manage MT5 trades"""
    
    # Symbol-specific pip size configuration
    # Note: For gold, 1 pip = 10 points on most platforms (50 pips = 500 points = $5.00)
    SYMBOL_PIP_SIZES = {
        # Gold (1 pip = 10 points = $0.10)
        'XAUUSD': 0.1,
        'XAUUSDm': 0.1,
        'GOLD': 0.1,
        
        # Silver
        'XAGUSD': 0.001,
        'XAGUSDm': 0.001,
        'SILVER': 0.001,
        
        # JPY pairs (2 decimal places)
        'USDJPY': 0.01,
        'EURJPY': 0.01,
        'GBPJPY': 0.01,
        'AUDJPY': 0.01,
        'NZDJPY': 0.01,
        'CADJPY': 0.01,
        'CHFJPY': 0.01,
        
        # Most forex pairs (4 decimal places)
        'EURUSD': 0.0001,
        'GBPUSD': 0.0001,
        'AUDUSD': 0.0001,
        'NZDUSD': 0.0001,
        'USDCAD': 0.0001,
        'USDCHF': 0.0001,
        'EURGBP': 0.0001,
        'EURAUD': 0.0001,
        'EURNZD': 0.0001,
        'EURCAD': 0.0001,
        'EURCHF': 0.0001,
        'GBPAUD': 0.0001,
        'GBPNZD': 0.0001,
        'GBPCAD': 0.0001,
        'GBPCHF': 0.0001,
        'AUDNZD': 0.0001,
        'AUDCAD': 0.0001,
        'AUDCHF': 0.0001,
        'NZDCAD': 0.0001,
        'NZDCHF': 0.0001,
        'CADCHF': 0.0001,
        
        # Indices (typically 1 point = 1 pip)
        'US30': 1.0,
        'US100': 1.0,
        'US500': 0.1,
        'GER40': 1.0,
        'UK100': 1.0,
        'JPN225': 1.0,
        
        # Crypto (varies)
        'BTCUSD': 1.0,
        'ETHUSD': 0.1,
    }
    
    def __init__(self, symbol: str = 'XAUUSDm'):
        """
        Initialize trade executor
        
        Args:
            symbol: Trading symbol
        """
        self.logger = logging.getLogger(__name__)
        self.symbol = symbol
        
        # Trading parameters from environment
        self.tp_pips = float(os.getenv('TP_PIPS', 100))
        self.sl_pips = float(os.getenv('SL_PIPS', 50))
        self.lot_size = float(os.getenv('DEFAULT_LOT_SIZE', 0.01))
        self.magic = 123456  # EA identifier
        self.deviation = 20  # Max slippage in pips
        
        # Auto-detect pip value based on symbol
        self.pip_value = self._detect_pip_value(symbol)
        
        self.logger.info(f"Trade executor initialized for {symbol}")
        self.logger.info(f"Pip value: {self.pip_value} | TP: {self.tp_pips} pips ({self.tp_pips * self.pip_value} points) | SL: {self.sl_pips} pips ({self.sl_pips * self.pip_value} points) | Lot: {self.lot_size}")
    
    def _detect_pip_value(self, symbol: str) -> float:
        """
        Auto-detect pip value based on symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Pip value for the symbol
        """
        # Clean symbol name (remove suffixes like 'm', '.raw', etc.)
        clean_symbol = symbol.upper()
        for suffix in ['M', '.RAW', '.', '_']:
            if suffix in clean_symbol:
                clean_symbol = clean_symbol.split(suffix)[0]
        
        # Check direct match first
        if symbol.upper() in self.SYMBOL_PIP_SIZES:
            pip_value = self.SYMBOL_PIP_SIZES[symbol.upper()]
            self.logger.info(f"Pip value detected for {symbol}: {pip_value}")
            return pip_value
        
        # Check cleaned symbol
        if clean_symbol in self.SYMBOL_PIP_SIZES:
            pip_value = self.SYMBOL_PIP_SIZES[clean_symbol]
            self.logger.info(f"Pip value detected for {symbol} (cleaned: {clean_symbol}): {pip_value}")
            return pip_value
        
        # Fallback rules based on symbol patterns
        if 'JPY' in clean_symbol or 'HUF' in clean_symbol:
            self.logger.warning(f"JPY/HUF pair detected for {symbol}, using pip value: 0.01")
            return 0.01
        elif 'XAU' in clean_symbol or 'GOLD' in clean_symbol:
            self.logger.warning(f"Gold symbol detected for {symbol}, using pip value: 0.1 (1 pip = 10 points)")
            return 0.1
        elif 'XAG' in clean_symbol or 'SILVER' in clean_symbol:
            self.logger.warning(f"Silver symbol detected for {symbol}, using pip value: 0.001")
            return 0.001
        elif 'BTC' in clean_symbol or 'ETH' in clean_symbol:
            self.logger.warning(f"Crypto symbol detected for {symbol}, using pip value: 1.0")
            return 1.0
        else:
            # Default to standard forex (4 decimal places)
            self.logger.warning(f"Unknown symbol {symbol}, defaulting to standard forex pip value: 0.0001")
            return 0.0001
    
    def set_symbol(self, symbol: str):
        """
        Change trading symbol
        
        Args:
            symbol: New symbol name
        """
        self.symbol = symbol
        self.pip_value = self._detect_pip_value(symbol)
        self.logger.info(f"Symbol changed to {symbol} | Pip value: {self.pip_value}")
    
    def open_position(self, signal: int, confidence: float) -> Dict:
        """
        Open a new position
        
        Args:
            signal: 1 for BUY, 0 for SELL
            confidence: Model confidence score
        
        Returns:
            Dictionary with trade result
        """
        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                return {
                    'success': False,
                    'error': f'Symbol {self.symbol} not found',
                    'symbol': self.symbol
                }
            
            # Ensure symbol is enabled
            if not symbol_info.visible:
                if not mt5.symbol_select(self.symbol, True):
                    return {
                        'success': False,
                        'error': f'Failed to enable symbol {self.symbol}',
                        'symbol': self.symbol
                    }
            
            # Get current price
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                return {
                    'success': False,
                    'error': 'Failed to get current price',
                    'symbol': self.symbol
                }
            
            # Determine order type and prices
            if signal == 1:  # BUY
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl = price - (self.sl_pips * self.pip_value)
                tp = price + (self.tp_pips * self.pip_value)
                direction = 'BUY'
            else:  # SELL
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl = price + (self.sl_pips * self.pip_value)
                tp = price - (self.tp_pips * self.pip_value)
                direction = 'SELL'
            
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": self.lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": self.deviation,
                "magic": self.magic,
                "comment": f"Goldmine ML (Conf: {confidence:.2f})",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            self.logger.info(f"Opening {direction} position on {self.symbol} at {price}")
            result = mt5.order_send(request)
            
            if result is None:
                return {
                    'success': False,
                    'error': 'Order send returned None',
                    'symbol': self.symbol
                }
            
            # Check result
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Order failed with code {result.retcode}: {result.comment}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'retcode': result.retcode,
                    'comment': result.comment,
                    'symbol': self.symbol
                }
            
            # Success
            self.logger.info(f"Position opened successfully - Ticket: {result.order}")
            return {
                'success': True,
                'ticket': result.order,
                'symbol': self.symbol,
                'direction': direction,
                'price': price,
                'sl': sl,
                'tp': tp,
                'volume': self.lot_size,
                'confidence': confidence,
                'time': datetime.now(),
            }
            
        except Exception as e:
            self.logger.error(f"Exception opening position: {e}")
            return {
                'success': False,
                'error': str(e),
                'symbol': self.symbol
            }
    
    def close_position(self, ticket: int) -> Dict:
        """
        Close a specific position
        
        Args:
            ticket: Position ticket number
        
        Returns:
            Dictionary with close result
        """
        try:
            # Get position
            positions = mt5.positions_get(ticket=ticket)
            if not positions or len(positions) == 0:
                return {
                    'success': False,
                    'error': f'Position {ticket} not found'
                }
            
            position = positions[0]
            
            # Determine closing order type (opposite of position)
            if position.type == mt5.ORDER_TYPE_BUY:
                close_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(position.symbol).bid
            else:
                close_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(position.symbol).ask
            
            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": close_type,
                "position": ticket,
                "price": price,
                "deviation": self.deviation,
                "magic": self.magic,
                "comment": "Close by system",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send close order
            self.logger.info(f"Closing position {ticket}")
            result = mt5.order_send(request)
            
            if result is None:
                return {
                    'success': False,
                    'error': 'Close order returned None'
                }
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Close failed with code {result.retcode}: {result.comment}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'retcode': result.retcode,
                }
            
            # Success
            self.logger.info(f"Position {ticket} closed successfully")
            return {
                'success': True,
                'ticket': ticket,
                'close_price': price,
                'profit': position.profit,
            }
            
        except Exception as e:
            self.logger.error(f"Exception closing position: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def modify_position(self, ticket: int, new_sl: float = None, 
                       new_tp: float = None) -> Dict:
        """
        Modify SL/TP of existing position
        
        Args:
            ticket: Position ticket number
            new_sl: New stop loss price (optional)
            new_tp: New take profit price (optional)
        
        Returns:
            Dictionary with modification result
        """
        try:
            # Get position
            positions = mt5.positions_get(ticket=ticket)
            if not positions or len(positions) == 0:
                return {
                    'success': False,
                    'error': f'Position {ticket} not found'
                }
            
            position = positions[0]
            
            # Use existing values if not provided
            sl = new_sl if new_sl is not None else position.sl
            tp = new_tp if new_tp is not None else position.tp
            
            # Prepare modification request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "sl": sl,
                "tp": tp,
                "position": ticket,
            }
            
            # Send modification
            self.logger.info(f"Modifying position {ticket} - SL: {sl}, TP: {tp}")
            result = mt5.order_send(request)
            
            if result is None:
                return {
                    'success': False,
                    'error': 'Modification returned None'
                }
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Modification failed with code {result.retcode}: {result.comment}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'retcode': result.retcode,
                }
            
            # Success
            self.logger.info(f"Position {ticket} modified successfully")
            return {
                'success': True,
                'ticket': ticket,
                'sl': sl,
                'tp': tp,
            }
            
        except Exception as e:
            self.logger.error(f"Exception modifying position: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_open_positions(self, symbol: str = None) -> List[Dict]:
        """
        Get all open positions
        
        Args:
            symbol: Optional symbol filter
        
        Returns:
            List of position dictionaries
        """
        try:
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get(symbol=self.symbol)
            
            if positions is None:
                return []
            
            position_list = []
            for pos in positions:
                position_list.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'direction': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'entry_price': pos.price_open,
                    'current_price': pos.price_current,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'time': datetime.fromtimestamp(pos.time),
                    'comment': pos.comment,
                })
            
            return position_list
            
        except Exception as e:
            self.logger.error(f"Exception getting positions: {e}")
            return []
    
    def close_all_positions(self) -> Dict:
        """
        Close all open positions (emergency)
        
        Returns:
            Dictionary with results
        """
        positions = self.get_open_positions()
        
        if not positions:
            return {
                'success': True,
                'closed': 0,
                'message': 'No open positions'
            }
        
        closed_count = 0
        failed_count = 0
        errors = []
        
        for position in positions:
            result = self.close_position(position['ticket'])
            if result['success']:
                closed_count += 1
            else:
                failed_count += 1
                errors.append(f"Ticket {position['ticket']}: {result.get('error', 'Unknown error')}")
        
        self.logger.warning(f"Emergency close: {closed_count} closed, {failed_count} failed")
        
        return {
            'success': failed_count == 0,
            'closed': closed_count,
            'failed': failed_count,
            'errors': errors,
        }
