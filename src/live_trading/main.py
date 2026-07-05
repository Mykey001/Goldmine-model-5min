"""
Main Trading Bot - Orchestrates the entire live trading system
"""
import time
import asyncio
import logging
from datetime import datetime
from typing import Optional
import MetaTrader5 as mt5

from mt5_terminal_manager import MT5TerminalManager
from mt5_connector import MT5Connector
from signal_generator import SignalGenerator
from trade_executor import TradeExecutor
from risk_manager import RiskManager
from database.db_manager import DatabaseManager
from utils.logger import setup_logger
from utils.config import config


class LiveTradingBot:
    """Main live trading bot"""
    
    def __init__(self):
        """Initialize trading bot"""
        # Setup logging
        self.logger = setup_logger('goldmine_ml', config.LOG_FILE, config.LOG_LEVEL)
        self.logger.info("="*60)
        self.logger.info("GOLDMINE ML LIVE TRADING BOT")
        self.logger.info("="*60)
        
        # Initialize components
        self.terminal_manager = MT5TerminalManager()
        self.mt5 = MT5Connector()
        self.db = DatabaseManager(config.DATABASE_URL)
        self.risk_mgr = RiskManager()
        
        # These will be initialized after connection
        self.signal_gen: Optional[SignalGenerator] = None
        self.executor: Optional[TradeExecutor] = None
        
        # State
        self.running = False
        self.current_symbol = 'XAUUSDm'  # Default symbol
        self.last_bar_time = {}  # Per-symbol bar tracking
        self.start_time = time.time()
        
        # WebSocket manager (will be set by API)
        self.ws_manager = None
        
        self.logger.info("Trading bot initialized")
    
    def set_websocket_manager(self, ws_manager):
        """Set WebSocket manager for real-time updates"""
        self.ws_manager = ws_manager
        self.logger.info("WebSocket manager connected")
    
    def connect_terminal(self, terminal_id: str, account: int, 
                        password: str, server: str) -> bool:
        """
        Connect to specific MT5 terminal
        
        Args:
            terminal_id: Terminal identifier
            account: MT5 account number
            password: Account password
            server: Broker server name
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Connecting to terminal {terminal_id}...")
        
        success = self.terminal_manager.initialize_terminal(
            terminal_id, account, password, server
        )
        
        if success:
            # Initialize trading components
            try:
                self.signal_gen = SignalGenerator(config.MODEL_PATH)
                self.executor = TradeExecutor(symbol=self.current_symbol)
                self.logger.info("Trading components initialized")
                
                # Broadcast connection status via WebSocket
                if self.ws_manager:
                    asyncio.create_task(self.ws_manager.emit_connection_status({
                        'connected': True,
                        'account': account,
                        'server': server
                    }))
                
                return True
            except Exception as e:
                self.logger.error(f"Failed to initialize trading components: {e}")
                return False
        else:
            return False
    
    def set_symbol(self, symbol: str) -> bool:
        """
        Change trading symbol
        
        Args:
            symbol: New symbol name
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Changing symbol to {symbol}...")
        
        # Verify symbol exists
        symbol_info = self.mt5.get_symbol_info(symbol)
        if not symbol_info:
            self.logger.error(f"Symbol {symbol} not found")
            return False
        
        # Enable in Market Watch
        if not symbol_info['visible']:
            if not self.mt5.enable_symbol(symbol):
                return False
        
        # Update current symbol
        self.current_symbol = symbol
        
        # Reinitialize executor with new symbol
        if self.executor:
            self.executor.set_symbol(symbol)
        
        # Reset bar tracking for new symbol
        self.last_bar_time[symbol] = None
        
        self.logger.info(f"Symbol changed to {symbol}")
        return True
    
    def get_current_symbol(self) -> str:
        """Get currently active symbol"""
        return self.current_symbol
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("Starting trading bot...")
        
        # Validate configuration
        if not config.validate():
            self.logger.error("Configuration validation failed")
            return
        
        # Initialize database
        if not self.db.init_database():
            self.logger.error("Database initialization failed")
            return
        
        self.logger.info("Database initialized successfully")
        
        # Check if terminal is connected
        if not self.terminal_manager.get_active_terminal():
            self.logger.warning("No terminal connected. Waiting for connection via API...")
        
        self.running = True
        self.logger.info("Trading bot started - Ready to accept connections")
        
        # Start main loop
        try:
            self.run_loop()
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
            self.stop()
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}", exc_info=True)
            self.stop()
    
    def run_loop(self):
        """Main trading loop"""
        self.logger.info("Entering main trading loop...")
        
        while self.running:
            try:
                # Check if connected
                if not self.terminal_manager.get_active_terminal():
                    time.sleep(5)  # Wait for connection
                    continue
                
                # Initialize components if not done
                if self.signal_gen is None:
                    try:
                        self.signal_gen = SignalGenerator(config.MODEL_PATH)
                        self.executor = TradeExecutor(symbol=self.current_symbol)
                        self.logger.info("Trading components initialized in loop")
                    except Exception as e:
                        self.logger.error(f"Failed to initialize components: {e}")
                        time.sleep(10)
                        continue
                
                # Check for new M5 bar
                current_bar = self.get_latest_bar(self.current_symbol)
                
                if current_bar and self.is_new_bar(current_bar):
                    self.logger.info(f"New M5 bar detected: {current_bar['time']}")
                    self.process_new_bar(current_bar)
                
                # Monitor open positions
                self.monitor_positions()
                
                # Update account snapshot (every minute)
                if int(time.time()) % 60 == 0:
                    self.save_account_snapshot()
                
                # Sleep
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in main loop iteration: {e}")
                time.sleep(5)
    
    def get_latest_bar(self, symbol: str) -> Optional[dict]:
        """Get latest M5 bar for symbol"""
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
    
    def process_new_bar(self, current_bar: dict):
        """Process new bar and generate signal"""
        try:
            # Fetch historical bars for feature calculation (200 bars)
            bars = self.mt5.get_latest_rates(
                self.current_symbol,
                mt5.TIMEFRAME_M5,
                200
            )
            
            if bars is None or len(bars) < 50:
                self.logger.warning("Insufficient bars for signal generation")
                return
            
            # Generate signal
            signal, confidence = self.signal_gen.generate_signal(bars)
            signal_name = self.signal_gen.get_signal_name(signal)
            
            self.logger.info(f"Signal: {signal_name} | Confidence: {confidence:.3f}")
            
            # Save signal to database
            self.db.save_signal({
                'timestamp': datetime.now(),
                'symbol': self.current_symbol,
                'signal': signal_name,
                'confidence': confidence,
                'was_executed': False,
            })
            
            # Emit signal to frontend via WebSocket
            if self.ws_manager:
                asyncio.create_task(self.ws_manager.emit_new_signal({
                    'signal': signal_name,
                    'confidence': confidence,
                    'symbol': self.current_symbol,
                    'timestamp': datetime.now().isoformat()
                }))
            
            # Execute trade if valid signal
            if signal in [0, 1]:
                self.execute_signal(signal, confidence)
            
        except Exception as e:
            self.logger.error(f"Error processing new bar: {e}", exc_info=True)
    
    def execute_signal(self, signal: int, confidence: float):
        """Execute trade based on signal"""
        try:
            # Check risk limits
            open_positions = len(self.executor.get_open_positions())
            can_trade, reason = self.risk_mgr.can_open_trade(confidence, open_positions)
            
            if not can_trade:
                self.logger.warning(f"Trade blocked: {reason}")
                return
            
            # Open position
            result = self.executor.open_position(signal, confidence)
            
            if result['success']:
                self.logger.info(f"✅ Trade opened: Ticket {result['ticket']}")
                
                # Save to database
                self.db.save_trade({
                    'ticket': result['ticket'],
                    'symbol': result['symbol'],
                    'direction': result['direction'],
                    'entry_price': result['price'],
                    'tp_price': result['tp'],
                    'sl_price': result['sl'],
                    'lot_size': result['volume'],
                    'entry_time': result['time'],
                    'confidence': result['confidence'],
                    'status': 'OPEN'
                })
                
                # Emit to frontend
                if self.ws_manager:
                    asyncio.create_task(self.ws_manager.emit_trade_opened(result))
            else:
                self.logger.error(f"❌ Trade failed: {result.get('error', 'Unknown error')}")
                
                # Emit error to frontend
                if self.ws_manager:
                    asyncio.create_task(self.ws_manager.emit_error({
                        'message': 'Trade execution failed',
                        'detail': result.get('error')
                    }))
        
        except Exception as e:
            self.logger.error(f"Error executing signal: {e}", exc_info=True)
    
    def monitor_positions(self):
        """Monitor open positions for closes"""
        try:
            # Get positions from database (marked as OPEN)
            db_positions = self.db.get_open_trades(symbol=self.current_symbol)
            
            # Get actual positions from MT5
            mt5_positions = self.executor.get_open_positions()
            mt5_tickets = {p['ticket'] for p in mt5_positions}
            
            # Check for closed positions
            for db_position in db_positions:
                if db_position.ticket not in mt5_tickets:
                    # Position was closed
                    self.logger.info(f"Position {db_position.ticket} detected as closed")
                    
                    # Get close details from history
                    # TODO: Implement history retrieval
                    # For now, mark as closed in database
                    self.db.close_trade(db_position.ticket, {
                        'exit_price': 0,  # TODO: Get actual exit price
                        'exit_time': datetime.now(),
                        'exit_reason': 'DETECTED',
                        'profit': 0  # TODO: Calculate actual profit
                    })
                    
                    # Update daily P&L
                    # self.risk_mgr.update_daily_pnl(profit)
                    
                    # Emit to frontend
                    if self.ws_manager:
                        asyncio.create_task(self.ws_manager.emit_trade_closed({
                            'ticket': db_position.ticket,
                            'symbol': db_position.symbol
                        }))
        
        except Exception as e:
            self.logger.error(f"Error monitoring positions: {e}")
    
    def save_account_snapshot(self):
        """Save account snapshot to database"""
        try:
            account_info = self.mt5.get_account_info()
            if account_info:
                self.db.save_account_snapshot({
                    'balance': account_info['balance'],
                    'equity': account_info['equity'],
                    'margin': account_info['margin'],
                    'free_margin': account_info['free_margin'],
                    'profit': account_info['profit'],
                    'account_number': account_info['account'],
                    'timestamp': datetime.now()
                })
        except Exception as e:
            self.logger.error(f"Error saving account snapshot: {e}")
    
    def stop(self):
        """Stop the bot gracefully"""
        self.logger.info("Stopping trading bot...")
        self.running = False
        
        # Shutdown MT5
        self.terminal_manager.shutdown()
        
        self.logger.info("Trading bot stopped")


def main():
    """Main entry point"""
    bot = LiveTradingBot()
    bot.start()


if __name__ == "__main__":
    main()
