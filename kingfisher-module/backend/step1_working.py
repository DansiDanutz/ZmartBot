#!/usr/bin/env python3
"""
STEP 1 WORKING: Find ALL images from Telegram
"""

import asyncio
import os
from datetime import datetime, timedelta
from telethon import TelegramClient, events

# Your Telegram App credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Create downloads folder
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Global counter
image_counter = 0
processed_messages = set()

client = TelegramClient('zmart_session', API_ID, API_HASH)

@client.on(events.NewMessage())
async def new_message_handler(event):
    """Handle ALL messages - incoming and outgoing"""
    global image_counter
    
    # Check if we already processed this message
    if event.message.id in processed_messages:
        return
    
    processed_messages.add(event.message.id)
    
    # Check for photo
    if event.photo:
        image_counter += 1
        
        # Get sender info
        if event.is_private:
            chat_name = "Private Chat"
        else:
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', 'Unknown')
        
        # Download image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        filename = f"{DOWNLOAD_FOLDER}/image_{image_counter:03d}_{timestamp}.jpg"
        
        try:
            await event.download_media(filename)
            print(f"\n✅ [{image_counter}] NEW IMAGE FOUND!")
            print(f"   From: {chat_name}")
            print(f"   Saved: {filename}")
            print(f"   Time: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        except Exception as e:
            print(f"❌ Error downloading image {image_counter}: {e}")

async def check_recent_messages():
    """Check recent messages for any missed images"""
    global image_counter
    
    print("\n🔍 Checking recent messages for images...")
    
    # Check last 30 minutes of messages
    time_limit = datetime.now(timezone.utc) - timedelta(minutes=30)
    
    async for dialog in client.iter_dialogs(limit=20):
        async for message in client.iter_messages(dialog, limit=50):
            if message.date < time_limit:
                break
                
            if message.id in processed_messages:
                continue
                
            if message.photo:
                processed_messages.add(message.id)
                image_counter += 1
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                filename = f"{DOWNLOAD_FOLDER}/image_{image_counter:03d}_{timestamp}.jpg"
                
                try:
                    await message.download_media(filename)
                    print(f"✅ Found recent image #{image_counter} from {dialog.name}")
                except:
                    pass

async def main():
    """Main function"""
    global image_counter
    
    print("="*60)
    print("STEP 1: TELEGRAM IMAGE FINDER (WORKING VERSION)")
    print("="*60)
    
    # Connect with phone if needed
    await client.start(
        phone=lambda: input("Enter phone (+40744602272): ") or "+40744602272"
    )
    
    # Verify connection
    me = await client.get_me()
    print(f"\n✅ CONNECTED AS: {me.first_name} (@{me.username})")
    
    if me.username != "SemeCJ":
        print(f"⚠️ WARNING: Expected @SemeCJ but got @{me.username}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    print(f"📁 Download folder: {os.path.abspath(DOWNLOAD_FOLDER)}")
    
    # Check for recent images first
    await check_recent_messages()
    
    print("\n" + "="*60)
    print(f"📊 Initial scan complete: Found {image_counter} recent images")
    print("="*60)
    print("🟢 NOW MONITORING FOR NEW IMAGES...")
    print("Send images to any chat and they will appear here!")
    print("-"*60)
    
    # Keep running
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        from datetime import timezone
    except ImportError:
        import pytz
        timezone = pytz
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n📊 FINAL SUMMARY:")
        print(f"   Total images found: {image_counter}")
        print(f"   Location: {os.path.abspath(DOWNLOAD_FOLDER)}")
        
        # List files
        if os.path.exists(DOWNLOAD_FOLDER):
            files = os.listdir(DOWNLOAD_FOLDER)
            if files:
                print(f"\n📁 Files downloaded:")
                for f in sorted(files)[:10]:
                    print(f"   - {f}")
                if len(files) > 10:
                    print(f"   ... and {len(files)-10} more")
        
        print("\n👋 Stopped")