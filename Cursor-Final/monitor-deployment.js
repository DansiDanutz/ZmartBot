#!/usr/bin/env node

const https = require('https');

async function checkDeployment() {
    return new Promise((resolve) => {
        https.get('https://vermillion-paprenjak-67497b.netlify.app', (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                // Check for our fixes
                const hasForgotPassword = data.includes('Forgot Password?');
                const hasTermsCheckbox = data.includes('termsCheckbox');
                const hasWelcomeEmail = data.includes('sendWelcomeEmail');
                const hasShowLoginForm = data.includes('showLoginForm');

                // Check version
                const versionMatch = data.match(/v4\.2\.[\d]/);
                const version = versionMatch ? versionMatch[0] : 'unknown';

                console.log(`[${new Date().toLocaleTimeString()}]`);
                console.log(`  Version: ${version}`);
                console.log(`  Forgot Password: ${hasForgotPassword ? '✅' : '❌'}`);
                console.log(`  Terms Checkbox: ${hasTermsCheckbox ? '✅' : '❌'}`);
                console.log(`  Welcome Email: ${hasWelcomeEmail ? '✅' : '❌'}`);
                console.log(`  Login Form: ${hasShowLoginForm ? '✅' : '❌'}`);

                const allFixed = hasForgotPassword && hasTermsCheckbox && hasWelcomeEmail && hasShowLoginForm;

                if (allFixed) {
                    console.log('  🎉 STATUS: ALL FIXES DEPLOYED!');
                } else {
                    console.log('  ⏳ STATUS: Waiting for deployment...');
                }
                console.log('─'.repeat(50));

                resolve(allFixed);
            });
        });
    });
}

async function monitor() {
    console.log('🔍 MONITORING DEPLOYMENT');
    console.log('═'.repeat(50));
    console.log('URL: https://vermillion-paprenjak-67497b.netlify.app');
    console.log('═'.repeat(50));

    let deployed = false;
    let attempts = 0;
    const maxAttempts = 20; // 10 minutes max

    while (!deployed && attempts < maxAttempts) {
        attempts++;
        console.log(`\nCheck #${attempts}:`);
        deployed = await checkDeployment();

        if (!deployed && attempts < maxAttempts) {
            await new Promise(r => setTimeout(r, 30000)); // Check every 30 seconds
        }
    }

    if (deployed) {
        console.log('\n✅ DEPLOYMENT SUCCESSFUL!');
        console.log('All fixes are now live. Score should be 100%!');
    } else {
        console.log('\n⚠️ Timeout after 10 minutes');
    }
}

monitor();