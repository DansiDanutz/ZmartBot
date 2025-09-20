// Test User Registration with Email Verification
// This will register a user in ZmartyBrain and trigger the verification email

import { createClient } from '@supabase/supabase-js';

// ZmartyBrain configuration (where users should be registered)
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

console.log('🚀 ZmartyChat - Testing User Registration');
console.log('=========================================\n');

async function registerUser() {
    const email = 'semebitcoin@gmail.com';
    const password = 'TestPassword123!'; // You can change this

    console.log('📧 Registering user:', email);
    console.log('🔐 Password:', password);
    console.log('📍 Project: ZmartyBrain (xhskmqsgtdhehzlvtuns)\n');

    console.log('🔄 Sending registration request...\n');

    try {
        const { data, error } = await supabase.auth.signUp({
            email: email,
            password: password,
            options: {
                emailRedirectTo: 'http://localhost:8083/verify',
                data: {
                    full_name: 'Seme Bitcoin',
                    source: 'test_registration'
                }
            }
        });

        if (error) {
            // Check if user already exists
            if (error.message.includes('already registered')) {
                console.log('⚠️  User already exists!');
                console.log('\n🔄 Attempting to resend verification email...\n');

                // Try to resend verification
                const { error: resendError } = await supabase.auth.resend({
                    type: 'signup',
                    email: email,
                    options: {
                        emailRedirectTo: 'http://localhost:8083/verify'
                    }
                });

                if (resendError) {
                    console.error('❌ Resend error:', resendError.message);
                } else {
                    console.log('✅ VERIFICATION EMAIL RESENT!');
                    console.log('\n📬 Check your inbox at: semebitcoin@gmail.com');
                }
            } else {
                console.error('❌ Registration error:', error.message);
            }
            return;
        }

        console.log('✅ REGISTRATION SUCCESSFUL!');
        console.log('\n📬 Email Details:');
        console.log('   To: semebitcoin@gmail.com');
        console.log('   From: zmarttradingbot2025@gmail.com');
        console.log('   Subject: Confirm Your Email');
        console.log('   Contains: 6-digit verification code');

        if (data.user) {
            console.log('\n👤 User Created:');
            console.log('   ID:', data.user.id);
            console.log('   Email:', data.user.email);
            console.log('   Created:', new Date().toLocaleString());
        }

        console.log('\n✉️  VERIFICATION EMAIL SENT!');
        console.log('   Check your inbox for the verification code');
        console.log('   The email should arrive within 1-2 minutes');

        console.log('\n📱 What to expect:');
        console.log('   1. Email with ZmartyChat branding');
        console.log('   2. 6-digit verification code');
        console.log('   3. Link to verify account');
        console.log('   4. Beautiful HTML template');

        console.log('\n🔍 Also check:');
        console.log('   • Spam/Junk folder');
        console.log('   • Promotions tab (Gmail)');
        console.log('   • All Mail folder');

    } catch (error) {
        console.error('❌ Unexpected error:', error);
    }
}

// Run the registration
console.log('Starting registration process...\n');
registerUser();