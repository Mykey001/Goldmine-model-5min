// API Response Types
export interface AccountInfo {
  balance: number;
  equity: number;
  margin: number;
  free_margin: number;
  profit: number;
  account: number;
  server: string;
  company: string;
}

export interface Terminal {
  id: string;
  name: string;
  path: string;
  broker: string;
  is_active: boolean;
}

export interface Symbol {
  name: string;
  description: string;
  digits: number;
  point: number;
  min_volume: number;
  max_volume: number;
  volume_step: number;
}

export interface Position {
  ticket: number;
  symbol: string;
  direction: 'BUY' | 'SELL';
  entry_price: number;
  current_price: number;
  tp: number;
  sl: number;
  profit: number;
  volume: number;
  open_time: string;
}

export interface Trade {
  id: number;
  ticket: number;
  symbol: string;
  direction: 'BUY' | 'SELL';
  entry_price: number;
  exit_price: number;
  tp: number;
  sl: number;
  profit: number;
  volume: number;
  entry_time: string;
  exit_time: string;
  duration_minutes: number;
}

export interface Signal {
  id: number;
  timestamp: string;
  symbol: string;
  direction: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  entry_price: number;
  tp: number;
  sl: number;
  executed: boolean;
}

export interface MetricsSummary {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  profit_factor: number;
  net_profit: number;
  gross_profit: number;
  gross_loss: number;
  avg_win: number;
  avg_loss: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  sharpe_ratio: number;
}

export interface DailyMetrics {
  date: string;
  trades_count: number;
  winning_trades: number;
  losing_trades: number;
  net_profit: number;
  win_rate: number;
}

export interface EquityPoint {
  timestamp: string;
  equity: number;
  balance: number;
}

export interface ConnectionStatus {
  connected: boolean;
  terminal: Terminal | null;
  account: number | null;
}

export interface Config {
  max_daily_loss: number;
  max_positions: number;
  min_confidence: number;
  default_lot_size: number;
  tp_pips: number;
  sl_pips: number;
}

// WebSocket Event Types
export interface WSTradeOpened {
  ticket: number;
  symbol: string;
  direction: 'BUY' | 'SELL';
  entry_price: number;
  tp: number;
  sl: number;
  volume: number;
  timestamp: string;
}

export interface WSTradeClosed {
  ticket: number;
  profit: number;
  exit_price: number;
  timestamp: string;
}

export interface WSNewSignal {
  symbol: string;
  direction: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  entry_price: number;
  timestamp: string;
}

export interface WSAccountUpdate {
  balance: number;
  equity: number;
  profit: number;
}

export interface WSMetricsUpdate {
  daily_pnl: number;
  daily_pnl_pct: number;
  win_rate: number;
  profit_factor: number;
}

export interface WSPositionUpdate {
  ticket: number;
  current_price: number;
  profit: number;
}

export interface WSConnectionStatus {
  connected: boolean;
  terminal_id: string | null;
}

export interface WSError {
  message: string;
  timestamp: string;
}
