const puppeteer = require('puppeteer');

async function testLiveDeployment() {
    console.log('🌐 Testing Live Deployment: https://vermillion-paprenjak-67497b.netlify.app');
    console.log('=' .repeat(60));

    let browser;
    const results = {
        url: 'https://vermillion-paprenjak-67497b.netlify.app',
        timestamp: new Date().toISOString(),
        tests: []
    };

    try {
        browser = await puppeteer.launch({
            headless: false,
            devtools: true
        });

        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });

        // Test 1: Page Load
        console.log('\n📱 Test 1: Page Load...');
        const startTime = Date.now();
        const response = await page.goto(results.url, { waitUntil: 'networkidle2' });
        const loadTime = Date.now() - startTime;

        results.tests.push({
            name: 'Page Load',
            status: response.status() === 200 ? '✅ PASS' : '❌ FAIL',
            details: `Status: ${response.status()}, Load time: ${loadTime}ms`
        });
        console.log(`   Status: ${response.status()} - Load Time: ${loadTime}ms`);

        // Test 2: Check Essential Elements
        console.log('\n🔍 Test 2: Essential Elements...');
        const elements = await page.evaluate(() => {
            return {
                logo: !!document.querySelector('.logo'),
                welcomeText: !!document.querySelector('h1'),
                getStartedButton: !!document.querySelector('.btn-primary'),
                progressBar: !!document.querySelector('.progress-bar'),
                step1Active: !!document.querySelector('#step1.active')
            };
        });

        const allElementsPresent = Object.values(elements).every(v => v === true);
        results.tests.push({
            name: 'Essential Elements',
            status: allElementsPresent ? '✅ PASS' : '❌ FAIL',
            details: elements
        });
        console.log(`   Elements: ${JSON.stringify(elements, null, 2)}`);

        // Test 3: Navigation
        console.log('\n🚀 Test 3: Navigation...');
        await page.click('.btn-primary');
        await new Promise(resolve => setTimeout(resolve, 1000));

        const onStep2 = await page.evaluate(() => {
            const activeStep = document.querySelector('.step.active');
            return activeStep?.id === 'step2';
        });

        results.tests.push({
            name: 'Navigation to Step 2',
            status: onStep2 ? '✅ PASS' : '❌ FAIL',
            details: `Navigated to step 2: ${onStep2}`
        });
        console.log(`   Navigation works: ${onStep2}`);

        // Test 4: Supabase Connection
        console.log('\n🔌 Test 4: Supabase Connection...');
        const supabaseConnected = await page.evaluate(() => {
            return typeof window.supabase !== 'undefined';
        });

        results.tests.push({
            name: 'Supabase Client',
            status: supabaseConnected ? '✅ PASS' : '❌ FAIL',
            details: `Supabase client initialized: ${supabaseConnected}`
        });
        console.log(`   Supabase connected: ${supabaseConnected}`);

        // Test 5: Mobile Responsive
        console.log('\n📱 Test 5: Mobile Responsive...');
        await page.setViewport({ width: 375, height: 667 });
        await new Promise(resolve => setTimeout(resolve, 500));

        const mobileLayout = await page.evaluate(() => {
            const container = document.querySelector('.onboarding-container');
            if (!container) return false;
            const rect = container.getBoundingClientRect();
            return rect.width <= window.innerWidth;
        });

        results.tests.push({
            name: 'Mobile Layout',
            status: mobileLayout ? '✅ PASS' : '❌ FAIL',
            details: `Mobile layout fits viewport: ${mobileLayout}`
        });
        console.log(`   Mobile responsive: ${mobileLayout}`);

        // Test 6: PWA Features
        console.log('\n📲 Test 6: PWA Features...');
        const pwaReady = await page.evaluate(() => {
            return {
                manifest: !!document.querySelector('link[rel="manifest"]'),
                serviceWorker: 'serviceWorker' in navigator
            };
        });

        results.tests.push({
            name: 'PWA Support',
            status: pwaReady.manifest && pwaReady.serviceWorker ? '✅ PASS' : '⚠️  PARTIAL',
            details: pwaReady
        });
        console.log(`   PWA ready: ${JSON.stringify(pwaReady)}`);

        // Test 7: Console Errors
        console.log('\n⚠️  Test 7: Console Errors...');
        const errors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                errors.push(msg.text());
            }
        });
        await page.reload();
        await new Promise(resolve => setTimeout(resolve, 2000));

        results.tests.push({
            name: 'Console Errors',
            status: errors.length === 0 ? '✅ PASS' : '⚠️  WARNING',
            details: errors.length > 0 ? errors : 'No console errors'
        });
        console.log(`   Console errors: ${errors.length === 0 ? 'None' : errors.join(', ')}`);

        // Generate Report
        console.log('\n' + '='.repeat(60));
        console.log('📊 DEPLOYMENT TEST RESULTS');
        console.log('='.repeat(60));

        const passed = results.tests.filter(t => t.status.includes('PASS')).length;
        const total = results.tests.length;
        const score = Math.round((passed / total) * 100);

        console.log(`\n🎯 Score: ${score}% (${passed}/${total} tests passed)`);
        console.log(`🌐 URL: ${results.url}`);
        console.log(`⏱️  Tested at: ${new Date().toLocaleString()}`);

        console.log('\n📋 Test Summary:');
        results.tests.forEach((test, i) => {
            console.log(`   ${i + 1}. ${test.status} ${test.name}`);
        });

        if (score === 100) {
            console.log('\n✨ PERFECT! Deployment is 100% ready!');
        } else if (score >= 80) {
            console.log('\n✅ GOOD! Deployment is functional with minor issues.');
        } else {
            console.log('\n⚠️  NEEDS ATTENTION! Some tests failed.');
        }

        return results;

    } catch (error) {
        console.error('\n❌ Test failed:', error.message);
        results.error = error.message;
    } finally {
        if (browser) {
            await browser.close();
        }
    }

    return results;
}

// Run the test
testLiveDeployment().then(results => {
    console.log('\n💾 Test complete. Results saved.');
    process.exit(results.error ? 1 : 0);
});