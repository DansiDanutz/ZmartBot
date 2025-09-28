/**
 * Browser Console Test Script for Onboarding Flow
 * Copy and paste this into Chrome Developer Tools Console at localhost:8890
 */

console.log('🧪 Starting interactive onboarding test...\n');

// Test utility functions
function isElementVisible(element) {
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    const style = window.getComputedStyle(element);
    return rect.width > 0 && rect.height > 0 &&
           style.opacity !== '0' && style.visibility !== 'hidden' &&
           style.display !== 'none';
}

function logBug(slideNumber, description, expected = '', actual = '') {
    console.log(`❌ FIRST BUG FOUND - Slide ${slideNumber}: ${description}`);
    if (expected) console.log(`   Expected: ${expected}`);
    if (actual) console.log(`   Actual: ${actual}`);
    console.log(`\n🛑 STOPPING TEST HERE - FIX THIS BUG FIRST`);
    return false; // Stop testing
}

function logSuccess(slideNumber, description) {
    console.log(`✅ PASS - Slide ${slideNumber}: ${description}`);
    return true;
}

// Test Step 1: Welcome Screen
function testSlide1() {
    console.log('\n🔍 Testing SLIDE 1 (Welcome)...');

    const slide1 = document.querySelector('#step1');
    if (!slide1) {
        return logBug(1, 'Slide 1 element not found in DOM', 'Element with id="step1"', 'Element missing');
    }

    if (!isElementVisible(slide1)) {
        return logBug(1, 'Slide 1 is not visible', 'Slide should be visible on page load', 'Slide is hidden');
    }

    logSuccess(1, 'Slide 1 element found and visible');

    // Check if slide has 'active' class
    if (!slide1.classList.contains('active')) {
        return logBug(1, 'Slide 1 does not have active class', 'Should have class "active"', 'Missing active class');
    }

    logSuccess(1, 'Slide 1 has active class');

    // Test title visibility
    const title = slide1.querySelector('h1');
    if (!title || !isElementVisible(title)) {
        return logBug(1, 'Welcome title not visible', 'h1 element should be visible', 'Title hidden or missing');
    }

    logSuccess(1, `Title visible: "${title.textContent.trim()}"`);

    // Test Start Free Trial button
    const startBtn = slide1.querySelector('button');
    if (!startBtn || !isElementVisible(startBtn)) {
        return logBug(1, 'Start Free Trial button not visible', 'Button should be visible and clickable', 'Button hidden or missing');
    }

    logSuccess(1, `Start button found: "${startBtn.textContent.trim()}"`);

    // Test button click functionality
    try {
        console.log('🖱️  Clicking Start Free Trial button...');
        startBtn.click();

        // Wait a moment for navigation
        setTimeout(() => {
            const currentStep = document.querySelector('.step.active');
            if (!currentStep || currentStep.id === 'step1') {
                logBug(1, 'Button click did not navigate to next slide', 'Should navigate to slide 2', 'Still on slide 1');
                return false;
            }

            logSuccess(1, `Button click worked - navigated to ${currentStep.id}`);

            // Continue testing slide 2
            testSlide2();
        }, 500);

    } catch (error) {
        return logBug(1, 'Start button click failed', 'Button should be clickable', `Error: ${error.message}`);
    }

    return true;
}

// Test Step 2: AI Models
function testSlide2() {
    console.log('\n🔍 Testing SLIDE 2 (AI Models)...');

    const slide2 = document.querySelector('#step2');
    if (!slide2) {
        return logBug(2, 'Slide 2 element not found', 'Element with id="step2"', 'Element missing');
    }

    if (!isElementVisible(slide2)) {
        return logBug(2, 'Slide 2 is not visible', 'Should be visible after navigation', 'Slide is hidden');
    }

    if (!slide2.classList.contains('active')) {
        return logBug(2, 'Slide 2 does not have active class', 'Should have class "active"', 'Missing active class');
    }

    logSuccess(2, 'Slide 2 is visible and active');

    // Test AI Models title
    const title = slide2.querySelector('h2');
    if (!title || !isElementVisible(title)) {
        return logBug(2, 'AI Models title not visible', 'h2 element should be visible', 'Title hidden or missing');
    }

    logSuccess(2, `Title visible: "${title.textContent.trim()}"`);

    // Test AI model cards
    const modelCards = slide2.querySelectorAll('.ai-model-card, .model-card, .card');
    if (modelCards.length === 0) {
        return logBug(2, 'No AI model cards found', 'Should have AI model cards', 'No cards found');
    }

    // Check if all cards are visible
    let visibleCards = 0;
    modelCards.forEach(card => {
        if (isElementVisible(card)) visibleCards++;
    });

    if (visibleCards === 0) {
        return logBug(2, 'AI model cards not visible', 'Model cards should be visible', 'All cards hidden');
    }

    logSuccess(2, `${visibleCards} AI model cards found and visible`);

    // Test Continue button
    const continueBtn = slide2.querySelector('button');
    if (!continueBtn || !isElementVisible(continueBtn)) {
        return logBug(2, 'Continue button not found', 'Should have Continue button', 'Button missing or hidden');
    }

    logSuccess(2, `Continue button found: "${continueBtn.textContent.trim()}"`);

    // Click continue to test slide 3
    console.log('🖱️  Clicking Continue button...');
    continueBtn.click();

    setTimeout(() => {
        testSlide3();
    }, 500);

    return true;
}

// Test Step 3: Exchanges
function testSlide3() {
    console.log('\n🔍 Testing SLIDE 3 (Exchanges)...');

    const slide3 = document.querySelector('#step3');
    if (!slide3) {
        return logBug(3, 'Slide 3 element not found', 'Element with id="step3"', 'Element missing');
    }

    if (!isElementVisible(slide3) || !slide3.classList.contains('active')) {
        return logBug(3, 'Slide 3 not active', 'Should be visible and active', 'Slide not showing');
    }

    logSuccess(3, 'Slide 3 is visible and active');

    // Test exchanges title
    const title = slide3.querySelector('h2');
    if (!title || !isElementVisible(title)) {
        return logBug(3, 'Exchanges title not visible', 'h2 element should be visible', 'Title hidden or missing');
    }

    logSuccess(3, `Title visible: "${title.textContent.trim()}"`);

    // Test exchange cards/logos
    const exchangeElements = slide3.querySelectorAll('.exchange-card, .exchange-logo, .grid-item, .card');
    if (exchangeElements.length === 0) {
        return logBug(3, 'No exchange elements found', 'Should have exchange cards or logos', 'No exchange elements found');
    }

    logSuccess(3, `${exchangeElements.length} exchange elements found`);

    // Test Continue button
    const continueBtn = slide3.querySelector('button');
    if (!continueBtn || !isElementVisible(continueBtn)) {
        return logBug(3, 'Continue button not found', 'Should have Continue button', 'Button missing');
    }

    // Click continue to test slide 4
    console.log('🖱️  Clicking Continue button...');
    continueBtn.click();

    setTimeout(() => {
        testSlide4();
    }, 500);

    return true;
}

// Test Step 4: Risk Management
function testSlide4() {
    console.log('\n🔍 Testing SLIDE 4 (Risk Management)...');

    const slide4 = document.querySelector('#step4');
    if (!slide4) {
        return logBug(4, 'Slide 4 element not found', 'Element with id="step4"', 'Element missing');
    }

    if (!isElementVisible(slide4) || !slide4.classList.contains('active')) {
        return logBug(4, 'Slide 4 not active', 'Should be visible and active', 'Slide not showing');
    }

    logSuccess(4, 'Slide 4 is visible and active');

    // Test risk management title
    const title = slide4.querySelector('h2');
    if (!title || !isElementVisible(title)) {
        return logBug(4, 'Risk Management title not visible', 'h2 element should be visible', 'Title hidden or missing');
    }

    logSuccess(4, `Title visible: "${title.textContent.trim()}"`);

    // Test risk feature cards
    const riskCards = slide4.querySelectorAll('.risk-card, .feature-card, .card, .grid-item');
    if (riskCards.length === 0) {
        return logBug(4, 'No risk feature cards found', 'Should have risk management feature cards', 'No cards found');
    }

    logSuccess(4, `${riskCards.length} risk feature elements found`);

    // Test Continue button
    const continueBtn = slide4.querySelector('button');
    if (!continueBtn || !isElementVisible(continueBtn)) {
        return logBug(4, 'Continue button not found', 'Should have Continue button', 'Button missing');
    }

    // Click continue to test slide 5 (Authentication)
    console.log('🖱️  Clicking Continue button...');
    continueBtn.click();

    setTimeout(() => {
        testSlide5();
    }, 500);

    return true;
}

// Test Step 5: Authentication
function testSlide5() {
    console.log('\n🔍 Testing SLIDE 5 (Authentication)...');

    const slide5 = document.querySelector('#step5');
    if (!slide5) {
        return logBug(5, 'Slide 5 element not found', 'Element with id="step5"', 'Element missing');
    }

    if (!isElementVisible(slide5) || !slide5.classList.contains('active')) {
        return logBug(5, 'Slide 5 not active', 'Should be visible and active', 'Slide not showing');
    }

    logSuccess(5, 'Slide 5 (Authentication) is visible and active');

    // Test authentication title
    const title = slide5.querySelector('h2');
    if (!title || !isElementVisible(title)) {
        return logBug(5, 'Authentication title not visible', 'h2 element should be visible', 'Title hidden or missing');
    }

    logSuccess(5, `Title visible: "${title.textContent.trim()}"`);

    // Test email input field
    const emailInput = slide5.querySelector('input[type="email"]');
    if (!emailInput || !isElementVisible(emailInput)) {
        return logBug(5, 'Email input field not found or visible', 'Should have visible email input field', 'Input missing or hidden');
    }

    logSuccess(5, 'Email input field found and visible');

    // Test password input field
    const passwordInput = slide5.querySelector('input[type="password"]');
    if (!passwordInput || !isElementVisible(passwordInput)) {
        return logBug(5, 'Password input field not found or visible', 'Should have visible password input field', 'Input missing or hidden');
    }

    logSuccess(5, 'Password input field found and visible');

    // Test form submission button
    const submitBtn = slide5.querySelector('button[type="submit"], .btn-primary, button');
    if (!submitBtn || !isElementVisible(submitBtn)) {
        return logBug(5, 'Submit button not found or visible', 'Should have visible submit button', 'Button missing or hidden');
    }

    logSuccess(5, `Submit button found: "${submitBtn.textContent.trim()}"`);

    // Test input functionality
    console.log('🖱️  Testing email input...');
    emailInput.focus();
    emailInput.value = 'test@example.com';

    if (emailInput.value !== 'test@example.com') {
        return logBug(5, 'Email input field not accepting input', 'Should accept email input', 'Input value not set');
    }

    logSuccess(5, 'Email input field accepts input');

    console.log('🖱️  Testing password input...');
    passwordInput.focus();
    passwordInput.value = 'testpassword123';

    if (passwordInput.value !== 'testpassword123') {
        return logBug(5, 'Password input field not accepting input', 'Should accept password input', 'Input value not set');
    }

    logSuccess(5, 'Password input field accepts input');

    // Final success message
    console.log('\n' + '='.repeat(60));
    console.log('🎉 ALL INTERACTIVE TESTS PASSED!');
    console.log('✅ All 5 slides are working correctly:');
    console.log('   • Slide 1: Welcome screen loads and navigates');
    console.log('   • Slide 2: AI Models display and continue works');
    console.log('   • Slide 3: Exchanges show and navigation works');
    console.log('   • Slide 4: Risk Management displays correctly');
    console.log('   • Slide 5: Authentication form is functional');
    console.log('='.repeat(60));

    return true;
}

// Start the test
console.log('🎬 Ready to start testing! The test will begin in 2 seconds...');
console.log('📱 Make sure you are on the first slide (Welcome page)');

setTimeout(() => {
    testSlide1();
}, 2000);