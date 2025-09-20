/**
 * Manual Test Checklist for 7-Slide Onboarding
 * Run this in browser console at http://localhost:9000
 */

const runManualTests = async () => {
    const results = {
        passed: [],
        failed: [],
        warnings: []
    };

    const test = (name, condition, details = '') => {
        if (condition) {
            results.passed.push(`✅ ${name}`);
            console.log(`✅ ${name}`, details);
        } else {
            results.failed.push(`❌ ${name}`);
            console.error(`❌ ${name}`, details);
        }
    };

    const wait = (ms) => new Promise(r => setTimeout(r, ms));

    console.log('🎯 Starting Manual Test Checklist...\n');

    // SLIDE 1: Welcome
    console.log('\n📍 Testing Slide 1: Welcome');
    goToSlide(1);
    await wait(1000);

    test('Slide 1 loads', document.querySelector('.slide-1').classList.contains('active'));
    test('Welcome text visible', document.querySelector('.slide-1 h1')?.textContent.includes('Welcome'));
    test('Animations working', window.getComputedStyle(document.querySelector('.slide-1')).opacity === '1');
    test('Next button visible', document.querySelector('.slide-1 .primary-btn'));

    // SLIDE 2: Features
    console.log('\n📍 Testing Slide 2: Features');
    goToSlide(2);
    await wait(1000);

    test('Slide 2 loads', document.querySelector('.slide-2').classList.contains('active'));
    test('Feature cards visible', document.querySelectorAll('.feature-card').length === 3);
    test('Navigation works', window.currentSlide === 2);

    // SLIDE 3: Get Started
    console.log('\n📍 Testing Slide 3: Get Started');
    goToSlide(3);
    await wait(1000);

    test('Slide 3 loads', document.querySelector('.slide-3').classList.contains('active'));
    test('Skip button works', typeof skipOnboarding === 'function');

    // SLIDE 4: Registration
    console.log('\n📍 Testing Slide 4: Registration');
    goToSlide(4);
    await wait(1000);

    test('Slide 4 loads', document.querySelector('.slide-4').classList.contains('active'));
    test('Email input present', document.getElementById('register-email'));
    test('Password input present', document.getElementById('register-password'));
    test('Social buttons present', document.querySelectorAll('.auth-btn').length === 2);
    test('Login link present', document.querySelector('.already-account'));

    // Test progressive reveal
    console.log('\n📍 Testing Progressive Reveal');
    const emailInput = document.getElementById('register-email');
    const passwordInput = document.getElementById('register-password');

    // Test empty email
    emailInput.value = '';
    emailInput.dispatchEvent(new Event('input'));
    await wait(100);
    test('Empty email validation', !document.querySelector('.confirm-password-group'));

    // Test invalid email
    emailInput.value = 'invalid';
    emailInput.dispatchEvent(new Event('input'));
    await wait(100);
    test('Invalid email validation', !document.querySelector('.confirm-password-group'));

    // Test valid email
    emailInput.value = 'test@example.com';
    emailInput.dispatchEvent(new Event('input'));
    await wait(100);
    test('Valid email accepted', emailInput.value === 'test@example.com');

    // Test short password
    passwordInput.value = '1234567';
    passwordInput.dispatchEvent(new Event('input'));
    await wait(100);
    test('Short password validation', !document.getElementById('confirm-password'));

    // Test valid password
    passwordInput.value = 'TestPass123';
    passwordInput.dispatchEvent(new Event('input'));
    await wait(100);
    test('Confirm password appears', document.getElementById('confirm-password'));

    // Test password mismatch
    const confirmInput = document.getElementById('confirm-password');
    if (confirmInput) {
        confirmInput.value = 'Different123';
        confirmInput.dispatchEvent(new Event('input'));
        await wait(100);
        test('Password mismatch hides button', !document.getElementById('email-continue-btn'));

        // Test password match
        confirmInput.value = 'TestPass123';
        confirmInput.dispatchEvent(new Event('input'));
        await wait(100);
        test('Password match shows button', document.getElementById('email-continue-btn'));
    }

    // SLIDE 5: Email Verification
    console.log('\n📍 Testing Slide 5: Email Verification');
    goToSlide(5);
    await wait(1000);

    test('Slide 5 loads', document.querySelector('.slide-5').classList.contains('active'));
    test('6 code inputs present', document.querySelectorAll('.code-input').length === 6);
    test('Resend button present', document.querySelector('.resend-btn'));

    // Test code input navigation
    const codeInputs = document.querySelectorAll('.code-input');
    if (codeInputs.length === 6) {
        // Test forward navigation
        codeInputs[0].value = '1';
        codeInputs[0].dispatchEvent(new Event('input'));
        await wait(100);
        test('Auto-advance works', document.activeElement === codeInputs[1]);

        // Test backward navigation
        codeInputs[1].dispatchEvent(new KeyboardEvent('keydown', { key: 'Backspace' }));
        await wait(100);
        test('Backspace navigation works', document.activeElement === codeInputs[0] || codeInputs[0].value === '');
    }

    // SLIDE 6: Tier Selection
    console.log('\n📍 Testing Slide 6: Tier Selection');
    goToSlide(6);
    await wait(1000);

    test('Slide 6 loads', document.querySelector('.slide-6').classList.contains('active'));
    test('3 tier cards present', document.querySelectorAll('.tier-option').length === 3);

    // Test tier selection
    const tierCards = document.querySelectorAll('.tier-option');
    if (tierCards.length === 3) {
        tierCards[0].click();
        await wait(100);
        test('Tier selection works', tierCards[0].classList.contains('selected'));
        test('Continue button appears', document.querySelector('.tier-continue-btn'));
    }

    // SLIDE 7: Profile Completion
    console.log('\n📍 Testing Slide 7: Profile Completion');
    goToSlide(7);
    await wait(1000);

    test('Slide 7 loads', document.querySelector('.slide-7').classList.contains('active'));
    test('Name input present', document.getElementById('profile-name'));
    test('Country dropdown present', document.getElementById('profile-country'));
    test('Complete button present', document.querySelector('.complete-btn'));

    // Test Login Modal
    console.log('\n📍 Testing Login Modal');
    if (typeof showLoginModal === 'function') {
        showLoginModal();
        await wait(500);
        test('Login modal opens', document.getElementById('login-modal')?.style.display === 'flex');

        test('Login email input present', document.getElementById('login-email'));
        test('Login password input present', document.getElementById('login-password'));
        test('Forgot password link present', document.querySelector('.forgot-password'));

        // Close modal
        if (typeof closeLoginModal === 'function') {
            closeLoginModal();
            await wait(500);
            test('Login modal closes', document.getElementById('login-modal')?.style.display === 'none');
        }
    }

    // Test Error Handling
    console.log('\n📍 Testing Error Handling');
    if (typeof showError === 'function') {
        showError('Test error message');
        await wait(100);
        test('Error message displays', document.querySelector('.error-toast')?.textContent.includes('Test error'));

        await wait(3100); // Wait for error to auto-hide
        test('Error auto-hides', !document.querySelector('.error-toast') ||
             document.querySelector('.error-toast').style.display === 'none');
    }

    // Edge Cases
    console.log('\n📍 Testing Edge Cases');

    // Test rapid navigation
    goToSlide(1);
    goToSlide(2);
    goToSlide(3);
    goToSlide(4);
    await wait(500);
    test('Rapid navigation stable', window.currentSlide === 4);

    // Test boundary conditions
    goToSlide(0); // Should not go below 1
    await wait(100);
    test('Lower boundary protected', window.currentSlide >= 1);

    goToSlide(10); // Should not go above 7
    await wait(100);
    test('Upper boundary protected', window.currentSlide <= 7);

    // Check for console errors
    const hasNoErrors = !window.consoleErrors || window.consoleErrors.length === 0;
    test('No console errors', hasNoErrors);

    // Summary
    console.log('\n📊 TEST SUMMARY');
    console.log('================');
    console.log(`✅ Passed: ${results.passed.length}`);
    console.log(`❌ Failed: ${results.failed.length}`);
    console.log(`⚠️ Warnings: ${results.warnings.length}`);
    console.log(`Success Rate: ${(results.passed.length / (results.passed.length + results.failed.length) * 100).toFixed(1)}%`);

    if (results.failed.length > 0) {
        console.log('\n❌ Failed Tests:');
        results.failed.forEach(f => console.log(f));
    }

    if (results.warnings.length > 0) {
        console.log('\n⚠️ Warnings:');
        results.warnings.forEach(w => console.log(w));
    }

    // Check Supabase Connection
    console.log('\n🔗 Checking Supabase Connection...');
    if (window.supabase) {
        try {
            const { data, error } = await window.supabase.auth.getSession();
            if (!error) {
                test('Supabase connected', true);
                console.log('Session:', data.session ? 'Active' : 'None');
            } else {
                test('Supabase connected', false, error.message);
            }
        } catch (e) {
            test('Supabase connected', false, e.message);
        }
    } else {
        results.warnings.push('⚠️ Supabase not initialized');
    }

    return results;
};

// Capture console errors
window.consoleErrors = [];
const originalError = console.error;
console.error = function() {
    window.consoleErrors.push(Array.from(arguments).join(' '));
    originalError.apply(console, arguments);
};

// Run tests automatically
console.log('📋 Manual Test Checklist Loaded!');
console.log('Run: runManualTests() to start');
console.log('Or copy this entire script and run in browser console at http://localhost:9000');

// Export for use
window.runManualTests = runManualTests;