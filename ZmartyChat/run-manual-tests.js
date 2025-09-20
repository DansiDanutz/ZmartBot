import puppeteer from 'puppeteer';
import fs from 'fs';

const runManualTestChecklist = async () => {
    console.log('🎯 Running Comprehensive Manual Test Checklist...\n');

    const browser = await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();

    // Capture console messages
    const consoleLogs = [];
    page.on('console', msg => {
        consoleLogs.push(`${msg.type()}: ${msg.text()}`);
    });

    try {
        // Navigate to app
        await page.goto('http://localhost:9000', {
            waitUntil: 'networkidle0',
            timeout: 30000
        });

        // Load and execute the manual test script
        const testScript = fs.readFileSync('./manual-test-checklist.js', 'utf8');

        // Execute the test script
        const results = await page.evaluate(async (script) => {
            // Inject the script
            eval(script);

            // Run the tests
            if (window.runManualTests) {
                return await window.runManualTests();
            } else {
                return { error: 'Test function not loaded' };
            }
        }, testScript);

        // Display results
        console.log('\n' + '='.repeat(60));
        console.log('📊 MANUAL TEST RESULTS');
        console.log('='.repeat(60));

        if (results.error) {
            console.error('❌ Error:', results.error);
        } else {
            console.log(`✅ Passed Tests: ${results.passed.length}`);
            console.log(`❌ Failed Tests: ${results.failed.length}`);
            console.log(`⚠️ Warnings: ${results.warnings.length}`);

            const totalTests = results.passed.length + results.failed.length;
            const successRate = (results.passed.length / totalTests * 100).toFixed(1);
            console.log(`\n📈 Success Rate: ${successRate}%`);

            if (results.failed.length > 0) {
                console.log('\n❌ Failed Tests:');
                results.failed.forEach(test => console.log(`  ${test}`));
            }

            if (results.warnings.length > 0) {
                console.log('\n⚠️ Warnings:');
                results.warnings.forEach(warning => console.log(`  ${warning}`));
            }

            if (successRate === '100.0') {
                console.log('\n🎉 PERFECT! All manual tests passed!');
            }
        }

        // Check for JavaScript errors
        const errors = consoleLogs.filter(log => log.startsWith('error:'));
        if (errors.length > 0) {
            console.log('\n⚠️ Console Errors Detected:');
            errors.forEach(err => console.log(`  ${err}`));
        }

        // Save detailed report
        const report = {
            timestamp: new Date().toISOString(),
            results: results,
            consoleLogs: consoleLogs,
            successRate: results.passed ? (results.passed.length / (results.passed.length + results.failed.length) * 100).toFixed(1) : 0
        };

        fs.writeFileSync('manual-test-report.json', JSON.stringify(report, null, 2));
        console.log('\n📄 Detailed report saved to manual-test-report.json');

    } catch (error) {
        console.error('❌ Test execution failed:', error.message);
    } finally {
        await browser.close();
    }
};

// Run the tests
runManualTestChecklist().catch(console.error);