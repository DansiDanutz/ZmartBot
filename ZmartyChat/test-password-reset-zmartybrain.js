// Test password reset email to verify SMTP is working
import { createClient } from '@supabase/supabase-js';

// ZmartyBrain project credentials (correct API key from dashboard)
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function testPasswordReset() {
    console.log('Testing password reset email for dansidanutz@yahoo.com...');

    try {
        const { data, error } = await supabase.auth.resetPasswordForEmail(
            'dansidanutz@yahoo.com',
            {
                redirectTo: 'http://localhost:8084/onboarding2/index.html'
            }
        );

        if (error) {
            console.error('Password reset error:', error);
            console.error('Error details:', {
                message: error.message,
                status: error.status,
                code: error.code
            });
        } else {
            console.log('Password reset email request successful!');
            console.log('Response:', data);
            console.log('\nCheck your email at dansidanutz@yahoo.com for the reset link.');
        }
    } catch (err) {
        console.error('Unexpected error:', err);
    }
}

// First, let's create the user if it doesn't exist
async function createUserThenReset() {
    console.log('Step 1: Attempting to create user first...');

    const { data: signupData, error: signupError } = await supabase.auth.signUp({
        email: 'dansidanutz@yahoo.com',
        password: 'Test123!@#',
        options: {
            data: {
                full_name: 'Test User',
                country: 'US'
            }
        }
    });

    if (signupError && !signupError.message.includes('already registered')) {
        console.error('Signup error:', signupError);
    } else if (signupData?.user) {
        console.log('User created or already exists:', signupData.user.email);
    }

    console.log('\nStep 2: Testing password reset email...');
    await testPasswordReset();
}

// Run the test
createUserThenReset();