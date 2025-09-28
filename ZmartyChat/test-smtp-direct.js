// Test SMTP connection directly
import nodemailer from 'nodemailer';

const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false, // true for 465, false for other ports
    auth: {
        user: 'zmarttradingbot2025@gmail.com',
        pass: 'jbdr xaet ryzt fxmm' // App password you provided
    },
    debug: true, // Enable debug output
    logger: true // Log to console
});

async function testSMTP() {
    console.log('Testing SMTP connection...');

    try {
        // Verify connection
        await transporter.verify();
        console.log('✅ SMTP connection successful!');

        // Try sending a test email
        console.log('\nSending test email to dansidanutz@yahoo.com...');

        const info = await transporter.sendMail({
            from: '"ZmartyChat" <zmarttradingbot2025@gmail.com>',
            to: 'dansidanutz@yahoo.com',
            subject: 'Test Email from ZmartyChat',
            text: 'This is a test email to verify SMTP configuration.',
            html: `
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Test Email from ZmartyChat</h2>
                    <p>This is a test email to verify that the SMTP configuration is working correctly.</p>
                    <p>If you receive this email, it means the SMTP settings are properly configured.</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        Sent from ZmartyChat SMTP Test Script
                    </p>
                </div>
            `
        });

        console.log('✅ Email sent successfully!');
        console.log('Message ID:', info.messageId);
        console.log('Response:', info.response);

    } catch (error) {
        console.error('❌ SMTP Error:', error);
        console.error('Error details:', {
            code: error.code,
            command: error.command,
            response: error.response,
            responseCode: error.responseCode
        });
    }
}

testSMTP();