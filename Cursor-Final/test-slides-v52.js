// Test script for v5.2.0 slide functionality
const puppeteer = require('puppeteer');

const DEPLOYED_URL = 'https://vermillion-paprenjak-67497b.netlify.app/';

async function testSlidesFunctionality() {
    console.log('\n🎯 Testing ZmartyBrain v5.2.0 Onboarding Slides\n');
    console.log('=' . repeat(60));

    const browser = await puppeteer.launch({
        headless: false, // Set to true for automated testing
        defaultViewport: { width: 450, height: 750 }
    });

    const page = await browser.newPage();

    // Enable console logging
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.log('❌ Console Error:', msg.text());
        }
    });

    const issues = [];

    try {
        // 1. Load the page
        console.log('\n📱 Loading deployed site...');
        await page.goto(DEPLOYED_URL, { waitUntil: 'networkidle2' });
        await new Promise(r => setTimeout(r, 2000));

        // 2. Check initial slide (should be slide 1)
        console.log('\n✅ Test 1: Initial slide check');
        let currentSlide = await page.evaluate(() => {
            return window.state ? window.state.currentStep : 1;
        });
        console.log(`   Current slide: ${currentSlide}`);
        if (currentSlide !== 1) {
            issues.push(`Initial slide is ${currentSlide}, should be 1`);
        }

        // 3. Test keyboard navigation (1-9 keys)
        console.log('\n✅ Test 2: Keyboard number navigation (1-9)');
        for (let i = 2; i <= 9; i++) {
            await page.keyboard.press(i.toString());
            await new Promise(r => setTimeout(r, 500));

            currentSlide = await page.evaluate(() => window.state.currentStep);
            console.log(`   Pressed ${i} → Slide ${currentSlide}`);

            if (currentSlide !== i) {
                issues.push(`Number key ${i} didn't navigate to slide ${i} (current: ${currentSlide})`);
            }
        }

        // 4. Test arrow key navigation
        console.log('\n✅ Test 3: Arrow key navigation');

        // Go to slide 5 first
        await page.keyboard.press('5');
        await page.waitForTimeout(500);

        // Test left arrow (should go to slide 4)
        await page.keyboard.press('ArrowLeft');
        await page.waitForTimeout(500);
        currentSlide = await page.evaluate(() => window.state.currentStep);
        console.log(`   Left arrow from slide 5 → Slide ${currentSlide}`);
        if (currentSlide !== 4) {
            issues.push(`Left arrow from slide 5 went to ${currentSlide}, expected 4`);
        }

        // Test right arrow (should go to slide 5)
        await page.keyboard.press('ArrowRight');
        await page.waitForTimeout(500);
        currentSlide = await page.evaluate(() => window.state.currentStep);
        console.log(`   Right arrow from slide 4 → Slide ${currentSlide}`);
        if (currentSlide !== 5) {
            issues.push(`Right arrow from slide 4 went to ${currentSlide}, expected 5`);
        }

        // 5. Test arrow button navigation
        console.log('\n✅ Test 4: Arrow button navigation');

        // Go back to slide 1
        await page.keyboard.press('1');
        await page.waitForTimeout(500);

        // Click next arrow button
        const hasNextArrow = await page.evaluate(() => {
            const nextBtn = document.querySelector('.nav-arrow.next');
            if (nextBtn && !nextBtn.classList.contains('hidden')) {
                nextBtn.click();
                return true;
            }
            return false;
        });

        if (hasNextArrow) {
            await new Promise(r => setTimeout(r, 500));
            currentSlide = await page.evaluate(() => window.state.currentStep);
            console.log(`   Next arrow button → Slide ${currentSlide}`);
            if (currentSlide !== 2) {
                issues.push(`Next arrow from slide 1 went to ${currentSlide}, expected 2`);
            }
        } else {
            console.log('   ⚠️  Next arrow not visible on slide 1');
        }

        // Click prev arrow button
        const hasPrevArrow = await page.evaluate(() => {
            const prevBtn = document.querySelector('.nav-arrow.prev');
            if (prevBtn && !prevBtn.classList.contains('hidden')) {
                prevBtn.click();
                return true;
            }
            return false;
        });

        if (hasPrevArrow) {
            await new Promise(r => setTimeout(r, 500));
            currentSlide = await page.evaluate(() => window.state.currentStep);
            console.log(`   Prev arrow button → Slide ${currentSlide}`);
            if (currentSlide !== 1) {
                issues.push(`Prev arrow from slide 2 went to ${currentSlide}, expected 1`);
            }
        } else {
            console.log('   ⚠️  Prev arrow not visible on slide 2');
        }

        // 6. Test swipe navigation (simulate touch events)
        console.log('\n✅ Test 5: Touch/swipe navigation');

        // Go to slide 3
        await page.keyboard.press('3');
        await page.waitForTimeout(500);

        // Simulate swipe left (should go to slide 4)
        await page.evaluate(() => {
            const container = document.querySelector('.onboarding-container');
            const touch = new Touch({
                identifier: 1,
                target: container,
                clientX: 300,
                clientY: 400
            });

            // Start touch
            container.dispatchEvent(new TouchEvent('touchstart', {
                touches: [touch],
                targetTouches: [touch],
                changedTouches: [touch],
                bubbles: true
            }));

            // Move touch
            const moveTouch = new Touch({
                identifier: 1,
                target: container,
                clientX: 100,
                clientY: 400
            });
            container.dispatchEvent(new TouchEvent('touchmove', {
                touches: [moveTouch],
                targetTouches: [moveTouch],
                changedTouches: [moveTouch],
                bubbles: true
            }));

            // End touch
            container.dispatchEvent(new TouchEvent('touchend', {
                touches: [],
                targetTouches: [],
                changedTouches: [moveTouch],
                bubbles: true
            }));
        });

        await page.waitForTimeout(500);
        currentSlide = await page.evaluate(() => window.state.currentStep);
        console.log(`   Swipe left from slide 3 → Slide ${currentSlide}`);
        if (currentSlide !== 4) {
            issues.push(`Swipe left from slide 3 went to ${currentSlide}, expected 4`);
        }

        // 7. Test state persistence
        console.log('\n✅ Test 6: State persistence (sessionStorage)');

        // Set some test data
        await page.evaluate(() => {
            window.state.userData.testField = 'test-value';
            window.state.selectedPlan = 'professional';
            window.state.saveToStorage();
        });

        // Reload page
        await page.reload({ waitUntil: 'networkidle2' });
        await new Promise(r => setTimeout(r, 1000));

        // Check if state was restored
        const restoredData = await page.evaluate(() => {
            return {
                testField: window.state.userData.testField,
                selectedPlan: window.state.selectedPlan,
                currentStep: window.state.currentStep
            };
        });

        console.log(`   Restored data:`, restoredData);
        if (restoredData.testField !== 'test-value') {
            issues.push('State persistence failed: userData not restored');
        }
        if (restoredData.selectedPlan !== 'professional') {
            issues.push('State persistence failed: selectedPlan not restored');
        }

        // 8. Test slide validation (e.g., can't proceed without email)
        console.log('\n✅ Test 7: Slide validation');

        // Go to slide 2 (auth)
        await page.keyboard.press('2');
        await page.waitForTimeout(500);

        // Try to continue without entering email
        const canProceedWithoutEmail = await page.evaluate(() => {
            const emailInput = document.querySelector('#email');
            const passwordInput = document.querySelector('#password');
            const signupBtn = document.querySelector('#signUpBtn');

            if (emailInput && passwordInput && signupBtn) {
                emailInput.value = '';
                passwordInput.value = '';
                signupBtn.click();

                // Check if we're still on slide 2
                setTimeout(() => {}, 500);
                return window.state.currentStep !== 2;
            }
            return false;
        });

        console.log(`   Can proceed without email: ${canProceedWithoutEmail ? 'YES (BUG!)' : 'NO (correct)'}`);
        if (canProceedWithoutEmail) {
            issues.push('Validation issue: Can proceed from auth slide without email');
        }

        // 9. Test slide visibility
        console.log('\n✅ Test 8: Slide visibility');

        for (let i = 1; i <= 9; i++) {
            await page.keyboard.press(i.toString());
            await new Promise(r => setTimeout(r, 300));

            const visibleSlide = await page.evaluate(() => {
                const slides = document.querySelectorAll('.slide');
                for (let slide of slides) {
                    if (!slide.classList.contains('hidden')) {
                        return slide.getAttribute('data-step');
                    }
                }
                return null;
            });

            console.log(`   Slide ${i}: Visible = ${visibleSlide == i ? '✓' : '✗'}`);
            if (visibleSlide != i) {
                issues.push(`Slide ${i} visibility issue: visible slide is ${visibleSlide}`);
            }
        }

        // 10. Test progress bar
        console.log('\n✅ Test 9: Progress bar updates');

        for (let i = 1; i <= 9; i++) {
            await page.keyboard.press(i.toString());
            await new Promise(r => setTimeout(r, 300));

            const progressWidth = await page.evaluate(() => {
                const progressFill = document.querySelector('.progress-fill');
                return progressFill ? progressFill.style.width : '0%';
            });

            const expectedProgress = Math.round((i / 9) * 100) + '%';
            console.log(`   Slide ${i}: Progress = ${progressWidth} (expected ~${expectedProgress})`);

            // Allow some margin for rounding
            const actualPercent = parseInt(progressWidth);
            const expectedPercent = Math.round((i / 9) * 100);
            if (Math.abs(actualPercent - expectedPercent) > 5) {
                issues.push(`Progress bar on slide ${i}: ${progressWidth} (expected ~${expectedProgress})`);
            }
        }

        // 11. Test slide transitions
        console.log('\n✅ Test 10: Slide transitions');

        const transitionTest = await page.evaluate(async () => {
            const results = [];

            // Test forward transition
            window.state.goToStep(1, 'forward', true);
            await new Promise(r => setTimeout(r, 100));

            const slide1 = document.querySelector('.slide[data-step="1"]');
            const slide2 = document.querySelector('.slide[data-step="2"]');

            window.state.goToStep(2, 'forward', true);

            // Check if transition classes are applied
            const hasTransition = slide2 && slide2.style.transition !== '';
            results.push({
                test: 'Forward transition',
                passed: hasTransition
            });

            await new Promise(r => setTimeout(r, 500));

            // Test backward transition
            window.state.goToStep(1, 'backward', true);
            const hasBackTransition = slide1 && slide1.style.transition !== '';
            results.push({
                test: 'Backward transition',
                passed: hasBackTransition
            });

            return results;
        });

        transitionTest.forEach(test => {
            console.log(`   ${test.test}: ${test.passed ? '✓' : '✗'}`);
            if (!test.passed) {
                issues.push(`Transition issue: ${test.test} failed`);
            }
        });

    } catch (error) {
        console.error('\n❌ Test Error:', error.message);
        issues.push(`Test execution error: ${error.message}`);
    }

    // Report results
    console.log('\n' + '=' . repeat(60));
    console.log('\n📊 TEST RESULTS SUMMARY\n');

    if (issues.length === 0) {
        console.log('✅ ALL TESTS PASSED! No issues found.');
        console.log('   All 9 slides are functioning correctly.');
        console.log('   Navigation methods: ✓ Keyboard ✓ Arrows ✓ Touch');
        console.log('   State management: ✓ Persistence ✓ Validation');
        console.log('   Visual elements: ✓ Progress bar ✓ Transitions');
    } else {
        console.log(`⚠️  FOUND ${issues.length} ISSUE(S):\n`);
        issues.forEach((issue, index) => {
            console.log(`   ${index + 1}. ${issue}`);
        });

        console.log('\n📝 Recommendations:');
        console.log('   - Fix the identified issues');
        console.log('   - Re-test after fixes');
        console.log('   - Consider adding automated tests');
    }

    console.log('\n' + '=' . repeat(60));

    await browser.close();

    return {
        passed: issues.length === 0,
        issues: issues,
        timestamp: new Date().toISOString()
    };
}

// Run the test
testSlidesFunctionality()
    .then(results => {
        process.exit(results.passed ? 0 : 1);
    })
    .catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });