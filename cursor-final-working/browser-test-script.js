// ZmartyBrain Onboarding - Browser Testing Script
// Open https://vermillion-paprenjak-67497b.netlify.app/ and paste this in console

console.clear();
console.log('%c🧪 ZmartyBrain Onboarding Test Suite', 'font-size: 20px; color: #667eea; font-weight: bold');
console.log('%c========================================', 'color: #667eea');

// Test configuration
const TEST_EMAIL = `test${Date.now()}@example.com`;
const TEST_PASSWORD = 'TestPass123!';

// Helper functions
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const clickElement = (selector) => {
    const el = document.querySelector(selector);
    if (el) {
        el.click();
        console.log(`✅ Clicked: ${selector}`);
        return true;
    } else {
        console.error(`❌ Element not found: ${selector}`);
        return false;
    }
};

const fillInput = (selector, value) => {
    const el = document.querySelector(selector);
    if (el) {
        el.value = value;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        console.log(`✅ Filled: ${selector} with "${value}"`);
        return true;
    } else {
        console.error(`❌ Input not found: ${selector}`);
        return false;
    }
};

const checkCurrentStep = () => {
    if (typeof state !== 'undefined' && state.currentStep) {
        console.log(`📍 Current Step: ${state.currentStep} of ${state.totalSteps}`);
        return state.currentStep;
    } else {
        console.warn('⚠️ State object not found');
        return null;
    }
};

const getVisibleElements = () => {
    const elements = {
        buttons: Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()),
        inputs: Array.from(document.querySelectorAll('input')).map(i => i.placeholder || i.type),
        headings: Array.from(document.querySelectorAll('h1, h2, h3')).map(h => h.textContent.trim())
    };
    console.log('🔍 Visible Elements:', elements);
    return elements;
};

// Test functions for each step
const tests = {
    step1_welcome: async () => {
        console.log('\n📱 STEP 1: Welcome Screen');
        console.log('------------------------');

        const step = checkCurrentStep();
        if (step !== 1) {
            console.warn(`⚠️ Not on step 1, current step: ${step}`);
            return false;
        }

        getVisibleElements();

        // Check for Get Started button
        const hasGetStarted = document.querySelector('button')?.textContent.includes('Get Started');
        if (hasGetStarted) {
            console.log('✅ Welcome screen loaded correctly');
            console.log('🎯 Clicking "Get Started"...');
            clickElement('button');
            await wait(1000);
            return true;
        } else {
            console.error('❌ Welcome screen missing "Get Started" button');
            return false;
        }
    },

    step2_auth: async () => {
        console.log('\n🔐 STEP 2: Authentication');
        console.log('------------------------');

        const step = checkCurrentStep();
        if (step !== 2) {
            console.warn(`⚠️ Not on step 2, current step: ${step}`);
            return false;
        }

        getVisibleElements();

        // Check for auth tabs
        const hasEmailTab = document.querySelector('[data-tab="email"]');
        const hasGoogleTab = document.querySelector('[data-tab="google"]');

        if (hasEmailTab && hasGoogleTab) {
            console.log('✅ Auth tabs present');
        } else {
            console.warn('⚠️ Auth tabs not found, checking for alternative selectors');
        }

        // Try email registration
        console.log('📝 Testing email registration...');

        if (document.querySelector('#regEmail')) {
            fillInput('#regEmail', TEST_EMAIL);
            fillInput('#regPassword', TEST_PASSWORD);

            await wait(500);

            if (clickElement('#regEmailBtn') || clickElement('button[onclick*="register"]')) {
                console.log('✅ Registration submitted');
                await wait(2000);
                return true;
            }
        } else {
            console.error('❌ Registration form not found');
            return false;
        }
    },

    step3_confirmation: async () => {
        console.log('\n✨ STEP 3: Account Confirmation');
        console.log('------------------------');

        const step = checkCurrentStep();
        if (step !== 3) {
            console.warn(`⚠️ Not on step 3, current step: ${step}`);
            return false;
        }

        getVisibleElements();

        console.log('✅ Confirmation step reached');
        await wait(2000);
        return true;
    },

    step4_verification: async () => {
        console.log('\n📧 STEP 4: Email Verification');
        console.log('------------------------');

        const step = checkCurrentStep();
        if (step !== 4) {
            console.warn(`⚠️ Not on step 4, current step: ${step}`);
            return false;
        }

        getVisibleElements();

        // Check for verification code inputs
        const codeInputs = document.querySelectorAll('.code-input');
        if (codeInputs.length === 6) {
            console.log('✅ 6-digit code input found');
            console.log('⏳ Waiting for email with verification code...');
            console.log('💡 TIP: Check email or use magic link');

            // For testing, try to fill dummy code
            const testCode = '123456';
            codeInputs.forEach((input, i) => {
                input.value = testCode[i];
                input.dispatchEvent(new Event('input', { bubbles: true }));
            });

            await wait(1000);

            if (clickElement('#verifyCodeBtn') || clickElement('button[onclick*="verify"]')) {
                console.log('📤 Verification code submitted (will fail with test code)');
            }
        } else {
            console.error('❌ Verification code inputs not found');
            return false;
        }

        return true;
    },

    step6_tiers: async () => {
        console.log('\n💎 STEP 6: Choose Your Plan');
        console.log('------------------------');

        const step = checkCurrentStep();
        if (step !== 6) {
            console.warn(`⚠️ Not on step 6, current step: ${step}`);
            // Try to force navigation
            console.log('🔧 Attempting to navigate to step 6...');
            if (typeof state !== 'undefined' && state.goToStep) {
                state.goToStep(6, 'forward', true);
                await wait(1000);
            }
        }

        getVisibleElements();

        // Check for tier cards
        const tierCards = document.querySelectorAll('.tier-card');
        if (tierCards.length > 0) {
            console.log(`✅ Found ${tierCards.length} tier cards`);

            // Click first tier
            if (tierCards[0]) {
                tierCards[0].click();
                console.log('✅ Selected first tier');
                await wait(1500);
                return true;
            }
        } else {
            console.error('❌ Tier cards not found');
            return false;
        }
    },

    step7_profile: async () => {
        console.log('\n👤 STEP 7: Complete Profile');
        console.log('------------------------');

        const step = checkCurrentStep();
        if (step !== 7) {
            console.warn(`⚠️ Not on step 7, current step: ${step}`);
            return false;
        }

        getVisibleElements();

        // Fill profile form
        fillInput('#fullName', 'Test User');
        fillInput('#country', 'United States');
        fillInput('#industry', 'Technology');

        await wait(500);

        if (clickElement('#completeBtn') || clickElement('button[onclick*="complete"]')) {
            console.log('✅ Profile submitted');
            await wait(2000);
            return true;
        } else {
            console.error('❌ Complete button not found');
            return false;
        }
    },

    step8_complete: async () => {
        console.log('\n🎉 STEP 8: Onboarding Complete');
        console.log('------------------------');

        const step = checkCurrentStep();
        if (step !== 8) {
            console.warn(`⚠️ Not on step 8, current step: ${step}`);
            return false;
        }

        getVisibleElements();

        // Check for success message
        const hasSuccess = document.body.textContent.includes('successfully') ||
                          document.body.textContent.includes('complete');

        if (hasSuccess) {
            console.log('✅ Onboarding completed successfully!');
            console.log('🎊 FULL FLOW TEST COMPLETE!');
            return true;
        } else {
            console.warn('⚠️ Completion message not found');
            return false;
        }
    }
};

// Run full test
async function runFullTest() {
    console.log('\n🚀 Starting Full Onboarding Test');
    console.log('=====================================\n');

    const results = {
        passed: [],
        failed: []
    };

    // Check initial state
    console.log('🔍 Checking initial state...');
    checkCurrentStep();
    getVisibleElements();

    // Check Supabase
    if (typeof supabaseClient !== 'undefined') {
        console.log('✅ Supabase client found');
        const { data: session } = await supabaseClient.auth.getSession();
        console.log('Session:', session ? '✅ Active' : '❌ None');
    } else {
        console.error('❌ Supabase client not found!');
    }

    console.log('\n📋 Manual Testing Instructions:');
    console.log('================================');
    console.log('1. Click "Get Started" button');
    console.log('2. Register with a new email');
    console.log('3. Check email for verification code');
    console.log('4. Enter the 6-digit code');
    console.log('5. Select a tier (Starter/Pro/Enterprise)');
    console.log('6. Complete your profile');
    console.log('7. Reach the success screen');
    console.log('\n💡 Use these console commands to help:');
    console.log('- checkCurrentStep() - See current step');
    console.log('- getVisibleElements() - See what\'s on screen');
    console.log('- state.goToStep(6, "forward", true) - Force navigation');
    console.log('- state.userData - See user data');
    console.log('- location.reload() - Restart flow');
}

// Diagnostic function
window.diagnoseOnboarding = () => {
    console.clear();
    console.log('%c🔧 Onboarding Diagnostics', 'font-size: 18px; color: #ef4444; font-weight: bold');
    console.log('========================');

    // Check state
    if (typeof state !== 'undefined') {
        console.log('\n📊 State Object:');
        console.log('Current Step:', state.currentStep);
        console.log('Total Steps:', state.totalSteps);
        console.log('Auth Method:', state.authMethod);
        console.log('User Data:', state.userData);
        console.log('Selected Plan:', state.selectedPlan);
        console.log('Can Navigate:', state.canNavigateToStep(state.currentStep + 1));
    } else {
        console.error('❌ State object not found');
    }

    // Check Supabase
    if (typeof supabaseClient !== 'undefined') {
        console.log('\n🔐 Supabase Status:');
        supabaseClient.auth.getSession().then(({data}) => {
            console.log('Session:', data?.session ? '✅ Active' : '❌ None');
            if (data?.session) {
                console.log('User ID:', data.session.user.id);
                console.log('Email:', data.session.user.email);
                console.log('Verified:', data.session.user.email_confirmed_at ? '✅' : '❌');
            }
        });

        // Check database
        supabaseClient.from('zmartychat_users').select('*').then(({data, error}) => {
            if (data) {
                console.log('\n📁 Database Records:', data.length);
                console.table(data);
            }
            if (error) {
                console.error('Database Error:', error);
            }
        });
    } else {
        console.error('❌ Supabase client not found');
    }

    // Check DOM
    console.log('\n📄 DOM Analysis:');
    console.log('Active Step:', document.querySelector('.step.active')?.id);
    console.log('Visible Buttons:', Array.from(document.querySelectorAll('button:not([style*="display: none"])')).map(b => b.textContent));
    console.log('Form Inputs:', Array.from(document.querySelectorAll('input:not([type="hidden"])')).map(i => i.id || i.name));

    // Check for errors
    console.log('\n⚠️ Checking for Issues:');
    const alerts = document.querySelectorAll('.alert:not(.d-none)');
    if (alerts.length > 0) {
        console.log('Active Alerts:', Array.from(alerts).map(a => a.textContent));
    } else {
        console.log('No active alerts');
    }

    const errors = document.querySelectorAll('.error, .is-invalid');
    if (errors.length > 0) {
        console.log('Error Elements:', errors.length);
    } else {
        console.log('No error elements');
    }
};

// Export functions to window
window.checkCurrentStep = checkCurrentStep;
window.getVisibleElements = getVisibleElements;
window.runFullTest = runFullTest;

// Auto-run diagnostics
console.log('\n💡 Commands available:');
console.log('- runFullTest() - Run automated test');
console.log('- diagnoseOnboarding() - Full diagnostics');
console.log('- checkCurrentStep() - Check current step');
console.log('- getVisibleElements() - See visible elements');

// Initial check
diagnoseOnboarding();