const puppeteer = require('puppeteer');

async function testSupabaseRegistration() {
    console.log('🔐 Testing Supabase Registration...');
    
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });
    
    const page = await browser.newPage();
    const testEmail = 'test' + Date.now() + '@example.com';
    
    try {
        await page.goto('http://localhost:8891');
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));
        
        console.log('Testing with email:', testEmail);
        await page.type('#regEmail', testEmail);
        await page.type('#regPassword', 'Test123\!@#');
        await page.type('#regConfirmPassword', 'Test123\!@#');
        
        console.log('Submitting registration...');
        await page.click('#regEmailBtn');
        await new Promise(r => setTimeout(r, 3000));
        
        const alertText = await page.$eval('#authAlert', el => el.textContent).catch(() => '');
        console.log('Response:', alertText || 'No alert shown');
        
        const onStep4 = await page.$eval('#step4', el => el.classList.contains('active')).catch(() => false);
        
        if (onStep4) {
            console.log('✅ Successfully navigated to email verification\!');
        } else {
            console.log('⚠️ Did not navigate to verification step');
        }
    } catch (error) {
        console.log('❌ Error:', error.message);
    } finally {
        setTimeout(() => browser.close(), 5000);
    }
}

testSupabaseRegistration().catch(console.error);
