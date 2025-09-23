// Complete Onboarding System for Zmarty
// Integrates authentication with full user journey

class ZmartyCompleteAuth {
    constructor() {
        this.supabase = window.supabase;
        this.isProcessing = false;
        
        // Initialize authentication system
        this.init();
    }
    
    async init() {
        console.log('Initializing Zmarty Complete Authentication System');
        
        // Check for existing session on page load
        await this.checkExistingSession();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Handle OAuth callback if present
        await this.handleOAuthCallback();
    }
    
    async checkExistingSession() {
        try {
            const session = await window.authUtils.getCurrentSession();
            if (session?.user) {
                console.log('Existing session found:', session.user.email);
                // Skip to dashboard if user is already authenticated
                this.skipToDashboard();
                return true;
            }
        } catch (error) {
            console.error('Error checking existing session:', error);
        }
        return false;
    }
    
    async handleOAuthCallback() {
        // Check if we're on a callback URL
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const error = urlParams.get('error');
        
        if (error) {
            console.error('OAuth error:', error);
            this.showError('Authentication failed. Please try again.');
            return;
        }
        
        if (code) {
            console.log('OAuth callback detected, waiting for session...');
            // Supabase will automatically handle the PKCE code exchange
            await this.waitForSession();
        }
    }
    
    async waitForSession(maxWaitTime = 10000) {
        const startTime = Date.now();
        
        return new Promise((resolve) => {
            const checkSession = async () => {
                try {
                    const session = await window.authUtils.getCurrentSession();
                    if (session?.user) {
                        console.log('OAuth session established:', session.user.email);
                        this.handleAuthenticationSuccess(session);
                        resolve(true);
                        return;
                    }
                    
                    // Check if we've exceeded max wait time
                    if (Date.now() - startTime > maxWaitTime) {
                        console.error('OAuth session timeout');
                        this.showError('Authentication timed out. Please try again.');
                        resolve(false);
                        return;
                    }
                    
                    // Continue waiting
                    setTimeout(checkSession, 500);
                } catch (error) {
                    console.error('Error checking session:', error);
                    this.showError('Authentication failed. Please try again.');
                    resolve(false);
                }
            };
            
            checkSession();
        });
    }
    
    setupEventListeners() {
        // Google OAuth buttons (both registration and login)
        const googleAuthBtn = document.getElementById('google-auth-btn');
        const googleLoginBtn = document.getElementById('google-login-btn');
        
        if (googleAuthBtn) {
            googleAuthBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleGoogleAuth();
            });
        }
        
        if (googleLoginBtn) {
            googleLoginBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleGoogleAuth();
            });
        }
        
        // Email registration form
        const emailForm = document.getElementById('email-registration-form');
        if (emailForm) {
            emailForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleEmailRegistration();
            });
        }
        
        // Email login form
        const loginForm = document.getElementById('email-login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleEmailLogin();
            });
        }
    }
    
    async handleGoogleAuth() {
        if (this.isProcessing) return;
        
        try {
            this.isProcessing = true;
            this.showLoading('Connecting to Google...');
            
            const { data, error } = await this.supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: `${window.location.origin}/auth/callback`,
                    queryParams: {
                        access_type: 'offline',
                        prompt: 'consent'
                    }
                }
            });
            
            if (error) {
                throw error;
            }
            
            console.log('Google OAuth initiated successfully');
            // The redirect will happen automatically
            
        } catch (error) {
            console.error('Google OAuth error:', error);
            this.showError('Failed to connect with Google. Please try again.');
        } finally {
            this.isProcessing = false;
            this.hideLoading();
        }
    }
    
    async handleEmailRegistration() {
        if (this.isProcessing) return;
        
        const email = document.getElementById('registration-email')?.value?.trim();
        const password = document.getElementById('registration-password')?.value;
        const termsAccepted = document.getElementById('terms-checkbox')?.checked;
        
        // Validation
        if (!email || !password) {
            this.showError('Please fill in all required fields.');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showError('Please enter a valid email address.');
            return;
        }
        
        if (!this.isValidPassword(password)) {
            this.showError('Password must be at least 8 characters with 1 uppercase letter and 1 number.');
            return;
        }
        
        if (!termsAccepted) {
            this.showError('Please accept the Terms and Privacy Policy.');
            return;
        }
        
        try {
            this.isProcessing = true;
            this.showLoading('Creating your account...');
            
            const { data, error } = await this.supabase.auth.signUp({
                email: email,
                password: password,
                options: {
                    emailRedirectTo: `${window.location.origin}/auth/callback`,
                    data: {
                        registration_source: 'email',
                        registration_timestamp: new Date().toISOString()
                    }
                }
            });
            
            if (error) {
                throw error;
            }
            
            console.log('Email registration successful:', data);
            
            // For email registration, we need email verification
            // Show success message and continue to profile setup after verification
            this.showSuccess('Account created! Please check your email to verify your account.');
            
            // Simulate successful verification for demo (in real app, this would happen after email verification)
            setTimeout(() => {
                this.handleAuthenticationSuccess({
                    user: {
                        email: email,
                        id: data.user?.id || 'temp-id',
                        app_metadata: { provider: 'email' },
                        user_metadata: {}
                    }
                });
            }, 2000);
            
        } catch (error) {
            console.error('Email registration error:', error);
            if (error.message.includes('already registered')) {
                this.showError('This email is already registered. Please sign in instead.');
            } else {
                this.showError('Failed to create account. Please try again.');
            }
        } finally {
            this.isProcessing = false;
            this.hideLoading();
        }
    }
    
    async handleEmailLogin() {
        if (this.isProcessing) return;
        
        const email = document.getElementById('login-email')?.value?.trim();
        const password = document.getElementById('login-password')?.value;
        
        if (!email || !password) {
            this.showError('Please enter your email and password.');
            return;
        }
        
        try {
            this.isProcessing = true;
            this.showLoading('Signing you in...');
            
            const { data, error } = await this.supabase.auth.signInWithPassword({
                email: email,
                password: password
            });
            
            if (error) {
                throw error;
            }
            
            console.log('Email login successful:', data.user.email);
            this.handleAuthenticationSuccess(data);
            
        } catch (error) {
            console.error('Email login error:', error);
            if (error.message.includes('Invalid login credentials')) {
                this.showError('Invalid email or password. Please try again.');
            } else if (error.message.includes('Email not confirmed')) {
                this.showError('Please verify your email address before signing in.');
            } else {
                this.showError('Failed to sign in. Please try again.');
            }
        } finally {
            this.isProcessing = false;
            this.hideLoading();
        }
    }
    
    handleAuthenticationSuccess(sessionData) {
        console.log('Authentication successful:', sessionData);
        
        // Store user data
        const userData = {
            email: sessionData.user.email,
            userId: sessionData.user.id,
            authProvider: sessionData.user.app_metadata?.provider || 'email',
            fullName: sessionData.user.user_metadata?.full_name || 
                     sessionData.user.user_metadata?.name || 
                     sessionData.user.user_metadata?.display_name || '',
            isAuthenticated: true,
            timestamp: Date.now()
        };
        
        localStorage.setItem('zmarty_user_data', JSON.stringify(userData));
        
        // Continue to profile setup in the onboarding flow
        if (window.handleAuthSuccess) {
            window.handleAuthSuccess(userData);
        } else {
            // Fallback: skip to dashboard
            this.skipToDashboard();
        }
    }
    
    skipToDashboard() {
        // Skip directly to dashboard slide
        if (window.currentSlide !== undefined && window.slides) {
            window.currentSlide = window.slides.length - 1; // Last slide (dashboard)
            window.showSlide(window.slides[window.currentSlide]);
        }
    }
    
    // Utility functions
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    isValidPassword(password) {
        // At least 8 characters, 1 uppercase, 1 number
        const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
        return passwordRegex.test(password);
    }
    
    showLoading(message) {
        console.log('Loading:', message);
        // Add visual loading indicator if needed
    }
    
    hideLoading() {
        console.log('Loading hidden');
        // Hide visual loading indicator if needed
    }
    
    showError(message) {
        console.error('Error:', message);
        // Show error message in UI
        this.showMessage(message, 'error');
    }
    
    showSuccess(message) {
        console.log('Success:', message);
        // Show success message in UI
        this.showMessage(message, 'success');
    }
    
    showMessage(message, type = 'info') {
        // Create and show a temporary message
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            max-width: 90%;
            text-align: center;
            ${type === 'error' ? 'background: #e74c3c;' : 
              type === 'success' ? 'background: #27ae60;' : 'background: #3498db;'}
        `;
        messageDiv.textContent = message;
        
        document.body.appendChild(messageDiv);
        
        // Remove message after 4 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 4000);
    }
}

// Initialize complete authentication system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Zmarty Complete Auth...');
    window.zmartyCompleteAuth = new ZmartyCompleteAuth();
});

console.log('Zmarty Complete Authentication System loaded');
