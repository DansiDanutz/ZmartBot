#!/usr/bin/env node

/**
 * Enable HIBP via Supabase Management API
 * Requires service role key
 */

const https = require('https');

const PROJECT_REF = 'xhskmqsgtdhehzlvtuns';

console.log('🔐 Enabling HIBP Protection via Management API');
console.log('==============================================\n');

// You need to get this from your dashboard
console.log('Get your Service Role Key from:');
console.log(`https://supabase.com/dashboard/project/${PROJECT_REF}/settings/api\n`);

const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.question('Enter your Service Role Key: ', (serviceKey) => {

    const data = JSON.stringify({
        password_min_length: 12,
        enable_signup: true,
        enable_password_recovery: true,
        password_required_characters: 'abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789',
        hibp_enabled: true,
        leaked_password_protection: true
    });

    const options = {
        hostname: 'api.supabase.com',
        port: 443,
        path: `/v1/projects/${PROJECT_REF}/config/auth`,
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${serviceKey}`,
            'Content-Type': 'application/json',
            'Content-Length': data.length
        }
    };

    const req = https.request(options, (res) => {
        let responseData = '';

        res.on('data', (chunk) => {
            responseData += chunk;
        });

        res.on('end', () => {
            console.log('\nResponse Status:', res.statusCode);

            if (res.statusCode === 200 || res.statusCode === 204) {
                console.log('✅ SUCCESS! HIBP protection should now be enabled!');
                console.log('Check your dashboard warnings to verify.');
            } else {
                console.log('❌ Failed to enable HIBP protection');
                console.log('Response:', responseData);
                console.log('\nYou may need to contact Supabase support.');
            }
        });
    });

    req.on('error', (e) => {
        console.error('Error:', e);
    });

    req.write(data);
    req.end();

    rl.close();
});