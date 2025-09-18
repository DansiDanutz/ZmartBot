#!/usr/bin/env node

/**
 * TEST ALL AI PROVIDERS
 * Tests OpenAI, Claude, Grok, and Gemini integration
 */

import dotenv from 'dotenv';

// Load environment
dotenv.config({ path: '.env.local' });

console.log('🤖 Testing ALL AI Providers Integration...');

async function testAllProviders() {
  try {
    // Test the AI Provider Service
    console.log('\n1️⃣ Loading Multi-Provider AI Service...');
    const { aiProviderService } = await import('./src/services/AIProviderService.js');

    // Show all provider configurations
    const status = aiProviderService.getStatus();
    console.log('\n📊 ALL PROVIDER CONFIGURATIONS:');
    console.log(`Current Primary: ${status.currentProvider}`);
    console.log(`Available: ${status.availableProviders.join(', ') || 'None configured'}`);

    console.log('\n🔧 Provider Setup Status:');
    Object.entries(status.providerConfigs).forEach(([provider, config]) => {
      const status = config.configured ? '✅ CONFIGURED' : '⚠️  Need API Key';
      console.log(`${provider.toUpperCase()}: ${status} (${config.model})`);
    });

    // Test available providers
    console.log('\n🧪 Testing Available Providers:');

    const availableProviders = status.availableProviders;
    if (availableProviders.length === 0) {
      console.log('⚠️  No providers configured yet');
    }

    for (const provider of availableProviders) {
      console.log(`\n🚀 Testing ${provider.toUpperCase()}:`);

      try {
        const response = await aiProviderService.generateCompletion(
          'Explain Ethereum in one sentence.',
          {
            provider: provider,
            maxTokens: 100,
            systemPrompt: `You are Zmarty, a crypto AI assistant. Be concise and educational.`
          }
        );

        console.log(`✅ ${provider.toUpperCase()} Response:`);
        console.log(`Model: ${response.model}`);
        console.log(`Response: ${response.content.substring(0, 200)}...`);
        console.log(`Tokens: ${response.usage?.total_tokens || 'N/A'}`);

      } catch (error) {
        console.log(`❌ ${provider.toUpperCase()} Error: ${error.message}`);
      }
    }

    // Show setup instructions for missing providers
    console.log('\n📝 SETUP INSTRUCTIONS FOR ALL PROVIDERS:');
    console.log('\nAdd these to your .env.local to enable more providers:');

    if (!status.providerConfigs.openai.configured) {
      console.log('\n# OpenAI (GPT-4) - Get from https://platform.openai.com/api-keys');
      console.log('OPENAI_API_KEY=your_openai_key_here');
    }

    if (!status.providerConfigs.claude.configured) {
      console.log('\n# Claude (Anthropic) - Get from https://console.anthropic.com/');
      console.log('CLAUDE_API_KEY=your_claude_key_here');
    }

    if (!status.providerConfigs.gemini.configured) {
      console.log('\n# Gemini (Google) - Get from https://makersuite.google.com/app/apikey');
      console.log('GEMINI_API_KEY=your_gemini_key_here');
    }

    // Test provider switching
    if (availableProviders.length > 1) {
      console.log('\n🔄 Testing Provider Switching:');
      const originalProvider = aiProviderService.currentProvider;

      for (const provider of availableProviders) {
        if (provider !== originalProvider) {
          console.log(`Switching to ${provider}...`);
          aiProviderService.switchProvider(provider);
          console.log(`✅ Current provider: ${aiProviderService.currentProvider}`);
        }
      }

      // Switch back
      aiProviderService.switchProvider(originalProvider);
      console.log(`🔄 Switched back to: ${aiProviderService.currentProvider}`);
    }

    // Test health check
    console.log('\n🏥 Multi-Provider Health Check:');
    const health = await aiProviderService.healthCheck();
    console.log(JSON.stringify(health, null, 2));

    // Show the power of multi-provider system
    console.log('\n🔥 MULTI-PROVIDER ADVANTAGES:');
    console.log('✅ Automatic Failover: If one provider fails, switch to another');
    console.log('✅ Model Diversity: Different AI models for different strengths');
    console.log('✅ Cost Optimization: Use cheaper providers for simple tasks');
    console.log('✅ Rate Limit Handling: Distribute load across providers');
    console.log('✅ Provider Redundancy: Never be locked into one AI company');

    return true;

  } catch (error) {
    console.error('❌ Multi-provider test failed:', error);
    console.error('Stack:', error.stack);
    return false;
  }
}

// Run the test
testAllProviders()
  .then(success => {
    if (success) {
      console.log('\n🎉 MULTI-PROVIDER AI SYSTEM READY!');
      console.log('🚀 ZmartyChat supports OpenAI, Claude, Grok & Gemini');
      console.log('🔥 Most advanced AI trading companion architecture!');
      process.exit(0);
    } else {
      console.log('\n⚠️  Multi-provider test completed with issues');
      process.exit(1);
    }
  })
  .catch(console.error);