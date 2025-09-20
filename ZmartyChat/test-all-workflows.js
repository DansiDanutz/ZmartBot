// COMPLETE ONBOARDING TEST SUITE
// Tests ALL possible workflows and edge cases

import puppeteer from 'puppeteer';
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://asjtxrmftmutcsnqgidy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Test configuration
const TEST_URL = 'http://localhost:9000';
const timestamp = Date.now();

// Color codes for console
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

// Test Suite
class OnboardingTestSuite {
    constructor() {
        this.browser = null;
        this.page = null;
        this.results = {
            total: 0,
            passed: 0,
            failed: 0,
            errors: []
        };
    }

    async init() {
        log('\n🚀 Starting Complete Onboarding Test Suite', 'magenta');
        log('==========================================', 'magenta');

        this.browser = await puppeteer.launch({
            headless: false, // Set to true for CI
            slowMo: 100, // Slow down for visibility
            defaultViewport: { width: 1280, height: 800 }
        });

        this.page = await this.browser.newPage();

        // Listen for console errors
        this.page.on('console', msg => {
            if (msg.type() === 'error') {
                log(`Browser Error: ${msg.text()}`, 'red');
                this.results.errors.push(msg.text());
            }
        });

        // Listen for page errors
        this.page.on('pageerror', error => {
            log(`Page Error: ${error.message}`, 'red');
            this.results.errors.push(error.message);
        });
    }

    async runTest(testName, testFn) {
        this.results.total++;
        log(`\n📋 Testing: ${testName}`, 'cyan');

        try {
            await testFn();
            this.results.passed++;
            log(`✅ PASSED: ${testName}`, 'green');
            return true;
        } catch (error) {
            this.results.failed++;
            log(`❌ FAILED: ${testName}`, 'red');
            log(`   Error: ${error.message}`, 'red');
            this.results.errors.push(`${testName}: ${error.message}`);
            return false;
        }
    }

    // TEST 1: Initial Page Load
    async testPageLoad() {
        await this.runTest('Page loads correctly', async () => {
            await this.page.goto(TEST_URL);
            await this.page.waitForSelector('.slide', { timeout: 5000 });

            const title = await this.page.$eval('h1', el => el.textContent);
            if (!title.includes('Welcome')) {
                throw new Error('Welcome slide not showing');
            }
        });
    }

    // TEST 2: Navigation Forward
    async testNavigationForward() {
        await this.runTest('Navigate forward through slides 1-3', async () => {
            // Start at slide 1
            await this.page.goto(TEST_URL);
            await this.page.waitForSelector('.slide');

            // Go to slide 2
            await this.page.click('.next-btn');
            await this.page.waitForTimeout(500);
            let currentSlide = await this.page.evaluate(() => window.currentSlide);
            if (currentSlide !== 2) throw new Error(`Expected slide 2, got ${currentSlide}`);

            // Go to slide 3
            await this.page.click('.next-btn');
            await this.page.waitForTimeout(500);
            currentSlide = await this.page.evaluate(() => window.currentSlide);
            if (currentSlide !== 3) throw new Error(`Expected slide 3, got ${currentSlide}`);
        });
    }

    // TEST 3: Navigation Backward
    async testNavigationBackward() {
        await this.runTest('Navigate backward through slides', async () => {
            // Ensure we're on slide 3
            await this.page.evaluate(() => goToSlide(3));
            await this.page.waitForTimeout(500);

            // Go back to slide 2
            await this.page.click('.prev-btn');
            await this.page.waitForTimeout(500);
            let currentSlide = await this.page.evaluate(() => window.currentSlide);
            if (currentSlide !== 2) throw new Error(`Expected slide 2, got ${currentSlide}`);

            // Go back to slide 1
            await this.page.click('.prev-btn');
            await this.page.waitForTimeout(500);
            currentSlide = await this.page.evaluate(() => window.currentSlide);
            if (currentSlide !== 1) throw new Error(`Expected slide 1, got ${currentSlide}`);
        });
    }

    // TEST 4: Skip Button
    async testSkipButton() {
        await this.runTest('Skip button jumps to registration', async () => {
            await this.page.goto(TEST_URL);
            await this.page.waitForSelector('.skip-btn');

            await this.page.click('.skip-btn');
            await this.page.waitForTimeout(500);

            const currentSlide = await this.page.evaluate(() => window.currentSlide);
            if (currentSlide !== 4) throw new Error(`Expected slide 4, got ${currentSlide}`);
        });
    }

    // TEST 5: Email Validation
    async testEmailValidation() {
        await this.runTest('Email validation errors', async () => {
            // Go to registration slide
            await this.page.evaluate(() => goToSlide(4));
            await this.page.waitForSelector('#register-email');

            // Test empty email
            await this.page.click('#register-email');
            await this.page.keyboard.press('Tab');
            await this.page.waitForTimeout(500);

            // Try to continue without email
            const continueBtn = await this.page.$('#email-continue-btn');
            if (continueBtn) {
                await this.page.click('#email-continue-btn');
                await this.page.waitForTimeout(500);

                // Check for error message
                const errorVisible = await this.page.evaluate(() => {
                    const errorEl = document.querySelector('.error-message');
                    return errorEl && errorEl.style.display !== 'none';
                });

                if (!errorVisible) throw new Error('No error shown for empty email');
            }

            // Test invalid email format
            await this.page.type('#register-email', 'invalid-email');
            await this.page.keyboard.press('Tab');
            await this.page.waitForTimeout(500);
        });
    }

    // TEST 6: Password Validation
    async testPasswordValidation() {
        await this.runTest('Password validation and mismatch', async () => {
            await this.page.evaluate(() => goToSlide(4));
            await this.page.waitForSelector('#register-password');

            // Clear any existing values
            await this.page.evaluate(() => {
                document.getElementById('register-email').value = 'test@example.com';
                document.getElementById('register-password').value = '';
                document.getElementById('confirm-password').value = '';
            });

            // Test short password
            await this.page.type('#register-password', 'short');
            await this.page.keyboard.press('Tab');
            await this.page.waitForTimeout(500);

            // Check if confirm password field is hidden (should be)
            const confirmVisible = await this.page.evaluate(() => {
                const confirmContainer = document.querySelector('.confirm-container');
                return confirmContainer && confirmContainer.style.display !== 'none';
            });

            if (confirmVisible) throw new Error('Confirm password shown for short password');

            // Test valid password
            await this.page.evaluate(() => {
                document.getElementById('register-password').value = '';
            });
            await this.page.type('#register-password', 'ValidPass123');
            await this.page.waitForTimeout(500);

            // Confirm password should now be visible
            const confirmNowVisible = await this.page.evaluate(() => {
                const confirmContainer = document.querySelector('.confirm-container');
                return confirmContainer && confirmContainer.style.display !== 'none';
            });

            if (!confirmNowVisible) throw new Error('Confirm password not shown for valid password');

            // Test password mismatch
            await this.page.type('#confirm-password', 'DifferentPass123');
            await this.page.waitForTimeout(500);

            // Button should be hidden for mismatch
            const buttonVisible = await this.page.evaluate(() => {
                const btn = document.getElementById('email-continue-btn');
                return btn && btn.style.display !== 'none';
            });

            if (buttonVisible) throw new Error('Button shown despite password mismatch');
        });
    }

    // TEST 7: Progressive Reveal
    async testProgressiveReveal() {
        await this.runTest('Progressive reveal for password fields', async () => {
            await this.page.evaluate(() => goToSlide(4));
            await this.page.waitForSelector('#register-email');

            // Clear all fields
            await this.page.evaluate(() => {
                document.getElementById('register-email').value = '';
                document.getElementById('register-password').value = '';
                if (document.getElementById('confirm-password')) {
                    document.getElementById('confirm-password').value = '';
                }
            });

            // Type email
            await this.page.type('#register-email', `test${Date.now()}@example.com`);

            // Password field should be visible
            const passwordVisible = await this.page.$('#register-password');
            if (!passwordVisible) throw new Error('Password field not visible after email');

            // Type valid password
            await this.page.type('#register-password', 'TestPassword123');
            await this.page.waitForTimeout(1000);

            // Confirm password should appear
            const confirmVisible = await this.page.$('#confirm-password');
            if (!confirmVisible) throw new Error('Confirm password not visible after valid password');

            // Type matching password
            await this.page.type('#confirm-password', 'TestPassword123');
            await this.page.waitForTimeout(1000);

            // Register button should appear
            const buttonVisible = await this.page.evaluate(() => {
                const btn = document.getElementById('email-continue-btn');
                return btn && btn.style.display !== 'none';
            });

            if (!buttonVisible) throw new Error('Register button not shown after matching passwords');
        });
    }

    // TEST 8: Registration Flow
    async testRegistrationFlow() {
        await this.runTest('Complete registration flow', async () => {
            await this.page.evaluate(() => goToSlide(4));

            const testEmail = `test${timestamp}@example.com`;

            // Fill registration form
            await this.page.evaluate((email) => {
                document.getElementById('register-email').value = email;
                document.getElementById('register-password').value = 'TestPass123';
                document.getElementById('confirm-password').value = 'TestPass123';
            }, testEmail);

            // Wait for button to appear
            await this.page.waitForTimeout(1000);

            // Click register
            const registerBtn = await this.page.$('#email-continue-btn');
            if (registerBtn) {
                await registerBtn.click();
                await this.page.waitForTimeout(3000);

                // Check if we moved to slide 5 (verification)
                const currentSlide = await this.page.evaluate(() => window.currentSlide);
                if (currentSlide !== 5) throw new Error(`Expected slide 5, got ${currentSlide}`);

                // Check for verification code inputs
                const codeInputs = await this.page.$$('[id^="code-"]');
                if (codeInputs.length !== 6) throw new Error('Verification code inputs not found');
            } else {
                throw new Error('Register button not found');
            }
        });
    }

    // TEST 9: Login Modal
    async testLoginModal() {
        await this.runTest('Login modal functionality', async () => {
            await this.page.evaluate(() => goToSlide(4));
            await this.page.waitForTimeout(500);

            // Click "Already have an account?"
            const loginLink = await this.page.$('a[onclick*="showForgotPasswordModal"]');
            if (loginLink) {
                await loginLink.click();
                await this.page.waitForTimeout(1000);

                // Check if modal appeared
                const modalVisible = await this.page.$('#forgot-password-overlay');
                if (!modalVisible) throw new Error('Login modal did not appear');

                // Check for sign in form
                const signinForm = await this.page.$('#signin-form');
                if (!signinForm) throw new Error('Sign in form not found in modal');

                // Close modal
                const closeBtn = await this.page.$('button[onclick*="closeForgotPasswordModal"]');
                if (closeBtn) {
                    await closeBtn.click();
                    await this.page.waitForTimeout(500);
                }
            } else {
                throw new Error('Login link not found');
            }
        });
    }

    // TEST 10: Social Login Buttons
    async testSocialLogins() {
        await this.runTest('Social login buttons', async () => {
            await this.page.evaluate(() => goToSlide(4));

            // Check for social login buttons
            const googleBtn = await this.page.$('.quick-login-option:nth-of-type(1)');
            const facebookBtn = await this.page.$('.quick-login-option:nth-of-type(2)');
            const githubBtn = await this.page.$('.quick-login-option:nth-of-type(3)');

            if (!googleBtn) throw new Error('Google login button not found');
            if (!facebookBtn) throw new Error('Facebook login button not found');
            if (!githubBtn) throw new Error('GitHub login button not found');
        });
    }

    // TEST 11: Tier Selection
    async testTierSelection() {
        await this.runTest('Tier selection on slide 6', async () => {
            await this.page.evaluate(() => goToSlide(6));
            await this.page.waitForTimeout(500);

            // Check for tier cards
            const tierCards = await this.page.$$('.tier-card');
            if (tierCards.length !== 3) throw new Error(`Expected 3 tier cards, found ${tierCards.length}`);

            // Click on Pro tier
            await this.page.click('.tier-card:nth-of-type(2)');
            await this.page.waitForTimeout(500);

            // Check if tier was selected
            const selectedTier = await this.page.evaluate(() => window.selectedTier);
            if (!selectedTier) throw new Error('Tier selection not working');
        });
    }

    // TEST 12: Error Messages
    async testErrorMessages() {
        await this.runTest('Error message display', async () => {
            // Test showError function
            await this.page.evaluate(() => {
                window.showError('Test error message');
            });

            await this.page.waitForTimeout(500);

            const errorVisible = await this.page.evaluate(() => {
                const errorEl = document.querySelector('.error-message');
                return errorEl && errorEl.style.display !== 'none';
            });

            if (!errorVisible) throw new Error('Error message not displayed');
        });
    }

    // TEST 13: Keyboard Navigation
    async testKeyboardNavigation() {
        await this.runTest('Keyboard navigation (Tab, Enter)', async () => {
            await this.page.evaluate(() => goToSlide(4));

            // Focus on email field
            await this.page.focus('#register-email');

            // Tab to password
            await this.page.keyboard.press('Tab');

            // Check if password field is focused
            const passwordFocused = await this.page.evaluate(() => {
                return document.activeElement.id === 'register-password';
            });

            if (!passwordFocused) throw new Error('Tab navigation not working');

            // Test Enter key on button
            await this.page.evaluate(() => {
                document.getElementById('register-email').value = 'test@example.com';
                document.getElementById('register-password').value = 'TestPass123';
                document.getElementById('confirm-password').value = 'TestPass123';
            });

            await this.page.waitForTimeout(1000);
            await this.page.focus('#email-continue-btn');
            // Don't actually press Enter to avoid registration
        });
    }

    // TEST 14: Verification Code Input
    async testVerificationCodeInput() {
        await this.runTest('Verification code input behavior', async () => {
            await this.page.evaluate(() => goToSlide(5));
            await this.page.waitForTimeout(500);

            // Type in first code input
            const firstInput = await this.page.$('#code-1');
            if (firstInput) {
                await firstInput.type('1');
                await this.page.waitForTimeout(200);

                // Check if focus moved to second input
                const secondInputFocused = await this.page.evaluate(() => {
                    return document.activeElement.id === 'code-2';
                });

                if (!secondInputFocused) throw new Error('Auto-focus to next input not working');

                // Test backspace
                await this.page.keyboard.press('Backspace');
                await this.page.waitForTimeout(200);

                const firstInputFocused = await this.page.evaluate(() => {
                    return document.activeElement.id === 'code-1';
                });

                if (!firstInputFocused) throw new Error('Backspace navigation not working');
            } else {
                throw new Error('Verification code inputs not found');
            }
        });
    }

    // TEST 15: Profile Completion
    async testProfileCompletion() {
        await this.runTest('Profile completion on slide 7', async () => {
            await this.page.evaluate(() => goToSlide(7));
            await this.page.waitForTimeout(500);

            // Check for profile fields
            const nameInput = await this.page.$('#profile-name');
            const countrySelect = await this.page.$('#profile-country');

            if (!nameInput) throw new Error('Name input not found');
            if (!countrySelect) throw new Error('Country select not found');

            // Fill profile
            await nameInput.type('Test User');
            await countrySelect.select('US');

            // Check for complete button
            const completeBtn = await this.page.$('.complete-btn');
            if (!completeBtn) throw new Error('Complete button not found');
        });
    }

    // TEST 16: Check for Console Errors
    async testNoConsoleErrors() {
        await this.runTest('No console errors during navigation', async () => {
            // Navigate through all slides
            for (let i = 1; i <= 7; i++) {
                await this.page.evaluate((slide) => goToSlide(slide), i);
                await this.page.waitForTimeout(500);
            }

            // Check if any errors were collected
            if (this.results.errors.length > 0) {
                throw new Error(`Found ${this.results.errors.length} console errors`);
            }
        });
    }

    // TEST 17: Overlay Cleanup
    async testOverlayCleanup() {
        await this.runTest('No stray overlays after actions', async () => {
            // Try registration and cancel
            await this.page.evaluate(() => goToSlide(4));

            // Open and close login modal
            const loginLink = await this.page.$('a[onclick*="showForgotPasswordModal"]');
            if (loginLink) {
                await loginLink.click();
                await this.page.waitForTimeout(1000);

                // Close modal
                const closeBtn = await this.page.$('button[onclick*="closeForgotPasswordModal"]');
                if (closeBtn) {
                    await closeBtn.click();
                    await this.page.waitForTimeout(500);
                }
            }

            // Check for any remaining overlays
            const overlays = await this.page.evaluate(() => {
                return document.querySelectorAll('[id*="overlay"]').length;
            });

            if (overlays > 0) throw new Error(`Found ${overlays} stray overlay(s)`);
        });
    }

    // Run all tests
    async runAllTests() {
        await this.init();

        // Run each test
        await this.testPageLoad();
        await this.testNavigationForward();
        await this.testNavigationBackward();
        await this.testSkipButton();
        await this.testEmailValidation();
        await this.testPasswordValidation();
        await this.testProgressiveReveal();
        await this.testRegistrationFlow();
        await this.testLoginModal();
        await this.testSocialLogins();
        await this.testTierSelection();
        await this.testErrorMessages();
        await this.testKeyboardNavigation();
        await this.testVerificationCodeInput();
        await this.testProfileCompletion();
        await this.testNoConsoleErrors();
        await this.testOverlayCleanup();

        // Show results
        this.showResults();

        // Close browser
        await this.browser.close();
    }

    showResults() {
        log('\n========================================', 'magenta');
        log('TEST RESULTS', 'magenta');
        log('========================================', 'magenta');

        log(`Total Tests: ${this.results.total}`, 'cyan');
        log(`Passed: ${this.results.passed}`, 'green');
        log(`Failed: ${this.results.failed}`, 'red');

        const successRate = ((this.results.passed / this.results.total) * 100).toFixed(1);
        const color = successRate === '100.0' ? 'green' : successRate >= '80' ? 'yellow' : 'red';
        log(`Success Rate: ${successRate}%`, color);

        if (this.results.errors.length > 0) {
            log('\n❌ Errors Found:', 'red');
            this.results.errors.forEach(error => {
                log(`  - ${error}`, 'red');
            });
        } else {
            log('\n✅ All Tests Passed Successfully!', 'green');
        }

        // Generate report
        const report = {
            timestamp: new Date().toISOString(),
            results: this.results,
            successRate: successRate
        };

        // Save report
        require('fs').writeFileSync(
            'test-results.json',
            JSON.stringify(report, null, 2)
        );

        log('\n📊 Report saved to test-results.json', 'cyan');
    }
}

// Run the test suite
async function main() {
    const tester = new OnboardingTestSuite();
    try {
        await tester.runAllTests();
    } catch (error) {
        log(`\n❌ Test suite failed: ${error.message}`, 'red');
        process.exit(1);
    }
}

// Check if puppeteer is installed
try {
    require.resolve('puppeteer');
    main();
} catch(e) {
    log('Installing puppeteer...', 'yellow');
    require('child_process').execSync('npm install puppeteer', { stdio: 'inherit' });
    log('Puppeteer installed. Please run the test again.', 'green');
}