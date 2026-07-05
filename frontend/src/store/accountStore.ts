import { create } from 'zustand';
import type { AccountInfo } from '../types';

interface AccountState {
  account: AccountInfo | null;
  isLoading: boolean;
  error: string | null;
  setAccount: (account: AccountInfo) => void;
  updateBalance: (balance: number) => void;
  updateEquity: (equity: number) => void;
  updateProfit: (profit: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  account: null,
  isLoading: false,
  error: null,
};

export const useAccountStore = create<AccountState>((set) => ({
  ...initialState,

  setAccount: (account) => set({ account, error: null }),

  updateBalance: (balance) =>
    set((state) => ({
      account: state.account ? { ...state.account, balance } : null,
    })),

  updateEquity: (equity) =>
    set((state) => ({
      account: state.account ? { ...state.account, equity } : null,
    })),

  updateProfit: (profit) =>
    set((state) => ({
      account: state.account ? { ...state.account, profit } : null,
    })),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  reset: () => set(initialState),
}));
