#!/bin/bash
# Clean up test KingFisher files

echo "Cleaning up test files..."

# Remove test monitors created today
rm -f simple_monitor.py
rm -f sync_monitor.py
rm -f working_monitor.py
rm -f fixed_monitor.py
rm -f quick_monitor.py
rm -f test_connection.py
rm -f kingfisher_working.py
rm -f kingfisher_auto_complete.py
rm -f proper_kingfisher_monitor.py
rm -f simple_kingfisher_monitor.py
rm -f use_existing_session.py
rm -f web_telegram_login.py
rm -f test_session.py
rm -f setup_and_start_monitor.py
rm -f manual_kingfisher_test.py
rm -f simple_debug_test.py
rm -f check_airtable_schema.py
rm -f complete_workflow_monitor.py
rm -f integrated_kingfisher_monitor.py
rm -f working_kingfisher_monitor.py

echo "✅ Cleaned up test files"
echo "Keeping the working versions:"
ls -la universal_kingfisher_monitor.py
ls -la enhanced_kingfisher_monitor.py
ls -la final_kingfisher_monitor.py
ls -la realtime_kingfisher_monitor.py