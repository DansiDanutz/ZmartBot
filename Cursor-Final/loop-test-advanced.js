const puppeteer = require('puppeteer');

async function advancedLoopTest() {
    console.log('🔄 ADVANCED LOOP TEST - FINDING ALL BUGS\n');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });

    const page = await browser.newPage();
    let bugs = [];

    try {
        await page.goto('http://localhost:8891');
        console.log('📍 Testing Step Navigation...\n');

        // Test Step 1 → 2
        console.log('Step 1 → 2:');
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        const step2Active = await page.$eval('#step2', el => el.classList.contains('active')).catch(() => false);
        if (step2Active) {
            console.log('✅ Can navigate to Step 2');
        } else {
            bugs.push('Cannot navigate from Step 1 to Step 2');
        }

        // Try to navigate to Step 3 without auth
        console.log('\nStep 2 → 3 (without auth):');
        const nextBtn = await page.$('#step2 #nextArrow');
        if (nextBtn) {
            await nextBtn.click();
            await new Promise(r => setTimeout(r, 1000));

            const step3Active = await page.$eval('#step3', el => el.classList.contains('active')).catch(() => false);
            if (step3Active) {
                bugs.push('BUG: Can navigate to Step 3 without authentication!');
                console.log('❌ BUG: Can navigate to Step 3 without auth');
            } else {
                console.log('✅ Correctly blocked without auth');
            }
        }

        // Test Google OAuth button
        console.log('\nTesting OAuth buttons:');
        // First switch to Google tab
        await page.click('#googleTab');
        await new Promise(r => setTimeout(r, 500));

        const googleBtn = await page.$('#googleLoginBtn');
        if (googleBtn) {
            await googleBtn.click();
            await new Promise(r => setTimeout(r, 2000));

            // Check if popup opened or error occurred
            const pages = await browser.pages();
            if (pages.length > 2) {
                console.log('✅ Google OAuth popup opened');
                // Close popup
                await pages[pages.length - 1].close();
            } else {
                const alertVisible = await page.$eval('#authAlert', el =>
                    window.getComputedStyle(el).display !== 'none'
                ).catch(() => false);

                if (!alertVisible) {
                    bugs.push('Google OAuth button does nothing');
                    console.log('❌ Google OAuth button not working');
                }
            }
        } else {
            bugs.push('Google Sign In button not found');
        }

        // Test Step 3-9 elements
        console.log('\nChecking Steps 3-9 content:');
        for (let i = 3; i <= 9; i++) {
            const stepExists = await page.$(`#step${i}`);
            if (!stepExists) {
                bugs.push(`Step ${i} element missing`);
                continue;
            }

            // Check if step has content
            const hasContent = await page.$eval(`#step${i}`, el => {
                return el.children.length > 0 && el.textContent.trim().length > 0;
            }).catch(() => false);

            if (!hasContent) {
                bugs.push(`Step ${i} has no content`);
                console.log(`❌ Step ${i}: No content`);
            } else {
                console.log(`✅ Step ${i}: Has content`);
            }
        }

        // Test swipe navigation
        console.log('\nTesting swipe gestures:');
        await page.evaluate(() => {
            const container = document.querySelector('.onboarding-container');
            const touchStart = new TouchEvent('touchstart', {
                touches: [{ clientX: 300, clientY: 400 }]
            });
            const touchMove = new TouchEvent('touchmove', {
                touches: [{ clientX: 100, clientY: 400 }]
            });
            const touchEnd = new TouchEvent('touchend', {
                changedTouches: [{ clientX: 100, clientY: 400 }]
            });

            container.dispatchEvent(touchStart);
            container.dispatchEvent(touchMove);
            container.dispatchEvent(touchEnd);
        });

        await new Promise(r => setTimeout(r, 500));

        const swipeWorked = await page.$eval('#step3', el => el.classList.contains('active')).catch(() => false);
        if (swipeWorked) {
            console.log('✅ Swipe navigation works');
        } else {
            bugs.push('Swipe gestures not working');
            console.log('❌ Swipe not working');
        }

        // Test step dots
        console.log('\nTesting step dots navigation:');
        const dot5 = await page.$('.step-dots .step-dot:nth-child(5)');
        if (dot5) {
            await dot5.click();
            await new Promise(r => setTimeout(r, 500));

            const onStep5 = await page.$eval('#step5', el => el.classList.contains('active')).catch(() => false);
            if (onStep5) {
                bugs.push('BUG: Can jump to Step 5 without completing previous steps!');
                console.log('❌ BUG: Can jump to Step 5 directly');
            } else {
                console.log('✅ Step dots correctly restricted');
            }
        }

        // Test form validation on Step 2
        console.log('\nTesting form validation:');
        await page.goto('http://localhost:8891');
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        // Test with invalid email
        await page.type('#regEmail', 'notanemail');
        await page.type('#regPassword', '123');
        await page.type('#regConfirmPassword', '456');
        await page.click('#regEmailBtn');
        await new Promise(r => setTimeout(r, 1000));

        const validationError = await page.$eval('#authAlert', el => {
            return window.getComputedStyle(el).display !== 'none';
        }).catch(() => false);

        if (validationError) {
            console.log('✅ Form validation works');
        } else {
            bugs.push('No validation for invalid email/password');
            console.log('❌ Form validation not working');
        }

    } catch (error) {
        bugs.push(`Test error: ${error.message}`);
    } finally {
        setTimeout(() => browser.close(), 3000);
    }

    // Report
    console.log('\n' + '='.repeat(50));
    console.log('🔍 LOOP TEST COMPLETE\n');

    if (bugs.length === 0) {
        console.log('🎉 NO BUGS FOUND! All systems working.');
    } else {
        console.log(`⚠️ Found ${bugs.length} bug(s) to fix:\n`);
        bugs.forEach((bug, i) => {
            console.log(`${i+1}. ${bug}`);
        });
        console.log('\n🔧 Working on first bug...');
    }

    return bugs;
}

advancedLoopTest().catch(console.error);