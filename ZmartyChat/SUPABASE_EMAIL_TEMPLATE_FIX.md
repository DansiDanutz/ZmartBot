# 🔧 Fix Supabase Email Template - 6-Digit Code Only

## Remove Magic Link from Template

In your Supabase Dashboard, go to **Authentication → Email Templates → Confirm signup** and:

### 1. REMOVE these lines:
```html
<!-- CTA Button (Optional - for magic link support) -->
<table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
    <tr>
        <td align="center">
            <a href="{{ .ConfirmationURL }}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #0066ff 0%, #4d94ff 100%); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 600; border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 102, 255, 0.3);">Verify Email</a>
        </td>
    </tr>
</table>

<p style="margin: 20px 0 0 0; color: #718096; font-size: 13px; text-align: center;">
    Or copy this link: {{ .ConfirmationURL }}
</p>
```

### 2. KEEP only the 6-digit code section:
```html
<!-- Verification Code Box -->
<table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
    <tr>
        <td align="center">
            <table cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #f0f7ff 0%, #e8f2ff 100%); border: 2px solid #0066ff; border-radius: 16px; padding: 30px 40px;">
                <tr>
                    <td align="center">
                        <p style="margin: 0 0 10px 0; color: #4a5568; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Your Verification Code</p>
                        <p style="margin: 0; color: #0066ff; font-size: 42px; font-weight: 700; letter-spacing: 8px; font-family: 'Courier New', monospace;">{{ .Token }}</p>
                        <p style="margin: 10px 0 0 0; color: #718096; font-size: 13px;">Valid for 24 hours</p>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>
```

## After Making Changes:

1. **Save the template** in Supabase
2. **Test with a new email**
3. You'll receive an email with ONLY the 6-digit code (like `123456`)
4. No clickable link will be included

## Important Notes:

- `{{ .Token }}` = The 6-digit verification code
- `{{ .ConfirmationURL }}` = The magic link (REMOVE THIS)
- `{{ .Email }}` = User's email address (keep this)

Once you remove the `{{ .ConfirmationURL }}` references, users will only get the 6-digit code and must enter it on Slide 5 to verify - exactly what you want!