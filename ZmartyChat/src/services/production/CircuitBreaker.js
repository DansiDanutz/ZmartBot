/**
 * Production-Grade Circuit Breaker with Exponential Backoff and Jitter
 * Implements the Circuit Breaker pattern to prevent cascading failures
 * Features: State management, metrics, backoff strategies, monitoring hooks
 */

class CircuitBreaker {
  constructor(options = {}) {
    // Circuit breaker configuration
    this.name = options.name || 'default';
    this.failureThreshold = options.failureThreshold || 5;
    this.recoveryTimeout = options.recoveryTimeout || 30000; // 30 seconds
    this.monitoringPeriod = options.monitoringPeriod || 60000; // 1 minute
    this.halfOpenMaxCalls = options.halfOpenMaxCalls || 3;
    this.timeout = options.timeout || 10000; // 10 seconds

    // Exponential backoff configuration
    this.baseDelay = options.baseDelay || 1000; // 1 second
    this.maxDelay = options.maxDelay || 30000; // 30 seconds
    this.backoffMultiplier = options.backoffMultiplier || 2;
    this.jitterMaxPercent = options.jitterMaxPercent || 0.1; // 10% jitter

    // Circuit breaker state
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    this.failureCount = 0;
    this.successCount = 0;
    this.halfOpenCallCount = 0;
    this.lastFailureTime = null;
    this.nextAttemptTime = 0;

    // Request tracking for monitoring period
    this.requestWindow = [];
    this.windowStartTime = Date.now();

    // Metrics tracking
    this.metrics = {
      totalRequests: 0,
      totalFailures: 0,
      totalSuccesses: 0,
      totalTimeouts: 0,
      totalCircuitOpenRejections: 0,
      averageResponseTime: 0,
      lastResponseTime: 0,
      consecutiveFailures: 0,
      consecutiveSuccesses: 0,
      stateChanges: 0,
      lastStateChange: null
    };

    // Event handlers
    this.eventHandlers = {
      stateChange: [],
      failure: [],
      success: [],
      timeout: [],
      circuitOpen: [],
      circuitClosed: [],
      halfOpen: []
    };

    // Health check function
    this.healthCheck = options.healthCheck || null;
    this.healthCheckInterval = options.healthCheckInterval || 30000;
    this.healthCheckTimer = null;

    this.startHealthCheck();
  }

  /**
   * Execute a function with circuit breaker protection
   * @param {Function} fn - Function to execute
   * @param {...any} args - Arguments to pass to the function
   * @returns {Promise} - Result of the function or rejection
   */
  async execute(fn, ...args) {
    return this.call(fn, ...args);
  }

  /**
   * Main call method with circuit breaker logic
   */
  async call(fn, ...args) {
    this.cleanRequestWindow();

    // Check if circuit is open
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttemptTime) {
        this.metrics.totalCircuitOpenRejections++;
        this.emit('circuitOpen', {
          name: this.name,
          state: this.state,
          nextAttemptTime: this.nextAttemptTime,
          timeUntilRetry: this.nextAttemptTime - Date.now()
        });

        const error = new Error(`Circuit breaker ${this.name} is OPEN. Next retry in ${this.nextAttemptTime - Date.now()}ms`);
        error.circuitBreakerOpen = true;
        throw error;
      } else {
        // Transition to HALF_OPEN
        this.transitionTo('HALF_OPEN');
      }
    }

    // Check half-open call limit
    if (this.state === 'HALF_OPEN' && this.halfOpenCallCount >= this.halfOpenMaxCalls) {
      this.metrics.totalCircuitOpenRejections++;
      const error = new Error(`Circuit breaker ${this.name} is HALF_OPEN and at call limit`);
      error.circuitBreakerOpen = true;
      throw error;
    }

    // Execute the protected function
    return this.executeWithTimeout(fn, args);
  }

  /**
   * Execute function with timeout and tracking
   */
  async executeWithTimeout(fn, args) {
    const startTime = Date.now();
    this.metrics.totalRequests++;

    if (this.state === 'HALF_OPEN') {
      this.halfOpenCallCount++;
    }

    try {
      // Create timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
          const error = new Error(`Circuit breaker ${this.name} timeout after ${this.timeout}ms`);
          error.isTimeout = true;
          reject(error);
        }, this.timeout);
      });

      // Race between function execution and timeout
      const result = await Promise.race([
        fn(...args),
        timeoutPromise
      ]);

      // Success handling
      const responseTime = Date.now() - startTime;
      this.onSuccess(responseTime);
      return result;

    } catch (error) {
      const responseTime = Date.now() - startTime;

      if (error.isTimeout) {
        this.onTimeout(responseTime);
      } else {
        this.onFailure(error, responseTime);
      }

      throw error;
    }
  }

  /**
   * Handle successful execution
   */
  onSuccess(responseTime) {
    this.metrics.totalSuccesses++;
    this.metrics.consecutiveSuccesses++;
    this.metrics.consecutiveFailures = 0;
    this.metrics.lastResponseTime = responseTime;
    this.updateAverageResponseTime(responseTime);

    this.addToRequestWindow('success', responseTime);

    // State transitions based on success
    if (this.state === 'HALF_OPEN') {
      this.successCount++;

      // If we've had enough successful calls in half-open, close the circuit
      if (this.successCount >= this.halfOpenMaxCalls) {
        this.transitionTo('CLOSED');
      }
    } else if (this.state === 'CLOSED') {
      // Reset failure count on success in closed state
      this.failureCount = 0;
    }

    this.emit('success', {
      name: this.name,
      responseTime,
      state: this.state,
      consecutiveSuccesses: this.metrics.consecutiveSuccesses
    });
  }

  /**
   * Handle failed execution
   */
  onFailure(error, responseTime) {
    this.metrics.totalFailures++;
    this.metrics.consecutiveFailures++;
    this.metrics.consecutiveSuccesses = 0;
    this.metrics.lastResponseTime = responseTime;
    this.updateAverageResponseTime(responseTime);

    this.addToRequestWindow('failure', responseTime);

    this.failureCount++;
    this.lastFailureTime = Date.now();

    // Check if we should open the circuit
    if (this.shouldOpenCircuit()) {
      this.transitionTo('OPEN');
    }

    this.emit('failure', {
      name: this.name,
      error: error.message,
      responseTime,
      state: this.state,
      failureCount: this.failureCount,
      consecutiveFailures: this.metrics.consecutiveFailures
    });
  }

  /**
   * Handle timeout
   */
  onTimeout(responseTime) {
    this.metrics.totalTimeouts++;
    this.onFailure(new Error('Timeout'), responseTime);

    this.emit('timeout', {
      name: this.name,
      responseTime,
      state: this.state,
      timeoutThreshold: this.timeout
    });
  }

  /**
   * Determine if circuit should open
   */
  shouldOpenCircuit() {
    if (this.state === 'HALF_OPEN') {
      // In half-open, any failure should open the circuit
      return true;
    }

    // Check failure threshold
    if (this.failureCount >= this.failureThreshold) {
      return true;
    }

    // Check failure rate in current window
    const recentFailures = this.getRecentFailureRate();
    if (recentFailures >= 0.8) { // 80% failure rate
      return true;
    }

    return false;
  }

  /**
   * Calculate recent failure rate
   */
  getRecentFailureRate() {
    if (this.requestWindow.length === 0) return 0;

    const failures = this.requestWindow.filter(req => req.type === 'failure').length;
    return failures / this.requestWindow.length;
  }

  /**
   * Transition circuit breaker to new state
   */
  transitionTo(newState) {
    const oldState = this.state;
    this.state = newState;
    this.metrics.stateChanges++;
    this.metrics.lastStateChange = Date.now();

    // State-specific logic
    switch (newState) {
      case 'OPEN':
        this.nextAttemptTime = Date.now() + this.calculateBackoffDelay();
        this.emit('circuitOpen', {
          name: this.name,
          previousState: oldState,
          nextAttemptTime: this.nextAttemptTime,
          failureCount: this.failureCount
        });
        break;

      case 'HALF_OPEN':
        this.halfOpenCallCount = 0;
        this.successCount = 0;
        this.emit('halfOpen', {
          name: this.name,
          previousState: oldState,
          maxCalls: this.halfOpenMaxCalls
        });
        break;

      case 'CLOSED':
        this.failureCount = 0;
        this.successCount = 0;
        this.halfOpenCallCount = 0;
        this.nextAttemptTime = 0;
        this.emit('circuitClosed', {
          name: this.name,
          previousState: oldState
        });
        break;
    }

    this.emit('stateChange', {
      name: this.name,
      oldState,
      newState,
      timestamp: Date.now(),
      metrics: { ...this.metrics }
    });
  }

  /**
   * Calculate exponential backoff delay with jitter
   */
  calculateBackoffDelay() {
    // Exponential backoff: baseDelay * (multiplier ^ failureCount)
    const exponentialDelay = this.baseDelay * Math.pow(this.backoffMultiplier, this.failureCount - 1);

    // Cap at maximum delay
    const cappedDelay = Math.min(exponentialDelay, this.maxDelay);

    // Add jitter to prevent thundering herd
    const jitter = cappedDelay * this.jitterMaxPercent * Math.random();

    return Math.round(cappedDelay + jitter);
  }

  /**
   * Add request to monitoring window
   */
  addToRequestWindow(type, responseTime) {
    const now = Date.now();
    this.requestWindow.push({
      type,
      responseTime,
      timestamp: now
    });

    // Keep only requests within monitoring period
    this.cleanRequestWindow();
  }

  /**
   * Clean old requests from window
   */
  cleanRequestWindow() {
    const cutoff = Date.now() - this.monitoringPeriod;
    this.requestWindow = this.requestWindow.filter(req => req.timestamp > cutoff);
  }

  /**
   * Update average response time
   */
  updateAverageResponseTime(responseTime) {
    if (this.metrics.averageResponseTime === 0) {
      this.metrics.averageResponseTime = responseTime;
    } else {
      // Exponential moving average with alpha = 0.1
      this.metrics.averageResponseTime =
        0.9 * this.metrics.averageResponseTime + 0.1 * responseTime;
    }
  }

  /**
   * Get current metrics
   */
  getMetrics() {
    this.cleanRequestWindow();

    const recentRequests = this.requestWindow.length;
    const recentFailures = this.requestWindow.filter(req => req.type === 'failure').length;
    const recentSuccesses = this.requestWindow.filter(req => req.type === 'success').length;

    return {
      ...this.metrics,
      state: this.state,
      nextAttemptTime: this.nextAttemptTime,
      timeUntilRetry: Math.max(0, this.nextAttemptTime - Date.now()),
      recentRequests,
      recentFailures,
      recentSuccesses,
      recentFailureRate: recentRequests > 0 ? recentFailures / recentRequests : 0,
      uptime: this.state === 'CLOSED' ? 1 : 0,
      requestWindow: this.requestWindow.slice(-10) // Last 10 requests
    };
  }

  /**
   * Force circuit state (for testing/emergency)
   */
  forceState(state) {
    this.transitionTo(state);
  }

  /**
   * Reset circuit breaker
   */
  reset() {
    this.failureCount = 0;
    this.successCount = 0;
    this.halfOpenCallCount = 0;
    this.lastFailureTime = null;
    this.nextAttemptTime = 0;
    this.requestWindow = [];

    // Reset metrics
    Object.keys(this.metrics).forEach(key => {
      if (typeof this.metrics[key] === 'number') {
        this.metrics[key] = 0;
      }
    });

    this.transitionTo('CLOSED');
  }

  /**
   * Start health check if configured
   */
  startHealthCheck() {
    if (!this.healthCheck) return;

    this.healthCheckTimer = setInterval(async () => {
      if (this.state === 'OPEN') {
        try {
          await this.healthCheck();
          // Health check passed, try to transition to half-open
          if (Date.now() >= this.nextAttemptTime) {
            this.transitionTo('HALF_OPEN');
          }
        } catch (error) {
          // Health check failed, extend the wait time
          this.nextAttemptTime = Date.now() + this.calculateBackoffDelay();
        }
      }
    }, this.healthCheckInterval);
  }

  /**
   * Stop health check
   */
  stopHealthCheck() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
    }
  }

  /**
   * Event handling
   */
  on(event, handler) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].push(handler);
    }
  }

  off(event, handler) {
    if (this.eventHandlers[event]) {
      const index = this.eventHandlers[event].indexOf(handler);
      if (index > -1) {
        this.eventHandlers[event].splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.eventHandlers[event]) {
      this.eventHandlers[event].forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Circuit breaker event handler error for ${event}:`, error);
        }
      });
    }
  }

  /**
   * Cleanup
   */
  destroy() {
    this.stopHealthCheck();
    this.eventHandlers = {};
    this.requestWindow = [];
  }
}

/**
 * Circuit Breaker Registry for managing multiple circuit breakers
 */
class CircuitBreakerRegistry {
  constructor() {
    this.breakers = new Map();
    this.globalMetrics = {
      totalBreakers: 0,
      openBreakers: 0,
      halfOpenBreakers: 0,
      closedBreakers: 0,
      totalRequests: 0,
      totalFailures: 0
    };
  }

  /**
   * Create or get a circuit breaker
   */
  getBreaker(name, options = {}) {
    if (!this.breakers.has(name)) {
      const breaker = new CircuitBreaker({ ...options, name });

      // Set up global metrics tracking
      breaker.on('stateChange', (data) => {
        this.updateGlobalMetrics();
      });

      breaker.on('success', (data) => {
        this.globalMetrics.totalRequests++;
      });

      breaker.on('failure', (data) => {
        this.globalMetrics.totalRequests++;
        this.globalMetrics.totalFailures++;
      });

      this.breakers.set(name, breaker);
      this.globalMetrics.totalBreakers++;
      this.updateGlobalMetrics();
    }

    return this.breakers.get(name);
  }

  /**
   * Update global metrics
   */
  updateGlobalMetrics() {
    let open = 0, halfOpen = 0, closed = 0;

    this.breakers.forEach(breaker => {
      switch (breaker.state) {
        case 'OPEN': open++; break;
        case 'HALF_OPEN': halfOpen++; break;
        case 'CLOSED': closed++; break;
      }
    });

    this.globalMetrics.openBreakers = open;
    this.globalMetrics.halfOpenBreakers = halfOpen;
    this.globalMetrics.closedBreakers = closed;
  }

  /**
   * Get all circuit breakers
   */
  getAllBreakers() {
    return Array.from(this.breakers.entries()).map(([name, breaker]) => ({
      name,
      state: breaker.state,
      metrics: breaker.getMetrics()
    }));
  }

  /**
   * Get global metrics
   */
  getGlobalMetrics() {
    this.updateGlobalMetrics();
    return { ...this.globalMetrics };
  }

  /**
   * Reset all circuit breakers
   */
  resetAll() {
    this.breakers.forEach(breaker => breaker.reset());
  }

  /**
   * Destroy all circuit breakers
   */
  destroy() {
    this.breakers.forEach(breaker => breaker.destroy());
    this.breakers.clear();
  }
}

// Global registry instance
const registry = new CircuitBreakerRegistry();

module.exports = {
  CircuitBreaker,
  CircuitBreakerRegistry,
  getBreaker: (name, options) => registry.getBreaker(name, options),
  getAllBreakers: () => registry.getAllBreakers(),
  getGlobalMetrics: () => registry.getGlobalMetrics(),
  resetAll: () => registry.resetAll()
};