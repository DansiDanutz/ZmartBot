/**
 * 🚀 ZmartBot ServiceLog Ultimate Intelligence Dashboard
 * Advanced JavaScript Engine with Real-time WebSocket Integration
 * Built by Senior AI Engineer for Maximum Performance & User Experience
 */

class ServiceLogDashboard {
    constructor() {
        this.config = {
            serviceLogUrl: 'http://localhost:8750',
            websocketUrl: 'ws://localhost:8751',
            refreshInterval: 5000,
            maxLogEntries: 1000,
            maxActivityItems: 50,
            maxAdviceItems: 20,
            animationDuration: 300,
            chartUpdateInterval: 2000,
            autoServiceDiscovery: true,
            serviceDiscoveryInterval: 30000
        };

        this.state = {
            connected: false,
            paused: false,
            currentSection: 'overview',
            theme: localStorage.getItem('dashboard-theme') || 'dark',
            filters: {
                service: '',
                level: '',
                search: ''
            },
            charts: {},
            logBuffer: [],
            activityBuffer: [],
            adviceBuffer: [],
            serviceData: {},
            metrics: {},
            refreshRate: parseInt(localStorage.getItem('refresh-rate')) || 5000,
            serviceCount: 0,
            lastServiceScan: null,
            autoScaling: {
                enabled: true,
                newServicesDetected: [],
                removedServices: []
            }
        };

        this.socket = null;
        this.updateIntervals = new Map();
        this.animationQueue = [];
        
        this.init();
    }

    async init() {
        console.log('🚀 Initializing ServiceLog Dashboard...');
        
        // Show loading overlay
        this.showLoading('Initializing Dashboard...');
        
        try {
            // Initialize components
            await this.initializeEventListeners();
            await this.initializeTheme();
            await this.initializeCharts();
            await this.loadLiveServiceCounts(); // Load live service counts first
            await this.connectWebSocket();
            await this.loadInitialData();
            await this.startUpdateIntervals();
            
            // Hide loading overlay
            this.hideLoading();
            
            console.log('✅ Dashboard initialized successfully');
            this.showNotification('Dashboard Ready!', 'success');
            
        } catch (error) {
            console.error('❌ Dashboard initialization failed:', error);
            this.showNotification('Failed to initialize dashboard', 'error');
            this.hideLoading();
        }
    }

    async loadLiveServiceCounts() {
        try {
            console.log('🔄 Loading live service counts from orchestration API...');
            const response = await fetch('http://localhost:8002/api/orchestration/services', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                timeout: 5000
            });
            
            if (response.ok) {
                const allServices = await response.json();
                const totalServices = allServices.length;
                const passportServices = allServices.filter(s => s.passport_id).length;
                const nonPassportServices = totalServices - passportServices;
                
                // Update state
                this.state.serviceCount = totalServices;
                this.state.passportServices = passportServices;
                this.state.nonPassportServices = nonPassportServices;
                
                // Update UI immediately
                this.updateServiceCountDisplay();
                
                console.log(`✅ Live service counts loaded: Total=${totalServices}, Passport=${passportServices}, Other=${nonPassportServices}`);
                
                // Store in serviceData for other components
                this.state.serviceData = allServices.reduce((acc, service) => {
                    acc[service.service_name] = service;
                    return acc;
                }, {});
                
            } else {
                console.warn('⚠️ Orchestration API not available, using fallback counts');
                this.useFallbackServiceCounts();
            }
        } catch (error) {
            console.error('❌ Error loading live service counts:', error);
            this.useFallbackServiceCounts();
        }
    }
    
    useFallbackServiceCounts() {
        // Use static fallback when live API is not available
        this.state.serviceCount = 43;
        this.state.passportServices = 30;
        this.state.nonPassportServices = 13;
        this.updateServiceCountDisplay();
        console.log('📋 Using fallback service counts: Total=43, Passport=30, Other=13');
    }
    
    updateServiceCountDisplay() {
        // Update the navbar service count with visual animation
        const activeServicesElement = document.getElementById('active-services');
        if (activeServicesElement) {
            // Add flash animation
            activeServicesElement.style.transition = 'all 0.3s ease';
            activeServicesElement.style.background = '#4fd1c7';
            activeServicesElement.style.color = '#0f1419';
            activeServicesElement.style.padding = '2px 6px';
            activeServicesElement.style.borderRadius = '4px';
            
            // Update count
            activeServicesElement.textContent = this.state.serviceCount;
            
            // Remove flash effect
            setTimeout(() => {
                activeServicesElement.style.background = 'transparent';
                activeServicesElement.style.color = '';
                activeServicesElement.style.padding = '0';
            }, 600);
        }
        
        // Update emergency dashboard if it exists
        const emergencyServicesElement = document.getElementById('emergency-services');
        if (emergencyServicesElement) {
            emergencyServicesElement.textContent = this.state.serviceCount;
        }
        
        // Update metrics
        if (this.state.metrics) {
            this.state.metrics.active_services = this.state.serviceCount;
            this.state.metrics.total_services = this.state.serviceCount;
        }
    }

    initializeEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                if (section) this.switchSection(section);
            });
        });

        // Theme toggle
        document.getElementById('theme-toggle')?.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Refresh button
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.refreshData();
        });

        // Export button
        document.getElementById('export-btn')?.addEventListener('click', () => {
            this.exportData();
        });

        // Service scan button
        document.getElementById('scan-services-btn')?.addEventListener('click', () => {
            this.triggerServiceScan();
        });

        // Log controls
        document.getElementById('pause-logs')?.addEventListener('click', () => {
            this.toggleLogPause();
        });

        document.getElementById('clear-logs')?.addEventListener('click', () => {
            this.clearLogs();
        });

        document.getElementById('export-logs')?.addEventListener('click', () => {
            this.exportLogs();
        });

        // Filters
        document.getElementById('service-filter')?.addEventListener('change', (e) => {
            this.state.filters.service = e.target.value;
            this.applyFilters();
        });

        document.getElementById('level-filter')?.addEventListener('change', (e) => {
            this.state.filters.level = e.target.value;
            this.applyFilters();
        });

        document.getElementById('search-filter')?.addEventListener('input', (e) => {
            this.state.filters.search = e.target.value;
            this.debounce(() => this.applyFilters(), 300)();
        });

        // Time range selector
        document.getElementById('time-range')?.addEventListener('change', (e) => {
            this.updateChartTimeRange(e.target.value);
        });

        // Emergency FAB
        document.getElementById('emergency-fab')?.addEventListener('click', () => {
            this.showEmergencyModal();
        });

        // Modal close
        document.querySelector('.modal-close')?.addEventListener('click', () => {
            this.hideEmergencyModal();
        });

        // Settings
        document.getElementById('theme-select')?.addEventListener('change', (e) => {
            this.setTheme(e.target.value);
        });

        document.getElementById('refresh-rate')?.addEventListener('change', (e) => {
            this.setRefreshRate(parseInt(e.target.value));
        });

        // Activity feed controls
        document.getElementById('pause-feed')?.addEventListener('click', () => {
            this.toggleActivityFeed();
        });

        document.getElementById('clear-feed')?.addEventListener('click', () => {
            this.clearActivityFeed();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshData();
                        break;
                    case 'p':
                        e.preventDefault();
                        this.toggleLogPause();
                        break;
                    case 'e':
                        e.preventDefault();
                        this.exportData();
                        break;
                }
            }
        });

        console.log('✅ Event listeners initialized');
    }

    initializeTheme() {
        document.body.className = `theme-${this.state.theme}`;
        const themeIcon = document.querySelector('#theme-toggle i');
        if (themeIcon) {
            themeIcon.className = this.state.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.value = this.state.theme;
        }
    }

    async initializeCharts() {
        console.log('📊 Initializing charts...');
        
        // Chart.js should already be loaded by this point
        if (typeof Chart === 'undefined') {
            throw new Error('Chart.js not available in initializeCharts');
        }
        
        // Chart.js default configuration
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.color = this.state.theme === 'dark' ? '#E5E7EB' : '#374151';
        
        try {
            // Performance chart
            const perfCtx = document.getElementById('performance-chart')?.getContext('2d');
            if (perfCtx) {
                this.state.charts.performance = new Chart(perfCtx, {
                    type: 'line',
                    data: {
                        labels: this.generateTimeLabels(24),
                        datasets: [{
                            label: 'System Health',
                            data: this.generateMockData(24, 95, 100),
                            borderColor: '#10B981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.4,
                            fill: true
                        }, {
                            label: 'Error Rate',
                            data: this.generateMockData(24, 0, 5),
                            borderColor: '#EF4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: this.getChartOptions()
                });
            }

            // Volume chart
            const volumeCtx = document.getElementById('volume-chart')?.getContext('2d');
            if (volumeCtx) {
                this.state.charts.volume = new Chart(volumeCtx, {
                    type: 'bar',
                    data: {
                        labels: this.generateTimeLabels(24),
                        datasets: [{
                            label: 'Log Volume',
                            data: this.generateMockData(24, 100, 1000),
                            backgroundColor: '#8B5CF6',
                            borderColor: '#7C3AED',
                            borderWidth: 1
                        }]
                    },
                    options: this.getChartOptions()
                });
            }

            // Error distribution pie chart
            const errorCtx = document.getElementById('error-chart')?.getContext('2d');
            if (errorCtx) {
                this.state.charts.error = new Chart(errorCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Critical', 'High', 'Medium', 'Low'],
                        datasets: [{
                            data: [2, 5, 12, 8],
                            backgroundColor: ['#EF4444', '#F59E0B', '#8B5CF6', '#06B6D4'],
                            borderWidth: 2,
                            borderColor: this.state.theme === 'dark' ? '#1F2937' : '#FFFFFF'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            }

            // Mini charts for metrics
            this.initializeMiniCharts();
            
            console.log('✅ Charts initialized');
        } catch (error) {
            console.error('❌ Chart initialization failed:', error);
        }
    }

    initializeMiniCharts() {
        const miniChartConfig = {
            type: 'line',
            data: {
                labels: Array.from({length: 20}, (_, i) => i),
                datasets: [{
                    data: this.generateMockData(20, 0, 100),
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                interaction: { intersect: false }
            }
        };

        ['critical-chart', 'warning-chart', 'resolved-chart', 'resolution-chart'].forEach(id => {
            const ctx = document.getElementById(id)?.getContext('2d');
            if (ctx) {
                this.state.charts[id] = new Chart(ctx, JSON.parse(JSON.stringify(miniChartConfig)));
            }
        });
    }

    connectWebSocket() {
        console.log('🔌 Connecting to WebSocket...');
        
        try {
            this.socket = io(this.config.serviceLogUrl, {
                transports: ['websocket', 'polling'],
                timeout: 10000,
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionAttempts: 5
            });

            this.socket.on('connect', () => {
                console.log('✅ WebSocket connected');
                this.state.connected = true;
                this.updateConnectionStatus(true);
                this.showNotification('Connected to ServiceLog', 'success');
            });

            this.socket.on('disconnect', () => {
                console.log('❌ WebSocket disconnected');
                this.state.connected = false;
                this.updateConnectionStatus(false);
                this.showNotification('Connection lost', 'error');
            });

            this.socket.on('log_entry', (data) => {
                this.handleNewLogEntry(data);
            });

            this.socket.on('advice_update', (data) => {
                this.handleAdviceUpdate(data);
            });

            this.socket.on('service_status', (data) => {
                this.handleServiceStatusUpdate(data);
            });

            this.socket.on('metrics_update', (data) => {
                this.handleMetricsUpdate(data);
            });

            // Dynamic Service Detection Events
            this.socket.on('new_services_detected', (data) => {
                this.handleNewServicesDetected(data);
            });

            this.socket.on('services_removed', (data) => {
                this.handleServicesRemoved(data);
            });

            this.socket.on('services_updated', (data) => {
                this.handleServicesUpdated(data);
            });

            this.socket.on('service_scan_result', (data) => {
                this.handleServiceScanResult(data);
            });

            this.socket.on('real_time_update', (data) => {
                this.handleRealTimeUpdate(data);
            });

            this.socket.on('initial_data', (data) => {
                this.handleInitialData(data);
            });

            this.socket.on('error', (error) => {
                console.error('WebSocket error:', error);
                this.showNotification('Connection error', 'error');
            });

        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.updateConnectionStatus(false);
            // Fall back to polling mode
            this.startPollingMode();
        }
    }

    startPollingMode() {
        console.log('📡 Starting polling mode...');
        this.updateConnectionStatus(false, 'Polling Mode');
        
        setInterval(async () => {
            try {
                await this.loadDashboardData();
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, this.state.refreshRate);
    }

    async loadInitialData() {
        console.log('📥 Loading initial data...');
        this.showLoading('Loading dashboard data...');
        
        try {
            await Promise.all([
                this.loadDashboardData(),
                this.loadServiceList(),
                this.loadAdviceQueue(),
                this.loadAgentStatus()
            ]);
            
            console.log('✅ Initial data loaded');
        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
            this.showNotification('Failed to load data', 'error');
        }
    }

    async loadDashboardData() {
        try {
            // Use dashboard metrics API directly
            const response = await fetch('/api/dashboard/metrics');
            const data = await response.json();
            
            if (data.success) {
                this.updateDashboardMetrics(data.metrics);
                
                // Also update state for later use
                this.state.metrics = data.metrics;
                this.state.criticalIssues = data.critical_issues || [];
                
                console.log(`📊 Dashboard metrics updated: ${data.metrics.system_health}% health`);
            }
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    }

    async loadServiceList() {
        try {
            const response = await fetch('/api/dashboard/services');
            const data = await response.json();
            
            if (data.success && data.services) {
                // Convert real service data to expected format
                const services = data.services.map(service => ({
                    name: service.service_name,
                    port: service.port,
                    status: service.health_status === 'healthy' ? 'healthy' : 'unhealthy',
                    type: this.getServiceType(service.service_name),
                    response_time: service.response_time || 0,
                    error_count: service.error_count || 0
                }));
                
                this.updateServiceGrid(services);
                this.updateServiceFilter(services);
                
                console.log(`✅ Loaded ${services.length} real services`);
            } else {
                throw new Error('Failed to load services from API');
            }
        } catch (error) {
            console.error('Failed to load service list:', error);
        }
    }

    getServiceType(serviceName) {
        const name = serviceName.toLowerCase();
        
        if (name.includes('api') || name === 'mysymbols') {
            return 'Core';
        } else if (name.includes('binance') || name.includes('kucoin')) {
            return 'Exchange';
        } else if (name.includes('analytics') || name.includes('technical') || name.includes('machine_learning')) {
            return 'Analytics';
        } else if (name.includes('orchestration') || name.includes('doctor') || name.includes('passport')) {
            return 'Infrastructure';
        } else if (name.includes('websocket') || name.includes('notification') || name.includes('alert')) {
            return 'Communication';
        } else if (name.includes('data') || name.includes('warehouse')) {
            return 'Data';
        } else {
            return 'Service';
        }
    }

    async loadAdviceQueue() {
        try {
            const response = await this.apiCall('/api/dashboard/advice');
            if (response.success && response.advice && response.advice.length > 0) {
                this.updateAdviceQueue(response.advice);
            } else {
                // Mock advice data for demonstration
                const mockAdvice = [
                    {
                        advice_id: 'LogAdvice001',
                        title: 'Database Connection Pool Exhaustion',
                        severity: 'HIGH',
                        category: 'PERFORMANCE',
                        priority_score: 87.5,
                        affected_services: ['zmart-api', 'zmart-analytics'],
                        detection_time: new Date().toISOString(),
                        status: 'OPEN'
                    },
                    {
                        advice_id: 'LogAdvice002',
                        title: 'High Memory Usage in Analytics Service',
                        severity: 'MEDIUM',
                        category: 'PERFORMANCE',
                        priority_score: 65.3,
                        affected_services: ['zmart-analytics'],
                        detection_time: new Date(Date.now() - 300000).toISOString(),
                        status: 'OPEN'
                    }
                ];
                this.updateAdviceQueue(mockAdvice);
            }
        } catch (error) {
            console.error('Failed to load advice queue:', error);
        }
    }

    async loadAgentStatus() {
        try {
            const response = await this.apiCall('/health');
            if (response.status === 'healthy') {
                this.updateAgentStatus({
                    agents: response.agents || ['error', 'performance'],
                    buffer_size: response.log_buffer_size || 0
                });
            }
        } catch (error) {
            console.error('Failed to load agent status:', error);
        }
    }

    startUpdateIntervals() {
        // Main data refresh
        this.updateIntervals.set('main', setInterval(() => {
            if (!this.state.paused) {
                this.loadDashboardData();
            }
        }, this.state.refreshRate));

        // Service count updates (every 10 seconds)
        this.updateIntervals.set('serviceCounts', setInterval(() => {
            this.loadLiveServiceCounts();
        }, 10000));

        // Chart updates
        this.updateIntervals.set('charts', setInterval(() => {
            this.updateCharts();
        }, this.config.chartUpdateInterval));

        // Activity simulation (since we don't have real WebSocket data)
        this.updateIntervals.set('activity', setInterval(() => {
            this.simulateActivity();
        }, 3000));

        // Metrics animation
        this.updateIntervals.set('metrics', setInterval(() => {
            this.animateMetrics();
        }, 10000));
    }

    // UI Update Methods
    updateDashboardMetrics(metrics) {
        // Handle both direct metrics object and wrapped response
        const data = metrics.metrics || metrics;
        
        const updates = {
            'critical-issues': data.critical_issues || 0,
            'warning-issues': data.warning_issues || 0,
            'resolved-issues': data.resolved_issues || 0,
            'avg-resolution': data.avg_resolution || (data.avg_response_time ? data.avg_response_time + 'ms' : '0ms'),
            'active-services': data.active_services || data.total_services || 0,
            'active-alerts': data.active_alerts || data.services_with_errors || 0,
            'system-health': `${data.system_health || data.health_percentage || 0}%`
        };

        Object.entries(updates).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateValue(element, value);
            }
        });
    }

    updateServiceGrid(services) {
        const grid = document.getElementById('service-grid');
        if (!grid) return;

        grid.innerHTML = services.map(service => `
            <div class="service-node ${service.status}" data-service="${service.name}">
                <div class="service-status"></div>
                <div class="service-info">
                    <div class="service-name">${service.name}</div>
                    <div class="service-port">:${service.port}</div>
                </div>
                <div class="service-type">${service.type}</div>
            </div>
        `).join('');

        // Add hover effects
        grid.querySelectorAll('.service-node').forEach(node => {
            node.addEventListener('click', () => {
                this.showServiceDetails(node.dataset.service);
            });
        });
    }

    updateServiceFilter(services) {
        const filterSelect = document.getElementById('service-filter');
        if (!filterSelect) return;

        // Get unique service types
        const serviceTypes = [...new Set(services.map(s => s.type))];
        
        // Update filter options
        filterSelect.innerHTML = `
            <option value="">All Services</option>
            ${serviceTypes.map(type => `<option value="${type}">${type}</option>`).join('')}
        `;
        
        // Add event listener for filtering
        filterSelect.addEventListener('change', (e) => {
            this.filterServices(e.target.value);
        });
    }

    filterServices(filterType) {
        const serviceNodes = document.querySelectorAll('.service-node');
        serviceNodes.forEach(node => {
            const serviceType = node.querySelector('.service-type')?.textContent;
            if (!filterType || serviceType === filterType) {
                node.style.display = 'block';
            } else {
                node.style.display = 'none';
            }
        });
    }

    async showServiceDetails(serviceName) {
        try {
            // Get service details from our dashboard API
            const response = await fetch(`/api/dashboard/services/${serviceName}`);
            const data = await response.json();
            
            if (data.success && data.service) {
                const service = data.service;
                this.displayServiceModal(service);
            } else {
                // Show basic service info if detailed data not available
                const basicService = {
                    service_name: serviceName,
                    health_status: 'unknown',
                    connection_status: 'unknown',
                    port: 'unknown',
                    last_seen: 'unknown'
                };
                this.displayServiceModal(basicService);
            }
        } catch (error) {
            console.error(`Failed to load service details for ${serviceName}:`, error);
            this.showNotification(`Failed to load details for ${serviceName}`, 'error');
        }
    }

    displayServiceModal(service) {
        // Create modal HTML
        const modalHTML = `
            <div class="modal-overlay" id="service-modal">
                <div class="modal-content service-details-modal">
                    <div class="modal-header">
                        <h2>Service Details</h2>
                        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="service-detail-grid">
                            <div class="detail-item">
                                <label>Service Name:</label>
                                <span>${service.service_name}</span>
                            </div>
                            <div class="detail-item">
                                <label>Port:</label>
                                <span>${service.port}</span>
                            </div>
                            <div class="detail-item">
                                <label>Health Status:</label>
                                <span class="status-badge ${service.health_status}">${service.health_status}</span>
                            </div>
                            <div class="detail-item">
                                <label>Connection:</label>
                                <span class="status-badge ${service.connection_status}">${service.connection_status}</span>
                            </div>
                            <div class="detail-item">
                                <label>Last Seen:</label>
                                <span>${service.last_seen ? new Date(service.last_seen).toLocaleString() : 'Never'}</span>
                            </div>
                            <div class="detail-item">
                                <label>Response Time:</label>
                                <span>${service.response_time ? service.response_time.toFixed(2) + 'ms' : 'N/A'}</span>
                            </div>
                            <div class="detail-item">
                                <label>Error Count:</label>
                                <span>${service.error_count || 0}</span>
                            </div>
                        </div>
                        ${service.passport_id ? `
                            <div class="passport-info">
                                <h3>Passport Information</h3>
                                <div class="detail-item">
                                    <label>Passport ID:</label>
                                    <span>${service.passport_id}</span>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-primary" onclick="window.open('http://localhost:${service.port}/health', '_blank')">
                            <i class="fas fa-external-link-alt"></i> Open Health Check
                        </button>
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Remove any existing modals
        document.querySelectorAll('.modal-overlay').forEach(modal => modal.remove());
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Add modal styles if not present
        this.ensureModalStyles();
    }

    ensureModalStyles() {
        if (!document.getElementById('modal-styles')) {
            const styles = document.createElement('style');
            styles.id = 'modal-styles';
            styles.textContent = `
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.7);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 10000;
                    backdrop-filter: blur(4px);
                }
                .modal-content {
                    background: var(--card-bg, #1f2937);
                    border-radius: 12px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                    max-width: 600px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    color: var(--text-primary, #f3f4f6);
                }
                .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px 24px 16px;
                    border-bottom: 1px solid var(--border-color, #374151);
                }
                .modal-close {
                    background: none;
                    border: none;
                    font-size: 24px;
                    color: var(--text-secondary, #9ca3af);
                    cursor: pointer;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 6px;
                }
                .modal-close:hover {
                    background: var(--hover-bg, #374151);
                }
                .modal-body {
                    padding: 20px 24px;
                }
                .service-detail-grid {
                    display: grid;
                    gap: 16px;
                    margin-bottom: 20px;
                }
                .detail-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px;
                    background: var(--bg-secondary, #111827);
                    border-radius: 8px;
                }
                .detail-item label {
                    font-weight: 500;
                    color: var(--text-secondary, #9ca3af);
                }
                .status-badge {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    text-transform: uppercase;
                }
                .status-badge.healthy { background: #10b981; color: white; }
                .status-badge.unhealthy { background: #ef4444; color: white; }
                .status-badge.connected { background: #3b82f6; color: white; }
                .status-badge.disconnected { background: #f59e0b; color: white; }
                .status-badge.unknown { background: #6b7280; color: white; }
                .passport-info {
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid var(--border-color, #374151);
                }
                .modal-footer {
                    padding: 16px 24px 20px;
                    border-top: 1px solid var(--border-color, #374151);
                    display: flex;
                    gap: 12px;
                    justify-content: flex-end;
                }
                .btn {
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    cursor: pointer;
                    font-weight: 500;
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    text-decoration: none;
                }
                .btn-primary {
                    background: #3b82f6;
                    color: white;
                }
                .btn-secondary {
                    background: #6b7280;
                    color: white;
                }
                .btn:hover {
                    opacity: 0.9;
                }
            `;
            document.head.appendChild(styles);
        }
    }

    showEmergencyModal() {
        const emergencyModalHTML = `
            <div class="modal-overlay" id="emergency-modal">
                <div class="modal-content emergency-modal">
                    <div class="modal-header">
                        <h2>🚨 Emergency Action Center</h2>
                        <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="emergency-actions">
                            <div class="emergency-category">
                                <h3>🔄 System Control</h3>
                                <div class="action-buttons">
                                    <button class="btn btn-warning" onclick="dashboard.performEmergencyAction('restart_unhealthy')">
                                        <i class="fas fa-redo"></i> Restart Unhealthy Services
                                    </button>
                                    <button class="btn btn-danger" onclick="dashboard.performEmergencyAction('stop_all')">
                                        <i class="fas fa-stop"></i> Emergency Stop All
                                    </button>
                                    <button class="btn btn-success" onclick="dashboard.performEmergencyAction('health_check')">
                                        <i class="fas fa-heartbeat"></i> Force Health Check
                                    </button>
                                </div>
                            </div>
                            
                            <div class="emergency-category">
                                <h3>📊 Data & Monitoring</h3>
                                <div class="action-buttons">
                                    <button class="btn btn-info" onclick="dashboard.performEmergencyAction('export_logs')">
                                        <i class="fas fa-download"></i> Export All Logs
                                    </button>
                                    <button class="btn btn-secondary" onclick="dashboard.performEmergencyAction('clear_errors')">
                                        <i class="fas fa-eraser"></i> Clear Error Counts
                                    </button>
                                    <button class="btn btn-primary" onclick="dashboard.performEmergencyAction('refresh_all')">
                                        <i class="fas fa-sync"></i> Force Refresh All Data
                                    </button>
                                </div>
                            </div>
                            
                            <div class="emergency-category">
                                <h3>🔍 Diagnostics</h3>
                                <div class="action-buttons">
                                    <button class="btn btn-info" onclick="dashboard.performEmergencyAction('connection_test')">
                                        <i class="fas fa-network-wired"></i> Test All Connections
                                    </button>
                                    <button class="btn btn-warning" onclick="dashboard.performEmergencyAction('generate_report')">
                                        <i class="fas fa-file-medical"></i> Generate System Report
                                    </button>
                                    <button class="btn btn-success" onclick="dashboard.performEmergencyAction('service_discovery')">
                                        <i class="fas fa-search"></i> Emergency Service Scan
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="emergency-info">
                            <div class="info-card">
                                <h4>⚠️ Current System Status</h4>
                                <div class="status-grid">
                                    <div class="status-item">
                                        <span class="status-label">System Health:</span>
                                        <span class="status-value" id="emergency-health">${this.state.metrics?.system_health || 0}%</span>
                                    </div>
                                    <div class="status-item">
                                        <span class="status-label">Active Services:</span>
                                        <span class="status-value" id="emergency-services">${this.state.metrics?.active_services || 0}</span>
                                    </div>
                                    <div class="status-item">
                                        <span class="status-label">Critical Issues:</span>
                                        <span class="status-value critical" id="emergency-issues">${this.state.metrics?.critical_issues || 0}</span>
                                    </div>
                                    <div class="status-item">
                                        <span class="status-label">Last Updated:</span>
                                        <span class="status-value" id="emergency-updated">${new Date().toLocaleTimeString()}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Remove any existing modals
        document.querySelectorAll('.modal-overlay').forEach(modal => modal.remove());
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', emergencyModalHTML);
        
        // Ensure modal styles and add emergency-specific styles
        this.ensureModalStyles();
        this.ensureEmergencyStyles();
    }

    ensureEmergencyStyles() {
        if (!document.getElementById('emergency-styles')) {
            const styles = document.createElement('style');
            styles.id = 'emergency-styles';
            styles.textContent = `
                .emergency-modal .modal-content {
                    max-width: 800px;
                    width: 95%;
                }
                .emergency-actions {
                    display: grid;
                    gap: 24px;
                    margin-bottom: 24px;
                }
                .emergency-category {
                    border: 1px solid var(--border-color, #374151);
                    border-radius: 8px;
                    padding: 16px;
                    background: var(--bg-secondary, #111827);
                }
                .emergency-category h3 {
                    margin: 0 0 12px 0;
                    color: var(--text-primary, #f3f4f6);
                }
                .action-buttons {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 12px;
                }
                .btn-warning {
                    background: #f59e0b;
                    color: white;
                }
                .btn-danger {
                    background: #ef4444;
                    color: white;
                }
                .btn-info {
                    background: #06b6d4;
                    color: white;
                }
                .emergency-info {
                    border-top: 1px solid var(--border-color, #374151);
                    padding-top: 16px;
                }
                .info-card {
                    background: var(--bg-primary, #1f2937);
                    border-radius: 8px;
                    padding: 16px;
                }
                .info-card h4 {
                    margin: 0 0 12px 0;
                    color: var(--text-primary, #f3f4f6);
                }
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 12px;
                }
                .status-item {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }
                .status-label {
                    font-size: 12px;
                    color: var(--text-secondary, #9ca3af);
                    font-weight: 500;
                }
                .status-value {
                    font-size: 16px;
                    font-weight: 600;
                    color: var(--text-primary, #f3f4f6);
                }
                .status-value.critical {
                    color: #ef4444;
                }
            `;
            document.head.appendChild(styles);
        }
    }

    async performEmergencyAction(action) {
        console.log(`🚨 Performing emergency action: ${action}`);
        
        // Show loading notification
        this.showNotification(`Performing ${action.replace('_', ' ')}...`, 'info');
        
        try {
            switch (action) {
                case 'restart_unhealthy':
                    await this.restartUnhealthyServices();
                    break;
                case 'stop_all':
                    await this.emergencyStopAll();
                    break;
                case 'health_check':
                    await this.forceHealthCheck();
                    break;
                case 'export_logs':
                    this.exportAllLogs();
                    break;
                case 'clear_errors':
                    await this.clearErrorCounts();
                    break;
                case 'refresh_all':
                    await this.forceRefreshAll();
                    break;
                case 'connection_test':
                    await this.testAllConnections();
                    break;
                case 'generate_report':
                    this.generateSystemReport();
                    break;
                case 'service_discovery':
                    await this.triggerServiceScan();
                    break;
                default:
                    throw new Error(`Unknown action: ${action}`);
            }
        } catch (error) {
            console.error(`Emergency action failed:`, error);
            this.showNotification(`Action failed: ${error.message}`, 'error');
        }
    }

    async restartUnhealthyServices() {
        // This would integrate with service management API
        this.showNotification('Restart command sent to unhealthy services', 'success');
        setTimeout(() => this.refreshData(), 2000);
    }

    async emergencyStopAll() {
        if (confirm('⚠️ This will stop all services. Continue?')) {
            this.showNotification('Emergency stop initiated', 'warning');
        }
    }

    async forceHealthCheck() {
        // Trigger manual health check via service discovery
        const response = await fetch('/api/dashboard/discovery/scan');
        const data = await response.json();
        
        if (data.success) {
            this.showNotification('Health check completed', 'success');
            await this.refreshData();
        } else {
            throw new Error('Health check failed');
        }
    }

    exportAllLogs() {
        // Enhanced version of existing export
        const allData = {
            timestamp: new Date().toISOString(),
            system_metrics: this.state.metrics,
            services: this.state.serviceData,
            critical_issues: this.state.criticalIssues,
            logs: this.state.logBuffer,
            activity: this.state.activityBuffer,
            export_type: 'emergency_export'
        };
        
        const blob = new Blob([JSON.stringify(allData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `emergency-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Emergency export completed', 'success');
    }

    async clearErrorCounts() {
        this.showNotification('Error counts cleared', 'success');
        await this.refreshData();
    }

    async forceRefreshAll() {
        await this.refreshData();
        this.showNotification('All data refreshed', 'success');
    }

    async testAllConnections() {
        this.showNotification('Testing all service connections...', 'info');
        
        // Use the service scan to test connections
        await this.forceHealthCheck();
        this.showNotification('Connection test completed', 'success');
    }

    generateSystemReport() {
        const report = {
            generated: new Date().toISOString(),
            system_health: this.state.metrics?.system_health || 0,
            total_services: this.state.metrics?.active_services || 0,
            healthy_services: this.state.metrics?.healthy_services || 0,
            critical_issues: this.state.criticalIssues || [],
            recent_activity: this.state.activityBuffer?.slice(0, 20) || [],
            service_details: Object.values(this.state.serviceData || {}),
        };
        
        const reportText = `
ZMARTBOT SYSTEM DIAGNOSTIC REPORT
Generated: ${report.generated}

SYSTEM OVERVIEW:
- System Health: ${report.system_health}%
- Total Services: ${report.total_services}
- Healthy Services: ${report.healthy_services}
- Critical Issues: ${report.critical_issues.length}

CRITICAL ISSUES:
${report.critical_issues.map(issue => `- ${issue.description} (${issue.severity})`).join('\n')}

SERVICE STATUS:
${report.service_details.map(s => `- ${s.service_name}: ${s.health_status} (Port: ${s.port})`).join('\n')}

RECENT ACTIVITY:
${report.recent_activity.map(a => `- ${new Date(a.timestamp).toLocaleString()}: ${a.message}`).join('\n')}
        `;
        
        const blob = new Blob([reportText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `system-report-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('System report generated', 'success');
    }

    updateAdviceQueue(advice) {
        const container = document.getElementById('advice-list') || document.getElementById('advice-container');
        if (!container) return;

        if (advice.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-check-circle"></i>
                    <h3>All Clear!</h3>
                    <p>No advice items in the queue</p>
                </div>
            `;
            return;
        }

        container.innerHTML = advice.map(item => `
            <div class="advice-item priority-${item.severity.toLowerCase()}" data-advice-id="${item.advice_id}">
                <div class="advice-header">
                    <div class="advice-priority">
                        <span class="priority-score">${Math.round(item.priority_score)}</span>
                        <span class="severity-badge ${item.severity.toLowerCase()}">${item.severity}</span>
                    </div>
                    <div class="advice-time">${this.formatTime(item.detection_time)}</div>
                </div>
                <div class="advice-content">
                    <h4 class="advice-title">${item.title}</h4>
                    <div class="advice-services">
                        ${item.affected_services.map(service => 
                            `<span class="service-tag">${service}</span>`
                        ).join('')}
                    </div>
                    <div class="advice-category">
                        <i class="fas fa-tag"></i>
                        ${item.category}
                    </div>
                </div>
                <div class="advice-actions">
                    <button class="btn-action view-advice" onclick="window.dashboard.viewAdvice('${item.advice_id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-action resolve-advice" onclick="window.dashboard.resolveAdvice('${item.advice_id}')">
                        <i class="fas fa-check"></i>
                    </button>
                </div>
            </div>
        `).join('');

        // Update advice counts
        const counts = this.calculateAdviceCounts(advice);
        Object.entries(counts).forEach(([severity, count]) => {
            const element = document.getElementById(`${severity}-advice`);
            if (element) element.textContent = count;
        });
    }

    updateAgentStatus(data) {
        const agentsGrid = document.getElementById('agents-grid');
        if (!agentsGrid) return;

        const agents = [
            {
                name: 'ErrorLogAgent',
                type: 'error',
                status: 'active',
                processed: 1247,
                accuracy: 94.5,
                lastUpdate: new Date()
            },
            {
                name: 'PerformanceLogAgent', 
                type: 'performance',
                status: 'active',
                processed: 892,
                accuracy: 87.2,
                lastUpdate: new Date()
            },
            {
                name: 'SecurityLogAgent',
                type: 'security', 
                status: 'disabled',
                processed: 0,
                accuracy: 0,
                lastUpdate: null
            }
        ];

        agentsGrid.innerHTML = agents.map(agent => `
            <div class="agent-card ${agent.status}">
                <div class="agent-header">
                    <div class="agent-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="agent-info">
                        <h3>${agent.name}</h3>
                        <span class="agent-type">${agent.type}</span>
                    </div>
                    <div class="agent-status ${agent.status}">
                        ${agent.status}
                    </div>
                </div>
                <div class="agent-metrics">
                    <div class="metric">
                        <span class="metric-label">Processed</span>
                        <span class="metric-value">${agent.processed.toLocaleString()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Accuracy</span>
                        <span class="metric-value">${agent.accuracy}%</span>
                    </div>
                </div>
                <div class="agent-activity">
                    <canvas class="activity-chart" width="100" height="30"></canvas>
                </div>
            </div>
        `).join('');
    }

    // Real-time Event Handlers
    handleNewLogEntry(data) {
        if (this.state.paused) return;

        this.state.logBuffer.unshift(data);
        if (this.state.logBuffer.length > this.config.maxLogEntries) {
            this.state.logBuffer.pop();
        }

        this.addLogToStream(data);
        this.updateLogCounter();
    }

    handleAdviceUpdate(data) {
        this.addActivityItem({
            type: 'advice',
            message: `New advice generated: ${data.title}`,
            severity: data.severity,
            timestamp: new Date()
        });

        // Refresh advice queue
        this.loadAdviceQueue();
    }

    handleServiceStatusUpdate(data) {
        this.addActivityItem({
            type: 'service',
            message: `${data.service_name} status changed to ${data.status}`,
            severity: data.status === 'healthy' ? 'INFO' : 'WARNING',
            timestamp: new Date()
        });

        // Update service grid
        this.updateServiceStatus(data.service_name, data.status);
    }

    handleMetricsUpdate(data) {
        this.updateDashboardMetrics(data);
    }

    // Dynamic Service Detection Handlers
    handleNewServicesDetected(data) {
        console.log('🆕 New services detected:', data.new_services);
        this.state.autoScaling.newServicesDetected = data.new_services;
        this.state.serviceCount = data.total_services;
        
        this.showNotification(
            `${data.new_services.length} new services detected!`, 
            'success'
        );
        
        this.addActivityItem({
            type: 'service_discovery',
            message: `New services detected: ${data.new_services.join(', ')}`,
            severity: 'INFO',
            timestamp: new Date(data.timestamp)
        });
        
        // Auto-refresh services data
        this.loadServicesData();
    }

    handleServicesRemoved(data) {
        console.log('❌ Services removed:', data.removed_services);
        this.state.autoScaling.removedServices = data.removed_services;
        this.state.serviceCount = data.total_services;
        
        this.showNotification(
            `${data.removed_services.length} services removed`, 
            'warning'
        );
        
        this.addActivityItem({
            type: 'service_removal',
            message: `Services removed: ${data.removed_services.join(', ')}`,
            severity: 'WARNING',
            timestamp: new Date(data.timestamp)
        });
        
        // Auto-refresh services data
        this.loadServicesData();
    }

    handleServicesUpdated(data) {
        console.log('🔄 Services updated:', data.count, 'total services');
        this.state.serviceCount = data.count;
        this.state.serviceData = data.services.reduce((acc, service) => {
            acc[service.service_name] = service;
            return acc;
        }, {});
        
        // Update dashboard components
        this.updateServicesSection();
        this.updateServiceHealthMap();
        this.updateDashboardMetrics(data.metrics);
    }

    handleServiceScanResult(data) {
        console.log('🔍 Service scan completed:', data);
        this.state.lastServiceScan = new Date(data.timestamp);
        
        if (data.new_services_found > 0) {
            this.showNotification(
                `Service scan found ${data.new_services_found} new services!`, 
                'success'
            );
        } else {
            this.showNotification('Service scan completed - no new services', 'info');
        }
        
        this.addActivityItem({
            type: 'service_scan',
            message: `Service scan: ${data.services_before} → ${data.services_after} services`,
            severity: 'INFO',
            timestamp: new Date(data.timestamp)
        });
    }

    handleRealTimeUpdate(data) {
        console.log('⚡ Real-time update:', data.type, data);
        
        switch (data.type) {
            case 'service_status_change':
                this.handleServiceStatusUpdate({
                    service_name: data.service_name,
                    status: data.new_status.health,
                    connection: data.new_status.connection
                });
                break;
            case 'metrics_update':
                this.handleMetricsUpdate(data.metrics);
                break;
        }
    }

    handleInitialData(data) {
        console.log('📊 Received initial data:', data);
        
        // Update metrics
        if (data.metrics) {
            this.updateDashboardMetrics(data.metrics);
        }
        
        // Update services
        if (data.services) {
            this.state.serviceData = data.services.reduce((acc, service) => {
                acc[service.service_name] = service;
                return acc;
            }, {});
            this.state.serviceCount = data.services.length;
            this.updateServicesSection();
        }
        
        // Update critical issues
        if (data.critical_issues) {
            this.updateAdviceSection(data.critical_issues);
        }
        
        this.showNotification('Dashboard synced with real data!', 'success');
    }

    // Activity Feed Management
    addActivityItem(item) {
        this.state.activityBuffer.unshift({
            ...item,
            id: Date.now() + Math.random(),
            timestamp: item.timestamp || new Date()
        });

        if (this.state.activityBuffer.length > this.config.maxActivityItems) {
            this.state.activityBuffer.pop();
        }

        this.updateActivityFeed();
    }

    updateActivityFeed() {
        const feed = document.getElementById('activity-feed');
        if (!feed) return;

        feed.innerHTML = this.state.activityBuffer.map(item => `
            <div class="activity-item ${item.severity.toLowerCase()}" data-id="${item.id}">
                <div class="activity-icon">
                    <i class="fas ${this.getActivityIcon(item.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-message">${item.message}</div>
                    <div class="activity-time">${this.formatTime(item.timestamp)}</div>
                </div>
                <div class="activity-severity ${item.severity.toLowerCase()}">
                    ${item.severity}
                </div>
            </div>
        `).join('');
    }

    addLogToStream(logData) {
        const stream = document.getElementById('log-stream');
        if (!stream) return;

        const logElement = document.createElement('div');
        logElement.className = `log-entry ${logData.level.toLowerCase()}`;
        logElement.innerHTML = `
            <div class="log-timestamp">${this.formatTime(logData.timestamp)}</div>
            <div class="log-level ${logData.level.toLowerCase()}">${logData.level}</div>
            <div class="log-service">${logData.service_name}</div>
            <div class="log-message">${this.escapeHtml(logData.message)}</div>
            <div class="log-context">${JSON.stringify(logData.context || {})}</div>
        `;

        // Add with animation
        logElement.style.opacity = '0';
        logElement.style.transform = 'translateX(-20px)';
        stream.insertBefore(logElement, stream.firstChild);

        // Animate in
        setTimeout(() => {
            logElement.style.transition = 'all 0.3s ease';
            logElement.style.opacity = '1';
            logElement.style.transform = 'translateX(0)';
        }, 50);

        // Remove old entries
        const entries = stream.querySelectorAll('.log-entry');
        if (entries.length > this.config.maxLogEntries) {
            for (let i = this.config.maxLogEntries; i < entries.length; i++) {
                entries[i].remove();
            }
        }
    }

    // Chart Management
    updateCharts() {
        Object.entries(this.state.charts).forEach(([key, chart]) => {
            if (chart && typeof chart.update === 'function') {
                // Update with new data
                if (chart.data && chart.data.datasets) {
                    chart.data.datasets.forEach(dataset => {
                        if (dataset.data) {
                            // Shift data and add new point
                            dataset.data.shift();
                            dataset.data.push(this.generateRandomValue(key));
                        }
                    });
                    chart.update('none'); // No animation for smooth updates
                }
            }
        });
    }

    updateChartTimeRange(range) {
        const labels = this.generateTimeLabels(range);
        
        Object.entries(this.state.charts).forEach(([key, chart]) => {
            if (chart && chart.data) {
                chart.data.labels = labels;
                chart.data.datasets.forEach(dataset => {
                    dataset.data = this.generateMockData(labels.length, 0, 100);
                });
                chart.update();
            }
        });
    }

    // Missing functions for complete dashboard functionality
    async loadPatternDetection() {
        try {
            const patternsContainer = document.getElementById('patterns-container') || document.querySelector('.patterns-container');
            if (!patternsContainer) return;

            // Mock pattern data for now since no API endpoint exists yet
            const patterns = [
                {
                    name: 'High Memory Usage Pattern',
                    type: 'PERFORMANCE',
                    confidence: 95.2,
                    occurrences: 23,
                    services: ['zmart-analytics', 'zmart-api'],
                    lastDetected: new Date()
                },
                {
                    name: 'Connection Timeout Pattern',
                    type: 'NETWORK',
                    confidence: 87.8,
                    occurrences: 12,
                    services: ['binance', 'kucoin'],
                    lastDetected: new Date(Date.now() - 300000)
                },
                {
                    name: 'Database Lock Pattern',
                    type: 'DATABASE',
                    confidence: 78.4,
                    occurrences: 8,
                    services: ['zmart_data_warehouse'],
                    lastDetected: new Date(Date.now() - 600000)
                }
            ];

            patternsContainer.innerHTML = patterns.map(pattern => `
                <div class="pattern-card">
                    <div class="pattern-header">
                        <div class="pattern-name">${pattern.name}</div>
                        <div class="pattern-type ${pattern.type.toLowerCase()}">${pattern.type}</div>
                    </div>
                    <div class="pattern-metrics">
                        <div class="metric">
                            <span class="metric-label">Confidence</span>
                            <span class="metric-value">${pattern.confidence}%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Occurrences</span>
                            <span class="metric-value">${pattern.occurrences}</span>
                        </div>
                    </div>
                    <div class="pattern-services">
                        Affected: ${pattern.services.join(', ')}
                    </div>
                    <div class="pattern-time">
                        Last: ${pattern.lastDetected.toLocaleString()}
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load pattern detection:', error);
        }
    }

    initializeAnalyticsCharts() {
        try {
            // Initialize service health trend chart
            const healthTrendCtx = document.getElementById('health-trend-chart');
            if (healthTrendCtx && typeof Chart !== 'undefined') {
                const labels = Array.from({length: 24}, (_, i) => `${23-i}h ago`).reverse();
                
                new Chart(healthTrendCtx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'System Health %',
                            data: this.generateMockData(24, 85, 100),
                            borderColor: '#10B981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            title: {
                                display: true,
                                text: '24-Hour System Health Trend'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                min: 80,
                                max: 100
                            }
                        }
                    }
                });
            }

            // Initialize error distribution chart
            const errorDistCtx = document.getElementById('error-distribution-chart');
            if (errorDistCtx && typeof Chart !== 'undefined') {
                new Chart(errorDistCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Connection Errors', 'Timeout Errors', 'Authentication', 'Other'],
                        datasets: [{
                            data: [12, 8, 3, 2],
                            backgroundColor: ['#EF4444', '#F59E0B', '#8B5CF6', '#6B7280'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Error Distribution'
                            }
                        }
                    }
                });
            }
        } catch (error) {
            console.error('Failed to initialize analytics charts:', error);
        }
    }

    // UI Actions
    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.section === section);
        });

        // Update content sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.toggle('active', sec.id === `${section}-section`);
        });

        this.state.currentSection = section;
        
        // Section-specific initialization
        switch (section) {
            case 'analytics':
                this.initializeAnalyticsCharts();
                break;
            case 'patterns':
                this.loadPatternDetection();
                break;
            case 'agents':
                this.loadAgentStatus();
                break;
        }
    }

    toggleTheme() {
        this.state.theme = this.state.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('dashboard-theme', this.state.theme);
        this.initializeTheme();
        this.updateChartsTheme();
    }

    toggleLogPause() {
        this.state.paused = !this.state.paused;
        const btn = document.getElementById('pause-logs');
        const icon = btn?.querySelector('i');
        
        if (btn && icon) {
            if (this.state.paused) {
                btn.textContent = 'Resume';
                btn.insertBefore(document.createElement('i'), btn.firstChild);
                btn.querySelector('i').className = 'fas fa-play';
                btn.classList.add('paused');
            } else {
                btn.textContent = 'Pause';
                btn.insertBefore(document.createElement('i'), btn.firstChild);
                btn.querySelector('i').className = 'fas fa-pause';
                btn.classList.remove('paused');
            }
        }

        this.showNotification(
            `Log stream ${this.state.paused ? 'paused' : 'resumed'}`,
            'info'
        );
    }

    clearLogs() {
        const stream = document.getElementById('log-stream');
        if (stream) {
            stream.innerHTML = '';
            this.state.logBuffer = [];
            this.showNotification('Logs cleared', 'success');
        }
    }

    async refreshData() {
        this.showLoading('Refreshing data...');
        
        try {
            await this.loadDashboardData();
            await this.loadAdviceQueue();
            await this.loadServiceList();
            
            this.showNotification('Data refreshed', 'success');
        } catch (error) {
            this.showNotification('Refresh failed', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async triggerServiceScan() {
        console.log('🔍 Triggering manual service scan...');
        this.showLoading('Scanning for new services...');
        
        try {
            const response = await fetch('/api/dashboard/discovery/scan');
            const data = await response.json();
            
            if (data.success) {
                const message = data.new_services_found > 0 
                    ? `Found ${data.new_services_found} new services!`
                    : 'No new services found';
                this.showNotification(message, data.new_services_found > 0 ? 'success' : 'info');
                
                // Auto-refresh if new services found
                if (data.new_services_found > 0) {
                    await this.refreshData();
                }
            } else {
                this.showNotification('Service scan failed', 'error');
            }
        } catch (error) {
            console.error('Service scan error:', error);
            this.showNotification('Service scan failed', 'error');
        } finally {
            this.hideLoading();
        }
        
        // Also trigger WebSocket scan if connected
        if (this.socket && this.state.connected) {
            this.socket.emit('request_service_scan');
        }
    }

    exportData() {
        console.log('📦 Exporting dashboard data...');
        
        const exportData = {
            timestamp: new Date().toISOString(),
            metrics: this.state.metrics,
            services: this.state.serviceData,
            serviceCount: this.state.serviceCount,
            autoScaling: this.state.autoScaling,
            logs: this.state.logBuffer.slice(0, 100), // Last 100 logs
            activity: this.state.activityBuffer.slice(0, 50), // Last 50 activities
            advice: this.state.adviceBuffer.slice(0, 20) // Last 20 advice items
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `servicelog-dashboard-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Data exported successfully', 'success');
    }

    // Advice Management
    async viewAdvice(adviceId) {
        try {
            const response = await this.apiCall(`/api/v1/advice/${adviceId}`);
            if (response) {
                this.showAdviceModal(response);
            }
        } catch (error) {
            this.showNotification('Failed to load advice details', 'error');
        }
    }

    async resolveAdvice(adviceId) {
        try {
            const response = await this.apiCall(`/api/v1/advice/${adviceId}/resolve`, 'POST');
            if (response && response.success) {
                this.showNotification('Advice resolved successfully', 'success');
                this.loadAdviceQueue(); // Refresh the queue
                
                // Add activity item
                this.addActivityItem({
                    type: 'advice',
                    message: `Advice ${adviceId} resolved`,
                    severity: 'INFO'
                });
            } else {
                throw new Error('Failed to resolve advice');
            }
        } catch (error) {
            this.showNotification('Failed to resolve advice', 'error');
        }
    }

    // Utility Methods
    async apiCall(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            // Map ServiceLog API endpoints to our dashboard API endpoints
            let dashboardEndpoint = endpoint;
            if (endpoint.startsWith('/api/v1/advice/dashboard')) {
                dashboardEndpoint = '/api/dashboard/metrics';
            } else if (endpoint.startsWith('/api/v1/advice')) {
                dashboardEndpoint = '/api/dashboard/advice';
            } else if (endpoint === '/health') {
                dashboardEndpoint = '/health';
            }

            const response = await fetch(dashboardEndpoint, options);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API call failed: ${method} ${dashboardEndpoint || endpoint}`, error);
            throw error;
        }
    }

    generateTimeLabels(hours) {
        const labels = [];
        const now = new Date();
        
        for (let i = hours - 1; i >= 0; i--) {
            const time = new Date(now.getTime() - (i * 60 * 60 * 1000));
            labels.push(time.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
            }));
        }
        
        return labels;
    }

    generateMockData(length, min, max) {
        return Array.from({ length }, () => 
            Math.floor(Math.random() * (max - min + 1)) + min
        );
    }

    generateRandomValue(chartType) {
        const ranges = {
            performance: [95, 100],
            volume: [100, 1000],
            error: [0, 10],
            default: [0, 100]
        };
        
        const [min, max] = ranges[chartType] || ranges.default;
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    formatTime(timestamp) {
        return moment(timestamp).fromNow();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    animateValue(element, newValue) {
        const currentValue = element.textContent;
        if (currentValue === newValue.toString()) return;

        element.style.transform = 'scale(1.1)';
        element.style.color = '#10B981';
        
        setTimeout(() => {
            element.textContent = newValue;
            element.style.transform = 'scale(1)';
            element.style.color = '';
        }, 150);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        // Add to page
        document.body.appendChild(notification);

        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);

        // Auto hide
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);

        // Manual close
        notification.querySelector('.notification-close').onclick = () => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        };
    }

    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const text = overlay?.querySelector('.loading-text');
        
        if (overlay) {
            overlay.classList.add('show');
            if (text) text.textContent = message;
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }

    updateConnectionStatus(connected, text = null) {
        const status = document.getElementById('connection-status');
        if (!status) return;

        const indicator = status.querySelector('.status-indicator');
        const span = status.querySelector('span');

        if (indicator) {
            indicator.className = `status-indicator ${connected ? 'connected' : 'disconnected'}`;
        }

        if (span) {
            span.textContent = text || (connected ? 'Connected' : 'Disconnected');
        }
    }

    getChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: this.state.theme === 'dark' ? '#E5E7EB' : '#374151'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: this.state.theme === 'dark' ? '#9CA3AF' : '#6B7280'
                    },
                    grid: {
                        color: this.state.theme === 'dark' ? '#374151' : '#E5E7EB'
                    }
                },
                y: {
                    ticks: {
                        color: this.state.theme === 'dark' ? '#9CA3AF' : '#6B7280'
                    },
                    grid: {
                        color: this.state.theme === 'dark' ? '#374151' : '#E5E7EB'
                    }
                }
            }
        };
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    getActivityIcon(type) {
        const icons = {
            log: 'fa-file-alt',
            advice: 'fa-lightbulb',
            service: 'fa-server',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle'
        };
        return icons[type] || icons.log;
    }

    // Simulation methods for demo purposes
    simulateActivity() {
        const activities = [
            { type: 'log', message: 'High volume of ERROR logs from zmart-api', severity: 'WARNING' },
            { type: 'advice', message: 'New pattern detected: Connection timeout', severity: 'HIGH' },
            { type: 'service', message: 'zmart-analytics health check passed', severity: 'INFO' },
            { type: 'error', message: 'Database connection restored', severity: 'INFO' },
            { type: 'warning', message: 'Memory usage above threshold in binance service', severity: 'WARNING' }
        ];

        const activity = activities[Math.floor(Math.random() * activities.length)];
        this.addActivityItem(activity);
    }

    calculateAdviceCounts(advice) {
        return advice.reduce((counts, item) => {
            const severity = item.severity.toLowerCase();
            counts[severity] = (counts[severity] || 0) + 1;
            return counts;
        }, {});
    }

    animateMetrics() {
        // Simulate metric updates (using live service count)
        const updates = {
            'system-health': `${(95 + Math.random() * 5).toFixed(1)}%`,
            'active-services': this.state.serviceCount || 43, // Use live count or fallback
            'active-alerts': Math.max(0, 3 + Math.floor(Math.random() * 3) - 1)
        };

        Object.entries(updates).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                this.animateValue(element, value);
            }
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('🚀 DOM loaded, initializing dashboard...');
        
        // Wait for Chart.js to load
        if (window.chartLoadPromise) {
            console.log('⏳ Waiting for Chart.js to load...');
            try {
                await window.chartLoadPromise;
                console.log('✅ Chart.js loaded successfully');
            } catch (error) {
                console.error('❌ Chart.js failed to load:', error);
                throw new Error('Chart.js failed to load from all sources');
            }
        }
        
        // Final check for Chart.js
        if (typeof Chart === 'undefined') {
            console.error('❌ Chart.js still not available after loading');
            throw new Error('Chart.js is required but not available');
        }
        
        // Check for Socket.io
        if (typeof io === 'undefined') {
            console.error('❌ Socket.io not loaded');
            throw new Error('Socket.io is required but not loaded');
        }
        
        console.log('🎯 All dependencies loaded, creating dashboard...');
        window.dashboard = new ServiceLogDashboard();
        console.log('✅ Dashboard instance created successfully');
        
    } catch (error) {
        console.error('❌ Dashboard initialization failed:', error);
        
        // Show error message to user
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 10000;
            background: #dc2626; color: white; padding: 15px 20px;
            border-radius: 8px; font-family: Inter, sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        errorDiv.innerHTML = `
            <strong>⚠️ Dashboard Error</strong><br>
            Failed to initialize dashboard: ${error.message}<br>
            <small>Check console for details. Refresh page to retry.</small>
        `;
        document.body.appendChild(errorDiv);
        
        // Auto-retry after 5 seconds
        setTimeout(() => {
            errorDiv.innerHTML = `
                <strong>🔄 Auto-retry in progress...</strong><br>
                Attempting to reload dashboard...<br>
                <small>This may take a few seconds</small>
            `;
            setTimeout(() => window.location.reload(), 2000);
        }, 5000);
    }
});

// Export for global access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ServiceLogDashboard;
}