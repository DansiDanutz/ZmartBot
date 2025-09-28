const puppeteer = require('puppeteer');

async function testSupabaseSignup() {
    console.log('🔄 Testing Supabase Signup Flow...\n');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });

    const page = await browser.newPage();

    try {
        // Navigate to onboarding
        await page.goto('http://localhost:8891');
        console.log('✅ Page loaded');

        // Go to Step 2 (Authentication)
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        // Generate unique test email
        const testEmail = `test${Date.now()}@example.com`;
        const testPassword = 'Test123!@#';

        console.log(`📧 Testing with: ${testEmail}`);

        // Fill signup form
        await page.type('#regEmail', testEmail);
        await page.type('#regPassword', testPassword);
        await page.type('#regConfirmPassword', testPassword);

        console.log('✅ Form filled');

        // Click Create Account
        await page.click('#regEmailBtn');
        console.log('🔄 Attempting signup...');

        // Wait for response
        await new Promise(r => setTimeout(r, 3000));

        // Check for success or error
        const alertVisible = await page.$eval('#authAlert', el => {
            return window.getComputedStyle(el).display !== 'none';
        }).catch(() => false);

        if (alertVisible) {
            const alertText = await page.$eval('#authAlert', el => el.textContent);
            console.log(`📋 Alert: ${alertText}`);

            if (alertText.includes('verify') || alertText.includes('confirm')) {
                console.log('✅ Signup successful - email verification required');
            } else if (alertText.includes('error')) {
                console.log('❌ Signup error:', alertText);
            } else {
                console.log('ℹ️ Alert message:', alertText);
            }
        }

        // Check if we moved to Step 3
        const onStep3 = await page.$eval('#step3', el =>
            el.classList.contains('active')
        ).catch(() => false);

        if (onStep3) {
            console.log('✅ Successfully navigated to Step 3!');
            console.log('✅ Supabase authentication is working!');
        } else {
            console.log('⚠️ Still on Step 2 - check authentication');
        }

    } catch (error) {
        console.error('❌ Test error:', error.message);
    } finally {
        setTimeout(() => browser.close(), 5000);
    }
}

testSupabaseSignup().catch(console.error);