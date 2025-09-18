/**
 * Production-Ready AI Provider Service with Circuit Breakers
 * Implements ChatGPT 5 Pro recommendations for enterprise-grade reliability
 * Features: Circuit breakers, cost tracking, provider routing, telemetry
 */

const { getBreaker } = require('./CircuitBreaker');
const crypto = require('crypto');

class ProductionAIProviderService {
  constructor() {
    // Provider configurations with circuit breakers
    this.providers = new Map([
      ['openai', {
        name: 'openai',
        endpoint: 'https://api.openai.com/v1/chat/completions',
        model: 'gpt-4',
        costPer1kTokens: 0.03,
        timeoutMs: 30000,
        rateLimit: 3500, // RPM
        priority: 1,
        healthEndpoint: 'https://api.openai.com/v1/models'
      }],
      ['claude', {
        name: 'claude',
        endpoint: 'https://api.anthropic.com/v1/messages',
        model: 'claude-3-sonnet-20240229',
        costPer1kTokens: 0.015,
        timeoutMs: 45000,
        rateLimit: 1000,
        priority: 2,
        healthEndpoint: 'https://api.anthropic.com/v1/messages'
      }],
      ['grok', {
        name: 'grok',
        endpoint: 'https://api.x.ai/v1/chat/completions',
        model: 'grok-beta',
        costPer1kTokens: 0.005,
        timeoutMs: 25000,
        rateLimit: 5000,
        priority: 3,
        healthEndpoint: 'https://api.x.ai/v1/models'
      }],
      ['gemini', {
        name: 'gemini',
        endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
        model: 'gemini-pro',
        costPer1kTokens: 0.001,
        timeoutMs: 20000,
        rateLimit: 60,
        priority: 4,
        healthEndpoint: 'https://generativelanguage.googleapis.com/v1beta/models'
      }]
    ]);

    // Cost governance
    this.costLimits = {
      perUser: {
        hourly: 10.00, // $10 per hour per user
        daily: 50.00,  // $50 per day per user
        monthly: 500.00 // $500 per month per user
      },
      global: {
        hourly: 1000.00,  // $1000 per hour globally
        daily: 10000.00,  // $10k per day globally
        monthly: 100000.00 // $100k per month globally
      }
    };

    // Provider routing configuration
    this.routingConfig = {
      defaultProvider: 'grok', // Cheapest for general use
      taskRouting: {
        'financial_analysis': 'claude', // Most accurate for finance
        'real_time_data': 'grok',      // Best for crypto/market data
        'code_generation': 'openai',   // Best for code
        'creative_writing': 'claude',  // Best for creative tasks
        'quick_qa': 'gemini'          // Fastest/cheapest for simple Q&A
      },
      loadBalancing: true,
      failoverEnabled: true
    };

    // Request tracking and metrics
    this.requestMetrics = new Map();
    this.costTracking = new Map();
    this.rateLimitTracking = new Map();

    // Initialize circuit breakers for each provider
    this.initializeCircuitBreakers();

    // Content policy configuration
    this.contentPolicy = {
      piiRedaction: true,
      financialDisclaimers: true,
      prohibitedContent: ['trading_advice', 'investment_recommendations'],
      allowedContent: ['market_analysis', 'educational_content', 'general_assistance']
    };

    // Telemetry and monitoring
    this.telemetry = {
      enabled: true,
      traceRequests: true,
      logSlowRequests: true,
      slowRequestThreshold: 2000, // 2 seconds
      metricsInterval: 60000 // 1 minute
    };

    this.startMetricsCollection();
  }

  /**
   * Initialize circuit breakers for each provider
   */
  initializeCircuitBreakers() {
    this.providers.forEach((config, providerName) => {
      const breaker = getBreaker(providerName, {
        name: providerName,
        failureThreshold: 5,
        recoveryTimeout: 30000,
        timeout: config.timeoutMs,
        halfOpenMaxCalls: 3,
        healthCheck: () => this.performHealthCheck(providerName)
      });

      // Set up monitoring
      breaker.on('stateChange', (data) => {
        console.log(`🔌 Circuit breaker ${data.name}: ${data.oldState} → ${data.newState}`);
        this.recordTelemetry('circuit_breaker_state_change', data);
      });

      breaker.on('circuitOpen', (data) => {
        console.warn(`⚠️ Circuit breaker ${data.name} opened due to failures`);
        this.recordTelemetry('circuit_breaker_open', data);
      });
    });
  }

  /**
   * Main method to generate AI completion with production safeguards
   */
  async generateCompletion(request) {
    const requestId = this.generateRequestId();
    const startTime = Date.now();

    try {
      // Validate and sanitize request
      const validatedRequest = await this.validateRequest(request);

      // Check cost limits
      await this.enforceRateLimits(validatedRequest.userId);

      // Apply content policy
      const policyFilteredRequest = await this.applyContentPolicy(validatedRequest);

      // Determine optimal provider
      const provider = await this.selectProvider(policyFilteredRequest);

      // Execute request with circuit breaker protection
      const result = await this.executeWithCircuitBreaker(provider, policyFilteredRequest, requestId);

      // Record success metrics
      const responseTime = Date.now() - startTime;
      await this.recordSuccess(provider, policyFilteredRequest, result, responseTime);

      return {
        ...result,
        requestId,
        provider,
        responseTime,
        costEstimate: this.calculateCost(provider, result)
      };

    } catch (error) {
      const responseTime = Date.now() - startTime;
      await this.recordFailure(requestId, error, responseTime);
      throw this.createUserFriendlyError(error);
    }
  }

  /**
   * Validate and sanitize incoming request
   */
  async validateRequest(request) {
    if (!request) {
      throw new Error('Request is required');
    }

    if (!request.prompt || typeof request.prompt !== 'string') {
      throw new Error('Valid prompt is required');
    }

    if (request.prompt.length > 8000) {
      throw new Error('Prompt too long. Maximum 8000 characters allowed.');
    }

    // Sanitize input
    const sanitizedPrompt = this.sanitizeInput(request.prompt);

    // Check for prompt injection attempts
    if (this.detectPromptInjection(sanitizedPrompt)) {
      throw new Error('Invalid prompt content detected');
    }

    return {
      prompt: sanitizedPrompt,
      userId: request.userId || 'anonymous',
      sessionId: request.sessionId || this.generateRequestId(),
      taskType: request.taskType || 'general',
      maxTokens: Math.min(request.maxTokens || 2000, 4000),
      temperature: Math.min(Math.max(request.temperature || 0.7, 0), 1),
      metadata: request.metadata || {}
    };
  }

  /**
   * Enforce rate limits and cost governance
   */
  async enforceRateLimits(userId) {
    const now = Date.now();
    const userKey = `user:${userId}`;

    // Check user rate limits
    const userCosts = this.getUserCosts(userId);

    if (userCosts.hourly > this.costLimits.perUser.hourly) {
      throw new Error('Hourly cost limit exceeded. Please try again later.');
    }

    if (userCosts.daily > this.costLimits.perUser.daily) {
      throw new Error('Daily cost limit exceeded. Please upgrade your plan.');
    }

    // Check global rate limits
    const globalCosts = this.getGlobalCosts();

    if (globalCosts.hourly > this.costLimits.global.hourly) {
      throw new Error('System temporarily overloaded. Please try again in a few minutes.');
    }

    return true;
  }

  /**
   * Apply content policy and safety filters
   */
  async applyContentPolicy(request) {
    let processedPrompt = request.prompt;

    // Redact PII if enabled
    if (this.contentPolicy.piiRedaction) {
      processedPrompt = this.redactPII(processedPrompt);
    }

    // Check for prohibited content
    const contentClassification = this.classifyContent(processedPrompt);

    for (const prohibited of this.contentPolicy.prohibitedContent) {
      if (contentClassification.includes(prohibited)) {
        // Add financial disclaimer instead of blocking
        if (prohibited.includes('trading') || prohibited.includes('investment')) {
          processedPrompt = this.addFinancialDisclaimer(processedPrompt);
        }
      }
    }

    return {
      ...request,
      prompt: processedPrompt,
      contentClassification,
      dataClass: {
        pii: this.detectPII(request.prompt),
        financial: contentClassification.includes('financial_analysis'),
        sensitive: this.detectSensitiveContent(request.prompt)
      }
    };
  }

  /**
   * Select optimal provider based on multiple factors
   */
  async selectProvider(request) {
    // Get available providers (circuit breaker status)
    const availableProviders = this.getAvailableProviders();

    if (availableProviders.length === 0) {
      throw new Error('All AI providers are currently unavailable');
    }

    // Task-based routing
    if (this.routingConfig.taskRouting[request.taskType]) {
      const preferredProvider = this.routingConfig.taskRouting[request.taskType];
      if (availableProviders.includes(preferredProvider)) {
        return preferredProvider;
      }
    }

    // Cost-based routing (prefer cheaper providers)
    if (request.taskType === 'quick_qa' || request.maxTokens < 500) {
      const cheapestProvider = availableProviders
        .sort((a, b) => this.providers.get(a).costPer1kTokens - this.providers.get(b).costPer1kTokens)[0];
      return cheapestProvider;
    }

    // Load balancing based on current load
    if (this.routingConfig.loadBalancing) {
      return this.selectLeastLoadedProvider(availableProviders);
    }

    // Default provider
    return availableProviders.includes(this.routingConfig.defaultProvider)
      ? this.routingConfig.defaultProvider
      : availableProviders[0];
  }

  /**
   * Execute request with circuit breaker protection
   */
  async executeWithCircuitBreaker(providerName, request, requestId) {
    const breaker = getBreaker(providerName);
    const provider = this.providers.get(providerName);

    return breaker.execute(async () => {
      // Create idempotency key for this specific request
      const idempotencyKey = this.generateIdempotencyKey(request, providerName);

      // Check if we've already processed this exact request
      const cachedResult = await this.getCachedResult(idempotencyKey);
      if (cachedResult) {
        return cachedResult;
      }

      // Execute the actual API call
      const result = await this.callProviderAPI(provider, request, requestId);

      // Cache the result for idempotency
      await this.cacheResult(idempotencyKey, result);

      return result;
    });
  }

  /**
   * Call provider API with proper formatting and error handling
   */
  async callProviderAPI(provider, request, requestId) {
    const startTime = Date.now();

    try {
      // Format request for specific provider
      const formattedRequest = this.formatRequestForProvider(provider, request);

      // Create request with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), provider.timeoutMs);

      const response = await fetch(provider.endpoint, {
        method: 'POST',
        headers: this.getProviderHeaders(provider),
        body: JSON.stringify(formattedRequest),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Provider ${provider.name} returned ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      const responseTime = Date.now() - startTime;

      // Format response to standard format
      return this.formatProviderResponse(provider, result, responseTime);

    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error(`Provider ${provider.name} timeout after ${provider.timeoutMs}ms`);
      }
      throw error;
    }
  }

  /**
   * Format request for specific provider
   */
  formatRequestForProvider(provider, request) {
    switch (provider.name) {
      case 'openai':
      case 'grok':
        return {
          model: provider.model,
          messages: [
            { role: 'system', content: 'You are a helpful AI assistant specialized in cryptocurrency and financial markets.' },
            { role: 'user', content: request.prompt }
          ],
          max_tokens: request.maxTokens,
          temperature: request.temperature
        };

      case 'claude':
        return {
          model: provider.model,
          max_tokens: request.maxTokens,
          messages: [
            { role: 'user', content: request.prompt }
          ],
          system: 'You are a helpful AI assistant specialized in cryptocurrency and financial markets.'
        };

      case 'gemini':
        return {
          contents: [{
            parts: [{ text: request.prompt }]
          }],
          generationConfig: {
            maxOutputTokens: request.maxTokens,
            temperature: request.temperature
          }
        };

      default:
        throw new Error(`Unknown provider: ${provider.name}`);
    }
  }

  /**
   * Get provider-specific headers
   */
  getProviderHeaders(provider) {
    const headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'ZmartyChat/1.0.0'
    };

    // Add provider-specific authentication
    switch (provider.name) {
      case 'openai':
        headers['Authorization'] = `Bearer ${process.env.OPENAI_API_KEY}`;
        break;
      case 'claude':
        headers['x-api-key'] = process.env.CLAUDE_API_KEY;
        headers['anthropic-version'] = '2023-06-01';
        break;
      case 'grok':
        headers['Authorization'] = `Bearer ${process.env.GROK_API_KEY}`;
        break;
      case 'gemini':
        headers['Authorization'] = `Bearer ${process.env.GEMINI_API_KEY}`;
        break;
    }

    return headers;
  }

  /**
   * Format provider response to standard format
   */
  formatProviderResponse(provider, result, responseTime) {
    let content, usage;

    switch (provider.name) {
      case 'openai':
      case 'grok':
        content = result.choices?.[0]?.message?.content || '';
        usage = result.usage || {};
        break;

      case 'claude':
        content = result.content?.[0]?.text || '';
        usage = result.usage || {};
        break;

      case 'gemini':
        content = result.candidates?.[0]?.content?.parts?.[0]?.text || '';
        usage = result.usageMetadata || {};
        break;

      default:
        content = String(result);
        usage = {};
    }

    return {
      content: this.sanitizeOutput(content),
      provider: provider.name,
      model: provider.model,
      usage: {
        promptTokens: usage.prompt_tokens || usage.promptTokenCount || 0,
        completionTokens: usage.completion_tokens || usage.candidatesTokenCount || 0,
        totalTokens: usage.total_tokens || (usage.promptTokenCount + usage.candidatesTokenCount) || 0
      },
      responseTime,
      timestamp: Date.now()
    };
  }

  /**
   * Get available providers (not in circuit breaker open state)
   */
  getAvailableProviders() {
    const available = [];

    this.providers.forEach((config, name) => {
      const breaker = getBreaker(name);
      if (breaker.state !== 'OPEN') {
        available.push(name);
      }
    });

    return available.sort((a, b) => this.providers.get(a).priority - this.providers.get(b).priority);
  }

  /**
   * Select least loaded provider for load balancing
   */
  selectLeastLoadedProvider(availableProviders) {
    let leastLoaded = availableProviders[0];
    let minLoad = this.getCurrentLoad(leastLoaded);

    for (const provider of availableProviders.slice(1)) {
      const load = this.getCurrentLoad(provider);
      if (load < minLoad) {
        minLoad = load;
        leastLoaded = provider;
      }
    }

    return leastLoaded;
  }

  /**
   * Get current load for a provider
   */
  getCurrentLoad(providerName) {
    const breaker = getBreaker(providerName);
    const metrics = breaker.getMetrics();

    // Combine multiple factors for load calculation
    const responseTimeWeight = 0.4;
    const requestVolumeWeight = 0.3;
    const failureRateWeight = 0.3;

    const normalizedResponseTime = Math.min(metrics.averageResponseTime / 1000, 1); // Normalize to 0-1
    const normalizedVolume = Math.min(metrics.recentRequests / 100, 1); // Normalize to 0-1
    const failureRate = metrics.recentFailureRate;

    return (normalizedResponseTime * responseTimeWeight) +
           (normalizedVolume * requestVolumeWeight) +
           (failureRate * failureRateWeight);
  }

  /**
   * Perform health check for a provider
   */
  async performHealthCheck(providerName) {
    const provider = this.providers.get(providerName);
    if (!provider.healthEndpoint) return true;

    try {
      const response = await fetch(provider.healthEndpoint, {
        method: 'GET',
        headers: this.getProviderHeaders(provider),
        timeout: 5000
      });

      return response.ok;
    } catch (error) {
      return false;
    }
  }

  /**
   * Utility methods for content processing
   */
  sanitizeInput(input) {
    return input
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .trim();
  }

  sanitizeOutput(output) {
    return output
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .trim();
  }

  detectPromptInjection(prompt) {
    const injectionPatterns = [
      /ignore\s+previous\s+instructions/i,
      /forget\s+everything\s+above/i,
      /system\s*:\s*ignore/i,
      /override\s+safety/i
    ];

    return injectionPatterns.some(pattern => pattern.test(prompt));
  }

  redactPII(text) {
    return text
      .replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[REDACTED-CARD]')
      .replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[REDACTED-SSN]')
      .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[REDACTED-EMAIL]');
  }

  detectPII(text) {
    const patterns = [
      /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/, // Credit card
      /\b\d{3}-\d{2}-\d{4}\b/, // SSN
      /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/ // Email
    ];

    return patterns.some(pattern => pattern.test(text));
  }

  classifyContent(text) {
    const classifications = [];

    if (/buy|sell|trade|invest|price target|recommendation/i.test(text)) {
      classifications.push('financial_analysis');
    }

    if (/real.?time|live|current|now|today/i.test(text)) {
      classifications.push('real_time_data');
    }

    if (/function|code|script|program|algorithm/i.test(text)) {
      classifications.push('code_generation');
    }

    return classifications;
  }

  addFinancialDisclaimer(prompt) {
    const disclaimer = '\n\n[IMPORTANT: This is not financial advice. Always do your own research and consult with qualified professionals before making investment decisions.]';
    return prompt + disclaimer;
  }

  /**
   * Cost and metrics tracking
   */
  calculateCost(providerName, result) {
    const provider = this.providers.get(providerName);
    const tokens = result.usage?.totalTokens || 0;
    return (tokens / 1000) * provider.costPer1kTokens;
  }

  async recordSuccess(provider, request, result, responseTime) {
    const cost = this.calculateCost(provider, result);

    // Record user costs
    this.recordUserCost(request.userId, cost);

    // Record provider metrics
    this.recordProviderMetrics(provider, {
      success: true,
      responseTime,
      tokens: result.usage?.totalTokens || 0,
      cost
    });

    // Record telemetry
    this.recordTelemetry('ai_completion_success', {
      provider,
      responseTime,
      cost,
      tokens: result.usage?.totalTokens || 0
    });
  }

  async recordFailure(requestId, error, responseTime) {
    this.recordTelemetry('ai_completion_failure', {
      requestId,
      error: error.message,
      responseTime
    });
  }

  recordUserCost(userId, cost) {
    const now = Date.now();
    const userKey = `user:${userId}`;

    if (!this.costTracking.has(userKey)) {
      this.costTracking.set(userKey, {
        hourly: [],
        daily: [],
        monthly: []
      });
    }

    const userCosts = this.costTracking.get(userKey);
    userCosts.hourly.push({ cost, timestamp: now });
    userCosts.daily.push({ cost, timestamp: now });
    userCosts.monthly.push({ cost, timestamp: now });

    // Clean old entries
    this.cleanOldCostEntries(userCosts);
  }

  getUserCosts(userId) {
    const userKey = `user:${userId}`;
    const userCosts = this.costTracking.get(userKey) || { hourly: [], daily: [], monthly: [] };

    const now = Date.now();
    const hour = 60 * 60 * 1000;
    const day = 24 * hour;
    const month = 30 * day;

    return {
      hourly: userCosts.hourly.filter(c => now - c.timestamp < hour).reduce((sum, c) => sum + c.cost, 0),
      daily: userCosts.daily.filter(c => now - c.timestamp < day).reduce((sum, c) => sum + c.cost, 0),
      monthly: userCosts.monthly.filter(c => now - c.timestamp < month).reduce((sum, c) => sum + c.cost, 0)
    };
  }

  getGlobalCosts() {
    const now = Date.now();
    let hourly = 0, daily = 0, monthly = 0;

    this.costTracking.forEach(userCosts => {
      const costs = this.getUserCosts(userCosts);
      hourly += costs.hourly;
      daily += costs.daily;
      monthly += costs.monthly;
    });

    return { hourly, daily, monthly };
  }

  /**
   * Utility methods
   */
  generateRequestId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
  }

  generateIdempotencyKey(request, provider) {
    const data = `${request.prompt}:${provider}:${request.maxTokens}:${request.temperature}`;
    return crypto.createHash('sha256').update(data).digest('hex').substring(0, 16);
  }

  async getCachedResult(key) {
    // Implement caching logic (Redis, memory, etc.)
    return null;
  }

  async cacheResult(key, result) {
    // Implement caching logic (Redis, memory, etc.)
  }

  recordTelemetry(event, data) {
    if (this.telemetry.enabled) {
      console.log(`📊 Telemetry: ${event}`, data);
      // Send to OpenTelemetry, DataDog, etc.
    }
  }

  createUserFriendlyError(error) {
    // Convert technical errors to user-friendly messages
    if (error.message.includes('timeout')) {
      return new Error('The request took too long to process. Please try again.');
    }
    if (error.message.includes('rate limit')) {
      return new Error('Too many requests. Please wait a moment before trying again.');
    }
    if (error.message.includes('cost limit')) {
      return new Error('Usage limit reached. Please check your plan or try again later.');
    }

    return new Error('Sorry, I encountered an issue while processing your request. Please try again.');
  }

  startMetricsCollection() {
    setInterval(() => {
      this.collectAndEmitMetrics();
    }, this.telemetry.metricsInterval);
  }

  collectAndEmitMetrics() {
    const globalMetrics = {
      totalRequests: 0,
      totalFailures: 0,
      totalCost: 0,
      averageResponseTime: 0
    };

    // Collect metrics from all circuit breakers
    this.providers.forEach((config, name) => {
      const breaker = getBreaker(name);
      const metrics = breaker.getMetrics();

      globalMetrics.totalRequests += metrics.totalRequests;
      globalMetrics.totalFailures += metrics.totalFailures;
      globalMetrics.averageResponseTime += metrics.averageResponseTime;
    });

    this.recordTelemetry('service_metrics', globalMetrics);
  }
}

module.exports = ProductionAIProviderService;