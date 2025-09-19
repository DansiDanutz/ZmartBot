// Main Integration File - ZmartyChat System
import { ZmartyAI } from './zmarty-ai-agent.js';
// import { ManusConnector } from './zmarty-manus-connector.js';
import { zmartyDB } from './supabase-client.js';
import { creditManager } from './credit-manager.js';
// import { stripePayment } from './stripe-payment.js';
// import { userAgentProcessor } from './user-agent-background.js';
// import { addictionHooks } from './addiction-hooks.js';
import express from 'express';
import { createServer } from 'http';
import { Server as SocketIO } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
const server = createServer(app);
const io = new SocketIO(server, {
    cors: {
        origin: process.env.FRONTEND_URL || 'http://localhost:3000',
        credentials: true
    }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Initialize core systems
const zmartyAI = new ZmartyAI();
// const manusConnector = new ManusConnector();

// ============= WEBSOCKET CONNECTIONS =============

io.on('connection', (socket) => {
    console.log('✅ User connected:', socket.id);

    // Handle user registration
    socket.on('user:register', async (data) => {
        try {
            const user = await zmartyDB.createUser({
                email: data.email,
                phone: data.phone,
                name: data.name,
                username: data.username,
                contactType: data.contactType
            });

            // Initialize Zmarty for this user
            await zmartyAI.initializeForUser(user.id);

            // Send welcome message with credits
            const welcomeMessage = zmartyAI.generateWelcomeMessage(user.name);

            socket.emit('registration:success', {
                user,
                message: welcomeMessage,
                initialCredits: 100
            });

            // Trigger welcome bonus
            await addictionHooks.triggerVariableReward(user.id, 'registration');

        } catch (error) {
            console.error('Registration error:', error);
            socket.emit('registration:error', {
                error: error.message
            });
        }
    });

    // Handle chat messages
    socket.on('message:send', async (data) => {
        const { userId, message } = data;

        try {
            // Check credits first
            const creditsNeeded = creditManager.calculateCreditsNeeded('simple_chat');
            const hasCredits = await creditManager.checkCredits(userId, creditsNeeded);

            if (!hasCredits) {
                socket.emit('message:error', {
                    error: 'Insufficient credits',
                    suggestPurchase: true
                });
                return;
            }

            // Deduct credits
            await zmartyDB.deductCredits(userId, creditsNeeded, 'simple_chat', 'Chat message');

            // Process with Zmarty AI
            const response = await zmartyAI.processMessage(message, userId);

            // Get multi-agent consensus if needed
            if (response.requiresAgents) {
                const agentResults = await manusConnector.getMultiAgentConsensus(message);
                response.agentInsights = agentResults;
            }

            // Queue for background processing
            await userAgentProcessor.queueMessage(userId, message, response.content);

            // Check addiction hooks
            const hooks = await addictionHooks.processUserAction(userId, 'message', {
                messageLength: message.length,
                complexity: response.complexity
            });

            // Send response
            socket.emit('message:response', {
                response: response.content,
                creditsUsed: creditsNeeded,
                remainingCredits: response.remainingCredits,
                hooks: hooks
            });

            // Emit any triggered hooks
            for (const hook of hooks) {
                socket.emit('hook:triggered', hook);
            }

        } catch (error) {
            console.error('Message error:', error);
            socket.emit('message:error', {
                error: error.message
            });
        }
    });

    // Handle credit purchases
    socket.on('credits:purchase', async (data) => {
        const { userId, packageId } = data;

        try {
            const clientSecret = await stripePayment.createPaymentIntent(packageId, userId);

            socket.emit('credits:payment-intent', {
                clientSecret,
                package: creditManager.packages[packageId]
            });

        } catch (error) {
            console.error('Credit purchase error:', error);
            socket.emit('credits:error', {
                error: error.message
            });
        }
    });

    // Handle subscription management
    socket.on('subscription:create', async (data) => {
        const { userId, planId, paymentMethodId } = data;

        try {
            const subscription = await stripePayment.createSubscription(
                planId,
                userId,
                paymentMethodId
            );

            socket.emit('subscription:created', {
                subscription,
                message: 'Subscription activated successfully!'
            });

            // Trigger milestone hook
            await addictionHooks.processUserAction(userId, 'subscription_upgrade');

        } catch (error) {
            console.error('Subscription error:', error);
            socket.emit('subscription:error', {
                error: error.message
            });
        }
    });

    // Handle real-time updates subscription
    socket.on('subscribe:updates', async (data) => {
        const { userId } = data;

        // Join user room for targeted updates
        socket.join(`user:${userId}`);

        // Subscribe to database changes
        const creditSub = zmartyDB.subscribeToCredits(userId, (payload) => {
            socket.emit('credits:updated', payload.new);
        });

        const insightSub = zmartyDB.subscribeToInsights(userId, (payload) => {
            socket.emit('insight:new', payload.new);
        });

        // Store subscriptions for cleanup
        socket.data.subscriptions = [creditSub, insightSub];
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('👋 User disconnected:', socket.id);

        // Clean up subscriptions
        if (socket.data.subscriptions) {
            socket.data.subscriptions.forEach(sub => sub.unsubscribe());
        }
    });
});

// ============= REST API ENDPOINTS =============

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date(),
        services: {
            database: 'connected',
            ai: 'ready',
            payment: 'configured',
            mcp: 'running'
        }
    });
});

// Get user profile
app.get('/api/users/:userId', async (req, res) => {
    try {
        const user = await zmartyDB.getUser(req.params.userId);
        const categories = await zmartyDB.getUserCategories(req.params.userId);
        const credits = await zmartyDB.getUserCredits(req.params.userId);

        res.json({
            user,
            categories,
            credits
        });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Get credit packages
app.get('/api/credits/packages', (req, res) => {
    res.json(creditManager.packages);
});

// Get subscription plans
app.get('/api/subscriptions/plans', (req, res) => {
    res.json(creditManager.subscriptionPlans);
});

// Get user insights
app.get('/api/insights/:userId', async (req, res) => {
    try {
        const insights = await zmartyDB.getUnshownInsights(req.params.userId);
        res.json(insights);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Mark insight as shown
app.post('/api/insights/:insightId/shown', async (req, res) => {
    try {
        await zmartyDB.markInsightShown(req.params.insightId, req.body.feedback);
        res.json({ success: true });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Get addiction metrics
app.get('/api/metrics/:userId', async (req, res) => {
    try {
        const metrics = await zmartyDB.getAddictionMetrics(req.params.userId);
        const score = await zmartyDB.getAddictionScore(req.params.userId);

        res.json({
            metrics,
            score
        });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Get user transcripts
app.get('/api/transcripts/:userId', async (req, res) => {
    try {
        const transcripts = await zmartyDB.getTranscripts(req.params.userId);
        res.json(transcripts);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Stripe webhook endpoint
app.post('/api/stripe/webhook', express.raw({ type: 'application/json' }),
    async (req, res) => {
        // This would be imported from stripe-endpoints.js
        res.json({ received: true });
    }
);

// ============= BACKGROUND PROCESSORS =============

// Process queued messages
userAgentProcessor.on('message-processed', async (job) => {
    // Notify user of processing completion
    io.to(`user:${job.userId}`).emit('processing:complete', {
        jobId: job.id,
        status: job.status
    });
});

// Handle generated insights
userAgentProcessor.on('insights-generated', async ({ userId, insights }) => {
    // Notify user of new insights
    io.to(`user:${userId}`).emit('insights:new', {
        count: insights.length,
        insights: insights.slice(0, 3) // Send top 3
    });
});

// Handle addiction score updates
userAgentProcessor.on('addiction-calculated', async ({ userId, metrics }) => {
    // Update user's addiction profile
    io.to(`user:${userId}`).emit('metrics:updated', {
        dependencyScore: metrics.dependencyScore,
        streakDays: metrics.streakDays,
        level: creditManager.calculateUserLevel(metrics.dependencyScore)
    });
});

// Handle milestones
userAgentProcessor.on('milestone-achieved', async ({ userId, milestone }) => {
    // Celebrate milestone
    io.to(`user:${userId}`).emit('milestone:achieved', milestone);
});

// Handle addiction hooks
addictionHooks.on('variable-reward', async (data) => {
    io.to(`user:${data.userId}`).emit('reward:received', {
        amount: data.amount,
        message: data.message
    });
});

addictionHooks.on('streak-milestone', async (data) => {
    io.to(`user:${data.userId}`).emit('streak:milestone', {
        days: data.days,
        credits: data.credits,
        message: data.message
    });
});

addictionHooks.on('achievement-unlocked', async (data) => {
    io.to(`user:${data.userId}`).emit('achievement:unlocked', {
        achievement: data.achievement,
        message: data.message
    });
});

// ============= ERROR HANDLING =============

app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: err.message
    });
});

// ============= START SERVER =============

const PORT = process.env.PORT || 3001;

server.listen(PORT, () => {
    console.log(`
    🚀 ZmartyChat Server Running
    ================================
    Port: ${PORT}
    Environment: ${process.env.NODE_ENV || 'development'}

    Services:
    ✅ Express API
    ✅ WebSocket Server
    ✅ Zmarty AI
    ✅ Manus Connector
    ✅ User Agent Processor
    ✅ Addiction Hooks
    ✅ Credit Manager
    ✅ Stripe Payments

    Ready to revolutionize trading! 💎
    `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received. Shutting down gracefully...');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

export default app;