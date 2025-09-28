// Test email with zmarty.me domain
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

async function testZmartyMeEmail() {
    console.log('🚀 Testing email from zmarty.me domain...');

    try {
        // Verify connection
        await transporter.verify();
        console.log('✅ Resend SMTP connection successful!');

        // Test if domain is verified
        console.log('\n📧 Attempting to send from noreply@zmarty.me...');

        const info = await transporter.sendMail({
            from: '"Zmarty" <noreply@zmarty.me>', // Your new domain!
            to: 'dansidanutz@yahoo.com', // Can send to anyone once verified
            subject: 'Welcome to Zmarty.me! 🚀',
            text: 'Your zmarty.me domain is configured!',
            html: `
                <div style="font-family: system-ui, -apple-system, sans-serif; max-width: 600px; margin: 0 auto;">
                    <!-- Header -->
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; border-radius: 12px 12px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 32px; font-weight: bold;">
                            ZMARTY.ME
                        </h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">
                            AI-Powered Trading Intelligence
                        </p>
                    </div>

                    <!-- Body -->
                    <div style="background: white; padding: 40px 30px; border: 1px solid #e5e7eb; border-top: none;">
                        <h2 style="color: #1f2937; margin: 0 0 20px 0;">
                            ✅ Domain Successfully Configured!
                        </h2>

                        <p style="color: #4b5563; line-height: 1.6; margin: 0 0 20px 0;">
                            Great news! Your custom domain <strong>zmarty.me</strong> is now ready to send professional emails through Resend.
                        </p>

                        <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 30px 0;">
                            <h3 style="color: #374151; margin: 0 0 15px 0; font-size: 16px;">
                                ✨ What's Now Possible:
                            </h3>
                            <ul style="color: #6b7280; margin: 0; padding-left: 20px; line-height: 1.8;">
                                <li>Send emails from <strong>@zmarty.me</strong></li>
                                <li>Reach any email address worldwide</li>
                                <li>Professional delivery (avoid spam folders)</li>
                                <li>Track email opens and clicks (optional)</li>
                            </ul>
                        </div>

                        <div style="background: #fef3c7; padding: 20px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                            <h3 style="color: #92400e; margin: 0 0 10px 0; font-size: 16px;">
                                🎯 Final Step:
                            </h3>
                            <p style="color: #92400e; margin: 0;">
                                Update Supabase SMTP settings to use <strong>noreply@zmarty.me</strong> as the sender email.
                            </p>
                        </div>
                    </div>

                    <!-- Footer -->
                    <div style="background: #f9fafb; padding: 20px; text-align: center; border-radius: 0 0 12px 12px; border: 1px solid #e5e7eb; border-top: none;">
                        <p style="color: #9ca3af; font-size: 14px; margin: 0;">
                            © 2025 Zmarty.me | Powered by Resend
                        </p>
                    </div>
                </div>
            `
        });

        console.log('✅ Email sent successfully!');
        console.log('📬 Message ID:', info.messageId);
        console.log('\n🎉 SUCCESS! Your zmarty.me domain is ready!');
        console.log('\n📝 Next: Update Supabase SMTP to use noreply@zmarty.me');

    } catch (error) {
        if (error.message.includes('not verified')) {
            console.error('\n⚠️  Domain not verified yet!\n');
            console.log('📋 Quick Setup Guide:');
            console.log('────────────────────');
            console.log('1. Go to: https://resend.com/domains');
            console.log('2. Add domain: zmarty.me');
            console.log('3. Copy the DNS records shown');
            console.log('4. Add them in GoDaddy DNS settings');
            console.log('5. Wait 5-30 minutes for DNS propagation');
            console.log('6. Click "Verify" in Resend');
            console.log('7. Run this test again!');
        } else {
            console.error('❌ Error:', error.message);
        }
    }
}

// Run the test
testZmartyMeEmail();