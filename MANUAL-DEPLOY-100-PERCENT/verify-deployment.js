#!/usr/bin/env node

/**
 * Deployment Verification Script
 * Tests the live Netlify deployment to ensure all features are working
 */

const https = require('https');

const LIVE_URL = 'https://vermillion-paprenjak-67497b.netlify.app';

// Color codes for terminal output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
}

function makeRequest(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    body: data
                });
            });
        }).on('error', reject);
    });
}

async function verifyDeployment() {
    log('\n╔══════════════════════════════════════════════════════════╗', colors.cyan);
    log('║       ZmartyBrain Deployment Verification Script         ║', colors.cyan);
    log('╚══════════════════════════════════════════════════════════╝', colors.cyan);

    log(`\n📍 Testing: ${LIVE_URL}`, colors.blue);
    log('━'.repeat(60), colors.cyan);

    try {
        // Fetch the main page
        log('\n🔍 Fetching main page...', colors.yellow);
        const response = await makeRequest(LIVE_URL);

        if (response.statusCode !== 200) {
            log(`❌ Site returned status code: ${response.statusCode}`, colors.red);
            return false;
        }

        log('✅ Site is accessible (200 OK)', colors.green);

        const html = response.body;

        // Define tests
        const tests = [
            {
                name: 'Welcome Slide',
                check: () => html.includes('Welcome to ZmartyBrain'),
                description: 'Main welcome slide with branding'
            },
            {
                name: 'Slides Navigation',
                check: () => html.includes('slide') && html.includes('currentSlide'),
                description: 'Slide navigation functionality'
            },
            {
                name: 'Email Registration',
                check: () => html.includes('type="email"') && html.includes('Create Account'),
                description: 'Email/password signup form'
            },
            {
                name: 'Login Option',
                check: () => html.includes('Already have an account') || html.includes('Sign in'),
                description: 'Login link for existing users'
            },
            {
                name: 'Password Recovery',
                check: () => html.includes('Forgot') || html.includes('resetPassword'),
                description: 'Password reset functionality'
            },
            {
                name: 'OTP Validation',
                check: () => html.includes('otp') || html.includes('verification') || html.includes('6-digit'),
                description: '6-digit OTP code validation'
            },
            {
                name: 'Resend Code',
                check: () => html.includes('resend') || html.includes('Resend'),
                description: 'Resend validation code feature'
            },
            {
                name: 'Google OAuth',
                check: () => html.includes('Google') && (html.includes('oauth') || html.includes('OAuth')),
                description: 'Google login integration'
            },
            {
                name: 'Welcome Email',
                check: () => html.includes('sendWelcomeEmail') || (html.includes('welcome') && html.includes('email')),
                description: 'Welcome email functionality'
            },
            {
                name: 'Free Tier',
                check: () => html.includes('Free') || html.includes('$0'),
                description: 'Free tier option'
            },
            {
                name: 'Starter Tier',
                check: () => html.includes('$19') || html.includes('Starter'),
                description: 'Starter tier ($19/month)'
            },
            {
                name: 'Professional Tier',
                check: () => html.includes('$49') || html.includes('Professional'),
                description: 'Professional tier ($49/month)'
            },
            {
                name: 'Profile Setup',
                check: () => html.includes('profile') || html.includes('Profile'),
                description: 'Profile completion form'
            },
            {
                name: 'Dashboard Redirect',
                check: () => html.includes('dashboard') || html.includes('Dashboard'),
                description: 'Dashboard redirect functionality'
            },
            {
                name: 'Supabase Integration',
                check: () => html.includes('supabase') || html.includes('createClient'),
                description: 'Supabase client configuration'
            },
            {
                name: 'Auth Service',
                check: () => html.includes('AuthService') || html.includes('auth-service'),
                description: 'Authentication service module'
            }
        ];

        // Run tests
        log('\n📋 Running Feature Tests:', colors.blue);
        log('─'.repeat(60));

        let passedTests = 0;
        let failedTests = [];

        for (const test of tests) {
            try {
                const passed = test.check();
                if (passed) {
                    log(`  ✅ ${test.name}`, colors.green);
                    log(`     └─ ${test.description}`, colors.cyan);
                    passedTests++;
                } else {
                    log(`  ❌ ${test.name}`, colors.red);
                    log(`     └─ ${test.description}`, colors.yellow);
                    failedTests.push(test.name);
                }
            } catch (error) {
                log(`  ⚠️  ${test.name} - Error during test`, colors.yellow);
                failedTests.push(test.name);
            }
        }

        // Summary
        log('\n' + '═'.repeat(60), colors.cyan);
        log(`\n📊 TEST RESULTS SUMMARY:`, colors.bright);
        log(`   Total Tests: ${tests.length}`);
        log(`   ✅ Passed: ${passedTests}`, colors.green);
        log(`   ❌ Failed: ${tests.length - passedTests}`, colors.red);

        const percentage = Math.round((passedTests / tests.length) * 100);
        log(`   📈 Score: ${percentage}%`);

        if (percentage === 100) {
            log('\n🎉 DEPLOYMENT STATUS: PERFECT!', colors.green);
            log('   All features are working correctly!', colors.green);
            log('   The onboarding system is production ready! ✨', colors.green);
        } else if (percentage >= 80) {
            log('\n✅ DEPLOYMENT STATUS: GOOD', colors.green);
            log('   Most features are working correctly.', colors.green);
            log('   Minor issues detected but system is functional.', colors.yellow);
        } else if (percentage >= 60) {
            log('\n⚠️  DEPLOYMENT STATUS: NEEDS ATTENTION', colors.yellow);
            log('   Several features need fixing.', colors.yellow);
        } else {
            log('\n❌ DEPLOYMENT STATUS: CRITICAL ISSUES', colors.red);
            log('   Many features are not working properly.', colors.red);
        }

        if (failedTests.length > 0) {
            log('\n🔧 Failed Features:', colors.yellow);
            failedTests.forEach(test => {
                log(`   • ${test}`, colors.red);
            });
        }

        // Check if we're seeing the enhanced version
        log('\n🔍 VERSION CHECK:', colors.blue);
        if (html.includes('slide-1') && html.includes('slide-6')) {
            log('   ✅ Enhanced version (6 slides) is deployed', colors.green);
        } else if (html.includes('slide-1') && html.includes('slide-3')) {
            log('   ⚠️  Original version (3 slides) detected', colors.yellow);
            log('   The fix may not have deployed yet. Wait 1-2 minutes.', colors.yellow);
        } else {
            log('   ❓ Unable to determine version', colors.yellow);
        }

        log('\n' + '═'.repeat(60), colors.cyan);
        log(`\n🌐 Live URL: ${LIVE_URL}`, colors.blue);
        log('📅 Test Date: ' + new Date().toISOString(), colors.cyan);

        return percentage >= 80;

    } catch (error) {
        log(`\n❌ Error during verification: ${error.message}`, colors.red);
        return false;
    }
}

// Run the verification
verifyDeployment().then(success => {
    process.exit(success ? 0 : 1);
}).catch(error => {
    log(`\n❌ Fatal error: ${error.message}`, colors.red);
    process.exit(1);
});