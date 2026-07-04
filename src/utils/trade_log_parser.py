"""
MT5 Trade Log Parser for Goldmine Strategy
Extracts trade execution data from EA logs
"""

import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Optional


class GoldmineLogParser:
    """Parse Goldmine EA trade logs to extract signals and trades"""
    
    def __init__(self):
        self.trades = []
        self.current_trade = None
        
    def parse_log_file(self, log_text: str) -> pd.DataFrame:
        """
        Parse log text and extract trade information
        
        Parameters:
        -----------
        log_text : str
            Raw log text from MT5
            
        Returns:
        --------
        pd.DataFrame : Parsed trades
        """
        lines = log_text.strip().split('\n')
        
        for line in lines:
            self._process_line(line)
        
        # Convert to dataframe
        if self.trades:
            df = pd.DataFrame(self.trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame()
    
    def _process_line(self, line: str):
        """Process a single log line"""
        
        # Extract timestamp and message
        parts = line.split('\t')
        if len(parts) < 3:
            return
        
        log_timestamp = parts[0]  # System time
        candle_timestamp = parts[1]  # Market time
        message = parts[2]
        
        # Parse RSI signal detection
        if "RSI BUY Signal" in message or "RSI SELL Signal" in message:
            self._parse_rsi_signal(candle_timestamp, message)
        
        # Parse trade opening
        elif "=== REVERSE TRADE GROUP" in message:
            self._parse_trade_open(candle_timestamp, message)
        
        # Parse trade closing
        elif "=== PROFIT TARGET REACHED ===" in message:
            self._parse_profit_target(candle_timestamp, message)
        
        elif "market buy" in message and "close #" in message:
            self._parse_trade_close(candle_timestamp, message)
    
    def _parse_rsi_signal(self, timestamp: str, message: str):
        """Parse RSI signal detection"""
        if self.current_trade is None:
            self.current_trade = {
                'signal_timestamp': timestamp,
                'signal_type': None,
                'rsi_prev': None,
                'rsi_curr': None,
                'reverse_direction': None
            }
        
        # Extract signal type
        if "RSI BUY Signal" in message:
            self.current_trade['signal_type'] = 'BUY'
        elif "RSI SELL Signal" in message:
            self.current_trade['signal_type'] = 'SELL'
        
        # Extract RSI values
        rsi_match = re.search(r'Prev:\s*([\d.]+)\s*→\s*Curr:\s*([\d.]+)', message)
        if rsi_match:
            self.current_trade['rsi_prev'] = float(rsi_match.group(1))
            self.current_trade['rsi_curr'] = float(rsi_match.group(2))
    
    def _parse_trade_open(self, timestamp: str, message: str):
        """Parse trade opening"""
        if self.current_trade is not None:
            self.current_trade['entry_timestamp'] = timestamp
    
    def _parse_profit_target(self, timestamp: str, message: str):
        """Parse profit target reached"""
        if self.current_trade is not None:
            self.current_trade['exit_timestamp'] = timestamp
            
            # Extract profit amount
            profit_match = re.search(r'Current:\s*\$?([\d.]+)', message)
            if profit_match:
                self.current_trade['profit_usd'] = float(profit_match.group(1))
    
    def _parse_trade_close(self, timestamp: str, message: str):
        """Parse individual position close"""
        if self.current_trade is not None:
            # Extract exit price
            price_match = re.search(r'at\s*([\d.]+)', message)
            if price_match and 'exit_price' not in self.current_trade:
                self.current_trade['exit_price'] = float(price_match.group(1))
                
                # Mark trade as complete
                if 'entry_timestamp' in self.current_trade:
                    # Calculate duration
                    try:
                        entry_dt = pd.to_datetime(self.current_trade['entry_timestamp'])
                        exit_dt = pd.to_datetime(self.current_trade['exit_timestamp'])
                        duration = (exit_dt - entry_dt).total_seconds()
                        self.current_trade['duration_seconds'] = duration
                        self.current_trade['duration_minutes'] = duration / 60
                    except:
                        pass
                    
                    # Save completed trade
                    self.trades.append(self.current_trade.copy())
                    self.current_trade = None


def parse_log_string(log_text: str) -> pd.DataFrame:
