// ZmartyChat Onboarding - FIXED VERSION
// All functions are immediately available on window object

// Initialize current slide
window.currentSlide = 1;
const totalSlides = 8;

// CRITICAL FIX: Define ALL navigation functions IMMEDIATELY on window
window.nextSlide = function() {
    console.log('nextSlide called, current:', window.currentSlide);
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

        window.currentSlide = slideNumber;
        updateDots();
        updateNextButton();
    }
};

// Update navigation dots
function updateDots() {
    document.querySelectorAll('.navigation-dots .dot').forEach((dot, index) => {
        if (index + 1 === window.currentSlide) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}

// Update next button text
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

// Email checking with progressive reveal
window.checkEmailExists = function() {
    const emailInput = document.getElementById('register-email');
    if (!emailInput) return;

    const email = emailInput.value.trim();
    const passwordField = document.getElementById('register-password');

    // Show password field if email has content
    if (email.length > 0 && email.includes('@')) {
        if (passwordField) {
            passwordField.style.display = 'block';
            passwordField.style.visibility = 'visible';
            passwordField.style.opacity = '1';
        }
    } else {
        if (passwordField) {
            passwordField.style.display = 'none';
        }
    }
};

// Show confirm password field
window.showConfirmPasswordField = function() {
    const passwordField = document.getElementById('register-password');
    const confirmField = document.getElementById('confirm-password');

    if (passwordField && confirmField && passwordField.value.length > 0) {
        confirmField.style.display = 'block';
        confirmField.style.visibility = 'visible';
        confirmField.style.opacity = '1';
    }
};

// Check if can register
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

// Simple register function
window.simpleRegister = function() {
    console.log('Register clicked');
    const email = document.getElementById('register-email')?.value;
    const password = document.getElementById('register-password')?.value;

    if (email && password) {
        // Move to verification slide
        goToSlide(5);
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Onboarding initialized');

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

    // Initialize first slide
    window.goToSlide(1);
});

// Expose all functions globally for debugging
window.onboardingFunctions = {
    nextSlide: window.nextSlide,
    previousSlide: window.previousSlide,
    goToSlide: window.goToSlide,
    checkEmailExists: window.checkEmailExists,
    showConfirmPasswordField: window.showConfirmPasswordField,
    checkIfCanRegister: window.checkIfCanRegister,
    simpleRegister: window.simpleRegister
};

console.log('✅ Onboarding functions loaded:', Object.keys(window.onboardingFunctions));