#!/usr/bin/env node

const https = require('https');

async function checkVersion() {
    return new Promise((resolve) => {
        https.get('https://vermillion-paprenjak-67497b.netlify.app', (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                const hasV42 = data.includes('v4.2') || data.includes('4.2.0');
                const hasForgot = data.includes('Forgot Password?');
                const hasTerms = data.includes('termsCheckbox');
                console.log(`[${new Date().toLocaleTimeString()}] v4.2: ${hasV42 ? '✅' : '❌'} | Forgot: ${hasForgot ? '✅' : '❌'} | Terms: ${hasTerms ? '✅' : '❌'}`);
                resolve(hasV42);
            });
        });
    });
}

async function waitForVersion() {
    console.log('⏳ Waiting for v4.2.0 deployment...\n');
    let deployed = false;
    let attempts = 0;

    while (!deployed && attempts < 20) {
        attempts++;
        deployed = await checkVersion();
        if (!deployed) {
            await new Promise(r => setTimeout(r, 10000)); // Check every 10 seconds
        }
    }

    if (deployed) {
        console.log('\n✅ VERSION 4.2.0 IS NOW LIVE!');
    } else {
        console.log('\n⚠️  Deployment timeout');
    }
}

waitForVersion();