// API Service - Central API Integration Layer
// Connects all UI components with ZmartyChat backend services

class APIService {
    constructor(config = {}) {
        this.config = {
            baseURL: config.baseURL || window.location.origin + '/api/v1',
            timeout: config.timeout || 30000,
            retryAttempts: config.retryAttempts || 3,
            retryDelay: config.retryDelay || 1000,
            headers: {
                'Content-Type': 'application/json',
                'X-Client-Version': '1.0.0',
                ...config.headers
            }
        };

        this.authToken = null;
        this.refreshToken = null;
        this.interceptors = [];
        this.cache = new Map();
        this.pendingRequests = new Map();

        this.init();
    }

    init() {
        // Load tokens from localStorage
        this.authToken = localStorage.getItem('authToken');
        this.refreshToken = localStorage.getItem('refreshToken');

        // Set up request interceptors
        this.setupInterceptors();

        // Set up automatic token refresh
        this.setupTokenRefresh();
    }

    // Core request method
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.config.baseURL}${endpoint}`;
        const requestId = `${method}-${endpoint}-${JSON.stringify(data)}`;

        // Check cache for GET requests
        if (method === 'GET' && options.cache !== false) {
            const cached = this.getFromCache(requestId);
            if (cached) {
                return cached;
            }
        }

        // Prevent duplicate requests
        if (this.pendingRequests.has(requestId)) {
            return this.pendingRequests.get(requestId);
        }

        const requestConfig = {
            method,
            headers: {
                ...this.config.headers,
                ...options.headers
            },
            signal: this.createAbortSignal(options.timeout || this.config.timeout)
        };

        // Add auth token if available
        if (this.authToken && options.auth !== false) {
            requestConfig.headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        // Add body for non-GET requests
        if (data && method !== 'GET') {
            requestConfig.body = JSON.stringify(data);
        }

        // Add query parameters for GET requests
        let finalURL = url;
        if (data && method === 'GET') {
            const params = new URLSearchParams(data);
            finalURL = `${url}?${params.toString()}`;
        }

        // Create request promise
        const requestPromise = this.executeRequest(finalURL, requestConfig, options);
        this.pendingRequests.set(requestId, requestPromise);

        try {
            const response = await requestPromise;
            this.pendingRequests.delete(requestId);

            // Cache successful GET requests
            if (method === 'GET' && options.cache !== false) {
                this.addToCache(requestId, response, options.cacheTime);
            }

            return response;
        } catch (error) {
            this.pendingRequests.delete(requestId);
            throw error;
        }
    }

    async executeRequest(url, config, options = {}) {
        let lastError;

        for (let attempt = 0; attempt < this.config.retryAttempts; attempt++) {
            try {
                // Run request interceptors
                const interceptedConfig = await this.runInterceptors('request', config);

                const response = await fetch(url, interceptedConfig);

                // Handle non-OK responses
                if (!response.ok) {
                    if (response.status === 401 && options.retry !== false) {
                        // Try to refresh token
                        const refreshed = await this.refreshAuthToken();
                        if (refreshed) {
                            // Retry with new token
                            config.headers['Authorization'] = `Bearer ${this.authToken}`;
                            continue;
                        }
                    }

                    const error = await this.parseError(response);
                    throw error;
                }

                const data = await response.json();

                // Run response interceptors
                const interceptedData = await this.runInterceptors('response', data);

                return interceptedData;

            } catch (error) {
                lastError = error;

                // Don't retry on certain errors
                if (error.name === 'AbortError' || error.status === 400 || error.status === 404) {
                    throw error;
                }

                // Wait before retrying
                if (attempt < this.config.retryAttempts - 1) {
                    await this.sleep(this.config.retryDelay * Math.pow(2, attempt));
                }
            }
        }

        throw lastError;
    }

    // Authentication methods
    async login(email, password) {
        const response = await this.request('POST', '/auth/login', {
            email,
            password
        }, { auth: false });

        this.authToken = response.accessToken;
        this.refreshToken = response.refreshToken;

        localStorage.setItem('authToken', this.authToken);
        localStorage.setItem('refreshToken', this.refreshToken);
        localStorage.setItem('userId', response.user.id);

        return response;
    }

    async logout() {
        try {
            await this.request('POST', '/auth/logout');
        } catch (error) {
            console.error('Logout error:', error);
        }

        this.authToken = null;
        this.refreshToken = null;

        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userId');

        window.location.href = '/login';
    }

    async refreshAuthToken() {
        if (!this.refreshToken) {
            return false;
        }

        try {
            const response = await this.request('POST', '/auth/refresh', {
                refreshToken: this.refreshToken
            }, { auth: false, retry: false });

            this.authToken = response.accessToken;
            localStorage.setItem('authToken', this.authToken);

            return true;
        } catch (error) {
            console.error('Token refresh failed:', error);
            this.logout();
            return false;
        }
    }

    setupTokenRefresh() {
        // Refresh token every 45 minutes
        setInterval(() => {
            if (this.authToken) {
                this.refreshAuthToken();
            }
        }, 45 * 60 * 1000);
    }

    // User API endpoints
    async getUserProfile() {
        return this.request('GET', '/user/profile');
    }

    async updateUserProfile(data) {
        return this.request('PUT', '/user/profile', data);
    }

    async changePassword(currentPassword, newPassword) {
        return this.request('POST', '/user/change-password', {
            currentPassword,
            newPassword
        });
    }

    async enable2FA() {
        return this.request('POST', '/user/2fa/enable');
    }

    async verify2FA(code) {
        return this.request('POST', '/user/2fa/verify', { code });
    }

    // Trading API endpoints
    async getMarketData(symbol) {
        return this.request('GET', `/market/ticker/${symbol}`, null, {
            cache: true,
            cacheTime: 5000 // Cache for 5 seconds
        });
    }

    async getOrderBook(symbol, depth = 20) {
        return this.request('GET', `/market/orderbook/${symbol}`, { depth });
    }

    async getRecentTrades(symbol, limit = 50) {
        return this.request('GET', `/market/trades/${symbol}`, { limit });
    }

    async placeOrder(order) {
        return this.request('POST', '/orders', order);
    }

    async cancelOrder(orderId) {
        return this.request('DELETE', `/orders/${orderId}`);
    }

    async getOrders(status = 'all') {
        return this.request('GET', '/orders', { status });
    }

    async getOrderHistory(limit = 100) {
        return this.request('GET', '/orders/history', { limit });
    }

    // Portfolio API endpoints
    async getPortfolio() {
        return this.request('GET', '/portfolio');
    }

    async getPortfolioHistory(period = '30d') {
        return this.request('GET', '/portfolio/history', { period });
    }

    async getBalances() {
        return this.request('GET', '/portfolio/balances');
    }

    async getPositions() {
        return this.request('GET', '/portfolio/positions');
    }

    // AI Analysis API endpoints
    async getAIAnalysis(symbol, providers = ['openai', 'claude']) {
        return this.request('POST', '/ai/analyze', {
            symbol,
            providers
        });
    }

    async getAISignals(filters = {}) {
        return this.request('GET', '/ai/signals', filters);
    }

    async getAISentiment(symbol) {
        return this.request('GET', `/ai/sentiment/${symbol}`);
    }

    async getAIPrediction(symbol, timeframe = '24h') {
        return this.request('GET', `/ai/predict/${symbol}`, { timeframe });
    }

    // Admin API endpoints
    async getSystemMetrics() {
        return this.request('GET', '/admin/metrics');
    }

    async getCircuitBreakers() {
        return this.request('GET', '/admin/circuit-breakers');
    }

    async updateCircuitBreaker(name, action) {
        return this.request('POST', `/admin/circuit-breakers/${name}`, { action });
    }

    async getUsers(filters = {}) {
        return this.request('GET', '/admin/users', filters);
    }

    async updateUser(userId, data) {
        return this.request('PUT', `/admin/users/${userId}`, data);
    }

    async getTransactions(filters = {}) {
        return this.request('GET', '/admin/transactions', filters);
    }

    async getAuditLog(filters = {}) {
        return this.request('GET', '/admin/audit-log', filters);
    }

    // Billing API endpoints
    async getSubscription() {
        return this.request('GET', '/billing/subscription');
    }

    async updateSubscription(planId) {
        return this.request('POST', '/billing/subscription', { planId });
    }

    async getInvoices() {
        return this.request('GET', '/billing/invoices');
    }

    async getPaymentMethods() {
        return this.request('GET', '/billing/payment-methods');
    }

    async addPaymentMethod(paymentMethod) {
        return this.request('POST', '/billing/payment-methods', paymentMethod);
    }

    // Notification API endpoints
    async getNotifications(unreadOnly = false) {
        return this.request('GET', '/notifications', { unreadOnly });
    }

    async markNotificationRead(notificationId) {
        return this.request('PUT', `/notifications/${notificationId}/read`);
    }

    async updateNotificationPreferences(preferences) {
        return this.request('PUT', '/notifications/preferences', preferences);
    }

    // File upload
    async uploadFile(file, type = 'document') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);

        const response = await fetch(`${this.config.baseURL}/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.authToken}`
            },
            body: formData
        });

        if (!response.ok) {
            throw await this.parseError(response);
        }

        return response.json();
    }

    // Interceptor management
    addInterceptor(type, interceptor) {
        this.interceptors.push({ type, interceptor });
        return () => {
            this.interceptors = this.interceptors.filter(i => i.interceptor !== interceptor);
        };
    }

    async runInterceptors(type, data) {
        let result = data;

        for (const { type: intType, interceptor } of this.interceptors) {
            if (intType === type) {
                result = await interceptor(result);
            }
        }

        return result;
    }

    // Cache management
    addToCache(key, data, ttl = 60000) {
        this.cache.set(key, {
            data,
            expiry: Date.now() + ttl
        });

        // Clean expired cache entries
        this.cleanCache();
    }

    getFromCache(key) {
        const cached = this.cache.get(key);

        if (cached && cached.expiry > Date.now()) {
            return cached.data;
        }

        if (cached) {
            this.cache.delete(key);
        }

        return null;
    }

    cleanCache() {
        const now = Date.now();
        for (const [key, value] of this.cache.entries()) {
            if (value.expiry < now) {
                this.cache.delete(key);
            }
        }
    }

    clearCache() {
        this.cache.clear();
    }

    // Utility methods
    createAbortSignal(timeout) {
        const controller = new AbortController();
        setTimeout(() => controller.abort(), timeout);
        return controller.signal;
    }

    async parseError(response) {
        let error;

        try {
            const data = await response.json();
            error = new Error(data.message || 'Request failed');
            error.code = data.code;
            error.details = data.details;
        } catch {
            error = new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        error.status = response.status;
        return error;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Batch requests
    async batchRequest(requests) {
        return this.request('POST', '/batch', { requests });
    }

    // GraphQL support
    async graphql(query, variables = {}) {
        return this.request('POST', '/graphql', { query, variables });
    }
}

// Create singleton instance
const apiService = new APIService();

// Export for global access
if (typeof window !== 'undefined') {
    window.apiService = apiService;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIService;
}

console.log('API Service initialized');