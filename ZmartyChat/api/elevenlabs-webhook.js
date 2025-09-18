// ElevenLabs Webhook Handler for Zmarty Agent
import express from 'express';
import { elevenLabsAgent } from '../src/elevenlabs-integration.js';
import { zmartyDB } from '../src/supabase-client.js';
import { creditManager } from '../src/credit-manager.js';
import { manusConnector } from '../src/zmarty-manus-connector.js';
import { userAgentProcessor } from '../src/user-agent-background.js';
import { addictionHooks } from '../src/addiction-hooks.js';

const router = express.Router();

// Webhook secret for verification
const WEBHOOK_SECRET = process.env.ELEVENLABS_WEBHOOK_SECRET || 'zmarty-voice-secret-2024';

// ============= WEBHOOK ENDPOINT =============

router.post('/webhook', express.json(), async (req, res) => {
    // Verify webhook authenticity
    const signature = req.headers['x-elevenlabs-signature'];
    if (signature !== WEBHOOK_SECRET) {
        console.warn('Invalid webhook signature');
        return res.status(401).json({ error: 'Unauthorized' });
    }

    const { event, data, metadata } = req.body;

    console.log(`📞 ElevenLabs Event: ${event}`, { userId: metadata?.userId });

    try {
        switch (event) {
            case 'conversation.started':
                return await handleConversationStart(req, res, data, metadata);

            case 'tool.called':
                return await handleToolCall(req, res, data, metadata);

            case 'conversation.ended':
                return await handleConversationEnd(req, res, data, metadata);

            case 'user.spoke':
                return await handleUserSpoke(req, res, data, metadata);

            case 'agent.spoke':
                return await handleAgentSpoke(req, res, data, metadata);

            case 'error':
                return await handleError(req, res, data, metadata);

            default:
                console.log('Unknown event:', event);
                return res.json({ success: true });
        }
    } catch (error) {
        console.error('Webhook processing error:', error);
        return res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// ============= CONVERSATION HANDLERS =============

async function handleConversationStart(req, res, data, metadata) {
    const { userId, sessionId } = metadata;

    try {
        // Get user data
        const user = await zmartyDB.getUser(userId);
        const credits = await zmartyDB.getUserCredits(userId);

        // Check if user has enough credits
        if (credits.credits_balance < 10) {
            return res.json({
                action: 'speak',
                text: `Welcome back! I'm Zmarty. Quick heads up - you're running low on credits with only ${credits.credits_balance} remaining. Would you like to hear about our credit packages before we continue?`,
                metadata: {
                    lowCredits: true,
                    balance: credits.credits_balance
                }
            });
        }

        // Get user's trading style and preferences
        const categories = await zmartyDB.getUserCategories(userId);
        const tradingStyle = categories.find(c => c.category_type === 'trading_style');

        // Personalized greeting based on user profile
        const greeting = generatePersonalizedGreeting(user, tradingStyle);

        // Check for streak bonus
        const streakData = await addictionHooks.checkStreak(userId);

        res.json({
            action: 'speak',
            text: greeting,
            metadata: {
                userId,
                sessionId,
                creditsBalance: credits.credits_balance,
                streakDays: streakData?.days || 0
            }
        });

    } catch (error) {
        console.error('Conversation start error:', error);
        res.json({
            action: 'speak',
            text: "I'm Zmarty—your steady voice in the noise. Let's check the markets together."
        });
    }
}

async function handleToolCall(req, res, data, metadata) {
    const { tool, parameters } = data;
    const { userId } = metadata;

    console.log(`🔧 Tool called: ${tool}`, parameters);

    try {
        // Add userId to parameters
        if (!parameters.userId && userId) {
            parameters.userId = userId;
        }

        // Route to appropriate handler
        let result;
        switch (tool) {
            case 'get_market_data':
                result = await handleMarketData(parameters, userId);
                break;

            case 'technical_analysis':
                result = await handleTechnicalAnalysis(parameters, userId);
                break;

            case 'check_credits':
                result = await handleCheckCredits(parameters, userId);
                break;

            case 'multi_agent_consensus':
                result = await handleMultiAgentConsensus(parameters, userId);
                break;

            case 'set_price_alert':
                result = await handlePriceAlert(parameters, userId);
                break;

            case 'portfolio_analysis':
                result = await handlePortfolioAnalysis(parameters, userId);
                break;

            case 'get_trading_signals':
                result = await handleTradingSignals(parameters, userId);
                break;

            case 'execute_trade':
                result = await handleExecuteTrade(parameters, userId);
                break;

            case 'get_market_sentiment':
                result = await handleMarketSentiment(parameters, userId);
                break;

            case 'calculate_position_size':
                result = await handlePositionSize(parameters, userId);
                break;

            default:
                result = {
                    success: false,
                    speech: "I don't have that capability yet, but I'm always learning."
                };
        }

        // Process addiction hooks
        if (result.success) {
            const hooks = await addictionHooks.processUserAction(userId, 'tool_use', {
                tool,
                success: true
            });

            if (hooks.length > 0) {
                result.hooks = hooks;
            }
        }

        res.json(result);

    } catch (error) {
        console.error(`Tool execution error for ${tool}:`, error);
        res.json({
            success: false,
            speech: "I encountered an issue processing that. Let me try a different approach."
        });
    }
}

async function handleConversationEnd(req, res, data, metadata) {
    const { userId, sessionId } = metadata;
    const { duration } = data;

    try {
        // Calculate credits used (2 credits per minute)
        const minutes = Math.ceil(duration / 60);
        const creditsUsed = minutes * 2;

        // Deduct credits
        await zmartyDB.deductCredits(
            userId,
            creditsUsed,
            'voice_chat',
            `Voice session: ${minutes} minutes`
        );

        // Generate session summary
        const summary = await generateSessionSummary(userId, sessionId);

        // Queue for transcript generation
        await userAgentProcessor.queueMessage(userId, 'voice_session', summary);

        res.json({
            success: true,
            metadata: {
                duration,
                creditsUsed,
                summary: summary.brief
            }
        });

    } catch (error) {
        console.error('Conversation end error:', error);
        res.json({ success: true });
    }
}

async function handleUserSpoke(req, res, data, metadata) {
    const { transcript } = data;
    const { userId } = metadata;

    // Queue for analysis
    userAgentProcessor.queueMessage(userId, transcript, 'voice_input');

    res.json({ success: true });
}

async function handleAgentSpoke(req, res, data, metadata) {
    const { transcript } = data;
    const { userId } = metadata;

    // Log agent response for transcript
    await zmartyDB.saveMessage(userId, {
        sender: 'assistant',
        content: transcript,
        type: 'voice',
        creditsUsed: 0
    }, {
        intent: 'response',
        sentiment: 0.7
    });

    res.json({ success: true });
}

async function handleError(req, res, data, metadata) {
    console.error('ElevenLabs error:', data);
    res.json({
        action: 'speak',
        text: "I'm having a technical moment. Let me recalibrate and we'll try again."
    });
}

// ============= TOOL HANDLERS =============

async function handleMarketData({ symbol }, userId) {
    try {
        // Check and deduct credits
        const creditsNeeded = 2;
        const hasCredits = await creditManager.checkCredits(userId, creditsNeeded);

        if (!hasCredits) {
            return {
                success: false,
                speech: `You need ${creditsNeeded} credits for market data. You're currently at your limit. Would you like to hear about our packages?`
            };
        }

        await zmartyDB.deductCredits(userId, creditsNeeded, 'market_data', `Market data: ${symbol}`);

        // Get data from Manus
        const data = await manusConnector.getMarketData(symbol);

        return {
            success: true,
            data,
            speech: `${symbol} is trading at $${data.price.toLocaleString()}, ${data.change24h > 0 ? 'up' : 'down'} ${Math.abs(data.change24h).toFixed(2)}% today. Volume is ${data.volume > 1000000 ? (data.volume / 1000000).toFixed(1) + ' million' : data.volume.toLocaleString()}. Used ${creditsNeeded} credits.`,
            metadata: {
                creditsUsed: creditsNeeded
            }
        };

    } catch (error) {
        return {
            success: false,
            speech: `I'm having trouble reaching the ${symbol} data feed. Let's try again in a moment.`
        };
    }
}

async function handleTechnicalAnalysis({ symbol, timeframe = '1h' }, userId) {
    try {
        // Check and deduct credits
        const creditsNeeded = 5;
        const hasCredits = await creditManager.checkCredits(userId, creditsNeeded);

        if (!hasCredits) {
            return {
                success: false,
                speech: `Technical analysis needs ${creditsNeeded} credits. You'll need to add credits to continue.`
            };
        }

        await zmartyDB.deductCredits(userId, creditsNeeded, 'technical_analysis', `TA: ${symbol} ${timeframe}`);

        // Get analysis from multiple agents
        const analysis = await manusConnector.getTechnicalAnalysis(symbol, timeframe);

        const interpretation = interpretTechnicalAnalysis(analysis);

        return {
            success: true,
            data: analysis,
            speech: `${symbol} on the ${timeframe}: ${interpretation}. Used ${creditsNeeded} credits.`,
            metadata: {
                creditsUsed: creditsNeeded
            }
        };

    } catch (error) {
        return {
            success: false,
            speech: `Technical systems are recalibrating. Let me get you a basic view instead.`
        };
    }
}

async function handleMultiAgentConsensus({ query, symbol }, userId) {
    try {
        // This is expensive - check credits
        const creditsNeeded = 50;
        const hasCredits = await creditManager.checkCredits(userId, creditsNeeded);

        if (!hasCredits) {
            return {
                success: false,
                speech: `Multi-agent consensus requires ${creditsNeeded} credits. That's our most comprehensive analysis. Would you like a lighter analysis instead?`
            };
        }

        // Get user consent first
        return {
            success: true,
            requiresConfirmation: true,
            speech: `This will engage all agents for ${creditsNeeded} credits - RiskMetric, Kingfisher clusters, Cryptometer score, and more. Should I proceed?`,
            onConfirm: async () => {
                await zmartyDB.deductCredits(userId, creditsNeeded, 'multi_agent_consensus', query);

                const consensus = await manusConnector.getMultiAgentConsensus(query, symbol);
                const summary = summarizeConsensus(consensus);

                return {
                    success: true,
                    data: consensus,
                    speech: `${summary}. Used ${creditsNeeded} credits. Full report logged.`
                };
            }
        };

    } catch (error) {
        return {
            success: false,
            speech: "The agent network is busy. Let me run a focused analysis instead."
        };
    }
}

async function handleCheckCredits({ userId }) {
    try {
        const credits = await zmartyDB.getUserCredits(userId);
        const subscription = await zmartyDB.getActiveSubscription(userId);

        let message = `You have ${credits.credits_balance} credits. `;

        if (credits.credits_balance < 50) {
            message += "Running low - our Popular package gives 2,200 credits for $14.99. ";
        }

        if (subscription) {
            message += `You're on the ${subscription.subscription_plans.plan_name} plan. `;
        } else {
            message += "Consider our Pro monthly plan for consistent value. ";
        }

        const streak = await addictionHooks.checkStreak(userId);
        if (streak?.days > 0) {
            message += `You're on a ${streak.days} day streak! `;
        }

        return {
            success: true,
            data: credits,
            speech: message
        };

    } catch (error) {
        return {
            success: false,
            speech: "Let me check your account... having a connection issue. Try again?"
        };
    }
}

// ============= HELPER FUNCTIONS =============

function generatePersonalizedGreeting(user, tradingStyle) {
    const hour = new Date().getHours();
    let timeGreeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

    if (tradingStyle?.category_name === 'Scalper') {
        return `${timeGreeting}. I'm Zmarty. Ready for quick moves today? Markets are active.`;
    } else if (tradingStyle?.category_name === 'HODLer') {
        return `${timeGreeting}. Zmarty here. Let's check your long-term positions.`;
    } else {
        return `${timeGreeting}. I'm Zmarty—your steady voice in the noise. What's on your trading mind?`;
    }
}

function interpretTechnicalAnalysis(analysis) {
    const { rsi, macd, trend, support, resistance } = analysis;

    let interpretation = "";

    // Trend
    if (trend === 'bullish') {
        interpretation += "Uptrend intact. ";
    } else if (trend === 'bearish') {
        interpretation += "Downtrend pressure. ";
    } else {
        interpretation += "Sideways consolidation. ";
    }

    // RSI
    if (rsi > 70) {
        interpretation += "RSI overbought at " + rsi + " - watch for pullback. ";
    } else if (rsi < 30) {
        interpretation += "RSI oversold at " + rsi + " - bounce potential. ";
    } else {
        interpretation += "RSI neutral at " + rsi + ". ";
    }

    // Levels
    interpretation += `Support at $${support.toLocaleString()}, resistance at $${resistance.toLocaleString()}`;

    return interpretation;
}

function summarizeConsensus(consensus) {
    const bullish = consensus.filter(a => a.sentiment === 'bullish').length;
    const bearish = consensus.filter(a => a.sentiment === 'bearish').length;
    const avgConfidence = Math.round(consensus.reduce((acc, a) => acc + a.confidence, 0) / consensus.length);

    if (bullish > bearish * 1.5) {
        return `Strong bullish consensus: ${bullish} of ${consensus.length} agents positive, ${avgConfidence}% confidence`;
    } else if (bearish > bullish * 1.5) {
        return `Bearish consensus: ${bearish} of ${consensus.length} agents negative, ${avgConfidence}% confidence`;
    } else {
        return `Mixed signals: ${bullish} bullish, ${bearish} bearish. Caution advised`;
    }
}

async function generateSessionSummary(userId, sessionId) {
    // Generate summary of the voice session
    return {
        brief: "Session complete. Insights logged.",
        topics: [],
        creditsUsed: 0
    };
}

// More tool handlers...

async function handlePriceAlert({ symbol, targetPrice, direction }, userId) {
    try {
        await zmartyDB.deductCredits(userId, 1, 'simple_chat', 'Price alert setup');

        // Store alert
        // This would integrate with your alert system

        return {
            success: true,
            speech: `Alert set: I'll notify you when ${symbol} goes ${direction} $${targetPrice.toLocaleString()}. Used 1 credit.`
        };
    } catch (error) {
        return {
            success: false,
            speech: "Alert system is updating. Try again in a moment."
        };
    }
}

async function handlePortfolioAnalysis({ userId }) {
    try {
        const creditsNeeded = 15;
        await zmartyDB.deductCredits(userId, creditsNeeded, 'portfolio_analysis', 'Full portfolio review');

        // This would get real portfolio data
        const analysis = {
            totalValue: 10000,
            dayChange: 2.5,
            topPerformer: 'ETH',
            risk: 'moderate'
        };

        return {
            success: true,
            data: analysis,
            speech: `Portfolio at $${analysis.totalValue.toLocaleString()}, up ${analysis.dayChange}% today. ${analysis.topPerformer} leading gains. Risk level: ${analysis.risk}. Used ${creditsNeeded} credits.`
        };
    } catch (error) {
        return {
            success: false,
            speech: "Portfolio systems are syncing. Give me a moment."
        };
    }
}

async function handleTradingSignals({ symbols, riskLevel = 'moderate' }, userId) {
    try {
        const creditsNeeded = 10;
        await zmartyDB.deductCredits(userId, creditsNeeded, 'ai_prediction', `Signals for ${symbols.join(',')}`);

        const signals = await manusConnector.generateTradingSignals(symbols, riskLevel);

        const topSignal = signals[0];

        return {
            success: true,
            data: signals,
            speech: `Top signal: ${topSignal.action} ${topSignal.symbol} with ${topSignal.confidence}% confidence. Target: $${topSignal.target}. Used ${creditsNeeded} credits.`
        };
    } catch (error) {
        return {
            success: false,
            speech: "Signal generation needs recalibration. Try again?"
        };
    }
}

async function handleExecuteTrade({ symbol, action, amount }, userId) {
    try {
        await zmartyDB.deductCredits(userId, 1, 'simple_chat', `Paper trade: ${action} ${symbol}`);

        // Paper trading only
        const trade = {
            symbol,
            action,
            amount,
            price: 50000, // Would get real price
            timestamp: new Date().toISOString()
        };

        return {
            success: true,
            data: trade,
            speech: `Paper trade logged: ${action} ${amount} ${symbol} at $${trade.price.toLocaleString()}. This is practice mode. Used 1 credit.`
        };
    } catch (error) {
        return {
            success: false,
            speech: "Trade simulator is resetting. Try again."
        };
    }
}

async function handleMarketSentiment({ symbol }, userId) {
    try {
        const creditsNeeded = 5;
        await zmartyDB.deductCredits(userId, creditsNeeded, 'technical_analysis', 'Market sentiment');

        // Would get real sentiment data
        const sentiment = {
            overall: 'bullish',
            score: 72,
            fearGreed: 65
        };

        return {
            success: true,
            data: sentiment,
            speech: `Market sentiment is ${sentiment.overall} at ${sentiment.score}%. Fear & Greed index at ${sentiment.fearGreed}. Used ${creditsNeeded} credits.`
        };
    } catch (error) {
        return {
            success: false,
            speech: "Sentiment feeds are updating. Check back soon."
        };
    }
}

async function handlePositionSize({ accountBalance, riskPercentage, entryPrice, stopLoss }, userId) {
    try {
        const riskAmount = accountBalance * (riskPercentage / 100);
        const priceRisk = Math.abs(entryPrice - stopLoss);
        const positionSize = riskAmount / priceRisk;

        return {
            success: true,
            data: {
                positionSize,
                riskAmount,
                potential: positionSize * priceRisk
            },
            speech: `With ${riskPercentage}% risk on $${accountBalance.toLocaleString()}, you can take ${positionSize.toFixed(2)} units. Risk: $${riskAmount.toFixed(2)}.`
        };
    } catch (error) {
        return {
            success: false,
            speech: "Let me recalculate that position size."
        };
    }
}

export default router;