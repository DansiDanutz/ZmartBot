/**
 * Systematic Onboarding Testing Script
 * Tests all slides and documents bugs found
 */

// Test configuration
const TEST_CONFIG = {
    baseUrl: 'http://localhost:8888',
    mobileWidth: 375,
    slides: [
        { id: 1, name: 'Welcome', selector: '#step-1' },
        { id: 2, name: 'AI Models', selector: '#step-2' },
        { id: 3, name: 'Exchanges', selector: '#step-3' },
        { id: 4, name: 'Risk Management', selector: '#step-4' },
        { id: 5, name: 'Authentication', selector: '#step-5' },
        { id: 7, name: 'Email Verification', selector: '#step-7' },
        { id: 10, name: 'Tier Selection', selector: '#step-10' },
        { id: 11, name: 'Profile Setup', selector: '#step-11' },
        { id: 12, name: 'Success', selector: '#step-12' }
    ]
};

// Bug tracking
let bugsFound = [];

function logBug(slideNumber, description, priority = 'Medium', expected = '', actual = '') {
    const bug = {
        slide: slideNumber,
        description,
        priority,
        expected,
        actual,
        timestamp: new Date().toISOString()
    };
    bugsFound.push(bug);
    console.log(`🐛 BUG FOUND - Slide ${slideNumber}: ${description} [${priority}]`);
    if (expected) console.log(`   Expected: ${expected}`);
    if (actual) console.log(`   Actual: ${actual}`);
}

function logSuccess(slideNumber, description) {
    console.log(`✅ PASS - Slide ${slideNumber}: ${description}`);
}

// Test utility functions
function isElementVisible(element) {
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    const style = window.getComputedStyle(element);

    return rect.width > 0 &&
           rect.height > 0 &&
           style.opacity !== '0' &&
           style.visibility !== 'hidden' &&
           style.display !== 'none';
}

function checkResponsiveness() {
    const originalWidth = window.innerWidth;

    // Test mobile responsiveness
    window.resizeTo(TEST_CONFIG.mobileWidth, 667);
    return new Promise(resolve => {
        setTimeout(() => {
            const isMobileResponsive = document.documentElement.clientWidth <= TEST_CONFIG.mobileWidth + 50;
            window.resizeTo(originalWidth, window.innerHeight);
            setTimeout(() => resolve(isMobileResponsive), 100);
        }, 100);
    });
}

// Individual slide tests
function testSlide1Welcome() {
    console.log('\n🔍 Testing SLIDE 1 (Welcome)...');

    const slide = document.querySelector('#step-1');
    if (!slide) {
        logBug(1, 'Slide 1 element not found', 'Critical', 'Slide should exist', 'Element missing');
        return;
    }

    // Test text visibility
    const titleElement = slide.querySelector('h1, .title, .main-title');
    if (!titleElement || !isElementVisible(titleElement)) {
        logBug(1, 'Main title not visible', 'High', 'Title should be visible', 'Title hidden or missing');
    } else {
        logSuccess(1, 'Main title is visible');
    }

    // Test Start Free Trial button
    const startButton = slide.querySelector('button:contains("Start Free Trial"), .btn-primary, [data-action="start"]');
    if (!startButton || !isElementVisible(startButton)) {
        logBug(1, 'Start Free Trial button not found or visible', 'Critical', 'Button should be visible and clickable', 'Button missing or hidden');
    } else {
        logSuccess(1, 'Start Free Trial button found');

        // Test button functionality
        try {
            startButton.click();
            logSuccess(1, 'Start Free Trial button is clickable');
        } catch (error) {
            logBug(1, 'Start Free Trial button click error', 'High', 'Button should be clickable', `Error: ${error.message}`);
        }
    }

    // Test features grid
    const featuresGrid = slide.querySelector('.features-grid, .grid, .features');
    if (!featuresGrid || !isElementVisible(featuresGrid)) {
        logBug(1, 'Features grid not found', 'Medium', 'Features grid should be visible', 'Grid missing or hidden');
    } else {
        logSuccess(1, 'Features grid found');

        const featureItems = featuresGrid.querySelectorAll('.feature-item, .feature, .grid-item');
        if (featureItems.length === 0) {
            logBug(1, 'No feature items in grid', 'Medium', 'Grid should contain feature items', 'No items found');
        } else {
            logSuccess(1, `Features grid contains ${featureItems.length} items`);
        }
    }

    console.log('✓ Slide 1 testing completed');
}

function testSlide2AIModels() {
    console.log('\n🔍 Testing SLIDE 2 (AI Models)...');

    const slide = document.querySelector('#step-2');
    if (!slide) {
        logBug(2, 'Slide 2 element not found', 'Critical');
        return;
    }

    // Test AI model cards
    const modelCards = slide.querySelectorAll('.ai-model-card, .model-card, .card');
    const expectedModels = ['Claude', 'GPT-4', 'Gemini', 'Grok'];

    if (modelCards.length !== 4) {
        logBug(2, `Incorrect number of AI model cards`, 'High', '4 model cards', `${modelCards.length} cards found`);
    } else {
        logSuccess(2, '4 AI model cards found');
    }

    // Test card responsiveness
    modelCards.forEach((card, index) => {
        if (!isElementVisible(card)) {
            logBug(2, `AI model card ${index + 1} not visible`, 'Medium');
        }
    });

    // Test Continue button
    const continueButton = slide.querySelector('button:contains("Continue"), .btn-continue, [data-action="continue"]');
    if (!continueButton || !isElementVisible(continueButton)) {
        logBug(2, 'Continue button not found', 'High');
    } else {
        logSuccess(2, 'Continue button found');
    }

    console.log('✓ Slide 2 testing completed');
}

function testSlide3Exchanges() {
    console.log('\n🔍 Testing SLIDE 3 (Exchanges)...');

    const slide = document.querySelector('#step-3');
    if (!slide) {
        logBug(3, 'Slide 3 element not found', 'Critical');
        return;
    }

    // Test exchange cards
    const exchangeCards = slide.querySelectorAll('.exchange-card, .card');
    const expectedExchanges = ['Binance', 'Coinbase', 'Kraken'];

    if (exchangeCards.length === 0) {
        logBug(3, 'No exchange cards found', 'High', 'Multiple exchange cards', 'No cards found');
    } else {
        logSuccess(3, `${exchangeCards.length} exchange cards found`);
    }

    // Test grid layout
    const grid = slide.querySelector('.grid, .exchanges-grid');
    if (grid) {
        const gridStyle = window.getComputedStyle(grid);
        if (!gridStyle.display.includes('grid') && !gridStyle.display.includes('flex')) {
            logBug(3, 'Exchange cards not using proper grid layout', 'Medium');
        } else {
            logSuccess(3, 'Exchange cards using grid layout');
        }
    }

    console.log('✓ Slide 3 testing completed');
}

function testSlide4RiskManagement() {
    console.log('\n🔍 Testing SLIDE 4 (Risk Management)...');

    const slide = document.querySelector('#step-4');
    if (!slide) {
        logBug(4, 'Slide 4 element not found', 'Critical');
        return;
    }

    // Test risk feature cards
    const riskCards = slide.querySelectorAll('.risk-card, .feature-card, .card');
    if (riskCards.length !== 4) {
        logBug(4, `Incorrect number of risk feature cards`, 'Medium', '4 risk cards', `${riskCards.length} cards found`);
    } else {
        logSuccess(4, '4 risk feature cards found');
    }

    // Test icons in cards
    riskCards.forEach((card, index) => {
        const icon = card.querySelector('svg, .icon, i');
        if (!icon) {
            logBug(4, `Risk card ${index + 1} missing icon`, 'Low');
        }
    });

    // Test bullet points
    const bulletPoints = slide.querySelectorAll('ul li, .bullet-point');
    if (bulletPoints.length === 0) {
        logBug(4, 'No bullet points found', 'Medium', 'Bullet points should be visible', 'No bullet points found');
    } else {
        logSuccess(4, `${bulletPoints.length} bullet points found`);
    }

    console.log('✓ Slide 4 testing completed');
}

function testSlide5Authentication() {
    console.log('\n🔍 Testing SLIDE 5 (Authentication)...');

    const slide = document.querySelector('#step-5');
    if (!slide) {
        logBug(5, 'Slide 5 element not found', 'Critical');
        return;
    }

    // Test email/Google tabs
    const emailTab = slide.querySelector('[data-tab="email"], .tab-email');
    const googleTab = slide.querySelector('[data-tab="google"], .tab-google');

    if (!emailTab && !googleTab) {
        logBug(5, 'Authentication tabs not found', 'High', 'Email and Google tabs', 'No tabs found');
    } else {
        logSuccess(5, 'Authentication tabs found');
    }

    // Test form fields
    const emailInput = slide.querySelector('input[type="email"], input[name="email"]');
    const passwordInput = slide.querySelector('input[type="password"], input[name="password"]');

    if (!emailInput) {
        logBug(5, 'Email input field not found', 'High');
    }
    if (!passwordInput) {
        logBug(5, 'Password input field not found', 'High');
    }

    // Test Create Account button
    const createAccountButton = slide.querySelector('button:contains("Create Account"), .btn-create-account');
    if (!createAccountButton) {
        logBug(5, 'Create Account button not found', 'High');
    } else {
        logSuccess(5, 'Create Account button found');
    }

    console.log('✓ Slide 5 testing completed');
}

function testSlide7EmailVerification() {
    console.log('\n🔍 Testing SLIDE 7 (Email Verification)...');

    const slide = document.querySelector('#step-7');
    if (!slide) {
        logBug(7, 'Slide 7 element not found', 'Critical');
        return;
    }

    // Test OTP input fields
    const otpInputs = slide.querySelectorAll('input[type="text"][maxlength="1"], .otp-input');
    if (otpInputs.length !== 6) {
        logBug(7, `Incorrect number of OTP inputs`, 'High', '6 OTP input fields', `${otpInputs.length} inputs found`);
    } else {
        logSuccess(7, '6 OTP input fields found');
    }

    // Test Verify Code button
    const verifyButton = slide.querySelector('button:contains("Verify"), .btn-verify');
    if (!verifyButton) {
        logBug(7, 'Verify Code button not found', 'High');
    } else {
        logSuccess(7, 'Verify Code button found');
    }

    // Test Resend Code functionality
    const resendButton = slide.querySelector('button:contains("Resend"), .btn-resend');
    if (!resendButton) {
        logBug(7, 'Resend Code button not found', 'Medium');
    } else {
        logSuccess(7, 'Resend Code button found');
    }

    console.log('✓ Slide 7 testing completed');
}

function testSlide10TierSelection() {
    console.log('\n🔍 Testing SLIDE 10 (Tier Selection)...');

    const slide = document.querySelector('#step-10');
    if (!slide) {
        logBug(10, 'Slide 10 element not found', 'Critical');
        return;
    }

    // Test pricing cards
    const pricingCards = slide.querySelectorAll('.pricing-card, .tier-card, .plan-card');
    if (pricingCards.length !== 3) {
        logBug(10, `Incorrect number of pricing cards`, 'High', '3 pricing cards (Free, Gold, Premium)', `${pricingCards.length} cards found`);
    } else {
        logSuccess(10, '3 pricing cards found');
    }

    // Test card selection
    pricingCards.forEach((card, index) => {
        card.addEventListener('click', () => {
            if (!card.classList.contains('selected')) {
                logBug(10, `Card ${index + 1} selection not working`, 'Medium');
            } else {
                logSuccess(10, `Card ${index + 1} selection working`);
            }
        });
    });

    // Test Continue button
    const continueButton = slide.querySelector('button:contains("Continue"), .btn-continue');
    if (!continueButton) {
        logBug(10, 'Continue button not found', 'High');
    }

    console.log('✓ Slide 10 testing completed');
}

function testSlide11ProfileSetup() {
    console.log('\n🔍 Testing SLIDE 11 (Profile Setup)...');

    const slide = document.querySelector('#step-11');
    if (!slide) {
        logBug(11, 'Slide 11 element not found', 'Critical');
        return;
    }

    // Test form fields
    const nameInput = slide.querySelector('input[name="name"], input[type="text"]');
    const countrySelect = slide.querySelector('select[name="country"], .country-select');

    if (!nameInput) {
        logBug(11, 'Name input field not found', 'High');
    } else {
        logSuccess(11, 'Name input field found');
    }

    if (!countrySelect) {
        logBug(11, 'Country dropdown not found', 'High');
    } else {
        logSuccess(11, 'Country dropdown found');

        // Test dropdown options
        const options = countrySelect.querySelectorAll('option');
        if (options.length < 10) {
            logBug(11, 'Country dropdown has too few options', 'Medium', 'Many country options', `Only ${options.length} options`);
        }
    }

    // Test Complete Setup button
    const completeButton = slide.querySelector('button:contains("Complete"), .btn-complete');
    if (!completeButton) {
        logBug(11, 'Complete Setup button not found', 'High');
    } else {
        logSuccess(11, 'Complete Setup button found');
    }

    console.log('✓ Slide 11 testing completed');
}

function testSlide12Success() {
    console.log('\n🔍 Testing SLIDE 12 (Success)...');

    const slide = document.querySelector('#step-12');
    if (!slide) {
        logBug(12, 'Slide 12 element not found', 'Critical');
        return;
    }

    // Test completion message
    const successMessage = slide.querySelector('.success-message, h1, .title');
    if (!successMessage || !isElementVisible(successMessage)) {
        logBug(12, 'Success completion message not visible', 'High');
    } else {
        logSuccess(12, 'Success completion message found');
    }

    // Test final CTAs
    const ctaButtons = slide.querySelectorAll('button, .btn, .cta');
    if (ctaButtons.length === 0) {
        logBug(12, 'No final CTA buttons found', 'Medium');
    } else {
        logSuccess(12, `${ctaButtons.length} CTA buttons found`);
    }

    console.log('✓ Slide 12 testing completed');
}

// Main testing function
async function runSystematicTests() {
    console.log('🚀 Starting Systematic Onboarding Testing...\n');

    // Wait for page to load
    await new Promise(resolve => {
        if (document.readyState === 'complete') {
            resolve();
        } else {
            window.addEventListener('load', resolve);
        }
    });

    // Test each slide
    testSlide1Welcome();
    testSlide2AIModels();
    testSlide3Exchanges();
    testSlide4RiskManagement();
    testSlide5Authentication();
    testSlide7EmailVerification();
    testSlide10TierSelection();
    testSlide11ProfileSetup();
    testSlide12Success();

    // Test mobile responsiveness
    console.log('\n🔍 Testing Mobile Responsiveness...');
    const isMobileResponsive = await checkResponsiveness();
    if (!isMobileResponsive) {
        logBug('General', 'Application not mobile responsive', 'High', 'Should work on 375px width', 'Layout breaks on mobile');
    } else {
        logSuccess('General', 'Mobile responsiveness works');
    }

    // Generate bug report
    console.log('\n' + '='.repeat(50));
    console.log('📊 SYSTEMATIC TESTING RESULTS');
    console.log('='.repeat(50));

    if (bugsFound.length === 0) {
        console.log('✅ NO BUGS FOUND! Onboarding is working perfectly.');
    } else {
        console.log(`🐛 ${bugsFound.length} BUGS FOUND:\n`);

        // Group by priority
        const critical = bugsFound.filter(bug => bug.priority === 'Critical');
        const high = bugsFound.filter(bug => bug.priority === 'High');
        const medium = bugsFound.filter(bug => bug.priority === 'Medium');
        const low = bugsFound.filter(bug => bug.priority === 'Low');

        if (critical.length > 0) {
            console.log('🚨 CRITICAL BUGS:');
            critical.forEach(bug => console.log(`   • Slide ${bug.slide}: ${bug.description}`));
            console.log();
        }

        if (high.length > 0) {
            console.log('⚠️ HIGH PRIORITY BUGS:');
            high.forEach(bug => console.log(`   • Slide ${bug.slide}: ${bug.description}`));
            console.log();
        }

        if (medium.length > 0) {
            console.log('📋 MEDIUM PRIORITY BUGS:');
            medium.forEach(bug => console.log(`   • Slide ${bug.slide}: ${bug.description}`));
            console.log();
        }

        if (low.length > 0) {
            console.log('📝 LOW PRIORITY BUGS:');
            low.forEach(bug => console.log(`   • Slide ${bug.slide}: ${bug.description}`));
            console.log();
        }
    }

    console.log('='.repeat(50));
    console.log('✅ Systematic testing completed!');

    return bugsFound;
}

// Auto-run when script loads
if (typeof window !== 'undefined') {
    runSystematicTests().then(bugs => {
        window.testResults = bugs;
        console.log('\n💾 Test results saved to window.testResults');
    });
}

// Export for Node.js if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runSystematicTests, bugsFound };
}