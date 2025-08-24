#!/usr/bin/env python3
"""
Setup and Start KingFisher Monitor
Handles authentication and starts monitoring
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import json

print("="*60)
print("🚀 KINGFISHER MONITOR SETUP")
print("="*60)

# Check for existing session
session_file = "integrated_kingfisher_session.session"
if os.path.exists(session_file):
    print(f"⚠️ Found existing session file: {session_file}")
    response = input("Delete and start fresh? (y/n): ")
    if response.lower() == 'y':
        os.remove(session_file)
        print("✅ Session file deleted")
    else:
        print("Keeping existing session")

print("\n📋 INSTRUCTIONS:")
print("="*60)
print("The monitor needs to authenticate with Telegram.")
print("You'll need:")
print("1. Your phone number (with country code)")
print("2. The verification code from Telegram")
print("3. Your 2FA password (if enabled)")
print("="*60)

print("\n🎯 The monitor will:")
print("✅ Watch @thekingfisher_liqmap_bot")
print("✅ Auto-detect image types")
print("✅ Extract symbols (BTC, ETH, SOL, etc.)")
print("✅ Store in correct Airtable fields")
print("="*60)

response = input("\nReady to start? (y/n): ")
if response.lower() != 'y':
    print("Setup cancelled")
    sys.exit(0)

print("\n🚀 Starting monitor...")
print("Please follow the authentication prompts...\n")

# Import and run the monitor
try:
    from integrated_kingfisher_monitor import IntegratedKingFisherMonitor
    
    async def run():
        monitor = IntegratedKingFisherMonitor()
        await monitor.start()
    
    asyncio.run(run())
    
except KeyboardInterrupt:
    print("\n⏹️ Monitor stopped by user")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Make sure you have internet connection")
    print("2. Check your Telegram app for verification code")
    print("3. If issues persist, delete the session file and try again")