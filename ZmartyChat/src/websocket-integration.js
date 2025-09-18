// WebSocket Integration for UI Components
// Connects all dashboards and interfaces to real-time data streams

class WebSocketIntegration {
    constructor() {
        this.wsService = null;
        this.subscriptions = [];
        this.componentUpdaters = new Map();
        this.init();
    }

    init() {
        // Load WebSocket service
        if (typeof wsService !== 'undefined') {
            this.wsService = wsService;
        } else if (typeof WebSocketService !== 'undefined') {
            this.wsService = new WebSocketService();
        } else {
            console.error('WebSocket service not found');
            return;
        }

        // Set up connection event handlers
        this.setupConnectionHandlers();
    }

    setupConnectionHandlers() {
        this.wsService.on('connected', () => {
            this.showConnectionStatus('connected');
            this.subscribeToAllChannels();
        });

        this.wsService.on('disconnected', () => {
            this.showConnectionStatus('disconnected');
        });

        this.wsService.on('reconnecting', (data) => {
            this.showConnectionStatus('reconnecting', data.attempt);
        });

        this.wsService.on('error', (error) => {
            console.error('WebSocket error:', error);
            this.showNotification('Connection error', 'error');
        });
    }

    showConnectionStatus(status, attempt = null) {
        const indicator = document.getElementById('ws-status-indicator');
        if (!indicator) return;

        const statusColors = {
            connected: '#00d67a',
            disconnected: '#ff3b30',
            reconnecting: '#ff9500'
        };

        indicator.style.backgroundColor = statusColors[status];
        indicator.title = status === 'reconnecting'
            ? `Reconnecting (attempt ${attempt})`
            : status;

        // Show toast notification for status changes
        if (status === 'connected') {
            this.showNotification('Real-time connection established', 'success');
        } else if (status === 'disconnected') {
            this.showNotification('Real-time connection lost', 'warning');
        }
    }

    showNotification(message, type = 'info') {
        // Use existing notification system if available
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    // Connect to WebSocket with authentication
    connect(authToken, userId) {
        return this.wsService.connect(authToken, userId);
    }

    disconnect() {
        this.unsubscribeAll();
        this.wsService.disconnect();
    }

    // Subscribe to all necessary channels based on current page
    subscribeToAllChannels() {
        const currentPage = this.detectCurrentPage();

        switch(currentPage) {
            case 'dashboard':
                this.subscribeToDashboardChannels();
                break;
            case 'admin':
                this.subscribeToAdminChannels();
                break;
            case 'trading':
                this.subscribeToTradingChannels();
                break;
            default:
                this.subscribeToGeneralChannels();
        }
    }

    detectCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('dashboard')) return 'dashboard';
        if (path.includes('admin')) return 'admin';
        if (path.includes('trading') || path.includes('web-app')) return 'trading';
        return 'general';
    }

    // Dashboard subscriptions
    subscribeToDashboardChannels() {
        const userId = localStorage.getItem('userId');

        // Portfolio updates
        this.subscriptions.push(
            this.wsService.subscribeToPortfolio(userId, (data) => {
                this.updatePortfolioDisplay(data);
            })
        );

        // Price updates for watched assets
        const watchedSymbols = this.getWatchedSymbols();
        this.subscriptions.push(
            this.wsService.subscribeToPriceUpdates(watchedSymbols, (data) => {
                this.updatePriceDisplay(data);
            })
        );

        // AI analysis updates
        this.subscriptions.push(
            this.wsService.subscribeToAIAnalysis((data) => {
                this.updateAIInsights(data);
            })
        );

        // Whale alerts
        this.subscriptions.push(
            this.wsService.subscribeToWhaleAlerts((data) => {
                this.displayWhaleAlert(data);
            })
        );

        // User notifications
        this.subscriptions.push(
            this.wsService.subscribeToNotifications(userId, (data) => {
                this.displayNotification(data);
            })
        );
    }

    // Admin panel subscriptions
    subscribeToAdminChannels() {
        // System metrics
        this.subscriptions.push(
            this.wsService.subscribeToSystemMetrics((data) => {
                this.updateSystemMetrics(data);
            })
        );

        // Circuit breaker status
        this.subscriptions.push(
            this.wsService.subscribeToCircuitBreakers((data) => {
                this.updateCircuitBreakerStatus(data);
            })
        );

        // System alerts
        this.subscriptions.push(
            this.wsService.subscribeToAlerts((data) => {
                this.displaySystemAlert(data);
            })
        );

        // AI provider status
        this.subscriptions.push(
            this.wsService.subscribeToAIStatus((data) => {
                this.updateAIProviderStatus(data);
            })
        );
    }

    // Trading interface subscriptions
    subscribeToTradingChannels() {
        const activeSymbol = this.getActiveSymbol();

        // Order book updates
        this.subscriptions.push(
            this.wsService.subscribeToOrderBook(activeSymbol, (data) => {
                this.updateOrderBook(data);
            })
        );

        // Recent trades
        this.subscriptions.push(
            this.wsService.subscribeToTrades(activeSymbol, (data) => {
                this.updateRecentTrades(data);
            })
        );

        // Price chart updates
        this.subscriptions.push(
            this.wsService.subscribeToPriceUpdates([activeSymbol], (data) => {
                this.updatePriceChart(data);
            })
        );
    }

    // General subscriptions for all pages
    subscribeToGeneralChannels() {
        const userId = localStorage.getItem('userId');
        if (userId) {
            this.subscriptions.push(
                this.wsService.subscribeToNotifications(userId, (data) => {
                    this.displayNotification(data);
                })
            );
        }
    }

    // UI Update Methods

    updatePortfolioDisplay(data) {
        const elements = {
            totalValue: document.getElementById('portfolio-total-value'),
            dailyPnl: document.getElementById('portfolio-daily-pnl'),
            positions: document.getElementById('portfolio-positions')
        };

        if (elements.totalValue) {
            elements.totalValue.textContent = `$${data.totalValue.toLocaleString()}`;
        }

        if (elements.dailyPnl) {
            const pnlClass = data.dailyPnl >= 0 ? 'positive' : 'negative';
            elements.dailyPnl.className = `metric-change ${pnlClass}`;
            elements.dailyPnl.textContent = `${data.dailyPnl >= 0 ? '+' : ''}${data.dailyPnl.toFixed(2)}%`;
        }

        if (elements.positions && data.positions) {
            this.renderPositions(elements.positions, data.positions);
        }
    }

    updatePriceDisplay(data) {
        const priceElement = document.querySelector(`[data-symbol="${data.symbol}"] .price`);
        if (priceElement) {
            priceElement.textContent = `$${data.price.toFixed(2)}`;

            // Add flash animation
            priceElement.classList.add('price-flash');
            setTimeout(() => {
                priceElement.classList.remove('price-flash');
            }, 300);
        }

        // Update chart if exists
        if (typeof updateChartData === 'function') {
            updateChartData(data.symbol, data.price, data.timestamp);
        }
    }

    updateAIInsights(data) {
        const insightsContainer = document.getElementById('ai-insights');
        if (!insightsContainer) return;

        const insight = document.createElement('div');
        insight.className = 'ai-insight-card';
        insight.innerHTML = `
            <div class="insight-header">
                <span class="insight-provider">${data.provider}</span>
                <span class="insight-time">${new Date(data.timestamp).toLocaleTimeString()}</span>
            </div>
            <div class="insight-content">
                <h4>${data.title}</h4>
                <p>${data.description}</p>
                <div class="insight-metrics">
                    <span class="confidence">Confidence: ${data.confidence}%</span>
                    <span class="impact ${data.impact}">${data.impact.toUpperCase()}</span>
                </div>
            </div>
        `;

        insightsContainer.insertBefore(insight, insightsContainer.firstChild);

        // Keep only last 10 insights
        while (insightsContainer.children.length > 10) {
            insightsContainer.removeChild(insightsContainer.lastChild);
        }
    }

    displayWhaleAlert(data) {
        const alertsContainer = document.getElementById('whale-alerts');
        if (!alertsContainer) return;

        const alert = document.createElement('div');
        alert.className = 'whale-alert animate-slide-in';
        alert.innerHTML = `
            <div class="alert-icon">🐋</div>
            <div class="alert-content">
                <div class="alert-title">${data.type} Alert</div>
                <div class="alert-description">
                    ${data.amount} ${data.currency} ${data.action}
                    ${data.from ? `from ${data.from}` : ''}
                    ${data.to ? `to ${data.to}` : ''}
                </div>
                <div class="alert-time">${new Date(data.timestamp).toLocaleTimeString()}</div>
            </div>
        `;

        alertsContainer.insertBefore(alert, alertsContainer.firstChild);

        // Keep only last 5 alerts
        while (alertsContainer.children.length > 5) {
            alertsContainer.removeChild(alertsContainer.lastChild);
        }

        // Show notification
        this.showNotification(`🐋 Whale Alert: ${data.amount} ${data.currency} ${data.action}`, 'info');
    }

    updateSystemMetrics(data) {
        Object.keys(data).forEach(metric => {
            const element = document.getElementById(`metric-${metric}`);
            if (element) {
                element.textContent = this.formatMetricValue(metric, data[metric]);
            }
        });
    }

    updateCircuitBreakerStatus(data) {
        const breakerCard = document.querySelector(`[data-breaker="${data.name}"]`);
        if (!breakerCard) return;

        const statusElement = breakerCard.querySelector('.breaker-status');
        if (statusElement) {
            statusElement.className = `breaker-status status-${data.status}`;
            statusElement.textContent = data.status.toUpperCase();
        }

        // Update stats
        if (data.stats) {
            Object.keys(data.stats).forEach(stat => {
                const statElement = breakerCard.querySelector(`[data-stat="${stat}"]`);
                if (statElement) {
                    statElement.textContent = data.stats[stat];
                }
            });
        }
    }

    updateOrderBook(data) {
        const bidsList = document.getElementById('order-book-bids');
        const asksList = document.getElementById('order-book-asks');

        if (bidsList && data.bids) {
            this.renderOrderBookSide(bidsList, data.bids, 'bid');
        }

        if (asksList && data.asks) {
            this.renderOrderBookSide(asksList, data.asks, 'ask');
        }

        // Update spread
        if (data.bids.length > 0 && data.asks.length > 0) {
            const spread = data.asks[0].price - data.bids[0].price;
            const spreadElement = document.getElementById('order-book-spread');
            if (spreadElement) {
                spreadElement.textContent = `Spread: $${spread.toFixed(2)}`;
            }
        }
    }

    renderOrderBookSide(container, orders, type) {
        container.innerHTML = orders.slice(0, 10).map(order => `
            <div class="order-book-row ${type}">
                <span class="order-price">${order.price.toFixed(2)}</span>
                <span class="order-amount">${order.amount.toFixed(4)}</span>
                <span class="order-total">${(order.price * order.amount).toFixed(2)}</span>
            </div>
        `).join('');
    }

    updateRecentTrades(data) {
        const tradesContainer = document.getElementById('recent-trades');
        if (!tradesContainer) return;

        const trade = document.createElement('div');
        trade.className = `trade-row ${data.side}`;
        trade.innerHTML = `
            <span class="trade-time">${new Date(data.timestamp).toLocaleTimeString()}</span>
            <span class="trade-price ${data.side}">${data.price.toFixed(2)}</span>
            <span class="trade-amount">${data.amount.toFixed(4)}</span>
        `;

        tradesContainer.insertBefore(trade, tradesContainer.firstChild);

        // Keep only last 20 trades
        while (tradesContainer.children.length > 20) {
            tradesContainer.removeChild(tradesContainer.lastChild);
        }
    }

    displayNotification(data) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${data.type}`;
        notification.innerHTML = `
            <div class="notification-icon">${this.getNotificationIcon(data.type)}</div>
            <div class="notification-content">
                <div class="notification-title">${data.title}</div>
                <div class="notification-message">${data.message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;

        const container = document.getElementById('notifications-container') || document.body;
        container.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    // Utility methods
    getWatchedSymbols() {
        // Get from localStorage or default list
        const stored = localStorage.getItem('watchedSymbols');
        return stored ? JSON.parse(stored) : ['BTC', 'ETH', 'SOL', 'MATIC'];
    }

    getActiveSymbol() {
        // Get from URL params or localStorage
        const params = new URLSearchParams(window.location.search);
        return params.get('symbol') || localStorage.getItem('activeSymbol') || 'BTC';
    }

    formatMetricValue(metric, value) {
        if (metric.includes('revenue') || metric.includes('cost')) {
            return `$${value.toLocaleString()}`;
        }
        if (metric.includes('percent') || metric.includes('rate')) {
            return `${value.toFixed(2)}%`;
        }
        if (metric.includes('count') || metric.includes('total')) {
            return value.toLocaleString();
        }
        return value;
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✓',
            warning: '⚠',
            error: '✕',
            info: 'ℹ',
            trade: '📊',
            alert: '🔔'
        };
        return icons[type] || '•';
    }

    renderPositions(container, positions) {
        container.innerHTML = positions.map(position => `
            <div class="position-row">
                <div class="position-symbol">${position.symbol}</div>
                <div class="position-amount">${position.amount}</div>
                <div class="position-value">$${position.value.toLocaleString()}</div>
                <div class="position-pnl ${position.pnl >= 0 ? 'positive' : 'negative'}">
                    ${position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)}%
                </div>
            </div>
        `).join('');
    }

    unsubscribeAll() {
        this.subscriptions.forEach(unsubscribe => {
            if (typeof unsubscribe === 'function') {
                unsubscribe();
            }
        });
        this.subscriptions = [];
    }
}

// Create and initialize integration
const wsIntegration = new WebSocketIntegration();

// Auto-connect when auth is available
document.addEventListener('DOMContentLoaded', () => {
    const authToken = localStorage.getItem('authToken');
    const userId = localStorage.getItem('userId');

    if (authToken) {
        wsIntegration.connect(authToken, userId);
    }
});

// Export for global access
window.wsIntegration = wsIntegration;

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    .price-flash {
        animation: priceFlash 0.3s ease;
    }

    @keyframes priceFlash {
        0% { background: transparent; }
        50% { background: rgba(0, 255, 136, 0.2); }
        100% { background: transparent; }
    }

    .animate-slide-in {
        animation: slideIn 0.3s ease;
    }

    .notification {
        position: fixed;
        right: 20px;
        top: 100px;
        padding: 15px 20px;
        background: var(--bg-card);
        border-radius: 8px;
        display: flex;
        gap: 10px;
        align-items: center;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        min-width: 300px;
        max-width: 500px;
    }

    .notification.fade-out {
        animation: fadeOut 0.3s ease;
    }

    @keyframes fadeOut {
        to { opacity: 0; transform: translateX(100%); }
    }

    #ws-status-indicator {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        z-index: 10000;
        transition: background-color 0.3s ease;
    }
`;
document.head.appendChild(style);