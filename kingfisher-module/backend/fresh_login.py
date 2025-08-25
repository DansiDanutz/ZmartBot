#!/usr/bin/env python3
"""
FRESH LOGIN - Simple and clear
"""

import asyncio
from telethon import TelegramClient
import time

API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"
PHONE = "+40744602272"

print("="*60)
print("🔐 FRESH TELEGRAM LOGIN")
print("="*60)
print(f"Phone: {PHONE}")
print("="*60)

async def main():
    # New session
    client = TelegramClient('fresh_session', API_ID, API_HASH)
    
    await client.connect()
    
    print("\n📱 Sending code to your Telegram...")
    
    # Send code
    await client.send_code_request(PHONE)
    
    print("\n✅ CODE SENT!")
    print("-"*60)
    print("CHECK YOUR TELEGRAM APP NOW!")
    print("Look for a message from 'Telegram'")
    print("It will say: 'Login code: XXXXX'")
    print("-"*60)
    
    # Wait a bit for user to check
    time.sleep(2)
    
    code = input("\nEnter the 5-digit code: ")
    
    try:
        # Try to sign in
        await client.sign_in(PHONE, code)
        print("\n✅ SUCCESS! Logged in!")
        
        me = await client.get_me()
        print(f"👤 Logged in as: {me.first_name} (@{me.username})")
        
        # Save session
        print("\n💾 Session saved as 'fresh_session.session'")
        print("You can now run the monitor!")
        
    except Exception as e:
        if "Two" in str(e) or "2FA" in str(e) or "password" in str(e).lower():
            print("\n🔐 2FA detected!")
            password = input("Enter your 2FA password: ")
            await client.sign_in(password=password)
            print("✅ Logged in with 2FA!")
        else:
            print(f"\n❌ Error: {e}")
            print("\nPossible issues:")
            print("1. Wrong code - try again")
            print("2. Code expired - run script again")
            print("3. Too many attempts - wait 5 minutes")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())