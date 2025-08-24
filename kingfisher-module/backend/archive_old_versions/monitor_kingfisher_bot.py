#!/usr/bin/env python3
"""
Monitor @thekingfisher_liqmap_bot and download images with sequential numbering
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

# Get next number based on existing files
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

@client.on(events.NewMessage(from_users=['thekingfisher_liqmap_bot']))
async def handler(event):
    """Monitor messages from @thekingfisher_liqmap_bot"""
    if event.photo:
        # Get next number
        num = get_next_number()
        filename = f"{DOWNLOAD_FOLDER}/{num}.jpg"
        
        # Download image
        await event.download_media(filename)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Downloaded image {num}")

async def main():
    print("="*60)
    print(f"MONITORING @thekingfisher_liqmap_bot")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    await client.start()
    me = await client.get_me()
    print(f"✅ Connected as: @{me.username}")
    print(f"📁 Downloads: {DOWNLOAD_FOLDER}/")
    print("="*60)
    print("Waiting for images from @thekingfisher_liqmap_bot...")
    print("Images will be saved as: 1.jpg, 2.jpg, 3.jpg, etc.")
    print("-"*60)
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())