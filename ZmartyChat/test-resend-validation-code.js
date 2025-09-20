// Test Resend Validation Code
// This will resend the verification email to an existing unverified user

import { createClient } from '@supabase/supabase-js';

// ZmartyBrain configuration (where users are registered)
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

console.log('🚀 Zmarty - Testing Resend Validation Code');
console.log('===========================================\n');

async function resendValidationCode() {
    const email = 'semebitcoin@gmail.com';

    console.log('📧 Resending validation code to:', email);
    console.log('📍 Project: ZmartyBrain (xhskmqsgtdhehzlvtuns)\n');

    console.log('🔄 Attempting to resend verification email...\n');

    try {
        // First, let's check if the user exists and their verification status
        const { data: { users }, error: listError } = await supabase.auth.admin.listUsers();

        if (listError) {
            console.log('⚠️  Cannot check user status (admin access needed)');
            console.log('   Proceeding with resend attempt...\n');
        } else {
            const user = users?.find(u => u.email === email);
            if (user) {
                console.log('👤 User found:');
                console.log('   Email:', user.email);
                console.log('   Verified:', user.email_confirmed_at ? 'Yes ✅' : 'No ❌');
                console.log('   Created:', new Date(user.created_at).toLocaleString());
                console.log('');
            }
        }

        // Try to resend the verification email
        const { data, error } = await supabase.auth.resend({
            type: 'signup',
            email: email,
            options: {
                emailRedirectTo: 'http://localhost:8083/verify'
            }
        });

        if (error) {
            if (error.message.includes('already confirmed')) {
                console.log('✅ User email is already verified!');
                console.log('   No need to resend validation code.\n');
            } else if (error.message.includes('rate limit')) {
                console.log('⏱️  Rate limit reached!');
                console.log('   Please wait a minute before resending.\n');
                console.log('   Supabase limits: Maximum 4 emails per hour per address');
            } else {
                console.error('❌ Error resending email:', error.message);
            }
            return;
        }

        console.log('✅ VALIDATION CODE RESENT SUCCESSFULLY!');
        console.log('\n📬 Email Details:');
        console.log('   To: semebitcoin@gmail.com');
        console.log('   From: zmarttradingbot2025@gmail.com');
        console.log('   Subject: Verify Your Zmarty Account');
        console.log('   Contains: 6-digit verification code');

        console.log('\n✉️  CHECK YOUR EMAIL!');
        console.log('   A new verification code has been sent');
        console.log('   The email should arrive within 1-2 minutes');

        console.log('\n📱 What to expect:');
        console.log('   1. Email with Zmarty branding (not ZmartyChat)');
        console.log('   2. New 6-digit verification code');
        console.log('   3. Verification button/link');
        console.log('   4. Links to Zmarty.Team website');

        console.log('\n⚠️  Important:');
        console.log('   • Previous codes are now invalid');
        console.log('   • Use the newest code received');
        console.log('   • Code expires in 60 minutes');

        console.log('\n🔍 Also check:');
        console.log('   • Spam/Junk folder');
        console.log('   • Promotions tab (Gmail)');
        console.log('   • All Mail folder');

    } catch (error) {
        console.error('❌ Unexpected error:', error);
    }
}

// Run the resend
console.log('Starting resend validation process...\n');
resendValidationCode();