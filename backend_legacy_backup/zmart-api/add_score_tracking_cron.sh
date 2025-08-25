#!/bin/bash

# Add daily score tracking cron job
echo "Adding daily score tracking cron job..."

# Get current cron jobs
crontab -l > /tmp/current_cron 2>/dev/null || touch /tmp/current_cron

# Add the new cron job
echo "0 2 * * * cd /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api && ./run_daily_score_tracker.sh >> /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api/score_tracking_cron.log 2>&1" >> /tmp/current_cron

# Install the updated cron jobs
crontab /tmp/current_cron

# Clean up
rm /tmp/current_cron

echo "Daily score tracking cron job added successfully!"
echo "The script will run daily at 2:00 AM"
echo "Logs will be saved to: /Users/dansidanutz/Desktop/ZmartBot/backend/zmart-api/score_tracking_cron.log"
