# 📧 Supabase Email Template Configuration

## Steps to Configure Email Template:

### 1. Go to Supabase Dashboard
https://app.supabase.com/project/asjtxrmftmutcsnqgidy

### 2. Navigate to:
**Authentication** → **Email Templates**

### 3. Select "Confirm signup" template

### 4. Configure as follows:

**Subject:**
```
Verification Email - Welcome to Zmarty 🚀
```

**Message:**
Copy the entire content from `email-template-verification.html`

### 5. Available Variables:

These variables are automatically replaced by Supabase:
- `{{ .Token }}` - The 6-digit verification code
- `{{ .Email }}` - User's email address
- `{{ .ConfirmationURL }}` - Direct verification link (if using magic link)

### 6. Other Email Templates to Configure:

#### **Invite user** template:
**Subject:** `You're invited to join Zmarty!`

#### **Magic Link** template:
**Subject:** `Your Zmarty Login Link`

#### **Change Email Address** template:
**Subject:** `Confirm your new email address`

#### **Reset Password** template:
**Subject:** `Reset your Zmarty password`

### 7. Save Changes

Click "Save" after updating each template.

## Template Features:

✅ **Professional Design**: Gradient header with Zmarty branding
✅ **Clear Code Display**: Large, easy-to-read verification code
✅ **Mobile Responsive**: Works on all devices
✅ **Feature Highlights**: Shows what users get after signing up
✅ **Security Notice**: Informs users about account safety
✅ **Both Methods**: Supports both OTP code and magic link
✅ **Branded Footer**: Professional footer with links

## Testing:

1. Register with a test email
2. Check inbox for the verification email
3. Verify the template renders correctly
4. Test the verification code input
5. Ensure successful account creation

## Preview:

The email will show:
- Zmarty gradient header
- Welcome message
- Large verification code box
- Features list (AI Analysis, Real-time Monitoring, etc.)
- Security note
- Professional footer

## Notes:

- The template uses inline CSS for maximum email client compatibility
- Works with all major email providers (Gmail, Outlook, Apple Mail, etc.)
- The verification code is prominently displayed
- Mobile-optimized for phone users