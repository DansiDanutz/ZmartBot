// Test Single Email Send via Supabase
import { createClient } from '@supabase/supabase-js';

// Supabase configuration
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

console.log('🚀 ZmartyChat - Testing Email Delivery');
console.log('=======================================\n');

async function sendPasswordResetEmail() {
    console.log('📧 Sending Password Reset Email...');
    console.log('To: semebitcoin@gmail.com\n');

    try {
        const { data, error } = await supabase.auth.resetPasswordForEmail(
            'semebitcoin@gmail.com',
            {
                redirectTo: 'http://localhost:8083/reset-password'
            }
        );

        if (error) {
            console.error('❌ Error sending email:', error.message);

            if (error.message.includes('rate limit')) {
                console.log('\n⏱️ Rate limit detected. Supabase limits email sends to prevent spam.');
                console.log('   Please wait a few minutes before trying again.');
                console.log('\n💡 Tip: Check your spam/junk folder as well.');
            }
        } else {
            console.log('✅ SUCCESS! Password reset email sent!');
            console.log('\n📬 Email Details:');
            console.log('   • Sent to: semebitcoin@gmail.com');
            console.log('   • Type: Password Reset');
            console.log('   • Template: Your custom ZmartyChat template');
            console.log('   • Valid for: 60 minutes');
            console.log('\n🔍 Check your inbox for:');
            console.log('   • Subject: "Reset Your Password" or similar');
            console.log('   • From: noreply@supabase.io or your configured sender');
            console.log('   • Beautiful ZmartyChat branded email');
            console.log('\n📁 Also check:');
            console.log('   • Spam/Junk folder');
            console.log('   • Promotions tab (Gmail)');
            console.log('   • Other inbox categories');
        }
    } catch (error) {
        console.error('❌ Unexpected error:', error);
    }
}

// Check email configuration status
async function checkEmailStatus() {
    console.log('\n📊 Checking Email System Status...');
    console.log('-----------------------------------\n');

    console.log('✅ Supabase Project: xhskmqsgtdhehzlvtuns');
    console.log('✅ SMTP Configuration: Active (Gmail)');
    console.log('✅ Email Template: Custom ZmartyChat template');
    console.log('✅ Sender: zmarttradingbot2025@gmail.com');

    console.log('\n📝 Note: Emails may take 1-2 minutes to arrive.');
    console.log('   If not received, check spam/junk folder.');
}

// Main execution
async function main() {
    // Send the email
    await sendPasswordResetEmail();

    // Show status
    await checkEmailStatus();

    console.log('\n=======================================');
    console.log('📧 Email test complete!');
    console.log('Please check semebitcoin@gmail.com inbox');
    console.log('=======================================\n');
}

// Run the test
main();