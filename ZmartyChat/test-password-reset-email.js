// Test Password Reset Email with Updated Zmarty Branding
// This will trigger a password reset email to semebitcoin@gmail.com

import { createClient } from '@supabase/supabase-js';

// ZmartyBrain configuration (where users are registered)
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

console.log('🚀 Zmarty - Testing Password Reset Email');
console.log('=========================================\n');

async function sendPasswordResetEmail() {
    const email = 'semebitcoin@gmail.com';

    console.log('📧 Requesting password reset for:', email);
    console.log('📍 Project: ZmartyBrain (xhskmqsgtdhehzlvtuns)\n');

    console.log('🔄 Sending password reset request...\n');

    try {
        const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: 'http://localhost:8083/reset-password',
        });

        if (error) {
            console.error('❌ Error sending reset email:', error.message);
            return;
        }

        console.log('✅ PASSWORD RESET EMAIL SENT!');
        console.log('\n📬 Email Details:');
        console.log('   To: semebitcoin@gmail.com');
        console.log('   From: zmarttradingbot2025@gmail.com');
        console.log('   Subject: Reset Your Zmarty Password');
        console.log('   Contains: Password reset link + joke');

        console.log('\n✉️  CHECK YOUR EMAIL!');
        console.log('   The email should arrive within 1-2 minutes');

        console.log('\n📱 What to expect:');
        console.log('   1. Email with Zmarty branding');
        console.log('   2. A crypto joke to brighten your day');
        console.log('   3. Password reset link');
        console.log('   4. Security notice');
        console.log('   5. Links to Zmarty.Team website');

        console.log('\n😄 Joke Preview:');
        console.log('   "Why don\'t crypto traders ever forget their passwords?');
        console.log('   Because they always keep them in cold storage!"');

        console.log('\n🔍 Also check:');
        console.log('   • Spam/Junk folder');
        console.log('   • Promotions tab (Gmail)');
        console.log('   • All Mail folder');

    } catch (error) {
        console.error('❌ Unexpected error:', error);
    }
}

// Run the password reset
console.log('Starting password reset process...\n');
sendPasswordResetEmail();