#!/bin/bash

# =====================================================
# ENABLE LEAKED PASSWORD PROTECTION VIA SUPABASE API
# =====================================================

# Set your project details
PROJECT_REF="xhskmqsgtdhehzlvtuns"
SUPABASE_ACCESS_TOKEN="YOUR_SUPABASE_ACCESS_TOKEN"  # You need to get this from your Supabase dashboard

# API endpoint
API_URL="https://api.supabase.com/v1/projects/${PROJECT_REF}/config/auth"

# Enable leaked password protection
curl -X PATCH "${API_URL}" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "SECURITY_UPDATE_PASSWORD_REQUIRE_REAUTHENTICATION": false,
    "PASSWORD_MIN_LENGTH": 8,
    "SECURITY_MANUAL_LINKING_ENABLED": false,
    "EXTERNAL_EMAIL_ENABLED": true,
    "EXTERNAL_PHONE_ENABLED": true,
    "EXTERNAL_APPLE_ENABLED": false,
    "EXTERNAL_AZURE_ENABLED": false,
    "EXTERNAL_BITBUCKET_ENABLED": false,
    "EXTERNAL_DISCORD_ENABLED": false,
    "EXTERNAL_FACEBOOK_ENABLED": false,
    "EXTERNAL_FIGMA_ENABLED": false,
    "EXTERNAL_GITHUB_ENABLED": false,
    "EXTERNAL_GITLAB_ENABLED": false,
    "EXTERNAL_GOOGLE_ENABLED": false,
    "EXTERNAL_KAKAO_ENABLED": false,
    "EXTERNAL_KEYCLOAK_ENABLED": false,
    "EXTERNAL_LINKEDIN_ENABLED": false,
    "EXTERNAL_LINKEDIN_OIDC_ENABLED": false,
    "EXTERNAL_NOTION_ENABLED": false,
    "EXTERNAL_SLACK_ENABLED": false,
    "EXTERNAL_SLACK_OIDC_ENABLED": false,
    "EXTERNAL_SPOTIFY_ENABLED": false,
    "EXTERNAL_TWITCH_ENABLED": false,
    "EXTERNAL_TWITTER_ENABLED": false,
    "EXTERNAL_WORKOS_ENABLED": false,
    "EXTERNAL_ZOOM_ENABLED": false,
    "SECURITY_HIBP_ENABLED": true
  }'

echo "Leaked password protection has been enabled!"