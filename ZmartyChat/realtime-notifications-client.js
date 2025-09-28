/**
 * Real-time Cross-Project Notifications Client
 * Provides WebSocket connection and notification handling for the frontend
 */

class RealtimeNotificationsClient {
    constructor(userId, baseUrl = 'ws://localhost:8903') {
        this.userId = userId;
        this.baseUrl = baseUrl;
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        this.heartbeatInterval = null;
        this.notificationHandlers = new Map();
        this.connectionHandlers = new Map();
        
        // Bind methods
        this.connect = this.connect.bind(this);
        this.disconnect = this.disconnect.bind(this);
        this.send = this.send.bind(this);
        this._handleMessage = this._handleMessage.bind(this);
        this._handleOpen = this._handleOpen.bind(this);
        this._handleClose = this._handleClose.bind(this);
        this._handleError = this._handleError.bind(this);
        this._startHeartbeat = this._startHeartbeat.bind(this);
        this._stopHeartbeat = this._stopHeartbeat.bind(this);
        this._reconnect = this._reconnect.bind(this);
    }

    /**
     * Connect to the WebSocket server
     */
    async connect() {
        if (this.isConnected) {
            console.warn('⚠️ Already connected to notifications server');
            return;
        }

        try {
            const wsUrl = `${this.baseUrl}/ws/${this.userId}`;
            console.log(`🔌 Connecting to notifications server: ${wsUrl}`);
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = this._handleOpen;
            this.ws.onmessage = this._handleMessage;
            this.ws.onclose = this._handleClose;
            this.ws.onerror = this._handleError;
            
        } catch (error) {
            console.error('❌ Failed to connect to notifications server:', error);
            this._reconnect();
        }
    }

    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        if (this.ws) {
            this._stopHeartbeat();
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        this.reconnectAttempts = 0;
        console.log('🔌 Disconnected from notifications server');
    }

    /**
     * Send a message to the server
     */
    send(message) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('⚠️ Cannot send message: not connected to server');
        }
    }

    /**
     * Register a handler for specific notification types
     */
    onNotification(type, handler) {
        if (!this.notificationHandlers.has(type)) {
            this.notificationHandlers.set(type, []);
        }
        this.notificationHandlers.get(type).push(handler);
    }

    /**
     * Remove a notification handler
     */
    offNotification(type, handler) {
        if (this.notificationHandlers.has(type)) {
            const handlers = this.notificationHandlers.get(type);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    /**
     * Register a connection event handler
     */
    onConnection(event, handler) {
        if (!this.connectionHandlers.has(event)) {
            this.connectionHandlers.set(event, []);
        }
        this.connectionHandlers.get(event).push(handler);
    }

    /**
     * Remove a connection event handler
     */
    offConnection(event, handler) {
        if (this.connectionHandlers.has(event)) {
            const handlers = this.connectionHandlers.get(event);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    /**
     * Handle WebSocket open event
     */
    _handleOpen(event) {
        console.log('✅ Connected to notifications server');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000; // Reset delay
        
        this._startHeartbeat();
        this._emitConnectionEvent('connected', event);
    }

    /**
     * Handle WebSocket message event
     */
    _handleMessage(event) {
        try {
            const message = JSON.parse(event.data);
            
            if (message.type === 'pong') {
                // Heartbeat response
                return;
            }
            
            if (message.type === 'notification') {
                this._handleNotification(message.notification);
            }
            
        } catch (error) {
            console.error('❌ Failed to parse WebSocket message:', error);
        }
    }

    /**
     * Handle WebSocket close event
     */
    _handleClose(event) {
        console.log('🔌 Disconnected from notifications server:', event.code, event.reason);
        this.isConnected = false;
        this._stopHeartbeat();
        
        this._emitConnectionEvent('disconnected', event);
        
        // Attempt to reconnect if not a manual disconnect
        if (event.code !== 1000) {
            this._reconnect();
        }
    }

    /**
     * Handle WebSocket error event
     */
    _handleError(event) {
        console.error('❌ WebSocket error:', event);
        this._emitConnectionEvent('error', event);
    }

    /**
     * Handle incoming notifications
     */
    _handleNotification(notification) {
        console.log('📨 Received notification:', notification);
        
        // Call type-specific handlers
        if (this.notificationHandlers.has(notification.type)) {
            const handlers = this.notificationHandlers.get(notification.type);
            handlers.forEach(handler => {
                try {
                    handler(notification);
                } catch (error) {
                    console.error('❌ Error in notification handler:', error);
                }
            });
        }
        
        // Call general notification handlers
        if (this.notificationHandlers.has('*')) {
            const handlers = this.notificationHandlers.get('*');
            handlers.forEach(handler => {
                try {
                    handler(notification);
                } catch (error) {
                    console.error('❌ Error in general notification handler:', error);
                }
            });
        }
        
        // Show browser notification if permission granted
        this._showBrowserNotification(notification);
    }

    /**
     * Show browser notification
     */
    _showBrowserNotification(notification) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const browserNotification = new Notification(notification.title, {
                body: notification.message,
                icon: this._getNotificationIcon(notification.type),
                tag: notification.id,
                data: notification.data
            });
            
            // Auto-close after 5 seconds
            setTimeout(() => {
                browserNotification.close();
            }, 5000);
            
            // Handle click
            browserNotification.onclick = () => {
                window.focus();
                browserNotification.close();
            };
        }
    }

    /**
     * Get notification icon based on type
     */
    _getNotificationIcon(type) {
        const icons = {
            'user_update': '/icons/user.svg',
            'trading_signal': '/icons/trading.svg',
            'portfolio_change': '/icons/portfolio.svg',
            'alert_triggered': '/icons/alert.svg',
            'engagement_update': '/icons/engagement.svg',
            'performance_update': '/icons/performance.svg',
            'system_event': '/icons/system.svg'
        };
        
        return icons[type] || '/icons/notification.svg';
    }

    /**
     * Start heartbeat to keep connection alive
     */
    _startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'ping' });
            }
        }, 30000); // Send ping every 30 seconds
    }

    /**
     * Stop heartbeat
     */
    _stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    /**
     * Attempt to reconnect
     */
    _reconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Max reconnection attempts reached');
            this._emitConnectionEvent('max_reconnect_attempts_reached');
            return;
        }
        
        this.reconnectAttempts++;
        const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay);
        
        console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }

    /**
     * Emit connection event to handlers
     */
    _emitConnectionEvent(event, data) {
        if (this.connectionHandlers.has(event)) {
            const handlers = this.connectionHandlers.get(event);
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error('❌ Error in connection handler:', error);
                }
            });
        }
    }

    /**
     * Request notification permission
     */
    static async requestNotificationPermission() {
        if ('Notification' in window) {
            if (Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                return permission === 'granted';
            }
            return Notification.permission === 'granted';
        }
        return false;
    }

    /**
     * Get connection status
     */
    getStatus() {
        return {
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.maxReconnectAttempts,
            notificationHandlers: this.notificationHandlers.size,
            connectionHandlers: this.connectionHandlers.size
        };
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeNotificationsClient;
}

// Global registration for browser use
if (typeof window !== 'undefined') {
    window.RealtimeNotificationsClient = RealtimeNotificationsClient;
}

