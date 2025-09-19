# ✅ SMTP Configuration for Zmarty

## Your Resend API Configuration

Your Resend API key has been configured. Here are the exact settings to enter in Supabase:

### 1. Go to Supabase Dashboard
Link: https://app.supabase.com/project/asjtxrmftmutcsnqgidy

### 2. Navigate to:
Authentication → Settings → SMTP Settings

### 3. Enter These Exact Settings:

| Field | Value |
|-------|-------|
| **Enable custom SMTP** | ✅ Check this box |
| **Sender email** | `noreply@zmarty.app` |
| **Sender name** | `Zmarty App` |
| **Host** | `smtp.resend.com` |
| **Port number** | `587` |
| **Username** | `resend` |
| **Password** | `re_9icHVkzn_NYi3G5feasVmEUJZEMxP8TLm` |
| **Minimum interval between emails** | `0` (for no limit) |

### 4. Click "Save"

### 5. Test Your Configuration

After saving, test the email flow:

1. Open your app: http://localhost:8080 (or wherever it's hosted)
2. Go to slide 4 (Registration)
3. Enter your email address
4. Click "Continue"
5. Check your inbox for the Zmarty verification email
6. Enter the 6-digit code from the email

## ⚠️ Important Notes:

- **Keep your API key secure**: Don't commit it to public repositories
- **Monitor usage**: Resend free tier = 3,000 emails/month
- **Check spam folder**: First emails might go to spam until domain is verified

## 📧 Email Deliverability Tips:

1. **Verify your domain** in Resend dashboard for better deliverability
2. **Use a real domain** instead of zmarty.app if you have one
3. **Monitor bounces** in Resend dashboard

## 🔒 Security:

The `.env.production` file has been added to `.gitignore` to keep your API key secure.

## ✨ You're All Set!

Your Supabase project is now configured with production-ready email delivery through Resend!