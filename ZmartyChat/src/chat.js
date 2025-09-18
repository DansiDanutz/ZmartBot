// ZmartTrade - Chat Module with MCP Integration
class ChatManager {
    constructor(app) {
        this.app = app;
        this.mcpClient = null;
        this.messageQueue = [];
        this.isProcessing = false;
        this.tradingTools = [
            'get_market_data',
            'analyze_trading_signal',
            'get_portfolio_status',
            'execute_trade',
            'get_risk_analysis',
            'get_news',
            'set_alerts',
            'get_chart'
        ];

        this.init();
    }

    init() {
        this.setupMCPConnection();
        this.setupQuickActions();
        this.setupVoiceCommands();
        this.setupMessageContextMenu();
    }

    async setupMCPConnection() {
        try {
            // Initialize MCP client connection
            // This will connect to the MCP server for Claude AI integration
            console.log('Initializing MCP connection for Claude AI...');

            // In production, this would connect to the actual MCP server
            this.mcpClient = {
                connected: false,
                async call(tool, params) {
                    // Simulate MCP tool calls
                    return ChatManager.simulateMCPToolCall(tool, params);
                }
            };

            // Simulate connection
            setTimeout(() => {
                this.mcpClient.connected = true;
                console.log('MCP connection established');
            }, 1000);

        } catch (error) {
            console.error('Failed to setup MCP connection:', error);
        }
    }

    setupQuickActions() {
        // Add quick action buttons below input
        const quickActionsHTML = `
            <div class="quick-actions">
                <button class="quick-action-btn" data-action="market-overview">📊 Market Overview</button>
                <button class="quick-action-btn" data-action="portfolio">💼 Portfolio</button>
                <button class="quick-action-btn" data-action="buy-crypto">💰 Buy Crypto</button>
                <button class="quick-action-btn" data-action="price-alerts">🔔 Alerts</button>
                <button class="quick-action-btn" data-action="news">📰 News</button>
            </div>
        `;

        const inputBar = document.querySelector('.input-bar');
        if (inputBar && !document.querySelector('.quick-actions')) {
            inputBar.insertAdjacentHTML('beforebegin', quickActionsHTML);
            this.bindQuickActions();
        }
    }

    bindQuickActions() {
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            });
        });
    }

    async handleQuickAction(action) {
        const actionMessages = {
            'market-overview': 'Show me the current market overview',
            'portfolio': 'Display my portfolio',
            'buy-crypto': 'I want to buy cryptocurrency',
            'price-alerts': 'Show my price alerts',
            'news': 'Get me the latest crypto news'
        };

        const message = actionMessages[action];
        if (message) {
            // Simulate user sending the message
            document.getElementById('messageInput').value = message;
            this.app.sendMessage();
        }
    }

    async processMessageWithMCP(message) {
        if (!this.mcpClient?.connected) {
            return this.getFallbackResponse(message);
        }

        try {
            // Determine which MCP tools to use based on message content
            const tools = this.determineRequiredTools(message);
            const results = [];

            for (const tool of tools) {
                const params = this.extractToolParams(message, tool);
                const result = await this.mcpClient.call(tool, params);
                results.push(result);
            }

            return this.formatMCPResponse(results, message);

        } catch (error) {
            console.error('MCP processing error:', error);
            return this.getFallbackResponse(message);
        }
    }

    determineRequiredTools(message) {
        const lowerMessage = message.toLowerCase();
        const tools = [];

        if (lowerMessage.includes('price') || lowerMessage.includes('cost')) {
            tools.push('get_market_data');
        }
        if (lowerMessage.includes('portfolio') || lowerMessage.includes('holdings')) {
            tools.push('get_portfolio_status');
        }
        if (lowerMessage.includes('buy') || lowerMessage.includes('sell')) {
            tools.push('execute_trade');
        }
        if (lowerMessage.includes('risk') || lowerMessage.includes('analysis')) {
            tools.push('get_risk_analysis');
        }
        if (lowerMessage.includes('news') || lowerMessage.includes('update')) {
            tools.push('get_news');
        }
        if (lowerMessage.includes('alert') || lowerMessage.includes('notify')) {
            tools.push('set_alerts');
        }
        if (lowerMessage.includes('chart') || lowerMessage.includes('graph')) {
            tools.push('get_chart');
        }
        if (lowerMessage.includes('signal') || lowerMessage.includes('trend')) {
            tools.push('analyze_trading_signal');
        }

        return tools.length > 0 ? tools : ['analyze_trading_signal'];
    }

    extractToolParams(message, tool) {
        const params = {};
        const lowerMessage = message.toLowerCase();

        switch(tool) {
            case 'get_market_data':
                // Extract cryptocurrency symbols
                const cryptos = ['btc', 'eth', 'sol', 'ada', 'dot', 'bnb'];
                for (const crypto of cryptos) {
                    if (lowerMessage.includes(crypto)) {
                        params.symbol = crypto.toUpperCase();
                        break;
                    }
                }
                params.symbol = params.symbol || 'BTC';
                break;

            case 'execute_trade':
                params.action = lowerMessage.includes('sell') ? 'sell' : 'buy';
                // Extract amount
                const amountMatch = message.match(/(\d+\.?\d*)/);
                if (amountMatch) {
                    params.amount = parseFloat(amountMatch[1]);
                }
                break;

            case 'set_alerts':
                // Extract price levels
                const priceMatch = message.match(/\$?(\d+,?\d*)/);
                if (priceMatch) {
                    params.price = parseFloat(priceMatch[1].replace(',', ''));
                }
                params.type = lowerMessage.includes('above') ? 'above' : 'below';
                break;
        }

        return params;
    }

    formatMCPResponse(results, originalMessage) {
        // Format the MCP tool results into a chat response
        if (results.length === 0) {
            return {
                type: 'text',
                content: 'I processed your request but couldn\'t find specific data. Could you please be more specific?'
            };
        }

        const firstResult = results[0];

        // Return formatted response based on tool type
        if (firstResult.tool === 'get_market_data') {
            return {
                type: 'card',
                content: 'Market Data',
                metadata: firstResult.data
            };
        } else if (firstResult.tool === 'get_portfolio_status') {
            return {
                type: 'card',
                content: 'Portfolio Status',
                metadata: {
                    cardType: 'portfolio',
                    ...firstResult.data
                }
            };
        } else {
            return {
                type: 'text',
                content: firstResult.response || 'Request processed successfully.'
            };
        }
    }

    getFallbackResponse(message) {
        // Fallback responses when MCP is not available
        return {
            type: 'text',
            content: `I'm processing your request: "${message}". The AI service is currently connecting. Please try again in a moment.`
        };
    }

    static simulateMCPToolCall(tool, params) {
        // Simulate MCP tool responses for demo
        const responses = {
            get_market_data: {
                tool: 'get_market_data',
                data: {
                    cardType: 'price',
                    symbol: params.symbol || 'BTC',
                    price: '$67,452.30',
                    change: '+2.45%',
                    high: '$68,120',
                    low: '$65,890',
                    volume: '$24.5B',
                    marketCap: '$1.32T'
                }
            },
            get_portfolio_status: {
                tool: 'get_portfolio_status',
                data: {
                    totalValue: '$125,430.50',
                    change24h: '+3.2%',
                    pnl: '+$3,890.25',
                    assets: [
                        { symbol: 'BTC', amount: '1.5', value: '$101,178.45', change: '+2.1%' },
                        { symbol: 'ETH', amount: '10', value: '$24,252.05', change: '+4.5%' }
                    ]
                }
            },
            analyze_trading_signal: {
                tool: 'analyze_trading_signal',
                response: '📈 **Trading Signal Analysis**\n\nBased on current market conditions:\n• Trend: Bullish momentum detected\n• RSI: 58 (Neutral)\n• MACD: Positive crossover\n• Support: $65,000 | Resistance: $70,000\n\n**Recommendation**: Consider taking partial profits near resistance levels. Market sentiment remains positive with increasing institutional interest.'
            },
            execute_trade: {
                tool: 'execute_trade',
                response: `✅ Trade Order Placed\n\n${params.action === 'buy' ? '🟢 BUY' : '🔴 SELL'} Order\nAmount: ${params.amount || '0.1'} BTC\nPrice: Market\nEstimated Total: $${((params.amount || 0.1) * 67452).toFixed(2)}\n\nYour order has been submitted and will be executed at the best available price.`
            },
            get_risk_analysis: {
                tool: 'get_risk_analysis',
                response: '⚠️ **Risk Analysis**\n\n• Portfolio Risk Score: 6.5/10 (Moderate)\n• Volatility: High (24h: ±4.2%)\n• Correlation Risk: Low\n• Suggested Stop Loss: -5%\n• Position Sizing: Max 10% per trade\n\nYour portfolio shows balanced risk with good diversification.'
            },
            get_news: {
                tool: 'get_news',
                response: '📰 **Latest Crypto News**\n\n1. 🔥 **Bitcoin ETF Sees Record Inflows**\n   Institutional investors pour $500M into spot Bitcoin ETFs\n\n2. 💎 **Ethereum Upgrade Successfully Deployed**\n   Gas fees reduced by 30% following latest network upgrade\n\n3. 🏦 **Major Bank Announces Crypto Services**\n   JPMorgan to offer cryptocurrency trading to retail clients'
            },
            set_alerts: {
                tool: 'set_alerts',
                response: `🔔 **Price Alert Set**\n\nI've set an alert for BTC ${params.type || 'above'} $${params.price || '70,000'}\n\nYou'll receive a notification when this price level is reached.`
            },
            get_chart: {
                tool: 'get_chart',
                response: '📊 **Price Chart Generated**\n\n[Chart would be displayed here]\n\nBTC/USD 1D Chart\n• Current: $67,452\n• 24h Change: +2.45%\n• Trend: Upward\n• Volume: Increasing'
            }
        };

        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(responses[tool] || {
                    tool: tool,
                    response: `Tool ${tool} executed successfully with params: ${JSON.stringify(params)}`
                });
            }, 500);
        });
    }

    setupVoiceCommands() {
        // Setup voice recognition for voice commands
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.handleVoiceCommand(transcript);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
            };
        }
    }

    startVoiceRecording() {
        if (this.recognition) {
            this.recognition.start();
            this.showVoiceRecordingUI();
        } else {
            alert('Voice recognition is not supported in your browser');
        }
    }

    stopVoiceRecording() {
        if (this.recognition) {
            this.recognition.stop();
            this.hideVoiceRecordingUI();
        }
    }

    handleVoiceCommand(transcript) {
        // Process voice command
        document.getElementById('messageInput').value = transcript;
        this.app.sendMessage();
    }

    showVoiceRecordingUI() {
        const voiceBtn = document.querySelector('.voice-btn');
        if (voiceBtn) {
            voiceBtn.classList.add('recording');
            voiceBtn.innerHTML = '🔴';
        }
    }

    hideVoiceRecordingUI() {
        const voiceBtn = document.querySelector('.voice-btn');
        if (voiceBtn) {
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '🎤';
        }
    }

    setupMessageContextMenu() {
        // Add context menu for messages (copy, forward, delete, star)
        document.addEventListener('contextmenu', (e) => {
            const messageEl = e.target.closest('.message-bubble');
            if (messageEl) {
                e.preventDefault();
                this.showMessageContextMenu(e, messageEl);
            }
        });
    }

    showMessageContextMenu(event, messageEl) {
        // Remove existing context menu
        const existingMenu = document.querySelector('.message-context-menu');
        if (existingMenu) existingMenu.remove();

        const menu = document.createElement('div');
        menu.className = 'message-context-menu';
        menu.innerHTML = `
            <div class="context-menu-item" data-action="copy">📋 Copy</div>
            <div class="context-menu-item" data-action="star">⭐ Star</div>
            <div class="context-menu-item" data-action="forward">↗️ Forward</div>
            <div class="context-menu-item" data-action="delete">🗑️ Delete</div>
        `;

        menu.style.position = 'fixed';
        menu.style.left = `${event.clientX}px`;
        menu.style.top = `${event.clientY}px`;

        document.body.appendChild(menu);

        // Handle menu actions
        menu.querySelectorAll('.context-menu-item').forEach(item => {
            item.addEventListener('click', () => {
                this.handleMessageAction(item.dataset.action, messageEl);
                menu.remove();
            });
        });

        // Close menu on click outside
        setTimeout(() => {
            document.addEventListener('click', () => menu.remove(), { once: true });
        }, 100);
    }

    handleMessageAction(action, messageEl) {
        const messageText = messageEl.textContent;

        switch(action) {
            case 'copy':
                navigator.clipboard.writeText(messageText);
                this.showToast('Message copied');
                break;
            case 'star':
                messageEl.classList.toggle('starred');
                this.showToast(messageEl.classList.contains('starred') ? 'Message starred' : 'Star removed');
                break;
            case 'forward':
                // Open forward dialog
                this.showToast('Forward feature coming soon');
                break;
            case 'delete':
                if (confirm('Delete this message?')) {
                    messageEl.closest('.message').remove();
                    this.showToast('Message deleted');
                }
                break;
        }
    }

    showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast animate-slideUp';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('animate-fadeOut');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }

    // Advanced trading features
    async executeTrade(params) {
        // Show trade confirmation dialog
        const confirmed = await this.showTradeConfirmation(params);
        if (!confirmed) return;

        // Execute trade via MCP
        const result = await this.mcpClient.call('execute_trade', params);

        // Show result
        this.app.receiveMessage({
            type: 'card',
            content: 'Trade Executed',
            metadata: result.data
        });
    }

    showTradeConfirmation(params) {
        return new Promise((resolve) => {
            const dialog = document.createElement('div');
            dialog.className = 'trade-confirmation-dialog';
            dialog.innerHTML = `
                <div class="dialog-content">
                    <h3>Confirm Trade</h3>
                    <div class="trade-details">
                        <p>Action: ${params.action}</p>
                        <p>Symbol: ${params.symbol}</p>
                        <p>Amount: ${params.amount}</p>
                        <p>Price: ${params.price || 'Market'}</p>
                    </div>
                    <div class="dialog-buttons">
                        <button class="btn-cancel">Cancel</button>
                        <button class="btn-confirm">Confirm</button>
                    </div>
                </div>
            `;

            document.body.appendChild(dialog);

            dialog.querySelector('.btn-confirm').onclick = () => {
                dialog.remove();
                resolve(true);
            };

            dialog.querySelector('.btn-cancel').onclick = () => {
                dialog.remove();
                resolve(false);
            };
        });
    }

    // Emoji picker
    showEmojiPicker() {
        const emojis = ['😀', '😍', '🤔', '😎', '🚀', '💰', '📈', '📉', '💎', '🔥', '⚡', '💪', '👍', '👎', '❤️', '💚'];

        const picker = document.createElement('div');
        picker.className = 'emoji-picker';
        picker.innerHTML = `
            <div class="emoji-grid">
                ${emojis.map(e => `<span class="emoji-item">${e}</span>`).join('')}
            </div>
        `;

        const emojiBtn = document.querySelector('.emoji-btn');
        const rect = emojiBtn.getBoundingClientRect();
        picker.style.bottom = `${window.innerHeight - rect.top + 10}px`;
        picker.style.left = `${rect.left}px`;

        document.body.appendChild(picker);

        picker.querySelectorAll('.emoji-item').forEach(item => {
            item.addEventListener('click', () => {
                const input = document.getElementById('messageInput');
                input.value += item.textContent;
                picker.remove();
            });
        });

        setTimeout(() => {
            document.addEventListener('click', () => picker.remove(), { once: true });
        }, 100);
    }
}

// Initialize chat manager when app is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.zmartApp) {
            window.zmartChat = new ChatManager(window.zmartApp);

            // Override app's process AI response to use MCP
            window.zmartApp.processAIResponse = async function(userMessage) {
                window.zmartApp.hideTypingIndicator();
                const response = await window.zmartChat.processMessageWithMCP(userMessage);
                window.zmartApp.receiveMessage(response);
            };

            // Override voice recording
            window.zmartApp.startVoiceRecording = function() {
                window.zmartChat.startVoiceRecording();
            };

            // Override emoji picker
            window.zmartApp.toggleEmojiPicker = function() {
                window.zmartChat.showEmojiPicker();
            };
        }
    }, 200);
});