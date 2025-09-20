# 🎯 SUPABASE PROJECT ORGANIZATION

## Current Situation (MESSY):
We've been using the WRONG project for user registration!

## Correct Organization:

### 1. **ZmartyBrain Project** (xhskmqsgtdhehzlvtuns)
**Purpose**: USER MANAGEMENT & AUTHENTICATION
- User registration/login
- Email verification
- User profiles
- User tiers (free/pro/enterprise)
- Dashboard access
**URL**: https://xhskmqsgtdhehzlvtuns.supabase.co

### 2. **ZmartBot Project** (asjtxrmftmutcsnqgidy)
**Purpose**: BOT & TRADING FUNCTIONALITY
- Trading strategies
- Bot configurations
- Market data
- Trading history
- API integrations
**URL**: https://asjtxrmftmutcsnqgidy.supabase.co

## WHAT WE NEED TO DO:

### Step 1: Get ZmartyBrain Credentials
1. Go to: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/settings/api
2. Copy the `anon` key
3. Update supabase-client.js

### Step 2: Configure Email Templates in ZmartyBrain
1. Go to: https://supabase.com/dashboard/project/xhskmqsgtdhehzlvtuns/auth/templates
2. Update "Confirm signup" template to show only 6-digit code

### Step 3: Check User Data
- Old users might be in ZmartBot project (wrong)
- New users should go to ZmartyBrain project (correct)

## ACTION NEEDED NOW:
Please provide the anon key from ZmartyBrain project so I can update the configuration!