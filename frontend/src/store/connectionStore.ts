import { create } from 'zustand';
import type { Terminal, Symbol } from '../types';

interface ConnectionState {
  isConnected: boolean;
  isWSConnected: boolean;
  activeTerminal: Terminal | null;
  availableTerminals: Terminal[];
  currentSymbol: string | null;
  symbolInfo: Symbol | null;
  setConnected: (connected: boolean) => void;
  setWSConnected: (connected: boolean) => void;
  setActiveTerminal: (terminal: Terminal | null) => void;
  setAvailableTerminals: (terminals: Terminal[]) => void;
  setCurrentSymbol: (symbol: string | null, info?: Symbol) => void;
  reset: () => void;
}

const initialState = {
  isConnected: false,
  isWSConnected: false,
  activeTerminal: null,
  availableTerminals: [],
  currentSymbol: null,
  symbolInfo: null,
};

export const useConnectionStore = create<ConnectionState>((set) => ({
  ...initialState,

  setConnected: (isConnected) => set({ isConnected }),

  setWSConnected: (isWSConnected) => set({ isWSConnected }),

  setActiveTerminal: (activeTerminal) => set({ activeTerminal }),

  setAvailableTerminals: (availableTerminals) => set({ availableTerminals }),

  setCurrentSymbol: (currentSymbol, symbolInfo) =>
    set({ currentSymbol, symbolInfo: symbolInfo || null }),

  reset: () => set(initialState),
}));
