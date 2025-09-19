// Zmarty-Manus Integration Connector
// Connects Zmarty AI to the Manus Webhook system and all backend agents

class ZmartyManusConnector {
    constructor(zmartyAI) {
        this.zmarty = zmartyAI;
        this.manusEndpoint = window.MANUS_WEBHOOK_URL || 'http://localhost:8000/api/webhooks/manus';
        this.apiServerUrl = 'http://localhost:8000';
        this.websocketUrl = 'ws://localhost:8000/ws';

        // Available AI Agents from Manus system
        this.agents = {
            kingfisher: {
                endpoint: '/api/kingfisher/analyze',
                description: 'AI analysis engine',
                capabilities: ['market_analysis', 'prediction', 'signals']
            },
            cryptometer: {
                endpoint: '/api/cryptometer/full-analysis',
                description: 'Comprehensive market data with 17 endpoints',
                capabilities: ['win_rate', 'multi_timeframe', 'all_symbols', 'ai_predictions']
            },
            riskmetric: {
                endpoint: '/api/riskmetric/analyze',
                description: 'Risk analysis and management',
                capabilities: ['risk_scoring', 'portfolio_risk', 'position_sizing']
            },
            unifiedAnalysis: {
                endpoint: '/api/unified-analysis',
                description: 'Comprehensive unified analysis',
                capabilities: ['full_market_view', 'combined_signals', 'meta_analysis']
            },
            multiModelAI: {
                endpoint: '/api/multi-model',
                description: 'Multiple AI models consensus',
                capabilities: ['gpt4', 'claude', 'gemini', 'consensus_prediction']
            },
            sentimentAnalysis: {
                endpoint: '/api/sentiment',
                description: 'Market sentiment scoring',
                capabilities: ['social_sentiment', 'news_analysis', 'fear_greed']
            },
            patternRecognition: {
                endpoint: '/api/patterns',
                description: 'Advanced pattern detection',
                capabilities: ['chart_patterns', 'candlestick_patterns', 'trend_detection']
            },
            signalCenter: {
                endpoint: '/api/signals',
                description: 'Trading signal generation',
                capabilities: ['buy_signals', 'sell_signals', 'entry_exit_points']
            },
            technicalAnalysis: {
                endpoint: '/api/technical',
                description: 'Technical indicators analysis',
                capabilities: ['indicators', 'oscillators', 'moving_averages']
            },
            professionalAI: {
                endpoint: '/api/professional-analysis',
                description: 'Professional grade AI reports',
                capabilities: ['executive_summary', 'detailed_reports', 'sol_usdt_format']
            }
        };

        this.websocket = null;
        this.isConnected = false;
        this.messageQueue = [];
        this.activeRequests = new Map();

        this.init();
    }

    async init() {
        await this.connectToManus();
        await this.establishWebSocket();
        this.startHeartbeat();
        console.log('🔌 Zmarty-Manus Connector initialized');
    }

    async connectToManus() {
        try {
            // Register Zmarty with Manus Webhook system
            const response = await fetch(`${this.manusEndpoint}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Service-Name': 'zmarty-ai',
                    'X-Service-Type': 'ai-assistant'
                },
                body: JSON.stringify({
                    service: 'zmarty',
                    type: 'ai_assistant',
                    capabilities: [
                        'natural_language_processing',
                        'trading_assistance',
                        'market_analysis',
                        'portfolio_management',
                        'education',
                        'real_time_alerts'
                    ],
                    webhook_url: `http://localhost:3002/zmarty/webhook`,
                    api_version: '1.0',
                    status: 'active'
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Registered with Manus:', data);
                this.isConnected = true;
            }
        } catch (error) {
            console.error('Failed to connect to Manus:', error);
            // Retry connection after delay
            setTimeout(() => this.connectToManus(), 5000);
        }
    }

    async establishWebSocket() {
        try {
            this.websocket = new WebSocket(`${this.websocketUrl}/zmarty`);

            this.websocket.onopen = () => {
                console.log('🔗 WebSocket connected to Manus');
                this.processQueuedMessages();
            };

            this.websocket.onmessage = async (event) => {
                const data = JSON.parse(event.data);
                await this.handleWebSocketMessage(data);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.websocket.onclose = () => {
                console.log('WebSocket disconnected, reconnecting...');
                setTimeout(() => this.establishWebSocket(), 3000);
            };

        } catch (error) {
            console.error('WebSocket connection failed:', error);
        }
    }

    async handleWebSocketMessage(data) {
        switch(data.type) {
            case 'market_update':
                await this.handleMarketUpdate(data.payload);
                break;
            case 'signal_alert':
                await this.handleSignalAlert(data.payload);
                break;
            case 'agent_response':
                await this.handleAgentResponse(data.payload);
                break;
            case 'system_notification':
                await this.handleSystemNotification(data.payload);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    // Main method to process user messages through all agents
    async processUserMessage(message, userData) {
        const requestId = this.generateRequestId();
        const startTime = Date.now();

        console.log(`🎯 Processing message through Manus agents: "${message}"`);

        // Determine which agents to use based on message intent
        const requiredAgents = this.determineRequiredAgents(message);

        // Create a comprehensive analysis request
        const analysisRequest = {
            id: requestId,
            user_id: userData.id,
            user_name: userData.name,
            message: message,
            context: {
                conversation_history: this.zmarty.conversationContext,
                user_preferences: this.zmarty.personality.memory,
                market_sentiment: this.zmarty.marketSentiment,
                timestamp: new Date().toISOString()
            },
            requested_agents: requiredAgents,
            priority: this.determinePriority(message)
        };

        // Store active request
        this.activeRequests.set(requestId, {
            request: analysisRequest,
            responses: {},
            startTime: startTime
        });

        // Execute parallel requests to multiple agents
        const agentPromises = requiredAgents.map(agentName =>
            this.callAgent(agentName, analysisRequest)
        );

        try {
            // Wait for all agents to respond
            const responses = await Promise.allSettled(agentPromises);

            // Combine and analyze all agent responses
            const combinedAnalysis = await this.combineAgentResponses(responses, requiredAgents);

            // Generate Zmarty's response based on all agent inputs
            const zmartyResponse = await this.generateSmartResponse(combinedAnalysis, message, userData);

            // Log performance metrics
            const processingTime = Date.now() - startTime;
            console.log(`⚡ Processed in ${processingTime}ms using ${requiredAgents.length} agents`);

            return zmartyResponse;

        } catch (error) {
            console.error('Error processing through Manus:', error);
            return this.getFallbackResponse(message);
        } finally {
            this.activeRequests.delete(requestId);
        }
    }

    determineRequiredAgents(message) {
        const agents = [];
        const lowerMessage = message.toLowerCase();

        // Always include unified analysis for comprehensive view
        agents.push('unifiedAnalysis');

        // Add specific agents based on message content
        if (lowerMessage.includes('price') || lowerMessage.includes('market')) {
            agents.push('cryptometer');
            agents.push('technicalAnalysis');
        }

        if (lowerMessage.includes('risk') || lowerMessage.includes('safe')) {
            agents.push('riskmetric');
        }

        if (lowerMessage.includes('buy') || lowerMessage.includes('sell') || lowerMessage.includes('signal')) {
            agents.push('signalCenter');
            agents.push('kingfisher');
        }

        if (lowerMessage.includes('sentiment') || lowerMessage.includes('feeling') || lowerMessage.includes('mood')) {
            agents.push('sentimentAnalysis');
        }

        if (lowerMessage.includes('pattern') || lowerMessage.includes('chart')) {
            agents.push('patternRecognition');
        }

        if (lowerMessage.includes('analysis') || lowerMessage.includes('report')) {
            agents.push('professionalAI');
            agents.push('multiModelAI');
        }

        // Limit to max 5 agents per request for performance
        return agents.slice(0, 5);
    }

    async callAgent(agentName, request) {
        const agent = this.agents[agentName];
        if (!agent) {
            console.warn(`Agent ${agentName} not found`);
            return null;
        }

        try {
            const response = await fetch(`${this.apiServerUrl}${agent.endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Request-ID': request.id,
                    'X-Agent-Name': agentName,
                    'X-Service': 'zmarty'
                },
                body: JSON.stringify({
                    query: request.message,
                    context: request.context,
                    capabilities_needed: agent.capabilities,
                    user_id: request.user_id
                })
            });

            if (response.ok) {
                const data = await response.json();
                return {
                    agent: agentName,
                    status: 'success',
                    data: data
                };
            } else {
                throw new Error(`Agent ${agentName} returned ${response.status}`);
            }

        } catch (error) {
            console.error(`Error calling agent ${agentName}:`, error);
            return {
                agent: agentName,
                status: 'error',
                error: error.message
            };
        }
    }

    async combineAgentResponses(responses, agentNames) {
        const combined = {
            consensus: {},
            insights: [],
            data: {},
            signals: [],
            risks: [],
            recommendations: [],
            confidence: 0
        };

        let successfulResponses = 0;

        responses.forEach((response, index) => {
            if (response.status === 'fulfilled' && response.value?.status === 'success') {
                successfulResponses++;
                const agentName = agentNames[index];
                const agentData = response.value.data;

                // Extract key information from each agent
                this.extractAgentInsights(agentName, agentData, combined);
            }
        });

        // Calculate overall confidence based on agent consensus
        combined.confidence = (successfulResponses / responses.length) * 100;

        // Process consensus from multiple agents
        combined.consensus = this.calculateConsensus(combined);

        return combined;
    }

    extractAgentInsights(agentName, data, combined) {
        switch(agentName) {
            case 'cryptometer':
                if (data.win_rate) combined.data.winRate = data.win_rate;
                if (data.price_prediction) combined.data.pricePrediction = data.price_prediction;
                if (data.signals) combined.signals.push(...data.signals);
                break;

            case 'kingfisher':
                if (data.analysis) combined.insights.push(data.analysis);
                if (data.recommendation) combined.recommendations.push(data.recommendation);
                break;

            case 'riskmetric':
                if (data.risk_score) combined.risks.push({
                    type: 'overall',
                    score: data.risk_score,
                    description: data.risk_description
                });
                break;

            case 'signalCenter':
                if (data.buy_signals) combined.signals.push(...data.buy_signals.map(s => ({...s, type: 'buy'})));
                if (data.sell_signals) combined.signals.push(...data.sell_signals.map(s => ({...s, type: 'sell'})));
                break;

            case 'sentimentAnalysis':
                if (data.sentiment_score) combined.data.sentiment = data.sentiment_score;
                if (data.social_buzz) combined.data.socialBuzz = data.social_buzz;
                break;

            case 'multiModelAI':
                if (data.consensus) combined.consensus.aiModels = data.consensus;
                if (data.predictions) combined.data.aiPredictions = data.predictions;
                break;

            case 'professionalAI':
                if (data.executive_summary) combined.insights.unshift(data.executive_summary);
                if (data.key_metrics) combined.data.keyMetrics = data.key_metrics;
                break;

            default:
                // Generic extraction
                if (data.insight) combined.insights.push(data.insight);
                if (data.recommendation) combined.recommendations.push(data.recommendation);
        }
    }

    calculateConsensus(combined) {
        const consensus = {
            direction: 'neutral',
            strength: 0,
            action: 'hold',
            confidence: combined.confidence
        };

        // Analyze signals for consensus
        if (combined.signals.length > 0) {
            const buySignals = combined.signals.filter(s => s.type === 'buy').length;
            const sellSignals = combined.signals.filter(s => s.type === 'sell').length;

            if (buySignals > sellSignals * 1.5) {
                consensus.direction = 'bullish';
                consensus.action = 'buy';
                consensus.strength = Math.min((buySignals / combined.signals.length) * 100, 100);
            } else if (sellSignals > buySignals * 1.5) {
                consensus.direction = 'bearish';
                consensus.action = 'sell';
                consensus.strength = Math.min((sellSignals / combined.signals.length) * 100, 100);
            }
        }

        // Factor in sentiment
        if (combined.data.sentiment) {
            if (combined.data.sentiment > 70) {
                consensus.direction = consensus.direction === 'bearish' ? 'neutral' : 'bullish';
            } else if (combined.data.sentiment < 30) {
                consensus.direction = consensus.direction === 'bullish' ? 'neutral' : 'bearish';
            }
        }

        return consensus;
    }

    async generateSmartResponse(analysis, originalMessage, userData) {
        const response = {
            text: '',
            type: 'manus_analysis',
            data: {},
            emotion: 'analytical',
            shouldSpeak: false,
            confidence: analysis.confidence
        };

        // Build response based on consensus and insights
        if (analysis.confidence > 80) {
            response.emotion = 'confident';
            response.text = `${userData.name}, I've consulted with all my AI agents and we have strong consensus here! `;
        } else if (analysis.confidence > 50) {
            response.emotion = 'thoughtful';
            response.text = `Alright ${userData.name}, I've analyzed this from multiple angles. `;
        } else {
            response.emotion = 'cautious';
            response.text = `${userData.name}, the signals are mixed on this one. Let me explain what I'm seeing. `;
        }

        // Add consensus view
        if (analysis.consensus.direction === 'bullish') {
            response.text += `📈 The overall outlook is BULLISH with ${analysis.consensus.strength.toFixed(0)}% strength. `;

            if (analysis.consensus.action === 'buy') {
                response.text += `This could be a good entry point. `;
            }
        } else if (analysis.consensus.direction === 'bearish') {
            response.text += `📉 We're seeing BEARISH signals with ${analysis.consensus.strength.toFixed(0)}% strength. `;

            if (analysis.consensus.action === 'sell') {
                response.text += `Consider taking profits or waiting for better entry. `;
            }
        } else {
            response.text += `The market is NEUTRAL right now - no clear direction. `;
        }

        // Add key insights
        if (analysis.insights.length > 0) {
            response.text += `\n\n💡 Key Insights:\n`;
            analysis.insights.slice(0, 3).forEach((insight, i) => {
                response.text += `${i + 1}. ${insight}\n`;
            });
        }

        // Add data points
        if (analysis.data.winRate) {
            response.text += `\n📊 Win Rate Prediction: ${analysis.data.winRate}%`;
        }
        if (analysis.data.sentiment) {
            response.text += `\n😊 Market Sentiment: ${analysis.data.sentiment}/100`;
        }

        // Add top signals
        if (analysis.signals.length > 0) {
            const topSignal = analysis.signals[0];
            response.text += `\n\n🎯 Top Signal: ${topSignal.type.toUpperCase()} - ${topSignal.description || 'Strong signal detected'}`;
        }

        // Add risk warning if needed
        if (analysis.risks.length > 0 && analysis.risks[0].score > 7) {
            response.text += `\n\n⚠️ Risk Alert: ${analysis.risks[0].description}`;
        }

        // Add recommendations
        if (analysis.recommendations.length > 0) {
            response.text += `\n\n💭 My Recommendation: ${analysis.recommendations[0]}`;
        }

        // Add engagement question
        response.text += `\n\nWant me to dive deeper into any of this?`;

        // Include structured data
        response.data = {
            consensus: analysis.consensus,
            metrics: analysis.data,
            signals: analysis.signals.slice(0, 3),
            confidence: analysis.confidence
        };

        // Add action buttons based on analysis
        response.actions = this.generateActionButtons(analysis);

        return response;
    }

    generateActionButtons(analysis) {
        const actions = [];

        if (analysis.consensus.action === 'buy') {
            actions.push({ label: 'Execute Buy', action: 'execute_buy' });
        } else if (analysis.consensus.action === 'sell') {
            actions.push({ label: 'Execute Sell', action: 'execute_sell' });
        }

        actions.push(
            { label: 'Set Alert', action: 'set_alert' },
            { label: 'View Chart', action: 'show_chart' },
            { label: 'Risk Analysis', action: 'deep_risk' }
        );

        return actions;
    }

    // Handle real-time updates from Manus
    async handleMarketUpdate(data) {
        // Process market update and notify Zmarty
        if (data.significant_change) {
            const alert = {
                type: 'market_update',
                symbol: data.symbol,
                change: data.change_percent,
                price: data.current_price,
                volume: data.volume
            };

            await this.zmarty.sendProactiveMessage(alert);
        }
    }

    async handleSignalAlert(data) {
        // Process trading signal and notify user
        const signal = {
            type: data.signal_type,
            symbol: data.symbol,
            action: data.recommended_action,
            confidence: data.confidence,
            entry: data.entry_price,
            target: data.target_price,
            stop: data.stop_loss
        };

        await this.zmarty.sendProactiveMessage({
            type: 'breakout',
            symbol: signal.symbol,
            percentIncrease: ((signal.target - signal.entry) / signal.entry * 100).toFixed(2),
            signal: signal
        });
    }

    async handleAgentResponse(data) {
        // Handle async responses from agents
        const request = this.activeRequests.get(data.request_id);
        if (request) {
            request.responses[data.agent_name] = data.response;
        }
    }

    async handleSystemNotification(data) {
        console.log('System notification:', data);
    }

    // Utility methods
    processQueuedMessages() {
        while (this.messageQueue.length > 0 && this.websocket?.readyState === WebSocket.OPEN) {
            const message = this.messageQueue.shift();
            this.websocket.send(JSON.stringify(message));
        }
    }

    startHeartbeat() {
        setInterval(() => {
            if (this.websocket?.readyState === WebSocket.OPEN) {
                this.websocket.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, 30000);
    }

    determinePriority(message) {
        const urgent = ['urgent', 'now', 'immediately', 'asap', 'quick'];
        const high = ['important', 'critical', 'alert', 'breaking'];

        const lower = message.toLowerCase();

        if (urgent.some(word => lower.includes(word))) return 'urgent';
        if (high.some(word => lower.includes(word))) return 'high';
        return 'normal';
    }

    generateRequestId() {
        return `zmarty_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getFallbackResponse(message) {
        return {
            text: `I'm having trouble connecting to my analysis engines right now, but I'm still here to help! Based on what I know, ${message} is an interesting question. Let me work on this locally and get back to you with insights.`,
            type: 'fallback',
            emotion: 'supportive',
            shouldSpeak: false
        };
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZmartyManusConnector;
} else {
    window.ZmartyManusConnector = ZmartyManusConnector;
}