#!/bin/bash

# ============================================
# Enable Leaked Password Protection via Supabase CLI
# ============================================

echo "🔐 Enabling Leaked Password Protection for ZmartyBrain Project"
echo "============================================"

# Step 1: Check if Supabase CLI is installed
echo ""
echo "Step 1: Checking Supabase CLI installation..."
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Installing..."

    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Installing via Homebrew..."
        brew install supabase/tap/supabase
    else
        # Linux/WSL
        echo "Installing via npm..."
        npm install -g supabase
    fi
else
    echo "✅ Supabase CLI is installed"
    supabase --version
fi

# Step 2: Login to Supabase (if not already logged in)
echo ""
echo "Step 2: Logging in to Supabase..."
echo "You may need to paste your access token from: https://supabase.com/dashboard/account/tokens"
supabase login

# Step 3: Link to your project
echo ""
echo "Step 3: Linking to your project..."
supabase link --project-ref xhskmqsgtdhehzlvtuns

# Step 4: Update auth configuration to enable HIBP
echo ""
echo "Step 4: Enabling leaked password protection..."

# Create a config file for the update
cat > supabase-auth-config.json << 'EOF'
{
  "auth": {
    "enable_signup": true,
    "enable_anonymous_sign_ins": false,
    "password": {
      "min_length": 12,
      "required_characters": "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 !@#$%^&*",
      "hibp_enabled": true
    },
    "security": {
      "refresh_token_reuse_interval": 10,
      "manual_linking_enabled": false,
      "enable_password_leaked_check": true
    }
  }
}
EOF

# Apply the configuration
echo "Applying configuration..."
supabase db push --config supabase-auth-config.json

# Alternative method using direct API call
echo ""
echo "Step 5: Attempting alternative method via API..."
PROJECT_REF="xhskmqsgtdhehzlvtuns"

# Get the service role key
echo "Please enter your service role key (from https://supabase.com/dashboard/project/${PROJECT_REF}/settings/api):"
read -s SERVICE_ROLE_KEY

# Make the API call to enable HIBP
curl -X PATCH \
  "https://api.supabase.com/v1/projects/${PROJECT_REF}/config" \
  -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "auth": {
      "password_leaked_check_enabled": true,
      "password_min_length": 12
    }
  }'

echo ""
echo "✅ Configuration update attempted!"
echo ""
echo "Step 6: Verifying the setting..."

# Check current configuration
supabase inspect auth

echo ""
echo "============================================"
echo "🎉 Process Complete!"
echo ""
echo "If the setting was successfully enabled, the warning should disappear."
echo "If you still see the warning, you may need to:"
echo "1. Wait a few minutes for the change to propagate"
echo "2. Contact Supabase support for manual enablement"
echo ""
echo "Your client-side protection is still active and protecting users!"
echo "============================================"

# Clean up
rm -f supabase-auth-config.json