# Supabase Email Template Configuration for Zmarty

To configure the verification email with Zmarty branding, follow these steps:

## 1. Access Supabase Dashboard

1. Go to https://app.supabase.com/
2. Open your project: `asjtxrmftmutcsnqgidy`
3. Navigate to Authentication > Email Templates

## 2. Configure Email Templates

### Confirm signup template:

**Subject:** `Verification Email`

**Body:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Zmarty Account</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #0066ff;
            margin-bottom: 10px;
        }
        .verification-code {
            background: #f8f9fa;
            border: 2px solid #0066ff;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin: 30px 0;
        }
        .code {
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 4px;
            color: #0066ff;
            font-family: 'Courier New', monospace;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🚀 Zmarty</div>
            <h1>Welcome to Zmarty!</h1>
            <p>We're excited to have you join our crypto trading community.</p>
        </div>

        <p>Hello there! 👋</p>

        <p>You're just one step away from completing your Zmarty account setup. Please enter the verification code below in your registration form:</p>

        <div class="verification-code">
            <div style="font-size: 16px; margin-bottom: 10px; color: #666;">Your verification code is:</div>
            <div class="code">{{ .Token }}</div>
            <div style="font-size: 14px; margin-top: 10px; color: #666;">This code will expire in 24 hours</div>
        </div>

        <p>Once verified, you'll have access to:</p>
        <ul>
            <li>🤖 AI-powered crypto insights</li>
            <li>📊 Real-time market analysis</li>
            <li>💹 Advanced trading signals</li>
            <li>🔔 Smart alerts and notifications</li>
        </ul>

        <p>If you didn't create a Zmarty account, you can safely ignore this email.</p>

        <div class="footer">
            <p>Happy trading! 🚀<br>
            The Zmarty Team</p>

            <p style="font-size: 12px; color: #999;">
                This email was sent from Zmarty App<br>
                If you have questions, contact us at support@zmarty.com
            </p>
        </div>
    </div>
</body>
</html>
```

## 3. Configuration Settings

1. **Site URL:** Set to your domain (e.g., `https://yourdomain.com`)
2. **Redirect URLs:** Add `https://yourdomain.com/ZmartyUserApp/index.html`
3. **Email Rate Limit:** Adjust as needed (default: 3 emails per hour)

## 4. SMTP Configuration (REQUIRED FOR PRODUCTION)

⚠️ **IMPORTANT**: The built-in Supabase email service has rate limits and is not suitable for production.

### Recommended SMTP Providers:

#### A. **Resend (Recommended - Easy Setup)**
1. Sign up at https://resend.com
2. Get your API key
3. In Supabase Dashboard:
   - Go to Authentication > Settings > SMTP Settings
   - Enable "Enable custom SMTP"
   - **SMTP Host:** smtp.resend.com
   - **SMTP Port:** 587
   - **SMTP User:** resend
   - **SMTP Pass:** Your Resend API key
   - **Sender Name:** Zmarty App
   - **Sender Email:** noreply@yourdomain.com

#### B. **SendGrid**
1. Sign up at https://sendgrid.com
2. Create API key with "Mail Send" permissions
3. In Supabase Dashboard:
   - **SMTP Host:** smtp.sendgrid.net
   - **SMTP Port:** 587
   - **SMTP User:** apikey
   - **SMTP Pass:** Your SendGrid API key
   - **Sender Name:** Zmarty App
   - **Sender Email:** noreply@yourdomain.com

#### C. **Mailgun**
1. Sign up at https://mailgun.com
2. Get SMTP credentials
3. In Supabase Dashboard:
   - **SMTP Host:** smtp.mailgun.org
   - **SMTP Port:** 587
   - **SMTP User:** Your Mailgun SMTP username
   - **SMTP Pass:** Your Mailgun SMTP password
   - **Sender Name:** Zmarty App
   - **Sender Email:** noreply@yourdomain.com

### Quick Setup Steps:
1. Choose a provider (Resend is easiest)
2. Sign up and get credentials
3. Go to Supabase Dashboard > Authentication > Settings
4. Scroll to "SMTP Settings"
5. Enable "Enable custom SMTP"
6. Enter your provider's settings
7. Test with a real email address

### Domain Setup (Important):
- Add SPF record: `v=spf1 include:_spf.resend.com ~all`
- Add DKIM records (provided by your email service)
- Set up DMARC policy for better deliverability

## 5. Testing

1. Test the registration flow
2. Check email delivery
3. Verify the email template renders correctly
4. Test the verification code process

## Notes

- The `{{ .Token }}` placeholder will be replaced with the actual 6-digit verification code
- The template is fully responsive and works on all email clients
- The design matches your Zmarty branding with blue (#0066ff) accent colors
- The verification code is prominently displayed and easy to read