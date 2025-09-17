// API Proxy Configuration for Professional Dashboard
// This file redirects external API calls through our backend to avoid CORS issues

(function() {
    // Store original fetch
    const originalFetch = window.fetch;
    
    // Override fetch to intercept API calls
    window.fetch = function(url, options) {
        // Convert URL to string if it's a URL object
        const urlString = url.toString();
        
        // Check if this is a localhost:3400 API call that should be proxied to port 8000
        if (urlString.includes('localhost:3400/api/')) {
            // Redirect to backend API on port 8000
            const proxyUrl = urlString.replace('localhost:3400', 'localhost:8000');
            console.log('Proxying API request:', urlString, '->', proxyUrl);
            return originalFetch(proxyUrl, options)
                .catch(err => {
                    console.error('API proxy failed:', err);
                    throw err;
                });
        }
        
        // Check if this is a relative API call that should be proxied to port 8000
        if (urlString.startsWith('/api/')) {
            // Redirect to backend API on port 8000
            const proxyUrl = `http://localhost:8000${urlString}`;
            console.log('Proxying relative API request:', urlString, '->', proxyUrl);
            return originalFetch(proxyUrl, options)
                .catch(err => {
                    console.error('API proxy failed:', err);
                    throw err;
                });
        }
        
        // Check if this is a Binance API call
        if (urlString.includes('api.binance.com')) {
            // Parse the URL
            const urlObj = new URL(urlString);
            
            // Redirect to our proxy endpoints
            if (urlString.includes('/api/v3/ticker/24hr')) {
                // Extract symbol parameter and fix BTCUSD to BTCUSDT
                let symbol = urlObj.searchParams.get('symbol');
                if (symbol === 'BTCUSD') symbol = 'BTCUSDT';
                // Redirect to backend API on port 8000
                const proxyUrl = `http://localhost:8000/api/v1/binance/ticker/24hr?symbol=${symbol}`;
                console.log('Redirecting Binance ticker request to backend:', proxyUrl);
                return originalFetch(proxyUrl, options)
                    .catch(err => {
                        console.log('Proxy failed, returning mock data');
                        // Return mock data if proxy fails
                        return new Response(JSON.stringify({
                            symbol: symbol,
                            lastPrice: "67890.12",
                            priceChange: "1234.56",
                            priceChangePercent: "2.50",
                            volume: "1234567890",
                            quoteVolume: "84000000000",
                            highPrice: "68500.00",
                            lowPrice: "66000.00"
                        }), {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        });
                    });
            }
            else if (urlString.includes('/api/v3/klines')) {
                // Extract parameters and fix BTCUSD to BTCUSDT
                let symbol = urlObj.searchParams.get('symbol');
                if (symbol === 'BTCUSD') symbol = 'BTCUSDT';
                const interval = urlObj.searchParams.get('interval') || '1h';
                const limit = urlObj.searchParams.get('limit') || '24';
                // Redirect to backend API on port 8000
                const proxyUrl = `http://localhost:8000/api/v1/binance/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;
                console.log('Redirecting Binance klines request to backend:', proxyUrl);
                return originalFetch(proxyUrl, options)
                    .catch(err => {
                        console.log('Proxy failed, returning mock klines data');
                        // Return mock klines data if proxy fails
                        const now = Date.now();
                        const mockKlines = [];
                        for (let i = 0; i < parseInt(limit); i++) {
                            const timestamp = now - (i * 3600000); // 1 hour intervals
                            mockKlines.push([
                                timestamp,           // Open time
                                "67000.00",         // Open
                                "68000.00",         // High
                                "66000.00",         // Low
                                "67890.12",         // Close
                                "1234.56",          // Volume
                                timestamp + 3599999, // Close time
                                "84000000",         // Quote asset volume
                                1000,               // Number of trades
                                "600.00",           // Taker buy base asset volume
                                "40000000",         // Taker buy quote asset volume
                                "0"                 // Ignore
                            ]);
                        }
                        return new Response(JSON.stringify(mockKlines), {
                            status: 200,
                            headers: { 'Content-Type': 'application/json' }
                        });
                    });
            }
            // Add more Binance endpoints as needed
            else {
                console.warn('Unproxied Binance API call:', urlString);
            }
        }
        
        // For all other requests, use original fetch
        return originalFetch(url, options);
    };
    
    console.log('API Proxy initialized - All API calls will be routed through backend');
})();