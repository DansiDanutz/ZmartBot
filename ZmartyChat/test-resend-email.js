// Test Resend email service
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

async function testResend() {
    console.log('Testing Resend SMTP connection...');

    try {
        // Verify connection
        await transporter.verify();
        console.log('✅ Resend SMTP connection successful!');

        // Send test email
        console.log('\nSending test email via Resend...');

        const info = await transporter.sendMail({
            from: '"ZmartyChat" <onboarding@resend.dev>',
            to: 'seme@kryptostack.com', // Resend requires sending to your account email or verified domain
            subject: 'Test Email from ZmartyChat via Resend',
            text: 'This test email confirms that Resend is working correctly with your Supabase project.',
            html: `
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #333;">🎉 Resend is Working!</h1>
                    <p style="font-size: 16px; line-height: 1.5;">
                        Great news! Your Resend email service is configured correctly.
                    </p>
                    <p style="font-size: 16px; line-height: 1.5;">
                        This means your ZmartyChat registration emails will now be delivered reliably.
                    </p>
                    <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <strong>Next Steps:</strong>
                        <ol>
                            <li>Update the SMTP settings in Supabase with these Resend credentials</li>
                            <li>Test user registration to receive verification emails</li>
                        </ol>
                    </div>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Sent via Resend SMTP | ZmartyChat Email System
                    </p>
                </div>
            `
        });

        console.log('✅ Email sent successfully via Resend!');
        console.log('Message ID:', info.messageId);
        console.log('Check your inbox at dansidanutz@yahoo.com');

    } catch (error) {
        console.error('❌ Resend Error:', error);
    }
}

testResend();