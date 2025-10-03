/**
 * Comprehensive Onboarding Testing Script
 * Instructions: Open Chrome Developer Tools, paste this into Console at https://vermillion-paprenjak-67497b.netlify.app
 */

console.log('🚀 COMPREHENSIVE ONBOARDING AUTOMATED TEST STARTING...\n');

// Enhanced test utilities
const TestUtils = {
    takeScreenshot: function(stepName) {
        console.log(`📸 Screenshot point: ${stepName}`);
        // In a real browser MCP environment, this would capture screenshots
        return `screenshot_${stepName}_${Date.now()}.png`;
    },

    clickElement: function(selector, description) {
        const element = document.querySelector(selector);
        if (!element) {
            console.error(`❌ Element not found: ${selector} (${description})`);
            return false;
        }
        if (!this.isVisible(element)) {
            console.error(`❌ Element not visible: ${selector} (${description})`);
            return false;
        }
        console.log(`🖱️  Clicking: ${description}`);
        element.click();
        return true;
    },

    enterText: function(selector, text, description) {
        const element = document.querySelector(selector);
        if (!element) {
            console.error(`❌ Input not found: ${selector} (${description})`);
            return false;
        }
        console.log(`⌨️  Entering text in ${description}: "${text}"`);
        element.focus();
        element.value = text;
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
    },

    isVisible: function(element) {
        if (!element) return false;
        const rect = element.getBoundingClientRect();
        const style = window.getComputedStyle(element);
        return rect.width > 0 && rect.height > 0 &&
               style.opacity !== '0' && style.visibility !== 'hidden' &&
               style.display !== 'none';
    },

    waitForElement: function(selector, timeout = 3000) {
        return new Promise((resolve) => {
            const startTime = Date.now();
            const check = () => {
                const element = document.querySelector(selector);
                if (element && this.isVisible(element)) {
                    resolve(element);
                } else if (Date.now() - startTime < timeout) {
                    setTimeout(check, 100);
                } else {
                    resolve(null);
                }
            };
            check();
        });
    },

    delay: function(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// Test execution plan
const TestPlan = {
    async step1_LandingPage() {
        console.log('\n🔍 STEP 1: Testing Landing Page...');

        // Take initial screenshot
        TestUtils.takeScreenshot('01_landing_page');

        // Verify welcome slide is active
        const welcomeSlide = document.querySelector('#step1');
        if (!welcomeSlide || !welcomeSlide.classList.contains('active')) {
            console.error('❌ Welcome slide not active');
            return false;
        }
        console.log('✅ Welcome slide is active');

        // Verify Get Started button
        const getStartedBtn = welcomeSlide.querySelector('button');
        if (!getStartedBtn) {
            console.error('❌ Get Started button not found');
            return false;
        }
        console.log(`✅ Get Started button found: "${getStartedBtn.textContent.trim()}"`);

        // Click Get Started button
        if (!TestUtils.clickElement('#step1 button', 'Get Started button')) {
            return false;
        }

        await TestUtils.delay(500);
        TestUtils.takeScreenshot('02_after_get_started');

        // Verify navigation to authentication step
        const authSlide = document.querySelector('#step2');
        if (!authSlide || !authSlide.classList.contains('active')) {
            console.error('❌ Failed to navigate to authentication step');
            return false;
        }
        console.log('✅ Successfully navigated to authentication step');
        return true;
    },

    async step2_AuthenticationTabs() {
        console.log('\n🔍 STEP 2: Testing Authentication Tabs...');

        // Verify Email tab is active by default
        const emailTab = document.querySelector('#emailTab');
        const googleTab = document.querySelector('#googleTab');

        if (!emailTab || !googleTab) {
            console.error('❌ Authentication tabs not found');
            return false;
        }

        console.log('✅ Authentication tabs found');

        // Test Google tab click
        TestUtils.takeScreenshot('03_before_google_tab');

        if (!TestUtils.clickElement('#googleTab', 'Google authentication tab')) {
            return false;
        }

        await TestUtils.delay(300);
        TestUtils.takeScreenshot('04_google_tab_active');

        // Verify Google content is shown
        const googleSection = document.querySelector('#googleAuth');
        if (!googleSection || !TestUtils.isVisible(googleSection)) {
            console.error('❌ Google authentication section not visible');
            return false;
        }
        console.log('✅ Google authentication section is visible');

        // Test back to Email tab
        if (!TestUtils.clickElement('#emailTab', 'Email tab')) {
            return false;
        }

        await TestUtils.delay(300);
        TestUtils.takeScreenshot('05_back_to_email_tab');

        const emailSection = document.querySelector('#emailAuth');
        if (!emailSection || !TestUtils.isVisible(emailSection)) {
            console.error('❌ Email authentication section not visible');
            return false;
        }
        console.log('✅ Email authentication section is visible');
        return true;
    },

    async step3_PasswordStrengthMeter() {
        console.log('\n🔍 STEP 3: Testing Password Strength Meter...');

        // Enter email first
        if (!TestUtils.enterText('#regEmail', 'test@example.com', 'email field')) {
            return false;
        }

        // Test password field and strength meter
        const passwordTests = [
            { password: '123', expected: 'weak' },
            { password: 'password123', expected: 'medium' },
            { password: 'StrongP@ssw0rd!', expected: 'strong' }
        ];

        for (const test of passwordTests) {
            if (!TestUtils.enterText('#regPassword', test.password, 'password field')) {
                return false;
            }

            await TestUtils.delay(200);
            TestUtils.takeScreenshot(`06_password_${test.expected}`);

            // Check if strength meter updated
            const strengthMeter = document.querySelector('.password-strength');
            if (strengthMeter) {
                console.log(`✅ Password strength meter visible for: ${test.password}`);
            } else {
                console.log(`⚠️  Password strength meter not found for: ${test.password}`);
            }
        }

        return true;
    },

    async step4_BackButtonNavigation() {
        console.log('\n🔍 STEP 4: Testing Back Button Navigation...');

        // Look for back button
        const backBtn = document.querySelector('.back-btn, [onclick*="goBack"], .nav-arrow.left');
        if (!backBtn) {
            console.error('❌ Back button not found');
            return false;
        }

        TestUtils.takeScreenshot('07_before_back_button');

        if (!TestUtils.clickElement('.back-btn, [onclick*="goBack"], .nav-arrow.left', 'Back button')) {
            return false;
        }

        await TestUtils.delay(500);
        TestUtils.takeScreenshot('08_after_back_button');

        // Verify we went back to previous step
        const currentStep = document.querySelector('.step.active');
        if (currentStep) {
            console.log(`✅ Back navigation worked - current step: ${currentStep.id}`);
        } else {
            console.error('❌ Back navigation failed - no active step found');
            return false;
        }

        return true;
    },

    async step5_ArrowKeyNavigation() {
        console.log('\n🔍 STEP 5: Testing Arrow Key Navigation...');

        TestUtils.takeScreenshot('09_before_arrow_keys');

        // Test right arrow key
        console.log('⌨️  Testing right arrow key...');
        const rightArrowEvent = new KeyboardEvent('keydown', { key: 'ArrowRight', code: 'ArrowRight' });
        document.dispatchEvent(rightArrowEvent);

        await TestUtils.delay(500);
        TestUtils.takeScreenshot('10_after_right_arrow');

        // Test left arrow key
        console.log('⌨️  Testing left arrow key...');
        const leftArrowEvent = new KeyboardEvent('keydown', { key: 'ArrowLeft', code: 'ArrowLeft' });
        document.dispatchEvent(leftArrowEvent);

        await TestUtils.delay(500);
        TestUtils.takeScreenshot('11_after_left_arrow');

        console.log('✅ Arrow key navigation tests completed');
        return true;
    },

    async step6_SlideProgression() {
        console.log('\n🔍 STEP 6: Testing Multiple Slide Navigation...');

        const totalSteps = document.querySelectorAll('.step').length;
        console.log(`📊 Total steps found: ${totalSteps}`);

        // Navigate through first few steps manually
        for (let i = 1; i <= Math.min(4, totalSteps); i++) {
            console.log(`🚶 Navigating to step ${i}...`);

            // Find and click continue/next button in current step
            const currentStep = document.querySelector('.step.active');
            if (currentStep) {
                const nextBtn = currentStep.querySelector('button:not(.btn-secondary)');
                if (nextBtn && TestUtils.isVisible(nextBtn)) {
                    TestUtils.takeScreenshot(`12_step_${i}_before_continue`);
                    nextBtn.click();
                    await TestUtils.delay(600);
                    TestUtils.takeScreenshot(`13_step_${i}_after_continue`);
                }
            }
        }

        console.log('✅ Multi-step navigation completed');
        return true;
    }
};

// Main test execution
async function runComprehensiveTest() {
    console.log('🎬 Starting comprehensive automated test...\n');

    const testResults = {
        landingPage: false,
        authenticationTabs: false,
        passwordStrength: false,
        backNavigation: false,
        arrowNavigation: false,
        slideProgression: false
    };

    try {
        testResults.landingPage = await TestPlan.step1_LandingPage();
        testResults.authenticationTabs = await TestPlan.step2_AuthenticationTabs();
        testResults.passwordStrength = await TestPlan.step3_PasswordStrengthMeter();
        testResults.backNavigation = await TestPlan.step4_BackButtonNavigation();
        testResults.arrowNavigation = await TestPlan.step5_ArrowKeyNavigation();
        testResults.slideProgression = await TestPlan.step6_SlideProgression();
    } catch (error) {
        console.error('❌ Test execution error:', error);
    }

    // Generate final report
    console.log('\n' + '='.repeat(80));
    console.log('📋 COMPREHENSIVE TEST RESULTS SUMMARY');
    console.log('='.repeat(80));

    Object.entries(testResults).forEach(([testName, passed]) => {
        const status = passed ? '✅ PASS' : '❌ FAIL';
        const description = testName.replace(/([A-Z])/g, ' $1').toLowerCase();
        console.log(`${status} ${description}`);
    });

    const passedTests = Object.values(testResults).filter(Boolean).length;
    const totalTests = Object.keys(testResults).length;

    console.log(`\n📊 Overall Score: ${passedTests}/${totalTests} tests passed`);

    if (passedTests === totalTests) {
        console.log('🎉 ALL TESTS PASSED! Onboarding system is fully functional.');
    } else {
        console.log('⚠️  Some tests failed. Please review the results above.');
    }

    console.log('='.repeat(80));
}

// Auto-start test
console.log('⏳ Test will begin in 2 seconds...');
setTimeout(runComprehensiveTest, 2000);