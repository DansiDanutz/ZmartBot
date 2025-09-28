#!/usr/bin/env node

/**
 * Check if Netlify deployment is complete
 */

const https = require('https');

function checkDeployment() {
    return new Promise((resolve) => {
        https.get('https://vermillion-paprenjak-67497b.netlify.app', (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            res.on('end', () => {
                const hasV41 = data.includes('v4.1');
                const hasForgotPassword = data.includes('Forgot Password?');
                const hasTermsCheckbox = data.includes('termsCheckbox');
                const hasWelcomeEmail = data.includes('sendWelcomeEmail');
                const hasLoginForm = data.includes('showLoginForm');

                console.log('═'.repeat(50));
                console.log('📡 DEPLOYMENT STATUS CHECK');
                console.log('═'.repeat(50));
                console.log(`✅ Site is accessible`);
                console.log(`${hasV41 ? '✅' : '⏳'} Version 4.1 title`);
                console.log(`${hasForgotPassword ? '✅' : '⏳'} Forgot Password link`);
                console.log(`${hasTermsCheckbox ? '✅' : '⏳'} Terms checkbox`);
                console.log(`${hasWelcomeEmail ? '✅' : '⏳'} Welcome email function`);
                console.log(`${hasLoginForm ? '✅' : '⏳'} Login form function`);
                console.log('─'.repeat(50));

                if (hasV41 || (hasForgotPassword && hasTermsCheckbox && hasWelcomeEmail)) {
                    console.log('🎉 NEW VERSION DEPLOYED!');
                    resolve(true);
                } else {
                    console.log('⏳ Still waiting for deployment...');
                    console.log('   Old version is still being served.');
                    console.log('   Netlify usually takes 1-3 minutes.');
                    resolve(false);
                }
                console.log('═'.repeat(50));
            });
        }).on('error', (err) => {
            console.error('Error checking deployment:', err);
            resolve(false);
        });
    });
}

async function waitForDeployment() {
    let deployed = false;
    let attempts = 0;
    const maxAttempts = 10; // Check for 5 minutes max

    while (!deployed && attempts < maxAttempts) {
        attempts++;
        console.log(`\n🔄 Check #${attempts} at ${new Date().toLocaleTimeString()}`);

        deployed = await checkDeployment();

        if (!deployed && attempts < maxAttempts) {
            console.log(`\n⏰ Waiting 30 seconds before next check...`);
            await new Promise(resolve => setTimeout(resolve, 30000));
        }
    }

    if (deployed) {
        console.log('\n✅ DEPLOYMENT COMPLETE! Ready for testing.');
    } else {
        console.log('\n⚠️  Timeout: Deployment taking longer than expected.');
        console.log('Check https://app.netlify.com for build status.');
    }
}

// Run the checker
waitForDeployment();