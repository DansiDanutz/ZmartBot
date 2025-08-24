#!/usr/bin/env python3
"""
Debug KingFisher Monitor - Check what's happening
"""

import asyncio
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import httpx
from dotenv import load_dotenv

load_dotenv()

# Credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"

async def check_telegram_connection():
    """Check if we can connect to Telegram"""
    print("\n1️⃣ CHECKING TELEGRAM CONNECTION...")
    
    client = TelegramClient('debug_session', API_ID, API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ Not authorized - need to login")
            return None, False
        
        me = await client.get_me()
        print(f"✅ Connected as: {me.first_name} (@{me.username})")
        return client, True
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None, False

async def check_kingfisher_channel(client):
    """Check access to KingFisher channel and recent messages"""
    print("\n2️⃣ CHECKING KINGFISHER CHANNEL...")
    
    channels_to_check = [
        "@thekingfisher_liqmap_bot",
        "thekingfisher_liqmap_bot",
        "@KingfisherBot",
        "KingfisherBot"
    ]
    
    for channel in channels_to_check:
        try:
            print(f"\nTrying: {channel}")
            entity = await client.get_entity(channel)
            
            if entity:
                print(f"✅ Found: {channel}")
                
                # Get recent messages
                print(f"📜 Checking last 20 messages...")
                
                image_count = 0
                text_count = 0
                latest_image = None
                
                async for message in client.iter_messages(entity, limit=20):
                    if message.photo:
                        image_count += 1
                        if not latest_image:
                            latest_image = message
                            print(f"\n🖼️ LATEST IMAGE:")
                            print(f"   Date: {message.date}")
                            print(f"   ID: {message.id}")
                            if message.text:
                                print(f"   Caption: {message.text[:100]}")
                    else:
                        text_count += 1
                
                print(f"\n📊 Found {image_count} images and {text_count} text messages")
                
                if image_count == 0:
                    print("⚠️ No images found in recent messages!")
                    print("   Make sure you're sending images to the right chat")
                
                return entity, latest_image
                
        except Exception as e:
            print(f"❌ Cannot access {channel}: {e}")
    
    return None, None

async def check_private_chats(client):
    """Check your private chats for KingFisher bot"""
    print("\n3️⃣ CHECKING YOUR PRIVATE CHATS...")
    
    dialogs = await client.get_dialogs(limit=50)
    
    print(f"📋 Checking {len(dialogs)} recent chats...")
    
    kingfisher_found = False
    for dialog in dialogs:
        name = dialog.name or ""
        if "kingfisher" in name.lower() or "liqmap" in name.lower():
            print(f"\n✅ Found: {name}")
            
            # Check for recent images
            image_count = 0
            async for message in client.iter_messages(dialog.entity, limit=10):
                if message.photo:
                    image_count += 1
            
            if image_count > 0:
                print(f"   📸 {image_count} recent images")
                kingfisher_found = True
                
                # Process latest image
                async for message in client.iter_messages(dialog.entity, limit=1):
                    if message.photo:
                        print(f"\n🎯 LATEST IMAGE IN THIS CHAT:")
                        print(f"   Date: {message.date}")
                        print(f"   From: {dialog.name}")
                        return dialog.entity, message
    
    if not kingfisher_found:
        print("\n⚠️ No KingFisher-related chats found with images")
        print("   Tips:")
        print("   - Start a chat with @thekingfisher_liqmap_bot")
        print("   - Or forward the image to your Saved Messages")
    
    return None, None

async def test_image_download(client, message):
    """Test downloading an image"""
    print("\n4️⃣ TESTING IMAGE DOWNLOAD...")
    
    try:
        # Download to memory
        image_bytes = await message.download_media(bytes)
        
        if image_bytes:
            print(f"✅ Downloaded image: {len(image_bytes)} bytes")
            
            # Save locally
            filename = f"test_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"💾 Saved as: {filename}")
            
            return True
        else:
            print("❌ Failed to download image")
            return False
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

async def check_airtable():
    """Check Airtable connection"""
    print("\n5️⃣ CHECKING AIRTABLE...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Get records
            response = await client.get(
                f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                print(f"✅ Airtable accessible")
                print(f"📊 Current records: {len(records)}")
                
                if records:
                    for record in records:
                        fields = record.get("fields", {})
                        print(f"   - {fields.get('Symbol', 'Unknown')}")
                
                return True
            else:
                print(f"❌ Airtable error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Airtable connection error: {e}")
        return False

async def main():
    """Main diagnostic function"""
    print("="*60)
    print("🔍 KINGFISHER MONITOR DIAGNOSTIC")
    print("="*60)
    
    # Check Telegram
    client, connected = await check_telegram_connection()
    
    if not connected:
        print("\n❌ PROBLEM: Not connected to Telegram")
        print("\n💡 SOLUTION:")
        print("1. Delete any .session files in this directory")
        print("2. Run: python integrated_kingfisher_monitor.py")
        print("3. Enter your phone number when prompted")
        return
    
    # Check KingFisher channel
    channel, latest_image = await check_kingfisher_channel(client)
    
    # If no channel, check private chats
    if not channel or not latest_image:
        channel, latest_image = await check_private_chats(client)
    
    if latest_image:
        # Test download
        success = await test_image_download(client, latest_image)
        
        if success:
            print("\n✅ Image download working!")
    else:
        print("\n⚠️ No images found to process")
        print("\n💡 NEXT STEPS:")
        print("1. Generate a new KingFisher image")
        print("2. Make sure it's sent to a chat you have access to")
        print("3. Run this diagnostic again")
    
    # Check Airtable
    await check_airtable()
    
    # Summary
    print("\n" + "="*60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    if connected and latest_image:
        print("✅ Telegram: Connected")
        print("✅ Images: Found")
        print("\n🎯 READY TO MONITOR!")
        print("\nRun: python integrated_kingfisher_monitor.py")
    else:
        print("❌ Issues detected - see above for solutions")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())