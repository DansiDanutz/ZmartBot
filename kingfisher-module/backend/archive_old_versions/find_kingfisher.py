#!/usr/bin/env python3
"""
Find images from @thekingfisher_liqmap_bot sent to @SemeCJ
"""

from telethon.sync import TelegramClient
from datetime import datetime, timedelta
import os

API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

print("="*60)
print("SEARCHING FOR KINGFISHER BOT IMAGES")
print("="*60)

with TelegramClient('fresh_session', API_ID, API_HASH) as client:
    me = client.get_me()
    print(f"✅ Connected as: {me.first_name} (@{me.username})")
    
    print("\n🔍 Searching for messages from @thekingfisher_liqmap_bot...")
    
    found_images = 0
    
    # Search in all dialogs
    for dialog in client.iter_dialogs():
        # Get messages from this dialog
        messages = client.get_messages(dialog, limit=100)
        
        for msg in messages:
            # Check if message is from last hour
            if msg.date and msg.date > datetime.now(msg.date.tzinfo) - timedelta(hours=1):
                # Check if from KingFisher bot
                if msg.sender:
                    sender_username = getattr(msg.sender, 'username', '')
                    sender_id = getattr(msg.sender, 'id', '')
                    
                    # Check if it's from the KingFisher bot
                    if 'kingfisher' in str(sender_username).lower() or sender_id == 5646047866:
                        if msg.photo:
                            found_images += 1
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"{DOWNLOAD_FOLDER}/kingfisher_{found_images:03d}_{timestamp}.jpg"
                            
                            client.download_media(msg, filename)
                            
                            print(f"\n✅ FOUND KINGFISHER IMAGE #{found_images}")
                            print(f"   From: @{sender_username}")
                            print(f"   Time: {msg.date.strftime('%H:%M:%S')}")
                            print(f"   Saved: {filename}")
                            print(f"   Chat: {dialog.name}")
    
    # Also check Saved Messages
    print("\n🔍 Checking Saved Messages...")
    saved = client.get_messages('me', limit=50)
    for msg in saved:
        if msg.photo and msg.date > datetime.now(msg.date.tzinfo) - timedelta(hours=1):
            found_images += 1
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{DOWNLOAD_FOLDER}/saved_{found_images:03d}_{timestamp}.jpg"
            
            client.download_media(msg, filename)
            print(f"✅ Found image in Saved Messages: {filename}")
    
    print("\n" + "="*60)
    print(f"📊 SUMMARY: Found {found_images} images")
    print(f"📁 All saved in: {os.path.abspath(DOWNLOAD_FOLDER)}")
    
    if found_images == 0:
        print("\n⚠️ No images found from KingFisher bot")
        print("Make sure the bot sent images to your account")