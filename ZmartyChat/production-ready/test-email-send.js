// Test email sending to semebitcoin@gmail.com
import nodemailer from 'nodemailer';

// Gmail SMTP configuration
const GMAIL_USER = 'zmarttradingbot2025@gmail.com';
const GMAIL_APP_PASSWORD = 'czxekqaeqpcmpgfz';
const RECIPIENT_EMAIL = 'semebitcoin@gmail.com';

// Create transporter
const transporter = nodemailer.createTransport({
    service: 'gmail',
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: {
        user: GMAIL_USER,
        pass: GMAIL_APP_PASSWORD
    }
});

// ZmartyChat verification email template
const emailTemplate = `
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f8fafc;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #0066ff;
            margin-bottom: 10px;
        }
        h1 {
            color: #1a202c;
            font-size: 24px;
            margin-bottom: 20px;
            text-align: center;
        }
        .button {
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #0066ff, #4d94ff);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: 600;
            font-size: 16px;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }
        .link-box {
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            word-break: break-all;
            font-family: monospace;
            font-size: 14px;
            color: #4a5568;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            color: #718096;
            font-size: 14px;
        }
        .features {
            margin: 30px 0;
            text-align: center;
        }
        .feature {
            display: inline-block;
            margin: 0 15px;
            color: #4d94ff;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🧠 ZmartyChat</div>
            <p style="color: #718096; margin: 0;">Your AI Trading Companion</p>
        </div>

        <h1>Welcome to ZmartyChat! 🎉</h1>

        <p>Hi there!</p>

        <p>Thank you for joining ZmartyChat, your intelligent crypto trading companion. We're excited to help you navigate the crypto markets with confidence.</p>

        <p><strong>Please verify your email address to get started:</strong></p>

        <a href="https://memoproapp.netlify.app?verified=true" class="button">
            ✅ Verify Email Address
        </a>

        <p>Or copy and paste this link into your browser:</p>
        <div class="link-box">
            https://memoproapp.netlify.app?verified=true
        </div>

        <div class="features">
            <div class="feature">🤖 Multi-AI Analysis</div>
            <div class="feature">📊 Portfolio Tracking</div>
            <div class="feature">⚡ Real-time Alerts</div>
            <div class="feature">🎯 Smart Insights</div>
        </div>

        <p>Once verified, you'll have access to:</p>
        <ul>
            <li>AI-powered market analysis from Claude, GPT-4, and Gemini</li>
            <li>Real-time portfolio tracking across 100+ exchanges</li>
            <li>Smart trading alerts and notifications</li>
            <li>Personalized investment insights</li>
        </ul>

        <p><strong>This verification link expires in 24 hours.</strong></p>

        <div class="footer">
            <p>© 2025 ZmartyChat. All rights reserved.</p>
            <p>If you didn't create an account, please ignore this email.</p>
            <p style="margin-top: 15px;">
                <a href="https://memoproapp.netlify.app" style="color: #4d94ff;">Visit ZmartyChat</a> •
                <a href="mailto:support@zmartychat.com" style="color: #4d94ff;">Support</a>
            </p>
        </div>
    </div>
</body>
</html>
`;

async function sendTestEmail() {
    console.log('📧 Sending test verification email to:', RECIPIENT_EMAIL);
    console.log('📤 From:', GMAIL_USER);

    try {
        // Send email
        const info = await transporter.sendMail({
            from: `"ZmartyChat" <${GMAIL_USER}>`,
            to: RECIPIENT_EMAIL,
            subject: '✅ Verify your email - Welcome to ZmartyChat!',
            html: emailTemplate
        });

        console.log('\n✅ SUCCESS! Email sent!');
        console.log('📬 Message ID:', info.messageId);
        console.log('📧 Check your inbox at:', RECIPIENT_EMAIL);
        console.log('\n🔍 If not in inbox, check SPAM/PROMOTIONS folder');
        console.log('📱 Email client: Gmail, Yahoo, Outlook, etc.');

    } catch (error) {
        console.error('\n❌ Error sending email:', error.message);

        if (error.message.includes('Invalid login')) {
            console.log('\n📋 ISSUE: Gmail App Password may have expired');
            console.log('   Solution: Generate new App Password in Gmail settings');
        }
    }
}

// Send the test email
sendTestEmail();