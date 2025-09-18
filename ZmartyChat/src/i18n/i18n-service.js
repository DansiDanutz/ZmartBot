// Internationalization (i18n) Service for ZmartyChat
// Supports multiple languages with dynamic loading and formatting

class I18nService {
    constructor() {
        this.currentLanguage = 'en';
        this.fallbackLanguage = 'en';
        this.translations = new Map();
        this.loadedLanguages = new Set();
        this.numberFormatters = new Map();
        this.dateFormatters = new Map();
        this.pluralRules = new Map();

        this.supportedLanguages = [
            { code: 'en', name: 'English', flag: '🇺🇸' },
            { code: 'es', name: 'Español', flag: '🇪🇸' },
            { code: 'fr', name: 'Français', flag: '🇫🇷' },
            { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
            { code: 'zh', name: '中文', flag: '🇨🇳' },
            { code: 'ja', name: '日本語', flag: '🇯🇵' },
            { code: 'ko', name: '한국어', flag: '🇰🇷' },
            { code: 'ru', name: 'Русский', flag: '🇷🇺' },
            { code: 'pt', name: 'Português', flag: '🇧🇷' },
            { code: 'ar', name: 'العربية', flag: '🇸🇦', rtl: true }
        ];

        this.init();
    }

    async init() {
        // Detect user's preferred language
        this.currentLanguage = this.detectLanguage();

        // Load the detected language
        await this.loadLanguage(this.currentLanguage);

        // Load fallback language if different
        if (this.currentLanguage !== this.fallbackLanguage) {
            await this.loadLanguage(this.fallbackLanguage);
        }

        // Apply language to document
        this.applyLanguage();

        // Set up language change listeners
        this.setupListeners();
    }

    detectLanguage() {
        // Check localStorage
        const stored = localStorage.getItem('language');
        if (stored && this.isSupported(stored)) {
            return stored;
        }

        // Check browser language
        const browserLang = navigator.language.split('-')[0];
        if (this.isSupported(browserLang)) {
            return browserLang;
        }

        // Default to English
        return 'en';
    }

    isSupported(langCode) {
        return this.supportedLanguages.some(lang => lang.code === langCode);
    }

    async loadLanguage(langCode) {
        if (this.loadedLanguages.has(langCode)) {
            return;
        }

        try {
            // In production, this would be an actual fetch request
            const translations = await this.fetchTranslations(langCode);
            this.translations.set(langCode, translations);
            this.loadedLanguages.add(langCode);

            // Initialize formatters for this language
            this.initializeFormatters(langCode);
        } catch (error) {
            console.error(`Failed to load language: ${langCode}`, error);
        }
    }

    async fetchTranslations(langCode) {
        // Simulated translation data - in production, fetch from server
        const translations = {
            en: {
                common: {
                    welcome: 'Welcome',
                    login: 'Login',
                    logout: 'Logout',
                    signup: 'Sign Up',
                    dashboard: 'Dashboard',
                    settings: 'Settings',
                    help: 'Help',
                    search: 'Search',
                    loading: 'Loading...',
                    save: 'Save',
                    cancel: 'Cancel',
                    delete: 'Delete',
                    edit: 'Edit',
                    close: 'Close',
                    confirm: 'Confirm',
                    yes: 'Yes',
                    no: 'No'
                },
                navigation: {
                    home: 'Home',
                    trading: 'Trading',
                    portfolio: 'Portfolio',
                    market: 'Market',
                    aiAnalysis: 'AI Analysis',
                    admin: 'Admin',
                    apiDocs: 'API Docs',
                    helpCenter: 'Help Center'
                },
                trading: {
                    buy: 'Buy',
                    sell: 'Sell',
                    orderBook: 'Order Book',
                    recentTrades: 'Recent Trades',
                    placeOrder: 'Place Order',
                    cancelOrder: 'Cancel Order',
                    orderType: 'Order Type',
                    limitOrder: 'Limit Order',
                    marketOrder: 'Market Order',
                    stopOrder: 'Stop Order',
                    price: 'Price',
                    amount: 'Amount',
                    total: 'Total',
                    balance: 'Balance',
                    available: 'Available'
                },
                portfolio: {
                    totalValue: 'Total Value',
                    dailyChange: 'Daily Change',
                    positions: 'Positions',
                    history: 'History',
                    deposits: 'Deposits',
                    withdrawals: 'Withdrawals',
                    profitLoss: 'Profit/Loss'
                },
                ai: {
                    signals: 'AI Signals',
                    sentiment: 'Sentiment Analysis',
                    prediction: 'Price Prediction',
                    recommendation: 'Recommendation',
                    confidence: 'Confidence',
                    provider: 'Provider',
                    bullish: 'Bullish',
                    bearish: 'Bearish',
                    neutral: 'Neutral'
                },
                messages: {
                    welcome: 'Welcome back, {name}!',
                    loginSuccess: 'Successfully logged in',
                    logoutSuccess: 'Successfully logged out',
                    orderPlaced: 'Order placed successfully',
                    orderCanceled: 'Order canceled',
                    errorGeneral: 'An error occurred',
                    errorNetwork: 'Network error',
                    errorAuth: 'Authentication required',
                    confirmDelete: 'Are you sure you want to delete {item}?',
                    saved: 'Changes saved',
                    copied: 'Copied to clipboard'
                },
                validation: {
                    required: 'This field is required',
                    email: 'Please enter a valid email',
                    minLength: 'Must be at least {min} characters',
                    maxLength: 'Must not exceed {max} characters',
                    pattern: 'Invalid format',
                    passwordMatch: 'Passwords do not match',
                    invalidAmount: 'Invalid amount',
                    insufficientBalance: 'Insufficient balance'
                },
                time: {
                    seconds: '{count, plural, =0 {0 seconds} =1 {1 second} other {# seconds}}',
                    minutes: '{count, plural, =0 {0 minutes} =1 {1 minute} other {# minutes}}',
                    hours: '{count, plural, =0 {0 hours} =1 {1 hour} other {# hours}}',
                    days: '{count, plural, =0 {0 days} =1 {1 day} other {# days}}',
                    ago: '{time} ago',
                    in: 'in {time}',
                    today: 'Today',
                    yesterday: 'Yesterday',
                    tomorrow: 'Tomorrow'
                }
            },
            es: {
                common: {
                    welcome: 'Bienvenido',
                    login: 'Iniciar sesión',
                    logout: 'Cerrar sesión',
                    signup: 'Registrarse',
                    dashboard: 'Panel',
                    settings: 'Configuración',
                    help: 'Ayuda',
                    search: 'Buscar',
                    loading: 'Cargando...',
                    save: 'Guardar',
                    cancel: 'Cancelar',
                    delete: 'Eliminar',
                    edit: 'Editar',
                    close: 'Cerrar',
                    confirm: 'Confirmar',
                    yes: 'Sí',
                    no: 'No'
                },
                trading: {
                    buy: 'Comprar',
                    sell: 'Vender',
                    orderBook: 'Libro de órdenes',
                    recentTrades: 'Operaciones recientes',
                    placeOrder: 'Colocar orden',
                    cancelOrder: 'Cancelar orden',
                    price: 'Precio',
                    amount: 'Cantidad',
                    total: 'Total',
                    balance: 'Saldo',
                    available: 'Disponible'
                }
                // ... more translations
            }
            // ... other languages
        };

        return translations[langCode] || translations.en;
    }

    initializeFormatters(langCode) {
        // Number formatter
        this.numberFormatters.set(langCode, new Intl.NumberFormat(langCode, {
            style: 'decimal',
            minimumFractionDigits: 2,
            maximumFractionDigits: 8
        }));

        // Currency formatter
        this.numberFormatters.set(`${langCode}-currency`, new Intl.NumberFormat(langCode, {
            style: 'currency',
            currency: 'USD'
        }));

        // Date formatter
        this.dateFormatters.set(langCode, new Intl.DateTimeFormat(langCode, {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }));

        // Time formatter
        this.dateFormatters.set(`${langCode}-time`, new Intl.DateTimeFormat(langCode, {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }));

        // Relative time formatter (if supported)
        if (typeof Intl.RelativeTimeFormat !== 'undefined') {
            this.dateFormatters.set(`${langCode}-relative`, new Intl.RelativeTimeFormat(langCode, {
                numeric: 'auto'
            }));
        }

        // Plural rules
        this.pluralRules.set(langCode, new Intl.PluralRules(langCode));
    }

    // Translation methods
    t(key, params = {}) {
        const translation = this.getTranslation(key);
        return this.interpolate(translation, params);
    }

    getTranslation(key) {
        const keys = key.split('.');
        let translation = this.translations.get(this.currentLanguage);

        for (const k of keys) {
            if (translation && typeof translation === 'object') {
                translation = translation[k];
            } else {
                break;
            }
        }

        // Fallback to default language
        if (!translation) {
            translation = this.getFallbackTranslation(key);
        }

        return translation || key;
    }

    getFallbackTranslation(key) {
        const keys = key.split('.');
        let translation = this.translations.get(this.fallbackLanguage);

        for (const k of keys) {
            if (translation && typeof translation === 'object') {
                translation = translation[k];
            } else {
                return null;
            }
        }

        return translation;
    }

    interpolate(text, params) {
        if (typeof text !== 'string') return text;

        // Simple interpolation: {variable}
        text = text.replace(/{(\w+)}/g, (match, key) => {
            return params.hasOwnProperty(key) ? params[key] : match;
        });

        // Plural interpolation: {count, plural, ...}
        text = text.replace(/{(\w+),\s*plural,\s*([^}]+)}/g, (match, variable, rules) => {
            const count = params[variable];
            if (count === undefined) return match;

            const pluralRule = this.pluralRules.get(this.currentLanguage).select(count);
            const ruleMap = this.parsePluralRules(rules);

            if (ruleMap[`=${count}`]) {
                return ruleMap[`=${count}`].replace('#', count);
            } else if (ruleMap[pluralRule]) {
                return ruleMap[pluralRule].replace('#', count);
            } else if (ruleMap.other) {
                return ruleMap.other.replace('#', count);
            }

            return match;
        });

        return text;
    }

    parsePluralRules(rules) {
        const ruleMap = {};
        const regex = /(\w+|=\d+)\s*{([^}]*)}/g;
        let match;

        while ((match = regex.exec(rules)) !== null) {
            ruleMap[match[1]] = match[2];
        }

        return ruleMap;
    }

    // Formatting methods
    formatNumber(number, options = {}) {
        const formatter = this.numberFormatters.get(this.currentLanguage);
        return formatter.format(number);
    }

    formatCurrency(amount, currency = 'USD') {
        const formatter = this.numberFormatters.get(`${this.currentLanguage}-currency`);
        return formatter.format(amount);
    }

    formatDate(date, options = {}) {
        const formatter = this.dateFormatters.get(this.currentLanguage);
        return formatter.format(new Date(date));
    }

    formatTime(date) {
        const formatter = this.dateFormatters.get(`${this.currentLanguage}-time`);
        return formatter.format(new Date(date));
    }

    formatRelativeTime(date) {
        const formatter = this.dateFormatters.get(`${this.currentLanguage}-relative`);
        if (!formatter) {
            return this.formatDate(date);
        }

        const now = new Date();
        const then = new Date(date);
        const diff = (then - now) / 1000; // in seconds

        const units = [
            { unit: 'year', seconds: 31536000 },
            { unit: 'month', seconds: 2592000 },
            { unit: 'week', seconds: 604800 },
            { unit: 'day', seconds: 86400 },
            { unit: 'hour', seconds: 3600 },
            { unit: 'minute', seconds: 60 },
            { unit: 'second', seconds: 1 }
        ];

        for (const { unit, seconds } of units) {
            const interval = Math.floor(Math.abs(diff) / seconds);
            if (interval >= 1) {
                return formatter.format(diff < 0 ? -interval : interval, unit);
            }
        }

        return formatter.format(0, 'second');
    }

    // Language management
    async changeLanguage(langCode) {
        if (!this.isSupported(langCode)) {
            console.error(`Language not supported: ${langCode}`);
            return;
        }

        await this.loadLanguage(langCode);
        this.currentLanguage = langCode;
        localStorage.setItem('language', langCode);

        this.applyLanguage();
        this.translatePage();

        // Emit language change event
        window.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language: langCode }
        }));
    }

    applyLanguage() {
        const langConfig = this.supportedLanguages.find(l => l.code === this.currentLanguage);

        // Set document language
        document.documentElement.lang = this.currentLanguage;

        // Set text direction
        document.documentElement.dir = langConfig?.rtl ? 'rtl' : 'ltr';

        // Update language selector if exists
        const selector = document.getElementById('language-selector');
        if (selector) {
            selector.value = this.currentLanguage;
        }
    }

    translatePage() {
        // Translate all elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const params = element.getAttribute('data-i18n-params');

            const translation = this.t(key, params ? JSON.parse(params) : {});

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });

        // Translate all elements with data-i18n-title attribute
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });
    }

    setupListeners() {
        // Listen for language selector changes
        const selector = document.getElementById('language-selector');
        if (selector) {
            selector.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }

        // Observe DOM changes and translate new elements
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // Element node
                        this.translateElement(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    translateElement(element) {
        if (element.hasAttribute('data-i18n')) {
            const key = element.getAttribute('data-i18n');
            const params = element.getAttribute('data-i18n-params');
            const translation = this.t(key, params ? JSON.parse(params) : {});

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        }

        // Translate children
        element.querySelectorAll('[data-i18n]').forEach(child => {
            this.translateElement(child);
        });
    }

    // Utility methods
    getLanguages() {
        return this.supportedLanguages;
    }

    getCurrentLanguage() {
        return this.currentLanguage;
    }

    addTranslations(langCode, namespace, translations) {
        const current = this.translations.get(langCode) || {};
        current[namespace] = { ...current[namespace], ...translations };
        this.translations.set(langCode, current);
    }

    // Create language selector component
    createLanguageSelector() {
        const selector = document.createElement('select');
        selector.id = 'language-selector';
        selector.className = 'language-selector';

        this.supportedLanguages.forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            option.textContent = `${lang.flag} ${lang.name}`;
            if (lang.code === this.currentLanguage) {
                option.selected = true;
            }
            selector.appendChild(option);
        });

        selector.addEventListener('change', (e) => {
            this.changeLanguage(e.target.value);
        });

        return selector;
    }
}

// Create singleton instance
const i18n = new I18nService();

// Export for global access
if (typeof window !== 'undefined') {
    window.i18n = i18n;
    window.t = (key, params) => i18n.t(key, params);
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = I18nService;
}

console.log('i18n Service initialized');