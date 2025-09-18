// Zmarty AI System Initializer
// Activates Zmarty after user registration and connects all systems

class ZmartyInitializer {
    constructor() {
        this.zmartyAI = null;
        this.manusConnector = null;
        this.isInitialized = false;
        this.initPromise = null;
    }

    // Main initialization after user registration
    async activateAfterRegistration(userData) {
        console.log(`🚀 Activating Zmarty for ${userData.name}...`);

        if (this.isInitialized) {
            console.log('Zmarty already active');
            return this.zmartyAI;
        }

        // Prevent multiple initialization attempts
        if (this.initPromise) {
            return this.initPromise;
        }

        this.initPromise = this.initialize(userData);
        const result = await this.initPromise;
        this.initPromise = null;
        return result;
    }

    async initialize(userData) {
        try {
            // Step 1: Create Zmarty AI instance
            console.log('1️⃣ Initializing Zmarty AI core...');
            this.zmartyAI = new ZmartyAI();
            this.zmartyAI.userProfile = userData;

            // Step 2: Connect to Manus Webhook system
            console.log('2️⃣ Connecting to Manus Webhook system...');
            this.manusConnector = new ZmartyManusConnector(this.zmartyAI);

            // Step 3: Initialize voice capabilities
            console.log('3️⃣ Setting up voice synthesis...');
            await this.setupVoiceCapabilities();

            // Step 4: Load user preferences and history
            console.log('4️⃣ Loading user preferences...');
            await this.loadUserContext(userData);

            // Step 5: Establish real-time connections
            console.log('5️⃣ Establishing real-time connections...');
            await this.establishConnections();

            // Step 6: Send welcome message
            console.log('6️⃣ Preparing personalized welcome...');
            await this.sendWelcomeSequence(userData);

            this.isInitialized = true;
            console.log('✅ Zmarty fully activated and ready!');

            // Make globally available
            window.zmartyAI = this.zmartyAI;
            window.zmartyManusConnector = this.manusConnector;

            return this.zmartyAI;

        } catch (error) {
            console.error('Failed to initialize Zmarty:', error);
            throw error;
        }
    }

    async setupVoiceCapabilities() {
        // Check for ElevenLabs API key
        const elevenLabsKey = process.env.ELEVENLABS_API_KEY || localStorage.getItem('elevenlabs_key');

        if (elevenLabsKey) {
            console.log('Using ElevenLabs for premium voice');
            // Premium voice setup done in ZmartyAI
        } else {
            console.log('Using browser TTS for voice');
            // Request speech synthesis permission
            if ('speechSynthesis' in window) {
                const voices = speechSynthesis.getVoices();
                console.log(`Found ${voices.length} voice options`);
            }
        }
    }

    async loadUserContext(userData) {
        try {
            // Load from localStorage
            const savedContext = localStorage.getItem(`zmarty_context_${userData.id}`);
            if (savedContext) {
                const context = JSON.parse(savedContext);

                // Restore conversation history
                if (context.conversations) {
                    this.zmartyAI.conversationContext = context.conversations;
                }

                // Restore user preferences
                if (context.preferences) {
                    context.preferences.forEach(([key, value]) => {
                        this.zmartyAI.personality.memory.set(key, value);
                    });
                }

                console.log('Restored user context');
            }

            // Load from backend
            const response = await fetch(`http://localhost:8000/api/users/${userData.id}/context`);
            if (response.ok) {
                const backendContext = await response.json();

                // Merge with local context
                if (backendContext.trading_preferences) {
                    this.zmartyAI.personality.memory.set('trading_style', backendContext.trading_preferences.style);
                    this.zmartyAI.personality.memory.set('risk_tolerance', backendContext.trading_preferences.risk);
                }

                if (backendContext.portfolio) {
                    this.zmartyAI.personality.memory.set('portfolio', backendContext.portfolio);
                }
            }

        } catch (error) {
            console.warn('Could not load full context:', error);
        }
    }

    async establishConnections() {
        // Ensure Manus connection is established
        if (!this.manusConnector.isConnected) {
            await this.manusConnector.connectToManus();
        }

        // Setup WebSocket for real-time updates
        if (!this.manusConnector.websocket ||
            this.manusConnector.websocket.readyState !== WebSocket.OPEN) {
            await this.manusConnector.establishWebSocket();
        }

        // Register for proactive notifications
        await this.registerForNotifications();
    }

    async registerForNotifications() {
        try {
            const response = await fetch('http://localhost:8000/api/notifications/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.zmartyAI.userProfile.id,
                    service: 'zmarty',
                    types: [
                        'price_alerts',
                        'trading_signals',
                        'portfolio_updates',
                        'market_news',
                        'risk_alerts'
                    ]
                })
            });

            if (response.ok) {
                console.log('Registered for notifications');
            }
        } catch (error) {
            console.warn('Notification registration failed:', error);
        }
    }

    async sendWelcomeSequence(userData) {
        // Delay for natural feel
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Send personalized welcome based on time and user
        const hour = new Date().getHours();
        let greeting = '';
        let followUp = '';

        if (hour < 12) {
            greeting = `Good morning ${userData.name}! ☀️ Welcome to ZmartTrade!`;
            followUp = `The markets are ${this.getMarketStatus()} today. I'm Zmarty, your AI trading companion, and I'm pumped to help you navigate the crypto world!`;
        } else if (hour < 17) {
            greeting = `Hey ${userData.name}! 🚀 Perfect timing to join ZmartTrade!`;
            followUp = `I'm Zmarty, your personal AI trading assistant. The afternoon session is showing some interesting opportunities. Ready to explore?`;
        } else {
            greeting = `Welcome ${userData.name}! 🌙 Great to have you on ZmartTrade!`;
            followUp = `I'm Zmarty, and I'll be your guide through the crypto markets. Even though it's evening, the crypto world never sleeps!`;
        }

        // Send initial greeting
        await this.sendMessage(greeting, 'welcome', true);

        // Short pause
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Send follow-up
        await this.sendMessage(followUp, 'introduction', true);

        // Another pause
        await new Promise(resolve => setTimeout(resolve, 2500));

        // Send capabilities message
        const capabilities = `Here's what I can do for you:
📊 Real-time market analysis with AI insights
💰 Smart trading signals from multiple agents
📈 Portfolio tracking and optimization
🎓 Personalized trading education
🔔 Instant alerts for opportunities
💬 24/7 support and guidance

What would you like to explore first?`;

        await this.sendMessage(capabilities, 'capabilities', false);

        // Set up quick action buttons
        this.setupQuickActions();
    }

    async sendMessage(content, type, shouldSpeak) {
        const message = {
            id: this.generateId(),
            sender: 'zmarty',
            type: type,
            content: content,
            timestamp: new Date().toISOString(),
            shouldSpeak: shouldSpeak
        };

        // Add to conversation context
        this.zmartyAI.conversationContext.push(message);

        // Display in chat
        if (window.zmartApp) {
            window.zmartApp.receiveMessage(message);
        }

        // Speak if enabled
        if (shouldSpeak && this.zmartyAI.voiceEngine) {
            this.zmartyAI.speak(content);
        }
    }

    setupQuickActions() {
        // Add quick action buttons for new users
        const actions = [
            { label: '📊 Market Overview', action: 'market_overview' },
            { label: '🎓 Learn Trading', action: 'education' },
            { label: '💼 Start Portfolio', action: 'create_portfolio' },
            { label: '⚙️ Settings', action: 'settings' }
        ];

        // Display actions in chat
        if (window.zmartApp) {
            const actionMessage = {
                id: this.generateId(),
                sender: 'zmarty',
                type: 'action_buttons',
                content: 'Quick Actions:',
                actions: actions,
                timestamp: new Date().toISOString()
            };

            window.zmartApp.receiveMessage(actionMessage);
        }
    }

    getMarketStatus() {
        const statuses = ['looking bullish 📈', 'showing volatility ⚡', 'relatively stable 💫', 'quite active 🔥'];
        return statuses[Math.floor(Math.random() * statuses.length)];
    }

    generateId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Save context periodically
    startContextSaver() {
        setInterval(() => {
            if (this.zmartyAI && this.zmartyAI.userProfile) {
                const context = {
                    conversations: this.zmartyAI.conversationContext.slice(-50), // Last 50 messages
                    preferences: Array.from(this.zmartyAI.personality.memory.entries()),
                    lastSaved: new Date().toISOString()
                };

                localStorage.setItem(
                    `zmarty_context_${this.zmartyAI.userProfile.id}`,
                    JSON.stringify(context)
                );
            }
        }, 60000); // Save every minute
    }

    // Handle user logout
    async deactivate() {
        console.log('Deactivating Zmarty...');

        // Save final context
        if (this.zmartyAI && this.zmartyAI.userProfile) {
            const context = {
                conversations: this.zmartyAI.conversationContext,
                preferences: Array.from(this.zmartyAI.personality.memory.entries()),
                lastSaved: new Date().toISOString()
            };

            localStorage.setItem(
                `zmarty_context_${this.zmartyAI.userProfile.id}`,
                JSON.stringify(context)
            );
        }

        // Close connections
        if (this.manusConnector?.websocket) {
            this.manusConnector.websocket.close();
        }

        // Reset state
        this.zmartyAI = null;
        this.manusConnector = null;
        this.isInitialized = false;

        console.log('Zmarty deactivated');
    }
}

// Create global initializer instance
window.zmartyInitializer = new ZmartyInitializer();

// Auto-activate when user completes registration
document.addEventListener('DOMContentLoaded', () => {
    // Listen for registration completion
    window.addEventListener('userRegistered', async (event) => {
        const userData = event.detail;
        console.log('User registered, activating Zmarty:', userData);

        try {
            await window.zmartyInitializer.activateAfterRegistration(userData);
            console.log('🎉 Zmarty successfully activated for', userData.name);
        } catch (error) {
            console.error('Failed to activate Zmarty:', error);
        }
    });

    // Also check if user is already logged in
    setTimeout(() => {
        if (window.zmartApp?.currentUser) {
            console.log('User already logged in, activating Zmarty');
            window.zmartyInitializer.activateAfterRegistration(window.zmartApp.currentUser);
        }
    }, 1000);
});

// Handle app integration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZmartyInitializer;
}