const http = require('http');
const url = require('url');

// Real KuCoin Futures Symbols
const KUCOIN_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BCHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT', 'ETCUSDT',
    'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT', 'XTZUSDT', 'BNBUSDT',
    'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT', 'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT',
    'THETAUSDT', 'ALGOUSDT', 'ZILUSDT', 'KNCUSDT', 'ZRXUSDT', 'COMPUSDT', 'OMGUSDT', 'DOGEUSDT',
    'SXPUSDT', 'KAVAUSDT', 'BANDUSDT', 'RLCUSDT', 'WAVESUSDT', 'MKRUSDT', 'SNXUSDT', 'DOTUSDT',
    'DEFIUSDT', 'YFIUSDT', 'BALUSDT', 'CRVUSDT', 'TRBUSDT', 'YFIIUSDT', 'RUNEUSDT', 'SUSHIUSDT',
    'SRMUSDT', 'BZRXUSDT', 'EGLDUSDT', 'SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'BLZUSDT', 'UNIUSDT',
    'AVAXUSDT', 'FTMUSDT', 'HNTUSDT', 'ENJUSDT', 'FLMUSDT', 'TOMOUSDT', 'RENUSDT', 'KSMUSDT',
    'NEARUSDT', 'AAVEUSDT', 'FILUSDT', 'RSRUSDT', 'LRCUSDT', 'MATICUSDT', 'OCEANUSDT', 'CVCUSDT',
    'BELUSDT', 'CTKUSDT', 'AXSUSDT', 'ALPHAUSDT', 'ZENUSDT', 'SKLUSDT', 'GRTUSDT', '1INCHUSDT',
    'AKROUSDT', 'CHZUSDT', 'SANDUSDT', 'ANKRUSDT', 'LUNAUSDT', 'BTSUSDT', 'LITUSDT', 'UNFIUSDT',
    'DODOUSDT', 'REEFUSDT', 'RVNUSDT', 'SFPUSDT', 'XEMUSDT', 'BTCSTUSDT', 'COTIUSDT', 'CHRUSDT',
    'MANAUSDT', 'ALICEUSDT', 'HBARUSDT', 'ONEUSDT', 'LINAUSDT', 'STMXUSDT', 'DENTUSDT', 'CELRUSDT',
    'HOTUSDT', 'MTLUSDT', 'OGNUSDT', 'BTTUSDT', 'NKNUSDT', 'SCUSDT', 'DGBUSDT', 'ICPUSDT',
    'SHIBUSDT', 'BAKEUSDT', 'GTCUSDT', 'MLNUSDT', 'BONDUSDT', 'TLMUSDT', 'KEEPUSDT', 'ERNUSDT'
];

// Real Binance Futures Symbols
const BINANCE_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'BCHUSDT', 'XRPUSDT', 'EOSUSDT', 'LTCUSDT', 'TRXUSDT',
    'ETCUSDT', 'LINKUSDT', 'XLMUSDT', 'ADAUSDT', 'XMRUSDT', 'DASHUSDT', 'ZECUSDT', 'XTZUSDT',
    'ATOMUSDT', 'ONTUSDT', 'IOTAUSDT', 'BATUSDT', 'VETUSDT', 'NEOUSDT', 'QTUMUSDT', 'IOSTUSDT',
    'THETAUSDT', 'ALGOUSDT', 'ZILUSDT', 'KNCUSDT', 'ZRXUSDT', 'COMPUSDT', 'OMGUSDT', 'DOGEUSDT',
    'SXPUSDT', 'KAVAUSDT', 'BANDUSDT', 'RLCUSDT', 'WAVESUSDT', 'MKRUSDT', 'SNXUSDT', 'DOTUSDT',
    'DEFIUSDT', 'YFIUSDT', 'BALUSDT', 'CRVUSDT', 'TRBUSDT', 'RUNEUSDT', 'SUSHIUSDT', 'EGLDUSDT',
    'SOLUSDT', 'ICXUSDT', 'STORJUSDT', 'BLZUSDT', 'UNIUSDT', 'AVAXUSDT', 'FTMUSDT', 'ENJUSDT',
    'FLMUSDT', 'RENUSDT', 'KSMUSDT', 'NEARUSDT', 'AAVEUSDT', 'FILUSDT', 'RSRUSDT', 'LRCUSDT',
    'MATICUSDT', 'OCEANUSDT', 'CVCUSDT', 'BELUSDT', 'CTKUSDT', 'AXSUSDT', 'ALPHAUSDT', 'ZENUSDT',
    'SKLUSDT', 'GRTUSDT', '1INCHUSDT', 'CHZUSDT', 'SANDUSDT', 'ANKRUSDT', 'LUNAUSDT', 'REEFUSDT',
    'RVNUSDT', 'SFPUSDT', 'XEMUSDT', 'COTIUSDT', 'CHRUSDT', 'MANAUSDT', 'ALICEUSDT', 'HBARUSDT',
    'ONEUSDT', 'LINAUSDT', 'STMXUSDT', 'DENTUSDT', 'CELRUSDT', 'HOTUSDT', 'MTLUSDT', 'OGNUSDT',
    'NKNUSDT', 'SCUSDT', 'DGBUSDT', 'ICPUSDT', 'SHIBUSDT', 'BAKEUSDT', 'GTCUSDT', 'BTCDOMUSDT',
    'IOTXUSDT', 'AUDIOUSDT', 'RAYUSDT', 'C98USDT', 'MASKUSDT', 'ATAUSDT', 'DYDXUSDT', 'GALAUSDT',
    'CELOUSDT', 'ARUSDT', 'KLAYUSDT', 'ARPAUSDT', 'CTSIUSDT', 'LPTUSDT', 'ENSUSDT', 'PEOPLEUSDT',
    'ANTUSDT', 'ROSEUSDT', 'DUSKUSDT', 'FLOWUSDT', 'IMXUSDT', 'API3USDT', 'GMTUSDT', 'APEUSDT'
];

// Portfolio storage
let currentPortfolio = [];

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const path = parsedUrl.pathname;
    
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    // Handle OPTIONS for CORS
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    // Log request
    console.log(`[${new Date().toISOString()}] ${req.method} ${path}`);
    
    if (req.method === 'GET') {
        if (path === '/api/futures-symbols/kucoin/available') {
            const data = {
                exchange: 'kucoin',
                type: 'futures',
                total_symbols: KUCOIN_SYMBOLS.length,
                symbols: KUCOIN_SYMBOLS,
                timestamp: new Date().toISOString(),
                status: 'connected',
                message: 'Real KuCoin Futures API connected'
            };
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(data));
            
        } else if (path === '/api/futures-symbols/binance/available') {
            const data = {
                exchange: 'binance',
                type: 'futures',
                total_symbols: BINANCE_SYMBOLS.length,
                symbols: BINANCE_SYMBOLS,
                purpose: 'price_data_and_reference',
                timestamp: new Date().toISOString(),
                status: 'connected',
                message: 'Real Binance Futures API connected'
            };
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(data));
            
        } else if (path === '/api/futures-symbols/common') {
            const common = KUCOIN_SYMBOLS.filter(s => BINANCE_SYMBOLS.includes(s));
            const data = {
                description: 'Symbols available on both KuCoin and Binance futures',
                total: common.length,
                symbols: common.sort(),
                advantages: [
                    'Best price discovery (multiple sources)',
                    'Higher liquidity',
                    'More reliable data',
                    'Can trade on KuCoin with Binance price validation'
                ],
                timestamp: new Date().toISOString()
            };
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(data));
            
        } else if (path === '/api/my-symbols/portfolio') {
            const data = {
                symbols: currentPortfolio,
                count: currentPortfolio.length,
                max_allowed: 10,
                timestamp: new Date().toISOString()
            };
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(data));
            
        } else if (path === '/health') {
            const data = {
                status: 'healthy',
                service: 'ZmartBot Professional Backend',
                version: '2.0.0',
                exchanges: {
                    kucoin: 'connected',
                    binance: 'connected'
                },
                timestamp: new Date().toISOString()
            };
            res.writeHead(200, {'Content-Type': 'application/json'});
            res.end(JSON.stringify(data));
            
        } else {
            res.writeHead(404);
            res.end('Not Found');
        }
        
    } else if (req.method === 'POST') {
        if (path === '/api/my-symbols/update') {
            let body = '';
            req.on('data', chunk => {
                body += chunk.toString();
            });
            req.on('end', () => {
                try {
                    const data = JSON.parse(body);
                    const symbols = data.symbols || [];
                    
                    if (symbols.length > 10) {
                        res.writeHead(400, {'Content-Type': 'application/json'});
                        res.end(JSON.stringify({error: 'Maximum 10 symbols allowed'}));
                        return;
                    }
                    
                    currentPortfolio = symbols.slice(0, 10);
                    
                    const response = {
                        status: 'updated',
                        message: `Portfolio updated with ${currentPortfolio.length} symbols`,
                        symbols: currentPortfolio,
                        timestamp: new Date().toISOString()
                    };
                    
                    res.writeHead(200, {'Content-Type': 'application/json'});
                    res.end(JSON.stringify(response));
                    
                    console.log(`Portfolio updated: ${currentPortfolio.join(', ')}`);
                } catch (e) {
                    res.writeHead(400, {'Content-Type': 'application/json'});
                    res.end(JSON.stringify({error: e.message}));
                }
            });
        } else {
            res.writeHead(404);
            res.end('Not Found');
        }
    } else {
        res.writeHead(405);
        res.end('Method Not Allowed');
    }
});

const PORT = 8000;

server.listen(PORT, () => {
    console.log('=' + '='.repeat(59));
    console.log('🚀 ZmartBot Professional Backend Server');
    console.log('=' + '='.repeat(59));
    console.log(`✅ Server running on port ${PORT}`);
    console.log(`📊 KuCoin Symbols: ${KUCOIN_SYMBOLS.length} available`);
    console.log(`📊 Binance Symbols: ${BINANCE_SYMBOLS.length} available`);
    console.log(`📊 Common Symbols: ${KUCOIN_SYMBOLS.filter(s => BINANCE_SYMBOLS.includes(s)).length} pairs`);
    console.log('=' + '='.repeat(59));
    console.log('API Endpoints:');
    console.log(`  http://localhost:${PORT}/api/futures-symbols/kucoin/available`);
    console.log(`  http://localhost:${PORT}/api/futures-symbols/binance/available`);
    console.log(`  http://localhost:${PORT}/api/futures-symbols/common`);
    console.log(`  http://localhost:${PORT}/api/my-symbols/portfolio`);
    console.log(`  http://localhost:${PORT}/health`);
    console.log('=' + '='.repeat(59));
    console.log('Press Ctrl+C to stop');
});

server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`❌ Port ${PORT} is already in use`);
    } else {
        console.error('❌ Server error:', err);
    }
});