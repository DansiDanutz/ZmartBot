#!/usr/bin/env python3
"""
STEP 1: Telegram Monitor - Find and Download ALL Images
Focus: Connect to Telegram and download EVERY image to downloads folder
"""

import asyncio
import os
from datetime import datetime
from telethon import TelegramClient, events

# Telegram credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Create downloads folder
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Counter for images
image_counter = 0

client = TelegramClient('fresh_session', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle ALL incoming messages and find ALL images"""
    global image_counter
    
    # Check if message has photo
    if event.photo:
        image_counter += 1
        
        # Get chat info
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        # Generate filename with counter
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{DOWNLOAD_FOLDER}/image_{image_counter:03d}_{timestamp}.jpg"
        
        # Download the image
        await event.download_media(filename)
        
        # Print found image
        print(f"[{image_counter}] Found image from: {chat_name}")
        print(f"    Saved as: {filename}")
        print(f"    Time: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)

async def main():
    """Main function - connect and monitor"""
    print("="*60)
    print("STEP 1: TELEGRAM IMAGE FINDER")
    print("="*60)
    
    # Connect to Telegram
    await client.start()
    me = await client.get_me()
    
    print(f"✅ Connected as: {me.first_name} (@{me.username})")
    print(f"📁 Download folder: {DOWNLOAD_FOLDER}/")
    print("="*60)
    print("MONITORING FOR IMAGES...")
    print("- Will find ALL images from ALL chats")
    print("- Each image gets numbered: image_001, image_002, etc.")
    print("="*60)
    print("\n🟢 READY - Send images to any chat!\n")
    print("Images found so far: 0")
    print("-"*60)
    
    # Run forever
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n📊 SUMMARY: Found {image_counter} images total")
        print(f"📁 All saved in: {DOWNLOAD_FOLDER}/")
        print("👋 Stopped")