#!/usr/bin/env python3
"""
Web Telegram Login - Alternative method
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

print("="*60)
print("🌐 WEB TELEGRAM LOGIN")
print("="*60)
print("\nThis will generate a login link for Telegram Web")
print("="*60)

async def main():
    # Use string session for portability
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print("\n📱 LOGIN OPTIONS:")
        print("="*60)
        print("1. Open Telegram Web: https://web.telegram.org")
        print("2. Login there first")
        print("3. Then run the monitor")
        print("\nOR")
        print("\n1. Open Telegram Desktop app")
        print("2. Go to Settings → Devices")
        print("3. Link a new device")
        print("4. You'll get a QR code or login code")
        print("\nOR")
        print("\nManual method:")
        phone = input("Enter phone number (+40744602272): ") or "+40744602272"
        
        await client.send_code_request(phone)
        print("\n✅ Code sent to your Telegram app!")
        print("Check your Telegram messages from Telegram itself")
        
        code = input("Enter the code: ")
        
        try:
            await client.sign_in(phone, code)
            print("✅ Logged in successfully!")
            
            # Save the session
            session_string = client.session.save()
            with open("session_string.txt", "w") as f:
                f.write(session_string)
            print("Session saved to session_string.txt")
            
        except Exception as e:
            print(f"Error: {e}")
            if "Two-steps verification" in str(e):
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)
    
    else:
        print("✅ Already authorized!")
    
    me = await client.get_me()
    print(f"\n👤 Logged in as: {me.first_name} (@{me.username})")
    
    await client.disconnect()

asyncio.run(main())