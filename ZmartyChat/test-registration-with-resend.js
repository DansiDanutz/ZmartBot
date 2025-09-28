// Test registration with Resend configured
import { createClient } from '@supabase/supabase-js';

// ZmartyBrain project credentials
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function testRegistration() {
    // Test with seme@kryptostack.com since Resend allows this email
    const testEmail = 'seme@kryptostack.com';
    const timestamp = Date.now();

    console.log('🚀 Testing registration with Resend email service...');
    console.log(`📧 Registering: ${testEmail}`);

    try {
        // First delete existing user if any
        const { data: existingUser } = await supabase.auth.admin?.deleteUser?.(testEmail).catch(() => ({ data: null }));

        // Sign up new user
        const { data, error } = await supabase.auth.signUp({
            email: testEmail,
            password: 'TestPassword123!@#',
            options: {
                emailRedirectTo: 'http://localhost:8084/onboarding2/index.html',
                data: {
                    full_name: 'Test User',
                    country: 'US',
                    selected_tier: 'free'
                }
            }
        });

        if (error) {
            console.error('❌ Signup error:', error.message);

            // If user exists, try to resend confirmation
            if (error.message.includes('already registered')) {
                console.log('🔄 User exists, trying to resend confirmation email...');

                const { error: resendError } = await supabase.auth.resend({
                    type: 'signup',
                    email: testEmail
                });

                if (resendError) {
                    console.error('❌ Resend error:', resendError);
                } else {
                    console.log('✅ Confirmation email resent successfully!');
                    console.log('📬 Check inbox at seme@kryptostack.com');
                }
            }
        } else {
            console.log('✅ User registered successfully!');
            console.log('User ID:', data.user?.id);
            console.log('Email:', data.user?.email);
            console.log('');
            console.log('📬 IMPORTANT: Check your email at seme@kryptostack.com');
            console.log('You should receive a verification email from onboarding@resend.dev');

            // Check if email was confirmed (it won't be until they click the link)
            if (!data.user?.email_confirmed_at) {
                console.log('⏳ Status: Waiting for email confirmation...');
            }
        }

    } catch (err) {
        console.error('❌ Unexpected error:', err);
    }
}

// Run the test
testRegistration();