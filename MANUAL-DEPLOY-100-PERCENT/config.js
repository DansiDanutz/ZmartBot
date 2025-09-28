/**
 * ZmartyBrain Onboarding - Configuration File
 * Centralized configuration for all services and APIs
 */

const CONFIG = {
    // Environment
    ENV: window.location.hostname === 'localhost' ? 'development' : 'production',

    // Supabase Configuration
    SUPABASE: {
        URL: 'https://asjtxrmftmutcsnqgidy.supabase.co',
        ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.w_S6VaAqJ6xYv0LXBBb5gfOJbKXV3r9EfGwGGxGHOcE',
        REDIRECT_URL: window.location.origin + '/auth/callback'
    },

    // Stripe Payment Configuration
    STRIPE: {
        PUBLIC_KEY: window.location.hostname === 'localhost'
            ? 'pk_test_51NaQqkGO9mhkLxVZ5QhXxYZ1234567890' // Test key
            : 'pk_live_YOUR_PRODUCTION_KEY', // Production key
        PRICES: {
            PROFESSIONAL: {
                MONTHLY: 'price_professional_monthly',
                YEARLY: 'price_professional_yearly'
            },
            ENTERPRISE: {
                MONTHLY: 'price_enterprise_monthly',
                YEARLY: 'price_enterprise_yearly'
            }
        }
    },

    // Google Analytics
    ANALYTICS: {
        GA_ID: 'G-YOUR_MEASUREMENT_ID',
        ENABLED: window.location.hostname !== 'localhost'
    },

    // Backend API Configuration
    API: {
        BASE_URL: window.location.hostname === 'localhost'
            ? 'http://localhost:8000'
            : 'https://api.zmartybrain.com',
        ENDPOINTS: {
            AUTH: '/api/auth',
            USER: '/api/user',
            PROFILE: '/api/profile',
            SUBSCRIPTION: '/api/subscription',
            ONBOARDING: '/api/onboarding',
            TRADING: '/api/trading'
        },
        TIMEOUT: 30000, // 30 seconds
        RETRY_ATTEMPTS: 3
    },

    // Feature Flags
    FEATURES: {
        PAYMENT_ENABLED: true,
        GOOGLE_AUTH_ENABLED: true,
        FACEBOOK_AUTH_ENABLED: false,
        ANALYTICS_ENABLED: true,
        DEBUG_MODE: window.location.hostname === 'localhost',
        MOCK_PAYMENT: window.location.hostname === 'localhost'
    },

    // UI Configuration
    UI: {
        ANIMATION_DURATION: 300,
        TOAST_DURATION: 5000,
        SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
        AUTO_SAVE_INTERVAL: 60000, // 1 minute
        SWIPE_THRESHOLD: 50 // pixels
    },

    // Plans Configuration
    PLANS: {
        PROFESSIONAL: {
            NAME: 'Professional',
            PRICE_MONTHLY: 29,
            PRICE_YEARLY: 290,
            FEATURES: [
                'Advanced Trading Signals',
                'Real-time Market Analysis',
                'Portfolio Management',
                '24/7 Support',
                'Custom Alerts'
            ]
        },
        ENTERPRISE: {
            NAME: 'Enterprise',
            PRICE_MONTHLY: 99,
            PRICE_YEARLY: 990,
            FEATURES: [
                'Everything in Professional',
                'API Access',
                'White Label Options',
                'Dedicated Account Manager',
                'Custom Integrations',
                'Advanced Analytics'
            ]
        }
    },

    // Email Configuration
    EMAIL: {
        FROM: 'noreply@zmartybrain.com',
        SUPPORT: 'support@zmartybrain.com',
        TEMPLATES: {
            WELCOME: 'welcome',
            VERIFICATION: 'verification',
            PASSWORD_RESET: 'password-reset',
            SUBSCRIPTION: 'subscription'
        }
    },

    // Storage Keys
    STORAGE: {
        USER_SESSION: 'zmarty_session',
        ONBOARDING_STEP: 'onboarding_step',
        USER_PREFERENCES: 'user_preferences',
        DRAFT_PROFILE: 'draft_profile'
    },

    // Validation Rules
    VALIDATION: {
        PASSWORD_MIN_LENGTH: 8,
        PASSWORD_REGEX: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
        EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        PHONE_REGEX: /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/
    },

    // Error Messages
    ERRORS: {
        NETWORK: 'Network error. Please check your connection.',
        AUTH_FAILED: 'Authentication failed. Please try again.',
        PAYMENT_FAILED: 'Payment processing failed. Please try again.',
        VALIDATION_FAILED: 'Please check your input and try again.',
        SESSION_EXPIRED: 'Your session has expired. Please log in again.',
        RATE_LIMIT: 'Too many requests. Please wait a moment.'
    },

    // Success Messages
    SUCCESS: {
        ACCOUNT_CREATED: 'Account created successfully!',
        EMAIL_VERIFIED: 'Email verified successfully!',
        PASSWORD_RESET: 'Password reset successfully!',
        PROFILE_UPDATED: 'Profile updated successfully!',
        SUBSCRIPTION_ACTIVE: 'Subscription activated successfully!'
    }
};

// Helper Functions
const ConfigHelper = {
    /**
     * Get API endpoint URL
     */
    getApiUrl: function(endpoint) {
        return CONFIG.API.BASE_URL + CONFIG.API.ENDPOINTS[endpoint];
    },

    /**
     * Check if feature is enabled
     */
    isFeatureEnabled: function(feature) {
        return CONFIG.FEATURES[feature] === true;
    },

    /**
     * Get storage item with prefix
     */
    getStorageKey: function(key) {
        return CONFIG.STORAGE[key] || key;
    },

    /**
     * Validate email format
     */
    isValidEmail: function(email) {
        return CONFIG.VALIDATION.EMAIL_REGEX.test(email);
    },

    /**
     * Validate password strength
     */
    isValidPassword: function(password) {
        return password.length >= CONFIG.VALIDATION.PASSWORD_MIN_LENGTH &&
               CONFIG.VALIDATION.PASSWORD_REGEX.test(password);
    },

    /**
     * Get plan details
     */
    getPlanDetails: function(planType) {
        return CONFIG.PLANS[planType.toUpperCase()] || null;
    },

    /**
     * Initialize analytics
     */
    initAnalytics: function() {
        if (CONFIG.FEATURES.ANALYTICS_ENABLED && CONFIG.ANALYTICS.GA_ID) {
            // Initialize Google Analytics
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', CONFIG.ANALYTICS.GA_ID);
        }
    },

    /**
     * Log debug message
     */
    debug: function(...args) {
        if (CONFIG.FEATURES.DEBUG_MODE) {
            console.log('[ZmartyBrain Debug]', ...args);
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, ConfigHelper };
}