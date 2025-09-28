#!/usr/bin/env node

const https = require('https');
const { chromium } = require('playwright');

async function analyzeCurrentState() {
    console.log('🔍 ANALYZING CURRENT LIVE STATE');
    console.log('═'.repeat(60));
    console.log('URL: https://vermillion-paprenjak-67497b.netlify.app');
    console.log('Time:', new Date().toISOString());
    console.log('─'.repeat(60));

    // First, check what's in the HTML
    const htmlContent = await new Promise((resolve) => {
        https.get('https://vermillion-paprenjak-67497b.netlify.app', (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => resolve(data));
        });
    });

    console.log('\n📄 HTML CONTENT ANALYSIS:');
    console.log('─'.repeat(40));

    // Check for key features in HTML
    const features = {
        'Has 6 slides': htmlContent.match(/class="slide"/g)?.length === 6,
        'Has email input': htmlContent.includes('type="email"'),
        'Has password input': htmlContent.includes('type="password"'),
        'Has Google tab': htmlContent.includes('googleTab'),
        'Has OTP inputs': htmlContent.includes('code1') && htmlContent.includes('code6'),
        'Has tier $0/Free': htmlContent.includes('Free') || htmlContent.includes('$0'),
        'Has tier $19': htmlContent.includes('$19'),
        'Has tier $49': htmlContent.includes('$49'),
        'Has profile section': htmlContent.includes('profile'),
        'Has dashboard redirect': htmlContent.includes('dashboard'),
        'Has Forgot text (wrong)': htmlContent.includes('showForgotPassword()">Already'),
        'Has Forgot text (correct)': htmlContent.includes('Forgot Password?'),
        'Has terms checkbox': htmlContent.includes('termsCheckbox'),
        'Has welcome email func': htmlContent.includes('sendWelcomeEmail'),
        'Has showLoginForm func': htmlContent.includes('showLoginForm')
    };

    for (const [feature, present] of Object.entries(features)) {
        console.log(`${present ? '✅' : '❌'} ${feature}`);
    }

    // Now test with browser
    console.log('\n🌐 BROWSER INTERACTION TEST:');
    console.log('─'.repeat(40));

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    try {
        await page.goto('https://vermillion-paprenjak-67497b.netlify.app');
        await page.waitForTimeout(2000);

        // Check what's actually visible
        const visibleElements = {
            'Welcome text': await page.locator('h1:has-text("Welcome")').isVisible(),
            'Get Started button': await page.locator('button:has-text("Get Started")').isVisible(),
        };

        // Click Get Started
        const getStarted = await page.locator('button:has-text("Get Started")').first();
        if (await getStarted.isVisible()) {
            await getStarted.click();
            await page.waitForTimeout(1000);

            // Check registration screen
            visibleElements['Email input after click'] = await page.locator('input[type="email"]').isVisible();
            visibleElements['Password input after click'] = await page.locator('input[type="password"]').isVisible();
            visibleElements['Google tab visible'] = await page.locator('#googleTab').isVisible();
            visibleElements['Login link visible'] = await page.locator('text=/Already have/i').isVisible();
            visibleElements['Forgot link visible'] = await page.locator('text=/Forgot/i').isVisible();
            visibleElements['Terms checkbox visible'] = await page.locator('input[type="checkbox"]').isVisible();
        }

        for (const [element, visible] of Object.entries(visibleElements)) {
            console.log(`${visible ? '✅' : '❌'} ${element}`);
        }

    } catch (error) {
        console.error('Browser test error:', error.message);
    } finally {
        await browser.close();
    }

    console.log('\n📊 SUMMARY:');
    console.log('─'.repeat(40));

    const htmlFeatures = Object.values(features).filter(v => v).length;
    const totalFeatures = Object.keys(features).length;

    console.log(`HTML Features: ${htmlFeatures}/${totalFeatures} (${Math.round(htmlFeatures/totalFeatures*100)}%)`);

    if (features['Has Forgot text (wrong)'] && !features['Has Forgot text (correct)']) {
        console.log('\n⚠️  OLD VERSION IS DEPLOYED');
        console.log('The "Forgot Password?" fix has NOT been deployed yet.');
    } else if (features['Has Forgot text (correct)']) {
        console.log('\n✅ NEW VERSION IS DEPLOYED');
        console.log('The fixes have been successfully deployed!');
    }

    console.log('\n═'.repeat(60));
}

analyzeCurrentState().catch(console.error);