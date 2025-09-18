// Performance Optimization Module for ZmartyChat
// Handles lazy loading, code splitting, caching, and runtime optimizations

class PerformanceOptimizer {
    constructor() {
        this.metrics = {
            fcp: 0,  // First Contentful Paint
            lcp: 0,  // Largest Contentful Paint
            fid: 0,  // First Input Delay
            cls: 0,  // Cumulative Layout Shift
            ttfb: 0  // Time to First Byte
        };

        this.resourceHints = new Set();
        this.lazyComponents = new Map();
        this.imageObserver = null;
        this.intersectionObserver = null;
        this.performanceObserver = null;

        this.init();
    }

    init() {
        // Start monitoring performance
        this.initPerformanceObserver();

        // Set up lazy loading
        this.initLazyLoading();

        // Optimize images
        this.initImageOptimization();

        // Set up resource hints
        this.initResourceHints();

        // Enable service worker for caching
        this.initServiceWorker();

        // Optimize animations
        this.optimizeAnimations();

        // Monitor and report metrics
        this.reportMetrics();
    }

    // Performance monitoring
    initPerformanceObserver() {
        if ('PerformanceObserver' in window) {
            // Monitor Largest Contentful Paint
            try {
                const lcpObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    this.metrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
                });
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                console.log('LCP observer not supported');
            }

            // Monitor First Input Delay
            try {
                const fidObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach(entry => {
                        this.metrics.fid = entry.processingStart - entry.startTime;
                    });
                });
                fidObserver.observe({ entryTypes: ['first-input'] });
            } catch (e) {
                console.log('FID observer not supported');
            }

            // Monitor Cumulative Layout Shift
            try {
                let clsValue = 0;
                let clsEntries = [];

                const clsObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                            clsEntries.push(entry);
                        }
                    }
                    this.metrics.cls = clsValue;
                });
                clsObserver.observe({ entryTypes: ['layout-shift'] });
            } catch (e) {
                console.log('CLS observer not supported');
            }
        }

        // Monitor Time to First Byte
        if (window.performance && window.performance.timing) {
            const timing = window.performance.timing;
            this.metrics.ttfb = timing.responseStart - timing.navigationStart;
            this.metrics.fcp = timing.domContentLoadedEventStart - timing.navigationStart;
        }
    }

    // Lazy loading for components
    initLazyLoading() {
        this.intersectionObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadComponent(entry.target);
                    }
                });
            },
            { rootMargin: '50px' }
        );

        // Mark components for lazy loading
        document.querySelectorAll('[data-lazy]').forEach(element => {
            this.intersectionObserver.observe(element);
        });
    }

    async loadComponent(element) {
        const componentName = element.dataset.lazy;

        if (this.lazyComponents.has(componentName)) {
            const component = this.lazyComponents.get(componentName);
            element.innerHTML = component;
        } else {
            try {
                // Dynamic import
                const module = await this.dynamicImport(componentName);
                if (module && module.render) {
                    element.innerHTML = module.render();
                }
            } catch (error) {
                console.error(`Failed to load component ${componentName}:`, error);
            }
        }

        this.intersectionObserver.unobserve(element);
    }

    async dynamicImport(componentName) {
        // Map component names to their paths
        const componentMap = {
            'chart': '/src/components/chart.js',
            'table': '/src/components/table.js',
            'modal': '/src/components/modal.js',
            'trading-panel': '/src/components/trading-panel.js'
        };

        const path = componentMap[componentName];
        if (path) {
            return import(path);
        }
        return null;
    }

    // Image optimization
    initImageOptimization() {
        this.imageObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadImage(entry.target);
                    }
                });
            },
            { rootMargin: '50px' }
        );

        // Lazy load images
        document.querySelectorAll('img[data-src]').forEach(img => {
            this.imageObserver.observe(img);
        });

        // Progressive image loading
        this.enableProgressiveImages();
    }

    loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;

        if (src) {
            img.src = src;
        }
        if (srcset) {
            img.srcset = srcset;
        }

        img.classList.add('loaded');
        this.imageObserver.unobserve(img);

        // Preload next image in viewport
        const nextImg = img.nextElementSibling;
        if (nextImg && nextImg.dataset.src) {
            this.preloadImage(nextImg.dataset.src);
        }
    }

    enableProgressiveImages() {
        document.querySelectorAll('.progressive-image').forEach(container => {
            const small = container.querySelector('.img-small');
            const large = new Image();

            large.src = small.dataset.large;
            large.onload = () => {
                large.classList.add('loaded');
                container.appendChild(large);
                setTimeout(() => {
                    small.classList.add('hidden');
                }, 300);
            };
        });
    }

    preloadImage(src) {
        const img = new Image();
        img.src = src;
    }

    // Resource hints
    initResourceHints() {
        // Preconnect to API endpoints
        this.addResourceHint('preconnect', 'https://api.zmartychat.com');

        // Prefetch critical resources
        this.addResourceHint('prefetch', '/src/api-service.js');
        this.addResourceHint('prefetch', '/src/websocket-service.js');

        // DNS prefetch for external resources
        this.addResourceHint('dns-prefetch', 'https://fonts.googleapis.com');
        this.addResourceHint('dns-prefetch', 'https://cdn.jsdelivr.net');

        // Preload critical fonts
        this.addResourceHint('preload', '/fonts/Inter-Regular.woff2', 'font');
    }

    addResourceHint(rel, href, as = null) {
        const key = `${rel}-${href}`;
        if (this.resourceHints.has(key)) return;

        const link = document.createElement('link');
        link.rel = rel;
        link.href = href;

        if (as) {
            link.as = as;
            if (as === 'font') {
                link.type = 'font/woff2';
                link.crossOrigin = 'anonymous';
            }
        }

        document.head.appendChild(link);
        this.resourceHints.add(key);
    }

    // Service Worker for caching
    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered:', registration);
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    // Animation optimization
    optimizeAnimations() {
        // Reduce motion for users who prefer it
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

        if (prefersReducedMotion.matches) {
            document.documentElement.classList.add('reduced-motion');
        }

        // Use CSS containment for animated elements
        document.querySelectorAll('.animated').forEach(element => {
            element.style.contain = 'layout style paint';
        });

        // Throttle scroll animations
        let scrollTimeout;
        let isScrolling = false;

        window.addEventListener('scroll', () => {
            if (!isScrolling) {
                window.requestAnimationFrame(() => {
                    document.body.classList.add('is-scrolling');
                    isScrolling = false;
                });
                isScrolling = true;
            }

            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                document.body.classList.remove('is-scrolling');
            }, 100);
        }, { passive: true });

        // Use transform instead of position for animations
        this.optimizeCSS();
    }

    optimizeCSS() {
        // Convert position animations to transforms
        const style = document.createElement('style');
        style.textContent = `
            .is-scrolling * {
                pointer-events: none !important;
            }

            .reduced-motion * {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }

            .loaded {
                animation: fadeIn 0.3s ease-in;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            /* Use GPU acceleration for animations */
            .animated {
                will-change: transform;
                transform: translateZ(0);
            }
        `;
        document.head.appendChild(style);
    }

    // Code splitting utilities
    async loadModule(moduleName) {
        const modules = {
            'trading': () => import('./modules/trading.js'),
            'portfolio': () => import('./modules/portfolio.js'),
            'admin': () => import('./modules/admin.js'),
            'charts': () => import('./modules/charts.js')
        };

        if (modules[moduleName]) {
            return await modules[moduleName]();
        }

        throw new Error(`Module ${moduleName} not found`);
    }

    // Bundle optimization
    optimizeBundle() {
        // Tree shaking hints
        if (process.env.NODE_ENV === 'production') {
            // Remove development-only code
            this.removeDevCode();

            // Minify inline scripts
            this.minifyInlineScripts();

            // Compress assets
            this.compressAssets();
        }
    }

    removeDevCode() {
        // Remove console logs in production
        if (!window.__DEV__) {
            console.log = console.warn = console.error = () => {};
        }
    }

    minifyInlineScripts() {
        document.querySelectorAll('script:not([src])').forEach(script => {
            // Basic minification (in production, use proper minifier)
            script.textContent = script.textContent
                .replace(/\/\*[\s\S]*?\*\//g, '') // Remove comments
                .replace(/\n\s+/g, ' ') // Remove unnecessary whitespace
                .trim();
        });
    }

    compressAssets() {
        // Enable gzip/brotli compression hints
        const meta = document.createElement('meta');
        meta.httpEquiv = 'Accept-Encoding';
        meta.content = 'gzip, deflate, br';
        document.head.appendChild(meta);
    }

    // Memory management
    cleanupMemory() {
        // Clear unused caches
        if ('caches' in window) {
            caches.keys().then(names => {
                names.forEach(name => {
                    if (name.startsWith('old-cache-')) {
                        caches.delete(name);
                    }
                });
            });
        }

        // Remove detached DOM nodes
        this.cleanupDetachedNodes();

        // Clear old data from localStorage
        this.cleanupLocalStorage();
    }

    cleanupDetachedNodes() {
        // Find and remove event listeners from detached nodes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.removedNodes.forEach(node => {
                    if (node.nodeType === 1) {
                        // Clean up event listeners
                        node.removeEventListener('click', null);
                        node.removeEventListener('scroll', null);
                    }
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    cleanupLocalStorage() {
        const now = Date.now();
        const keys = Object.keys(localStorage);

        keys.forEach(key => {
            if (key.startsWith('cache-')) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    if (data.expiry && data.expiry < now) {
                        localStorage.removeItem(key);
                    }
                } catch {
                    localStorage.removeItem(key);
                }
            }
        });
    }

    // Performance reporting
    reportMetrics() {
        // Wait for page to be fully loaded
        window.addEventListener('load', () => {
            setTimeout(() => {
                this.sendMetrics();
            }, 2000);
        });
    }

    sendMetrics() {
        const metrics = {
            ...this.metrics,
            url: window.location.href,
            timestamp: Date.now(),
            userAgent: navigator.userAgent,
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            } : null
        };

        console.log('Performance Metrics:', metrics);

        // Send to analytics service
        if (window.gtag) {
            window.gtag('event', 'performance', {
                event_category: 'Web Vitals',
                event_label: 'FCP',
                value: Math.round(metrics.fcp)
            });
        }

        // Show performance badge in development
        if (window.__DEV__) {
            this.showPerformanceBadge(metrics);
        }
    }

    showPerformanceBadge(metrics) {
        const badge = document.createElement('div');
        badge.className = 'performance-badge';
        badge.innerHTML = `
            <div>FCP: ${Math.round(metrics.fcp)}ms</div>
            <div>LCP: ${Math.round(metrics.lcp)}ms</div>
            <div>FID: ${Math.round(metrics.fid)}ms</div>
            <div>CLS: ${metrics.cls.toFixed(3)}</div>
        `;

        badge.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            z-index: 10000;
        `;

        document.body.appendChild(badge);
    }

    // Prefetch next page resources
    prefetchNextPage(url) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    }

    // Virtual scrolling for large lists
    enableVirtualScrolling(container, items, itemHeight) {
        const visibleCount = Math.ceil(container.clientHeight / itemHeight);
        const totalHeight = items.length * itemHeight;

        const content = document.createElement('div');
        content.style.height = `${totalHeight}px`;
        content.style.position = 'relative';

        const renderItems = () => {
            const scrollTop = container.scrollTop;
            const startIndex = Math.floor(scrollTop / itemHeight);
            const endIndex = Math.min(startIndex + visibleCount + 1, items.length);

            // Clear previous items
            content.innerHTML = '';

            // Render visible items
            for (let i = startIndex; i < endIndex; i++) {
                const item = document.createElement('div');
                item.style.position = 'absolute';
                item.style.top = `${i * itemHeight}px`;
                item.style.height = `${itemHeight}px`;
                item.innerHTML = items[i];
                content.appendChild(item);
            }
        };

        container.appendChild(content);
        container.addEventListener('scroll', renderItems, { passive: true });
        renderItems();
    }
}

// Create and export singleton instance
const performanceOptimizer = new PerformanceOptimizer();

if (typeof window !== 'undefined') {
    window.performanceOptimizer = performanceOptimizer;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceOptimizer;
}

console.log('Performance Optimizer initialized');