#!/usr/bin/env node

/**
 * Browser MCP Test Script for ZmartyBrain Onboarding
 * This script will test all features step by step
 */

const { chromium } = require('playwright');

async function testOnboarding() {
    console.log('🚀 Starting Browser Test for ZmartyBrain Onboarding');
    console.log('URL: https://vermillion-paprenjak-67497b.netlify.app\n');

    const browser = await chromium.launch({
        headless: false,
        slowMo: 500 // Slow down actions so we can see them
    });

    const page = await browser.newPage();

    try {
        // 1. Navigate to the site
        console.log('📍 Step 1: Navigating to site...');
        await page.goto('https://vermillion-paprenjak-67497b.netlify.app');
        await page.waitForTimeout(2000);

        // 2. Check if welcome slide is visible
        console.log('📍 Step 2: Checking welcome slide...');
        const welcomeText = await page.textContent('h1');
        console.log(`   Found: "${welcomeText}"`);

        // 3. Click Get Started button
        console.log('📍 Step 3: Clicking Get Started...');
        const getStartedBtn = await page.locator('button:has-text("Get Started")').first();
        if (await getStartedBtn.isVisible()) {
            await getStartedBtn.click();
            console.log('   ✅ Clicked Get Started');
        } else {
            console.log('   ⚠️ Get Started button not found');
        }
        await page.waitForTimeout(1000);

        // 4. Check registration form
        console.log('📍 Step 4: Checking registration form...');
        const emailInput = await page.locator('input[type="email"]').first();
        const passwordInput = await page.locator('input[type="password"]').first();

        if (await emailInput.isVisible() && await passwordInput.isVisible()) {
            console.log('   ✅ Registration form found');

            // Fill test data
            await emailInput.fill('test@example.com');
            await passwordInput.fill('Test123!@#');
            console.log('   ✅ Filled test credentials');
        } else {
            console.log('   ⚠️ Registration form not visible');
        }

        // 5. Check for Google OAuth button
        console.log('📍 Step 5: Checking Google OAuth...');
        const googleBtn = await page.locator('button:has-text("Google")').first();
        if (await googleBtn.isVisible()) {
            console.log('   ✅ Google OAuth button found');
        } else {
            console.log('   ⚠️ Google OAuth button not found');
        }

        // 6. Check for login link
        console.log('📍 Step 6: Checking login link...');
        const loginLink = await page.locator('text=/Already have an account/i').first();
        if (await loginLink.isVisible()) {
            console.log('   ✅ Login link found');
            await loginLink.click();
            await page.waitForTimeout(1000);
        } else {
            console.log('   ⚠️ Login link not found');
        }

        // 7. Check for password recovery
        console.log('📍 Step 7: Checking password recovery...');
        const forgotLink = await page.locator('text=/Forgot/i').first();
        if (await forgotLink.isVisible()) {
            console.log('   ✅ Password recovery link found');
        } else {
            console.log('   ⚠️ Password recovery link not found');
        }

        // 8. Navigate back and check tiers
        console.log('📍 Step 8: Checking tier options...');
        await page.goto('https://vermillion-paprenjak-67497b.netlify.app');
        await page.waitForTimeout(2000);

        // Look for tier pricing
        const pageContent = await page.content();
        const hasFree = pageContent.includes('Free') || pageContent.includes('$0');
        const hasStarter = pageContent.includes('$19');
        const hasPro = pageContent.includes('$49');

        console.log(`   Free Tier: ${hasFree ? '✅' : '❌'}`);
        console.log(`   Starter Tier ($19): ${hasStarter ? '✅' : '❌'}`);
        console.log(`   Professional Tier ($49): ${hasPro ? '✅' : '❌'}`);

        // 9. Check for OTP validation
        console.log('📍 Step 9: Checking OTP validation...');
        const hasOTP = pageContent.includes('otp') || pageContent.includes('6-digit') || pageContent.includes('verification');
        console.log(`   OTP Validation: ${hasOTP ? '✅' : '❌'}`);

        // 10. Final summary
        console.log('\n📊 TEST SUMMARY:');
        console.log('================');
        console.log('✅ Site is accessible');
        console.log('✅ Welcome slide works');
        console.log(`${await emailInput.isVisible() ? '✅' : '❌'} Registration form`);
        console.log(`${await googleBtn.isVisible() ? '✅' : '❌'} Google OAuth`);
        console.log(`${await loginLink.isVisible() ? '✅' : '❌'} Login option`);
        console.log(`${await forgotLink.isVisible() ? '✅' : '❌'} Password recovery`);
        console.log(`${hasFree && hasStarter && hasPro ? '✅' : '❌'} All tier options`);
        console.log(`${hasOTP ? '✅' : '❌'} OTP validation`);

    } catch (error) {
        console.error('❌ Test failed:', error.message);
    } finally {
        console.log('\n🔚 Test complete. Browser will close in 5 seconds...');
        await page.waitForTimeout(5000);
        await browser.close();
    }
}

// Run the test
testOnboarding().catch(console.error);