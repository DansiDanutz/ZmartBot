#!/bin/bash

# ZmartyChat Database Setup Script
echo "🚀 ZmartyChat Database Setup"
echo "============================"
echo ""
echo "This script will help you set up the ZmartyChat database tables in Supabase."
echo ""
echo "📋 MANUAL STEPS REQUIRED:"
echo ""
echo "1. Open Supabase SQL Editor:"
echo "   https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy/sql/new"
echo ""
echo "2. Copy and paste the SQL from:"
echo "   database/zmartychat_complete_schema.sql"
echo ""
echo "3. Click 'Run' to create all tables"
echo ""
echo "4. Then run this command to test:"
echo "   node test-setup.js"
echo ""
echo "Press Enter to open the Supabase SQL Editor in your browser..."
read

# Open Supabase SQL Editor
open "https://supabase.com/dashboard/project/asjtxrmftmutcsnqgidy/sql/new"

echo ""
echo "✅ Browser opened. Please:"
echo "1. Paste the SQL from database/zmartychat_complete_schema.sql"
echo "2. Click 'Run'"
echo "3. Come back here and press Enter when done..."
read

# Test the setup
echo ""
echo "Testing database connection..."
node test-setup.js

echo ""
echo "Setup complete! If the test passed, you can now run:"
echo "  npm run dev    # Start the server"
echo "  npm run serve  # In another terminal"