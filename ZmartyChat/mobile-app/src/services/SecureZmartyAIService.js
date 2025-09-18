/**
 * SecureZmartyAIService - Production-ready AI service
 * SECURITY-FIRST: No API keys, proper circuit breakers, rate limiting
 * Uses only secure proxy endpoints with JWT authentication
 */

class SecureZmartyAIService {
  constructor() {
    // SECURE: Only environment-based endpoints, NO API KEYS
    this.apiBaseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001';
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:3001';

    // WebSocket connection
    this.socket = null;
    this.isConnected = false;
    this.connectionAttempts = 0;
    this.maxConnectionAttempts = 3;

    // Event management
    this.eventListeners = new Map();
    this.pendingRequests = new Map();

    // Circuit breaker implementation
    this.circuitBreaker = {
      state: 'CLOSED', // CLOSED, OPEN, HALF_OPEN
      failureCount: 0,
      failureThreshold: 5,
      timeout: 30000, // 30 seconds
      nextAttempt: 0,
      successCount: 0,
      halfOpenMaxCalls: 3,
      callsInHalfOpen: 0
    };

    // Rate limiting (client-side protection)
    this.rateLimiter = {
      requests: [],
      windowMs: 60000, // 1 minute window
      maxRequests: 50   // Conservative limit
    };

    // Authentication
    this.authToken = null;
    this.tokenExpiry = null;
    this.refreshPromise = null;

    // Request timeout and retry
    this.defaultTimeout = 10000; // 10 seconds
    this.maxRetries = 2;

    // Initialize secure connection
    this.initializeSecureConnection();
  }

  /**
   * Initialize secure WebSocket connection with authentication
   */
  async initializeSecureConnection() {
    try {
      // Ensure we have valid authentication
      await this.ensureAuthenticated();

      if (typeof window !== 'undefined' && window.io) {
        this.socket = window.io(this.wsUrl, {
          transports: ['websocket', 'polling'],
          upgrade: true,
          autoConnect: false,
          auth: {
            token: this.authToken
          },
          timeout: 5000
        });

        this.setupSocketEventHandlers();
        this.socket.connect();
      }
    } catch (error) {
      console.error('🔒 Failed to initialize secure connection:', error);
      this.handleConnectionFailure(error);
    }
  }

  /**
   * Setup WebSocket event handlers with proper error handling
   */
  setupSocketEventHandlers() {
    this.socket.on('connect', () => {
      console.log('🔒 Secure connection established');
      this.isConnected = true;
      this.connectionAttempts = 0;
      this.resetCircuitBreaker();
      this.emit('connection', { status: 'connected', secure: true });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('🔒 Secure connection lost:', reason);
      this.isConnected = false;
      this.emit('connection', { status: 'disconnected', reason, secure: false });

      // Auto-reconnect with backoff
      if (reason === 'io server disconnect') {
        this.scheduleReconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('🔒 Connection error:', error);
      this.connectionAttempts++;
      this.recordFailure();

      if (this.connectionAttempts >= this.maxConnectionAttempts) {
        this.emit('connection_failed', { error: 'Max connection attempts exceeded' });
      } else {
        this.scheduleReconnect();
      }
    });

    // Secure message handlers
    this.socket.on('ai_response', (data) => this.handleSecureResponse(data));
    this.socket.on('market_alert', (data) => this.handleSecureAlert(data, 'market'));
    this.socket.on('whale_alert', (data) => this.handleSecureAlert(data, 'whale'));
    this.socket.on('pattern_trigger', (data) => this.handleSecureAlert(data, 'pattern'));
    this.socket.on('error', (error) => this.handleSecureError(error));
  }

  /**
   * Send secure message with circuit breaker and rate limiting
   */
  async sendMessage(message, options = {}) {
    // Input validation and sanitization
    if (!this.validateInput(message)) {
      throw new Error('Invalid input detected');
    }

    // Rate limiting check
    if (!this.checkRateLimit()) {
      throw new Error('Rate limit exceeded. Please wait before sending another message.');
    }

    // Circuit breaker check
    if (!this.canMakeRequest()) {
      throw new Error('Service temporarily unavailable. Please try again later.');
    }

    try {
      const requestId = this.generateRequestId();
      const sanitizedMessage = this.sanitizeInput(message);

      const messageData = {
        requestId,
        message: sanitizedMessage,
        userId: await this.getSecureUserId(),
        timestamp: Date.now(),
        messageType: options.messageType || 'chat',
        context: {
          isMobile: true,
          location: options.location || 'chat',
          sessionId: this.getSessionId()
        }
      };

      // Record rate limit request
      this.recordRequest();

      let result;

      // Try WebSocket first, fallback to HTTPS
      if (this.socket && this.socket.connected) {
        result = await this.sendViaWebSocket(messageData, requestId);
      } else {
        result = await this.sendViaHTTPS(messageData);
      }

      // Record success for circuit breaker
      this.recordSuccess();

      return result;

    } catch (error) {
      this.recordFailure();
      throw this.createSecureError(error);
    }
  }

  /**
   * Send message via secure WebSocket
   */
  async sendViaWebSocket(messageData, requestId) {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingRequests.delete(requestId);
        reject(new Error('Request timeout'));
      }, this.defaultTimeout);

      this.pendingRequests.set(requestId, { resolve, reject, timeout });
      this.socket.emit('secure_ai_message', messageData);
    });
  }

  /**
   * Send message via secure HTTPS with retry logic
   */
  async sendViaHTTPS(messageData, attempt = 1) {
    try {
      await this.ensureAuthenticated();

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.defaultTimeout);

      const response = await fetch(`${this.apiBaseUrl}/api/v1/ai/secure-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.authToken}`,
          'X-Client-Version': '1.0.0',
          'X-Request-ID': messageData.requestId
        },
        body: JSON.stringify(messageData),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, refresh and retry
          if (attempt === 1) {
            await this.refreshAuthentication();
            return this.sendViaHTTPS(messageData, attempt + 1);
          }
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      return this.validateAndSanitizeResponse(result);

    } catch (error) {
      if (attempt < this.maxRetries && this.isRetryableError(error)) {
        await this.exponentialBackoff(attempt);
        return this.sendViaHTTPS(messageData, attempt + 1);
      }
      throw error;
    }
  }

  /**
   * Handle secure response with validation
   */
  handleSecureResponse(data) {
    try {
      // Validate response structure and content
      const validatedData = this.validateAndSanitizeResponse(data);

      // Resolve pending request if exists
      if (data.requestId && this.pendingRequests.has(data.requestId)) {
        const { resolve, timeout } = this.pendingRequests.get(data.requestId);
        clearTimeout(timeout);
        this.pendingRequests.delete(data.requestId);
        resolve(validatedData);
        return;
      }

      // Emit to UI components
      this.emit('ai_response', validatedData);

    } catch (error) {
      console.error('🔒 Invalid response received:', error);
      this.emit('security_warning', { type: 'invalid_response', error: error.message });
    }
  }

  /**
   * Handle secure alerts with validation
   */
  handleSecureAlert(data, alertType) {
    try {
      const validatedAlert = this.validateAndSanitizeAlert(data, alertType);
      this.emit(`${alertType}_alert`, validatedAlert);

      // Show secure notification
      this.showSecureNotification(validatedAlert);

    } catch (error) {
      console.error('🔒 Invalid alert received:', error);
      this.emit('security_warning', { type: 'invalid_alert', error: error.message });
    }
  }

  /**
   * Circuit breaker implementation
   */
  canMakeRequest() {
    const now = Date.now();

    switch (this.circuitBreaker.state) {
      case 'OPEN':
        if (now >= this.circuitBreaker.nextAttempt) {
          this.circuitBreaker.state = 'HALF_OPEN';
          this.circuitBreaker.callsInHalfOpen = 0;
          return true;
        }
        return false;

      case 'HALF_OPEN':
        return this.circuitBreaker.callsInHalfOpen < this.circuitBreaker.halfOpenMaxCalls;

      case 'CLOSED':
      default:
        return true;
    }
  }

  recordSuccess() {
    if (this.circuitBreaker.state === 'HALF_OPEN') {
      this.circuitBreaker.successCount++;
      if (this.circuitBreaker.successCount >= this.circuitBreaker.halfOpenMaxCalls) {
        this.resetCircuitBreaker();
      }
    } else {
      this.circuitBreaker.failureCount = 0;
    }
  }

  recordFailure() {
    this.circuitBreaker.failureCount++;

    if (this.circuitBreaker.state === 'HALF_OPEN') {
      this.openCircuit();
    } else if (this.circuitBreaker.failureCount >= this.circuitBreaker.failureThreshold) {
      this.openCircuit();
    }
  }

  openCircuit() {
    this.circuitBreaker.state = 'OPEN';
    this.circuitBreaker.nextAttempt = Date.now() + this.circuitBreaker.timeout;
    console.warn('🔒 Circuit breaker opened - service temporarily unavailable');
    this.emit('circuit_breaker_open', { nextAttempt: this.circuitBreaker.nextAttempt });
  }

  resetCircuitBreaker() {
    this.circuitBreaker.state = 'CLOSED';
    this.circuitBreaker.failureCount = 0;
    this.circuitBreaker.successCount = 0;
    this.circuitBreaker.callsInHalfOpen = 0;
  }

  /**
   * Rate limiting implementation
   */
  checkRateLimit() {
    const now = Date.now();
    const windowStart = now - this.rateLimiter.windowMs;

    // Clean old requests
    this.rateLimiter.requests = this.rateLimiter.requests.filter(time => time > windowStart);

    return this.rateLimiter.requests.length < this.rateLimiter.maxRequests;
  }

  recordRequest() {
    this.rateLimiter.requests.push(Date.now());
  }

  /**
   * Authentication management
   */
  async ensureAuthenticated() {
    if (this.isTokenValid()) {
      return this.authToken;
    }

    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.refreshAuthentication();
    try {
      await this.refreshPromise;
      return this.authToken;
    } finally {
      this.refreshPromise = null;
    }
  }

  async refreshAuthentication() {
    try {
      const deviceId = this.getDeviceId();
      const response = await fetch(`${this.apiBaseUrl}/api/v1/auth/mobile-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          deviceId,
          clientVersion: '1.0.0',
          platform: 'web-mobile'
        })
      });

      if (!response.ok) {
        throw new Error(`Authentication failed: ${response.status}`);
      }

      const authData = await response.json();
      this.authToken = authData.token;
      this.tokenExpiry = authData.expiresAt;

      // Securely store token (consider encryption for sensitive data)
      sessionStorage.setItem('secure_token', authData.token);
      sessionStorage.setItem('token_expiry', authData.expiresAt);

    } catch (error) {
      console.error('🔒 Authentication refresh failed:', error);
      throw new Error('Unable to authenticate with secure service');
    }
  }

  isTokenValid() {
    return this.authToken && this.tokenExpiry && Date.now() < this.tokenExpiry - 60000; // 1 minute buffer
  }

  /**
   * Input validation and sanitization
   */
  validateInput(message) {
    if (!message || typeof message !== 'string') return false;
    if (message.length > 4000) return false; // Reasonable limit
    if (this.containsSuspiciousPatterns(message)) return false;
    return true;
  }

  sanitizeInput(message) {
    // Remove potentially dangerous patterns
    return message
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .trim();
  }

  containsSuspiciousPatterns(message) {
    const suspiciousPatterns = [
      /<script/i,
      /javascript:/i,
      /data:text\/html/i,
      /vbscript:/i,
      /on\w+\s*=/i
    ];

    return suspiciousPatterns.some(pattern => pattern.test(message));
  }

  /**
   * Response validation and sanitization
   */
  validateAndSanitizeResponse(response) {
    if (!response || typeof response !== 'object') {
      throw new Error('Invalid response format');
    }

    const sanitized = {
      content: this.sanitizeContent(response.content),
      provider: this.validateProvider(response.provider),
      timestamp: response.timestamp || Date.now(),
      requestId: response.requestId,
      metadata: this.sanitizeMetadata(response.metadata || {})
    };

    return sanitized;
  }

  sanitizeContent(content) {
    if (!content || typeof content !== 'string') return '';

    return content
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .substring(0, 10000); // Reasonable content limit
  }

  validateProvider(provider) {
    const validProviders = ['openai', 'claude', 'grok', 'gemini'];
    return validProviders.includes(provider) ? provider : 'unknown';
  }

  sanitizeMetadata(metadata) {
    const allowedKeys = ['responseTime', 'tokens', 'model', 'confidence'];
    const sanitized = {};

    for (const key of allowedKeys) {
      if (metadata[key] !== undefined) {
        sanitized[key] = metadata[key];
      }
    }

    return sanitized;
  }

  /**
   * Utility methods
   */
  async getSecureUserId() {
    // Generate or retrieve secure user identifier
    let userId = sessionStorage.getItem('secure_user_id');
    if (!userId) {
      userId = await this.generateSecureUserId();
      sessionStorage.setItem('secure_user_id', userId);
    }
    return userId;
  }

  async generateSecureUserId() {
    const deviceId = this.getDeviceId();
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2);

    // Create a hash-based user ID (not cryptographically secure, but sufficient for client-side)
    const data = `${deviceId}-${timestamp}-${random}`;
    return btoa(data).replace(/[^a-zA-Z0-9]/g, '').substring(0, 16);
  }

  getDeviceId() {
    let deviceId = localStorage.getItem('device_id');
    if (!deviceId) {
      deviceId = this.generateDeviceId();
      localStorage.setItem('device_id', deviceId);
    }
    return deviceId;
  }

  generateDeviceId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
  }

  getSessionId() {
    let sessionId = sessionStorage.getItem('session_id');
    if (!sessionId) {
      sessionId = this.generateRequestId();
      sessionStorage.setItem('session_id', sessionId);
    }
    return sessionId;
  }

  generateRequestId() {
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
  }

  /**
   * Error handling
   */
  isRetryableError(error) {
    if (error.name === 'AbortError') return false;
    if (error.message.includes('401')) return false;
    if (error.message.includes('403')) return false;
    return true;
  }

  async exponentialBackoff(attempt) {
    const delay = Math.min(1000 * Math.pow(2, attempt), 10000);
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  createSecureError(error) {
    // Don't expose sensitive error details to the client
    const secureMessage = this.getSecureErrorMessage(error);
    return new Error(secureMessage);
  }

  getSecureErrorMessage(error) {
    if (error.message.includes('rate limit')) {
      return 'Too many requests. Please wait a moment before trying again.';
    }
    if (error.message.includes('timeout')) {
      return 'Request timed out. Please check your connection and try again.';
    }
    if (error.message.includes('network') || error.message.includes('fetch')) {
      return 'Network error. Please check your connection and try again.';
    }
    return 'Service temporarily unavailable. Please try again later.';
  }

  /**
   * Event management
   */
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.eventListeners.has(event)) {
      const listeners = this.eventListeners.get(event);
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('🔒 Event handler error:', error);
        }
      });
    }
  }

  /**
   * Cleanup and connection management
   */
  scheduleReconnect() {
    if (this.connectionAttempts < this.maxConnectionAttempts) {
      const delay = Math.min(1000 * Math.pow(2, this.connectionAttempts), 30000);
      setTimeout(() => {
        if (!this.isConnected) {
          this.initializeSecureConnection();
        }
      }, delay);
    }
  }

  handleConnectionFailure(error) {
    this.emit('connection_error', { error: error.message, timestamp: Date.now() });
  }

  handleSecureError(error) {
    console.error('🔒 Secure service error:', error);
    this.emit('service_error', { error: this.getSecureErrorMessage(error) });
  }

  /**
   * Secure notification display
   */
  showSecureNotification(alert) {
    // Sanitize notification content
    const sanitizedAlert = {
      title: this.sanitizeContent(alert.title || ''),
      body: this.sanitizeContent(alert.body || ''),
      priority: alert.priority || 'normal'
    };

    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(sanitizedAlert.title, {
        body: sanitizedAlert.body,
        icon: '/assets/icons/zmarty-icon.png',
        badge: '/assets/icons/zmarty-badge.png',
        tag: 'zmarty-alert',
        requireInteraction: sanitizedAlert.priority === 'urgent'
      });

      notification.onclick = () => {
        window.focus();
        this.emit('notification_click', alert);
      };
    }

    this.emit('show_notification', sanitizedAlert);
  }

  /**
   * Cleanup
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }

    // Clear pending requests
    this.pendingRequests.forEach(({ timeout }) => clearTimeout(timeout));
    this.pendingRequests.clear();

    // Clear event listeners
    this.eventListeners.clear();

    // Clear authentication
    this.authToken = null;
    this.tokenExpiry = null;
    sessionStorage.removeItem('secure_token');
    sessionStorage.removeItem('token_expiry');
  }
}

// Export singleton instance
const secureZmartyAI = new SecureZmartyAIService();
export default secureZmartyAI;