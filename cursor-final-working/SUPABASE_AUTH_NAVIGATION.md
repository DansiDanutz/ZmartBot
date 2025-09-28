# 🔍 Finding Password Security Settings in Supabase

## Navigate Step-by-Step:

### 1. Open Your Project
Go to: https://app.supabase.com/project/xhskmqsgtdhehzlvtuns

### 2. Try These Locations (in order):

#### Location A: Auth Configuration
1. Click **Authentication** in left sidebar
2. Click **Configuration** tab (not Providers)
3. Look for **Security** section
4. Check for:
   - "Password strength requirements"
   - "Security policies"
   - "Advanced security"

#### Location B: Project Settings
1. Click **Settings** (gear icon) in left sidebar
2. Click **Authentication**
3. Scroll down to find:
   - "Password policies"
   - "Security settings"
   - "Auth configuration"

#### Location C: Auth Providers Email Settings
1. Click **Authentication** in left sidebar
2. Click **Providers** tab
3. Find **Email** in the list
4. Click **Settings** or gear icon next to Email
5. Look in the modal/panel that opens for:
   - "Password requirements"
   - "Security options"

## 🎯 What the Setting Looks Like:

The leaked password protection setting might appear as:

- **Toggle switch** labeled:
  - "Check passwords against data breaches"
  - "Enable HaveIBeenPwned integration"
  - "Leaked password protection"
  - "Compromised password detection"

- **Checkbox** with text like:
  - "Prevent users from using compromised passwords"
  - "Enable breach detection"

- **Dropdown** with options:
  - "Password security level: Basic / Enhanced / Maximum"

## 📸 Can't Find It?

If you still can't find the option:

### Check Your Plan
1. Go to **Settings** → **Billing**
2. Check your current plan
3. This feature might require:
   - Pro plan or higher
   - Or might be in beta/preview

### Alternative Locations to Check:
1. **Database** → **Extensions** → Look for "auth" related extensions
2. **SQL Editor** → Run: `SELECT * FROM auth.config;`
3. **Edge Functions** → Check if password policies are configured there

## 🔧 Manual Override via SQL:

If the UI option doesn't exist, try this in SQL Editor:

```sql
-- Check current auth configuration
SELECT * FROM auth.config;

-- If the table exists, you might be able to update it
-- (This may not work depending on permissions)
UPDATE auth.config
SET raw_app_meta_data = jsonb_set(
    COALESCE(raw_app_meta_data, '{}'),
    '{password_min_length}',
    '8'
)
WHERE instance_id = (SELECT instance_id FROM auth.config LIMIT 1);
```

## 💡 If Nothing Works:

The feature might be:
1. **Not available on free tier** - Upgrade to Pro
2. **Region-locked** - Not available in your region
3. **Renamed/Moved** - Contact Supabase support
4. **Coming soon** - Feature in development

## 📞 Contact Support:

If you can't find it:
1. Go to: https://app.supabase.com/support/new
2. Ask: "How do I enable leaked password protection (HaveIBeenPwned) for my project?"
3. Include project ref: `xhskmqsgtdhehzlvtuns`

---

**Note**: Supabase UI changes frequently. If these instructions don't match what you see, the feature may have been moved or renamed recently.