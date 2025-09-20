# 🔧 FIX SUPABASE EMAIL - URGENT

## PROBLEM:
You're receiving a LINK in emails instead of the 6-DIGIT CODE

## SOLUTION:

### Go to Supabase Dashboard:
1. **Open**: https://app.supabase.com/project/asjtxrmftmutcsnqgidy/auth/templates
2. **Click** on "Confirm signup" template

### Replace the Email Template:

**DELETE** everything and paste this:

```html
<h2>Confirm your signup</h2>

<p>Enter this code to verify your email:</p>

<h1 style="font-size: 32px; font-weight: bold; color: #0066ff; letter-spacing: 5px;">
  {{ .Token }}
</h1>

<p>This code expires in 60 minutes.</p>
```

### IMPORTANT:
- **REMOVE** any {{ .ConfirmationURL }} links
- **KEEP ONLY** the {{ .Token }} code
- **SAVE** the template

## RESULT:
✅ Emails will show ONLY the 6-digit code
✅ No more confusing links
✅ Verification will work properly

## TEST:
1. Register a new account
2. Check email - you should see ONLY the 6-digit code
3. Enter the code in the app
4. Success!