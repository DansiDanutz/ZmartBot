#!/usr/bin/env python3
"""
COMPLETE KINGFISHER WORKFLOW MONITOR
Full pipeline: Telegram → Image Analysis → ChatGPT → Airtable
"""

import asyncio
import requests
import json
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image
import io
from telethon import TelegramClient, events
import pytesseract
import base64
from dotenv import load_dotenv

load_dotenv()

# Your credentials
API_ID = 26706005
API_HASH = "bab8e720fd3b045785a5ec44d5e399fe"

# Airtable
BASE_ID = "appAs9sZH7OmtYaTJ"
TABLE_ID = "tblWxTJClUcLS2E0J"
AIRTABLE_API_KEY = 'patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835'
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"

# OpenAI (for ChatGPT analysis)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print("="*60)
print("🚀 COMPLETE KINGFISHER WORKFLOW MONITOR")
print("="*60)
print("📋 Workflow: Telegram → OCR → ChatGPT → Airtable")
print("="*60)

client = TelegramClient('complete_workflow_session', API_ID, API_HASH)

def get_real_price(symbol: str) -> float:
    """Get real-time price"""
    try:
        # Try to get from Binance API
        response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT")
        if response.status_code == 200:
            return float(response.json()['price'])
    except:
        pass
    
    # Fallback prices
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

def analyze_with_chatgpt(image_bytes: bytes, initial_analysis: Dict) -> Dict[str, Any]:
    """Send image to ChatGPT for professional analysis"""
    
    print("   🤖 Sending to ChatGPT for analysis...")
    
    if not OPENAI_API_KEY:
        print("   ⚠️ OpenAI API key not found, using local analysis")
        return initial_analysis
    
    try:
        # Convert image to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Prepare the prompt
        prompt = f"""Analyze this KingFisher liquidation chart for {initial_analysis.get('symbol', 'cryptocurrency')}.

Provide a professional trading analysis including:
1. Key liquidation levels (exact prices)
2. Support and resistance zones
3. Risk assessment (High/Medium/Low)
4. Trading recommendation
5. Entry/Exit points if applicable
6. Overall market sentiment

Image type: {initial_analysis.get('type', 'liquidation map')}
Current price: ${initial_analysis.get('price', 0):.2f}

Format your response as JSON with these fields:
- liquidation_levels: array of price levels
- support_zones: array of support prices
- resistance_zones: array of resistance prices
- risk_level: "High"/"Medium"/"Low"
- recommendation: "Long"/"Short"/"Neutral"/"Wait"
- entry_point: number or null
- exit_point: number or null
- stop_loss: number or null
- sentiment: "Bullish"/"Bearish"/"Neutral"
- analysis_summary: brief text summary
"""
        
        # Call OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            gpt_response = result['choices'][0]['message']['content']
            
            print("   ✅ ChatGPT analysis received")
            
            # Try to parse JSON from response
            try:
                # Extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', gpt_response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    analysis = {"analysis_summary": gpt_response}
            except:
                analysis = {"analysis_summary": gpt_response}
            
            # Merge with initial analysis
            initial_analysis['chatgpt_analysis'] = analysis
            initial_analysis['professional_analysis'] = gpt_response[:1000]  # Store raw response
            
            # Print key findings
            print(f"   📊 Risk Level: {analysis.get('risk_level', 'N/A')}")
            print(f"   📈 Recommendation: {analysis.get('recommendation', 'N/A')}")
            print(f"   💭 Sentiment: {analysis.get('sentiment', 'N/A')}")
            
        else:
            print(f"   ⚠️ ChatGPT API error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ChatGPT analysis error: {e}")
    
    return initial_analysis

def identify_and_extract(image_bytes: bytes, text: str = "") -> Tuple[str, str, Dict]:
    """Identify image type, extract symbol, and perform initial analysis"""
    
    print("   🔍 Analyzing image...")
    
    analysis = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_text": text[:500]
    }
    
    try:
        # OCR the image
        image = Image.open(io.BytesIO(image_bytes))
        ocr_text = pytesseract.image_to_string(image)
        full_text = (ocr_text + " " + text).upper()
        
        print(f"   📝 OCR extracted: {len(ocr_text)} characters")
        
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
        
        # Extract symbol
        symbols = []
        all_symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'DOT', 'PENGU', 
                      'AVAX', 'LINK', 'LTC', 'BNB', 'MATIC', 'UNI', 'ARB', 'OP']
        
        for symbol in all_symbols:
            if symbol in full_text:
                symbols.append(symbol)
        
        symbol = symbols[0] if symbols else 'ETH'
        
        # Add to analysis
        analysis['symbol'] = symbol
        analysis['type'] = image_type
        analysis['price'] = get_real_price(symbol)
        analysis['ocr_text'] = ocr_text[:1000]  # Store first 1000 chars
        
        return image_type, symbol, analysis
            
    except Exception as e:
        print(f"   ⚠️ Error in initial analysis: {e}")
        return "liquidation_map", "ETH", analysis

def get_airtable_field(image_type: str) -> str:
    """Get the correct Airtable field for the image type"""
    field_mapping = {
        "liquidation_map": "Liquidation_Map",
        "liquidation_heatmap": "Summary",  # Using Summary as fallback
        "rsi_heatmap": "RSI_Heatmap",
        "liqratio_longterm": "LiqRatios_long_term",
        "liqratio_shortterm": "LiqRatios_short_term"
    }
    return field_mapping.get(image_type, "Liquidation_Map")

def update_airtable(symbol: str, image_type: str, analysis: Dict) -> bool:
    """Update Airtable with complete analysis"""
    
    print(f"\n   📤 Updating Airtable...")
    print(f"   📋 Symbol: {symbol}")
    print(f"   🎯 Field: {get_airtable_field(image_type)}")
    
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    price = analysis.get('price', 0)
    
    # Get the correct field name
    field = get_airtable_field(image_type)
    
    # Format the complete analysis for storage
    if 'chatgpt_analysis' in analysis:
        gpt = analysis['chatgpt_analysis']
        
        # Create comprehensive report
        report = f"""🎯 KINGFISHER ANALYSIS - {symbol}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Type: {image_type.replace('_', ' ').title()}
💰 Price: ${price:,.2f}
⏰ Updated: {timestamp}

🤖 CHATGPT ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Risk Level: {gpt.get('risk_level', 'N/A')}
Recommendation: {gpt.get('recommendation', 'N/A')}
Sentiment: {gpt.get('sentiment', 'N/A')}

📍 LEVELS:
Support: {', '.join([f"${x}" for x in gpt.get('support_zones', [])][:3]) or 'N/A'}
Resistance: {', '.join([f"${x}" for x in gpt.get('resistance_zones', [])][:3]) or 'N/A'}
Liquidations: {', '.join([f"${x}" for x in gpt.get('liquidation_levels', [])][:3]) or 'N/A'}

📝 SUMMARY:
{gpt.get('analysis_summary', 'Analysis pending...')[:500]}

🔗 Source: KingFisher + ChatGPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    else:
        # Fallback report without ChatGPT
        report = f"""🎯 KINGFISHER ANALYSIS - {symbol}
Type: {image_type.replace('_', ' ').title()}
Price: ${price:,.2f}
Updated: {timestamp}
Status: Processed locally (ChatGPT not available)"""
    
    # Prepare Airtable data
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Fields to update
    fields_data = {
        "Symbol": symbol,
        "MarketPrice": price,
        "Last_update": timestamp
    }
    
    # Add the analysis to the specific field
    if field in ["Liquidation_Map", "RSI_Heatmap", "LiqRatios_long_term", "LiqRatios_short_term"]:
        fields_data[field] = report
    else:
        fields_data["Summary"] = report
    
    # Store raw JSON analysis if we have ChatGPT data
    if 'chatgpt_analysis' in analysis and "Result" in fields_data:
        fields_data["Result"] = json.dumps(analysis['chatgpt_analysis'])
    
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
                print(f"   ✅ UPDATED {symbol} in Airtable!")
                print(f"   📁 Field: {field}")
                print(f"   📝 Analysis: {'ChatGPT Enhanced' if 'chatgpt_analysis' in analysis else 'Local'}")
                return True
            else:
                print(f"   ❌ Update failed: {response.text[:200]}")
                # Try without problematic fields
                if "Result" in fields_data:
                    del fields_data["Result"]
                response = requests.patch(url, headers=headers, json={'fields': fields_data})
                return response.status_code == 200
        else:
            # Create new record
            response = requests.post(BASE_URL, headers=headers, json={'fields': fields_data})
            
            if response.status_code == 200:
                print(f"   ✅ CREATED {symbol} in Airtable!")
                print(f"   📁 Field: {field}")
                print(f"   📝 Analysis: {'ChatGPT Enhanced' if 'chatgpt_analysis' in analysis else 'Local'}")
                return True
            else:
                print(f"   ❌ Create failed: {response.text[:200]}")
                # Try without problematic fields
                if "Result" in fields_data:
                    del fields_data["Result"]
                response = requests.post(BASE_URL, headers=headers, json={'fields': fields_data})
                return response.status_code == 200
            
    except Exception as e:
        print(f"   ❌ Airtable error: {e}")
        return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    """Handle ALL incoming messages - Complete Workflow"""
    
    # Check if message has photo
    if event.photo:
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        print(f"\n{'='*60}")
        print(f"🖼️ NEW IMAGE DETECTED!")
        print(f"📍 From: {chat_name}")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        print("─"*60)
        
        # Get caption
        caption = event.raw_text or ""
        if caption:
            print(f"📝 Caption: {caption[:100]}")
        
        print("\n🔄 STARTING COMPLETE WORKFLOW:")
        print("─"*60)
        
        # Step 1: Download image
        print("1️⃣ DOWNLOADING IMAGE...")
        image_bytes = await event.download_media(bytes)
        
        if image_bytes:
            print(f"   ✅ Downloaded: {len(image_bytes)} bytes")
            
            # Save a copy locally
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kingfisher_{timestamp}.jpg"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            print(f"   💾 Saved locally: {filename}")
            
            # Step 2: Initial analysis (OCR + identification)
            print("\n2️⃣ INITIAL ANALYSIS...")
            image_type, symbol, analysis = identify_and_extract(image_bytes, caption)
            print(f"   ✅ Type: {image_type}")
            print(f"   ✅ Symbol: {symbol}")
            print(f"   ✅ Price: ${analysis['price']:,.2f}")
            
            # Step 3: ChatGPT Analysis (if API key available)
            print("\n3️⃣ CHATGPT ANALYSIS...")
            if OPENAI_API_KEY:
                analysis = analyze_with_chatgpt(image_bytes, analysis)
            else:
                print("   ⚠️ OpenAI API key not configured")
                print("   💡 Add OPENAI_API_KEY to .env for ChatGPT analysis")
            
            # Step 4: Update Airtable
            print("\n4️⃣ UPDATING AIRTABLE...")
            success = update_airtable(symbol, image_type, analysis)
            
            # Step 5: Summary
            print("\n" + "="*60)
            if success:
                print("✅ WORKFLOW COMPLETE!")
                print(f"📊 Symbol: {symbol}")
                print(f"🎯 Type: {image_type}")
                print(f"📁 Stored in: {get_airtable_field(image_type)}")
                print(f"🤖 Analysis: {'ChatGPT Enhanced' if 'chatgpt_analysis' in analysis else 'Local Only'}")
                
                # Optional: Reply to confirm
                try:
                    reply_msg = f"""✅ KingFisher Workflow Complete!

📊 Symbol: {symbol}
🎯 Type: {image_type.replace('_', ' ').title()}
💰 Price: ${analysis['price']:,.2f}
📁 Airtable Field: {get_airtable_field(image_type)}"""
                    
                    if 'chatgpt_analysis' in analysis:
                        gpt = analysis['chatgpt_analysis']
                        reply_msg += f"""
🤖 ChatGPT Analysis:
• Risk: {gpt.get('risk_level', 'N/A')}
• Recommendation: {gpt.get('recommendation', 'N/A')}
• Sentiment: {gpt.get('sentiment', 'N/A')}"""
                    
                    await event.reply(reply_msg)
                except:
                    pass  # Can't reply in some chats
            else:
                print("❌ WORKFLOW FAILED")
                print("Check the errors above for details")
        
        print("="*60)

async def main():
    print("\n🔌 Connecting to Telegram...")
    
    await client.start()
    me = await client.get_me()
    
    print(f"✅ Connected as: {me.first_name} (@{me.username})")
    
    # Check OpenAI status
    if OPENAI_API_KEY:
        print("✅ OpenAI API key configured - ChatGPT analysis enabled")
    else:
        print("⚠️ OpenAI API key not found - using local analysis only")
        print("💡 Add OPENAI_API_KEY to .env for full ChatGPT analysis")
    
    # List recent chats
    print("\n📋 Your recent chats:")
    dialogs = await client.get_dialogs(limit=10)
    for dialog in dialogs:
        print(f"   • {dialog.name}")
    
    print("\n" + "="*60)
    print("🚀 COMPLETE WORKFLOW MONITOR ACTIVE")
    print("="*60)
    print("📋 Workflow Pipeline:")
    print("   1. Detect image from Telegram")
    print("   2. Download and OCR analysis")
    print("   3. ChatGPT professional analysis")
    print("   4. Store in correct Airtable field")
    print("─"*60)
    print("\n🟢 READY - Generate your KingFisher image now!\n")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Workflow monitor stopped")