const puppeteer = require('puppeteer');

async function testAllSteps() {
    console.log('🔄 COMPLETE LOOP TEST - ALL STEPS\n');
    
    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });
    
    const page = await browser.newPage();
    let bugs = [];
    
    try {
        await page.goto('http://localhost:8891');
        console.log('📍 Step 1: Welcome...');
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));
        
        console.log('📍 Step 2: Authentication...');
        // Try clicking Create Account without filling form
        const createBtn = await page.$('#regEmailBtn');
        if (createBtn) {
            await createBtn.click();
            await new Promise(r => setTimeout(r, 1000));
            
            // Check for alert
            const alertVisible = await page.$eval('#authAlert', el => 
                window.getComputedStyle(el).display !== 'none'
            ).catch(() => false);
            
            if (!alertVisible) {
                bugs.push('No validation alert when submitting empty form');
            } else {
                console.log('✅ Form validation works');
            }
        }
        
        // Fill form
        await page.type('#regEmail', 'test@example.com');
        await page.type('#regPassword', 'Test123!@#');  
        await page.type('#regConfirmPassword', 'Test123!@#');
        console.log('✅ Forms filled');
        
        // Test navigation arrows
        console.log('📍 Testing navigation arrows...');
        const prevArrow = await page.$('#prevArrow');
        if (prevArrow) {
            await prevArrow.click();
            await new Promise(r => setTimeout(r, 500));
            
            const onStep1 = await page.$eval('#step1', el => 
                el.classList.contains('active')
            ).catch(() => false);
            
            if (!onStep1) {
                bugs.push('Back arrow not working');
            } else {
                console.log('✅ Back arrow works');
                // Go forward again
                await page.click('#nextArrow');
                await new Promise(r => setTimeout(r, 500));
            }
        }
        
        // Test Google tab
        console.log('📍 Testing auth tabs...');
        await page.click('#googleTab');
        await new Promise(r => setTimeout(r, 500));
        
        const googleAuthVisible = await page.$eval('#googleAuth', el => 
            !el.classList.contains('hidden')
        ).catch(() => false);
        
        if (!googleAuthVisible) {
            bugs.push('Google tab switching not working');
        } else {
            console.log('✅ Tab switching works');
        }
        
        // Check all step elements exist
        console.log('📍 Checking all 9 steps exist...');
        for (let i = 1; i <= 9; i++) {
            const exists = await page.$(`#step${i}`);
            if (!exists) {
                bugs.push(`Step ${i} element missing`);
            }
        }
        console.log('✅ All step elements present');
        
        // Check step dots
        const dots = await page.$$('.step-dot');
        if (dots.length !== 9) {
            bugs.push(`Wrong number of step dots: ${dots.length}`);
        } else {
            console.log('✅ All 9 step dots present');
        }
        
    } catch (error) {
        bugs.push(`Error: ${error.message}`);
    } finally {
        setTimeout(() => browser.close(), 3000);
    }
    
    // Report
    console.log('\n' + '='.repeat(50));
    if (bugs.length === 0) {
        console.log('🎉 ALL TESTS PASSED!');
    } else {
        console.log(`⚠️ Found ${bugs.length} bugs:`);
        bugs.forEach((bug, i) => {
            console.log(`${i+1}. ${bug}`);
        });
    }
    
    return bugs;
}

testAllSteps().catch(console.error);
