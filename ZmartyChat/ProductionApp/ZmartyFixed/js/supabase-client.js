// Supabase Client Configuration
// Dual Database Setup for Zmarty
// CONFIGURED WITH YOUR ACTUAL KEYS

// Check if Supabase library is loaded
if (typeof window.supabase === 'undefined') {
    console.error('⚠️ Supabase client library not loaded!');
    console.log('Add this to your HTML before this script:');
    console.log('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>');
    throw new Error('Supabase client library required');
}

// Configuration with your actual keys
const ZMARTY_CONFIG = {
    // ZmartyBrain Project (Authentication & User Management) - YOUR ACTUAL KEY
    AUTH: {
        URL: 'https://xhskmqsgtdhehzlvtuns.supabase.co',
        ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw'
    },
    
    // Smart Trading Project (Trading Operations) - YOUR ACTUAL KEY
    TRADING: {
        URL: 'https://asjtxrmftmutcsnqgidy.supabase.co',
        ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM'
    },
    
    // NEVER put service_role keys in frontend code!
    // Service keys should only be used in secure backend environments
};

// Validate configuration
function validateConfig() {
    const errors = [];
    
    if (ZMARTY_CONFIG.AUTH.ANON_KEY === 'YOUR_ZMARTYBRAIN_ANON_KEY_HERE') {
        errors.push('❌ ZmartyBrain anon key not configured');
        console.error('Get it from: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/api');
    }
    
    if (!ZMARTY_CONFIG.TRADING.ANON_KEY.startsWith('eyJ')) {
        errors.push('❌ Smart Trading anon key invalid');
    } else {
        console.log('✅ Smart Trading key configured');
    }
    
    if (errors.length > 0) {
        console.warn('Configuration issues:', errors);
        return false;
    }
    
    return true;
}

// Initialize Supabase clients
let supabaseAuth = null;
let supabaseTrading = null;

try {
    // Primary authentication client (ZmartyBrain)
    if (ZMARTY_CONFIG.AUTH.ANON_KEY !== 'YOUR_ZMARTYBRAIN_ANON_KEY_HERE') {
        supabaseAuth = window.supabase.createClient(
            ZMARTY_CONFIG.AUTH.URL,
            ZMARTY_CONFIG.AUTH.ANON_KEY,
            {
                auth: {
                    autoRefreshToken: true,
                    persistSession: true,
                    detectSessionInUrl: true,
                    storageKey: 'zmarty-auth-storage',
                    storage: window.localStorage,
                    flowType: 'pkce'
                },
                global: {
                    headers: {
                        'x-client-info': 'zmarty-onboarding/2.0.0'
                    }
                },
                db: {
                    schema: 'public'
                },
                realtime: {
                    params: {
                        eventsPerSecond: 2
                    }
                }
            }
        );
        console.log('✅ ZmartyBrain client initialized');
    } else {
        console.warn('⚠️ ZmartyBrain client not initialized - missing key');
    }

    // Secondary trading client (Smart Trading) - CONFIGURED WITH YOUR KEY
    supabaseTrading = window.supabase.createClient(
        ZMARTY_CONFIG.TRADING.URL,
        ZMARTY_CONFIG.TRADING.ANON_KEY,
        {
            auth: {
                autoRefreshToken: false,
                persistSession: false
            },
            global: {
                headers: {
                    'x-client-info': 'zmarty-trading/2.0.0'
                }
            },
            db: {
                schema: 'public'
            }
        }
    );
    console.log('✅ Smart Trading client initialized');

} catch (error) {
    console.error('Failed to initialize Supabase clients:', error);
}

// Authentication Service
const AuthService = {
    // Test connection to ZmartyBrain
    async testAuthConnection() {
        if (!supabaseAuth) {
            console.error('❌ ZmartyBrain client not initialized');
            return false;
        }
        
        try {
            const { data, error } = await supabaseAuth
                .from('user_profiles')
                .select('count')
                .limit(1);
            
            if (error) {
                console.error('❌ ZmartyBrain connection failed:', error.message);
                return false;
            }
            
            console.log('✅ ZmartyBrain connection successful');
            return true;
        } catch (err) {
            console.error('❌ ZmartyBrain test failed:', err);
            return false;
        }
    },

    // Sign up new user
    async signUp(email, password, metadata = {}) {
        if (!supabaseAuth) {
            throw new Error('Authentication not configured. Add ZmartyBrain key.');
        }

        try {
            const { data, error } = await supabaseAuth.auth.signUp({
                email,
                password,
                options: {
                    emailRedirectTo: `${window.location.origin}/verify`,
                    data: {
                        ...metadata,
                        signup_timestamp: new Date().toISOString(),
                        app_version: '2.0.0'
                    }
                }
            });

            if (error) throw error;

            // If successful, also create reference in trading database
            if (data.user && supabaseTrading) {
                await this.createTradingReference(data.user.id, email);
            }

            return { success: true, data };
        } catch (error) {
            console.error('SignUp Error:', error);
            return { success: false, error };
        }
    },

    // Create user reference in trading database
    async createTradingReference(userId, email) {
        if (!supabaseTrading) {
            console.warn('Trading database not connected');
            return;
        }

        try {
            const { error } = await supabaseTrading
                .from('user_references')
                .insert({
                    user_id: userId,
                    email: email,
                    tier: 'free',
                    credits_balance: 100,
                    is_active: true,
                    created_at: new Date().toISOString()
                });

            if (error && !error.message.includes('duplicate')) {
                console.error('Failed to create trading reference:', error);
            }
        } catch (err) {
            console.error('Trading reference error:', err);
        }
    },

    // Sign in existing user
    async signIn(email, password) {
        if (!supabaseAuth) {
            throw new Error('Authentication not configured. Add ZmartyBrain key.');
        }

        try {
            const { data, error } = await supabaseAuth.auth.signInWithPassword({
                email,
                password
            });

            if (error) throw error;
            return { success: true, data };
        } catch (error) {
            console.error('SignIn Error:', error);
            return { success: false, error };
        }
    },

    // Sign out
    async signOut() {
        if (!supabaseAuth) return;
        
        try {
            const { error } = await supabaseAuth.auth.signOut();
            if (error) throw error;
            return { success: true };
        } catch (error) {
            console.error('SignOut Error:', error);
            return { success: false, error };
        }
    },

    // Get current user
    async getCurrentUser() {
        if (!supabaseAuth) return null;
        
        try {
            const { data: { user }, error } = await supabaseAuth.auth.getUser();
            if (error) throw error;
            return user;
        } catch (error) {
            console.error('Get User Error:', error);
            return null;
        }
    }
};

// Trading Service
const TradingService = {
    // Test connection to Smart Trading
    async testTradingConnection() {
        if (!supabaseTrading) {
            console.error('❌ Trading client not initialized');
            return false;
        }
        
        try {
            const { data, error } = await supabaseTrading
                .from('portfolios')
                .select('count')
                .limit(1);
            
            if (error) {
                console.error('❌ Smart Trading connection failed:', error.message);
                console.log('This might be because RLS is enabled. Try with a real user query.');
                return false;
            }
            
            console.log('✅ Smart Trading connection successful');
            return true;
        } catch (err) {
            console.error('❌ Smart Trading test failed:', err);
            return false;
        }
    },

    // Get user portfolios
    async getPortfolios(userId) {
        if (!supabaseTrading) {
            throw new Error('Trading database not configured');
        }

        try {
            const { data, error } = await supabaseTrading
                .from('portfolios')
                .select('*')
                .eq('user_id', userId);

            if (error) throw error;
            return { success: true, data };
        } catch (error) {
            console.error('Get Portfolios Error:', error);
            return { success: false, error };
        }
    },

    // Create portfolio
    async createPortfolio(userId, name, description = '') {
        if (!supabaseTrading) {
            throw new Error('Trading database not configured');
        }

        try {
            const { data, error } = await supabaseTrading
                .from('portfolios')
                .insert({
                    user_id: userId,
                    name: name,
                    description: description,
                    is_default: false,
                    created_at: new Date().toISOString()
                })
                .select()
                .single();

            if (error) throw error;
            return { success: true, data };
        } catch (error) {
            console.error('Create Portfolio Error:', error);
            return { success: false, error };
        }
    }
};

// Test connections on load
window.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Zmarty Supabase Configuration Loaded');
    console.log('================================');
    
    validateConfig();
    
    // Only test if we're in development
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('📡 Testing database connections...');
        
        if (supabaseAuth) {
            AuthService.testAuthConnection();
        }
        
        if (supabaseTrading) {
            TradingService.testTradingConnection();
        }
    }
});

// Export for use in other modules
window.supabaseAuth = supabaseAuth;
window.supabaseTrading = supabaseTrading;
window.AuthService = AuthService;
window.TradingService = TradingService;

// Also export under the old names for compatibility
window.supabase = supabaseAuth; // Primary client for auth
window.dataClient = supabaseTrading; // Trading client