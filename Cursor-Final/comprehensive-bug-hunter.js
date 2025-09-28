const puppeteer = require('puppeteer');

async function runComprehensiveBugHunt() {
    console.log('🔍 Starting Comprehensive Bug Hunt...');
    const bugs = [];
    let browser;

    try {
        browser = await puppeteer.launch({
            headless: false,
            devtools: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });

        // Enable console logging
        page.on('console', msg => {
            if (msg.type() === 'error') {
                bugs.push({
                    type: 'Console Error',
                    message: msg.text(),
                    timestamp: new Date().toISOString()
                });
            }
        });

        // Catch page errors
        page.on('pageerror', error => {
            bugs.push({
                type: 'Page Error',
                message: error.message,
                timestamp: new Date().toISOString()
            });
        });

        // Navigate to onboarding
        console.log('📱 Loading onboarding page...');
        await page.goto('http://localhost:8891', { waitUntil: 'networkidle2' });

        // Test 1: Visual Overlap Check
        console.log('🎨 Checking for visual overlaps...');
        const overlaps = await page.evaluate(() => {
            const slides = document.querySelectorAll('.step');
            const issues = [];
            slides.forEach((slide, index) => {
                const rect = slide.getBoundingClientRect();
                const isVisible = window.getComputedStyle(slide).display !== 'none';
                const opacity = window.getComputedStyle(slide).opacity;
                if (isVisible && index > 0) {
                    issues.push({
                        slide: index,
                        display: window.getComputedStyle(slide).display,
                        visibility: window.getComputedStyle(slide).visibility,
                        opacity: opacity
                    });
                }
            });
            return issues;
        });
        if (overlaps.length > 0) {
            bugs.push({
                type: 'Visual Overlap',
                details: overlaps,
                fix: 'Ensure only active slide is visible'
            });
        }

        // Test 2: Navigation Flow
        console.log('🚀 Testing navigation flow...');
        for (let i = 1; i <= 9; i++) {
            const canNavigate = await page.evaluate((step) => {
                const nextBtn = document.querySelector('.btn-primary') || document.querySelector('button[onclick*="nextStep"]');
                const currentStep = parseInt(document.querySelector('.step.active')?.id?.replace('step', '') || '1');
                return currentStep === step && nextBtn && !nextBtn.disabled;
            }, i);

            if (!canNavigate && i < 9) {
                bugs.push({
                    type: 'Navigation Issue',
                    step: i,
                    message: `Cannot navigate from step ${i}`
                });
            }

            // Try to go to next step
            if (i < 9) {
                await page.evaluate(() => {
                    const nextBtn = document.querySelector('.btn-primary') || document.querySelector('button[onclick*="nextStep"]');
                    if (nextBtn && !nextBtn.disabled) nextBtn.click();
                });
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }

        // Test 3: Form Validation
        console.log('📝 Testing form validation...');
        await page.goto('http://localhost:8891', { waitUntil: 'networkidle2' });

        // Try submitting empty email
        const emailValidation = await page.evaluate(() => {
            const emailInput = document.querySelector('input[type="email"]');
            const nextBtn = document.querySelector('.btn-primary') || document.querySelector('button[onclick*="nextStep"]');
            if (emailInput && nextBtn) {
                emailInput.value = 'invalid-email';
                nextBtn.click();
                return emailInput.validationMessage || 'No validation';
            }
            return 'Email input not found';
        });
        if (emailValidation !== 'No validation') {
            console.log('✅ Email validation working');
        }

        // Test 4: Supabase Connection
        console.log('🔌 Testing Supabase connection...');
        const supabaseStatus = await page.evaluate(() => {
            return typeof window.supabase !== 'undefined' ? 'Connected' : 'Not Connected';
        });
        if (supabaseStatus !== 'Connected') {
            bugs.push({
                type: 'Supabase Issue',
                message: 'Supabase client not initialized'
            });
        }

        // Test 5: Responsive Design
        console.log('📱 Testing responsive design...');
        const viewports = [
            { width: 375, height: 667, name: 'iPhone SE' },
            { width: 768, height: 1024, name: 'iPad' },
            { width: 1920, height: 1080, name: 'Desktop' }
        ];

        for (const viewport of viewports) {
            await page.setViewport(viewport);
            await new Promise(resolve => setTimeout(resolve, 500));
            const layoutIssue = await page.evaluate(() => {
                const container = document.querySelector('.onboarding-container');
                const rect = container?.getBoundingClientRect();
                return rect && (rect.width > window.innerWidth || rect.height > window.innerHeight);
            });
            if (layoutIssue) {
                bugs.push({
                    type: 'Responsive Issue',
                    viewport: viewport.name,
                    message: 'Content overflows viewport'
                });
            }
        }

        // Test 6: Accessibility
        console.log('♿ Checking accessibility...');
        const a11yIssues = await page.evaluate(() => {
            const issues = [];

            // Check for missing alt text
            document.querySelectorAll('img').forEach(img => {
                if (!img.alt) {
                    issues.push(`Missing alt text: ${img.src}`);
                }
            });

            // Check for missing labels
            document.querySelectorAll('input').forEach(input => {
                if (!input.getAttribute('aria-label') && !input.id) {
                    issues.push(`Input missing label: ${input.type}`);
                }
            });

            // Check color contrast
            const buttons = document.querySelectorAll('button');
            buttons.forEach(btn => {
                const style = window.getComputedStyle(btn);
                const bg = style.backgroundColor;
                const color = style.color;
                // Basic check - would need proper contrast calculation
                if (bg === color) {
                    issues.push('Potential contrast issue on button');
                }
            });

            return issues;
        });
        if (a11yIssues.length > 0) {
            bugs.push({
                type: 'Accessibility',
                issues: a11yIssues
            });
        }

        // Test 7: Memory Leaks
        console.log('💾 Checking for memory leaks...');
        const metrics1 = await page.metrics();

        // Navigate through all steps multiple times
        for (let cycle = 0; cycle < 3; cycle++) {
            await page.goto('http://localhost:8891', { waitUntil: 'networkidle2' });
            for (let i = 1; i <= 9; i++) {
                await page.evaluate(() => {
                    const nextBtn = document.querySelector('.next-btn');
                    if (nextBtn && !nextBtn.disabled) nextBtn.click();
                });
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }

        const metrics2 = await page.metrics();
        const memoryIncrease = metrics2.JSHeapUsedSize - metrics1.JSHeapUsedSize;
        if (memoryIncrease > 10000000) { // 10MB threshold
            bugs.push({
                type: 'Performance',
                message: `Potential memory leak: ${(memoryIncrease / 1000000).toFixed(2)}MB increase`
            });
        }

        // Generate report
        console.log('\n📊 BUG HUNT COMPLETE');
        console.log('===================');

        if (bugs.length === 0) {
            console.log('✅ No bugs found! System is clean.');
        } else {
            console.log(`🐛 Found ${bugs.length} issue(s):\n`);
            bugs.forEach((bug, index) => {
                console.log(`${index + 1}. ${bug.type}: ${bug.message || JSON.stringify(bug.details)}`);
                if (bug.fix) {
                    console.log(`   Fix: ${bug.fix}`);
                }
            });
        }

        return bugs;

    } catch (error) {
        console.error('❌ Bug hunt failed:', error);
        bugs.push({
            type: 'Test Failure',
            message: error.message
        });
    } finally {
        if (browser) {
            await browser.close();
        }
    }

    return bugs;
}

// Run the bug hunt
runComprehensiveBugHunt().then(bugs => {
    if (bugs.length > 0) {
        console.log('\n🔧 Ready to fix detected issues');
        process.exit(1); // Exit with error if bugs found
    } else {
        console.log('\n✨ System ready for deployment');
        process.exit(0); // Success
    }
});