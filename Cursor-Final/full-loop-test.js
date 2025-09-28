const puppeteer = require('puppeteer');

async function runFullLoopTest() {
    console.log('🚀 Starting FULL LOOP TEST...\n');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });

    const page = await browser.newPage();
    let bugs = [];

    try {
        await page.goto('http://localhost:8891', { waitUntil: 'networkidle2' });
        console.log('✅ Page loaded\n');

        // Test Step 1
        console.log('Testing Step 1...');
        const step1 = await page.$('#step1.active');
        if (!step1) {
            bugs.push('Step 1 not active');
            return bugs;
        }
        
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));
        
        // Test Step 2
        console.log('Testing Step 2...');
        const step2Active = await page.$eval('#step2', el => el.classList.contains('active')).catch(() => false);
        if (!step2Active) {
            bugs.push('Cannot navigate to Step 2');
            return bugs;
        }
        
        console.log('✅ Navigation works! Testing forms...');
        
        // Test email form
        await page.type('#regEmail', 'test@example.com');
        await page.type('#regPassword', 'Test123!@#');
        await page.type('#regConfirmPassword', 'Test123!@#');
        
        console.log('✅ Forms filled!');
        
    } catch (error) {
        bugs.push(error.message);
    } finally {
        setTimeout(async () => {
            await browser.close();
        }, 3000);
    }

    return bugs;
}

runFullLoopTest().then(bugs => {
    if (bugs.length > 0) {
        console.log('❌ Bugs found:', bugs);
    } else {
        console.log('✅ All tests passed!');
    }
});
