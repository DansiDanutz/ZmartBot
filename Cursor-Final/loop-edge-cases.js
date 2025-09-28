const puppeteer = require('puppeteer');

async function testEdgeCases() {
    console.log('🎯 EDGE CASE BUG HUNTER\n');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 450, height: 750 }
    });

    const page = await browser.newPage();
    let bugs = [];

    try {
        await page.goto('http://localhost:8891');

        // Test 1: Password mismatch
        console.log('🔍 Test 1: Password Mismatch');
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        await page.type('#regEmail', 'test@example.com');
        await page.type('#regPassword', 'Password123!');
        await page.type('#regConfirmPassword', 'DifferentPassword123!');
        await page.click('#regEmailBtn');
        await new Promise(r => setTimeout(r, 1000));

        const passwordError = await page.$eval('#authAlert', el => {
            const visible = window.getComputedStyle(el).display !== 'none';
            return visible && el.textContent.toLowerCase().includes('password');
        }).catch(() => false);

        if (!passwordError) {
            bugs.push('No error shown for password mismatch');
            console.log('  ❌ Password mismatch not validated');
        } else {
            console.log('  ✅ Password mismatch caught');
        }

        // Test 2: Weak password
        console.log('\n🔍 Test 2: Weak Password');
        await page.reload();
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        // Clear fields first
        await page.evaluate(() => {
            document.querySelector('#regEmail').value = '';
            document.querySelector('#regPassword').value = '';
            document.querySelector('#regConfirmPassword').value = '';
        });

        await page.type('#regEmail', 'test@example.com');
        await page.type('#regPassword', '123');
        await page.type('#regConfirmPassword', '123');
        await page.click('#regEmailBtn');
        await new Promise(r => setTimeout(r, 1000));

        const weakPasswordError = await page.$eval('#authAlert', el => {
            const visible = window.getComputedStyle(el).display !== 'none';
            return visible;
        }).catch(() => false);

        if (!weakPasswordError) {
            bugs.push('Weak password (123) accepted');
            console.log('  ❌ Weak password not blocked');
        } else {
            console.log('  ✅ Weak password blocked');
        }

        // Test 3: Special characters in email
        console.log('\n🔍 Test 3: Special Email Characters');
        await page.reload();
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        await page.type('#regEmail', 'test+tag@example.com');
        await page.type('#regPassword', 'ValidPassword123!');
        await page.type('#regConfirmPassword', 'ValidPassword123!');
        await page.click('#regEmailBtn');
        await new Promise(r => setTimeout(r, 2000));

        const specialEmailAccepted = await page.$eval('#authAlert', el => {
            const visible = window.getComputedStyle(el).display !== 'none';
            const text = el.textContent;
            return visible && (text.includes('created') || text.includes('verify'));
        }).catch(() => false);

        if (!specialEmailAccepted) {
            bugs.push('Email with + character not accepted');
            console.log('  ❌ Special email characters blocked');
        } else {
            console.log('  ✅ Special email characters work');
        }

        // Test 4: Rapid clicking
        console.log('\n🔍 Test 4: Rapid Navigation Clicks');
        await page.reload();
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 500));

        // Click next arrow rapidly
        for (let i = 0; i < 5; i++) {
            const nextArrow = await page.$('#nextArrow');
            if (nextArrow) {
                await nextArrow.click();
            }
        }
        await new Promise(r => setTimeout(r, 1000));

        const stillOnStep2 = await page.$eval('#step2', el =>
            el.classList.contains('active')
        ).catch(() => false);

        if (!stillOnStep2) {
            bugs.push('Rapid clicking breaks navigation');
            console.log('  ❌ Rapid clicks cause issues');
        } else {
            console.log('  ✅ Rapid clicks handled correctly');
        }

        // Test 5: Browser back button
        console.log('\n🔍 Test 5: Browser Back Button');
        await page.goBack();
        await new Promise(r => setTimeout(r, 1000));

        const afterBackButton = await page.url();
        if (!afterBackButton.includes('localhost:8891')) {
            bugs.push('Browser back button leaves the app');
            console.log('  ❌ Back button navigation issue');
        } else {
            console.log('  ✅ Back button handled');
        }

        // Test 6: Long email address
        console.log('\n🔍 Test 6: Very Long Email');
        await page.goto('http://localhost:8891');
        await page.click('#step1 .btn-primary');
        await new Promise(r => setTimeout(r, 1000));

        const longEmail = 'verylongemailaddress'.repeat(10) + '@example.com';
        await page.type('#regEmail', longEmail);

        const emailOverflow = await page.evaluate(() => {
            const input = document.querySelector('#regEmail');
            return input.scrollWidth > input.clientWidth;
        });

        if (emailOverflow) {
            bugs.push('Long email causes UI overflow');
            console.log('  ❌ Email field overflow');
        } else {
            console.log('  ✅ Long email handled');
        }

        // Test 7: Network interruption simulation
        console.log('\n🔍 Test 7: Offline Mode');
        await page.setOfflineMode(true);

        await page.type('#regPassword', 'Test123!@#');
        await page.type('#regConfirmPassword', 'Test123!@#');
        await page.click('#regEmailBtn');
        await new Promise(r => setTimeout(r, 2000));

        const offlineError = await page.$eval('#authAlert', el => {
            const visible = window.getComputedStyle(el).display !== 'none';
            return visible;
        }).catch(() => false);

        if (!offlineError) {
            bugs.push('No error shown when offline');
            console.log('  ❌ Offline error not shown');
        } else {
            console.log('  ✅ Offline handled');
        }

        await page.setOfflineMode(false);

    } catch (error) {
        bugs.push(`Test error: ${error.message}`);
    } finally {
        setTimeout(() => browser.close(), 3000);
    }

    // Report
    console.log('\n' + '='.repeat(50));
    console.log('🔍 EDGE CASE TESTING COMPLETE\n');

    if (bugs.length === 0) {
        console.log('🎉 NO BUGS FOUND! System handles edge cases well.');
    } else {
        console.log(`⚠️ Found ${bugs.length} issue(s):\n`);
        bugs.forEach((bug, i) => {
            console.log(`${i+1}. ${bug}`);
        });
        console.log('\n🔧 Working on first bug...');
    }

    return bugs;
}

testEdgeCases().catch(console.error);