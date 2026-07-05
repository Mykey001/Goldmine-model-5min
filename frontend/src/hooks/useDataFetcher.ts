import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import * as api from '../services/api';
import { useAccountStore } from '../store/accountStore';
import { useTradesStore } from '../store/tradesStore';
import { useMetricsStore } from '../store/metricsStore';
import { useConnectionStore } from '../store/connectionStore';

export const useDataFetcher = () => {
  const { setAccount } = useAccountStore();
  const { setOpenPositions, setClosedTrades, setSignals } = useTradesStore();
  const { setSummary, setDaily, setEquityCurve } = useMetricsStore();
  const { setConnected, isConnected } = useConnectionStore();

  // Fetch connection status
  const { data: connectionStatus } = useQuery({
    queryKey: ['connectionStatus'],
    queryFn: api.getConnectionStatus,
    refetchInterval: 5000,
    retry: false,
  });

  useEffect(() => {
    if (connectionStatus) {
      setConnected(connectionStatus.connected);
    }
  }, [connectionStatus, setConnected]);

  // Fetch account info
  const { data: accountInfo } = useQuery({
    queryKey: ['accountInfo'],
    queryFn: api.getAccountInfo,
    enabled: isConnected,
    refetchInterval: 2000,
    retry: false,
  });

  useEffect(() => {
    if (accountInfo) {
      setAccount(accountInfo);
    }
  }, [accountInfo, setAccount]);

  // Fetch open positions
  const { data: positions } = useQuery({
    queryKey: ['openPositions'],
    queryFn: api.getOpenPositions,
    enabled: isConnected,
    refetchInterval: 1000,
    retry: false,
  });

  useEffect(() => {
    if (positions) {
      setOpenPositions(positions);
    }
  }, [positions, setOpenPositions]);

  // Fetch trade history
  const { data: tradeHistory } = useQuery({
    queryKey: ['tradeHistory'],
    queryFn: () => api.getTradeHistory(50, 0),
    enabled: isConnected,
    refetchInterval: 5000,
    retry: false,
  });

  useEffect(() => {
    if (tradeHistory) {
      setClosedTrades(tradeHistory);
    }
  }, [tradeHistory, setClosedTrades]);

  // Fetch signal history
  const { data: signalHistory } = useQuery({
    queryKey: ['signalHistory'],
    queryFn: () => api.getSignalHistory(50, 0),
    enabled: isConnected,
    refetchInterval: 5000,
    retry: false,
  });

  useEffect(() => {
    if (signalHistory) {
      setSignals(signalHistory);
    }
  }, [signalHistory, setSignals]);

  // Fetch metrics summary
  const { data: metricsSummary } = useQuery({
    queryKey: ['metricsSummary'],
    queryFn: api.getMetricsSummary,
    enabled: isConnected,
    refetchInterval: 10000,
    retry: false,
  });

  useEffect(() => {
    if (metricsSummary) {
      setSummary(metricsSummary);
    }
  }, [metricsSummary, setSummary]);

  // Fetch daily metrics
  const { data: dailyMetrics } = useQuery({
    queryKey: ['dailyMetrics'],
    queryFn: api.getDailyMetrics,
    enabled: isConnected,
    refetchInterval: 5000,
    retry: false,
  });

  useEffect(() => {
    if (dailyMetrics) {
      setDaily(dailyMetrics);
    }
  }, [dailyMetrics, setDaily]);

  // Fetch equity curve
  const { data: equityCurve } = useQuery({
    queryKey: ['equityCurve'],
    queryFn: api.getEquityCurve,
    enabled: isConnected,
    refetchInterval: 30000,
    retry: false,
  });

  useEffect(() => {
    if (equityCurve) {
      setEquityCurve(equityCurve);
    }
  }, [equityCurve, setEquityCurve]);
};
