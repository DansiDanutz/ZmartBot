const express = require('express');
const WebSocket = require('ws');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const winston = require('winston');
const FreeDataAggregator = require('./lib/FreeDataAggregator');

// Setup logging
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.printf(({ timestamp, level, message }) => {
            return `${timestamp} [${level.toUpperCase()}]: ${message}`;
        })
    ),
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: 'logs/server.log' })
    ]
});

// ZmartBot PortManager Integration
class CryptoChartsService {
    constructor() {
        this.name = "crypto_charts_free";
        this.type = "frontend";
        this.port = null;
        this.wsPort = null;
        this.dataAggregator = new FreeDataAggregator();
        this.app = express();
        this.wss = null;
        this.clients = new Set();
        
        this.setupExpress();
    }

    setupExpress() {
        // Security and performance middleware
        this.app.use(helmet({
            contentSecurityPolicy: {
                directives: {
                    defaultSrc: ["'self'"],
                    styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
                    fontSrc: ["'self'", "https://fonts.gstatic.com"],
                    scriptSrc: ["'self'", "'unsafe-inline'", "https://unpkg.com"],
                    connectSrc: ["'self'", "ws:", "wss:"],
                }
            }
        }));
        
        this.app.use(compression());
        this.app.use(cors());
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.static(path.join(__dirname, 'public')));

        this.setupRoutes();
    }

    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                service: this.name,
                port: this.port,
                websocket: this.wsPort,
                timestamp: new Date().toISOString(),
                apiUsage: this.dataAggregator.getAPIUsageStats(),
                apiKeys: {
                    coingecko: this.dataAggregator.apiKeys.coingecko ? '✅ Loaded' : '❌ Not loaded',
                    cryptometer: '✅ Loaded'
                }
            });
        });

        // Get supported symbols
        this.app.get('/api/symbols', (req, res) => {
            try {
                const symbols = this.dataAggregator.getSupportedSymbols();
                res.json({
                    success: true,
                    data: symbols,
                    count: symbols.length
                });
            } catch (error) {
                logger.error(`Error getting symbols: ${error.message}`);
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Get current prices
        this.app.get('/api/prices', async (req, res) => {
            try {
                const { symbol } = req.query;
                if (!symbol) {
                    return res.status(400).json({ success: false, error: 'Symbol parameter required' });
                }

                const price = await this.dataAggregator.getCurrentPrice(symbol);
                res.json({
                    success: true,
                    data: {
                        symbol: symbol.toUpperCase(),
                        price: price,
                        timestamp: new Date().toISOString()
                    }
                });
            } catch (error) {
                logger.error(`Error getting price for ${req.query.symbol}: ${error.message}`);
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Get historical data
        this.app.get('/api/history', async (req, res) => {
            try {
                const { symbol, interval = '1d', limit = 100 } = req.query;
                if (!symbol) {
                    return res.status(400).json({ success: false, error: 'Symbol parameter required' });
                }

                const history = await this.dataAggregator.getHistoricalData(symbol, interval, parseInt(limit));
                res.json({
                    success: true,
                    data: history,
                    count: history.length
                });
            } catch (error) {
                logger.error(`Error getting history for ${req.query.symbol}: ${error.message}`);
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // Get market overview
        this.app.get('/api/market-overview', async (req, res) => {
            try {
                const overview = await this.dataAggregator.getMarketOverview();
                res.json({
                    success: true,
                    data: overview
                });
            } catch (error) {
                logger.error(`Error getting market overview: ${error.message}`);
                res.status(500).json({ success: false, error: error.message });
            }
        });

        // WebSocket endpoint for real-time data
        this.app.get('/ws', (req, res) => {
            res.json({
                success: true,
                message: 'WebSocket endpoint available at /ws',
                port: this.wsPort
            });
        });
    }

    setupWebSocket() {
        if (!this.wsPort) {
            this.wsPort = this.port + 1;
        }

        this.wss = new WebSocket.Server({ port: this.wsPort });

        this.wss.on('connection', (ws) => {
            logger.info('New WebSocket client connected');
            this.clients.add(ws);

            ws.on('message', (message) => {
                try {
                    const data = JSON.parse(message);
                    this.handleWebSocketMessage(ws, data);
                } catch (error) {
                    logger.error(`WebSocket message error: ${error.message}`);
                }
            });

            ws.on('close', () => {
                logger.info('WebSocket client disconnected');
                this.clients.delete(ws);
            });
        });

        logger.info(`WebSocket server started on port ${this.wsPort}`);
    }

    handleWebSocketMessage(ws, data) {
        switch (data.type) {
            case 'subscribe':
                this.handleSubscription(ws, data);
                break;
            case 'unsubscribe':
                this.handleUnsubscription(ws, data);
                break;
            default:
                ws.send(JSON.stringify({
                    type: 'error',
                    message: 'Unknown message type'
                }));
        }
    }

    handleSubscription(ws, data) {
        const { symbol, interval } = data;
        if (!symbol) {
            ws.send(JSON.stringify({
                type: 'error',
                message: 'Symbol required for subscription'
            }));
            return;
        }

        // Store subscription info
        ws.subscriptions = ws.subscriptions || new Set();
        ws.subscriptions.add(`${symbol}:${interval || '1m'}`);

        ws.send(JSON.stringify({
            type: 'subscribed',
            symbol: symbol,
            interval: interval || '1m'
        }));

        logger.info(`Client subscribed to ${symbol}:${interval || '1m'}`);
    }

    handleUnsubscription(ws, data) {
        const { symbol, interval } = data;
        if (ws.subscriptions) {
            ws.subscriptions.delete(`${symbol}:${interval || '1m'}`);
        }

        ws.send(JSON.stringify({
            type: 'unsubscribed',
            symbol: symbol,
            interval: interval || '1m'
        }));

        logger.info(`Client unsubscribed from ${symbol}:${interval || '1m'}`);
    }

    broadcastToSubscribers(symbol, interval, data) {
        this.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN && 
                client.subscriptions && 
                client.subscriptions.has(`${symbol}:${interval}`)) {
                client.send(JSON.stringify({
                    type: 'price_update',
                    symbol: symbol,
                    interval: interval,
                    data: data,
                    timestamp: new Date().toISOString()
                }));
            }
        });
    }

    async start(port = 0) {
        try {
            // Get port from PortManager or use default
            this.port = port || 3001;
            
            // Start Express server
            await new Promise((resolve, reject) => {
                this.app.listen(this.port, (err) => {
                    if (err) reject(err);
                    else resolve();
                });
            });

            // Start WebSocket server
            this.setupWebSocket();

            logger.info(`CryptoCharts service started on port ${this.port}`);
            logger.info(`WebSocket server running on port ${this.wsPort}`);
            logger.info(`Health check available at http://localhost:${this.port}/health`);

            // Start data broadcasting
            this.startDataBroadcasting();

        } catch (error) {
            logger.error(`Failed to start CryptoCharts service: ${error.message}`);
            throw error;
        }
    }

    startDataBroadcasting() {
        // Broadcast price updates every 30 seconds
        setInterval(async () => {
            try {
                const symbols = this.dataAggregator.getSupportedSymbols();
                for (const symbol of symbols.slice(0, 10)) { // Limit to top 10 symbols
                    const price = await this.dataAggregator.getCurrentPrice(symbol);
                    this.broadcastToSubscribers(symbol, '1m', { price });
                }
            } catch (error) {
                logger.error(`Error in data broadcasting: ${error.message}`);
            }
        }, 30000);
    }

    stop() {
        if (this.wss) {
            this.wss.close();
        }
        logger.info('CryptoCharts service stopped');
    }
}

// Start service if run directly
if (require.main === module) {
    const service = new CryptoChartsService();
    const port = process.env.PORT || 3001;
    
    service.start(port).catch(error => {
        logger.error(`Service startup failed: ${error.message}`);
        process.exit(1);
    });

    // Graceful shutdown
    process.on('SIGINT', () => {
        logger.info('Received SIGINT, shutting down gracefully');
        service.stop();
        process.exit(0);
    });

    process.on('SIGTERM', () => {
        logger.info('Received SIGTERM, shutting down gracefully');
        service.stop();
        process.exit(0);
    });
}

module.exports = CryptoChartsService;
