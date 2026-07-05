"""
MT5 Terminal Manager - Discover and manage multiple MT5 terminals
"""
import os
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Optional
import MetaTrader5 as mt5


class MT5TerminalManager:
    """Manage multiple MT5 terminal installations"""
    
    def __init__(self):
        self.terminals: Dict[str, Dict] = {}
        self.active_terminal_id: Optional[str] = None
        self.logger = logging.getLogger(__name__)
    
    def discover_terminals(self) -> List[Dict]:
        """
        Discover all installed MT5 terminals on the system
        
        Returns:
            List of terminal configurations
        """
        self.logger.info("Discovering MT5 terminals...")
        terminals = []
        
        # Common MT5 installation paths on Windows
        search_paths = [
            r"C:\Program Files\MetaTrader 5",
            r"C:\Program Files (x86)\MetaTrader 5",
            os.path.expanduser(r"~\AppData\Roaming\MetaQuotes\Terminal"),
        ]
        
        # Additional: Check Program Files for broker-specific installations
        program_files = [r"C:\Program Files", r"C:\Program Files (x86)"]
        for pf_dir in program_files:
            if os.path.exists(pf_dir):
                for item in os.listdir(pf_dir):
                    if 'mt5' in item.lower() or 'metatrader' in item.lower():
                        search_paths.append(os.path.join(pf_dir, item))
        
        # Search for terminal64.exe
        for base_path in search_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    if 'terminal64.exe' in files:
                        terminal_path = os.path.join(root, 'terminal64.exe')
                        
                        terminal_info = {
                            'id': self._generate_terminal_id(terminal_path),
                            'path': terminal_path,
                            'name': self._get_terminal_name(terminal_path),
                            'broker': self._detect_broker(root),
                            'connected': False,
                        }
                        terminals.append(terminal_info)
                        self.logger.info(f"Found terminal: {terminal_info['name']} at {terminal_path}")
        
        # Store discovered terminals
        self.terminals = {t['id']: t for t in terminals}
        
        self.logger.info(f"Discovered {len(terminals)} terminal(s)")
        return terminals
    
    def _generate_terminal_id(self, path: str) -> str:
        """Generate unique ID for terminal based on path"""
        return hashlib.md5(path.encode()).hexdigest()[:8]
    
    def _get_terminal_name(self, path: str) -> str:
        """Extract terminal name from path"""
        parent_dir = Path(path).parent.name
        
        # Try to get a friendly name
        if 'MetaTrader' in parent_dir:
            return parent_dir
        
        # Otherwise use grandparent directory name
        grandparent = Path(path).parent.parent.name
        return grandparent if grandparent != 'Terminal' else 'MT5 Terminal'
    
    def _detect_broker(self, terminal_root: str) -> str:
        """Try to detect broker from directory structure"""
        # Check parent directories for broker names
        path_parts = Path(terminal_root).parts
        
        # Common broker patterns
        for part in reversed(path_parts):
            if part.lower() not in ['program files', 'program files (x86)', 'metatrader 5', 'terminal']:
                if 'mt5' not in part.lower() and 'metatrader' not in part.lower():
                    return part
        
        return "Unknown Broker"
    
    def initialize_terminal(self, terminal_id: str, account: int, 
                          password: str, server: str) -> bool:
        """
        Initialize and connect to specific MT5 terminal
        
        Args:
            terminal_id: Terminal identifier
            account: MT5 account number
            password: Account password
            server: Broker server name
        
        Returns:
            True if successful, False otherwise
        """
        if terminal_id not in self.terminals:
            self.logger.error(f"Terminal {terminal_id} not found")
            return False
        
        terminal = self.terminals[terminal_id]
        
        try:
            # Shutdown current connection if exists
            if self.active_terminal_id:
                self.logger.info("Shutting down current terminal connection...")
                mt5.shutdown()
            
            # Initialize with specific terminal path
            self.logger.info(f"Initializing terminal: {terminal['name']}")
            if not mt5.initialize(terminal['path']):
                error = mt5.last_error()
                self.logger.error(f"Failed to initialize terminal: {error}")
                return False
            
            # Login to account
            self.logger.info(f"Logging in to account {account} on server {server}")
            if not mt5.login(account, password=password, server=server):
                error = mt5.last_error()
                self.logger.error(f"Login failed: {error}")
                mt5.shutdown()
                return False
            
            # Update terminal info
            self.active_terminal_id = terminal_id
            self.terminals[terminal_id]['connected'] = True
            self.terminals[terminal_id]['account'] = account
            self.terminals[terminal_id]['server'] = server
            
            # Get account info
            account_info = mt5.account_info()
            if account_info:
                self.terminals[terminal_id]['company'] = account_info.company
            
            self.logger.info(f"Successfully connected to {terminal['name']} - Account: {account}")
            return True
            
        except Exception as e:
            self.logger.error(f"Exception during terminal initialization: {e}")
            return False
    
    def get_active_terminal(self) -> Optional[Dict]:
        """Get currently active terminal information"""
        if self.active_terminal_id and self.active_terminal_id in self.terminals:
            return self.terminals[self.active_terminal_id]
        return None
    
    def get_available_symbols(self) -> List[Dict]:
        """
        Get all available symbols from active terminal
        
        Returns:
            List of symbol dictionaries
        """
        if not self.active_terminal_id:
            self.logger.warning("No active terminal")
            return []
        
        try:
            symbols = mt5.symbols_get()
            if symbols is None:
                self.logger.error("Failed to get symbols")
                return []
            
            symbol_list = []
            for symbol in symbols:
                symbol_list.append({
                    'name': symbol.name,
                    'description': symbol.description,
                    'path': symbol.path,
                    'digits': symbol.digits,
                    'trade_mode': symbol.trade_mode,
                    'point': symbol.point,
                    'min_volume': symbol.volume_min,
                    'max_volume': symbol.volume_max,
                })
            
            self.logger.info(f"Retrieved {len(symbol_list)} symbols")
            return symbol_list
            
        except Exception as e:
            self.logger.error(f"Exception getting symbols: {e}")
            return []
    
    def switch_terminal(self, terminal_id: str, account: int,
                       password: str, server: str) -> bool:
        """
        Switch to different terminal
        
        Args:
            terminal_id: Target terminal identifier
            account: MT5 account number
            password: Account password
            server: Broker server name
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info(f"Switching to terminal: {terminal_id}")
        return self.initialize_terminal(terminal_id, account, password, server)
    
    def shutdown(self):
        """Shutdown current MT5 connection"""
        if self.active_terminal_id:
            self.logger.info("Shutting down MT5 connection")
            mt5.shutdown()
            
            # Update connection status
            if self.active_terminal_id in self.terminals:
                self.terminals[self.active_terminal_id]['connected'] = False
            
            self.active_terminal_id = None
