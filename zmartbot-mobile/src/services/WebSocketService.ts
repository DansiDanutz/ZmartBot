type MessageHandler = (data: any) => void;
type ConnectionHandler = () => void;

export interface PriceUpdate {
  symbol: string;
  price: number;
  timestamp: number;
  change: number;
  changePercent: number;
  volume: string;
}

export interface SignalUpdate {
  id: string;
  symbol: string;
  type: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  timestamp: number;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private connectionHandlers: Set<ConnectionHandler> = new Set();
  private isConnected = false;

  constructor(url: string = 'ws://localhost:8000/ws') {
    this.url = url;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.connectionHandlers.forEach(handler => handler());
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.isConnected = false;
        this.stopHeartbeat();
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private handleMessage(data: any): void {
    const { type, payload } = data;

    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.forEach(handler => handler(payload));
    }

    // Handle specific message types
    switch (type) {
      case 'price_update':
        this.handlePriceUpdate(payload);
        break;
      case 'signal_update':
        this.handleSignalUpdate(payload);
        break;
      case 'pong':
        // Heartbeat response
        break;
      default:
        console.log('Unhandled message type:', type);
    }
  }

  private handlePriceUpdate(data: PriceUpdate): void {
    const handlers = this.messageHandlers.get('price');
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  private handleSignalUpdate(data: SignalUpdate): void {
    const handlers = this.messageHandlers.get('signal');
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  subscribe(type: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }

    this.messageHandlers.get(type)!.add(handler);

    // Send subscription message to server
    if (this.isConnected) {
      this.send({
        type: 'subscribe',
        channel: type
      });
    }

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(type);
          // Send unsubscribe message to server
          if (this.isConnected) {
            this.send({
              type: 'unsubscribe',
              channel: type
            });
          }
        }
      }
    };
  }

  onConnection(handler: ConnectionHandler): () => void {
    this.connectionHandlers.add(handler);

    // Call immediately if already connected
    if (this.isConnected) {
      handler();
    }

    return () => {
      this.connectionHandlers.delete(handler);
    };
  }

  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, message not sent:', data);
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      this.send({ type: 'ping' });
    }, 30000);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.messageHandlers.clear();
    this.connectionHandlers.clear();
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  // Convenience methods for common subscriptions
  subscribeToPrices(symbols: string[], handler: (update: PriceUpdate) => void): () => void {
    this.send({
      type: 'subscribe_prices',
      symbols
    });
    return this.subscribe('price', handler);
  }

  subscribeToSignals(handler: (update: SignalUpdate) => void): () => void {
    return this.subscribe('signal', handler);
  }
}

// Singleton instance
export const wsService = new WebSocketService();