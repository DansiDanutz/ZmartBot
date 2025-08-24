#!/usr/bin/env python3
"""
Fetch KingFisher bot images
"""

from telethon.sync import TelegramClient
from datetime import datetime, timedelta
import os

API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

print(f"Fetching KingFisher images at {datetime.now().strftime('%H:%M:%S')}...")

with TelegramClient('fresh_session', API_ID, API_HASH) as client:
    count = 0
    
    # Search all dialogs
    for dialog in client.iter_dialogs():
        messages = client.get_messages(dialog, limit=100)
        
        for msg in messages:
            # Check if recent (last 10 minutes)
            if msg.date and msg.date > datetime.now(msg.date.tzinfo) - timedelta(minutes=10):
                if msg.photo:
                    # Check sender
                    if msg.sender:
                        sender_id = getattr(msg.sender, 'id', 0)
                        # KingFisher bot ID: 5646047866
                        if sender_id == 5646047866:
                            count += 1
                            filename = f"{DOWNLOAD_FOLDER}/{count}.jpg"
                            client.download_media(msg, filename)
                            print(f"Downloaded image {count}")
    
    print(f"\nTotal: {count} images")