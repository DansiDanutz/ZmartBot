// Supabase Client Configuration
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// User Management Functions
const UserService = {
    // Register new user and send OTP
    async register(email, password, tier = 'free') {
        try {
            // Store registration data for later use
            sessionStorage.setItem('temp_email', email);
            sessionStorage.setItem('temp_password', password);
            sessionStorage.setItem('temp_tier', tier);

            // Step 1: Create the user account with email confirmation
            console.log('🚀 Creating Supabase user account:', email);
            const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
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

            if (signUpError) {
                console.error('❌ Supabase Registration Error:', signUpError);
                // Check if user already exists
                if (signUpError.message.includes('already registered')) {
                    return {
                        success: false,
                        error: 'This email is already registered. Please sign in instead.',
                        supabaseError: signUpError
                    };
                }
                throw signUpError;
            }

            console.log('✅ Supabase user created successfully:', signUpData);

            // Step 2: Sign out immediately to prevent auto-login
            await supabase.auth.signOut();

            // Check if user was created
            if (signUpData.user) {
                console.log('📧 User created in Supabase:', signUpData.user.email);
                console.log('🔑 User ID:', signUpData.user.id);
                console.log('📊 User Metadata:', signUpData.user.user_metadata);

                // PRODUCTION MODE - Real emails
                sessionStorage.setItem('pending_verification', 'true');
                return {
                    success: true,
                    message: `✅ Verification email sent to ${signUpData.user.email}! Check your inbox.`,
                    needsVerification: true,
                    userId: signUpData.user.id,
                    userEmail: signUpData.user.email
                };

                /* PRODUCTION MODE - Uncomment for real emails
                sessionStorage.setItem('pending_verification', 'true');
                return {
                    success: true,
                    message: `✅ Verification email sent to ${signUpData.user.email}! Check your inbox.`,
                    needsVerification: true,
                    userId: signUpData.user.id,
                    userEmail: signUpData.user.email
                };
                */
            } else {
                console.log('⚠️ User confirmation pending - check email');
                return {
                    success: true,
                    message: '📧 Check your email for the 6-digit verification code',
                    needsVerification: true
                };
            }
        } catch (error) {
            console.error('Registration error:', error);

            // Handle rate limiting
            if (error.message && error.message.includes('security purposes')) {
                const waitTime = error.message.match(/\d+/);
                return {
                    success: false,
                    error: `Please wait ${waitTime ? waitTime[0] : '60'} seconds before trying again (security limit).`,
                    isRateLimit: true
                };
            }

            return {
                success: false,
                error: error.message || 'Registration failed. Please try again.'
            };
        }
    },

    // Verify email with OTP code
    async verifyEmail(email, code) {
        try {
            console.log('🔐 Verifying code:', { email, code });

            // Use real Supabase OTP verification
            const { data, error } = await supabase.auth.verifyOtp({
                email: email,
                token: code,
                type: 'signup'
            });

            if (!error && data.session) {
                console.log('✅ OTP verification successful');

                // Clean up any session storage
                sessionStorage.removeItem('pending_verification');
                sessionStorage.removeItem('temp_password');
                sessionStorage.removeItem('temp_email');

                return {
                    success: true,
                    message: 'Email verified successfully',
                    session: data.session,
                    user: data.user,
                    userId: data.user?.id
                };
            }

            if (error) {
                console.error('Verification error:', error);
                return {
                    success: false,
                    error: 'Invalid verification code. Please check your email and try again.'
                };
            }

            return {
                success: false,
                error: 'Invalid code. Please check your email.'
            };
        } catch (error) {
            console.error('Verification error:', error);
            return {
                success: false,
                error: 'Verification failed. Please try again.'
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

    // Check if we're in the middle of registration
    const isPendingVerification = sessionStorage.getItem('pending_verification');

    if (event === 'SIGNED_IN') {
        console.log('User signed in:', session.user.email);
    } else if (event === 'SIGNED_OUT') {
        console.log('User signed out');
        // Don't redirect if we're in the middle of registration/verification
        if (!isPendingVerification && !window.location.pathname.includes('index.html')) {
            window.location.href = 'index.html';
        }
    }
});