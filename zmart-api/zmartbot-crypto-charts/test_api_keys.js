const FreeDataAggregator = require('./lib/FreeDataAggregator');

async function testAPIKeys() {
    console.log('🧪 Testing API Key Integration...\n');
    
    const aggregator = new FreeDataAggregator();
    
    // Wait a moment for API keys to load
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('📊 API Key Status:');
    console.log(`CoinGecko: ${aggregator.apiKeys.coingecko ? '✅ Loaded' : '❌ Not loaded'}`);
    console.log(`CryptoMeter: ${aggregator.apiKeys.cryptometer ? '✅ Loaded' : '❌ Not loaded'}`);
    
    if (aggregator.apiKeys.coingecko) {
        console.log(`\n🔑 CoinGecko API Key: ${aggregator.apiKeys.coingecko.substring(0, 8)}...`);
    }
    
    console.log('\n🧪 Testing API Calls...');
    
    try {
        // Test CoinGecko API call
        console.log('\n📈 Testing CoinGecko API...');
        const btcPrice = await aggregator.getCurrentPrice('bitcoin');
        console.log(`Bitcoin Price: $${btcPrice}`);
        
        // Test API usage stats
        console.log('\n📊 API Usage Stats:');
        const stats = aggregator.getAPIUsageStats();
        console.log(JSON.stringify(stats, null, 2));
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
    
    await aggregator.close();
    console.log('\n✅ Test completed');
}

testAPIKeys().catch(console.error);
