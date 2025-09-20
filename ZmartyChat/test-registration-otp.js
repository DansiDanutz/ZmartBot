// Test Registration OTP Flow
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://asjtxrmftmutcsnqgidy.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Generate a unique test email
const timestamp = Date.now();
const TEST_EMAIL = `testuser${timestamp}@zmartbot.com`;

console.log('🚀 Testing Registration OTP Flow');
console.log('==================================');
console.log(`📧 Test Email: ${TEST_EMAIL}`);
console.log('');

async function testRegistrationOTP() {
    try {
        // Send OTP for registration
        console.log('📤 Sending OTP email...');
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

        if (error) {
            console.error('❌ Error sending OTP:', error.message);
            return;
        }

        console.log('✅ OTP sent successfully!');
        console.log('');
        console.log('📋 Next Steps:');
        console.log('1. Check email for the 6-digit verification code');
        console.log('2. The email should display the code prominently');
        console.log('3. Use the code in your app to verify the email');
        console.log('');
        console.log('⚠️  Note: If you receive a magic link instead of a code,');
        console.log('    the Supabase email template needs to be updated.');
        console.log('');
        console.log('📧 Email Details:');
        console.log(`   To: ${TEST_EMAIL}`);
        console.log('   Subject: Verification Email - Welcome to Zmarty 🚀');
        console.log('   Should contain: 6-digit verification code');

    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

// Run the test
testRegistrationOTP();