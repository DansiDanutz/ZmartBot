// ZmartyChat Dashboard JavaScript
class ZmartyChatDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.charts = {};
        this.websocket = null;
        this.isRealTimeEnabled = true;
        this.updateInterval = null;
        this.portfolioData = {
            value: 24750.00,
            change: 5.2,
            changeAmount: 1220,
            positions: 8
        };
        this.tradingData = {
            pair: 'BTC/USDT',
            price: 43250.00,
            spread: 2.50
        };

        this.init();
    }

    init() {
        this.hideLoadingScreen();
        this.setupEventListeners();
        this.initializeCharts();
        this.loadData();
        this.startRealTimeUpdates();
        this.setupWebSocket();
    }

    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {
                loadingScreen.classList.add('hidden');
            }
        }, 1500);
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                this.navigateToSection(section);
            });
        });

        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('collapsed');
            });
        }

        // User menu dropdown
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userDropdown = document.getElementById('userDropdown');
        if (userMenuBtn && userDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                userDropdown.classList.toggle('active');
            });

            document.addEventListener('click', () => {
                userDropdown.classList.remove('active');
            });
        }

        // Notifications dropdown
        const notificationBtn = document.querySelector('.notification-btn');
        const notificationDropdown = document.getElementById('notificationDropdown');
        if (notificationBtn && notificationDropdown) {
            notificationBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                notificationDropdown.classList.toggle('active');
            });

            document.addEventListener('click', () => {
                notificationDropdown.classList.remove('active');
            });
        }

        // Chart period buttons
        document.querySelectorAll('.chart-period').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const period = btn.getAttribute('data-period');
                this.updateChartPeriod(period);

                // Update active state
                btn.parentElement.querySelectorAll('.chart-period').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // Trading form
        this.setupTradingForm();

        // Search functionality
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            globalSearch.addEventListener('input', (e) => {
                this.performSearch(e.target.value);
            });
        }

        // Quick action buttons
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.handleQuickAction(btn);
            });
        });
    }

    navigateToSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        const activeLink = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        // Update page title and breadcrumb
        this.updatePageHeader(sectionName);

        // Store current section
        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    updatePageHeader(sectionName) {
        const pageTitle = document.getElementById('pageTitle');
        const breadcrumb = document.getElementById('breadcrumb');

        const sectionTitles = {
            'dashboard': 'Dashboard',
            'trading': 'Trading Terminal',
            'portfolio': 'Portfolio',
            'ai-insights': 'AI Insights',
            'whale-alerts': 'Whale Alerts',
            'news': 'Market News',
            'analytics': 'Analytics',
            'settings': 'Settings',
            'profile': 'Profile'
        };

        if (pageTitle) {
            pageTitle.textContent = sectionTitles[sectionName] || 'Dashboard';
        }

        if (breadcrumb) {
            breadcrumb.innerHTML = `
                <span>Home</span>
                <span class="separator">></span>
                <span class="active">${sectionTitles[sectionName] || 'Dashboard'}</span>
            `;
        }
    }

    initializeCharts() {
        this.initPortfolioChart();
        this.initAllocationChart();
        this.initTradingChart();
        this.initSentimentGauge();
    }

    initPortfolioChart() {
        const ctx = document.getElementById('portfolioChart');
        if (!ctx) return;

        const data = this.generatePortfolioData();

        this.charts.portfolio = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Portfolio Value',
                    data: data.values,
                    borderColor: '#0066ff',
                    backgroundColor: 'rgba(0, 102, 255, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: '#333333'
                        },
                        ticks: {
                            color: '#b0b0b0'
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: '#333333'
                        },
                        ticks: {
                            color: '#b0b0b0',
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    initAllocationChart() {
        const ctx = document.getElementById('allocationChart');
        if (!ctx) return;

        const data = this.generateAllocationData();

        this.charts.allocation = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        '#0066ff',
                        '#00ff88',
                        '#ffa726',
                        '#9c27b0',
                        '#ff4757'
                    ],
                    borderWidth: 0,
                    hoverBorderWidth: 2,
                    hoverBorderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#b0b0b0',
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    initTradingChart() {
        const ctx = document.getElementById('tradingChart');
        if (!ctx) return;

        const data = this.generateCandlestickData();

        this.charts.trading = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'BTC/USDT',
                    data: data.prices,
                    borderColor: '#0066ff',
                    backgroundColor: 'rgba(0, 102, 255, 0.1)',
                    fill: false,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            color: '#333333'
                        },
                        ticks: {
                            color: '#b0b0b0',
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: '#333333'
                        },
                        ticks: {
                            color: '#b0b0b0',
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    initSentimentGauge() {
        const ctx = document.getElementById('sentimentGauge');
        if (!ctx) return;

        this.charts.sentiment = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [87, 13],
                    backgroundColor: ['#00ff88', '#333333'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                cutout: '80%'
            }
        });
    }

    generatePortfolioData() {
        const labels = [];
        const values = [];
        const baseValue = 23500;
        const now = new Date();

        for (let i = 30; i >= 0; i--) {
            const date = new Date(now);
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));

            const randomChange = (Math.random() - 0.5) * 1000;
            const value = baseValue + (randomChange * (30 - i));
            values.push(Math.max(value, baseValue * 0.8));
        }

        return { labels, values };
    }

    generateAllocationData() {
        return {
            labels: ['Bitcoin', 'Ethereum', 'Cardano', 'Solana', 'Others'],
            values: [45, 25, 15, 10, 5]
        };
    }

    generateCandlestickData() {
        const labels = [];
        const prices = [];
        const basePrice = 43000;
        const now = new Date();

        for (let i = 100; i >= 0; i--) {
            const date = new Date(now);
            date.setMinutes(date.getMinutes() - i);
            labels.push(date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));

            const randomChange = (Math.random() - 0.5) * 500;
            const price = basePrice + randomChange;
            prices.push(Math.max(price, basePrice * 0.95));
        }

        return { labels, prices };
    }

    setupTradingForm() {
        const priceInput = document.getElementById('priceInput');
        const amountInput = document.getElementById('amountInput');
        const totalDisplay = document.getElementById('totalDisplay');
        const placeOrderBtn = document.getElementById('placeOrderBtn');

        // Update total when price or amount changes
        const updateTotal = () => {
            const price = parseFloat(priceInput?.value || 0);
            const amount = parseFloat(amountInput?.value || 0);
            const total = price * amount;

            if (totalDisplay) {
                totalDisplay.textContent = '$' + total.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
        };

        if (priceInput) {
            priceInput.addEventListener('input', updateTotal);
            priceInput.value = this.tradingData.price.toLocaleString();
        }

        if (amountInput) {
            amountInput.addEventListener('input', updateTotal);
        }

        // Amount percentage buttons
        document.querySelectorAll('.amount-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const percent = parseInt(btn.getAttribute('data-percent'));
                const maxAmount = 1.0; // Example max amount
                const amount = (maxAmount * percent) / 100;

                if (amountInput) {
                    amountInput.value = amount.toFixed(6);
                    updateTotal();
                }
            });
        });

        // Trade tabs
        document.querySelectorAll('.trade-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.trade-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                const tradeType = tab.getAttribute('data-type');
                if (placeOrderBtn) {
                    placeOrderBtn.textContent = `Place ${tradeType.charAt(0).toUpperCase() + tradeType.slice(1)} Order`;
                    placeOrderBtn.className = `place-order-btn ${tradeType}`;
                }
            });
        });

        // Place order button
        if (placeOrderBtn) {
            placeOrderBtn.addEventListener('click', () => {
                this.placeOrder();
            });
        }
    }

    placeOrder() {
        const orderData = {
            pair: this.tradingData.pair,
            type: document.querySelector('.trade-tab.active')?.getAttribute('data-type') || 'buy',
            price: document.getElementById('priceInput')?.value,
            amount: document.getElementById('amountInput')?.value
        };

        console.log('Placing order:', orderData);

        // Show success notification
        this.showNotification('Order placed successfully!', 'success');

        // Reset form
        document.getElementById('amountInput').value = '';
        document.getElementById('totalDisplay').textContent = '$0.00';
    }

    loadData() {
        this.loadDashboardData();
        this.loadPortfolioData();
        this.loadOrderBookData();
        this.loadActivityData();
        this.loadWhaleAlerts();
        this.loadNotifications();
    }

    loadDashboardData() {
        // Update overview cards with real data
        const portfolioValue = document.getElementById('portfolioValue');
        const portfolioChange = document.getElementById('portfolioChange');
        const todayPnL = document.getElementById('todayPnL');
        const activePositions = document.getElementById('activePositions');
        const aiConfidence = document.getElementById('aiConfidence');

        if (portfolioValue) portfolioValue.textContent = '$' + this.portfolioData.value.toLocaleString();
        if (portfolioChange) {
            portfolioChange.textContent = `+${this.portfolioData.change}% (+$${this.portfolioData.changeAmount})`;
            portfolioChange.className = 'card-change positive';
        }
        if (todayPnL) todayPnL.textContent = '+$485.20';
        if (activePositions) activePositions.textContent = this.portfolioData.positions.toString();
        if (aiConfidence) aiConfidence.textContent = '87%';
    }

    loadPortfolioData() {
        const holdingsTableBody = document.getElementById('holdingsTableBody');
        if (!holdingsTableBody) return;

        const holdings = [
            { asset: 'BTC', balance: '0.5742', value: '$24,580.00', change: '+5.2%', allocation: '45%' },
            { asset: 'ETH', balance: '8.234', value: '$13,750.00', change: '+3.8%', allocation: '25%' },
            { asset: 'ADA', balance: '12,543', value: '$8,250.00', change: '+12.5%', allocation: '15%' },
            { asset: 'SOL', balance: '156.78', value: '$5,490.00', change: '+8.3%', allocation: '10%' },
            { asset: 'DOT', balance: '987.12', value: '$2,750.00', change: '-2.1%', allocation: '5%' }
        ];

        holdingsTableBody.innerHTML = holdings.map(holding => `
            <tr>
                <td><strong>${holding.asset}</strong></td>
                <td>${holding.balance}</td>
                <td>${holding.value}</td>
                <td class="${holding.change.startsWith('+') ? 'text-success' : 'text-error'}">
                    ${holding.change}
                </td>
                <td>${holding.allocation}</td>
                <td>
                    <button class="action-btn secondary" style="padding: 0.5rem 1rem; font-size: 0.8rem;">
                        Trade
                    </button>
                </td>
            </tr>
        `).join('');

        // Load open orders
        const openOrdersBody = document.getElementById('openOrdersBody');
        if (openOrdersBody) {
            const orders = [
                { pair: 'BTC/USDT', type: 'Limit', side: 'Buy', amount: '0.001', price: '$42,500', filled: '0%', status: 'Open' },
                { pair: 'ETH/USDT', type: 'Market', side: 'Sell', amount: '2.5', price: 'Market', filled: '100%', status: 'Filled' }
            ];

            openOrdersBody.innerHTML = orders.map(order => `
                <tr>
                    <td>${order.pair}</td>
                    <td>${order.type}</td>
                    <td class="${order.side === 'Buy' ? 'text-success' : 'text-error'}">${order.side}</td>
                    <td>${order.amount}</td>
                    <td>${order.price}</td>
                    <td>${order.filled}</td>
                    <td>
                        <span class="status-badge ${order.status.toLowerCase()}">${order.status}</span>
                    </td>
                    <td>
                        ${order.status === 'Open' ? '<button class="btn-cancel">Cancel</button>' : '-'}
                    </td>
                </tr>
            `).join('');
        }
    }

    loadOrderBookData() {
        const asksList = document.getElementById('asksList');
        const bidsList = document.getElementById('bidsList');
        const currentPrice = document.getElementById('currentPrice');
        const spreadValue = document.getElementById('spreadValue');

        if (currentPrice) {
            currentPrice.textContent = '$' + this.tradingData.price.toLocaleString();
        }
        if (spreadValue) {
            spreadValue.textContent = `Spread: $${this.tradingData.spread}`;
        }

        // Generate order book data
        const basePrice = this.tradingData.price;
        const asks = [];
        const bids = [];

        for (let i = 0; i < 15; i++) {
            // Asks (sell orders) - above current price
            const askPrice = basePrice + (i + 1) * 10;
            const askAmount = (Math.random() * 0.5 + 0.1).toFixed(6);
            const askTotal = (askPrice * askAmount).toFixed(2);

            asks.push(`
                <div class="order-item ask">
                    <span>${askPrice.toLocaleString()}</span>
                    <span>${askAmount}</span>
                    <span>${askTotal}</span>
                </div>
            `);

            // Bids (buy orders) - below current price
            const bidPrice = basePrice - (i + 1) * 10;
            const bidAmount = (Math.random() * 0.5 + 0.1).toFixed(6);
            const bidTotal = (bidPrice * bidAmount).toFixed(2);

            bids.push(`
                <div class="order-item bid">
                    <span>${bidPrice.toLocaleString()}</span>
                    <span>${bidAmount}</span>
                    <span>${bidTotal}</span>
                </div>
            `);
        }

        if (asksList) asksList.innerHTML = asks.join('');
        if (bidsList) bidsList.innerHTML = bids.join('');
    }

    loadActivityData() {
        const activityList = document.getElementById('activityList');
        if (!activityList) return;

        const activities = [
            {
                icon: '💰',
                title: 'Bought 0.5 BTC',
                description: 'Market order executed at $43,250',
                time: '2 minutes ago'
            },
            {
                icon: '🎯',
                title: 'Take Profit Triggered',
                description: 'ETH position closed with +12.5% profit',
                time: '15 minutes ago'
            },
            {
                icon: '🚨',
                title: 'Whale Alert',
                description: '500 BTC moved to unknown wallet',
                time: '1 hour ago'
            },
            {
                icon: '📊',
                title: 'AI Analysis Complete',
                description: 'New trading opportunities identified',
                time: '2 hours ago'
            }
        ];

        activityList.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">${activity.icon}</div>
                <div class="activity-details">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                </div>
                <div class="activity-time">${activity.time}</div>
            </div>
        `).join('');
    }

    loadWhaleAlerts() {
        const whaleAlertsList = document.getElementById('whaleAlertsList');
        if (!whaleAlertsList) return;

        const alerts = [
            {
                amount: '500 BTC',
                value: '$21.6M',
                from: 'Binance',
                to: 'Unknown Wallet',
                time: '5 min ago',
                type: 'outflow'
            },
            {
                amount: '1,250 ETH',
                value: '$3.4M',
                from: 'Unknown Wallet',
                to: 'Coinbase',
                time: '12 min ago',
                type: 'inflow'
            },
            {
                amount: '750 BTC',
                value: '$32.4M',
                from: 'Kraken',
                to: 'Cold Storage',
                time: '1 hour ago',
                type: 'withdrawal'
            }
        ];

        whaleAlertsList.innerHTML = alerts.map(alert => `
            <div class="whale-alert-item">
                <div class="alert-header">
                    <span class="alert-amount">${alert.amount}</span>
                    <span class="alert-value">${alert.value}</span>
                    <span class="alert-type ${alert.type}">${alert.type}</span>
                </div>
                <div class="alert-details">
                    <span class="alert-from">From: ${alert.from}</span>
                    <span class="alert-to">To: ${alert.to}</span>
                    <span class="alert-time">${alert.time}</span>
                </div>
            </div>
        `).join('');
    }

    loadNotifications() {
        const notificationList = document.getElementById('notificationList');
        const notificationBadge = document.getElementById('notificationBadge');

        if (!notificationList) return;

        const notifications = [
            {
                title: 'Price Alert',
                message: 'BTC reached your target of $43,000',
                time: '5 min ago',
                type: 'price',
                unread: true
            },
            {
                title: 'Trade Executed',
                message: 'Your limit order for ETH has been filled',
                time: '1 hour ago',
                type: 'trade',
                unread: true
            },
            {
                title: 'Market Update',
                message: 'Major resistance level broken on SOL',
                time: '2 hours ago',
                type: 'market',
                unread: false
            }
        ];

        const unreadCount = notifications.filter(n => n.unread).length;
        if (notificationBadge) {
            notificationBadge.textContent = unreadCount.toString();
            notificationBadge.style.display = unreadCount > 0 ? 'flex' : 'none';
        }

        notificationList.innerHTML = notifications.map(notification => `
            <div class="notification-item ${notification.unread ? 'unread' : ''}">
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time">${notification.time}</div>
                </div>
                ${notification.unread ? '<div class="notification-dot"></div>' : ''}
            </div>
        `).join('');
    }

    loadSectionData(sectionName) {
        switch (sectionName) {
            case 'trading':
                this.loadTradingData();
                break;
            case 'ai-insights':
                this.loadAIInsights();
                break;
            case 'whale-alerts':
                this.loadWhaleAlerts();
                break;
            default:
                break;
        }
    }

    loadTradingData() {
        // Initialize trading-specific data
        this.updateTradingChart();
        this.loadOrderBookData();
    }

    loadAIInsights() {
        // Load AI-specific insights
        const predictions = [
            { symbol: 'BTC', current: '$43,250', predicted: '$45,800', change: '+5.9%' },
            { symbol: 'ETH', current: '$2,680', predicted: '$2,920', change: '+8.9%' },
            { symbol: 'ADA', current: '$0.65', predicted: '$0.78', change: '+20.0%' }
        ];

        const opportunities = [
            { type: 'Long', pair: 'ETH/USDT', entry: '$2,680', target: '$2,850', rr: '1:3' },
            { type: 'Short', pair: 'BTC/USDT', entry: '$43,200', target: '$41,500', rr: '1:2.5' }
        ];

        // Update predictions UI
        const predictionsList = document.querySelector('.predictions-list');
        if (predictionsList) {
            predictionsList.innerHTML = predictions.map(pred => `
                <div class="prediction-item">
                    <div class="crypto-info">
                        <span class="crypto-symbol">${pred.symbol}</span>
                    </div>
                    <div class="prediction-values">
                        <span class="current-price">${pred.current}</span>
                        <span class="predicted-price positive">${pred.predicted}</span>
                        <span class="prediction-change">${pred.change}</span>
                    </div>
                </div>
            `).join('');
        }

        // Update opportunities UI
        const opportunitiesList = document.querySelector('.opportunities-list');
        if (opportunitiesList) {
            opportunitiesList.innerHTML = opportunities.map(opp => `
                <div class="opportunity-item">
                    <div class="opportunity-header">
                        <span class="opportunity-type">${opp.type}</span>
                        <span class="opportunity-pair">${opp.pair}</span>
                    </div>
                    <div class="opportunity-details">
                        <span class="entry-price">Entry: ${opp.entry}</span>
                        <span class="target-price">Target: ${opp.target}</span>
                        <span class="risk-reward">R:R ${opp.rr}</span>
                    </div>
                </div>
            `).join('');
        }
    }

    updateChartPeriod(period) {
        console.log('Updating chart period to:', period);
        // Update chart data based on period
        if (this.charts.portfolio) {
            // Generate new data for the selected period
            const newData = this.generatePortfolioData();
            this.charts.portfolio.data.labels = newData.labels;
            this.charts.portfolio.data.datasets[0].data = newData.values;
            this.charts.portfolio.update();
        }
    }

    updateTradingChart() {
        if (this.charts.trading) {
            const newData = this.generateCandlestickData();
            this.charts.trading.data.labels = newData.labels;
            this.charts.trading.data.datasets[0].data = newData.prices;
            this.charts.trading.update();
        }
    }

    startRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            if (this.isRealTimeEnabled) {
                this.updateRealTimeData();
            }
        }, 5000); // Update every 5 seconds
    }

    updateRealTimeData() {
        // Simulate real-time price updates
        const newPrice = this.tradingData.price + (Math.random() - 0.5) * 100;
        this.tradingData.price = Math.max(newPrice, 40000);

        // Update price display
        const currentPrice = document.getElementById('currentPrice');
        if (currentPrice) {
            currentPrice.textContent = '$' + this.tradingData.price.toLocaleString();
        }

        // Update order book
        this.loadOrderBookData();

        // Update charts
        if (this.currentSection === 'trading') {
            this.updateTradingChart();
        }
    }

    setupWebSocket() {
        // In a real implementation, this would connect to your WebSocket server
        console.log('Setting up WebSocket connection...');

        // Simulate WebSocket connection
        setTimeout(() => {
            this.simulateWebSocketMessages();
        }, 2000);
    }

    simulateWebSocketMessages() {
        // Simulate receiving real-time market data
        setInterval(() => {
            if (this.isRealTimeEnabled) {
                this.handleWebSocketMessage({
                    type: 'price_update',
                    symbol: 'BTC/USDT',
                    price: this.tradingData.price,
                    volume: Math.random() * 1000000
                });
            }
        }, 1000);
    }

    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'price_update':
                this.handlePriceUpdate(message);
                break;
            case 'whale_alert':
                this.handleWhaleAlert(message);
                break;
            case 'trade_update':
                this.handleTradeUpdate(message);
                break;
        }
    }

    handlePriceUpdate(data) {
        // Update price displays in real-time
        if (data.symbol === this.tradingData.pair) {
            this.tradingData.price = data.price;

            const priceInput = document.getElementById('priceInput');
            if (priceInput) {
                priceInput.value = data.price.toLocaleString();
            }
        }
    }

    handleWhaleAlert(data) {
        // Show whale alert notification
        this.showNotification(`Whale Alert: ${data.amount} moved`, 'warning');
    }

    handleTradeUpdate(data) {
        // Update trade-related UI
        console.log('Trade update received:', data);
    }

    performSearch(query) {
        if (query.length < 2) return;

        console.log('Searching for:', query);

        // Implement search functionality
        // This could search through assets, news, or other data
    }

    handleQuickAction(button) {
        const actionText = button.querySelector('.action-text')?.textContent;

        switch (actionText) {
            case 'Buy Crypto':
                this.navigateToSection('trading');
                break;
            case 'Market Analysis':
                this.navigateToSection('ai-insights');
                break;
            case 'AI Suggestions':
                this.navigateToSection('ai-insights');
                break;
            case 'Quick Trade':
                this.showQuickTradeModal();
                break;
        }
    }

    showQuickTradeModal() {
        // Implement quick trade modal
        this.showNotification('Quick trade modal would open here', 'info');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification toast ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        document.body.appendChild(notification);

        // Add event listener for close button
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);

        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
    }

    destroy() {
        // Cleanup
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        if (this.websocket) {
            this.websocket.close();
        }

        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// CSS for notifications
const notificationStyles = `
<style>
.notification.toast {
    position: fixed;
    top: 80px;
    right: 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-lg);
    padding: 1rem;
    min-width: 300px;
    box-shadow: var(--shadow-lg);
    z-index: 10000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
}

.notification.toast.show {
    transform: translateX(0);
}

.notification.toast.success {
    border-left: 4px solid var(--text-success);
}

.notification.toast.error {
    border-left: 4px solid var(--text-error);
}

.notification.toast.warning {
    border-left: 4px solid var(--text-warning);
}

.notification.toast.info {
    border-left: 4px solid var(--primary-blue);
}

.notification-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

.notification-message {
    color: var(--text-primary);
    font-size: 0.9rem;
}

.notification-close {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification-close:hover {
    color: var(--text-primary);
}

.status-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
}

.status-badge.open {
    background: rgba(0, 102, 255, 0.2);
    color: var(--primary-blue);
}

.status-badge.filled {
    background: rgba(0, 255, 136, 0.2);
    color: var(--text-success);
}

.btn-cancel {
    background: var(--accent-red);
    border: none;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
}

.notification-item {
    padding: 1rem;
    border-bottom: 1px solid var(--border-primary);
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.notification-item:hover {
    background: var(--bg-secondary);
}

.notification-item.unread {
    background: rgba(0, 102, 255, 0.05);
    border-left: 3px solid var(--primary-blue);
}

.notification-dot {
    width: 8px;
    height: 8px;
    background: var(--primary-blue);
    border-radius: 50%;
    position: absolute;
    top: 1rem;
    right: 1rem;
}

.notification-title {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.notification-message {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.notification-time {
    color: var(--text-muted);
    font-size: 0.8rem;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', notificationStyles);

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.zmartyChatDashboard = new ZmartyChatDashboard();
});

// Export for external use
window.ZmartyChatDashboard = ZmartyChatDashboard;