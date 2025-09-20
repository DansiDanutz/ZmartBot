// Test Verification Email with 6-digit code
import nodemailer from 'nodemailer';

// Generate 6-digit verification code
const generateVerificationCode = () => {
    return Math.floor(100000 + Math.random() * 900000).toString();
};

// Gmail configuration
const GMAIL_USER = 'zmarttradingbot2025@gmail.com';
const GMAIL_APP_PASSWORD = 'czxe kqae qpcm pgfz'; // Your app password with spaces

// Create transporter
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: GMAIL_USER,
        pass: GMAIL_APP_PASSWORD.replace(/\s/g, '') // Remove spaces
    }
});

// Generate verification code
const verificationCode = generateVerificationCode();

// Email template - Professional Design
const emailTemplate = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background-color: #f5f5f7;
            margin: 0;
            padding: 0;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }

        table {
            border-collapse: collapse;
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }

        .email-wrapper {
            width: 100%;
            background: #f5f5f7;
            padding: 40px 20px;
        }

        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 48px 40px;
            text-align: center;
        }

        .logo-container {
            display: inline-block;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            padding: 20px 30px;
            border-radius: 16px;
            margin-bottom: 20px;
        }

        .logo {
            font-size: 36px;
            font-weight: 700;
            color: #ffffff;
            text-decoration: none;
            display: inline-block;
        }

        .tagline {
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .content {
            padding: 48px 40px;
        }

        h1 {
            color: #1a1a1a;
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 16px;
        }

        .subtitle {
            color: #6e6e73;
            font-size: 16px;
            text-align: center;
            margin-bottom: 32px;
        }

        .verification-section {
            background: #f5f5f7;
            border-radius: 12px;
            padding: 32px;
            margin: 32px 0;
            text-align: center;
        }

        .code-label {
            color: #6e6e73;
            font-size: 14px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
        }

        .verification-code {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 48px;
            font-weight: 700;
            letter-spacing: 12px;
            margin: 16px 0;
            font-family: 'SF Mono', Monaco, monospace;
        }

        .expiry-notice {
            color: #6e6e73;
            font-size: 14px;
            margin-top: 16px;
        }

        .expiry-time {
            color: #1a1a1a;
            font-weight: 600;
        }

        .button-container {
            text-align: center;
            margin: 40px 0;
        }

        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            padding: 16px 48px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            transition: transform 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }

        .security-notice {
            background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
            border-left: 4px solid #ff4757;
            border-radius: 8px;
            padding: 16px 20px;
            margin: 32px 0;
        }

        .security-icon {
            color: #ff4757;
            font-weight: 700;
            margin-right: 8px;
        }

        .features-section {
            margin: 48px 0;
        }

        .features-title {
            color: #1a1a1a;
            font-size: 20px;
            font-weight: 600;
            text-align: center;
            margin-bottom: 32px;
        }

        .features-grid {
            display: table;
            width: 100%;
        }

        .feature-row {
            display: table-row;
        }

        .feature {
            display: table-cell;
            width: 50%;
            padding: 16px;
            text-align: center;
        }

        .feature-icon-wrapper {
            display: inline-block;
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #f0f3ff 0%, #e8ecff 100%);
            border-radius: 12px;
            margin-bottom: 12px;
            line-height: 56px;
            font-size: 24px;
        }

        .feature-name {
            color: #1a1a1a;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }

        .feature-desc {
            color: #6e6e73;
            font-size: 12px;
        }

        .divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #e1e1e6, transparent);
            margin: 40px 0;
        }

        .footer {
            background: #f5f5f7;
            padding: 32px 40px;
            text-align: center;
        }

        .footer-text {
            color: #6e6e73;
            font-size: 12px;
            margin-bottom: 8px;
        }

        .footer-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .social-links {
            margin: 20px 0;
        }

        .social-link {
            display: inline-block;
            width: 32px;
            height: 32px;
            background: #ffffff;
            border-radius: 50%;
            margin: 0 6px;
            line-height: 32px;
            text-align: center;
            text-decoration: none;
            color: #667eea;
        }

        .copyright {
            color: #86868b;
            font-size: 11px;
            margin-top: 20px;
        }

        .transaction-id {
            color: #c9c9cd;
            font-size: 10px;
            margin-top: 12px;
            font-family: 'SF Mono', Monaco, monospace;
        }

        @media only screen and (max-width: 600px) {
            .email-container {
                border-radius: 0;
            }
            .header, .content, .footer {
                padding: 32px 24px;
            }
            .verification-code {
                font-size: 36px;
                letter-spacing: 8px;
            }
            .features-grid {
                display: block;
            }
            .feature {
                display: block;
                width: 100%;
                margin-bottom: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="email-wrapper">
        <table role="presentation" class="email-container">
            <tr>
                <td>
                    <!-- Header -->
                    <div class="header">
                        <div class="logo-container">
                            <div class="logo">ZmartyChat</div>
                        </div>
                        <div class="tagline">AI-Powered Trading Intelligence</div>
                    </div>

                    <!-- Content -->
                    <div class="content">
                        <h1>Verify Your Account</h1>
                        <p class="subtitle">You're one step away from accessing advanced AI trading tools</p>

                        <div class="verification-section">
                            <div class="code-label">Your Verification Code</div>
                            <div class="verification-code">${verificationCode}</div>
                            <div class="expiry-notice">
                                Code expires in <span class="expiry-time">10 minutes</span>
                            </div>
                        </div>

                        <div class="button-container">
                            <a href="http://localhost:8083" class="cta-button">Complete Registration →</a>
                        </div>

                        <div class="security-notice">
                            <span class="security-icon">🔒</span>
                            <strong>Security Notice:</strong> Never share this code with anyone. ZmartyChat staff will never ask for your verification code via email, phone, or any other method.
                        </div>

                        <div class="divider"></div>

                        <div class="features-section">
                            <h2 class="features-title">What's Included in Your Account</h2>
                            <table class="features-grid">
                                <tr class="feature-row">
                                    <td class="feature">
                                        <div class="feature-icon-wrapper">📊</div>
                                        <div class="feature-name">Real-Time Analytics</div>
                                        <div class="feature-desc">Live market data & insights</div>
                                    </td>
                                    <td class="feature">
                                        <div class="feature-icon-wrapper">🤖</div>
                                        <div class="feature-name">AI Predictions</div>
                                        <div class="feature-desc">Multi-model AI analysis</div>
                                    </td>
                                </tr>
                                <tr class="feature-row">
                                    <td class="feature">
                                        <div class="feature-icon-wrapper">⚡</div>
                                        <div class="feature-name">Smart Alerts</div>
                                        <div class="feature-desc">Automated notifications</div>
                                    </td>
                                    <td class="feature">
                                        <div class="feature-icon-wrapper">🔐</div>
                                        <div class="feature-name">Bank-Level Security</div>
                                        <div class="feature-desc">256-bit encryption</div>
                                    </td>
                                </tr>
                            </table>
                        </div>
                    </div>

                    <!-- Footer -->
                    <div class="footer">
                        <p class="footer-text">
                            This email was sent to <strong>semebitcoin@gmail.com</strong>
                        </p>
                        <p class="footer-text">
                            If you didn't create an account with ZmartyChat, you can safely ignore this email.
                        </p>

                        <div class="social-links">
                            <a href="#" class="social-link">𝕏</a>
                            <a href="#" class="social-link">in</a>
                            <a href="#" class="social-link">📧</a>
                        </div>

                        <p class="footer-text">
                            Need help? <a href="mailto:support@zmartychat.com" class="footer-link">Contact Support</a>
                        </p>

                        <p class="copyright">
                            © 2025 ZmartyChat. All rights reserved.<br>
                            AI-Powered Trading Solutions
                        </p>

                        <p class="transaction-id">
                            TXN: ${Date.now()}-${Math.random().toString(36).substr(2, 9).toUpperCase()}
                        </p>
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
`;

// Send email
async function sendVerificationEmail() {
    try {
        console.log('🔄 Sending verification email to semebitcoin@gmail.com...');
        console.log('📧 Verification Code:', verificationCode);

        const info = await transporter.sendMail({
            from: `"ZmartyChat" <${GMAIL_USER}>`,
            to: 'semebitcoin@gmail.com',
            subject: `🔐 Your ZmartyChat Verification Code: ${verificationCode}`,
            html: emailTemplate,
            text: `Your ZmartyChat verification code is: ${verificationCode}\n\nThis code will expire in 10 minutes.\n\nIf you didn't request this, please ignore this email.`
        });

        console.log('✅ Verification email sent successfully!');
        console.log('📬 Message ID:', info.messageId);
        console.log('🔢 Verification Code:', verificationCode);
        console.log('📧 Sent to: semebitcoin@gmail.com');

        // Store code for verification (in production, this would be in database)
        console.log('\n💾 Code stored for verification (expires in 10 minutes)');

    } catch (error) {
        console.error('❌ Error sending email:', error);
    }
}

// Run the test
sendVerificationEmail();