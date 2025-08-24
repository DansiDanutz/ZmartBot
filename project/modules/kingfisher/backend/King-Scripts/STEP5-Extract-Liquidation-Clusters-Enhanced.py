#!/usr/bin/env python3
"""
STEP 5 ENHANCED: EXTRACT LIQUIDATION CLUSTERS WITH MAXIMUM ACCURACY
- Finds the latest analyzed image from imagesanalysed folders
- Uses ChatGPT to extract EXACT liquidation clusters directly from image
- Updates Airtable with 4 closest clusters (2 below, 2 above current price)
- Ensures minimum 2% distance from current price
- Runs every 5 minutes for continuous updates
"""

import os
import re
import time
import base64
from datetime import datetime, timedelta
from pyairtable import Api
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

# Load environment variables
load_dotenv('../.env')

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'KingFisher')

# Check if Airtable is configured
AIRTABLE_ENABLED = AIRTABLE_API_KEY and AIRTABLE_BASE_ID

# OpenAI setup - King-Image-Telegram key
API_KEYS = [
    "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"
]

# Folders to monitor for images
FOLDERS_TO_MONITOR = [
    "../downloads/LiquidationMap/imagesanalysed",
    "../downloads/LiquidationHeatmap/imagesanalysed"
]

def get_latest_image():
    """Get the most recently modified image from monitored folders"""
    latest_file = None
    latest_time = None
    latest_folder = None
    
    for folder in FOLDERS_TO_MONITOR:
        if not os.path.exists(folder):
            continue
        
        # Get all image files
        image_files = [f for f in os.listdir(folder) 
                      if f.endswith(('.jpg', '.jpeg', '.png')) and os.path.isfile(os.path.join(folder, f))]
        
        for img_file in image_files:
            filepath = os.path.join(folder, img_file)
            file_time = os.path.getmtime(filepath)
            
            if latest_time is None or file_time > latest_time:
                latest_time = file_time
                latest_file = filepath
                latest_folder = folder
    
    return latest_file, latest_folder

def extract_clusters_with_chatgpt(image_path, api_key_index=0):
    """Use ChatGPT to extract exact liquidation clusters from image"""
    
    if api_key_index >= len(API_KEYS):
        return None, None, []
    
    try:
        client = OpenAI(api_key=API_KEYS[api_key_index])
        
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Specialized prompt for exact data extraction
        prompt = """You are analyzing a liquidation map/heatmap image. Extract EXACT numerical data:

CRITICAL TASK: Identify and list ALL liquidation clusters/levels with their EXACT prices.

Please extract:
1. SYMBOL: The exact cryptocurrency symbol (e.g., BTC, ETH, SOL, LINK)
2. CURRENT PRICE: The exact current price shown (e.g., $11.24)
3. ALL LIQUIDATION CLUSTERS: List EVERY liquidation level/cluster you can see with exact prices

For liquidation clusters, look for:
- Horizontal lines on charts
- Color concentrations (blue/red areas in heatmaps)
- Spike patterns in bar charts
- Any price levels with significant liquidation activity
- Support and resistance levels mentioned
- Any prices where liquidations are concentrated

Format your response EXACTLY like this:
SYMBOL: XXX
CURRENT_PRICE: $XXX.XX
LIQUIDATION_CLUSTERS:
$XXX.XX
$XXX.XX
$XXX.XX
(list ALL visible liquidation levels)

Be EXTREMELY precise with numbers. If you see a cluster at $16,059.50, write exactly $16059.50
List EVERY single liquidation level you can identify, from lowest to highest."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.1  # Low temperature for accuracy
        )
        
        # Parse the response
        content = response.choices[0].message.content
        if content:
            print(f"\n   ChatGPT Response Preview:")
            print(f"   {content[:200]}...")  # Show first 200 chars for debugging
        
        # Extract symbol
        symbol_match = re.search(r"SYMBOL:\s*([A-Z]+)", content) if content else None
        symbol = symbol_match.group(1) if symbol_match else None
        
        # Extract current price
        price_match = re.search(r"CURRENT_PRICE:\s*\$?([\d,]+\.?\d*)", content) if content else None
        current_price = None
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            try:
                current_price = float(price_str)
            except:
                pass
        
        # Extract all liquidation clusters
        clusters = []
        lines = content.split('\n') if content else []
        in_clusters = False
        for line in lines:
            if 'LIQUIDATION_CLUSTERS:' in line:
                in_clusters = True
                continue
            if in_clusters:
                # Extract any price from the line
                price_matches = re.findall(r"\$?([\d,]+\.?\d+)", line)
                for match in price_matches:
                    try:
                        price = float(match.replace(',', ''))
                        if 0.01 < price < 1000000:  # Sanity check
                            clusters.append(price)
                    except:
                        continue
        
        # Remove duplicates and sort
        clusters = sorted(list(set(clusters)))
        
        return symbol, current_price, clusters
        
    except Exception as e:
        if "rate_limit" in str(e).lower() and api_key_index < len(API_KEYS) - 1:
            print(f"   ⚠️ Rate limit, trying next API key...")
            time.sleep(2)
            return extract_clusters_with_chatgpt(image_path, api_key_index + 1)
        else:
            print(f"   ❌ ChatGPT error: {e}")
            return None, None, []

def find_closest_clusters(current_price, clusters, min_distance_pct=0.02):
    """Find the 4 closest liquidation clusters with minimum distance requirement"""
    if not clusters or not current_price:
        return None, None, None, None
    
    # Calculate minimum distance
    min_distance = current_price * min_distance_pct
    
    # Separate below and above clusters with minimum distance requirement
    below = [c for c in clusters if c < (current_price - min_distance)]
    above = [c for c in clusters if c > (current_price + min_distance)]
    
    # Sort by distance from current price
    below.sort(key=lambda x: current_price - x)  # Closest first
    above.sort(key=lambda x: x - current_price)   # Closest first
    
    # Get the required clusters
    liqcluster_minus2 = below[1] if len(below) > 1 else None
    liqcluster_minus1 = below[0] if len(below) > 0 else None
    liqcluster_plus1 = above[0] if len(above) > 0 else None
    liqcluster_plus2 = above[1] if len(above) > 1 else None
    
    return liqcluster_minus2, liqcluster_minus1, liqcluster_plus1, liqcluster_plus2

def update_airtable(symbol, current_price, clusters_data):
    """Update Airtable with liquidation cluster data"""
    if not AIRTABLE_ENABLED:
        print(f"   📝 TEST MODE - Would update Airtable for {symbol}")
        return True
    
    try:
        api = Api(AIRTABLE_API_KEY)
        table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Prepare update data
        update_fields = {}
        
        # Add current price
        update_fields['CurrentPrice'] = current_price
        
        # Add liquidation clusters
        if clusters_data[0] is not None:
            update_fields['Liqcluster-2'] = clusters_data[0]
        if clusters_data[1] is not None:
            update_fields['Liqcluster-1'] = clusters_data[1]
        if clusters_data[2] is not None:
            update_fields['Liqcluster1'] = clusters_data[2]
        if clusters_data[3] is not None:
            update_fields['Liqcluster2'] = clusters_data[3]
        
        # Add timestamp
        update_fields['LastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Find record by symbol
        records = table.all(formula=f"{{Symbol}} = '{symbol}'")
        
        if records:
            # Update existing record
            record_id = records[0]['id']
            table.update(record_id, update_fields)
            action = "Updated"
        else:
            # Create new record
            update_fields['Symbol'] = symbol
            table.create(update_fields)
            action = "Created"
        
        print(f"\n✅ {action} Airtable record for {symbol}:")
        print(f"   Current Price: ${current_price:.2f}")
        print(f"   Liqcluster-2: ${clusters_data[0]:.2f}" if clusters_data[0] else "   Liqcluster-2: None")
        print(f"   Liqcluster-1: ${clusters_data[1]:.2f}" if clusters_data[1] else "   Liqcluster-1: None")
        print(f"   Liqcluster+1: ${clusters_data[2]:.2f}" if clusters_data[2] else "   Liqcluster+1: None")
        print(f"   Liqcluster+2: ${clusters_data[3]:.2f}" if clusters_data[3] else "   Liqcluster+2: None")
        print(f"   Updated at: {datetime.now().strftime('%H:%M:%S')}")
        return True
            
    except Exception as e:
        print(f"❌ Error updating Airtable: {e}")
        return False

def process_latest_image():
    """Process the latest image to extract and update liquidation clusters"""
    
    # Get the latest image
    latest_image, folder = get_latest_image()
    
    if not latest_image:
        print("   No images found to process")
        return False
    
    # Show what we're processing
    file_age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(latest_image))).total_seconds()
    print(f"\n📸 Processing Latest Image:")
    print(f"   File: {os.path.basename(latest_image)}")
    print(f"   Age: {int(file_age/60)} minutes old")
    print(f"   Type: {os.path.basename(os.path.dirname(folder))}")
    
    # Extract data using ChatGPT
    print(f"\n🤖 Analyzing with ChatGPT for maximum accuracy...")
    symbol, current_price, clusters = extract_clusters_with_chatgpt(latest_image)
    
    if not symbol or not current_price:
        print("   ⚠️ Could not extract symbol or price from image")
        return False
    
    print(f"\n📊 Extracted Data:")
    print(f"   Symbol: {symbol}")
    print(f"   Current Price: ${current_price:.2f}")
    print(f"   Found {len(clusters)} liquidation levels")
    
    if clusters:
        print(f"   All Clusters: {[f'${c:.2f}' for c in clusters[:10]]}")  # Show first 10
    
    # Find the 4 closest clusters with 2% minimum distance
    liq_minus2, liq_minus1, liq_plus1, liq_plus2 = find_closest_clusters(current_price, clusters)
    
    print(f"\n🎯 Selected Clusters (min 2% from ${current_price:.2f}):")
    print(f"   Below current price:")
    if liq_minus2:
        pct_diff = ((current_price - liq_minus2) / current_price) * 100
        print(f"     Liqcluster-2: ${liq_minus2:.2f} (-{pct_diff:.1f}%)")
    else:
        print(f"     Liqcluster-2: None")
    if liq_minus1:
        pct_diff = ((current_price - liq_minus1) / current_price) * 100
        print(f"     Liqcluster-1: ${liq_minus1:.2f} (-{pct_diff:.1f}%)")
    else:
        print(f"     Liqcluster-1: None")
    
    print(f"   Above current price:")
    if liq_plus1:
        pct_diff = ((liq_plus1 - current_price) / current_price) * 100
        print(f"     Liqcluster+1: ${liq_plus1:.2f} (+{pct_diff:.1f}%)")
    else:
        print(f"     Liqcluster+1: None")
    if liq_plus2:
        pct_diff = ((liq_plus2 - current_price) / current_price) * 100
        print(f"     Liqcluster+2: ${liq_plus2:.2f} (+{pct_diff:.1f}%)")
    else:
        print(f"     Liqcluster+2: None")
    
    # Update Airtable
    return update_airtable(symbol, current_price, (liq_minus2, liq_minus1, liq_plus1, liq_plus2))

def monitor_continuous(update_interval=300):
    """Monitor and update every 5 minutes"""
    print("="*60)
    print("STEP 5 ENHANCED: MAXIMUM ACCURACY LIQUIDATION EXTRACTION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print("\n♾️  Continuous monitoring mode - Updates every 5 minutes")
    print("Using ChatGPT to analyze actual images for maximum accuracy")
    print("Press Ctrl+C to stop\n")
    
    last_update_time = datetime.now()
    
    while True:
        current_time = datetime.now()
        time_since_update = (current_time - last_update_time).total_seconds()
        
        # Process every 5 minutes
        if time_since_update >= update_interval:
            print(f"\n[{current_time.strftime('%H:%M:%S')}] Starting accuracy-focused analysis...")
            
            if process_latest_image():
                print(f"\n✅ Successfully updated Airtable with maximum accuracy")
            else:
                print(f"\n⚠️ Update failed - will retry in 5 minutes")
            
            last_update_time = current_time
            
            # Show countdown to next update
            next_update = current_time + timedelta(seconds=update_interval)
            print(f"\n⏰ Next update at {next_update.strftime('%H:%M:%S')}")
        
        # Show progress
        remaining = update_interval - time_since_update
        if remaining > 0:
            print(f"\r⏳ Next update in {int(remaining)} seconds...", end="", flush=True)
        time.sleep(1)

def main():
    """Main function"""
    import sys
    
    # Check if running in one-time mode
    one_time = "--once" in sys.argv or "-o" in sys.argv
    
    if one_time:
        print("="*60)
        print("STEP 5 ENHANCED: MAXIMUM ACCURACY LIQUIDATION EXTRACTION")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        print("\n🔍 Running in one-time mode with ChatGPT analysis")
        
        if process_latest_image():
            print("\n✅ Successfully extracted and updated liquidation data")
        else:
            print("\n⚠️ Failed to process image")
    else:
        try:
            monitor_continuous()
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()