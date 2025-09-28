// Test direct signup with Supabase Auth
import { createClient } from '@supabase/supabase-js';

// ZmartyBrain project credentials (correct project for auth)
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQzODU0MDAsImV4cCI6MjA0OTk2MTQwMH0.eCBN-KuF-EuUpS0lO1aBP2HpJyqQrVNfGLJmx7PwMBU';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function testSignup() {
    console.log('Testing signup with dansidanutz@yahoo.com...');

    try {
        // Test signup with OTP
        const { data, error } = await supabase.auth.signUp({
            email: 'dansidanutz@yahoo.com',
            password: 'Test123!@#',
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
            console.error('Signup error:', error);
            console.error('Error details:', {
                message: error.message,
                status: error.status,
                code: error.code,
                name: error.name
            });
        } else {
            console.log('Signup successful!');
            console.log('User:', data.user);
            console.log('Session:', data.session);

            // Check if confirmation email was sent
            if (data.user && !data.user.confirmed_at) {
                console.log('Confirmation email should have been sent to:', data.user.email);
            }
        }
    } catch (err) {
        console.error('Unexpected error:', err);
    }
}

// Run the test
testSignup();