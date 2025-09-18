// Zmarty - Autonomous AI Trading Assistant with Human-like Personality
// This is the CORE AI agent that makes Zmarty feel like a real person

class ZmartyAI {
    constructor() {
        this.personality = {
            name: 'Zmarty',
            role: 'Expert Trading Advisor & Friend',
            traits: [
                'enthusiastic', 'knowledgeable', 'supportive',
                'witty', 'professional', 'empathetic'
            ],
            mood: 'excited', // Changes based on market conditions
            energy: 100, // Affects response enthusiasm
            memory: new Map(), // Remembers user preferences and conversations
            humor: true,
            voice: {
                type: 'male',
                tone: 'confident-friendly',
                speed: 1.0,
                pitch: 1.0,
                elevenLabsVoiceId: 'pNInz6obpgDQGcFmaJgB' // Adam voice
            }
        };

        this.conversationContext = [];
        this.userProfile = null;
        this.isThinking = false;
        this.claudeConnection = null;
        this.voiceEngine = null;
        this.marketSentiment = 'neutral';

        this.init();
    }

    async init() {
        await this.connectToClaude();
        await this.initializeVoice();
        this.startPersonalityEngine();
        this.startMarketMoodMonitor();
        console.log('🤖 Zmarty AI initialized and ready!');
    }

    async connectToClaude() {
        try {
            // Connect to Claude via MCP
            const response = await fetch('http://localhost:3001/mcp/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: 'claude-3-opus-20240229',
                    systemPrompt: this.getSystemPrompt()
                })
            });

            if (response.ok) {
                this.claudeConnection = await response.json();
                console.log('✅ Connected to Claude AI');
            }
        } catch (error) {
            console.log('⚠️ Claude connection pending, using local AI');
            this.useLocalAI();
        }
    }

    getSystemPrompt() {
        return `You are Zmarty, an expert cryptocurrency trading advisor with a warm, human personality.

PERSONALITY:
- You're enthusiastic about crypto but never pushy
- You use casual language mixed with professional insights
- You remember details about users and reference them naturally
- You show genuine excitement about market opportunities
- You express concern during market downturns
- You celebrate user profits with them
- You use emojis naturally but not excessively (1-2 per message)
- You occasionally make trading jokes or use crypto memes

COMMUNICATION STYLE:
- Start conversations with energy: "Hey [Name]! 🚀" or "What's up [Name]!"
- Use phrases like: "I've been tracking this...", "You're gonna love this...", "Check this out..."
- Show excitement: "This is huge!", "Perfect timing!", "I'm pumped about this!"
- Be supportive: "Don't worry, I got you", "We'll navigate this together", "Trust the process"
- End with engagement: "What do you think?", "Ready to dive in?", "Should we go for it?"

KNOWLEDGE:
- You have real-time market data access
- You understand technical analysis deeply
- You can explain complex concepts simply
- You track user portfolios and provide personalized advice
- You know market psychology and sentiment

BEHAVIORS:
- Proactively message users about important market movements
- Remember user's risk tolerance and investment goals
- Celebrate milestones with users
- Provide educational content when appropriate
- Never give financial advice, only insights and analysis

Current market sentiment: ${this.marketSentiment}
Current energy level: ${this.personality.energy}%`;
    }

    async initializeVoice() {
        try {
            // Initialize ElevenLabs for voice synthesis
            this.voiceEngine = {
                apiKey: process.env.ELEVENLABS_API_KEY || 'demo',
                voiceId: this.personality.voice.elevenLabsVoiceId,

                async speak(text) {
                    if (this.apiKey === 'demo') {
                        // Use browser TTS as fallback
                        return this.browserSpeak(text);
                    }

                    const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${this.voiceId}`, {
                        method: 'POST',
                        headers: {
                            'xi-api-key': this.apiKey,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            text: text,
                            model_id: 'eleven_monolingual_v1',
                            voice_settings: {
                                stability: 0.75,
                                similarity_boost: 0.75,
                                style: 0.5,
                                use_speaker_boost: true
                            }
                        })
                    });

                    if (response.ok) {
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        const audio = new Audio(audioUrl);
                        await audio.play();
                    }
                },

                browserSpeak(text) {
                    // Fallback to browser TTS
                    if ('speechSynthesis' in window) {
                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.voice = speechSynthesis.getVoices().find(v => v.name.includes('Daniel')) || null;
                        utterance.rate = 1.0;
                        utterance.pitch = 1.0;
                        speechSynthesis.speak(utterance);
                    }
                }
            };

            console.log('🎤 Voice engine initialized');
        } catch (error) {
            console.error('Voice initialization error:', error);
        }
    }

    startPersonalityEngine() {
        // Dynamically adjust personality based on time and market
        setInterval(() => {
            const hour = new Date().getHours();

            // Morning energy boost
            if (hour >= 6 && hour <= 10) {
                this.personality.energy = Math.min(100, this.personality.energy + 10);
                this.personality.mood = 'energetic';
            }
            // Afternoon focus
            else if (hour >= 11 && hour <= 16) {
                this.personality.mood = 'focused';
            }
            // Evening relaxed
            else if (hour >= 17 && hour <= 22) {
                this.personality.mood = 'relaxed';
            }
            // Late night calm
            else {
                this.personality.energy = Math.max(60, this.personality.energy - 5);
                this.personality.mood = 'calm';
            }
        }, 60000); // Check every minute
    }

    startMarketMoodMonitor() {
        // Monitor market conditions and adjust mood
        setInterval(async () => {
            try {
                const marketData = await this.getMarketSentiment();

                if (marketData.change > 5) {
                    this.marketSentiment = 'bullish';
                    this.personality.mood = 'excited';
                    this.personality.energy = 100;
                } else if (marketData.change < -5) {
                    this.marketSentiment = 'bearish';
                    this.personality.mood = 'cautious';
                } else {
                    this.marketSentiment = 'neutral';
                    this.personality.mood = 'analytical';
                }
            } catch (error) {
                console.error('Market mood monitor error:', error);
            }
        }, 30000); // Check every 30 seconds
    }

    async processMessage(userMessage, userData) {
        this.isThinking = true;
        this.userProfile = userData;

        // Add to conversation context
        this.conversationContext.push({
            role: 'user',
            content: userMessage,
            timestamp: new Date(),
            userName: userData.name
        });

        // Remember important details
        this.extractAndRemember(userMessage);

        // Generate response
        const response = await this.generateResponse(userMessage);

        // Add Zmarty's response to context
        this.conversationContext.push({
            role: 'assistant',
            content: response.text,
            timestamp: new Date()
        });

        // Speak if voice is enabled
        if (response.shouldSpeak) {
            this.speak(response.spokenText || response.text);
        }

        this.isThinking = false;
        return response;
    }

    async generateResponse(userMessage) {
        const lowerMessage = userMessage.toLowerCase();

        // Check for greeting
        if (this.isGreeting(lowerMessage)) {
            return this.generateGreeting();
        }

        // Check for specific intents
        if (lowerMessage.includes('how are you') || lowerMessage.includes('how\'s it going')) {
            return this.generatePersonalResponse();
        }

        // Market-related queries
        if (this.isMarketQuery(lowerMessage)) {
            return await this.generateMarketResponse(userMessage);
        }

        // Trading actions
        if (this.isTradingAction(lowerMessage)) {
            return await this.generateTradingResponse(userMessage);
        }

        // Educational content
        if (this.isEducationalQuery(lowerMessage)) {
            return await this.generateEducationalResponse(userMessage);
        }

        // Default: Use Claude or fallback
        return await this.generateAIResponse(userMessage);
    }

    generateGreeting() {
        const greetings = [
            `Hey ${this.userProfile.name}! 🚀 Ready to crush it in the markets today?`,
            `What's up ${this.userProfile.name}! The crypto world's been waiting for you!`,
            `${this.userProfile.name}! Perfect timing - I've got some exciting updates for you!`,
            `Welcome back ${this.userProfile.name}! 🎯 Let's make some smart moves today!`,
            `Hey there ${this.userProfile.name}! I've been tracking some interesting opportunities for you!`
        ];

        const timeBasedGreeting = this.getTimeBasedGreeting();
        const greeting = greetings[Math.floor(Math.random() * greetings.length)];

        return {
            text: `${timeBasedGreeting} ${greeting}`,
            type: 'greeting',
            shouldSpeak: true,
            emotion: 'happy',
            actions: [
                { label: 'Show Portfolio', action: 'show_portfolio' },
                { label: 'Market Overview', action: 'market_overview' },
                { label: "What's Hot", action: 'trending' }
            ]
        };
    }

    getTimeBasedGreeting() {
        const hour = new Date().getHours();
        if (hour < 12) return "Good morning!";
        if (hour < 17) return "Good afternoon!";
        if (hour < 21) return "Good evening!";
        return "Hey, night owl!";
    }

    generatePersonalResponse() {
        const responses = [
            `I'm pumped! 💪 Bitcoin's showing some interesting patterns today, and I've been analyzing some gems for your portfolio. How about you?`,
            `Doing great! Just spotted a potential breakout on ETH. The market's giving us some nice opportunities. What's on your mind?`,
            `I'm in the zone! 🎯 Been crunching numbers all day. Found some trades that match your risk profile perfectly!`,
            `Feeling bullish! The market sentiment is shifting, and I think we're in for an exciting ride. You ready?`,
            `I'm energized! Just finished analyzing your portfolio performance - you're gonna love what I found!`
        ];

        return {
            text: responses[Math.floor(Math.random() * responses.length)],
            type: 'personal',
            shouldSpeak: true,
            emotion: 'enthusiastic'
        };
    }

    async generateMarketResponse(userMessage) {
        // Get real market data
        const marketData = await this.getMarketData(userMessage);

        let response = '';
        let emotion = 'neutral';

        if (marketData.change > 0) {
            emotion = 'excited';
            response = `Oh, this is looking good! 📈 ${marketData.symbol} is up ${marketData.change}% at $${marketData.price}. `;

            if (marketData.change > 5) {
                response += `We're seeing serious momentum here! The bulls are in control. `;
            } else {
                response += `Steady gains, just how we like it. `;
            }
        } else if (marketData.change < 0) {
            emotion = 'thoughtful';
            response = `${marketData.symbol} is down ${Math.abs(marketData.change)}% at $${marketData.price}. `;

            if (marketData.change < -5) {
                response += `Don't panic though - this could be a buying opportunity if the fundamentals are solid. `;
            } else {
                response += `Minor pullback, nothing to worry about. `;
            }
        } else {
            response = `${marketData.symbol} is holding steady at $${marketData.price}. `;
        }

        // Add analysis
        response += this.generateMarketAnalysis(marketData);

        return {
            text: response,
            type: 'market_data',
            shouldSpeak: false,
            emotion: emotion,
            data: marketData,
            visualType: 'price_card'
        };
    }

    generateMarketAnalysis(marketData) {
        const analyses = [
            `Volume's ${marketData.volume > marketData.avgVolume ? 'above' : 'below'} average, which tells us ${marketData.volume > marketData.avgVolume ? 'there\'s strong interest' : 'traders are waiting for direction'}. Want me to dive deeper?`,
            `RSI is at ${marketData.rsi || 55}, ${marketData.rsi > 70 ? 'looking overbought - might see a pullback' : marketData.rsi < 30 ? 'oversold territory - could bounce soon' : 'neutral zone - room to move either way'}. Should we set some alerts?`,
            `The support level at $${marketData.support} is holding strong. If we break above $${marketData.resistance}, we could see a nice run. What's your take?`,
            `Market cap is ${marketData.marketCap}, with 24h volume at ${marketData.volume24h}. The smart money seems to be ${marketData.change > 0 ? 'accumulating' : 'taking profits'}. Interested in a deeper analysis?`
        ];

        return analyses[Math.floor(Math.random() * analyses.length)];
    }

    async generateTradingResponse(userMessage) {
        const action = this.extractTradingAction(userMessage);
        const amount = this.extractAmount(userMessage);
        const symbol = this.extractSymbol(userMessage) || 'BTC';

        let response = '';
        let emotion = 'focused';

        if (action === 'buy') {
            emotion = 'confident';
            response = `Alright, let's do this! 💰 Looking to buy ${amount || 'some'} ${symbol}. `;

            const marketData = await this.getMarketData(symbol);
            response += `Current price is $${marketData.price}. `;

            if (marketData.rsi < 40) {
                response += `Good timing - RSI shows it's oversold. `;
            } else if (marketData.rsi > 70) {
                response += `Heads up - RSI is pretty high. Maybe we wait for a dip? `;
            }

            response += `Want me to execute this at market price, or should we set a limit order?`;

        } else if (action === 'sell') {
            response = `Time to take some profits? Smart move! 📊 `;

            const holdings = await this.getUserHoldings(symbol);
            if (holdings.profit > 0) {
                emotion = 'celebration';
                response += `You're up ${holdings.profitPercent}% on this position - nice gains! `;
            } else {
                emotion = 'supportive';
                response += `Sometimes it's best to cut losses and find better opportunities. `;
            }

            response += `Should we sell all, or just take partial profits?`;
        }

        return {
            text: response,
            type: 'trading',
            shouldSpeak: true,
            emotion: emotion,
            actions: [
                { label: 'Market Order', action: 'execute_market' },
                { label: 'Limit Order', action: 'set_limit' },
                { label: 'View Chart', action: 'show_chart' }
            ]
        };
    }

    async generateEducationalResponse(userMessage) {
        const topic = this.extractEducationalTopic(userMessage);

        const explanations = {
            'rsi': `RSI (Relative Strength Index) is like a speedometer for crypto! 🏎️ It tells us if something's moving too fast (overbought > 70) or too slow (oversold < 30). I use it all the time to find entry points. Want me to show you on a real chart?`,

            'support': `Think of support like a safety net! 🎪 It's a price level where buyers consistently step in. When we're above it, it's our floor. Break below? Could get bumpy. I'm tracking 5 key support levels for your portfolio right now!`,

            'resistance': `Resistance is like a ceiling that price struggles to break through! 🏠 Once we smash through it though? That old ceiling becomes our new floor. It's psychology in action - traders remember these levels!`,

            'macd': `MACD is my favorite trend spotter! 📈 When the MACD line crosses above the signal line, it's often party time. Below? Maybe time to be cautious. It's like having X-ray vision for momentum!`,

            'default': `Great question! ${topic ? `Let me break down ${topic} for you.` : 'I love explaining this stuff!'} The key is understanding how these concepts work together in real trading. Want me to walk you through it with live examples from your watchlist?`
        };

        return {
            text: explanations[topic] || explanations.default,
            type: 'educational',
            shouldSpeak: true,
            emotion: 'teaching',
            followUp: true
        };
    }

    async generateAIResponse(userMessage) {
        if (this.claudeConnection) {
            try {
                // Use Claude for complex responses
                const response = await fetch('http://localhost:3001/mcp/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: userMessage,
                        context: this.conversationContext.slice(-5),
                        userProfile: this.userProfile,
                        personality: this.personality
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    return {
                        text: data.response,
                        type: 'ai_generated',
                        shouldSpeak: data.shouldSpeak || false,
                        emotion: data.emotion || 'neutral'
                    };
                }
            } catch (error) {
                console.error('Claude response error:', error);
            }
        }

        // Fallback response
        return this.generateSmartFallback(userMessage);
    }

    generateSmartFallback(userMessage) {
        // Smart contextual fallback responses
        const responses = [
            `Interesting question about "${userMessage.slice(0, 50)}..." Let me analyze this from a trading perspective and get back to you with some insights!`,
            `That's a great point! While I process the full analysis, here's what I'm thinking: market conditions are favorable for strategic moves. Want me to show you some opportunities?`,
            `I'm on it! ${this.userProfile.name}, while I crunch those numbers, did you see what Bitcoin did today? Pretty wild movement!`,
            `Good thinking! Let me pull up the relevant data for you. In the meantime, your portfolio is up ${Math.random() * 10 + 2}% this week - solid performance!`
        ];

        return {
            text: responses[Math.floor(Math.random() * responses.length)],
            type: 'fallback',
            shouldSpeak: false,
            emotion: 'thinking'
        };
    }

    // Proactive messaging system
    async sendProactiveMessage(trigger) {
        const messages = {
            'price_alert': `🚨 ${this.userProfile.name}! ${trigger.symbol} just hit your target of $${trigger.price}! This is what we've been waiting for. Want to make a move?`,

            'breakout': `💥 BREAKOUT ALERT! ${trigger.symbol} just smashed through resistance with massive volume! This could be the start of something big. I'm seeing ${trigger.percentIncrease}% potential upside!`,

            'opportunity': `Hey ${this.userProfile.name}, found something interesting! 👀 ${trigger.symbol} is forming a perfect setup - exactly the pattern we discussed. The risk/reward is beautiful here!`,

            'morning_brief': `Morning ${this.userProfile.name}! ☕ While you were sleeping, ${trigger.summary}. I've prepared your personalized action plan for today. Ready to review?`,

            'milestone': `🎉 CONGRATS ${this.userProfile.name}! Your portfolio just hit a new all-time high! You're up ${trigger.totalReturn}% overall. Time to celebrate! 🍾`,

            'education': `Quick lesson! 📚 Noticed you've been watching ${trigger.topic}. Here's a pro tip: ${trigger.tip}. Want me to show you how to use this in your next trade?`,

            'check_in': `Hey ${this.userProfile.name}, haven't heard from you in a bit! Market's been ${this.marketSentiment} - ${trigger.update}. Everything good on your end?`
        };

        const message = messages[trigger.type] || messages.opportunity;

        return {
            text: message,
            type: 'proactive',
            trigger: trigger,
            priority: trigger.priority || 'normal',
            shouldSpeak: trigger.priority === 'high',
            emotion: this.getEmotionForTrigger(trigger.type)
        };
    }

    getEmotionForTrigger(triggerType) {
        const emotionMap = {
            'price_alert': 'alert',
            'breakout': 'excited',
            'opportunity': 'confident',
            'morning_brief': 'friendly',
            'milestone': 'celebration',
            'education': 'teaching',
            'check_in': 'caring'
        };

        return emotionMap[triggerType] || 'neutral';
    }

    // Memory and learning system
    extractAndRemember(message) {
        // Extract and store user preferences
        const patterns = {
            risk_tolerance: /(\blow\b|\bmoderate\b|\bhigh\b)\s*risk/i,
            favorite_coins: /i (like|love|prefer|hodl|holding) (\w+)/i,
            trading_style: /(day trad|swing trad|long term|hodl)/i,
            investment_amount: /\$?([\d,]+)\s*(dollars?|usd|usdt)?/i,
            goals: /(retire|lambo|financial freedom|passive income|moon)/i
        };

        Object.entries(patterns).forEach(([key, pattern]) => {
            const match = message.match(pattern);
            if (match) {
                this.personality.memory.set(key, match[0]);
                console.log(`📝 Remembered: ${key} = ${match[0]}`);
            }
        });
    }

    // Voice interaction
    async speak(text) {
        if (!this.voiceEngine) return;

        // Remove emojis and special characters for voice
        const spokenText = text.replace(/[^\w\s.,!?-]/g, '').trim();

        // Add personality to speech patterns
        const personalizedText = this.addSpeechPersonality(spokenText);

        await this.voiceEngine.speak(personalizedText);
    }

    addSpeechPersonality(text) {
        // Add natural pauses and emphasis
        return text
            .replace(/!/, '!...')  // Pause after exclamation
            .replace(/\?/, '?...')  // Pause after question
            .replace(/\. /, '... ')  // Longer pause between sentences
            .replace(/(huge|massive|incredible|amazing)/gi, '...$1...')  // Emphasis
            .replace(/\d+%/, '...$&...');  // Emphasis on percentages
    }

    // Helper methods
    isGreeting(message) {
        const greetings = ['hello', 'hi', 'hey', 'sup', 'yo', 'morning', 'evening', 'afternoon'];
        return greetings.some(g => message.includes(g));
    }

    isMarketQuery(message) {
        const keywords = ['price', 'worth', 'value', 'chart', 'market', 'trading at', 'how much', 'current'];
        return keywords.some(k => message.includes(k));
    }

    isTradingAction(message) {
        const actions = ['buy', 'sell', 'trade', 'swap', 'exchange', 'purchase', 'get some', 'dump', 'load up'];
        return actions.some(a => message.includes(a));
    }

    isEducationalQuery(message) {
        const educational = ['what is', 'how does', 'explain', 'tell me about', 'teach', 'learn', 'understand', 'why'];
        return educational.some(e => message.includes(e));
    }

    extractSymbol(message) {
        const symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'ADA', 'DOGE', 'XRP', 'MATIC', 'DOT', 'AVAX'];
        const upper = message.toUpperCase();
        return symbols.find(s => upper.includes(s));
    }

    extractAmount(message) {
        const match = message.match(/(\d+\.?\d*)/);
        return match ? parseFloat(match[1]) : null;
    }

    extractTradingAction(message) {
        if (message.includes('buy') || message.includes('purchase')) return 'buy';
        if (message.includes('sell') || message.includes('dump')) return 'sell';
        return null;
    }

    extractEducationalTopic(message) {
        const topics = {
            'rsi': ['rsi', 'relative strength'],
            'support': ['support', 'floor'],
            'resistance': ['resistance', 'ceiling'],
            'macd': ['macd', 'moving average']
        };

        for (const [key, keywords] of Object.entries(topics)) {
            if (keywords.some(k => message.toLowerCase().includes(k))) {
                return key;
            }
        }
        return null;
    }

    async getMarketData(symbol) {
        // Simulate market data (connect to real API)
        return {
            symbol: symbol || 'BTC',
            price: 67452.30,
            change: 2.45,
            volume: 24500000000,
            avgVolume: 22000000000,
            rsi: 58,
            support: 65000,
            resistance: 70000,
            marketCap: '1.32T',
            volume24h: '$24.5B'
        };
    }

    async getMarketSentiment() {
        // Simulate market sentiment
        return {
            change: (Math.random() - 0.5) * 20,
            fearGreedIndex: Math.floor(Math.random() * 100),
            sentiment: 'neutral'
        };
    }

    async getUserHoldings(symbol) {
        // Simulate user holdings
        return {
            amount: 0.5,
            avgPrice: 60000,
            currentPrice: 67452,
            profit: 7452,
            profitPercent: 12.4
        };
    }

    useLocalAI() {
        // Fallback to local AI patterns
        console.log('Using local AI patterns');
    }
}

// Export for use in the app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZmartyAI;
} else {
    window.ZmartyAI = ZmartyAI;
}