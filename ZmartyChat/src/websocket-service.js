// WebSocket Service for Real-time Communication
// Handles all real-time data streams for ZmartyChat

class WebSocketService {
    constructor(config = {}) {
        this.config = {
            url: config.url || 'wss://api.zmartychat.com/ws',
            reconnectDelay: config.reconnectDelay || 1000,
            maxReconnectDelay: config.maxReconnectDelay || 30000,
            reconnectDecay: config.reconnectDecay || 1.5,
            maxReconnectAttempts: config.maxReconnectAttempts || null,
            heartbeatInterval: config.heartbeatInterval || 30000,
            debug: config.debug || false
        };

        this.ws = null;
        this.reconnectAttempts = 0;
        this.reconnectTimeout = null;
        this.heartbeatInterval = null;
        this.messageQueue = [];
        this.subscriptions = new Map();
        this.eventHandlers = new Map();
        this.connectionState = 'disconnected';
        this.authToken = null;
        this.userId = null;
    }

    // Connection Management
    connect(authToken = null, userId = null) {
        if (this.connectionState === 'connected' || this.connectionState === 'connecting') {
            this.log('Already connected or connecting');
            return Promise.resolve();
        }

        this.authToken = authToken;
        this.userId = userId;

        return new Promise((resolve, reject) => {
            try {
                this.connectionState = 'connecting';
                this.emit('connecting');

                // Build connection URL with auth params
                let wsUrl = this.config.url;
                if (authToken) {
                    wsUrl += `?token=${encodeURIComponent(authToken)}`;
                    if (userId) {
                        wsUrl += `&userId=${encodeURIComponent(userId)}`;
                    }
                }

                this.ws = new WebSocket(wsUrl);

                // Connection opened
                this.ws.onopen = () => {
                    this.connectionState = 'connected';
                    this.reconnectAttempts = 0;
                    this.log('WebSocket connected');

                    // Start heartbeat
                    this.startHeartbeat();

                    // Process queued messages
                    this.processMessageQueue();

                    // Re-establish subscriptions
                    this.resubscribe();

                    this.emit('connected');
                    resolve();
                };

                // Message received
                this.ws.onmessage = (event) => {
                    this.handleMessage(event.data);
                };

                // Connection closed
                this.ws.onclose = (event) => {
                    this.connectionState = 'disconnected';
                    this.stopHeartbeat();
                    this.log(`WebSocket closed: ${event.code} - ${event.reason}`);
                    this.emit('disconnected', { code: event.code, reason: event.reason });

                    // Auto-reconnect if not a manual close
                    if (event.code !== 1000 && event.code !== 1001) {
                        this.scheduleReconnect();
                    }
                };

                // Connection error
                this.ws.onerror = (error) => {
                    this.log('WebSocket error:', error);
                    this.emit('error', error);
                    reject(error);
                };

            } catch (error) {
                this.connectionState = 'disconnected';
                this.log('Connection failed:', error);
                reject(error);
            }
        });
    }

    disconnect() {
        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = null;
        }

        this.stopHeartbeat();

        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
            this.ws = null;
        }

        this.connectionState = 'disconnected';
        this.emit('disconnected', { manual: true });
    }

    // Auto-reconnection logic
    scheduleReconnect() {
        if (this.config.maxReconnectAttempts &&
            this.reconnectAttempts >= this.config.maxReconnectAttempts) {
            this.log('Max reconnect attempts reached');
            this.emit('reconnectFailed');
            return;
        }

        const delay = Math.min(
            this.config.reconnectDelay * Math.pow(this.config.reconnectDecay, this.reconnectAttempts),
            this.config.maxReconnectDelay
        );

        this.reconnectAttempts++;
        this.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);

        this.reconnectTimeout = setTimeout(() => {
            this.log(`Reconnect attempt ${this.reconnectAttempts}`);
            this.emit('reconnecting', { attempt: this.reconnectAttempts });
            this.connect(this.authToken, this.userId);
        }, delay);
    }

    // Heartbeat to keep connection alive
    startHeartbeat() {
        this.stopHeartbeat();
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected()) {
                this.send({ type: 'ping' });
            }
        }, this.config.heartbeatInterval);
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    // Message handling
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            this.log('Received message:', message);

            // Handle system messages
            if (message.type === 'pong') {
                return; // Heartbeat response
            }

            if (message.type === 'error') {
                this.emit('error', message);
                return;
            }

            // Handle subscription messages
            if (message.channel && this.subscriptions.has(message.channel)) {
                const handlers = this.subscriptions.get(message.channel);
                handlers.forEach(handler => {
                    try {
                        handler(message.data, message);
                    } catch (error) {
                        console.error('Subscription handler error:', error);
                    }
                });
            }

            // Handle general event messages
            if (message.event && this.eventHandlers.has(message.event)) {
                const handlers = this.eventHandlers.get(message.event);
                handlers.forEach(handler => {
                    try {
                        handler(message.data, message);
                    } catch (error) {
                        console.error('Event handler error:', error);
                    }
                });
            }

            // Emit raw message for custom handling
            this.emit('message', message);

        } catch (error) {
            this.log('Failed to parse message:', error);
            this.emit('parseError', { data, error });
        }
    }

    // Message sending
    send(data) {
        if (!this.isConnected()) {
            this.log('Not connected, queuing message');
            this.messageQueue.push(data);
            return false;
        }

        try {
            const message = typeof data === 'string' ? data : JSON.stringify(data);
            this.ws.send(message);
            this.log('Sent message:', data);
            return true;
        } catch (error) {
            this.log('Failed to send message:', error);
            this.emit('sendError', { data, error });
            return false;
        }
    }

    processMessageQueue() {
        while (this.messageQueue.length > 0 && this.isConnected()) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }

    // Channel subscriptions
    subscribe(channel, handler) {
        if (!this.subscriptions.has(channel)) {
            this.subscriptions.set(channel, new Set());

            // Send subscription request if connected
            if (this.isConnected()) {
                this.send({
                    type: 'subscribe',
                    channel: channel
                });
            }
        }

        this.subscriptions.get(channel).add(handler);
        this.log(`Subscribed to channel: ${channel}`);

        // Return unsubscribe function
        return () => this.unsubscribe(channel, handler);
    }

    unsubscribe(channel, handler) {
        if (!this.subscriptions.has(channel)) return;

        const handlers = this.subscriptions.get(channel);
        handlers.delete(handler);

        if (handlers.size === 0) {
            this.subscriptions.delete(channel);

            // Send unsubscribe request if connected
            if (this.isConnected()) {
                this.send({
                    type: 'unsubscribe',
                    channel: channel
                });
            }
        }

        this.log(`Unsubscribed from channel: ${channel}`);
    }

    resubscribe() {
        this.subscriptions.forEach((handlers, channel) => {
            this.send({
                type: 'subscribe',
                channel: channel
            });
        });
    }

    // Event handling
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, new Set());
        }
        this.eventHandlers.get(event).add(handler);

        // Return unsubscribe function
        return () => this.off(event, handler);
    }

    off(event, handler) {
        if (!this.eventHandlers.has(event)) return;

        const handlers = this.eventHandlers.get(event);
        handlers.delete(handler);

        if (handlers.size === 0) {
            this.eventHandlers.delete(event);
        }
    }

    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Error in event handler for ${event}:`, error);
                }
            });
        }
    }

    // Utility methods
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    getConnectionState() {
        return this.connectionState;
    }

    log(...args) {
        if (this.config.debug) {
            console.log('[WebSocket]', ...args);
        }
    }

    // Domain-specific methods for ZmartyChat

    // Trading data streams
    subscribeToPriceUpdates(symbols, handler) {
        return this.subscribe('price-updates', (data) => {
            if (symbols.includes(data.symbol)) {
                handler(data);
            }
        });
    }

    subscribeToOrderBook(symbol, handler) {
        return this.subscribe(`orderbook-${symbol}`, handler);
    }

    subscribeToTrades(symbol, handler) {
        return this.subscribe(`trades-${symbol}`, handler);
    }

    subscribeToPortfolio(userId, handler) {
        return this.subscribe(`portfolio-${userId}`, handler);
    }

    // AI provider updates
    subscribeToAIStatus(handler) {
        return this.subscribe('ai-status', handler);
    }

    subscribeToAIAnalysis(handler) {
        return this.subscribe('ai-analysis', handler);
    }

    // System monitoring
    subscribeToSystemMetrics(handler) {
        return this.subscribe('system-metrics', handler);
    }

    subscribeToCircuitBreakers(handler) {
        return this.subscribe('circuit-breakers', handler);
    }

    subscribeToAlerts(handler) {
        return this.subscribe('alerts', handler);
    }

    // User notifications
    subscribeToNotifications(userId, handler) {
        return this.subscribe(`notifications-${userId}`, handler);
    }

    subscribeToWhaleAlerts(handler) {
        return this.subscribe('whale-alerts', handler);
    }

    // Trading operations
    placeTrade(order) {
        return this.send({
            type: 'trade',
            action: 'place',
            data: order
        });
    }

    cancelTrade(orderId) {
        return this.send({
            type: 'trade',
            action: 'cancel',
            orderId: orderId
        });
    }

    // Request-response pattern
    request(type, data, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const requestId = this.generateRequestId();
            const timeoutId = setTimeout(() => {
                this.off(`response-${requestId}`, responseHandler);
                reject(new Error('Request timeout'));
            }, timeout);

            const responseHandler = (response) => {
                clearTimeout(timeoutId);
                if (response.error) {
                    reject(new Error(response.error));
                } else {
                    resolve(response.data);
                }
            };

            this.on(`response-${requestId}`, responseHandler);

            this.send({
                type: 'request',
                requestType: type,
                requestId: requestId,
                data: data
            });
        });
    }

    generateRequestId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
}

// Create singleton instance
const wsService = new WebSocketService({
    url: window.location.protocol === 'https:'
        ? 'wss://' + window.location.host + '/ws'
        : 'ws://localhost:8080/ws',
    debug: true
});

// Auto-connect if auth token exists
if (typeof window !== 'undefined') {
    window.addEventListener('load', () => {
        const authToken = localStorage.getItem('authToken');
        const userId = localStorage.getItem('userId');
        if (authToken) {
            wsService.connect(authToken, userId);
        }
    });

    // Export to window for global access
    window.wsService = wsService;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketService;
}