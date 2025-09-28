# Checking Supabase Auth Settings

If you don't see "Leaked password protection" option, it might be under a different location or name. Let's check all possible locations:

## Option 1: Authentication > Configuration
1. Go to: https://app.supabase.com/project/xhskmqsgtdhehzlvtuns/auth/configuration
2. Look for sections:
   - **Password Policy**
   - **Security Settings**
   - **Advanced Settings**

## Option 2: Project Settings > Auth
1. Go to: https://app.supabase.com/project/xhskmqsgtdhehzlvtuns/settings/auth
2. Check for:
   - **Password Requirements**
   - **Security Options**
   - **HaveIBeenPwned Integration**

## Option 3: Authentication > Policies
1. Go to: https://app.supabase.com/project/xhskmqsgtdhehzlvtuns/auth/policies
2. Look for password-related policies

## What You Should See:
Look for any of these terms:
- "Leaked password protection"
- "HaveIBeenPwned" or "HIBP"
- "Compromised password check"
- "Password breach detection"
- "Password security"

## If Still Not Found:

This could mean:
1. **Feature not available on your plan** - Some features require Pro plan
2. **Region restriction** - Feature might not be available in all regions
3. **Feature renamed/moved** - UI might have changed

## Alternative Solution: Implement Client-Side

Since the dashboard option isn't visible, we can implement password checking client-side in your onboarding flow.

Would you like me to:
1. Add client-side password breach checking to your onboarding?
2. Contact Supabase support about enabling this feature?
3. Check if this is a plan limitation?

## Current Workaround:

We can add password strength validation in the onboarding form:
- Minimum 8 characters
- Mix of uppercase/lowercase
- Include numbers
- Include special characters
- Check against common passwords list

This won't check HaveIBeenPwned but will still improve security.