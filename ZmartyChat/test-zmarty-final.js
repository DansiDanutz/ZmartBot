// Final test for zmarty.me email setup
import nodemailer from 'nodemailer';

async function testZmartyEmail() {
    console.log('🚀 Testing zmarty.me email configuration...\n');

    const transporter = nodemailer.createTransport({
        host: 'smtp.resend.com',
        port: 587,
        secure: false,
        auth: {
            user: 'resend',
            pass: 're_FbA39H6g_L2uZQktnoGQgMQZMcDc3xgWg'
        }
    });

    try {
        // Test connection
        await transporter.verify();
        console.log('✅ SMTP connection successful!\n');

        // Send test email
        console.log('📧 Sending test email to dansidanutz@yahoo.com...');

        const info = await transporter.sendMail({
            from: '"Zmarty" <noreply@zmarty.me>',
            to: 'dansidanutz@yahoo.com',
            subject: '✅ Zmarty.me Email Configuration Successful!',
            html: `
                <div style="font-family: system-ui; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #059669;">🎉 Success!</h2>
                    <p>Your <strong>zmarty.me</strong> domain is now fully configured and working!</p>

                    <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0;">✅ Configuration Complete:</h3>
                        <ul>
                            <li>Domain: zmarty.me</li>
                            <li>Sender: noreply@zmarty.me</li>
                            <li>Provider: Resend</li>
                            <li>Status: Verified & Active</li>
                        </ul>
                    </div>

                    <p><strong>Supabase is now configured</strong> to send all authentication emails from your custom domain!</p>

                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        Powered by Resend • zmarty.me
                    </p>
                </div>
            `
        });

        console.log('\n✅ EMAIL SENT SUCCESSFULLY!');
        console.log('📬 Message ID:', info.messageId);
        console.log('📧 Check your inbox at dansidanutz@yahoo.com');
        console.log('\n🎉 COMPLETE! Your email system is fully operational!');

    } catch (error) {
        console.error('\n❌ Error:', error.message);

        if (error.responseCode === 450) {
            console.log('\n⚠️  The domain might not be fully verified yet.');
            console.log('   Try again in a few minutes or check Resend dashboard.');
        }
    }
}

testZmartyEmail();