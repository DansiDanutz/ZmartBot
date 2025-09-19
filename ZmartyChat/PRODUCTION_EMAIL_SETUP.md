# 🚀 Production Email Setup for Zmarty

## ⚠️ URGENT: Configure SMTP for Production

The Supabase built-in email service has severe limitations:
- **Rate limits**: Only 3-4 emails per hour
- **Not reliable**: Emails may not be delivered
- **Not production-ready**: Meant only for development/testing

## 🎯 Quick Solution: Resend (Recommended)

### Step 1: Sign up for Resend
1. Go to https://resend.com
2. Sign up (free tier: 3,000 emails/month)
3. Verify your account

### Step 2: Get API Key
1. In Resend dashboard, go to "API Keys"
2. Click "Create API Key"
3. Name it "Zmarty Production"
4. Copy the key (starts with `re_`)

### Step 3: Configure Supabase
1. Go to https://app.supabase.com/project/asjtxrmftmutcsnqgidy
2. Navigate to Authentication > Settings
3. Scroll to "SMTP Settings"
4. Enable "Enable custom SMTP"
5. Enter these settings:

```
SMTP Host: smtp.resend.com
SMTP Port: 587
SMTP User: resend
SMTP Pass: [Your Resend API Key]
Sender Name: Zmarty App
Sender Email: noreply@yourdomain.com
```

### Step 4: Test
1. Save the SMTP settings
2. Test your registration flow
3. Check email delivery

## 🔧 Alternative: SendGrid (If you prefer)

### Free tier: 100 emails/day forever

1. Sign up at https://sendgrid.com
2. Create API key with "Mail Send" permissions
3. Use these SMTP settings:

```
SMTP Host: smtp.sendgrid.net
SMTP Port: 587
SMTP User: apikey
SMTP Pass: [Your SendGrid API Key]
Sender Name: Zmarty App
Sender Email: noreply@yourdomain.com
```

## 📧 Domain Configuration (Optional but Recommended)

If you have your own domain, add these DNS records:

### For Resend:
- **SPF**: `v=spf1 include:_spf.resend.com ~all`
- **DKIM**: (Provided by Resend after domain verification)

### For SendGrid:
- **SPF**: `v=spf1 include:sendgrid.net ~all`
- **DKIM**: (Provided by SendGrid after domain verification)

## ✅ Verification Steps

1. Configure SMTP in Supabase
2. Test registration with your email
3. Check spam folder if not received
4. Verify email template renders correctly
5. Test verification code process

## 🚨 Without SMTP Setup:

- Emails will NOT be delivered reliably
- Users cannot complete registration
- Production app will fail
- Rate limits will block new users

**Action Required**: Set up SMTP before launching to users!