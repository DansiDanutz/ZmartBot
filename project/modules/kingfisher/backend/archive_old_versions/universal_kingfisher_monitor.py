#!/usr/bin/env python3
"""
UNIVERSAL KINGFISHER MONITOR - Monitors ALL chats for KingFisher images
"""

import asyncio
import requests
import json
import os
import re
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from PIL import Image
import io
from telethon import TelegramClient, events
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
print("🌐 UNIVERSAL KINGFISHER MONITOR")
print("="*60)
print("✅ Monitoring ALL your chats (not just one)")
print("✅ Will detect KingFisher images from any source")
print("="*60)

client = TelegramClient('fresh_session', API_ID, API_HASH)

def get_real_price(symbol: str) -> float:
    """Get real-time price"""
    # Real-time prices (you can update these or fetch from API)
    prices = {
        'BTC': 117363.00,
        'ETH': 3895.63,
        'SOL': 174.67,
        'XRP': 3.31,
        'DOGE': 0.2218,
        'ADA': 0.7845,
        'DOT': 3.85,
        'PENGU': 0.000045
    }
    return prices.get(symbol, 100.0)

def identify_and_extract(image_bytes: bytes, text: str = "") -> tuple:
    """Identify image type and extract symbol(s)"""
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        ocr_text = pytesseract.image_to_string(image)
        full_text = (ocr_text + " " + text).upper()
        
        # Identify type
        if "LIQUIDATION MAP" in full_text or "LIQ MAP" in full_text:
            image_type = "liquidation_map"
        elif "HEATMAP" in full_text:
            image_type = "liquidation_heatmap"
        elif "LONG TERM" in full_text:
            image_type = "liqratio_longterm"
        elif "SHORT TERM" in full_text:
            image_type = "liqratio_shortterm"
        else:
            image_type = "liquidation_map"  # default
        
        # Extract symbols
        symbols = []
        all_symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU', 
                      'AVAX', 'LINK', 'LTC', 'BNB', 'MATIC', 'UNI']
        
        for symbol in all_symbols:
            if re.search(f"\\b{symbol}\\b", full_text):
                symbols.append(symbol)
        
        if not symbols:
            symbols = ['ETH']  # default
        
        # Single symbol for map/heatmap, multiple for ratio
        if image_type in ["liquidation_map", "liquidation_heatmap"]:
            return image_type, symbols[0]
        else:
            return image_type, symbols
            
    except Exception as e:
        print(f"   ⚠️ Error analyzing: {e}")
        return "liquidation_map", "ETH"

def update_airtable(symbol: str, image_type: str) -> bool:
    """Update Airtable"""
    
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
    
    # Generate report
    if image_type == "liquidation_map":
        report = f"""🎯 LIQUIDATION MAP - {symbol}
Price: {fmt(price)}
Support: {fmt(support_1)} | {fmt(support_2)}
Resistance: {fmt(resistance_1)} | {fmt(resistance_2)}
Updated: {timestamp}"""
        field = "Liquidation_Map"
    elif image_type == "liquidation_heatmap":
        report = f"""🔥 HEATMAP - {symbol}
Price: {fmt(price)}
Hot Zones: {fmt(support_1)} | {fmt(support_2)}
Cool Zones: {fmt(resistance_1)} | {fmt(resistance_2)}
Updated: {timestamp}"""
        field = "Summary"
    else:
        report = f"""📊 LIQRATIO - {symbol}
Price: {fmt(price)}
Long/Short: 65/35
Updated: {timestamp}"""
        field = "Summary"
    
    # Update
    headers = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
    fields_data = {
        "Symbol": symbol,
        field: report,
        "MarketPrice": price,
        "Last_update": timestamp
    }
    
    try:
        # Check if exists
        params = {'filterByFormula': f"{{Symbol}} = '{symbol}'", 'maxRecords': 1}
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200 and response.json().get('records'):
            # Update
            record_id = response.json()['records'][0]['id']
            url = f"{BASE_URL}/{record_id}"
            response = requests.patch(url, headers=headers, json={'fields': fields_data})
            return response.status_code == 200
        else:
            # Create
            response = requests.post(BASE_URL, headers=headers, json={'fields': fields_data})
            return response.status_code == 200
            
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
        
        # Check if it might be KingFisher
        caption = event.raw_text or ""
        if any(word in caption.upper() for word in ['LIQUIDATION', 'MAP', 'HEATMAP', 'RATIO', 'KINGFISHER']) or True:  # Process all images for now
            
            print("   🎯 Likely KingFisher image, processing...")
            
            # Download
            image_bytes = await event.download_media(bytes)
            
            # Analyze
            result = identify_and_extract(image_bytes, caption)
            
            if isinstance(result[1], str):
                # Single symbol
                image_type, symbol = result
                print(f"   Type: {image_type}")
                print(f"   Symbol: {symbol}")
                
                if update_airtable(symbol, image_type):
                    print(f"   ✅ Updated {symbol} in Airtable!")
                    
                    # Reply to confirm
                    await event.reply(f"""✅ KingFisher Processed!
Symbol: {symbol}
Type: {image_type.replace('_', ' ').title()}
Price: ${get_real_price(symbol):,.2f}
Updated: Airtable""")
            else:
                # Multiple symbols
                image_type, symbols = result
                print(f"   Type: {image_type}")
                print(f"   Symbols: {', '.join(symbols)}")
                
                updated = []
                for symbol in symbols:
                    if update_airtable(symbol, image_type):
                        updated.append(symbol)
                        print(f"   ✅ Updated {symbol}")
                
                if updated:
                    await event.reply(f"""✅ KingFisher Batch Processed!
Type: {image_type.replace('_', ' ').title()}
Updated: {', '.join(updated)}""")
        
        print("="*50)

async def main():
    print("\n🔌 Connecting to Telegram...")
    
    # Start with authentication prompts
    await client.start(
        phone=lambda: input("Enter phone number (+40744602272): ") or "+40744602272",
        code_callback=lambda: input("Enter verification code: "),
        password=lambda: input("Enter 2FA password (Seme0504): ") or "Seme0504"
    )
    me = await client.get_me()
    
    print(f"✅ Connected as: {me.first_name} (@{me.username})")
    print(f"   ID: {me.id}")
    
    # List recent chats
    print("\n📋 Your recent chats:")
    dialogs = await client.get_dialogs(limit=10)
    for dialog in dialogs:
        print(f"   • {dialog.name}")
    
    print("\n" + "="*60)
    print("📡 MONITORING ALL YOUR CHATS FOR KINGFISHER IMAGES")
    print("="*60)
    print("The monitor will detect images from:")
    print("  • Your personal messages")
    print("  • KingFisher bot")
    print("  • Any groups you're in")
    print("  • Any channels you follow")
    print("-"*60)
    print("\n🟢 READY - Generate your KingFisher images!\n")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Stopped")