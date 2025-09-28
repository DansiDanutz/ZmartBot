const puppeteer = require('puppeteer');

async function huntBugs() {
    console.log('🎯 BUG HUNTER - COMPREHENSIVE TESTING\n');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });

    const page = await browser.newPage();
    let bugs = [];

    try {
        await page.goto('http://localhost:8891');

        // Test 1: Check all steps have proper content
        console.log('📋 Test 1: Step Content Check');
        for (let i = 1; i <= 9; i++) {
            const hasProperContent = await page.$eval(`#step${i}`, el => {
                const heading = el.querySelector('h2, h3, h1');
                const hasText = el.textContent.trim().length > 10;
                const hasElements = el.children.length > 0;
                return heading && hasText && hasElements;
            }).catch(() => false);

            if (!hasProperContent) {
                bugs.push(`Step ${i} lacks proper content (no heading/text/elements)`);
                console.log(`  ❌ Step ${i}: Missing content`);
            } else {
                console.log(`  ✅ Step ${i}: Has content`);
            }
        }

        // Test 2: Navigation restrictions
        console.log('\n📋 Test 2: Navigation Security');

        // Try to jump to Step 5 directly
        const canJumpToStep5 = await page.evaluate(() => {
            // Try to call the global function if it exists
            if (typeof window.navigateToStep === 'function') {
                window.navigateToStep(5);
            } else {
                // Try clicking on step dot 5
                const dot5 = document.querySelector('.step-dots .step-dot:nth-child(5)');
                if (dot5) dot5.click();
            }
            return document.querySelector('#step5').classList.contains('active');
        });

        if (canJumpToStep5) {
            bugs.push('Security issue: Can jump to Step 5 without completing previous steps');
            console.log('  ❌ Can jump to later steps');
        } else {
            console.log('  ✅ Cannot jump ahead');
        }

        // Test 3: Form validation
        console.log('\n📋 Test 3: Form Validation');
        await page.reload();
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        // Test empty form submission
        await page.click('#regEmailBtn');
        await new Promise(r => setTimeout(r, 500));

        const emptyFormBlocked = await page.$eval('#authAlert', el =>
            window.getComputedStyle(el).display !== 'none'
        ).catch(() => false);

        if (!emptyFormBlocked) {
            bugs.push('Form validation: Empty form can be submitted');
            console.log('  ❌ Empty form not blocked');
        } else {
            console.log('  ✅ Empty form blocked');
        }

        // Test invalid email
        await page.type('#regEmail', 'notanemail');
        await page.type('#regPassword', 'short');
        await page.type('#regConfirmPassword', 'different');
        await page.click('#regEmailBtn');
        await new Promise(r => setTimeout(r, 500));

        const invalidBlocked = await page.$eval('#authAlert', el =>
            window.getComputedStyle(el).display !== 'none'
        ).catch(() => false);

        if (!invalidBlocked) {
            bugs.push('Form validation: Invalid email/password accepted');
            console.log('  ❌ Invalid data not validated');
        } else {
            console.log('  ✅ Invalid data blocked');
        }

        // Test 4: Step indicators
        console.log('\n📋 Test 4: Step Indicators');
        const dots = await page.$$('.step-dot');
        if (dots.length !== 9) {
            bugs.push(`Wrong number of step dots: ${dots.length} instead of 9`);
            console.log(`  ❌ ${dots.length} dots instead of 9`);
        } else {
            console.log('  ✅ 9 step dots present');
        }

        // Check active dot matches active step
        const activeDotIndex = await page.$$eval('.step-dot', dots => {
            return dots.findIndex(d => d.classList.contains('active')) + 1;
        });

        const activeStepIndex = await page.$$eval('.step', steps => {
            return steps.findIndex(s => s.classList.contains('active')) + 1;
        });

        if (activeDotIndex !== activeStepIndex) {
            bugs.push('Step dot indicator doesn\'t match active step');
            console.log(`  ❌ Dot ${activeDotIndex} vs Step ${activeStepIndex}`);
        } else {
            console.log('  ✅ Indicators match');
        }

        // Test 5: Mobile responsiveness
        console.log('\n📋 Test 5: Mobile Responsiveness');
        const viewport = await page.evaluate(() => {
            return {
                width: window.innerWidth,
                height: window.innerHeight
            };
        });

        if (viewport.width > 500) {
            bugs.push('Not mobile optimized - viewport too wide');
            console.log(`  ❌ Width: ${viewport.width}px (should be ≤450)`);
        } else {
            console.log('  ✅ Mobile viewport OK');
        }

        // Test 6: Back navigation
        console.log('\n📋 Test 6: Back Navigation');
        const prevArrow = await page.$('#prevArrow');
        if (prevArrow) {
            await prevArrow.click();
            await new Promise(r => setTimeout(r, 500));

            const backOnStep1 = await page.$eval('#step1', el =>
                el.classList.contains('active')
            ).catch(() => false);

            if (!backOnStep1) {
                bugs.push('Back navigation not working from Step 2');
                console.log('  ❌ Back arrow failed');
            } else {
                console.log('  ✅ Back navigation works');
            }
        } else {
            bugs.push('Previous arrow button not found');
            console.log('  ❌ No back button');
        }

        // Test 7: Session persistence
        console.log('\n📋 Test 7: Session Storage');
        const hasSession = await page.evaluate(() => {
            return sessionStorage.getItem('onboarding_state') !== null;
        });

        if (!hasSession) {
            bugs.push('Session storage not saving progress');
            console.log('  ❌ No session storage');
        } else {
            console.log('  ✅ Session storage working');
        }

    } catch (error) {
        bugs.push(`Test error: ${error.message}`);
    } finally {
        setTimeout(() => browser.close(), 3000);
    }

    // Final Report
    console.log('\n' + '='.repeat(50));
    console.log('🔍 BUG HUNT COMPLETE\n');

    if (bugs.length === 0) {
        console.log('🎉 NO BUGS FOUND! System is solid.');
    } else {
        console.log(`⚠️ Found ${bugs.length} issue(s):\n`);
        bugs.forEach((bug, i) => {
            console.log(`${i+1}. ${bug}`);
        });
        console.log('\n🔧 Next: Fix the first bug...');
    }

    return bugs;
}

huntBugs().catch(console.error);