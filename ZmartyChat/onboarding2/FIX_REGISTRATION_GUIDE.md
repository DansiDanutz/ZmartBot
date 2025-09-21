# 🔧 Fix Registration Error for seme@kryptostack.com

## Problem Identified
The registration is failing with "Database error saving new user" because there's a mismatch between the database trigger and table names:
- The trigger `handle_new_user()` is trying to insert into `user_profiles` table
- But the actual table is named `zmartychat_users`

## Solution Steps

### Step 1: Apply the Fix to ZmartyBrain Database

1. Open the ZmartyBrain SQL Editor:
   https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/sql

2. Copy and run the entire contents of: `fix-zmartybrain-trigger.sql`

3. You should see a success message: "Trigger fixed successfully!"

### Step 2: Clean Up Any Existing Test Users (Optional)

If seme@kryptostack.com was partially created, run this to clean up:

```sql
-- Check if user exists
SELECT id, email, created_at
FROM auth.users
WHERE email = 'seme@kryptostack.com';

-- If exists, delete it (replace USER_ID with actual ID from above)
DELETE FROM auth.users WHERE email = 'seme@kryptostack.com';
```

### Step 3: Test Registration Again

1. Go to: http://localhost:8084/index.html
2. Click "Get Started"
3. Register with:
   - Email: seme@kryptostack.com
   - Password: (your choice, min 8 chars with uppercase, number, special char)
   - Accept terms

4. You should see the verification code screen

### Step 4: Verify Success

Check in the database:
```sql
-- In ZmartyBrain, check if user was created
SELECT
    zu.email,
    zu.auth_id,
    zu.created_at,
    zus.credits_remaining
FROM zmartychat_users zu
LEFT JOIN zmartychat_user_subscriptions zus ON zu.id = zus.user_id
WHERE zu.email = 'seme@kryptostack.com';
```

## Alternative Quick Test

Use the test page I created: http://localhost:8084/test-registration.html

This will directly test the registration and show detailed error messages.

## Root Cause Summary

The issue was that when Supabase Auth creates a new user, it triggers `handle_new_user()` function which was trying to insert into tables that didn't exist (`user_profiles`, `user_subscriptions`) instead of the correct tables (`zmartychat_users`, `zmartychat_user_subscriptions`).

The fix updates the trigger to use the correct table names and adds proper error handling.