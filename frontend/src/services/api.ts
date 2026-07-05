import axios from 'axios';
import type {
  AccountInfo,
  Terminal,
  Symbol,
  Position,
  Trade,
  Signal,
  MetricsSummary,
  DailyMetrics,
  EquityPoint,
  ConnectionStatus,
  Config,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Terminal Management
export const discoverTerminals = async (): Promise<Terminal[]> => {
  const response = await api.get<{ terminals: Terminal[] }>('/api/terminals/discover');
  return response.data.terminals;
};

export const connectTerminal = async (data: {
  terminal_id: string;
  account: number;
  password: string;
  server: string;
}): Promise<{ success: boolean; terminal: Terminal }> => {
  const response = await api.post('/api/terminals/connect', data);
  return response.data;
};

export const getActiveTerminal = async (): Promise<Terminal> => {
  const response = await api.get<Terminal>('/api/terminals/active');
  return response.data;
};

// Symbol Management
export const getAvailableSymbols = async (): Promise<Symbol[]> => {
  const response = await api.get<{ symbols: Symbol[] }>('/api/symbols/available');
  return response.data.symbols;
};

export const searchSymbols = async (query: string): Promise<Symbol[]> => {
  const response = await api.get<{ symbols: Symbol[] }>(`/api/symbols/search?query=${query}`);
  return response.data.symbols;
};

export const selectSymbol = async (symbol: string): Promise<{ success: boolean; symbol: string }> => {
  const response = await api.post('/api/symbols/select', { symbol });
  return response.data;
};

export const getCurrentSymbol = async (): Promise<{ symbol: string; info: Symbol }> => {
  const response = await api.get('/api/symbols/current');
  return response.data;
};

// Account & Connection
export const getAccountInfo = async (): Promise<AccountInfo> => {
  const response = await api.get<AccountInfo>('/api/account/info');
  return response.data;
};

export const getConnectionStatus = async (): Promise<ConnectionStatus> => {
  const response = await api.get<ConnectionStatus>('/api/connection/status');
  return response.data;
};

export const getHealth = async (): Promise<{ status: string; timestamp: string }> => {
  const response = await api.get('/api/health');
  return response.data;
};

// Positions & Trades
export const getOpenPositions = async (): Promise<Position[]> => {
  const response = await api.get<Position[]>('/api/positions/open');
  return response.data;
};

export const closePosition = async (ticket: number): Promise<{ success: boolean }> => {
  const response = await api.post(`/api/positions/close/${ticket}`);
  return response.data;
};

export const closeAllPositions = async (): Promise<{ success: boolean; closed_count: number }> => {
  const response = await api.post('/api/positions/close_all');
  return response.data;
};

export const getTradeHistory = async (
  limit: number = 50,
  offset: number = 0
): Promise<Trade[]> => {
  const response = await api.get<Trade[]>(`/api/trades/history?limit=${limit}&offset=${offset}`);
  return response.data;
};

// Signals
export const getSignalHistory = async (
  limit: number = 50,
  offset: number = 0
): Promise<Signal[]> => {
  const response = await api.get<Signal[]>(`/api/signals/history?limit=${limit}&offset=${offset}`);
  return response.data;
};

export const getLatestSignal = async (): Promise<Signal | null> => {
  const response = await api.get<Signal | null>('/api/signals/latest');
  return response.data;
};

// Metrics
export const getMetricsSummary = async (): Promise<MetricsSummary> => {
  const response = await api.get<MetricsSummary>('/api/metrics/summary');
  return response.data;
};

export const getDailyMetrics = async (): Promise<DailyMetrics> => {
  const response = await api.get<DailyMetrics>('/api/metrics/daily');
  return response.data;
};

export const getEquityCurve = async (): Promise<EquityPoint[]> => {
  const response = await api.get<EquityPoint[]>('/api/metrics/equity_curve');
  return response.data;
};

// Configuration
export const getConfig = async (): Promise<Config> => {
  const response = await api.get<Config>('/api/config');
  return response.data;
};

export const updateConfig = async (config: Partial<Config>): Promise<{ success: boolean }> => {
  const response = await api.post('/api/config/update', config);
  return response.data;
};

export default api;
