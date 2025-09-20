// Test Script for Supabase Email Flows
// This script tests: Registration OTP, Password Reset, and Password Update

import { createClient } from '@supabase/supabase-js';
import readline from 'readline';

const SUPABASE_URL = 'https://asjtxrmftmutcsnqgidy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Test configuration
const TEST_EMAIL = 'test@zmartbot.com'; // Replace with your test email
const TEST_PASSWORD = 'TestPass123!';
const NEW_PASSWORD = 'NewTestPass456!';

// Color codes for console output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

// Test 1: Registration with OTP
async function testRegistrationOTP() {
    log('\n========================================', 'blue');
    log('TEST 1: Registration with OTP', 'blue');
    log('========================================', 'blue');

    try {
        // Send OTP for registration
        log('Sending OTP to ' + TEST_EMAIL + '...', 'yellow');
        const { data, error } = await supabase.auth.signInWithOtp({
            email: TEST_EMAIL,
            options: {
                shouldCreateUser: true,
                data: {
                    tier: 'free',
                    name: 'Test User',
                    country: 'US',
                    profile_completed: false
                }
            }
        });

        if (error) throw error;

        log('✅ OTP sent successfully!', 'green');
        log('Check your email for a 6-digit code', 'green');
        log('Email should contain: Verification code, not a magic link', 'yellow');

        // Wait for user to enter code
        const code = await getUserInput('Enter the 6-digit code from your email: ');

        // Verify OTP
        log('Verifying OTP...', 'yellow');
        const { data: verifyData, error: verifyError } = await supabase.auth.verifyOtp({
            email: TEST_EMAIL,
            token: code,
            type: 'email'
        });

        if (verifyError) throw verifyError;

        log('✅ Email verified successfully!', 'green');
        log('User created with ID: ' + verifyData.user.id, 'green');

        // Set password after OTP verification
        log('Setting password...', 'yellow');
        const { error: passwordError } = await supabase.auth.updateUser({
            password: TEST_PASSWORD
        });

        if (passwordError) throw passwordError;
        log('✅ Password set successfully!', 'green');

        return true;
    } catch (error) {
        log('❌ Registration test failed: ' + error.message, 'red');
        return false;
    }
}

// Test 2: Password Reset Flow
async function testPasswordReset() {
    log('\n========================================', 'blue');
    log('TEST 2: Password Reset Flow', 'blue');
    log('========================================', 'blue');

    try {
        // Request password reset
        log('Requesting password reset for ' + TEST_EMAIL + '...', 'yellow');
        const { data, error } = await supabase.auth.resetPasswordForEmail(TEST_EMAIL, {
            redirectTo: 'http://localhost:9001/reset-password.html'
        });

        if (error) throw error;

        log('✅ Password reset email sent!', 'green');
        log('Check your email for the reset link', 'green');
        log('Email should contain: Password reset link or code', 'yellow');

        // In production, user would click the link in email
        log('After clicking the link in your email:', 'yellow');
        log('1. You will be redirected to reset-password.html', 'magenta');
        log('2. Enter your new password', 'magenta');
        log('3. Password will be updated in Supabase', 'magenta');

        return true;
    } catch (error) {
        log('❌ Password reset test failed: ' + error.message, 'red');
        return false;
    }
}

// Test 3: Login with Password
async function testPasswordLogin() {
    log('\n========================================', 'blue');
    log('TEST 3: Login with Password', 'blue');
    log('========================================', 'blue');

    try {
        log('Attempting login with email and password...', 'yellow');
        const { data, error } = await supabase.auth.signInWithPassword({
            email: TEST_EMAIL,
            password: TEST_PASSWORD
        });

        if (error) throw error;

        log('✅ Login successful!', 'green');
        log('Session created with access token', 'green');
        log('User ID: ' + data.user.id, 'green');

        return true;
    } catch (error) {
        log('❌ Login test failed: ' + error.message, 'red');
        return false;
    }
}

// Test 4: Update Password (while logged in)
async function testPasswordUpdate() {
    log('\n========================================', 'blue');
    log('TEST 4: Update Password (while logged in)', 'blue');
    log('========================================', 'blue');

    try {
        // First, ensure we're logged in
        const { data: { user } } = await supabase.auth.getUser();

        if (!user) {
            log('Not logged in, attempting login first...', 'yellow');
            await testPasswordLogin();
        }

        log('Updating password...', 'yellow');
        const { data, error } = await supabase.auth.updateUser({
            password: NEW_PASSWORD
        });

        if (error) throw error;

        log('✅ Password updated successfully!', 'green');

        // Test login with new password
        log('Testing login with new password...', 'yellow');
        await supabase.auth.signOut();

        const { data: loginData, error: loginError } = await supabase.auth.signInWithPassword({
            email: TEST_EMAIL,
            password: NEW_PASSWORD
        });

        if (loginError) throw loginError;

        log('✅ Login with new password successful!', 'green');

        return true;
    } catch (error) {
        log('❌ Password update test failed: ' + error.message, 'red');
        return false;
    }
}

// Test 5: Resend OTP
async function testResendOTP() {
    log('\n========================================', 'blue');
    log('TEST 5: Resend OTP', 'blue');
    log('========================================', 'blue');

    try {
        log('Resending OTP to ' + TEST_EMAIL + '...', 'yellow');
        const { data, error } = await supabase.auth.resend({
            type: 'signup',
            email: TEST_EMAIL
        });

        if (error) throw error;

        log('✅ OTP resent successfully!', 'green');
        log('Check your email for a new 6-digit code', 'green');

        return true;
    } catch (error) {
        // This might fail if user is already verified
        if (error.message.includes('already registered')) {
            log('ℹ️ User already verified, resend not needed', 'yellow');
            return true;
        }
        log('❌ Resend OTP test failed: ' + error.message, 'red');
        return false;
    }
}

// Helper function to get user input
function getUserInput(prompt) {
    return new Promise((resolve) => {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        rl.question(prompt, (answer) => {
            rl.close();
            resolve(answer.trim());
        });
    });
}

// Main test runner
async function runAllTests() {
    log('\n🚀 Starting Supabase Email Flow Tests', 'magenta');
    log('=====================================', 'magenta');

    const results = {
        registration: false,
        passwordReset: false,
        login: false,
        passwordUpdate: false,
        resendOTP: false
    };

    // Ask user what to test
    log('\nSelect tests to run:', 'yellow');
    log('1. Registration with OTP', 'reset');
    log('2. Password Reset', 'reset');
    log('3. Login Test', 'reset');
    log('4. Password Update', 'reset');
    log('5. Resend OTP', 'reset');
    log('6. Run All Tests', 'reset');

    const choice = await getUserInput('\nEnter choice (1-6): ');

    switch(choice) {
        case '1':
            results.registration = await testRegistrationOTP();
            break;
        case '2':
            results.passwordReset = await testPasswordReset();
            break;
        case '3':
            results.login = await testPasswordLogin();
            break;
        case '4':
            results.passwordUpdate = await testPasswordUpdate();
            break;
        case '5':
            results.resendOTP = await testResendOTP();
            break;
        case '6':
            results.registration = await testRegistrationOTP();
            results.login = await testPasswordLogin();
            results.passwordUpdate = await testPasswordUpdate();
            results.passwordReset = await testPasswordReset();
            results.resendOTP = await testResendOTP();
            break;
        default:
            log('Invalid choice', 'red');
            return;
    }

    // Summary
    log('\n========================================', 'magenta');
    log('TEST SUMMARY', 'magenta');
    log('========================================', 'magenta');

    Object.entries(results).forEach(([test, passed]) => {
        if (passed !== false) {
            const status = passed ? '✅ PASSED' : '⏭️  SKIPPED';
            const color = passed ? 'green' : 'yellow';
            log(`${test}: ${status}`, color);
        }
    });

    log('\n📧 Email Configuration Status:', 'blue');
    log('================================', 'blue');

    log('\n1. OTP Emails:', 'yellow');
    log('   - Should send 6-digit codes, not magic links', 'reset');
    log('   - Check Supabase Dashboard → Authentication → Email Templates', 'reset');
    log('   - Template: "Confirm signup" or "Magic Link"', 'reset');

    log('\n2. Password Reset:', 'yellow');
    log('   - Should send reset link with recovery token', 'reset');
    log('   - Link format: /reset-password.html#access_token=...&type=recovery', 'reset');
    log('   - Template: "Reset Password"', 'reset');

    log('\n3. Required Supabase Settings:', 'yellow');
    log('   - Enable Email Provider', 'reset');
    log('   - Enable Email Confirmations', 'reset');
    log('   - OTP Expiry: 3600 seconds (60 minutes)', 'reset');
    log('   - Max Attempts: 5', 'reset');

    log('\n✅ Test script complete!', 'green');
}

// Run tests
runAllTests().catch(console.error);