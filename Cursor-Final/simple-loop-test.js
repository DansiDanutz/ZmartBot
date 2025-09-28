const puppeteer = require('puppeteer');

async function simpleLoopTest() {
    console.log('🔄 SIMPLE LOOP TEST - CHECKING BASIC FUNCTIONALITY\n');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });

    const page = await browser.newPage();
    let bugs = [];

    try {
        // Test 1: Basic navigation
        console.log('Test 1: Basic Navigation');
        await page.goto('http://localhost:8891');
        await new Promise(r => setTimeout(r, 1000));

        // Check if we can go to step 2
        const step1Btn = await page.$('#step1 .btn-primary');
        if (!step1Btn) {
            bugs.push('Step 1 button not found');
            console.log('❌ No button on Step 1');
        } else {
            await step1Btn.click();
            await new Promise(r => setTimeout(r, 1000));

            const onStep2 = await page.$eval('#step2', el =>
                el.classList.contains('active')
            ).catch(() => false);

            if (onStep2) {
                console.log('✅ Can navigate to Step 2');
            } else {
                bugs.push('Cannot navigate to Step 2');
                console.log('❌ Navigation failed');
            }
        }

        // Test 2: Check if all steps exist
        console.log('\nTest 2: All Steps Present');
        for (let i = 1; i <= 9; i++) {
            const stepExists = await page.$(`#step${i}`);
            if (!stepExists) {
                bugs.push(`Step ${i} missing`);
                console.log(`❌ Step ${i} missing`);
            }
        }
        if (bugs.length === 0) {
            console.log('✅ All 9 steps exist');
        }

        // Test 3: Test authentication form
        console.log('\nTest 3: Auth Form');
        const emailField = await page.$('#regEmail');
        const passwordField = await page.$('#regPassword');
        const confirmField = await page.$('#regConfirmPassword');

        if (!emailField || !passwordField || !confirmField) {
            bugs.push('Auth form fields missing');
            console.log('❌ Form fields missing');
        } else {
            console.log('✅ Auth form fields present');
        }

        // Test 4: Step indicators
        console.log('\nTest 4: Step Dots');
        const dots = await page.$$('.step-dot');
        if (dots.length !== 9) {
            bugs.push(`Wrong number of dots: ${dots.length}`);
            console.log(`❌ ${dots.length} dots instead of 9`);
        } else {
            console.log('✅ 9 step dots present');
        }

        // Test 5: Test arrows
        console.log('\nTest 5: Navigation Arrows');
        const prevArrow = await page.$('#prevArrow');
        const nextArrow = await page.$('#nextArrow');

        if (!prevArrow || !nextArrow) {
            bugs.push('Navigation arrows missing');
            console.log('❌ Arrows missing');
        } else {
            console.log('✅ Arrows present');

            // Try going back to step 1
            await prevArrow.click();
            await new Promise(r => setTimeout(r, 1000));

            const backOnStep1 = await page.$eval('#step1', el =>
                el.classList.contains('active')
            ).catch(() => false);

            if (!backOnStep1) {
                bugs.push('Cannot go back to Step 1');
                console.log('❌ Back navigation failed');
            } else {
                console.log('✅ Back navigation works');
            }
        }

    } catch (error) {
        bugs.push(`Error: ${error.message}`);
        console.error('Test error:', error);
    } finally {
        setTimeout(() => browser.close(), 3000);
    }

    // Final report
    console.log('\n' + '='.repeat(50));
    if (bugs.length === 0) {
        console.log('🎉 PERFECT! No bugs found.');
    } else {
        console.log(`⚠️ Found ${bugs.length} bug(s):`);
        bugs.forEach((bug, i) => {
            console.log(`  ${i+1}. ${bug}`);
        });
    }

    return bugs;
}

simpleLoopTest().catch(console.error);