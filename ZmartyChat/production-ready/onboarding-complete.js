// ZmartyChat Complete Onboarding System - PRODUCTION READY
// Combines all working features: navigation, email detection, registration

// ========================================
// CORE CONFIGURATION
// ========================================
window.currentSlide = 1;
const totalSlides = 8;
let touchStartX = 0;
let touchEndX = 0;
let selectedTier = null;
window.emailCheckTimeout = null;

// ========================================
// NAVIGATION FUNCTIONS - IMMEDIATELY AVAILABLE
// ========================================
window.nextSlide = function() {
    console.log('nextSlide called, current:', window.currentSlide);

    // Special handling for slide 4 (registration)
    if (window.currentSlide === 4) {
        const emailInput = document.getElementById('register-email');
        if (!emailInput || !emailInput.value.trim()) {
            showError('Please enter your email to continue');
            return;
        }
        // If email is entered, trigger registration
        const registerBtn = document.getElementById('email-continue-btn');
        if (registerBtn && registerBtn.style.display !== 'none') {
            registerBtn.click();
            return;
        }
    }

    if (window.currentSlide < totalSlides) {
        goToSlide(window.currentSlide + 1);
    }
};

window.previousSlide = function() {
    console.log('previousSlide called, current:', window.currentSlide);
    if (window.currentSlide > 1) {
        goToSlide(window.currentSlide - 1);
    }
};

window.goToSlide = function(slideNumber) {
    console.log('goToSlide called:', slideNumber);
    if (slideNumber < 1 || slideNumber > totalSlides) return;

    // Hide all slides
    document.querySelectorAll('.slide').forEach(slide => {
        slide.classList.remove('active');
        slide.style.opacity = '0';
        slide.style.transform = 'translateX(100%)';
    });

    // Show target slide
    const targetSlide = document.getElementById(`slide-${slideNumber}`);
    if (targetSlide) {
        targetSlide.classList.add('active');
        targetSlide.style.opacity = '1';
        targetSlide.style.transform = 'translateX(0)';
        targetSlide.style.display = 'flex';

        window.currentSlide = slideNumber;
        updateDots();
        updateNextButton();
    }
};

// ========================================
// EMAIL DETECTION & PROGRESSIVE REVEAL
// ========================================
window.checkEmailExists = async function() {
    const emailInput = document.getElementById('register-email');
    if (!emailInput) return;

    // Don't check if input is disabled (after registration)
    if (emailInput.disabled) return;

    const email = emailInput.value.trim().toLowerCase();
    const passwordField = document.getElementById('register-password');
    const confirmField = document.getElementById('confirm-password');
    const registerBtn = document.getElementById('email-continue-btn');

    // Show password field if email has content
    if (email.length > 0 && email.includes('@')) {
        if (passwordField) {
            passwordField.style.display = 'block';
            passwordField.style.visibility = 'visible';
            passwordField.style.opacity = '1';
        }

        // Clear previous timeout
        if (window.emailCheckTimeout) clearTimeout(window.emailCheckTimeout);

        // Debounce email check
        window.emailCheckTimeout = setTimeout(async () => {
            try {
                console.log('Checking if email exists:', email);

                // Use ZmartyBrain client for user management
                const supabaseClient = window.brainClient || window.supabase;

                // Try to sign in with dummy password to check if user exists
                const { error } = await supabaseClient.auth.signInWithPassword({
                    email: email,
                    password: 'dummy_check_123456789'
                });

                console.log('Error type:', error?.message || 'No error');

                // Check different error types to determine if user exists
                const userExists = error && (
                    error.message.includes('Invalid login credentials') ||
                    error.message.includes('Email not confirmed') ||
                    error.message.includes('Wrong email or password')
                );

                if (userExists) {
                    // User exists - show login mode
                    console.log('User exists - showing login mode');

                    passwordField.placeholder = 'Enter your password to login';

                    // Hide confirm password for login
                    if (confirmField) {
                        confirmField.style.display = 'none';
                    }

                    // Show login button
                    if (registerBtn) {
                        registerBtn.style.display = 'flex';
                        registerBtn.textContent = '🔐 Login';
                        registerBtn.onclick = function() { quickLogin(); };
                    }

                    // Add forgot password link
                    let forgotLink = document.getElementById('forgot-password-link');
                    if (!forgotLink && registerBtn) {
                        forgotLink = document.createElement('a');
                        forgotLink.id = 'forgot-password-link';
                        forgotLink.href = '#';
                        forgotLink.style.cssText = 'color: #4d94ff; font-size: 12px; margin-top: 8px; text-decoration: underline;';
                        forgotLink.textContent = 'Forgot password?';
                        forgotLink.onclick = function(e) {
                            e.preventDefault();
                            sendPasswordReset();
                        };
                        registerBtn.parentNode.appendChild(forgotLink);
                    }

                } else {
                    // New user OR other error - show registration mode
                    console.log('New user or email error - registration mode');

                    passwordField.placeholder = 'Create password (min 8 characters)';

                    // Show confirm password for registration
                    if (confirmField) {
                        confirmField.style.display = 'block';
                    }

                    // Reset button to register mode
                    if (registerBtn) {
                        registerBtn.textContent = '✉️ Register';
                        registerBtn.onclick = function() { continueWithEmail(); };
                    }

                    // Remove forgot password link if exists
                    const forgotLink = document.getElementById('forgot-password-link');
                    if (forgotLink) forgotLink.remove();
                }
            } catch (error) {
                console.error('Error checking email:', error);
            }
        }, 500); // 500ms debounce
    } else {
        // Hide fields if email is empty
        if (passwordField) passwordField.style.display = 'none';
        if (confirmField) confirmField.style.display = 'none';
        if (registerBtn) registerBtn.style.display = 'none';
    }
};

window.showPasswordField = function() {
    const emailInput = document.getElementById('register-email');
    const passwordField = document.getElementById('register-password');

    if (emailInput && emailInput.value.length > 0 && passwordField) {
        passwordField.style.display = 'block';
        passwordField.style.visibility = 'visible';
        passwordField.style.opacity = '1';
    }
};

window.showConfirmPasswordField = function() {
    const passwordField = document.getElementById('register-password');
    const confirmField = document.getElementById('confirm-password');

    if (passwordField && confirmField && passwordField.value.length > 0) {
        confirmField.style.display = 'block';
        confirmField.style.visibility = 'visible';
        confirmField.style.opacity = '1';
    }
};

window.checkIfCanRegister = function() {
    const password = document.getElementById('register-password')?.value || '';
    const confirmPassword = document.getElementById('confirm-password')?.value || '';
    const registerBtn = document.getElementById('email-continue-btn');

    if (password.length >= 8 && password === confirmPassword && registerBtn) {
        registerBtn.style.display = 'flex';
        registerBtn.style.visibility = 'visible';
        registerBtn.style.opacity = '1';
    }
};

// ========================================
// REGISTRATION & LOGIN FUNCTIONS
// ========================================
window.continueWithEmail = async function() {
    console.log('Registration initiated');

    const emailInput = document.getElementById('register-email');
    const passwordInput = document.getElementById('register-password');
    const email = emailInput?.value.trim().toLowerCase();
    const password = passwordInput?.value;

    if (!email || !password) {
        showError('Please fill in all fields');
        return;
    }

    try {
        const supabaseClient = window.brainClient || window.supabase;

        const { data, error } = await supabaseClient.auth.signUp({
            email: email,
            password: password,
            options: {
                emailRedirectTo: window.location.origin + '/dashboard.html'
            }
        });

        if (error) throw error;

        console.log('Registration successful:', data);
        localStorage.setItem('zmarty_verification_email', email);

        // Disable email input to prevent re-checking
        if (emailInput) {
            emailInput.disabled = true;
            emailInput.style.opacity = '0.6';
        }

        // Clear the email check timeout to prevent it from running
        if (window.emailCheckTimeout) {
            clearTimeout(window.emailCheckTimeout);
        }

        goToSlide(5); // Go to verification slide
        showError('✅ Check your email for verification link!', 'success');

    } catch (error) {
        console.error('Registration error:', error);
        showError(error.message || 'Registration failed');
    }
};

window.simpleRegister = function() {
    return continueWithEmail();
};

window.quickLogin = async function() {
    console.log('Login initiated');

    const emailInput = document.getElementById('register-email');
    const passwordInput = document.getElementById('register-password');
    const email = emailInput?.value.trim().toLowerCase();
    const password = passwordInput?.value;

    if (!email || !password) {
        showError('Please enter email and password');
        return;
    }

    try {
        const supabaseClient = window.brainClient || window.supabase;

        const { data, error } = await supabaseClient.auth.signInWithPassword({
            email: email,
            password: password
        });

        if (error) throw error;

        console.log('Login successful', data);

        // Check if user is verified
        if (data.user && !data.user.email_confirmed_at) {
            console.log('User not verified, going to verification slide');
            goToSlide(5); // Go to verification slide
            showError('Please verify your email first', 'warning');
        } else {
            console.log('User verified, redirecting to dashboard');
            // Force immediate redirect without any delays
            setTimeout(() => {
                window.location.replace('dashboard.html');
            }, 100);
        }

    } catch (error) {
        console.error('Login error:', error);

        // If user not confirmed, show specific message
        if (error.message?.includes('Email not confirmed')) {
            console.log('Email not confirmed error, going to verification slide');
            goToSlide(5); // Go to verification slide
            showError('Please check your email to verify your account', 'warning');
        } else if (error.message?.includes('Invalid login credentials')) {
            showError('Wrong password. Please try again or reset your password.');
        } else {
            showError(error.message || 'Login failed');
        }
    }
};

window.sendPasswordReset = async function() {
    const emailInput = document.getElementById('register-email');
    const email = emailInput?.value.trim();

    if (!email) {
        showError('Please enter your email address');
        return;
    }

    try {
        const supabaseClient = window.brainClient || window.supabase;

        const { error } = await supabaseClient.auth.resetPasswordForEmail(email, {
            redirectTo: window.location.origin + '/reset-password.html'
        });

        if (error) throw error;

        showError('✅ Password reset link sent to your email!', 'success');

    } catch (error) {
        console.error('Password reset error:', error);
        showError(error.message || 'Failed to send reset email');
    }
};

// ========================================
// UI HELPER FUNCTIONS
// ========================================
function updateDots() {
    document.querySelectorAll('.navigation-dots .dot').forEach((dot, index) => {
        if (index + 1 === window.currentSlide) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}

function updateNextButton() {
    const nextBtn = document.querySelector('.next-btn');
    const nextText = document.getElementById('next-text');
    if (nextBtn && nextText) {
        if (window.currentSlide === totalSlides) {
            nextText.textContent = 'Finish';
        } else {
            nextText.textContent = 'Next';
        }
    }
}

window.showError = function(message, type = 'error') {
    console.log(`[${type}] ${message}`);

    // Remove existing toast
    const existingToast = document.querySelector('.error-toast');
    if (existingToast) existingToast.remove();

    // Create new toast
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#00c896' : '#ff4757'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
};

// ========================================
// TIER SELECTION
// ========================================
window.selectTier = function(tier) {
    selectedTier = tier;

    // Update UI
    document.querySelectorAll('.tier-card').forEach(card => {
        card.classList.remove('selected');
    });

    const selectedCard = document.querySelector(`.tier-card[onclick*="${tier}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }

    // Store tier
    localStorage.setItem('zmarty_selected_tier', tier);

    // Auto-advance after selection
    setTimeout(() => goToSlide(7), 500);
};

// ========================================
// PROFILE COMPLETION
// ========================================
window.completeProfile = async function() {
    const name = document.getElementById('profile-name')?.value.trim();
    const country = document.getElementById('profile-country')?.value;

    if (!name || !country) {
        showError('Please fill in all fields');
        return;
    }

    try {
        localStorage.setItem('zmarty_user_name', name);
        localStorage.setItem('zmarty_user_country', country);

        // Navigate to dashboard
        window.location.href = 'dashboard.html';

    } catch (error) {
        console.error('Profile error:', error);
        showError('Failed to save profile');
    }
};

// ========================================
// INITIALIZATION
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Onboarding system initialized');

    // Set up arrow key navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            window.nextSlide();
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            window.previousSlide();
        }
    });

    // Set up dots navigation
    document.querySelectorAll('.navigation-dots .dot').forEach((dot, index) => {
        dot.addEventListener('click', () => window.goToSlide(index + 1));
    });

    // Set up touch/swipe navigation
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        if (touchEndX < touchStartX - swipeThreshold) {
            window.nextSlide();
        } else if (touchEndX > touchStartX + swipeThreshold) {
            window.previousSlide();
        }
    }

    // Initialize first slide
    window.goToSlide(1);

    // Check for returning user
    checkReturningUser();
});

// Check if user is returning from email verification
async function checkReturningUser() {
    if (window.location.hash && window.location.hash.includes('access_token')) {
        console.log('User returning from email verification');

        // Clear the hash
        window.history.replaceState({}, document.title, window.location.pathname);

        // Mark as verified
        localStorage.setItem('zmarty_email_verified', 'true');

        // Go to tier selection
        goToSlide(6);
        showError('✅ Email verified! Choose your plan.', 'success');
    }
}

// ========================================
// EXPORT ALL FUNCTIONS
// ========================================
window.onboardingFunctions = {
    nextSlide: window.nextSlide,
    previousSlide: window.previousSlide,
    goToSlide: window.goToSlide,
    checkEmailExists: window.checkEmailExists,
    showPasswordField: window.showPasswordField,
    showConfirmPasswordField: window.showConfirmPasswordField,
    checkIfCanRegister: window.checkIfCanRegister,
    simpleRegister: window.simpleRegister,
    continueWithEmail: window.continueWithEmail,
    quickLogin: window.quickLogin,
    sendPasswordReset: window.sendPasswordReset,
    selectTier: window.selectTier,
    completeProfile: window.completeProfile,
    showError: window.showError
};

console.log('✅ All functions loaded:', Object.keys(window.onboardingFunctions));