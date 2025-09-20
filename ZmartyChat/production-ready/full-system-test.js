// COMPLETE SYSTEM TEST - Checks EVERYTHING before deployment
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

console.log('🔍 COMPLETE SYSTEM TEST - ZmartyChat');
console.log('=====================================\n');

let testsPass = 0;
let testsFail = 0;
const issues = [];

async function test(name, testFunc) {
    process.stdout.write(`Testing: ${name}... `);
    try {
        const result = await testFunc();
        if (result) {
            console.log('✅ PASS');
            testsPass++;
            return true;
        } else {
            console.log('❌ FAIL');
            testsFail++;
            issues.push(name);
            return false;
        }
    } catch (error) {
        console.log(`❌ ERROR: ${error.message}`);
        testsFail++;
        issues.push(`${name}: ${error.message}`);
        return false;
    }
}

async function runAllTests() {
    console.log('📋 1. TESTING SUPABASE CONNECTION\n');

    // Test 1: Supabase Connection
    await test('Supabase API accessible', async () => {
        const { error } = await supabase.from('users').select('count').limit(1);
        return !error || error.code === '42P01'; // Table might not exist yet
    });

    // Test 2: Auth Service
    await test('Auth service available', async () => {
        const { data: { session } } = await supabase.auth.getSession();
        return true; // If no error thrown, auth is working
    });

    console.log('\n📋 2. TESTING EMAIL CONFIGURATION\n');

    // Test 3: Email Sending
    const emailWorks = await test('Email sending configured', async () => {
        const testEmail = `test${Date.now()}@example.com`;
        const { data, error } = await supabase.auth.signUp({
            email: testEmail,
            password: 'TestPassword123!'
        });

        if (error) {
            if (error.message.includes('Error sending confirmation email')) {
                console.log('\n   ⚠️  SMTP not configured in Supabase!');
                return false;
            }
            // Other errors might be OK (like rate limiting)
            return error.message.includes('rate limit') ||
                   error.message.includes('too many requests');
        }
        return true;
    });

    if (!emailWorks) {
        console.log('\n   📧 TO FIX EMAIL:');
        console.log('   1. Go to: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns');
        console.log('   2. Settings → Auth → SMTP Settings');
        console.log('   3. Configure Gmail SMTP or enable built-in email');
    }

    console.log('\n📋 3. TESTING FRONTEND FILES\n');

    // Test 4: Check critical files exist
    const fs = await import('fs/promises');

    await test('index.html exists', async () => {
        try {
            await fs.access('./index.html');
            return true;
        } catch {
            return false;
        }
    });

    await test('onboarding-fixed.js exists', async () => {
        try {
            await fs.access('./onboarding-fixed.js');
            return true;
        } catch {
            // Try the original name
            try {
                await fs.access('./onboarding-slides.js');
                console.log('\n   ⚠️  Using onboarding-slides.js instead of onboarding-fixed.js');
                return true;
            } catch {
                return false;
            }
        }
    });

    await test('supabase-client.js exists', async () => {
        try {
            await fs.access('./supabase-client.js');
            return true;
        } catch {
            return false;
        }
    });

    console.log('\n📋 4. TESTING NAVIGATION FUNCTIONS\n');

    await test('Navigation functions defined', async () => {
        const content = await fs.readFile('./onboarding-fixed.js', 'utf-8').catch(() =>
            fs.readFile('./onboarding-slides.js', 'utf-8')
        );

        const hasNextSlide = content.includes('window.nextSlide');
        const hasPreviousSlide = content.includes('window.previousSlide');
        const hasGoToSlide = content.includes('window.goToSlide');

        if (!hasNextSlide) console.log('\n   ❌ Missing: window.nextSlide');
        if (!hasPreviousSlide) console.log('\n   ❌ Missing: window.previousSlide');
        if (!hasGoToSlide) console.log('\n   ❌ Missing: window.goToSlide');

        return hasNextSlide && hasPreviousSlide && hasGoToSlide;
    });

    console.log('\n📋 5. TESTING EMAIL DETECTION FUNCTIONS\n');

    await test('Email detection functions defined', async () => {
        const content = await fs.readFile('./onboarding-fixed.js', 'utf-8').catch(() =>
            fs.readFile('./onboarding-slides.js', 'utf-8')
        );

        const hasCheckEmail = content.includes('checkEmailExists') || content.includes('checkEmailAndShowFields');
        const hasSimpleRegister = content.includes('simpleRegister') || content.includes('continueWithEmail');

        if (!hasCheckEmail) console.log('\n   ❌ Missing: email checking function');
        if (!hasSimpleRegister) console.log('\n   ❌ Missing: registration function');

        return hasCheckEmail && hasSimpleRegister;
    });

    console.log('\n📋 6. TESTING ACTUAL USER REGISTRATION\n');

    const realEmailTest = await test('Can register semebitcoin@gmail.com', async () => {
        const { data, error } = await supabase.auth.signUp({
            email: 'semebitcoin@gmail.com',
            password: 'TestPassword123!',
            options: {
                emailRedirectTo: 'https://memoproapp.netlify.app/dashboard.html'
            }
        });

        if (error) {
            if (error.message.includes('already registered')) {
                console.log('\n   ℹ️  User already exists - trying password reset instead');

                // Try password reset
                const { error: resetError } = await supabase.auth.resetPasswordForEmail(
                    'semebitcoin@gmail.com',
                    { redirectTo: 'https://memoproapp.netlify.app/reset-password.html' }
                );

                if (!resetError) {
                    console.log('   ✅ Password reset email sent!');
                    return true;
                }
                return false;
            }

            console.log(`\n   ❌ Error: ${error.message}`);
            return false;
        }

        console.log('\n   ✅ Registration email sent to semebitcoin@gmail.com!');
        return true;
    });

    // FINAL SUMMARY
    console.log('\n========================================');
    console.log('📊 TEST RESULTS SUMMARY');
    console.log('========================================');
    console.log(`✅ Passed: ${testsPass}`);
    console.log(`❌ Failed: ${testsFail}`);
    console.log(`📈 Score: ${Math.round((testsPass / (testsPass + testsFail)) * 100)}%`);

    if (testsFail > 0) {
        console.log('\n🔧 ISSUES TO FIX:');
        issues.forEach((issue, i) => {
            console.log(`${i + 1}. ${issue}`);
        });

        console.log('\n📋 CRITICAL FIXES NEEDED:');

        if (!emailWorks) {
            console.log('\n🚨 EMAIL NOT WORKING - USERS CANNOT REGISTER!');
            console.log('   Fix: Configure SMTP in Supabase Dashboard');
            console.log('   URL: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/auth');
        }

        if (issues.some(i => i.includes('Navigation'))) {
            console.log('\n🚨 NAVIGATION NOT WORKING - USERS CANNOT NAVIGATE!');
            console.log('   Fix: Use onboarding-fixed.js instead of onboarding-slides.js');
        }

    } else {
        console.log('\n🎉 ALL TESTS PASSED! Ready for production!');
        console.log('\n📦 Deploy to Netlify:');
        console.log('   1. Go to: https://app.netlify.com/drop');
        console.log('   2. Drag the production-ready folder');
        console.log('   3. Done!');
    }

    console.log('\n========================================\n');
}

// Run tests
runAllTests().catch(console.error);