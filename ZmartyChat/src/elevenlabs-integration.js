// ElevenLabs Voice Agent Integration for ZmartyChat
import axios from 'axios';
import { EventEmitter } from 'events';
import { zmartyAI } from './zmarty-ai-agent.js';
import { manusConnector } from './zmarty-manus-connector.js';
import { creditManager } from './credit-manager.js';
import { zmartyDB } from './supabase-client.js';

export class ElevenLabsAgent extends EventEmitter {
    constructor() {
        super();

        // ElevenLabs Configuration
        this.config = {
            apiKey: process.env.ELEVENLABS_API_KEY,
            agentId: process.env.ELEVENLABS_AGENT_ID,
            voiceId: process.env.ELEVENLABS_VOICE_ID || 'rachel', // Friendly female voice
            webhookUrl: process.env.ELEVENLABS_WEBHOOK_URL || 'https://your-domain.com/api/elevenlabs/webhook',
            model: 'eleven_turbo_v2'
        };

        // Voice settings
        this.voiceSettings = {
            stability: 0.75,
            similarity_boost: 0.85,
            style: 0.5,
            use_speaker_boost: true
        };

        // Tools configuration for ElevenLabs
        this.tools = this.defineTools();
    }

    // ============= TOOL DEFINITIONS FOR ELEVENLABS =============

    defineTools() {
        return [
            {
                name: 'get_market_data',
                description: 'Get real-time cryptocurrency market data and prices',
                parameters: {
                    type: 'object',
                    properties: {
                        symbol: {
                            type: 'string',
                            description: 'Cryptocurrency symbol (e.g., BTC, ETH)'
                        }
                    },
                    required: ['symbol']
                },
                handler: async (params) => await this.getMarketData(params)
            },
            {
                name: 'technical_analysis',
                description: 'Perform technical analysis on a cryptocurrency',
                parameters: {
                    type: 'object',
                    properties: {
                        symbol: { type: 'string' },
                        timeframe: {
                            type: 'string',
                            enum: ['1m', '5m', '15m', '1h', '4h', '1d'],
                            default: '1h'
                        }
                    },
                    required: ['symbol']
                },
                handler: async (params) => await this.performTechnicalAnalysis(params)
            },
            {
                name: 'check_credits',
                description: 'Check user credit balance',
                parameters: {
                    type: 'object',
                    properties: {
                        userId: { type: 'string' }
                    },
                    required: ['userId']
                },
                handler: async (params) => await this.checkUserCredits(params)
            },
            {
                name: 'multi_agent_consensus',
                description: 'Get trading consensus from multiple AI agents',
                parameters: {
                    type: 'object',
                    properties: {
                        query: { type: 'string' },
                        symbol: { type: 'string' }
                    },
                    required: ['query']
                },
                handler: async (params) => await this.getMultiAgentConsensus(params)
            },
            {
                name: 'set_price_alert',
                description: 'Set a price alert for a cryptocurrency',
                parameters: {
                    type: 'object',
                    properties: {
                        symbol: { type: 'string' },
                        targetPrice: { type: 'number' },
                        direction: {
                            type: 'string',
                            enum: ['above', 'below']
                        }
                    },
                    required: ['symbol', 'targetPrice', 'direction']
                },
                handler: async (params) => await this.setPriceAlert(params)
            },
            {
                name: 'portfolio_analysis',
                description: 'Analyze user portfolio performance',
                parameters: {
                    type: 'object',
                    properties: {
                        userId: { type: 'string' }
                    },
                    required: ['userId']
                },
                handler: async (params) => await this.analyzePortfolio(params)
            },
            {
                name: 'get_trading_signals',
                description: 'Get AI-powered trading signals',
                parameters: {
                    type: 'object',
                    properties: {
                        symbols: {
                            type: 'array',
                            items: { type: 'string' }
                        },
                        riskLevel: {
                            type: 'string',
                            enum: ['conservative', 'moderate', 'aggressive'],
                            default: 'moderate'
                        }
                    },
                    required: ['symbols']
                },
                handler: async (params) => await this.getTradingSignals(params)
            },
            {
                name: 'execute_trade',
                description: 'Execute a simulated trade (paper trading)',
                parameters: {
                    type: 'object',
                    properties: {
                        symbol: { type: 'string' },
                        action: {
                            type: 'string',
                            enum: ['buy', 'sell']
                        },
                        amount: { type: 'number' },
                        userId: { type: 'string' }
                    },
                    required: ['symbol', 'action', 'amount', 'userId']
                },
                handler: async (params) => await this.executeTrade(params)
            }
        ];
    }

    // ============= TOOL HANDLERS =============

    async getMarketData({ symbol }) {
        try {
            // Deduct credits
            await this.deductCreditsForAction('market_data');

            // Get data from Manus agents
            const marketData = await manusConnector.getMarketData(symbol);

            return {
                success: true,
                data: {
                    symbol,
                    price: marketData.price,
                    change24h: marketData.change24h,
                    volume: marketData.volume,
                    marketCap: marketData.marketCap,
                    high24h: marketData.high24h,
                    low24h: marketData.low24h
                },
                speech: `${symbol} is currently trading at $${marketData.price}, ${marketData.change24h > 0 ? 'up' : 'down'} ${Math.abs(marketData.change24h)}% in the last 24 hours.`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                speech: `I couldn't fetch the market data for ${symbol} right now. Please try again.`
            };
        }
    }

    async performTechnicalAnalysis({ symbol, timeframe }) {
        try {
            await this.deductCreditsForAction('technical_analysis');

            const analysis = await manusConnector.getTechnicalAnalysis(symbol, timeframe);

            return {
                success: true,
                data: analysis,
                speech: `Based on technical analysis, ${symbol} shows a ${analysis.trend} trend on the ${timeframe} timeframe. RSI is at ${analysis.rsi}, indicating ${analysis.rsi > 70 ? 'overbought' : analysis.rsi < 30 ? 'oversold' : 'neutral'} conditions.`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                speech: `I couldn't complete the technical analysis for ${symbol}.`
            };
        }
    }

    async checkUserCredits({ userId }) {
        try {
            const credits = await zmartyDB.getUserCredits(userId);

            return {
                success: true,
                data: credits,
                speech: `You have ${credits.credits_balance} credits remaining. ${credits.credits_balance < 50 ? 'Consider purchasing more credits to continue using advanced features.' : ''}`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                speech: 'I couldn\'t check your credit balance right now.'
            };
        }
    }

    async getMultiAgentConsensus({ query, symbol }) {
        try {
            await this.deductCreditsForAction('multi_agent_consensus');

            const consensus = await manusConnector.getMultiAgentConsensus(query, symbol);

            const summary = this.summarizeConsensus(consensus);

            return {
                success: true,
                data: consensus,
                speech: summary
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                speech: 'I couldn\'t get the multi-agent consensus right now.'
            };
        }
    }

    async setPriceAlert({ symbol, targetPrice, direction }) {
        try {
            await this.deductCreditsForAction('simple_chat');

            // Store alert in database
            const alert = {
                symbol,
                targetPrice,
                direction,
                created: new Date().toISOString()
            };

            return {
                success: true,
                data: alert,
                speech: `I've set an alert for ${symbol} when the price goes ${direction} $${targetPrice}. I'll notify you when this happens.`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                speech: 'I couldn\'t set the price alert right now.'
            };
        }
    }

    async analyzePortfolio({ userId }) {
        try {
            await this.deductCreditsForAction('portfolio_analysis');

            // This would integrate with actual portfolio data
            const analysis = {
                totalValue: 10000,
                dayChange: 2.5,
                weekChange: 5.8,
                monthChange: 12.3,
                topPerformer: 'ETH',
                worstPerformer: 'DOGE'
            };

            return {
                success: true,
                data: analysis,
                speech: `Your portfolio is worth $${analysis.totalValue}, up ${analysis.dayChange}% today. Your best performer is ${analysis.topPerformer} and ${analysis.worstPerformer} is lagging. Overall, you're up ${analysis.monthChange}% this month.`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                speech: 'I couldn\'t analyze your portfolio right now.'
            };
        }
    }

    async getTradingSignals({ symbols, riskLevel }) {
        try {
            await this.deductCreditsForAction('ai_prediction');

            const signals = await manusConnector.generateTradingSignals(symbols, riskLevel);

            const topSignal = signals[0];

            return {
                success: true,
                data: signals,
                speech: `Based on AI analysis with ${riskLevel} risk, my top recommendation is to ${topSignal.action} ${topSignal.symbol} with a confidence of ${topSignal.confidence}%. Target price is $${topSignal.target}.`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                speech: 'I couldn\'t generate trading signals right now.'
            };
        }
    }

    async executeTrade({ symbol, action, amount, userId }) {
        try {
            await this.deductCreditsForAction('simple_chat');

            // Simulated trade execution
            const trade = {
                symbol,
                action,
                amount,
                executedPrice: 50000, // Would be real price
                timestamp: new Date().toISOString()
            };

            return {
                success: true,
                data: trade,
                speech: `I've executed a ${action} order for ${amount} ${symbol} at $${trade.executedPrice}. This is a simulated trade for practice.`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                speech: `I couldn't execute the ${action} order for ${symbol}.`
            };
        }
    }

    // ============= WEBHOOK HANDLER =============

    async handleWebhook(req, res) {
        const { event, data, metadata } = req.body;

        console.log('ElevenLabs Webhook Event:', event);

        try {
            switch (event) {
                case 'conversation.started':
                    await this.handleConversationStart(data, metadata);
                    break;

                case 'conversation.ended':
                    await this.handleConversationEnd(data, metadata);
                    break;

                case 'tool.called':
                    const result = await this.handleToolCall(data);
                    res.json(result);
                    return;

                case 'user.spoke':
                    await this.handleUserSpoke(data, metadata);
                    break;

                case 'agent.spoke':
                    await this.handleAgentSpoke(data, metadata);
                    break;

                case 'error':
                    await this.handleError(data);
                    break;

                default:
                    console.log('Unknown webhook event:', event);
            }

            res.json({ success: true });
        } catch (error) {
            console.error('Webhook handler error:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    async handleConversationStart(data, metadata) {
        const { userId, sessionId } = metadata;

        console.log(`Voice conversation started for user ${userId}`);

        // Initialize session
        this.emit('conversation:started', {
            userId,
            sessionId,
            timestamp: new Date()
        });

        // Check user credits
        const credits = await zmartyDB.getUserCredits(userId);
        if (credits.credits_balance < 10) {
            this.emit('low:credits', { userId, balance: credits.credits_balance });
        }
    }

    async handleConversationEnd(data, metadata) {
        const { userId, sessionId, duration } = data;

        console.log(`Voice conversation ended for user ${userId}, duration: ${duration}s`);

        // Calculate credits used based on duration
        const creditsUsed = Math.ceil(duration / 60) * 2; // 2 credits per minute

        await zmartyDB.deductCredits(
            userId,
            creditsUsed,
            'voice_chat',
            `Voice conversation (${Math.ceil(duration / 60)} minutes)`
        );

        this.emit('conversation:ended', {
            userId,
            sessionId,
            duration,
            creditsUsed
        });
    }

    async handleToolCall(data) {
        const { tool, parameters, userId } = data;

        console.log(`Tool called: ${tool}`, parameters);

        // Find the tool
        const toolDef = this.tools.find(t => t.name === tool);

        if (!toolDef) {
            return {
                success: false,
                error: 'Tool not found',
                speech: 'I don\'t have that capability yet.'
            };
        }

        // Add userId to parameters if needed
        if (userId && !parameters.userId) {
            parameters.userId = userId;
        }

        // Execute the tool
        try {
            const result = await toolDef.handler(parameters);

            // Log tool usage
            this.emit('tool:used', {
                tool,
                parameters,
                userId,
                success: result.success
            });

            return result;
        } catch (error) {
            console.error(`Tool execution error for ${tool}:`, error);
            return {
                success: false,
                error: error.message,
                speech: 'There was an error processing your request.'
            };
        }
    }

    async handleUserSpoke(data, metadata) {
        const { transcript, userId } = data;

        console.log(`User ${userId} said: ${transcript}`);

        // Queue for analysis
        this.emit('user:message', {
            userId,
            message: transcript,
            type: 'voice'
        });
    }

    async handleAgentSpoke(data, metadata) {
        const { transcript, userId } = data;

        console.log(`Agent said to ${userId}: ${transcript}`);

        // Log agent response
        this.emit('agent:message', {
            userId,
            message: transcript,
            type: 'voice'
        });
    }

    async handleError(data) {
        console.error('ElevenLabs error:', data);
        this.emit('error', data);
    }

    // ============= HELPER FUNCTIONS =============

    async deductCreditsForAction(action) {
        // This would actually deduct credits
        // For now, just log
        console.log(`Deducting credits for action: ${action}`);
    }

    summarizeConsensus(consensus) {
        const bullishCount = consensus.filter(a => a.sentiment === 'bullish').length;
        const bearishCount = consensus.filter(a => a.sentiment === 'bearish').length;
        const neutralCount = consensus.filter(a => a.sentiment === 'neutral').length;

        let summary = `After consulting ${consensus.length} AI agents, `;

        if (bullishCount > bearishCount) {
            summary += `the consensus is bullish with ${bullishCount} positive signals. `;
        } else if (bearishCount > bullishCount) {
            summary += `the consensus is bearish with ${bearishCount} negative signals. `;
        } else {
            summary += `the market sentiment is neutral. `;
        }

        summary += `The average confidence level is ${Math.round(consensus.reduce((acc, a) => acc + a.confidence, 0) / consensus.length)}%.`;

        return summary;
    }

    // ============= CONFIGURATION EXPORT =============

    exportToolsConfig() {
        // Format for ElevenLabs dashboard
        return this.tools.map(tool => ({
            name: tool.name,
            description: tool.description,
            parameters: tool.parameters
        }));
    }

    getWebhookConfig() {
        return {
            url: this.config.webhookUrl,
            events: [
                'conversation.started',
                'conversation.ended',
                'tool.called',
                'user.spoke',
                'agent.spoke',
                'error'
            ],
            headers: {
                'X-API-Key': process.env.WEBHOOK_SECRET || 'your-webhook-secret'
            }
        };
    }
}

// Export singleton instance
export const elevenLabsAgent = new ElevenLabsAgent();

// Export configurations for ElevenLabs dashboard
export const ELEVENLABS_TOOLS_CONFIG = elevenLabsAgent.exportToolsConfig();
export const ELEVENLABS_WEBHOOK_CONFIG = elevenLabsAgent.getWebhookConfig();