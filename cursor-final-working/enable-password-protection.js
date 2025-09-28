#!/usr/bin/env node

/**
 * Enable Leaked Password Protection via Supabase Management API
 *
 * This script enables HaveIBeenPwned password checking for your Supabase project.
 *
 * Required: Supabase Management API key (from dashboard.supabase.com/account/tokens)
 */

const https = require('https');

// Configuration
const PROJECT_REF = 'xhskmqsgtdhehzlvtuns'; // Your project reference
const SUPABASE_ACCESS_TOKEN = process.env.SUPABASE_ACCESS_TOKEN; // Set this environment variable

if (!SUPABASE_ACCESS_TOKEN) {
    console.error('❌ Error: SUPABASE_ACCESS_TOKEN environment variable not set');
    console.log('\nTo get your access token:');
    console.log('1. Go to https://app.supabase.com/account/tokens');
    console.log('2. Create a new access token');
    console.log('3. Run: export SUPABASE_ACCESS_TOKEN="your-token-here"');
    console.log('4. Run this script again');
    process.exit(1);
}

// Function to update auth config
function updateAuthConfig() {
    const data = JSON.stringify({
        hibp_enabled: true,
        password_min_length: 8,
        password_required_symbols: ['lower_case', 'upper_case', 'numbers']
    });

    const options = {
        hostname: 'api.supabase.com',
        port: 443,
        path: `/v1/projects/${PROJECT_REF}/config/auth`,
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${SUPABASE_ACCESS_TOKEN}`,
            'Content-Length': data.length
        }
    };

    console.log('🔐 Enabling leaked password protection for project:', PROJECT_REF);

    const req = https.request(options, (res) => {
        let responseData = '';

        res.on('data', (chunk) => {
            responseData += chunk;
        });

        res.on('end', () => {
            if (res.statusCode === 200 || res.statusCode === 204) {
                console.log('✅ Successfully enabled leaked password protection!');
                console.log('\n📊 New settings:');
                console.log('  - HaveIBeenPwned checking: ENABLED');
                console.log('  - Minimum password length: 8 characters');
                console.log('  - Required: lowercase, uppercase, numbers');
                console.log('\n🧪 Test it by trying to register with password: "Password123"');
                console.log('   (Should be rejected as compromised)');
            } else {
                console.error('❌ Error:', res.statusCode, responseData);
                if (res.statusCode === 401) {
                    console.log('\n⚠️  Your access token may be invalid or expired.');
                    console.log('   Get a new one from: https://app.supabase.com/account/tokens');
                }
            }
        });
    });

    req.on('error', (error) => {
        console.error('❌ Request failed:', error.message);
    });

    req.write(data);
    req.end();
}

// Alternative: Use Supabase CLI if available
function checkSupabaseCLI() {
    const { exec } = require('child_process');

    exec('supabase --version', (error, stdout, stderr) => {
        if (!error) {
            console.log('\n📦 Supabase CLI detected:', stdout.trim());
            console.log('You can also enable this via CLI:');
            console.log('supabase auth config update --project-ref', PROJECT_REF);
            console.log('  --hibp-enabled true');
            console.log('  --password-min-length 8');
        }
    });
}

// Run the update
updateAuthConfig();
checkSupabaseCLI();

console.log('\n📝 Manual Alternative:');
console.log('1. Go to: https://app.supabase.com/project/' + PROJECT_REF);
console.log('2. Navigate to: Authentication → Providers → Email');
console.log('3. Enable: "Leaked password protection"');
console.log('4. Click: Save');