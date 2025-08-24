#!/usr/bin/env node
/**
 * Simple Node.js server for the Professional Dashboard
 * Handles static files and Binance API proxy
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const https = require('https');

const PORT = 3400;

// MIME types for different file extensions
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'application/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

// Proxy Binance API request
function proxyBinanceRequest(endpoint, params, res) {
    const binanceUrl = `https://api.binance.com${endpoint}?${new URLSearchParams(params)}`;
    
    https.get(binanceUrl, (binanceRes) => {
        let data = '';
        
        binanceRes.on('data', (chunk) => {
            data += chunk;
        });
        
        binanceRes.on('end', () => {
            res.writeHead(200, {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            });
            res.end(data);
        });
    }).on('error', (err) => {
        console.error('Binance API error:', err);
        
        // Send mock data on error
        const mockData = endpoint.includes('ticker') 
            ? JSON.stringify({
                symbol: params.symbol || 'BTCUSDT',
                lastPrice: '67890.12',
                priceChange: '1234.56',
                priceChangePercent: '2.50',
                volume: '1234567890'
            })
            : JSON.stringify([]); // Mock klines
            
        res.writeHead(200, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        });
        res.end(mockData);
    });
}

// Create server
const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    let pathname = parsedUrl.pathname;
    
    // Handle API proxy endpoints
    if (pathname === '/api/binance/ticker/24hr') {
        const symbol = parsedUrl.query.symbol || 'BTCUSDT';
        proxyBinanceRequest('/api/v3/ticker/24hr', { symbol }, res);
        return;
    }
    
    if (pathname === '/api/binance/klines') {
        const { symbol = 'BTCUSDT', interval = '1h', limit = '24' } = parsedUrl.query;
        proxyBinanceRequest('/api/v3/klines', { symbol, interval, limit }, res);
        return;
    }
    
    // Handle health check
    if (pathname === '/health') {
        res.writeHead(200, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        });
        res.end(JSON.stringify({
            status: 'healthy',
            service: 'node-dashboard-server',
            port: PORT
        }));
        return;
    }
    
    // Serve index.html for root path
    if (pathname === '/') {
        pathname = '/index.html';
    }
    
    // Construct file path
    let filePath = path.join(__dirname, pathname);
    
    // Security check - prevent directory traversal
    if (!filePath.startsWith(__dirname)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }
    
    // Check if file exists
    fs.stat(filePath, (err, stats) => {
        if (err) {
            res.writeHead(404);
            res.end('Not Found');
            return;
        }
        
        // If it's a directory, serve index.html
        if (stats.isDirectory()) {
            filePath = path.join(filePath, 'index.html');
        }
        
        // Read and serve the file
        fs.readFile(filePath, (err, data) => {
            if (err) {
                res.writeHead(500);
                res.end('Internal Server Error');
                return;
            }
            
            // Get MIME type
            const ext = path.extname(filePath);
            const mimeType = mimeTypes[ext] || 'application/octet-stream';
            
            // Send response
            res.writeHead(200, {
                'Content-Type': mimeType,
                'Access-Control-Allow-Origin': '*'
            });
            res.end(data);
        });
    });
});

// Start server
server.listen(PORT, () => {
    console.log('=' + '='.repeat(59));
    console.log('🚀 ZmartBot Professional Dashboard Server (Node.js)');
    console.log('=' + '='.repeat(59));
    console.log(`📁 Serving from: ${__dirname}`);
    console.log(`🌐 Server URL: http://localhost:${PORT}/`);
    console.log(`🏥 Health check: http://localhost:${PORT}/health`);
    console.log('=' + '='.repeat(59));
    console.log('✅ Binance API proxy endpoints:');
    console.log('  - /api/binance/ticker/24hr');
    console.log('  - /api/binance/klines');
    console.log('=' + '='.repeat(59));
});

// Handle server errors
server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`❌ Port ${PORT} is already in use`);
        console.log('Try stopping the existing server or use a different port');
    } else {
        console.error('❌ Server error:', err);
    }
    process.exit(1);
});