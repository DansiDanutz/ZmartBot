/**
 * ZmartyAI Service - Mobile Integration
 * Connects mobile app to our multi-provider AI backend
 */

class ZmartyAIService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:3001';
    this.wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:3001';
    this.socket = null;
    this.eventListeners = new Map();
    this.currentProvider = 'grok'; // Default to Grok for mobile
    this.conversationHistory = [];
    this.initializeWebSocket();
  }

  /**
   * Initialize WebSocket connection for real-time AI responses
   */
  initializeWebSocket() {
    if (typeof window !== 'undefined' && window.io) {
      this.socket = window.io(this.wsUrl, {
        transports: ['websocket', 'polling'],
        upgrade: true,
        autoConnect: true
      });

      this.socket.on('connect', () => {
        console.log('🤖 Connected to ZmartyAI backend');
        this.emit('connection', { status: 'connected' });
      });

      this.socket.on('ai_response', (data) => {
        this.handleAIResponse(data);
      });

      this.socket.on('market_alert', (data) => {
        this.handleMarketAlert(data);
      });

      this.socket.on('whale_alert', (data) => {
        this.handleWhaleAlert(data);
      });

      this.socket.on('pattern_trigger', (data) => {
        this.handlePatternTrigger(data);
      });

      this.socket.on('disconnect', () => {
        console.log('🤖 Disconnected from ZmartyAI backend');
        this.emit('connection', { status: 'disconnected' });
      });
    }
  }

  /**
   * Send message to AI and get response
   */
  async sendMessage(message, options = {}) {
    try {
      const messageData = {
        message: message,
        provider: options.provider || this.currentProvider,
        userId: this.getUserId(),
        conversationId: this.getConversationId(),
        timestamp: Date.now(),
        messageType: options.messageType || 'chat',
        context: {
          isMobile: true,
          location: 'chat',
          previousMessages: this.getRecentHistory(3)
        }
      };

      // Add to conversation history
      this.conversationHistory.push({
        role: 'user',
        content: message,
        timestamp: Date.now()
      });

      // Send via WebSocket for real-time response
      if (this.socket && this.socket.connected) {
        this.socket.emit('ai_message', messageData);
        return { status: 'sending', messageId: this.generateMessageId() };
      }

      // Fallback to HTTP request
      const response = await fetch(`${this.baseURL}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`
        },
        body: JSON.stringify(messageData)
      });

      const aiResponse = await response.json();
      this.handleAIResponse(aiResponse);

      return aiResponse;

    } catch (error) {
      console.error('❌ AI Service Error:', error);
      return this.generateErrorResponse(error);
    }
  }

  /**
   * Handle AI response from backend
   */
  handleAIResponse(data) {
    // Add to conversation history
    this.conversationHistory.push({
      role: 'assistant',
      content: data.content,
      provider: data.provider,
      timestamp: Date.now(),
      metadata: data.metadata || {}
    });

    // Optimize for mobile display
    const mobileOptimized = this.optimizeForMobile(data);

    // Emit to UI components
    this.emit('ai_response', mobileOptimized);

    // Track analytics
    this.trackInteraction('ai_response', {
      provider: data.provider,
      responseTime: data.responseTime,
      tokens: data.usage?.total_tokens
    });
  }

  /**
   * Optimize AI response for mobile display
   */
  optimizeForMobile(response) {
    const { content, provider, usage } = response;

    // Check if response is too long for mobile
    if (content.length > 200) {
      const summary = this.generateSummary(content);
      return {
        ...response,
        displayContent: summary,
        fullContent: content,
        isExpandable: true,
        actions: this.extractActionButtons(content),
        mobileFormat: true
      };
    }

    return {
      ...response,
      displayContent: content,
      fullContent: content,
      isExpandable: false,
      actions: this.extractActionButtons(content),
      mobileFormat: true
    };
  }

  /**
   * Generate summary for long responses
   */
  generateSummary(content) {
    // Extract key points from AI response
    const sentences = content.split('. ');
    if (sentences.length <= 2) return content;

    // Take first sentence and any sentences with key crypto terms
    const keyTerms = ['BTC', 'ETH', 'price', 'bullish', 'bearish', 'pump', 'dump', 'whale', 'alert'];
    const keySentences = sentences.filter(sentence =>
      keyTerms.some(term => sentence.toLowerCase().includes(term.toLowerCase()))
    );

    const summary = [sentences[0], ...keySentences.slice(0, 2)].join('. ');
    return summary.length > 150 ? sentences[0] + '...' : summary + '.';
  }

  /**
   * Extract action buttons from AI response
   */
  extractActionButtons(content) {
    const actions = [];

    // Check for common patterns that should become buttons
    if (content.includes('chart') || content.includes('Chart')) {
      actions.push({ type: 'view_chart', label: '📊 View Chart' });
    }

    if (content.includes('alert') || content.includes('Alert')) {
      actions.push({ type: 'set_alert', label: '🔔 Set Alert' });
    }

    if (content.includes('buy') || content.includes('sell')) {
      actions.push({ type: 'trade_action', label: '💰 Trade Now' });
    }

    if (content.includes('share') || content.includes('friends')) {
      actions.push({ type: 'share', label: '📱 Share' });
    }

    return actions;
  }

  /**
   * Handle market alerts
   */
  handleMarketAlert(data) {
    const mobileAlert = {
      ...data,
      title: this.formatAlertTitle(data),
      body: this.formatAlertBody(data),
      priority: data.severity || 'normal',
      actions: this.getAlertActions(data.type)
    };

    this.emit('market_alert', mobileAlert);
    this.showNotification(mobileAlert);
  }

  /**
   * Handle whale alerts
   */
  handleWhaleAlert(data) {
    const whaleAlert = {
      ...data,
      title: `🐋 Whale Alert: ${data.amount} ${data.symbol}`,
      body: `Large ${data.type} detected - ${data.amount} ${data.symbol}`,
      priority: 'high',
      actions: [
        { type: 'analyze', label: '🔍 Analyze Impact' },
        { type: 'track', label: '📊 Track Wallet' },
        { type: 'share', label: '📱 Share Alert' }
      ]
    };

    this.emit('whale_alert', whaleAlert);
    this.showNotification(whaleAlert);
  }

  /**
   * Handle pattern triggers
   */
  handlePatternTrigger(data) {
    const patternAlert = {
      ...data,
      title: `⚡ Pattern Alert: ${data.pattern}`,
      body: `${data.pattern} detected on ${data.symbol}`,
      priority: 'high',
      actions: [
        { type: 'view_chart', label: '📊 View Chart' },
        { type: 'set_alert', label: '🔔 Set Alert' },
        { type: 'share', label: '📱 Share Pattern' }
      ]
    };

    this.emit('pattern_trigger', patternAlert);
    this.showNotification(patternAlert);
  }

  /**
   * Show mobile notification
   */
  showNotification(alert) {
    if ('Notification' in window && Notification.permission === 'granted') {
      const notification = new Notification(alert.title, {
        body: alert.body,
        icon: '/assets/icons/zmarty-icon.png',
        badge: '/assets/icons/zmarty-badge.png',
        tag: alert.type,
        requireInteraction: alert.priority === 'urgent'
      });

      notification.onclick = () => {
        window.focus();
        this.emit('notification_click', alert);
      };
    }

    // Also emit for in-app notification system
    this.emit('show_notification', alert);
  }

  /**
   * Switch AI provider
   */
  switchProvider(provider) {
    const validProviders = ['openai', 'claude', 'grok', 'gemini'];
    if (validProviders.includes(provider)) {
      this.currentProvider = provider;
      this.emit('provider_changed', { provider });
      console.log(`🤖 Switched to ${provider.toUpperCase()}`);
    }
  }

  /**
   * Get available AI providers
   */
  async getAvailableProviders() {
    try {
      const response = await fetch(`${this.baseURL}/api/ai/providers`, {
        headers: { 'Authorization': `Bearer ${this.getAuthToken()}` }
      });
      return await response.json();
    } catch (error) {
      console.error('Error fetching providers:', error);
      return ['grok']; // Fallback
    }
  }

  /**
   * Get AI provider status
   */
  async getProviderStatus() {
    try {
      const response = await fetch(`${this.baseURL}/api/ai/status`, {
        headers: { 'Authorization': `Bearer ${this.getAuthToken()}` }
      });
      return await response.json();
    } catch (error) {
      console.error('Error fetching provider status:', error);
      return { status: 'unknown' };
    }
  }

  /**
   * Event listener management
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
      this.eventListeners.get(event).forEach(callback => callback(data));
    }
  }

  /**
   * Utility methods
   */
  getUserId() {
    return localStorage.getItem('user_id') || 'anonymous';
  }

  getConversationId() {
    return localStorage.getItem('conversation_id') || this.generateMessageId();
  }

  getAuthToken() {
    return localStorage.getItem('auth_token') || '';
  }

  generateMessageId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  getRecentHistory(count = 5) {
    return this.conversationHistory.slice(-count);
  }

  formatAlertTitle(data) {
    const icons = {
      price: '💰',
      volume: '📊',
      news: '📰',
      whale: '🐋',
      pattern: '⚡'
    };
    return `${icons[data.type] || '🔔'} ${data.title}`;
  }

  formatAlertBody(data) {
    return data.body || data.message || 'New market activity detected';
  }

  getAlertActions(type) {
    const actionMap = {
      price: [
        { type: 'view_chart', label: '📊 Chart' },
        { type: 'set_alert', label: '🔔 Alert' }
      ],
      whale: [
        { type: 'analyze', label: '🔍 Analyze' },
        { type: 'track', label: '📊 Track' }
      ],
      pattern: [
        { type: 'view_chart', label: '📊 Chart' },
        { type: 'share', label: '📱 Share' }
      ]
    };
    return actionMap[type] || [{ type: 'dismiss', label: '✕ Dismiss' }];
  }

  generateErrorResponse(error) {
    return {
      content: "🤖 I'm having trouble connecting right now. Please try again in a moment!",
      error: true,
      provider: 'system',
      timestamp: Date.now(),
      actions: [
        { type: 'retry', label: '🔄 Retry' },
        { type: 'support', label: '💬 Get Help' }
      ]
    };
  }

  trackInteraction(action, data) {
    // Track user interactions for analytics
    console.log('📊 Analytics:', action, data);

    // Send to analytics service
    if (window.gtag) {
      window.gtag('event', action, {
        custom_parameter_1: data.provider,
        custom_parameter_2: data.responseTime
      });
    }
  }

  /**
   * Cleanup
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
    this.eventListeners.clear();
  }
}

// Export singleton instance
const zmartyAI = new ZmartyAIService();
export default zmartyAI;