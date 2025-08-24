#!/usr/bin/env python3
"""
STEP 2: FINAL OPENAI SORTING
Correctly identifies:
- Images with many symbols = Ratio images
- OPTICAL_OPTI = Short Term Ratio
- ALL_LEVERAGE with multiple symbols = Long Term Ratio
"""

import os
import shutil
import base64
import requests
import json
import time
from PIL import Image
import pytesseract
from datetime import datetime
from openai import OpenAI

# Folders
DOWNLOAD_FOLDER = "../downloads"
LIQUIDATION_MAP = "../downloads/LiquidationMap"
LIQUIDATION_HEATMAP = "../downloads/LiquidationHeatmap"
LONG_TERM_RATIO = "../downloads/LongTermRatio"
SHORT_TERM_RATIO = "../downloads/ShortTermRatio"

# Try different API keys
API_KEYS = [
    "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",
    "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"
]

def create_folders():
    """Create the 4 category folders"""
    folders = [LIQUIDATION_MAP, LIQUIDATION_HEATMAP, LONG_TERM_RATIO, SHORT_TERM_RATIO]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Created folder: {folder}")

def analyze_with_ocr_first(image_path):
    """Quick OCR check for obvious patterns"""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img).upper()
        
        # Check for clear indicators
        if "OPTICAL_OPTI" in text:
            print(f"   ✅ OCR found: OPTICAL_OPTI = Short Term Ratio")
            return "ShortTermRatio"
        
        if "HEATMAP" in text:
            print(f"   ✅ OCR found: HEATMAP")
            return "LiquidationHeatmap"
            
        # Check if has multiple symbols (ratio indicator)
        symbols = ["BTC", "ETH", "SOL", "AVAX", "DOGE", "SAND", "TRX", "HBAR", "PEPE", "XLM", "ENA", "AGLD", "PENGU", "LINK"]
        symbol_count = sum(1 for s in symbols if s in text)
        
        if symbol_count >= 8:  # Many symbols = ratio chart
            if "ALL_LEVERAGE" in text:
                print(f"   ✅ OCR found: ALL_LEVERAGE with {symbol_count} symbols = Long Term Ratio")
                return "LongTermRatio"
            else:
                print(f"   ✅ OCR found: {symbol_count} symbols = Ratio chart")
                return "LongTermRatio"
        
        return None  # Need OpenAI check
        
    except Exception as e:
        print(f"   OCR error: {e}")
        return None

def analyze_with_openai(image_path, api_key_index=0):
    """Use OpenAI to analyze image"""
    
    if api_key_index >= len(API_KEYS):
        print("   ❌ All API keys exhausted")
        return "LiquidationMap"  # default
    
    try:
        client = OpenAI(api_key=API_KEYS[api_key_index])
        
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper, faster model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this KingFisher image and classify it:

1. SHORT TERM RATIO: Has text "OPTICAL_OPTI" or "OPTICAL" and shows MANY crypto symbols in a grid/list
2. LONG TERM RATIO: Has text "ALL_LEVERAGE" and shows MANY crypto symbols (10+ different ones) in a grid/list format
3. LIQUIDATION HEATMAP: Has "HEATMAP" text with color gradients
4. LIQUIDATION MAP: Shows a single symbol with price levels and liquidation zones

IMPORTANT: If you see MANY symbols (like BTC, ETH, SOL, AVAX, etc) listed together, it's a RATIO chart.

Reply with ONLY one word:
- ShortTermRatio
- LongTermRatio  
- LiquidationHeatmap
- LiquidationMap"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        category = response.choices[0].message.content.strip()
        print(f"   ✅ OpenAI: {category}")
        return category
        
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            print(f"   ⚠️ Rate limit on key {api_key_index + 1}, trying next...")
            time.sleep(3)
            return analyze_with_openai(image_path, api_key_index + 1)
        else:
            print(f"   ❌ OpenAI error: {e}")
            return "LiquidationMap"

def analyze_image(image_path):
    """Analyze image using OCR first, then OpenAI if needed"""
    
    # First try OCR for obvious cases
    ocr_result = analyze_with_ocr_first(image_path)
    if ocr_result:
        return ocr_result
    
    # Use OpenAI for unclear cases
    print("   🤖 Using OpenAI for detailed analysis...")
    return analyze_with_openai(image_path)

def sort_images():
    """Sort all images"""
    
    images = [f for f in os.listdir(DOWNLOAD_FOLDER) 
              if f.endswith('.jpg') and os.path.isfile(os.path.join(DOWNLOAD_FOLDER, f))]
    
    if not images:
        print("No images found")
        return
    
    print(f"\n📊 Found {len(images)} images to analyze")
    print("="*60)
    
    sorted_count = {
        "LiquidationMap": 0,
        "LiquidationHeatmap": 0,
        "LongTermRatio": 0,
        "ShortTermRatio": 0
    }
    
    for i, image in enumerate(sorted(images), 1):
        filepath = os.path.join(DOWNLOAD_FOLDER, image)
        print(f"\n[{i}/{len(images)}] Processing: {image}")
        
        # Add delay to avoid rate limits
        if i > 1:
            time.sleep(1)
        
        # Analyze
        category = analyze_image(filepath)
        
        # Map to folder
        if category == "LiquidationMap":
            dest_folder = LIQUIDATION_MAP
        elif category == "LiquidationHeatmap":
            dest_folder = LIQUIDATION_HEATMAP
        elif category == "LongTermRatio":
            dest_folder = LONG_TERM_RATIO
        elif category == "ShortTermRatio":
            dest_folder = SHORT_TERM_RATIO
        else:
            dest_folder = LIQUIDATION_MAP  # default
            category = "LiquidationMap"
        
        # Move file
        dest_path = os.path.join(dest_folder, image)
        shutil.move(filepath, dest_path)
        print(f"   ✅ Moved to: {dest_folder.split('/')[-1]}/")
        
        sorted_count[category] += 1
    
    # Summary
    print("\n" + "="*60)
    print("📊 FINAL SORTING COMPLETE!")
    print("="*60)
    print(f"LiquidationMap:     {sorted_count['LiquidationMap']} images")
    print(f"LiquidationHeatmap: {sorted_count['LiquidationHeatmap']} images")
    print(f"LongTermRatio:      {sorted_count['LongTermRatio']} images")
    print(f"ShortTermRatio:     {sorted_count['ShortTermRatio']} images")
    print("-"*60)
    print(f"Total sorted:       {sum(sorted_count.values())} images")

def main():
    print("="*60)
    print("STEP 2: FINAL SORTING WITH OPENAI")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    print("\n📋 Detection logic:")
    print("   • OPTICAL_OPTI → Short Term Ratio")
    print("   • ALL_LEVERAGE + many symbols → Long Term Ratio")
    print("   • HEATMAP → Liquidation Heatmap")
    print("   • Single symbol charts → Liquidation Map")
    
    # Create folders
    print("\n📁 Creating folders...")
    create_folders()
    
    # Sort
    print("\n🔍 Starting analysis...")
    sort_images()
    
    print("\n✅ COMPLETE!")

if __name__ == "__main__":
    main()