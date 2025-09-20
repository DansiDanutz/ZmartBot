// Node.js script to test Supabase email sending
// Run with: node send-test-email.js

import { createClient } from '@supabase/supabase-js';

// ZmartyBrain Supabase configuration (for user management)
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function sendTestEmail() {
    const email = 'semebitcoin@gmail.com';
    const password = 'TestPassword123!';

    console.log('=================================');
    console.log('📧 SENDING TEST EMAIL TO:', email);
    console.log('=================================\n');

    try {
        console.log('🔄 Attempting to register user...');

        // Try to sign up the user
        const { data, error } = await supabase.auth.signUp({
            email: email,
            password: password,
            options: {
                emailRedirectTo: 'https://memoproapp.netlify.app/dashboard.html',
                data: {
                    source: 'node-test-script',
                    timestamp: new Date().toISOString()
                }
            }
        });

        if (error) {
            console.error('❌ Error:', error.message);

            if (error.message.includes('already registered')) {
                console.log('\n⚠️  User already exists, trying to resend confirmation...\n');

                // Try to resend the confirmation email
                const { error: resendError } = await supabase.auth.resend({
                    type: 'signup',
                    email: email
                });

                if (resendError) {
                    console.error('❌ Resend failed:', resendError.message);
                } else {
                    console.log('✅ Confirmation email RESENT successfully!');
                    console.log('📬 Check your inbox at:', email);
                }
            }
        } else {
            console.log('\n✅ SUCCESS! Email sent to:', email);
            console.log('📬 Details:');
            console.log('   - User ID:', data.user?.id);
            console.log('   - Email:', data.user?.email);
            console.log('   - Created:', data.user?.created_at);
            console.log('\n📮 Please check your inbox (and spam folder)!');
        }

    } catch (error) {
        console.error('❌ Unexpected error:', error);
    }

    console.log('\n=================================');
    console.log('📧 EMAIL TEST COMPLETE');
    console.log('=================================');
}

// Run the test
sendTestEmail();