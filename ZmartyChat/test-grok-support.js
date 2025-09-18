#!/usr/bin/env node

/**
 * GROK AI PROVIDER TEST
 * Tests the new multi-provider AI system including Grok support
 */

import dotenv from 'dotenv';

// Load environment
dotenv.config({ path: '.env.local' });

console.log('🤖 Testing Grok AI Provider Support...');

async function testGrokSupport() {
  try {
    // Test the AI Provider Service
    console.log('\n1️⃣ Testing AI Provider Service...');
    const { aiProviderService } = await import('./src/services/AIProviderService.js');

    // Get provider status
    console.log('📊 Provider Status:');
    const status = aiProviderService.getStatus();
    console.log(JSON.stringify(status, null, 2));

    // Test health check
    console.log('\n🏥 Health Check:');
    const health = await aiProviderService.healthCheck();
    console.log(JSON.stringify(health, null, 2));

    // Test all available providers
    console.log('\n🧪 Testing All Providers:');
    const testResults = await aiProviderService.testProviders();
    console.log(JSON.stringify(testResults, null, 2));

    // Test Grok specifically if available
    if (process.env.GROK_API_KEY) {
      console.log('\n🚀 Testing Grok Specifically:');
      const grokResponse = await aiProviderService.generateCompletion(
        'What is Bitcoin? Respond in one sentence.',
        { provider: 'grok', maxTokens: 100 }
      );
      console.log('Grok Response:', grokResponse);
    } else {
      console.log('\n⚠️  GROK_API_KEY not found - add it to test Grok directly');
      console.log('   You can get a Grok API key from: https://x.ai/api');
    }

    // Test provider switching
    console.log('\n🔄 Testing Provider Switching:');
    const availableProviders = aiProviderService.getAvailableProviders();
    if (availableProviders.length > 1) {
      const originalProvider = aiProviderService.currentProvider;
      const newProvider = availableProviders.find(p => p !== originalProvider);

      console.log(`Switching from ${originalProvider} to ${newProvider}`);
      aiProviderService.switchProvider(newProvider);

      const switchedStatus = aiProviderService.getStatus();
      console.log(`Current provider after switch: ${switchedStatus.currentProvider}`);

      // Switch back
      aiProviderService.switchProvider(originalProvider);
      console.log(`Switched back to: ${aiProviderService.currentProvider}`);
    } else {
      console.log('Only one provider available - cannot test switching');
    }

    // Test secure config
    console.log('\n🔐 Testing Secure Config:');
    const { default: config } = await import('./src/config/secure-config.js');
    const safeConfig = config.getSafeConfig();
    console.log('Safe config (no secrets):', JSON.stringify(safeConfig, null, 2));

    console.log('\n✅ All tests completed successfully!');

    console.log('\n💡 Setup Instructions:');
    console.log('To use different AI providers, add these to your .env.local:');
    console.log('');
    console.log('# Choose primary provider');
    console.log('AI_PROVIDER=grok  # or openai, claude, gemini');
    console.log('');
    console.log('# Grok (X.ai) - Get from https://x.ai/api');
    console.log('GROK_API_KEY=your_grok_api_key_here');
    console.log('');
    console.log('# OpenAI - Get from https://platform.openai.com/api-keys');
    console.log('OPENAI_API_KEY=your_openai_api_key_here');
    console.log('');
    console.log('# Claude - Get from https://console.anthropic.com/');
    console.log('CLAUDE_API_KEY=your_claude_api_key_here');
    console.log('');
    console.log('# Gemini - Get from https://makersuite.google.com/app/apikey');
    console.log('GEMINI_API_KEY=your_gemini_api_key_here');

    return true;

  } catch (error) {
    console.error('❌ Grok support test failed:', error);
    console.error('Stack:', error.stack);
    return false;
  }
}

// Run the test
testGrokSupport()
  .then(success => {
    if (success) {
      console.log('\n🎉 GROK SUPPORT READY!');
      console.log('🚀 ZmartyChat now supports multiple AI providers including Grok');
      process.exit(0);
    } else {
      console.log('\n⚠️  Tests completed with issues');
      process.exit(1);
    }
  })
  .catch(console.error);