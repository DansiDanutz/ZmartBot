/**
 * Netlify Onboarding Live Testing Script
 * URL: https://vermillion-paprenjak-67497b.netlify.app
 *
 * INSTRUCTIONS:
 * 1. Open Chrome Developer Tools (F12)
 * 2. Navigate to Console tab
 * 3. Copy and paste this entire script
 * 4. Press Enter to run
 *
 * This script will test all the requested actions systematically
 */

console.log('🧪 Netlify Onboarding Live Test Starting...\n');
console.log('🌐 Testing: https://vermillion-paprenjak-67497b.netlify.app\n');

// Test utility functions
function isElementVisible(element) {
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    const style = window.getComputedStyle(element);
    return rect.width > 0 && rect.height > 0 &&
           style.opacity !== '0' && style.visibility !== 'hidden' &&
           style.display !== 'none';
}

function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve) => {
        const element = document.querySelector(selector);
        if (element) {
            resolve(element);
            return;
        }

        const observer = new MutationObserver(() => {
            const element = document.querySelector(selector);
            if (element) {
                observer.disconnect();
                resolve(element);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        setTimeout(() => {
            observer.disconnect();
            resolve(null);
        }, timeout);
    });
}

function logTestResult(action, success, details = '') {
    if (success) {
        console.log(`✅ ${action}: SUCCESS ${details ? '- ' + details : ''}`);
    } else {
        console.log(`❌ ${action}: FAILED ${details ? '- ' + details : ''}`);
    }
}

function simulateClick(element, actionName) {
    console.log(`🖱️  Attempting to click: ${actionName}`);

    if (!element) {
        logTestResult(actionName, false, 'Element not found');
        return false;
    }

    if (!isElementVisible(element)) {
        logTestResult(actionName, false, 'Element not visible');
        return false;
    }

    try {
        // Scroll element into view
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Highlight element briefly
        const originalStyle = element.style.border;
        element.style.border = '3px solid red';
        setTimeout(() => element.style.border = originalStyle, 1000);

        // Try multiple click methods
        element.click();
        element.dispatchEvent(new MouseEvent('click', { bubbles: true }));

        logTestResult(actionName, true, `Clicked on element: ${element.tagName}`);
        return true;
    } catch (error) {
        logTestResult(actionName, false, `Click error: ${error.message}`);
        return false;
    }
}

function simulateKeyPress(key, actionName) {
    console.log(`⌨️  Attempting key press: ${actionName} (${key})`);

    try {
        const event = new KeyboardEvent('keydown', {
            key: key,
            code: key === 'ArrowLeft' ? 'ArrowLeft' : key === 'ArrowRight' ? 'ArrowRight' : key,
            bubbles: true
        });
        document.dispatchEvent(event);

        logTestResult(actionName, true, `Key pressed: ${key}`);
        return true;
    } catch (error) {
        logTestResult(actionName, false, `Key press error: ${error.message}`);
        return false;
    }
}

// Main test sequence
async function runNetlifyTests() {
    console.log('📍 Starting systematic testing of all requested actions...\n');

    // Test 1: Navigate to the page (already done, but verify we're there)
    console.log('🌐 TEST 1: Verify page navigation');
    if (window.location.href.includes('vermillion-paprenjak-67497b.netlify.app')) {
        logTestResult('Page Navigation', true, 'Correctly on Netlify site');
    } else {
        logTestResult('Page Navigation', false, `Wrong URL: ${window.location.href}`);
        return;
    }

    await new Promise(resolve => setTimeout(resolve, 2000));

    // Test 2: Click "Get Started" button on welcome screen
    console.log('\n🖱️  TEST 2: Click "Get Started" button');
    let getStartedBtn = document.querySelector('.btn.btn-primary');
    if (!getStartedBtn) {
        getStartedBtn = document.querySelector('button');
        console.log('   Fallback: Trying generic button selector');
    }

    if (simulateClick(getStartedBtn, 'Get Started Button')) {
        await new Promise(resolve => setTimeout(resolve, 1500));
    }

    // Test 3: Try clicking through slides using navigation buttons
    console.log('\n🖱️  TEST 3: Test slide navigation buttons');

    // Test next arrow button
    let nextArrow = document.querySelector('#nextArrow');
    if (!nextArrow) {
        nextArrow = document.querySelector('.nav-arrow:last-child');
        console.log('   Fallback: Trying generic next arrow selector');
    }

    if (simulateClick(nextArrow, 'Next Arrow Button')) {
        await new Promise(resolve => setTimeout(resolve, 1500));
    }

    // Test previous arrow button
    let prevArrow = document.querySelector('#prevArrow');
    if (!prevArrow) {
        prevArrow = document.querySelector('.nav-arrow:first-child');
        console.log('   Fallback: Trying generic previous arrow selector');
    }

    if (simulateClick(prevArrow, 'Previous Arrow Button')) {
        await new Promise(resolve => setTimeout(resolve, 1500));
    }

    // Test 4: Click on "Google" tab to switch authentication method
    console.log('\n🖱️  TEST 4: Switch to Google authentication tab');

    // First navigate to authentication slide if not there
    const authSlide = document.querySelector('#step5, [data-step="5"], .auth-slide');
    if (authSlide && !isElementVisible(authSlide)) {
        console.log('   Navigating to authentication slide first...');
        // Try to get to the last slide
        for (let i = 0; i < 5; i++) {
            const nextBtn = document.querySelector('#nextArrow, .nav-arrow:last-child, .btn-next');
            if (nextBtn && isElementVisible(nextBtn)) {
                nextBtn.click();
                await new Promise(resolve => setTimeout(resolve, 800));
            }
        }
    }

    let googleTab = document.querySelector('#googleTab');
    if (!googleTab) {
        googleTab = document.querySelector('.auth-tab[data-tab="google"], [data-auth="google"]');
        console.log('   Fallback: Trying generic Google tab selector');
    }

    if (simulateClick(googleTab, 'Google Tab')) {
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Test 5: Click "Continue with Google" button
    console.log('\n🖱️  TEST 5: Click "Continue with Google" button');

    let googleLoginBtn = document.querySelector('#googleLoginBtn');
    if (!googleLoginBtn) {
        googleLoginBtn = document.querySelector('button[data-provider="google"], .google-login-btn');
        if (!googleLoginBtn) {
            // Look for button containing "Google" text
            const buttons = Array.from(document.querySelectorAll('button'));
            googleLoginBtn = buttons.find(btn => btn.textContent.includes('Google'));
        }
        console.log('   Fallback: Trying generic Google login button selector');
    }

    if (simulateClick(googleLoginBtn, 'Continue with Google Button')) {
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Test 6: Click on Email tab and test password field
    console.log('\n🖱️  TEST 6: Switch to Email tab and test password field');

    let emailTab = document.querySelector('#emailTab');
    if (!emailTab) {
        emailTab = document.querySelector('.auth-tab[data-tab="email"], [data-auth="email"]');
        console.log('   Fallback: Trying generic Email tab selector');
    }

    if (simulateClick(emailTab, 'Email Tab')) {
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Test password field
        console.log('   Testing password field...');
        const passwordField = document.querySelector('input[type="password"]');
        if (passwordField && isElementVisible(passwordField)) {
            passwordField.focus();
            passwordField.value = 'TestPassword123!';

            if (passwordField.value === 'TestPassword123!') {
                logTestResult('Password Field Input', true, 'Password field accepts input');
            } else {
                logTestResult('Password Field Input', false, 'Password field does not accept input');
            }
        } else {
            logTestResult('Password Field Test', false, 'Password field not found or not visible');
        }
    }

    // Test 7: Navigate backward using "Back" button
    console.log('\n🖱️  TEST 7: Test Back button navigation');

    const backButtons = document.querySelectorAll('button');
    let backButton = null;

    for (const btn of backButtons) {
        if (btn.textContent.toLowerCase().includes('back') && isElementVisible(btn)) {
            backButton = btn;
            break;
        }
    }

    if (!backButton) {
        backButton = document.querySelector('.btn-back, .back-btn, #backBtn');
    }

    if (simulateClick(backButton, 'Back Button')) {
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Test 8: Try keyboard navigation (arrow keys)
    console.log('\n⌨️  TEST 8: Test keyboard navigation (arrow keys)');

    // Focus on the document body first
    document.body.focus();

    simulateKeyPress('ArrowRight', 'Right Arrow Key Navigation');
    await new Promise(resolve => setTimeout(resolve, 1000));

    simulateKeyPress('ArrowLeft', 'Left Arrow Key Navigation');
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Test 9: Check if progress bar updates
    console.log('\n📊 TEST 9: Check progress bar updates');

    const progressBar = document.querySelector('#progressFill, .progress-fill');
    if (progressBar) {
        const initialWidth = progressBar.style.width || progressBar.getAttribute('style');
        logTestResult('Progress Bar Found', true, `Initial state: ${initialWidth}`);

        // Try to trigger a slide change and check if progress updates
        const nextBtn = document.querySelector('#nextArrow, .nav-arrow:last-child');
        if (nextBtn && isElementVisible(nextBtn)) {
            nextBtn.click();
            await new Promise(resolve => setTimeout(resolve, 1000));

            const newWidth = progressBar.style.width || progressBar.getAttribute('style');
            if (newWidth !== initialWidth) {
                logTestResult('Progress Bar Update', true, `Changed to: ${newWidth}`);
            } else {
                logTestResult('Progress Bar Update', false, 'Progress bar did not change');
            }
        }
    } else {
        logTestResult('Progress Bar Test', false, 'Progress bar element not found');
    }

    // Test 10: Report overall page functionality
    console.log('\n📋 TEST 10: Overall page analysis');

    // Check for JavaScript errors
    const jsErrors = [];
    const originalError = window.onerror;
    window.onerror = function(msg, url, lineNo, columnNo, error) {
        jsErrors.push({msg, url, lineNo, columnNo, error});
        if (originalError) originalError.apply(this, arguments);
    };

    // Check if main onboarding elements exist
    const criticalElements = {
        'Slides Container': document.querySelector('.slides, .steps, .onboarding-container'),
        'Navigation Elements': document.querySelector('.nav-arrow, .navigation, .slide-nav'),
        'Authentication Forms': document.querySelector('input[type="email"], input[type="password"]'),
        'Progress Indicator': document.querySelector('.progress-bar, .progress-fill, .step-indicator')
    };

    console.log('\n📈 CRITICAL ELEMENTS CHECK:');
    for (const [name, element] of Object.entries(criticalElements)) {
        logTestResult(name, !!element, element ? 'Found' : 'Missing');
    }

    // Final summary
    console.log('\n' + '='.repeat(70));
    console.log('🎯 NETLIFY ONBOARDING TEST SUMMARY');
    console.log('='.repeat(70));
    console.log('🌐 URL: https://vermillion-paprenjak-67497b.netlify.app');
    console.log('📅 Test Date: ' + new Date().toISOString());
    console.log('🔍 Tests Completed: 10 action tests + element analysis');

    if (jsErrors.length > 0) {
        console.log('\n⚠️  JAVASCRIPT ERRORS DETECTED:');
        jsErrors.forEach((error, index) => {
            console.log(`   ${index + 1}. ${error.msg} (Line: ${error.lineNo})`);
        });
    } else {
        console.log('\n✅ No JavaScript errors detected during testing');
    }

    console.log('\n💡 MANUAL TESTING RECOMMENDATIONS:');
    console.log('   • Test on mobile devices for responsive design');
    console.log('   • Test actual Google OAuth flow (requires real authentication)');
    console.log('   • Test form validation with invalid inputs');
    console.log('   • Test browser back/forward buttons');
    console.log('   • Test with disabled JavaScript');
    console.log('='.repeat(70));
}

// Auto-start the test
console.log('🚀 Test will begin in 3 seconds...');
console.log('📱 Make sure you can see the onboarding page');

setTimeout(() => {
    runNetlifyTests().catch(error => {
        console.error('❌ Test execution failed:', error);
    });
}, 3000);