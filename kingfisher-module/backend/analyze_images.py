#!/usr/bin/env python3
"""
Analyze KingFisher Images Manually
Safe manual-first approach for image analysis
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from pathlib import Path
import glob

async def analyze_kingfisher_images():
    """Analyze all KingFisher images in the test_images directory"""
    
    base_url = "http://localhost:8100"
    
    print("🔍 KingFisher Image Analysis")
    print("=" * 50)
    print("🎯 SAFE MANUAL-FIRST APPROACH")
    print("=" * 50)
    
    # Check for test images directory
    test_dir = Path("test_images")
    if not test_dir.exists():
        test_dir.mkdir(exist_ok=True)
        print(f"📁 Created test directory: {test_dir.absolute()}")
        print("📸 Please add KingFisher images to this directory")
        return
    
    # Find all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        image_files.extend(test_dir.glob(ext))
    
    if not image_files:
        print("📝 No images found in test_images/ directory")
        print("💡 Please add KingFisher images and run again")
        return
    
    print(f"📸 Found {len(image_files)} images to analyze:")
    for img in image_files:
        print(f"   📸 {img.name}")
    
    print(f"\n🚀 Starting analysis...")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        for i, image_path in enumerate(image_files, 1):
            print(f"\n{i}/{len(image_files)} Analyzing: {image_path.name}")
            print("-" * 30)
            
            try:
                # Process the image
                response = await client.post(
                    f"{base_url}/api/v1/images/process-file",
                    params={
                        "file_path": str(image_path.absolute()),
                        "user_id": 424184493,
                        "username": "SemeCJ"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Analysis completed successfully!")
                    
                    # Display results
                    analysis = result.get('analysis', {})
                    significance = analysis.get('significance_score', 0)
                    sentiment = analysis.get('market_sentiment', 'neutral')
                    confidence = analysis.get('confidence', 0)
                    
                    print(f"📊 Results:")
                    print(f"   🎯 Significance: {significance:.2%}")
                    print(f"   📈 Sentiment: {sentiment.title()}")
                    print(f"   🎯 Confidence: {confidence:.2%}")
                    
                    # Liquidation clusters
                    clusters = analysis.get('liquidation_clusters', [])
                    print(f"   🔴 Liquidation Clusters: {len(clusters)}")
                    
                    # Toxic flow
                    toxic_flow = analysis.get('toxic_flow', 0)
                    print(f"   🟢 Toxic Flow: {toxic_flow:.2%}")
                    
                    # Alert level
                    if significance > 0.7:
                        print("   🚨 HIGH SIGNIFICANCE - ALERT!")
                    elif significance > 0.5:
                        print("   ⚠️ Medium significance")
                    else:
                        print("   ℹ️ Low significance")
                        
                else:
                    print(f"❌ Analysis failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error analyzing {image_path.name}: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS COMPLETE")
    print("=" * 50)
    print("📱 Check your Telegram for detailed results")
    print("📊 High significance results (>70%) trigger alerts")
    print("💡 Add more images to test_images/ for additional analysis")

def list_available_images():
    """List all available images for analysis"""
    test_dir = Path("test_images")
    
    if not test_dir.exists():
        print("📁 No test_images directory found")
        return []
    
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        image_files.extend(test_dir.glob(ext))
    
    if image_files:
        print(f"📸 Found {len(image_files)} images:")
        for img in image_files:
            size = img.stat().st_size / 1024  # KB
            print(f"   📸 {img.name} ({size:.1f} KB)")
    else:
        print("📝 No images found in test_images/ directory")
    
    return image_files

if __name__ == "__main__":
    print("🔍 KingFisher Image Analysis Tool")
    print("=" * 50)
    
    # List available images
    images = list_available_images()
    
    if images:
        # Run analysis
        asyncio.run(analyze_kingfisher_images())
    else:
        print("\n💡 To analyze images:")
        print("1. Create test_images/ directory")
        print("2. Add KingFisher images to the directory")
        print("3. Run this script again") 