// ZmartBot Professional Dashboard JavaScript

// Service data structure
let servicesData = {
    level1: [],
    level2: [],
    level3: []
};

let currentFilter = 'all';
let currentService = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadServicesData();
    setupEventListeners();
    refreshDashboard();
});

// Setup event listeners
function setupEventListeners() {
    // Filter button event listeners
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const filter = this.dataset.filter;
            const container = this.closest('.services-grid');
            
            // Update active filter
            container.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            currentFilter = filter;
            renderServices(container.id.replace('-services', ''));
        });
    });
}

// Load services data from the audit results
function loadServicesData() {
    // Level 1 Services (Discovery) - 237 services
    servicesData.level1 = [
        { name: '21indicators', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: '21indicatorsDatabase', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: 'API-Manager', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: 'AnalyticsServer', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: 'Backend', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: 'BackendDoctorPack', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: 'BackendFrontendProtection', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: 'BinanceServices', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: 'CertificationService', port: null, status: 'online', passport: false, certified: false, level: 1 },
        { name: 'ClaudeMDCUpdate', port: null, status: 'online', passport: false, certified: false, level: 1 },
        // Add more Level 1 services as needed
    ];

    // Level 2 Services (Active/Passport) - 21 services
    servicesData.level2 = [
        { name: 'OrchestrationStart', port: 8616, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'RegistryConsolidator', port: 8898, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'TradingStrategy', port: 8888, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'YAMLGovernanceService', port: 8897, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'YAMLMonitoringDaemon', port: 8899, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'background-mdc-agent', port: 8091, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'binance-worker', port: 8304, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'cryptometer-service', port: 8093, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'discovery-database-service', port: 8780, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'explainability-service', port: 8099, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'gpt-mds-agent', port: 8701, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'historical-data-service', port: 8094, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'kingfisher-module', port: 8100, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'pattern-recognition-service', port: 8096, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'professional-dashboard', port: 3434, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'registration-service', port: 8902, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'scoring-service', port: 8199, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'sentiment-analysis-service', port: 8097, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'test-analytics-service', port: 8003, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'test-websocket-service', port: 8004, status: 'online', passport: true, certified: false, level: 2 },
        { name: 'trading-orchestration-agent', port: 8777, status: 'online', passport: true, certified: false, level: 2 }
    ];

    // Level 3 Services (Certified) - 43 services
    servicesData.level3 = [
        { name: 'achievements', port: 8026, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'api-keys-manager-service', port: 8006, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'binance', port: 8303, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'certification', port: 8901, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'database-service', port: 8900, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'doctor-service', port: 8700, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'enhanced-mdc-monitor', port: 8101, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'grok-x-module', port: 8092, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'kingfisher-ai', port: 8098, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'kucoin', port: 8302, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'live-alerts', port: 8217, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'maradona-alerts', port: 8016, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'market-data-service', port: 8095, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'master-orchestration-agent', port: 8002, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'mdc-dashboard', port: 8090, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'mdc-orchestration-agent', port: 8615, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'messi-alerts', port: 8214, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'my-symbols-extended-service', port: 8005, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'mysymbols', port: 8201, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'optimization-claude-service', port: 8080, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'passport-service', port: 8620, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'pele-alerts', port: 8215, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'port-manager-service', port: 8050, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'service-dashboard', port: 3000, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'service-discovery', port: 8550, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'service-lifecycle-manager', port: 8920, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'servicelog-service', port: 8750, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'snapshot-service', port: 8085, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'system-protection-service', port: 8999, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'test-service', port: 8301, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'whale-alerts', port: 8018, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'ziva-agent', port: 8930, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart-api', port: 8000, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart-dashboard', port: 3400, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart-notification', port: 8008, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart-websocket', port: 8009, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart_alert_system', port: 8012, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart_analytics', port: 8007, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart_backtesting', port: 8013, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart_data_warehouse', port: 8015, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart_machine_learning', port: 8014, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart_risk_management', port: 8010, status: 'online', passport: true, certified: true, level: 3 },
        { name: 'zmart_technical_analysis', port: 8011, status: 'online', passport: true, certified: true, level: 3 }
    ];

    // Add some offline services for demonstration
    servicesData.level1[5].status = 'offline';
    servicesData.level2[3].status = 'offline';
    servicesData.level3[8].status = 'offline';
}

// Toggle level details
function toggleLevelDetails(level) {
    const levelCard = document.querySelector(`#${level}-services`).parentElement;
    const servicesGrid = document.getElementById(`${level}-services`);
    const toggleIcon = levelCard.querySelector('.toggle-icon');
    
    if (servicesGrid.style.display === 'none') {
        servicesGrid.style.display = 'block';
        levelCard.classList.add('expanded');
        renderServices(level);
    } else {
        servicesGrid.style.display = 'none';
        levelCard.classList.remove('expanded');
    }
}

// Render services for a specific level
function renderServices(level) {
    const container = document.getElementById(`${level}-services-container`);
    const services = servicesData[level];
    
    // Filter services based on current filter
    let filteredServices = services;
    if (currentFilter === 'passport') {
        filteredServices = services.filter(s => s.passport);
    } else if (currentFilter === 'cert') {
        filteredServices = services.filter(s => s.certified);
    }
    
    const html = filteredServices.map(service => createServiceCard(service)).join('');
    container.innerHTML = html;
    
    // Update service count
    document.getElementById(`${level}-count`).textContent = filteredServices.length;
}

// Create service card HTML
function createServiceCard(service) {
    const statusClass = service.status === 'online' ? 'online' : 'offline';
    const statusText = service.status === 'online' ? 'Online' : 'Offline';
    const statusColor = service.status === 'online' ? 'var(--success-color)' : 'var(--error-color)';
    
    return `
        <div class="service-card ${statusClass}" onclick="openServiceModal('${service.name}')">
            <div class="service-header">
                <div class="service-icon">
                    <i class="fas fa-${getServiceIcon(service.name)}"></i>
                </div>
                <div class="service-info">
                    <div class="service-name">${service.name}</div>
                    <div class="service-port">${service.port ? `Port: ${service.port}` : 'No Port'}</div>
                </div>
                <div class="service-status">
                    <div class="status-light ${statusClass}"></div>
                    <span class="status-text">${statusText}</span>
                </div>
            </div>
            <div class="service-actions">
                <button class="action-btn restart" onclick="event.stopPropagation(); restartService('${service.name}')" title="Restart">
                    <i class="fas fa-redo"></i>
                </button>
                <button class="action-btn fix" onclick="event.stopPropagation(); fixService('${service.name}')" title="Fix Bug">
                    <i class="fas fa-wrench"></i>
                </button>
                <button class="action-btn doctor" onclick="event.stopPropagation(); sendToDoctor('${service.name}')" title="Send to Doctor">
                    <i class="fas fa-user-md"></i>
                </button>
            </div>
        </div>
    `;
}

// Get service icon based on name
function getServiceIcon(serviceName) {
    const iconMap = {
        'api': 'code',
        'database': 'database',
        'dashboard': 'tachometer-alt',
        'service': 'cogs',
        'agent': 'robot',
        'worker': 'cogs',
        'orchestration': 'network-wired',
        'monitor': 'eye',
        'alert': 'bell',
        'analytics': 'chart-line',
        'trading': 'chart-bar',
        'crypto': 'bitcoin',
        'web': 'globe',
        'socket': 'plug',
        'notification': 'envelope',
        'certification': 'certificate',
        'passport': 'id-card',
        'doctor': 'user-md',
        'protection': 'shield-alt',
        'discovery': 'search',
        'registry': 'book',
        'governance': 'balance-scale',
        'lifecycle': 'recycle',
        'snapshot': 'camera',
        'backtesting': 'history',
        'machine-learning': 'brain',
        'risk': 'exclamation-triangle',
        'technical': 'chart-area',
        'sentiment': 'smile',
        'pattern': 'puzzle-piece',
        'scoring': 'star',
        'historical': 'clock',
        'explainability': 'question-circle',
        'optimization': 'magic',
        'enhanced': 'plus-circle',
        'grok': 'lightbulb',
        'kingfisher': 'fish',
        'ziva': 'user-secret',
        'zmart': 'robot'
    };
    
    const name = serviceName.toLowerCase();
    for (const [key, icon] of Object.entries(iconMap)) {
        if (name.includes(key)) {
            return icon;
        }
    }
    
    return 'microchip'; // Default icon
}

// Open service modal
function openServiceModal(serviceName) {
    const service = findService(serviceName);
    if (!service) return;
    
    currentService = service;
    
    // Populate modal
    document.getElementById('modal-service-name').textContent = service.name;
    document.getElementById('modal-status').textContent = service.status === 'online' ? 'Online' : 'Offline';
    document.getElementById('modal-port').textContent = service.port || 'N/A';
    document.getElementById('modal-level').textContent = `Level ${service.level}`;
    document.getElementById('modal-passport').textContent = service.passport ? 'Active' : 'Inactive';
    
    // Show modal
    document.getElementById('serviceModal').style.display = 'block';
}

// Close modal
function closeModal() {
    document.getElementById('serviceModal').style.display = 'none';
    currentService = null;
}

// Find service by name
function findService(serviceName) {
    for (const level of Object.values(servicesData)) {
        const service = level.find(s => s.name === serviceName);
        if (service) return service;
    }
    return null;
}

// Service actions
function restartService(serviceName) {
    showNotification(`Restarting ${serviceName}...`, 'info');
    // Simulate API call
    setTimeout(() => {
        showNotification(`${serviceName} restarted successfully!`, 'success');
        refreshDashboard();
    }, 2000);
}

function fixService(serviceName) {
    showNotification(`Fixing bugs in ${serviceName}...`, 'info');
    // Simulate API call
    setTimeout(() => {
        showNotification(`Bugs fixed in ${serviceName}!`, 'success');
        refreshDashboard();
    }, 3000);
}

function sendToDoctor(serviceName) {
    showNotification(`Sending ${serviceName} to Doctor Service...`, 'info');
    // Simulate API call
    setTimeout(() => {
        showNotification(`${serviceName} sent to Doctor Service for analysis!`, 'success');
        refreshDashboard();
    }, 2500);
}

// Refresh dashboard
function refreshDashboard() {
    // Simulate loading
    document.body.classList.add('loading');
    
    setTimeout(() => {
        // Update system overview
        const totalServices = servicesData.level1.length + servicesData.level2.length + servicesData.level3.length;
        const onlineServices = totalServices - 3; // 3 offline services
        const offlineServices = 3;
        
        document.getElementById('total-services').textContent = totalServices;
        document.getElementById('online-services').textContent = onlineServices;
        document.getElementById('offline-services').textContent = offlineServices;
        
        // Update level counts
        document.getElementById('level1-count').textContent = servicesData.level1.length;
        document.getElementById('level2-count').textContent = servicesData.level2.length;
        document.getElementById('level3-count').textContent = servicesData.level3.length;
        
        document.body.classList.remove('loading');
        showNotification('Dashboard refreshed!', 'success');
    }, 1000);
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        color: var(--text-primary);
        z-index: 10000;
        box-shadow: var(--shadow-lg);
        transform: translateX(100%);
        transition: var(--transition);
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const modal = document.getElementById('serviceModal');
    if (event.target === modal) {
        closeModal();
    }
});

// Auto-refresh every 30 seconds
setInterval(refreshDashboard, 30000);











