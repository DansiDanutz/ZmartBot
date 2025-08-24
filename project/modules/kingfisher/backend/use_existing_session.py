#!/usr/bin/env python3
"""
USE EXISTING SESSION - No login needed
"""

import asyncio
import requests
import json
from datetime import datetime, timezone
from telethon import TelegramClient, events
from PIL import Image
import io
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
print("🚀 USING EXISTING SESSION - NO LOGIN NEEDED")
print("="*60)

# Try to use an existing session file
session_files = [
    'kingfisher_ready',
    'working_kingfisher_session',
    'complete_workflow_session',
    'universal_kingfisher_session',
    'kingfisher_live_session'
]

client = None
for session in session_files:
    try:
        print(f"Trying session: {session}...")
        client = TelegramClient(session, API_ID, API_HASH)
        break
    except:
        continue

if not client:
    print("No valid session found, using new one")
    client = TelegramClient('new_session', API_ID, API_HASH)

def get_real_price(symbol: str) -> float:
    """Get price"""
    prices = {
        'BTC': 102363.00,
        'ETH': 3395.63,
        'SOL': 174.67,
        'XRP': 3.31,
        'DOGE': 0.2218,
        'ADA': 0.7845
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
            full_text = text.upper() if text else ""
        
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
        symbol = 'ETH'
        for s in symbols:
            if s in full_text:
                symbol = s
                break
        
        return image_type, symbol
    except:
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
    
    # Add to field
    if field in ["Liquidation_Map", "RSI_Heatmap", "LiqRatios_long_term", "LiqRatios_short_term"]:
        fields_data[field] = report
    
    print(f"📤 Updating Airtable field: {field}")
    
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
        else:
            # Create
            response = requests.post(
                BASE_URL,
                headers=headers,
                json={'fields': fields_data}
            )
        
        if response.status_code == 200:
            print(f"✅ SUCCESS! Updated {symbol} in {field}")
            return True
        else:
            print(f"❌ Failed: {response.text[:100]}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle images"""
    if event.photo:
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        print(f"\n{'='*50}")
        print(f"🖼️ IMAGE from {chat_name}")
        
        # Download
        image_bytes = await event.download_media(bytes)
        
        if image_bytes:
            # Save
            filename = f"kingfisher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"💾 Saved: {filename}")
            
            # Identify
            caption = event.raw_text or ""
            image_type, symbol = identify_image(image_bytes, caption)
            print(f"🎯 {image_type} for {symbol}")
            
            # Update
            update_airtable(symbol, image_type)
        
        print("="*50)

async def main():
    """Main"""
    print("\n🔌 Connecting...")
    
    # Connect without prompting
    await client.connect()
    
    # Check if authorized
    if await client.is_user_authorized():
        print("✅ Already logged in! No code needed!")
        
        me = await client.get_me()
        print(f"👤 Connected as: {me.first_name} (@{me.username})")
        
        print("\n" + "="*60)
        print("🟢 MONITOR ACTIVE - Generate your image!")
        print("="*60)
        
        # Register handler
        client.add_event_handler(handler, events.NewMessage(incoming=True))
        
        # Keep running
        await client.run_until_disconnected()
    else:
        print("❌ Session not authorized")
        print("\nTry one of these:")
        print("1. Delete all .session files and start fresh")
        print("2. Use the Telegram desktop app to get the code")
        print("3. Check if you have 2FA enabled")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped")