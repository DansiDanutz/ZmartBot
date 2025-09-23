# 🔐 Zmarty Platform - COMPLETE System Specifications & Credentials

## 🎯 Executive Summary

**Platform:** Zmarty - AI-Powered Cryptocurrency Trading Assistant
**Component:** Complete Onboarding System with Authentication
**Environment:** Production
**URL:** https://zmarty.me
**Status:** Production Ready
**Version:** 2.0.0

---

## 📊 Supabase Complete Configuration

### Project Credentials
```yaml
Project Name: Zmarty Production
Project URL: https://xhskmqsgtdhehzlvtuns.supabase.co
Project ID: xhskmqsgtdhehzlvtuns
Project Ref: xhskmqsgtdhehzlvtuns
Region: US East 1 (N. Virginia)
Organization: Zmarty

Database Host: db.xhskmqsgtdhehzlvtuns.supabase.co
Database Port: 5432
Database Name: postgres
Database User: postgres
Database Password: [Check Supabase Dashboard]

API URL: https://xhskmqsgtdhehzlvtuns.supabase.co
API Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhoc2ttcXNndGRoZWh6bHZ0dW5zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNDkzNTQsImV4cCI6MjA3MzcyNTM1NH0.ULAf9vNHS4nasSnv9UOKS2MCKsSxcMtV3C-R7Wm6qMw
API Service Key: [SENSITIVE - Check Dashboard Settings > API]

JWT Secret: [SENSITIVE - Check Dashboard Settings > API]
```

### Supabase Dashboard URLs
```
Main Dashboard: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns
Authentication: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/auth/users
Database: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/database/tables
Storage: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/storage/buckets
Settings: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/general
```

---

## 🔑 OAuth Provider Configurations

### Google OAuth 2.0

#### Google Cloud Console Setup
```yaml
Console URL: https://console.cloud.google.com
Project Name: Zmarty Trading Platform
Project ID: zmarty-trading-[unique-id]
```

#### OAuth 2.0 Client Configuration
```javascript
Client ID: [Get from Google Cloud Console]
Client Secret: [Get from Google Cloud Console]
Authorized JavaScript Origins:
  - https://zmarty.me
  - https://www.zmarty.me
  - http://localhost:3008 (development)

Authorized Redirect URIs:
  - https://xhskmqsgtdhehzlvtuns.supabase.co/auth/v1/callback
  - https://zmarty.me/auth/callback
  - http://localhost:3008/auth/callback (development)

Scopes Required:
  - email
  - profile
  - openid
```

#### Google Setup Steps:
1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth Client ID
5. Application Type: Web application
6. Add authorized origins and redirect URIs
7. Copy Client ID and Secret to Supabase

### Facebook OAuth

#### Facebook Developer Console
```yaml
Developer URL: https://developers.facebook.com
App Name: Zmarty Trading
App ID: [Get from Facebook Developer Console]
App Secret: [Get from Facebook Developer Console]
App Type: Business
```

#### Facebook App Configuration
```javascript
App Domains:
  - zmarty.me
  - supabase.co

Valid OAuth Redirect URIs:
  - https://xhskmqsgtdhehzlvtuns.supabase.co/auth/v1/callback
  - https://zmarty.me/auth/callback

Settings:
  - Client OAuth Login: Yes
  - Web OAuth Login: Yes
  - Enforce HTTPS: Yes
  - Use Strict Mode: Yes
  - Require App Secret: Yes

Permissions/Scopes:
  - email (default)
  - public_profile (default)
```

#### Facebook Setup Steps:
1. Go to https://developers.facebook.com
2. Create App → Business Type
3. Add Facebook Login product
4. Settings → Basic → Add Platform → Website
5. Site URL: https://zmarty.me
6. Facebook Login → Settings → Add redirect URIs
7. Copy App ID and Secret to Supabase

### Apple Sign In

#### Apple Developer Configuration
```yaml
Developer URL: https://developer.apple.com
Team ID: [Get from Apple Developer Account]
Service ID: com.zmarty.web
Key ID: [Get from Apple Developer Account]
```

#### Apple Service Configuration
```javascript
Service ID: com.zmarty.web
Name: Zmarty Trading
Primary App ID: com.zmarty.app

Domains and Subdomains:
  - zmarty.me
  - xhskmqsgtdhehzlvtuns.supabase.co

Return URLs:
  - https://xhskmqsgtdhehzlvtuns.supabase.co/auth/v1/callback
  - https://zmarty.me/auth/callback

Private Key: [Download .p8 file from Apple Developer]
```

#### Apple Setup Steps:
1. Go to https://developer.apple.com
2. Certificates, IDs & Profiles → Identifiers
3. Create Service ID (com.zmarty.web)
4. Enable Sign In with Apple
5. Configure domains and return URLs
6. Create Private Key for Sign In with Apple
7. Upload .p8 file to Supabase

---

## 📧 Email Configuration & Templates

### SMTP Configuration (Supabase)

#### Email Provider: Resend
```yaml
Provider: Resend
API Key: [Get from https://resend.com]
From Email: noreply@zmarty.me
From Name: Zmarty
Reply To: support@zmarty.me
```

#### Alternative: Custom SMTP
```yaml
SMTP Host: smtp.gmail.com (example)
SMTP Port: 587
SMTP User: noreply@zmarty.me
SMTP Password: [App-specific password]
Secure: TLS/STARTTLS
```

### Email Templates

#### 1. Confirmation Email (OTP)
```html
Subject: Your Zmarty Verification Code: {{ .Token }}

<html>
<body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
    <h1 style="color: #667eea; text-align: center;">Welcome to Zmarty! 🚀</h1>

    <p style="font-size: 16px; color: #333;">
      Your verification code is:
    </p>

    <div style="background: #667eea; color: white; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 10px; margin: 20px 0; letter-spacing: 5px;">
      {{ .Token }}
    </div>

    <p style="font-size: 14px; color: #666;">
      This code will expire in 10 minutes. If you didn't request this, please ignore this email.
    </p>

    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

    <p style="font-size: 12px; color: #999; text-align: center;">
      © 2025 Zmarty. All rights reserved.<br>
      AI-Powered Crypto Trading Made Simple
    </p>
  </div>
</body>
</html>
```

#### 2. Password Reset Email
```html
Subject: Reset Your Zmarty Password

<html>
<body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
    <h1 style="color: #667eea; text-align: center;">Password Reset Request</h1>

    <p style="font-size: 16px; color: #333;">
      Hi there,<br><br>
      We received a request to reset your password. Click the button below to create a new password:
    </p>

    <div style="text-align: center; margin: 30px 0;">
      <a href="{{ .ConfirmationURL }}" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block;">
        Reset Password
      </a>
    </div>

    <p style="font-size: 14px; color: #666;">
      Or copy this link: {{ .ConfirmationURL }}
    </p>

    <p style="font-size: 14px; color: #666;">
      This link will expire in 1 hour. If you didn't request this, please ignore this email.
    </p>

    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

    <p style="font-size: 12px; color: #999; text-align: center;">
      © 2025 Zmarty | support@zmarty.me
    </p>
  </div>
</body>
</html>
```

#### 3. Magic Link Email
```html
Subject: Your Zmarty Login Link

<html>
<body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
    <h1 style="color: #667eea; text-align: center;">Quick Login to Zmarty</h1>

    <p style="font-size: 16px; color: #333;">
      Click the button below to instantly log in to your account:
    </p>

    <div style="text-align: center; margin: 30px 0;">
      <a href="{{ .ConfirmationURL }}" style="background: #667eea; color: white; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block;">
        Log In to Zmarty
      </a>
    </div>

    <p style="font-size: 14px; color: #666;">
      This link expires in 1 hour and can only be used once.
    </p>
  </div>
</body>
</html>
```

---

## 🌐 Domain & DNS Configuration

### Primary Domain
```yaml
Domain: zmarty.me
Registrar: [Your Registrar]
DNS Provider: Netlify DNS
SSL: Automatic (Let's Encrypt)
```

### DNS Records
```
Type    Name    Value                           TTL
A       @       75.2.60.5                       3600
CNAME   www     zmarty.netlify.app              3600
MX      @       mx1.privateemail.com            3600 (Priority: 10)
MX      @       mx2.privateemail.com            3600 (Priority: 20)
TXT     @       v=spf1 include:spf.privateemail.com ~all   3600
TXT     _dmarc  v=DMARC1; p=none; rua=mailto:dmarc@zmarty.me   3600
```

### Email Configuration
```yaml
Email Provider: PrivateEmail / Namecheap
Email Addresses:
  - support@zmarty.me
  - noreply@zmarty.me
  - admin@zmarty.me
  - hello@zmarty.me
```

---

## 🚀 Netlify Configuration

### Deployment Settings
```yaml
Team: Zmarty Team
Site Name: zmarty
Site ID: [Check Netlify Dashboard]
API ID: [Check Netlify Dashboard]
```

### Build & Deploy
```yaml
Repository: [GitHub/GitLab URL]
Branch: main
Build Command: # No build required (vanilla JS)
Publish Directory: ProductionApp
Production Domain: https://zmarty.me
Deploy Previews: Enabled
Branch Deploys: Disabled
```

### Environment Variables
```bash
SUPABASE_URL=https://xhskmqsgtdhehzlvtuns.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
RESEND_API_KEY=[Your Resend API Key]
```

### Headers (_headers file)
```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self' https://*.supabase.co; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline';
```

### Redirects (_redirects file)
```
# Auth callback
/auth/callback  /auth/callback/index.html  200

# SPA fallback
/*    /index.html    200

# Force HTTPS
http://zmarty.me/*  https://zmarty.me/:splat  301!
http://www.zmarty.me/*  https://zmarty.me/:splat  301!
https://www.zmarty.me/*  https://zmarty.me/:splat  301!
```

---

## 📱 Resend Email Service Configuration

### Account Details
```yaml
Service: Resend
URL: https://resend.com
Account Email: admin@zmarty.me
```

### API Configuration
```javascript
const resend = new Resend('re_[your_api_key]');

// Sending configuration
{
  from: 'Zmarty <noreply@zmarty.me>',
  to: ['user@example.com'],
  subject: 'Welcome to Zmarty',
  html: '<html>...</html>',
  reply_to: 'support@zmarty.me',
  headers: {
    'X-Entity-Ref-ID': '123456789'
  }
}
```

### Domain Verification (Resend)
```
Type    Name              Value
TXT     @                 resend-verification=[code]
TXT     resend._domainkey [DKIM value from Resend]
CNAME   resend._domainkey.zmarty.me   [Value from Resend]
```

---

## 🔒 Security & Compliance

### API Key Security
```javascript
// Client-side (PUBLIC - Safe to expose)
const SUPABASE_URL = 'https://xhskmqsgtdhehzlvtuns.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

// Server-side only (NEVER expose)
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const RESEND_API_KEY = process.env.RESEND_API_KEY;
const JWT_SECRET = process.env.JWT_SECRET;
```

### Row Level Security (RLS) Policies
```sql
-- Enable RLS on profiles table
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Users can only read their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
FOR SELECT USING (auth.uid() = id);

-- Users can only update their own profile
CREATE POLICY "Users can update own profile" ON public.profiles
FOR UPDATE USING (auth.uid() = id);

-- Users can insert their own profile
CREATE POLICY "Users can insert own profile" ON public.profiles
FOR INSERT WITH CHECK (auth.uid() = id);
```

### GDPR Compliance
```yaml
Data Controller: Zmarty Inc.
Data Protection Officer: dpo@zmarty.me
Privacy Policy URL: https://zmarty.me/privacy
Terms of Service URL: https://zmarty.me/terms
Cookie Policy URL: https://zmarty.me/cookies

User Rights Implemented:
  - Right to Access (Data Export)
  - Right to Rectification (Profile Edit)
  - Right to Erasure (Account Delete)
  - Right to Data Portability (JSON Export)
  - Right to Restrict Processing (Pause Account)
```

---

## 📊 Analytics & Tracking

### Google Analytics 4
```javascript
// GA4 Configuration
const GA_MEASUREMENT_ID = 'G-XXXXXXXXXX';

// Initialize
gtag('config', GA_MEASUREMENT_ID, {
  page_path: window.location.pathname,
  cookie_domain: 'zmarty.me',
  cookie_flags: 'SameSite=None;Secure'
});
```

### Custom Events Tracking
```javascript
// Onboarding Funnel Events
trackEvent('onboarding_start', {
  entry_point: 'homepage',
  device_type: 'mobile',
  referrer: document.referrer
});

trackEvent('auth_method_selected', {
  method: 'google', // google, facebook, apple, email
  slide_number: 1
});

trackEvent('tier_selected', {
  tier: 'pro',
  price: 29,
  currency: 'USD'
});

trackEvent('onboarding_complete', {
  duration_seconds: 120,
  selected_tier: 'pro',
  auth_method: 'google'
});
```

### Conversion Tracking
```javascript
// Google Ads Conversion
gtag('event', 'conversion', {
  'send_to': 'AW-XXXXXXXXXX/XXXXX',
  'value': 29.00,
  'currency': 'USD'
});

// Facebook Pixel
fbq('track', 'CompleteRegistration', {
  value: 29.00,
  currency: 'USD',
  content_name: 'Pro Tier'
});
```

---

## 🛠️ Development & Testing

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/zmarty/onboarding.git
cd ZmartyChat/ProductionApp

# Install dependencies (if any)
# No npm install needed - vanilla JS

# Start local server
python3 -m http.server 3008
# OR
npx http-server -p 3008
# OR
php -S localhost:3008

# Access at
http://localhost:3008
```

### Testing Accounts
```yaml
Test Email: test@zmarty.me
Test Password: Test123!@#
Test OTP: 123456 (development mode only)

OAuth Test Accounts:
  Google: test.zmarty@gmail.com
  Facebook: test_user_zmarty@tfbnw.net
```

### Debug Mode
```javascript
// Enable debug mode
localStorage.setItem('debug', 'true');

// Or via URL
https://zmarty.me?debug=true

// Debug output in console
if (localStorage.getItem('debug')) {
  console.log('Debug: Auth state', authState);
  console.log('Debug: API call', apiEndpoint);
}
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Deploy to Netlify

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Deploy to Netlify
        uses: netlify/actions/cli@master
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
        with:
          args: deploy --dir=ProductionApp --prod
```

### Pre-deployment Checklist
```markdown
- [ ] All tests passing
- [ ] OAuth providers configured
- [ ] Email templates updated
- [ ] Environment variables set
- [ ] DNS records configured
- [ ] SSL certificate active
- [ ] RLS policies enabled
- [ ] Analytics configured
- [ ] Error tracking setup
- [ ] Mobile responsive tested
```

---

## 📞 Support & Maintenance

### Contact Information
```yaml
Technical Support: support@zmarty.me
Sales: sales@zmarty.me
General Inquiries: hello@zmarty.me
Bug Reports: bugs@zmarty.me
Security: security@zmarty.me

Phone: +1 (XXX) XXX-XXXX
Address: [Company Address]
```

### Monitoring & Alerts
```yaml
Uptime Monitoring: UptimeRobot / Pingdom
Error Tracking: Sentry
Log Management: Logtail / Papertrail
Performance: Google PageSpeed / GTmetrix
Security: Snyk / OWASP ZAP
```

### SLA & Support Tiers
```yaml
Free Tier:
  - Community support
  - 72-hour response time

Pro Tier ($29/month):
  - Email support
  - 24-hour response time
  - Priority bug fixes

Premium Tier ($99/month):
  - Priority support
  - 4-hour response time
  - Dedicated account manager
  - Phone support
```

---

## 📈 Business Metrics & KPIs

### Key Metrics to Track
```yaml
Acquisition:
  - Visitor to Sign-up Rate
  - OAuth vs Email Registration Split
  - Channel Attribution

Activation:
  - Email Verification Rate
  - Time to First Action
  - Onboarding Completion Rate

Revenue:
  - Free to Paid Conversion
  - Average Revenue Per User (ARPU)
  - Customer Lifetime Value (CLV)

Retention:
  - Daily/Monthly Active Users
  - Churn Rate
  - Feature Adoption Rate
```

### Success Metrics
```yaml
Target Onboarding Completion: >60%
Target Email Verification: >80%
Target Free to Paid: >5%
Target Monthly Churn: <10%
Target NPS Score: >50
```

---

## 📄 Legal & Compliance Documents

### Required Documents
1. **Privacy Policy** - https://zmarty.me/privacy
2. **Terms of Service** - https://zmarty.me/terms
3. **Cookie Policy** - https://zmarty.me/cookies
4. **GDPR Compliance** - https://zmarty.me/gdpr
5. **CCPA Compliance** - https://zmarty.me/ccpa
6. **Acceptable Use Policy** - https://zmarty.me/aup
7. **SLA Agreement** - https://zmarty.me/sla

---

## 🔄 Version History

```yaml
v2.0.0 (Current):
  - Mobile optimizations
  - Keyboard avoidance
  - Safe area support
  - Performance improvements

v1.5.0:
  - Added OAuth providers
  - Email templates
  - Analytics integration

v1.0.0:
  - Initial release
  - Basic authentication
  - Email verification
```

---

## 🚨 Emergency Procedures

### Service Outage
1. Check Netlify Status: https://www.netlifystatus.com
2. Check Supabase Status: https://status.supabase.com
3. Check DNS propagation
4. Rollback if needed via Netlify

### Security Breach
1. Revoke all API keys
2. Reset JWT secret
3. Force password reset for all users
4. Notify users within 72 hours
5. Document incident

### Data Recovery
```bash
# Supabase backup
pg_dump postgres://postgres:[password]@db.xhskmqsgtdhehzlvtuns.supabase.co:5432/postgres > backup.sql

# Restore
psql postgres://postgres:[password]@db.xhskmqsgtdhehzlvtuns.supabase.co:5432/postgres < backup.sql
```

---

**Document Classification:** CONFIDENTIAL
**Last Updated:** January 21, 2025
**Next Review:** February 21, 2025
**Owner:** Zmarty Development Team
**Total Pages:** 25+

--- END OF COMPLETE SPECIFICATIONS ---