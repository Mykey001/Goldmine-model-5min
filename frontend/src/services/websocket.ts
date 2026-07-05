import type {
  WSTradeOpened,
  WSTradeClosed,
  WSNewSignal,
  WSAccountUpdate,
  WSMetricsUpdate,
  WSPositionUpdate,
  WSConnectionStatus,
  WSError,
} from '../types';

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000';

export type WebSocketEventHandlers = {
  onTradeOpened?: (data: WSTradeOpened) => void;
  onTradeClosed?: (data: WSTradeClosed) => void;
  onNewSignal?: (data: WSNewSignal) => void;
  onAccountUpdate?: (data: WSAccountUpdate) => void;
  onMetricsUpdate?: (data: WSMetricsUpdate) => void;
  onPositionUpdate?: (data: WSPositionUpdate) => void;
  onConnectionStatus?: (data: WSConnectionStatus) => void;
  onError?: (data: WSError) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
};

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: WebSocketEventHandlers = {};
  private reconnectInterval: number = 3000;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;

  connect(handlers: WebSocketEventHandlers) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.handlers = handlers;
    const wsUrl = WS_URL.replace('http://', 'ws://').replace('https://', 'wss://');
    
    try {
      this.ws = new WebSocket(`${wsUrl}/ws`);
      this.setupListeners();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.scheduleReconnect();
    }
  }

  private setupListeners() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.handlers.onConnect?.();
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.handlers.onDisconnect?.();
      this.scheduleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  private handleMessage(message: any) {
    const { type, data } = message;

    switch (type) {
      case 'trade_opened':
        this.handlers.onTradeOpened?.(data);
        break;
      case 'trade_closed':
        this.handlers.onTradeClosed?.(data);
        break;
      case 'new_signal':
        this.handlers.onNewSignal?.(data);
        break;
      case 'account_update':
        this.handlers.onAccountUpdate?.(data);
        break;
      case 'metrics_update':
        this.handlers.onMetricsUpdate?.(data);
        break;
      case 'position_update':
        this.handlers.onPositionUpdate?.(data);
        break;
      case 'connection_status':
        this.handlers.onConnectionStatus?.(data);
        break;
      case 'error':
        this.handlers.onError?.(data);
        break;
      default:
        console.log('Unknown WebSocket message type:', type);
    }
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`Reconnecting in ${this.reconnectInterval}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.handlers.onConnect) {
        this.connect(this.handlers);
      }
    }, this.reconnectInterval);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }
}

export const websocketService = new WebSocketService();
export default websocketService;
