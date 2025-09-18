/**
 * AI Provider Service
 * Unified interface for multiple AI providers including OpenAI, Grok, Claude, and Gemini
 */

import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import config from '../config/secure-config.js';

export default class AIProviderService {
  constructor() {
    this.currentProvider = config.ai.provider;
    this.clients = {};
    this.initializeProviders();
  }

  /**
   * Initialize all available AI providers
   */
  initializeProviders() {
    console.log(`🤖 Initializing AI Provider Service with primary: ${this.currentProvider}`);

    // Initialize OpenAI
    if (config.ai.openai.apiKey) {
      this.clients.openai = new OpenAI({
        apiKey: config.ai.openai.apiKey,
        baseURL: config.ai.openai.baseUrl
      });
      console.log('✅ OpenAI provider initialized');
    }

    // Initialize Grok (using OpenAI-compatible API)
    if (config.ai.grok.apiKey) {
      this.clients.grok = new OpenAI({
        apiKey: config.ai.grok.apiKey,
        baseURL: config.ai.grok.baseUrl
      });
      console.log('✅ Grok provider initialized');
    }

    // Initialize Claude (using native Anthropic SDK)
    if (config.ai.claude.apiKey) {
      this.clients.claude = new Anthropic({
        apiKey: config.ai.claude.apiKey
      });
      console.log('✅ Claude provider initialized');
    }

    // Initialize Gemini (using OpenAI-compatible wrapper)
    if (config.ai.gemini.apiKey) {
      this.clients.gemini = new OpenAI({
        apiKey: config.ai.gemini.apiKey,
        baseURL: config.ai.gemini.baseUrl
      });
      console.log('✅ Gemini provider initialized');
    }

    // Fallback to any available provider if primary is not available
    if (!this.clients[this.currentProvider]) {
      const availableProviders = Object.keys(this.clients);
      if (availableProviders.length > 0) {
        this.currentProvider = availableProviders[0];
        console.log(`⚠️  Primary provider not available, falling back to: ${this.currentProvider}`);
      } else {
        console.log('⚠️  No AI providers configured - will use mock responses');
      }
    }
  }

  /**
   * Generate completion using the active provider
   */
  async generateCompletion(prompt, options = {}) {
    try {
      const provider = options.provider || this.currentProvider;
      const client = this.clients[provider];

      if (!client) {
        console.log(`⚠️  Provider ${provider} not available, using mock response`);
        return this.generateMockResponse(prompt);
      }

      const providerConfig = config.ai[provider];
      const model = options.model || providerConfig.model;
      const maxTokens = options.maxTokens || providerConfig.maxTokens;

      console.log(`🤖 Generating completion with ${provider} (${model})`);

      let response;

      if (provider === 'claude') {
        // Use Claude's native API format
        response = await client.messages.create({
          model: model,
          max_tokens: maxTokens,
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          system: options.systemPrompt || this.getDefaultSystemPrompt(),
          temperature: options.temperature || 0.7
        });

        return {
          content: response.content[0].text,
          provider: provider,
          model: model,
          usage: response.usage,
          finishReason: response.stop_reason
        };
      } else {
        // Use OpenAI-compatible format for other providers
        response = await client.chat.completions.create({
          model: model,
          messages: [
            {
              role: 'system',
              content: options.systemPrompt || this.getDefaultSystemPrompt()
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          max_tokens: maxTokens,
          temperature: options.temperature || 0.7,
          top_p: options.topP || 1,
          frequency_penalty: options.frequencyPenalty || 0,
          presence_penalty: options.presencePenalty || 0
        });

        return {
          content: response.choices[0].message.content,
          provider: provider,
          model: model,
          usage: response.usage,
          finishReason: response.choices[0].finish_reason
        };
      }

    } catch (error) {
      console.error(`❌ AI Provider error (${this.currentProvider}):`, error.message);

      // Try fallback provider
      const availableProviders = Object.keys(this.clients).filter(p => p !== this.currentProvider);
      if (availableProviders.length > 0 && !options.noFallback) {
        console.log(`🔄 Trying fallback provider: ${availableProviders[0]}`);
        return await this.generateCompletion(prompt, {
          ...options,
          provider: availableProviders[0],
          noFallback: true
        });
      }

      // Return mock response if all providers fail
      return this.generateMockResponse(prompt);
    }
  }

  /**
   * Generate embeddings for semantic search
   */
  async generateEmbeddings(text, options = {}) {
    try {
      const provider = options.provider || this.currentProvider;
      const client = this.clients[provider];

      if (!client) {
        return this.generateMockEmbeddings(text);
      }

      // For now, use OpenAI for embeddings as it has dedicated models
      const embeddingClient = this.clients.openai || client;

      const response = await embeddingClient.embeddings.create({
        model: options.model || 'text-embedding-ada-002',
        input: text
      });

      return {
        embedding: response.data[0].embedding,
        provider: provider,
        usage: response.usage
      };

    } catch (error) {
      console.error(`❌ Embedding error:`, error.message);
      return this.generateMockEmbeddings(text);
    }
  }

  /**
   * Switch primary provider
   */
  switchProvider(provider) {
    if (this.clients[provider]) {
      this.currentProvider = provider;
      console.log(`🔄 Switched to provider: ${provider}`);
      return true;
    } else {
      console.error(`❌ Provider ${provider} not available`);
      return false;
    }
  }

  /**
   * Get available providers
   */
  getAvailableProviders() {
    return Object.keys(this.clients);
  }

  /**
   * Get current provider status
   */
  getStatus() {
    return {
      currentProvider: this.currentProvider,
      availableProviders: this.getAvailableProviders(),
      providerConfigs: Object.keys(config.ai).reduce((acc, provider) => {
        if (provider !== 'provider') {
          acc[provider] = {
            configured: !!config.ai[provider].apiKey,
            model: config.ai[provider].model,
            baseUrl: config.ai[provider].baseUrl
          };
        }
        return acc;
      }, {})
    };
  }

  /**
   * Default system prompt for Zmarty
   */
  getDefaultSystemPrompt() {
    return `You are Zmarty, an AI-powered cryptocurrency trading companion. You provide:

1. **Data-driven insights** based on market analysis, not trading advice
2. **Educational content** about cryptocurrency and trading concepts
3. **Risk assessment** using statistical probability analysis
4. **Market probabilities** similar to poker odds calculations
5. **Engaging content** to keep users informed and learning

Key characteristics:
- Always emphasize that you provide educational content, not financial advice
- Use probability language (like "65% chance of..." rather than predictions)
- Be engaging and slightly addictive in your responses
- Include interesting facts and comparisons
- Focus on helping users understand market dynamics
- Encourage responsible decision-making

Remember: You analyze data and probabilities, you don't give trading advice.`;
  }

  /**
   * Generate mock response when no providers are available
   */
  generateMockResponse(prompt) {
    const mockResponses = [
      "I'm currently running in demo mode. To get full AI-powered insights, please configure an AI provider (OpenAI, Grok, Claude, or Gemini) in your environment variables.",
      "Demo mode active! This is a placeholder response. Configure your AI provider API keys to get real-time crypto analysis and insights.",
      "🤖 Mock response: I'd love to analyze that for you! Please set up an AI provider (like Grok) to get detailed market insights and probability analysis."
    ];

    return {
      content: mockResponses[Math.floor(Math.random() * mockResponses.length)],
      provider: 'mock',
      model: 'demo',
      usage: { total_tokens: 50, prompt_tokens: 25, completion_tokens: 25 },
      finishReason: 'stop'
    };
  }

  /**
   * Generate mock embeddings
   */
  generateMockEmbeddings(text) {
    // Generate a deterministic but pseudo-random embedding based on text hash
    const hash = this.simpleHash(text);
    const embedding = Array.from({ length: 1536 }, (_, i) => {
      return Math.sin(hash + i) * 0.5; // Values between -0.5 and 0.5
    });

    return {
      embedding: embedding,
      provider: 'mock',
      usage: { total_tokens: text.length }
    };
  }

  /**
   * Simple hash function for mock embeddings
   */
  simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash;
  }

  /**
   * Test all providers
   */
  async testProviders() {
    const results = {};

    for (const provider of this.getAvailableProviders()) {
      try {
        console.log(`🧪 Testing ${provider}...`);
        const response = await this.generateCompletion(
          "Test message: respond with 'OK' if you're working",
          { provider, maxTokens: 10 }
        );
        results[provider] = {
          status: 'working',
          response: response.content.substring(0, 50)
        };
        console.log(`✅ ${provider}: Working`);
      } catch (error) {
        results[provider] = {
          status: 'error',
          error: error.message
        };
        console.log(`❌ ${provider}: ${error.message}`);
      }
    }

    return results;
  }

  /**
   * Health check
   */
  async healthCheck() {
    const status = this.getStatus();
    const hasAnyProvider = status.availableProviders.length > 0;

    return {
      status: hasAnyProvider ? 'healthy' : 'degraded',
      currentProvider: status.currentProvider,
      availableProviders: status.availableProviders,
      message: hasAnyProvider
        ? `AI Provider Service ready with ${status.availableProviders.length} provider(s)`
        : 'No AI providers configured - running in demo mode'
    };
  }
}

// Export singleton instance
const aiProviderService = new AIProviderService();
export { aiProviderService };