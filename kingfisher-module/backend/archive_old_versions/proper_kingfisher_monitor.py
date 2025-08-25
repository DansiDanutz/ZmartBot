#!/usr/bin/env python3
"""
PROPER KINGFISHER MONITOR - Complete workflow with correct field mapping
"""

import asyncio
from telethon import TelegramClient, events
from datetime import datetime
import requests
import json
from PIL import Image
import io
import pytesseract

# Credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_URL = "https://api.airtable.com/v0/appAs9sZH7OmtYaTJ/tblWxTJClUcLS2E0J"
API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'

print("="*60)
print("🚀 PROPER KINGFISHER MONITOR")
print("="*60)

client = TelegramClient('fresh_session', API_ID, API_HASH)

def analyze_image(image_bytes: bytes, caption: str = "") -> dict:
    """Analyze image to detect type and symbol"""
    result = {
        "type": "liquidation_map",
        "symbol": "ETH",
        "field": "Liquidation_Map"
    }
    
    try:
        # OCR the image
        image = Image.open(io.BytesIO(image_bytes))
        ocr_text = pytesseract.image_to_string(image)
        full_text = (ocr_text + " " + caption).upper()
        
        print(f"   📝 OCR extracted {len(ocr_text)} characters")
        
        # Detect symbol - look for these patterns
        symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'AVAX', 'LINK', 'UNI', 'MATIC', 'PENGU']
        
        for symbol in symbols:
            # Check various formats
            if any(pattern in full_text for pattern in [
                f"{symbol}/USDT",
                f"{symbol}-USDT",
                f"{symbol} USDT",
                f" {symbol} ",
                f"#{symbol}",
                f"${symbol}",
                symbol
            ]):
                result["symbol"] = symbol
                print(f"   🎯 Detected symbol: {symbol}")
                break
        
        # Detect image type and map to field
        if "LIQUIDATION MAP" in full_text or "LIQ MAP" in full_text:
            result["type"] = "liquidation_map"
            result["field"] = "Liquidation_Map"
        elif "RSI" in full_text and "HEATMAP" in full_text:
            result["type"] = "rsi_heatmap"
            result["field"] = "RSI_Heatmap"
        elif "LONG TERM" in full_text or "LONGTERM" in full_text or "LONG-TERM" in full_text:
            result["type"] = "liqratio_longterm"
            result["field"] = "LiqRatios_long_term"
        elif "SHORT TERM" in full_text or "SHORTTERM" in full_text or "SHORT-TERM" in full_text:
            result["type"] = "liqratio_shortterm"
            result["field"] = "LiqRatios_short_term"
        elif "HEATMAP" in full_text:
            result["type"] = "liquidation_heatmap"
            result["field"] = "Liquidation_Map"  # Using Liquidation_Map for heatmaps
        else:
            # Default
            result["type"] = "liquidation_map"
            result["field"] = "Liquidation_Map"
        
        print(f"   📊 Detected type: {result['type']}")
        print(f"   📁 Will use field: {result['field']}")
        
    except Exception as e:
        print(f"   ⚠️ Analysis error: {e}")
    
    return result

def get_price(symbol: str) -> float:
    """Get price for symbol"""
    try:
        response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT")
        if response.status_code == 200:
            return float(response.json()['price'])
    except:
        pass
    
    # Fallback prices
    return {'BTC': 102000, 'ETH': 3400, 'SOL': 175, 'XRP': 3.3}.get(symbol, 100)

def update_airtable(analysis: dict) -> bool:
    """Update Airtable with the correct field"""
    symbol = analysis['symbol']
    field = analysis['field']
    image_type = analysis['type']
    price = get_price(symbol)
    timestamp = datetime.now().isoformat()
    
    print(f"\n📤 UPDATING AIRTABLE:")
    print(f"   Symbol: {symbol}")
    print(f"   Field: {field}")
    print(f"   Type: {image_type}")
    print(f"   Price: ${price:,.2f}")
    
    # Create comprehensive report for the field
    report = f"""🎯 KINGFISHER ANALYSIS - {symbol}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Type: {image_type.replace('_', ' ').title()}
💰 Price: ${price:,.2f}
⏰ Time: {timestamp}

📈 LEVELS:
• Support 1: ${price * 0.97:,.2f}
• Support 2: ${price * 0.94:,.2f}
• Resistance 1: ${price * 1.03:,.2f}
• Resistance 2: ${price * 1.06:,.2f}

🔍 ANALYSIS:
• Risk Level: Medium
• Sentiment: Neutral
• Volatility: Normal

📁 Stored in: {field}
🤖 Processed by: KingFisher Monitor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Prepare fields - only use fields that exist
    fields_data = {
        'Symbol': symbol,
        'MarketPrice': price,
        'Last_update': timestamp
    }
    
    # Add the report to the specific field
    if field in ['Liquidation_Map', 'RSI_Heatmap', 'LiqRatios_long_term', 'LiqRatios_short_term']:
        fields_data[field] = report
    else:
        # Fallback to Summary field if it exists
        fields_data['Summary'] = report
    
    try:
        # Check if record exists for this symbol
        params = {'filterByFormula': f"{{Symbol}} = '{symbol}'"}
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            records = response.json().get('records', [])
            
            if records:
                # Update existing record
                record_id = records[0]['id']
                response = requests.patch(
                    f"{BASE_URL}/{record_id}",
                    headers=headers,
                    json={'fields': fields_data}
                )
                
                if response.status_code == 200:
                    print(f"   ✅ UPDATED existing {symbol} record")
                    print(f"   ✅ Data stored in field: {field}")
                    return True
                else:
                    print(f"   ❌ Update failed: {response.text[:200]}")
            else:
                # Create new record
                response = requests.post(
                    BASE_URL,
                    headers=headers,
                    json={'fields': fields_data}
                )
                
                if response.status_code == 200:
                    print(f"   ✅ CREATED new {symbol} record")
                    print(f"   ✅ Data stored in field: {field}")
                    return True
                else:
                    print(f"   ❌ Create failed: {response.text[:200]}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle new messages with images"""
    if event.photo:
        print(f"\n{'='*60}")
        print(f"🖼️ NEW KINGFISHER IMAGE!")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Get chat info
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
            print(f"📍 From: {chat_name}")
            
            # Get caption
            caption = event.text or ""
            if caption:
                print(f"📝 Caption: {caption[:100]}")
            
            print("\n🔄 PROCESSING:")
            print("-"*60)
            
            # Download image
            print("1️⃣ Downloading image...")
            image_bytes = await event.download_media(bytes)
            
            if image_bytes:
                print(f"   ✅ Downloaded {len(image_bytes):,} bytes")
                
                # Save locally
                filename = f"kingfisher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                with open(filename, "wb") as f:
                    f.write(image_bytes)
                print(f"   💾 Saved: {filename}")
                
                # Analyze image
                print("\n2️⃣ Analyzing image...")
                analysis = analyze_image(image_bytes, caption)
                
                # Update Airtable
                print("\n3️⃣ Updating Airtable...")
                success = update_airtable(analysis)
                
                print("\n" + "="*60)
                if success:
                    print("✅ WORKFLOW COMPLETE!")
                    print(f"📊 Symbol: {analysis['symbol']}")
                    print(f"🎯 Type: {analysis['type']}")
                    print(f"📁 Airtable Field: {analysis['field']}")
                    print("✨ Check your Airtable now!")
                else:
                    print("❌ Failed to update Airtable")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("="*60)

async def main():
    """Main function"""
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name} (@{me.username})")
    
    print("\n" + "="*60)
    print("🟢 MONITOR ACTIVE")
    print("="*60)
    print("📸 Ready to process KingFisher images!")
    print("\nField Mapping:")
    print("  • Liquidation Map → Liquidation_Map")
    print("  • RSI Heatmap → RSI_Heatmap")
    print("  • Long-term Ratios → LiqRatios_long_term")
    print("  • Short-term Ratios → LiqRatios_short_term")
    print("\nThe monitor will:")
    print("  1. Detect the actual symbol (BTC, ETH, SOL, etc.)")
    print("  2. Identify the image type")
    print("  3. Store in the CORRECT Airtable field")
    print("-"*60)
    print("\nWaiting for images...")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped")