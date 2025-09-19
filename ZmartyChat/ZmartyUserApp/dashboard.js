// Dashboard JavaScript - WhatsApp Style Interactions

document.addEventListener('DOMContentLoaded', function() {

    // Tab Navigation
    const tabs = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update active content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${targetTab}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });

    // Quick Actions
    const quickActions = document.querySelectorAll('.quick-action-chip');
    quickActions.forEach(action => {
        action.addEventListener('click', () => {
            const actionText = action.querySelector('span:last-child').textContent;
            handleQuickAction(actionText);
        });
    });

    // Chat Items
    const chatItems = document.querySelectorAll('.chat-item');
    chatItems.forEach(chat => {
        chat.addEventListener('click', () => {
            const chatName = chat.querySelector('.chat-name').textContent;
            openChat(chatName);
        });
    });

    // Floating Action Button
    const fab = document.getElementById('newChatBtn');
    if (fab) {
        fab.addEventListener('click', () => {
            startNewChat();
        });
    }

    // Header Actions
    document.getElementById('searchBtn')?.addEventListener('click', () => {
        showSearch();
    });

    document.getElementById('notificationBtn')?.addEventListener('click', () => {
        showNotifications();
    });

    document.getElementById('menuBtn')?.addEventListener('click', () => {
        showMenu();
    });

    // AI Provider Selection
    const aiProviders = document.querySelectorAll('.ai-provider-chip');
    aiProviders.forEach(provider => {
        provider.addEventListener('click', () => {
            aiProviders.forEach(p => p.classList.remove('active'));
            provider.classList.add('active');
            filterSignalsByProvider(provider);
        });
    });

    // Tool Cards
    const toolCards = document.querySelectorAll('.tool-card');
    toolCards.forEach(tool => {
        tool.addEventListener('click', () => {
            const toolName = tool.querySelector('.tool-name').textContent;
            openTool(toolName);
        });
    });

    // Functions
    function handleQuickAction(action) {
        console.log('Quick action:', action);
        switch(action) {
            case 'Quick Trade':
                openQuickTrade();
                break;
            case 'BTC Price':
                showBTCPrice();
                break;
            case 'Hot Coins':
                showHotCoins();
                break;
            case 'Whale Alert':
                showWhaleAlerts();
                break;
        }
    }

    function openChat(chatName) {
        console.log('Opening chat:', chatName);
        // Navigate to chat interface
        window.location.href = `chat.html?chat=${encodeURIComponent(chatName)}`;
    }

    function startNewChat() {
        console.log('Starting new chat');
        showNewChatModal();
    }

    function showSearch() {
        console.log('Showing search');
        // Implement search overlay
    }

    function showNotifications() {
        console.log('Showing notifications');
        // Clear notification badge
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.style.display = 'none';
        }
        // Show notification panel
    }

    function showMenu() {
        console.log('Showing menu');
        showMenuModal();
    }

    function filterSignalsByProvider(provider) {
        const providerName = provider.querySelector('span:last-child').textContent;
        console.log('Filtering signals by:', providerName);
        // Implement signal filtering
    }

    function openTool(toolName) {
        console.log('Opening tool:', toolName);
        // Implement tool opening
    }

    function openQuickTrade() {
        console.log('Opening quick trade');
        // Implement quick trade modal
    }

    function showBTCPrice() {
        // Simulate fetching BTC price
        const price = '$65,432.21';
        const change = '+2.34%';
        showToast(`BTC: ${price} (${change})`);
    }

    function showHotCoins() {
        console.log('Showing hot coins');
        // Implement hot coins panel
    }

    function showWhaleAlerts() {
        console.log('Showing whale alerts');
        // Implement whale alerts
    }

    function showNewChatModal() {
        const modal = createModal('New Chat', `
            <div class="modal-options">
                <button class="modal-option" onclick="startAIChat()">
                    <span class="option-icon">🤖</span>
                    <span class="option-text">AI Assistant</span>
                </button>
                <button class="modal-option" onclick="startGroupChat()">
                    <span class="option-icon">👥</span>
                    <span class="option-text">Create Group</span>
                </button>
                <button class="modal-option" onclick="startSignalChannel()">
                    <span class="option-icon">📊</span>
                    <span class="option-text">Signal Channel</span>
                </button>
            </div>
        `);
        document.body.appendChild(modal);
    }

    function showMenuModal() {
        const modal = createModal('Menu', `
            <div class="modal-menu">
                <button class="menu-item" onclick="openSettings()">
                    <span class="menu-icon">⚙️</span>
                    <span>Settings</span>
                </button>
                <button class="menu-item" onclick="openProfile()">
                    <span class="menu-icon">👤</span>
                    <span>Profile</span>
                </button>
                <button class="menu-item" onclick="openHelp()">
                    <span class="menu-icon">❓</span>
                    <span>Help & Support</span>
                </button>
                <button class="menu-item" onclick="logout()">
                    <span class="menu-icon">🚪</span>
                    <span>Logout</span>
                </button>
            </div>
        `);
        document.body.appendChild(modal);
    }

    function createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" onclick="closeModal(this)">&times;</button>
                </div>
                <div class="modal-content">
                    ${content}
                </div>
            </div>
        `;
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        return modal;
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 100);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Global functions for modal actions
    window.closeModal = function(btn) {
        btn.closest('.modal-overlay').remove();
    };

    window.startAIChat = function() {
        console.log('Starting AI chat');
        closeModal(document.querySelector('.modal-close'));
        openChat('Zmarty AI Assistant');
    };

    window.startGroupChat = function() {
        console.log('Starting group chat');
        closeModal(document.querySelector('.modal-close'));
    };

    window.startSignalChannel = function() {
        console.log('Starting signal channel');
        closeModal(document.querySelector('.modal-close'));
    };

    window.openSettings = function() {
        window.location.href = 'settings.html';
    };

    window.openProfile = function() {
        window.location.href = 'profile.html';
    };

    window.openHelp = function() {
        window.location.href = 'help.html';
    };

    window.logout = function() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.clear();
            window.location.href = 'index.html';
        }
    };

    // Add animation on load
    setTimeout(() => {
        document.querySelectorAll('.chat-item, .stat-card, .tool-card, .signal-card').forEach((el, i) => {
            setTimeout(() => {
                el.style.animation = 'slideInUp 0.3s ease forwards';
            }, i * 50);
        });
    }, 100);

    // Add CSS for animations and modals
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            animation: fadeIn 0.2s ease;
        }

        .modal {
            background: var(--bg-card);
            border-radius: 16px;
            width: 90%;
            max-width: 400px;
            animation: slideUp 0.3s ease;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid var(--border-primary);
        }

        .modal-header h3 {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .modal-close {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 24px;
            cursor: pointer;
        }

        .modal-content {
            padding: 20px;
        }

        .modal-options {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .modal-option {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 12px;
            color: var(--text-primary);
            cursor: pointer;
            transition: all 0.2s;
        }

        .modal-option:hover {
            background: var(--bg-tertiary);
            border-color: var(--primary-blue);
        }

        .option-icon {
            font-size: 24px;
        }

        .option-text {
            font-size: 14px;
            font-weight: 500;
        }

        .modal-menu {
            display: flex;
            flex-direction: column;
        }

        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background: transparent;
            border: none;
            color: var(--text-primary);
            cursor: pointer;
            transition: background 0.2s;
        }

        .menu-item:hover {
            background: var(--bg-secondary);
        }

        .menu-icon {
            font-size: 20px;
        }

        .toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            padding: 12px 24px;
            background: var(--bg-card);
            border: 1px solid var(--border-primary);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
            z-index: 2000;
            transition: transform 0.3s ease;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
        }

        .toast-info {
            background: var(--primary-blue);
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
});