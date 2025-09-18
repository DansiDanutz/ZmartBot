#!/usr/bin/env node

/**
 * DIRECT GROK API TEST
 * Tests the live Grok integration with real API key
 */

import dotenv from 'dotenv';

// Load environment
dotenv.config({ path: '.env.local' });

console.log('🚀 Testing Direct Grok API Integration...');

async function testGrokDirect() {
  try {
    // Test the AI Provider Service directly
    console.log('\n🤖 Loading AI Provider Service...');
    const { aiProviderService } = await import('./src/services/AIProviderService.js');

    // Check provider status
    const status = aiProviderService.getStatus();
    console.log('📊 Provider Status:');
    console.log(`Current Provider: ${status.currentProvider}`);
    console.log(`Available Providers: ${status.availableProviders.join(', ')}`);
    console.log(`Grok Configured: ${status.providerConfigs.grok.configured}`);

    if (!status.providerConfigs.grok.configured) {
      throw new Error('Grok not configured properly');
    }

    // Test Grok with a simple crypto question
    console.log('\n🚀 Testing Live Grok Response...');
    console.log('Question: "What is Bitcoin in one sentence?"');

    const response = await aiProviderService.generateCompletion(
      'What is Bitcoin in one sentence?',
      {
        provider: 'grok',
        maxTokens: 100,
        temperature: 0.7,
        systemPrompt: 'You are Zmarty, a helpful crypto AI assistant. Be concise and educational.'
      }
    );

    console.log('\n✅ SUCCESS! Grok responded:');
    console.log('🤖 Provider:', response.provider);
    console.log('📝 Model:', response.model);
    console.log('💬 Response:', response.content);
    console.log('📊 Usage:', response.usage);
    console.log('🎯 Finish Reason:', response.finishReason);

    // Test another question about trading
    console.log('\n🔍 Testing Crypto Trading Question...');
    console.log('Question: "Give me 3 key factors that affect crypto prices."');

    const tradingResponse = await aiProviderService.generateCompletion(
      'Give me 3 key factors that affect crypto prices.',
      {
        provider: 'grok',
        maxTokens: 150,
        temperature: 0.7
      }
    );

    console.log('\n💡 Grok Trading Analysis:');
    console.log(tradingResponse.content);

    // Test health check
    console.log('\n🏥 Provider Health Check:');
    const health = await aiProviderService.healthCheck();
    console.log(JSON.stringify(health, null, 2));

    console.log('\n🎉 GROK INTEGRATION FULLY WORKING!');
    console.log('✅ Live API calls successful');
    console.log('✅ Crypto knowledge accessible');
    console.log('✅ ZmartyChat ready for users');

    return true;

  } catch (error) {
    console.error('❌ Direct Grok test failed:', error);
    console.error('Stack:', error.stack);
    return false;
  }
}

// Run the test
testGrokDirect()
  .then(success => {
    if (success) {
      console.log('\n🚀 LIVE GROK INTEGRATION CONFIRMED!');
      console.log('🎯 Your ZmartyChat system is powered by Grok AI');
      console.log('🔥 Ready to deploy to users!');
      process.exit(0);
    } else {
      console.log('\n⚠️  Integration test failed');
      process.exit(1);
    }
  })
  .catch(console.error);