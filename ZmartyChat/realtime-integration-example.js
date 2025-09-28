/**
 * Real-time Integration Example
 * Demonstrates how to integrate real-time notifications with ZmartyChat
 */

// Initialize real-time notifications when user is authenticated
async function initializeRealtimeNotifications(userId) {
    // Request notification permission
    const hasPermission = await RealtimeNotificationsClient.requestNotificationPermission();
    if (hasPermission) {
        console.log('✅ Browser notifications enabled');
    } else {
        console.log('⚠️ Browser notifications disabled');
    }

    // Create notifications client
    const notificationsClient = new RealtimeNotificationsClient(userId, 'ws://localhost:8903');
    
    // Connection event handlers
    notificationsClient.onConnection('connected', () => {
        console.log('🔌 Real-time notifications connected');
        showNotificationToast('Real-time notifications connected', 'success');
    });
    
    notificationsClient.onConnection('disconnected', () => {
        console.log('🔌 Real-time notifications disconnected');
        showNotificationToast('Real-time notifications disconnected', 'warning');
    });
    
    notificationsClient.onConnection('error', (error) => {
        console.error('❌ Real-time notifications error:', error);
        showNotificationToast('Real-time notifications error', 'error');
    });
    
    // Notification type handlers
    notificationsClient.onNotification('trading_signal', (notification) => {
        console.log('📈 Trading signal received:', notification);
        handleTradingSignal(notification);
    });
    
    notificationsClient.onNotification('portfolio_change', (notification) => {
        console.log('💼 Portfolio change received:', notification);
        handlePortfolioChange(notification);
    });
    
    notificationsClient.onNotification('alert_triggered', (notification) => {
        console.log('🚨 Alert triggered:', notification);
        handleAlertTriggered(notification);
    });
    
    notificationsClient.onNotification('engagement_update', (notification) => {
        console.log('📊 Engagement update received:', notification);
        handleEngagementUpdate(notification);
    });
    
    notificationsClient.onNotification('user_update', (notification) => {
        console.log('👤 User update received:', notification);
        handleUserUpdate(notification);
    });
    
    notificationsClient.onNotification('performance_update', (notification) => {
        console.log('📈 Performance update received:', notification);
        handlePerformanceUpdate(notification);
    });
    
    notificationsClient.onNotification('system_event', (notification) => {
        console.log('⚙️ System event received:', notification);
        handleSystemEvent(notification);
    });
    
    // General notification handler
    notificationsClient.onNotification('*', (notification) => {
        console.log('📨 General notification received:', notification);
        updateNotificationBadge();
    });
    
    // Connect to the server
    await notificationsClient.connect();
    
    // Store client globally for access
    window.notificationsClient = notificationsClient;
    
    return notificationsClient;
}

// Trading signal handler
function handleTradingSignal(notification) {
    const { symbol, pnl, trade_id } = notification.data;
    
    // Update trading dashboard
    updateTradingDashboard(symbol, pnl);
    
    // Show success/error toast based on P&L
    const toastType = pnl >= 0 ? 'success' : 'error';
    const message = `Trade executed for ${symbol}: ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}`;
    showNotificationToast(message, toastType);
    
    // Update portfolio if visible
    if (document.getElementById('portfolio-section')) {
        refreshPortfolio();
    }
}

// Portfolio change handler
function handlePortfolioChange(notification) {
    const { total_value, portfolio_id } = notification.data;
    
    // Update portfolio display
    updatePortfolioValue(total_value);
    
    // Show portfolio update toast
    showNotificationToast(`Portfolio updated: $${total_value.toFixed(2)}`, 'info');
    
    // Refresh portfolio charts if visible
    if (document.getElementById('portfolio-chart')) {
        refreshPortfolioChart();
    }
}

// Alert triggered handler
function handleAlertTriggered(notification) {
    const { symbol, alert_type, alert_id } = notification.data;
    
    // Show alert notification
    showAlertNotification(symbol, alert_type, notification.message);
    
    // Update alerts list
    updateAlertsList(alert_id, 'triggered');
    
    // Play alert sound if enabled
    if (localStorage.getItem('alertSoundEnabled') === 'true') {
        playAlertSound();
    }
}

// Engagement update handler
function handleEngagementUpdate(notification) {
    const { old_score, new_score } = notification.data;
    
    // Update engagement display
    updateEngagementScore(new_score);
    
    // Show engagement change toast
    const change = new_score - old_score;
    const changeText = change > 0 ? `+${change.toFixed(2)}` : change.toFixed(2);
    showNotificationToast(`Engagement score: ${changeText}`, 'info');
    
    // Update progress bar
    updateEngagementProgress(new_score);
}

// User update handler
function handleUserUpdate(notification) {
    // Refresh user profile data
    refreshUserProfile();
    
    // Show user update toast
    showNotificationToast('Profile updated', 'info');
}

// Performance update handler
function handlePerformanceUpdate(notification) {
    // Update performance metrics
    updatePerformanceMetrics(notification.data);
    
    // Show performance update toast
    showNotificationToast('Performance metrics updated', 'info');
    
    // Refresh performance charts
    if (document.getElementById('performance-chart')) {
        refreshPerformanceChart();
    }
}

// System event handler
function handleSystemEvent(notification) {
    // Show system event toast
    showNotificationToast(notification.message, 'info');
    
    // Log system event
    console.log('System event:', notification);
}

// UI Update Functions
function showNotificationToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `notification-toast notification-toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add to page
    let toastContainer = document.getElementById('notification-toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'notification-toast-container';
        toastContainer.className = 'notification-toast-container';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function showAlertNotification(symbol, alertType, message) {
    // Create alert notification
    const alert = document.createElement('div');
    alert.className = 'alert-notification';
    alert.innerHTML = `
        <div class="alert-header">
            <span class="alert-icon">🚨</span>
            <span class="alert-title">Alert Triggered</span>
        </div>
        <div class="alert-content">
            <div class="alert-symbol">${symbol}</div>
            <div class="alert-type">${alertType}</div>
            <div class="alert-message">${message}</div>
        </div>
        <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Add to page
    let alertContainer = document.getElementById('alert-notification-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-notification-container';
        alertContainer.className = 'alert-notification-container';
        document.body.appendChild(alertContainer);
    }
    
    alertContainer.appendChild(alert);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 10000);
}

function updateNotificationBadge() {
    const badge = document.getElementById('notification-badge');
    if (badge) {
        const currentCount = parseInt(badge.textContent) || 0;
        badge.textContent = currentCount + 1;
        badge.style.display = 'block';
    }
}

function updateTradingDashboard(symbol, pnl) {
    // Update trading dashboard with new trade
    const dashboard = document.getElementById('trading-dashboard');
    if (dashboard) {
        // Add trade to recent trades list
        const recentTrades = dashboard.querySelector('.recent-trades');
        if (recentTrades) {
            const tradeElement = document.createElement('div');
            tradeElement.className = `trade-item ${pnl >= 0 ? 'profit' : 'loss'}`;
            tradeElement.innerHTML = `
                <span class="trade-symbol">${symbol}</span>
                <span class="trade-pnl">${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}</span>
                <span class="trade-time">${new Date().toLocaleTimeString()}</span>
            `;
            recentTrades.insertBefore(tradeElement, recentTrades.firstChild);
            
            // Keep only last 10 trades
            while (recentTrades.children.length > 10) {
                recentTrades.removeChild(recentTrades.lastChild);
            }
        }
    }
}

function updatePortfolioValue(totalValue) {
    const portfolioValue = document.getElementById('portfolio-total-value');
    if (portfolioValue) {
        portfolioValue.textContent = `$${totalValue.toFixed(2)}`;
    }
}

function updateEngagementScore(score) {
    const engagementScore = document.getElementById('engagement-score');
    if (engagementScore) {
        engagementScore.textContent = score.toFixed(2);
    }
}

function updateEngagementProgress(score) {
    const progressBar = document.getElementById('engagement-progress');
    if (progressBar) {
        progressBar.style.width = `${(score * 100)}%`;
    }
}

function updateAlertsList(alertId, status) {
    const alertsList = document.getElementById('alerts-list');
    if (alertsList) {
        const alertItem = alertsList.querySelector(`[data-alert-id="${alertId}"]`);
        if (alertItem) {
            alertItem.classList.add('triggered');
            alertItem.querySelector('.alert-status').textContent = status;
        }
    }
}

function refreshPortfolio() {
    // Trigger portfolio refresh
    if (typeof refreshPortfolioData === 'function') {
        refreshPortfolioData();
    }
}

function refreshPortfolioChart() {
    // Trigger portfolio chart refresh
    if (typeof updatePortfolioChart === 'function') {
        updatePortfolioChart();
    }
}

function refreshUserProfile() {
    // Trigger user profile refresh
    if (typeof loadUserProfile === 'function') {
        loadUserProfile();
    }
}

function refreshPerformanceChart() {
    // Trigger performance chart refresh
    if (typeof updatePerformanceChart === 'function') {
        updatePerformanceChart();
    }
}

function updatePerformanceMetrics(data) {
    // Update performance metrics display
    Object.keys(data).forEach(key => {
        const element = document.getElementById(`performance-${key}`);
        if (element) {
            element.textContent = data[key];
        }
    });
}

function playAlertSound() {
    // Play alert sound
    const audio = new Audio('/sounds/alert.mp3');
    audio.play().catch(e => console.log('Could not play alert sound:', e));
}

// Initialize when user is authenticated
document.addEventListener('DOMContentLoaded', async () => {
    // Check if user is authenticated
    const userResult = await ZmartyService.auth.getCurrentUser();
    if (userResult.success && userResult.data) {
        const userId = userResult.data.id;
        console.log('👤 User authenticated, initializing real-time notifications for:', userId);
        
        // Initialize real-time notifications
        await initializeRealtimeNotifications(userId);
    } else {
        console.log('⚠️ User not authenticated, skipping real-time notifications');
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.notificationsClient) {
        window.notificationsClient.disconnect();
    }
});

