// Help Center JavaScript

class HelpCenter {
    constructor() {
        this.searchIndex = [];
        this.faqItems = [];
        this.chatMessages = [];
        this.init();
    }

    init() {
        this.buildSearchIndex();
        this.initSearch();
        this.initFAQ();
        this.initChatWidget();
        this.initSmoothScroll();
        this.initVideoTutorials();
        this.trackPageView();
    }

    // Build search index from all help content
    buildSearchIndex() {
        const articles = [
            {
                title: "Getting Started with ZmartyChat",
                content: "Learn how to set up your account, complete KYC verification, and make your first trade",
                url: "#getting-started",
                category: "basics"
            },
            {
                title: "API Keys and Authentication",
                content: "Generate API keys, manage permissions, and secure your account",
                url: "#api-keys",
                category: "security"
            },
            {
                title: "Trading with AI Signals",
                content: "Use AI-powered signals from OpenAI, Claude, Gemini, and Grok for trading",
                url: "#ai-signals",
                category: "trading"
            },
            {
                title: "Portfolio Management",
                content: "Track your portfolio, analyze performance, and manage risk",
                url: "#portfolio",
                category: "trading"
            },
            {
                title: "Two-Factor Authentication",
                content: "Enable 2FA for enhanced account security",
                url: "#security-2fa",
                category: "security"
            },
            {
                title: "WebSocket API",
                content: "Real-time data streaming and live market updates",
                url: "#websocket",
                category: "api"
            },
            {
                title: "Circuit Breakers",
                content: "Automatic protection mechanisms for your trading",
                url: "#circuit-breakers",
                category: "trading"
            },
            {
                title: "Billing and Subscriptions",
                content: "Manage your plan, payments, and invoices",
                url: "#billing",
                category: "account"
            }
        ];

        this.searchIndex = articles;
    }

    // Initialize search functionality
    initSearch() {
        const searchInput = document.getElementById('help-search');
        const searchBtn = document.querySelector('.search-btn');

        if (searchInput) {
            // Real-time search as user types
            searchInput.addEventListener('input', (e) => {
                this.performSearch(e.target.value);
            });

            // Search on Enter key
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performSearch(e.target.value);
                }
            });
        }

        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performSearch(searchInput.value);
            });
        }

        // Popular search tags
        document.querySelectorAll('.popular-searches a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const query = link.textContent;
                searchInput.value = query;
                this.performSearch(query);
            });
        });
    }

    performSearch(query) {
        if (!query || query.length < 2) {
            this.clearSearchResults();
            return;
        }

        const results = this.searchIndex.filter(item => {
            const searchText = `${item.title} ${item.content}`.toLowerCase();
            return searchText.includes(query.toLowerCase());
        });

        this.displaySearchResults(results, query);
    }

    displaySearchResults(results, query) {
        // Create or get search results container
        let resultsContainer = document.getElementById('search-results');

        if (!resultsContainer) {
            resultsContainer = document.createElement('div');
            resultsContainer.id = 'search-results';
            resultsContainer.className = 'search-results';

            const helpContent = document.querySelector('.help-content');
            if (helpContent) {
                helpContent.insertBefore(resultsContainer, helpContent.firstChild);
            }
        }

        if (results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="search-results-header">
                    <h3>No results found for "${query}"</h3>
                    <button class="close-results">×</button>
                </div>
                <p>Try searching with different keywords or browse our categories.</p>
            `;
        } else {
            resultsContainer.innerHTML = `
                <div class="search-results-header">
                    <h3>${results.length} result${results.length > 1 ? 's' : ''} for "${query}"</h3>
                    <button class="close-results">×</button>
                </div>
                <div class="results-list">
                    ${results.map(item => `
                        <a href="${item.url}" class="result-item">
                            <h4>${this.highlightText(item.title, query)}</h4>
                            <p>${this.highlightText(item.content, query)}</p>
                            <span class="result-category">${item.category}</span>
                        </a>
                    `).join('')}
                </div>
            `;
        }

        // Add close button functionality
        const closeBtn = resultsContainer.querySelector('.close-results');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.clearSearchResults();
            });
        }

        // Smooth scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    highlightText(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    clearSearchResults() {
        const resultsContainer = document.getElementById('search-results');
        if (resultsContainer) {
            resultsContainer.remove();
        }
    }

    // Initialize FAQ accordion
    initFAQ() {
        const faqItems = document.querySelectorAll('.faq-item');

        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');

            question.addEventListener('click', () => {
                const isActive = item.classList.contains('active');

                // Close all other FAQs
                faqItems.forEach(otherItem => {
                    otherItem.classList.remove('active');
                });

                // Toggle current FAQ
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        });
    }

    // Initialize chat widget
    initChatWidget() {
        const chatToggle = document.querySelector('.chat-toggle');
        const chatWindow = document.querySelector('.chat-window');
        const chatClose = document.querySelector('.chat-close');
        const chatInput = document.querySelector('.chat-input input');
        const sendBtn = document.querySelector('.send-btn');

        if (chatToggle && chatWindow) {
            chatToggle.addEventListener('click', () => {
                chatWindow.classList.add('active');
                chatToggle.style.display = 'none';
                if (chatInput) {
                    chatInput.focus();
                }
            });
        }

        if (chatClose) {
            chatClose.addEventListener('click', () => {
                chatWindow.classList.remove('active');
                chatToggle.style.display = 'flex';
            });
        }

        if (chatInput && sendBtn) {
            const sendMessage = () => {
                const message = chatInput.value.trim();
                if (message) {
                    this.addChatMessage(message, 'user');
                    this.processChatMessage(message);
                    chatInput.value = '';
                }
            };

            sendBtn.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
    }

    addChatMessage(message, sender = 'bot') {
        const chatMessages = document.querySelector('.chat-messages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        messageDiv.innerHTML = `<p>${message}</p>`;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    processChatMessage(message) {
        // Simulate AI response
        setTimeout(() => {
            const responses = {
                'api': "You can find API documentation at /api-docs. Need help with authentication, endpoints, or integration?",
                'trading': "For trading help, check our Trading Guide. I can help with order types, AI signals, or portfolio management.",
                'account': "For account issues, visit Account Settings. Need help with verification, security, or billing?",
                'help': "I'm here to help! You can ask about:\n• Getting started\n• Trading features\n• API integration\n• Account management\n• Security settings",
                'default': "I'm searching for an answer to your question. Meanwhile, you can browse our help articles or contact support for immediate assistance."
            };

            let response = responses.default;
            const lowerMessage = message.toLowerCase();

            for (const [key, value] of Object.entries(responses)) {
                if (lowerMessage.includes(key)) {
                    response = value;
                    break;
                }
            }

            this.addChatMessage(response, 'bot');
        }, 1000);
    }

    // Smooth scroll for anchor links
    initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });

                    // Update active state in sidebar
                    this.updateActiveNav(anchor.getAttribute('href'));
                }
            });
        });
    }

    updateActiveNav(hash) {
        document.querySelectorAll('.help-nav a').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === hash) {
                link.classList.add('active');
            }
        });
    }

    // Initialize video tutorials
    initVideoTutorials() {
        const tutorialCards = document.querySelectorAll('.tutorial-card');

        tutorialCards.forEach(card => {
            card.addEventListener('click', () => {
                this.playVideo(card.querySelector('h4').textContent);
            });
        });
    }

    playVideo(title) {
        // Create video modal
        const modal = document.createElement('div');
        modal.className = 'video-modal';
        modal.innerHTML = `
            <div class="video-modal-content">
                <button class="video-close">×</button>
                <h3>${title}</h3>
                <div class="video-player">
                    <div class="video-placeholder">
                        <span>🎥</span>
                        <p>Video player would load here</p>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close modal
        modal.querySelector('.video-close').addEventListener('click', () => {
            modal.remove();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    // Track helpful votes
    trackHelpful(isHelpful) {
        console.log(`Article marked as ${isHelpful ? 'helpful' : 'not helpful'}`);

        // Show thank you message
        const promptDiv = document.querySelector('.helpful-prompt');
        if (promptDiv) {
            promptDiv.innerHTML = '<span>Thank you for your feedback!</span>';
        }

        // Send analytics
        this.trackEvent('Article Feedback', isHelpful ? 'Helpful' : 'Not Helpful');
    }

    // Analytics
    trackPageView() {
        console.log('Help Center page view tracked');
    }

    trackEvent(category, action, label = null) {
        console.log(`Event tracked: ${category} - ${action}`, label);
    }
}

// Initialize Help Center when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const helpCenter = new HelpCenter();

    // Helpful buttons
    document.querySelectorAll('.helpful-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            helpCenter.trackHelpful(btn.classList.contains('yes'));
        });
    });

    // Add search results styling
    const style = document.createElement('style');
    style.textContent = `
        .search-results {
            background: var(--bg-card);
            border-radius: 12px;
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-xl);
            border: 1px solid var(--primary-blue);
        }

        .search-results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-lg);
        }

        .close-results {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 1.5rem;
            cursor: pointer;
        }

        .results-list {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-md);
        }

        .result-item {
            display: block;
            padding: var(--spacing-md);
            background: var(--bg-dark);
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s ease;
        }

        .result-item:hover {
            background: var(--bg-card-hover);
            transform: translateX(4px);
        }

        .result-item h4 {
            color: var(--text-primary);
            margin-bottom: var(--spacing-xs);
        }

        .result-item p {
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin-bottom: var(--spacing-xs);
        }

        .result-category {
            display: inline-block;
            padding: 2px 8px;
            background: var(--bg-card);
            border-radius: 4px;
            font-size: 0.75rem;
            color: var(--primary-blue);
        }

        mark {
            background: rgba(0, 102, 255, 0.2);
            color: var(--primary-blue);
            padding: 0 2px;
            border-radius: 2px;
        }

        .video-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }

        .video-modal-content {
            background: var(--bg-card);
            border-radius: 12px;
            padding: var(--spacing-xl);
            max-width: 800px;
            width: 90%;
        }

        .video-close {
            float: right;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 2rem;
            cursor: pointer;
        }

        .video-player {
            margin-top: var(--spacing-lg);
            background: var(--bg-dark);
            border-radius: 8px;
            aspect-ratio: 16/9;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .video-placeholder {
            text-align: center;
            color: var(--text-secondary);
        }

        .video-placeholder span {
            font-size: 3rem;
            display: block;
            margin-bottom: var(--spacing-md);
        }
    `;
    document.head.appendChild(style);
});

console.log('Help Center initialized');