#!/usr/bin/env python3
"""
STEP 3: REMOVE DUPLICATE IMAGES
Removes duplicate images from all folders, keeping only unique ones
"""

import os
import hashlib
from datetime import datetime

# Folders to check
FOLDERS = [
    "../downloads/LiquidationMap",
    "../downloads/LiquidationHeatmap",
    "../downloads/LongTermRatio",
    "../downloads/ShortTermRatio",
    "../downloads"
]

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def remove_duplicates():
    """Remove duplicate images across all folders"""
    
    print("🔍 Scanning for duplicate images...")
    print("="*60)
    
    # Dictionary to store hash -> first file path
    seen_hashes = {}
    duplicates_removed = 0
    total_files = 0
    
    for folder in FOLDERS:
        if not os.path.exists(folder):
            continue
            
        print(f"\n📁 Checking: {folder}")
        
        # Get all jpg files in this folder
        images = [f for f in os.listdir(folder) 
                 if f.endswith('.jpg') and os.path.isfile(os.path.join(folder, f))]
        
        if not images:
            print("   No images found")
            continue
            
        folder_duplicates = 0
        
        for image in sorted(images):
            filepath = os.path.join(folder, image)
            total_files += 1
            
            # Calculate hash
            file_hash = get_file_hash(filepath)
            
            if file_hash in seen_hashes:
                # This is a duplicate
                print(f"   ❌ Duplicate found: {image}")
                print(f"      Original: {seen_hashes[file_hash]}")
                
                # Remove the duplicate
                os.remove(filepath)
                duplicates_removed += 1
                folder_duplicates += 1
                print(f"      ✅ Removed duplicate")
            else:
                # First time seeing this image
                seen_hashes[file_hash] = filepath
                print(f"   ✅ Unique: {image}")
        
        print(f"   Removed {folder_duplicates} duplicates from this folder")
    
    # Summary
    print("\n" + "="*60)
    print("📊 DUPLICATE REMOVAL COMPLETE!")
    print("="*60)
    print(f"Total files scanned:    {total_files}")
    print(f"Unique images kept:     {len(seen_hashes)}")
    print(f"Duplicates removed:     {duplicates_removed}")
    
    # Show remaining files per folder
    print("\n📁 Files remaining in each folder:")
    for folder in FOLDERS:
        if os.path.exists(folder):
            count = len([f for f in os.listdir(folder) if f.endswith('.jpg')])
            print(f"   {folder.split('/')[-1]:20} {count} images")

def main():
    print("="*60)
    print("STEP 3: REMOVE DUPLICATE IMAGES")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    print("\nThis will:")
    print("• Check all folders for duplicate images")
    print("• Keep the first occurrence of each unique image")
    print("• Remove all duplicates")
    
    remove_duplicates()
    
    print("\n✅ STEP 3 COMPLETE!")
    print("All duplicate images have been removed")

if __name__ == "__main__":
    main()