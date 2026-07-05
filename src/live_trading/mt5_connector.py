"""
MT5 Connector - Basic MT5 operations and data retrieval
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List
import MetaTrader5 as mt5
import pandas as pd


class MT5Connector:
    """Handle basic MT5 operations"""
    
    def __init__(self):
        self.connected = False
        self.current_symbol = None
        self.logger = logging.getLogger(__name__)
    
    def initialize(self, terminal_path: str = None) -> bool:
        """
        Initialize MT5 connection
        
        Args:
            terminal_path: Optional path to specific MT5 terminal
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if terminal_path:
                if not mt5.initialize(terminal_path):
                    error = mt5.last_error()
                    self.logger.error(f"MT5 initialization failed: {error}")
                    return False
            else:
                if not mt5.initialize():
                    error = mt5.last_error()
                    self.logger.error(f"MT5 initialization failed: {error}")
                    return False
            
            self.connected = True
            self.logger.info("MT5 initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception during initialization: {e}")
            return False
    
    def login(self, account: int, password: str, server: str) -> bool:
        """
        Login to MT5 account
        
        Args:
            account: Account number
            password: Account password
            server: Broker server name
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            self.initialize()
        
        try:
            if not mt5.login(account, password=password, server=server):
                error = mt5.last_error()
                self.logger.error(f"Login failed: {error}")
                return False
            
            self.logger.info(f"Logged in successfully to account {account}")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception during login: {e}")
            return False
    
    def shutdown(self):
        """Shutdown MT5 connection"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.logger.info("MT5 connection closed")
    
    def check_connection(self) -> bool:
        """
        Check if MT5 is connected
        
        Returns:
            True if connected, False otherwise
        """
        try:
            terminal_info = mt5.terminal_info()
            return terminal_info is not None
        except:
            return False
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Get account information
        
        Returns:
            Dictionary with account info or None
        """
        try:
            account = mt5.account_info()
            if account is None:
                self.logger.error("Failed to get account info")
                return None
            
            return {
                'balance': account.balance,
                'equity': account.equity,
                'margin': account.margin,
                'free_margin': account.margin_free,
                'profit': account.profit,
                'account': account.login,
                'server': account.server,
                'company': account.company,
                'currency': account.currency,
                'leverage': account.leverage,
            }
            
        except Exception as e:
            self.logger.error(f"Exception getting account info: {e}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get symbol specifications
        
        Args:
            symbol: Symbol name (e.g., 'XAUUSDm')
        
        Returns:
            Dictionary with symbol info or None
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.logger.error(f"Symbol {symbol} not found")
                return None
            
            return {
                'name': symbol_info.name,
                'description': symbol_info.description,
                'point': symbol_info.point,
                'digits': symbol_info.digits,
                'spread': symbol_info.spread,
                'trade_mode': symbol_info.trade_mode,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step,
                'trade_contract_size': symbol_info.trade_contract_size,
                'visible': symbol_info.visible,
            }
            
        except Exception as e:
            self.logger.error(f"Exception getting symbol info: {e}")
            return None
    
    def enable_symbol(self, symbol: str) -> bool:
        """
        Enable symbol in Market Watch
        
        Args:
            symbol: Symbol name
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not mt5.symbol_select(symbol, True):
                self.logger.error(f"Failed to enable symbol {symbol}")
                return False
            
            self.logger.info(f"Symbol {symbol} enabled in Market Watch")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception enabling symbol: {e}")
            return False
    
    def get_latest_tick(self, symbol: str) -> Optional[Dict]:
        """
        Get latest tick data for symbol
        
        Args:
            symbol: Symbol name
        
        Returns:
            Dictionary with tick data or None
        """
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                self.logger.error(f"Failed to get tick for {symbol}")
                return None
            
            return {
                'time': datetime.fromtimestamp(tick.time),
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'volume': tick.volume,
            }
            
        except Exception as e:
            self.logger.error(f"Exception getting tick: {e}")
            return None
    
    def get_latest_rates(self, symbol: str, timeframe: int, count: int = 200) -> Optional[pd.DataFrame]:
        """
        Get latest OHLCV bars
        
        Args:
            symbol: Symbol name
            timeframe: MT5 timeframe constant (e.g., mt5.TIMEFRAME_M5)
            count: Number of bars to retrieve
        
        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                self.logger.error(f"Failed to get rates for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            
            # Convert time to datetime
            df['timestamp'] = pd.to_datetime(df['time'], unit='s')
            
            # Rename columns for consistency
            df = df.rename(columns={'tick_volume': 'volume'})
            
            self.logger.debug(f"Retrieved {len(df)} bars for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Exception getting rates: {e}")
            return None
    
    def get_rates_range(self, symbol: str, timeframe: int, 
                       date_from: datetime, date_to: datetime) -> Optional[pd.DataFrame]:
        """
        Get historical bars for date range
        
        Args:
            symbol: Symbol name
            timeframe: MT5 timeframe constant
            date_from: Start date
            date_to: End date
        
        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            rates = mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
            
            if rates is None or len(rates) == 0:
                self.logger.error(f"Failed to get rates range for {symbol}")
                return None
            
            df = pd.DataFrame(rates)
            df['timestamp'] = pd.to_datetime(df['time'], unit='s')
            df = df.rename(columns={'tick_volume': 'volume'})
            
            return df
            
        except Exception as e:
            self.logger.error(f"Exception getting rates range: {e}")
            return None
    
    def get_positions(self, symbol: str = None) -> List[Dict]:
        """
        Get open positions
        
        Args:
            symbol: Optional symbol filter
        
        Returns:
            List of position dictionaries
        """
        try:
            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()
            
            if positions is None:
                return []
            
            position_list = []
            for pos in positions:
                position_list.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
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
    
    def get_terminal_info(self) -> Optional[Dict]:
        """
        Get MT5 terminal information
        
        Returns:
            Dictionary with terminal info or None
        """
        try:
            terminal = mt5.terminal_info()
            if terminal is None:
                return None
            
            return {
                'connected': terminal.connected,
                'trade_allowed': terminal.trade_allowed,
                'company': terminal.company,
                'name': terminal.name,
                'language': terminal.language,
                'build': terminal.build,
                'path': terminal.path,
            }
            
        except Exception as e:
            self.logger.error(f"Exception getting terminal info: {e}")
            return None
