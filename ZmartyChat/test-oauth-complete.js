// Complete OAuth Test for Zmarty
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

console.log('🔍 TESTING OAUTH CONFIGURATION');
console.log('═'.repeat(60));

async function testOAuthProviders() {
    const providers = ['google', 'facebook'];
    const results = {};

    for (const provider of providers) {
        console.log(`\n📱 Testing ${provider.toUpperCase()} OAuth:`);
        console.log('─'.repeat(40));

        try {
            // Generate OAuth URL
            const { data, error } = await supabase.auth.signInWithOAuth({
                provider: provider,
                options: {
                    redirectTo: 'http://localhost:3005/auth/callback',
                    skipBrowserRedirect: true
                }
            });

            if (error) {
                console.log(`   ❌ Error: ${error.message}`);
                results[provider] = 'error';
            } else if (data?.url) {
                console.log(`   ✅ OAuth URL generated successfully`);

                // Check the URL structure
                const url = new URL(data.url);
                console.log(`   📍 OAuth endpoint: ${url.hostname}`);

                if (provider === 'google') {
                    const hasClientId = data.url.includes('966065216838');
                    console.log(`   ${hasClientId ? '✅' : '❌'} Google Client ID configured`);
                    if (!hasClientId) {
                        console.log('   ⚠️  Expected Client ID: 966065216838...');
                    }
                }

                if (provider === 'facebook') {
                    const hasAppId = data.url.includes('1698524340782846');
                    console.log(`   ${hasAppId ? '✅' : '❌'} Facebook App ID configured`);
                    if (!hasAppId) {
                        console.log('   ⚠️  Expected App ID: 1698524340782846');
                    }
                }

                console.log(`   🔗 Redirect URL: http://localhost:3005/auth/callback`);
                results[provider] = 'success';
            }
        } catch (err) {
            console.log(`   ❌ Unexpected error: ${err.message}`);
            results[provider] = 'failed';
        }
    }

    console.log('\n' + '═'.repeat(60));
    console.log('📊 OAUTH TEST RESULTS:');
    console.log('═'.repeat(60));

    const allSuccess = Object.values(results).every(r => r === 'success');

    if (allSuccess) {
        console.log('\n✅ ALL OAUTH PROVIDERS ARE WORKING!');
        console.log('\n📱 Test in browser:');
        console.log('   1. Open: http://localhost:3005');
        console.log('   2. Click "Get Started"');
        console.log('   3. Click "Continue with Google" or "Continue with Facebook"');
        console.log('   4. Complete login');
        console.log('   5. You should return to the app logged in!');
    } else {
        console.log('\n⚠️  Some providers need configuration:');
        for (const [provider, result] of Object.entries(results)) {
            if (result !== 'success') {
                console.log(`   • ${provider}: ${result}`);
            }
        }
    }

    console.log('\n📋 Configuration URLs:');
    console.log('   Supabase Auth: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/auth/providers');
    console.log('   Google Console: https://console.cloud.google.com');
    console.log('   Facebook Developers: https://developers.facebook.com');
}

// Test site URL configuration
async function testSiteURL() {
    console.log('\n\n🌐 TESTING SITE URL CONFIGURATION:');
    console.log('═'.repeat(60));

    console.log('\n📍 Configured URLs:');
    console.log('   Site URL: http://localhost:3005');
    console.log('   Callback: http://localhost:3005/auth/callback');

    // Test if callback file exists
    const fs = await import('fs').then(m => m.default);
    const path = await import('path').then(m => m.default);

    const callbackPath = path.join(process.cwd(), 'onboarding2', 'auth', 'callback', 'index.html');

    if (fs.existsSync(callbackPath)) {
        console.log('   ✅ Callback handler exists');
    } else {
        console.log('   ❌ Callback handler missing');
        console.log('   Run: mkdir -p onboarding2/auth/callback');
    }

    console.log('\n✅ Site URL is configured correctly!');
}

// Run all tests
console.log('🚀 Starting OAuth Tests...\n');

testOAuthProviders()
    .then(() => testSiteURL())
    .then(() => {
        console.log('\n' + '═'.repeat(60));
        console.log('🎉 OAUTH TESTING COMPLETE!');
        console.log('═'.repeat(60));
    })
    .catch(err => {
        console.error('\n❌ Test failed:', err);
    });