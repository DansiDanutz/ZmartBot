#!/bin/bash

# ============================================
# Quick Enable Leaked Password Protection
# ============================================

echo "🔐 Enabling HIBP Password Protection"
echo "====================================="
echo ""

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "Installing Supabase CLI..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install supabase/tap/supabase
    else
        npm install -g supabase
    fi
fi

# Login (you'll need your access token)
echo "Step 1: Login to Supabase"
echo "Get your token from: https://supabase.com/dashboard/account/tokens"
supabase login

# Link to project
echo ""
echo "Step 2: Linking to ZmartyBrain project..."
supabase link --project-ref xhskmqsgtdhehzlvtuns

# Enable the feature
echo ""
echo "Step 3: Enabling leaked password protection..."
supabase projects update xhskmqsgtdhehzlvtuns \
  --password-leaked-check-enabled=true \
  --password-min-length=12

echo ""
echo "✅ Done! The leaked password protection should now be enabled."
echo "Check your dashboard warnings to verify."