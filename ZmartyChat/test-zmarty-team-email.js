// Test email with zmarty.team domain
import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
    host: 'smtp.resend.com',
    port: 587,
    secure: false,
    auth: {
        user: 'resend',
        pass: 're_FbA39H6g_L2uZQktnoGQgMQZMcDc3xgWg'
    }
});

async function testZmartyTeamEmail() {
    console.log('🚀 Testing email from zmarty.team domain...');

    try {
        // Verify connection
        await transporter.verify();
        console.log('✅ Resend SMTP connection successful!');

        // Send test email from your domain
        console.log('\n📧 Sending test email from noreply@zmarty.team...');

        const info = await transporter.sendMail({
            from: '"ZmartyChat" <noreply@zmarty.team>', // YOUR DOMAIN!
            to: 'dansidanutz@yahoo.com', // Can send to ANY email now!
            subject: 'Welcome to Zmarty.team! 🎉',
            text: 'Your zmarty.team domain is working perfectly with Resend!',
            html: `
                <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #6366f1; margin: 0;">Zmarty.team</h1>
                        <p style="color: #64748b; margin: 5px 0;">Intelligent Trading Insights</p>
                    </div>

                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                        <h2 style="margin: 0 0 10px 0;">🎉 Domain Configured Successfully!</h2>
                        <p style="margin: 0; opacity: 0.95;">Your emails are now being sent from zmarty.team</p>
                    </div>

                    <div style="padding: 30px 0;">
                        <h3 style="color: #334155;">What's Working:</h3>
                        <ul style="color: #475569; line-height: 1.8;">
                            <li>✅ Custom domain email sending</li>
                            <li>✅ Professional email delivery via Resend</li>
                            <li>✅ Can send to any email address</li>
                            <li>✅ Improved deliverability (no spam folders)</li>
                        </ul>
                    </div>

                    <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h4 style="color: #334155; margin: 0 0 10px 0;">Next Steps:</h4>
                        <ol style="color: #475569; line-height: 1.8; margin: 5px 0;">
                            <li>Update Supabase SMTP sender to noreply@zmarty.team</li>
                            <li>Test user registration flow</li>
                            <li>All users will receive emails from your domain!</li>
                        </ol>
                    </div>

                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">

                    <div style="text-align: center; color: #94a3b8; font-size: 12px;">
                        <p>© 2025 Zmarty.team | Powered by Resend</p>
                        <p style="margin: 5px 0;">Professional Email Infrastructure</p>
                    </div>
                </div>
            `
        });

        console.log('✅ Email sent successfully!');
        console.log('📬 Message ID:', info.messageId);
        console.log('\n🎯 SUCCESS: Your zmarty.team domain is ready for production!');
        console.log('Update Supabase to use noreply@zmarty.team as sender');

    } catch (error) {
        if (error.message.includes('verify a domain')) {
            console.error('\n⚠️  Domain not verified yet!');
            console.log('\n📋 To fix this:');
            console.log('1. Go to https://resend.com/domains');
            console.log('2. Add zmarty.team domain');
            console.log('3. Add the DNS records to your domain provider');
            console.log('4. Wait for verification (usually 5-30 minutes)');
            console.log('5. Then run this test again');
        } else {
            console.error('❌ Error:', error.message);
        }
    }
}

// Run the test
testZmartyTeamEmail();