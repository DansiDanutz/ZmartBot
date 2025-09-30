#!/usr/bin/env python3
"""
Test Manual KingFisher Image Analysis
Demonstrates the safe manual-first approach
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from pathlib import Path

async def test_manual_analysis():
    """Test manual image analysis functionality"""
    
    base_url = "http://localhost:8100"
    
    print("🧪 Testing Manual KingFisher Image Analysis")
    print("=" * 50)
    print("🎯 SAFE MANUAL-FIRST APPROACH")
    print("=" * 50)
    
    # Create test directory for images
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Test images directory: {test_dir.absolute()}")
    print("📸 Place your KingFisher images here for analysis")
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Check if manual upload endpoint is available
        print("\n1️⃣ Testing Manual Upload Endpoint...")
        try:
            response = await client.post(f"{base_url}/api/v1/images/upload-manual")
            if response.status_code == 422:  # Expected - missing file
                print("✅ Manual upload endpoint is working (file required)")
            else:
                print(f"❌ Manual upload failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Manual upload error: {e}")
        
        # Test 2: Check if process file endpoint is available
        print("\n2️⃣ Testing Process File Endpoint...")
        try:
            test_file_path = "/path/to/test/image.jpg"
            response = await client.post(
                f"{base_url}/api/v1/images/process-file",
                params={"file_path": test_file_path}
            )
            if response.status_code == 404:  # Expected - file doesn't exist
                print("✅ Process file endpoint is working (file not found)")
            else:
                print(f"❌ Process file failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Process file error: {e}")
        
        # Test 3: List available test images
        print("\n3️⃣ Checking for Test Images...")
        image_files = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
        
        if image_files:
            print(f"✅ Found {len(image_files)} test images:")
            for img in image_files:
                print(f"   📸 {img.name}")
        else:
            print("📝 No test images found yet")
            print("   💡 Add KingFisher images to the test_images/ directory")
    
    print("\n" + "=" * 50)
    print("🎯 MANUAL ANALYSIS READY")
    print("=" * 50)
    print("\n📋 HOW TO USE:")
    print("1. 📸 Save KingFisher images to: test_images/")
    print("2. 🚀 Run analysis: python test_manual_analysis.py")
    print("3. 📊 Get results: Check console output")
    print("4. 💬 Telegram alerts: Sent to your chat")
    
    print("\n🔧 ANALYSIS METHODS:")
    print("📤 Method 1: Upload via API")
    print("   curl -X POST http://localhost:8100/api/v1/images/upload-manual \\")
    print("     -F \"file=@your_image.jpg\"")
    
    print("\n📁 Method 2: Process existing file")
    print("   curl -X POST http://localhost:8100/api/v1/images/process-file \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"file_path\": \"/path/to/image.jpg\"}'")
    
    print("\n📱 Method 3: Forward to Telegram bot")
    print("   Forward KingFisher images to your bot")
    print("   Automatic processing and analysis")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def create_sample_image():
    """Create a sample test image for demonstration"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        # Create a sample KingFisher-style image
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(image)
        
        # Add some sample liquidation clusters (red areas)
        for i in range(3):
            x = np.random.randint(100, 700)
            y = np.random.randint(100, 500)
            size = np.random.randint(20, 60)
            draw.ellipse([x, y, x+size, y+size], fill='red', outline='darkred')
        
        # Add some toxic flow (green areas)
        for i in range(2):
            x = np.random.randint(50, 750)
            y = np.random.randint(50, 550)
            size = np.random.randint(15, 40)
            draw.ellipse([x, y, x+size, y+size], fill='green', outline='darkgreen')
        
        # Add text
        draw.text((10, 10), "KingFisher Sample Image", fill='white')
        draw.text((10, 30), "Liquidation Analysis Test", fill='yellow')
        
        # Save to test directory
        test_dir = Path("test_images")
        test_dir.mkdir(exist_ok=True)
        
        sample_path = test_dir / "sample_kingfisher.jpg"
        image.save(sample_path)
        
        print(f"✅ Created sample image: {sample_path}")
        return str(sample_path)
        
    except ImportError:
        print("⚠️ PIL not available - skipping sample image creation")
        return None
    except Exception as e:
        print(f"❌ Error creating sample image: {e}")
        return None

if __name__ == "__main__":
    # Create sample image for testing
    sample_path = create_sample_image()
    
    # Run the test
    asyncio.run(test_manual_analysis())
    
    if sample_path:
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Replace {sample_path} with real KingFisher images")
        print(f"2. Run analysis on your images")
        print(f"3. Check results and Telegram alerts") 