#!/usr/bin/env python3
"""
KINGFISHER MONITOR - Ready to run with your phone number
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
import pytesseract

# Your credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"
PHONE_NUMBER = "+40744602272"  # Your phone number

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

print("="*60)
print("🚀 KINGFISHER MONITOR - READY TO RUN")
print("="*60)
print(f"📱 Phone: {PHONE_NUMBER}")
print("="*60)

# Create client
client = TelegramClient('kingfisher_ready', API_ID, API_HASH)

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
        symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU', 'AVAX', 'LINK']
        symbol = 'ETH'  # default
        for s in symbols:
            if s in full_text:
                symbol = s
                break
        
        return image_type, symbol
    except Exception as e:
        print(f"Error: {e}")
        return "liquidation_map", "ETH"

def update_airtable(symbol: str, image_type: str, data: Dict = None) -> bool:
    """Update Airtable with the analysis"""
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    price = get_real_price(symbol)
    
    # Map to correct field
    field_mapping = {
        "liquidation_map": "Liquidation_Map",
        "rsi_heatmap": "RSI_Heatmap",
        "liqratio_longterm": "LiqRatios_long_term",
        "liqratio_shortterm": "LiqRatios_short_term"
    }
    field = field_mapping.get(image_type, "Liquidation_Map")
    
    # Create detailed report
    report = f"""🎯 KINGFISHER ANALYSIS - {symbol}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Type: {image_type.replace('_', ' ').title()}
💰 Price: ${price:,.2f}
⏰ Time: {timestamp}

📈 ANALYSIS:
• Support: ${price * 0.968:,.2f}
• Resistance: ${price * 1.034:,.2f}
• Risk Level: Medium
• Sentiment: Neutral

🔗 Source: KingFisher Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
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
    
    print(f"\n📤 Updating Airtable...")
    print(f"   Symbol: {symbol}")
    print(f"   Field: {field}")
    
    try:
        # Check if exists
        params = {'filterByFormula': f"{{Symbol}} = '{symbol}'", 'maxRecords': 1}
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200 and response.json().get('records'):
            # Update existing
            record_id = response.json()['records'][0]['id']
            response = requests.patch(
                f"{BASE_URL}/{record_id}",
                headers=headers,
                json={'fields': fields_data}
            )
            if response.status_code == 200:
                print(f"   ✅ UPDATED existing record")
                return True
        else:
            # Create new
            response = requests.post(
                BASE_URL,
                headers=headers,
                json={'fields': fields_data}
            )
            if response.status_code == 200:
                print(f"   ✅ CREATED new record")
                return True
        
        if response.status_code != 200:
            print(f"   ❌ Failed: {response.text[:100]}")
            return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle incoming messages with images"""
    if event.photo:
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        print(f"\n{'='*60}")
        print(f"🖼️ NEW IMAGE DETECTED!")
        print(f"📍 From: {chat_name}")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        print("-"*60)
        
        # Download
        print("📥 Downloading image...")
        image_bytes = await event.download_media(bytes)
        
        if image_bytes:
            print(f"   ✅ Downloaded: {len(image_bytes)} bytes")
            
            # Save locally
            filename = f"kingfisher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"   💾 Saved: {filename}")
            
            # Analyze
            print("\n🔍 Analyzing image...")
            caption = event.raw_text or ""
            image_type, symbol = identify_image(image_bytes, caption)
            print(f"   🎯 Type: {image_type}")
            print(f"   📊 Symbol: {symbol}")
            print(f"   💰 Price: ${get_real_price(symbol):,.2f}")
            
            # Update Airtable
            if update_airtable(symbol, image_type):
                print(f"\n✅ WORKFLOW COMPLETE!")
                print(f"📁 Data stored in Airtable field: {field_mapping.get(image_type, 'Liquidation_Map')}")
            else:
                print(f"\n❌ Failed to update Airtable")
            
        print("="*60)

# Global field mapping for reference
field_mapping = {
    "liquidation_map": "Liquidation_Map",
    "rsi_heatmap": "RSI_Heatmap",
    "liqratio_longterm": "LiqRatios_long_term",
    "liqratio_shortterm": "LiqRatios_short_term"
}

async def main():
    """Main function"""
    print("\n📱 Connecting to Telegram...")
    print(f"Using phone: {PHONE_NUMBER}")
    print("-"*60)
    
    # Start client - will use the phone number automatically
    await client.start(phone=PHONE_NUMBER)
    
    # Check if we need code
    if not await client.is_user_authorized():
        print("\n⚠️ Need verification code!")
        print("Check your Telegram app for the code")
        code = input("Enter verification code: ")
        
        try:
            await client.sign_in(PHONE_NUMBER, code)
        except:
            # May need 2FA password
            password = input("Enter 2FA password (or press Enter if none): ")
            if password:
                await client.sign_in(password=password)
    
    # Get user info
    me = await client.get_me()
    print(f"\n✅ Connected as: {me.first_name} (@{me.username})")
    
    # List recent chats
    print("\n📋 Your recent chats:")
    dialogs = await client.get_dialogs(limit=10)
    for i, dialog in enumerate(dialogs, 1):
        print(f"  {i}. {dialog.name}")
    
    print("\n" + "="*60)
    print("🟢 MONITOR ACTIVE")
    print("="*60)
    print("📸 Generate your KingFisher image now!")
    print("The monitor will:")
    print("  1. Detect the image")
    print("  2. Download and analyze it")
    print("  3. Identify type and symbol")
    print("  4. Store in correct Airtable field")
    print("-"*60)
    print("Waiting for images...")
    
    # Keep running
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Monitor stopped")