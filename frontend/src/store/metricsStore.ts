import { create } from 'zustand';
import type { MetricsSummary, DailyMetrics, EquityPoint } from '../types';

interface MetricsState {
  summary: MetricsSummary | null;
  daily: DailyMetrics | null;
  equityCurve: EquityPoint[];
  setSummary: (summary: MetricsSummary) => void;
  setDaily: (daily: DailyMetrics) => void;
  setEquityCurve: (curve: EquityPoint[]) => void;
  updateDailyMetrics: (data: { daily_pnl: number; daily_pnl_pct: number; win_rate: number; profit_factor: number }) => void;
  reset: () => void;
}

const initialState = {
  summary: null,
  daily: null,
  equityCurve: [],
};

export const useMetricsStore = create<MetricsState>((set) => ({
  ...initialState,

  setSummary: (summary) => set({ summary }),

  setDaily: (daily) => set({ daily }),

  setEquityCurve: (equityCurve) => set({ equityCurve }),

  updateDailyMetrics: (data) =>
    set((state) => ({
      daily: state.daily
        ? {
            ...state.daily,
            net_profit: data.daily_pnl,
            win_rate: data.win_rate,
          }
        : null,
      summary: state.summary
        ? {
            ...state.summary,
            win_rate: data.win_rate,
            profit_factor: data.profit_factor,
          }
        : null,
    })),

  reset: () => set(initialState),
}));
