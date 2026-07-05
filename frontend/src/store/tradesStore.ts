import { create } from 'zustand';
import type { Position, Trade, Signal } from '../types';

interface TradesState {
  openPositions: Position[];
  closedTrades: Trade[];
  signals: Signal[];
  setOpenPositions: (positions: Position[]) => void;
  addPosition: (position: Position) => void;
  updatePositionProfit: (ticket: number, profit: number, currentPrice: number) => void;
  removePosition: (ticket: number) => void;
  setClosedTrades: (trades: Trade[]) => void;
  addClosedTrade: (trade: Trade) => void;
  setSignals: (signals: Signal[]) => void;
  addSignal: (signal: Signal) => void;
  reset: () => void;
}

const initialState = {
  openPositions: [],
  closedTrades: [],
  signals: [],
};

export const useTradesStore = create<TradesState>((set) => ({
  ...initialState,

  setOpenPositions: (openPositions) => set({ openPositions }),

  addPosition: (position) =>
    set((state) => ({
      openPositions: [...state.openPositions, position],
    })),

  updatePositionProfit: (ticket, profit, currentPrice) =>
    set((state) => ({
      openPositions: state.openPositions.map((pos) =>
        pos.ticket === ticket ? { ...pos, profit, current_price: currentPrice } : pos
      ),
    })),

  removePosition: (ticket) =>
    set((state) => ({
      openPositions: state.openPositions.filter((pos) => pos.ticket !== ticket),
    })),

  setClosedTrades: (closedTrades) => set({ closedTrades }),

  addClosedTrade: (trade) =>
    set((state) => ({
      closedTrades: [trade, ...state.closedTrades].slice(0, 100), // Keep last 100
    })),

  setSignals: (signals) => set({ signals }),

  addSignal: (signal) =>
    set((state) => ({
      signals: [signal, ...state.signals].slice(0, 50), // Keep last 50
    })),

  reset: () => set(initialState),
}));
