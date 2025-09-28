import { createClient } from '@supabase/supabase-js';
import axios from 'axios';

// Supabase configuration
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDg0MDA0MTQsImV4cCI6MjAyMzk3NjQxNH0.IakJtbqPPCykXXqPRmg-WumSF9NECVJ4zYOc25qDBLI';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Generate unique test email
const timestamp = Date.now();
const testEmail = `test_${timestamp}@example.com`;
const testPassword = 'TestPass123!';

console.log('🧪 Starting Zmarty App Testing Suite\n');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

async function testRegistration() {
    console.log('1️⃣  Testing User Registration');
    console.log(`   Email: ${testEmail}`);
    console.log(`   Password: ${testPassword}`);

    try {
        // Test registration via Supabase
        const { data, error } = await supabase.auth.signUp({
            email: testEmail,
            password: testPassword,
            options: {
                data: {
                    full_name: 'Test User',
                    country: 'US'
                }
            }
        });

        if (error) {
            console.log(`   ❌ Registration failed: ${error.message}`);
            return false;
        }

        console.log(`   ✅ Registration successful!`);
        console.log(`   User ID: ${data.user?.id}`);
        console.log(`   Confirmation required: ${!data.user?.confirmed_at}`);

        return data.user;
    } catch (err) {
        console.log(`   ❌ Unexpected error: ${err.message}`);
        return false;
    }
}

async function testLogin() {
    console.log('\n2️⃣  Testing User Login');

    try {
        const { data, error } = await supabase.auth.signInWithPassword({
            email: testEmail,
            password: testPassword
        });

        if (error) {
            console.log(`   ❌ Login failed: ${error.message}`);
            if (error.message.includes('Email not confirmed')) {
                console.log(`   ℹ️  Email verification required`);
            }
            return false;
        }

        console.log(`   ✅ Login successful!`);
        console.log(`   Session: ${data.session ? 'Active' : 'None'}`);
        return data.session;
    } catch (err) {
        console.log(`   ❌ Unexpected error: ${err.message}`);
        return false;
    }
}

async function testPasswordReset() {
    console.log('\n3️⃣  Testing Password Reset');

    try {
        const { error } = await supabase.auth.resetPasswordForEmail(testEmail, {
            redirectTo: 'https://zmarty.netlify.app/reset-password'
        });

        if (error) {
            console.log(`   ❌ Password reset failed: ${error.message}`);
            return false;
        }

        console.log(`   ✅ Password reset email sent!`);
        return true;
    } catch (err) {
        console.log(`   ❌ Unexpected error: ${err.message}`);
        return false;
    }
}

async function testAPIEndpoint() {
    console.log('\n4️⃣  Testing API Endpoints');

    const endpoints = [
        'https://zmarty.netlify.app/',
        'https://zmarty.netlify.app/auth/callback',
    ];

    for (const endpoint of endpoints) {
        try {
            const response = await axios.get(endpoint, {
                timeout: 5000,
                validateStatus: () => true
            });
            console.log(`   ✅ ${endpoint}: Status ${response.status}`);
        } catch (err) {
            console.log(`   ❌ ${endpoint}: ${err.message}`);
        }
    }
}

async function checkDatabaseUser() {
    console.log('\n5️⃣  Checking Database for User');

    try {
        // Try to get user profile
        const { data, error } = await supabase
            .from('user_profiles')
            .select('*')
            .eq('email', testEmail)
            .single();

        if (error) {
            console.log(`   ⚠️  Profile not found: ${error.message}`);
        } else {
            console.log(`   ✅ User profile exists in database`);
            console.log(`   Profile data:`, JSON.stringify(data, null, 2));
        }
    } catch (err) {
        console.log(`   ❌ Database check failed: ${err.message}`);
    }
}

async function cleanupTestUser() {
    console.log('\n🧹 Cleanup Test User');

    try {
        // Sign out first
        await supabase.auth.signOut();
        console.log(`   ✅ Test user signed out`);

        // Note: User deletion requires service role key
        console.log(`   ℹ️  Test user (${testEmail}) remains in database`);
        console.log(`   ℹ️  Manual cleanup may be required`);
    } catch (err) {
        console.log(`   ⚠️  Cleanup warning: ${err.message}`);
    }
}

// Run all tests
async function runTestSuite() {
    console.log('🌐 Testing Live Site: https://zmarty.netlify.app\n');

    // Test registration
    const user = await testRegistration();

    // Test login
    await testLogin();

    // Test password reset
    await testPasswordReset();

    // Test API endpoints
    await testAPIEndpoint();

    // Check database
    await checkDatabaseUser();

    // Cleanup
    await cleanupTestUser();

    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('✨ Test Suite Complete!\n');

    // Summary
    console.log('📊 Test Summary:');
    console.log('   • Registration: Tested');
    console.log('   • Login: Tested');
    console.log('   • Password Reset: Tested');
    console.log('   • API Endpoints: Tested');
    console.log('   • Database: Checked');
    console.log('\n🔗 Live App: https://zmarty.netlify.app');
}

// Execute tests
runTestSuite().catch(console.error);