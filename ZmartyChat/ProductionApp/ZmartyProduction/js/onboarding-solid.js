// Solid Authentication System for Zmarty
// Implements proper Supabase PKCE OAuth flow and email authentication

class ZmartyAuth {
    constructor() {
        this.supabase = window.supabase;
        this.currentSlide = 0;
        this.slides = document.querySelectorAll('.onboarding-slide');
        this.isProcessing = false;
        
        // Initialize authentication system
        this.init();
    }
    
    async init() {
        console.log('Initializing Zmarty Authentication System');
        
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
                this.redirectToSuccess();
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
            // We just need to wait for the session to be established
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
                        this.redirectToSuccess();
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
        // Google OAuth button
        const googleBtn = document.getElementById('google-auth-btn');
        if (googleBtn) {
            googleBtn.addEventListener('click', (e) => {
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
        
        // Email verification form
        const verificationForm = document.getElementById('email-verification-form');
        if (verificationForm) {
            verificationForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleEmailVerification();
            });
        }
        
        // Forgot password form
        const forgotPasswordForm = document.getElementById('forgot-password-form');
        if (forgotPasswordForm) {
            forgotPasswordForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleForgotPassword();
            });
        }
        
        // Resend verification code
        const resendBtn = document.getElementById('resend-verification-btn');
        if (resendBtn) {
            resendBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.resendVerificationCode();
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
            
            // Store email for verification step
            localStorage.setItem('verification_email', email);
            
            // Show verification screen
            this.showEmailVerificationScreen(email);
            
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
            this.redirectToSuccess();
            
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
    
    async handleForgotPassword() {
        if (this.isProcessing) return;
        
        const email = document.getElementById('reset-email')?.value?.trim();
        
        if (!email) {
            this.showError('Please enter your email address.');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showError('Please enter a valid email address.');
            return;
        }
        
        try {
            this.isProcessing = true;
            this.showLoading('Sending reset link...');
            
            const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
                redirectTo: `${window.location.origin}/reset-password-confirm.html`
            });
            
            if (error) {
                throw error;
            }
            
            this.showSuccess('Password reset link sent to your email!');
            
        } catch (error) {
            console.error('Password reset error:', error);
            this.showError('Failed to send reset link. Please try again.');
        } finally {
            this.isProcessing = false;
            this.hideLoading();
        }
    }
    
    showEmailVerificationScreen(email) {
        // Update verification screen with email
        const emailDisplay = document.getElementById('verification-email-display');
        if (emailDisplay) {
            emailDisplay.textContent = email;
        }
        
        // Show verification slide
        this.showSlide('email-verification');
        
        // Start resend countdown
        this.startResendCountdown();
    }
    
    startResendCountdown(seconds = 60) {
        const resendBtn = document.getElementById('resend-verification-btn');
        if (!resendBtn) return;
        
        let countdown = seconds;
        resendBtn.disabled = true;
        
        const updateButton = () => {
            if (countdown > 0) {
                resendBtn.textContent = `Resend Code (${countdown}s)`;
                countdown--;
                setTimeout(updateButton, 1000);
            } else {
                resendBtn.textContent = 'Resend Code';
                resendBtn.disabled = false;
            }
        };
        
        updateButton();
    }
    
    async resendVerificationCode() {
        const email = localStorage.getItem('verification_email');
        if (!email) {
            this.showError('Email not found. Please try registering again.');
            return;
        }
        
        try {
            this.showLoading('Resending verification code...');
            
            const { error } = await this.supabase.auth.resend({
                type: 'signup',
                email: email,
                options: {
                    emailRedirectTo: `${window.location.origin}/auth/callback`
                }
            });
            
            if (error) {
                throw error;
            }
            
            this.showSuccess('Verification code sent!');
            this.startResendCountdown();
            
        } catch (error) {
            console.error('Resend verification error:', error);
            this.showError('Failed to resend code. Please try again.');
        } finally {
            this.hideLoading();
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
    
    showSlide(slideId) {
        // Hide all slides
        this.slides.forEach(slide => slide.style.display = 'none');
        
        // Show target slide
        const targetSlide = document.getElementById(slideId);
        if (targetSlide) {
            targetSlide.style.display = 'block';
        }
    }
    
    showLoading(message) {
        // Implementation depends on your loading UI
        console.log('Loading:', message);
    }
    
    hideLoading() {
        // Implementation depends on your loading UI
        console.log('Loading hidden');
    }
    
    showError(message) {
        // Implementation depends on your error UI
        console.error('Error:', message);
        alert(message); // Temporary - replace with proper UI
    }
    
    showSuccess(message) {
        // Implementation depends on your success UI
        console.log('Success:', message);
        alert(message); // Temporary - replace with proper UI
    }
    
    redirectToSuccess() {
        // Redirect to main app or dashboard
        console.log('Redirecting to success page...');
        // window.location.href = '/dashboard';
        alert('Authentication successful! (Redirect to dashboard would happen here)');
    }
}

// Initialize authentication system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Zmarty Auth...');
    window.zmartyAuth = new ZmartyAuth();
});

console.log('Zmarty Authentication System loaded');
