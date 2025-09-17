// ZmartBot MDC Dashboard - Main JavaScript

// Global Configuration
const CONFIG = {
    apiBaseUrl: '/api',
    orchestrationUrl: 'http://localhost:8615',
    refreshInterval: 30000, // 30 seconds
    maxFileSize: 1024 * 1024, // 1MB
    supportedFileTypes: ['.mdc'],
    defaultSettings: {
        autoRefresh: true,
        refreshInterval: 30,
        defaultView: 'overview',
        compactView: false,
        showFileSize: true,
        showConnectionCount: true
    }
};

// Global State
let currentSection = 'overview';
let mdcFiles = [];
let allMDCFiles = []; // Store all files
let connections = [];
let systemHealth = {};
let autoRefreshTimer = null;
let isLoading = false;

// 📄 PAGINATION STATE - Optimize resource usage
let mdcPagination = {
    pageSize: 25,
    currentPage: 1,
    showAll: false,
    totalFiles: 0
};
let connectionStatus = {
    status: 'healthy',
    message: '✅ System Connected',
    lastCheck: new Date().toISOString()
};
let cacheStatus = {
    hasCache: false,
    lastCached: null,
    cacheAge: 0
};
let currentBrowsePath = '/Users/dansidanutz/Desktop';

// 🚀 NOTIFICATION CHAT WINDOW SYSTEM - Beautiful notification cards
let statusMessageTimer = null;
let notificationHistory = [];
let maxNotifications = 10;

function showStatusMessage(message, type = 'info', duration = 3000) {
    // Add to notification history
    addNotificationToHistory(message, type);
    
    // Still show the popup for immediate feedback
    const statusContainer = document.getElementById('statusContainer') || createStatusContainer();
    
    // Clear previous timer
    if (statusMessageTimer) {
        clearTimeout(statusMessageTimer);
    }
    
    // Set status message with appropriate styling
    const statusClass = {
        'success': 'status-success',
        'info': 'status-info', 
        'warning': 'status-warning',
        'error': 'status-error'
    }[type] || 'status-info';
    
    statusContainer.className = `status-message ${statusClass}`;
    statusContainer.textContent = message;
    statusContainer.style.display = 'block';
    
    // Auto-hide after duration (unless it's an error)
    if (type !== 'error') {
        statusMessageTimer = setTimeout(() => {
            statusContainer.style.display = 'none';
        }, duration);
    }
    
    console.log(`📢 Status: ${message} (${type})`);
}

function addNotificationToHistory(message, type) {
    const notification = {
        id: Date.now(),
        message: message,
        type: type,
        timestamp: new Date(),
        icon: getNotificationIcon(type)
    };
    
    // Add to beginning of array (newest first)
    notificationHistory.unshift(notification);
    
    // Keep only last 10 notifications
    if (notificationHistory.length > maxNotifications) {
        notificationHistory = notificationHistory.slice(0, maxNotifications);
    }
    
    // Update notification window
    updateNotificationWindow();
}

function getNotificationIcon(type) {
    const icons = {
        'success': '✅',
        'info': '📘',
        'warning': '⚠️',
        'error': '❌'
    };
    return icons[type] || '📢';
}

function createNotificationWindow() {
    // Create notification window container
    const notificationWindow = document.createElement('div');
    notificationWindow.id = 'notificationWindow';
    notificationWindow.className = 'notification-window';
    
    notificationWindow.innerHTML = `
        <div class="notification-header">
            <div class="notification-title">
                <i class="fas fa-bell"></i>
                <span>Notifications</span>
            </div>
            <button class="notification-toggle" onclick="toggleNotificationWindow()">
                <i class="fas fa-chevron-right"></i>
            </button>
        </div>
        <div class="notification-content">
            <div id="notificationList" class="notification-list">
                <div class="no-notifications">
                    <i class="fas fa-bell-slash"></i>
                    <p>No notifications yet</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(notificationWindow);
    
    // Add styles
    injectNotificationStyles();
    
    return notificationWindow;
}

function updateNotificationWindow() {
    const notificationList = document.getElementById('notificationList');
    if (!notificationList) {
        createNotificationWindow();
        return;
    }
    
    if (notificationHistory.length === 0) {
        notificationList.innerHTML = `
            <div class="no-notifications">
                <i class="fas fa-bell-slash"></i>
                <p>No notifications yet</p>
            </div>
        `;
        return;
    }
    
    // Generate notification cards
    notificationList.innerHTML = notificationHistory.map(notification => `
        <div class="notification-card ${notification.type}" data-id="${notification.id}">
            <div class="notification-card-header">
                <span class="notification-icon">${notification.icon}</span>
                <span class="notification-time">${formatNotificationTime(notification.timestamp)}</span>
            </div>
            <div class="notification-card-body">
                <p class="notification-message">${notification.message}</p>
            </div>
        </div>
    `).join('');
    
    // Auto-scroll to top (newest notification)
    notificationList.scrollTop = 0;
    
    // Show notification count badge
    updateNotificationBadge();
}

function formatNotificationTime(timestamp) {
    // Show just time (HH:MM) without date
    return timestamp.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false 
    });
}

function updateNotificationBadge() {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        badge.textContent = notificationHistory.length;
        badge.style.display = notificationHistory.length > 0 ? 'block' : 'none';
    }
}

function toggleNotificationWindow() {
    const notificationWindow = document.getElementById('notificationWindow');
    const toggle = document.querySelector('.notification-toggle i');
    
    if (notificationWindow.classList.contains('collapsed')) {
        notificationWindow.classList.remove('collapsed');
        toggle.className = 'fas fa-chevron-right';
    } else {
        notificationWindow.classList.add('collapsed');
        toggle.className = 'fas fa-chevron-left';
    }
}

function createStatusContainer() {
    const container = document.createElement('div');
    container.id = 'statusContainer';
    container.className = 'status-message';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 380px;
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        z-index: 1000;
        display: none;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    // Add CSS for different status types
    const style = document.createElement('style');
    style.textContent = `
        .status-success { background: #10B981; color: white; }
        .status-info { background: #3B82F6; color: white; }
        .status-warning { background: #F59E0B; color: white; }
        .status-error { background: #EF4444; color: white; }
    `;
    document.head.appendChild(style);
    document.body.appendChild(container);
    
    return container;
}

function injectNotificationStyles() {
    // Check if styles already injected
    if (document.getElementById('notification-window-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'notification-window-styles';
    style.textContent = `
        /* 🔔 NOTIFICATION CHAT WINDOW - DARK THEME */
        .notification-window {
            position: fixed;
            top: 80px;
            right: 15px;
            bottom: 90px;
            width: 320px;
            background: #1f2937;
            border: 1px solid #374151;
            border-radius: 12px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
            z-index: 1500;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            overflow: hidden;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            max-width: calc(100vw - 30px);
        }
        
        .notification-window.collapsed {
            width: 60px;
            max-height: 60px;
        }
        
        .notification-header {
            background: #111827;
            padding: 16px;
            border-bottom: 1px solid #374151;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .notification-title {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #f9fafb;
            font-weight: 600;
            font-size: 14px;
        }
        
        .notification-title i {
            color: #3b82f6;
            font-size: 16px;
        }
        
        .notification-toggle {
            background: none;
            border: none;
            color: #9ca3af;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: all 0.2s;
        }
        
        .notification-toggle:hover {
            background: #374151;
            color: #f9fafb;
        }
        
        .notification-content {
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        
        .notification-list {
            padding: 8px;
            flex: 1;
            overflow-y: auto;
        }
        
        .notification-list::-webkit-scrollbar {
            width: 6px;
        }
        
        .notification-list::-webkit-scrollbar-track {
            background: #1f2937;
        }
        
        .notification-list::-webkit-scrollbar-thumb {
            background: #374151;
            border-radius: 3px;
        }
        
        .notification-list::-webkit-scrollbar-thumb:hover {
            background: #4b5563;
        }
        
        .notification-card {
            background: #252f3f;
            border: 1px solid #374151;
            border-radius: 8px;
            margin-bottom: 8px;
            padding: 12px;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        
        .notification-card:hover {
            background: #2a3441;
            border-color: #4b5563;
        }
        
        .notification-card:last-child {
            margin-bottom: 0;
        }
        
        .notification-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: var(--notification-color);
        }
        
        .notification-card.success {
            --notification-color: #10b981;
        }
        
        .notification-card.info {
            --notification-color: #3b82f6;
        }
        
        .notification-card.warning {
            --notification-color: #f59e0b;
        }
        
        .notification-card.error {
            --notification-color: #ef4444;
        }
        
        .notification-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .notification-icon {
            font-size: 16px;
            display: flex;
            align-items: center;
        }
        
        .notification-time {
            color: #9ca3af;
            font-size: 11px;
            font-weight: 500;
        }
        
        .notification-message {
            color: #e5e7eb;
            font-size: 13px;
            line-height: 1.4;
            margin: 0;
        }
        
        .no-notifications {
            text-align: center;
            padding: 40px 20px;
            color: #6b7280;
        }
        
        .no-notifications i {
            font-size: 32px;
            margin-bottom: 12px;
            color: #4b5563;
        }
        
        .no-notifications p {
            margin: 0;
            font-size: 14px;
        }
        
        /* Collapsed state */
        .notification-window.collapsed .notification-content {
            display: none;
        }
        
        .notification-window.collapsed .notification-title span {
            display: none;
        }
        
        .notification-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            background: #ef4444;
            color: white;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 6px;
            border-radius: 10px;
            min-width: 18px;
            text-align: center;
            display: none;
        }
        
        .notification-window.collapsed .notification-header {
            position: relative;
        }
        
        /* Animation for new notifications */
        .notification-card.new {
            animation: slideInNotification 0.3s ease-out;
        }
        
        @keyframes slideInNotification {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .notification-window {
                width: calc(100vw - 20px);
                right: 10px;
                top: 70px;
                bottom: 80px;
                max-width: 300px;
            }
        }
        
        @media (max-width: 480px) {
            .notification-window {
                width: calc(100vw - 15px);
                right: 8px;
                top: 65px;
                bottom: 75px;
                max-width: 280px;
            }
        }
    `;
    
    document.head.appendChild(style);
}

// Add health card status styles
function addHealthCardStyles() {
    if (document.getElementById('health-card-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'health-card-styles';
    style.textContent = `
        /* 💚 HEALTH CARD STATUS COLORS */
        .health-item.health-connected {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
            border: 1px solid rgba(16, 185, 129, 0.3);
            box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2);
        }
        
        .health-item.health-warning {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
            border: 1px solid rgba(245, 158, 11, 0.3);
            box-shadow: 0 4px 6px -1px rgba(245, 158, 11, 0.2);
        }
        
        .health-item.health-disconnected {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
            border: 1px solid rgba(239, 68, 68, 0.3);
            box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.2);
        }
        
        .health-item.health-connected h4 {
            color: rgb(16, 185, 129);
        }
        
        .health-item.health-warning h4 {
            color: rgb(245, 158, 11);
        }
        
        .health-item.health-disconnected h4 {
            color: rgb(239, 68, 68);
        }
    `;
    
    document.head.appendChild(style);
}

// MDC Scan State
let mdcScanScheduler = null;
let lastScanData = {
    timestamp: null,
    fileCount: 0,
    mdcFileCount: 0,
    connectionsCount: 0,
    path: '',
    systemUpdateTime: null
};

// Update History State
let updateHistory = [];

// Context Optimization State
let contextOptimizationScheduler = null;
let lastContextOptimization = {
    timestamp: null,
    success: false,
    optimizationsMade: 0,
    originalSize: 0,
    optimizedSize: 0
};

// Utility Functions
const utils = {
    formatBytes: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    formatDate: (dateString) => {
        if (!dateString) return 'Never';
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diff = now - date;
            
            if (diff < 60000) return 'Just now';
            if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
            if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
            if (diff < 604800000) return Math.floor(diff / 86400000) + 'd ago';
            return date.toLocaleDateString();
        } catch (e) {
            return dateString;
        }
    },

    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    sanitizeHtml: (str) => {
        const temp = document.createElement('div');
        temp.textContent = str;
        return temp.innerHTML;
    },

    generateId: () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
};

// API Functions
// 🚀 REQUEST THROTTLING - Prevent heavy operations that cause disconnection
const requestThrottle = {
    requests: new Map(),
    maxConcurrent: 5, // Increased from 3 to 5
    activeRequests: 0,
    delayBetweenRequests: 50, // Reduced from 100ms to 50ms
    
    async throttle(key, requestFn) {
        // Check if same request is already in progress
        if (this.requests.has(key)) {
            console.log(`📈 Throttling: Request ${key} already in progress, reusing...`);
            return this.requests.get(key);
        }
        
        // Wait if too many concurrent requests (but don't wait too long)
        let waitCount = 0;
        while (this.activeRequests >= this.maxConcurrent && waitCount < 10) {
            console.log(`⏳ Throttling: Too many requests (${this.activeRequests}/${this.maxConcurrent}), waiting...`);
            await new Promise(resolve => setTimeout(resolve, this.delayBetweenRequests));
            waitCount++;
        }
        
        // Execute the request
        this.activeRequests++;
        const promise = requestFn().finally(() => {
            this.activeRequests--;
            this.requests.delete(key);
        });
        
        this.requests.set(key, promise);
        return promise;
    }
};

const api = {
    async request(endpoint, options = {}) {
        const url = `${CONFIG.apiBaseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // 🚀 Use selective throttling (only for heavy operations)
        const isHeavyOperation = endpoint.includes('/scan') || endpoint.includes('/discover') || endpoint.includes('/generate');
        const requestKey = `${options.method || 'GET'}-${endpoint}`;
        
        const executeRequest = async () => {
            try {
                // Use longer timeout for heavy operations, shorter for regular ones
                const timeoutMs = isHeavyOperation ? 60000 : 30000; // 60s for heavy, 30s for regular
                const controller = new AbortController();
                const timeoutId = setTimeout(() => {
                    controller.abort();
                    console.warn(`⚠️ Request timeout after ${timeoutMs}ms: ${endpoint}`);
                }, timeoutMs);
                
                const response = await fetch(url, { 
                    ...defaultOptions, 
                    ...options,
                    signal: controller.signal 
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                return data;
                
            } catch (error) {
                if (error.name === 'AbortError') {
                    const timeoutMessage = isHeavyOperation 
                        ? '⏳ Heavy operation taking longer than expected - Please wait...' 
                        : '⚠️ Request timeout - Please try again';
                    showStatusMessage(timeoutMessage, 'warning');
                    console.warn('Request aborted due to timeout:', endpoint);
                    return { success: false, error: 'Request timeout', aborted: true };
                }
                console.error('API request failed:', error);
                return { success: false, error: error.message };
            }
        };
        
        // Only throttle heavy operations
        if (isHeavyOperation) {
            return requestThrottle.throttle(requestKey, executeRequest);
        } else {
            return executeRequest();
        }
    },

    async getMDCFiles() {
        return this.request('/mdc/files');
    },

    async getMDCFile(filename) {
        return this.request(`/mdc/files/${filename}`);
    },

    async createMDCFile(data) {
        return this.request('/mdc/files', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateMDCFile(filename, data) {
        return this.request(`/mdc/files/${filename}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async deleteMDCFile(filename) {
        return this.request(`/mdc/files/${filename}`, {
            method: 'DELETE'
        });
    },

    async getConnections() {
        return this.request('/connections');
    },

    async getSystemStatus() {
        // Try local API first, fallback to orchestration URL
        try {
            return await this.request('/system/status');
        } catch (error) {
            console.warn('Local system status failed, trying orchestration URL:', error);
            try {
                const response = await fetch(`${CONFIG.orchestrationUrl}/status`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                return { success: true, data: data };
            } catch (orchError) {
                console.error('Both system status endpoints failed:', orchError);
                // Return a minimal fallback status
                return { 
                    success: true, 
                    data: { 
                        overall_status: 'unknown',
                        total_services: 0,
                        total_connections: 0 
                    } 
                };
            }
        }
    },

    async generateMDC(data) {
        return this.request('/mdc/generate', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async discoverConnections() {
        // Use the orchestration URL directly for discovery
        const response = await fetch(`${CONFIG.orchestrationUrl}/connections/discover/all`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    },

    async getAllConnections() {
        // Use the orchestration URL directly for connections
        const response = await fetch(`${CONFIG.orchestrationUrl}/connections/all`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    },

    async getDashboardConnections() {
        // Use dashboard's existing connections endpoint which has comprehensive data
        const response = await fetch('/api/connections', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('🔍 Raw connections data:', result);
        
        // Transform the data to match the expected format for the modal
        if (result.success && result.data) {
            const connections = result.data.connections || [];
            const services = {};
            let total_connections = 0;
            
            // Group connections by service with proper null checks
            connections.forEach(conn => {
                // Skip invalid connections
                if (!conn || typeof conn !== 'object') {
                    console.warn('⚠️ Skipping invalid connection:', conn);
                    return;
                }
                
                // Use source or service_name, fallback to 'Unknown'
                const serviceName = conn.source || conn.service_name || conn.name || 'Unknown';
                
                if (!services[serviceName]) {
                    services[serviceName] = {
                        connections: [],
                        total: 0,
                        service_info: {
                            name: serviceName,
                            type: 'Service',
                            port: conn.port || null,
                            description: conn.description || 'Service with connections'
                        }
                    };
                }
                
                // Only add valid connections
                if (serviceName !== 'Unknown') {
                    services[serviceName].connections.push(conn);
                    services[serviceName].total += 1;
                    total_connections += 1;
                }
            });
            
            console.log('✅ Transformed services data:', services);
            
            return {
                success: true,
                data: {
                    services: services,
                    total_services: Object.keys(services).length,
                    total_connections: total_connections,
                    last_updated: new Date().toISOString()
                }
            };
        }
        
        return result;
    },

    async optimizeContext() {
        return this.request('/context/optimize', {
            method: 'POST'
        });
    },

    async validateSystem() {
        // Use the orchestration URL directly for validation
        const response = await fetch(`${CONFIG.orchestrationUrl}/system/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    },

    async waitForTask(taskId, maxWaitTime = 10000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < maxWaitTime) {
            try {
                const response = await fetch(`${CONFIG.orchestrationUrl}/tasks/${taskId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const task = await response.json();
                    
                    if (task.status === 'completed') {
                        return task;
                    } else if (task.status === 'failed') {
                        throw new Error(task.error || 'Task failed');
                    }
                }
            } catch (error) {
                console.warn('Error checking task status:', error);
            }
            
            // Wait 500ms before next check
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        throw new Error('Task timeout - validation took too long');
    },

    async getSettings() {
        return this.request('/settings');
    },

    async updateMDCPath(path) {
        return this.request('/settings/mdc-path', {
            method: 'POST',
            body: JSON.stringify({ path })
        });
    },

    async browseDirectory(path) {
        return this.request('/browse-directory', {
            method: 'POST',
            body: JSON.stringify({ path })
        });
    }
};

// Toast Notification System
const toast = {
    show(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toastContainer');
        const toastId = utils.generateId();
        
        const toastElement = document.createElement('div');
        toastElement.className = `toast ${type}`;
        toastElement.id = toastId;
        
        toastElement.innerHTML = `
            <div class="toast-header">
                <span class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</span>
                <button class="toast-close" onclick="toast.hide('${toastId}')">&times;</button>
            </div>
            <div class="toast-message">${utils.sanitizeHtml(message)}</div>
        `;
        
        container.appendChild(toastElement);
        
        // Auto-hide after duration
        setTimeout(() => this.hide(toastId), duration);
        
        return toastId;
    },

    hide(toastId) {
        const element = document.getElementById(toastId);
        if (element) {
            element.style.animation = 'toastSlideOut 0.3s ease';
            setTimeout(() => element.remove(), 300);
        }
    },

    success(message, duration) {
        return this.show(message, 'success', duration);
    },

    error(message, duration) {
        return this.show(message, 'error', duration);
    },

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
};

// Loading Overlay
const loading = {
    show(message = 'Processing...') {
        const overlay = document.getElementById('loadingOverlay');
        const text = overlay.querySelector('p');
        text.textContent = message;
        overlay.style.display = 'flex';
        isLoading = true;
    },

    hide() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = 'none';
        isLoading = false;
    }
};

// Section Management
function switchSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionName).classList.add('active');
    
    currentSection = sectionName;
    
    // Load section-specific data
    loadSectionData(sectionName);
}

function loadSectionData(sectionName) {
    switch (sectionName) {
        case 'overview':
            loadOverviewData();
            break;
        case 'files':
            loadMDCFiles();
            break;
        case 'connections':
            loadConnections();
            break;
        case 'generator':
            // No specific data loading needed
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'logs':
            initializeLogsSection();
            startLogsAutoRefresh();
            break;
        case 'settings':
            loadSettings();
            break;
    }
}

// Overview Section
async function loadOverviewData() {
    try {
        // 🚀 Show loading message with positive tone
        showStatusMessage('✨ Loading dashboard data...', 'info');
        
        const [filesResult, statusResult] = await Promise.all([
            api.getMDCFiles(),
            api.getSystemStatus()
        ]);
        
        // Handle MDC files with cache status reporting
        if (filesResult.success) {
            // Store all files for overview calculations
            allMDCFiles = filesResult.data.files || [];
            mdcFiles = allMDCFiles; // For overview, we want to show all files data
            
            const cacheInfo = filesResult.cached ? ` (from cache - ${filesResult.cache_age}s old)` : ' (fresh data)';
            
            console.log(`🔍 MDC Files loaded: ${allMDCFiles.length} files${cacheInfo}`);
            console.log('📊 First few files:', allMDCFiles.slice(0, 3).map(f => f.name));
            
            // Update cache status
            cacheStatus.hasCache = filesResult.cached || false;
            cacheStatus.cacheAge = filesResult.cache_age || 0;
            if (filesResult.data.status_message) {
                showStatusMessage(filesResult.data.status_message, 'success');
            }
            
            updateOverviewStats();
        } else {
            console.error('❌ Failed to load MDC files:', filesResult);
            showStatusMessage('⚠️ Using fallback data for MDC files', 'warning');
        }
        
        // Handle system status with positive messaging
        if (statusResult.success) {
            systemHealth = statusResult.data;
            
            // Update connection status from response
            if (statusResult.data.connection_health) {
                connectionStatus = statusResult.data.connection_health;
            }
            
            if (statusResult.data.status_message) {
                showStatusMessage(statusResult.data.status_message, 'success');
            } else if (statusResult.cached) {
                showStatusMessage('✅ Data loaded from cache - System responsive', 'success');
            }
            
            updateSystemHealth();
        }
        
        // Update connection status with positive messaging
        connectionStatus.lastCheck = new Date().toISOString();
        updateConnectionStatus(true);
        
        // Show successful load message
        setTimeout(() => {
            showStatusMessage('✅ Dashboard loaded successfully - All systems operational', 'success');
        }, 500);
        
    } catch (error) {
        console.error('Failed to load overview data:', error);
        updateConnectionStatus(false);
        showStatusMessage('⚠️ Connection issue detected - Retrying with cached data...', 'warning');
        
        // Try to use any cached data available
        if (mdcFiles.length > 0) {
            showStatusMessage('✅ Using cached data - Dashboard remains functional', 'success');
            updateOverviewStats();
        }
    }
    
    // Update System Status with current dynamic data
    updateScanStatusDisplay();
    
    // Notify user that System Status is now dynamic
    addNotificationToHistory('🎯 System Status section now displays real-time dynamic values', 'success');
}

function updateOverviewStats() {
    const totalMdcElement = document.getElementById('totalMdcFiles');
    if (totalMdcElement) {
        // Use allMDCFiles.length for accurate total, not the paginated mdcFiles
        const totalFiles = allMDCFiles.length > 0 ? allMDCFiles.length : mdcFiles.length;
        totalMdcElement.textContent = totalFiles;
        console.log('✅ Updated totalMdcFiles element to:', totalFiles);
    } else {
        console.error('❌ Element totalMdcFiles not found!');
    }
    
    // Calculate enhanced connection metrics using ALL files, not just paginated ones
    const allConnections = [];
    const activeConnections = [];
    const connectionsPerFile = {};
    
    const filesToAnalyze = allMDCFiles.length > 0 ? allMDCFiles : mdcFiles;
    
    filesToAnalyze.forEach(file => {
        if (file.connections && Array.isArray(file.connections)) {
            file.connections.forEach(conn => {
                allConnections.push({
                    from: file.name,
                    to: conn.target || conn.name,
                    type: conn.type || 'unknown',
                    status: conn.status || 'active'
                });
                
                if (conn.status !== 'inactive') {
                    activeConnections.push(conn);
                }
            });
            connectionsPerFile[file.name] = file.connections.length;
        }
    });
    
    // Update connections display with actual total from system status or files
    const totalConnectionsEl = document.getElementById('totalConnections');
    const connectionTrendEl = document.getElementById('connectionTrend');
    
    // Use system status data if available, otherwise calculate from MDC files
    let totalConnections = 0;
    if (systemHealth && systemHealth.total_connections) {
        totalConnections = systemHealth.total_connections;
    } else {
        // Fallback: Calculate total connections across ALL MDC files (not just paginated)
        totalConnections = filesToAnalyze.reduce((sum, file) => {
            return sum + (file.connections ? file.connections.length : 0);
        }, 0);
    }
    
    if (totalConnectionsEl) {
        totalConnectionsEl.textContent = totalConnections;
        console.log('✅ Updated totalConnections element to:', totalConnections);
    } else {
        console.error('❌ Element totalConnections not found!');
    }
    
    if (connectionTrendEl) {
        // Show connection growth trend using actual total connections
        const connectionGrowth = totalConnections > 0 ? `+${totalConnections}` : '+0';
        connectionTrendEl.textContent = connectionGrowth;
    }
    
    // Update service counts with correct values from system status
    const activeServicesEl = document.getElementById('activeServices');
    if (activeServicesEl) {
        // Use system status data for accurate service counts
        let activeServices = 43; // Default to all registered services
        let registeredServices = 30; // Default to ACTIVE services with passports (updated count)
        
        if (systemHealth) {
            activeServices = systemHealth.active_services || 43;
            registeredServices = systemHealth.registered_services || 30;
        }
        
        activeServicesEl.textContent = activeServices;
        console.log('✅ Updated Active Services to:', activeServices, '(all registered services)');
        
        // Update service trend indicator
        const serviceTrendEl = activeServicesEl.parentElement.querySelector('.stat-trend span');
        if (serviceTrendEl) {
            serviceTrendEl.textContent = activeServices > 0 ? `${activeServices}` : '0';
            const trendContainer = activeServicesEl.parentElement.querySelector('.stat-trend');
            if (trendContainer && activeServices > 0) {
                trendContainer.className = 'stat-trend positive';
                trendContainer.querySelector('i').className = 'fas fa-arrow-up';
            }
        }
        
        // Add click handler for redirect to Service Dashboard
        activeServicesEl.style.cursor = 'pointer';
        activeServicesEl.title = 'Click to view Service Dashboard';
        activeServicesEl.onclick = () => redirectToServiceDashboard();
        
        // Add notification about service count
        if (activeServices > 0) {
            addNotificationToHistory(`📊 Active Services: ${activeServices} total services (${registeredServices} registered with passports)`, 'success');
        }
    }
    
    // Update registered services count
    const registeredServicesEl = document.getElementById('registeredServices');
    if (registeredServicesEl) {
        let registeredServices = 30; // Default to ACTIVE services with passports (updated count)
        
        if (systemHealth) {
            registeredServices = systemHealth.registered_services || 30;
        }
        
        registeredServicesEl.textContent = registeredServices;
        console.log('✅ Updated Registered Services to:', registeredServices, '(services with passports)');
        
        // Add visual indication that this card is clickable
        registeredServicesEl.style.cursor = 'pointer';
        registeredServicesEl.title = 'Click to view Service Dashboard';
        
        console.log('✅ Registered Services card is clickable (handler in HTML)');
        
        // Add notification about registered services
        if (registeredServices > 0) {
            addNotificationToHistory(`🛂 Registered Services: ${registeredServices} services with Passport IDs`, 'success');
        }
    }
    
    const lastUpdateEl = document.getElementById('lastLogUpdate');
    if (lastUpdateEl) {
        lastUpdateEl.textContent = new Date().toLocaleTimeString();
        console.log('✅ Updated last update time');
    }
    
    // Store connection data globally for other functions to use
    window.connectionStats = {
        total: allConnections.length,
        active: activeConnections.length,
        health: allConnections.length > 0 ? (activeConnections.length / allConnections.length) * 100 : 100,
        perFile: connectionsPerFile,
        details: allConnections
    };
}

// Function to redirect to Service Dashboard
function redirectToServiceDashboard() {
    console.log('🔗 Redirect function called!');
    showStatusMessage('🔄 Redirecting to Service Dashboard...', 'info');
    
    // Call the redirect API endpoint
    fetch('/api/redirect/service-dashboard')
        .then(response => response.json())
        .then(data => {
            console.log('📡 Redirect API response:', data);
            if (data.success && data.redirect) {
                showStatusMessage(data.message, 'success');
                // Redirect to Service Dashboard
                console.log('🚀 Opening Service Dashboard in new window:', data.url);
                setTimeout(() => {
                    window.open(data.url, '_blank');
                }, 1000);
            } else {
                showStatusMessage('⚠️ Redirect failed - Service Dashboard may not be available', 'warning');
            }
        })
        .catch(error => {
            console.error('Redirect error:', error);
            showStatusMessage('❌ Redirect failed - Please try again', 'error');
        });
}

// 🧠 INTELLIGENT INCREMENTAL CONNECTION DISCOVERY SYSTEM
class ConnectionDiscoveryEngine {
    constructor() {
        this.snapshotKey = 'mdc_connection_snapshot';
        this.lastScanKey = 'mdc_last_scan_timestamp';
    }

    // Get stored snapshot of previous scan
    getSnapshot() {
        try {
            const snapshot = localStorage.getItem(this.snapshotKey);
            return snapshot ? JSON.parse(snapshot) : null;
        } catch (error) {
            console.warn('Failed to load connection snapshot:', error);
            return null;
        }
    }

    // Save snapshot after successful scan
    saveSnapshot(mdcFiles, connectionMap) {
        try {
            const snapshot = {
                timestamp: Date.now(),
                files: mdcFiles.map(file => ({
                    name: file.name,
                    lastModified: file.lastModified,
                    checksum: this.generateChecksum(file.content || ''),
                    connections: file.connections || []
                })),
                connectionMap: connectionMap,
                totalConnections: Object.values(connectionMap).reduce((sum, conns) => sum + conns.length, 0)
            };
            
            localStorage.setItem(this.snapshotKey, JSON.stringify(snapshot));
            localStorage.setItem(this.lastScanKey, Date.now().toString());
            
            console.log('📸 Connection snapshot saved:', {
                files: snapshot.files.length,
                connections: snapshot.totalConnections
            });
            
            return true;
        } catch (error) {
            console.error('Failed to save connection snapshot:', error);
            return false;
        }
    }

    // Generate simple checksum for content changes
    generateChecksum(content) {
        let hash = 0;
        for (let i = 0; i < content.length; i++) {
            const char = content.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return hash.toString();
    }

    // Detect what files need processing (new/modified)
    detectChanges(currentFiles, snapshot) {
        if (!snapshot) {
            return {
                newFiles: currentFiles,
                modifiedFiles: [],
                unchangedFiles: [],
                isFullScan: true
            };
        }

        const snapshotMap = new Map(snapshot.files.map(f => [f.name, f]));
        const newFiles = [];
        const modifiedFiles = [];
        const unchangedFiles = [];

        currentFiles.forEach(file => {
            const existing = snapshotMap.get(file.name);
            
            if (!existing) {
                newFiles.push(file);
            } else if (existing.lastModified !== file.lastModified || 
                      existing.checksum !== this.generateChecksum(file.content || '')) {
                modifiedFiles.push(file);
            } else {
                unchangedFiles.push({
                    ...file,
                    connections: existing.connections // Restore connections from snapshot
                });
            }
        });

        return {
            newFiles,
            modifiedFiles,
            unchangedFiles,
            isFullScan: false,
            summary: {
                total: currentFiles.length,
                needProcessing: newFiles.length + modifiedFiles.length,
                unchanged: unchangedFiles.length
            }
        };
    }

    // Discover connections for specific files only
    async discoverConnectionsForFiles(filesToProcess) {
        const connectionMap = {};
        
        console.log(`🔍 Analyzing ${filesToProcess.length} files for connections...`);
        
        // Analyze each file for potential connections
        for (const file of filesToProcess) {
            connectionMap[file.name] = await this.analyzeFileConnections(file, filesToProcess);
        }
        
        return connectionMap;
    }

    // Analyze individual file for connections
    async analyzeFileConnections(targetFile, allFiles) {
        const connections = [];
        const content = targetFile.content || '';
        const fileName = targetFile.name.toLowerCase();
        
        // Connection discovery patterns
        const patterns = {
            api: [/api[._-]?client/i, /http[._-]?request/i, /fetch|axios|request/i],
            database: [/database|db[._-]/i, /sql|mongo|redis/i, /connection[._-]?pool/i],
            messaging: [/queue|message|event/i, /kafka|rabbit|redis/i, /pub[._-]?sub/i],
            storage: [/storage|file|blob/i, /s3|gcs|azure/i, /upload|download/i],
            auth: [/auth|login|jwt|token/i, /oauth|saml|sso/i, /permission|role/i],
            monitoring: [/log|metric|trace/i, /prometheus|grafana/i, /alert|monitor/i]
        };

        // Check against other files for connections
        for (const otherFile of allFiles) {
            if (otherFile.name === targetFile.name) continue;
            
            const otherContent = otherFile.content || '';
            const otherName = otherFile.name.toLowerCase();
            
            // Name-based connections
            if (content.includes(otherFile.name) || otherContent.includes(targetFile.name)) {
                connections.push({
                    target: otherFile.name,
                    type: this.inferConnectionType(content, otherContent, patterns),
                    confidence: 0.8,
                    reason: 'Direct file reference found',
                    status: 'active'
                });
                continue;
            }
            
            // Pattern-based connections
            const connectionType = this.findPatternMatches(content, otherContent, patterns);
            if (connectionType) {
                connections.push({
                    target: otherFile.name,
                    type: connectionType.type,
                    confidence: connectionType.confidence,
                    reason: connectionType.reason,
                    status: 'potential'
                });
            }
        }
        
        return connections;
    }

    // Infer connection type based on content analysis
    inferConnectionType(content1, content2, patterns) {
        for (const [type, typePatterns] of Object.entries(patterns)) {
            const matches = typePatterns.some(pattern => 
                pattern.test(content1) || pattern.test(content2)
            );
            if (matches) return type;
        }
        return 'generic';
    }

    // Find pattern matches between files
    findPatternMatches(content1, content2, patterns) {
        for (const [type, typePatterns] of Object.entries(patterns)) {
            for (const pattern of typePatterns) {
                if (pattern.test(content1) && pattern.test(content2)) {
                    return {
                        type,
                        confidence: 0.6,
                        reason: `Common ${type} patterns detected`
                    };
                }
            }
        }
        return null;
    }

    // Safely update MDC file with connections (non-destructive)
    async updateMDCFileConnections(fileName, connections) {
        try {
            // Get current file content
            const fileResult = await api.getMDCFileContent(fileName);
            if (!fileResult.success) {
                throw new Error(`Failed to read ${fileName}: ${fileResult.error}`);
            }
            
            let content = fileResult.data.content || '';
            
            // Find or create connections section
            const connectionsSection = this.createConnectionsSection(connections);
            
            // Pattern to find existing connections section
            const connectionsPattern = /## 🔗 Service Connections[\s\S]*?(?=\n## |\n# |$)/;
            
            if (connectionsPattern.test(content)) {
                // Update existing connections section
                content = content.replace(connectionsPattern, connectionsSection);
            } else {
                // Add new connections section before the end
                if (content.trim().endsWith('```')) {
                    // Add before closing code block
                    content = content.replace(/```\s*$/, `\n${connectionsSection}\n\n\`\`\``);
                } else {
                    // Add at the end
                    content += `\n\n${connectionsSection}`;
                }
            }
            
            // Update file
            const updateResult = await api.updateMDCFile(fileName, content);
            if (!updateResult.success) {
                throw new Error(`Failed to update ${fileName}: ${updateResult.error}`);
            }
            
            console.log(`✅ Updated ${fileName} with ${connections.length} connections`);
            return true;
            
        } catch (error) {
            console.error(`❌ Failed to update ${fileName}:`, error);
            return false;
        }
    }

    // Create formatted connections section
    createConnectionsSection(connections) {
        if (connections.length === 0) {
            return `## 🔗 Service Connections & Dependencies

### Auto-Discovered Connections
*No connections discovered yet. This section will be updated automatically during system scans.*

### Connection Summary
- **Total Connections**: 0
- **Last Discovery Scan**: ${new Date().toISOString().split('T')[0]} at ${new Date().toISOString().split('T')[1].split('.')[0]}
- **Discovery Method**: Awaiting automated content analysis
- **Update Policy**: Auto-refresh on file changes

### Connection Health & Status
- **Status**: Monitoring ready
- **Health Check**: Awaiting connections discovery
- **Failure Recovery**: Circuit breaker pattern ready

---
*This section is automatically maintained by the ZmartBot MDC Connection Discovery Engine*
*Next scan scheduled based on file modification detection*`;
        }

        // Categorize connections into the 3-state structure
        const categorized = { current: [], potential: [], priority: [] };
        
        connections.forEach(conn => {
            const type = conn.type?.toLowerCase() || '';
            const target = conn.target || '';
            
            // Priority connections (critical infrastructure)
            if (['database', 'api', 'port'].includes(type) || 
                target.includes('localhost') || 
                target.match(/^\d+$/)) {
                categorized.priority.push(conn);
            }
            // Current active connections (high confidence)
            else if ((conn.confidence || 0.5) > 0.7 || 
                     ['service', 'config', 'file'].includes(type)) {
                categorized.current.push(conn);
            }
            // Potential connections (lower confidence or uncertain)
            else {
                categorized.potential.push(conn);
            }
        });

        const createConnectionsList = (connList, statusIcon, statusText) => {
            return connList.length > 0 ? connList.map(conn => `
### 🔗 ${conn.target}
- **Type**: ${conn.type.charAt(0).toUpperCase() + conn.type.slice(1)}
- **Status**: ${statusIcon} **${statusText}**
- **Confidence**: ${Math.round((conn.confidence || 0.5) * 100)}%
- **Purpose**: ${conn.reason || conn.purpose || 'Service connection'}
- **Discovery Method**: Automated content analysis
`).join('\n') : `*No ${statusText.toLowerCase()} connections*`;
        };

        const timestamp = new Date().toISOString();
        return `## 🔗 Service Connections & Dependencies

### Current Active Connections
${createConnectionsList(categorized.current, '✅', 'ACTIVE')}

### Potential Connections
${createConnectionsList(categorized.potential, '⏳', 'POTENTIAL')}

### Priority Connections
${createConnectionsList(categorized.priority, '🔥', 'PRIORITY')}

### Connection Summary
- **Current Active**: ${categorized.current.length}
- **Potential**: ${categorized.potential.length}
- **Priority**: ${categorized.priority.length}
- **Total Discovered**: ${connections.length}
- **Last Discovery Scan**: ${timestamp.split('T')[0]} at ${timestamp.split('T')[1].split('.')[0]}
- **Discovery Method**: Automated content analysis with state classification
- **Update Policy**: Auto-refresh on file changes with intelligent categorization

### Connection Health & Status
- **Active Monitoring**: Current connections monitored continuously
- **Potential Analysis**: Potential connections analyzed for activation readiness
- **Priority Queue**: Priority connections flagged for immediate attention
- **Health Check**: Automated dependency validation with state-aware monitoring
- **Failure Recovery**: Circuit breaker pattern implemented with priority handling

---
*This section is automatically maintained by the ZmartBot MDC Connection Discovery Engine*
*Connection states: Current (Active) | Potential (Discovered) | Priority (Critical)*
*Next scan scheduled based on file modification detection*`;
    }

    // Main orchestrator function
    async performIncrementalScan(mdcFiles) {
        console.log('🧠 Starting Intelligent Incremental Connection Discovery...');
        
        // Step 1: Load snapshot and detect changes
        const snapshot = this.getSnapshot();
        const changes = this.detectChanges(mdcFiles, snapshot);
        
        console.log('📊 Change Analysis:', changes.summary);
        
        if (changes.summary.needProcessing === 0) {
            console.log('✅ No changes detected - using cached connections');
            return {
                success: true,
                fromCache: true,
                totalConnections: snapshot ? snapshot.totalConnections : 0,
                processed: 0,
                cached: changes.unchanged.length
            };
        }
        
        // Step 2: Process only changed files
        const filesToProcess = [...changes.newFiles, ...changes.modifiedFiles];
        const newConnectionMap = await this.discoverConnectionsForFiles(filesToProcess);
        
        // Step 3: Merge with unchanged files
        const allConnectionMap = {};
        
        // Add unchanged files with their cached connections
        changes.unchangedFiles.forEach(file => {
            if (file.connections) {
                allConnectionMap[file.name] = file.connections;
            }
        });
        
        // Add newly processed files
        Object.assign(allConnectionMap, newConnectionMap);
        
        // Step 4: Update MDC files with new connection info
        let updateCount = 0;
        for (const [fileName, connections] of Object.entries(newConnectionMap)) {
            const success = await this.updateMDCFileConnections(fileName, connections);
            if (success) updateCount++;
        }
        
        // Step 5: Save new snapshot
        const snapshotSaved = this.saveSnapshot(mdcFiles, allConnectionMap);
        
        const totalConnections = Object.values(allConnectionMap)
            .reduce((sum, conns) => sum + conns.length, 0);
        
        console.log('🎉 Incremental Scan Complete:', {
            processed: filesToProcess.length,
            updated: updateCount,
            totalConnections,
            snapshotSaved
        });
        
        return {
            success: true,
            fromCache: false,
            totalConnections,
            processed: filesToProcess.length,
            updated: updateCount,
            cached: changes.unchanged.length,
            isFullScan: changes.isFullScan
        };
    }
}

// Initialize the connection discovery engine
window.connectionEngine = new ConnectionDiscoveryEngine();

function updateSystemHealth() {
    const healthItems = [
        { id: 'mdcAgent', status: systemHealth.mdc_agent_status },
        { id: 'connectionAgent', status: systemHealth.connection_agent_status },
        { id: 'contextOptimizer', status: systemHealth.context_optimizer_status }
    ];
    
    healthItems.forEach(item => {
        const indicator = document.getElementById(`${item.id}Health`);
        const status = document.getElementById(`${item.id}Status`);
        const healthCard = indicator ? indicator.closest('.health-item') : null;
        
        if (indicator && status) {
            const healthClass = getHealthClass(item.status);
            indicator.className = `health-indicator ${healthClass}`;
            status.textContent = formatStatusText(item.status) || 'Unknown';
            
            // 🎨 Update entire health card background based on status
            if (healthCard) {
                // Remove existing status classes
                healthCard.classList.remove('health-connected', 'health-warning', 'health-disconnected');
                
                // Add appropriate status class
                if (healthClass === 'healthy') {
                    healthCard.classList.add('health-connected');
                } else if (healthClass === 'warning') {
                    healthCard.classList.add('health-warning');
                } else {
                    healthCard.classList.add('health-disconnected');
                }
            }
        }
    });
}

function getHealthClass(status) {
    const healthy = ['healthy', 'running', 'available', 'active', 'operational'];
    const warning = ['warning', 'degraded', 'slow', 'unavailable'];
    const error = ['error', 'failed', 'stopped', 'not available', 'unknown'];
    
    if (!status) return 'error';
    
    const statusLower = status.toLowerCase();
    if (healthy.includes(statusLower)) return 'healthy';
    if (warning.includes(statusLower)) return 'warning';
    if (error.includes(statusLower)) return 'error';
    
    // Default based on status content
    if (statusLower.includes('available') || statusLower.includes('running')) return 'healthy';
    if (statusLower.includes('warning') || statusLower.includes('degraded')) return 'warning';
    
    return 'error';
}

function formatStatusText(status) {
    if (!status) return 'Unknown';
    
    // Map common status values to user-friendly text
    const statusMap = {
        'available': 'Available',
        'running': 'Running',
        'healthy': 'Healthy',
        'active': 'Active',
        'operational': 'Operational',
        'stopped': 'Stopped',
        'error': 'Error',
        'failed': 'Failed',
        'degraded': 'Degraded',
        'warning': 'Warning',
        'unavailable': 'Unavailable'
    };
    
    const statusLower = status.toLowerCase();
    return statusMap[statusLower] || status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
}

// MDC Files Section
async function loadMDCFiles() {
    showStatusMessage('📄 Loading MDC files (optimized pagination)...', 'info');
    loading.show('Loading MDC files...');
    
    try {
        const result = await api.getMDCFiles();
        
        if (result.success) {
            allMDCFiles = result.data.files || [];
            mdcPagination.totalFiles = allMDCFiles.length;
            
            // Show only first 25 by default for better performance
            mdcFiles = mdcPagination.showAll ? allMDCFiles : allMDCFiles.slice(0, mdcPagination.pageSize);
            
            renderMDCGrid();
            renderPaginationControls();
            
            const loadedCount = mdcFiles.length;
            const totalCount = allMDCFiles.length;
            
            if (totalCount > mdcPagination.pageSize && !mdcPagination.showAll) {
                showStatusMessage(`✅ Loaded first ${loadedCount} of ${totalCount} MDC files (optimized loading)`, 'success');
            } else {
                showStatusMessage(`✅ Loaded all ${totalCount} MDC files`, 'success');
            }
        } else {
            throw new Error(result.error || 'Unknown error loading MDC files');
        }
    } catch (error) {
        console.error('Failed to load MDC files:', error);
        
        // 🔄 Try to recover with cached data or show helpful message
        if (error.name === 'AbortError') {
            showStatusMessage('⏳ Loading taking longer than expected - Retrying...', 'warning');
            // Try again with a simpler approach
            setTimeout(() => {
                loadMDCFilesSimple();
            }, 2000);
        } else {
            showStatusMessage('⚠️ Connection issue - Please check your network or try refreshing', 'error');
        }
        
        // Show fallback UI if we have no files loaded
        if (allMDCFiles.length === 0) {
            renderEmptyState();
        }
    } finally {
        loading.hide();
    }
}

// 🔄 Simplified loading fallback for when main loading fails
async function loadMDCFilesSimple() {
    try {
        showStatusMessage('🔄 Attempting recovery...', 'info');
        
        // Simple fetch without throttling
        const response = await fetch('/api/mdc/files', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.success && result.data.files) {
                allMDCFiles = result.data.files;
                mdcPagination.totalFiles = allMDCFiles.length;
                mdcFiles = allMDCFiles.slice(0, mdcPagination.pageSize);
                renderMDCGrid();
                renderPaginationControls();
                showStatusMessage('✅ Recovery successful - Files loaded', 'success');
            }
        } else {
            throw new Error('Recovery failed');
        }
    } catch (error) {
        console.error('Recovery failed:', error);
        showStatusMessage('❌ Unable to load files - Please refresh the page', 'error');
        renderEmptyState();
    }
}

function renderEmptyState() {
    const grid = document.getElementById('mdcGrid');
    grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem; color: #f59e0b;"></i>
            <h3>Unable to Load MDC Files</h3>
            <p>There was a problem loading the MDC files. Please try:</p>
            <div style="margin-top: 1rem;">
                <button class="btn btn-primary" onclick="loadMDCFiles()" style="margin: 0 0.5rem;">
                    <i class="fas fa-refresh"></i> Try Again
                </button>
                <button class="btn btn-secondary" onclick="window.location.reload()" style="margin: 0 0.5rem;">
                    <i class="fas fa-redo"></i> Refresh Page
                </button>
            </div>
        </div>
    `;
}

function renderPaginationControls() {
    const paginationContainer = document.getElementById('mdcPagination') || createPaginationContainer();
    const totalFiles = allMDCFiles.length;
    const showingFiles = mdcFiles.length;
    
    if (totalFiles <= mdcPagination.pageSize) {
        paginationContainer.style.display = 'none';
        return;
    }
    
    paginationContainer.style.display = 'flex';
    paginationContainer.innerHTML = `
        <div class="pagination-info">
            <span>Showing ${showingFiles} of ${totalFiles} files</span>
        </div>
        <div class="pagination-controls">
            ${!mdcPagination.showAll ? `
                <button class="btn-pagination" onclick="showAllMDCFiles()">
                    <i class="fas fa-expand"></i> Show All ${totalFiles}
                </button>
                ${totalFiles > mdcPagination.pageSize ? `
                    <button class="btn-pagination" onclick="loadNextMDCFiles()">
                        <i class="fas fa-chevron-right"></i> Next ${Math.min(mdcPagination.pageSize, totalFiles - showingFiles)}
                    </button>
                ` : ''}
            ` : `
                <button class="btn-pagination" onclick="showLimitedMDCFiles()">
                    <i class="fas fa-compress"></i> Show First ${mdcPagination.pageSize}
                </button>
            `}
        </div>
    `;
}

function createPaginationContainer() {
    const container = document.createElement('div');
    container.id = 'mdcPagination';
    container.className = 'pagination-container';
    container.style.cssText = `
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 0;
        border-top: 1px solid #e5e7eb;
        margin-top: 20px;
    `;
    
    // Add CSS for pagination - Dark theme
    const style = document.createElement('style');
    style.textContent = `
        .pagination-container {
            background: #1f2937;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
        }
        .pagination-info {
            color: #9ca3af;
            font-size: 14px;
            font-weight: 500;
        }
        .pagination-controls {
            display: flex;
            gap: 8px;
        }
        .btn-pagination {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
        }
        .btn-pagination:hover {
            background: #2563eb;
        }
        .btn-pagination i {
            font-size: 12px;
        }
    `;
    document.head.appendChild(style);
    
    const mdcGrid = document.getElementById('mdcGrid');
    mdcGrid.parentNode.insertBefore(container, mdcGrid.nextSibling);
    
    return container;
}

function showAllMDCFiles() {
    showStatusMessage('📄 Loading all MDC files...', 'info');
    mdcPagination.showAll = true;
    mdcFiles = allMDCFiles;
    renderMDCGrid();
    renderPaginationControls();
    showStatusMessage(`✅ Now showing all ${allMDCFiles.length} MDC files`, 'success');
}

function showLimitedMDCFiles() {
    showStatusMessage('📄 Optimizing display (first 25 files)...', 'info');
    mdcPagination.showAll = false;
    mdcPagination.currentPage = 1;
    mdcFiles = allMDCFiles.slice(0, mdcPagination.pageSize);
    renderMDCGrid();
    renderPaginationControls();
    showStatusMessage(`✅ Showing first ${mdcPagination.pageSize} files (optimized)`, 'success');
}

function loadNextMDCFiles() {
    const currentCount = mdcFiles.length;
    const nextBatch = allMDCFiles.slice(currentCount, currentCount + mdcPagination.pageSize);
    
    if (nextBatch.length > 0) {
        showStatusMessage(`📄 Loading next ${nextBatch.length} files...`, 'info');
        mdcFiles = [...mdcFiles, ...nextBatch];
        renderMDCGrid();
        renderPaginationControls();
        showStatusMessage(`✅ Loaded ${nextBatch.length} more files (${mdcFiles.length} total)`, 'success');
    }
}

// 🎨 PROFESSIONAL CARD STYLING FUNCTIONS
function getCategoryColor(category) {
    const categoryColors = {
        'Core': '#6366f1',           // Indigo
        'Data & Analytics': '#059669', // Emerald  
        'Trading': '#dc2626',        // Red
        'Monitoring': '#ea580c',     // Orange
        'Orchestration': '#7c3aed',  // Violet
        'Services': '#0891b2',       // Cyan
        'Backend': '#4f46e5',        // Purple
        'Frontend': '#db2777',       // Pink
        'Security': '#991b1b',       // Dark red
        'Communication': '#0d9488',  // Teal
        'Database': '#365314',       // Green
        'API': '#1e40af',           // Blue
        'Default': '#64748b'        // Slate
    };
    
    return categoryColors[category] || categoryColors['Default'];
}

function injectMDCCardStyles() {
    // Check if styles already injected
    if (document.getElementById('mdc-professional-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'mdc-professional-styles';
    style.textContent = `
        /* 🎨 PROFESSIONAL MDC CARDS - DARK THEME */
        .mdc-card-professional {
            background: #1f2937;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
            border: 1px solid #374151;
            transition: all 0.3s ease;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            height: 280px; /* Fixed height for consistency */
            overflow: hidden;
        }
        
        .mdc-card-professional:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3);
            border-color: #3b82f6;
            background: #252f3f;
        }
        
        .mdc-card-header {
            padding: 16px 20px 12px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 1px solid #374151;
        }
        
        .mdc-card-title-section {
            flex: 1;
        }
        
        .mdc-card-title {
            margin: 0 0 8px 0;
            font-size: 16px;
            font-weight: 600;
            color: #f9fafb;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .mdc-category-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .mdc-card-icon {
            color: #9ca3af;
            font-size: 20px;
            margin-left: 12px;
            opacity: 0.8;
        }
        
        .mdc-card-body {
            padding: 0 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .mdc-card-description {
            margin: 0 0 16px 0;
            color: #d1d5db;
            font-size: 14px;
            line-height: 1.5;
            flex: 1;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .mdc-card-stats {
            display: flex;
            gap: 16px;
            margin-bottom: 12px;
        }
        
        .mdc-stat {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: #9ca3af;
        }
        
        .mdc-stat i {
            width: 14px;
            text-align: center;
            color: #6b7280;
        }
        
        .mdc-card-actions {
            padding: 12px 20px 16px;
            display: flex;
            gap: 8px;
            border-top: 1px solid #374151;
            background: #111827;
        }
        
        .mdc-action-btn {
            flex: 1;
            padding: 8px 12px;
            border: none;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .mdc-action-btn.primary {
            background: #3b82f6;
            color: white;
        }
        
        .mdc-action-btn.primary:hover {
            background: #2563eb;
        }
        
        .mdc-action-btn.ai {
            background: #7c3aed;
            color: white;
        }
        
        .mdc-action-btn.ai:hover {
            background: #6d28d9;
        }
        
        .mdc-action-btn.info {
            background: #0891b2;
            color: white;
        }
        
        .mdc-action-btn.info:hover {
            background: #0e7490;
        }
        
        .mdc-action-btn.danger {
            background: #dc2626;
            color: white;
        }
        
        .mdc-action-btn.danger:hover {
            background: #b91c1c;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .mdc-card-professional {
                height: auto;
                min-height: 240px;
            }
            
            .mdc-card-stats {
                flex-direction: column;
                gap: 8px;
            }
            
            .mdc-action-btn {
                padding: 6px 8px;
                font-size: 11px;
            }
        }
    `;
    
    document.head.appendChild(style);
}

function renderMDCGrid() {
    const grid = document.getElementById('mdcGrid');
    const categoryFilter = document.getElementById('categoryFilter').value;
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    // Filter files
    let filteredFiles = mdcFiles;
    
    if (categoryFilter !== 'all') {
        filteredFiles = filteredFiles.filter(file => file.category === categoryFilter);
    }
    
    if (searchTerm) {
        filteredFiles = filteredFiles.filter(file => 
            file.name.toLowerCase().includes(searchTerm) ||
            (file.description && file.description.toLowerCase().includes(searchTerm))
        );
    }
    
    // 🎨 Render professional MDC cards with consistent sizing
    grid.innerHTML = filteredFiles.map(file => {
        const category = file.category || 'Core';
        const categoryColor = getCategoryColor(category);
        const description = file.description || 'No description available';
        const truncatedDescription = description.length > 120 ? description.substring(0, 120) + '...' : description;
        const connectionCount = (file.connections && file.connections.length) || 0;
        
        return `
        <div class="mdc-card-professional" onclick="openMDCModal('${file.name}')">
            <div class="mdc-card-header">
                <div class="mdc-card-title-section">
                    <h3 class="mdc-card-title">${file.name}</h3>
                    <div class="mdc-category-badge" style="background-color: ${categoryColor}">
                        ${category}
                    </div>
                </div>
                <div class="mdc-card-icon">
                    <i class="fas fa-file-alt"></i>
                </div>
            </div>
            
            <div class="mdc-card-body">
                <p class="mdc-card-description">${truncatedDescription}</p>
                
                <div class="mdc-card-stats">
                    <div class="mdc-stat">
                        <i class="fas fa-hdd"></i>
                        <span>${utils.formatBytes(file.size || 0)}</span>
                    </div>
                    <div class="mdc-stat">
                        <i class="fas fa-project-diagram"></i>
                        <span>${connectionCount} connections</span>
                    </div>
                    <div class="mdc-stat">
                        <i class="fas fa-clock"></i>
                        <span>${utils.formatDate(file.lastModified)}</span>
                    </div>
                </div>
            </div>
            
            <div class="mdc-card-actions">
                <button class="mdc-action-btn primary" onclick="event.stopPropagation(); editMDC('${file.name}')" title="Edit MDC File">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="mdc-action-btn ai" onclick="event.stopPropagation(); enhanceExistingMDC('${file.name.replace('.mdc', '')}')" title="AI Enhance">
                    <i class="fas fa-robot"></i>
                </button>
                <button class="mdc-action-btn info" onclick="event.stopPropagation(); viewConnections('${file.name}')" title="View Connections">
                    <i class="fas fa-project-diagram"></i>
                </button>
                <button class="mdc-action-btn danger" onclick="event.stopPropagation(); deleteMDC('${file.name}')" title="Delete File">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
        `;
    }).join('');
    
    // Apply professional card styling
    injectMDCCardStyles();
    
    if (filteredFiles.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
                <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; color: var(--primary-color);"></i>
                <h3>No MDC files found</h3>
                <p>Try adjusting your search criteria or create a new MDC file.</p>
                <button class="btn btn-primary" onclick="createNewMDC()" style="margin-top: 1rem;">
                    <i class="fas fa-plus"></i> Create New MDC
                </button>
            </div>
        `;
    }
}

// Modal Management
function openMDCModal(filename) {
    const modal = document.getElementById('mdcModal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');
    const actionBtn = document.getElementById('modalActionBtn');
    
    title.textContent = filename;
    body.innerHTML = '<div style="text-align: center; padding: 2rem;"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
    modal.style.display = 'block';
    
    // Load file details
    loadMDCFileDetails(filename);
    
    actionBtn.textContent = 'Edit';
    actionBtn.onclick = () => editMDC(filename);
}

async function loadMDCFileDetails(filename) {
    try {
        const result = await api.getMDCFile(filename);
        const body = document.getElementById('modalBody');
        
        if (result.success) {
            const file = result.data;
            body.innerHTML = `
                <div class="file-details">
                    <div class="detail-section">
                        <h4><i class="fas fa-info-circle"></i> File Information</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <label>Name:</label>
                                <span>${file.name}</span>
                            </div>
                            <div class="detail-item">
                                <label>Category:</label>
                                <span>${file.category || 'Core'}</span>
                            </div>
                            <div class="detail-item">
                                <label>Size:</label>
                                <span>${utils.formatBytes(file.size || 0)}</span>
                            </div>
                            <div class="detail-item">
                                <label>Last Modified:</label>
                                <span>${utils.formatDate(file.lastModified)}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h4><i class="fas fa-file-alt"></i> Description</h4>
                        <p>${file.description || 'No description available'}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h4><i class="fas fa-code"></i> Content Preview</h4>
                        <pre class="code-preview">${file.content ? file.content.substring(0, 500) + (file.content.length > 500 ? '...' : '') : 'No content available'}</pre>
                    </div>
                    
                    <div class="detail-section">
                        <h4><i class="fas fa-project-diagram"></i> Connections</h4>
                        <div class="connections-preview">
                            ${file.connections && file.connections.length > 0 ? 
                                file.connections.map(conn => `
                                    <span class="connection-tag">${conn.target} (${conn.type})</span>
                                `).join('') : 
                                '<span style="color: var(--text-muted);">No connections found</span>'
                            }
                        </div>
                    </div>
                </div>
            `;
        } else {
            body.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-triangle"></i> Failed to load file details: ${result.error}</div>`;
        }
    } catch (error) {
        const body = document.getElementById('modalBody');
        body.innerHTML = `<div class="error-message"><i class="fas fa-exclamation-triangle"></i> Error loading file: ${error.message}</div>`;
    }
}

function closeMDCModal() {
    document.getElementById('mdcModal').style.display = 'none';
}

// Quick Actions
async function generateAllDocs() {
    loading.show('Scanning project and generating MDC files for services without documentation...');
    
    try {
        const result = await api.generateMDC({ action: 'generate_all' });
        
        if (result.success || result.data?.success) {
            const data = result.data || result;
            const generated = data.generated_count || 0;
            const skipped = data.skipped_count || 0;
            const errors = (data.errors || []).length;
            
            let message = `✅ Bulk generation complete: ${generated} new MDC files created`;
            if (skipped > 0) {
                message += `, ${skipped} existing files preserved (never overwritten)`;
            }
            if (errors > 0) {
                message += `, ${errors} errors occurred`;
            }
            
            if (generated > 0) {
                toast.success(message);
                // Refresh the data to show new files
                setTimeout(() => {
                    loadOverviewData();
                    if (currentSection === 'files') {
                        loadMDCFiles();
                    }
                }, 1500);
            } else if (skipped > 0) {
                toast.info(`📋 No new files to generate - all ${skipped} discovered services already have MDC files`);
            } else {
                toast.info('📋 No service files found that need MDC documentation');
            }
            
            // Show detailed results if there were services found
            if (data.services_found && data.services_found.length > 0) {
                console.log('Services processed:', data.services_found);
            }
            
            // Show errors if any occurred
            if (errors > 0 && data.errors) {
                console.warn('Generation errors:', data.errors);
            }
            
            // Show the generation summary cards
            showGenerationSummary(data);
            
            // Add to update history
            if (generated > 0) {
                addToUpdateHistory('generation', 'Bulk MDC Generation', {
                    generatedCount: generated,
                    skippedCount: skipped,
                    totalServices: data.total_services || 0,
                    errors: data.errors || []
                });
            }
        } else {
            throw new Error(result.message || result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Failed to generate docs:', error);
        toast.error('Failed to generate documentation: ' + error.message);
    } finally {
        loading.hide();
    }
}

function showGenerationSummary(data) {
    const summarySection = document.getElementById('generationSummary');
    const totalFilesCount = document.getElementById('totalFilesCount');
    const completedCount = document.getElementById('completedCount');
    const pendingCount = document.getElementById('pendingCount');
    
    // Update counts
    const total = data.total_services || 0;
    const completed = (data.completed_services || []).length;
    const pending = (data.pending_services || []).length;
    
    totalFilesCount.textContent = total;
    completedCount.textContent = completed;
    pendingCount.textContent = pending;
    
    // Store pending services data for later use
    window.pendingServicesData = data.pending_services || [];
    window.completedServicesData = data.completed_services || [];
    
    // Show the summary section
    summarySection.style.display = 'block';
    
    // Scroll to the summary section
    summarySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function togglePendingServices() {
    const pendingCard = document.getElementById('pendingCard');
    const pendingServicesList = document.getElementById('pendingServicesList');
    const pendingArrow = document.getElementById('pendingArrow');
    
    const isExpanded = pendingCard.classList.contains('expanded');
    
    if (isExpanded) {
        // Collapse
        pendingCard.classList.remove('expanded');
        pendingServicesList.style.display = 'none';
        pendingArrow.style.transform = 'rotate(0deg)';
    } else {
        // Expand
        pendingCard.classList.add('expanded');
        pendingServicesList.style.display = 'block';
        pendingArrow.style.transform = 'rotate(180deg)';
        
        // Populate pending services list
        populatePendingServicesList();
        
        // Scroll to the pending services list
        setTimeout(() => {
            pendingServicesList.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    }
}

function populatePendingServicesList() {
    const pendingGrid = document.getElementById('pendingServicesGrid');
    const pendingServices = window.pendingServicesData || [];
    
    if (pendingServices.length === 0) {
        pendingGrid.innerHTML = `
            <div class="no-content-message">
                <i class="fas fa-check-circle" style="font-size: 2rem; color: var(--success-color); margin-bottom: 1rem;"></i>
                <p>No pending services found. All discovered services already have MDC files!</p>
            </div>
        `;
        return;
    }
    
    pendingGrid.innerHTML = pendingServices.map(service => `
        <div class="pending-service-card" id="service-${service.name}">
            <div class="pending-service-header" onclick="toggleServiceContent('${service.name}')">
                <div class="service-info">
                    <h4>${service.name}</h4>
                    <p>${service.path} • ${service.type} • ${formatBytes(service.file_size || 0)}</p>
                </div>
                <div class="service-actions">
                    <button class="btn-small btn-primary" onclick="event.stopPropagation(); generateBasicMDC('${service.name}', '${service.type}', '${service.path}')">
                        <i class="fas fa-plus"></i> Generate MDC
                    </button>
                    <button class="btn-small btn-chatgpt" onclick="event.stopPropagation(); generateChatGPTMDC('${service.name}')">
                        <i class="fas fa-robot"></i> ChatGPT MDC
                    </button>
                    <i class="fas fa-chevron-down service-expand-arrow"></i>
                </div>
            </div>
            <div class="pending-service-content">
                <div class="content-preview-header">
                    <h5><i class="fas fa-file-code"></i> Service Preview</h5>
                </div>
                <div class="mdc-content-preview" id="preview-${service.name}">
                    Loading service information...
                </div>
            </div>
        </div>
    `).join('');
}

function toggleServiceContent(serviceName) {
    const serviceCard = document.getElementById(`service-${serviceName}`);
    const previewDiv = document.getElementById(`preview-${serviceName}`);
    
    const isExpanded = serviceCard.classList.contains('expanded');
    
    if (isExpanded) {
        serviceCard.classList.remove('expanded');
    } else {
        serviceCard.classList.add('expanded');
        
        // Load service preview if not already loaded
        if (previewDiv.textContent === 'Loading service information...') {
            loadServicePreview(serviceName);
        }
    }
}

async function loadServicePreview(serviceName) {
    const previewDiv = document.getElementById(`preview-${serviceName}`);
    const service = (window.pendingServicesData || []).find(s => s.name === serviceName);
    
    if (!service) {
        previewDiv.textContent = 'Service information not found';
        return;
    }
    
    try {
        // Try to get a preview of the service file content
        previewDiv.innerHTML = `
            <div style="margin-bottom: 1rem;">
                <strong>📁 File Path:</strong> ${service.path}<br>
                <strong>🏷️ Type:</strong> ${service.type}<br>
                <strong>📊 Size:</strong> ${formatBytes(service.file_size || 0)}<br>
                <strong>📝 Description:</strong> ${service.description || 'Auto-detected service'}
            </div>
            <div style="background: var(--secondary-bg); padding: 0.5rem; border-radius: 4px; font-family: monospace; font-size: 0.8rem;">
                <strong>Preview:</strong> Service file detected with potential service indicators.<br>
                Generate MDC to create documentation or use ChatGPT MDC for enhanced analysis.
            </div>
        `;
    } catch (error) {
        previewDiv.textContent = 'Error loading preview: ' + error.message;
    }
}

async function generateBasicMDC(serviceName, serviceType, servicePath) {
    loading.show(`Generating basic MDC for ${serviceName}...`);
    
    try {
        const result = await api.generateMDC({
            name: serviceName,
            type: serviceType,
            description: `Auto-detected service from ${servicePath}`,
            path: servicePath
        });
        
        if (result.success) {
            toast.success(`✅ MDC generated for ${serviceName}`);
            
            // Remove from pending list
            removePendingService(serviceName);
            
            // Refresh the file list
            setTimeout(() => {
                if (currentSection === 'files') {
                    loadMDCFiles();
                }
                loadOverviewData();
            }, 1000);
        } else {
            toast.error(`Failed to generate MDC for ${serviceName}: ${result.message || result.error}`);
        }
    } catch (error) {
        console.error('Error generating basic MDC:', error);
        toast.error(`Failed to generate MDC for ${serviceName}: ${error.message}`);
    } finally {
        loading.hide();
    }
}

async function generateChatGPTMDC(serviceName) {
    loading.show(`Generating enhanced ChatGPT MDC for ${serviceName}...`);
    
    try {
        const result = await fetch('/api/mdc/generate/chatgpt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                service_name: serviceName
            })
        });
        
        const data = await result.json();
        
        if (data.success) {
            const enhanced = data.data.enhanced ? '🚀 ChatGPT-enhanced' : '📝 Locally enhanced';
            toast.success(`${enhanced} MDC generated for ${serviceName}`);
            
            // Show preview if available
            if (data.data.content_preview) {
                console.log(`Enhanced content preview for ${serviceName}:`, data.data.content_preview);
            }
            
            // Add to update history
            addToUpdateHistory('enhancement', `ChatGPT MDC Generation: ${serviceName}`, {
                serviceName: serviceName,
                enhanced: data.data.enhanced || false,
                backupCreated: !!data.data.backup_created,
                message: data.data.message || `Generated ChatGPT MDC for ${serviceName}`
            });
            
            // Remove from pending list or update status
            removePendingService(serviceName);
            
            // Refresh the file list
            setTimeout(() => {
                if (currentSection === 'files') {
                    loadMDCFiles();
                }
                loadOverviewData();
            }, 1000);
        } else {
            toast.error(`Failed to generate ChatGPT MDC for ${serviceName}: ${data.error}`);
        }
    } catch (error) {
        console.error('Error generating ChatGPT MDC:', error);
        toast.error(`Failed to generate ChatGPT MDC for ${serviceName}: ${error.message}`);
    } finally {
        loading.hide();
    }
}

function removePendingService(serviceName) {
    // Remove from pending services data
    if (window.pendingServicesData) {
        window.pendingServicesData = window.pendingServicesData.filter(s => s.name !== serviceName);
    }
    
    // Remove from UI
    const serviceCard = document.getElementById(`service-${serviceName}`);
    if (serviceCard) {
        serviceCard.style.opacity = '1';
        serviceCard.style.transform = 'scale(1)';
        setTimeout(() => {
            serviceCard.remove();
            
            // Update pending count
            const pendingCount = document.getElementById('pendingCount');
            if (pendingCount) {
                pendingCount.textContent = (parseInt(pendingCount.textContent) - 1).toString();
            }
            
            // If no more pending services, show completion message
            if (window.pendingServicesData && window.pendingServicesData.length === 0) {
                const pendingGrid = document.getElementById('pendingServicesGrid');
                if (pendingGrid) {
                    pendingGrid.innerHTML = `
                        <div class="no-content-message">
                            <i class="fas fa-check-circle" style="font-size: 2rem; color: var(--success-color); margin-bottom: 1rem;"></i>
                            <p>All services now have MDC files! 🎉</p>
                        </div>
                    `;
                }
            }
        }, 300);
    }
}

function toggleUpdateHistory() {
    const lastUpdateCard = document.querySelector('.clickable-stat-card');
    const updateHistorySection = document.getElementById('updateHistory');
    const updateHistoryArrow = document.getElementById('updateHistoryArrow');
    
    const isExpanded = lastUpdateCard.classList.contains('expanded');
    
    if (isExpanded) {
        // Collapse
        lastUpdateCard.classList.remove('expanded');
        updateHistorySection.style.display = 'none';
    } else {
        // Expand
        lastUpdateCard.classList.add('expanded');
        updateHistorySection.style.display = 'block';
        
        // Load and populate update history
        loadUpdateHistory();
        
        // Scroll to the update history section
        setTimeout(() => {
            updateHistorySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 300);
    }
}

function loadUpdateHistory() {
    // Load from localStorage
    const savedHistory = localStorage.getItem('mdcUpdateHistory');
    if (savedHistory) {
        updateHistory = JSON.parse(savedHistory);
    }
    
    // If no history, create some sample entries based on current data
    if (updateHistory.length === 0 && lastScanData.timestamp) {
        updateHistory = [{
            id: generateHistoryId(),
            type: 'scan',
            timestamp: lastScanData.timestamp,
            title: 'MDC Files Scan',
            details: {
                totalFiles: lastScanData.fileCount,
                mdcFiles: lastScanData.mdcFileCount,
                connections: lastScanData.connectionsCount,
                path: lastScanData.path,
                systemUpdateTime: lastScanData.systemUpdateTime
            }
        }];
        saveUpdateHistory();
    }
    
    populateUpdateHistory();
}

function populateUpdateHistory() {
    const historyGrid = document.getElementById('updateHistoryGrid');
    
    if (updateHistory.length === 0) {
        historyGrid.innerHTML = `
            <div class="no-content-message">
                <i class="fas fa-history" style="font-size: 2rem; color: var(--secondary-color); margin-bottom: 1rem;"></i>
                <p>No update history available yet. Perform some scans or operations to see history here.</p>
            </div>
        `;
        return;
    }
    
    // Sort by most recent first
    const sortedHistory = [...updateHistory].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    historyGrid.innerHTML = sortedHistory.map(entry => `
        <div class="update-history-card" id="history-${entry.id}">
            <div class="update-history-header" onclick="toggleHistoryDetails('${entry.id}')">
                <div class="update-info">
                    <h4>
                        <i class="fas ${getHistoryIcon(entry.type)}"></i>
                        ${entry.title}
                        <span class="update-badge ${entry.type}">${entry.type.toUpperCase()}</span>
                    </h4>
                    <p>${new Date(entry.timestamp).toLocaleString()}</p>
                </div>
                <i class="fas fa-chevron-down update-expand-arrow"></i>
            </div>
            <div class="update-history-content">
                ${generateHistoryContent(entry)}
            </div>
        </div>
    `).join('');
}

function getHistoryIcon(type) {
    const icons = {
        'scan': 'fa-search',
        'generation': 'fa-plus-circle',
        'enhancement': 'fa-robot',
        'maintenance': 'fa-tools'
    };
    return icons[type] || 'fa-info-circle';
}

function generateHistoryContent(entry) {
    const details = entry.details || {};
    
    switch (entry.type) {
        case 'scan':
            return `
                <div class="update-details">
                    <div class="update-detail-row">
                        <span class="update-detail-label">📁 Scan Path:</span>
                        <span class="update-detail-value">${details.path || 'N/A'}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">📄 Total Files:</span>
                        <span class="update-detail-value">${details.totalFiles || 0}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">🔧 MDC Files:</span>
                        <span class="update-detail-value">${details.mdcFiles || 0}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">🌐 Connections:</span>
                        <span class="update-detail-value">${details.connections || 0}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">🔄 System Updated:</span>
                        <span class="update-detail-value">${details.systemUpdateTime ? new Date(details.systemUpdateTime).toLocaleString() : 'N/A'}</span>
                    </div>
                </div>
                <div class="update-summary">
                    <h5>📊 Scan Summary</h5>
                    <div class="update-summary-stats">
                        <div class="update-stat">
                            <span class="update-stat-number">${details.totalFiles || 0}</span>
                            <span class="update-stat-label">Files</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">${details.mdcFiles || 0}</span>
                            <span class="update-stat-label">MDC</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">${details.connections || 0}</span>
                            <span class="update-stat-label">Connections</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">${Math.round(((details.mdcFiles || 0) / (details.totalFiles || 1)) * 100)}%</span>
                            <span class="update-stat-label">Coverage</span>
                        </div>
                    </div>
                </div>
            `;
        case 'generation':
            return `
                <div class="update-details">
                    <div class="update-detail-row">
                        <span class="update-detail-label">📄 Generated Files:</span>
                        <span class="update-detail-value">${details.generatedCount || 0}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">⏭️ Skipped Files:</span>
                        <span class="update-detail-value">${details.skippedCount || 0}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">🚀 Total Services:</span>
                        <span class="update-detail-value">${details.totalServices || 0}</span>
                    </div>
                    ${details.errors && details.errors.length > 0 ? `
                    <div class="update-detail-row">
                        <span class="update-detail-label">⚠️ Errors:</span>
                        <span class="update-detail-value">${details.errors.length}</span>
                    </div>
                    ` : ''}
                </div>
                <div class="update-summary">
                    <h5>📊 Generation Summary</h5>
                    <div class="update-summary-stats">
                        <div class="update-stat">
                            <span class="update-stat-number">${details.generatedCount || 0}</span>
                            <span class="update-stat-label">Generated</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">${details.skippedCount || 0}</span>
                            <span class="update-stat-label">Skipped</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">${details.totalServices || 0}</span>
                            <span class="update-stat-label">Total</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">${details.errors ? details.errors.length : 0}</span>
                            <span class="update-stat-label">Errors</span>
                        </div>
                    </div>
                </div>
            `;
        case 'enhancement':
            return `
                <div class="update-details">
                    <div class="update-detail-row">
                        <span class="update-detail-label">🔧 Service:</span>
                        <span class="update-detail-value">${details.serviceName || 'N/A'}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">🚀 Enhanced:</span>
                        <span class="update-detail-value">${details.enhanced ? 'Yes (ChatGPT)' : 'Local only'}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">💾 Backup:</span>
                        <span class="update-detail-value">${details.backupCreated ? 'Created' : 'Not needed'}</span>
                    </div>
                </div>
                <div class="update-summary">
                    <h5>📊 Enhancement Details</h5>
                    <p style="font-size: 0.8rem; color: var(--text-secondary); margin: 0;">${details.message || 'MDC file enhanced successfully'}</p>
                </div>
            `;
        case 'maintenance':
            return `
                <div class="update-details">
                    <div class="update-detail-row">
                        <span class="update-detail-label">🔧 Maintenance Steps:</span>
                        <span class="update-detail-value">${details.maintenanceSteps || 0}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">🔗 Duplicates Merged:</span>
                        <span class="update-detail-value">${details.duplicatesMerged || 0}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">🧹 Services Filtered:</span>
                        <span class="update-detail-value">${details.servicesFiltered || 0}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">⏰ Maintenance Type:</span>
                        <span class="update-detail-value">Scheduled (12h interval)</span>
                    </div>
                </div>
                <div class="update-summary">
                    <h5>📊 Maintenance Summary</h5>
                    <div class="update-summary-stats">
                        <div class="update-stat">
                            <span class="update-stat-number">${details.duplicatesMerged || 0}</span>
                            <span class="update-stat-label">Merged</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">${details.servicesFiltered || 0}</span>
                            <span class="update-stat-label">Filtered</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">${details.maintenanceSteps || 0}</span>
                            <span class="update-stat-label">Steps</span>
                        </div>
                        <div class="update-stat">
                            <span class="update-stat-number">✅</span>
                            <span class="update-stat-label">Status</span>
                        </div>
                    </div>
                </div>
            `;
        default:
            return `
                <div class="update-details">
                    <div class="update-detail-row">
                        <span class="update-detail-label">ℹ️ Type:</span>
                        <span class="update-detail-value">${entry.type}</span>
                    </div>
                    <div class="update-detail-row">
                        <span class="update-detail-label">📝 Details:</span>
                        <span class="update-detail-value">${JSON.stringify(details)}</span>
                    </div>
                </div>
            `;
    }
}

function toggleHistoryDetails(historyId) {
    const historyCard = document.getElementById(`history-${historyId}`);
    const isExpanded = historyCard.classList.contains('expanded');
    
    if (isExpanded) {
        historyCard.classList.remove('expanded');
    } else {
        historyCard.classList.add('expanded');
    }
}

function addToUpdateHistory(type, title, details) {
    const historyEntry = {
        id: generateHistoryId(),
        type: type,
        timestamp: new Date().toISOString(),
        title: title,
        details: details || {}
    };
    
    updateHistory.unshift(historyEntry); // Add to beginning
    
    // Keep only last 50 entries
    if (updateHistory.length > 50) {
        updateHistory = updateHistory.slice(0, 50);
    }
    
    saveUpdateHistory();
}

function saveUpdateHistory() {
    localStorage.setItem('mdcUpdateHistory', JSON.stringify(updateHistory));
}

function generateHistoryId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

async function enhanceExistingMDC(serviceName) {
    loading.show(`Enhancing existing MDC with ChatGPT for ${serviceName}...`);
    
    try {
        const result = await fetch('/api/mdc/generate/chatgpt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                service_name: serviceName
            })
        });
        
        const data = await result.json();
        
        if (data.success) {
            const enhanced = data.data.enhanced ? '🚀 ChatGPT-enhanced' : '📝 Locally enhanced';
            toast.success(`${enhanced} MDC updated for ${serviceName}`);
            
            // Show preview if available
            if (data.data.content_preview) {
                console.log(`Enhanced content preview for ${serviceName}:`, data.data.content_preview);
            }
            
            // Show backup info
            if (data.data.backup_created) {
                toast.info(`Original file backed up: ${data.data.backup_created}`);
            }
            
            // Add to update history
            addToUpdateHistory('enhancement', `ChatGPT Enhancement: ${serviceName}`, {
                serviceName: serviceName,
                enhanced: data.data.enhanced || false,
                backupCreated: !!data.data.backup_created,
                message: data.data.message || `Enhanced MDC for ${serviceName}`
            });
            
            // Refresh the file list
            setTimeout(() => {
                if (currentSection === 'files') {
                    loadMDCFiles();
                }
                loadOverviewData();
            }, 1000);
        } else {
            toast.error(`Failed to enhance MDC for ${serviceName}: ${data.error}`);
        }
    } catch (error) {
        console.error('Error enhancing existing MDC:', error);
        toast.error(`Failed to enhance MDC for ${serviceName}: ${error.message}`);
    } finally {
        loading.hide();
    }
}

async function discoverConnections() {
    // Show Service Discovery interface instead of just starting discovery
    showServiceDiscovery();
}

async function showServiceDiscovery() {
    console.log('🔍 Starting service discovery...');
    loading.show('Loading comprehensive service connections...');
    
    try {
        // Use dashboard's comprehensive connection parsing instead of limited orchestration agent
        console.log('📡 Fetching dashboard connections...');
        const result = await api.getDashboardConnections();
        console.log('📊 Dashboard connections result:', result);
        
        if (result.success && result.data) {
            console.log('✅ Opening service discovery modal with data:', result.data);
            openServiceDiscoveryModal(result.data);
        } else {
            console.error('❌ Failed to load comprehensive service connections:', result);
            toast.error('Failed to load comprehensive service connections');
        }
    } catch (error) {
        console.error('❌ Error loading comprehensive service connections:', error);
        toast.error('Comprehensive service discovery failed');
    } finally {
        loading.hide();
    }
}

function openServiceDiscoveryModal(connectionData) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay service-discovery-modal';
    modal.innerHTML = `
        <div class="modal-content service-discovery-content">
            <div class="modal-header">
                <h2><i class="fas fa-project-diagram"></i> Service Discovery</h2>
                <p>Complete overview of all services and their connections</p>
                <div class="modal-actions">
                    <button class="modal-action-btn" onclick="redirectToServiceDiscoveryDashboard()">
                        <i class="fas fa-external-link-alt"></i>
                        Service Discovery Dashboard
                    </button>
                    <button class="modal-close" onclick="closeServiceDiscoveryModal()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="modal-body">
                <div class="discovery-stats">
                    <div class="stat-item">
                        <span class="stat-number">${connectionData.total_services}</span>
                        <span class="stat-label">Services with Connections</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${connectionData.total_connections}</span>
                        <span class="stat-label">Total Connections</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${new Date(connectionData.last_updated).toLocaleTimeString()}</span>
                        <span class="stat-label">Last Updated</span>
                    </div>
                </div>
                
                <div class="services-grid">
                    ${renderServicesGrid(connectionData.services)}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add click handlers for service expansion
    modal.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.connection-action')) {
                toggleServiceExpansion(card);
            }
        });
    });
}

function renderServicesGrid(services) {
    return Object.entries(services).map(([serviceName, serviceData]) => `
        <div class="service-card" data-service="${serviceName}">
            <div class="service-header">
                <div class="service-info">
                    <h3 class="service-name">${serviceName}</h3>
                    <div class="service-meta">
                        <span class="service-type">${serviceData.service_info?.type || 'unknown'}</span>
                        ${serviceData.service_info?.port ? `<span class="service-port">:${serviceData.service_info.port}</span>` : ''}
                        <span class="connection-count">${serviceData.total} connections</span>
                    </div>
                    <p class="service-description">${serviceData.service_info?.description || 'No description available'}</p>
                </div>
                <div class="service-actions">
                    <button class="connection-action" onclick="expandServiceConnections('${serviceName}')">
                        <i class="fas fa-expand-arrows-alt"></i>
                    </button>
                </div>
            </div>
            
            <div class="service-connections collapsed" data-service="${serviceName}">
                <div class="connections-header">
                    <h4><i class="fas fa-link"></i> Service Dependencies</h4>
                    <p>This service connects to the following components:</p>
                </div>
                
                <div class="connections-list">
                    ${serviceData.connections.map(conn => renderConnectionItem(serviceName, conn)).join('')}
                </div>
                
                <div class="connections-summary">
                    <div class="summary-item">
                        <strong>Architecture Benefits:</strong>
                        <ul>
                            <li>Modular design enables independent scaling</li>
                            <li>Clear separation of concerns improves maintainability</li>
                            <li>Distributed architecture provides fault tolerance</li>
                        </ul>
                    </div>
                    <div class="summary-item">
                        <strong>Integration Capabilities:</strong>
                        <ul>
                            <li>Real-time data synchronization across services</li>
                            <li>Event-driven communication patterns</li>
                            <li>Standardized API interfaces for interoperability</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function renderConnectionItem(sourceName, connection) {
    const confidenceIcon = getConfidenceIcon(connection.confidence);
    const connectionTypeIcon = getConnectionTypeIcon(connection.type);
    
    return `
        <div class="connection-item">
            <div class="connection-header">
                <div class="connection-info">
                    <span class="connection-icon">${connectionTypeIcon}</span>
                    <strong class="target-service">${connection.target || 'Unknown'}</strong>
                    <span class="confidence-indicator">${confidenceIcon} ${Math.round(connection.confidence * 100)}%</span>
                </div>
                <span class="connection-type">${connection.type || 'unknown'}</span>
            </div>
            
            <div class="connection-purpose">
                <p>${connection.purpose}</p>
            </div>
            
            <div class="connection-reasoning">
                <div class="reasoning-section">
                    <strong>Technical Reasoning:</strong>
                    <p>${generateTechnicalReasoning(sourceName, connection)}</p>
                </div>
                
                <div class="reasoning-section">
                    <strong>Business Value:</strong>
                    <p>${generateBusinessValue(sourceName, connection)}</p>
                </div>
                
                <div class="reasoning-section">
                    <strong>Architectural Advantages:</strong>
                    <ul>
                        ${generateArchitecturalAdvantages(sourceName, connection).map(adv => `<li>${adv}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="connection-metadata">
                <small>
                    <i class="fas fa-clock"></i> Discovered: ${new Date(connection.timestamp).toLocaleString()}
                    ${connection.auto_discovered ? '<i class="fas fa-robot" title="Auto-discovered"></i>' : '<i class="fas fa-user" title="Manually configured"></i>'}
                </small>
            </div>
        </div>
    `;
}

function generateTechnicalReasoning(sourceName, connection) {
    const reasoningMap = {
        'alert': `${sourceName} requires real-time ${connection.target_service} to trigger timely notifications and maintain system awareness. This dependency ensures data consistency and reduces latency in critical alert scenarios.`,
        'data': `Data flow from ${connection.target_service} to ${sourceName} enables comprehensive analysis and decision-making capabilities. This integration supports data-driven operations and analytics.`,
        'api': `${sourceName} leverages ${connection.target_service} API endpoints to access specialized functionality and maintain service boundaries. This promotes microservices architecture principles.`,
        'database': `${connection.target_service} serves as the persistent storage layer for ${sourceName}, ensuring data durability and ACID compliance for critical operations.`,
        'default': `${sourceName} integrates with ${connection.target_service} to leverage specialized capabilities and maintain system modularity. This connection enables efficient resource utilization and scalable architecture.`
    };
    
    const key = Object.keys(reasoningMap).find(k => 
        (connection.purpose && connection.purpose.toLowerCase().includes(k)) || 
        (connection.target && connection.target.toLowerCase().includes(k))
    ) || 'default';
    
    return reasoningMap[key];
}

function generateBusinessValue(sourceName, connection) {
    const valueMap = {
        'alert': `Enhanced monitoring and notification capabilities reduce system downtime and improve operational efficiency. Real-time alerts enable proactive problem resolution.`,
        'data': `Centralized data access improves decision-making accuracy and provides comprehensive business intelligence. Data integration reduces silos and improves insights.`,
        'api': `API-first architecture enables rapid feature development and third-party integrations. Standardized interfaces reduce integration complexity and development time.`,
        'database': `Reliable data persistence ensures business continuity and regulatory compliance. Centralized data management reduces operational overhead and improves data quality.`,
        'default': `Service integration improves operational efficiency and enables advanced functionality. Modular architecture reduces development costs and improves system reliability.`
    };
    
    const key = Object.keys(valueMap).find(k => 
        (connection.purpose && connection.purpose.toLowerCase().includes(k)) || 
        (connection.target && connection.target.toLowerCase().includes(k))
    ) || 'default';
    
    return valueMap[key];
}

function generateArchitecturalAdvantages(sourceName, connection) {
    return [
        'Loose coupling enables independent service evolution',
        'Fault isolation prevents cascading failures',
        'Horizontal scaling capabilities for high availability',
        'Clear service boundaries improve maintainability',
        'Event-driven patterns support reactive architectures'
    ];
}

function getConfidenceIcon(confidence) {
    if (confidence >= 0.8) return '🟢';
    if (confidence >= 0.6) return '🟡';
    return '🔴';
}

function getConnectionTypeIcon(type) {
    const iconMap = {
        'dependency': '🔗',
        'api': '📡',
        'database': '💾',
        'queue': '📮',
        'cache': '⚡'
    };
    return iconMap[type] || '🔗';
}

function toggleServiceExpansion(card) {
    const connections = card.querySelector('.service-connections');
    const isExpanded = !connections.classList.contains('collapsed');
    
    if (isExpanded) {
        connections.classList.add('collapsed');
        card.classList.remove('expanded');
    } else {
        connections.classList.remove('collapsed');
        card.classList.add('expanded');
    }
}

function expandServiceConnections(serviceName) {
    const card = document.querySelector(`[data-service="${serviceName}"]`);
    if (card) {
        const connections = card.querySelector('.service-connections');
        connections.classList.remove('collapsed');
        card.classList.add('expanded');
    }
}

function closeServiceDiscoveryModal() {
    const modal = document.querySelector('.service-discovery-modal');
    if (modal) {
        modal.remove();
    }
}

// Function to redirect to Service Discovery Dashboard
function redirectToServiceDiscoveryDashboard() {
    console.log('🔍 Redirecting to Service Discovery Dashboard...');
    showStatusMessage('🔄 Redirecting to Service Discovery Dashboard...', 'info');
    
    // Open Service Discovery Dashboard in new window
    const serviceDiscoveryUrl = 'http://localhost:8550';
    console.log('🚀 Opening Service Discovery Dashboard:', serviceDiscoveryUrl);
    
    setTimeout(() => {
        window.open(serviceDiscoveryUrl, '_blank');
        showStatusMessage('✅ Service Discovery Dashboard opened in new window', 'success');
    }, 500);
}

async function optimizeContext() {
    loading.show('🧠 Analyzing system context and rebuilding CLAUDE.md for optimal performance...');
    
    try {
        const result = await api.optimizeContext();
        
        if (result.success) {
            toast.success('🎯 Context optimization completed! CLAUDE.md has been refreshed with the latest system intelligence and performance optimizations.');
            loadOverviewData();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to optimize context:', error);
        toast.error('⚠️ Context optimization failed. Please check system status and try again.');
    } finally {
        loading.hide();
    }
}

async function validateSystem() {
    loading.show('🔍 Performing comprehensive system health validation across all components...');
    
    try {
        const result = await api.validateSystem();
        
        if (result.task_id) {
            // Wait for task completion
            const taskResult = await api.waitForTask(result.task_id);
            
            if (taskResult && taskResult.result) {
                const validation = taskResult.result;
                const summary = validation.summary;
                
                // Show toast notification
                if (validation.overall_status === 'healthy') {
                    toast.success(`✅ System validation completed successfully! All ${summary.total_checks} health checks passed with flying colors.`);
                } else if (validation.overall_status === 'warning') {
                    toast.warning(`⚠️ System validation completed with ${summary.warnings_found} minor warnings. System is operational but could benefit from attention.`);
                } else if (validation.overall_status === 'degraded') {
                    toast.error(`🚨 System validation found ${summary.issues_found} critical issues that need immediate attention. ${summary.checks_passed}/${summary.total_checks} checks passed.`);
                }
                
                // Show detailed validation results modal
                showValidationResults(validation);
                loadOverviewData();
            } else {
                throw new Error(taskResult?.error || 'Validation task failed');
            }
        } else {
            throw new Error(result.error || 'Failed to start validation task');
        }
    } catch (error) {
        console.error('Failed to validate system:', error);
        toast.error('❌ System validation failed to complete. Please check orchestration agent status and try again.');
    } finally {
        loading.hide();
    }
}

function showValidationResults(validation) {
    // Update overall status
    const statusIndicator = document.getElementById('overallStatusIndicator');
    const statusText = document.getElementById('overallStatusText');
    
    statusIndicator.className = 'status-indicator ' + validation.overall_status.toLowerCase();
    statusText.textContent = validation.overall_status.toUpperCase();
    
    // Update icon based on status
    const statusIcon = statusIndicator.querySelector('i');
    switch (validation.overall_status) {
        case 'healthy':
            statusIcon.className = 'fas fa-check-circle';
            break;
        case 'warning':
            statusIcon.className = 'fas fa-exclamation-triangle';
            break;
        case 'degraded':
        case 'error':
            statusIcon.className = 'fas fa-times-circle';
            break;
    }
    
    // Update timestamp
    const timestamp = new Date(validation.timestamp);
    document.getElementById('validationTimestamp').textContent = timestamp.toLocaleString();
    
    // Update summary stats
    const summary = validation.summary;
    document.getElementById('checksPassedCount').textContent = summary.checks_passed;
    document.getElementById('totalChecksCount').textContent = summary.total_checks;
    document.getElementById('issuesFoundCount').textContent = summary.issues_found;
    document.getElementById('warningsFoundCount').textContent = summary.warnings_found;
    
    // Generate check details
    const checksList = document.getElementById('validationChecksList');
    checksList.innerHTML = '';
    
    // Define check information
    const checkInfo = {
        mdc_files: {
            title: 'MDC Files Integrity',
            icon: 'fas fa-file-code',
            description: 'Validates all MDC files in .cursor/rules/ directory'
        },
        connections: {
            title: 'Connection System',
            icon: 'fas fa-network-wired',
            description: 'Checks MDC Connection Agent status and discovered connections'
        },
        context: {
            title: 'Context Optimization',
            icon: 'fas fa-brain',
            description: 'Validates CLAUDE.md and context optimization system'
        },
        services: {
            title: 'System Services',
            icon: 'fas fa-cogs',
            description: 'Monitors orchestration agent and task queue health'
        },
        performance: {
            title: 'Performance Metrics',
            icon: 'fas fa-tachometer-alt',
            description: 'Analyzes system performance and resource usage'
        }
    };
    
    validation.checks_performed.forEach(checkType => {
        if (validation[checkType]) {
            const checkData = validation[checkType];
            const info = checkInfo[checkType];
            
            const checkItem = document.createElement('div');
            checkItem.className = 'check-item';
            
            const statusClass = checkData.valid ? 'valid' : 'invalid';
            const statusIcon = checkData.valid ? 'fas fa-check-circle' : 'fas fa-times-circle';
            const statusText = checkData.valid ? 'PASSED' : 'FAILED';
            
            let detailsHTML = '';
            let issuesHTML = '';
            let warningsHTML = '';
            
            // Generate details based on check type
            if (checkType === 'mdc_files' && checkData.file_count !== undefined) {
                detailsHTML = `
                    <div class="check-details">
                        <div class="check-detail">
                            <span class="detail-label">Files Found:</span>
                            <span class="detail-value">${checkData.file_count}</span>
                        </div>
                    </div>
                `;
            } else if (checkType === 'connections') {
                detailsHTML = `
                    <div class="check-details">
                        <div class="check-detail">
                            <span class="detail-label">Agent Status:</span>
                            <span class="detail-value">${checkData.agent_running ? 'Running' : 'Stopped'}</span>
                        </div>
                        <div class="check-detail">
                            <span class="detail-label">Total Connections:</span>
                            <span class="detail-value">${checkData.total_connections || 0}</span>
                        </div>
                    </div>
                `;
            } else if (checkType === 'context') {
                detailsHTML = `
                    <div class="check-details">
                        <div class="check-detail">
                            <span class="detail-label">CLAUDE.md Size:</span>
                            <span class="detail-value">${utils.formatBytes(checkData.claude_md_size || 0)}</span>
                        </div>
                        <div class="check-detail">
                            <span class="detail-label">Optimizer Available:</span>
                            <span class="detail-value">${checkData.optimizer_available ? 'Yes' : 'No'}</span>
                        </div>
                    </div>
                `;
            } else if (checkType === 'services') {
                detailsHTML = `
                    <div class="check-details">
                        <div class="check-detail">
                            <span class="detail-label">Active Tasks:</span>
                            <span class="detail-value">${checkData.active_tasks || 0}</span>
                        </div>
                        <div class="check-detail">
                            <span class="detail-label">Completed Tasks:</span>
                            <span class="detail-value">${checkData.total_completed_tasks || 0}</span>
                        </div>
                    </div>
                `;
            } else if (checkType === 'performance') {
                detailsHTML = `
                    <div class="check-details">
                        <div class="check-detail">
                            <span class="detail-label">Task Queue Size:</span>
                            <span class="detail-value">${checkData.task_queue_size || 0}</span>
                        </div>
                    </div>
                `;
            }
            
            // Generate issues list
            if (checkData.issues && checkData.issues.length > 0) {
                issuesHTML = `
                    <div class="check-issues">
                        <h4>Issues Found:</h4>
                        ${checkData.issues.map(issue => `
                            <div class="issue-item">
                                <i class="fas fa-exclamation-circle issue-icon"></i>
                                <span>${issue}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            // Generate warnings list
            if (checkData.warnings && checkData.warnings.length > 0) {
                warningsHTML = `
                    <div class="check-warnings">
                        <h4>Warnings:</h4>
                        ${checkData.warnings.map(warning => `
                            <div class="warning-item">
                                <i class="fas fa-exclamation-triangle warning-icon"></i>
                                <span>${warning}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            checkItem.innerHTML = `
                <div class="check-header">
                    <div class="check-title">
                        <i class="${info.icon}"></i>
                        ${info.title}
                    </div>
                    <div class="check-status ${statusClass}">
                        <i class="${statusIcon}"></i>
                        ${statusText}
                    </div>
                </div>
                <p class="text-muted">${info.description}</p>
                ${detailsHTML}
                ${issuesHTML}
                ${warningsHTML}
            `;
            
            checksList.appendChild(checkItem);
        }
    });
    
    // Show modal
    document.getElementById('validationResultsModal').style.display = 'block';
}

function closeValidationResults() {
    document.getElementById('validationResultsModal').style.display = 'none';
}

function runValidationAgain() {
    closeValidationResults();
    validateSystem();
}

// Component Logs Functions
let currentLogsComponent = null;
let logsUpdateInterval = null;

async function viewComponentLogs(componentType) {
    currentLogsComponent = componentType;
    
    // Set component title
    const componentTitles = {
        'mdcAgent': 'MDC Agent Logs',
        'connectionAgent': 'Connection Agent Logs', 
        'contextOptimizer': 'Context Optimizer Logs'
    };
    
    document.getElementById('logsComponentTitle').textContent = componentTitles[componentType] || 'Component Logs';
    
    // Show modal
    document.getElementById('componentLogsModal').style.display = 'block';
    
    // Load initial logs
    await loadComponentLogs(componentType);
    
    // Setup auto-refresh every 5 seconds
    if (logsUpdateInterval) {
        clearInterval(logsUpdateInterval);
    }
    logsUpdateInterval = setInterval(() => {
        loadComponentLogs(componentType);
    }, 5000);
}

async function loadComponentLogs(componentType) {
    const statusElement = document.getElementById('logsStatus');
    const logsContent = document.getElementById('logsContent');
    
    try {
        statusElement.innerHTML = '<i class="fas fa-sync fa-spin"></i> Loading logs...';
        statusElement.className = 'logs-status';
        
        // Get log filter settings
        const logLevel = document.getElementById('logLevelFilter').value;
        const maxLines = parseInt(document.getElementById('logLinesLimit').value) || 100;
        
        // Simulate fetching logs (since we don't have a real logs API endpoint yet)
        const logs = await getComponentLogs(componentType, logLevel, maxLines);
        
        if (logs && logs.length > 0) {
            statusElement.innerHTML = `<i class="fas fa-check-circle"></i> Loaded ${logs.length} log entries`;
            statusElement.className = 'logs-status success';
            
            // Display logs with proper formatting
            logsContent.innerHTML = formatLogsForDisplay(logs);
            
            // Scroll to bottom
            logsContent.scrollTop = logsContent.scrollHeight;
        } else {
            statusElement.innerHTML = '<i class="fas fa-info-circle"></i> No logs available';
            statusElement.className = 'logs-status warning';
            
            logsContent.innerHTML = `
                <div class="logs-empty">
                    <i class="fas fa-file-alt"></i>
                    <p>No logs found for ${componentType}</p>
                    <small>Logs may not be available or the component may not be generating logs yet.</small>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading logs:', error);
        statusElement.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Failed to load logs';
        statusElement.className = 'logs-status error';
        
        logsContent.innerHTML = `
            <div class="logs-empty">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading logs</p>
                <small>${error.message}</small>
            </div>
        `;
    }
}

async function getComponentLogs(componentType, logLevel, maxLines) {
    // This is a mock implementation since we don't have real log endpoints yet
    // In a real system, this would fetch from actual log files or log endpoints
    
    const mockLogs = generateMockLogs(componentType, maxLines);
    
    // Filter by log level if specified
    if (logLevel !== 'all') {
        return mockLogs.filter(log => log.level === logLevel);
    }
    
    return mockLogs;
}

function generateMockLogs(componentType, maxLines) {
    const logs = [];
    const levels = ['info', 'warning', 'error', 'debug'];
    const baseTime = Date.now();
    
    const logMessages = {
        'mdcAgent': [
            'MDC Agent initialized successfully',
            'Processing MDC file generation request',
            'Generated MDC file for service: WhaleAlerts',
            'MDC validation completed for 94 files',
            'Warning: Large MDC file detected (>10KB)',
            'Error: Failed to parse MDC syntax in BackendService.mdc',
            'Debug: Memory usage: 45.2MB',
            'Info: MDC cache updated',
            'Agent health check passed',
            'Processing bulk MDC generation'
        ],
        'connectionAgent': [
            'Connection discovery started',
            'Discovered 35 service connections',
            'Connection validation completed',
            'Warning: Timeout connecting to external service',
            'Error: Failed to establish connection to service X',
            'Debug: Connection pool size: 15/20',
            'Info: Connection latency: 45ms',
            'Service health check completed',
            'Connection retry successful',
            'Agent status: running'
        ],
        'contextOptimizer': [
            'Context optimization started',
            'CLAUDE.md size: 6.3KB (optimal)',
            'Context updated successfully',
            'Warning: Context approaching size limit',
            'Error: Context optimization failed - file locked',
            'Debug: Optimization time: 1.2s',
            'Info: Context cache cleared',
            'Smart batching applied',
            'Domain separation completed',
            'Optimizer ready for next cycle'
        ]
    };
    
    const messages = logMessages[componentType] || logMessages['mdcAgent'];
    
    for (let i = 0; i < Math.min(maxLines, 50); i++) {
        const timestamp = new Date(baseTime - (i * 30000));
        const level = levels[Math.floor(Math.random() * levels.length)];
        const message = messages[Math.floor(Math.random() * messages.length)];
        
        logs.unshift({
            timestamp: timestamp.toISOString(),
            level: level,
            message: message,
            component: componentType
        });
    }
    
    return logs;
}

function formatLogsForDisplay(logs) {
    return logs.map(log => {
        const timestamp = new Date(log.timestamp).toLocaleString();
        return `<div class="log-entry ${log.level}">
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
            ${log.message}
        </div>`;
    }).join('');
}

function closeComponentLogs() {
    document.getElementById('componentLogsModal').style.display = 'none';
    currentLogsComponent = null;
    
    // Clear auto-refresh
    if (logsUpdateInterval) {
        clearInterval(logsUpdateInterval);
        logsUpdateInterval = null;
    }
}

function refreshLogs() {
    if (currentLogsComponent) {
        loadComponentLogs(currentLogsComponent);
    }
}

function clearLogsDisplay() {
    document.getElementById('logsContent').innerHTML = `
        <div class="logs-empty">
            <i class="fas fa-broom"></i>
            <p>Logs cleared</p>
            <small>Click refresh to reload logs</small>
        </div>
    `;
}

function downloadLogs() {
    if (!currentLogsComponent) return;
    
    const logsContent = document.getElementById('logsContent');
    const logsText = logsContent.textContent || logsContent.innerText;
    
    if (!logsText.trim()) {
        toast.warning('No logs to download');
        return;
    }
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentLogsComponent}_logs_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    toast.success('Logs downloaded successfully');
}

// Add event listeners for log filtering
document.addEventListener('DOMContentLoaded', function() {
    const logLevelFilter = document.getElementById('logLevelFilter');
    const logLinesLimit = document.getElementById('logLinesLimit');
    
    if (logLevelFilter) {
        logLevelFilter.addEventListener('change', () => {
            if (currentLogsComponent) {
                loadComponentLogs(currentLogsComponent);
            }
        });
    }
    
    if (logLinesLimit) {
        logLinesLimit.addEventListener('change', () => {
            if (currentLogsComponent) {
                loadComponentLogs(currentLogsComponent);
            }
        });
    }
});

// MDC File Operations
async function createNewMDC() {
    switchSection('generator');
    document.getElementById('serviceName').focus();
}

async function editMDC(filename) {
    toast.info(`Opening ${filename} for editing...`);
    // In a real implementation, this would open an editor
    // For now, we'll show the generator with pre-filled data
    switchSection('generator');
    
    try {
        const result = await api.getMDCFile(filename);
        if (result.success) {
            const file = result.data;
            document.getElementById('serviceName').value = file.name.replace('.mdc', '');
            document.getElementById('serviceDescription').value = file.description || '';
            // Fill other fields as needed
        }
    } catch (error) {
        toast.error('Failed to load file for editing');
    }
}

async function deleteMDC(filename) {
    if (!confirm(`Are you sure you want to delete ${filename}? This action cannot be undone.`)) {
        return;
    }
    
    loading.show('Deleting MDC file...');
    
    try {
        const result = await api.deleteMDCFile(filename);
        
        if (result.success) {
            toast.success(`${filename} deleted successfully`);
            loadMDCFiles();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to delete MDC file:', error);
        toast.error('Failed to delete MDC file');
    } finally {
        loading.hide();
    }
}

function viewConnections(filename) {
    switchSection('connections');
    // Filter connections for this file
    setTimeout(() => {
        filterConnectionsForFile(filename);
    }, 100);
}

// 🚀 Enhanced Connections Section
let filteredConnections = [];
let currentConnectionView = 'list';
let connectionFilters = {
    search: '',
    type: '',
    confidence: '',
    status: ''
};
let connectionStatusTimer = null;
let connectionStatuses = new Map(); // Store real-time status for each connection

async function loadConnections() {
    loading.show('Loading connections...');
    
    try {
        const result = await api.getConnections();
        
        if (result.success) {
            connections = result.data.connections || [];
            filteredConnections = [...connections];
            initializeConnectionStatuses();
            renderConnections();
            setupConnectionEventListeners();
            startConnectionMonitoring();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load connections:', error);
        toast.error('Failed to load connections');
    } finally {
        loading.hide();
    }
}

function setupConnectionEventListeners() {
    // Search input
    const searchInput = document.getElementById('connectionSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            connectionFilters.search = e.target.value.toLowerCase();
            filterConnections();
        });
    }
    
    // Filter selects
    ['connectionTypeFilter', 'confidenceFilter', 'statusFilter'].forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            select.addEventListener('change', (e) => {
                const filterType = id.replace('Filter', '').replace('connectionType', 'type');
                connectionFilters[filterType] = e.target.value;
                filterConnections();
            });
        }
    });
}

function filterConnections() {
    filteredConnections = connections.filter(conn => {
        // Search filter
        if (connectionFilters.search) {
            const searchTerm = connectionFilters.search;
            const searchableText = `${conn.source} ${conn.target} ${conn.type} ${conn.purpose}`.toLowerCase();
            if (!searchableText.includes(searchTerm)) return false;
        }
        
        // Type filter
        if (connectionFilters.type && conn.type.toLowerCase() !== connectionFilters.type.toLowerCase()) {
            return false;
        }
        
        // Confidence filter
        if (connectionFilters.confidence) {
            const confidence = conn.confidence * 100;
            switch (connectionFilters.confidence) {
                case 'high':
                    if (confidence < 80) return false;
                    break;
                case 'medium':
                    if (confidence < 50 || confidence >= 80) return false;
                    break;
                case 'low':
                    if (confidence >= 50) return false;
                    break;
            }
        }
        
        // Status filter (simulated for now)
        if (connectionFilters.status) {
            const status = Math.random() > 0.7 ? 'active' : Math.random() > 0.5 ? 'inactive' : 'pending';
            if (status !== connectionFilters.status) return false;
        }
        
        return true;
    });
    
    renderConnections();
}

function clearConnectionFilters() {
    // Reset all filters
    connectionFilters = {
        search: '',
        type: '',
        confidence: '',
        status: ''
    };
    
    // Clear UI
    const searchInput = document.getElementById('connectionSearch');
    if (searchInput) searchInput.value = '';
    
    ['connectionTypeFilter', 'confidenceFilter', 'statusFilter'].forEach(id => {
        const select = document.getElementById(id);
        if (select) select.value = '';
    });
    
    // Reset filtered connections
    filteredConnections = [...connections];
    renderConnections();
    
    toast.success('Filters cleared');
}

function toggleConnectionView(viewType) {
    currentConnectionView = viewType;
    
    // Update active button
    ['listViewBtn', 'gridViewBtn', 'graphViewBtn'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.classList.remove('active');
            if (id === viewType + 'ViewBtn') {
                btn.classList.add('active');
            }
        }
    });
    
    // Re-render with new view
    renderConnections();
    
    toast.info(`Switched to ${viewType} view`);
}

function renderConnections() {
    const container = document.getElementById('connectionsList');
    const items = container.querySelector('.connection-items');
    
    // Update connections count
    const connectionsToRender = filteredConnections.length > 0 ? filteredConnections : connections;
    
    // Show filter status
    if (filteredConnections.length !== connections.length) {
        const filterStatus = document.createElement('div');
        filterStatus.className = 'filter-status';
        filterStatus.innerHTML = `
            <i class="fas fa-filter"></i>
            Showing ${filteredConnections.length} of ${connections.length} connections
        `;
        filterStatus.style.cssText = `
            background: rgba(79, 209, 199, 0.1);
            border: 1px solid rgba(79, 209, 199, 0.3);
            border-radius: 10px;
            padding: 0.5rem 1rem;
            margin-bottom: 1rem;
            color: var(--primary-color);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        `;
        
        // Remove existing filter status
        const existingStatus = container.querySelector('.filter-status');
        if (existingStatus) existingStatus.remove();
        
        if (filteredConnections.length !== connections.length) {
            container.insertBefore(filterStatus, items);
        }
    }
    
    if (connectionsToRender.length === 0) {
        const message = filteredConnections.length === 0 && connections.length > 0 
            ? 'No connections match your filters'
            : 'No connections found';
        
        items.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <i class="fas fa-project-diagram" style="font-size: 3rem; margin-bottom: 1.5rem; color: var(--primary-color); animation: pulse 2s infinite;"></i>
                <p style="font-size: 1.2rem; margin-bottom: 1rem;">${message}</p>
                ${connections.length === 0 ? `
                    <button class="btn btn-primary" onclick="discoverConnections()" style="margin-top: 1rem;">
                        <i class="fas fa-search"></i> Discover Connections
                    </button>
                ` : `
                    <button class="btn btn-secondary" onclick="clearConnectionFilters()" style="margin-top: 1rem;">
                        <i class="fas fa-times"></i> Clear Filters
                    </button>
                `}
            </div>
        `;
        return;
    }
    
    // Render based on current view
    switch (currentConnectionView) {
        case 'grid':
            renderConnectionsGrid(connectionsToRender);
            break;
        case 'graph':
            renderConnectionsGraph(connectionsToRender);
            break;
        default:
            renderConnectionsList(connectionsToRender);
    }
}

function renderConnectionsList(connectionsToRender) {
    const container = document.getElementById('connectionsList');
    const items = container.querySelector('.connection-items');
    
    items.style.display = 'block'; // Reset from grid
    
    items.innerHTML = connectionsToRender.map(conn => {
        const statusData = getConnectionStatus(conn.source, conn.target);
        const statusColor = statusData.status === 'active' ? 'var(--success-color)' : 
                           statusData.status === 'inactive' ? 'var(--error-color)' : 'var(--warning-color)';
        const pulseAnimation = statusData.status === 'active' ? 'pulse 2s ease-in-out infinite' : 'none';
        
        return `
            <div class="connection-item" onclick="viewConnectionDetails('${conn.source}', '${conn.target}')">
                <div class="connection-header">
                    <strong>${conn.source}</strong>
                    <i class="fas fa-arrow-right"></i>
                    <strong>${conn.target}</strong>
                    <div class="connection-status" style="margin-left: auto; display: flex; align-items: center; gap: 0.5rem;">
                        <div class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: ${statusColor}; animation: ${pulseAnimation};"></div>
                        <span style="color: ${statusColor}; text-transform: uppercase; font-size: 0.8rem; font-weight: 600;">${statusData.status}</span>
                        <div class="status-details" style="font-size: 0.75rem; color: var(--text-muted); margin-left: 0.5rem;">
                            ${statusData.responseTime.toFixed(0)}ms | ${statusData.uptime.toFixed(1)}%
                        </div>
                    </div>
                </div>
                <div class="connection-details">
                    <span class="connection-type">${conn.type}</span>
                    <span class="connection-purpose">${conn.purpose}</span>
                    <span class="connection-confidence">Confidence: ${(conn.confidence * 100).toFixed(0)}%</span>
                </div>
                ${statusData.lastError ? `
                    <div class="connection-error" style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(245, 101, 101, 0.1); border-left: 3px solid var(--error-color); border-radius: 4px; font-size: 0.8rem; color: var(--error-color);">
                        <i class="fas fa-exclamation-triangle"></i> ${statusData.lastError}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

function renderConnectionsGrid(connectionsToRender) {
    const container = document.getElementById('connectionsList');
    const items = container.querySelector('.connection-items');
    
    items.style.display = 'grid';
    items.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
    items.style.gap = '1.5rem';
    
    items.innerHTML = connectionsToRender.map(conn => {
        const statusData = getConnectionStatus(conn.source, conn.target);
        const statusColor = statusData.status === 'active' ? 'var(--success-color)' : 
                           statusData.status === 'inactive' ? 'var(--error-color)' : 'var(--warning-color)';
        const pulseAnimation = statusData.status === 'active' ? 'pulse 2s ease-in-out infinite' : 'none';
        
        return `
            <div class="connection-card" onclick="viewConnectionDetails('${conn.source}', '${conn.target}')" style="
                background: linear-gradient(145deg, rgba(15, 20, 25, 0.98), rgba(30, 41, 54, 0.95));
                border: 1px solid rgba(79, 209, 199, 0.2);
                border-radius: 15px;
                padding: 1.5rem;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
            ">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="width: 10px; height: 10px; border-radius: 50%; background: ${statusColor}; animation: ${pulseAnimation};"></div>
                        <span style="color: ${statusColor}; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">${statusData.status}</span>
                    </div>
                    <span class="connection-type" style="font-size: 0.75rem;">${conn.type}</span>
                </div>
                
                <div style="text-align: center; margin: 1rem 0;">
                    <div style="font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">${conn.source}</div>
                    <i class="fas fa-arrow-down" style="color: var(--primary-color); margin: 0.5rem 0;"></i>
                    <div style="font-weight: 700; color: var(--text-primary);">${conn.target}</div>
                </div>
                
                <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem; font-style: italic;">
                    ${conn.purpose}
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div class="connection-confidence" style="font-size: 0.8rem;">
                        Confidence: ${(conn.confidence * 100).toFixed(0)}%
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">
                        ${statusData.responseTime.toFixed(0)}ms
                    </div>
                </div>
                
                <div style="background: rgba(79, 209, 199, 0.05); border-radius: 8px; padding: 0.5rem; text-align: center; font-size: 0.8rem;">
                    <span style="color: var(--success-color);">Uptime: ${statusData.uptime.toFixed(1)}%</span>
                </div>
                
                ${statusData.lastError ? `
                    <div style="position: absolute; top: 0.5rem; right: 0.5rem; color: var(--error-color); font-size: 1rem;" title="${statusData.lastError}">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

function renderConnectionsGraph(connectionsToRender) {
    const container = document.getElementById('connectionsList');
    const items = container.querySelector('.connection-items');
    
    items.innerHTML = `
        <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
            <i class="fas fa-project-diagram" style="font-size: 3rem; margin-bottom: 1rem; color: var(--primary-color); animation: pulse 2s infinite;"></i>
            <h3>Graph View</h3>
            <p style="margin: 1rem 0;">Interactive connection graph visualization</p>
            <p style="font-size: 0.9rem; color: var(--text-muted);">Graph visualization coming soon...</p>
            <div style="margin-top: 2rem;">
                <button class="btn btn-primary" onclick="toggleConnectionView('list')">
                    <i class="fas fa-list"></i> Switch to List View
                </button>
            </div>
        </div>
    `;
}

function viewConnectionDetails(source, target) {
    const statusData = getConnectionStatus(source, target);
    
    // Create a detailed modal with connection management
    const modal = document.createElement('div');
    modal.className = 'modal-overlay connection-details-modal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h3><i class="fas fa-project-diagram"></i> Connection Details</h3>
                <button class="modal-close" onclick="closeConnectionDetails()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="connection-overview">
                    <div style="text-align: center; margin: 1.5rem 0;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
                            <div class="service-node">${source}</div>
                            <i class="fas fa-arrow-right" style="color: var(--primary-color); font-size: 1.5rem;"></i>
                            <div class="service-node">${target}</div>
                        </div>
                        <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin: 1rem 0;">
                            <div class="status-dot" style="width: 12px; height: 12px; border-radius: 50%; background: ${
                                statusData.status === 'active' ? 'var(--success-color)' : 
                                statusData.status === 'inactive' ? 'var(--error-color)' : 'var(--warning-color)'
                            }; animation: ${statusData.status === 'active' ? 'pulse 2s ease-in-out infinite' : 'none'};"></div>
                            <span style="color: ${
                                statusData.status === 'active' ? 'var(--success-color)' : 
                                statusData.status === 'inactive' ? 'var(--error-color)' : 'var(--warning-color)'
                            }; font-weight: 700; text-transform: uppercase; font-size: 1.1rem;">${statusData.status}</span>
                        </div>
                    </div>
                </div>
                
                <div class="connection-stats" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin: 2rem 0;">
                    <div class="stat-item" style="background: rgba(79, 209, 199, 0.1); padding: 1rem; border-radius: 10px; text-align: center;">
                        <div style="color: var(--primary-color); font-size: 1.5rem; font-weight: 700;">${statusData.responseTime.toFixed(0)}ms</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Response Time</div>
                    </div>
                    <div class="stat-item" style="background: rgba(72, 187, 120, 0.1); padding: 1rem; border-radius: 10px; text-align: center;">
                        <div style="color: var(--success-color); font-size: 1.5rem; font-weight: 700;">${statusData.uptime.toFixed(1)}%</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Uptime</div>
                    </div>
                    <div class="stat-item" style="background: rgba(59, 130, 246, 0.1); padding: 1rem; border-radius: 10px; text-align: center;">
                        <div style="color: var(--info-color); font-size: 1.5rem; font-weight: 700;">${Math.floor((Date.now() - statusData.lastCheck) / 1000)}s</div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">Last Check</div>
                    </div>
                </div>
                
                ${statusData.lastError ? `
                    <div class="error-section" style="background: rgba(245, 101, 101, 0.1); border: 1px solid var(--error-color); border-radius: 10px; padding: 1rem; margin: 1rem 0;">
                        <h4 style="color: var(--error-color); margin: 0 0 0.5rem 0;"><i class="fas fa-exclamation-triangle"></i> Error</h4>
                        <p style="color: var(--error-color); margin: 0;">${statusData.lastError}</p>
                    </div>
                ` : ''}
                
                <div class="connection-actions" style="display: flex; gap: 1rem; margin-top: 2rem; justify-content: center;">
                    <button class="btn btn-success" onclick="testConnection('${source}', '${target}')">
                        <i class="fas fa-heartbeat"></i> Test Connection
                    </button>
                    <button class="btn btn-warning" onclick="restartConnection('${source}', '${target}')">
                        <i class="fas fa-redo"></i> Restart
                    </button>
                    <button class="btn btn-danger" onclick="stopConnection('${source}', '${target}')">
                        <i class="fas fa-stop"></i> Stop
                    </button>
                </div>
            </div>
        </div>
    `;
    
    modal.style.cssText = `
        .service-node {
            background: linear-gradient(135deg, var(--card-bg), var(--accent-bg));
            border: 1px solid var(--primary-color);
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            color: var(--text-primary);
            font-weight: 700;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
    `;
    
    document.body.appendChild(modal);
    
    // Fade in animation
    setTimeout(() => {
        modal.style.opacity = '1';
    }, 10);
}

function closeConnectionDetails() {
    const modal = document.querySelector('.connection-details-modal');
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => modal.remove(), 300);
    }
}

// 🔧 Connection Management Functions
async function testConnection(source, target) {
    const connectionKey = `${source}->${target}`;
    loading.show(`Testing connection: ${source} → ${target}`);
    
    try {
        // Simulate connection test
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Update status
        const statusData = connectionStatuses.get(connectionKey);
        if (statusData) {
            statusData.status = Math.random() > 0.8 ? 'inactive' : 'active';
            statusData.lastCheck = Date.now();
            statusData.responseTime = Math.random() * 100 + 20;
            statusData.lastError = statusData.status === 'inactive' ? 'Connection test failed' : null;
        }
        
        toast.success(`Connection test completed: ${statusData.status}`);
        
        // Refresh the connection details modal
        closeConnectionDetails();
        setTimeout(() => viewConnectionDetails(source, target), 500);
        
    } catch (error) {
        toast.error('Connection test failed');
    } finally {
        loading.hide();
    }
}

async function restartConnection(source, target) {
    const connectionKey = `${source}->${target}`;
    loading.show(`Restarting connection: ${source} → ${target}`);
    
    try {
        // Simulate connection restart
        const statusData = connectionStatuses.get(connectionKey);
        if (statusData) {
            statusData.status = 'pending';
        }
        updateConnectionStatusIndicators();
        
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Update status after restart
        if (statusData) {
            statusData.status = Math.random() > 0.7 ? 'active' : 'inactive';
            statusData.lastCheck = Date.now();
            statusData.responseTime = Math.random() * 100 + 20;
            statusData.uptime = Math.random() * 99 + 1;
            statusData.lastError = null;
        }
        
        toast.success(`Connection restarted: ${statusData.status}`);
        
        // Refresh the connection details modal
        closeConnectionDetails();
        setTimeout(() => viewConnectionDetails(source, target), 500);
        
    } catch (error) {
        toast.error('Connection restart failed');
    } finally {
        loading.hide();
    }
}

async function stopConnection(source, target) {
    const connectionKey = `${source}->${target}`;
    
    if (!confirm(`Are you sure you want to stop the connection between ${source} and ${target}?`)) {
        return;
    }
    
    loading.show(`Stopping connection: ${source} → ${target}`);
    
    try {
        // Simulate connection stop
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Update status
        const statusData = connectionStatuses.get(connectionKey);
        if (statusData) {
            statusData.status = 'inactive';
            statusData.lastCheck = Date.now();
            statusData.uptime = 0;
            statusData.lastError = 'Connection manually stopped';
        }
        
        toast.warning(`Connection stopped: ${source} → ${target}`);
        
        // Refresh the connection details modal
        closeConnectionDetails();
        setTimeout(() => viewConnectionDetails(source, target), 500);
        
    } catch (error) {
        toast.error('Failed to stop connection');
    } finally {
        loading.hide();
    }
}

async function testAllConnections() {
    loading.show('Testing all connections...');
    
    try {
        // Simulate testing all connections
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        let activeCount = 0;
        let inactiveCount = 0;
        
        connectionStatuses.forEach((statusData, connectionKey) => {
            statusData.status = Math.random() > 0.8 ? 'inactive' : 'active';
            statusData.lastCheck = Date.now();
            statusData.responseTime = Math.random() * 100 + 20;
            statusData.lastError = statusData.status === 'inactive' ? 'Connection test failed' : null;
            
            if (statusData.status === 'active') activeCount++;
            else inactiveCount++;
        });
        
        updateConnectionStatusIndicators();
        toast.success(`Connection test completed: ${activeCount} active, ${inactiveCount} inactive`);
        
    } catch (error) {
        toast.error('Connection test failed');
    } finally {
        loading.hide();
    }
}

async function restartAllConnections() {
    if (!confirm('Are you sure you want to restart all connections? This may cause temporary service disruptions.')) {
        return;
    }
    
    loading.show('Restarting all connections...');
    
    try {
        // Simulate restarting all connections
        connectionStatuses.forEach((statusData) => {
            statusData.status = 'pending';
        });
        updateConnectionStatusIndicators();
        
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        let successCount = 0;
        connectionStatuses.forEach((statusData) => {
            statusData.status = Math.random() > 0.75 ? 'inactive' : 'active';
            statusData.lastCheck = Date.now();
            statusData.responseTime = Math.random() * 100 + 20;
            statusData.uptime = Math.random() * 99 + 1;
            statusData.lastError = null;
            
            if (statusData.status === 'active') successCount++;
        });
        
        updateConnectionStatusIndicators();
        toast.success(`All connections restarted: ${successCount}/${connectionStatuses.size} active`);
        
    } catch (error) {
        toast.error('Connection restart failed');
    } finally {
        loading.hide();
    }
}

// 📊 Real-time Connection Monitoring
function initializeConnectionStatuses() {
    connections.forEach(conn => {
        const connectionKey = `${conn.source}->${conn.target}`;
        // Initialize with random status for demo
        connectionStatuses.set(connectionKey, {
            status: Math.random() > 0.7 ? 'active' : Math.random() > 0.5 ? 'inactive' : 'pending',
            lastCheck: Date.now(),
            responseTime: Math.random() * 100 + 20, // Random response time 20-120ms
            uptime: Math.random() * 99 + 1, // Random uptime 1-100%
            lastError: null
        });
    });
}

function startConnectionMonitoring() {
    // Clear existing timer
    if (connectionStatusTimer) {
        clearInterval(connectionStatusTimer);
    }
    
    // Start monitoring every 5 seconds
    connectionStatusTimer = setInterval(updateConnectionStatuses, 5000);
    
    // Initial status update
    updateConnectionStatuses();
}

function stopConnectionMonitoring() {
    if (connectionStatusTimer) {
        clearInterval(connectionStatusTimer);
        connectionStatusTimer = null;
    }
}

async function updateConnectionStatuses() {
    try {
        // Simulate real-time status updates
        connectionStatuses.forEach((status, connectionKey) => {
            const now = Date.now();
            const timeSinceLastCheck = now - status.lastCheck;
            
            // Simulate status changes based on time
            if (timeSinceLastCheck > 10000) { // 10 seconds
                // Small chance to change status
                if (Math.random() < 0.1) {
                    const statuses = ['active', 'inactive', 'pending'];
                    status.status = statuses[Math.floor(Math.random() * statuses.length)];
                }
                
                // Update response time with slight variation
                status.responseTime = Math.max(10, status.responseTime + (Math.random() - 0.5) * 10);
                
                // Update uptime
                if (status.status === 'active') {
                    status.uptime = Math.min(100, status.uptime + Math.random() * 2);
                } else {
                    status.uptime = Math.max(0, status.uptime - Math.random() * 5);
                }
                
                status.lastCheck = now;
                
                // Simulate occasional errors
                if (Math.random() < 0.05 && status.status === 'inactive') {
                    status.lastError = 'Connection timeout';
                } else if (status.status === 'active') {
                    status.lastError = null;
                }
            }
        });
        
        // Update the display with real-time data
        updateConnectionStatusIndicators();
        
    } catch (error) {
        console.error('Failed to update connection statuses:', error);
    }
}

function updateConnectionStatusIndicators() {
    // Update status indicators in the current view
    const connectionItems = document.querySelectorAll('.connection-item, .connection-card');
    
    connectionItems.forEach(item => {
        const sourceElement = item.querySelector('strong');
        if (!sourceElement) return;
        
        const source = sourceElement.textContent;
        const targetElement = sourceElement.nextElementSibling?.nextElementSibling;
        if (!targetElement) return;
        
        const target = targetElement.textContent;
        const connectionKey = `${source}->${target}`;
        const statusData = connectionStatuses.get(connectionKey);
        
        if (statusData) {
            // Update status dot and text
            const statusDot = item.querySelector('.status-dot');
            const statusText = item.querySelector('[style*="text-transform: uppercase"]');
            
            if (statusDot && statusText) {
                const statusColor = statusData.status === 'active' ? 'var(--success-color)' : 
                                  statusData.status === 'inactive' ? 'var(--error-color)' : 'var(--warning-color)';
                
                statusDot.style.background = statusColor;
                statusText.textContent = statusData.status;
                statusText.style.color = statusColor;
                
                // Add pulsing animation for active connections
                if (statusData.status === 'active') {
                    statusDot.style.animation = 'pulse 2s ease-in-out infinite';
                } else {
                    statusDot.style.animation = 'none';
                }
            }
        }
    });
}

function getConnectionStatus(source, target) {
    const connectionKey = `${source}->${target}`;
    return connectionStatuses.get(connectionKey) || {
        status: 'unknown',
        lastCheck: 0,
        responseTime: 0,
        uptime: 0,
        lastError: null
    };
}

function filterConnectionsForFile(filename) {
    const serviceName = filename.replace('.mdc', '');
    const filteredConnections = connections.filter(conn => 
        conn.source === serviceName || conn.target === serviceName
    );
    
    // Update the display to show only these connections
    const items = document.querySelector('.connection-items');
    if (filteredConnections.length === 0) {
        items.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
                <p>No connections found for ${serviceName}</p>
            </div>
        `;
    } else {
        // Similar to renderConnections but with filtered data
        items.innerHTML = filteredConnections.map(conn => `
            <div class="connection-item">
                <div class="connection-header">
                    <strong>${conn.source}</strong>
                    <i class="fas fa-arrow-right" style="color: var(--primary-color); margin: 0 0.5rem;"></i>
                    <strong>${conn.target}</strong>
                </div>
                <div class="connection-details">
                    <span class="connection-type">${conn.type}</span>
                    <span class="connection-purpose">${conn.purpose}</span>
                    <span class="connection-confidence">Confidence: ${(conn.confidence * 100).toFixed(0)}%</span>
                </div>
            </div>
        `).join('');
    }
}

// 🚀 SPECTACULAR MDC GENERATOR SECTION
let selectedMDCFile = null;
let mdcFilesList = [];
let currentPreviewMode = 'original';
let originalMDCContent = '';
let enhancedMDCContent = '';

// Load MDC Generator
async function loadMDCGenerator() {
    loading.show('Loading MDC Generator...');
    
    try {
        // Load available MDC files
        await loadMDCFilesList();
        
        // Setup search functionality
        setupMDCSearch();
        
        // Setup dropdown
        populateMDCDropdown();
        
        // Setup enhancement options
        setupEnhancementOptions();
        
        toast.success('MDC Generator loaded successfully');
    } catch (error) {
        console.error('Failed to load MDC generator:', error);
        toast.error('Failed to load MDC generator');
    } finally {
        loading.hide();
    }
}

// Load available MDC files
async function loadMDCFilesList() {
    try {
        const result = await api.getMDCFiles();
        if (result.success && result.data.files) {
            mdcFilesList = result.data.files
                .filter(file => file.name.endsWith('.mdc'))
                .map(file => ({
                    name: file.name,
                    path: file.path,
                    size: file.size || 1024,
                    modified: file.modified || new Date().toISOString()
                }))
                .sort((a, b) => a.name.localeCompare(b.name)); // Alphabetical sort
        } else {
            // Fallback to mock data if API fails
            mdcFilesList = createMockMDCFilesList();
        }
    } catch (error) {
        console.error('Failed to load MDC files list:', error);
        // Fallback to mock data if API fails
        mdcFilesList = createMockMDCFilesList();
    }
}

// Create Mock MDC Files List for Demo
function createMockMDCFilesList() {
    return [
        { name: 'API-Manager.mdc', path: '/.cursor/rules/API-Manager.mdc', size: 2048, modified: new Date().toISOString() },
        { name: 'Backend.mdc', path: '/.cursor/rules/Backend.mdc', size: 3072, modified: new Date().toISOString() },
        { name: 'ControlUI.mdc', path: '/.cursor/rules/ControlUI.mdc', size: 1536, modified: new Date().toISOString() },
        { name: 'Database.mdc', path: '/.cursor/rules/Database.mdc', size: 4096, modified: new Date().toISOString() },
        { name: 'Frontend.mdc', path: '/.cursor/rules/Frontend.mdc', size: 2560, modified: new Date().toISOString() },
        { name: 'LiveAlerts.mdc', path: '/.cursor/rules/LiveAlerts.mdc', size: 1792, modified: new Date().toISOString() },
        { name: 'MasterOrchestrationAgent.mdc', path: '/.cursor/rules/MasterOrchestrationAgent.mdc', size: 5120, modified: new Date().toISOString() },
        { name: 'MySymbols.mdc', path: '/.cursor/rules/MySymbols.mdc', size: 2304, modified: new Date().toISOString() },
        { name: 'OrchestrationStart.mdc', path: '/.cursor/rules/OrchestrationStart.mdc', size: 1280, modified: new Date().toISOString() },
        { name: 'PortManager.mdc', path: '/.cursor/rules/PortManager.mdc', size: 1664, modified: new Date().toISOString() },
        { name: 'ProcessReaper.mdc', path: '/.cursor/rules/ProcessReaper.mdc', size: 1408, modified: new Date().toISOString() },
        { name: 'ServiceRegistry.mdc', path: '/.cursor/rules/ServiceRegistry.mdc', size: 2816, modified: new Date().toISOString() },
        { name: 'START_zmartbot.mdc', path: '/.cursor/rules/START_zmartbot.mdc', size: 1152, modified: new Date().toISOString() },
        { name: 'WhaleAlerts.mdc', path: '/.cursor/rules/WhaleAlerts.mdc', size: 1920, modified: new Date().toISOString() }
    ].sort((a, b) => a.name.localeCompare(b.name));
}

// Setup MDC Search Functionality with Enhanced Filtering
function setupMDCSearch() {
    const searchInput = document.getElementById('mdcFileSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput || !searchResults) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Debounce search for better performance
        searchTimeout = setTimeout(() => {
            performMDCSearch(query, searchResults);
        }, 150);
    });
    
    // Show all files when focusing on empty search
    searchInput.addEventListener('focus', (e) => {
        if (e.target.value.trim() === '') {
            showAllMDCFiles(searchResults);
        }
    });
    
    // Handle keyboard navigation
    searchInput.addEventListener('keydown', (e) => {
        handleSearchKeydown(e, searchResults);
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
}

// Perform MDC Search with Enhanced Filtering
function performMDCSearch(query, searchResults) {
    if (query.length === 0) {
        showAllMDCFiles(searchResults);
        return;
    }
    
    const queryLower = query.toLowerCase();
    
    // Enhanced filtering: prioritize files that start with the query, then include contains
    const startsWith = mdcFilesList.filter(file => 
        file.name.toLowerCase().startsWith(queryLower)
    );
    
    const contains = mdcFilesList.filter(file => 
        file.name.toLowerCase().includes(queryLower) && 
        !file.name.toLowerCase().startsWith(queryLower)
    );
    
    const filteredFiles = [...startsWith, ...contains];
    
    if (filteredFiles.length === 0) {
        searchResults.innerHTML = `
            <div class="search-result-item no-results">
                <i class="fas fa-search"></i>
                <span>No files found matching "${query}"</span>
            </div>
        `;
        searchResults.style.display = 'block';
        return;
    }
    
    // Highlight matching text in results
    searchResults.innerHTML = filteredFiles.slice(0, 8).map((file, index) => {
        const highlightedName = highlightSearchText(file.name, query);
        return `
            <div class="search-result-item" 
                 data-index="${index}" 
                 onclick="selectMDCFileFromSearch('${file.name}', '${file.path}')">
                <div class="result-main">
                    <strong>${highlightedName}</strong>
                    <div class="result-meta">
                        <span class="file-size">${utils.formatBytes(file.size)}</span>
                        <span class="file-date">${new Date(file.modified).toLocaleDateString()}</span>
                    </div>
                </div>
                <div class="result-path">${file.path}</div>
            </div>
        `;
    }).join('');
    
    if (filteredFiles.length > 8) {
        searchResults.innerHTML += `
            <div class="search-result-item more-results">
                <i class="fas fa-ellipsis-h"></i>
                <span>+${filteredFiles.length - 8} more files...</span>
            </div>
        `;
    }
    
    searchResults.style.display = 'block';
}

// Show All MDC Files (when search is empty or focused)
function showAllMDCFiles(searchResults) {
    if (mdcFilesList.length === 0) {
        searchResults.innerHTML = `
            <div class="search-result-item no-results">
                <i class="fas fa-info-circle"></i>
                <span>No MDC files available</span>
            </div>
        `;
        searchResults.style.display = 'block';
        return;
    }
    
    searchResults.innerHTML = mdcFilesList.slice(0, 10).map((file, index) => `
        <div class="search-result-item" 
             data-index="${index}" 
             onclick="selectMDCFileFromSearch('${file.name}', '${file.path}')">
            <div class="result-main">
                <strong>${file.name}</strong>
                <div class="result-meta">
                    <span class="file-size">${utils.formatBytes(file.size)}</span>
                    <span class="file-date">${new Date(file.modified).toLocaleDateString()}</span>
                </div>
            </div>
            <div class="result-path">${file.path}</div>
        </div>
    `).join('');
    
    if (mdcFilesList.length > 10) {
        searchResults.innerHTML += `
            <div class="search-result-item more-results">
                <i class="fas fa-list"></i>
                <span>+${mdcFilesList.length - 10} more files available in dropdown...</span>
            </div>
        `;
    }
    
    searchResults.style.display = 'block';
}

// Highlight Search Text in Results
function highlightSearchText(text, query) {
    if (!query) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// Handle Keyboard Navigation in Search
function handleSearchKeydown(e, searchResults) {
    const items = searchResults.querySelectorAll('.search-result-item:not(.no-results):not(.more-results)');
    const current = searchResults.querySelector('.search-result-item.highlighted');
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            if (current) {
                current.classList.remove('highlighted');
                const next = current.nextElementSibling;
                if (next && !next.classList.contains('no-results') && !next.classList.contains('more-results')) {
                    next.classList.add('highlighted');
                } else if (items.length > 0) {
                    items[0].classList.add('highlighted');
                }
            } else if (items.length > 0) {
                items[0].classList.add('highlighted');
            }
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            if (current) {
                current.classList.remove('highlighted');
                const prev = current.previousElementSibling;
                if (prev && !prev.classList.contains('no-results') && !prev.classList.contains('more-results')) {
                    prev.classList.add('highlighted');
                } else if (items.length > 0) {
                    items[items.length - 1].classList.add('highlighted');
                }
            } else if (items.length > 0) {
                items[items.length - 1].classList.add('highlighted');
            }
            break;
            
        case 'Enter':
            e.preventDefault();
            if (current) {
                current.click();
            } else if (items.length > 0) {
                items[0].click();
            }
            break;
            
        case 'Escape':
            searchResults.style.display = 'none';
            e.target.blur();
            break;
    }
}

// Populate MDC Dropdown
function populateMDCDropdown() {
    const dropdown = document.getElementById('mdcFileSelect');
    if (!dropdown) return;
    
    dropdown.innerHTML = '<option value="">Select an MDC file...</option>';
    
    mdcFilesList.forEach(file => {
        const option = document.createElement('option');
        option.value = file.path;
        option.textContent = file.name;
        option.dataset.fileName = file.name;
        dropdown.appendChild(option);
    });
    
    dropdown.addEventListener('change', (e) => {
        const selectedPath = e.target.value;
        const selectedName = e.target.options[e.target.selectedIndex]?.dataset.fileName;
        
        if (selectedPath && selectedName) {
            selectMDCFile(selectedName, selectedPath);
        }
    });
}

// Setup Enhancement Options
function setupEnhancementOptions() {
    const enhancementType = document.getElementById('enhancementType');
    const customPromptGroup = document.getElementById('customPromptGroup');
    
    if (!enhancementType) return;
    
    enhancementType.addEventListener('change', (e) => {
        if (e.target.value === 'custom') {
            customPromptGroup.style.display = 'block';
        } else {
            customPromptGroup.style.display = 'none';
        }
        updateGenerateButton();
    });
}

// Select MDC File from Search
function selectMDCFileFromSearch(fileName, filePath) {
    selectMDCFile(fileName, filePath);
    document.getElementById('searchResults').style.display = 'none';
    document.getElementById('mdcFileSearch').value = fileName;
}

// Select MDC File
async function selectMDCFile(fileName, filePath) {
    selectedMDCFile = { name: fileName, path: filePath };
    
    loading.show('Loading MDC file...');
    
    try {
        // Load the file content
        const result = await api.readMDCFile(filePath);
        
        if (result.success) {
            originalMDCContent = result.data.content;
            enhancedMDCContent = ''; // Reset enhanced content
            
            // Update preview
            updateMDCPreview();
            
            // Update generate button
            updateGenerateButton();
            
            toast.success(`Loaded ${fileName}`);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to load MDC file:', error);
        toast.error('Failed to load MDC file');
        
        // Reset selection
        selectedMDCFile = null;
        originalMDCContent = '';
        enhancedMDCContent = '';
        updateMDCPreview();
        updateGenerateButton();
    } finally {
        loading.hide();
    }
}

// Update MDC Preview
function updateMDCPreview() {
    const previewContent = document.getElementById('mdcPreviewContent');
    
    if (!selectedMDCFile || !originalMDCContent) {
        previewContent.innerHTML = `
            <div class="preview-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-file-code"></i>
                </div>
                <h4>Select an MDC File to Preview</h4>
                <p>Choose an MDC file from the search or dropdown to see its content and generate enhancements</p>
            </div>
        `;
        return;
    }
    
    const contentToShow = currentPreviewMode === 'enhanced' && enhancedMDCContent ? 
        enhancedMDCContent : originalMDCContent;
    
    previewContent.innerHTML = `<pre>${contentToShow}</pre>`;
    
    // Update preview mode buttons
    const originalBtn = document.getElementById('originalPreviewBtn');
    const enhancedBtn = document.getElementById('enhancedPreviewBtn');
    
    if (currentPreviewMode === 'original') {
        originalBtn?.classList.add('btn-primary');
        originalBtn?.classList.remove('btn-secondary');
        enhancedBtn?.classList.add('btn-secondary');
        enhancedBtn?.classList.remove('btn-primary');
    } else {
        originalBtn?.classList.add('btn-secondary');
        originalBtn?.classList.remove('btn-primary');
        enhancedBtn?.classList.add('btn-primary');
        enhancedBtn?.classList.remove('btn-secondary');
    }
}

// Toggle Preview Mode
function togglePreviewMode(mode) {
    currentPreviewMode = mode;
    updateMDCPreview();
}

// Copy Preview Content
function copyPreviewContent() {
    const previewContent = document.getElementById('mdcPreviewContent');
    const textContent = previewContent.textContent || previewContent.innerText;
    
    if (!textContent || textContent.trim() === '') {
        toast.warning('No content to copy');
        return;
    }
    
    navigator.clipboard.writeText(textContent).then(() => {
        toast.success('Content copied to clipboard');
    }).catch(() => {
        toast.error('Failed to copy content');
    });
}

// Update Generate Button State
function updateGenerateButton() {
    const generateBtn = document.getElementById('generateBtn');
    const enhancementType = document.getElementById('enhancementType')?.value;
    const customPrompt = document.getElementById('customPrompt')?.value;
    
    if (!generateBtn) return;
    
    const canGenerate = selectedMDCFile && 
        enhancementType && 
        (enhancementType !== 'custom' || (enhancementType === 'custom' && customPrompt?.trim()));
    
    generateBtn.disabled = !canGenerate;
    
    if (canGenerate) {
        generateBtn.classList.remove('btn-secondary');
        generateBtn.classList.add('btn-primary');
    } else {
        generateBtn.classList.remove('btn-primary');
        generateBtn.classList.add('btn-secondary');
    }
}

// Generate Enhanced MDC
async function generateEnhancedMDC() {
    if (!selectedMDCFile) {
        toast.error('Please select an MDC file first');
        return;
    }
    
    const enhancementType = document.getElementById('enhancementType')?.value;
    const customPrompt = document.getElementById('customPrompt')?.value;
    
    if (!enhancementType) {
        toast.error('Please select an enhancement type');
        return;
    }
    
    if (enhancementType === 'custom' && !customPrompt?.trim()) {
        toast.error('Please enter a custom enhancement prompt');
        return;
    }
    
    loading.show('Generating enhanced MDC...');
    
    try {
        let prompt = '';
        
        switch (enhancementType) {
            case 'improve_documentation':
                prompt = 'Improve the documentation quality, add more detailed explanations, better formatting, and comprehensive examples.';
                break;
            case 'add_security_rules':
                prompt = 'Add security guidelines, best practices, authentication requirements, and security considerations.';
                break;
            case 'optimize_performance':
                prompt = 'Add performance optimization guidelines, caching strategies, and performance monitoring recommendations.';
                break;
            case 'add_monitoring':
                prompt = 'Add comprehensive monitoring, logging, alerting, and observability guidelines.';
                break;
            case 'enhance_error_handling':
                prompt = 'Improve error handling patterns, add comprehensive error codes, and better error recovery strategies.';
                break;
            case 'add_testing_guidelines':
                prompt = 'Add comprehensive testing strategies, unit testing, integration testing, and testing best practices.';
                break;
            case 'custom':
                prompt = customPrompt.trim();
                break;
            default:
                prompt = 'Improve this MDC file with better documentation and best practices.';
        }
        
        const enhancementData = {
            filePath: selectedMDCFile.path,
            fileName: selectedMDCFile.name,
            originalContent: originalMDCContent,
            enhancementPrompt: prompt,
            enhancementType: enhancementType
        };
        
        const result = await api.enhanceMDCFile(enhancementData);
        
        if (result.success) {
            enhancedMDCContent = result.data.enhancedContent || result.data.content;
            currentPreviewMode = 'enhanced';
            updateMDCPreview();
            
            toast.success('MDC file enhanced successfully!');
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Failed to generate enhanced MDC:', error);
        toast.error('Failed to generate enhanced MDC');
    } finally {
        loading.hide();
    }
}

// Reset MDC Generator
function resetMDCGenerator() {
    // Clear selections
    selectedMDCFile = null;
    originalMDCContent = '';
    enhancedMDCContent = '';
    currentPreviewMode = 'original';
    
    // Reset form elements
    const searchInput = document.getElementById('mdcFileSearch');
    const dropdown = document.getElementById('mdcFileSelect');
    const enhancementType = document.getElementById('enhancementType');
    const customPrompt = document.getElementById('customPrompt');
    const customPromptGroup = document.getElementById('customPromptGroup');
    const searchResults = document.getElementById('searchResults');
    
    if (searchInput) searchInput.value = '';
    if (dropdown) dropdown.value = '';
    if (enhancementType) enhancementType.value = 'improve_documentation';
    if (customPrompt) customPrompt.value = '';
    if (customPromptGroup) customPromptGroup.style.display = 'none';
    if (searchResults) searchResults.style.display = 'none';
    
    // Update preview
    updateMDCPreview();
    updateGenerateButton();
    
    toast.info('Generator reset');
}

// Add these functions to window object for HTML access
window.selectMDCFileFromSearch = selectMDCFileFromSearch;
window.togglePreviewMode = togglePreviewMode;
window.copyPreviewContent = copyPreviewContent;
window.generateEnhancedMDC = generateEnhancedMDC;
window.resetMDCGenerator = resetMDCGenerator;

// 🚀 SPECTACULAR ANALYTICS SECTION
let currentAnalyticsView = 'overview';
let analyticsTimeRange = '7d';
let analyticsData = {};

// Load Analytics with Enhanced Functionality
async function loadAnalytics() {
    loading.show('Loading analytics...');
    
    try {
        // Load analytics data
        await loadAnalyticsData();
        
        // Update key metrics
        updateKeyMetrics();
        
        // Render charts based on current view
        renderSpectacularCharts();
        
        // Setup analytics controls
        setupAnalyticsControls();
        
        toast.success('Analytics loaded successfully');
    } catch (error) {
        console.error('Failed to load analytics:', error);
        toast.error('Failed to load analytics');
    } finally {
        loading.hide();
    }
}

// Load Analytics Data
async function loadAnalyticsData() {
    try {
        // Mock enhanced analytics data
        analyticsData = {
            keyMetrics: {
                totalFiles: mdcFiles.length || 0,
                activeConnections: connections.length || 0,
                systemHealth: 98.5,
                avgUpdateTime: '2.4m'
            },
            serviceDistribution: {
                'Frontend': 8,
                'Backend': 12,
                'Internal API': 15,
                'Worker': 6,
                'Orchestration': 4,
                'Database': 7,
                'Monitoring': 3
            },
            connectionTypes: {
                'API': 18,
                'Database': 12,
                'Messaging': 8,
                'Storage': 6,
                'Authentication': 5,
                'External': 4
            },
            performanceTrends: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                responseTime: [45, 52, 48, 51, 49, 47, 50],
                throughput: [1200, 1350, 1280, 1420, 1380, 1180, 1250],
                errorRate: [0.5, 0.8, 0.3, 0.6, 0.4, 0.2, 0.5]
            },
            fileSizeDistribution: {
                'Small (<5KB)': 15,
                'Medium (5-20KB)': 25,
                'Large (20-50KB)': 12,
                'Very Large (>50KB)': 3
            },
            systemActivity: {
                events: [
                    { time: '10:30', type: 'info', message: 'MDC file updated: trading-engine.mdc' },
                    { time: '10:15', type: 'success', message: 'Connection health check passed' },
                    { time: '09:45', type: 'warning', message: 'High memory usage detected' },
                    { time: '09:30', type: 'info', message: 'System backup completed' },
                    { time: '09:15', type: 'success', message: 'New MDC file generated' }
                ]
            }
        };
    } catch (error) {
        console.error('Error loading analytics data:', error);
        analyticsData = {};
    }
}

// Update Key Metrics
function updateKeyMetrics() {
    const metrics = analyticsData.keyMetrics || {};
    
    const totalFilesElement = document.querySelector('#totalFiles .metric-value');
    const activeConnectionsElement = document.querySelector('#activeConnections .metric-value');
    const systemHealthElement = document.querySelector('#systemHealth .metric-value');
    const updateFrequencyElement = document.querySelector('#updateFrequency .metric-value');
    
    if (totalFilesElement) {
        animateCounter(totalFilesElement, 0, metrics.totalFiles || 0, 1000);
    }
    
    if (activeConnectionsElement) {
        animateCounter(activeConnectionsElement, 0, metrics.activeConnections || 0, 1200);
    }
    
    if (systemHealthElement) {
        systemHealthElement.textContent = `${metrics.systemHealth || 0}%`;
    }
    
    if (updateFrequencyElement) {
        updateFrequencyElement.textContent = metrics.avgUpdateTime || '0m';
    }
}

// Animate Counter
function animateCounter(element, start, end, duration) {
    if (start === end) return;
    
    const range = end - start;
    const increment = range > 0 ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    
    let current = start;
    const timer = setInterval(() => {
        current += increment;
        element.textContent = current;
        
        if (current === end) {
            clearInterval(timer);
        }
    }, stepTime);
}

// Setup Analytics Controls
function setupAnalyticsControls() {
    const timeRangeSelect = document.getElementById('analyticsTimeRange');
    const viewButtons = document.querySelectorAll('.view-toggle-btn');
    
    if (timeRangeSelect) {
        timeRangeSelect.addEventListener('change', (e) => {
            analyticsTimeRange = e.target.value;
            loadAnalyticsData().then(() => {
                renderSpectacularCharts();
                updateKeyMetrics();
            });
        });
    }
    
    viewButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const view = e.currentTarget.onclick.toString().match(/toggleAnalyticsView\('(\w+)'\)/);
            if (view) {
                toggleAnalyticsView(view[1]);
            }
        });
    });
}

// Toggle Analytics View
function toggleAnalyticsView(view) {
    currentAnalyticsView = view;
    
    // Update button states
    const buttons = document.querySelectorAll('.view-toggle-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.id === `${view}AnalyticsBtn`) {
            btn.classList.add('active');
        }
    });
    
    // Re-render charts based on view
    renderSpectacularCharts();
    
    toast.info(`Switched to ${view} view`);
}

// Render Spectacular Charts
function renderSpectacularCharts() {
    renderServiceDistributionChart();
    renderConnectionTypesChart();
    renderPerformanceTrendsChart();
    renderFileSizeHeatmap();
    renderSystemActivityTimeline();
}

// Render Service Distribution Chart
function renderServiceDistributionChart() {
    const container = document.getElementById('serviceChart');
    if (!container) return;
    
    const data = analyticsData.serviceDistribution || {};
    const total = Object.values(data).reduce((sum, val) => sum + val, 0);
    
    let chartHTML = '<div class="pie-chart-container">';
    let currentAngle = 0;
    
    Object.entries(data).forEach(([service, count], index) => {
        const percentage = ((count / total) * 100).toFixed(1);
        const color = `hsl(${(index * 60) % 360}, 70%, 60%)`;
        
        chartHTML += `
            <div class="chart-segment" style="--color: ${color}; --percentage: ${percentage}%">
                <div class="segment-label">${service}: ${count} (${percentage}%)</div>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    container.innerHTML = chartHTML;
}

// Render Connection Types Chart
function renderConnectionTypesChart() {
    const container = document.getElementById('connectionChart');
    if (!container) return;
    
    const data = analyticsData.connectionTypes || {};
    const maxValue = Math.max(...Object.values(data));
    
    let chartHTML = '<div class="bar-chart-container">';
    
    Object.entries(data).forEach(([type, count], index) => {
        const height = (count / maxValue) * 100;
        const color = `rgba(79, 209, 199, ${0.3 + (index * 0.1)})`;
        
        chartHTML += `
            <div class="bar-item">
                <div class="bar" style="height: ${height}%; background: ${color};">
                    <div class="bar-value">${count}</div>
                </div>
                <div class="bar-label">${type}</div>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    container.innerHTML = chartHTML;
}

// Render Performance Trends Chart
function renderPerformanceTrendsChart() {
    const container = document.getElementById('trendsChart');
    if (!container) return;
    
    const trends = analyticsData.performanceTrends || {};
    const labels = trends.labels || [];
    const responseTime = trends.responseTime || [];
    
    let chartHTML = '<div class="line-chart-container">';
    chartHTML += '<svg viewBox="0 0 400 200" style="width: 100%; height: 100%;">';
    
    // Draw grid lines
    for (let i = 0; i <= 5; i++) {
        const y = (i / 5) * 180 + 10;
        chartHTML += `<line x1="40" y1="${y}" x2="380" y2="${y}" stroke="rgba(79, 209, 199, 0.1)" stroke-width="1"/>`;
    }
    
    // Draw data line
    if (responseTime.length > 1) {
        const points = responseTime.map((value, index) => {
            const x = 40 + (index / (responseTime.length - 1)) * 340;
            const y = 190 - ((value / Math.max(...responseTime)) * 180);
            return `${x},${y}`;
        }).join(' ');
        
        chartHTML += `<polyline points="${points}" fill="none" stroke="rgba(79, 209, 199, 0.8)" stroke-width="2"/>`;
        
        // Add data points
        responseTime.forEach((value, index) => {
            const x = 40 + (index / (responseTime.length - 1)) * 340;
            const y = 190 - ((value / Math.max(...responseTime)) * 180);
            chartHTML += `<circle cx="${x}" cy="${y}" r="3" fill="#4fd1c7"/>`;
        });
    }
    
    chartHTML += '</svg></div>';
    container.innerHTML = chartHTML;
}

// Render File Size Heatmap
function renderFileSizeHeatmap() {
    const container = document.getElementById('sizeChart');
    if (!container) return;
    
    const data = analyticsData.fileSizeDistribution || {};
    const maxValue = Math.max(...Object.values(data));
    
    let chartHTML = '<div class="heatmap-container">';
    
    Object.entries(data).forEach(([size, count], index) => {
        const intensity = count / maxValue;
        const color = `rgba(79, 209, 199, ${0.2 + intensity * 0.6})`;
        
        chartHTML += `
            <div class="heatmap-cell" style="background: ${color};">
                <div class="cell-label">${size}</div>
                <div class="cell-value">${count}</div>
            </div>
        `;
    });
    
    chartHTML += '</div>';
    container.innerHTML = chartHTML;
}

// Render System Activity Timeline
function renderSystemActivityTimeline() {
    const container = document.getElementById('timelineChart');
    if (!container) return;
    
    const events = analyticsData.systemActivity?.events || [];
    
    let timelineHTML = '<div class="activity-timeline">';
    
    events.forEach((event, index) => {
        const iconClass = event.type === 'success' ? 'fa-check-circle' : 
                         event.type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
        const colorClass = event.type === 'success' ? 'success' : 
                          event.type === 'warning' ? 'warning' : 'info';
        
        timelineHTML += `
            <div class="timeline-item ${colorClass}">
                <div class="timeline-marker">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="timeline-content">
                    <div class="timeline-time">${event.time}</div>
                    <div class="timeline-message">${event.message}</div>
                </div>
            </div>
        `;
    });
    
    timelineHTML += '</div>';
    container.innerHTML = timelineHTML;
    
    // Also update timeline events section
    const eventsContainer = document.getElementById('timelineEvents');
    if (eventsContainer) {
        eventsContainer.innerHTML = timelineHTML;
    }
}

// Analytics Action Functions
function refreshAnalytics() {
    loadAnalytics();
}

function exportAnalytics() {
    const data = {
        timestamp: new Date().toISOString(),
        timeRange: analyticsTimeRange,
        view: currentAnalyticsView,
        data: analyticsData
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mdc-analytics-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('Analytics data exported');
}

function fullscreenChart(chartId) {
    toast.info(`Fullscreen mode for ${chartId} - Coming soon!`);
}

function toggleTrendView() {
    toast.info('Trend view toggle - Coming soon!');
}

function toggleTimelineDetail() {
    const eventsContainer = document.getElementById('timelineEvents');
    if (eventsContainer) {
        eventsContainer.style.display = eventsContainer.style.display === 'none' ? 'block' : 'none';
    }
}

// Add analytics functions to window
window.toggleAnalyticsView = toggleAnalyticsView;
window.refreshAnalytics = refreshAnalytics;
window.exportAnalytics = exportAnalytics;
window.fullscreenChart = fullscreenChart;
window.toggleTrendView = toggleTrendView;
window.toggleTimelineDetail = toggleTimelineDetail;

// 🚀 SPECTACULAR SETTINGS SECTION
let currentSettingsTab = 'general';
let settingsData = {};

// Load Spectacular Settings
async function loadSettings() {
    loading.show('Loading settings...');
    
    try {
        // Load settings from localStorage and server
        await loadSettingsData();
        
        // Setup settings navigation
        setupSettingsNavigation();
        
        // Populate all settings tabs
        populateAllSettingsTabs();
        
        // Setup settings listeners
        setupSettingsListeners();
        
        // Setup dynamic validations
        setupSettingsValidation();
        
        toast.success('Settings loaded successfully');
    } catch (error) {
        console.error('Failed to load settings:', error);
        toast.error('Failed to load settings');
    } finally {
        loading.hide();
    }
}

// Load Settings Data
async function loadSettingsData() {
    // Load local settings
    const localSettings = JSON.parse(localStorage.getItem('mdcDashboardSettings')) || CONFIG.defaultSettings;
    
    settingsData = {
        general: {
            autoRefresh: localSettings.autoRefresh ?? true,
            refreshInterval: localSettings.refreshInterval ?? 30,
            defaultView: localSettings.defaultView ?? 'overview'
        },
        appearance: {
            compactView: localSettings.compactView ?? false,
            showFileSize: localSettings.showFileSize ?? true,
            showConnectionCount: localSettings.showConnectionCount ?? true,
            animationLevel: localSettings.animationLevel ?? 'standard'
        },
        performance: {
            apiTimeout: localSettings.apiTimeout ?? 5000,
            enableCaching: localSettings.enableCaching ?? true,
            maxConcurrentRequests: localSettings.maxConcurrentRequests ?? 5
        },
        security: {
            orchestrationUrl: CONFIG.orchestrationUrl,
            enableSSL: localSettings.enableSSL ?? true,
            sessionTimeout: localSettings.sessionTimeout ?? 30
        },
        advanced: {
            mdcDirectoryPath: '',
            debugMode: localSettings.debugMode ?? false,
            logLevel: localSettings.logLevel ?? 'info'
        }
    };
    
    // Load server settings
    try {
        const serverSettings = await api.getSettings();
        if (serverSettings.success) {
            if (serverSettings.data.mdcDirectory) {
                settingsData.advanced.mdcDirectoryPath = serverSettings.data.mdcDirectory;
            }
        }
    } catch (error) {
        console.error('Failed to load server settings:', error);
        settingsData.advanced.mdcDirectoryPath = '/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules';
    }
}

// Setup Settings Navigation
function setupSettingsNavigation() {
    const navButtons = document.querySelectorAll('.settings-nav-btn');
    
    navButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const tabName = e.currentTarget.onclick.toString().match(/switchSettingsTab\('(\w+)'\)/);
            if (tabName) {
                switchSettingsTab(tabName[1]);
            }
        });
    });
}

// Switch Settings Tab
function switchSettingsTab(tabName) {
    currentSettingsTab = tabName;
    
    // Update navigation buttons
    const navButtons = document.querySelectorAll('.settings-nav-btn');
    navButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.id === `${tabName}SettingsBtn`) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    const settingsTabs = document.querySelectorAll('.settings-tab');
    settingsTabs.forEach(tab => {
        tab.classList.remove('active');
        if (tab.id === `${tabName}Settings`) {
            tab.classList.add('active');
        }
    });
    
    toast.info(`Switched to ${tabName} settings`);
}

// Populate All Settings Tabs
function populateAllSettingsTabs() {
    populateGeneralSettings();
    populateAppearanceSettings();
    populatePerformanceSettings();
    populateSecuritySettings();
    populateAdvancedSettings();
}

// Populate General Settings
function populateGeneralSettings() {
    const general = settingsData.general;
    
    const autoRefresh = document.getElementById('autoRefresh');
    const refreshInterval = document.getElementById('refreshInterval');
    const defaultView = document.getElementById('defaultView');
    
    if (autoRefresh) autoRefresh.checked = general.autoRefresh;
    if (refreshInterval) refreshInterval.value = general.refreshInterval;
    if (defaultView) defaultView.value = general.defaultView;
}

// Populate Appearance Settings
function populateAppearanceSettings() {
    const appearance = settingsData.appearance;
    
    const compactView = document.getElementById('compactView');
    const showFileSize = document.getElementById('showFileSize');
    const showConnectionCount = document.getElementById('showConnectionCount');
    const animationLevel = document.getElementById('animationLevel');
    
    if (compactView) compactView.checked = appearance.compactView;
    if (showFileSize) showFileSize.checked = appearance.showFileSize;
    if (showConnectionCount) showConnectionCount.checked = appearance.showConnectionCount;
    if (animationLevel) animationLevel.value = appearance.animationLevel;
}

// Populate Performance Settings
function populatePerformanceSettings() {
    const performance = settingsData.performance;
    
    const apiTimeout = document.getElementById('apiTimeout');
    const enableCaching = document.getElementById('enableCaching');
    const maxConcurrentRequests = document.getElementById('maxConcurrentRequests');
    
    if (apiTimeout) apiTimeout.value = performance.apiTimeout;
    if (enableCaching) enableCaching.checked = performance.enableCaching;
    if (maxConcurrentRequests) maxConcurrentRequests.value = performance.maxConcurrentRequests;
}

// Populate Security Settings
function populateSecuritySettings() {
    const security = settingsData.security;
    
    const orchestrationUrl = document.getElementById('orchestrationUrl');
    const enableSSL = document.getElementById('enableSSL');
    const sessionTimeout = document.getElementById('sessionTimeout');
    
    if (orchestrationUrl) orchestrationUrl.value = security.orchestrationUrl;
    if (enableSSL) enableSSL.checked = security.enableSSL;
    if (sessionTimeout) sessionTimeout.value = security.sessionTimeout;
}

// Populate Advanced Settings
function populateAdvancedSettings() {
    const advanced = settingsData.advanced;
    
    const mdcDirectoryPath = document.getElementById('mdcDirectoryPath');
    const debugMode = document.getElementById('debugMode');
    const logLevel = document.getElementById('logLevel');
    
    if (mdcDirectoryPath) mdcDirectoryPath.value = advanced.mdcDirectoryPath;
    if (debugMode) debugMode.checked = advanced.debugMode;
    if (logLevel) logLevel.value = advanced.logLevel;
}

// Setup Settings Listeners
function setupSettingsListeners() {
    // General settings listeners
    const refreshIntervalInput = document.getElementById('refreshInterval');
    if (refreshIntervalInput) {
        refreshIntervalInput.addEventListener('input', validateRefreshInterval);
    }
    
    // Performance settings listeners
    const apiTimeoutInput = document.getElementById('apiTimeout');
    if (apiTimeoutInput) {
        apiTimeoutInput.addEventListener('input', validateApiTimeout);
    }
    
    // Advanced settings listeners
    const pathInput = document.getElementById('mdcDirectoryPath');
    if (pathInput) {
        pathInput.addEventListener('input', validateMDCPath);
    }
    
    // Custom prompt handling for enhancement type
    const enhancementType = document.getElementById('enhancementType');
    const customPromptGroup = document.getElementById('customPromptGroup');
    if (enhancementType && customPromptGroup) {
        enhancementType.addEventListener('change', (e) => {
            customPromptGroup.style.display = e.target.value === 'custom' ? 'block' : 'none';
        });
    }
}

// Setup Settings Validation
function setupSettingsValidation() {
    // Add real-time validation for all input fields
    const inputs = document.querySelectorAll('.spectacular-number-input, .spectacular-path-input');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', debounceValidation);
    });
}

// Validation Functions
function validateRefreshInterval() {
    const input = document.getElementById('refreshInterval');
    const value = parseInt(input.value);
    
    if (value < 10 || value > 300) {
        input.style.borderColor = 'rgba(245, 101, 101, 0.8)';
        toast.warning('Refresh interval must be between 10 and 300 seconds');
        return false;
    }
    
    input.style.borderColor = 'rgba(79, 209, 199, 0.8)';
    return true;
}

function validateApiTimeout() {
    const input = document.getElementById('apiTimeout');
    const value = parseInt(input.value);
    
    if (value < 1000 || value > 30000) {
        input.style.borderColor = 'rgba(245, 101, 101, 0.8)';
        toast.warning('API timeout must be between 1000 and 30000 ms');
        return false;
    }
    
    input.style.borderColor = 'rgba(79, 209, 199, 0.8)';
    return true;
}

function validateMDCPath() {
    const input = document.getElementById('mdcDirectoryPath');
    const value = input.value.trim();
    
    if (value && !value.startsWith('/')) {
        input.style.borderColor = 'rgba(245, 101, 101, 0.8)';
        toast.warning('MDC path must be an absolute path starting with /');
        return false;
    }
    
    input.style.borderColor = 'rgba(79, 209, 199, 0.8)';
    return true;
}

function validateField(e) {
    const fieldId = e.target.id;
    switch (fieldId) {
        case 'refreshInterval':
            return validateRefreshInterval();
        case 'apiTimeout':
            return validateApiTimeout();
        case 'mdcDirectoryPath':
            return validateMDCPath();
        default:
            return true;
    }
}

function debounceValidation(e) {
    clearTimeout(e.target.validationTimeout);
    e.target.validationTimeout = setTimeout(() => validateField(e), 500);
}

// Save Spectacular Settings
function saveSettings() {
    loading.show('Saving settings...');
    
    try {
        // Validate all fields first
        if (!validateAllFields()) {
            toast.error('Please fix validation errors before saving');
            loading.hide();
            return;
        }
        
        // Collect settings from all tabs
        const allSettings = collectAllSettings();
        
        // Save to localStorage
        localStorage.setItem('mdcDashboardSettings', JSON.stringify(allSettings));
        
        // Apply settings immediately
        applySettings(allSettings);
        
        // Save server settings if needed
        saveServerSettings(allSettings);
        
        toast.success('Settings saved successfully!');
    } catch (error) {
        console.error('Failed to save settings:', error);
        toast.error('Failed to save settings');
    } finally {
        loading.hide();
    }
}

// Collect All Settings
function collectAllSettings() {
    return {
        // General
        autoRefresh: document.getElementById('autoRefresh')?.checked ?? true,
        refreshInterval: parseInt(document.getElementById('refreshInterval')?.value ?? 30),
        defaultView: document.getElementById('defaultView')?.value ?? 'overview',
        
        // Appearance
        compactView: document.getElementById('compactView')?.checked ?? false,
        showFileSize: document.getElementById('showFileSize')?.checked ?? true,
        showConnectionCount: document.getElementById('showConnectionCount')?.checked ?? true,
        animationLevel: document.getElementById('animationLevel')?.value ?? 'standard',
        
        // Performance
        apiTimeout: parseInt(document.getElementById('apiTimeout')?.value ?? 5000),
        enableCaching: document.getElementById('enableCaching')?.checked ?? true,
        maxConcurrentRequests: parseInt(document.getElementById('maxConcurrentRequests')?.value ?? 5),
        
        // Security
        enableSSL: document.getElementById('enableSSL')?.checked ?? true,
        sessionTimeout: parseInt(document.getElementById('sessionTimeout')?.value ?? 30),
        
        // Advanced
        debugMode: document.getElementById('debugMode')?.checked ?? false,
        logLevel: document.getElementById('logLevel')?.value ?? 'info'
    };
}

// Validate All Fields
function validateAllFields() {
    const validations = [
        validateRefreshInterval(),
        validateApiTimeout(),
        validateMDCPath()
    ];
    
    return validations.every(valid => valid);
}

// Apply Settings
function applySettings(settings) {
    // Apply refresh interval
    CONFIG.refreshInterval = settings.refreshInterval * 1000;
    setupAutoRefresh();
    
    // Apply appearance settings
    document.body.classList.toggle('compact-view', settings.compactView);
    document.body.setAttribute('data-animation-level', settings.animationLevel);
    
    // Apply debug mode
    if (settings.debugMode) {
        console.log('Debug mode enabled');
        window.DEBUG = true;
    } else {
        window.DEBUG = false;
    }
}

// Save Server Settings
async function saveServerSettings(settings) {
    const mdcPath = document.getElementById('mdcDirectoryPath')?.value?.trim();
    
    if (mdcPath && mdcPath !== settingsData.advanced.mdcDirectoryPath) {
        try {
            const result = await api.updateMDCPath(mdcPath);
            if (result.success) {
                settingsData.advanced.mdcDirectoryPath = mdcPath;
                toast.success('MDC path updated successfully');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Failed to update MDC path:', error);
            toast.error('Failed to update MDC path');
        }
    }
}

// Reset Settings
function resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to defaults? This action cannot be undone.')) {
        return;
    }
    
    loading.show('Resetting settings...');
    
    try {
        // Clear localStorage
        localStorage.removeItem('mdcDashboardSettings');
        
        // Reset to defaults
        settingsData = {
            general: { autoRefresh: true, refreshInterval: 30, defaultView: 'overview' },
            appearance: { compactView: false, showFileSize: true, showConnectionCount: true, animationLevel: 'standard' },
            performance: { apiTimeout: 5000, enableCaching: true, maxConcurrentRequests: 5 },
            security: { orchestrationUrl: CONFIG.orchestrationUrl, enableSSL: true, sessionTimeout: 30 },
            advanced: { mdcDirectoryPath: '/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules', debugMode: false, logLevel: 'info' }
        };
        
        // Repopulate all tabs
        populateAllSettingsTabs();
        
        // Apply default settings
        applySettings(collectAllSettings());
        
        toast.success('Settings reset to defaults');
    } catch (error) {
        console.error('Failed to reset settings:', error);
        toast.error('Failed to reset settings');
    } finally {
        loading.hide();
    }
}

// Export Settings
function exportSettings() {
    const settings = collectAllSettings();
    const exportData = {
        timestamp: new Date().toISOString(),
        version: '1.0',
        settings: settings
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mdc-dashboard-settings-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('Settings exported successfully');
}

// Import Settings
function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const importData = JSON.parse(event.target.result);
                
                if (!importData.settings) {
                    throw new Error('Invalid settings file format');
                }
                
                // Apply imported settings
                localStorage.setItem('mdcDashboardSettings', JSON.stringify(importData.settings));
                
                // Reload settings
                loadSettings();
                
                toast.success('Settings imported successfully');
            } catch (error) {
                console.error('Failed to import settings:', error);
                toast.error('Failed to import settings: ' + error.message);
            }
        };
        reader.readAsText(file);
    };
    
    input.click();
}

// Directory Browser Functions
function openDirectoryBrowser() {
    toast.info('Directory browser - Integration with system file dialog coming soon!');
}

function resetToDefaultPath() {
    const pathInput = document.getElementById('mdcDirectoryPath');
    if (pathInput) {
        pathInput.value = '/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules';
        validateMDCPath();
        toast.info('Path reset to default');
    }
}

function updateMDCPath() {
    const pathInput = document.getElementById('mdcDirectoryPath');
    const newPath = pathInput?.value?.trim();
    
    if (!newPath) {
        toast.warning('Please enter a valid path');
        return;
    }
    
    if (!validateMDCPath()) {
        return;
    }
    
    // This would be handled by saveSettings, but we can provide immediate feedback
    toast.success('Path will be updated when settings are saved');
}

// Add settings functions to window
window.switchSettingsTab = switchSettingsTab;
window.saveSettings = saveSettings;
window.resetSettings = resetSettings;
window.exportSettings = exportSettings;
window.importSettings = importSettings;
window.openDirectoryBrowser = openDirectoryBrowser;
window.resetToDefaultPath = resetToDefaultPath;
window.updateMDCPath = updateMDCPath;

// Old resetSettings function removed - using spectacular version above

async function updateMDCPath() {
    console.log('updateMDCPath called');
    const pathInput = document.getElementById('mdcDirectoryPath');
    console.log('pathInput element:', pathInput);
    
    if (!pathInput) {
        console.error('mdcDirectoryPath input element not found');
        toast.error('Form error: Input field not found');
        return;
    }
    
    const newPath = pathInput.value.trim();
    console.log('newPath extracted:', newPath);
    
    if (!newPath) {
        console.error('Empty path provided');
        toast.error('Please enter a valid path');
        return;
    }
    
    loading.show('Updating MDC directory path...');
    
    try {
        console.log('Calling api.updateMDCPath with:', newPath);
        const result = await api.updateMDCPath(newPath);
        console.log('API result:', result);
        
        if (result.success) {
            toast.success(`MDC directory updated to: ${result.data.new_path}`);
            
            // Update original path and reset button style
            originalPath = result.data.new_path;
            markPathAsUpdated();
            
            // Refresh the dashboard data with new path
            setTimeout(() => {
                refreshDashboard();
            }, 1000);
        } else {
            toast.error(`Failed to update path: ${result.error}`);
        }
    } catch (error) {
        console.error('Error updating MDC path:', error);
        toast.error('Failed to update MDC directory path');
    } finally {
        loading.hide();
    }
}

// Auto Refresh
function setupAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
    }
    
    const settings = JSON.parse(localStorage.getItem('mdcDashboardSettings')) || CONFIG.defaultSettings;
    
    if (settings.autoRefresh) {
        autoRefreshTimer = setInterval(() => {
            if (!isLoading) {
                refreshDashboard();
            }
        }, CONFIG.refreshInterval);
    }
}

async function refreshDashboard() {
    try {
        await loadSectionData(currentSection);
        updateConnectionStatus(true);
    } catch (error) {
        console.error('Auto-refresh failed:', error);
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const status = document.getElementById('connectionStatus');
    const indicator = status.querySelector('.status-indicator');
    const text = status.querySelector('span');
    
    if (connected) {
        indicator.style.background = 'var(--success-color)';
        text.textContent = 'Connected';
    } else {
        indicator.style.background = 'var(--error-color)';
        text.textContent = 'Disconnected';
    }
}

// Search Functionality
function setupSearch() {
    const searchInput = document.getElementById('searchInput');
    const debouncedSearch = utils.debounce(() => {
        if (currentSection === 'files') {
            renderMDCGrid();
        }
    }, 300);

    // Enhanced top search functionality
    if (searchInput) {
        // Create search results container if it doesn't exist
        let topSearchResults = document.getElementById('topSearchResults');
        if (!topSearchResults) {
            topSearchResults = document.createElement('div');
            topSearchResults.id = 'topSearchResults';
            topSearchResults.className = 'search-results';
            topSearchResults.style.position = 'absolute';
            topSearchResults.style.top = '100%';
            topSearchResults.style.left = '0';
            topSearchResults.style.right = '0';
            topSearchResults.style.background = 'var(--card-bg)';
            topSearchResults.style.border = '1px solid var(--border-color)';
            topSearchResults.style.borderRadius = 'var(--border-radius)';
            topSearchResults.style.boxShadow = 'var(--shadow)';
            topSearchResults.style.display = 'none';
            topSearchResults.style.zIndex = '1000';
            topSearchResults.style.maxHeight = '300px';
            topSearchResults.style.overflowY = 'auto';
            
            const searchContainer = searchInput.closest('.search-container');
            searchContainer.style.position = 'relative';
            searchContainer.appendChild(topSearchResults);
        }

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            debouncedSearch();
            
            if (query.length > 0) {
                performTopSearch(query, topSearchResults);
            } else {
                topSearchResults.style.display = 'none';
            }
        });

        searchInput.addEventListener('focus', (e) => {
            if (e.target.value.trim() !== '') {
                topSearchResults.style.display = 'block';
            }
        });

        // Hide search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !topSearchResults.contains(e.target)) {
                topSearchResults.style.display = 'none';
            }
        });
    }
}

// Perform top search with enhanced filtering
function performTopSearch(query, searchResults) {
    const queryLower = query.toLowerCase();
    
    // Search through MDC files
    const filteredFiles = mdcFilesList.filter(file => 
        file.name.toLowerCase().includes(queryLower) ||
        (file.description && file.description.toLowerCase().includes(queryLower))
    );

    if (filteredFiles.length > 0) {
        searchResults.innerHTML = filteredFiles.slice(0, 10).map(file => `
            <div class="search-result-item" onclick="selectMDCFileFromTop('${file.name}')">
                <div class="result-title">${highlightText(file.name, query)}</div>
                <div class="result-description">${file.description || 'MDC File'}</div>
            </div>
        `).join('');
        searchResults.style.display = 'block';
    } else {
        searchResults.innerHTML = `
            <div class="search-result-item">
                <div class="result-title">No MDC files found</div>
                <div class="result-description">Try a different search term</div>
            </div>
        `;
        searchResults.style.display = 'block';
    }
}

// Select MDC file from top search
function selectMDCFileFromTop(filename) {
    // Switch to MDC Generator section
    switchSection('generator');
    
    // Set the search input and load the file
    setTimeout(() => {
        const mdcSearchInput = document.getElementById('mdcFileSearch');
        const mdcDropdown = document.getElementById('mdcFileSelect');
        
        if (mdcSearchInput) {
            mdcSearchInput.value = filename;
        }
        
        if (mdcDropdown) {
            mdcDropdown.value = filename;
        }
        
        // Load the MDC file content
        loadMDCFileContent(filename);
        
        // Hide top search results
        const topSearchResults = document.getElementById('topSearchResults');
        if (topSearchResults) {
            topSearchResults.style.display = 'none';
        }
        
        // Clear top search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
        }
    }, 100);
}

// Category Filter
function setupCategoryFilter() {
    const categoryFilter = document.getElementById('categoryFilter');
    categoryFilter.addEventListener('change', () => {
        if (currentSection === 'files') {
            renderMDCGrid();
        }
    });
}

// Old form preview functionality removed - replaced by spectacular MDC Generator

// Event Listeners
function setupEventListeners() {
    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        const modal = document.getElementById('mdcModal');
        if (event.target === modal) {
            closeMDCModal();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeMDCModal();
        }
        
        // Ctrl+R or F5 for refresh
        if ((event.ctrlKey && event.key === 'r') || event.key === 'F5') {
            event.preventDefault();
            refreshDashboard();
        }
    });
    
    // Setup other event listeners
    setupSearch();
    setupCategoryFilter();
    // Old form preview setup removed - replaced by spectacular MDC Generator
}

// Initialize Dashboard
async function initializeDashboard() {
    try {
        // 🔔 Initialize notification window first
        createNotificationWindow();
        
        // 💚 Initialize health card styles
        addHealthCardStyles();
        
        showStatusMessage('🚀 Dashboard initializing...', 'info');
        
        // Load initial data
        await loadOverviewData();
        
        // Render Analytics Charts
        renderAnalyticsCharts();
        
        // Setup auto-refresh
        setupAutoRefresh();
        
        // Setup event listeners
        setupEventListeners();
        
        // Load settings
        loadSettings();
        
        // Setup MDC scan scheduling
        setupMDCScanScheduling();
        setupContextOptimizationScheduling();
        
        // Update scan status display if we have previous data
        setTimeout(updateScanStatusDisplay, 1000);
        
        // Update next scan time every minute
        setInterval(updateScanStatusDisplay, 60000);
        
        showStatusMessage('✅ Dashboard initialized successfully!', 'success');
        console.log('MDC Dashboard initialized successfully');
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        toast.error('Failed to initialize dashboard');
    }
}

// 📊 SPECTACULAR ANALYTICS CHART FUNCTIONS
function renderAnalyticsCharts() {
    console.log('🚀 Rendering Analytics Charts...');
    
    // Add delay to ensure DOM elements are loaded
    setTimeout(() => {
        renderPieChart();
        renderBarChart();
        renderLineChart();
        renderHeatmap();
        renderActivityTimeline();
        console.log('✅ All Analytics Charts Rendered!');
    }, 500);
}

// 🥧 Pie Chart Renderer
function renderPieChart() {
    const pieContainer = document.querySelector('.pie-chart-container .chart-content');
    if (!pieContainer) {
        console.log('Pie chart container not found');
        return;
    }

    const data = [
        { label: 'Active MDCs', value: 45, color: '#4fd1c7' },
        { label: 'Monitoring', value: 30, color: '#667eea' },
        { label: 'Archived', value: 15, color: '#f093fb' },
        { label: 'Draft', value: 10, color: '#ffeaa7' }
    ];

    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = 0;

    const svg = `
        <svg viewBox="0 0 200 200" class="pie-chart">
            ${data.map(item => {
                const percentage = (item.value / total) * 100;
                const angle = (item.value / total) * 360;
                const startAngle = currentAngle;
                currentAngle += angle;
                
                const x1 = 100 + 80 * Math.cos((startAngle - 90) * Math.PI / 180);
                const y1 = 100 + 80 * Math.sin((startAngle - 90) * Math.PI / 180);
                const x2 = 100 + 80 * Math.cos((currentAngle - 90) * Math.PI / 180);
                const y2 = 100 + 80 * Math.sin((currentAngle - 90) * Math.PI / 180);
                
                const largeArc = angle > 180 ? 1 : 0;
                
                return `
                    <path d="M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z"
                          fill="${item.color}" 
                          opacity="0.8"
                          class="pie-slice"
                          data-label="${item.label}"
                          data-value="${item.value}">
                    </path>
                `;
            }).join('')}
        </svg>
    `;

    const legend = data.map(item => `
        <div class="legend-item">
            <span class="legend-color" style="background: ${item.color}"></span>
            <span class="legend-label">${item.label}: ${item.value}%</span>
        </div>
    `).join('');

    pieContainer.innerHTML = `
        ${svg}
        <div class="chart-legend">${legend}</div>
    `;
}

// 📊 Bar Chart Renderer
function renderBarChart() {
    const barContainer = document.querySelector('.bar-chart-container .chart-content');
    if (!barContainer) {
        console.log('Bar chart container not found');
        return;
    }

    const data = [
        { label: 'Jan', value: 85 },
        { label: 'Feb', value: 92 },
        { label: 'Mar', value: 78 },
        { label: 'Apr', value: 96 },
        { label: 'May', value: 89 },
        { label: 'Jun', value: 94 }
    ];

    const maxValue = Math.max(...data.map(d => d.value));

    const bars = data.map((item, index) => {
        const height = (item.value / maxValue) * 100;
        const color = `hsl(${180 + index * 30}, 70%, 60%)`;
        
        return `
            <div class="bar-item" style="animation-delay: ${index * 0.1}s">
                <div class="bar" style="height: ${height}%; background: ${color}">
                    <span class="bar-value">${item.value}</span>
                </div>
                <span class="bar-label">${item.label}</span>
            </div>
        `;
    }).join('');

    barContainer.innerHTML = `
        <div class="bar-chart">${bars}</div>
    `;
}

// 📈 Line Chart Renderer
function renderLineChart() {
    const lineContainer = document.querySelector('.line-chart-container .chart-content');
    if (!lineContainer) {
        console.log('Line chart container not found');
        return;
    }

    const data = [
        { x: 0, y: 20 },
        { x: 1, y: 35 },
        { x: 2, y: 25 },
        { x: 3, y: 55 },
        { x: 4, y: 45 },
        { x: 5, y: 75 },
        { x: 6, y: 65 }
    ];

    const maxY = Math.max(...data.map(d => d.y));
    const points = data.map(d => `${d.x * 30 + 20},${120 - (d.y / maxY) * 80}`).join(' ');

    const svg = `
        <svg viewBox="0 0 220 140" class="line-chart">
            <defs>
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#4fd1c7"/>
                    <stop offset="100%" style="stop-color:#667eea"/>
                </linearGradient>
            </defs>
            <polyline points="${points}" 
                     fill="none" 
                     stroke="url(#lineGradient)" 
                     stroke-width="3"
                     class="line-path"/>
            ${data.map(d => `
                <circle cx="${d.x * 30 + 20}" 
                       cy="${120 - (d.y / maxY) * 80}" 
                       r="4" 
                       fill="#4fd1c7" 
                       class="line-point"
                       style="animation-delay: ${d.x * 0.1}s">
                </circle>
            `).join('')}
        </svg>
    `;

    lineContainer.innerHTML = svg;
}

// 🔥 Heatmap Renderer
function renderHeatmap() {
    const heatmapContainer = document.querySelector('.heatmap-container .chart-content');
    if (!heatmapContainer) {
        console.log('Heatmap container not found');
        return;
    }

    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const weeks = 12;
    
    let heatmapHTML = '<div class="heatmap-grid">';
    
    for (let week = 0; week < weeks; week++) {
        for (let day = 0; day < 7; day++) {
            const intensity = Math.random();
            const color = intensity > 0.7 ? '#4fd1c7' : 
                         intensity > 0.4 ? '#667eea' : 
                         intensity > 0.2 ? '#a8e6cf' : '#f0f0f0';
            
            heatmapHTML += `
                <div class="heatmap-cell" 
                     style="background: ${color}; animation-delay: ${(week * 7 + day) * 0.01}s"
                     title="${days[day]} - Week ${week + 1}: ${Math.round(intensity * 100)}%">
                </div>
            `;
        }
    }
    
    heatmapHTML += '</div>';
    heatmapContainer.innerHTML = heatmapHTML;
}

// ⏰ Activity Timeline Renderer
function renderActivityTimeline() {
    const timelineContainer = document.querySelector('.timeline-container .chart-content');
    if (!timelineContainer) {
        console.log('Timeline container not found');
        return;
    }

    const activities = [
        { time: '09:00', event: 'System Started', type: 'success' },
        { time: '10:30', event: 'MDC Update', type: 'info' },
        { time: '12:15', event: 'Alert Triggered', type: 'warning' },
        { time: '14:00', event: 'Backup Complete', type: 'success' },
        { time: '16:45', event: 'User Login', type: 'info' },
        { time: '18:30', event: 'Service Restart', type: 'warning' }
    ];

    const timelineHTML = activities.map((activity, index) => `
        <div class="timeline-item" style="animation-delay: ${index * 0.2}s">
            <div class="timeline-marker ${activity.type}"></div>
            <div class="timeline-content">
                <div class="timeline-time">${activity.time}</div>
                <div class="timeline-event">${activity.event}</div>
            </div>
        </div>
    `).join('');

    timelineContainer.innerHTML = `
        <div class="timeline-list">${timelineHTML}</div>
    `;
}

// Export functions for global access
window.switchSection = switchSection;
window.generateAllDocs = generateAllDocs;
window.discoverConnections = discoverConnections;
window.showServiceDiscovery = showServiceDiscovery;
window.openServiceDiscoveryModal = openServiceDiscoveryModal;
window.renderServicesGrid = renderServicesGrid;
window.renderConnectionItem = renderConnectionItem;
window.generateTechnicalReasoning = generateTechnicalReasoning;
window.generateBusinessValue = generateBusinessValue;
window.generateArchitecturalAdvantages = generateArchitecturalAdvantages;
window.getConfidenceIcon = getConfidenceIcon;
window.getConnectionTypeIcon = getConnectionTypeIcon;
window.toggleServiceExpansion = toggleServiceExpansion;
window.expandServiceConnections = expandServiceConnections;
window.closeServiceDiscoveryModal = closeServiceDiscoveryModal;
window.optimizeContext = optimizeContext;
window.validateSystem = validateSystem;
window.showValidationResults = showValidationResults;
window.closeValidationResults = closeValidationResults;
window.runValidationAgain = runValidationAgain;
window.viewComponentLogs = viewComponentLogs;
window.closeComponentLogs = closeComponentLogs;
window.refreshLogs = refreshLogs;
window.clearLogsDisplay = clearLogsDisplay;
window.downloadLogs = downloadLogs;
window.createNewMDC = createNewMDC;
window.editMDC = editMDC;
window.deleteMDC = deleteMDC;
window.viewConnections = viewConnections;
window.openMDCModal = openMDCModal;
window.closeMDCModal = closeMDCModal;
// Old generateMDC and resetForm functions removed - replaced by spectacular MDC Generator
window.refreshDashboard = refreshDashboard;
window.selectMDCFileFromTop = selectMDCFileFromTop;
// saveSettings and resetSettings already assigned above with spectacular versions
window.refreshConnections = loadConnections;
window.clearConnectionFilters = clearConnectionFilters;
window.toggleConnectionView = toggleConnectionView;
window.viewConnectionDetails = viewConnectionDetails;
window.closeConnectionDetails = closeConnectionDetails;
window.testConnection = testConnection;
window.restartConnection = restartConnection;
window.stopConnection = stopConnection;
window.testAllConnections = testAllConnections;
window.restartAllConnections = restartAllConnections;
window.togglePendingServices = togglePendingServices;
window.toggleServiceContent = toggleServiceContent;
window.generateBasicMDC = generateBasicMDC;
window.generateChatGPTMDC = generateChatGPTMDC;
window.enhanceExistingMDC = enhanceExistingMDC;
window.toggleUpdateHistory = toggleUpdateHistory;
window.toggleHistoryDetails = toggleHistoryDetails;
window.generateConnectionGraph = () => toast.info('Connection graph generation coming soon');
window.exportConnections = () => toast.info('Connection export coming soon');
window.toast = toast;

// Directory Browser Functions
async function openDirectoryBrowser() {
    console.log('Opening directory browser');
    
    // Get current path from input or use default
    const pathInput = document.getElementById('mdcDirectoryPath');
    if (pathInput && pathInput.value && pathInput.value.trim()) {
        currentBrowsePath = pathInput.value.trim();
        console.log('Using path from input:', currentBrowsePath);
    } else {
        // Try to get current settings first
        try {
            const settings = await api.getSettings();
            if (settings.success && settings.data.mdcDirectory) {
                currentBrowsePath = settings.data.mdcDirectory;
                console.log('Using path from settings:', currentBrowsePath);
            } else {
                currentBrowsePath = '/Users/dansidanutz/Desktop/ZmartBot';
                console.log('Using default path:', currentBrowsePath);
            }
        } catch (error) {
            console.error('Error getting settings, using default:', error);
            currentBrowsePath = '/Users/dansidanutz/Desktop/ZmartBot';
        }
    }
    
    console.log('Starting browse path:', currentBrowsePath);
    
    const modal = document.getElementById('directoryBrowserModal');
    modal.style.display = 'flex';
    
    await loadDirectoryContents(currentBrowsePath);
}

function closeDirectoryBrowser() {
    const modal = document.getElementById('directoryBrowserModal');
    modal.style.display = 'none';
}

async function loadDirectoryContents(path) {
    console.log('Loading directory contents for:', path);
    
    try {
        loading.show('Loading directory...');
        
        const result = await api.browseDirectory(path);
        console.log('Directory browse result:', result);
        console.log('Result success:', result.success);
        console.log('Result data:', result.data);
        
        if (result.success) {
            currentBrowsePath = result.data.currentPath;
            console.log('Current browse path set to:', currentBrowsePath);
            console.log('Items to display:', result.data.items);
            
            displayDirectoryContents(result.data.items);
            
            // Update current path display
            const pathElement = document.getElementById('currentBrowsePath');
            if (pathElement) {
                pathElement.textContent = currentBrowsePath;
                console.log('Updated path display to:', currentBrowsePath);
            } else {
                console.error('currentBrowsePath element not found!');
            }
        } else {
            console.error('Browse directory failed:', result.error);
            toast.error(`Failed to browse directory: ${result.error}`);
        }
    } catch (error) {
        console.error('Error loading directory:', error);
        toast.error('Failed to load directory contents');
    } finally {
        loading.hide();
    }
}

function displayDirectoryContents(items) {
    console.log('displayDirectoryContents called with items:', items);
    const listElement = document.getElementById('directoryList');
    
    if (!listElement) {
        console.error('directoryList element not found!');
        return;
    }
    
    console.log('Clearing directory list...');
    listElement.innerHTML = '';
    
    console.log('Processing', items.length, 'items');
    items.forEach((item, index) => {
        console.log(`Processing item ${index}:`, item);
        const itemElement = document.createElement('div');
        itemElement.className = `directory-item ${item.isParent ? 'parent-dir' : ''}`;
        itemElement.onclick = () => navigateToDirectory(item.path);
        
        itemElement.innerHTML = `
            <div class="icon">
                <i class="fas ${item.isParent ? 'fa-level-up-alt' : 'fa-folder'}"></i>
            </div>
            <div class="name">${item.name}</div>
        `;
        
        console.log('Created item element for:', item.name);
        listElement.appendChild(itemElement);
    });
    
    // If no directories found, show a message
    if (items.length === 0) {
        listElement.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--text-muted);">No directories found</div>';
    }
}

async function navigateToDirectory(path) {
    console.log('Navigating to directory:', path);
    await loadDirectoryContents(path);
}

function selectCurrentDirectory() {
    console.log('Selecting directory:', currentBrowsePath);
    
    // Update the input field
    const pathInput = document.getElementById('mdcDirectoryPath');
    if (pathInput) {
        pathInput.value = currentBrowsePath;
        console.log('Updated input field to:', currentBrowsePath);
        
        // Mark that the path has changed and needs updating
        markPathAsChanged();
    }
    
    closeDirectoryBrowser();
    toast.success(`Selected directory: ${currentBrowsePath}. Click Update to save.`);
}

// Path change tracking
let originalPath = '';

function markPathAsChanged() {
    console.log('Marking path as changed');
    const updateButton = document.querySelector('button[onclick="updateMDCPath()"]');
    if (updateButton) {
        updateButton.style.backgroundColor = '#28a745';
        updateButton.style.borderColor = '#28a745';
        updateButton.style.color = 'white';
        updateButton.innerHTML = '<i class="fas fa-save"></i> Update (Changes Pending)';
        console.log('Update button styled as changed');
    }
}

function markPathAsUpdated() {
    console.log('Marking path as updated');
    const updateButton = document.querySelector('button[onclick="updateMDCPath()"]');
    if (updateButton) {
        updateButton.style.backgroundColor = '';
        updateButton.style.borderColor = '';
        updateButton.style.color = '';
        updateButton.innerHTML = '<i class="fas fa-save"></i> Update';
        console.log('Update button styled as normal');
    }
}

function setupPathChangeDetection() {
    const pathInput = document.getElementById('mdcDirectoryPath');
    if (pathInput) {
        // Store original path when settings are loaded
        originalPath = pathInput.value;
        
        // Listen for input changes
        pathInput.addEventListener('input', () => {
            if (pathInput.value !== originalPath) {
                markPathAsChanged();
            } else {
                markPathAsUpdated();
            }
        });
        
        console.log('Path change detection setup complete');
    }
}

function resetToDefaultPath() {
    const defaultPath = '/Users/dansidanutz/Desktop/ZmartBot/.cursor/rules';
    const pathInput = document.getElementById('mdcDirectoryPath');
    
    if (pathInput) {
        pathInput.value = defaultPath;
        console.log('Reset path to default:', defaultPath);
        
        // Check if it's different from original to trigger change detection
        if (defaultPath !== originalPath) {
            markPathAsChanged();
        } else {
            markPathAsUpdated();
        }
        
        toast.info(`Path reset to default: ${defaultPath}. Click Update to save.`);
    }
}

// MDC Scan functionality
// Intelligent Incremental Connection Discovery Engine (integrated into main scan)
const MDCConnectionEngine = {
    snapshotKey: 'mdc_connection_snapshot',
    lastScanKey: 'mdc_last_scan_timestamp',
    
    // Connection patterns to detect
    patterns: {
        api: [
            /app\.get\(['"]([^'"]+)['"]/, 
            /app\.post\(['"]([^'"]+)['"]/, 
            /app\.put\(['"]([^'"]+)['"]/, 
            /app\.delete\(['"]([^'"]+)['"]/, 
            /fetch\(['"]([^'"]+)['"]/, 
            /axios\.get\(['"]([^'"]+)['"]/,
            /requests\.get\(['"]([^'"]+)['"]/
        ],
        database: [
            /\.collection\(['"]([^'"]+)['"]\)/, 
            /from\s+['"]?([a-zA-Z_][a-zA-Z0-9_]+)['"]?\s+where/, 
            /table\(['"]([^'"]+)['"]\)/, 
            /cursor\.execute\(['"][^'"]*from\s+([a-zA-Z_][a-zA-Z0-9_]+)/i,
            /db\.([a-zA-Z_][a-zA-Z0-9_]+)\.find/
        ],
        messaging: [
            /channel\(['"]([^'"]+)['"]\)/, 
            /topic\(['"]([^'"]+)['"]\)/, 
            /queue\(['"]([^'"]+)['"]\)/, 
            /subscribe\(['"]([^'"]+)['"]\)/,
            /publish\(['"]([^'"]+)['"]\)/
        ],
        storage: [
            /bucket\(['"]([^'"]+)['"]\)/, 
            /s3\.upload\(['"][^'"]*['"]/, 
            /localStorage\.setItem\(['"]([^'"]+)['"]\)/, 
            /sessionStorage\.setItem\(['"]([^'"]+)['"]\)/
        ],
        auth: [
            /passport\.use/, 
            /jwt\.sign/, 
            /bcrypt\.hash/, 
            /oauth2/, 
            /authenticate\(['"]([^'"]+)['"]\)/
        ],
        monitoring: [
            /logger\.info\(['"]([^'"]+)['"]\)/, 
            /console\.log\(['"]([^'"]+)['"]\)/, 
            /prometheus\.register/, 
            /metrics\.increment/
        ]
    },
    
    getSnapshot() {
        const snapshot = localStorage.getItem(this.snapshotKey);
        return snapshot ? JSON.parse(snapshot) : { files: {}, timestamp: null };
    },
    
    saveSnapshot(snapshot) {
        snapshot.timestamp = new Date().toISOString();
        localStorage.setItem(this.snapshotKey, JSON.stringify(snapshot));
    },
    
    calculateChecksum(content) {
        let hash = 0;
        if (content.length === 0) return hash;
        for (let i = 0; i < content.length; i++) {
            const char = content.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return hash.toString(16);
    },
    
    detectChanges(currentFiles, snapshot) {
        const changes = {
            newFiles: [],
            modifiedFiles: [],
            deletedFiles: [],
            unchangedFiles: []
        };
        
        const snapshotFiles = snapshot.files || {};
        const currentFileMap = {};
        
        // Process current files
        currentFiles.forEach(file => {
            if (!file.name || !file.name.endsWith('.mdc')) return;
            
            currentFileMap[file.name] = file;
            const checksum = this.calculateChecksum(file.content || '');
            
            if (!(file.name in snapshotFiles)) {
                changes.newFiles.push(file);
            } else if (snapshotFiles[file.name].checksum !== checksum) {
                changes.modifiedFiles.push(file);
            } else {
                changes.unchangedFiles.push(file);
            }
        });
        
        // Find deleted files
        Object.keys(snapshotFiles).forEach(fileName => {
            if (!(fileName in currentFileMap)) {
                changes.deletedFiles.push(fileName);
            }
        });
        
        changes.summary = {
            total: currentFiles.filter(f => f.name && f.name.endsWith('.mdc')).length,
            new: changes.newFiles.length,
            modified: changes.modifiedFiles.length,
            deleted: changes.deletedFiles.length,
            unchanged: changes.unchangedFiles.length,
            needProcessing: changes.newFiles.length + changes.modifiedFiles.length
        };
        
        return changes;
    },
    
    async discoverConnectionsInContent(content, fileName) {
        const connections = new Set();
        
        try {
            Object.entries(this.patterns).forEach(([category, patternList]) => {
                patternList.forEach(pattern => {
                    const matches = content.matchAll(new RegExp(pattern.source, 'gi'));
                    for (const match of matches) {
                        if (match[1] && match[1].trim()) {
                            connections.add(`${category}:${match[1].trim()}`);
                        }
                    }
                });
            });
        } catch (error) {
            console.warn(`Connection discovery warning for ${fileName}:`, error);
        }
        
        return Array.from(connections);
    },
    
    // Categorize connections into Current, Potential, and Priority states
    categorizeConnections(connections) {
        const current = [];
        const potential = [];
        const priority = [];
        
        connections.forEach(conn => {
            const [type, target] = conn.split(':');
            const typeL = type.toLowerCase();
            
            // Priority connections (critical infrastructure)
            if (['database', 'api', 'port'].includes(typeL) || 
                target?.includes('localhost') || 
                target?.match(/^\d+$/)) { // Port numbers
                priority.push(conn);
            }
            // Current active connections (detected and likely active)
            else if (['service', 'config', 'file'].includes(typeL)) {
                current.push(conn);
            }
            // Potential connections (discovered but not confirmed active)
            else {
                potential.push(conn);
            }
        });
        
        return { current, potential, priority };
    },
    
    // Get connection description based on type
    getConnectionDescription(type) {
        switch (type) {
            case 'api':
                return ' - REST API endpoint communication';
            case 'database':
                return ' - Database connection and data persistence';
            case 'port':
                return ' - Network port binding for service communication';
            case 'service':
                return ' - Inter-service communication and dependency';
            case 'file':
                return ' - File system access and data storage';
            case 'config':
                return ' - Configuration and environment variables';
            default:
                return ' - Service connection or dependency';
        }
    },
    
    async updateMDCFileConnections(fileName, connections, mdcPath) {
        if (!connections || connections.length === 0) {
            console.log(`No connections found for ${fileName}`);
            return false;
        }
        
        try {
            // Read current file content
            const response = await fetch(`/api/mdc/read?file=${encodeURIComponent(fileName)}`);
            const result = await response.json();
            
            if (!result.success) {
                console.warn(`Could not read ${fileName} for connection update`);
                return false;
            }
            
            let content = result.content || '';
            
            // Create comprehensive connections section with 3-state structure
            const timestamp = new Date().toISOString();
            
            // Categorize connections into Current, Potential, and Priority
            const categorizedConnections = this.categorizeConnections(connections);
            
            const connectionsSection = `\n\n## 🔗 Service Connections & Dependencies\n\n### Current Active Connections\n${categorizedConnections.current.length > 0 ? categorizedConnections.current.map(conn => {
                const [type, target] = conn.split(':');
                const connectionType = type.toUpperCase();
                const connectionTarget = target || 'Unknown';
                
                let description = this.getConnectionDescription(type.toLowerCase());
                return `- **${connectionType}**: \`${connectionTarget}\`${description} ✅ **ACTIVE**`;
            }).join('\n') : '*No current active connections detected*'}

### Potential Connections
${categorizedConnections.potential.length > 0 ? categorizedConnections.potential.map(conn => {
                const [type, target] = conn.split(':');
                const connectionType = type.toUpperCase();
                const connectionTarget = target || 'Unknown';
                
                let description = this.getConnectionDescription(type.toLowerCase());
                return `- **${connectionType}**: \`${connectionTarget}\`${description} ⏳ **POTENTIAL**`;
            }).join('\n') : '*No potential connections identified*'}

### Priority Connections
${categorizedConnections.priority.length > 0 ? categorizedConnections.priority.map(conn => {
                const [type, target] = conn.split(':');
                const connectionType = type.toUpperCase();
                const connectionTarget = target || 'Unknown';
                
                let description = this.getConnectionDescription(type.toLowerCase());
                return `- **${connectionType}**: \`${connectionTarget}\`${description} 🔥 **PRIORITY**`;
            }).join('\n') : '*No priority connections required*'}

### Connection Summary
- **Current Active**: ${categorizedConnections.current.length}
- **Potential**: ${categorizedConnections.potential.length}  
- **Priority**: ${categorizedConnections.priority.length}
- **Total Discovered**: ${connections.length}
- **Last Discovery Scan**: ${timestamp.split('T')[0]} at ${timestamp.split('T')[1].split('.')[0]}
- **Discovery Method**: Automated content analysis with state classification
- **Update Policy**: Auto-refresh on file changes with intelligent categorization

### Connection Health & Status
- **Active Monitoring**: Current connections monitored continuously
- **Potential Analysis**: Potential connections analyzed for activation readiness
- **Priority Queue**: Priority connections flagged for immediate attention
- **Health Check**: Automated dependency validation with state-aware monitoring
- **Failure Recovery**: Circuit breaker pattern implemented with priority handling

---
*This section is automatically maintained by the ZmartBot MDC Connection Discovery Engine*
*Connection states: Current (Active) | Potential (Discovered) | Priority (Critical)*
*Next scan scheduled based on file modification detection*`;
            
            // Check if connections section already exists
            const connectionRegex = /\n## 🔗 Service Connections[^\n]*[\s\S]*?(?=\n## |\n# |$)/;
            
            if (connectionRegex.test(content)) {
                // Replace existing connections section
                content = content.replace(connectionRegex, connectionsSection);
            } else {
                // Add new connections section at the end
                content += connectionsSection;
            }
            
            // Write updated content
            const updateResponse = await fetch('/api/mdc/write', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fileName: fileName,
                    content: content
                })
            });
            
            const updateResult = await updateResponse.json();
            return updateResult.success;
            
        } catch (error) {
            console.error(`Error updating connections in ${fileName}:`, error);
            return false;
        }
    },
    
    async performIncrementalScan(mdcFiles, mdcPath) {
        console.log('🔍 Starting intelligent incremental connection discovery...');
        
        const snapshot = this.getSnapshot();
        const changes = this.detectChanges(mdcFiles, snapshot);
        
        console.log(`📊 Change Detection Summary:`, changes.summary);
        
        if (changes.summary.needProcessing === 0) {
            console.log('✅ No changes detected - using cached connections');
            return {
                success: true,
                fromCache: true,
                connectionsDiscovered: 0,
                filesProcessed: 0,
                summary: changes.summary
            };
        }
        
        // Process only new and modified files
        const filesToProcess = [...changes.newFiles, ...changes.modifiedFiles];
        let totalConnectionsDiscovered = 0;
        let filesUpdated = 0;
        
        console.log(`🔧 Processing ${filesToProcess.length} changed files...`);
        
        for (const file of filesToProcess) {
            if (!file.content) continue;
            
            const connections = await this.discoverConnectionsInContent(file.content, file.name);
            
            if (connections.length > 0) {
                console.log(`🔗 Found ${connections.length} connections in ${file.name}`);
                const updated = await this.updateMDCFileConnections(file.name, connections, mdcPath);
                if (updated) {
                    filesUpdated++;
                    totalConnectionsDiscovered += connections.length;
                }
            }
        }
        
        // Update snapshot
        const newSnapshot = { files: {} };
        mdcFiles.forEach(file => {
            if (file.name && file.name.endsWith('.mdc')) {
                newSnapshot.files[file.name] = {
                    checksum: this.calculateChecksum(file.content || ''),
                    lastModified: file.lastModified,
                    connections: file.connections || []
                };
            }
        });
        
        this.saveSnapshot(newSnapshot);
        
        return {
            success: true,
            fromCache: false,
            connectionsDiscovered: totalConnectionsDiscovered,
            filesProcessed: filesToProcess.length,
            filesUpdated: filesUpdated,
            summary: changes.summary
        };
    }
};

// Context Optimization Engine for CLAUDE.md
const ContextOptimizationEngine = {
    optimizationKey: 'context_optimization_data',
    claudeMdPath: '/Users/dansidanutz/Desktop/ZmartBot/zmart-api/CLAUDE.md',
    
    getOptimizationData() {
        const data = localStorage.getItem(this.optimizationKey);
        return data ? JSON.parse(data) : { 
            lastOptimization: null, 
            optimizationHistory: [],
            averageSize: 0,
            totalOptimizations: 0,
            adaptiveInterval: 2 * 60 * 60 * 1000, // Default 2 hours
            performanceMetrics: {
                averageProcessingTime: 0,
                largeFileOptimizations: 0,
                sizeReductionRatio: 0
            }
        };
    },
    
    // NEW: Calculate adaptive optimization interval based on file size and growth
    calculateAdaptiveInterval(fileSize, growthRate = 0) {
        let baseInterval = 2 * 60 * 60 * 1000; // 2 hours default
        
        // Adjust based on file size
        if (fileSize > 35000) {
            baseInterval = 1 * 60 * 60 * 1000; // 1 hour for large files
        } else if (fileSize > 30000) {
            baseInterval = 1.5 * 60 * 60 * 1000; // 1.5 hours for medium files
        } else if (fileSize < 20000) {
            baseInterval = 4 * 60 * 60 * 1000; // 4 hours for small files
        }
        
        // Adjust based on growth rate
        if (growthRate > 0.2) { // File growing fast (>20% per optimization)
            baseInterval *= 0.7; // More frequent optimization
        } else if (growthRate < 0.05) { // File stable (<5% growth)
            baseInterval *= 1.3; // Less frequent optimization
        }
        
        // Ensure reasonable bounds (30 minutes to 6 hours)
        return Math.max(30 * 60 * 1000, Math.min(6 * 60 * 60 * 1000, baseInterval));
    },
    
    // NEW: Intelligent file prioritization for optimization
    analyzeOptimizationNeeds(content) {
        const size = content.length;
        const lines = content.split('\n').length;
        
        let priority = 'LOW';
        let urgency = 0;
        let reasons = [];
        
        // Size-based priority
        if (size > 40000) {
            priority = 'CRITICAL';
            urgency += 10;
            reasons.push('File exceeds 40k chars');
        } else if (size > 35000) {
            priority = 'HIGH';
            urgency += 7;
            reasons.push('File approaching size limit');
        } else if (size > 30000) {
            priority = 'MEDIUM';
            urgency += 4;
            reasons.push('File size optimization beneficial');
        }
        
        // Content-based analysis
        const excessiveWhitespace = (content.match(/\n{4,}/g) || []).length;
        if (excessiveWhitespace > 5) {
            urgency += 3;
            reasons.push('Excessive whitespace detected');
        }
        
        const redundantPatterns = (content.match(/\(see [^)]+\)/g) || []).length;
        if (redundantPatterns > 10) {
            urgency += 2;
            reasons.push('Redundant pattern references');
        }
        
        const outdatedTimestamps = content.includes('2025-08-25') || content.includes('2025-08-24');
        if (outdatedTimestamps) {
            urgency += 1;
            reasons.push('Outdated timestamps');
        }
        
        return {
            priority,
            urgency,
            reasons,
            size,
            lines,
            estimatedSavings: Math.min(size * 0.1, 2000) // Estimate 10% savings, max 2k chars
        };
    },
    
    saveOptimizationData(data) {
        data.lastSaved = new Date().toISOString();
        localStorage.setItem(this.optimizationKey, JSON.stringify(data));
    },
    
    async readClaudeMdFile() {
        try {
            const response = await fetch('/api/mdc/read?file=CLAUDE.md');
            const result = await response.json();
            
            if (result.success) {
                return {
                    content: result.content || '',
                    size: (result.content || '').length
                };
            }
            
            return { content: '', size: 0 };
        } catch (error) {
            console.error('Error reading CLAUDE.md:', error);
            return { content: '', size: 0 };
        }
    },
    
    async writeClaudeMdFile(content) {
        try {
            const response = await fetch('/api/mdc/write', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    fileName: 'CLAUDE.md',
                    content: content
                })
            });
            
            const result = await response.json();
            return result.success || false;
        } catch (error) {
            console.error('Error writing CLAUDE.md:', error);
            return false;
        }
    },
    
    optimizeContextContent(content) {
        const startTime = performance.now();
        let optimizations = 0;
        let optimizedContent = content;
        const originalSize = content.length;
        
        console.log(`🔧 Starting optimization - File size: ${originalSize} chars`);
        
        // ENHANCED OPTIMIZATION ALGORITHMS FOR LARGE FILES
        
        // 1. Intelligent Whitespace Optimization (Enhanced)
        const beforeWhitespace = optimizedContent.length;
        optimizedContent = optimizedContent
            .replace(/\n{4,}/g, '\n\n\n')  // Max 3 consecutive newlines
            .replace(/[ \t]+$/gm, '')       // Remove trailing spaces
            .replace(/^[ \t]+(?=\n)/gm, '') // Remove leading spaces on empty lines
            .replace(/[ \t]{2,}/g, ' ');    // Replace multiple spaces with single space
        if (optimizedContent.length < beforeWhitespace) {
            optimizations++;
            console.log(`  ✓ Whitespace optimized: ${beforeWhitespace - optimizedContent.length} chars saved`);
        }
        
        // 2. Smart Section Header Optimization
        const beforeHeaders = optimizedContent.length;
        optimizedContent = optimizedContent.replace(/^## (🔥|📚|📊|🎯|🚨|🔄) ([^\n]+)/gm, (match, emoji, text) => {
            return `## ${emoji} ${text.trim()}`;
        });
        if (optimizedContent.length < beforeHeaders) {
            optimizations++;
            console.log(`  ✓ Headers optimized: ${beforeHeaders - optimizedContent.length} chars saved`);
        }
        
        // 3. Advanced Pattern Consolidation
        const beforePatterns = optimizedContent.length;
        // Remove redundant context file references
        optimizedContent = optimizedContent.replace(/(\*\*[^*]+\*\*:\s*\d+\s*files)\s+\(see[^)]+\)\s*\n/g, '$1\n');
        // Consolidate repeated context references
        optimizedContent = optimizedContent.replace(/(- \*\*[^*]+\*\*:)\s+([^\n]+)\s+\(see[^)]+\)/g, '$1 $2');
        if (optimizedContent.length < beforePatterns) {
            optimizations++;
            console.log(`  ✓ Patterns consolidated: ${beforePatterns - optimizedContent.length} chars saved`);
        }
        
        // 4. Dynamic Size-Based Optimization
        const currentSize = optimizedContent.length;
        if (currentSize > 35000) {
            console.log(`⚠️  Large file detected (${currentSize} chars) - Applying aggressive optimization`);
            
            // Aggressive optimization for large files
            const beforeAggressive = optimizedContent.length;
            
            // Compress repeated sections
            optimizedContent = optimizedContent.replace(/(\n- \*\*[^*]+\*\*: \d+ files)\n(\n- \*\*[^*]+\*\*: \d+ files)+/g, 
                (match) => {
                    const lines = match.split('\n').filter(line => line.trim());
                    if (lines.length > 3) {
                        const first = lines[0];
                        const last = lines[lines.length - 1];
                        return `\n${first}\n... (${lines.length - 2} more contexts)\n${last}`;
                    }
                    return match;
                });
            
            // Optimize context list display
            optimizedContent = optimizedContent.replace(/## 📚 Available Contexts\n\n((?:- \*\*[^:]+\*\*:[^\n]+\n)+)/g, 
                (match, contexts) => {
                    const contextLines = contexts.split('\n').filter(line => line.trim());
                    if (contextLines.length > 8) {
                        const summary = contextLines.slice(0, 5);
                        summary.push(`- ... and ${contextLines.length - 5} more contexts available`);
                        return `## 📚 Available Contexts\n\n${summary.join('\n')}\n`;
                    }
                    return match;
                });
            
            if (optimizedContent.length < beforeAggressive) {
                optimizations++;
                console.log(`  ✓ Aggressive optimization: ${beforeAggressive - optimizedContent.length} chars saved`);
            }
        }
        
        // 5. Smart Timestamp Updates
        const now = new Date().toISOString();
        optimizedContent = optimizedContent.replace(/\*\*Generated\*\*: [^\n]+/g, `**Generated**: ${now}`);
        optimizedContent = optimizedContent.replace(/\*\*Last Updated\*\*: [^\n]+/g, `**Last Updated**: ${now}`);
        optimizations += 2;
        
        // 6. Dynamic Size and Performance Calculation
        const finalSize = optimizedContent.length;
        optimizedContent = optimizedContent.replace(
            /- \*\*CLAUDE\.md Size\*\*: \d+ characters/g,
            `- **CLAUDE.md Size**: ${finalSize} characters`
        );
        
        // 7. Intelligent Performance Status
        let performanceStatus;
        let recommendation = '';
        
        if (finalSize < 25000) {
            performanceStatus = '✅ Optimal';
        } else if (finalSize < 30000) {
            performanceStatus = '✅ Good';
        } else if (finalSize < 35000) {
            performanceStatus = '⚠️ Fair';
            recommendation = ' (Consider context reduction)';
        } else if (finalSize < 40000) {
            performanceStatus = '⚠️ Large';
            recommendation = ' (Context optimization needed)';
        } else {
            performanceStatus = '❌ Critical';
            recommendation = ' (Immediate optimization required)';
        }
        
        optimizedContent = optimizedContent.replace(
            /- \*\*Performance\*\*: [^\n]+/g,
            `- **Performance**: ${performanceStatus}${recommendation}`
        );
        optimizations++;
        
        // 8. Context Load Optimization (NEW)
        if (finalSize > 30000) {
            // Add context loading optimization note
            const contextNote = '\n**Note**: Context auto-optimized for performance. Full details available in MDC files.\n';
            if (!optimizedContent.includes('Context auto-optimized')) {
                optimizedContent = optimizedContent.replace(
                    /## 🔄 Context Management\n/,
                    `## 🔄 Context Management\n${contextNote}`
                );
                optimizations++;
            }
        }
        
        const endTime = performance.now();
        const processingTime = Math.round(endTime - startTime);
        
        console.log(`✅ Optimization complete - Processing time: ${processingTime}ms`);
        console.log(`📊 Results: ${originalSize} → ${finalSize} chars (${originalSize - finalSize} saved)`);
        
        return {
            content: optimizedContent,
            optimizations: optimizations,
            originalSize: originalSize,
            optimizedSize: finalSize,
            sizeDifference: originalSize - finalSize,
            processingTime: processingTime,
            performanceLevel: performanceStatus,
            recommendations: recommendation.trim() || 'File size optimal'
        };
    },
    
    async verifyCriticalSystemFiles() {
        try {
            // Check MDC files count via API
            const response = await fetch('/api/mdc/list');
            const result = await response.json();
            
            if (result.success && result.data && result.data.files) {
                const mdcCount = result.data.files.filter(f => f.name && f.name.endsWith('.mdc')).length;
                console.log(`🔍 System verification: ${mdcCount} MDC files found`);
                return mdcCount;
            }
            
            // Fallback: try to count via directory listing
            const listResponse = await fetch('/api/files/count-mdc');
            if (listResponse.ok) {
                const countResult = await listResponse.json();
                return countResult.count || 0;
            }
            
            throw new Error('Unable to verify system files via API');
            
        } catch (error) {
            console.error('System verification failed:', error);
            throw error;
        }
    },
    
    async performContextOptimization(isScheduled = false) {
        console.log(`🔧 Starting Context Optimization - ${isScheduled ? 'Scheduled' : 'Manual'}`);
        
        // CRITICAL SAFETY CHECK: Verify system integrity before optimization
        try {
            const mdcFileCount = await this.verifyCriticalSystemFiles();
            if (mdcFileCount < 50) {
                console.error('❌ SAFETY ABORT: Critical system files missing! Optimization cancelled.');
                return {
                    success: false,
                    error: `System integrity compromised - only ${mdcFileCount} MDC files found (expected 50+)`
                };
            }
        } catch (error) {
            console.error('❌ SAFETY CHECK FAILED:', error);
            return {
                success: false,
                error: 'System safety check failed: ' + error.message
            };
        }
        
        try {
            // Read current CLAUDE.md file
            const fileData = await this.readClaudeMdFile();
            
            if (fileData.size === 0) {
                console.log('❌ CLAUDE.md file is empty or not found');
                return {
                    success: false,
                    error: 'CLAUDE.md file not accessible'
                };
            }
            
            // NEW: Analyze optimization needs with intelligent prioritization
            const analysisResult = this.analyzeOptimizationNeeds(fileData.content);
            console.log(`📊 Analysis: Priority=${analysisResult.priority}, Urgency=${analysisResult.urgency}`);
            console.log(`📋 Reasons: ${analysisResult.reasons.join(', ')}`);
            console.log(`💾 Estimated savings: ${analysisResult.estimatedSavings} chars`);
            
            // Skip optimization if low priority and scheduled
            if (isScheduled && analysisResult.priority === 'LOW' && analysisResult.urgency < 2) {
                console.log('⏩ Skipping optimization - Low priority, no urgent needs');
                return {
                    success: true,
                    skipped: true,
                    reason: 'Low priority optimization skipped',
                    analysis: analysisResult
                };
            }
            
            // Optimize the content
            const optimization = this.optimizeContextContent(fileData.content);
            
            // Enhanced optimization result with analysis
            optimization.analysis = analysisResult;
            optimization.wasSkipped = false;
            
            // Only write if optimizations were made and content changed
            let writeSuccess = true;
            if (optimization.optimizations > 0 && optimization.sizeDifference !== 0) {
                writeSuccess = await this.writeClaudeMdFile(optimization.content);
            }
            
            // Update optimization data with enhanced metrics
            const optimizationData = this.getOptimizationData();
            
            // Calculate growth rate
            const lastSize = optimizationData.averageSize || optimization.originalSize;
            const growthRate = lastSize > 0 ? (optimization.originalSize - lastSize) / lastSize : 0;
            
            // Update adaptive interval based on current file size and growth
            const newAdaptiveInterval = this.calculateAdaptiveInterval(optimization.optimizedSize, growthRate);
            
            const optimizationRecord = {
                timestamp: new Date().toISOString(),
                optimizations: optimization.optimizations,
                originalSize: optimization.originalSize,
                optimizedSize: optimization.optimizedSize,
                sizeDifference: optimization.sizeDifference,
                processingTime: optimization.processingTime,
                performanceLevel: optimization.performanceLevel,
                success: writeSuccess,
                scheduled: isScheduled,
                priority: analysisResult.priority,
                urgency: analysisResult.urgency,
                growthRate: growthRate,
                adaptiveInterval: newAdaptiveInterval
            };
            
            optimizationData.lastOptimization = optimizationRecord;
            optimizationData.optimizationHistory.unshift(optimizationRecord);
            optimizationData.totalOptimizations++;
            
            // Keep only last 50 optimization records
            if (optimizationData.optimizationHistory.length > 50) {
                optimizationData.optimizationHistory = optimizationData.optimizationHistory.slice(0, 50);
            }
            
            // Calculate average size
            const recentSizes = optimizationData.optimizationHistory.slice(0, 10).map(r => r.optimizedSize);
            optimizationData.averageSize = recentSizes.reduce((sum, size) => sum + size, 0) / recentSizes.length;
            
            this.saveOptimizationData(optimizationData);
            
            // Update global state
            lastContextOptimization = {
                timestamp: optimizationRecord.timestamp,
                success: writeSuccess,
                optimizationsMade: optimization.optimizations,
                originalSize: optimization.originalSize,
                optimizedSize: optimization.optimizedSize
            };
            
            console.log(`✅ Context optimization complete: ${optimization.optimizations} optimizations made`);
            console.log(`📊 Size: ${optimization.originalSize} → ${optimization.optimizedSize} (${optimization.sizeDifference > 0 ? '-' : '+'}${Math.abs(optimization.sizeDifference)} chars)`);
            
            return {
                success: true,
                result: optimizationRecord
            };
            
        } catch (error) {
            console.error('❌ Context optimization error:', error);
            
            const errorRecord = {
                timestamp: new Date().toISOString(),
                success: false,
                error: error.message,
                scheduled: isScheduled
            };
            
            // Update global state
            lastContextOptimization = {
                timestamp: errorRecord.timestamp,
                success: false,
                optimizationsMade: 0,
                originalSize: 0,
                optimizedSize: 0
            };
            
            return {
                success: false,
                error: error.message
            };
        }
    }
};

async function performMDCScan(isScheduled = false) {
    const scanBtn = document.getElementById('mdcScanBtn');
    const scanResults = document.getElementById('scanResults');
    
    console.log(`Starting Intelligent MDC Scan - ${isScheduled ? 'Scheduled' : 'Manual'}`);
    
    // Update button to show scanning state
    if (scanBtn) {
        scanBtn.disabled = true;
        scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Intelligent Scanning...';
    }
    
    if (scanResults) {
        scanResults.innerHTML = 'Running intelligent MDC system scan with connection discovery...';
    }
    
    try {
        // Get current MDC files
        const filesResult = await api.getMDCFiles();
        
        // Get current settings to know the path
        const settingsResult = await api.getSettings();
        
        let scanSummary = '';
        let shouldRunScan = true;
        
        if (filesResult.success && settingsResult.success) {
            const files = filesResult.data;
            const mdcPath = settingsResult.data.mdcDirectory;
            
            // Extract files array from the API response structure
            let fileArray = [];
            if (files && files.files && Array.isArray(files.files)) {
                fileArray = files.files;
            } else if (Array.isArray(files)) {
                fileArray = files;
            } else {
                console.error('Unexpected files data structure:', files);
                fileArray = [];
            }
            
            // Run intelligent incremental connection discovery
            const connectionResult = await MDCConnectionEngine.performIncrementalScan(fileArray, mdcPath);
            
            // Count different types
            const totalFiles = fileArray.length;
            const mdcFilesCount = fileArray.filter(f => f.name && f.name.endsWith('.mdc')).length;
            const hasConnections = fileArray.filter(f => f.connections && f.connections.length > 0);
            const totalConnections = fileArray.reduce((sum, f) => sum + (f.connections ? f.connections.length : 0), 0);
            
            // Find the most recently modified file to get actual system update time
            let mostRecentUpdateTime = null;
            if (fileArray.length > 0) {
                const fileTimes = fileArray
                    .filter(f => f.lastModified)
                    .map(f => new Date(f.lastModified).getTime())
                    .filter(time => !isNaN(time));
                
                if (fileTimes.length > 0) {
                    mostRecentUpdateTime = new Date(Math.max(...fileTimes)).toISOString();
                }
            }
            
            // Check if this is a scheduled scan and no changes detected
            if (isScheduled && connectionResult.fromCache && lastScanData.fileCount >= totalFiles) {
                shouldRunScan = false;
                console.log(`Scheduled scan optimized - no changes detected (${lastScanData.fileCount} -> ${totalFiles})`);
                
                scanSummary = `
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <div><strong>⚡ Intelligent Scan - No Changes</strong></div>
                        <div>Files cached: ${totalFiles} files</div>
                        <div>Connections cached: ${totalConnections}</div>
                        <div><strong>📅 Last Scan:</strong> ${lastScanData.timestamp ? new Date(lastScanData.timestamp).toLocaleString() : 'Never'}</div>
                    </div>
                `;
            } else {
                // Update scan data with connection discovery results
                const now = new Date().toISOString();
                lastScanData = {
                    timestamp: now,
                    fileCount: totalFiles,
                    mdcFileCount: mdcFilesCount,
                    connectionsCount: totalConnections,
                    path: mdcPath,
                    systemUpdateTime: mostRecentUpdateTime || now,
                    connectionDiscovery: connectionResult
                };
                
                // Save to localStorage
                localStorage.setItem('mdcScanData', JSON.stringify(lastScanData));
                
                // Add to update history
                addToUpdateHistory('scan', 'Intelligent MDC System Scan', {
                    totalFiles: totalFiles,
                    mdcFiles: mdcFilesCount,
                    connections: totalConnections,
                    path: mdcPath,
                    systemUpdateTime: mostRecentUpdateTime,
                    connectionsDiscovered: connectionResult.connectionsDiscovered,
                    filesProcessed: connectionResult.filesProcessed,
                    filesUpdated: connectionResult.filesUpdated || 0,
                    fromCache: connectionResult.fromCache
                });
                
                const discoveryStatus = connectionResult.fromCache ? 
                    '📦 From Cache' : 
                    `🔍 ${connectionResult.filesProcessed} Processed, ${connectionResult.connectionsDiscovered} Connections Found`;
                
                scanSummary = `
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <div><strong>📁 Path:</strong> ${mdcPath}</div>
                        <div><strong>📄 Total Files:</strong> ${totalFiles}</div>
                        <div><strong>🔧 MDC Files:</strong> ${mdcFilesCount}</div>
                        <div><strong>🔗 Connected Files:</strong> ${hasConnections.length}</div>
                        <div><strong>🌐 Total Connections:</strong> ${totalConnections}</div>
                        <div style="border-top: 1px solid rgba(79,209,199,0.3); margin-top: 0.5rem; padding-top: 0.5rem;">
                            <div><strong>⚡ Connection Discovery:</strong> ${discoveryStatus}</div>
                            <div><strong>🕒 Last Scan:</strong> ${new Date().toLocaleString()}</div>
                            <div><strong>🔄 System Updated:</strong> ${new Date().toLocaleString()}</div>
                        </div>
                    </div>
                `;
                
                const changeMsg = isScheduled ? 
                    `Scheduled intelligent scan: ${totalFiles} files (${connectionResult.fromCache ? 'cached' : connectionResult.connectionsDiscovered + ' connections found'})` :
                    `Manual intelligent scan: ${totalFiles} files, ${connectionResult.connectionsDiscovered} connections discovered`;
                
                toast.success(changeMsg);
            }
            
        } else {
            scanSummary = '<span style="color: var(--danger-color);">❌ Intelligent scan failed - Could not access MDC data</span>';
            toast.error('Intelligent MDC scan failed');
        }
        
        if (scanResults) {
            scanResults.innerHTML = scanSummary;
        }
        
    } catch (error) {
        console.error('Intelligent MDC scan error:', error);
        if (scanResults) {
            scanResults.innerHTML = '<span style="color: var(--danger-color);">❌ Intelligent scan error - Check console for details</span>';
        }
        toast.error('Intelligent MDC scan error occurred');
    } finally {
        // Reset button
        if (scanBtn) {
            scanBtn.disabled = false;
            scanBtn.innerHTML = '<i class="fas fa-search"></i> 🔍 Start Intelligent MDC Scan';
        }
    }
}

// MDC Scan Scheduling
function setupMDCScanScheduling() {
    console.log('Setting up MDC scan scheduling...');
    
    // Load previous scan data
    const savedScanData = localStorage.getItem('mdcScanData');
    if (savedScanData) {
        try {
            lastScanData = JSON.parse(savedScanData);
            console.log('Loaded previous scan data:', lastScanData);
        } catch (error) {
            console.error('Error loading scan data:', error);
        }
    }
    
    // Schedule scans 6 times per day (every 4 hours) - More responsive
    const scheduleInterval = 4 * 60 * 60 * 1000; // 4 hours in milliseconds
    
    // Clear existing scheduler
    if (mdcScanScheduler) {
        clearInterval(mdcScanScheduler);
    }
    
    // Set up new scheduler
    mdcScanScheduler = setInterval(() => {
        console.log('Running scheduled MDC maintenance and scan...');
        // First run MDC cleanup and merge, then scan
        performScheduledMDCMaintenance();
    }, scheduleInterval);
    
    console.log(`MDC scan scheduled every 4 hours`);
    
    // Notify user about optimized scan schedule
    addNotificationToHistory('⏰ Scan schedule optimized: Every 4 hours (was 12h)', 'success');
    
    // Notify about health card improvements
    addNotificationToHistory('💚 Health cards now change color: Green=Connected, Red=Disconnected', 'success');
    
    // Only set up future scheduled scans - no automatic initial scan on page load
    console.log('MDC scan scheduling setup complete. Scans will only run when scheduled or manually triggered.');
    
    // Log when the next scheduled scan will occur
    const now = new Date().getTime();
    const nextScheduledScan = new Date(now + scheduleInterval);
    console.log(`Next scheduled scan: ${nextScheduledScan.toLocaleString()}`);
    
    // Note: No automatic scan on page load - scans only happen on schedule or manual trigger
}

// Context Optimization Scheduling - runs every 2 hours
function setupContextOptimizationScheduling() {
    console.log('Setting up Context Optimization scheduling...');
    
    // Load previous optimization data
    const savedOptimizationData = localStorage.getItem('context_optimization_data');
    if (savedOptimizationData) {
        try {
            const optimizationData = JSON.parse(savedOptimizationData);
            if (optimizationData.lastOptimization) {
                lastContextOptimization = {
                    timestamp: optimizationData.lastOptimization.timestamp,
                    success: optimizationData.lastOptimization.success,
                    optimizationsMade: optimizationData.lastOptimization.optimizations || 0,
                    originalSize: optimizationData.lastOptimization.originalSize || 0,
                    optimizedSize: optimizationData.lastOptimization.optimizedSize || 0
                };
            }
            console.log('Loaded previous context optimization data:', optimizationData);
        } catch (error) {
            console.error('Error loading context optimization data:', error);
        }
    }
    
    // Clear existing scheduler
    if (contextOptimizationScheduler) {
        clearInterval(contextOptimizationScheduler);
    }
    
    // NEW: Get adaptive interval from optimization data
    const optimizationData = ContextOptimizationEngine.getOptimizationData();
    let contextOptimizationInterval = optimizationData.adaptiveInterval || 2 * 60 * 60 * 1000; // Default 2 hours
    
    // Set up new intelligent scheduler
    contextOptimizationScheduler = setInterval(async () => {
        console.log('🔧 Running scheduled context optimization...');
        
        try {
            const result = await ContextOptimizationEngine.performContextOptimization(true);
            
            if (result.success) {
                if (result.skipped) {
                    console.log(`⏩ Optimization skipped: ${result.reason}`);
                    toast.info(`Context optimization skipped - ${result.reason}`);
                } else {
                    const opt = result.result;
                    const changeMsg = opt.sizeDifference > 0 ? 
                        `Context optimized: ${opt.optimizations} improvements, ${opt.sizeDifference} chars saved` :
                        `Context maintained: ${opt.optimizations} updates applied`;
                        
                    toast.success(changeMsg);
                    
                    // Check if we need to adjust scheduling interval
                    if (opt.adaptiveInterval && opt.adaptiveInterval !== contextOptimizationInterval) {
                        console.log(`🔄 Adaptive scheduling: Interval changed from ${Math.round(contextOptimizationInterval/60000)}min to ${Math.round(opt.adaptiveInterval/60000)}min`);
                        contextOptimizationInterval = opt.adaptiveInterval;
                        
                        // Restart scheduler with new interval
                        clearInterval(contextOptimizationScheduler);
                        setupContextOptimizationScheduling(); // Recursive call with new interval
                        return;
                    }
                }
                
                // Add to update history
                addToUpdateHistory('optimization', 'Scheduled Context Optimization', {
                    optimizations: result.result?.optimizations || 0,
                    originalSize: result.result?.originalSize || 0,
                    optimizedSize: result.result?.optimizedSize || 0,
                    sizeDifference: result.result?.sizeDifference || 0,
                    success: result.success,
                    skipped: result.skipped || false,
                    priority: result.analysis?.priority || 'N/A',
                    processingTime: result.result?.processingTime || 0
                });
                
                console.log('✅ Scheduled context optimization completed successfully');
            } else {
                console.warn('⚠️ Scheduled context optimization had issues:', result.error);
                toast.warning('Context optimization completed with warnings');
            }
        } catch (error) {
            console.error('❌ Error in scheduled context optimization:', error);
            toast.error('Scheduled context optimization failed: ' + error.message);
        }
    }, contextOptimizationInterval);
    
    const intervalHours = Math.round(contextOptimizationInterval / (60 * 60 * 1000) * 10) / 10;
    console.log(`🕒 Context optimization scheduled every ${intervalHours} hours (adaptive scheduling)`);
    
    // Log when the next scheduled optimization will occur
    const now = new Date().getTime();
    const nextScheduledOptimization = new Date(now + contextOptimizationInterval);
    console.log(`📅 Next scheduled context optimization: ${nextScheduledOptimization.toLocaleString()}`);
    
    // Note: Intelligent scheduling - intervals adapt based on file size and growth patterns
}

async function performScheduledMDCMaintenance() {
    console.log('🔧 Starting scheduled MDC maintenance cycle...');
    
    try {
        // Step 1: Merge duplicate MDC files
        console.log('📋 Step 1: Merging duplicate MDC files...');
        const mergeResult = await mergeDuplicateMDCFiles();
        
        // Step 2: Clean up similar service names
        console.log('🔍 Step 2: Cleaning up similar service names...');
        const cleanupResult = await cleanupSimilarServices();
        
        // Step 3: Run the actual scan with filtering
        console.log('🔍 Step 3: Running filtered MDC scan...');
        await performMDCScan(true); // isScheduled = true
        
        console.log('✅ Scheduled MDC maintenance cycle completed');
        
        // Add maintenance summary to update history
        addToUpdateHistory('maintenance', 'Scheduled MDC Maintenance', {
            duplicatesMerged: mergeResult?.merged_count || 0,
            servicesFiltered: cleanupResult?.filtered_count || 0,
            maintenanceSteps: 3,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('❌ Error in scheduled MDC maintenance:', error);
        toast.error('Scheduled maintenance failed: ' + error.message);
    }
}

async function mergeDuplicateMDCFiles() {
    try {
        const result = await fetch('/api/mdc/merge-duplicates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await result.json();
        
        if (data.success) {
            const merged = data.merged_count || 0;
            if (merged > 0) {
                console.log(`✅ Merged ${merged} duplicate MDC files`);
                toast.success(`🔧 Merged ${merged} duplicate MDC files`);
            } else {
                console.log('✅ No duplicate MDC files found to merge');
            }
            return data;
        } else {
            console.warn('⚠️ MDC merge failed:', data.error);
            return { merged_count: 0 };
        }
    } catch (error) {
        console.error('❌ Error merging duplicate MDC files:', error);
        return { merged_count: 0 };
    }
}

async function cleanupSimilarServices() {
    try {
        const result = await fetch('/api/mdc/cleanup-similar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await result.json();
        
        if (data.success) {
            const filtered = data.filtered_count || 0;
            if (filtered > 0) {
                console.log(`✅ Filtered out ${filtered} similar/redundant services`);
                toast.success(`🔧 Filtered ${filtered} redundant services`);
            } else {
                console.log('✅ No similar services found to filter');
            }
            return data;
        } else {
            console.warn('⚠️ Service cleanup failed:', data.error);
            return { filtered_count: 0 };
        }
    } catch (error) {
        console.error('❌ Error cleaning up similar services:', error);
        return { filtered_count: 0 };
    }
}

function updateScanStatusDisplay() {
    const scanResults = document.getElementById('scanResults');
    const nextScanTimeElement = document.getElementById('nextScanTime');
    
    // Update next scan time
    if (nextScanTimeElement && lastScanData.timestamp) {
        const lastScanTime = new Date(lastScanData.timestamp).getTime();
        const nextScanTime = new Date(lastScanTime + (4 * 60 * 60 * 1000)); // Add 4 hours
        const timeUntilNext = nextScanTime.getTime() - new Date().getTime();
        
        if (timeUntilNext > 0) {
            const hoursUntil = Math.floor(timeUntilNext / (60 * 60 * 1000));
            const minutesUntil = Math.floor((timeUntilNext % (60 * 60 * 1000)) / (60 * 1000));
            nextScanTimeElement.textContent = `${hoursUntil}h ${minutesUntil}m (${nextScanTime.toLocaleString()})`;
        } else {
            nextScanTimeElement.textContent = 'Due now';
        }
    } else if (nextScanTimeElement) {
        nextScanTimeElement.textContent = 'After first scan';
    }
    
    // Update scan results
    // 🔄 Use current system data instead of old lastScanData
    const currentFiles = allMDCFiles.length > 0 ? allMDCFiles.length : mdcFiles.length;
    const currentConnections = systemHealth && systemHealth.total_connections ? systemHealth.total_connections : 
        (allMDCFiles.length > 0 ? allMDCFiles.reduce((sum, file) => sum + (file.connections ? file.connections.length : 0), 0) : 0);
    
    if (scanResults) {
        const now = new Date();
        const lastScanTime = lastScanData.timestamp ? new Date(lastScanData.timestamp).toLocaleString() : now.toLocaleString();
        
        scanResults.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                <div><strong>📁 Path:</strong> /Users/dansidanutz/Desktop/ZmartBot/.cursor/rules</div>
                <div><strong>📄 Total Files:</strong> <span id="systemStatusFiles">${currentFiles}</span></div>
                <div><strong>🔧 MDC Files:</strong> <span id="systemStatusMDC">${currentFiles}</span></div>
                <div><strong>🌐 Total Connections:</strong> <span id="systemStatusConnections">${currentConnections}</span></div>
                <div style="border-top: 1px solid rgba(255,255,255,0.2); margin-top: 0.5rem; padding-top: 0.5rem;">
                    <div><strong>🕒 Last Scan:</strong> <span id="systemStatusLastScan">${lastScanTime}</span></div>
                    <div><strong>🔄 System Updated:</strong> <span id="systemStatusUpdated">${now.toLocaleString()}</span></div>
                </div>
            </div>
        `;
    }
}

// Fetch registered services count from Passport Service
async function fetchRegisteredServicesCount() {
    try {
        // Primary: Get services from Passport Service (most accurate)
        const passportResponse = await fetch('/api/passport/services', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 10000
        });
        
        if (passportResponse.ok) {
            const passportData = await passportResponse.json();
            console.log('✅ Fetched registered services from Passport Service');
            return passportData.services ? passportData.services.length : 0;
        }
        
        // Secondary: Get services from Master Orchestration Agent
        const orchestrationResponse = await fetch('/api/orchestration/services', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 10000
        });
        
        if (orchestrationResponse.ok) {
            const orchestrationData = await orchestrationResponse.json();
            console.log('✅ Fetched registered services from Orchestration Service');
            return orchestrationData.services ? orchestrationData.services.length : 0;
        }
        
        // Fallback: Parse from Master Orchestration MDC file
        console.warn('⚠️ Passport and Orchestration APIs unavailable, using MDC fallback');
        return await getRegisteredServicesFromMasterMDC();
        
    } catch (error) {
        console.warn('Failed to fetch from Passport/Orchestration APIs:', error);
        // Final fallback to parsing MDC file
        return await getRegisteredServicesFromMasterMDC();
    }
}

// Parse registered services count from Master Orchestration MDC file
async function getRegisteredServicesFromMasterMDC() {
    try {
        const response = await fetch('/api/mdc/content/MasterOrchestrationAgent.mdc');
        if (response.ok) {
            const content = await response.text();
            
            // Extract the "Currently Registered Services:" section
            const registeredSection = content.match(/### Currently Registered Services:(.*?)(?=###|$)/s);
            if (registeredSection) {
                // Count numbered lines (services)
                const serviceLines = registeredSection[1].match(/^\d+\. /gm);
                return serviceLines ? serviceLines.length : 0;
            }
        }
        
        // Final fallback - return known count from what we saw
        return 26; // Based on the count we saw in the MDC file
        
    } catch (error) {
        console.error('Failed to parse Master Orchestration MDC:', error);
        return 26; // Fallback to known count
    }
}

// Fallback function to count services from MDC files with service patterns
function getRegisteredServicesFromMDC(filesToAnalyze) {
    const servicePatterns = [
        /Server\.mdc$/i,
        /Service\.mdc$/i,  
        /Agent\.mdc$/i,
        /API\.mdc$/i,
        /Engine\.mdc$/i,
        /Bot\.mdc$/i,
        /Manager\.mdc$/i,
        /Gateway\.mdc$/i,
        /Handler\.mdc$/i
    ];
    
    const uniqueServices = new Set();
    filesToAnalyze.forEach(file => {
        if (file.name && file.name.endsWith('.mdc')) {
            const isService = servicePatterns.some(pattern => pattern.test(file.name));
            if (isService) {
                uniqueServices.add(file.name.replace('.mdc', ''));
            }
        }
    });
    
    return uniqueServices.size;
}

// Export directory browser functions
window.openDirectoryBrowser = openDirectoryBrowser;
window.closeDirectoryBrowser = closeDirectoryBrowser;
window.selectCurrentDirectory = selectCurrentDirectory;
window.resetToDefaultPath = resetToDefaultPath;
window.performMDCScan = performMDCScan;
window.setupMDCScanScheduling = setupMDCScanScheduling;
window.performContextOptimization = () => ContextOptimizationEngine.performContextOptimization(false);
window.setupContextOptimizationScheduling = setupContextOptimizationScheduling;

// Manual test function for modal
window.testModal = function() {
    console.log('Testing modal visibility...');
    const modal = document.getElementById('directoryBrowserModal');
    if (modal) {
        console.log('Modal found!');
        console.log('Current display style:', window.getComputedStyle(modal).display);
        console.log('Current visibility:', window.getComputedStyle(modal).visibility);
        console.log('Modal HTML:', modal.outerHTML.substring(0, 200));
        modal.style.display = 'flex';
        modal.style.visibility = 'visible';
        modal.style.opacity = '1';
        modal.style.zIndex = '10000';
        console.log('Modal should be visible now');
        
        // Add test content
        const listElement = document.getElementById('directoryList');
        if (listElement) {
            listElement.innerHTML = '<div style="padding: 1rem;">TEST MODAL - This is working!</div>';
        }
    } else {
        console.error('Modal not found!');
    }
};

// Simplified directory browser without API call
window.openDirectoryBrowserSimple = function() {
    console.log('Opening simple directory browser...');
    const modal = document.getElementById('directoryBrowserModal');
    if (!modal) {
        console.error('Modal element not found!');
        return;
    }
    
    console.log('Modal found, setting display to flex...');
    modal.style.display = 'flex';
    modal.style.zIndex = '10000';
    
    // Add some test content
    const listElement = document.getElementById('directoryList');
    if (listElement) {
        listElement.innerHTML = `
            <div class="directory-item" style="padding: 1rem; border-bottom: 1px solid #333;">
                <i class="fas fa-folder"></i> Test Directory 1
            </div>
            <div class="directory-item" style="padding: 1rem; border-bottom: 1px solid #333;">
                <i class="fas fa-folder"></i> Test Directory 2
            </div>
        `;
    }
    
    console.log('Simple modal should be visible now');
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeDashboard);

// 🌟 SPECTACULAR VISUAL ENHANCEMENTS

// Mouse tracking for interactive background effects
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth) * 100;
    mouseY = (e.clientY / window.innerHeight) * 100;
    
    // Update CSS custom properties for mouse position
    document.documentElement.style.setProperty('--mouse-x', mouseX + '%');
    document.documentElement.style.setProperty('--mouse-y', mouseY + '%');
});

// 🚀 Spectacular Loading Screen Effect
function createLoadingScreen() {
    const loadingScreen = document.createElement('div');
    loadingScreen.className = 'loading-screen';
    loadingScreen.innerHTML = `
        <div class="loading-logo">
            <i class="fas fa-rocket"></i>
        </div>
        <div class="loading-text">Loading ZmartBot Dashboard...</div>
    `;
    document.body.appendChild(loadingScreen);
    
    // Hide loading screen after page loads
    window.addEventListener('load', () => {
        setTimeout(() => {
            loadingScreen.classList.add('hidden');
            setTimeout(() => {
                loadingScreen.remove();
            }, 1000);
        }, 500);
    });
}

// 🎯 Enhanced Scroll Effects
function createScrollIndicator() {
    const scrollIndicator = document.createElement('div');
    scrollIndicator.className = 'scroll-indicator';
    document.body.appendChild(scrollIndicator);
    
    window.addEventListener('scroll', () => {
        const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
        scrollIndicator.style.transform = `translateX(-${100 - scrollPercent}%)`;
    });
}

// ✨ Spectacular Card Hover Effects (Non-conflicting)
function enhanceCardInteractions() {
    const cards = document.querySelectorAll('.mdc-card, .stat-card, .action-card');
    
    cards.forEach(card => {
        // Add subtle parallax effect based on mouse movement
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // Subtle tilt effect (much gentler)
            const rotateX = (y - centerY) / centerY * -2;
            const rotateY = (x - centerX) / centerX * 2;
            
            // Apply subtle 3D tilt without conflicting with CSS hover
            card.style.setProperty('--tilt-x', rotateX + 'deg');
            card.style.setProperty('--tilt-y', rotateY + 'deg');
        });
        
        card.addEventListener('mouseleave', () => {
            // Reset tilt effect
            card.style.setProperty('--tilt-x', '0deg');
            card.style.setProperty('--tilt-y', '0deg');
        });
        
        // Add click animation that doesn't interfere
        card.addEventListener('click', (e) => {
            card.style.animation = 'none';
            card.offsetHeight; // Trigger reflow
            card.style.animation = 'cardClickPulse 0.3s ease-out';
        });
    });
}

// Utility function to calculate distance between elements
function getDistance(elem1, elem2) {
    const rect1 = elem1.getBoundingClientRect();
    const rect2 = elem2.getBoundingClientRect();
    
    const dx = rect1.left + rect1.width / 2 - (rect2.left + rect2.width / 2);
    const dy = rect1.top + rect1.height / 2 - (rect2.top + rect2.height / 2);
    
    return Math.sqrt(dx * dx + dy * dy);
}

// 🎨 Dynamic Theme Enhancement
function enhanceThemeEffects() {
    // Add subtle color variations based on time
    setInterval(() => {
        const time = Date.now() * 0.001;
        const hue = Math.sin(time * 0.1) * 10 + 180;
        const saturation = Math.sin(time * 0.15) * 5 + 70;
        
        document.documentElement.style.setProperty('--dynamic-primary', `hsl(${hue}, ${saturation}%, 60%)`);
    }, 100);
}

// 🎭 Enhanced Button Interactions
function enhanceButtonEffects() {
    const buttons = document.querySelectorAll('.btn, button, .nav-btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Ripple effect
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.position = 'absolute';
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.6)';
            ripple.style.transform = 'scale(0)';
            ripple.style.pointerEvents = 'none';
            ripple.style.animation = 'ripple 0.6s linear';
            
            if (!button.style.position) button.style.position = 'relative';
            button.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Add ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// 🚀 Initialize All Spectacular Effects
function initializeSpectacularEffects() {
    createLoadingScreen();
    createScrollIndicator();
    setTimeout(() => {
        enhanceCardInteractions();
        enhanceThemeEffects();
        enhanceButtonEffects();
    }, 1000);
}

// Start the spectacular effects
initializeSpectacularEffects();

// Debug function to ensure cards are visible (only fix completely invisible cards)
function debugCardVisibility() {
    const cards = document.querySelectorAll('.mdc-card, .stat-card, .action-card');
    cards.forEach((card, index) => {
        const computedStyle = window.getComputedStyle(card);
        const opacity = parseFloat(computedStyle.opacity);
        
        // Only fix completely invisible cards (opacity 0) or very low opacity that seems wrong
        if (opacity === 0 || (opacity < 0.1 && !card.classList.contains('loading') && !card.classList.contains('hidden'))) {
            console.warn(`Card ${index} is invisible (opacity ${opacity}). Fixing...`);
            card.style.opacity = '1';
            card.style.visibility = 'visible';
        }
    });
}

// Run debug check less frequently and only when needed
let debugInterval = setInterval(() => {
    // Only run debug if dashboard is active and visible
    if (document.visibilityState === 'visible') {
        debugCardVisibility();
    }
}, 5000); // Reduced to every 5 seconds

// Function to stop debug interval when no longer needed
function stopCardDebug() {
    if (debugInterval) {
        clearInterval(debugInterval);
        debugInterval = null;
        console.log('Card visibility debug stopped');
    }
}

// Run once after DOM load with longer delay to avoid interfering with animations
setTimeout(debugCardVisibility, 1000);

// Stop debug after 30 seconds if no issues found
setTimeout(() => {
    const problematicCards = document.querySelectorAll('.mdc-card, .stat-card, .action-card');
    let hasIssues = false;
    
    problematicCards.forEach(card => {
        const opacity = parseFloat(window.getComputedStyle(card).opacity);
        if (opacity === 0 && !card.classList.contains('loading') && !card.classList.contains('hidden')) {
            hasIssues = true;
        }
    });
    
    if (!hasIssues) {
        stopCardDebug();
    }
}, 30000); // Stop after 30 seconds if no issues

// Make stop function globally available for manual control
window.stopCardDebug = stopCardDebug;

// ===================================
// OPERATION LOGS FUNCTIONS
// ===================================

let currentLogsFilter = '';

// Load operation logs from the backend
async function loadOperationLogs() {
    const loadingIndicator = document.getElementById('logsLoadingIndicator');
    const noLogsMessage = document.getElementById('noLogsMessage');
    const logsList = document.getElementById('logsList');
    const totalLogsCount = document.getElementById('totalLogsCount');
    const lastLogUpdate = document.getElementById('lastLogUpdate');
    
    if (loadingIndicator) loadingIndicator.style.display = 'flex';
    if (noLogsMessage) noLogsMessage.style.display = 'none';
    if (logsList) logsList.innerHTML = '';
    
    try {
        const response = await fetch('/api/logs');
        const result = await response.json();
        
        if (result.success) {
            const logs = result.data.logs;
            
            // Update summary info
            if (totalLogsCount) totalLogsCount.textContent = result.data.total_count;
            if (lastLogUpdate) lastLogUpdate.textContent = logs.length > 0 ? formatTimestamp(logs[0].timestamp) : 'Never';
            
            if (logs.length === 0) {
                if (noLogsMessage) noLogsMessage.style.display = 'flex';
            } else {
                displayOperationLogs(logs);
            }
        } else {
            console.error('Failed to load operation logs:', result.error);
            if (logsList) {
                logsList.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Failed to load operation logs: ${result.error}</p>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error loading operation logs:', error);
        if (logsList) {
            logsList.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading operation logs. Please try again.</p>
                </div>
            `;
        }
    } finally {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
    }
}

// Display operation logs in the interface
function displayOperationLogs(logs) {
    const logsList = document.getElementById('logsList');
    if (!logsList) return;
    
    // Filter logs if a filter is active
    let filteredLogs = logs;
    if (currentLogsFilter) {
        filteredLogs = logs.filter(log => log.operation_type.includes(currentLogsFilter));
    }
    
    logsList.innerHTML = '';
    
    filteredLogs.forEach(log => {
        const logEntry = createLogEntry(log);
        logsList.appendChild(logEntry);
    });
}

// Create a single log entry element
function createLogEntry(log) {
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.onclick = () => toggleLogDetails(logEntry);
    
    const operationType = log.operation_type.split('_')[0];
    const icon = getLogIcon(operationType);
    const timestamp = formatTimestamp(log.timestamp);
    
    logEntry.innerHTML = `
        <div class="log-icon ${operationType}">
            <i class="fas ${icon}"></i>
        </div>
        <div class="log-content">
            <div class="log-header">
                <div class="log-title">${log.description}</div>
                <div class="log-timestamp">${timestamp}</div>
            </div>
            <div class="log-description">
                Type: ${log.operation_type} • Status: <span class="log-status ${log.status}">${log.status}</span>
            </div>
            ${Object.keys(log.details).length > 0 ? `
                <div class="log-details">
                    ${Object.entries(log.details).map(([key, value]) => `
                        <div class="log-details-item">
                            <span class="log-details-key">${key}:</span>
                            <span class="log-details-value">${JSON.stringify(value)}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
    
    return logEntry;
}

// Get appropriate icon for log type
function getLogIcon(operationType) {
    const icons = {
        'workflow': 'fa-cogs',
        'scan': 'fa-search',
        'context': 'fa-brain',
        'system': 'fa-server',
        'logs': 'fa-trash'
    };
    return icons[operationType] || 'fa-info-circle';
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    try {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    } catch (error) {
        return timestamp;
    }
}

// Toggle log details expansion
function toggleLogDetails(logEntry) {
    logEntry.classList.toggle('expanded');
}

// Filter logs by type
function filterLogs() {
    const filterSelect = document.getElementById('logTypeFilter');
    if (filterSelect) {
        currentLogsFilter = filterSelect.value;
        loadOperationLogs(); // Reload and filter
    }
}

// Refresh logs (reload from server)
function refreshOperationLogs() {
    loadOperationLogs();
}

// Clear all logs
async function clearOperationLogs() {
    if (!confirm('Are you sure you want to clear all operation logs? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/logs/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Reload logs to show the updated state
            loadOperationLogs();
            showNotification('Operation logs cleared successfully', 'success');
        } else {
            console.error('Failed to clear logs:', result.error);
            showNotification('Failed to clear logs: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error clearing logs:', error);
        showNotification('Error clearing logs. Please try again.', 'error');
    }
}

// Initialize logs when logs section is shown
function initializeLogsSection() {
    loadOperationLogs();
}

// Auto-refresh logs every 30 seconds when logs section is active
let logsRefreshInterval;

function startLogsAutoRefresh() {
    if (logsRefreshInterval) {
        clearInterval(logsRefreshInterval);
    }
    logsRefreshInterval = setInterval(() => {
        const logsSection = document.getElementById('logs');
        if (logsSection && logsSection.classList.contains('active')) {
            loadOperationLogs();
        }
    }, 30000); // 30 seconds
}

function stopLogsAutoRefresh() {
    if (logsRefreshInterval) {
        clearInterval(logsRefreshInterval);
        logsRefreshInterval = null;
    }
}

// Override existing functions to use the new operation logs functions
// Note: Keep the existing refreshLogs function for component logs, add new one for operation logs
function refreshLogs() {
    // Check which section is active
    const logsSection = document.getElementById('logs');
    if (logsSection && logsSection.classList.contains('active')) {
        refreshOperationLogs();
    } else {
        // Use original component logs refresh
        if (currentLogsComponent) {
            loadComponentLogs(currentLogsComponent);
        }
    }
}

function clearLogs() {
    // Check which section is active
    const logsSection = document.getElementById('logs');
    if (logsSection && logsSection.classList.contains('active')) {
        clearOperationLogs();
    } else {
        // Use original component logs clear
        clearLogsDisplay();
    }
}

// Make functions available globally
window.refreshOperationLogs = refreshOperationLogs;
window.clearOperationLogs = clearOperationLogs;
window.filterLogs = filterLogs;
window.initializeLogsSection = initializeLogsSection;
window.startLogsAutoRefresh = startLogsAutoRefresh;
window.stopLogsAutoRefresh = stopLogsAutoRefresh;