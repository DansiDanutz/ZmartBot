// Admin Dashboard JavaScript
class AdminDashboard {
    constructor() {
        this.currentSection = 'overview';
        this.chartInstances = {};
        this.wsConnection = null;
        this.refreshIntervals = {};
        this.init();
    }

    init() {
        this.initNavigation();
        this.initCharts();
        this.initWebSocket();
        this.loadOverviewData();
        this.initEventListeners();
        this.startAutoRefresh();
    }

    initNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });
    }

    switchSection(sectionId) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.section === sectionId) {
                item.classList.add('active');
            }
        });

        // Update content
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        const targetSection = document.getElementById(`${sectionId}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
            this.currentSection = sectionId;
            this.loadSectionData(sectionId);
        }
    }

    loadSectionData(section) {
        switch(section) {
            case 'overview':
                this.loadOverviewData();
                break;
            case 'circuit-breakers':
                this.loadCircuitBreakers();
                break;
            case 'users':
                this.loadUsersData();
                break;
            case 'transactions':
                this.loadTransactions();
                break;
            case 'ai-providers':
                this.loadAIProviders();
                break;
            case 'security':
                this.loadSecurityAudit();
                break;
            case 'system-logs':
                this.loadSystemLogs();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    }

    // Overview Section
    loadOverviewData() {
        this.updateMetrics();
        this.updateServiceHealth();
        this.updateActivityFeed();
        this.updateAIProviderStatus();
    }

    updateMetrics() {
        const metrics = {
            totalUsers: 45678,
            activeUsers: 12345,
            totalRevenue: 1234567.89,
            totalTransactions: 89012,
            aiRequests: 456789,
            systemUptime: 99.98
        };

        document.getElementById('total-users').textContent = metrics.totalUsers.toLocaleString();
        document.getElementById('active-users').textContent = metrics.activeUsers.toLocaleString();
        document.getElementById('total-revenue').textContent = `$${metrics.totalRevenue.toLocaleString()}`;
        document.getElementById('total-transactions').textContent = metrics.totalTransactions.toLocaleString();
        document.getElementById('ai-requests').textContent = metrics.aiRequests.toLocaleString();
        document.getElementById('system-uptime').textContent = `${metrics.systemUptime}%`;
    }

    updateServiceHealth() {
        const services = [
            { name: 'API Gateway', status: 'healthy' },
            { name: 'Trading Engine', status: 'healthy' },
            { name: 'WebSocket Server', status: 'healthy' },
            { name: 'Database', status: 'healthy' },
            { name: 'Cache Layer', status: 'degraded' },
            { name: 'Message Queue', status: 'healthy' },
            { name: 'AI Orchestrator', status: 'healthy' },
            { name: 'Monitoring', status: 'down' }
        ];

        const container = document.getElementById('service-health-grid');
        container.innerHTML = services.map(service => `
            <div class="service-card">
                <span class="service-name">${service.name}</span>
                <span class="service-status status-${service.status}">${service.status.toUpperCase()}</span>
            </div>
        `).join('');
    }

    updateActivityFeed() {
        const activities = [
            { type: 'success', title: 'New user registration', description: 'User john.doe@example.com completed KYC', time: '2 minutes ago' },
            { type: 'warning', title: 'High API usage', description: 'OpenAI API usage at 85% of limit', time: '5 minutes ago' },
            { type: 'error', title: 'Circuit breaker opened', description: 'Gemini API circuit breaker triggered', time: '10 minutes ago' },
            { type: 'success', title: 'Large transaction completed', description: '$50,000 BTC trade executed successfully', time: '15 minutes ago' },
            { type: 'success', title: 'System backup completed', description: 'Daily backup completed successfully', time: '30 minutes ago' }
        ];

        const container = document.getElementById('activity-feed');
        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${activity.type}">
                    ${this.getActivityIcon(activity.type)}
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-time">${activity.time}</div>
                </div>
            </div>
        `).join('');
    }

    getActivityIcon(type) {
        const icons = {
            success: '✓',
            warning: '⚠',
            error: '✕',
            info: 'i'
        };
        return icons[type] || '•';
    }

    updateAIProviderStatus() {
        const providers = [
            { name: 'OpenAI', status: 'online', requests: 45678 },
            { name: 'Claude', status: 'online', requests: 34567 },
            { name: 'Gemini', status: 'offline', requests: 23456 },
            { name: 'Grok', status: 'online', requests: 12345 }
        ];

        const container = document.getElementById('ai-provider-status');
        container.innerHTML = providers.map(provider => `
            <div class="provider-quick-status">
                <span class="provider-name">${provider.name}</span>
                <span class="status-indicator ${provider.status}"></span>
                <span class="request-count">${provider.requests.toLocaleString()} reqs</span>
            </div>
        `).join('');
    }

    // Circuit Breakers Section
    loadCircuitBreakers() {
        const breakers = [
            { name: 'OpenAI API', status: 'closed', requests: 1234, failures: 5, successRate: 99.6 },
            { name: 'Claude API', status: 'closed', requests: 987, failures: 2, successRate: 99.8 },
            { name: 'Gemini API', status: 'open', requests: 654, failures: 65, successRate: 90.0 },
            { name: 'Grok API', status: 'half-open', requests: 321, failures: 10, successRate: 96.9 },
            { name: 'Database', status: 'closed', requests: 5432, failures: 1, successRate: 99.98 },
            { name: 'Cache', status: 'closed', requests: 8765, failures: 0, successRate: 100 }
        ];

        const container = document.getElementById('circuit-breakers-grid');
        container.innerHTML = breakers.map(breaker => `
            <div class="breaker-card">
                <div class="breaker-header">
                    <span class="breaker-name">${breaker.name}</span>
                    <span class="breaker-status status-${breaker.status}">${breaker.status.toUpperCase()}</span>
                </div>
                <div class="breaker-stats">
                    <div class="stat">
                        <div class="stat-label">Requests</div>
                        <div class="stat-value">${breaker.requests}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Failures</div>
                        <div class="stat-value">${breaker.failures}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Success</div>
                        <div class="stat-value">${breaker.successRate}%</div>
                    </div>
                </div>
                <div class="breaker-actions">
                    <button class="breaker-btn force-open" onclick="adminDashboard.forceBreakerOpen('${breaker.name}')">Force Open</button>
                    <button class="breaker-btn force-close" onclick="adminDashboard.forceBreakerClose('${breaker.name}')">Force Close</button>
                    <button class="breaker-btn" onclick="adminDashboard.resetBreaker('${breaker.name}')">Reset</button>
                </div>
            </div>
        `).join('');
    }

    forceBreakerOpen(name) {
        console.log(`Forcing circuit breaker open: ${name}`);
        this.showNotification(`Circuit breaker ${name} forced open`, 'warning');
    }

    forceBreakerClose(name) {
        console.log(`Forcing circuit breaker closed: ${name}`);
        this.showNotification(`Circuit breaker ${name} forced closed`, 'success');
    }

    resetBreaker(name) {
        console.log(`Resetting circuit breaker: ${name}`);
        this.showNotification(`Circuit breaker ${name} reset`, 'info');
    }

    // Users Section
    loadUsersData() {
        const users = [
            { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active', kyc: 'verified', plan: 'pro', balance: 50000 },
            { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'active', kyc: 'verified', plan: 'enterprise', balance: 150000 },
            { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'pending', kyc: 'unverified', plan: 'free', balance: 0 },
            { id: 4, name: 'Alice Williams', email: 'alice@example.com', status: 'active', kyc: 'verified', plan: 'pro', balance: 75000 },
            { id: 5, name: 'Charlie Brown', email: 'charlie@example.com', status: 'suspended', kyc: 'verified', plan: 'pro', balance: 25000 }
        ];

        const tbody = document.getElementById('users-table-body');
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div class="user-avatar-small"></div>
                        <div>
                            <div>${user.name}</div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary)">${user.email}</div>
                        </div>
                    </div>
                </td>
                <td><span class="status-badge badge-${user.status}">${user.status.toUpperCase()}</span></td>
                <td><span class="status-badge badge-${user.kyc}">${user.kyc.toUpperCase()}</span></td>
                <td><span class="plan-badge ${user.plan}">${user.plan.toUpperCase()}</span></td>
                <td>$${user.balance.toLocaleString()}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn" onclick="adminDashboard.viewUser(${user.id})">View</button>
                        <button class="action-btn" onclick="adminDashboard.editUser(${user.id})">Edit</button>
                        <button class="action-btn" onclick="adminDashboard.suspendUser(${user.id})">Suspend</button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    viewUser(id) {
        console.log(`Viewing user ${id}`);
    }

    editUser(id) {
        console.log(`Editing user ${id}`);
    }

    suspendUser(id) {
        console.log(`Suspending user ${id}`);
        this.showNotification(`User ${id} suspended`, 'warning');
    }

    searchUsers() {
        const query = document.getElementById('user-search').value;
        console.log(`Searching users: ${query}`);
    }

    filterUsers(filter) {
        console.log(`Filtering users: ${filter}`);
        this.loadUsersData();
    }

    exportUsers() {
        console.log('Exporting users data');
        this.showNotification('User data exported successfully', 'success');
    }

    // Transactions Section
    loadTransactions() {
        const transactions = [
            { id: 'TXN001', user: 'john@example.com', type: 'credit', amount: 5000, description: 'Deposit', status: 'completed', date: '2025-09-18 10:30' },
            { id: 'TXN002', user: 'jane@example.com', type: 'debit', amount: 2500, description: 'Trading fee', status: 'completed', date: '2025-09-18 10:25' },
            { id: 'TXN003', user: 'bob@example.com', type: 'credit', amount: 10000, description: 'Wire transfer', status: 'pending', date: '2025-09-18 10:20' },
            { id: 'TXN004', user: 'alice@example.com', type: 'debit', amount: 500, description: 'AI API usage', status: 'completed', date: '2025-09-18 10:15' },
            { id: 'TXN005', user: 'charlie@example.com', type: 'credit', amount: 25000, description: 'Crypto deposit', status: 'completed', date: '2025-09-18 10:10' }
        ];

        const tbody = document.getElementById('transactions-table-body');
        tbody.innerHTML = transactions.map(txn => `
            <tr>
                <td>${txn.id}</td>
                <td>${txn.user}</td>
                <td><span class="badge-${txn.type}">${txn.type.toUpperCase()}</span></td>
                <td class="${txn.type}">$${txn.amount.toLocaleString()}</td>
                <td>${txn.description}</td>
                <td><span class="status-badge badge-${txn.status}">${txn.status.toUpperCase()}</span></td>
                <td>${txn.date}</td>
                <td>
                    <div class="table-actions">
                        <button class="action-btn" onclick="adminDashboard.viewTransaction('${txn.id}')">View</button>
                        ${txn.status === 'pending' ? '<button class="action-btn" onclick="adminDashboard.approveTransaction(\'' + txn.id + '\')">Approve</button>' : ''}
                    </div>
                </td>
            </tr>
        `).join('');

        // Update summary
        document.getElementById('total-credits').textContent = '$40,000';
        document.getElementById('total-debits').textContent = '$3,000';
        document.getElementById('net-balance').textContent = '$37,000';
        document.getElementById('pending-amount').textContent = '$10,000';
    }

    viewTransaction(id) {
        console.log(`Viewing transaction ${id}`);
    }

    approveTransaction(id) {
        console.log(`Approving transaction ${id}`);
        this.showNotification(`Transaction ${id} approved`, 'success');
    }

    // AI Providers Section
    loadAIProviders() {
        const providers = [
            { name: 'OpenAI', requests: 456789, cost: 12345.67, avgLatency: 234, errors: 45, usage: 85 },
            { name: 'Claude', requests: 345678, cost: 9876.54, avgLatency: 198, errors: 23, usage: 72 },
            { name: 'Gemini', requests: 234567, cost: 6543.21, avgLatency: 267, errors: 67, usage: 58 },
            { name: 'Grok', requests: 123456, cost: 3210.98, avgLatency: 145, errors: 12, usage: 41 }
        ];

        const container = document.getElementById('ai-providers-grid');
        container.innerHTML = providers.map(provider => `
            <div class="provider-card">
                <div class="provider-header">
                    <span class="provider-name">${provider.name}</span>
                    <span class="provider-status"></span>
                </div>
                <div class="provider-stats">
                    <div class="provider-stat">
                        <span class="provider-stat-label">Total Requests</span>
                        <span class="provider-stat-value">${provider.requests.toLocaleString()}</span>
                    </div>
                    <div class="provider-stat">
                        <span class="provider-stat-label">Total Cost</span>
                        <span class="provider-stat-value">$${provider.cost.toLocaleString()}</span>
                    </div>
                    <div class="provider-stat">
                        <span class="provider-stat-label">Avg Latency</span>
                        <span class="provider-stat-value">${provider.avgLatency}ms</span>
                    </div>
                    <div class="provider-stat">
                        <span class="provider-stat-label">Error Rate</span>
                        <span class="provider-stat-value">${(provider.errors / provider.requests * 100).toFixed(2)}%</span>
                    </div>
                </div>
                <div class="usage-bar">
                    <div class="usage-fill" style="width: ${provider.usage}%"></div>
                </div>
                <div style="margin-top: 10px; text-align: center; font-size: 0.875rem; color: var(--text-secondary)">
                    ${provider.usage}% of quota used
                </div>
            </div>
        `).join('');
    }

    // Security Audit Section
    loadSecurityAudit() {
        const events = [
            { severity: 'critical', event: 'Failed login attempts', user: 'unknown@hacker.com', ip: '192.168.1.100', time: '2 minutes ago', details: 'Multiple failed login attempts detected' },
            { severity: 'warning', event: 'Unusual trading pattern', user: 'john@example.com', ip: '10.0.0.50', time: '10 minutes ago', details: 'High frequency trading detected' },
            { severity: 'info', event: 'Password changed', user: 'jane@example.com', ip: '172.16.0.1', time: '30 minutes ago', details: 'User password successfully updated' },
            { severity: 'critical', event: 'API key compromised', user: 'bob@example.com', ip: '192.168.1.200', time: '1 hour ago', details: 'Potential API key leak detected' },
            { severity: 'warning', event: 'Large withdrawal', user: 'alice@example.com', ip: '10.0.0.100', time: '2 hours ago', details: 'Withdrawal exceeds daily limit' }
        ];

        const container = document.getElementById('security-audit-log');
        container.innerHTML = events.map(event => `
            <div class="audit-item">
                <div class="audit-severity severity-${event.severity}"></div>
                <div class="audit-content">
                    <div class="audit-event">${event.event}</div>
                    <div class="audit-details">${event.details}</div>
                    <div class="audit-meta">
                        <span>User: ${event.user}</span>
                        <span>IP: ${event.ip}</span>
                        <span>Time: ${event.time}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    filterSecurityEvents(type) {
        console.log(`Filtering security events: ${type}`);
        this.loadSecurityAudit();
    }

    exportSecurityLog() {
        console.log('Exporting security log');
        this.showNotification('Security log exported successfully', 'success');
    }

    // System Logs Section
    loadSystemLogs() {
        const logsContainer = document.getElementById('system-logs-container');
        if (!logsContainer) return;

        const logs = [
            { level: 'info', timestamp: '2025-09-18 10:30:45', service: 'API Gateway', message: 'Request processed successfully' },
            { level: 'warning', timestamp: '2025-09-18 10:30:43', service: 'Database', message: 'Connection pool reaching limit' },
            { level: 'error', timestamp: '2025-09-18 10:30:40', service: 'AI Orchestrator', message: 'Failed to connect to Gemini API' },
            { level: 'debug', timestamp: '2025-09-18 10:30:38', service: 'Cache', message: 'Cache hit ratio: 85%' },
            { level: 'info', timestamp: '2025-09-18 10:30:35', service: 'Trading Engine', message: 'Order executed successfully' }
        ];

        logsContainer.innerHTML = `
            <div class="logs-viewer">
                ${logs.map(log => `
                    <div class="log-entry log-${log.level}">
                        <span class="log-timestamp">[${log.timestamp}]</span>
                        <span class="log-level">[${log.level.toUpperCase()}]</span>
                        <span class="log-service">[${log.service}]</span>
                        <span class="log-message">${log.message}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Settings Section
    loadSettings() {
        console.log('Loading settings');
    }

    // Charts
    initCharts() {
        // Initialize any charts if Chart.js is loaded
        if (typeof Chart !== 'undefined') {
            this.createRevenueChart();
            this.createUsersChart();
        }
    }

    createRevenueChart() {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        this.chartInstances.revenue = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [65000, 78000, 90000, 105000, 125000, 145000],
                    borderColor: '#0066ff',
                    backgroundColor: 'rgba(0, 102, 255, 0.1)',
                    tension: 0.4
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
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    createUsersChart() {
        const ctx = document.getElementById('usersChart');
        if (!ctx) return;

        this.chartInstances.users = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'New Users',
                    data: [1200, 1900, 3000, 5000, 6000, 7000],
                    backgroundColor: '#00ff88'
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
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // WebSocket
    initWebSocket() {
        // Simulated WebSocket for real-time updates
        this.simulateRealtimeUpdates();
    }

    simulateRealtimeUpdates() {
        setInterval(() => {
            if (this.currentSection === 'overview') {
                this.updateRandomMetric();
            }
        }, 5000);
    }

    updateRandomMetric() {
        const metrics = ['active-users', 'ai-requests', 'total-transactions'];
        const randomMetric = metrics[Math.floor(Math.random() * metrics.length)];
        const element = document.getElementById(randomMetric);
        if (element) {
            const currentValue = parseInt(element.textContent.replace(/[^0-9]/g, ''));
            const change = Math.floor(Math.random() * 100) - 50;
            element.textContent = (currentValue + change).toLocaleString();
        }
    }

    // Event Listeners
    initEventListeners() {
        // Search functionality
        const userSearch = document.getElementById('user-search');
        if (userSearch) {
            userSearch.addEventListener('input', (e) => {
                this.searchUsers();
            });
        }

        // Filter dropdowns
        document.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', (e) => {
                const filterType = e.target.id;
                const filterValue = e.target.value;
                this.applyFilter(filterType, filterValue);
            });
        });

        // Logout button
        const logoutBtn = document.querySelector('.logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                if (confirm('Are you sure you want to logout?')) {
                    this.logout();
                }
            });
        }
    }

    applyFilter(filterType, filterValue) {
        console.log(`Applying filter: ${filterType} = ${filterValue}`);
        // Reload relevant section data
        this.loadSectionData(this.currentSection);
    }

    // Auto Refresh
    startAutoRefresh() {
        // Refresh overview data every 30 seconds
        this.refreshIntervals.overview = setInterval(() => {
            if (this.currentSection === 'overview') {
                this.loadOverviewData();
            }
        }, 30000);

        // Refresh circuit breakers every 10 seconds
        this.refreshIntervals.circuitBreakers = setInterval(() => {
            if (this.currentSection === 'circuit-breakers') {
                this.loadCircuitBreakers();
            }
        }, 10000);
    }

    // Utility Functions
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            padding: 15px 20px;
            background: var(--bg-card);
            border: 1px solid ${type === 'success' ? 'var(--success-green)' : type === 'warning' ? 'var(--warning-orange)' : type === 'error' ? 'var(--danger-red)' : 'var(--info-blue)'};
            border-radius: 8px;
            color: ${type === 'success' ? 'var(--success-green)' : type === 'warning' ? 'var(--warning-orange)' : type === 'error' ? 'var(--danger-red)' : 'var(--info-blue)'};
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    logout() {
        console.log('Logging out...');
        // Clear intervals
        Object.values(this.refreshIntervals).forEach(interval => clearInterval(interval));
        // Redirect to login
        window.location.href = '/login';
    }

    // Mobile menu toggle
    toggleMobileMenu() {
        const sidebar = document.querySelector('.admin-sidebar');
        sidebar.classList.toggle('mobile-open');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
});

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    .notification {
        transition: all 0.3s ease;
    }

    .log-entry {
        font-family: 'Courier New', monospace;
        padding: 5px;
        border-bottom: 1px solid var(--border-color);
    }

    .log-info { color: var(--info-blue); }
    .log-warning { color: var(--warning-orange); }
    .log-error { color: var(--danger-red); }
    .log-debug { color: var(--text-secondary); }

    .logs-viewer {
        background: var(--bg-dark);
        padding: var(--spacing-md);
        border-radius: 8px;
        max-height: 600px;
        overflow-y: auto;
        font-size: 0.875rem;
    }
`;
document.head.appendChild(style);