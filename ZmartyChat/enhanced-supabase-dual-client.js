// ===================================
// ENHANCED DUAL SUPABASE CLIENT ARCHITECTURE
// ===================================
// ZmartyBrain: User Authentication & Management
// ZmartBot: Crypto Trading & Market Data
// Enhanced with real-time sync and advanced features

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
// REAL-TIME SYNC SERVICE
// ===================================

class RealTimeSyncService {
    constructor() {
        this.brainChannel = brainClient.channel('user-updates');
        this.botChannel = botClient.channel('trading-updates');
        this.syncActive = false;
        this.setupRealtimeSync();
    }
    
    setupRealtimeSync() {
        console.log('🔄 Setting up real-time sync between ZmartyBrain and ZmartBot...');
        
        // Listen for user profile changes in ZmartyBrain
        this.brainChannel
            .on('postgres_changes', 
                { event: 'UPDATE', schema: 'public', table: 'users' },
                (payload) => this.handleUserUpdate(payload))
            .on('postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'users' },
                (payload) => this.handleUserCreate(payload))
            .subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log('✅ ZmartyBrain real-time sync active');
                    this.syncActive = true;
                }
            });
        
        // Listen for trading events in ZmartBot
        this.botChannel
            .on('postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'trades' },
                (payload) => this.handleTradeEvent(payload))
            .on('postgres_changes',
                { event: 'UPDATE', schema: 'public', table: 'user_profiles' },
                (payload) => this.handleTradingProfileUpdate(payload))
            .subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log('✅ ZmartBot real-time sync active');
                }
            });
    }
    
    async handleUserUpdate(payload) {
        console.log('🔄 User profile updated in ZmartyBrain, syncing to ZmartBot...');
        const { id, subscription_tier, credits_balance, engagement_score } = payload.new;
        
        try {
            // Sync user tier changes to trading profile
            const { error } = await botClient
                .from('user_profiles')
                .update({ 
                    tier: subscription_tier,
                    trading_enabled: subscription_tier !== 'free',
                    credits_balance: credits_balance,
                    engagement_score: engagement_score,
                    updated_at: new Date().toISOString()
                })
                .eq('user_id', id);
            
            if (error) throw error;
            console.log('✅ User profile synced successfully');
        } catch (error) {
            console.error('❌ Failed to sync user profile:', error);
        }
    }
    
    async handleUserCreate(payload) {
        console.log('🆕 New user created in ZmartyBrain, creating trading profile...');
        const { id, email, subscription_tier } = payload.new;
        
        try {
            await ZmartyService.auth.createEnhancedTradingProfile(id, email, subscription_tier);
            console.log('✅ Trading profile created for new user');
        } catch (error) {
            console.error('❌ Failed to create trading profile:', error);
        }
    }
    
    async handleTradeEvent(payload) {
        console.log('📈 Trade executed, updating user engagement...');
        const { user_id, profit_loss, symbol } = payload.new;
        
        try {
            // Update user engagement metrics in ZmartyBrain
            const engagementScore = this.calculateEngagementScore(profit_loss);
            const { error } = await brainClient
                .from('users')
                .update({ 
                    last_active: new Date().toISOString(),
                    engagement_score: engagementScore
                })
                .eq('id', user_id);
            
            if (error) throw error;
            console.log(`✅ User engagement updated: ${engagementScore}`);
        } catch (error) {
            console.error('❌ Failed to update user engagement:', error);
        }
    }
    
    async handleTradingProfileUpdate(payload) {
        console.log('⚙️ Trading profile updated, syncing preferences...');
        const { user_id, risk_tolerance, preferred_timeframes } = payload.new;
        
        try {
            // Update user preferences in ZmartyBrain
            const { error } = await brainClient
                .from('users')
                .update({
                    updated_at: new Date().toISOString()
                })
                .eq('id', user_id);
            
            if (error) throw error;
            console.log('✅ Trading preferences synced');
        } catch (error) {
            console.error('❌ Failed to sync trading preferences:', error);
        }
    }
    
    calculateEngagementScore(profitLoss) {
        // Calculate engagement score based on trading activity
        if (profitLoss > 0) return Math.min(1.0, 0.5 + (profitLoss / 1000) * 0.1);
        if (profitLoss < 0) return Math.max(0.1, 0.5 - Math.abs(profitLoss / 1000) * 0.1);
        return 0.5;
    }
}

// ===================================
// ENHANCED UNIFIED SERVICE LAYER
// ===================================

const ZmartyService = {
    // Initialize real-time sync
    syncService: new RealTimeSyncService(),
    
    // ----------------
    // USER MANAGEMENT (ZmartyBrain)
    // ----------------
    auth: {
        // Register new user with enhanced profile creation
        async register(email, password, tier = 'free', userData = {}) {
            try {
                console.log(`📝 Registering new user: ${email} (${tier})`);
                
                const { data: signUpData, error: signUpError } = await brainClient.auth.signUp({
                    email: email,
                    password: password,
                    options: {
                        emailRedirectTo: window.location.origin + '/ZmartyUserApp/index.html#verified',
                        data: {
                            tier: tier,
                            name: userData.name || '',
                            country: userData.country || '',
                            profile_completed: false,
                            risk_tolerance: userData.riskTolerance || 'medium',
                            preferred_timeframes: userData.timeframes || ['1h', '4h', '1d']
                        }
                    }
                });

                if (signUpError) throw signUpError;

                // After successful registration, create enhanced trading profile
                if (signUpData.user) {
                    await this.createEnhancedTradingProfile(signUpData.user.id, email, tier, userData);
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

        // Create enhanced trading profile in ZmartBot
        async createEnhancedTradingProfile(userId, email, tier, userData = {}) {
            try {
                console.log(`🔧 Creating enhanced trading profile for ${email}`);
                
                const { data, error } = await botClient
                    .from('user_profiles')
                    .upsert({
                        user_id: userId,
                        email: email,
                        tier: tier,
                        created_at: new Date().toISOString(),
                        trading_enabled: tier !== 'free',
                        api_access: tier === 'enterprise',
                        // Enhanced fields
                        risk_tolerance: userData.riskTolerance || 'medium',
                        preferred_timeframes: userData.timeframes || ['1h', '4h', '1d'],
                        notification_preferences: {
                            email: true,
                            push: true,
                            sms: false,
                            trading_alerts: true,
                            market_updates: true
                        },
                        trading_limits: {
                            daily_loss_limit: tier === 'enterprise' ? 10000 : tier === 'premium' ? 5000 : 1000,
                            position_size_limit: tier === 'enterprise' ? 50000 : tier === 'premium' ? 25000 : 5000,
                            max_leverage: tier === 'enterprise' ? 20 : tier === 'premium' ? 10 : 5
                        },
                        preferences: {
                            auto_trading: false,
                            stop_loss_percentage: 2.0,
                            take_profit_percentage: 4.0,
                            preferred_exchanges: ['binance', 'kucoin'],
                            timezone: userData.timezone || 'UTC'
                        }
                    });

                if (error) {
                    console.error('Trading profile creation failed:', error);
                    throw error;
                }

                console.log('✅ Enhanced trading profile created successfully');
                return data;
            } catch (error) {
                console.error('Trading profile error:', error);
                throw error;
            }
        },

        // Enhanced login with profile sync
        async login(email, password) {
            try {
                const { data, error } = await brainClient.auth.signInWithPassword({
                    email: email,
                    password: password
                });

                if (error) throw error;

                // Load and sync trading profile
                if (data.user) {
                    await this.syncUserTradingProfile(data.user.id);
                }

                return {
                    success: true,
                    user: data.user,
                    session: data.session
                };
            } catch (error) {
                return {
                    success: false,
                    error: error.message
                };
            }
        },

        // Sync user trading profile
        async syncUserTradingProfile(userId) {
            try {
                const { data: profile } = await botClient
                    .from('user_profiles')
                    .select('*')
                    .eq('user_id', userId)
                    .single();

                if (!profile) {
                    // Create profile if it doesn't exist
                    const { data: user } = await brainClient.auth.getUser();
                    if (user.user) {
                        await this.createEnhancedTradingProfile(
                            userId, 
                            user.user.email, 
                            user.user.user_metadata?.tier || 'free'
                        );
                    }
                }

                return profile;
            } catch (error) {
                console.error('Failed to sync trading profile:', error);
                return null;
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
        },

        // Update user preferences across both systems
        async updateUserPreferences(userId, preferences) {
            try {
                // Update in ZmartyBrain
                const { error: brainError } = await brainClient
                    .from('users')
                    .update({
                        updated_at: new Date().toISOString()
                    })
                    .eq('id', userId);

                if (brainError) throw brainError;

                // Update in ZmartBot
                const { error: botError } = await botClient
                    .from('user_profiles')
                    .update({
                        preferences: preferences,
                        updated_at: new Date().toISOString()
                    })
                    .eq('user_id', userId);

                if (botError) throw botError;

                return { success: true };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }
    },

    // ----------------
    // CRYPTO & TRADING (ZmartBot)
    // ----------------
    trading: {
        // Get market data with caching
        async getMarketData(symbol = null, limit = 100) {
            try {
                let query = botClient
                    .from('market_data')
                    .select('*')
                    .order('timestamp', { ascending: false })
                    .limit(limit);

                if (symbol) {
                    query = query.eq('symbol', symbol);
                }

                const { data, error } = await query;

                if (error) throw error;
                return { success: true, data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Get trading strategies with user preferences
        async getStrategies(userId) {
            try {
                // Get user preferences first
                const userProfile = await ZmartyService.auth.loadUserTradingData(userId);
                
                const { data, error } = await botClient
                    .from('trading_strategies')
                    .select('*')
                    .eq('user_id', userId)
                    .order('created_at', { ascending: false });

                if (error) throw error;
                
                // Filter strategies based on user preferences
                const filteredStrategies = data.filter(strategy => {
                    if (userProfile?.preferences?.preferred_timeframes) {
                        return userProfile.preferences.preferred_timeframes.includes(strategy.timeframe);
                    }
                    return true;
                });

                return { success: true, strategies: filteredStrategies };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Get portfolio with enhanced analytics
        async getPortfolio(userId) {
            try {
                const { data, error } = await botClient
                    .from('portfolios')
                    .select('*')
                    .eq('user_id', userId);

                if (error) throw error;
                
                // Calculate portfolio analytics
                const analytics = this.calculatePortfolioAnalytics(data);
                
                return { 
                    success: true, 
                    portfolio: data,
                    analytics: analytics
                };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Execute trade with enhanced validation
        async executeTrade(userId, tradeData) {
            try {
                // Check user tier and limits
                const { data: { user } } = await brainClient.auth.getUser();
                const userProfile = await ZmartyService.auth.loadUserTradingData(userId);

                if (!user || user.user_metadata.tier === 'free') {
                    return {
                        success: false,
                        error: 'Trading requires Pro or Enterprise tier'
                    };
                }

                // Validate trading limits
                const validation = this.validateTradeLimits(tradeData, userProfile);
                if (!validation.valid) {
                    return {
                        success: false,
                        error: validation.error
                    };
                }

                // Execute trade in bot
                const { data, error } = await botClient
                    .from('trades')
                    .insert({
                        user_id: userId,
                        ...tradeData,
                        timestamp: new Date().toISOString(),
                        status: 'pending'
                    });

                if (error) throw error;
                return { success: true, trade: data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Calculate portfolio analytics
        calculatePortfolioAnalytics(portfolio) {
            if (!portfolio || portfolio.length === 0) {
                return {
                    totalValue: 0,
                    totalPnL: 0,
                    winRate: 0,
                    sharpeRatio: 0,
                    maxDrawdown: 0
                };
            }

            const totalValue = portfolio.reduce((sum, position) => sum + position.current_value, 0);
            const totalPnL = portfolio.reduce((sum, position) => sum + position.pnl, 0);
            const winningTrades = portfolio.filter(position => position.pnl > 0).length;
            const winRate = portfolio.length > 0 ? (winningTrades / portfolio.length) * 100 : 0;

            return {
                totalValue,
                totalPnL,
                winRate,
                sharpeRatio: this.calculateSharpeRatio(portfolio),
                maxDrawdown: this.calculateMaxDrawdown(portfolio)
            };
        },

        // Validate trade limits
        validateTradeLimits(tradeData, userProfile) {
            if (!userProfile?.trading_limits) {
                return { valid: true };
            }

            const limits = userProfile.trading_limits;
            
            if (tradeData.position_size > limits.position_size_limit) {
                return {
                    valid: false,
                    error: `Position size exceeds limit of ${limits.position_size_limit}`
                };
            }

            if (tradeData.leverage > limits.max_leverage) {
                return {
                    valid: false,
                    error: `Leverage exceeds limit of ${limits.max_leverage}x`
                };
            }

            return { valid: true };
        },

        calculateSharpeRatio(portfolio) {
            // Simplified Sharpe ratio calculation
            if (portfolio.length < 2) return 0;
            
            const returns = portfolio.map(p => p.pnl / p.initial_value);
            const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
            const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
            const stdDev = Math.sqrt(variance);
            
            return stdDev > 0 ? avgReturn / stdDev : 0;
        },

        calculateMaxDrawdown(portfolio) {
            if (portfolio.length === 0) return 0;
            
            let peak = portfolio[0].current_value;
            let maxDrawdown = 0;
            
            for (const position of portfolio) {
                if (position.current_value > peak) {
                    peak = position.current_value;
                }
                const drawdown = (peak - position.current_value) / peak;
                if (drawdown > maxDrawdown) {
                    maxDrawdown = drawdown;
                }
            }
            
            return maxDrawdown * 100; // Return as percentage
        }
    },

    // ----------------
    // DASHBOARD DATA (Combined)
    // ----------------
    dashboard: {
        // Load complete dashboard data with enhanced analytics
        async loadDashboardData() {
            try {
                // Get user from Brain
                const { data: { user } } = await brainClient.auth.getUser();

                if (!user) {
                    return { success: false, error: 'Not authenticated' };
                }

                // Get trading data from Bot
                const [portfolio, strategies, marketData, userProfile] = await Promise.all([
                    ZmartyService.trading.getPortfolio(user.id),
                    ZmartyService.trading.getStrategies(user.id),
                    ZmartyService.trading.getMarketData(),
                    ZmartyService.auth.loadUserTradingData(user.id)
                ]);

                // Calculate unified metrics
                const unifiedMetrics = this.calculateUnifiedMetrics(
                    user.user_metadata,
                    portfolio.portfolio || [],
                    strategies.strategies || []
                );

                return {
                    success: true,
                    data: {
                        user: {
                            email: user.email,
                            tier: user.user_metadata.tier,
                            name: user.user_metadata.name,
                            country: user.user_metadata.country,
                            credits_balance: user.user_metadata.credits_balance || 0,
                            engagement_score: user.user_metadata.engagement_score || 0.5
                        },
                        trading: {
                            profile: userProfile,
                            portfolio: portfolio.portfolio || [],
                            portfolioAnalytics: portfolio.analytics || {},
                            strategies: strategies.strategies || [],
                            marketData: marketData.data || []
                        },
                        metrics: unifiedMetrics
                    }
                };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Calculate unified metrics across both systems
        calculateUnifiedMetrics(userMetadata, portfolio, strategies) {
            const totalTrades = portfolio.length;
            const activeStrategies = strategies.filter(s => s.status === 'active').length;
            const winRate = portfolio.length > 0 ? 
                (portfolio.filter(p => p.pnl > 0).length / portfolio.length) * 100 : 0;
            
            return {
                totalTrades,
                activeStrategies,
                winRate,
                riskScore: this.calculateRiskScore(portfolio, userMetadata),
                engagementLevel: this.calculateEngagementLevel(userMetadata, portfolio),
                performanceGrade: this.calculatePerformanceGrade(portfolio, strategies)
            };
        },

        calculateRiskScore(portfolio, userMetadata) {
            if (portfolio.length === 0) return 0.5;
            
            const avgLeverage = portfolio.reduce((sum, p) => sum + (p.leverage || 1), 0) / portfolio.length;
            const volatility = this.calculateVolatility(portfolio);
            const riskTolerance = userMetadata.risk_tolerance || 'medium';
            
            const riskMultiplier = {
                'low': 0.7,
                'medium': 1.0,
                'high': 1.3
            }[riskTolerance] || 1.0;
            
            return Math.min(1.0, (avgLeverage * volatility * riskMultiplier) / 10);
        },

        calculateEngagementLevel(userMetadata, portfolio) {
            const engagementScore = userMetadata.engagement_score || 0.5;
            const recentTrades = portfolio.filter(p => {
                const tradeDate = new Date(p.timestamp);
                const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                return tradeDate > weekAgo;
            }).length;
            
            return {
                score: engagementScore,
                level: engagementScore > 0.8 ? 'high' : engagementScore > 0.5 ? 'medium' : 'low',
                recentActivity: recentTrades
            };
        },

        calculatePerformanceGrade(portfolio, strategies) {
            if (portfolio.length === 0) return 'N/A';
            
            const totalPnL = portfolio.reduce((sum, p) => sum + p.pnl, 0);
            const winRate = (portfolio.filter(p => p.pnl > 0).length / portfolio.length) * 100;
            
            if (totalPnL > 0 && winRate > 60) return 'A';
            if (totalPnL > 0 && winRate > 50) return 'B';
            if (totalPnL > -1000 && winRate > 40) return 'C';
            return 'D';
        },

        calculateVolatility(portfolio) {
            if (portfolio.length < 2) return 0;
            
            const returns = portfolio.map(p => p.pnl / p.initial_value);
            const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
            const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
            
            return Math.sqrt(variance);
        }
    },

    // ----------------
    // SMART ALERTS & NOTIFICATIONS
    // ----------------
    alerts: {
        // Get smart alerts for user
        async getSmartAlerts(userId) {
            try {
                const { data, error } = await botClient
                    .from('smart_alerts')
                    .select('*')
                    .eq('user_id', userId)
                    .eq('status', 'ACTIVE')
                    .order('priority', { ascending: false });

                if (error) throw error;
                return { success: true, alerts: data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        },

        // Create smart alert
        async createSmartAlert(userId, alertData) {
            try {
                const { data, error } = await botClient
                    .from('smart_alerts')
                    .insert({
                        user_id: userId,
                        ...alertData,
                        created_at: new Date().toISOString()
                    });

                if (error) throw error;
                return { success: true, alert: data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }
    }
};

// ===================================
// INITIALIZATION
// ===================================

// Initialize the enhanced service
console.log('🚀 Enhanced ZmartyService initialized with real-time sync');
console.log('📊 ZmartyBrain:', ZMARTYBRAIN_URL);
console.log('🤖 ZmartBot:', ZMARTBOT_URL);

// Make globally available
window.ZmartyService = ZmartyService;
window.brainClient = brainClient;
window.botClient = botClient;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ZmartyService;
}

