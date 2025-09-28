const puppeteer = require('puppeteer');

async function testStepsBug() {
    console.log('🔍 INVESTIGATING STEPS DISAPPEARING BUG\n');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });

    const page = await browser.newPage();

    try {
        await page.goto('http://localhost:8891');

        // Check steps at start
        console.log('Initial state:');
        for (let i = 1; i <= 9; i++) {
            const exists = await page.$(`#step${i}`);
            console.log(`  Step ${i}: ${exists ? '✅ Exists' : '❌ Missing'}`);
        }

        // Navigate to Step 2
        console.log('\nAfter navigating to Step 2:');
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        for (let i = 1; i <= 9; i++) {
            const exists = await page.$(`#step${i}`);
            console.log(`  Step ${i}: ${exists ? '✅ Exists' : '❌ Missing'}`);
        }

        // Switch to Google tab
        console.log('\nAfter switching to Google tab:');
        await page.click('#googleTab');
        await new Promise(r => setTimeout(r, 1000));

        for (let i = 1; i <= 9; i++) {
            const exists = await page.$(`#step${i}`);
            console.log(`  Step ${i}: ${exists ? '✅ Exists' : '❌ Missing'}`);
        }

        // Check if steps are hidden or removed
        const step3Display = await page.$eval('#step3', el => {
            return window.getComputedStyle(el).display;
        }).catch(() => 'element not found');

        console.log(`\nStep 3 display style: ${step3Display}`);

        // Check parent container
        const containerChildren = await page.$$eval('.onboarding-container', els => {
            return els[0].children.length;
        }).catch(() => 0);

        console.log(`Container has ${containerChildren} children`);

    } catch (error) {
        console.error('Error:', error.message);
    } finally {
        setTimeout(() => browser.close(), 3000);
    }
}

testStepsBug().catch(console.error);