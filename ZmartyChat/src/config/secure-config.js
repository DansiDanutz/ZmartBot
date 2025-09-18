/**
 * SECURE CONFIGURATION LOADER
 * Loads sensitive credentials from environment variables or API manager
 * Never stores secrets in code or files
 */

import dotenv from 'dotenv';

// Load .env file
dotenv.config();

class SecureConfig {
  constructor() {
    this.validateRequired();
  }

  // Supabase configuration
  get supabase() {
    return {
      url: this.getRequired('SUPABASE_URL'),
      anonKey: this.getRequired('SUPABASE_ANON_KEY'),
      serviceKey: this.getRequired('SUPABASE_SERVICE_KEY')
    };
  }

  // AI Providers configuration
  get ai() {
    return {
      // Primary provider
      provider: this.getOptional('AI_PROVIDER', 'openai'), // openai, grok, claude, gemini

      // OpenAI configuration
      openai: {
        apiKey: this.getOptional('OPENAI_API_KEY'),
        baseUrl: this.getOptional('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
        model: this.getOptional('OPENAI_MODEL', 'gpt-4'),
        maxTokens: parseInt(this.getOptional('OPENAI_MAX_TOKENS', '4000'))
      },

      // Grok (X.ai) configuration
      grok: {
        apiKey: this.getOptional('GROK_API_KEY'),
        baseUrl: this.getOptional('GROK_BASE_URL', 'https://api.x.ai/v1'),
        model: this.getOptional('GROK_MODEL', 'grok-3'),
        maxTokens: parseInt(this.getOptional('GROK_MAX_TOKENS', '4000'))
      },

      // Claude configuration
      claude: {
        apiKey: this.getOptional('CLAUDE_API_KEY'),
        baseUrl: this.getOptional('CLAUDE_BASE_URL', 'https://api.anthropic.com'),
        model: this.getOptional('CLAUDE_MODEL', 'claude-3-sonnet-20240229'),
        maxTokens: parseInt(this.getOptional('CLAUDE_MAX_TOKENS', '4000'))
      },

      // Gemini configuration
      gemini: {
        apiKey: this.getOptional('GEMINI_API_KEY'),
        baseUrl: this.getOptional('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta'),
        model: this.getOptional('GEMINI_MODEL', 'gemini-pro'),
        maxTokens: parseInt(this.getOptional('GEMINI_MAX_TOKENS', '4000'))
      }
    };
  }

  // Legacy OpenAI getter for backward compatibility
  get openai() {
    return this.ai.openai;
  }

  // JWT configuration
  get jwt() {
    return {
      secret: this.getRequired('JWT_SECRET')
    };
  }

  // Stripe configuration
  get stripe() {
    return {
      secretKey: this.getRequired('STRIPE_SECRET_KEY'),
      publishableKey: this.getRequired('STRIPE_PUBLISHABLE_KEY'),
      webhookSecret: this.getRequired('STRIPE_WEBHOOK_SECRET')
    };
  }

  // ElevenLabs configuration
  get elevenlabs() {
    return {
      apiKey: this.getRequired('ELEVENLABS_API_KEY'),
      agentId: this.getOptional('ELEVENLABS_AGENT_ID'),
      voiceId: this.getOptional('ELEVENLABS_VOICE_ID'),
      webhookUrl: this.getOptional('ELEVENLABS_WEBHOOK_URL'),
      webhookSecret: this.getOptional('ELEVENLABS_WEBHOOK_SECRET')
    };
  }

  // Trading API configuration
  get trading() {
    return {
      binance: {
        apiKey: this.getOptional('BINANCE_API_KEY'),
        secretKey: this.getOptional('BINANCE_SECRET_KEY')
      },
      cryptocompare: {
        apiKey: this.getOptional('CRYPTOCOMPARE_API_KEY')
      }
    };
  }

  // Server configuration
  get server() {
    return {
      port: parseInt(this.getOptional('PORT', '3001')),
      environment: this.getOptional('NODE_ENV', 'development'),
      frontendUrl: this.getOptional('FRONTEND_URL', 'http://localhost:3000')
    };
  }

  // Feature flags
  get features() {
    return {
      voiceChat: this.getBool('ENABLE_VOICE_CHAT', true),
      multiAgent: this.getBool('ENABLE_MULTI_AGENT', true),
      addictionHooks: this.getBool('ENABLE_ADDICTION_HOOKS', true),
      paperTrading: this.getBool('ENABLE_PAPER_TRADING', true)
    };
  }

  // Rate limits
  get limits() {
    return {
      maxCreditsPerDay: parseInt(this.getOptional('MAX_CREDITS_PER_DAY', '1000')),
      maxMessagesPerMinute: parseInt(this.getOptional('MAX_MESSAGES_PER_MINUTE', '10')),
      maxVoiceDurationMinutes: parseInt(this.getOptional('MAX_VOICE_DURATION_MINUTES', '30'))
    };
  }

  // Viral growth configuration
  get viral() {
    return {
      inviteOnlyMode: this.getBool('INVITE_ONLY_MODE', true),
      founderLimit: parseInt(this.getOptional('FOUNDER_LIMIT', '100')),
      defaultCredits: parseInt(this.getOptional('DEFAULT_CREDITS', '100')),
      commissionRateBase: parseFloat(this.getOptional('COMMISSION_RATE_BASE', '0.05'))
    };
  }

  // Helper methods
  getRequired(key) {
    const value = process.env[key];
    if (!value) {
      throw new Error(`Missing required environment variable: ${key}`);
    }
    return value;
  }

  getOptional(key, defaultValue = null) {
    return process.env[key] || defaultValue;
  }

  getBool(key, defaultValue = false) {
    const value = process.env[key];
    if (!value) return defaultValue;
    return value.toLowerCase() === 'true';
  }

  validateRequired() {
    const requiredVars = [
      'SUPABASE_URL',
      'SUPABASE_ANON_KEY',
      'SUPABASE_SERVICE_KEY',
      'JWT_SECRET'
    ];

    const missing = requiredVars.filter(key => !process.env[key]);

    if (missing.length > 0) {
      console.error('❌ Missing required environment variables:');
      missing.forEach(key => console.error(`   - ${key}`));
      console.error('\n💡 Add these to your environment or .env file');
      console.error('   For production, use your hosting platform\'s environment variable settings');
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }

  // Security check - never log sensitive data
  getSafeConfig() {
    return {
      server: this.server,
      features: this.features,
      limits: this.limits,
      viral: this.viral,
      // Don't include any actual secrets
      hasSupabase: !!process.env.SUPABASE_URL,
      aiProvider: this.ai.provider,
      aiProviders: {
        hasOpenAI: !!process.env.OPENAI_API_KEY,
        hasGrok: !!process.env.GROK_API_KEY,
        hasClaude: !!process.env.CLAUDE_API_KEY,
        hasGemini: !!process.env.GEMINI_API_KEY
      },
      hasStripe: !!process.env.STRIPE_SECRET_KEY,
      hasElevenLabs: !!process.env.ELEVENLABS_API_KEY
    };
  }
}

// Export singleton instance
const config = new SecureConfig();
export default config;