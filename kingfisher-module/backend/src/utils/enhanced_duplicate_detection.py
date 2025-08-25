#!/usr/bin/env python3
"""
Enhanced Duplicate Detection for KingFisher
Combines MD5 exact matching with perceptual hashing for near-duplicate detection
"""

import os
import hashlib
import logging
from typing import List, Dict, Set, Tuple
from pathlib import Path
from PIL import Image
import imagehash
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedDuplicateDetector:
    """Advanced duplicate detection using MD5 + perceptual hashing"""
    
    def __init__(self, phash_threshold: int = 5, dhash_threshold: int = 5):
        """
        Initialize detector with configurable thresholds
        
        Args:
            phash_threshold: Hamming distance threshold for pHash (default: 5)
            dhash_threshold: Hamming distance threshold for dHash (default: 5)
        """
        self.phash_threshold = phash_threshold
        self.dhash_threshold = dhash_threshold
        self.md5_cache: Dict[str, str] = {}  # file_path -> md5_hash
        self.phash_cache: Dict[str, str] = {}  # file_path -> phash
        self.dhash_cache: Dict[str, str] = {}  # file_path -> dhash
        
    def calculate_md5(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        if file_path in self.md5_cache:
            return self.md5_cache[file_path]
            
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            self.md5_cache[file_path] = file_hash
            return file_hash
        except Exception as e:
            logger.error(f"Error calculating MD5 for {file_path}: {e}")
            return ""
    
    def calculate_perceptual_hashes(self, file_path: str) -> Tuple[str, str]:
        """Calculate pHash and dHash for image"""
        if file_path in self.phash_cache and file_path in self.dhash_cache:
            return self.phash_cache[file_path], self.dhash_cache[file_path]
            
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                # Calculate perceptual hashes
                phash = str(imagehash.phash(img))
                dhash = str(imagehash.dhash(img))
                
                # Cache results
                self.phash_cache[file_path] = phash
                self.dhash_cache[file_path] = dhash
                
                return phash, dhash
                
        except Exception as e:
            logger.error(f"Error calculating perceptual hashes for {file_path}: {e}")
            return "", ""
    
    def is_exact_duplicate(self, file1: str, file2: str) -> bool:
        """Check if files are exact duplicates using MD5"""
        md5_1 = self.calculate_md5(file1)
        md5_2 = self.calculate_md5(file2)
        
        if not md5_1 or not md5_2:
            return False
            
        return md5_1 == md5_2
    
    def is_near_duplicate(self, file1: str, file2: str) -> bool:
        """Check if images are near duplicates using perceptual hashing"""
        phash1, dhash1 = self.calculate_perceptual_hashes(file1)
        phash2, dhash2 = self.calculate_perceptual_hashes(file2)
        
        if not all([phash1, dhash1, phash2, dhash2]):
            return False
        
        try:
            # Convert string hashes back to imagehash objects for comparison
            phash1_obj = imagehash.hex_to_hash(phash1)
            phash2_obj = imagehash.hex_to_hash(phash2)
            dhash1_obj = imagehash.hex_to_hash(dhash1)
            dhash2_obj = imagehash.hex_to_hash(dhash2)
            
            # Calculate Hamming distances
            phash_distance = phash1_obj - phash2_obj
            dhash_distance = dhash1_obj - dhash2_obj
            
            # Consider near-duplicate if either hash is within threshold
            is_phash_similar = phash_distance <= self.phash_threshold
            is_dhash_similar = dhash_distance <= self.dhash_threshold
            
            return is_phash_similar or is_dhash_similar
            
        except Exception as e:
            logger.error(f"Error comparing perceptual hashes: {e}")
            return False
    
    def find_duplicates(self, image_paths: List[str]) -> Dict[str, List[str]]:
        """
        Find all duplicates in a list of image paths
        
        Returns:
            Dict mapping original file to list of duplicates
        """
        duplicates = {}
        processed = set()
        
        logger.info(f"🔍 Analyzing {len(image_paths)} images for duplicates...")
        
        for i, file1 in enumerate(image_paths):
            if file1 in processed:
                continue
                
            duplicate_group = []
            
            # Check against remaining files
            for j in range(i + 1, len(image_paths)):
                file2 = image_paths[j]
                
                if file2 in processed:
                    continue
                
                # Fast exact duplicate check first
                if self.is_exact_duplicate(file1, file2):
                    duplicate_group.append(file2)
                    processed.add(file2)
                    logger.debug(f"📄 Exact duplicate found: {file1} <-> {file2}")
                    
                # Near duplicate check if not exact
                elif self.is_near_duplicate(file1, file2):
                    duplicate_group.append(file2)
                    processed.add(file2)
                    logger.debug(f"🖼️  Near duplicate found: {file1} <-> {file2}")
            
            if duplicate_group:
                duplicates[file1] = duplicate_group
                logger.info(f"🗂️  Found {len(duplicate_group)} duplicates for {file1}")
        
        return duplicates
    
    def remove_duplicates(self, image_directory: str, dry_run: bool = False) -> Dict[str, any]:
        """
        Remove duplicates from directory, keeping the oldest file
        
        Args:
            image_directory: Directory to scan for duplicates
            dry_run: If True, only report what would be deleted
            
        Returns:
            Dict with removal statistics
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        
        # Find all image files
        image_paths = []
        for root, dirs, files in os.walk(image_directory):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    image_paths.append(os.path.join(root, file))
        
        if not image_paths:
            logger.warning(f"No images found in {image_directory}")
            return {"removed": 0, "kept": 0, "errors": 0}
        
        logger.info(f"📁 Scanning {len(image_paths)} images in {image_directory}")
        
        # Find duplicates
        duplicates = self.find_duplicates(image_paths)
        
        stats = {"removed": 0, "kept": 0, "errors": 0, "duplicate_groups": len(duplicates)}
        
        # Process duplicate groups
        for original, duplicate_list in duplicates.items():
            try:
                # Keep the oldest file (by creation time)
                all_files = [original] + duplicate_list
                file_times = []
                
                for file_path in all_files:
                    try:
                        stat = os.stat(file_path)
                        file_times.append((file_path, stat.st_ctime))
                    except OSError:
                        logger.error(f"Cannot stat file: {file_path}")
                        stats["errors"] += 1
                        continue
                
                # Sort by creation time (oldest first)
                file_times.sort(key=lambda x: x[1])
                oldest_file = file_times[0][0]
                
                logger.info(f"📝 Keeping oldest file: {oldest_file}")
                stats["kept"] += 1
                
                # Remove the rest
                for file_path, _ in file_times[1:]:
                    if dry_run:
                        logger.info(f"🗑️  Would remove: {file_path}")
                    else:
                        try:
                            os.remove(file_path)
                            logger.info(f"🗑️  Removed duplicate: {file_path}")
                        except OSError as e:
                            logger.error(f"Error removing {file_path}: {e}")
                            stats["errors"] += 1
                            continue
                    
                    stats["removed"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing duplicate group for {original}: {e}")
                stats["errors"] += 1
        
        # Log summary
        logger.info(f"✅ Duplicate removal complete:")
        logger.info(f"   📊 Duplicate groups found: {stats['duplicate_groups']}")
        logger.info(f"   📁 Files kept: {stats['kept']}")
        logger.info(f"   🗑️  Files removed: {stats['removed']}")
        logger.info(f"   ❌ Errors: {stats['errors']}")
        
        return stats
    
    def clear_cache(self):
        """Clear all cached hashes"""
        self.md5_cache.clear()
        self.phash_cache.clear()
        self.dhash_cache.clear()
        logger.info("🧹 Hash cache cleared")


def main():
    """Command line interface for duplicate detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced duplicate detection for KingFisher images")
    parser.add_argument("directory", help="Directory to scan for duplicates")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed without actually removing")
    parser.add_argument("--phash-threshold", type=int, default=5, help="pHash similarity threshold (default: 5)")
    parser.add_argument("--dhash-threshold", type=int, default=5, help="dHash similarity threshold (default: 5)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize detector
    detector = EnhancedDuplicateDetector(
        phash_threshold=args.phash_threshold,
        dhash_threshold=args.dhash_threshold
    )
    
    # Run duplicate detection
    start_time = datetime.now()
    stats = detector.remove_duplicates(args.directory, dry_run=args.dry_run)
    elapsed = datetime.now() - start_time
    
    print(f"\n🎯 Enhanced Duplicate Detection Complete")
    print(f"⏱️  Processing time: {elapsed.total_seconds():.2f} seconds")
    print(f"📊 Results: {stats}")


if __name__ == "__main__":
    main()