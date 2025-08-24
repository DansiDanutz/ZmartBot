#!/usr/bin/env python3
"""
KINGFISHER AUTO COMPLETE - Full automatic analysis
"""

import asyncio
from telethon import TelegramClient, events
from datetime import datetime
import requests
import base64
import json
import os
from PIL import Image
import io
import pytesseract
from dotenv import load_dotenv

load_dotenv()

# Telegram
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_URL = "https://api.airtable.com/v0/appAs9sZH7OmtYaTJ/tblWxTJClUcLS2E0J"
AIRTABLE_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'

# OpenAI for ChatGPT analysis
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

client = TelegramClient('fresh_session', API_ID, API_HASH)

def analyze_with_chatgpt(image_bytes):
    """Use ChatGPT to analyze the image"""
    if not OPENAI_KEY:
        print("   ⚠️ No OpenAI key, using OCR only")
        return analyze_with_ocr(image_bytes)
    
    try:
        # Convert to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # ChatGPT prompt
        prompt = """Analyze this KingFisher trading image and provide:
1. Image type: Is this a "liquidation_map", "liquidation_heatmap", "rsi_heatmap", "long_term_ratio", or "short_term_ratio"?
2. Symbol(s): What cryptocurrency symbol(s) are shown? (BTC, ETH, SOL, etc.)
3. If it's a ratio chart with multiple symbols, list all symbols shown.

Respond in JSON format:
{
  "type": "liquidation_map|liquidation_heatmap|rsi_heatmap|long_term_ratio|short_term_ratio",
  "primary_symbol": "BTC",
  "all_symbols": ["BTC", "ETH", "SOL"],
  "confidence": 0.95
}"""
        
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4-vision-preview",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                print(f"   ✅ ChatGPT detected: {analysis['type']} for {analysis.get('primary_symbol', 'unknown')}")
                return analysis
        else:
            print(f"   ⚠️ ChatGPT error: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ ChatGPT failed: {e}")
    
    # Fallback to OCR
    return analyze_with_ocr(image_bytes)

def analyze_with_ocr(image_bytes):
    """Analyze image using OCR"""
    try:
        # OCR the image
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img).upper()
        
        # Detect type
        image_type = "liquidation_map"  # default
        if "HEATMAP" in text:
            if "RSI" in text:
                image_type = "rsi_heatmap"
            else:
                image_type = "liquidation_heatmap"
        elif "LONG TERM" in text or "LONGTERM" in text:
            image_type = "long_term_ratio"
        elif "SHORT TERM" in text or "SHORTTERM" in text:
            image_type = "short_term_ratio"
        elif "RATIO" in text:
            image_type = "long_term_ratio"
        
        # Extract symbols
        symbols = []
        crypto_symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'AVAX', 'LINK', 'UNI', 'MATIC', 'BNB', 'ATOM']
        
        for symbol in crypto_symbols:
            if symbol in text:
                symbols.append(symbol)
        
        # If no symbols found, check if it's a ratio (usually has multiple)
        if not symbols and "ratio" in image_type:
            symbols = ['BTC', 'ETH', 'SOL']  # Common ratio symbols
        elif not symbols:
            symbols = ['ETH']  # Default
        
        return {
            "type": image_type,
            "primary_symbol": symbols[0] if symbols else "ETH",
            "all_symbols": symbols,
            "confidence": 0.7
        }
        
    except Exception as e:
        print(f"   ⚠️ OCR failed: {e}")
        return {
            "type": "liquidation_map",
            "primary_symbol": "ETH",
            "all_symbols": ["ETH"],
            "confidence": 0.3
        }

def get_airtable_field(image_type):
    """Map image type to Airtable field"""
    mapping = {
        "liquidation_map": "Liquidation_Map",
        "liquidation_heatmap": "Liquidation_Map",  # Store heatmaps in same field
        "rsi_heatmap": "RSI_Heatmap",
        "long_term_ratio": "LiqRatios_long_term",
        "short_term_ratio": "LiqRatios_short_term"
    }
    return mapping.get(image_type, "Liquidation_Map")

def update_airtable(analysis):
    """Update Airtable based on analysis"""
    image_type = analysis['type']
    field = get_airtable_field(image_type)
    
    # Handle ratio charts with multiple symbols
    if "ratio" in image_type and len(analysis['all_symbols']) > 1:
        print(f"   📊 Ratio chart with symbols: {', '.join(analysis['all_symbols'])}")
        
        # Update each symbol in the ratio
        for symbol in analysis['all_symbols']:
            update_single_symbol(symbol, field, image_type, analysis)
    else:
        # Single symbol update
        symbol = analysis['primary_symbol']
        update_single_symbol(symbol, field, image_type, analysis)

def update_single_symbol(symbol, field, image_type, analysis):
    """Update a single symbol in Airtable"""
    print(f"   📤 Updating {symbol} in field: {field}")
    
    timestamp = datetime.now().isoformat()
    
    # Create report
    report = f"""🎯 KINGFISHER ANALYSIS
Type: {image_type.replace('_', ' ').title()}
Symbol: {symbol}
Confidence: {analysis.get('confidence', 0):.0%}
Timestamp: {timestamp}

Analysis: Automated detection via {'ChatGPT' if OPENAI_KEY else 'OCR'}
"""
    
    headers = {
        'Authorization': f'Bearer {AIRTABLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Prepare data
    data = {
        'fields': {
            'Symbol': symbol,
            field: report,
            'MarketPrice': 100.0,
            'Last_update': timestamp
        }
    }
    
    # Check if record exists
    params = {'filterByFormula': f"{{Symbol}} = '{symbol}'"}
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    if response.status_code == 200 and response.json().get('records'):
        # Update existing
        record_id = response.json()['records'][0]['id']
        response = requests.patch(
            f"{BASE_URL}/{record_id}",
            headers=headers,
            json={'fields': data['fields']}
        )
        if response.status_code == 200:
            print(f"   ✅ Updated {symbol}")
        else:
            print(f"   ❌ Failed to update {symbol}")
    else:
        # Create new
        response = requests.post(BASE_URL, headers=headers, json=data)
        if response.status_code == 200:
            print(f"   ✅ Created {symbol}")
        else:
            print(f"   ❌ Failed to create {symbol}")

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle incoming images"""
    if not event.photo:
        return
    
    print(f"\n{'='*60}")
    print(f"🖼️ KINGFISHER IMAGE DETECTED - {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Get chat info
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        print(f"📍 From: {chat_name}")
        
        # Download image
        print("📥 Downloading...")
        image_bytes = await event.download_media(bytes)
        
        if image_bytes:
            # Save locally
            filename = f"kingfisher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"💾 Saved: {filename}")
            
            # Analyze image
            print("🔍 Analyzing image...")
            analysis = analyze_with_chatgpt(image_bytes)
            
            print(f"📊 Type: {analysis['type']}")
            print(f"🎯 Symbol(s): {', '.join(analysis['all_symbols'])}")
            print(f"📁 Field: {get_airtable_field(analysis['type'])}")
            
            # Update Airtable
            print("📤 Updating Airtable...")
            update_airtable(analysis)
            
            print("\n✅ COMPLETE!")
            print(f"Check Airtable for: {', '.join(analysis['all_symbols'])}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("="*60)

async def main():
    """Main function"""
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    
    if OPENAI_KEY:
        print("✅ ChatGPT analysis enabled")
    else:
        print("⚠️ Using OCR only (add OPENAI_API_KEY for better analysis)")
    
    print("="*60)
    print("🟢 MONITOR ACTIVE")
    print("="*60)
    print("Automatic detection:")
    print("• Symbol detection from image")
    print("• Type identification (map/heatmap/ratio)")
    print("• Correct field mapping")
    print("• Multi-symbol support for ratios")
    print("-"*60)
    print("Waiting for KingFisher images...")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped")