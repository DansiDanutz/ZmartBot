# Alternative Password Protection Implementation

Since the Authentication Settings are not available in your Supabase Dashboard, here are alternative approaches to implement leaked password protection.

## Option 1: Check Different Dashboard Locations

The setting might be in one of these locations:

1. **Project Settings → Auth**
   - URL: `https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/auth`

2. **Authentication → Policies**
   - URL: `https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/auth/policies`

3. **Authentication → Providers**
   - URL: `https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/auth/providers`
   - Look for "Email" provider settings

4. **Project Settings → General**
   - URL: `https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/general`
   - Sometimes auth settings are under general configuration

## Option 2: Use Supabase CLI Configuration

If you have Supabase CLI installed, you can check and modify settings:

```bash
# Login to Supabase CLI
supabase login

# Link to your project
supabase link --project-ref xhskmqsgtdhehzlvtuns

# Get current config
supabase config get

# Update auth settings (if available)
supabase config set --auth.enable_signup=true
```

## Option 3: Custom Implementation with Edge Functions

Since Supabase might not have the leaked password protection setting exposed, we can implement it ourselves using Edge Functions:

### Create Custom Auth Hook

```typescript
// supabase/functions/check-password-security/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { password } = await req.json()

    // Hash the password
    const encoder = new TextEncoder()
    const data = encoder.encode(password)
    const hashBuffer = await crypto.subtle.digest('SHA-1', data)
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase()

    // Check with HIBP
    const prefix = hashHex.substring(0, 5)
    const suffix = hashHex.substring(5)

    const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`)
    const text = await response.text()
    const hashes = text.split('\n')

    for (const hash of hashes) {
      const [hashSuffix] = hash.split(':')
      if (hashSuffix === suffix) {
        return new Response(
          JSON.stringify({
            compromised: true,
            message: 'This password has been found in a data breach'
          }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
      }
    }

    return new Response(
      JSON.stringify({ compromised: false }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})
```

### Deploy the Edge Function

```bash
# Deploy the function
supabase functions deploy check-password-security

# Test the function
supabase functions invoke check-password-security --body '{"password":"P@ssw0rd"}'
```

## Option 4: Client-Side Implementation (Already Created)

Since we already have a robust client-side implementation, you can enforce password security entirely on the frontend:

### Update Your Registration/Password Change Forms

```javascript
// In your signup component
import { validatePasswordComplete } from './security/password-validation.js';
import { handlePasswordError } from './security/auth-error-handler.js';

async function handleSignUp(email, password) {
  // Validate password before sending to Supabase
  const validation = await validatePasswordComplete(password, email);

  if (!validation.valid) {
    // Show error to user
    if (validation.compromised) {
      showError('This password has been found in a data breach. Please choose a different password.');
    } else {
      showError(validation.errors.join('. '));
    }
    return;
  }

  // If validation passes, proceed with Supabase signup
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  });

  if (error) {
    const parsedError = handlePasswordError(password, error);
    showError(parsedError.message);
  }
}
```

## Option 5: Database Trigger Implementation

Create a database trigger that validates passwords on user creation/update:

```sql
-- Create a function to check password strength
CREATE OR REPLACE FUNCTION check_password_security()
RETURNS TRIGGER AS $$
BEGIN
  -- Check minimum length
  IF LENGTH(NEW.raw_user_meta_data->>'password_temp') < 12 THEN
    RAISE EXCEPTION 'Password must be at least 12 characters long';
  END IF;

  -- Check for common weak passwords (basic list)
  IF LOWER(NEW.raw_user_meta_data->>'password_temp') IN (
    'password', 'password123', 'admin123', 'qwerty123',
    'welcome123', 'changeme', 'letmein', 'monkey123'
  ) THEN
    RAISE EXCEPTION 'This password is too common. Please choose a stronger password.';
  END IF;

  -- Clear temporary password from metadata
  NEW.raw_user_meta_data = NEW.raw_user_meta_data - 'password_temp';

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: This is a simplified version. Full HIBP integration
-- would require an HTTP extension or external service
```

## Option 6: Use Auth Hooks (If Available in Your Plan)

Some Supabase plans support Auth Hooks. Check if you have access to:

1. Go to: **Database → Functions**
2. Look for "Auth Hooks" or "Webhooks"
3. Create a hook for `before_sign_up` and `before_update_user`

## Recommended Approach

Given the dashboard limitations, I recommend:

1. **Immediate:** Use the client-side validation (Option 4)
   - Already implemented in `password-validation.js`
   - Provides immediate protection
   - Works without server changes

2. **Next Step:** Deploy the Edge Function (Option 3)
   - Adds server-side validation
   - Provides API endpoint for password checking
   - Works with any Supabase plan

3. **Future:** Monitor Supabase updates
   - They may add this feature to the dashboard
   - Check release notes regularly

## Testing Your Implementation

Regardless of which approach you use, test with:

```javascript
// Test script
const testPasswords = [
  'P@ssw0rd',        // Known compromised
  'MyS3cur3P@ss!',   // Likely safe
  'password123',     // Weak
];

for (const password of testPasswords) {
  const result = await validatePasswordComplete(password);
  console.log(`${password}: ${result.valid ? 'VALID' : 'INVALID'}`);
  if (!result.valid) {
    console.log(`  Reason: ${result.errors.join(', ')}`);
  }
}
```

## Support Contacts

If you need the dashboard feature enabled:
- Supabase Support: support@supabase.com
- Discord: https://discord.supabase.com
- GitHub Issues: https://github.com/supabase/supabase/issues

Request: "Enable leaked password protection setting in dashboard for project xhskmqsgtdhehzlvtuns"