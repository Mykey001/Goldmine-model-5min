"""
Live Backtest Engine
Handles on-demand backtesting from frontend with data fetching, feature engineering, and signal generation
"""
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import ta
import joblib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Engine for running backtests with fresh data"""
    
    def __init__(self, model_path: str = None):
        """Initialize backtest engine
        
        Args:
            model_path: Path to trained model file
        """
        self.model_path = model_path or "models/final/xgboost_model.pkl"
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load the trained ML model"""
        try:
            model_file = Path(self.model_path)
            if model_file.exists():
                self.model = joblib.load(str(model_file))
                logger.info(f"Model loaded from {self.model_path}")
            else:
                logger.warning(f"Model file not found: {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            
    def fetch_data(
        self, 
        symbol: str, 
        timeframe: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """Fetch historical data from MT5
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe (M5, M3, M1, H1)
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Check if MT5 is initialized
            if not mt5.terminal_info():
                logger.error("MT5 not initialized. Please connect to MT5 terminal first.")
                return None
            
            # Ensure symbol is selected
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return None
            
            if not symbol_info.visible:
                logger.info(f"Enabling symbol {symbol} in Market Watch...")
                if not mt5.symbol_select(symbol, True):
                    logger.error(f"Failed to select symbol {symbol}")
                    return None
            
            # Map timeframe string to MT5 constant
            tf_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M3': mt5.TIMEFRAME_M3,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1,
            }
            
            tf = tf_map.get(timeframe)
            if tf is None:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
            
            logger.info(f"Fetching {timeframe} data for {symbol} from {start_date.date()} to {end_date.date()}...")
            logger.info(f"MT5 Terminal Info: {mt5.terminal_info()}")
            logger.info(f"Symbol Info: {mt5.symbol_info(symbol)}")
            
            # Try using copy_rates_from_pos which is more reliable
            # Calculate approximate number of bars needed
            delta_days = (end_date - start_date).days
            
            # Estimate bars based on timeframe
            tf_minutes = {
                mt5.TIMEFRAME_M1: 1, mt5.TIMEFRAME_M3: 3, mt5.TIMEFRAME_M5: 5,
                mt5.TIMEFRAME_M15: 15, mt5.TIMEFRAME_M30: 30, mt5.TIMEFRAME_H1: 60,
                mt5.TIMEFRAME_H4: 240, mt5.TIMEFRAME_D1: 1440
            }
            minutes = tf_minutes.get(tf, 5)
            estimated_bars = int((delta_days * 24 * 60) / minutes) + 100  # Add buffer
            
            logger.info(f"Estimated bars needed: {estimated_bars}")
            
            # First try: copy_rates_range (original method)
            rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
            
            # If that fails, try copy_rates_from_pos (from most recent backwards)
            if rates is None or len(rates) == 0:
                logger.warning("copy_rates_range failed, trying copy_rates_from_pos...")
                rates = mt5.copy_rates_from_pos(symbol, tf, 0, min(estimated_bars, 10000))
                
                # Filter to date range if we got data
                if rates is not None and len(rates) > 0:
                    df_temp = pd.DataFrame(rates)
                    df_temp['timestamp'] = pd.to_datetime(df_temp['time'], unit='s')
                    mask = (df_temp['timestamp'] >= start_date) & (df_temp['timestamp'] <= end_date)
                    filtered_indices = df_temp[mask].index.tolist()
                    
                    if len(filtered_indices) > 0:
                        rates = rates[filtered_indices]
                        logger.info(f"Filtered to {len(rates)} bars in date range")
                    else:
                        rates = None
                        logger.error("No data found in specified date range")
            
            logger.info(f"Fetch result: {len(rates) if rates is not None else 'None'} candles")
            
            if rates is None or len(rates) == 0:
                error_code = mt5.last_error()
                logger.error(f"No data returned for {symbol} {timeframe}. MT5 Error: {error_code}")
                logger.error(f"Date range: {start_date} to {end_date}")
                logger.error(f"Check that: 1) MT5 is connected, 2) Symbol is correct, 3) Broker has data for this period")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['timestamp'] = pd.to_datetime(df['time'], unit='s')
            df['timeframe'] = timeframe
            
            # Rename columns to match expected format
            df = df.rename(columns={
                'tick_volume': 'tickvol'
            })
            
            # Add volume columns for compatibility
            df['vol'] = df['tickvol']  # Real volume (same as tick for most brokers)
            df['spread'] = 0  # Spread in points (not available in historical data)
            
            # Select relevant columns
            df = df[['timestamp', 'timeframe', 'open', 'high', 'low', 'close', 'tickvol', 'vol', 'spread']]
            
            logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
            
    def calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators and features
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with features added
        """
        try:
            # Create a copy to avoid modifying original
            data = df.copy()
            
            # ===== RSI FEATURES (CORE STRATEGY) =====
            data['rsi'] = ta.momentum.RSIIndicator(data['close'], window=14).rsi()
            data['rsi_oversold'] = (data['rsi'] < 35).astype(int)
            data['rsi_overbought'] = (data['rsi'] > 65).astype(int)
            data['rsi_cross_above_35'] = ((data['rsi'] > 35) & (data['rsi'].shift(1) <= 35)).astype(int)
            data['rsi_cross_below_65'] = ((data['rsi'] < 65) & (data['rsi'].shift(1) >= 65)).astype(int)
            data['rsi_momentum'] = data['rsi'].diff()
            data['rsi_slope'] = data['rsi'].diff(3)
            
            # ===== PRICE ACTION FEATURES =====
            for period in [1, 3, 5, 10, 20]:
                data[f'momentum_{period}'] = data['close'].pct_change(period) * 100
            
            data['volatility_10'] = data['close'].rolling(10).std()
            data['volatility_20'] = data['close'].rolling(20).std()
            
            data['candle_body'] = abs(data['close'] - data['open'])
            data['candle_range'] = data['high'] - data['low']
            data['upper_wick'] = data['high'] - data[['open', 'close']].max(axis=1)
            data['lower_wick'] = data[['open', 'close']].min(axis=1) - data['low']
            data['body_ratio'] = data['candle_body'] / (data['candle_range'] + 0.0001)
            
            # ===== TREND INDICATORS =====
            data['ema_20'] = ta.trend.EMAIndicator(data['close'], window=20).ema_indicator()
            data['ema_50'] = ta.trend.EMAIndicator(data['close'], window=50).ema_indicator()
            data['price_above_ema20'] = (data['close'] > data['ema_20']).astype(int)
            data['price_above_ema50'] = (data['close'] > data['ema_50']).astype(int)
            data['ema_distance'] = (data['close'] - data['ema_20']) / data['close'] * 100
            
            macd = ta.trend.MACD(data['close'])
            data['macd'] = macd.macd()
            data['macd_signal'] = macd.macd_signal()
            data['macd_diff'] = macd.macd_diff()
            
            data['adx'] = ta.trend.ADXIndicator(data['high'], data['low'], data['close'], window=14).adx()
            
            # ===== VOLUME FEATURES =====
            # NOTE: The model was trained with tickvol, vol, spread as raw features
            # NOT with volume_ma, volume_ratio, volume_surge
            # So we skip creating derived volume features for backtest
            # The raw tickvol, vol, spread columns will be excluded from features anyway
            
            # ===== TEMPORAL FEATURES =====
            data['hour'] = data['timestamp'].dt.hour
            data['day_of_week'] = data['timestamp'].dt.dayofweek
            data['day_of_month'] = data['timestamp'].dt.day
            data['week_of_year'] = data['timestamp'].dt.isocalendar().week
            
            data['session_asian'] = ((data['hour'] >= 0) & (data['hour'] < 8)).astype(int)
            data['session_european'] = ((data['hour'] >= 8) & (data['hour'] < 13)).astype(int)
            data['session_us'] = ((data['hour'] >= 13) & (data['hour'] < 21)).astype(int)
            
            # Remove NaN rows
            data = data.dropna().reset_index(drop=True)
            
            logger.info(f"Features calculated: {len(data)} candles")
            return data
            
        except Exception as e:
            logger.error(f"Error calculating features: {e}")
            return df
            
    def calculate_h1_trend(self, df_h1: pd.DataFrame, ema_period: int = 200) -> pd.DataFrame:
        """Calculate H1 trend filter
        
        Args:
            df_h1: H1 timeframe data
            ema_period: EMA period for trend
            
        Returns:
            DataFrame with h1_trend column
        """
        try:
            data = df_h1.copy()
            data['h1_ema'] = ta.trend.EMAIndicator(data['close'], window=ema_period).ema_indicator()
            data['h1_trend'] = np.where(data['close'] > data['h1_ema'], 1, 0)
            
            # Keep only necessary columns
            trend_data = data[['timestamp', 'h1_trend', 'h1_ema', 'close']].copy()
            trend_data.rename(columns={'close': 'h1_close'}, inplace=True)
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error calculating H1 trend: {e}")
            return df_h1
            
    def generate_signals(
        self, 
        df: pd.DataFrame, 
        min_confidence: float = 0.5,
        h1_trend_data: Optional[pd.DataFrame] = None,
        config: Optional[Dict] = None
    ) -> pd.DataFrame:
        """Generate trading signals using ML model
        
        Args:
            df: DataFrame with features
            min_confidence: Minimum confidence threshold
            h1_trend_data: Optional H1 trend data for filtering
            
        Returns:
            DataFrame with signals and predictions
        """
        try:
            if self.model is None:
                logger.error("Model not loaded")
                return df
                
            data = df.copy()
            
            # Prepare feature columns (exclude non-feature columns)
            # The model expects tickvol, vol, spread AS features (they were included in training)
            exclude_cols = [
                'timestamp', 'timeframe', 'label', 'open', 'high', 'low', 'close', 
                'date', 'time', 'h1_trend', 'h1_ema', 'h1_close'
                # NOTE: tickvol, vol, spread are INCLUDED as features
            ]
            feature_cols = [c for c in data.columns if c not in exclude_cols]
            
            # Verify we have the expected features
            logger.info(f"Generating signals with {len(feature_cols)} features")
            logger.debug(f"Features: {feature_cols}")
            
            # Predict
            X = data[feature_cols]
            data['prediction'] = self.model.predict(X)
            data['confidence'] = np.max(self.model.predict_proba(X), axis=1)
            
            # Filter by confidence
            data['signal'] = data['prediction'].where(data['confidence'] >= min_confidence, -1)
            
            # Apply H1 trend filter if enabled
            if h1_trend_data is not None:
                data = data.sort_values('timestamp')
                h1_trend_data = h1_trend_data.sort_values('timestamp')
                
                # Merge H1 trend
                data = pd.merge_asof(
                    data,
                    h1_trend_data,
                    on='timestamp',
                    direction='backward'
                )
                
                # Filter signals
                signals_before = (data['signal'] != -1).sum()
                
                # Only BUY in uptrend, only SELL in downtrend
                buy_in_downtrend = (data['signal'] == 1) & (data['h1_trend'] == 0)
                sell_in_uptrend = (data['signal'] == 0) & (data['h1_trend'] == 1)
                
                data.loc[buy_in_downtrend, 'signal'] = -1
                data.loc[sell_in_uptrend, 'signal'] = -1
                
                signals_after = (data['signal'] != -1).sum()
                logger.info(f"H1 filter applied: {signals_before} -> {signals_after} signals")
            
            # Apply volatility filter if enabled (from config)
            use_volatility_filter = config.get('use_volatility_filter', False) if config else False
            if use_volatility_filter and 'adx' in data.columns:
                min_atr = config.get('min_atr', 0.5)
                max_atr = config.get('max_atr', 5.0)
                
                # Calculate ATR if not present
                if 'atr' not in data.columns:
                    from ta.volatility import AverageTrueRange
                    atr_indicator = AverageTrueRange(data['high'], data['low'], data['close'], window=14)
                    data['atr'] = atr_indicator.average_true_range()
                
                signals_before_vol = (data['signal'] != -1).sum()
                
                # Filter out signals where ATR is outside acceptable range
                low_volatility = data['atr'] < min_atr
                high_volatility = data['atr'] > max_atr
                
                data.loc[low_volatility, 'signal'] = -1
                data.loc[high_volatility, 'signal'] = -1
                
                signals_after_vol = (data['signal'] != -1).sum()
                filtered_vol = signals_before_vol - signals_after_vol
                logger.info(f"Volatility filter applied: {signals_before_vol} -> {signals_after_vol} signals ({filtered_vol} filtered)")
            
            logger.info(f"Signals generated: BUY={sum(data.signal==1)}, SELL={sum(data.signal==0)}, NO_TRADE={sum(data.signal==-1)}")
            return data
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}", exc_info=True)
            # Add signal column with all -1 (no trade) if generation failed
            data['signal'] = -1
            data['prediction'] = -1
            data['confidence'] = 0.0
            return data
            
    def run_backtest(
        self,
        data: pd.DataFrame,
        tp_pips: int = 100,
        sl_pips: int = 50,
        lot_size: float = 0.01,
        pip_value: float = 0.01,
        starting_capital: float = 10000
    ) -> Dict:
        """Run backtest simulation
        
        Args:
            data: DataFrame with signals
            tp_pips: Take profit in pips
            sl_pips: Stop loss in pips
            lot_size: Position size
            pip_value: Pip value
            starting_capital: Starting capital
            
        Returns:
            Dictionary with backtest results
        """
        try:
            # Validate data has required columns
            if 'signal' not in data.columns:
                logger.error("Data missing 'signal' column")
                return {'success': False, 'error': "No signals generated"}
            
            if len(data) == 0:
                logger.error("No data to backtest")
                return {'success': False, 'error': "Empty dataset"}
            dollars_per_pip = 10 * lot_size
            
            trades = []
            equity = starting_capital
            equity_curve = [{'timestamp': data.iloc[0]['timestamp'], 'equity': equity}]
            
            active_trade = None
            
            for idx in range(len(data)):
                row = data.iloc[idx]
                
                # Check if active trade hits TP or SL
                if active_trade is not None:
                    if active_trade['direction'] == 'BUY':
                        if row['high'] >= active_trade['tp']:
                            profit = tp_pips * dollars_per_pip
                            active_trade['exit_price'] = active_trade['tp']
                            active_trade['exit_time'] = row['timestamp']
                            active_trade['profit'] = profit
                            active_trade['exit_reason'] = 'TP'
                            trades.append(active_trade)
                            equity += profit
                            equity_curve.append({'timestamp': row['timestamp'], 'equity': equity})
                            active_trade = None
                            continue
                        elif row['low'] <= active_trade['sl']:
                            loss = -sl_pips * dollars_per_pip
                            active_trade['exit_price'] = active_trade['sl']
                            active_trade['exit_time'] = row['timestamp']
                            active_trade['profit'] = loss
                            active_trade['exit_reason'] = 'SL'
                            trades.append(active_trade)
                            equity += loss
                            equity_curve.append({'timestamp': row['timestamp'], 'equity': equity})
                            active_trade = None
                            continue
                            
                    elif active_trade['direction'] == 'SELL':
                        if row['low'] <= active_trade['tp']:
                            profit = tp_pips * dollars_per_pip
                            active_trade['exit_price'] = active_trade['tp']
                            active_trade['exit_time'] = row['timestamp']
                            active_trade['profit'] = profit
                            active_trade['exit_reason'] = 'TP'
                            trades.append(active_trade)
                            equity += profit
                            equity_curve.append({'timestamp': row['timestamp'], 'equity': equity})
                            active_trade = None
                            continue
                        elif row['high'] >= active_trade['sl']:
                            loss = -sl_pips * dollars_per_pip
                            active_trade['exit_price'] = active_trade['sl']
                            active_trade['exit_time'] = row['timestamp']
                            active_trade['profit'] = loss
                            active_trade['exit_reason'] = 'SL'
                            trades.append(active_trade)
                            equity += loss
                            equity_curve.append({'timestamp': row['timestamp'], 'equity': equity})
                            active_trade = None
                            continue
                
                # Open new trade
                if active_trade is None and row['signal'] in [0, 1]:
                    entry_price = row['close']
                    
                    if row['signal'] == 1:  # BUY
                        active_trade = {
                            'direction': 'BUY',
                            'entry_time': row['timestamp'],
                            'entry_price': entry_price,
                            'tp': entry_price + (tp_pips * pip_value),
                            'sl': entry_price - (sl_pips * pip_value),
                            'confidence': row['confidence']
                        }
                    elif row['signal'] == 0:  # SELL
                        active_trade = {
                            'direction': 'SELL',
                            'entry_time': row['timestamp'],
                            'entry_price': entry_price,
                            'tp': entry_price - (tp_pips * pip_value),
                            'sl': entry_price + (sl_pips * pip_value),
                            'confidence': row['confidence']
                        }
            
            # Convert trades to JSON-serializable format
            for trade in trades:
                for key, value in trade.items():
                    if hasattr(value, 'item'):  # numpy type
                        trade[key] = value.item()
                    elif hasattr(value, 'isoformat'):  # datetime
                        trade[key] = value.isoformat()
            
            # Convert equity curve to JSON-serializable format
            for point in equity_curve:
                if 'timestamp' in point and hasattr(point['timestamp'], 'isoformat'):
                    point['timestamp'] = point['timestamp'].isoformat()
                if 'equity' in point and hasattr(point['equity'], 'item'):
                    point['equity'] = float(point['equity'])
            
            # Calculate metrics
            trades_df = pd.DataFrame(trades)
            
            if len(trades_df) > 0:
                winning_trades = trades_df[trades_df['profit'] > 0]
                losing_trades = trades_df[trades_df['profit'] < 0]
                
                total_trades = len(trades_df)
                wins = len(winning_trades)
                losses = len(losing_trades)
                win_rate = wins / total_trades * 100 if total_trades > 0 else 0
                
                gross_profit = winning_trades['profit'].sum() if wins > 0 else 0
                gross_loss = abs(losing_trades['profit'].sum()) if losses > 0 else 0
                net_profit = gross_profit - gross_loss
                profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
                
                avg_win = winning_trades['profit'].mean() if wins > 0 else 0
                avg_loss = losing_trades['profit'].mean() if losses > 0 else 0
                
                # Drawdown
                equity_series = pd.Series([point['equity'] for point in equity_curve])
                rolling_max = equity_series.expanding().max()
                drawdown = equity_series - rolling_max
                max_drawdown = drawdown.min()
                max_drawdown_pct = (max_drawdown / rolling_max.max()) * 100 if rolling_max.max() > 0 else 0
                
                # Sharpe Ratio
                returns = equity_series.pct_change().dropna()
                sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
                
                return {
                    'success': True,
                    'trades': trades,
                    'equity_curve': equity_curve,
                    'metrics': {
                        'total_trades': int(total_trades),
                        'winning_trades': int(wins),
                        'losing_trades': int(losses),
                        'win_rate': float(win_rate),
                        'gross_profit': float(gross_profit),
                        'gross_loss': float(gross_loss),
                        'net_profit': float(net_profit),
                        'profit_factor': float(profit_factor),
                        'avg_win': float(avg_win),
                        'avg_loss': float(avg_loss),
                        'max_drawdown': float(max_drawdown),
                        'max_drawdown_pct': float(max_drawdown_pct),
                        'sharpe_ratio': float(sharpe),
                        'final_equity': float(equity),
                        'return_pct': float(((equity / starting_capital) - 1) * 100) if starting_capital > 0 else 0
                    }
                }
            else:
                return {
                    'success': True,
                    'trades': [],
                    'equity_curve': equity_curve,
                    'metrics': {
                        'total_trades': 0,
                        'winning_trades': 0,
                        'losing_trades': 0,
                        'win_rate': 0,
                        'gross_profit': 0,
                        'gross_loss': 0,
                        'net_profit': 0,
                        'profit_factor': 0,
                        'avg_win': 0,
                        'avg_loss': 0,
                        'max_drawdown': 0,
                        'max_drawdown_pct': 0,
                        'sharpe_ratio': 0,
                        'final_equity': starting_capital,
                        'return_pct': 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Error running backtest: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
            
    def full_backtest(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        config: Dict
    ) -> Dict:
        """Run full backtest pipeline: fetch -> features -> signals -> backtest
        
        Args:
            symbol: Trading symbol
            start_date: Start date
            end_date: End date
            config: Configuration dictionary
            
        Returns:
            Complete backtest results
        """
        try:
            # 1. Fetch M5 data
            logger.info(f"Fetching M5 data for {symbol}...")
            m5_data = self.fetch_data(symbol, 'M5', start_date, end_date)
            if m5_data is None or len(m5_data) == 0:
                return {'success': False, 'error': 'Failed to fetch M5 data'}
            
            # 2. Fetch H1 data if trend filter enabled
            h1_trend_data = None
            if config.get('use_h1_filter', False):
                logger.info(f"Fetching H1 data for trend filter...")
                h1_data = self.fetch_data(symbol, 'H1', start_date, end_date)
                if h1_data is not None and len(h1_data) > 0:
                    h1_trend_data = self.calculate_h1_trend(
                        h1_data, 
                        config.get('h1_ema_period', 200)
                    )
            
            # 3. Calculate features
            logger.info("Calculating features...")
            m5_data = self.calculate_features(m5_data)
            
            # 4. Generate signals
            logger.info("Generating signals...")
            m5_data = self.generate_signals(
                m5_data,
                config.get('min_confidence', 0.5),
                h1_trend_data,
                config  # Pass full config for volatility filter
            )
            
            # 5. Run backtest
            logger.info("Running backtest...")
            results = self.run_backtest(
                m5_data,
                tp_pips=config.get('tp_pips', 100),
                sl_pips=config.get('sl_pips', 50),
                lot_size=config.get('lot_size', 0.01),
                pip_value=config.get('pip_value', 0.01),
                starting_capital=config.get('starting_capital', 10000)
            )
            
            if not results.get('success', False):
                logger.error(f"Backtest failed: {results.get('error', 'Unknown error')}")
                return results
            
            # Add configuration to results
            results['config'] = config
            results['symbol'] = symbol
            results['start_date'] = start_date.isoformat()
            results['end_date'] = end_date.isoformat()
            results['total_candles'] = len(m5_data)
            
            logger.info(f"Backtest complete: {results.get('metrics', {}).get('total_trades', 0)} trades")
            return results
            
        except Exception as e:
            logger.error(f"Error in full backtest: {e}")
            return {'success': False, 'error': str(e)}
