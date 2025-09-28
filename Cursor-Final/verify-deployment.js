const puppeteer = require('puppeteer');

async function verifyDeployment() {
    console.log('🔍 Verifying Fixed Deployment...\n');

    const browser = await puppeteer.launch({
        headless: false,
        devtools: false,
        args: ['--window-size=1920,1080']
    });

    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1920, height: 1080 });

        console.log('📱 Loading https://vermillion-paprenjak-67497b.netlify.app...');
        await page.goto('https://vermillion-paprenjak-67497b.netlify.app', {
            waitUntil: 'networkidle2'
        });

        // Check Step 1 visibility
        console.log('\n✅ Checking Step 1...');
        const step1Check = await page.evaluate(() => {
            const steps = document.querySelectorAll('.step');
            let visibleCount = 0;
            let step1Visible = false;

            steps.forEach(step => {
                const styles = window.getComputedStyle(step);
                if (styles.display !== 'none' &&
                    styles.visibility === 'visible' &&
                    styles.opacity === '1') {
                    visibleCount++;
                    if (step.id === 'step1') step1Visible = true;
                }
            });

            return {
                totalSteps: steps.length,
                visibleSteps: visibleCount,
                step1Active: step1Visible,
                welcomeText: document.querySelector('h1')?.textContent
            };
        });

        console.log(`   Total steps: ${step1Check.totalSteps}`);
        console.log(`   Visible steps: ${step1Check.visibleSteps}`);
        console.log(`   Step 1 active: ${step1Check.step1Active}`);
        console.log(`   Welcome text: ${step1Check.welcomeText}`);

        // Test navigation to Step 2
        console.log('\n🚀 Testing navigation to Step 2...');
        await page.click('.btn-primary');
        await new Promise(resolve => setTimeout(resolve, 1500));

        const step2Check = await page.evaluate(() => {
            const activeStep = document.querySelector('.step.active');
            const visibleSteps = Array.from(document.querySelectorAll('.step')).filter(step => {
                const styles = window.getComputedStyle(step);
                return styles.display !== 'none' &&
                       styles.visibility === 'visible' &&
                       styles.opacity === '1';
            });

            return {
                currentStepId: activeStep?.id,
                visibleCount: visibleSteps.length,
                hasEmailForm: !!document.querySelector('#regEmail'),
                canNavigate: true
            };
        });

        console.log(`   Current step: ${step2Check.currentStepId}`);
        console.log(`   Visible steps: ${step2Check.visibleCount}`);
        console.log(`   Has email form: ${step2Check.hasEmailForm}`);

        // Test navigation to Step 3
        console.log('\n🚀 Testing navigation to Step 3...');
        await page.click('.nav-arrow#nextArrow');
        await new Promise(resolve => setTimeout(resolve, 1000));

        const step3Check = await page.evaluate(() => {
            const activeStep = document.querySelector('.step.active');
            return activeStep?.id;
        });
        console.log(`   Current step: ${step3Check}`);

        // Final verdict
        console.log('\n' + '='.repeat(50));
        console.log('📊 VERIFICATION RESULTS');
        console.log('='.repeat(50));

        const issues = [];
        if (step1Check.visibleSteps > 1) {
            issues.push('❌ Multiple steps visible on load');
        }
        if (!step2Check.currentStepId?.includes('step2')) {
            issues.push('❌ Navigation to Step 2 failed');
        }
        if (!step3Check?.includes('step3')) {
            issues.push('❌ Navigation to Step 3 failed');
        }

        if (issues.length === 0) {
            console.log('\n✅ DEPLOYMENT VERIFIED - ALL ISSUES FIXED!');
            console.log('   • No duplicate text');
            console.log('   • Navigation working');
            console.log('   • Only active step visible');
        } else {
            console.log('\n⚠️  ISSUES FOUND:');
            issues.forEach(issue => console.log(`   ${issue}`));
        }

        await new Promise(resolve => setTimeout(resolve, 3000));

    } catch (error) {
        console.error('❌ Verification failed:', error);
    } finally {
        await browser.close();
        console.log('\n🏁 Verification complete');
    }
}

verifyDeployment();