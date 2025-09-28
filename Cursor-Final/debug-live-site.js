const puppeteer = require('puppeteer');

async function debugLiveSite() {
    console.log('🔍 Debugging Live Site Issues...\n');

    const browser = await puppeteer.launch({
        headless: false,
        devtools: true,
        args: ['--window-size=1920,1080']
    });

    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });

        console.log('📱 Loading site...');
        await page.goto('https://vermillion-paprenjak-67497b.netlify.app', {
            waitUntil: 'networkidle2'
        });

        // Take screenshot of initial state
        await page.screenshot({
            path: 'issue-step1.png',
            fullPage: true
        });
        console.log('📸 Screenshot saved: issue-step1.png');

        // Check for duplicate text
        console.log('\n🔍 Checking for duplicate elements...');
        const duplicates = await page.evaluate(() => {
            const allSteps = document.querySelectorAll('.step');
            const visibleSteps = [];

            allSteps.forEach((step, index) => {
                const styles = window.getComputedStyle(step);
                const rect = step.getBoundingClientRect();

                if (styles.display !== 'none' &&
                    styles.visibility !== 'hidden' &&
                    styles.opacity !== '0' &&
                    rect.width > 0 &&
                    rect.height > 0) {
                    visibleSteps.push({
                        id: step.id,
                        display: styles.display,
                        visibility: styles.visibility,
                        opacity: styles.opacity,
                        zIndex: styles.zIndex,
                        position: styles.position,
                        transform: styles.transform,
                        hasActiveClass: step.classList.contains('active')
                    });
                }
            });

            return visibleSteps;
        });

        console.log('Visible steps:', JSON.stringify(duplicates, null, 2));

        // Try to navigate to step 2
        console.log('\n🚀 Attempting navigation to Step 2...');

        // Click Get Started button
        const clicked = await page.evaluate(() => {
            const btn = document.querySelector('.btn-primary');
            if (btn) {
                console.log('Button found:', btn.textContent);
                btn.click();
                return true;
            }
            return false;
        });

        console.log('Button clicked:', clicked);

        await new Promise(resolve => setTimeout(resolve, 2000));

        // Check current step
        const currentStep = await page.evaluate(() => {
            const active = document.querySelector('.step.active');
            return {
                id: active?.id,
                hasAuthForm: !!document.querySelector('#emailAuth'),
                errorMessages: Array.from(document.querySelectorAll('.alert')).map(a => a.textContent)
            };
        });

        console.log('\nCurrent step after navigation:', currentStep);

        // Check JavaScript errors
        const jsErrors = [];
        page.on('pageerror', error => jsErrors.push(error.message));
        page.on('console', msg => {
            if (msg.type() === 'error') {
                jsErrors.push(msg.text());
            }
        });

        await page.reload();
        await new Promise(resolve => setTimeout(resolve, 2000));

        console.log('\n❌ JavaScript Errors:', jsErrors.length > 0 ? jsErrors : 'None');

        // Check CSS issues
        const cssIssues = await page.evaluate(() => {
            const step1 = document.querySelector('#step1');
            const step2 = document.querySelector('#step2');

            return {
                step1Styles: step1 ? {
                    display: window.getComputedStyle(step1).display,
                    visibility: window.getComputedStyle(step1).visibility,
                    opacity: window.getComputedStyle(step1).opacity,
                    position: window.getComputedStyle(step1).position,
                    zIndex: window.getComputedStyle(step1).zIndex
                } : null,
                step2Styles: step2 ? {
                    display: window.getComputedStyle(step2).display,
                    visibility: window.getComputedStyle(step2).visibility,
                    opacity: window.getComputedStyle(step2).opacity,
                    position: window.getComputedStyle(step2).position,
                    zIndex: window.getComputedStyle(step2).zIndex
                } : null
            };
        });

        console.log('\n🎨 CSS Analysis:');
        console.log('Step 1:', cssIssues.step1Styles);
        console.log('Step 2:', cssIssues.step2Styles);

        console.log('\n📊 DIAGNOSIS COMPLETE');
        console.log('='.repeat(50));
        console.log('Issues found - preparing fix...');

    } catch (error) {
        console.error('Debug failed:', error);
    } finally {
        // Keep browser open for manual inspection
        console.log('\n👀 Browser left open for manual inspection');
        console.log('Close browser window when done.');
    }
}

debugLiveSite();