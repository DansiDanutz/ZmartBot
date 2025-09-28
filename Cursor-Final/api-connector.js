/**
 * ZmartyBrain API Connector
 * Handles all backend API communications
 */

class APIConnector {
    constructor() {
        this.baseUrl = CONFIG.API.BASE_URL;
        this.timeout = CONFIG.API.TIMEOUT;
        this.retryAttempts = CONFIG.API.RETRY_ATTEMPTS;
        this.headers = {
            'Content-Type': 'application/json',
            'X-Client-Version': '2.0.0'
        };
        this.initializeAuth();
    }

    /**
     * Initialize authentication headers
     */
    initializeAuth() {
        const session = this.getStoredSession();
        if (session?.access_token) {
            this.setAuthHeader(session.access_token);
        }
    }

    /**
     * Set authorization header
     */
    setAuthHeader(token) {
        this.headers['Authorization'] = `Bearer ${token}`;
    }

    /**
     * Get stored session
     */
    getStoredSession() {
        const sessionStr = localStorage.getItem(CONFIG.STORAGE.USER_SESSION);
        return sessionStr ? JSON.parse(sessionStr) : null;
    }

    /**
     * Make API request with retry logic
     */
    async request(endpoint, options = {}) {
        const url = this.baseUrl + endpoint;
        let lastError;

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);

                const response = await fetch(url, {
                    ...options,
                    headers: {
                        ...this.headers,
                        ...options.headers
                    },
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                // Handle rate limiting
                if (response.status === 429) {
                    const retryAfter = response.headers.get('Retry-After') || 5;
                    await this.delay(retryAfter * 1000);
                    continue;
                }

                // Handle authentication errors
                if (response.status === 401) {
                    await this.refreshAuth();
                    continue;
                }

                // Parse response
                const data = await response.json();

                if (!response.ok) {
                    throw new APIError(data.message || 'Request failed', response.status, data);
                }

                return data;

            } catch (error) {
                lastError = error;

                // Don't retry on client errors (4xx) except 429
                if (error.status >= 400 && error.status < 500 && error.status !== 429) {
                    throw error;
                }

                // Wait before retry with exponential backoff
                if (attempt < this.retryAttempts) {
                    await this.delay(Math.pow(2, attempt) * 1000);
                }
            }
        }

        throw lastError || new Error('Request failed after retries');
    }

    /**
     * Helper method for delays
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Refresh authentication token
     */
    async refreshAuth() {
        try {
            const session = this.getStoredSession();
            if (!session?.refresh_token) {
                throw new Error('No refresh token available');
            }

            const { data, error } = await supabase.auth.refreshSession({
                refresh_token: session.refresh_token
            });

            if (error) throw error;

            localStorage.setItem(CONFIG.STORAGE.USER_SESSION, JSON.stringify(data.session));
            this.setAuthHeader(data.session.access_token);

        } catch (error) {
            // Redirect to login if refresh fails
            window.location.href = '/login';
        }
    }

    // Authentication APIs
    async register(email, password, userData = {}) {
        return this.request(CONFIG.API.ENDPOINTS.AUTH + '/register', {
            method: 'POST',
            body: JSON.stringify({ email, password, ...userData })
        });
    }

    async verifyEmail(email, code) {
        return this.request(CONFIG.API.ENDPOINTS.AUTH + '/verify', {
            method: 'POST',
            body: JSON.stringify({ email, code })
        });
    }

    async resendVerification(email) {
        return this.request(CONFIG.API.ENDPOINTS.AUTH + '/resend', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    }

    async resetPassword(email) {
        return this.request(CONFIG.API.ENDPOINTS.AUTH + '/reset-password', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
    }

    // User Profile APIs
    async getProfile() {
        return this.request(CONFIG.API.ENDPOINTS.PROFILE);
    }

    async updateProfile(profileData) {
        return this.request(CONFIG.API.ENDPOINTS.PROFILE, {
            method: 'PUT',
            body: JSON.stringify(profileData)
        });
    }

    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);

        return this.request(CONFIG.API.ENDPOINTS.PROFILE + '/avatar', {
            method: 'POST',
            body: formData,
            headers: {
                // Remove Content-Type to let browser set it with boundary
            }
        });
    }

    // Subscription APIs
    async createSubscription(planId, paymentMethodId) {
        return this.request(CONFIG.API.ENDPOINTS.SUBSCRIPTION, {
            method: 'POST',
            body: JSON.stringify({
                plan_id: planId,
                payment_method_id: paymentMethodId
            })
        });
    }

    async cancelSubscription() {
        return this.request(CONFIG.API.ENDPOINTS.SUBSCRIPTION, {
            method: 'DELETE'
        });
    }

    async getSubscriptionStatus() {
        return this.request(CONFIG.API.ENDPOINTS.SUBSCRIPTION + '/status');
    }

    // Onboarding APIs
    async saveOnboardingProgress(step, data) {
        return this.request(CONFIG.API.ENDPOINTS.ONBOARDING + '/progress', {
            method: 'POST',
            body: JSON.stringify({ step, data })
        });
    }

    async completeOnboarding() {
        return this.request(CONFIG.API.ENDPOINTS.ONBOARDING + '/complete', {
            method: 'POST'
        });
    }

    async getOnboardingStatus() {
        return this.request(CONFIG.API.ENDPOINTS.ONBOARDING + '/status');
    }

    // Trading APIs
    async getTradingSignals() {
        return this.request(CONFIG.API.ENDPOINTS.TRADING + '/signals');
    }

    async getMarketData(symbols) {
        return this.request(CONFIG.API.ENDPOINTS.TRADING + '/market', {
            method: 'POST',
            body: JSON.stringify({ symbols })
        });
    }

    async executeTrade(tradeData) {
        return this.request(CONFIG.API.ENDPOINTS.TRADING + '/execute', {
            method: 'POST',
            body: JSON.stringify(tradeData)
        });
    }

    // Analytics tracking
    trackEvent(eventName, eventData = {}) {
        if (CONFIG.FEATURES.ANALYTICS_ENABLED) {
            // Send to backend
            this.request('/api/analytics/event', {
                method: 'POST',
                body: JSON.stringify({
                    event: eventName,
                    data: eventData,
                    timestamp: new Date().toISOString()
                })
            }).catch(error => {
                console.error('Analytics tracking failed:', error);
            });

            // Also track in Google Analytics if available
            if (typeof gtag !== 'undefined') {
                gtag('event', eventName, eventData);
            }
        }
    }

    // WebSocket connection for real-time updates
    connectWebSocket() {
        const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws';
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.ws.send(JSON.stringify({
                type: 'auth',
                token: this.headers.Authorization
            }));
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'market_update':
                window.dispatchEvent(new CustomEvent('marketUpdate', { detail: data }));
                break;
            case 'trade_signal':
                window.dispatchEvent(new CustomEvent('tradeSignal', { detail: data }));
                break;
            case 'notification':
                window.dispatchEvent(new CustomEvent('notification', { detail: data }));
                break;
            default:
                console.log('Unknown WebSocket message:', data);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Custom Error class for API errors
class APIError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

// Create singleton instance
const apiConnector = new APIConnector();

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = apiConnector;
}