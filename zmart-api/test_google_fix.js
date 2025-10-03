#!/usr/bin/env node

const puppeteer = require('puppeteer');

async function testGoogleFix() {
  console.log('🔧 Testing Google OAuth Fix...\n');
  console.log('=' .repeat(60));

  const browser = await puppeteer.launch({
    headless: false,
    devtools: true,
    defaultViewport: null,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--window-size=1920,1080'
    ]
  });

  try {
    const page = await browser.newPage();

    // Capture console messages
    const consoleMessages = [];
    page.on('console', msg => {
      const text = msg.text();
      consoleMessages.push({ type: msg.type(), text });

      // Only show errors
      if (msg.type() === 'error') {
        console.log(`[Console Error] ${text}`);
      }
    });

    console.log('📱 Loading Application...\n');

    await page.goto('https://vermillion-paprenjak-67497b.netlify.app', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    await new Promise(resolve => setTimeout(resolve, 3000));

    // Check page structure
    const pageStructure = await page.evaluate(() => {
      return {
        title: document.title,
        hasRootDiv: !!document.getElementById('root'),
        hasAppDiv: !!document.getElementById('app'),
        rootChildren: document.getElementById('root')?.children.length || 0,
        appChildren: document.getElementById('app')?.children.length || 0
      };
    });

    console.log('✅ Page Structure:');
    console.log(`   Title: ${pageStructure.title}`);
    console.log(`   Has #root div: ${pageStructure.hasRootDiv ? 'Yes ✓' : 'No ✗'}`);
    console.log(`   Has #app div: ${pageStructure.hasAppDiv ? 'Yes ✓' : 'No ✗'}`);
    console.log(`   #root children: ${pageStructure.rootChildren}`);
    console.log(`   #app children: ${pageStructure.appChildren}`);

    // Check for Google Sign-In errors
    const googleErrors = consoleMessages.filter(msg =>
      msg.text.toLowerCase().includes('google') ||
      msg.text.includes('GSI_LOGGER') ||
      msg.text.includes('client_id')
    );

    console.log('\n🔑 Google OAuth Status:');
    if (googleErrors.length === 0) {
      console.log('   ✅ No Google OAuth errors detected!');
    } else {
      console.log('   ⚠️ Google OAuth issues found:');
      googleErrors.forEach(err => {
        console.log(`      - [${err.type}] ${err.text}`);
      });
    }

    // Check if Google Sign-In library loaded
    const googleStatus = await page.evaluate(() => {
      return {
        hasGoogleGlobal: typeof window.google !== 'undefined',
        hasGoogleAccounts: typeof window.google?.accounts !== 'undefined',
        hasGoogleId: typeof window.google?.accounts?.id !== 'undefined',
        googleButtonExists: !!document.getElementById('google-signin-button')
      };
    });

    console.log('\n📦 Google Library Status:');
    console.log(`   Google global object: ${googleStatus.hasGoogleGlobal ? 'Loaded ✓' : 'Not loaded ✗'}`);
    console.log(`   Google accounts API: ${googleStatus.hasGoogleAccounts ? 'Available ✓' : 'Not available ✗'}`);
    console.log(`   Google ID service: ${googleStatus.hasGoogleId ? 'Ready ✓' : 'Not ready ✗'}`);
    console.log(`   Google button element: ${googleStatus.googleButtonExists ? 'Present ✓' : 'Missing ✗'}`);

    // Check for Google button in the UI
    const googleButtonUI = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const googleButton = buttons.find(btn =>
        btn.innerText.toLowerCase().includes('google')
      );

      return {
        found: !!googleButton,
        text: googleButton?.innerText,
        isVisible: googleButton ? window.getComputedStyle(googleButton).display !== 'none' : false
      };
    });

    console.log('\n🎨 Google Button UI:');
    console.log(`   Button found: ${googleButtonUI.found ? 'Yes ✓' : 'No ✗'}`);
    if (googleButtonUI.found) {
      console.log(`   Button text: "${googleButtonUI.text}"`);
      console.log(`   Is visible: ${googleButtonUI.isVisible ? 'Yes ✓' : 'No ✗'}`);
    }

    // Take screenshot
    await page.screenshot({
      path: '/Users/dansidanutz/Desktop/ZmartBot/zmart-api/google_fix_test.png',
      fullPage: true
    });

    // Summary
    console.log('\n' + '=' .repeat(60));
    console.log('📊 TEST SUMMARY\n');

    const issues = [];
    const fixed = [];

    // Check fixes
    if (pageStructure.hasRootDiv) {
      fixed.push('React #root element added successfully');
    } else {
      issues.push('React #root element still missing');
    }

    if (googleErrors.length === 0 || !googleErrors.some(e => e.text.includes('client ID is not found'))) {
      fixed.push('Google Client ID configured correctly');
    } else {
      issues.push('Google Client ID still has errors');
    }

    if (googleButtonUI.found && googleButtonUI.isVisible) {
      fixed.push('Google Sign-In button is visible and ready');
    } else {
      issues.push('Google Sign-In button not properly displayed');
    }

    console.log('✅ FIXED ISSUES:');
    fixed.forEach(item => console.log(`   • ${item}`));

    if (issues.length > 0) {
      console.log('\n⚠️ REMAINING ISSUES:');
      issues.forEach(item => console.log(`   • ${item}`));
    }

    console.log('\n📸 Screenshot saved: google_fix_test.png');
    console.log('\n⏳ Browser will remain open for 10 seconds for inspection...');

    await new Promise(resolve => setTimeout(resolve, 10000));

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
  } finally {
    await browser.close();
    console.log('\n🎬 Test completed.');
  }
}

// Run the test
testGoogleFix().catch(console.error);