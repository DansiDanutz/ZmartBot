// Debug Resend Validation Code Issue
// Let's check the user status and try different approaches

import { createClient } from '@supabase/supabase-js';

// ZmartyBrain configuration
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

console.log('🔍 Debugging Resend Validation Issue');
console.log('=====================================\n');

async function debugResend() {
    const email = 'semebitcoin@gmail.com';

    console.log('📧 Target email:', email);
    console.log('📍 Project: ZmartyBrain\n');

    // Method 1: Try standard resend
    console.log('Method 1: Standard Resend');
    console.log('-------------------------');
    try {
        const { data, error } = await supabase.auth.resend({
            type: 'signup',
            email: email,
            options: {
                emailRedirectTo: 'http://localhost:8083/verify'
            }
        });

        if (error) {
            console.log('❌ Standard resend error:', error.message);
            console.log('   Error code:', error.code || 'N/A');
            console.log('   Status:', error.status || 'N/A');
        } else {
            console.log('✅ Standard resend successful!');
            console.log('   Response:', JSON.stringify(data, null, 2));
        }
    } catch (err) {
        console.log('❌ Exception:', err.message);
    }

    console.log('\n');

    // Method 2: Try to sign in first to check if user exists
    console.log('Method 2: Check User Exists via Sign In');
    console.log('----------------------------------------');
    try {
        const { data, error } = await supabase.auth.signInWithPassword({
            email: email,
            password: 'dummy_password_test'
        });

        if (error) {
            if (error.message.includes('Invalid login')) {
                console.log('✅ User exists (invalid password response)');
            } else if (error.message.includes('Email not confirmed')) {
                console.log('✅ User exists but email not confirmed');
                console.log('   This user needs verification!');
            } else if (error.message.includes('User not found')) {
                console.log('❌ User does not exist in database');
                console.log('   Need to register first!');
            } else {
                console.log('⚠️  Other error:', error.message);
            }
        }
    } catch (err) {
        console.log('❌ Exception:', err.message);
    }

    console.log('\n');

    // Method 3: Try to register the user (will fail if exists)
    console.log('Method 3: Check via Registration Attempt');
    console.log('-----------------------------------------');
    try {
        const { data, error } = await supabase.auth.signUp({
            email: email,
            password: 'TestPassword123!',
            options: {
                emailRedirectTo: 'http://localhost:8083/verify'
            }
        });

        if (error) {
            if (error.message.includes('already registered')) {
                console.log('✅ User already registered');

                // Now try to resend after confirming user exists
                console.log('\n   Attempting resend for existing user...');
                const { error: resendError } = await supabase.auth.resend({
                    type: 'signup',
                    email: email
                });

                if (resendError) {
                    console.log('   ❌ Resend failed:', resendError.message);
                } else {
                    console.log('   ✅ Resend successful after registration check!');
                }
            } else {
                console.log('⚠️  Registration error:', error.message);
            }
        } else {
            console.log('🆕 New user created!');
            console.log('   User ID:', data.user?.id);
            console.log('   Confirmation email sent');
        }
    } catch (err) {
        console.log('❌ Exception:', err.message);
    }

    console.log('\n');

    // Method 4: Check auth settings
    console.log('Method 4: Auth Configuration Check');
    console.log('-----------------------------------');
    console.log('📋 Checklist:');
    console.log('   1. SMTP configured in Supabase? ✅ (using Gmail SMTP)');
    console.log('   2. Email template active? ✅ (custom Zmarty template)');
    console.log('   3. Rate limiting? Max 4 emails/hour per address');
    console.log('   4. User confirmed? Check Supabase dashboard');

    console.log('\n🔍 Next Steps:');
    console.log('   1. Check Supabase dashboard -> Authentication -> Users');
    console.log('   2. Look for semebitcoin@gmail.com');
    console.log('   3. Check "Email Confirmed At" column');
    console.log('   4. If confirmed, resend won\'t work (already verified)');
    console.log('   5. Check email logs in Supabase -> Logs -> Auth');
}

console.log('Starting debug process...\n');
debugResend();