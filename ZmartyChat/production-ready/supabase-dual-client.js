// ===================================
// DUAL SUPABASE CLIENT ARCHITECTURE
// ===================================
// ZmartyBrain: User Authentication & Management
// ZmartBot: Crypto Trading & Market Data

// PROJECT 1: ZmartyBrain - User Management
const ZMARTYBRAIN_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const ZMARTYBRAIN_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

// PROJECT 2: ZmartBot - Crypto Trading Platform
const ZMARTBOT_URL = 'https://asjtxrmftmutcsnqgidy.supabase.co';
const ZMARTBOT_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM';

// Initialize both Supabase clients
const brainClient = window.supabase.createClient(ZMARTYBRAIN_URL, ZMARTYBRAIN_ANON_KEY);
const botClient = window.supabase.createClient(ZMARTBOT_URL, ZMARTBOT_ANON_KEY);

// ===================================
// UNIFIED SERVICE LAYER
// ===================================

const ZmartyService = {
    // ----------------
    // USER MANAGEMENT (ZmartyBrain)
    // ----------------
    auth: {
        // Register new user
        async register(email, password, tier = 'free') {
            try {
                
                const { data: signUpData, error: signUpError } = await brainClient.auth.signUp({
                    email: email,
                    password: password,
                    options: {
                        emailRedirectTo: window.location.origin + '/ZmartyUserApp/index.html#verified',
                        data: {
                            tier: tier,
                            name: '',
                            country: '',
                            profile_completed: false
                        }
                    }
                });

                if (signUpError) throw signUpError;

                // After successful registration, create profile in ZmartBot
                if (signUpData.user) {
                    await this.createTradingProfile(signUpData.user.id, email, tier);
                }

                return {
                    success: true,
                    message: `✅ Account created! Check ${email} for verification code.`,
                    needsVerification: true,
                    userId: signUpData.user?.id,
                    userEmail: signUpData.user?.email
                };
            } catch (error) {
                console.error('Registration error:', error);
                return {
                    success: false,
                    error: error.message || 'Registration failed'
                };
            }
        },

        // Verify email with OTP
        async verifyEmail(email, code) {
            try {
                
                const { data, error } = await brainClient.auth.verifyOtp({
                    email: email,
                    token: code,
                    type: 'signup'
                });

                if (!error && data.session) {
                    return {
                        success: true,
                        message: 'Email verified successfully',
                        session: data.session,
                        user: data.user,
                        userId: data.user?.id
                    };
                }

                return {
                    success: false,
                    error: error?.message || 'Invalid verification code'
                };
            } catch (error) {
                return {
                    success: false,
                    error: 'Verification failed'
                };
            }
        },

        // Login user
        async login(email, password) {
            try {
                const { data, error } = await brainClient.auth.signInWithPassword({
                    email: email,
                    password: password
                });

                if (error) throw error;

                // Load trading data after login
                if (data.user) {
                    await this.loadUserTradingData(data.user.id);
                }

                return {
                    success: true,
                    message: 'Logged in successfully',
                    session: data.session,
                    user: data.user
                };
            } catch (error) {
                return {
                    success: false,
                    error: 'Invalid credentials'
                };
            }
        },

        // Get current user
        async getCurrentUser() {
            const { data: { user }, error } = await brainClient.auth.getUser();

            if (error || !user) {
                return { success: false, error: 'Not authenticated' };
            }

            return { success: true, user };
        },

        // Update profile
        async updateProfile(name, country) {
            try {
                const { data, error } = await brainClient.auth.updateUser({
                    data: {
                        name: name,
                        country: country,
                        profile_completed: true
                    }
                });

                if (error) throw error;

                return {
                    success: true,
                    message: 'Profile updated',
                    user: data.user
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        },

        // Logout
        async logout() {
            try {
                await brainClient.auth.signOut();
                return { success: true, message: 'Logged out' };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Create trading profile in ZmartBot
        async createTradingProfile(userId, email, tier) {
            try {
                
                const { data, error } = await botClient
                    .from('user_profiles')
                    .upsert({
                        user_id: userId,
                        email: email,
                        tier: tier,
                        created_at: new Date().toISOString(),
                        trading_enabled: tier !== 'free',
                        api_access: tier === 'enterprise'
                    });

                if (error) {
                    console.error('Trading profile creation failed:', error);
                }

                return data;
            } catch (error) {
                console.error('Trading profile error:', error);
            }
        },

        // Load user's trading data
        async loadUserTradingData(userId) {
            try {
                const { data: profile } = await botClient
                    .from('user_profiles')
                    .select('*')
                    .eq('user_id', userId)
                    .single();

                return profile;
            } catch (error) {
                console.error('Failed to load trading data:', error);
                return null;
            }
        }
    },

    // ----------------
    // CRYPTO & TRADING (ZmartBot)
    // ----------------
    trading: {
        // Get market data
        async getMarketData() {
            try {
                const { data, error } = await botClient
                    .from('market_data')
                    .select('*')
                    .order('timestamp', { ascending: false })
                    .limit(100);

                if (error) throw error;
                return { success: true, data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Get trading strategies
        async getStrategies(userId) {
            try {
                const { data, error } = await botClient
                    .from('trading_strategies')
                    .select('*')
                    .eq('user_id', userId);

                if (error) throw error;
                return { success: true, strategies: data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Get portfolio
        async getPortfolio(userId) {
            try {
                const { data, error } = await botClient
                    .from('portfolios')
                    .select('*')
                    .eq('user_id', userId);

                if (error) throw error;
                return { success: true, portfolio: data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Execute trade
        async executeTrade(userId, tradeData) {
            try {
                // Check user tier from brain
                const { data: { user } } = await brainClient.auth.getUser();

                if (!user || user.user_metadata.tier === 'free') {
                    return {
                        success: false,
                        error: 'Trading requires Pro or Enterprise tier'
                    };
                }

                // Execute trade in bot
                const { data, error } = await botClient
                    .from('trades')
                    .insert({
                        user_id: userId,
                        ...tradeData,
                        timestamp: new Date().toISOString()
                    });

                if (error) throw error;
                return { success: true, trade: data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }
    },

    // ----------------
    // DASHBOARD DATA (Combined)
    // ----------------
    dashboard: {
        // Load complete dashboard data
        async loadDashboardData() {
            try {
                // Get user from Brain
                const { data: { user } } = await brainClient.auth.getUser();

                if (!user) {
                    return { success: false, error: 'Not authenticated' };
                }

                // Get trading data from Bot
                const [portfolio, strategies, marketData] = await Promise.all([
                    ZmartyService.trading.getPortfolio(user.id),
                    ZmartyService.trading.getStrategies(user.id),
                    ZmartyService.trading.getMarketData()
                ]);

                return {
                    success: true,
                    data: {
                        user: {
                            email: user.email,
                            tier: user.user_metadata.tier,
                            name: user.user_metadata.name,
                            country: user.user_metadata.country
                        },
                        portfolio: portfolio.portfolio || [],
                        strategies: strategies.strategies || [],
                        marketData: marketData.data || []
                    }
                };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }
    }
};

// ===================================
// BACKWARDS COMPATIBILITY
// ===================================
// Keep old UserService working with new architecture
const UserService = {
    register: (email, password, tier) => ZmartyService.auth.register(email, password, tier),
    verifyEmail: (email, code) => ZmartyService.auth.verifyEmail(email, code),
    login: (email, password) => ZmartyService.auth.login(email, password),
    getCurrentUser: () => ZmartyService.auth.getCurrentUser(),
    updateProfile: (name, country) => ZmartyService.auth.updateProfile(name, country),
    logout: () => ZmartyService.auth.logout(),
    updateTier: async (tier) => {
        try {
            const { data, error } = await brainClient.auth.updateUser({
                data: { tier: tier }
            });
            if (error) throw error;
            return { success: true, message: 'Tier updated', tier };
        } catch (error) {
            return { success: false, error: error.message };
        }
    },
    resendCode: async (email) => {
        try {
            const { data, error } = await brainClient.auth.resend({
                type: 'signup',
                email: email
            });
            if (error) throw error;
            return { success: true, message: `Code sent to ${email}` };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
};

// ===================================
// AUTH STATE MANAGEMENT
// ===================================

// Listen for auth state changes
brainClient.auth.onAuthStateChange((event, session) => {
    
    if (event === 'SIGNED_IN' && session) {
        
        // Load trading data when user signs in
        ZmartyService.trading.getPortfolio(session.user.id);

        // Redirect to dashboard if profile is complete
        if (session.user.user_metadata.profile_completed) {
            if (window.location.pathname.includes('index.html')) {
                window.location.href = 'dashboard.html';
            }
        }
    } else if (event === 'SIGNED_OUT') {
        
        // Clear any cached data
        sessionStorage.clear();
        localStorage.removeItem('zmarty_email_verified');

        // Redirect to login
        if (!window.location.pathname.includes('index.html')) {
            window.location.href = 'index.html';
        }
    }
});

// Check initial auth state
window.addEventListener('load', async () => {
    const { data: { session } } = await brainClient.auth.getSession();

    if (session) {
                
        // Load trading data
        const tradingProfile = await ZmartyService.auth.loadUserTradingData(session.user.id);
        if (tradingProfile) {
                    }
    } else {
            }
});

// Export for use in other scripts
window.ZmartyService = ZmartyService;
window.brainClient = brainClient;
window.botClient = botClient;

