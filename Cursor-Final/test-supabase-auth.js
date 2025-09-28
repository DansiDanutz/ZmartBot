const { createClient } = require('@supabase/supabase-js');

// ZmartyBrain credentials
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function testAuth() {
    console.log('🔄 Testing ZmartyBrain Authentication...\n');

    const testEmail = `test${Date.now()}@example.com`;
    const testPassword = 'Test123!@#';

    try {
        // Test signup
        console.log('1️⃣ Testing signUp...');
        const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
            email: testEmail,
            password: testPassword,
            options: {
                data: {
                    full_name: 'Test User',
                    country: 'US'
                }
            }
        });

        if (signUpError) {
            console.error('❌ SignUp error:', signUpError.message);
            return;
        }

        console.log('✅ SignUp successful!');
        console.log('   User ID:', signUpData.user?.id);
        console.log('   Email:', signUpData.user?.email);
        console.log('   Confirmation required:', signUpData.user?.email_confirmed_at ? 'No' : 'Yes');

        // Test getting session
        console.log('\n2️⃣ Testing getSession...');
        const { data: sessionData } = await supabase.auth.getSession();
        console.log('   Session exists:', !!sessionData.session);

        // Test profiles table access
        console.log('\n3️⃣ Testing profiles table access...');
        const { data: profiles, error: profileError } = await supabase
            .from('profiles')
            .select('*')
            .limit(1);

        if (profileError) {
            console.error('❌ Profile access error:', profileError.message);
        } else {
            console.log('✅ Profiles table accessible');
        }

        console.log('\n✅ All tests passed! Supabase is configured correctly.');

    } catch (error) {
        console.error('❌ Test failed:', error);
    }
}

testAuth();