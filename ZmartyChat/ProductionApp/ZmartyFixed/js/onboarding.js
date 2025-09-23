// Zmarty Onboarding System - Main JavaScript
// Version: 2.0.0
// Production Ready

// Global State Management
const OnboardingState = {
    currentSlide: 1,
    totalSlides: 9,
    userData: {
        email: '',
        password: '',
        fullName: '',
        experience: '',
        tradingPairs: [],
        riskTolerance: 3,
        notifications: [],
        selectedTier: 'free',
        source: 'organic',
        device: null,
        sessionId: null,
        startTime: Date.now()
    },
    metrics: {
        slideTimings: {},
        interactions: [],
        errors: []
    },
    config: {
        otpLength: 6,
        resendCooldown: 60,
        passwordMinLength: 8,
        sessionTimeout: 30 * 60 * 1000, // 30 minutes
        maxLoginAttempts: 5
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeOnboarding();
});

// Main Initialization
function initializeOnboarding() {
    // Generate session ID
    OnboardingState.userData.sessionId = generateSessionId();
    
    // Detect device type
    OnboardingState.userData.device = detectDevice();
    
    // Check for existing session
    checkExistingSession();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize OTP inputs
    setupOTPInputs();
    
    // Start metrics tracking
    startMetricsTracking();
    
    // Hide loading screen
    setTimeout(() => {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        }
    }, 1000);
    
    // Check URL parameters
    checkURLParams();
}

// Session Management
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function detectDevice() {
    const ua = navigator.userAgent;
    if (/mobile/i.test(ua)) return 'mobile';
    if (/tablet/i.test(ua)) return 'tablet';
    return 'desktop';
}

function checkExistingSession() {
    const session = localStorage.getItem('zmarty_session');
    if (session) {
        try {
            const sessionData = JSON.parse(session);
            if (Date.now() - sessionData.timestamp < OnboardingState.config.sessionTimeout) {
                // Resume session
                OnboardingState.userData = { ...OnboardingState.userData, ...sessionData.userData };
                if (sessionData.currentSlide) {
                    goToSlide(sessionData.currentSlide);
                }
            }
        } catch (e) {
            console.error('Failed to restore session:', e);
        }
    }
}

function saveSession() {
    const sessionData = {
        userData: OnboardingState.userData,
        currentSlide: OnboardingState.currentSlide,
        timestamp: Date.now()
    };
    localStorage.setItem('zmarty_session', JSON.stringify(sessionData));
}

// URL Parameters Handling
async function checkURLParams() {
    const params = new URLSearchParams(window.location.search);
    const hash = window.location.hash;

    // Check for OAuth callback (access_token in hash)
    if (hash && hash.includes('access_token')) {
        console.log('OAuth callback detected');

        // Parse the hash parameters
        const hashParams = new URLSearchParams(hash.substring(1));
        const accessToken = hashParams.get('access_token');
        const refreshToken = hashParams.get('refresh_token');

        if (accessToken) {
            console.log('Found access token, setting session...');

            try {
                // Manually set the session with the tokens from the URL
                const { data, error } = await supabase.auth.setSession({
                    access_token: accessToken,
                    refresh_token: refreshToken
                });

                if (error) {
                    console.error('Error setting session:', error);
                    throw error;
                }

                // Get the session to verify it worked
                const { data: { session }, error: sessionError } = await supabase.auth.getSession();

                if (sessionError) {
                    console.error('Session error:', sessionError);
                    throw sessionError;
                }

                if (session && session.user) {
                    console.log('OAuth login successful!', session.user.email);
                    trackEvent('oauth_login_success', {
                        provider: session.user?.app_metadata?.provider || 'unknown',
                        email: session.user?.email
                    });

                    // Store user data
                    OnboardingState.userData.email = session.user.email;
                    OnboardingState.userData.authProvider = session.user.app_metadata?.provider;
                    OnboardingState.userData.userId = session.user.id;
                    OnboardingState.isAuthenticated = true;

                    // Clear the hash from URL first
                    window.history.replaceState(null, '', window.location.pathname);

                    // Redirect to profile setup
                    setTimeout(() => {
                        console.log('Redirecting to profile setup...');
                        goToSlide(6); // Go to profile setup slide
                    }, 500);
                } else {
                    console.error('No session after setting tokens');
                }
            } catch (error) {
                console.error('OAuth callback error:', error);
                trackError('oauth_callback_failed', error);
                alert('Authentication failed. Please try again.');
            }
        }
    }

    // Track referral source
    if (params.get('ref')) {
        OnboardingState.userData.source = params.get('ref');
    }

    // Handle deep links
    if (params.get('action') === 'verify') {
        goToSlide(5);
    } else if (params.get('action') === 'login') {
        showLogin();
    }

    // Pre-fill email if provided
    if (params.get('email')) {
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.value = params.get('email');
        }
    }
}

// Navigation Functions
function nextSlide() {
    if (OnboardingState.currentSlide < OnboardingState.totalSlides) {
        trackSlideComplete(OnboardingState.currentSlide);
        goToSlide(OnboardingState.currentSlide + 1);
    }
}

function previousSlide() {
    if (OnboardingState.currentSlide > 1) {
        goToSlide(OnboardingState.currentSlide - 1);
    }
}

function goToSlide(slideNumber) {
    // Track slide timing
    if (OnboardingState.metrics.slideTimings[OnboardingState.currentSlide]) {
        OnboardingState.metrics.slideTimings[OnboardingState.currentSlide].endTime = Date.now();
    }
    
    // Hide all slides
    document.querySelectorAll('.slide').forEach(slide => {
        slide.classList.remove('active');
    });
    
    // Show target slide
    const targetSlide = document.getElementById(`slide-${slideNumber}`);
    if (targetSlide) {
        targetSlide.classList.add('active');
        OnboardingState.currentSlide = slideNumber;
        
        // Update progress bar
        updateProgressBar();
        
        // Start timing for new slide
        OnboardingState.metrics.slideTimings[slideNumber] = {
            startTime: Date.now()
        };
        
        // Track slide view
        trackEvent('slide_viewed', {
            slide_number: slideNumber,
            slide_name: getSlideName()
        });
        
        // Save session
        saveSession();
        
        // Slide-specific initialization
        initializeSlide(slideNumber);
    }
}

function updateProgressBar() {
    const progress = (OnboardingState.currentSlide / OnboardingState.totalSlides) * 100;
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        progressFill.style.width = `${progress}%`;
    }
}

function getSlideName() {
    const slideNames = {
        1: 'welcome',
        2: 'ai_showcase',
        3: 'features',
        4: 'registration',
        5: 'verification',
        6: 'tier_selection',
        7: 'profile_setup',
        8: 'login',
        9: 'success'
    };
    return slideNames[OnboardingState.currentSlide] || 'unknown';
}

// Slide Initialization
function initializeSlide(slideNumber) {
    switch (slideNumber) {
        case 4:
            setupPasswordStrengthIndicator();
            break;
        case 5:
            startResendTimer();
            document.getElementById('user-email').textContent = OnboardingState.userData.email;
            break;
        case 6:
            setupTierCards();
            break;
        case 7:
            setupProfileForm();
            break;
    }
}

// Registration Handler
async function handleRegistration(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = form.email.value.trim().toLowerCase();
    const password = form.password.value;
    const terms = form.terms.checked;
    
    // Clear previous errors
    clearErrors();
    
    // Validate inputs
    if (!validateEmail(email)) {
        showError('email-error', 'Please enter a valid email address');
        return;
    }
    
    if (!validatePassword(password)) {
        showError('password-error', 'Password must be at least 8 characters with uppercase, number, and special character');
        return;
    }
    
    if (!terms) {
        alert('Please accept the terms and conditions');
        return;
    }
    
    // Show loading state
    const button = document.getElementById('register-btn');
    const originalText = button.innerHTML;
    button.innerHTML = 'Creating Account...';
    button.disabled = true;
    
    try {
        // Track registration attempt
        trackEvent('registration_started', { email: email });
        
        // Call Supabase auth
        const { data, error } = await supabase.auth.signUp({
            email: email,
            password: password,
            options: {
                emailRedirectTo: `${window.location.origin}/verify`,
                data: {
                    source: OnboardingState.userData.source,
                    device: OnboardingState.userData.device,
                    session_id: OnboardingState.userData.sessionId
                }
            }
        });
        
        if (error) {
            throw error;
        }

        // Check if user needs email verification
        if (data.user && !data.user.email_confirmed_at) {
            // Save user data
            OnboardingState.userData.email = email;
            OnboardingState.userData.password = password; // Note: In production, never store passwords

            // Track successful registration
            trackEvent('registration_completed', { email: email });

            // Move to verification slide
            nextSlide();
        } else if (data.user && data.user.email_confirmed_at) {
            // User is already verified, skip to dashboard
            trackEvent('auto_login_verified_user', { email: email });
            alert('Your account is already verified! Redirecting to dashboard...');
            window.location.href = '/dashboard';
        }
        
    } catch (error) {
        console.error('Registration error:', error);
        console.error('Error message:', error.message);
        console.error('Error details:', error);

        // Track error
        trackError('registration_failed', error);

        // Show user-friendly error with actual error for debugging
        if (error.message.includes('already registered') || error.message.includes('User already registered')) {
            showError('email-error', 'This email is already registered. Please sign in instead.');
            // DO NOT move to next slide for existing users
            setTimeout(() => {
                if (confirm('Would you like to sign in with this email?')) {
                    showLogin();
                }
            }, 1000);
        } else if (error.message.includes('Email rate limit exceeded')) {
            showError('email-error', 'Too many attempts. Please try again in a few minutes.');
        } else {
            // Show actual error for debugging
            showError('email-error', 'Registration failed: ' + (error.message || 'Unknown error. Check console.'));
            console.error('Full error object:', error);
        }
    } finally {
        // Restore button state
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Login Handler
async function handleLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = form.email.value.trim().toLowerCase();
    const password = form.password.value;
    const remember = document.getElementById('remember').checked;
    
    // Clear previous errors
    clearErrors();
    
    // Show loading state
    const button = document.getElementById('login-btn');
    const originalText = button.innerHTML;
    button.innerHTML = 'Signing In...';
    button.disabled = true;
    
    try {
        // Track login attempt
        trackEvent('login_attempted', { email: email });
        
        // Call Supabase auth
        const { data, error } = await supabase.auth.signInWithPassword({
            email: email,
            password: password
        });
        
        if (error) {
            throw error;
        }
        
        // Check email verification
        if (!data.user.email_confirmed_at) {
            // Move to verification slide
            OnboardingState.userData.email = email;
            goToSlide(5);
            return;
        }
        
        // Save session if remember me is checked
        if (remember) {
            localStorage.setItem('zmarty_remember', email);
        }
        
        // Track successful login
        trackEvent('login_successful', { email: email });
        
        // Check if profile is complete
        const profile = await checkProfileCompletion(data.user.id);
        
        if (!profile.isComplete) {
            // Move to profile setup
            goToSlide(7);
        } else {
            // Move to success slide
            goToSlide(9);
        }
        
    } catch (error) {
        console.error('Login error:', error);
        
        // Track error
        trackError('login_failed', error);
        
        // Show user-friendly error
        if (error.message.includes('Invalid login credentials')) {
            alert('Invalid email or password. Please try again.');
        } else if (error.message.includes('Email not confirmed')) {
            OnboardingState.userData.email = email;
            goToSlide(5);
        } else {
            alert('Login failed. Please try again.');
        }
    } finally {
        // Restore button state
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Enhanced Social Authentication
async function handleSocialAuth(provider) {
    console.log(`Starting ${provider} OAuth authentication...`);
    
    try {
        // Check if Supabase is properly initialized
        if (!window.supabase) {
            throw new Error('Supabase client not initialized');
        }

        // Check if already logged in
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
            console.log('Already logged in as', session.user.email);
            goToSlide(6); // Go to tier selection
            return;
        }

        // Track OAuth attempt
        trackEvent('social_auth_started', { provider: provider });

        // Show loading state - get the button that was clicked
        const button = event ? event.target : document.querySelector(`[onclick*="${provider}"]`);
        let originalText = '';
        
        if (button) {
            originalText = button.innerHTML;
            button.innerHTML = `<span style="display: inline-block; width: 20px; height: 20px; border: 2px solid #fff; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px;"></span>Connecting...`;
            button.disabled = true;
        }

        // Configure OAuth options based on provider
        const oauthOptions = {
            redirectTo: `${window.location.origin}/auth/callback`,
            queryParams: {
                access_type: 'offline',
                prompt: 'consent'
            }
        };

        // Provider-specific scopes
        switch (provider) {
            case 'google':
                oauthOptions.scopes = 'email profile';
                break;
            case 'facebook':
                oauthOptions.scopes = 'email public_profile';
                break;
            case 'apple':
                oauthOptions.scopes = 'email name';
                break;
        }

        console.log('OAuth options:', oauthOptions);
        console.log('Initiating OAuth for provider:', provider);

        // Initiate OAuth flow
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: provider,
            options: oauthOptions
        });
        
        if (error) {
            console.error('OAuth error:', error);
            throw error;
        }
        
        console.log('OAuth redirect initiated successfully for', provider);
        trackEvent('social_auth_redirecting', { provider: provider });
        
        // The user will be redirected to the OAuth provider
        // The callback will be handled by auth/callback/index.html
        
    } catch (error) {
        console.error(`${provider} auth error:`, error);
        trackError('social_auth_failed', error);
        
        // Restore button state
        const button = event ? event.target : document.querySelector(`[onclick*="${provider}"]`);
        if (button && originalText) {
            button.innerHTML = originalText;
            button.disabled = false;
        }
        
        // Show user-friendly error message
        let errorMessage = `${provider.charAt(0).toUpperCase() + provider.slice(1)} authentication failed. Please try again.`;
        
        if (error.message.includes('not configured') || error.message.includes('not enabled')) {
            errorMessage = `${provider.charAt(0).toUpperCase() + provider.slice(1)} authentication is not properly configured. Please try email registration.`;
        } else if (error.message.includes('network')) {
            errorMessage = 'Network error. Please check your connection and try again.';
        } else if (error.message.includes('popup')) {
            errorMessage = 'Popup blocked. Please allow popups and try again.';
        }
        
        console.error('Showing error:', errorMessage);
        showNotification(errorMessage, 'error');
    }
}

// Email Verification
async function verifyOTP() {
    const otpInputs = document.querySelectorAll('.otp-input');
    const otp = Array.from(otpInputs).map(input => input.value).join('');
    
    if (otp.length !== OnboardingState.config.otpLength) {
        alert('Please enter all 6 digits');
        return;
    }
    
    const button = document.getElementById('verify-btn');
    const originalText = button.innerHTML;
    button.innerHTML = 'Verifying...';
    button.disabled = true;
    
    try {
        trackEvent('otp_verification_started', { email: OnboardingState.userData.email });
        
        const { data, error } = await supabase.auth.verifyOtp({
            email: OnboardingState.userData.email,
            token: otp,
            type: 'signup'
        });
        
        if (error) {
            throw error;
        }
        
        trackEvent('otp_verification_successful', { email: OnboardingState.userData.email });
        
        // Move to tier selection
        nextSlide();
        
    } catch (error) {
        console.error('Verification error:', error);
        trackError('otp_verification_failed', error);
        
        if (error.message.includes('expired')) {
            alert('Verification code expired. Please request a new one.');
        } else if (error.message.includes('invalid')) {
            alert('Invalid verification code. Please try again.');
        } else {
            alert('Verification failed. Please try again.');
        }
        
        // Clear OTP inputs
        otpInputs.forEach(input => input.value = '');
        otpInputs[0].focus();
        
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Resend OTP
async function resendOTP() {
    const button = document.getElementById('resend-btn');

    if (button.disabled) return;

    try {
        trackEvent('otp_resend_requested', { email: OnboardingState.userData.email });

        const { error } = await supabase.auth.resend({
            type: 'signup',
            email: OnboardingState.userData.email
        });

        if (error) {
            throw error;
        }

        alert('New verification code sent! Check your email.');
        trackEvent('otp_resend_successful', { email: OnboardingState.userData.email });

        // Start cooldown timer
        startResendTimer();

    } catch (error) {
        console.error('Resend error:', error);
        trackError('otp_resend_failed', error);
        alert('Failed to resend code. Please try again.');
    }
}

// Cancel verification and go back to registration/login
function cancelVerification() {
    trackEvent('verification_cancelled', { email: OnboardingState.userData.email });

    // Clear any OTP inputs
    const otpInputs = document.querySelectorAll('.otp-input');
    otpInputs.forEach(input => input.value = '');

    // Go back to registration slide (slide 4)
    goToSlide(4);

    // Show a message
    setTimeout(() => {
        if (confirm('Would you like to try with a different email?')) {
            // Clear the email field for new attempt
            const emailInput = document.getElementById('email');
            if (emailInput) emailInput.value = '';
        }
    }, 500);
}

// Tier Selection
function selectTier(tierName) {
    // Remove previous selection
    document.querySelectorAll('.tier-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to clicked tier
    event.currentTarget.classList.add('selected');
    
    // Update state
    OnboardingState.userData.selectedTier = tierName;
    
    // Update button text based on tier
    const button = document.getElementById('tier-continue-btn');
    if (tierName === 'free') {
        button.innerHTML = 'Start Free Forever <span>→</span>';
    } else {
        button.innerHTML = 'Start 14-Day Free Trial <span>→</span>';
    }
    
    trackEvent('tier_selected', { 
        tier: tierName,
        price: getTierPrice(tierName)
    });
}

function confirmTierSelection() {
    if (!OnboardingState.userData.selectedTier) {
        alert('Please select a plan to continue');
        return;
    }
    
    trackEvent('tier_confirmed', { 
        tier: OnboardingState.userData.selectedTier 
    });
    
    // Save tier selection to database
    saveTierSelection();
    
    // Move to profile setup
    nextSlide();
}

async function saveTierSelection() {
    try {
        const { data: { user } } = await supabase.auth.getUser();
        
        if (user) {
            const { error } = await supabase
                .from('user_subscriptions')
                .insert({
                    user_id: user.id,
                    tier: OnboardingState.userData.selectedTier,
                    status: 'trial',
                    trial_ends_at: calculateTrialEndDate(),
                    created_at: new Date().toISOString()
                });
            
            if (error) {
                console.error('Failed to save tier:', error);
            }
        }
    } catch (error) {
        console.error('Save tier error:', error);
    }
}

// Profile Setup
async function saveProfile(event) {
    event.preventDefault();

    const form = event.target;
    const fullName = form.fullname.value.trim();
    const country = form.country ? form.country.value : '';

    // Validate required fields
    if (!fullName || !country) {
        alert('Please fill in all required fields');
        return;
    }

    // Update state
    OnboardingState.userData.fullName = fullName;
    OnboardingState.userData.country = country;

    const button = event.target.querySelector('button[type="submit"]');
    const originalText = button.innerHTML;
    button.innerHTML = 'Saving...';
    button.disabled = true;

    try {
        // Save profile to database
        const { data: { user } } = await supabase.auth.getUser();

        if (user) {
            // Update zmartychat_users table
            const { error } = await supabase
                .from('zmartychat_users')
                .update({
                    full_name: fullName,
                    country: country,
                    onboarding_completed: true,
                    updated_at: new Date().toISOString()
                })
                .eq('auth_id', user.id);

            if (error) {
                console.error('Database error:', error);
                // Try alternative approach - might be in different table
                const { error: altError } = await supabase
                    .from('user_profiles')
                    .upsert({
                        user_id: user.id,
                        full_name: fullName,
                        country: country,
                        updated_at: new Date().toISOString()
                    });

                if (altError) {
                    throw altError;
                }
            }
        }

        trackEvent('profile_completed', {
            country: country,
            has_name: !!fullName
        });

        // Move to success slide
        goToSlide(9);

    } catch (error) {
        console.error('Profile save error:', error);
        trackError('profile_save_failed', error);
        alert('Failed to save profile. Please try again.');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

function skipProfile() {
    trackEvent('profile_skipped');
    goToSlide(9);
}

// Helper Functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    const hasMinLength = password.length >= OnboardingState.config.passwordMinLength;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[^A-Za-z0-9]/.test(password);
    
    return hasMinLength && hasUpperCase && hasLowerCase && hasNumber && hasSpecialChar;
}

function setupPasswordStrengthIndicator() {
    const passwordInput = document.getElementById('password');
    const strengthIndicator = document.getElementById('password-strength');
    
    if (!passwordInput || !strengthIndicator) return;
    
    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        const strength = calculatePasswordStrength(password);
        
        strengthIndicator.className = 'password-strength-fill';
        
        if (strength < 3) {
            strengthIndicator.classList.add('strength-weak');
        } else if (strength < 5) {
            strengthIndicator.classList.add('strength-medium');
        } else {
            strengthIndicator.classList.add('strength-strong');
        }
    });
}

function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    
    return strength;
}

function setupOTPInputs() {
    const otpInputs = document.querySelectorAll('.otp-input');
    
    otpInputs.forEach((input, index) => {
        // Auto-advance on input
        input.addEventListener('input', (e) => {
            if (e.target.value.length === 1) {
                if (index < otpInputs.length - 1) {
                    otpInputs[index + 1].focus();
                } else {
                    // All inputs filled, attempt verification
                    const otp = Array.from(otpInputs).map(i => i.value).join('');
                    if (otp.length === OnboardingState.config.otpLength) {
                        verifyOTP();
                    }
                }
            }
        });
        
        // Handle backspace
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                otpInputs[index - 1].focus();
            }
        });
        
        // Paste handling
        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const pastedData = e.clipboardData.getData('text').slice(0, 6);
            const digits = pastedData.split('');
            
            digits.forEach((digit, i) => {
                if (otpInputs[i] && /^\d$/.test(digit)) {
                    otpInputs[i].value = digit;
                }
            });
            
            // Focus last filled input or next empty one
            const lastFilled = digits.length - 1;
            if (otpInputs[lastFilled]) {
                otpInputs[Math.min(lastFilled + 1, otpInputs.length - 1)].focus();
            }
        });
    });
}

function startResendTimer() {
    const button = document.getElementById('resend-btn');
    const timer = document.getElementById('resend-timer');
    
    if (!button || !timer) return;
    
    let seconds = OnboardingState.config.resendCooldown;
    button.disabled = true;
    
    const interval = setInterval(() => {
        seconds--;
        timer.textContent = `(${seconds}s)`;
        
        if (seconds <= 0) {
            clearInterval(interval);
            button.disabled = false;
            timer.textContent = '';
        }
    }, 1000);
}

function setupTierCards() {
    // Pre-select free tier
    const freeCard = document.querySelector('.tier-card');
    if (freeCard) {
        freeCard.classList.add('selected');
    }
}

function setupProfileForm() {
    // Pre-fill any saved data
    if (OnboardingState.userData.fullName) {
        document.getElementById('fullname').value = OnboardingState.userData.fullName;
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.style.display = 'block';
    }
}

function clearErrors() {
    document.querySelectorAll('.error-message').forEach(element => {
        element.textContent = '';
        element.style.display = 'none';
    });
}

function getTierPrice(tier) {
    const prices = {
        free: 0,
        starter: 19,
        pro: 49,
        enterprise: 'custom'
    };
    return prices[tier] || 0;
}

function calculateTrialEndDate() {
    const date = new Date();
    date.setDate(date.getDate() + 14);
    return date.toISOString();
}

async function checkProfileCompletion(userId) {
    try {
        const { data, error } = await supabase
            .from('user_profiles')
            .select('*')
            .eq('user_id', userId)
            .single();
        
        if (error || !data) {
            return { isComplete: false };
        }
        
        const requiredFields = ['full_name', 'experience_level'];
        const isComplete = requiredFields.every(field => data[field]);
        
        return { isComplete, profile: data };
    } catch (error) {
        console.error('Profile check error:', error);
        return { isComplete: false };
    }
}

// Navigation Functions
function showLogin() {
    goToSlide(8);
    trackEvent('show_login_form');
}

function showRegistration() {
    goToSlide(4);
    trackEvent('show_registration_form');
}

function showForgotPassword() {
    trackEvent('forgot_password_clicked');
    window.location.href = '/reset-password.html';
}

function goToDashboard() {
    trackEvent('onboarding_completed', {
        total_time: Date.now() - OnboardingState.userData.startTime,
        selected_tier: OnboardingState.userData.selectedTier
    });
    
    window.location.href = '/dashboard.html';
}

// Event Listeners Setup
function setupEventListeners() {
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            const activeSlide = document.querySelector('.slide.active');
            const primaryBtn = activeSlide?.querySelector('.btn-primary');
            if (primaryBtn) {
                primaryBtn.click();
            }
        }
    });
    
    // Prevent form resubmission on refresh
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }
}

// Analytics Tracking
function trackEvent(eventName, properties = {}) {
    const eventData = {
        event: eventName,
        timestamp: Date.now(),
        session_id: OnboardingState.userData.sessionId,
        ...properties
    };
    
    // Send to Google Analytics if available
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, eventData);
    }
    
    // Store in metrics
    OnboardingState.metrics.interactions.push(eventData);
    
    // Console log in development
    if (window.location.hostname === 'localhost') {
        console.log('Track Event:', eventName, properties);
    }
}

function trackError(errorType, error) {
    const errorData = {
        type: errorType,
        message: error.message,
        timestamp: Date.now(),
        slide: OnboardingState.currentSlide
    };
    
    OnboardingState.metrics.errors.push(errorData);
    
    // Send to error tracking service
    if (typeof Sentry !== 'undefined') {
        Sentry.captureException(error);
    }
}

function trackSlideComplete(slideNumber) {
    const timing = OnboardingState.metrics.slideTimings[slideNumber];
    if (timing && !timing.endTime) {
        timing.endTime = Date.now();
        timing.duration = timing.endTime - timing.startTime;
        
        trackEvent('slide_completed', {
            slide_number: slideNumber,
            duration: timing.duration
        });
    }
}

function startMetricsTracking() {
    // Track page visibility changes
    document.addEventListener('visibilitychange', () => {
        trackEvent('visibility_changed', {
            hidden: document.hidden
        });
    });
    
    // Track before unload
    window.addEventListener('beforeunload', () => {
        trackEvent('page_unload', {
            completed: OnboardingState.currentSlide === OnboardingState.totalSlides,
            last_slide: OnboardingState.currentSlide
        });
    });
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(n => n.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add styles if not already present
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                max-width: 400px;
                padding: 16px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                animation: slideIn 0.3s ease-out;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .notification-info {
                background: #3b82f6;
                color: white;
            }
            
            .notification-success {
                background: #10b981;
                color: white;
            }
            
            .notification-error {
                background: #ef4444;
                color: white;
            }
            
            .notification-warning {
                background: #f59e0b;
                color: white;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .notification-message {
                flex: 1;
                margin-right: 12px;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: inherit;
                font-size: 20px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 4px;
                opacity: 0.8;
            }
            
            .notification-close:hover {
                opacity: 1;
                background: rgba(255, 255, 255, 0.2);
            }
            
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @media (max-width: 480px) {
                .notification {
                    left: 20px;
                    right: 20px;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideIn 0.3s ease-out reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }
}

// OAuth callback success handler
function handleOAuthSuccess() {
    // Check for OAuth success in localStorage
    const oauthSuccess = localStorage.getItem('zmarty_oauth_success');
    if (oauthSuccess) {
        try {
            const userData = JSON.parse(oauthSuccess);
            console.log('OAuth success detected:', userData);
            
            // Store in OnboardingState
            OnboardingState.userData.email = userData.email;
            OnboardingState.userData.fullName = userData.fullName;
            OnboardingState.userData.authProvider = userData.authProvider;
            OnboardingState.userData.userId = userData.userId;
            OnboardingState.userData.isAuthenticated = true;
            
            // Show success notification
            showNotification(`Welcome ${userData.fullName || userData.email}! You're now signed in with ${userData.authProvider}.`, 'success');
            
            // Clear the success flag
            localStorage.removeItem('zmarty_oauth_success');
            
            // Go to tier selection slide
            setTimeout(() => {
                goToSlide(6);
            }, 1500);
            
            return true;
        } catch (error) {
            console.error('Error parsing OAuth success data:', error);
            localStorage.removeItem('zmarty_oauth_success');
        }
    }
    return false;
}

// Enhanced initialization
function initializeEnhancedOnboarding() {
    console.log('Initializing enhanced onboarding...');
    
    // Check for OAuth success on page load
    if (handleOAuthSuccess()) {
        return; // OAuth success handled, don't continue with normal init
    }
    
    // Check URL parameters for OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const oauthParam = urlParams.get('oauth');
    const slideParam = urlParams.get('slide');
    
    if (oauthParam === 'success' && slideParam) {
        // Handle OAuth success from URL
        const slideNumber = parseInt(slideParam);
        if (slideNumber >= 1 && slideNumber <= OnboardingState.totalSlides) {
            goToSlide(slideNumber);
        }
        
        // Clean up URL
        const cleanUrl = window.location.pathname;
        window.history.replaceState({}, document.title, cleanUrl);
    }
    
    // Add CSS for spin animation if not present
    if (!document.querySelector('#oauth-styles')) {
        const styles = document.createElement('style');
        styles.id = 'oauth-styles';
        styles.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(styles);
    }
    
    console.log('Enhanced onboarding initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEnhancedOnboarding);
} else {
    initializeEnhancedOnboarding();
}
