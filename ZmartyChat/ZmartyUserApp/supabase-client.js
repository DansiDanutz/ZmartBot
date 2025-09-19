// Supabase Client Configuration
const SUPABASE_URL = 'https://asjtxrmftmutcsnqgidy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// User Management Functions
const UserService = {
    // Register new user and send OTP
    async register(email, password, tier = 'free') {
        try {
            // Store password temporarily for later use
            sessionStorage.setItem('temp_password', password);
            sessionStorage.setItem('temp_tier', tier);

            // Send OTP to email (this will create user if doesn't exist)
            console.log('Sending OTP to:', email);
            const { data, error } = await supabase.auth.signInWithOtp({
                email: email,
                options: {
                    shouldCreateUser: true,  // Create user if doesn't exist
                    data: {
                        tier: tier,
                        name: '',
                        country: '',
                        profile_completed: false
                    }
                }
            });

            if (error) throw error;

            return {
                success: true,
                message: `Verification code sent to ${email}`,
                userId: null,  // Will get after OTP verification
                needsVerification: true
            };
        } catch (error) {
            console.error('Registration error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Verify email with OTP code
    async verifyEmail(email, code) {
        try {
            console.log('Verifying OTP:', { email, code });
            const { data, error } = await supabase.auth.verifyOtp({
                email: email,
                token: code,
                type: 'email'  // Changed from 'signup' to 'email' for OTP
            });

            if (error) throw error;

            // After successful OTP verification, update password if stored
            const tempPassword = sessionStorage.getItem('temp_password');
            if (tempPassword && data.user) {
                await supabase.auth.updateUser({
                    password: tempPassword
                });
                sessionStorage.removeItem('temp_password');
            }

            return {
                success: true,
                message: 'Email verified successfully',
                session: data.session,
                user: data.user
            };
        } catch (error) {
            console.error('Verification error:', error);
            return {
                success: false,
                error: 'Invalid verification code. Please check and try again.'
            };
        }
    },

    // Update user profile
    async updateProfile(name, country) {
        try {
            const { data: { user } } = await supabase.auth.getUser();

            if (!user) throw new Error('No user logged in');

            const { data, error } = await supabase.auth.updateUser({
                data: {
                    name: name,
                    country: country,
                    profile_completed: true
                }
            });

            if (error) throw error;

            return {
                success: true,
                message: 'Profile updated successfully',
                user: data.user
            };
        } catch (error) {
            console.error('Profile update error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Login with email and password
    async login(email, password) {
        try {
            const { data, error } = await supabase.auth.signInWithPassword({
                email: email,
                password: password
            });

            if (error) throw error;

            return {
                success: true,
                message: 'Logged in successfully',
                session: data.session,
                user: data.user
            };
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: 'Invalid email or password'
            };
        }
    },

    // Social login (Google/Apple)
    async socialLogin(provider) {
        try {
            const { data, error } = await supabase.auth.signInWithOAuth({
                provider: provider.toLowerCase(),
                options: {
                    redirectTo: window.location.origin + '/dashboard.html'
                }
            });

            if (error) throw error;

            return {
                success: true,
                message: `Redirecting to ${provider} login...`,
                url: data.url
            };
        } catch (error) {
            console.error('Social login error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Get current user
    async getCurrentUser() {
        try {
            const { data: { user }, error } = await supabase.auth.getUser();

            if (error) throw error;

            return {
                success: true,
                user: user
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
            const { error } = await supabase.auth.signOut();
            if (error) throw error;

            return {
                success: true,
                message: 'Logged out successfully'
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Resend verification code
    async resendCode(email) {
        try {
            const { data, error } = await supabase.auth.resend({
                type: 'signup',
                email: email,
                options: {
                    emailRedirectTo: window.location.origin + '/ZmartyUserApp/index.html'
                }
            });

            if (error) throw error;

            return {
                success: true,
                message: `New verification code sent to ${email}`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    },

    // Update user tier
    async updateTier(tier) {
        try {
            const { data: { user } } = await supabase.auth.getUser();

            if (!user) throw new Error('No user logged in');

            const { data, error } = await supabase.auth.updateUser({
                data: { tier: tier }
            });

            if (error) throw error;

            return {
                success: true,
                message: 'Tier updated successfully',
                tier: tier
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
};

// Check if user is logged in on page load
window.addEventListener('load', async () => {
    const { data: { session } } = await supabase.auth.getSession();

    if (session) {
        console.log('User logged in:', session.user.email);

        // If on onboarding page and logged in, redirect to dashboard
        if (window.location.pathname.includes('index.html')) {
            if (session.user.user_metadata.profile_completed) {
                window.location.href = 'dashboard.html';
            }
        }
    }
});

// Listen for auth state changes
supabase.auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event);

    if (event === 'SIGNED_IN') {
        console.log('User signed in:', session.user.email);
    } else if (event === 'SIGNED_OUT') {
        console.log('User signed out');
        // Redirect to onboarding
        if (!window.location.pathname.includes('index.html')) {
            window.location.href = 'index.html';
        }
    }
});