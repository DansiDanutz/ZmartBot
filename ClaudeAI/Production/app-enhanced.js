// Enhanced ZmartyBrain Onboarding Application with Supabase Integration

const App = {
    currentStep: 1,
    totalSteps: 9,
    userData: {},
    selectedPlan: 'professional',
    supabase: window.supabaseClient,

    // Navigation
    goToStep(step) {
        if (step < 1 || step > this.totalSteps) return;

        // Hide current step
        const currentSlide = document.getElementById(`step${this.currentStep}`);
        if (currentSlide) currentSlide.classList.remove('active');

        // Show new step
        const newSlide = document.getElementById(`step${step}`);
        if (newSlide) newSlide.classList.add('active');

        // Update current step
        this.currentStep = step;

        // Update UI
        this.updateProgress();
        this.updateNavigation();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.goToStep(this.currentStep + 1);
        }
    },

    prevStep() {
        if (this.currentStep > 1) {
            this.goToStep(this.currentStep - 1);
        }
    },

    updateProgress() {
        const progress = (this.currentStep / this.totalSteps) * 100;
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `Step ${this.currentStep} of ${this.totalSteps}`;
    },

    updateNavigation() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        if (prevBtn) prevBtn.disabled = this.currentStep === 1;
        if (nextBtn) nextBtn.style.display = this.currentStep >= 2 ? 'none' : 'flex';
    },

    // Authentication
    switchAuthTab(tab) {
        const tabs = document.querySelectorAll('.auth-tab');
        tabs.forEach(t => t.classList.remove('active'));

        const forms = document.querySelectorAll('.auth-form');
        forms.forEach(f => f.classList.remove('active'));

        const selectedTab = document.querySelector(`[data-tab="${tab}"]`);
        const selectedForm = document.getElementById(`${tab}Form`);

        if (selectedTab) selectedTab.classList.add('active');
        if (selectedForm) selectedForm.classList.add('active');
    },

    async signup(event) {
        event.preventDefault();
        const email = document.getElementById('signupEmail').value.trim();
        const password = document.getElementById('signupPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Validation
        if (!email || !password || !confirmPassword) {
            this.showAlert('Please fill in all fields', 'error');
            return;
        }

        if (password.length < 8) {
            this.showAlert('Password must be at least 8 characters', 'error');
            return;
        }

        if (password !== confirmPassword) {
            this.showAlert('Passwords do not match', 'error');
            return;
        }

        this.showAlert('Creating your account...', 'success');

        try {
            const { data, error } = await this.supabase.auth.signUp({
                email: email,
                password: password,
                options: {
                    data: {
                        onboarding_started: new Date().toISOString()
                    }
                }
            });

            if (error) throw error;

            this.userData.email = email;
            this.userData.userId = data.user?.id;

            this.showAlert('Account created! Check your email for verification.', 'success');
            setTimeout(() => this.goToStep(3), 2000);

        } catch (error) {
            console.error('Signup error:', error);
            this.showAlert(error.message || 'Signup failed. Please try again.', 'error');
        }
    },

    async login(event) {
        event.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;

        if (!email || !password) {
            this.showAlert('Please fill in all fields', 'error');
            return;
        }

        this.showAlert('Signing in...', 'success');

        try {
            const { data, error } = await this.supabase.auth.signInWithPassword({
                email: email,
                password: password
            });

            if (error) throw error;

            this.userData.email = email;
            this.userData.userId = data.user?.id;

            this.showAlert('Welcome back!', 'success');

            // Check if user has completed onboarding
            const { data: profile } = await this.supabase
                .from('user_profiles')
                .select('onboarding_completed')
                .eq('user_id', data.user.id)
                .single();

            if (profile?.onboarding_completed) {
                setTimeout(() => window.location.href = '/dashboard', 1500);
            } else {
                setTimeout(() => this.goToStep(5), 1500);
            }

        } catch (error) {
            console.error('Login error:', error);
            this.showAlert(error.message || 'Login failed. Please check your credentials.', 'error');
        }
    },

    async googleSignIn() {
        try {
            const { data, error } = await this.supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: window.location.origin + '/onboarding?step=5'
                }
            });

            if (error) throw error;
        } catch (error) {
            console.error('Google sign-in error:', error);
            this.showAlert('Google sign-in failed. Please try again.', 'error');
        }
    },

    // OTP Verification
    async verifyOTP(event) {
        event.preventDefault();
        const inputs = document.querySelectorAll('.otp-input');
        const otp = Array.from(inputs).map(input => input.value).join('');

        if (otp.length !== 6) {
            this.showAlert('Please enter all 6 digits', 'error');
            return;
        }

        this.showAlert('Verifying code...', 'success');

        try {
            const { data, error } = await this.supabase.auth.verifyOtp({
                email: this.userData.email,
                token: otp,
                type: 'signup'
            });

            if (error) throw error;

            this.showAlert('Email verified successfully!', 'success');
            setTimeout(() => this.nextStep(), 1500);

        } catch (error) {
            console.error('OTP verification error:', error);
            this.showAlert('Invalid code. Please try again.', 'error');
        }
    },

    async resendOTP() {
        if (!this.userData.email) {
            this.showAlert('Email not found. Please sign up again.', 'error');
            return;
        }

        try {
            const { error } = await this.supabase.auth.resend({
                type: 'signup',
                email: this.userData.email
            });

            if (error) throw error;

            this.showAlert('Verification code sent!', 'success');
        } catch (error) {
            console.error('Resend OTP error:', error);
            this.showAlert('Failed to resend code. Please try again.', 'error');
        }
    },

    // OTP Input handling
    handleOTPInput(event, index) {
        const input = event.target;
        const value = input.value;

        if (value.length === 1 && index < 5) {
            const nextInput = document.querySelectorAll('.otp-input')[index + 1];
            if (nextInput) nextInput.focus();
        }

        if (event.key === 'Backspace' && !value && index > 0) {
            const prevInput = document.querySelectorAll('.otp-input')[index - 1];
            if (prevInput) prevInput.focus();
        }
    },

    // Profile Setup
    async saveProfile(event) {
        event.preventDefault();
        const fullName = document.getElementById('fullName').value.trim();
        const username = document.getElementById('username').value.trim();
        const phoneNumber = document.getElementById('phoneNumber').value.trim();

        if (!fullName || !username) {
            this.showAlert('Name and username are required', 'error');
            return;
        }

        this.showAlert('Saving profile...', 'success');

        try {
            const { data: user } = await this.supabase.auth.getUser();

            const { error } = await this.supabase
                .from('user_profiles')
                .upsert({
                    user_id: user.user.id,
                    full_name: fullName,
                    username: username,
                    phone_number: phoneNumber,
                    updated_at: new Date().toISOString()
                });

            if (error) throw error;

            this.userData.fullName = fullName;
            this.userData.username = username;
            this.userData.phoneNumber = phoneNumber;

            this.showAlert('Profile saved!', 'success');
            setTimeout(() => this.nextStep(), 1500);

        } catch (error) {
            console.error('Profile save error:', error);
            this.showAlert('Failed to save profile. Please try again.', 'error');
        }
    },

    // Trading Preferences
    async savePreferences(event) {
        event.preventDefault();
        const experience = document.getElementById('experience').value;
        const riskTolerance = document.getElementById('riskTolerance').value;
        const tradingStyle = document.getElementById('tradingStyle').value;

        this.showAlert('Saving preferences...', 'success');

        try {
            const { data: user } = await this.supabase.auth.getUser();

            const { error } = await this.supabase
                .from('trading_preferences')
                .upsert({
                    user_id: user.user.id,
                    experience_level: experience,
                    risk_tolerance: riskTolerance,
                    trading_style: tradingStyle,
                    updated_at: new Date().toISOString()
                });

            if (error) throw error;

            this.userData.experience = experience;
            this.userData.riskTolerance = riskTolerance;
            this.userData.tradingStyle = tradingStyle;

            this.showAlert('Preferences saved!', 'success');
            setTimeout(() => this.nextStep(), 1500);

        } catch (error) {
            console.error('Preferences save error:', error);
            this.showAlert('Failed to save preferences. Please try again.', 'error');
        }
    },

    // Plan Selection
    selectPlan(plan) {
        this.selectedPlan = plan;

        // Update UI
        document.querySelectorAll('.plan-card').forEach(card => {
            card.classList.remove('selected');
        });

        const selectedCard = document.querySelector(`[data-plan="${plan}"]`);
        if (selectedCard) selectedCard.classList.add('selected');

        const planNames = {
            basic: 'Basic ($29/mo)',
            professional: 'Professional ($99/mo)',
            enterprise: 'Enterprise (Custom)'
        };

        const selectedPlanText = document.getElementById('selectedPlanText');
        const summaryPlan = document.getElementById('summaryPlan');

        if (selectedPlanText) selectedPlanText.textContent = planNames[plan].split(' ')[0];
        if (summaryPlan) summaryPlan.textContent = planNames[plan];
    },

    async confirmPlan() {
        try {
            const { data: user } = await this.supabase.auth.getUser();

            const { error } = await this.supabase
                .from('user_subscriptions')
                .insert({
                    user_id: user.user.id,
                    plan_type: this.selectedPlan,
                    status: 'pending',
                    created_at: new Date().toISOString()
                });

            if (error) throw error;

            this.userData.plan = this.selectedPlan;
            this.nextStep();

        } catch (error) {
            console.error('Plan confirmation error:', error);
            this.showAlert('Failed to confirm plan. Continuing anyway...', 'warning');
            setTimeout(() => this.nextStep(), 1500);
        }
    },

    // Complete Onboarding
    async completeOnboarding(event) {
        if (event) event.preventDefault();

        // Update summary
        const summaryEmail = document.getElementById('summaryEmail');
        if (summaryEmail) summaryEmail.textContent = this.userData.email || 'user@example.com';

        this.showAlert('Setting up your account...', 'success');

        try {
            const { data: user } = await this.supabase.auth.getUser();

            // Mark onboarding as complete
            const { error } = await this.supabase
                .from('user_profiles')
                .update({
                    onboarding_completed: true,
                    onboarding_completed_at: new Date().toISOString()
                })
                .eq('user_id', user.user.id);

            if (error) throw error;

            // Award welcome credits
            await this.supabase.from('user_credits').insert({
                user_id: user.user.id,
                amount: 100,
                type: 'welcome_bonus',
                description: 'Welcome bonus for completing onboarding',
                created_at: new Date().toISOString()
            });

            setTimeout(() => this.nextStep(), 2000);

        } catch (error) {
            console.error('Complete onboarding error:', error);
            setTimeout(() => this.nextStep(), 2000);
        }
    },

    goToDashboard() {
        this.showAlert('Redirecting to dashboard...', 'success');
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 2000);
    },

    // Password Toggle
    togglePassword(inputId) {
        const input = document.getElementById(inputId);
        if (!input) return;

        const button = input.parentElement.querySelector('.password-toggle');
        if (input.type === 'password') {
            input.type = 'text';
            if (button) button.textContent = '🙈';
        } else {
            input.type = 'password';
            if (button) button.textContent = '👁️';
        }
    },

    // Utilities
    showAlert(message, type = 'info') {
        const container = document.getElementById('alertContainer') ||
                         document.querySelector('.slide.active .slide-content') ||
                         document.body;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        alert.style.cssText = `
            padding: 12px 20px;
            margin: 10px 0;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            animation: slideIn 0.3s ease;
        `;

        // Style based on type
        const styles = {
            success: { background: '#10b981', color: 'white' },
            error: { background: '#ef4444', color: 'white' },
            warning: { background: '#f59e0b', color: 'white' },
            info: { background: '#3b82f6', color: 'white' }
        };

        Object.assign(alert.style, styles[type] || styles.info);

        // Remove existing alerts
        container.querySelectorAll('.alert').forEach(a => a.remove());

        // Insert alert
        if (container === document.body) {
            alert.style.position = 'fixed';
            alert.style.top = '20px';
            alert.style.right = '20px';
            alert.style.zIndex = '10000';
        } else {
            container.insertBefore(alert, container.firstChild);
        }

        container.appendChild(alert);

        // Auto-remove after 5 seconds
        setTimeout(() => alert.remove(), 5000);
    },

    // Session Management
    async checkAuth() {
        try {
            const { data: { session } } = await this.supabase.auth.getSession();

            if (session) {
                this.userData.userId = session.user.id;
                this.userData.email = session.user.email;
                return true;
            }
            return false;
        } catch (error) {
            console.error('Auth check error:', error);
            return false;
        }
    },

    async logout() {
        try {
            await this.supabase.auth.signOut();
            window.location.href = '/';
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', async () => {
    App.updateProgress();
    App.updateNavigation();

    // Check authentication state
    const isAuthenticated = await App.checkAuth();
    if (isAuthenticated) {
        console.log('User is authenticated:', App.userData.email);
    }

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;

        if (e.key === 'ArrowRight') {
            App.nextStep();
        } else if (e.key === 'ArrowLeft') {
            App.prevStep();
        }
    });

    console.log('✅ ZmartyBrain Onboarding System Ready');
    console.log('📊 Supabase Connected:', !!window.supabaseClient);
});

// Export App globally
window.App = App;
