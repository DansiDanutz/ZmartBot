// Zmarty Analytics & Tracking System
// Comprehensive event tracking for onboarding optimization

// Google Analytics Setup (gtag.js)
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-XXXXXXXXXX'); // Replace with your GA4 Measurement ID

// Analytics Configuration
const AnalyticsConfig = {
    enabled: true,
    debug: window.location.hostname === 'localhost',
    sendToGA: true,
    sendToMixpanel: false,
    sendToSegment: false,
    sendToAmplitude: false,
    batchSize: 10,
    flushInterval: 30000 // 30 seconds
};

// Main Analytics Class
class ZmartyAnalytics {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.userId = null;
        this.events = [];
        this.pageLoadTime = Date.now();
        this.interactionCount = 0;
        this.conversionFunnel = new ConversionFunnel();
        this.performanceMonitor = new PerformanceMonitor();
        
        this.initialize();
    }

    initialize() {
        // Get or create user ID
        this.userId = this.getUserId();
        
        // Start session tracking
        this.startSessionTracking();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Start performance monitoring
        this.performanceMonitor.start();
        
        // Setup batch processing
        this.setupBatchProcessing();
        
        // Track initial page view
        this.trackPageView();
    }

    generateSessionId() {
        return `zmarty_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getUserId() {
        let userId = localStorage.getItem('zmarty_user_id');
        if (!userId) {
            userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem('zmarty_user_id', userId);
        }
        return userId;
    }

    // Core tracking methods
    track(eventName, properties = {}) {
        const event = {
            event_name: eventName,
            user_id: this.userId,
            session_id: this.sessionId,
            timestamp: Date.now(),
            properties: {
                ...properties,
                ...this.getDefaultProperties()
            }
        };

        // Add to queue
        this.events.push(event);
        
        // Send immediately if critical event
        if (this.isCriticalEvent(eventName)) {
            this.sendEvent(event);
        }
        
        // Check if batch should be sent
        if (this.events.length >= AnalyticsConfig.batchSize) {
            this.flush();
        }

        // Debug logging
        if (AnalyticsConfig.debug) {
            console.log(`[Analytics] ${eventName}`, properties);
        }

        // Update interaction count
        this.interactionCount++;
    }

    trackPageView(page = window.location.pathname) {
        this.track('page_view', {
            page_path: page,
            page_title: document.title,
            page_referrer: document.referrer
        });
    }

    trackEngagement() {
        const engagementTime = Date.now() - this.pageLoadTime;
        const scrollDepth = this.calculateScrollDepth();
        
        this.track('user_engagement', {
            engagement_time_msec: engagementTime,
            scroll_depth_percent: scrollDepth,
            interaction_count: this.interactionCount
        });
    }

    trackConversion(step, value = null) {
        this.conversionFunnel.trackStep(step);
        
        this.track('conversion_step', {
            step_name: step,
            step_number: this.conversionFunnel.getStepNumber(step),
            value: value,
            funnel_id: 'onboarding'
        });

        // Send to GA4 as conversion event
        if (AnalyticsConfig.sendToGA && typeof gtag !== 'undefined') {
            gtag('event', 'conversion', {
                send_to: 'G-XXXXXXXXXX',
                value: value,
                currency: 'USD',
                conversion_step: step
            });
        }
    }

    trackError(errorType, errorMessage, errorStack = null) {
        this.track('error_occurred', {
            error_type: errorType,
            error_message: errorMessage,
            error_stack: errorStack,
            page_path: window.location.pathname,
            user_agent: navigator.userAgent
        });

        // Also send to error tracking service
        if (typeof Sentry !== 'undefined') {
            Sentry.captureMessage(errorMessage, errorType);
        }
    }

    // Helper methods
    getDefaultProperties() {
        return {
            // Page context
            page_url: window.location.href,
            page_path: window.location.pathname,
            page_search: window.location.search,
            page_title: document.title,
            
            // Device info
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            viewport_width: window.innerWidth,
            viewport_height: window.innerHeight,
            device_type: this.getDeviceType(),
            
            // Browser info
            browser_name: this.getBrowserName(),
            browser_version: this.getBrowserVersion(),
            platform: navigator.platform,
            language: navigator.language,
            
            // Time info
            timestamp_unix: Math.floor(Date.now() / 1000),
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            hour_of_day: new Date().getHours(),
            day_of_week: new Date().getDay(),
            
            // Session info
            time_on_site: Date.now() - this.pageLoadTime,
            interaction_count: this.interactionCount
        };
    }

    getDeviceType() {
        const ua = navigator.userAgent;
        if (/tablet/i.test(ua)) return 'tablet';
        if (/mobile/i.test(ua)) return 'mobile';
        return 'desktop';
    }

    getBrowserName() {
        const ua = navigator.userAgent;
        if (ua.indexOf('Chrome') > -1) return 'Chrome';
        if (ua.indexOf('Safari') > -1) return 'Safari';
        if (ua.indexOf('Firefox') > -1) return 'Firefox';
        if (ua.indexOf('Edge') > -1) return 'Edge';
        return 'Other';
    }

    getBrowserVersion() {
        const ua = navigator.userAgent;
        const match = ua.match(/(Chrome|Safari|Firefox|Edge)\/(\d+)/);
        return match ? match[2] : 'Unknown';
    }

    calculateScrollDepth() {
        const scrolled = window.pageYOffset || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        return Math.round((scrolled / height) * 100);
    }

    isCriticalEvent(eventName) {
        const criticalEvents = [
            'registration_completed',
            'email_verified',
            'tier_selected',
            'profile_completed',
            'error_occurred',
            'payment_initiated'
        ];
        return criticalEvents.includes(eventName);
    }

    // Event sending methods
    async sendEvent(event) {
        // Send to Google Analytics
        if (AnalyticsConfig.sendToGA && typeof gtag !== 'undefined') {
            gtag('event', event.event_name, event.properties);
        }

        // Send to Mixpanel
        if (AnalyticsConfig.sendToMixpanel && typeof mixpanel !== 'undefined') {
            mixpanel.track(event.event_name, event.properties);
        }

        // Send to backend
        try {
            await this.sendToBackend([event]);
        } catch (error) {
            console.error('Failed to send analytics event:', error);
        }
    }

    async sendToBackend(events) {
        if (!AnalyticsConfig.enabled) return;

        try {
            const response = await fetch('/api/analytics/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    events: events,
                    session_id: this.sessionId,
                    user_id: this.userId
                })
            });

            if (!response.ok) {
                throw new Error(`Analytics API error: ${response.status}`);
            }
        } catch (error) {
            // Store failed events for retry
            this.storeFailedEvents(events);
            throw error;
        }
    }

    storeFailedEvents(events) {
        const failedEvents = JSON.parse(localStorage.getItem('zmarty_failed_events') || '[]');
        failedEvents.push(...events);
        
        // Keep only last 100 failed events
        const trimmed = failedEvents.slice(-100);
        localStorage.setItem('zmarty_failed_events', JSON.stringify(trimmed));
    }

    async retryFailedEvents() {
        const failedEvents = JSON.parse(localStorage.getItem('zmarty_failed_events') || '[]');
        if (failedEvents.length === 0) return;

        try {
            await this.sendToBackend(failedEvents);
            localStorage.removeItem('zmarty_failed_events');
        } catch (error) {
            console.error('Failed to retry events:', error);
        }
    }

    // Batch processing
    setupBatchProcessing() {
        // Flush events periodically
        setInterval(() => {
            if (this.events.length > 0) {
                this.flush();
            }
        }, AnalyticsConfig.flushInterval);

        // Flush on page unload
        window.addEventListener('beforeunload', () => {
            this.flush();
        });

        // Flush on visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.flush();
            }
        });
    }

    async flush() {
        if (this.events.length === 0) return;

        const eventsToSend = [...this.events];
        this.events = [];

        try {
            await this.sendToBackend(eventsToSend);
        } catch (error) {
            // Re-add events to queue for retry
            this.events.unshift(...eventsToSend);
        }
    }

    // Session tracking
    startSessionTracking() {
        // Track session start
        this.track('session_start', {
            referrer: document.referrer,
            landing_page: window.location.pathname,
            utm_source: this.getUTMParameter('utm_source'),
            utm_medium: this.getUTMParameter('utm_medium'),
            utm_campaign: this.getUTMParameter('utm_campaign')
        });

        // Track session end
        window.addEventListener('beforeunload', () => {
            this.track('session_end', {
                session_duration: Date.now() - this.pageLoadTime,
                total_interactions: this.interactionCount
            });
        });

        // Track engagement every 30 seconds
        setInterval(() => {
            this.trackEngagement();
        }, 30000);
    }

    getUTMParameter(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param) || null;
    }

    // Event listeners
    setupEventListeners() {
        // Track clicks
        document.addEventListener('click', (e) => {
            const target = e.target.closest('a, button, [data-track]');
            if (target) {
                const trackData = target.dataset.track ? 
                    JSON.parse(target.dataset.track) : 
                    { element: target.tagName.toLowerCase() };
                
                this.track('element_clicked', {
                    ...trackData,
                    text: target.textContent?.trim().substring(0, 100),
                    href: target.href,
                    id: target.id,
                    class: target.className
                });
            }
        });

        // Track form submissions
        document.addEventListener('submit', (e) => {
            const form = e.target;
            this.track('form_submitted', {
                form_id: form.id,
                form_name: form.name,
                form_action: form.action
            });
        });

        // Track input changes
        let inputTimer;
        document.addEventListener('input', (e) => {
            clearTimeout(inputTimer);
            inputTimer = setTimeout(() => {
                this.track('input_changed', {
                    input_id: e.target.id,
                    input_name: e.target.name,
                    input_type: e.target.type
                });
            }, 1000);
        });

        // Track scroll depth
        let maxScrollDepth = 0;
        window.addEventListener('scroll', () => {
            const scrollDepth = this.calculateScrollDepth();
            if (scrollDepth > maxScrollDepth) {
                maxScrollDepth = scrollDepth;
                if (scrollDepth % 25 === 0) {
                    this.track('scroll_milestone', {
                        depth_percent: scrollDepth
                    });
                }
            }
        });
    }
}

// Conversion Funnel Tracking
class ConversionFunnel {
    constructor() {
        this.steps = [
            'landing_viewed',
            'registration_started',
            'registration_completed',
            'email_verified',
            'tier_selected',
            'profile_started',
            'profile_completed',
            'onboarding_complete'
        ];
        
        this.completedSteps = new Set();
        this.stepTimings = {};
    }

    trackStep(step) {
        if (!this.steps.includes(step)) {
            console.warn(`Unknown funnel step: ${step}`);
            return;
        }

        this.completedSteps.add(step);
        this.stepTimings[step] = Date.now();

        // Calculate conversion rate
        const stepIndex = this.steps.indexOf(step);
        if (stepIndex > 0) {
            const previousStep = this.steps[stepIndex - 1];
            if (this.stepTimings[previousStep]) {
                const duration = this.stepTimings[step] - this.stepTimings[previousStep];
                console.log(`Time from ${previousStep} to ${step}: ${duration}ms`);
            }
        }
    }

    getStepNumber(step) {
        return this.steps.indexOf(step) + 1;
    }

    getConversionRate() {
        return (this.completedSteps.size / this.steps.length) * 100;
    }

    getDropoffPoint() {
        for (let i = 0; i < this.steps.length; i++) {
            if (!this.completedSteps.has(this.steps[i])) {
                return this.steps[i];
            }
        }
        return null;
    }
}

// Performance Monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
    }

    start() {
        // Use Performance Observer API
        if ('PerformanceObserver' in window) {
            // Monitor long tasks
            try {
                const longTaskObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        window.zmartyAnalytics.track('long_task_detected', {
                            duration: entry.duration,
                            start_time: entry.startTime
                        });
                    }
                });
                longTaskObserver.observe({ entryTypes: ['longtask'] });
            } catch (e) {}

            // Monitor resource loading
            try {
                const resourceObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 1000) { // Resources taking > 1s
                            window.zmartyAnalytics.track('slow_resource', {
                                name: entry.name,
                                duration: entry.duration,
                                type: entry.initiatorType
                            });
                        }
                    }
                });
                resourceObserver.observe({ entryTypes: ['resource'] });
            } catch (e) {}
        }

        // Track page load metrics
        window.addEventListener('load', () => {
            setTimeout(() => {
                this.collectMetrics();
            }, 0);
        });
    }

    collectMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const paint = performance.getEntriesByType('paint');

        this.metrics = {
            // Navigation timing
            dns_lookup: navigation?.domainLookupEnd - navigation?.domainLookupStart,
            tcp_connect: navigation?.connectEnd - navigation?.connectStart,
            request_time: navigation?.responseStart - navigation?.requestStart,
            response_time: navigation?.responseEnd - navigation?.responseStart,
            dom_processing: navigation?.domComplete - navigation?.domInteractive,
            load_complete: navigation?.loadEventEnd - navigation?.fetchStart,

            // Paint timing
            first_paint: paint.find(p => p.name === 'first-paint')?.startTime,
            first_contentful_paint: paint.find(p => p.name === 'first-contentful-paint')?.startTime,

            // Memory usage (if available)
            memory_used: performance.memory?.usedJSHeapSize,
            memory_total: performance.memory?.totalJSHeapSize
        };

        // Send performance metrics
        window.zmartyAnalytics.track('performance_metrics', this.metrics);
    }
}

// Initialize analytics
window.zmartyAnalytics = new ZmartyAnalytics();

// Export for use in other scripts
window.trackEvent = (eventName, properties) => {
    window.zmartyAnalytics.track(eventName, properties);
};

window.trackError = (errorType, error) => {
    window.zmartyAnalytics.trackError(errorType, error.message, error.stack);
};

window.trackConversion = (step, value) => {
    window.zmartyAnalytics.trackConversion(step, value);
};