// ZmartyChat Onboarding - Complete Working Implementation
// All functions available immediately

// Global state
let currentSlide = 1;
const totalSlides = 7;
let userEmail = '';
let authMode = 'register'; // 'register' or 'login'
let selectedTier = null;

// Supabase configuration - Using ZmartyBrain (for user authentication)
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Navigation functions - Available immediately
window.nextSlide = function() {
    console.log('Next slide called, current:', currentSlide);

    // Validation for slide 4 (registration)
    if (currentSlide === 4) {
        const email = document.getElementById('email-input').value.trim();
        if (!email) {
            showMessage('Please enter your email to continue', 'error');
            return;
        }

        // If in registration mode, require password
        if (authMode === 'register') {
            const password = document.getElementById('password-input').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (!password || password.length < 8) {
                showMessage('Password must be at least 8 characters', 'error');
                return;
            }

            if (password !== confirmPassword) {
                showMessage('Passwords do not match', 'error');
                return;
            }
        }
    }

    // Validation for slide 7 (profile)
    if (currentSlide === 7) {
        const name = document.getElementById('full-name').value.trim();
        const country = document.getElementById('country').value;

        if (!name || !country) {
            showMessage('Please fill in all fields', 'error');
            return;
        }
    }

    if (currentSlide < totalSlides) {
        goToSlide(currentSlide + 1);
    }
};

window.previousSlide = function() {
    console.log('Previous slide called, current:', currentSlide);
    if (currentSlide > 1) {
        goToSlide(currentSlide - 1);
    }
};

window.goToSlide = function(slideNumber) {
    console.log('Going to slide:', slideNumber);

    if (slideNumber < 1 || slideNumber > totalSlides) return;

    // Hide all slides
    document.querySelectorAll('.slide').forEach(slide => {
        slide.classList.remove('active');
    });

    // Show target slide
    const targetSlide = document.getElementById(`slide-${slideNumber}`);
    if (targetSlide) {
        targetSlide.classList.add('active');
        currentSlide = slideNumber;
        updateDots();
        updateNavigationButtons();
    }
};

// Email handling
window.handleEmailInput = function() {
    const email = document.getElementById('email-input').value.trim();
    const passwordInput = document.getElementById('password-input');
    const confirmPassword = document.getElementById('confirm-password');
    const authButton = document.getElementById('auth-button');
    const forgotPassword = document.getElementById('forgot-password');

    if (email.length > 0 && email.includes('@')) {
        // Show password field
        passwordInput.style.display = 'block';

        // Check if user exists (debounced)
        clearTimeout(window.emailCheckTimeout);
        window.emailCheckTimeout = setTimeout(async () => {
            await checkEmailExists(email);
        }, 500);
    } else {
        // Hide all fields if email is invalid
        passwordInput.style.display = 'none';
        confirmPassword.style.display = 'none';
        authButton.style.display = 'none';
        forgotPassword.style.display = 'none';
    }
};

async function checkEmailExists(email) {
    try {
        console.log('Checking if email exists:', email);

        const passwordInput = document.getElementById('password-input');
        const confirmPassword = document.getElementById('confirm-password');
        const authButton = document.getElementById('auth-button');
        const forgotPassword = document.getElementById('forgot-password');

        // Try to sign in with dummy password to check if user exists
        const { error } = await supabase.auth.signInWithPassword({
            email: email,
            password: 'dummy_password_check_123'
        });

        // Check if user exists based on error type
        const userExists = error && (
            error.message.includes('Invalid login credentials') ||
            error.message.includes('Email not confirmed') ||
            error.message.includes('Wrong email or password')
        );

        if (userExists) {
            // User exists - show LOGIN mode (single password field)
            console.log('User exists - login mode');
            authMode = 'login';

            passwordInput.placeholder = 'Enter your password';
            confirmPassword.style.display = 'none';
            authButton.textContent = '🔐 Login';
            authButton.style.display = 'none'; // Hide until password entered
            forgotPassword.style.display = 'block';

        } else {
            // New user - show REGISTRATION mode (two password fields)
            console.log('New user - registration mode');
            authMode = 'register';

            passwordInput.placeholder = 'Create password (min 8 characters)';
            confirmPassword.style.display = 'none'; // Hide until first password valid
            authButton.textContent = '✉️ Register';
            authButton.style.display = 'none'; // Hide until both passwords match
            forgotPassword.style.display = 'none';
        }

    } catch (error) {
        console.error('Error checking email:', error);
    }
}

window.handlePasswordInput = function() {
    const password = document.getElementById('password-input').value;
    const confirmPassword = document.getElementById('confirm-password');
    const authButton = document.getElementById('auth-button');

    if (authMode === 'register') {
        // For registration: show confirm password when first password is 8+ chars
        if (password.length >= 8) {
            confirmPassword.style.display = 'block';
            // Don't show button yet - wait for confirm password to match
        } else {
            confirmPassword.style.display = 'none';
            authButton.style.display = 'none';
        }
    } else if (authMode === 'login') {
        // For login: show button when password has any content
        if (password.length > 0) {
            authButton.style.display = 'block';
        } else {
            authButton.style.display = 'none';
        }
    }
};

window.handleConfirmPassword = function() {
    const password = document.getElementById('password-input').value;
    const confirmPasswordValue = document.getElementById('confirm-password').value;
    const authButton = document.getElementById('auth-button');

    if (authMode === 'register') {
        // Show Register button ONLY when both passwords match and are 8+ chars
        if (password === confirmPasswordValue && password.length >= 8) {
            authButton.style.display = 'block';
        } else {
            authButton.style.display = 'none';
        }
    }
};

// Authentication
window.handleAuth = async function() {
    const email = document.getElementById('email-input').value.trim();
    const password = document.getElementById('password-input').value;

    userEmail = email;

    try {
        if (authMode === 'register') {
            console.log('Registering user:', email);

            const { data, error } = await supabase.auth.signUp({
                email: email,
                password: password,
                options: {
                    emailRedirectTo: window.location.origin + '/final-onboarding/index.html?verified=true'
                }
            });

            if (error) throw error;

            console.log('Registration successful');
            showMessage('✅ Registration successful! Check your email.', 'success');
            goToSlide(5); // Email verification slide

        } else {
            console.log('Logging in user:', email);

            const { data, error } = await supabase.auth.signInWithPassword({
                email: email,
                password: password
            });

            if (error) {
                if (error.message.includes('Email not confirmed')) {
                    showMessage('Please verify your email first', 'warning');
                    goToSlide(5);
                    return;
                }
                throw error;
            }

            console.log('Login successful');
            showMessage('✅ Login successful!', 'success');
            goToSlide(6); // Skip to plan selection
        }

    } catch (error) {
        console.error('Auth error:', error);
        showMessage(error.message || 'Authentication failed', 'error');
    }
};

window.resetPassword = async function() {
    const email = document.getElementById('email-input').value.trim();

    if (!email) {
        showMessage('Please enter your email address first', 'error');
        return;
    }

    try {
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: window.location.origin + '/final-onboarding/reset-password.html'
        });

        if (error) throw error;

        showMessage('✅ Password reset link sent to your email!', 'success');

    } catch (error) {
        console.error('Reset password error:', error);
        showMessage(error.message || 'Failed to send reset email', 'error');
    }
};

window.resendEmail = async function() {
    if (!userEmail) {
        showMessage('No email to resend to', 'error');
        return;
    }

    try {
        const { error } = await supabase.auth.resend({
            type: 'signup',
            email: userEmail,
            options: {
                emailRedirectTo: window.location.origin + '/final-onboarding/index.html?verified=true'
            }
        });

        if (error) throw error;

        showMessage('✅ Verification email sent!', 'success');

    } catch (error) {
        console.error('Resend email error:', error);
        showMessage(error.message || 'Failed to resend email', 'error');
    }
};

// OAuth Authentication
window.signInWithGoogle = async function() {
    try {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: {
                redirectTo: window.location.origin + '/final-onboarding/index.html?verified=true&oauth=google'
            }
        });

        if (error) throw error;

        showMessage('🔄 Redirecting to Google...', 'info');
    } catch (error) {
        console.error('Google auth error:', error);
        showMessage(error.message || 'Failed to sign in with Google', 'error');
    }
};

window.signInWithApple = async function() {
    try {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'apple',
            options: {
                redirectTo: window.location.origin + '/final-onboarding/index.html?verified=true&oauth=apple'
            }
        });

        if (error) throw error;

        showMessage('🔄 Redirecting to Apple...', 'info');
    } catch (error) {
        console.error('Apple auth error:', error);
        showMessage(error.message || 'Failed to sign in with Apple', 'error');
    }
};

// Plan selection
window.selectTier = function(tier) {
    console.log('Selected tier:', tier);
    selectedTier = tier;

    // Update UI
    document.querySelectorAll('.tier').forEach(t => {
        t.classList.remove('selected');
    });

    // Find and select the clicked tier
    const tiers = document.querySelectorAll('.tier');
    const tierNames = ['free', 'pro', 'enterprise'];
    const tierIndex = tierNames.indexOf(tier);

    if (tierIndex !== -1 && tiers[tierIndex]) {
        tiers[tierIndex].classList.add('selected');
    }

    // Auto-advance after 1 second
    setTimeout(() => {
        goToSlide(7);
    }, 1000);
};

// Complete onboarding
window.completeOnboarding = async function() {
    const name = document.getElementById('full-name').value.trim();
    const country = document.getElementById('country').value;

    if (!name || !country) {
        showMessage('Please fill in all fields', 'error');
        return;
    }

    try {
        // Save profile data
        localStorage.setItem('zmarty_user_name', name);
        localStorage.setItem('zmarty_user_country', country);
        localStorage.setItem('zmarty_selected_tier', selectedTier || 'free');
        localStorage.setItem('zmarty_onboarding_complete', 'true');

        showMessage('✅ Welcome to ZmartyChat!', 'success');

        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = '../dashboard.html';
        }, 2000);

    } catch (error) {
        console.error('Complete onboarding error:', error);
        showMessage('Failed to complete setup', 'error');
    }
};

// UI helpers
function updateDots() {
    document.querySelectorAll('.dot').forEach((dot, index) => {
        if (index + 1 === currentSlide) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}

function updateNavigationButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    // Update previous button
    if (prevBtn) {
        prevBtn.disabled = currentSlide === 1;
        prevBtn.style.opacity = currentSlide === 1 ? '0.5' : '1';
    }

    // Update next button text
    if (nextBtn) {
        if (currentSlide === totalSlides) {
            nextBtn.textContent = 'Complete';
            nextBtn.onclick = completeOnboarding;
        } else {
            nextBtn.textContent = 'Next →';
            nextBtn.onclick = nextSlide;
        }
    }
}

function showMessage(message, type = 'info') {
    // Remove existing message
    const existing = document.querySelector('.message-toast');
    if (existing) existing.remove();

    // Create new message
    const toast = document.createElement('div');
    toast.className = 'message-toast';
    toast.textContent = message;

    const colors = {
        success: '#00c896',
        error: '#ff4757',
        warning: '#ffa502',
        info: '#4d94ff'
    };

    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 10000;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;

    document.body.appendChild(toast);

    // Auto remove after 4 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 4000);
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight') {
        e.preventDefault();
        nextSlide();
    } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        previousSlide();
    }
});

// Check for email verification on load
document.addEventListener('DOMContentLoaded', async function() {
    console.log('✅ ZmartyChat onboarding loaded');

    // Check for OAuth or email verification
    const urlParams = new URLSearchParams(window.location.search);
    const verified = urlParams.get('verified') === 'true';
    const oauthProvider = urlParams.get('oauth');

    if (verified) {
        if (oauthProvider) {
            // OAuth login successful
            console.log(`OAuth ${oauthProvider} login successful`);
            showMessage(`✅ Signed in with ${oauthProvider}!`, 'success');
            goToSlide(6); // Go to plan selection
        } else {
            // Email verified
            console.log('Email verified - going to plan selection');
            showMessage('✅ Email verified successfully!', 'success');
            goToSlide(6);
        }

        // Clear the URL parameters
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Check if user is already logged in
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
        console.log('User already logged in:', user.email);
        userEmail = user.email;

        // Check if onboarding is complete
        const onboardingComplete = localStorage.getItem('zmarty_onboarding_complete');
        if (onboardingComplete === 'true') {
            // Redirect to dashboard
            window.location.href = '../dashboard.html';
        } else {
            // Continue onboarding from plan selection
            goToSlide(6);
        }
    }

    // Initialize
    updateDots();
    updateNavigationButtons();

    console.log('All functions loaded and ready');
});

// Add slideIn animation to CSS
const style = document.createElement('style');
style.textContent = `
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
`;
document.head.appendChild(style);