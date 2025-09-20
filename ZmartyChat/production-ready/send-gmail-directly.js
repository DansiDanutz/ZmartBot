// Send email directly using Gmail SMTP with Nodemailer
// This bypasses Supabase and sends directly from your Gmail

import nodemailer from 'nodemailer';

// Gmail SMTP configuration
const GMAIL_USER = 'zmarttradingbot2025@gmail.com';
const GMAIL_APP_PASSWORD = 'czxekqaeqpcmpgfz'; // Your Gmail App Password
const RECIPIENT_EMAIL = 'semebitcoin@gmail.com'; // Where to send the confirmation

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

// Email template
const emailTemplate = `
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4d94ff;
            padding-bottom: 10px;
        }
        .button {
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(135deg, #0066ff, #4d94ff);
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to ZmartyChat! 🎉</h1>

        <p>Hi there!</p>

        <p>Thank you for registering with ZmartyChat. Please confirm your email address by clicking the button below:</p>

        <a href="https://memoproapp.netlify.app/dashboard.html?verified=true" class="button">
            ✅ Confirm Email Address
        </a>

        <p>Or copy this link:</p>
        <p style="background: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all;">
            https://memoproapp.netlify.app/dashboard.html?verified=true
        </p>

        <p>This link will expire in 24 hours.</p>

        <div class="footer">
            <p>© 2025 ZmartyChat. All rights reserved.</p>
            <p>If you didn't create an account, please ignore this email.</p>
        </div>
    </div>
</body>
</html>
`;

async function sendConfirmationEmail() {
    console.log('📧 Sending confirmation email to:', RECIPIENT_EMAIL);

    if (GMAIL_APP_PASSWORD === 'YOUR_APP_PASSWORD_HERE') {
        console.error('\n❌ ERROR: You need to set up Gmail App Password first!\n');
        console.log('📋 HOW TO GET GMAIL APP PASSWORD:\n');
        console.log('1. Go to: https://myaccount.google.com/security');
        console.log('2. Enable 2-factor authentication if not already enabled');
        console.log('3. Search for "App passwords" or go to:');
        console.log('   https://myaccount.google.com/apppasswords');
        console.log('4. Create a new app password for "Mail"');
        console.log('5. Copy the 16-character password (remove spaces)');
        console.log('6. Replace YOUR_APP_PASSWORD_HERE in this file\n');
        return;
    }

    try {
        // Send email
        const info = await transporter.sendMail({
            from: `"ZmartyChat" <${GMAIL_USER}>`,
            to: RECIPIENT_EMAIL,
            subject: '✅ Confirm your email - ZmartyChat',
            html: emailTemplate
        });

        console.log('\n✅ SUCCESS! Email sent!');
        console.log('📬 Message ID:', info.messageId);
        console.log('📧 Check your inbox at:', RECIPIENT_EMAIL);
        console.log('\n🔍 If not in inbox, check SPAM folder');

    } catch (error) {
        console.error('\n❌ Error sending email:', error.message);

        if (error.message.includes('Invalid login')) {
            console.log('\n📋 FIX: You need an App Password, not your regular Gmail password');
            console.log('   Follow the instructions above to get an App Password');
        }
    }
}

// Install nodemailer first
console.log('Installing nodemailer...');
import { execSync } from 'child_process';
try {
    execSync('npm install nodemailer', { stdio: 'inherit' });
    console.log('✅ Nodemailer installed\n');
} catch (e) {
    console.log('Nodemailer already installed\n');
}

// Send the email
sendConfirmationEmail();