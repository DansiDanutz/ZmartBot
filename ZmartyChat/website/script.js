// ZmartyChat Landing Website JavaScript

class ZmartyChatWebsite {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupIntersectionObserver();
        this.setupMobileMenu();
        this.setupScrollEffects();
        this.setupAnimations();
        this.initializeCounters();
    }

    setupEventListeners() {
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // CTA button interactions
        document.querySelectorAll('.cta-button, .btn-primary').forEach(button => {
            button.addEventListener('click', (e) => {
                this.handleCTAClick(e);
            });
        });

        // Header scroll effect
        window.addEventListener('scroll', () => {
            this.handleScroll();
        });

        // Resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');

                    // Trigger counter animation for stats
                    if (entry.target.classList.contains('stat')) {
                        this.animateCounter(entry.target);
                    }
                }
            });
        }, observerOptions);

        // Observe elements for fade-in animation
        document.querySelectorAll('.fade-in, .feature-card, .pricing-card, .provider-card').forEach(el => {
            el.classList.add('fade-in');
            this.observer.observe(el);
        });
    }

    setupMobileMenu() {
        const toggle = document.querySelector('.mobile-menu-toggle');
        const navLinks = document.querySelector('.nav-links');

        if (toggle && navLinks) {
            toggle.addEventListener('click', () => {
                navLinks.classList.toggle('active');
                this.updateMobileMenuIcon(toggle, navLinks.classList.contains('active'));
            });

            // Close mobile menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('nav')) {
                    navLinks.classList.remove('active');
                    this.updateMobileMenuIcon(toggle, false);
                }
            });
        }
    }

    updateMobileMenuIcon(toggle, isOpen) {
        toggle.innerHTML = isOpen ? '✕' : '☰';
    }

    setupScrollEffects() {
        // Parallax effect for hero background
        const hero = document.querySelector('.hero');
        if (hero) {
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                hero.style.transform = `translateY(${rate}px)`;
            });
        }
    }

    setupAnimations() {
        // Add stagger animation to feature cards
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
        });

        // Add floating animation to provider cards
        const providerCards = document.querySelectorAll('.provider-card');
        providerCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.2}s`;
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) scale(1.02)';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    initializeCounters() {
        this.counters = {
            users: { target: 10000, current: 0, element: null },
            trades: { target: 50000, current: 0, element: null },
            profit: { target: 25, current: 0, element: null, suffix: '%' }
        };

        // Find counter elements
        Object.keys(this.counters).forEach(key => {
            const element = document.querySelector(`[data-counter="${key}"]`);
            if (element) {
                this.counters[key].element = element;
            }
        });
    }

    animateCounter(statElement) {
        const counterElement = statElement.querySelector('[data-counter]');
        if (!counterElement) return;

        const counterId = counterElement.getAttribute('data-counter');
        const counter = this.counters[counterId];

        if (!counter || counter.animated) return;
        counter.animated = true;

        const duration = 2000; // 2 seconds
        const startTime = performance.now();
        const startValue = counter.current;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function (ease-out)
            const easedProgress = 1 - Math.pow(1 - progress, 3);

            counter.current = Math.floor(startValue + (counter.target - startValue) * easedProgress);

            const displayValue = counter.current.toLocaleString() + (counter.suffix || '');
            counterElement.textContent = displayValue;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    handleScroll() {
        const header = document.querySelector('header');
        if (header) {
            if (window.scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }

        // Update active navigation link
        this.updateActiveNavLink();
    }

    updateActiveNavLink() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');

        let currentSection = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            const sectionHeight = section.offsetHeight;

            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                currentSection = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSection}`) {
                link.classList.add('active');
            }
        });
    }

    handleResize() {
        // Close mobile menu on resize to desktop
        if (window.innerWidth > 768) {
            const navLinks = document.querySelector('.nav-links');
            const toggle = document.querySelector('.mobile-menu-toggle');
            if (navLinks && toggle) {
                navLinks.classList.remove('active');
                this.updateMobileMenuIcon(toggle, false);
            }
        }
    }

    handleCTAClick(e) {
        const button = e.currentTarget;
        const href = button.getAttribute('href');

        // Add click animation
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
        }, 150);

        // Handle different CTA actions
        if (href === '#download') {
            this.showDownloadModal();
        } else if (href === '#demo') {
            this.startDemo();
        } else if (href === '#pricing') {
            // Scroll to pricing with highlight effect
            const pricingSection = document.querySelector('#pricing');
            if (pricingSection) {
                pricingSection.scrollIntoView({ behavior: 'smooth' });
                // Highlight popular plan
                setTimeout(() => {
                    const popularCard = document.querySelector('.pricing-card.popular');
                    if (popularCard) {
                        popularCard.style.transform = 'scale(1.05)';
                        setTimeout(() => {
                            popularCard.style.transform = '';
                        }, 1000);
                    }
                }, 500);
            }
        }
    }

    showDownloadModal() {
        // Create and show download modal
        const modal = this.createModal({
            title: 'Download ZmartyChat',
            content: `
                <div class="download-options">
                    <div class="download-option">
                        <div class="platform-icon">📱</div>
                        <h4>Mobile App</h4>
                        <p>iOS & Android</p>
                        <button class="btn-primary" onclick="window.open('https://apps.apple.com/app/zmartychat', '_blank')">
                            Download for iOS
                        </button>
                        <button class="btn-secondary" onclick="window.open('https://play.google.com/store/apps/details?id=com.zmartychat', '_blank')">
                            Download for Android
                        </button>
                    </div>
                    <div class="download-option">
                        <div class="platform-icon">💻</div>
                        <h4>Web App</h4>
                        <p>Access from any browser</p>
                        <button class="btn-primary" onclick="window.open('/app', '_blank')">
                            Launch Web App
                        </button>
                    </div>
                </div>
            `,
            className: 'download-modal'
        });
    }

    startDemo() {
        // Create and show demo modal or redirect to demo
        const modal = this.createModal({
            title: 'Interactive Demo',
            content: `
                <div class="demo-content">
                    <p>Experience ZmartyChat's AI-powered trading insights with our interactive demo.</p>
                    <div class="demo-features">
                        <div class="demo-feature">
                            <div class="demo-icon">🤖</div>
                            <span>AI Analysis</span>
                        </div>
                        <div class="demo-feature">
                            <div class="demo-icon">📊</div>
                            <span>Real-time Charts</span>
                        </div>
                        <div class="demo-feature">
                            <div class="demo-icon">🐋</div>
                            <span>Whale Alerts</span>
                        </div>
                    </div>
                    <button class="btn-primary" onclick="window.open('/demo', '_blank')">
                        Start Demo
                    </button>
                </div>
            `,
            className: 'demo-modal'
        });
    }

    createModal({ title, content, className = '' }) {
        // Remove existing modal if any
        const existingModal = document.querySelector('.modal-overlay');
        if (existingModal) {
            existingModal.remove();
        }

        // Create modal HTML
        const modalHTML = `
            <div class="modal-overlay ${className}">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${title}</h3>
                        <button class="modal-close">&times;</button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        const modal = document.querySelector('.modal-overlay');

        // Add event listeners
        modal.querySelector('.modal-close').addEventListener('click', () => {
            this.closeModal(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
            }
        });

        // Animate in
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);

        return modal;
    }

    closeModal(modal) {
        modal.classList.remove('active');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }

    // Utility function to create loading state
    createLoader() {
        return `
            <div class="loader">
                <div class="loader-spinner"></div>
                <p>Loading...</p>
            </div>
        `;
    }

    // Analytics tracking
    trackEvent(eventName, properties = {}) {
        // Implement analytics tracking here
        console.log('Event tracked:', eventName, properties);

        // Example integration with analytics service
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, properties);
        }
    }
}

// Initialize website functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.zmartyChatWebsite = new ZmartyChatWebsite();
});

// Add modal styles dynamically
const modalStyles = `
<style>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(5px);
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}

.modal-overlay.active {
    opacity: 1;
    visibility: visible;
}

.modal-content {
    background: var(--gradient-dark);
    border-radius: 20px;
    border: 1px solid var(--border-color);
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    transform: scale(0.8) translateY(50px);
    transition: all 0.3s ease;
}

.modal-overlay.active .modal-content {
    transform: scale(1) translateY(0);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
    margin: 0;
    color: var(--text-light);
}

.modal-close {
    background: none;
    border: none;
    color: var(--text-gray);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.5rem;
    transition: color 0.3s ease;
}

.modal-close:hover {
    color: var(--text-light);
}

.modal-body {
    padding: 1.5rem;
}

.download-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.download-option {
    text-align: center;
    padding: 1rem;
    border: 1px solid var(--border-color);
    border-radius: 15px;
    background: var(--card-bg);
}

.platform-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.download-option h4 {
    margin: 0.5rem 0;
    color: var(--text-light);
}

.download-option p {
    color: var(--text-gray);
    margin-bottom: 1rem;
}

.download-option .btn-primary,
.download-option .btn-secondary {
    width: 100%;
    margin: 0.25rem 0;
}

.demo-content {
    text-align: center;
}

.demo-features {
    display: flex;
    justify-content: space-around;
    margin: 1.5rem 0;
}

.demo-feature {
    text-align: center;
}

.demo-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.loader {
    text-align: center;
    padding: 2rem;
}

.loader-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-color);
    border-top: 3px solid var(--primary-blue);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', modalStyles);