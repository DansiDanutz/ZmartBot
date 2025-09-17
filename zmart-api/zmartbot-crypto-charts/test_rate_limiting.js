const FreeDataAggregator = require('./lib/FreeDataAggregator');

async function testRateLimiting() {
    console.log('🧪 Testing Enhanced Rate Limiting...\n');
    
    const aggregator = new FreeDataAggregator();
    
    // Wait for API keys to load
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('📊 Initial API Key Status:');
    console.log(`CoinGecko: ${aggregator.apiKeys.coingecko ? '✅ Loaded' : '❌ Not loaded'}`);
    console.log(`CryptoMeter: ${aggregator.apiKeys.cryptometer ? '✅ Loaded' : '❌ Not loaded'}`);
    
    if (aggregator.apiKeys.coingecko) {
        console.log(`🔑 CoinGecko API Key: ${aggregator.apiKeys.coingecko.substring(0, 8)}...`);
    }
    
    console.log('\n🧪 Testing Rate-Limited API Calls...');
    console.log('This will make multiple API calls with proper delays...\n');
    
    const symbols = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana'];
    const startTime = Date.now();
    
    try {
        for (let i = 0; i < symbols.length; i++) {
            const symbol = symbols[i];
            console.log(`📈 [${i + 1}/${symbols.length}] Getting price for ${symbol.toUpperCase()}...`);
            
            try {
                const price = await aggregator.getCurrentPrice(symbol);
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                console.log(`   ✅ ${symbol.toUpperCase()}: $${price} (${elapsed}s elapsed)`);
            } catch (error) {
                console.log(`   ❌ ${symbol.toUpperCase()}: ${error.message}`);
            }
            
            // Small delay between symbols for better visibility
            if (i < symbols.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }
        
        console.log('\n📊 Rate Limiting Stats:');
        const stats = aggregator.getAPIUsageStats();
        console.log('API Usage:');
        console.log(`  CoinGecko: ${stats.coingecko.calls} calls, last: ${stats.coingecko.lastCall}`);
        console.log(`  Binance: ${stats.binance.calls} calls, last: ${stats.binance.lastCall}`);
        console.log(`  CryptoMeter: ${stats.cryptometer.calls} calls, last: ${stats.cryptometer.lastCall}`);
        
        console.log('\nRate Limits:');
        Object.entries(stats.rateLimits).forEach(([source, limit]) => {
            console.log(`  ${source}: ${limit.calls}/${limit.maxCalls} calls, delay: ${limit.minDelayMs}ms`);
        });
        
        const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
        console.log(`\n⏱️ Total test time: ${totalTime} seconds`);
        console.log('✅ Rate limiting test completed successfully!');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    } finally {
        await aggregator.close();
        console.log('\n🔒 Resources cleaned up');
    }
}

// Run the test
testRateLimiting().catch(console.error);
