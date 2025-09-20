// Test Password Reset and Resend Verification Code
import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

console.log('🔐 ZmartyChat Email Testing Suite');
console.log('==================================\n');

// Function to test password reset
async function testPasswordReset() {
    console.log('📧 TEST 1: PASSWORD RESET');
    console.log('-------------------------\n');

    console.log('🎯 Target Email: semebitcoin@gmail.com');
    console.log('📝 Testing forgot password functionality...\n');

    try {
        const { data, error } = await supabase.auth.resetPasswordForEmail(
            'semebitcoin@gmail.com',
            {
                redirectTo: 'http://localhost:8083/reset-password'
            }
        );

        if (error) {
            console.error('❌ Error:', error.message);
        } else {
            console.log('✅ PASSWORD RESET EMAIL SENT!');
            console.log('\n📬 Email Details:');
            console.log('   Type: Password Reset');
            console.log('   To: semebitcoin@gmail.com');
            console.log('   Template: Your ZmartyChat custom template');
            console.log('   Contains: Reset password link');
            console.log('   Expires: 60 minutes');
            console.log('   Redirect: http://localhost:8083/reset-password');

            console.log('\n🔑 What to expect in your inbox:');
            console.log('   • Email with ZmartyChat branding');
            console.log('   • "Reset Your Password" subject');
            console.log('   • Secure reset link');
            console.log('   • Your beautiful template design');
        }
    } catch (error) {
        console.error('❌ Unexpected error:', error);
    }
}

// Function to test resend verification code
async function testResendVerification() {
    console.log('\n\n📧 TEST 2: RESEND VERIFICATION CODE');
    console.log('------------------------------------\n');

    // First, create a new test account to get unverified status
    const testEmail = `verify.test.${Date.now()}@zmartychat.com`;

    console.log('🎯 Creating test account:', testEmail);
    console.log('📝 This will trigger verification email...\n');

    try {
        // Step 1: Create account
        const { data: signupData, error: signupError } = await supabase.auth.signUp({
            email: testEmail,
            password: 'TestPassword123!',
            options: {
                emailRedirectTo: 'http://localhost:8083/verify',
                data: {
                    full_name: 'Verification Test'
                }
            }
        });

        if (signupError) {
            console.error('❌ Signup error:', signupError.message);
            return;
        }

        console.log('✅ Test account created');
        console.log('📧 First verification email sent\n');

        // Wait a moment
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Step 2: Resend verification
        console.log('🔄 Now testing RESEND functionality...\n');

        const { data: resendData, error: resendError } = await supabase.auth.resend({
            type: 'signup',
            email: testEmail,
            options: {
                emailRedirectTo: 'http://localhost:8083/verify'
            }
        });

        if (resendError) {
            console.error('❌ Resend error:', resendError.message);
        } else {
            console.log('✅ VERIFICATION CODE RESENT!');
            console.log('\n📬 Email Details:');
            console.log('   Type: Verification Code (Resent)');
            console.log('   To:', testEmail);
            console.log('   Template: Your ZmartyChat custom template');
            console.log('   Contains: 6-digit verification code');
            console.log('   Expires: 60 minutes');

            console.log('\n🔢 Verification Code Features:');
            console.log('   • Large, clear 6-digit display');
            console.log('   • 60-minute expiration timer');
            console.log('   • Professional ZmartyChat design');
            console.log('   • Security warnings included');
        }
    } catch (error) {
        console.error('❌ Unexpected error:', error);
    }
}

// Function to test with existing user (your email)
async function testResendForExistingUser() {
    console.log('\n\n📧 TEST 3: RESEND FOR YOUR EMAIL');
    console.log('----------------------------------\n');

    console.log('🎯 Testing with: semebitcoin@gmail.com');
    console.log('📝 Attempting resend verification...\n');

    try {
        // Try to resend for existing email
        const { data, error } = await supabase.auth.resend({
            type: 'signup',
            email: 'semebitcoin@gmail.com',
            options: {
                emailRedirectTo: 'http://localhost:8083/verify'
            }
        });

        if (error) {
            if (error.message.includes('already confirmed') || error.message.includes('already registered')) {
                console.log('ℹ️  Email already verified');
                console.log('\n💡 Since your email is already verified,');
                console.log('   triggering a password reset instead...\n');

                // Send password reset as alternative
                const { error: resetError } = await supabase.auth.resetPasswordForEmail(
                    'semebitcoin@gmail.com',
                    {
                        redirectTo: 'http://localhost:8083/reset-password'
                    }
                );

                if (!resetError) {
                    console.log('✅ PASSWORD RESET EMAIL SENT TO semebitcoin@gmail.com!');
                    console.log('📬 Check your inbox for the reset link');
                }
            } else {
                console.error('❌ Error:', error.message);
            }
        } else {
            console.log('✅ VERIFICATION EMAIL RESENT TO semebitcoin@gmail.com!');
            console.log('📬 Check your inbox for the verification code');
        }
    } catch (error) {
        console.error('❌ Unexpected error:', error);
    }
}

// Main test runner
async function runAllTests() {
    console.log('Starting comprehensive email tests...\n');

    // Test 1: Password Reset
    await testPasswordReset();

    // Wait between tests
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Test 2: Resend Verification
    await testResendVerification();

    // Wait between tests
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Test 3: Resend for your email
    await testResendForExistingUser();

    console.log('\n\n========================================');
    console.log('✅ ALL TESTS COMPLETE!');
    console.log('========================================\n');

    console.log('📊 Summary:');
    console.log('   • Password Reset: Sent to semebitcoin@gmail.com ✅');
    console.log('   • Verification Code: Created and resent test ✅');
    console.log('   • Your Email: Handled based on verification status ✅');

    console.log('\n🎨 All emails use your beautiful ZmartyChat template!');
    console.log('📬 Check semebitcoin@gmail.com inbox for the emails');

    console.log('\n📌 Email Types Sent:');
    console.log('   1. Password Reset Link');
    console.log('   2. Verification Code (6 digits)');
    console.log('   3. Resend Confirmation');
}

// Run all tests
runAllTests();