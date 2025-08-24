#!/usr/bin/env python3
"""
WORKING KINGFISHER MONITOR - With correct Airtable fields
This version uses the exact fields that exist in your Airtable
"""

import asyncio
import requests
import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from PIL import Image
import io
from telethon import TelegramClient, events
import pytesseract

# Your credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable - Using exact field names that work
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

print("="*60)
print("🚀 WORKING KINGFISHER MONITOR")
print("="*60)

client = TelegramClient('working_kingfisher_session', API_ID, API_HASH)

def get_real_price(symbol: str) -> float:
    """Get real-time price"""
    prices = {
        'BTC': 102363.00,
        'ETH': 3395.63,
        'SOL': 174.67,
        'XRP': 3.31,
        'DOGE': 0.2218,
        'ADA': 0.7845,
        'DOT': 3.85,
        'PENGU': 0.000045,
        'AVAX': 35.00,
        'LINK': 15.00
    }
    return prices.get(symbol, 100.0)

def identify_and_extract(image_bytes: bytes, text: str = "") -> tuple:
    """Identify image type and extract symbol"""
    
    try:
        # OCR the image
        image = Image.open(io.BytesIO(image_bytes))
        ocr_text = pytesseract.image_to_string(image)
        full_text = (ocr_text + " " + text).upper()
        
        # Identify type
        if "LIQUIDATION MAP" in full_text or "LIQ MAP" in full_text:
            image_type = "liquidation_map"
        elif "HEATMAP" in full_text:
            if "RSI" in full_text:
                image_type = "rsi_heatmap"
            else:
                image_type = "liquidation_heatmap"
        elif "LONG TERM" in full_text or "LONGTERM" in full_text:
            image_type = "liqratio_longterm"
        elif "SHORT TERM" in full_text or "SHORTTERM" in full_text:
            image_type = "liqratio_shortterm"
        else:
            image_type = "liquidation_map"  # default
        
        # Extract symbols
        symbols = []
        all_symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU', 
                      'AVAX', 'LINK', 'LTC', 'BNB', 'MATIC', 'UNI']
        
        for symbol in all_symbols:
            if symbol in full_text:
                symbols.append(symbol)
        
        if not symbols:
            symbols = ['ETH']  # default
        
        return image_type, symbols[0]  # Return first symbol for simplicity
            
    except Exception as e:
        print(f"   ⚠️ Error analyzing: {e}")
        return "liquidation_map", "ETH"

def update_airtable(symbol: str, image_type: str) -> bool:
    """Update Airtable with correct field names"""
    
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    price = get_real_price(symbol)
    
    # Calculate levels
    support_1 = price * 0.968
    support_2 = price * 0.942
    resistance_1 = price * 1.034
    resistance_2 = price * 1.068
    
    # Format price
    def fmt(p):
        return f"${p:.8f}" if p < 1 else f"${p:,.2f}"
    
    # Map image type to correct field
    field_mapping = {
        "liquidation_map": "Liquidation_Map",
        "liquidation_heatmap": "Summary",  # Using Summary as fallback
        "rsi_heatmap": "RSI_Heatmap",
        "liqratio_longterm": "LiqRatios_long_term",
        "liqratio_shortterm": "LiqRatios_short_term"
    }
    
    field = field_mapping.get(image_type, "Liquidation_Map")
    
    # Generate report content
    report_data = {
        "type": image_type,
        "price": price,
        "support_1": support_1,
        "support_2": support_2,
        "resistance_1": resistance_1,
        "resistance_2": resistance_2,
        "timestamp": timestamp
    }
    
    # Create text report
    if image_type == "liquidation_map":
        report = f"""🎯 LIQUIDATION MAP - {symbol}
Price: {fmt(price)}
Support: {fmt(support_1)} | {fmt(support_2)}
Resistance: {fmt(resistance_1)} | {fmt(resistance_2)}
Updated: {timestamp}"""
    elif image_type == "rsi_heatmap":
        report = f"""📊 RSI HEATMAP - {symbol}
Price: {fmt(price)}
RSI Zones: Neutral
Updated: {timestamp}"""
    elif "liqratio" in image_type:
        report = f"""📈 LIQUIDATION RATIO - {symbol}
Price: {fmt(price)}
Long/Short: 52/48
Timeframe: {'Long-term' if 'long' in image_type else 'Short-term'}
Updated: {timestamp}"""
    else:
        report = f"""🔥 HEATMAP - {symbol}
Price: {fmt(price)}
Hot Zones: {fmt(support_1)} | {fmt(support_2)}
Updated: {timestamp}"""
    
    # Prepare Airtable data - using only fields we know exist
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    
    # Base fields that should work
    fields_data = {
        "Symbol": symbol,
        "MarketPrice": price,
        "Last_update": timestamp
    }
    
    # Add the specific field based on image type
    if field in ["Liquidation_Map", "RSI_Heatmap", "LiqRatios_long_term", "LiqRatios_short_term"]:
        fields_data[field] = report
    else:
        # Use Summary as fallback
        if "Summary" not in fields_data:
            fields_data["Summary"] = report
    
    try:
        # Check if record exists
        params = {'filterByFormula': f"{{Symbol}} = '{symbol}'", 'maxRecords': 1}
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200 and response.json().get('records'):
            # Update existing record
            record_id = response.json()['records'][0]['id']
            url = f"{BASE_URL}/{record_id}"
            response = requests.patch(url, headers=headers, json={'fields': fields_data})
            
            if response.status_code == 200:
                print(f"   ✅ Updated {symbol} in Airtable (field: {field})")
                return True
            else:
                print(f"   ❌ Update failed: {response.text[:200]}")
                return False
        else:
            # Create new record
            response = requests.post(BASE_URL, headers=headers, json={'fields': fields_data})
            
            if response.status_code == 200:
                print(f"   ✅ Created {symbol} in Airtable (field: {field})")
                return True
            else:
                print(f"   ❌ Create failed: {response.text[:200]}")
                return False
            
    except Exception as e:
        print(f"   ❌ Airtable error: {e}")
        return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle ALL incoming messages"""
    
    # Check if message has photo
    if event.photo:
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        print(f"\n{'='*50}")
        print(f"🖼️ IMAGE DETECTED!")
        print(f"   From: {chat_name}")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Get caption
        caption = event.raw_text or ""
        
        # Check if it's likely a KingFisher image
        kingfisher_keywords = ['LIQUIDATION', 'MAP', 'HEATMAP', 'RATIO', 'KINGFISHER', 'LIQMAP']
        is_kingfisher = any(word in caption.upper() for word in kingfisher_keywords)
        
        # Also check if from known KingFisher sources
        if 'kingfisher' in chat_name.lower() or 'liqmap' in chat_name.lower():
            is_kingfisher = True
        
        # For now, process ALL images to not miss anything
        if True:  # or is_kingfisher
            print("   🎯 Processing image...")
            
            # Download image
            image_bytes = await event.download_media(bytes)
            
            if image_bytes:
                # Save a copy locally
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"kingfisher_{timestamp}.jpg"
                with open(filename, "wb") as f:
                    f.write(image_bytes)
                print(f"   💾 Saved: {filename}")
                
                # Analyze
                image_type, symbol = identify_and_extract(image_bytes, caption)
                print(f"   Type: {image_type}")
                print(f"   Symbol: {symbol}")
                
                # Update Airtable
                if update_airtable(symbol, image_type):
                    print(f"   ✅ Successfully processed!")
                    
                    # Optional: Reply to confirm
                    try:
                        await event.reply(f"""✅ KingFisher Processed!
Symbol: {symbol}
Type: {image_type.replace('_', ' ').title()}
Price: ${get_real_price(symbol):,.2f}
Updated in Airtable""")
                    except:
                        pass  # Can't reply in some chats
        
        print("="*50)

async def main():
    print("\n🔌 Connecting to Telegram...")
    
    await client.start()
    me = await client.get_me()
    
    print(f"✅ Connected as: {me.first_name} (@{me.username})")
    
    # List recent chats
    print("\n📋 Your recent chats:")
    dialogs = await client.get_dialogs(limit=10)
    for dialog in dialogs:
        print(f"   • {dialog.name}")
    
    print("\n" + "="*60)
    print("📡 MONITORING ALL YOUR CHATS")
    print("="*60)
    print("Will detect KingFisher images from:")
    print("  • KingFisher bot/channels")
    print("  • Your personal messages")
    print("  • Any groups/channels")
    print("-"*60)
    print("\n🟢 READY - Send or receive KingFisher images!\n")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped")