// ZmartTrade App - Main Application Controller
class ZmartTradeApp {
    constructor() {
        this.currentUser = null;
        this.currentScreen = 'welcome';
        this.theme = localStorage.getItem('theme') || 'light';
        this.messages = [];
        this.socket = null;
        this.isTyping = false;

        this.init();
    }

    init() {
        this.checkExistingSession();
        this.setupTheme();
        this.bindGlobalEvents();
        this.initializeScreenManager();

        if (this.currentUser) {
            this.showScreen('chat');
            this.initializeChat();
        } else {
            this.showScreen('welcome');
        }
    }

    checkExistingSession() {
        const sessionData = localStorage.getItem('zmart_session');
        if (sessionData) {
            try {
                const session = JSON.parse(sessionData);
                if (session.expiresAt > Date.now()) {
                    this.currentUser = session.user;
                    this.restoreMessages();
                }
            } catch (e) {
                localStorage.removeItem('zmart_session');
            }
        }
    }

    setupTheme() {
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(`theme-${this.theme}`);
        this.updateThemeButton();
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.theme);
        this.setupTheme();

        // Animate theme change
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }

    updateThemeButton() {
        const button = document.querySelector('.theme-button');
        if (button) {
            const sunIcon = button.querySelector('.sun-icon');
            const moonIcon = button.querySelector('.moon-icon');

            if (this.theme === 'light') {
                sunIcon?.classList.add('hidden');
                moonIcon?.classList.remove('hidden');
            } else {
                sunIcon?.classList.remove('hidden');
                moonIcon?.classList.add('hidden');
            }
        }
    }

    bindGlobalEvents() {
        // Theme toggle
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-button')) {
                this.toggleTheme();
            }
        });

        // Prevent context menu on long press (mobile)
        document.addEventListener('contextmenu', (e) => {
            if (window.innerWidth <= 768) {
                e.preventDefault();
            }
        });

        // Handle back button
        window.addEventListener('popstate', (e) => {
            if (e.state?.screen) {
                this.showScreen(e.state.screen, false);
            }
        });

        // Handle online/offline
        window.addEventListener('online', () => this.handleConnectionStatus(true));
        window.addEventListener('offline', () => this.handleConnectionStatus(false));
    }

    initializeScreenManager() {
        this.screens = {
            welcome: document.getElementById('welcomeScreen'),
            name: document.getElementById('nameScreen'),
            contact: document.getElementById('contactScreen'),
            verify: document.getElementById('verifyScreen'),
            chat: document.getElementById('chatScreen')
        };
    }

    showScreen(screenName, updateHistory = true) {
        // Hide all screens
        Object.values(this.screens).forEach(screen => {
            if (screen) {
                screen.classList.add('hidden');
                screen.classList.remove('animate-slideIn');
            }
        });

        // Show target screen
        const targetScreen = this.screens[screenName];
        if (targetScreen) {
            targetScreen.classList.remove('hidden');
            requestAnimationFrame(() => {
                targetScreen.classList.add('animate-slideIn');
            });

            this.currentScreen = screenName;

            // Update browser history
            if (updateHistory) {
                history.pushState({ screen: screenName }, '', `#${screenName}`);
            }

            // Screen-specific initialization
            this.onScreenChange(screenName);
        }
    }

    onScreenChange(screenName) {
        switch(screenName) {
            case 'chat':
                this.initializeChat();
                this.focusMessageInput();
                break;
            case 'name':
                document.getElementById('nameInput')?.focus();
                break;
            case 'contact':
                document.getElementById('phoneInput')?.focus();
                break;
            case 'verify':
                document.querySelector('.otp-input')?.focus();
                break;
        }
    }

    initializeChat() {
        if (!this.chatInitialized) {
            this.loadMessages();
            this.setupChatHeader();
            this.bindChatEvents();
            this.connectWebSocket();
            this.sendWelcomeMessage();
            this.chatInitialized = true;
        }
    }

    setupChatHeader() {
        const headerName = document.querySelector('.chat-header .contact-name');
        const headerStatus = document.querySelector('.chat-header .contact-status');

        if (headerName) headerName.textContent = 'Zmarty';
        if (headerStatus) headerStatus.textContent = 'online';

        // Add online indicator animation
        headerStatus?.classList.add('animate-pulse');
    }

    loadMessages() {
        const savedMessages = localStorage.getItem('zmart_messages');
        if (savedMessages) {
            try {
                this.messages = JSON.parse(savedMessages);
                this.renderMessages();
            } catch (e) {
                this.messages = [];
            }
        }
    }

    saveMessages() {
        localStorage.setItem('zmart_messages', JSON.stringify(this.messages));
    }

    sendWelcomeMessage() {
        if (this.messages.length === 0 && this.currentUser) {
            setTimeout(() => {
                this.receiveMessage({
                    type: 'text',
                    content: `Hey ${this.currentUser.name}! 👋 Welcome to ZmartTrade! I'm Zmarty, your AI trading assistant. I'm here to help you navigate the markets, analyze trends, and execute trades. How can I assist you today?`,
                    timestamp: new Date().toISOString()
                });
            }, 1000);
        }
    }

    connectWebSocket() {
        // WebSocket connection for real-time updates
        // This will be implemented when backend is ready
        console.log('WebSocket connection will be established when backend is ready');
    }

    bindChatEvents() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendMessage');
        const attachButton = document.querySelector('.attach-btn');
        const emojiButton = document.querySelector('.emoji-btn');
        const voiceButton = document.querySelector('.voice-btn');

        // Send message
        sendButton?.addEventListener('click', () => this.sendMessage());

        // Enter key to send
        messageInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        messageInput?.addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
            this.handleTypingIndicator();
        });

        // Attachment handling
        attachButton?.addEventListener('click', () => this.showAttachmentMenu());

        // Emoji picker
        emojiButton?.addEventListener('click', () => this.toggleEmojiPicker());

        // Voice note
        voiceButton?.addEventListener('click', () => this.startVoiceRecording());

        // Menu actions
        this.bindMenuEvents();
    }

    bindMenuEvents() {
        const menuButton = document.querySelector('.menu-btn');
        const menuDropdown = document.querySelector('.menu-dropdown');

        menuButton?.addEventListener('click', (e) => {
            e.stopPropagation();
            menuDropdown?.classList.toggle('hidden');
        });

        // Close menu when clicking outside
        document.addEventListener('click', () => {
            menuDropdown?.classList.add('hidden');
        });

        // Menu items
        document.querySelector('[data-action="new-chat"]')?.addEventListener('click', () => {
            this.clearChat();
        });

        document.querySelector('[data-action="settings"]')?.addEventListener('click', () => {
            this.showSettings();
        });

        document.querySelector('[data-action="help"]')?.addEventListener('click', () => {
            this.showHelp();
        });

        document.querySelector('[data-action="logout"]')?.addEventListener('click', () => {
            this.logout();
        });
    }

    sendMessage() {
        const input = document.getElementById('messageInput');
        const content = input?.value.trim();

        if (!content) return;

        const message = {
            id: this.generateId(),
            sender: 'user',
            type: 'text',
            content: content,
            timestamp: new Date().toISOString(),
            status: 'sending'
        };

        this.messages.push(message);
        this.renderMessage(message);
        this.saveMessages();

        // Clear input
        if (input) {
            input.value = '';
            input.style.height = 'auto';
        }

        // Send to backend
        this.sendToBackend(message);

        // Simulate Zmarty thinking
        this.showTypingIndicator();

        // Get AI response (connected to MCP)
        setTimeout(() => {
            this.hideTypingIndicator();
            this.processAIResponse(content);
        }, 1500);
    }

    sendToBackend(message) {
        // Update message status
        setTimeout(() => {
            message.status = 'sent';
            this.updateMessageStatus(message.id, 'sent');

            setTimeout(() => {
                message.status = 'delivered';
                this.updateMessageStatus(message.id, 'delivered');

                setTimeout(() => {
                    message.status = 'read';
                    this.updateMessageStatus(message.id, 'read');
                }, 500);
            }, 300);
        }, 200);
    }

    processAIResponse(userMessage) {
        // This will connect to MCP server for Claude AI
        // For now, simulate intelligent responses
        let response = this.getSmartResponse(userMessage);

        this.receiveMessage({
            type: response.type || 'text',
            content: response.content,
            metadata: response.metadata,
            timestamp: new Date().toISOString()
        });
    }

    getSmartResponse(message) {
        const lowerMessage = message.toLowerCase();

        // Trading-related responses
        if (lowerMessage.includes('price') || lowerMessage.includes('bitcoin') || lowerMessage.includes('btc')) {
            return {
                type: 'card',
                content: 'Bitcoin Price Update',
                metadata: {
                    cardType: 'price',
                    symbol: 'BTC',
                    price: '$67,452.30',
                    change: '+2.45%',
                    high: '$68,120',
                    low: '$65,890'
                }
            };
        }

        if (lowerMessage.includes('buy') || lowerMessage.includes('sell')) {
            return {
                type: 'text',
                content: `I can help you ${lowerMessage.includes('buy') ? 'buy' : 'sell'} cryptocurrency. What asset would you like to trade, and what quantity?`
            };
        }

        if (lowerMessage.includes('portfolio') || lowerMessage.includes('balance')) {
            return {
                type: 'card',
                content: 'Portfolio Overview',
                metadata: {
                    cardType: 'portfolio',
                    totalValue: '$125,430.50',
                    change24h: '+3.2%',
                    assets: [
                        { symbol: 'BTC', amount: '1.5', value: '$101,178.45' },
                        { symbol: 'ETH', amount: '10', value: '$24,252.05' }
                    ]
                }
            };
        }

        if (lowerMessage.includes('help')) {
            return {
                type: 'text',
                content: "I can help you with:\n📊 Check live prices\n💰 View your portfolio\n📈 Analyze market trends\n🔔 Set price alerts\n💱 Execute trades\n📰 Get market news\n\nWhat would you like to do?"
            };
        }

        // Default response
        return {
            type: 'text',
            content: "I'm analyzing your request. You can ask me about market prices, your portfolio, trading signals, or any crypto-related questions. How can I help you today?"
        };
    }

    receiveMessage(messageData) {
        const message = {
            id: this.generateId(),
            sender: 'zmarty',
            ...messageData
        };

        this.messages.push(message);
        this.renderMessage(message);
        this.saveMessages();

        // Play notification sound
        this.playNotificationSound();
    }

    renderMessage(message) {
        const container = document.getElementById('messagesList');
        if (!container) return;

        const messageElement = this.createMessageElement(message);
        container.appendChild(messageElement);

        // Animate message entry
        requestAnimationFrame(() => {
            messageElement.classList.add('animate-slideUp');
        });

        // Scroll to bottom
        this.scrollToBottom();
    }

    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message ${message.sender === 'user' ? 'sent' : 'received'}`;
        div.dataset.messageId = message.id;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        // Handle different message types
        if (message.type === 'card' && message.metadata) {
            bubble.innerHTML = this.createCardContent(message.metadata);
        } else {
            bubble.textContent = message.content;
        }

        // Add timestamp and status
        const meta = document.createElement('div');
        meta.className = 'message-meta';

        const time = document.createElement('span');
        time.className = 'message-time';
        time.textContent = this.formatTime(message.timestamp);
        meta.appendChild(time);

        if (message.sender === 'user') {
            const status = document.createElement('span');
            status.className = `message-status ${message.status || ''}`;
            status.innerHTML = this.getStatusIcon(message.status);
            meta.appendChild(status);
        }

        bubble.appendChild(meta);
        div.appendChild(bubble);

        return div;
    }

    createCardContent(metadata) {
        if (metadata.cardType === 'price') {
            return `
                <div class="price-card">
                    <div class="price-header">
                        <span class="symbol">${metadata.symbol}</span>
                        <span class="change ${metadata.change.startsWith('+') ? 'positive' : 'negative'}">${metadata.change}</span>
                    </div>
                    <div class="price-value">${metadata.price}</div>
                    <div class="price-range">
                        <span>H: ${metadata.high}</span>
                        <span>L: ${metadata.low}</span>
                    </div>
                </div>
            `;
        }

        if (metadata.cardType === 'portfolio') {
            const assetsHtml = metadata.assets.map(asset =>
                `<div class="asset-row">
                    <span>${asset.symbol}: ${asset.amount}</span>
                    <span>${asset.value}</span>
                </div>`
            ).join('');

            return `
                <div class="portfolio-card">
                    <div class="portfolio-header">
                        <div class="total-value">${metadata.totalValue}</div>
                        <span class="change ${metadata.change24h.startsWith('+') ? 'positive' : 'negative'}">${metadata.change24h}</span>
                    </div>
                    <div class="assets-list">${assetsHtml}</div>
                </div>
            `;
        }

        return '';
    }

    getStatusIcon(status) {
        switch(status) {
            case 'sending': return '🕐';
            case 'sent': return '✓';
            case 'delivered': return '✓✓';
            case 'read': return '<span class="text-green">✓✓</span>';
            default: return '';
        }
    }

    updateMessageStatus(messageId, status) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        const statusElement = messageElement?.querySelector('.message-status');

        if (statusElement) {
            statusElement.className = `message-status ${status}`;
            statusElement.innerHTML = this.getStatusIcon(status);
        }

        // Update in messages array
        const message = this.messages.find(m => m.id === messageId);
        if (message) {
            message.status = status;
            this.saveMessages();
        }
    }

    showTypingIndicator() {
        const container = document.getElementById('messagesList');
        if (!container || this.isTyping) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message received typing-indicator';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-bubble">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;

        container.appendChild(typingDiv);
        this.scrollToBottom();
        this.isTyping = true;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
            this.isTyping = false;
        }
    }

    handleTypingIndicator() {
        // This would send typing status to other user via WebSocket
        // For now, just log it
        console.log('User is typing...');
    }

    renderMessages() {
        const container = document.getElementById('messagesList');
        if (!container) return;

        container.innerHTML = '';
        this.messages.forEach(message => {
            this.renderMessage(message);
        });
    }

    clearChat() {
        if (confirm('Clear all messages? This cannot be undone.')) {
            this.messages = [];
            this.saveMessages();
            this.renderMessages();
            this.sendWelcomeMessage();
        }
    }

    showSettings() {
        // Implement settings modal
        alert('Settings coming soon!');
    }

    showHelp() {
        this.receiveMessage({
            type: 'text',
            content: "📚 **Help Menu**\n\nHere are some things you can try:\n• 'Show BTC price' - Get latest Bitcoin price\n• 'My portfolio' - View your holdings\n• 'Buy 0.1 BTC' - Execute a trade\n• 'Market analysis' - Get AI-powered insights\n• 'Set alert BTC > 70000' - Price alerts\n• 'Latest crypto news' - Market updates\n\nNeed more help? Just ask!",
            timestamp: new Date().toISOString()
        });
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('zmart_session');
            localStorage.removeItem('zmart_messages');
            this.currentUser = null;
            this.messages = [];
            this.chatInitialized = false;
            this.showScreen('welcome');
        }
    }

    showAttachmentMenu() {
        // Implement attachment menu
        console.log('Attachment menu coming soon');
    }

    toggleEmojiPicker() {
        // Implement emoji picker
        console.log('Emoji picker coming soon');
    }

    startVoiceRecording() {
        // Implement voice recording
        console.log('Voice recording coming soon');
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    scrollToBottom() {
        const container = document.querySelector('.messages-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    focusMessageInput() {
        setTimeout(() => {
            document.getElementById('messageInput')?.focus();
        }, 100);
    }

    handleConnectionStatus(isOnline) {
        const statusElement = document.querySelector('.contact-status');
        if (statusElement) {
            statusElement.textContent = isOnline ? 'online' : 'offline';
            statusElement.classList.toggle('offline', !isOnline);
        }
    }

    playNotificationSound() {
        // Play notification sound when receiving messages
        // Audio file to be added
    }

    generateId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    restoreMessages() {
        const savedMessages = localStorage.getItem('zmart_messages');
        if (savedMessages) {
            try {
                this.messages = JSON.parse(savedMessages);
            } catch (e) {
                this.messages = [];
            }
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.zmartApp = new ZmartTradeApp();
});