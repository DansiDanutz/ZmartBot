/**
 * Direct Onboarding Testing Script for localhost:8890
 * This script tests the onboarding flow systematically and reports the first bug found
 */

const TEST_URL = 'http://localhost:8890';

async function testOnboardingFlow() {
    console.log('🚀 Starting systematic onboarding flow test...\n');

    try {
        // Step 1: Test if server is accessible
        console.log('📡 Testing server accessibility...');
        const response = await fetch(TEST_URL);

        if (!response.ok) {
            console.log(`❌ FIRST BUG FOUND: Server not responding`);
            console.log(`   Expected: HTTP 200 response`);
            console.log(`   Actual: HTTP ${response.status} ${response.statusText}`);
            return false;
        }

        console.log('✅ Server accessible at localhost:8890');

        // Step 2: Get the HTML content
        console.log('\n📄 Fetching HTML content...');
        const htmlContent = await response.text();

        if (!htmlContent || htmlContent.length < 1000) {
            console.log(`❌ FIRST BUG FOUND: HTML content too short or empty`);
            console.log(`   Expected: Full HTML document (>1000 chars)`);
            console.log(`   Actual: ${htmlContent.length} characters`);
            return false;
        }

        console.log('✅ HTML content loaded successfully');

        // Step 3: Test Slide 1 (Welcome) - Check HTML structure
        console.log('\n🔍 Testing SLIDE 1 (Welcome) HTML structure...');

        // Check if step1 element exists
        if (!htmlContent.includes('id="step1"')) {
            console.log(`❌ FIRST BUG FOUND: Slide 1 element missing`);
            console.log(`   Expected: Element with id="step1"`);
            console.log(`   Actual: id="step1" not found in HTML`);
            return false;
        }
        console.log('✅ Slide 1 element (id="step1") found');

        // Check if Welcome title exists
        if (!htmlContent.includes('Welcome to Zmarty')) {
            console.log(`❌ FIRST BUG FOUND: Welcome title missing`);
            console.log(`   Expected: "Welcome to Zmarty" text`);
            console.log(`   Actual: Welcome text not found`);
            return false;
        }
        console.log('✅ Welcome title found');

        // Check if Start Free Trial button exists
        if (!htmlContent.includes('Start Free Trial')) {
            console.log(`❌ FIRST BUG FOUND: Start Free Trial button missing`);
            console.log(`   Expected: "Start Free Trial" button`);
            console.log(`   Actual: Button text not found`);
            return false;
        }
        console.log('✅ Start Free Trial button found');

        // Step 4: Test Slide 2 (AI Models) structure
        console.log('\n🔍 Testing SLIDE 2 (AI Models) HTML structure...');

        if (!htmlContent.includes('id="step2"')) {
            console.log(`❌ FIRST BUG FOUND: Slide 2 element missing`);
            console.log(`   Expected: Element with id="step2"`);
            console.log(`   Actual: id="step2" not found in HTML`);
            return false;
        }
        console.log('✅ Slide 2 element found');

        // Check for AI Models title
        if (!htmlContent.includes('Powered by Multiple AI Models')) {
            console.log(`❌ FIRST BUG FOUND: AI Models title missing`);
            console.log(`   Expected: "Powered by Multiple AI Models" text`);
            console.log(`   Actual: AI Models title not found`);
            return false;
        }
        console.log('✅ AI Models title found');

        // Check for AI model cards (Claude, GPT-4, etc.)
        const aiModels = ['Claude', 'GPT-4', 'Gemini', 'Grok'];
        const missingModels = aiModels.filter(model => !htmlContent.includes(model));

        if (missingModels.length > 0) {
            console.log(`❌ FIRST BUG FOUND: AI model cards missing`);
            console.log(`   Expected: ${aiModels.join(', ')} model cards`);
            console.log(`   Actual: Missing ${missingModels.join(', ')}`);
            return false;
        }
        console.log('✅ All AI model cards found (Claude, GPT-4, Gemini, Grok)');

        // Step 5: Test Slide 3 (Exchanges) structure
        console.log('\n🔍 Testing SLIDE 3 (Exchanges) HTML structure...');

        if (!htmlContent.includes('id="step3"')) {
            console.log(`❌ FIRST BUG FOUND: Slide 3 element missing`);
            console.log(`   Expected: Element with id="step3"`);
            console.log(`   Actual: id="step3" not found in HTML`);
            return false;
        }
        console.log('✅ Slide 3 element found');

        // Check for Exchanges title
        if (!htmlContent.includes('Track Everything, Everywhere')) {
            console.log(`❌ FIRST BUG FOUND: Exchanges title missing`);
            console.log(`   Expected: "Track Everything, Everywhere" text`);
            console.log(`   Actual: Exchanges title not found`);
            return false;
        }
        console.log('✅ Exchanges title found');

        // Check for major exchanges
        const exchanges = ['Binance', 'Coinbase', 'Kraken'];
        const missingExchanges = exchanges.filter(exchange => !htmlContent.includes(exchange));

        if (missingExchanges.length > 0) {
            console.log(`❌ FIRST BUG FOUND: Exchange cards missing`);
            console.log(`   Expected: ${exchanges.join(', ')} exchange cards`);
            console.log(`   Actual: Missing ${missingExchanges.join(', ')}`);
            return false;
        }
        console.log('✅ Major exchange cards found (Binance, Coinbase, Kraken)');

        // Step 6: Test Slide 4 (Risk Management) structure
        console.log('\n🔍 Testing SLIDE 4 (Risk Management) HTML structure...');

        if (!htmlContent.includes('id="step4"')) {
            console.log(`❌ FIRST BUG FOUND: Slide 4 element missing`);
            console.log(`   Expected: Element with id="step4"`);
            console.log(`   Actual: id="step4" not found in HTML`);
            return false;
        }
        console.log('✅ Slide 4 element found');

        // Check for Risk Management title
        if (!htmlContent.includes('Advanced Risk Management')) {
            console.log(`❌ FIRST BUG FOUND: Risk Management title missing`);
            console.log(`   Expected: "Advanced Risk Management" text`);
            console.log(`   Actual: Risk Management title not found`);
            return false;
        }
        console.log('✅ Risk Management title found');

        // Step 7: Test Slide 5 (Authentication) structure
        console.log('\n🔍 Testing SLIDE 5 (Authentication) HTML structure...');

        if (!htmlContent.includes('id="step5"')) {
            console.log(`❌ FIRST BUG FOUND: Slide 5 element missing`);
            console.log(`   Expected: Element with id="step5"`);
            console.log(`   Actual: id="step5" not found in HTML`);
            return false;
        }
        console.log('✅ Slide 5 element found');

        // Check for Authentication title
        if (!htmlContent.includes('Create Your Account')) {
            console.log(`❌ FIRST BUG FOUND: Authentication title missing`);
            console.log(`   Expected: "Create Your Account" text`);
            console.log(`   Actual: Authentication title not found`);
            return false;
        }
        console.log('✅ Authentication title found');

        // Check for email input
        if (!htmlContent.includes('type="email"')) {
            console.log(`❌ FIRST BUG FOUND: Email input field missing`);
            console.log(`   Expected: input[type="email"] element`);
            console.log(`   Actual: Email input not found`);
            return false;
        }
        console.log('✅ Email input field found');

        // Check for password input
        if (!htmlContent.includes('type="password"')) {
            console.log(`❌ FIRST BUG FOUND: Password input field missing`);
            console.log(`   Expected: input[type="password"] element`);
            console.log(`   Actual: Password input not found`);
            return false;
        }
        console.log('✅ Password input field found');

        // Step 8: Test CSS and JavaScript inclusion
        console.log('\n🔍 Testing CSS and JavaScript inclusion...');

        // Check for CSS styles
        if (!htmlContent.includes('<style>') && !htmlContent.includes('.css')) {
            console.log(`❌ FIRST BUG FOUND: No CSS found`);
            console.log(`   Expected: <style> tags or .css files`);
            console.log(`   Actual: No styling found`);
            return false;
        }
        console.log('✅ CSS styling found');

        // Check for JavaScript functionality
        if (!htmlContent.includes('nextStep') || !htmlContent.includes('goToStep')) {
            console.log(`❌ FIRST BUG FOUND: Navigation JavaScript missing`);
            console.log(`   Expected: nextStep() and goToStep() functions`);
            console.log(`   Actual: Navigation functions not found`);
            return false;
        }
        console.log('✅ Navigation JavaScript found');

        // Final success
        console.log('\n' + '='.repeat(60));
        console.log('🎉 ALL TESTS PASSED! No bugs found in initial analysis.');
        console.log('='.repeat(60));
        console.log('\n💡 NEXT STEPS:');
        console.log('1. Open http://localhost:8890 in your browser');
        console.log('2. Test navigation between slides manually');
        console.log('3. Test form interactions and button clicks');
        console.log('4. Test mobile responsiveness');
        console.log('5. Test authentication flow with real inputs');

        return true;

    } catch (error) {
        console.log(`❌ FIRST BUG FOUND: Server connection error`);
        console.log(`   Expected: Successful HTTP connection`);
        console.log(`   Actual: ${error.message}`);
        return false;
    }
}

// Auto-run the test
testOnboardingFlow().then(success => {
    if (success) {
        console.log('\n✅ Static analysis complete. Manual testing recommended for interactive features.');
    } else {
        console.log('\n❌ Bug found! Please fix the reported issue before proceeding.');
    }
});