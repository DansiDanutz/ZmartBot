// PROGRESSIVE REVEAL FUNCTIONS - Must be defined immediately for HTML oninput handlers
window.showPasswordField = function() {
    console.log('=== showPasswordField TRIGGERED ===');
    const emailInput = document.getElementById('register-email');
    const passwordField = document.getElementById('register-password');

    if (!emailInput || !passwordField) {
        console.error('Cannot find elements:', {
            emailInput: !!emailInput,
            passwordField: !!passwordField
        });
        return;
    }

    console.log('Email length:', emailInput.value.length);

    if (emailInput.value.length > 0) {
        console.log('>>> SHOWING PASSWORD FIELD <<<');
        // FORCE the field to be visible with important styles
        passwordField.style.cssText = 'display: block !important; visibility: visible !important; opacity: 1 !important; margin-top: 8px !important; width: 100% !important; padding: 12px !important; background: rgba(255,255,255,0.1) !important; border: 2px solid rgba(255,255,255,0.2) !important; border-radius: 12px !important; color: white !important; font-size: 14px !important;';
        passwordField.removeAttribute('hidden');
        passwordField.classList.remove('hidden');
    } else {
        passwordField.style.display = 'none';
        passwordField.value = '';
        // Reset chain
        const confirmField = document.getElementById('confirm-password');
        const registerBtn = document.getElementById('email-continue-btn');
        if (confirmField) {
            confirmField.style.display = 'none';
            confirmField.value = '';
        }
        if (registerBtn) {
            registerBtn.style.display = 'none';
        }
    }
};

window.showConfirmPasswordField = function() {
    console.log('=== showConfirmPasswordField TRIGGERED ===');
    const passwordField = document.getElementById('register-password');
    const confirmField = document.getElementById('confirm-password');

    if (!passwordField || !confirmField) {
        console.error('Cannot find password fields');
        return;
    }

    console.log('Password length:', passwordField.value.length);

    if (passwordField.value.length > 0) {
        console.log('>>> SHOWING CONFIRM PASSWORD FIELD <<<');
        // FORCE the field to be visible with important styles
        confirmField.style.cssText = 'display: block !important; visibility: visible !important; opacity: 1 !important; margin-top: 8px !important; width: 100% !important; padding: 12px !important; background: rgba(255,255,255,0.1) !important; border: 2px solid rgba(255,255,255,0.2) !important; border-radius: 12px !important; color: white !important; font-size: 14px !important;';
        confirmField.removeAttribute('hidden');
        confirmField.classList.remove('hidden');
    } else {
        confirmField.style.display = 'none';
        confirmField.value = '';
        const registerBtn = document.getElementById('email-continue-btn');
        if (registerBtn) {
            registerBtn.style.display = 'none';
        }
    }
};

window.checkIfCanRegister = function() {
    console.log('=== checkIfCanRegister TRIGGERED ===');
    const passwordField = document.getElementById('register-password');
    const confirmField = document.getElementById('confirm-password');
    const registerBtn = document.getElementById('email-continue-btn');

    if (!passwordField || !confirmField || !registerBtn) {
        console.error('Cannot find form elements');
        return;
    }

    const password = passwordField.value;
    const confirmPassword = confirmField.value;

    console.log('Password match:', password === confirmPassword, 'Length:', password.length);

    if (password.length >= 8 && password === confirmPassword) {
        console.log('>>> SHOWING REGISTER BUTTON <<<');
        // FORCE the button to be visible with important styles
        registerBtn.style.cssText = 'display: flex !important; visibility: visible !important; opacity: 1 !important; margin-top: 10px !important; width: 100% !important; padding: 12px 20px !important; background: linear-gradient(135deg, #0066ff, #4d94ff) !important; border: none !important; border-radius: 12px !important; color: white !important; font-size: 14px !important; font-weight: 600 !important; cursor: pointer !important; justify-content: center !important;';
        registerBtn.removeAttribute('hidden');
        registerBtn.classList.remove('hidden');
    } else {
        registerBtn.style.display = 'none';
        // NO POPUP HERE - removed completely from typing
    }
};

// Email detection with debouncing
let emailCheckTimeout = null;
window.checkEmailExists = async function() {
    const emailInput = document.getElementById('register-email');
    const email = emailInput.value.trim().toLowerCase();

    if (!email || !email.includes('@')) return;

    // Clear previous timeout
    if (emailCheckTimeout) clearTimeout(emailCheckTimeout);

    // Debounce the check
    emailCheckTimeout = setTimeout(async () => {
        try {
            console.log('Checking if email exists:', email);

            // Try to sign in with a dummy password to check if user exists
            const { error } = await supabase.auth.signInWithPassword({
                email: email,
                password: 'dummy_check_123456789'
            });

            const passwordField = document.getElementById('register-password');
            const confirmField = document.getElementById('confirm-password');
            const registerBtn = document.getElementById('email-continue-btn');

            if (error && error.message.includes('Invalid login credentials')) {
                // User exists - show login mode
                console.log('User exists - showing login mode');

                // Show password field for login
                passwordField.style.cssText = 'display: block !important; visibility: visible !important; opacity: 1 !important; margin-top: 8px !important; width: 100% !important; padding: 12px !important; background: rgba(255,255,255,0.1) !important; border: 2px solid rgba(255,255,255,0.2) !important; border-radius: 12px !important; color: white !important; font-size: 14px !important;';
                passwordField.placeholder = 'Enter your password';

                // Hide confirm password for login
                if (confirmField) {
                    confirmField.style.display = 'none';
                    confirmField.value = '';
                }

                // Change button to "Login"
                registerBtn.style.cssText = 'display: flex !important; visibility: visible !important; opacity: 1 !important; margin-top: 10px !important; width: 100% !important; padding: 12px 20px !important; background: linear-gradient(135deg, #0066ff, #4d94ff) !important; border: none !important; border-radius: 12px !important; color: white !important; font-size: 14px !important; font-weight: 600 !important; cursor: pointer !important; justify-content: center !important;';
                registerBtn.textContent = '🔐 Login';
                registerBtn.onclick = function() { quickLogin(); };

                // Add forgot password link
                let forgotLink = document.getElementById('forgot-password-link');
                if (!forgotLink) {
                    forgotLink = document.createElement('a');
                    forgotLink.id = 'forgot-password-link';
                    forgotLink.href = '#';
                    forgotLink.style.cssText = 'color: #4d94ff; font-size: 12px; margin-top: 8px; text-decoration: underline; cursor: pointer;';
                    forgotLink.textContent = 'Forgot password?';
                    forgotLink.onclick = function(e) {
                        e.preventDefault();
                        sendPasswordReset();
                    };
                    registerBtn.parentNode.appendChild(forgotLink);
                }

            } else {
                // New user - show registration mode
                console.log('New user - showing registration mode');

                // Progressive reveal is already handled by showPasswordField
                window.showPasswordField();

                // Reset button to register mode
                const registerBtn = document.getElementById('email-continue-btn');
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
};

// Simple register function (alias for continueWithEmail)
window.simpleRegister = async function() {
    return continueWithEmail();
};

// Log that functions are ready
console.log('Progressive reveal functions loaded and ready!');

// TEST: Force check that functions work on page load
window.addEventListener('load', function() {
    console.log('PAGE LOADED - Testing progressive reveal...');

    // Check if functions exist
    console.log('showPasswordField exists?', typeof window.showPasswordField === 'function');
    console.log('showConfirmPasswordField exists?', typeof window.showConfirmPasswordField === 'function');
    console.log('checkIfCanRegister exists?', typeof window.checkIfCanRegister === 'function');
    console.log('checkEmailExists exists?', typeof window.checkEmailExists === 'function');
    console.log('simpleRegister exists?', typeof window.simpleRegister === 'function');

    // Check if elements exist on slide 4
    setTimeout(() => {
        const emailField = document.getElementById('register-email');
        const passwordField = document.getElementById('register-password');
        const confirmField = document.getElementById('confirm-password');
        const registerBtn = document.getElementById('email-continue-btn');

        console.log('Elements found:', {
            email: !!emailField,
            password: !!passwordField,
            confirm: !!confirmField,
            button: !!registerBtn
        });

        // Force the password field to be ready
        if (passwordField) {
            passwordField.style.display = 'none';
            passwordField.style.visibility = 'visible';
            passwordField.style.opacity = '1';
        }
        if (confirmField) {
            confirmField.style.display = 'none';
            confirmField.style.visibility = 'visible';
            confirmField.style.opacity = '1';
        }
        if (registerBtn) {
            registerBtn.style.display = 'none';
        }
    }, 500);
});

// Slide navigation with swipe support
let currentSlide = 1;
const totalSlides = 8; // Updated to include login slide: Welcome, AI, Crypto, Register, Verify, Tier, Profile, Login
let touchStartX = 0;
let touchEndX = 0;
let selectedTier = null;

// Stripe Payment Configuration
const STRIPE_LINKS = {
    gold: 'https://buy.stripe.com/test_28o5nQfGa3Qr8Sc144', // Replace with your actual Gold tier Stripe link
    premium: 'https://buy.stripe.com/test_14k03wcua2Mn5G06op', // Replace with your actual Premium tier Stripe link
    // Set to null to use demo mode (shows alert instead of redirecting)
    demoMode: true // Set to false when you have real Stripe links
};

// Check for magic link in URL and handle it properly
function handleMagicLink() {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    const errorDescription = urlParams.get('error_description');

    // Check if this is a magic link callback
    if (window.location.hash && window.location.hash.includes('access_token')) {
        console.log('Magic link clicked - auto-verifying...');

        // Extract the access token
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hashParams.get('access_token');

        // Clear the URL to remove the token
        window.history.replaceState({}, document.title, window.location.pathname);

        // Since they clicked the magic link, they're verified
        localStorage.setItem('zmarty_email_verified', 'true');

        // Clean up verification states
        sessionStorage.removeItem('verification_code');
        sessionStorage.removeItem('pending_verification');

        // Go directly to tier selection (slide 6) since they're verified
        goToSlide(6);
        showError('✅ Email verified! Choose your plan to continue.');

        return true;
    }

    if (error) {
        console.error('Auth error:', errorDescription);
        showError(errorDescription || 'Authentication error occurred');
        return true;
    }

    return false;
}

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    console.log('=== PAGE LOADED ===');
    console.log('URL:', window.location.href);

    // CLEAR EVERYTHING FOR FRESH START
    // Comment this line if you want to preserve login state
    await supabase.auth.signOut();
    sessionStorage.clear();
    localStorage.removeItem('zmarty_email_verified');
    localStorage.removeItem('zmarty_temp_email');
    localStorage.removeItem('zmarty_temp_tier');
    currentSlide = 1;

    // First check for magic link and redirect appropriately
    if (handleMagicLink()) {
        return;
    }

    // Clean up any stray overlays, modals, error messages, and unwanted elements
    const strayElements = document.querySelectorAll('[id*="overlay"], .modal-overlay, .login-modal, [class*="modal"], .error-toast');
    strayElements.forEach(element => {
        console.warn('Removing stray element on load:', element.className || element.id);
        element.remove();
    });

    // REMOVED ALL CLICK BLOCKERS - They were causing bugs

    // REMOVED GLOBAL CLICK BLOCKER - It was causing bugs

    // ONLY process magic link if we have BOTH access_token AND it's a real verification
    const hashParams = new URLSearchParams(window.location.hash.substring(1));
    const accessToken = hashParams.get('access_token');
    const isVerificationCallback = window.location.hash.includes('access_token') && window.location.hash.includes('type=signup');

    if (accessToken && isVerificationCallback) {
        console.log('Magic Link detected! Processing authentication...');

        // Wait for Supabase to process the Magic Link
        setTimeout(async () => {
            const { data: { session } } = await supabase.auth.getSession();
            console.log('Session after Magic Link:', session);

            if (session) {
                // User verified! Jump to tier selection
                console.log('Email verified! Moving to tier selection...');

                // Clear the URL hash to clean up
                window.location.hash = '';

                // Jump directly to slide 6 (tier selection)
                currentSlide = 6;

                // Hide all slides first
                document.querySelectorAll('.slide').forEach(s => {
                    s.classList.remove('active');
                    s.style.opacity = '0';
                    s.style.transform = 'translateX(100%)';
                });

                // Show slide 6
                const slide6 = document.getElementById('slide-6');
                if (slide6) {
                    slide6.classList.add('active');
                    slide6.style.opacity = '1';
                    slide6.style.transform = 'translateX(0)';

                    // Force visibility
                    slide6.style.display = 'flex';
                    slide6.style.visibility = 'visible';
                }

                // Update navigation dots
                updateDots();

                // Show success message
                setTimeout(() => {
                    showError('✅ Email verified successfully! Choose your plan to continue.');
                }, 500);

                return;
            }
        }, 1000);

        return;
    }

    // Check if already logged in - BUT DON'T AUTO-JUMP TO TIER SCREEN
    const { data: { session } } = await supabase.auth.getSession();
    console.log('Existing session:', session);

    // REMOVED AUTO-JUMP - Let user navigate through slides normally
    // If you want to skip logged-in users to dashboard, uncomment below:
    /*
    if (session && session.user?.user_metadata?.profile_completed) {
        // Only redirect if profile is complete
        window.location.href = 'dashboard.html';
        return;
    }
    */

    // Normal flow - start from slide 1
    const slide1 = document.getElementById('slide-1');
    if (slide1) {
        slide1.classList.add('active');
        slide1.style.opacity = '1';
        slide1.style.transform = 'translateX(0)';
    }

    currentSlide = 1;

    // Add swipe listeners to slides wrapper
    const slidesWrapper = document.querySelector('.slides-wrapper');
    if (slidesWrapper) {
        slidesWrapper.addEventListener('touchstart', handleTouchStart, { passive: true });
        slidesWrapper.addEventListener('touchend', handleTouchEnd, { passive: true });
    }

    // Add keyboard navigation - FIXED
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight' || e.keyCode === 39) {
            e.preventDefault();
            nextSlide();
        } else if (e.key === 'ArrowLeft' || e.keyCode === 37) {
            e.preventDefault();
            previousSlide();
        }
    });

    // Initialize dots if they exist
    initializeDots();

    // Update next button text on last slide
    updateNextButton();
});

// Touch handling for swipe
function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].screenX;
}

function handleTouchEnd(e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}

function handleSwipe() {
    const swipeThreshold = 50; // minimum distance for swipe
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - next slide
            nextSlide();
        } else {
            // Swipe right - previous slide
            previousSlide();
        }
    }
}

// Initialize dots navigation
function initializeDots() {
    const dots = document.querySelectorAll('.dot');
    if (dots && dots.length > 0) {
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => goToSlide(index + 1));
        });
    }
}

// Navigate to specific slide
function goToSlide(slideNumber) {
    // Validate slide number
    if (slideNumber < 1 || slideNumber > totalSlides) return;

    // Allow navigation to slide 5 if coming from slide 4 or if there's a pending verification
    if (slideNumber === 5 && currentSlide !== 4 && slideNumber > currentSlide) {
        const isVerified = localStorage.getItem('zmarty_email_verified');
        const hasPendingVerification = sessionStorage.getItem('pending_verification');
        const hasVerificationEmail = localStorage.getItem('zmarty_verification_email');

        if (!isVerified && !hasPendingVerification && !hasVerificationEmail) {
            showError('Please complete email registration first');
            return;
        }
    }

    // Block navigation to slide 6 unless verification and user info are complete
    if (slideNumber === 6 && slideNumber > currentSlide) {
        const isVerified = localStorage.getItem('zmarty_email_verified');
        const hasUserInfo = localStorage.getItem('zmarty_user_name') && localStorage.getItem('zmarty_user_country');

        if (!isVerified || !hasUserInfo) {
            showError('Please complete the verification process first');
            return;
        }
    }

    // Hide all slides IMMEDIATELY with direct style
    document.querySelectorAll('.slide').forEach(slide => {
        slide.classList.remove('active', 'prev');
        slide.style.opacity = '0';
        slide.style.transform = 'translateX(100%)';
    });

    // Show current slide IMMEDIATELY with direct style
    const targetSlide = document.getElementById(`slide-${slideNumber}`);
    if (targetSlide) {
        targetSlide.classList.add('active');
        targetSlide.style.opacity = '1';
        targetSlide.style.transform = 'translateX(0)';

        // Mark previous slides
        for (let i = 1; i < slideNumber; i++) {
            const prevSlide = document.getElementById(`slide-${i}`);
            if (prevSlide) {
                prevSlide.classList.add('prev');
                prevSlide.style.transform = 'translateX(-100%)';
            }
        }
    }

    // Update dots
    document.querySelectorAll('.dot').forEach((dot, index) => {
        dot.classList.toggle('active', index === slideNumber - 1);
    });

    currentSlide = slideNumber;
    updateNextButton();
}

// Next slide
function nextSlide() {
    // Block navigation from slide 4 to 5 until email is registered
    if (currentSlide === 4) {
        const emailInput = document.getElementById('register-email');
        if (!emailInput || !emailInput.value.trim()) {
            showError('Please enter your email to continue');
            return;
        }
        // If email is entered, trigger the email registration process
        continueWithEmail();
        return;
    }

    // Block navigation from slide 5 to 6 until verification is complete
    if (currentSlide === 5) {
        const isVerified = localStorage.getItem('zmarty_email_verified');
        const hasUserInfo = localStorage.getItem('zmarty_user_name') && localStorage.getItem('zmarty_user_country');

        if (!isVerified || !hasUserInfo) {
            showError('Please complete the verification process first');
            return;
        }
    }

    if (currentSlide < totalSlides) {
        goToSlide(currentSlide + 1);
    } else if (currentSlide === 7) {
        // On slide 7 (Profile), complete profile
        completeProfile();
    } else if (currentSlide === 8) {
        // On slide 8 (Login), handle sign in
        return;
    }
}

// Previous slide
function previousSlide() {
    if (currentSlide > 1) {
        goToSlide(currentSlide - 1);
    }
}

// Update next button
function updateNextButton() {
    const nextBtn = document.querySelector('.next-btn');
    const nextText = document.getElementById('next-text');

    // Check if elements exist (might not be present on all pages)
    if (!nextBtn) return;

    if (currentSlide === totalSlides) {
        // Hide next button on last slide (using login options instead)
        nextBtn.classList.add('hidden');
    } else {
        nextBtn.classList.remove('hidden');
        if (nextText) {
            nextText.textContent = 'Next';
        }
    }
}

// Skip onboarding
function skipOnboarding() {
    goToSlide(4); // Go to email registration (now slide 4)
}

// Quick login with provider
async function quickLogin(provider, evt) {
    // Prevent any bubbling or propagation
    if (evt) {
        evt.stopPropagation();
        evt.preventDefault();
    }

    // Only proceed if we have a valid provider
    if (!provider || (provider !== 'google' && provider !== 'apple')) {
        console.error('Invalid provider:', provider);
        return;
    }

    // Animate button if we have a valid event target
    if (evt && evt.target) {
        evt.target.style.transform = 'scale(0.95)';
    }

    setTimeout(async () => {
        try {
            // Social login with Supabase
            const result = await UserService.socialLogin(provider);

            if (result.success) {
                // Save provider temporarily
                localStorage.setItem('zmarty_temp_provider', provider);
                localStorage.setItem('zmarty_temp_tier', selectedTier || 'free');
                localStorage.setItem('zmarty_email_verified', 'true'); // Social login auto-verifies

                showError(`Redirecting to ${provider} login...`);

                // Redirect to OAuth provider
                if (result.url) {
                    window.location.href = result.url;
                }
            } else {
                showError(result.error || `Failed to authenticate with ${provider}`);
            }
        } catch (error) {
            showError(`Failed to authenticate with ${provider}: ${error.message}`);
        }
    }, 200);
}

// Select tier
async function selectTier(tier) {
    selectedTier = tier;

    // Update UI
    document.querySelectorAll('.tier-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    if (event && event.target) {
        event.target.closest('.tier-option').classList.add('selected');
    }

    // Save tier selection
    sessionStorage.setItem('selected_tier', tier);
    localStorage.setItem('zmarty_tier', tier);

    // Update user profile with selected tier
    const result = await UserService.updateTier(tier);

    if (result.success) {
        showError(`${tier.charAt(0).toUpperCase() + tier.slice(1)} tier selected!`);
        // Move to profile setup (slide 7)
        setTimeout(() => nextSlide(), 500);
    } else {
        showError('Failed to update tier. Please try again.');
    }
}

// Continue with email
async function continueWithEmail() {
    console.log('REGISTER BUTTON CLICKED!');

    const emailInput = document.getElementById('register-email');
    const passwordInput = document.getElementById('register-password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput ? confirmPasswordInput.value : '';

    console.log('Registration attempt:', { email, passwordLength: password.length });

    // Clear any previous errors
    emailInput.classList.remove('error');
    passwordInput.classList.remove('error');
    if (confirmPasswordInput) confirmPasswordInput.classList.remove('error');

    if (!email) {
        showError('Please enter your email');
        emailInput.classList.add('error');
        return;
    }

    if (!password || password.length < 8) {
        showError('Password must be at least 8 characters');
        passwordInput.classList.add('error');
        return;
    }

    // Check if passwords match - only check, don't show popup unless critical
    if (password !== confirmPassword) {
        // Don't show popup, just show inline error
        showError('Passwords do not match. Please check and try again.');
        confirmPasswordInput.classList.add('error');
        return;
    }

    // Proper email validation regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('Please enter a valid email address');
        emailInput.classList.add('error');
        return;
    }

    // Save email and tier temporarily
    localStorage.setItem('zmarty_temp_email', email);
    localStorage.setItem('zmarty_temp_tier', selectedTier || 'free');

    // Show loading state on button
    const registerBtn = document.getElementById('email-continue-btn');
    const originalText = registerBtn.innerHTML;
    registerBtn.innerHTML = '<span>Registering...</span>';
    registerBtn.disabled = true;

    try {
        // Register user with Supabase with actual password
        console.log('Calling UserService.register...');
        const result = await UserService.register(email, password, selectedTier || 'free');

        if (result.success) {
            console.log('Registration successful!');

            // Store email for verification step
            localStorage.setItem('zmarty_verification_email', email);
            localStorage.setItem('zmarty_temp_email', email);

            // Restore button state BEFORE transitioning
            registerBtn.innerHTML = originalText;
            registerBtn.disabled = false;

            // Immediately go to email verification slide (slide 5)
            console.log('Transitioning to slide 5 (verification)...');
            goToSlide(5);

            // Show success message after slide transition
            setTimeout(() => {
                showError(`✅ Verification code sent to ${email}! Check your inbox.`);
            }, 500);
        } else {
            showError(result.error || 'Failed to send verification email');
            // Restore button state
            registerBtn.innerHTML = originalText;
            registerBtn.disabled = false;

            // If rate limited, show countdown
            if (result.isRateLimit) {
                const waitMatch = result.error.match(/\d+/);
                if (waitMatch) {
                    const seconds = parseInt(waitMatch[0]);
                    startRateLimitCountdown(registerBtn, seconds);
                }
            }
        }
    } catch (error) {
        showError('Failed to send verification email: ' + error.message);
        // Restore button state
        registerBtn.innerHTML = originalText;
        registerBtn.disabled = false;
    }
}

// Move to next code input
function moveToNext(current, nextId) {
    if (current.value.length === 1) {
        const next = document.getElementById(nextId);
        if (next) {
            next.focus();
        } else {
            // If this is the last input, verify the code
            verifyCode();
        }
    }

    // Handle backspace
    current.addEventListener('keydown', function(e) {
        if (e.key === 'Backspace' && current.value === '') {
            const prevId = parseInt(current.id.split('-')[1]) - 1;
            if (prevId >= 1) {
                document.getElementById(`code-${prevId}`).focus();
            }
        }
    });
}

// Verify code
async function verifyCode() {
    const codeInputs = Array.from({length: 6}, (_, i) =>
        document.getElementById(`code-${i + 1}`)
    );

    const enteredCode = codeInputs.map(input => input.value).join('');

    // Clear any previous error states
    codeInputs.forEach(input => input.classList.remove('error'));

    if (enteredCode.length !== 6 || !/^\d{6}$/.test(enteredCode)) {
        showError('Please enter all 6 digits');
        codeInputs.forEach(input => {
            if (!input.value) input.classList.add('error');
        });
        return;
    }

    // Try both keys for backward compatibility
    const email = localStorage.getItem('zmarty_verification_email') || localStorage.getItem('zmarty_temp_email');
    if (!email) {
        showError('Session expired. Please start over.');
        goToSlide(4); // Go back to email registration slide
        return;
    }

    try {
        // Verify email with Supabase
        const result = await UserService.verifyEmail(email, enteredCode);

        if (result.success) {
            showError('Email verified successfully!');
            localStorage.setItem('zmarty_email_verified', 'true');
            localStorage.setItem('zmarty_session', JSON.stringify(result.session));
            localStorage.setItem('zmarty_user', JSON.stringify(result.user));

            // Show user info form instead of advancing
            setTimeout(() => {
                document.getElementById('user-info-container').style.display = 'block';
                document.querySelector('.verification-container .code-inputs').style.display = 'none';
                document.querySelector('.verify-btn').style.display = 'none';
                document.querySelector('.resend-text').style.display = 'none';
            }, 1000);
        } else {
            showError(result.error || 'Invalid verification code');
            // Clear the input fields
            for (let i = 1; i <= 6; i++) {
                document.getElementById(`code-${i}`).value = '';
            }
            document.getElementById('code-1').focus();
        }
    } catch (error) {
        showError('Invalid code. Please try again.');
        // Clear the input fields
        for (let i = 1; i <= 6; i++) {
            document.getElementById(`code-${i}`).value = '';
        }
        document.getElementById('code-1').focus();
    }
}

// Resend verification code
async function resendCode() {
    const email = localStorage.getItem('zmarty_verification_email') || localStorage.getItem('zmarty_temp_email');

    try {
        const result = await UserService.resendCode(email);

        if (result.success) {
            showError(`New verification code sent to ${email}. Please check your inbox.`);
        } else {
            showError(result.error || 'Failed to resend code');
        }
    } catch (error) {
        showError('Failed to resend code: ' + error.message);
    }
}

// Finish onboarding
async function finishOnboarding() {
    const name = document.getElementById('user-name').value;
    const country = document.getElementById('user-country').value;
    const email = localStorage.getItem('zmarty_temp_email');
    const provider = localStorage.getItem('zmarty_temp_provider');
    const tier = localStorage.getItem('zmarty_temp_tier') || selectedTier || 'free';

    if (!name) {
        showError('Please enter your name');
        return;
    }

    if (!country) {
        showError('Please select your country');
        return;
    }

    try {
        // Update user profile with Supabase
        const result = await UserService.updateProfile(name, country);

        if (result.success) {
            // Update tier if needed
            if (tier !== 'free') {
                await UserService.updateTier(tier);
            }

            // Save to localStorage
            localStorage.setItem('zmarty_onboarding_complete', 'true');
            localStorage.setItem('zmarty_user', JSON.stringify(result.user));

            // Clear temp data
            localStorage.removeItem('zmarty_temp_email');
            localStorage.removeItem('zmarty_temp_provider');
            localStorage.removeItem('zmarty_temp_tier');
            localStorage.removeItem('zmarty_temp_user_id');

            showError('Account created successfully!');

            // Go to dashboard
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showError(result.error || 'Failed to complete profile');
        }
    } catch (error) {
        showError('Failed to complete profile: ' + error.message);
    }
}

// Show error message
function showError(message) {
    // Remove existing error if any
    const existingError = document.querySelector('.error-toast');
    if (existingError) existingError.remove();

    const error = document.createElement('div');
    error.className = 'error-toast';
    error.textContent = message;
    error.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #ff4757;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        z-index: 9999;
        animation: slideDown 0.3s ease;
        font-size: 14px;
        font-weight: 500;
    `;
    document.body.appendChild(error);

    setTimeout(() => error.remove(), 3000);
}

// Removed duplicate - keyboard navigation is already handled in DOMContentLoaded

// Enable enter key on email field
document.addEventListener('DOMContentLoaded', function() {
    const emailField = document.getElementById('email');
    if (emailField) {
        emailField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                quickStart();
            }
        });
    }
});

// Add slide animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translate(-50%, -20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }
`;
document.head.appendChild(style);
// Complete profile function
async function completeProfile() {
    const name = document.getElementById('profile-name').value.trim();
    const country = document.getElementById('profile-country').value;

    if (!name || !country) {
        showError('Please fill in all fields');
        return;
    }

    try {
        const result = await UserService.updateProfile(name, country);

        if (result.success) {
            showError('Profile completed! Redirecting to dashboard...');
            localStorage.setItem('zmarty_profile_completed', 'true');

            // Redirect to dashboard after 1.5 seconds
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showError(result.error || 'Failed to update profile');
        }
    } catch (error) {
        showError('Error updating profile. Please try again.');
    }
}

// Show password mismatch popup and reset
function showPasswordMismatchPopup() {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease;
    `;

    // Create popup
    const popup = document.createElement('div');
    popup.style.cssText = `
        background: white;
        border-radius: 20px;
        padding: 30px;
        max-width: 400px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.3s ease;
    `;

    popup.innerHTML = `
        <div style="
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #ff4444, #ff6666);
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
        </div>
        <h2 style="color: #1a1a1a; margin: 0 0 10px 0; font-size: 24px; font-weight: 600;">
            Passwords Don't Match
        </h2>
        <p style="color: #6b7280; margin: 0 0 25px 0; font-size: 16px; line-height: 1.5;">
            The passwords you entered don't match. Please try again with matching passwords.
        </p>
        <button id="reset-password-btn" style="
            background: linear-gradient(135deg, #0066ff, #4d94ff);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px 32px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            OK, Try Again
        </button>
    `;

    overlay.appendChild(popup);
    document.body.appendChild(overlay);

    // Add animation styles if not already present
    if (!document.getElementById('popup-animations')) {
        const style = document.createElement('style');
        style.id = 'popup-animations';
        style.textContent = `
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Handle button click
    document.getElementById('reset-password-btn').addEventListener('click', function() {
        // Reset password fields
        const passwordInput = document.getElementById('register-password');
        const confirmPasswordInput = document.getElementById('confirm-password');
        const confirmPasswordContainer = document.getElementById('confirm-password-container');
        const continueBtn = document.getElementById('email-continue-btn');
        const passwordHint = document.getElementById('password-hint');
        const confirmHint = document.getElementById('confirm-password-hint');

        // Clear password values
        if (passwordInput) {
            passwordInput.value = '';
            passwordInput.classList.remove('error');
        }
        if (confirmPasswordInput) {
            confirmPasswordInput.value = '';
            confirmPasswordInput.classList.remove('error');
        }

        // Hide password-related elements
        if (confirmPasswordContainer) {
            confirmPasswordContainer.style.display = 'none';
        }
        if (continueBtn) {
            continueBtn.style.display = 'none';
        }
        if (passwordHint) {
            passwordHint.style.display = 'none';
        }
        if (confirmHint) {
            confirmHint.style.display = 'none';
        }

        // Remove overlay
        overlay.remove();

        // Focus on password field
        if (passwordInput) {
            passwordInput.focus();
        }
    });
}

// Quick start function - skip to registration
function quickStart() {
    goToSlide(4); // Go to email registration slide (now slide 4)
}

// Move to next code input
function moveToNext(current, nextId) {
    if (current.value.length === 1 && nextId) {
        document.getElementById(nextId).focus();
    }
    // If all 6 digits entered, auto-verify
    if (nextId === null) {
        const allFilled = Array.from({length: 6}, (_, i) =>
            document.getElementById(`code-${i + 1}`).value
        ).every(val => val.length === 1);

        if (allFilled) {
            verifyCode();
        }
    }
}

// Functions moved to top of file for immediate availability

// OLD FUNCTION - NOT USED ANYMORE
// Progressive reveal: Handle password input
/*
function onPasswordInput() {
    const emailInput = document.getElementById('register-email');
    const passwordInput = document.getElementById('register-password');
    const confirmPasswordContainer = document.getElementById('confirm-password-container');
    const passwordHint = document.getElementById('password-hint');
    const continueBtn = document.getElementById('email-continue-btn');

    if (!emailInput || !passwordInput || !confirmPasswordContainer) return;

    // Check password validity
    const hasValidEmail = emailInput.value.trim().length > 0 && emailInput.value.includes('@');
    const passwordLength = passwordInput.value.length;

    // Show hint for password requirements
    if (passwordLength > 0 && passwordLength < 8) {
        passwordHint.style.display = 'block';
        passwordHint.style.color = 'var(--error-red, #ff4444)';
        passwordHint.textContent = 'Password must be at least 8 characters';
    } else if (passwordLength >= 8) {
        passwordHint.style.display = 'block';
        passwordHint.style.color = 'var(--success-green, #00ff88)';
        passwordHint.textContent = '✓ Password is valid';
    } else {
        passwordHint.style.display = 'none';
    }

    // Show confirm password field when password has at least 1 character
    if (passwordLength > 0) {
        confirmPasswordContainer.style.display = 'block';
        confirmPasswordContainer.style.opacity = '0';
        confirmPasswordContainer.style.animation = 'fadeIn 0.3s ease forwards';
    } else {
        confirmPasswordContainer.style.display = 'none';
        // Reset confirm password field when password is cleared
        const confirmPasswordInput = document.getElementById('confirm-password');
        if (confirmPasswordInput) {
            confirmPasswordInput.value = '';
        }
        // Hide button
        if (continueBtn) {
            continueBtn.style.display = 'none';
        }
    }

    // Check if confirm password field has value to update button state
    const confirmPassword = document.getElementById('confirm-password');
    if (confirmPassword && confirmPassword.value) {
        onConfirmPasswordInput();
    }
}
*/

// OLD FUNCTION - NOT USED ANYMORE
/*
// Handle confirm password input
function onConfirmPasswordInput() {
    const passwordInput = document.getElementById('register-password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const continueBtn = document.getElementById('email-continue-btn');
    const confirmHint = document.getElementById('confirm-password-hint');
    const confirmMessage = document.getElementById('confirm-password-message');

    if (!passwordInput || !confirmPasswordInput || !continueBtn) return;

    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    const passwordLength = password.length;
    const confirmLength = confirmPassword.length;

    // Show hint about password matching
    if (confirmLength > 0) {
        confirmHint.style.display = 'block';

        if (confirmPassword === password && passwordLength >= 8) {
            // Passwords match and are valid - SHOW REGISTER BUTTON
            confirmHint.style.color = 'var(--success-green, #00ff88)';
            confirmMessage.textContent = '✓ Passwords match';

            // Show register button immediately when passwords match
            continueBtn.style.display = 'block';
            continueBtn.style.opacity = '0';
            continueBtn.style.animation = 'fadeIn 0.3s ease forwards';
            continueBtn.innerHTML = '<span>Register →</span>';
            continueBtn.disabled = false;
        } else if (passwordLength < 8) {
            // First password is too short - HIDE BUTTON
            confirmHint.style.color = 'var(--text-muted)';
            confirmMessage.textContent = 'First password needs 8+ characters';
            continueBtn.style.display = 'none';
        } else if (confirmLength < password.length) {
            // Still typing confirm password - HIDE BUTTON
            confirmHint.style.color = 'var(--text-muted)';
            confirmMessage.textContent = 'Keep typing...';
            continueBtn.style.display = 'none';
        } else if (confirmPassword !== password) {
            // Passwords don't match (fully typed) - HIDE BUTTON
            confirmHint.style.color = 'var(--error-red, #ff4444)';
            confirmMessage.textContent = '✗ Passwords do not match';
            continueBtn.style.display = 'none';
        }
    } else {
        // No confirm password entered - HIDE EVERYTHING
        confirmHint.style.display = 'none';
        continueBtn.style.display = 'none';
    }
}
*/

// Keep the old function for compatibility but redirect to new ones
function toggleContinueButton() {
    // Not used anymore - using new progressive reveal functions
    console.log('toggleContinueButton called - using new progressive reveal');
}

function checkPasswordStrength() {
    // Not used anymore - using new progressive reveal functions
    console.log('checkPasswordStrength called - using new progressive reveal');
}

// Save user info and continue to tier selection
async function saveUserInfo() {
    const nameInput = document.getElementById('user-name');
    const countryInput = document.getElementById('user-country');

    const name = nameInput.value.trim();
    const country = countryInput.value.trim();

    // Clear any previous errors
    nameInput.classList.remove('error');
    countryInput.classList.remove('error');

    if (!name) {
        showError('Please enter your name');
        nameInput.classList.add('error');
        return;
    }

    if (!country) {
        showError('Please enter your country');
        countryInput.classList.add('error');
        return;
    }

    try {
        // Update user profile in Supabase
        const result = await UserService.updateProfile(name, country);

        if (result.success) {
            // Save user info locally as well
            localStorage.setItem('zmarty_user_name', name);
            localStorage.setItem('zmarty_user_country', country);

            showError(`Nice to meet you, ${name} from ${country}!`);

            // Continue to tier selection (slide 6)
            setTimeout(() => goToSlide(6), 1500);
        } else {
            showError(result.error || 'Failed to save profile');
        }
    } catch (error) {
        showError('Failed to save profile: ' + error.message);
    }
}

// Go to dashboard
function goToDashboard() {
    localStorage.setItem('zmarty_onboarding_complete', 'true');
    window.location.href = 'dashboard.html';
}

// Show countdown timer for rate limiting
function startRateLimitCountdown(button, seconds) {
    let timeLeft = seconds;
    const originalText = button.innerHTML;

    button.disabled = true;

    const countdown = setInterval(() => {
        if (timeLeft > 0) {
            button.innerHTML = `Wait ${timeLeft}s...`;
            timeLeft--;
        } else {
            clearInterval(countdown);
            button.innerHTML = originalText;
            button.disabled = false;
            showError('You can now try registering again');
        }
    }, 1000);
}

// Handle sign in from slide 8
async function handleSignIn(event) {
    event.preventDefault();

    const emailInput = document.getElementById('login-email');
    const passwordInput = document.getElementById('login-password');
    const signInBtn = event.target;

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    // Show loading state
    const originalText = signInBtn.textContent;
    signInBtn.textContent = 'Signing In...';
    signInBtn.disabled = true;

    try {
        // Sign in with Supabase using the correct method name
        const result = await UserService.login(email, password);

        if (result.success) {
            showError('✅ Sign in successful! Redirecting...');

            // Store session
            localStorage.setItem('zmarty_session', JSON.stringify(result.session));
            localStorage.setItem('zmarty_user_email', email);
            localStorage.setItem('zmarty_user_id', result.user?.id);
            localStorage.setItem('zmarty_onboarding_complete', 'true');

            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showError(result.error || 'Invalid email or password');
            signInBtn.textContent = originalText;
            signInBtn.disabled = false;
        }
    } catch (error) {
        console.error('Sign in error:', error);
        showError('Sign in failed. Please check your credentials.');
        signInBtn.textContent = originalText;
        signInBtn.disabled = false;
    }
}

// Show forgot password slide (for future implementation)
function showForgotPasswordSlide() {
    // For now, show the modal, but could be Slide 9 in future
    showForgotPasswordModal();
}

// Show forgot password / sign in modal (DEPRECATED - will be replaced with slide)
function showForgotPasswordModal() {
    // Check if overlay already exists and remove it
    const existingOverlay = document.getElementById('forgot-password-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'forgot-password-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease;
    `;

    // Create modal
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: white;
        border-radius: 20px;
        padding: 40px;
        max-width: 440px;
        width: 90%;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: slideUp 0.3s ease;
        position: relative;
    `;

    modal.innerHTML = `
        <!-- Close button -->
        <button onclick="closeForgotPasswordModal()" style="
            position: absolute;
            top: 20px;
            right: 20px;
            background: none;
            border: none;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background 0.2s ease;
        " onmouseover="this.style.background='#f3f4f6'" onmouseout="this.style.background='none'">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
        </button>

        <!-- Icon -->
        <div style="
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #0066ff, #4d94ff);
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
        </div>

        <!-- Title -->
        <h2 style="color: #1a1a1a; margin: 0 0 10px 0; font-size: 24px; font-weight: 600; text-align: center;">
            Welcome Back!
        </h2>
        <p style="color: #6b7280; margin: 0 0 30px 0; font-size: 14px; text-align: center;">
            Sign in to your Zmarty account
        </p>

        <!-- Sign In Form -->
        <div id="signin-form">
            <input type="email"
                   id="signin-email"
                   class="modern-email-input"
                   placeholder="Enter your email address"
                   style="width: 100%; margin-bottom: 12px; box-sizing: border-box;"
                   onkeyup="if(event.key === 'Enter' && this.value && document.getElementById('signin-password').value) signInUser()" />

            <input type="password"
                   id="signin-password"
                   class="modern-email-input"
                   placeholder="Enter your password"
                   style="width: 100%; margin-bottom: 20px; box-sizing: border-box;"
                   onkeyup="if(event.key === 'Enter' && this.value && document.getElementById('signin-email').value) signInUser()" />

            <button onclick="signInUser()" style="
                background: linear-gradient(135deg, #0066ff, #4d94ff);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 32px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                transition: transform 0.2s ease;
                margin-bottom: 15px;
            " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                Sign In
            </button>

            <a href="#" onclick="showResetPasswordForm(); return false;" style="
                display: block;
                text-align: center;
                color: var(--primary-blue);
                text-decoration: none;
                font-size: 14px;
                opacity: 0.8;
                transition: opacity 0.2s ease;
            " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">
                Forgot your password?
            </a>
        </div>

        <!-- Reset Password Form (Hidden initially) -->
        <div id="reset-password-form" style="display: none;">
            <input type="email"
                   id="reset-email"
                   class="modern-email-input"
                   placeholder="Enter your email address"
                   style="width: 100%; margin-bottom: 20px; box-sizing: border-box;"
                   onkeyup="if(event.key === 'Enter' && this.value) sendPasswordReset()" />

            <button onclick="sendPasswordReset()" style="
                background: linear-gradient(135deg, #0066ff, #4d94ff);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 32px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                transition: transform 0.2s ease;
                margin-bottom: 15px;
            " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                Send Reset Link
            </button>

            <a href="#" onclick="showSignInForm(); return false;" style="
                display: block;
                text-align: center;
                color: var(--primary-blue);
                text-decoration: none;
                font-size: 14px;
                opacity: 0.8;
                transition: opacity 0.2s ease;
            " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">
                Back to Sign In
            </a>
        </div>

        <!-- Success Message (Hidden initially) -->
        <div id="reset-success" style="display: none; text-align: center;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #22c55e, #16a34a);
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                    <path d="M20 6L9 17l-5-5"/>
                </svg>
            </div>
            <h3 style="color: #1a1a1a; margin: 0 0 10px 0; font-size: 20px; font-weight: 600;">
                Email Sent!
            </h3>
            <p style="color: #6b7280; margin: 0 0 25px 0; font-size: 14px; line-height: 1.5;">
                Check your email for a password reset link. It may take a few minutes to arrive.
            </p>
            <button onclick="closeForgotPasswordModal()" style="
                background: linear-gradient(135deg, #0066ff, #4d94ff);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 32px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                OK
            </button>
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Focus on email field
    setTimeout(() => {
        document.getElementById('signin-email').focus();
    }, 100);
}

// Close forgot password modal
function closeForgotPasswordModal() {
    const overlay = document.getElementById('forgot-password-overlay');
    if (overlay) {
        overlay.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => overlay.remove(), 300);
    }
}

// Show reset password form
function showResetPasswordForm() {
    // Check if the overlay exists first
    const overlay = document.getElementById('forgot-password-overlay');
    if (!overlay) {
        console.error('Forgot password overlay not found');
        return;
    }

    const signinForm = document.getElementById('signin-form');
    const resetForm = document.getElementById('reset-password-form');
    const resetSuccess = document.getElementById('reset-success');

    if (signinForm) signinForm.style.display = 'none';
    if (resetForm) resetForm.style.display = 'block';
    if (resetSuccess) resetSuccess.style.display = 'none';

    // Update title
    const modal = document.querySelector('#forgot-password-overlay h2');
    if (modal) {
        modal.textContent = 'Reset Password';
    }
    const subtitle = document.querySelector('#forgot-password-overlay p');
    if (subtitle) {
        subtitle.textContent = 'Enter your email to receive a reset link';
    }

    // Focus on reset email field
    setTimeout(() => {
        const resetEmail = document.getElementById('reset-email');
        if (resetEmail) resetEmail.focus();
    }, 100);
}

// Show sign in form
function showSignInForm() {
    // Check if the overlay exists first
    const overlay = document.getElementById('forgot-password-overlay');
    if (!overlay) {
        console.error('Forgot password overlay not found');
        return;
    }

    const signinForm = document.getElementById('signin-form');
    const resetForm = document.getElementById('reset-password-form');
    const resetSuccess = document.getElementById('reset-success');

    if (signinForm) signinForm.style.display = 'block';
    if (resetForm) resetForm.style.display = 'none';
    if (resetSuccess) resetSuccess.style.display = 'none';

    // Update title back
    const modal = document.querySelector('#forgot-password-overlay h2');
    if (modal) {
        modal.textContent = 'Welcome Back!';
    }
    const subtitle = document.querySelector('#forgot-password-overlay p');
    if (subtitle) {
        subtitle.textContent = 'Sign in to your Zmarty account';
    }
}

// Sign in user
async function signInUser() {
    const emailInput = document.getElementById('signin-email');
    const passwordInput = document.getElementById('signin-password');
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    try {
        // Show loading state
        const signInBtn = event.target;
        const originalText = signInBtn.textContent;
        signInBtn.textContent = 'Signing in...';
        signInBtn.disabled = true;

        const result = await UserService.login(email, password);

        if (result.success) {
            showError('Sign in successful! Redirecting...');

            // Store session
            localStorage.setItem('zmarty_user', JSON.stringify(result.user));
            localStorage.setItem('zmarty_session', JSON.stringify(result.session));

            // Close modal and redirect
            setTimeout(() => {
                closeForgotPasswordModal();
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showError(result.error || 'Invalid email or password');
            signInBtn.textContent = originalText;
            signInBtn.disabled = false;
        }
    } catch (error) {
        showError('Sign in failed. Please try again.');
        const signInBtn = event.target;
        signInBtn.textContent = 'Sign In';
        signInBtn.disabled = false;
    }
}

// Send password reset email
async function sendPasswordReset() {
    // Try to get email from register-email field first, then reset-email
    let emailInput = document.getElementById('register-email') || document.getElementById('reset-email');
    const email = emailInput ? emailInput.value.trim() : '';

    if (!email) {
        showError('Please enter your email address');
        return;
    }

    try {
        // Show loading state
        const resetBtn = event.target;
        const originalText = resetBtn.textContent;
        resetBtn.textContent = 'Sending...';
        resetBtn.disabled = true;

        // Call Supabase password reset
        const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: window.location.origin + '/ZmartyUserApp/reset-password.html',
        });

        if (error) throw error;

        // Show success message
        document.getElementById('signin-form').style.display = 'none';
        document.getElementById('reset-password-form').style.display = 'none';
        document.getElementById('reset-success').style.display = 'block';

        // Update title
        const modal = document.querySelector('#forgot-password-overlay h2');
        if (modal) {
            modal.textContent = 'Check Your Email';
        }
        const subtitle = document.querySelector('#forgot-password-overlay p');
        if (subtitle) {
            subtitle.style.display = 'none';
        }
    } catch (error) {
        showError('Failed to send reset email. Please try again.');
        const resetBtn = event.target;
        resetBtn.textContent = 'Send Reset Link';
        resetBtn.disabled = false;
    }
}

// Make functions globally accessible for HTML onclick handlers
window.nextSlide = nextSlide;
window.previousSlide = previousSlide;
window.goToSlide = goToSlide;
window.skipOnboarding = skipOnboarding;
window.selectTier = selectTier;
window.continueWithEmail = continueWithEmail;
window.verifyCode = verifyCode;
window.resendCode = resendCode;
window.showError = showError;
// Make currentSlide a getter so it always returns the current value
Object.defineProperty(window, 'currentSlide', {
    get: function() { return currentSlide; },
    set: function(value) { currentSlide = value; }
});
window.completeProfile = completeProfile;
window.quickLogin = quickLogin;
window.simpleRegister = simpleRegister;
window.checkEmailExists = checkEmailExists;
window.sendPasswordReset = sendPasswordReset;
window.quickStart = quickStart;
window.moveToNext = moveToNext;
window.toggleContinueButton = toggleContinueButton;
window.checkPasswordStrength = checkPasswordStrength;
window.saveUserInfo = saveUserInfo;
window.goToDashboard = goToDashboard;
window.showForgotPasswordModal = showForgotPasswordModal;
window.showForgotPasswordSlide = showForgotPasswordSlide;
window.handleSignIn = handleSignIn;
window.closeForgotPasswordModal = closeForgotPasswordModal;
window.showResetPasswordForm = showResetPasswordForm;
window.showSignInForm = showSignInForm;
window.signInUser = signInUser;
window.sendPasswordReset = sendPasswordReset;
window.showPasswordMismatchPopup = showPasswordMismatchPopup;
// Progressive reveal functions already defined at top of file
