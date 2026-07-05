import { useEffect } from 'react';
import websocketService from '../services/websocket';
import { useAccountStore } from '../store/accountStore';
import { useTradesStore } from '../store/tradesStore';
import { useMetricsStore } from '../store/metricsStore';
import { useConnectionStore } from '../store/connectionStore';
import type { Position } from '../types';

export const useWebSocket = () => {
  const { updateEquity, updateProfit } = useAccountStore();
  const { addPosition, removePosition, updatePositionProfit, addSignal } = useTradesStore();
  const { updateDailyMetrics } = useMetricsStore();
  const { setWSConnected } = useConnectionStore();

  useEffect(() => {
    websocketService.connect({
      onConnect: () => {
        console.log('WebSocket connected');
        setWSConnected(true);
      },

      onDisconnect: () => {
        console.log('WebSocket disconnected');
        setWSConnected(false);
      },

      onTradeOpened: (data) => {
        const position: Position = {
          ticket: data.ticket,
          symbol: data.symbol,
          direction: data.direction,
          entry_price: data.entry_price,
          current_price: data.entry_price,
          tp: data.tp,
          sl: data.sl,
          profit: 0,
          volume: data.volume,
          open_time: data.timestamp,
        };
        addPosition(position);
      },

      onTradeClosed: (data) => {
        removePosition(data.ticket);
      },

      onNewSignal: (data) => {
        addSignal({
          id: Date.now(),
          timestamp: data.timestamp,
          symbol: data.symbol,
          direction: data.direction,
          confidence: data.confidence,
          entry_price: data.entry_price,
          tp: 0,
          sl: 0,
          executed: false,
        });
      },

      onAccountUpdate: (data) => {
        updateEquity(data.equity);
        updateProfit(data.profit);
      },

      onMetricsUpdate: (data) => {
        updateDailyMetrics(data);
      },

      onPositionUpdate: (data) => {
        updatePositionProfit(data.ticket, data.profit, data.current_price);
      },

      onConnectionStatus: (data) => {
        console.log('Connection status update:', data);
      },

      onError: (data) => {
        console.error('WebSocket error:', data.message);
      },
    });

    return () => {
      websocketService.disconnect();
    };
  }, [
    setWSConnected,
    addPosition,
    removePosition,
    updatePositionProfit,
    addSignal,
    updateEquity,
    updateProfit,
    updateDailyMetrics,
  ]);

  return {
    isConnected: websocketService.isConnected(),
  };
};
