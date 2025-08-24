#!/usr/bin/env python3
"""
Fixed monitor for KingFisher bot images
"""

import asyncio
import os
from datetime import datetime
from telethon import TelegramClient, events

API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def get_next_number():
    existing = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.endswith('.jpg')]
    if not existing:
        return 1
    numbers = []
    for f in existing:
        try:
            num = int(f.split('.')[0])
            numbers.append(num)
        except:
            pass
    return max(numbers) + 1 if numbers else 1

client = TelegramClient('fresh_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Monitor ALL incoming messages for KingFisher images"""
    if event.photo:
        # Check if from KingFisher bot (ID: 5646047866)
        sender = await event.get_sender()
        if sender:
            sender_id = getattr(sender, 'id', None)
            sender_username = getattr(sender, 'username', '')
            
            # Check if it's KingFisher bot
            if (sender_id == 5646047866 or 
                'kingfisher' in str(sender_username).lower() or
                'thekingfisher_liqmap_bot' in str(sender_username).lower()):
                
                num = get_next_number()
                filename = f"{DOWNLOAD_FOLDER}/{num}.jpg"
                
                await event.download_media(filename)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Downloaded image {num} from @{sender_username}")

async def main():
    print("="*60)
    print(f"MONITORING KINGFISHER BOT (FIXED)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print(f"📁 Downloads: {DOWNLOAD_FOLDER}/")
    print(f"🤖 Monitoring bot ID: 5646047866 (@thekingfisher_liqmap_bot)")
    print("="*60)
    print("Ready! Images will be: 1.jpg, 2.jpg, 3.jpg...")
    print("-"*60)
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())