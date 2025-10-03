#!/usr/bin/env node

const puppeteer = require('puppeteer');

async function testAllFunctionalities() {
  console.log('🚀 Starting comprehensive functionality test...\n');
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

  const testResults = {
    passed: [],
    failed: [],
    warnings: []
  };

  try {
    const page = await browser.newPage();

    // Enable console logging
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`[Console Error] ${msg.text()}`);
      }
    });

    // Log network errors
    page.on('pageerror', error => {
      console.error(`[Page Error]`, error.message);
      testResults.warnings.push(`Page error: ${error.message}`);
    });

    // ============================================
    // TEST 1: INITIAL PAGE LOAD
    // ============================================
    console.log('📱 TEST 1: INITIAL PAGE LOAD');
    console.log('-'.repeat(40));

    await page.goto('https://vermillion-paprenjak-67497b.netlify.app', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    await new Promise(resolve => setTimeout(resolve, 3000));

    const pageTitle = await page.title();
    console.log(`✓ Page Title: ${pageTitle}`);

    if (pageTitle.includes('ZmartyBrain')) {
      testResults.passed.push('Page title correct');
    } else {
      testResults.failed.push('Page title incorrect');
    }

    // Check if React app loaded
    const reactLoaded = await page.evaluate(() => {
      return !!document.querySelector('#root')?.children.length;
    });

    console.log(`✓ React App Loaded: ${reactLoaded ? 'Yes' : 'No'}`);
    if (reactLoaded) {
      testResults.passed.push('React app loaded');
    } else {
      testResults.failed.push('React app failed to load');
    }

    // ============================================
    // TEST 2: ONBOARDING SLIDES STRUCTURE
    // ============================================
    console.log('\n📊 TEST 2: ONBOARDING SLIDES STRUCTURE');
    console.log('-'.repeat(40));

    // Check for slide container
    const slideStructure = await page.evaluate(() => {
      const slides = document.querySelectorAll('.slide, [class*="slide"]');
      const container = document.querySelector('.onboarding-container, [class*="onboarding"]');
      return {
        hasContainer: !!container,
        slideCount: slides.length,
        currentSlide: document.querySelector('.slide.active, [class*="slide"][class*="active"]')?.innerText?.substring(0, 50)
      };
    });

    console.log(`✓ Onboarding Container: ${slideStructure.hasContainer ? 'Found' : 'Not found'}`);
    console.log(`✓ Number of Slides: ${slideStructure.slideCount}`);
    console.log(`✓ Current Slide: ${slideStructure.currentSlide || 'Unknown'}`);

    if (slideStructure.hasContainer) {
      testResults.passed.push('Onboarding container found');
    } else {
      testResults.failed.push('Onboarding container missing');
    }

    // ============================================
    // TEST 3: NAVIGATION ELEMENTS
    // ============================================
    console.log('\n🔄 TEST 3: NAVIGATION ELEMENTS');
    console.log('-'.repeat(40));

    const navigationElements = await page.evaluate(() => {
      const nextButton = document.querySelector('button[class*="next"], button:has-text("Next"), button:has-text("Continue")');
      const prevButton = document.querySelector('button[class*="prev"], button:has-text("Previous"), button:has-text("Back")');
      const skipButton = document.querySelector('button[class*="skip"], a[class*="skip"], button:has-text("Skip")');
      const indicators = document.querySelectorAll('.indicator, [class*="indicator"], [class*="dot"]');

      return {
        hasNext: !!nextButton,
        hasPrev: !!prevButton,
        hasSkip: !!skipButton,
        indicatorCount: indicators.length,
        nextText: nextButton?.innerText,
        prevText: prevButton?.innerText
      };
    });

    console.log(`✓ Next Button: ${navigationElements.hasNext ? `Found ("${navigationElements.nextText}")` : 'Not found'}`);
    console.log(`✓ Previous Button: ${navigationElements.hasPrev ? `Found ("${navigationElements.prevText}")` : 'Not found'}`);
    console.log(`✓ Skip Link: ${navigationElements.hasSkip ? 'Found' : 'Not found'}`);
    console.log(`✓ Progress Indicators: ${navigationElements.indicatorCount}`);

    // ============================================
    // TEST 4: AUTHENTICATION FORM
    // ============================================
    console.log('\n🔐 TEST 4: AUTHENTICATION FORM');
    console.log('-'.repeat(40));

    // Look for auth form or navigate to it
    const authForm = await page.evaluate(() => {
      const emailInput = document.querySelector('input[type="email"], input[name="email"], input[placeholder*="email" i]');
      const passwordInput = document.querySelector('input[type="password"], input[name="password"]');
      const submitButton = document.querySelector('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")');
      const googleButton = Array.from(document.querySelectorAll('button')).find(b =>
        b.innerText.toLowerCase().includes('google')
      );
      const signUpLink = Array.from(document.querySelectorAll('a, button')).find(el =>
        el.innerText.toLowerCase().includes('sign up') ||
        el.innerText.toLowerCase().includes('create account') ||
        el.innerText.toLowerCase().includes('register')
      );

      return {
        hasEmailInput: !!emailInput,
        hasPasswordInput: !!passwordInput,
        hasSubmitButton: !!submitButton,
        hasGoogleAuth: !!googleButton,
        hasSignUpLink: !!signUpLink,
        emailPlaceholder: emailInput?.placeholder,
        submitText: submitButton?.innerText,
        googleText: googleButton?.innerText
      };
    });

    console.log(`✓ Email Input: ${authForm.hasEmailInput ? `Found (placeholder: "${authForm.emailPlaceholder}")` : 'Not found'}`);
    console.log(`✓ Password Input: ${authForm.hasPasswordInput ? 'Found' : 'Not found'}`);
    console.log(`✓ Submit Button: ${authForm.hasSubmitButton ? `Found ("${authForm.submitText}")` : 'Not found'}`);
    console.log(`✓ Google Auth: ${authForm.hasGoogleAuth ? `Found ("${authForm.googleText}")` : 'Not found'}`);
    console.log(`✓ Sign Up Link: ${authForm.hasSignUpLink ? 'Found' : 'Not found'}`);

    if (authForm.hasEmailInput && authForm.hasPasswordInput) {
      testResults.passed.push('Authentication form found');
    } else {
      testResults.failed.push('Authentication form incomplete');
    }

    // ============================================
    // TEST 5: FORM VALIDATION
    // ============================================
    console.log('\n✅ TEST 5: FORM VALIDATION');
    console.log('-'.repeat(40));

    if (authForm.hasEmailInput && authForm.hasSubmitButton) {
      // Try submitting empty form
      await page.evaluate(() => {
        const submitBtn = document.querySelector('button[type="submit"], button:has-text("Sign In")');
        submitBtn?.click();
      });

      await new Promise(resolve => setTimeout(resolve, 1000));

      const validationState = await page.evaluate(() => {
        const errorMessages = document.querySelectorAll('.error, [class*="error"], [role="alert"]');
        const emailInput = document.querySelector('input[type="email"]');
        const hasRequired = emailInput?.hasAttribute('required');
        const hasValidation = emailInput?.validity ? !emailInput.validity.valid : false;

        return {
          errorCount: errorMessages.length,
          hasRequired: hasRequired,
          hasValidation: hasValidation,
          firstError: errorMessages[0]?.innerText
        };
      });

      console.log(`✓ Error Messages: ${validationState.errorCount} found`);
      console.log(`✓ Required Attribute: ${validationState.hasRequired ? 'Yes' : 'No'}`);
      console.log(`✓ HTML5 Validation: ${validationState.hasValidation ? 'Active' : 'Not active'}`);
      if (validationState.firstError) {
        console.log(`✓ First Error: "${validationState.firstError}"`);
      }

      // Test invalid email
      await page.evaluate(() => {
        const emailInput = document.querySelector('input[type="email"]');
        if (emailInput) {
          emailInput.value = 'invalid-email';
          emailInput.dispatchEvent(new Event('input', { bubbles: true }));
          emailInput.dispatchEvent(new Event('blur', { bubbles: true }));
        }
      });

      await new Promise(resolve => setTimeout(resolve, 500));

      const emailValidation = await page.evaluate(() => {
        const emailInput = document.querySelector('input[type="email"]');
        return emailInput?.validity ? !emailInput.validity.valid : false;
      });

      console.log(`✓ Email Validation: ${emailValidation ? 'Working' : 'Not working'}`);

      if (validationState.hasRequired || validationState.errorCount > 0) {
        testResults.passed.push('Form validation working');
      } else {
        testResults.warnings.push('Form validation may not be configured');
      }
    }

    // ============================================
    // TEST 6: SLIDE NAVIGATION FUNCTIONALITY
    // ============================================
    console.log('\n🎯 TEST 6: SLIDE NAVIGATION');
    console.log('-'.repeat(40));

    // Try to navigate slides
    const slideNavigation = await page.evaluate(async () => {
      const results = { canNavigate: false, slideChanged: false };

      // Get initial state
      const initialContent = document.body.innerText;

      // Try clicking next button
      const nextBtn = document.querySelector('button[class*="next"], button:has-text("Next"), button:has-text("Continue")');
      if (nextBtn) {
        nextBtn.click();
        await new Promise(resolve => setTimeout(resolve, 1000));
        const newContent = document.body.innerText;
        results.slideChanged = initialContent !== newContent;
        results.canNavigate = true;
      }

      // Try keyboard navigation
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight' }));
      await new Promise(resolve => setTimeout(resolve, 500));

      return results;
    });

    console.log(`✓ Can Navigate: ${slideNavigation.canNavigate ? 'Yes' : 'No'}`);
    console.log(`✓ Slide Changed: ${slideNavigation.slideChanged ? 'Yes' : 'No'}`);

    if (slideNavigation.canNavigate) {
      testResults.passed.push('Slide navigation working');
    } else {
      testResults.warnings.push('Slide navigation may not be working');
    }

    // ============================================
    // TEST 7: SUPABASE CONNECTION
    // ============================================
    console.log('\n🔌 TEST 7: SUPABASE CONNECTION');
    console.log('-'.repeat(40));

    const supabaseCheck = await page.evaluate(() => {
      // Check if Supabase is loaded in window
      const hasSupabase = typeof window.supabase !== 'undefined' ||
                         !!window.__SUPABASE_LOADED__ ||
                         !!document.querySelector('script[src*="supabase"]');

      // Check for Supabase in network requests
      const supabaseInNetwork = performance.getEntries()
        .filter(entry => entry.name.includes('supabase'))
        .length > 0;

      // Check localStorage for Supabase tokens
      const hasSupabaseAuth = Object.keys(localStorage).some(key =>
        key.includes('supabase') || key.includes('auth-token')
      );

      return {
        hasSupabase,
        supabaseInNetwork,
        hasSupabaseAuth
      };
    });

    console.log(`✓ Supabase Library: ${supabaseCheck.hasSupabase ? 'Loaded' : 'Not detected'}`);
    console.log(`✓ Supabase Network Calls: ${supabaseCheck.supabaseInNetwork ? 'Found' : 'Not found'}`);
    console.log(`✓ Supabase Auth Storage: ${supabaseCheck.hasSupabaseAuth ? 'Found' : 'Not found'}`);

    if (supabaseCheck.hasSupabase || supabaseCheck.supabaseInNetwork) {
      testResults.passed.push('Supabase integration detected');
    } else {
      testResults.warnings.push('Supabase integration not detected');
    }

    // ============================================
    // TEST 8: RESPONSIVE DESIGN
    // ============================================
    console.log('\n📱 TEST 8: RESPONSIVE DESIGN');
    console.log('-'.repeat(40));

    // Test mobile viewport
    await page.setViewport({ width: 375, height: 667 }); // iPhone SE
    await new Promise(resolve => setTimeout(resolve, 1000));

    const mobileLayout = await page.evaluate(() => {
      const container = document.querySelector('.onboarding-container, [class*="onboarding"], #root > div');
      const isMobileOptimized = window.innerWidth <= 768 &&
                               container?.offsetWidth <= window.innerWidth;
      const hasViewportMeta = !!document.querySelector('meta[name="viewport"]');

      return {
        isMobileOptimized,
        hasViewportMeta,
        containerWidth: container?.offsetWidth,
        windowWidth: window.innerWidth
      };
    });

    console.log(`✓ Mobile Optimized: ${mobileLayout.isMobileOptimized ? 'Yes' : 'No'}`);
    console.log(`✓ Viewport Meta: ${mobileLayout.hasViewportMeta ? 'Found' : 'Not found'}`);
    console.log(`✓ Container Width: ${mobileLayout.containerWidth}px`);
    console.log(`✓ Window Width: ${mobileLayout.windowWidth}px`);

    // Test tablet viewport
    await page.setViewport({ width: 768, height: 1024 }); // iPad
    await new Promise(resolve => setTimeout(resolve, 1000));

    const tabletLayout = await page.evaluate(() => {
      const container = document.querySelector('.onboarding-container, [class*="onboarding"], #root > div');
      return container?.offsetWidth <= window.innerWidth;
    });

    console.log(`✓ Tablet Layout: ${tabletLayout ? 'Responsive' : 'Not responsive'}`);

    // Restore desktop viewport
    await page.setViewport({ width: 1920, height: 1080 });

    if (mobileLayout.isMobileOptimized && mobileLayout.hasViewportMeta) {
      testResults.passed.push('Responsive design working');
    } else {
      testResults.warnings.push('Responsive design needs improvement');
    }

    // ============================================
    // TEST 9: ASSETS AND RESOURCES
    // ============================================
    console.log('\n📦 TEST 9: ASSETS AND RESOURCES');
    console.log('-'.repeat(40));

    const resourceCheck = await page.evaluate(() => {
      const images = document.querySelectorAll('img');
      const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
      const scripts = document.querySelectorAll('script[src]');

      const brokenImages = Array.from(images).filter(img => !img.complete || img.naturalHeight === 0);

      return {
        imageCount: images.length,
        brokenImages: brokenImages.length,
        stylesheetCount: stylesheets.length,
        scriptCount: scripts.length,
        hasLogo: Array.from(images).some(img =>
          img.src.toLowerCase().includes('logo') ||
          img.alt?.toLowerCase().includes('logo')
        )
      };
    });

    console.log(`✓ Images: ${resourceCheck.imageCount} (${resourceCheck.brokenImages} broken)`);
    console.log(`✓ Stylesheets: ${resourceCheck.stylesheetCount}`);
    console.log(`✓ Scripts: ${resourceCheck.scriptCount}`);
    console.log(`✓ Logo: ${resourceCheck.hasLogo ? 'Found' : 'Not found'}`);

    if (resourceCheck.brokenImages === 0) {
      testResults.passed.push('All images loading correctly');
    } else {
      testResults.failed.push(`${resourceCheck.brokenImages} broken images`);
    }

    // ============================================
    // TEST 10: PERFORMANCE METRICS
    // ============================================
    console.log('\n⚡ TEST 10: PERFORMANCE METRICS');
    console.log('-'.repeat(40));

    const metrics = await page.evaluate(() => {
      const perf = performance.getEntriesByType('navigation')[0];
      return {
        domContentLoaded: Math.round(perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart),
        loadComplete: Math.round(perf.loadEventEnd - perf.loadEventStart),
        domInteractive: Math.round(perf.domInteractive),
        firstPaint: performance.getEntriesByName('first-paint')[0]?.startTime
      };
    });

    console.log(`✓ DOM Content Loaded: ${metrics.domContentLoaded}ms`);
    console.log(`✓ Page Load Complete: ${metrics.loadComplete}ms`);
    console.log(`✓ DOM Interactive: ${metrics.domInteractive}ms`);
    if (metrics.firstPaint) {
      console.log(`✓ First Paint: ${Math.round(metrics.firstPaint)}ms`);
    }

    if (metrics.domInteractive < 3000) {
      testResults.passed.push('Good performance metrics');
    } else {
      testResults.warnings.push('Performance could be improved');
    }

    // ============================================
    // TEST 11: SECURITY HEADERS
    // ============================================
    console.log('\n🔒 TEST 11: SECURITY HEADERS');
    console.log('-'.repeat(40));

    const response = await page.goto('https://vermillion-paprenjak-67497b.netlify.app', {
      waitUntil: 'networkidle2'
    });

    const securityHeaders = {
      'strict-transport-security': response.headers()['strict-transport-security'],
      'x-frame-options': response.headers()['x-frame-options'],
      'x-content-type-options': response.headers()['x-content-type-options'],
      'cache-control': response.headers()['cache-control']
    };

    console.log(`✓ HSTS: ${securityHeaders['strict-transport-security'] ? 'Set' : 'Not set'}`);
    console.log(`✓ X-Frame-Options: ${securityHeaders['x-frame-options'] || 'Not set'}`);
    console.log(`✓ X-Content-Type-Options: ${securityHeaders['x-content-type-options'] || 'Not set'}`);
    console.log(`✓ Cache-Control: ${securityHeaders['cache-control'] || 'Not set'}`);

    if (securityHeaders['strict-transport-security']) {
      testResults.passed.push('Security headers configured');
    } else {
      testResults.warnings.push('Some security headers missing');
    }

    // ============================================
    // FINAL SUMMARY
    // ============================================
    console.log('\n' + '='.repeat(60));
    console.log('📊 TEST SUMMARY');
    console.log('='.repeat(60));

    console.log(`\n✅ PASSED TESTS: ${testResults.passed.length}`);
    testResults.passed.forEach(test => console.log(`   • ${test}`));

    if (testResults.failed.length > 0) {
      console.log(`\n❌ FAILED TESTS: ${testResults.failed.length}`);
      testResults.failed.forEach(test => console.log(`   • ${test}`));
    }

    if (testResults.warnings.length > 0) {
      console.log(`\n⚠️ WARNINGS: ${testResults.warnings.length}`);
      testResults.warnings.forEach(warning => console.log(`   • ${warning}`));
    }

    // Take final screenshots
    console.log('\n📸 Taking screenshots...');

    await page.setViewport({ width: 1920, height: 1080 });
    await page.screenshot({
      path: '/Users/dansidanutz/Desktop/ZmartBot/zmart-api/final_desktop.png',
      fullPage: true
    });
    console.log('   ✓ Desktop screenshot: final_desktop.png');

    await page.setViewport({ width: 375, height: 667 });
    await page.screenshot({
      path: '/Users/dansidanutz/Desktop/ZmartBot/zmart-api/final_mobile.png',
      fullPage: true
    });
    console.log('   ✓ Mobile screenshot: final_mobile.png');

    console.log('\n✨ All functionality tests completed!');
    console.log('\n⏳ Browser will remain open for 15 seconds for manual inspection...');

    await new Promise(resolve => setTimeout(resolve, 15000));

  } catch (error) {
    console.error('\n❌ Test suite failed:', error);
    testResults.failed.push(`Test suite error: ${error.message}`);
  } finally {
    await browser.close();
    console.log('\n🎬 Test session ended.');
  }
}

// Run the comprehensive test
testAllFunctionalities().catch(console.error);