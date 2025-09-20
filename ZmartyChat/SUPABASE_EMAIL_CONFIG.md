# 🔧 SUPABASE EMAIL CONFIGURATION - CRITICAL

## WHY EMAILS NOT WORKING:

Supabase needs SMTP configuration OR uses their built-in email service.

## CHECK EMAIL STATUS:

1. **Go to**: https://app.supabase.com/project/asjtxrmftmutcsnqgidy/settings/auth
2. **Scroll to**: "Email Settings"
3. **Check if**:
   - Email Provider is enabled
   - Rate limits are not exceeded (max 3 emails/hour for free tier)

## OPTION 1: Use Supabase Built-in (LIMITED - 3/hour)

Already configured but LIMITED to 3 emails per hour on free tier.

## OPTION 2: Configure Custom SMTP (UNLIMITED)

### Use Gmail SMTP:
1. Go to: https://app.supabase.com/project/asjtxrmftmutcsnqgidy/settings/auth
2. Scroll to "SMTP Settings"
3. Enable "Custom SMTP"
4. Configure:
   - Host: `smtp.gmail.com`
   - Port: `587`
   - Username: Your Gmail address
   - Password: App-specific password (not regular password!)
   - Sender email: Your Gmail address
   - Sender name: `ZmartyChat`

### Get Gmail App Password:
1. Go to: https://myaccount.google.com/apppasswords
2. Generate new app password
3. Use this in Supabase SMTP settings

## OPTION 3: Use Resend.com (RECOMMENDED - FREE)

1. Sign up at https://resend.com (free tier = 100 emails/day)
2. Get API key
3. In Supabase:
   - Host: `smtp.resend.com`
   - Port: `465`
   - Username: `resend`
   - Password: Your Resend API key
   - Sender email: `onboarding@resend.dev` (or your domain)

## TEST YOUR EMAIL:

After configuration, test:
1. Register new account at http://localhost:9000
2. Check email inbox
3. You should receive 6-digit code (not link!)

## CURRENT ISSUE:

Your Supabase is likely hitting the 3 emails/hour limit on free tier.
**SOLUTION**: Configure custom SMTP above for unlimited emails.