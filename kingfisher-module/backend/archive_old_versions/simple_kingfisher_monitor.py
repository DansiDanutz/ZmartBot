#!/usr/bin/env python3
"""
SIMPLE KINGFISHER MONITOR - With clear prompts
"""

import asyncio
import requests
import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from PIL import Image
import io
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import pytesseract

# Your credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

print("="*60)
print("🚀 SIMPLE KINGFISHER MONITOR")
print("="*60)

# Create client with explicit session file
client = TelegramClient('kingfisher_simple', API_ID, API_HASH)

def get_real_price(symbol: str) -> float:
    """Get price for symbol"""
    prices = {
        'BTC': 102363.00,
        'ETH': 3395.63,
        'SOL': 174.67,
        'XRP': 3.31,
        'DOGE': 0.2218,
        'ADA': 0.7845,
        'DOT': 3.85,
        'PENGU': 0.000045
    }
    return prices.get(symbol, 100.0)

def identify_image(image_bytes: bytes, text: str = "") -> tuple:
    """Identify image type and symbol"""
    try:
        # Try OCR
        try:
            image = Image.open(io.BytesIO(image_bytes))
            ocr_text = pytesseract.image_to_string(image)
            full_text = (ocr_text + " " + text).upper()
        except:
            full_text = text.upper()
        
        # Identify type
        if "LIQUIDATION MAP" in full_text or "LIQ MAP" in full_text:
            image_type = "liquidation_map"
        elif "RSI" in full_text and "HEATMAP" in full_text:
            image_type = "rsi_heatmap"
        elif "LONG TERM" in full_text:
            image_type = "liqratio_longterm"
        elif "SHORT TERM" in full_text:
            image_type = "liqratio_shortterm"
        else:
            image_type = "liquidation_map"
        
        # Extract symbol
        symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU']
        symbol = 'ETH'  # default
        for s in symbols:
            if s in full_text:
                symbol = s
                break
        
        return image_type, symbol
    except Exception as e:
        print(f"Error: {e}")
        return "liquidation_map", "ETH"

def update_airtable(symbol: str, image_type: str) -> bool:
    """Update Airtable"""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    price = get_real_price(symbol)
    
    # Map to field
    field_mapping = {
        "liquidation_map": "Liquidation_Map",
        "rsi_heatmap": "RSI_Heatmap",
        "liqratio_longterm": "LiqRatios_long_term",
        "liqratio_shortterm": "LiqRatios_short_term"
    }
    field = field_mapping.get(image_type, "Liquidation_Map")
    
    # Create report
    report = f"""🎯 KINGFISHER - {symbol}
Type: {image_type.replace('_', ' ').title()}
Price: ${price:,.2f}
Time: {timestamp}"""
    
    # Prepare data
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    fields_data = {
        "Symbol": symbol,
        "MarketPrice": price,
        "Last_update": timestamp
    }
    
    # Add to correct field
    if field in ["Liquidation_Map", "RSI_Heatmap", "LiqRatios_long_term", "LiqRatios_short_term"]:
        fields_data[field] = report
    
    try:
        # Check if exists
        params = {'filterByFormula': f"{{Symbol}} = '{symbol}'", 'maxRecords': 1}
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200 and response.json().get('records'):
            # Update
            record_id = response.json()['records'][0]['id']
            response = requests.patch(
                f"{BASE_URL}/{record_id}",
                headers=headers,
                json={'fields': fields_data}
            )
            success = response.status_code == 200
        else:
            # Create
            response = requests.post(
                BASE_URL,
                headers=headers,
                json={'fields': fields_data}
            )
            success = response.status_code == 200
        
        if success:
            print(f"✅ Updated {symbol} in Airtable field: {field}")
        else:
            print(f"❌ Failed: {response.text[:100]}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle incoming messages with images"""
    if event.photo:
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        print(f"\n{'='*50}")
        print(f"🖼️ IMAGE DETECTED from {chat_name}")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        
        # Download
        print("📥 Downloading...")
        image_bytes = await event.download_media(bytes)
        
        if image_bytes:
            # Save locally
            filename = f"kingfisher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"💾 Saved: {filename}")
            
            # Identify
            caption = event.raw_text or ""
            image_type, symbol = identify_image(image_bytes, caption)
            print(f"🎯 Type: {image_type}, Symbol: {symbol}")
            
            # Update Airtable
            if update_airtable(symbol, image_type):
                print(f"✅ SUCCESS! Check Airtable")
            
        print("="*50)

async def main():
    """Main function"""
    print("\n📱 Starting Telegram client...")
    print("You may need to enter:")
    print("1. Phone number (with country code, e.g., +40744602272)")
    print("2. Verification code from Telegram")
    print("3. 2FA password (if you have it)")
    print("-"*60)
    
    # Start client with explicit authentication
    await client.start(
        phone=lambda: input("Enter phone number: "),
        code_callback=lambda: input("Enter verification code: "),
        password=lambda: input("Enter 2FA password (or press Enter if none): ")
    )
    
    # Get user info
    me = await client.get_me()
    print(f"\n✅ Connected as: {me.first_name} (@{me.username})")
    
    # List recent chats
    print("\n📋 Your recent chats:")
    dialogs = await client.get_dialogs(limit=10)
    for i, dialog in enumerate(dialogs, 1):
        print(f"  {i}. {dialog.name}")
    
    print("\n" + "="*60)
    print("🟢 MONITOR ACTIVE - Generate your KingFisher image!")
    print("="*60)
    print("Waiting for images...")
    
    # Keep running
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped")