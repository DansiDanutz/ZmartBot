#!/usr/bin/env python3
"""
STABLE MONITOR - Working version that correctly updates Airtable
"""

import asyncio
import requests
import json
from datetime import datetime
from telethon import TelegramClient, events
from PIL import Image
import pytesseract
import io

# Telegram
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable - CORRECT configuration
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

print("="*60)
print("🌐 STABLE KINGFISHER MONITOR")
print("="*60)

client = TelegramClient('fresh_session', API_ID, API_HASH)

def detect_symbol_and_type(image_bytes, caption=""):
    """Detect symbol and image type from image"""
    try:
        # OCR the image
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img).upper()
        full_text = text + " " + caption.upper()
        
        # Find symbol - check all possible symbols
        symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU', 
                  'AVAX', 'LINK', 'LTC', 'BNB', 'MATIC', 'UNI', 'ATOM']
        
        found_symbol = None
        for symbol in symbols:
            if symbol in full_text:
                found_symbol = symbol
                break
        
        if not found_symbol:
            found_symbol = 'ETH'  # default
        
        # Detect type
        if "LIQUIDATION" in full_text and "MAP" in full_text:
            img_type = "liquidation_map"
        elif "HEATMAP" in full_text:
            img_type = "heatmap"
        elif "RSI" in full_text:
            img_type = "rsi"
        elif "RATIO" in full_text:
            img_type = "ratio"
        else:
            img_type = "liquidation_map"  # default
        
        return found_symbol, img_type
        
    except Exception as e:
        print(f"Error in detection: {e}")
        return 'ETH', 'liquidation_map'

def get_or_create_record(symbol):
    """Get existing record or return None"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Search for existing record
    params = {
        'filterByFormula': f"{{Symbol}} = '{symbol}'",
        'maxRecords': 1
    }
    
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])
        if records:
            return records[0]['id']
    
    return None

def update_airtable(symbol, img_type, image_bytes):
    """Update or create record in Airtable"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Generate report
    report = f"""🎯 KINGFISHER ANALYSIS - {symbol}
Type: {img_type.replace('_', ' ').title()}
Time: {timestamp}

📊 Analysis:
• Symbol detected: {symbol}
• Image type: {img_type}
• Processed: {timestamp}

✅ Auto-detected from Telegram"""
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Prepare fields
    fields = {
        'Symbol': symbol,
        'Liquidation_Map': report,
        'Last_update': timestamp,
        'MarketPrice': 100.0  # You can fetch real price here
    }
    
    # Check if record exists
    record_id = get_or_create_record(symbol)
    
    if record_id:
        # Update existing record
        print(f"   Updating existing {symbol} record...")
        response = requests.patch(
            f"{BASE_URL}/{record_id}",
            headers=headers,
            json={'fields': fields}
        )
    else:
        # Create new record
        print(f"   Creating new {symbol} record...")
        response = requests.post(
            BASE_URL,
            headers=headers,
            json={'records': [{'fields': fields}]}
        )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Successfully {'updated' if record_id else 'created'} {symbol}")
        return True
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
        return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle incoming messages with photos"""
    if not event.photo:
        return
    
    try:
        # Get chat info
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        print(f"\n{'='*50}")
        print(f"🖼️ IMAGE DETECTED - {datetime.now().strftime('%H:%M:%S')}")
        print(f"📍 From: {chat_name}")
        
        # Download image
        print("📥 Downloading...")
        image_bytes = await event.download_media(bytes)
        
        if image_bytes:
            # Save locally
            filename = f"kg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"💾 Saved: {filename}")
            
            # Detect symbol and type
            caption = event.raw_text or ""
            symbol, img_type = detect_symbol_and_type(image_bytes, caption)
            print(f"🎯 Detected: {symbol} ({img_type})")
            
            # Update Airtable
            if update_airtable(symbol, img_type, image_bytes):
                # Send confirmation
                await event.reply(f"✅ Processed {symbol} - Check Airtable!")
            
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Main function"""
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    
    print("\n" + "="*60)
    print("📡 MONITORING FOR KINGFISHER IMAGES")
    print("="*60)
    print("Features:")
    print("  ✅ Auto-detect symbols from images")
    print("  ✅ Update existing records (no duplicates)")
    print("  ✅ Identify image types")
    print("-"*60)
    print("\n🟢 READY - Send KingFisher images!\n")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped")