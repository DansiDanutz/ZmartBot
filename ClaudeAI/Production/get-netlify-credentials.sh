#!/bin/bash

echo "🚀 Netlify Credentials Setup Helper"
echo "=================================="
echo ""

echo "📋 Follow these steps to get your Netlify credentials:"
echo ""

echo "1️⃣  Get Netlify Auth Token:"
echo "   • Go to: https://app.netlify.com/user/applications#personal-access-tokens"
echo "   • Click 'New access token'"
echo "   • Give it a name (e.g., 'GitHub Actions')"
echo "   • Click 'Generate token'"
echo "   • Copy the token (you won't see it again!)"
echo ""

echo "2️⃣  Get Netlify Site ID:"
echo "   • Go to: https://app.netlify.com/"
echo "   • Select your site"
echo "   • Go to Site settings → General → Site details"
echo "   • Copy the 'Site ID'"
echo ""

echo "3️⃣  Add to GitHub Secrets:"
echo "   • Go to your GitHub repository"
echo "   • Click 'Settings' tab"
echo "   • Go to 'Secrets and variables' → 'Actions'"
echo "   • Click 'New repository secret'"
echo "   • Add these two secrets:"
echo "     - Name: NETLIFY_AUTH_TOKEN, Value: [your token]"
echo "     - Name: NETLIFY_SITE_ID, Value: [your site id]"
echo ""

echo "✅ After adding the secrets, the warnings will disappear!"
echo ""

echo "🔗 Quick Links:"
echo "   • Netlify Tokens: https://app.netlify.com/user/applications#personal-access-tokens"
echo "   • Netlify Dashboard: https://app.netlify.com/"
echo "   • GitHub Secrets: [Your Repo]/settings/secrets/actions"
echo ""

echo "📖 For detailed instructions, see: .github/workflows/SETUP_GUIDE.md"
