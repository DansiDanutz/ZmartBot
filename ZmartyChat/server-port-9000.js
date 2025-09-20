// ZmartyChat Server - Port 9000
// This server handles the ZmartyUserApp functionality

import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import fetch from 'node-fetch';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 9000;

// Middleware
app.use(cors({
    origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:8000', 'http://localhost:9000'],
    credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from ZmartyUserApp directory
app.use('/app', express.static(path.join(__dirname, 'ZmartyUserApp')));
app.use(express.static(path.join(__dirname, 'ZmartyUserApp')));

// Serve the main ZmartyUserApp
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'ZmartyUserApp', 'index.html'));
});

// API Routes for ZmartyChat
app.get('/api/status', (req, res) => {
    res.json({
        status: 'online',
        service: 'ZmartyChat',
        port: PORT,
        timestamp: new Date().toISOString(),
        features: {
            userApp: 'active',
            chat: 'enabled',
            ai: 'connected',
            dashboard: 'available'
        }
    });
});

// User authentication endpoints (proxy to main API)
app.post('/api/auth/register', async (req, res) => {
    try {
        // Forward to main API on port 8000
        const response = await fetch('http://localhost:8000/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req.body)
        });

        const data = await response.json();
        res.status(response.status).json(data);
    } catch (error) {
        res.status(500).json({ error: 'Registration service unavailable' });
    }
});

app.post('/api/auth/login', async (req, res) => {
    try {
        // Forward to main API on port 8000
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(req.body)
        });

        const data = await response.json();
        res.status(response.status).json(data);
    } catch (error) {
        res.status(500).json({ error: 'Login service unavailable' });
    }
});

// Chat endpoints
app.get('/api/chat/history', (req, res) => {
    res.json({
        messages: [],
        user: req.query.userId || 'anonymous'
    });
});

app.post('/api/chat/send', (req, res) => {
    const { message, userId } = req.body;
    res.json({
        response: `Echo: ${message}`,
        timestamp: new Date().toISOString(),
        userId
    });
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        port: PORT
    });
});

// Serve ZmartyUserApp routes
app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'ZmartyUserApp', 'dashboard.html'));
});

app.get('/onboarding', (req, res) => {
    res.sendFile(path.join(__dirname, 'ZmartyUserApp', 'index.html'));
});

app.get('/reset-password', (req, res) => {
    res.sendFile(path.join(__dirname, 'ZmartyUserApp', 'reset-password.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: err.message
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not found',
        path: req.url
    });
});

// Start server
const server = app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════╗
║                                                    ║
║        ZmartyChat Server - Port ${PORT}              ║
║                                                    ║
║  Status: ✅ ONLINE                                 ║
║  URL: http://localhost:${PORT}                      ║
║                                                    ║
║  Features:                                         ║
║  • ZmartyUserApp Dashboard                        ║
║  • Chat Interface                                  ║
║  • Authentication Proxy                            ║
║  • API Integration                                 ║
║                                                    ║
║  Endpoints:                                        ║
║  • GET  /                 - Main App               ║
║  • GET  /dashboard        - User Dashboard         ║
║  • GET  /api/status       - Server Status          ║
║  • POST /api/auth/login   - User Login             ║
║  • POST /api/auth/register - User Registration     ║
║  • GET  /api/chat/history - Chat History           ║
║  • POST /api/chat/send    - Send Message           ║
║                                                    ║
╚════════════════════════════════════════════════════╝
    `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM signal received: closing HTTP server');
    server.close(() => {
        console.log('HTTP server closed');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('\nSIGINT signal received: closing HTTP server');
    server.close(() => {
        console.log('HTTP server closed');
        process.exit(0);
    });
});

export default app;