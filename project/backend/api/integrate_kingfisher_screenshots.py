#!/usr/bin/env python3
"""
KingFisher Screenshot Integration with HistoryIndicators Database
Automatically captures and stores indicator screenshots for historical analysis
"""

import sqlite3
import os
import shutil
import glob
import logging
from datetime import datetime
from pathlib import Path
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KingFisherScreenshotIntegrator:
    """Integrates KingFisher screenshots with the HistoryIndicators database"""
    
    def __init__(self):
        self.kingfisher_path = "/Users/dansidanutz/Desktop/ZmartBot/kingfisher-module/backend"
        self.history_db_path = "/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/data/indicators_history.db"
        self.screenshots_dir = "/Users/dansidanutz/Desktop/ZmartBot/project/backend/api/src/data/screenshots"
        
        # Ensure screenshots directory exists
        Path(self.screenshots_dir).mkdir(parents=True, exist_ok=True)
    
    def capture_indicator_screenshots(self):
        """Capture and integrate KingFisher screenshots with indicators database"""
        try:
            logger.info("🚀 Starting KingFisher screenshot integration...")
            
            # Get all KingFisher screenshots
            kg_screenshots = glob.glob(f"{self.kingfisher_path}/kg_*.jpg")
            logger.info(f"📸 Found {len(kg_screenshots)} KingFisher screenshots")
            
            if not kg_screenshots:
                logger.warning("⚠️ No KingFisher screenshots found")
                return
            
            # Connect to database
            conn = sqlite3.connect(self.history_db_path)
            cursor = conn.cursor()
            
            # Get recent snapshots without screenshots
            cursor.execute("""
                SELECT id, symbol, timeframe, timestamp 
                FROM indicator_snapshots 
                WHERE screenshot_path IS NULL 
                ORDER BY timestamp DESC 
                LIMIT 20
            """)
            snapshots = cursor.fetchall()
            
            logger.info(f"🔍 Found {len(snapshots)} snapshots without screenshots")
            
            screenshots_processed = 0
            
            for i, (snapshot_id, symbol, timeframe, timestamp) in enumerate(snapshots):
                if i < len(kg_screenshots):
                    kg_file = kg_screenshots[i]
                    
                    # Create new filename
                    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                    new_filename = f"{symbol}_{timeframe}_{timestamp_str}.jpg"
                    new_path = os.path.join(self.screenshots_dir, new_filename)
                    
                    try:
                        # Copy screenshot
                        shutil.copy2(kg_file, new_path)
                        
                        # Convert to base64 for database
                        with open(new_path, 'rb') as f:
                            screenshot_data = f.read()
                            screenshot_base64 = base64.b64encode(screenshot_data).decode('utf-8')
                        
                        # Create metadata
                        metadata = {
                            'source': 'kingfisher',
                            'original_file': os.path.basename(kg_file),
                            'capture_time': timestamp_str,
                            'file_size': len(screenshot_data),
                            'integration_version': '1.0'
                        }
                        
                        # Update database
                        cursor.execute("""
                            UPDATE indicator_snapshots 
                            SET screenshot_path = ?, 
                                screenshot_base64 = ?, 
                                screenshot_metadata = ?
                            WHERE id = ?
                        """, (new_path, screenshot_base64, str(metadata), snapshot_id))
                        
                        screenshots_processed += 1
                        logger.info(f"✅ Integrated screenshot for {symbol} {timeframe}")
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing {kg_file}: {e}")
                        continue
            
            conn.commit()
            conn.close()
            
            logger.info(f"🎯 Integration complete! Processed {screenshots_processed} screenshots")
            
            # Update statistics
            self._update_collection_stats(screenshots_processed)
            
        except Exception as e:
            logger.error(f"❌ Error during screenshot integration: {e}")
    
    def _update_collection_stats(self, screenshots_count):
        """Update collection statistics"""
        try:
            conn = sqlite3.connect(self.history_db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
                INSERT OR REPLACE INTO collection_stats 
                (date, screenshots_captured) 
                VALUES (?, COALESCE((SELECT screenshots_captured FROM collection_stats WHERE date = ?), 0) + ?)
            """, (today, today, screenshots_count))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📊 Updated collection stats: +{screenshots_count} screenshots")
            
        except Exception as e:
            logger.error(f"❌ Error updating stats: {e}")
    
    def get_integration_status(self):
        """Get current integration status"""
        try:
            conn = sqlite3.connect(self.history_db_path)
            cursor = conn.cursor()
            
            # Get total snapshots
            cursor.execute("SELECT COUNT(*) FROM indicator_snapshots")
            total_snapshots = cursor.fetchone()[0]
            
            # Get snapshots with screenshots
            cursor.execute("SELECT COUNT(*) FROM indicator_snapshots WHERE screenshot_path IS NOT NULL")
            screenshots_count = cursor.fetchone()[0]
            
            # Get latest screenshot
            cursor.execute("""
                SELECT symbol, timeframe, timestamp 
                FROM indicator_snapshots 
                WHERE screenshot_path IS NOT NULL 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            latest_screenshot = cursor.fetchone()
            
            conn.close()
            
            status = {
                'total_snapshots': total_snapshots,
                'screenshots_integrated': screenshots_count,
                'integration_percentage': round((screenshots_count / total_snapshots * 100), 2) if total_snapshots > 0 else 0,
                'latest_screenshot': latest_screenshot,
                'kingfisher_screenshots_available': len(glob.glob(f"{self.kingfisher_path}/kg_*.jpg")),
                'last_check': datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting integration status: {e}")
            return {}

def main():
    """Main integration function"""
    integrator = KingFisherScreenshotIntegrator()
    
    print("🎯 KINGFISHER SCREENSHOT INTEGRATION")
    print("===================================")
    
    # Get current status
    status = integrator.get_integration_status()
    print(f"📊 Current Status:")
    print(f"   Total Snapshots: {status.get('total_snapshots', 0)}")
    print(f"   Screenshots Integrated: {status.get('screenshots_integrated', 0)}")
    print(f"   Integration %: {status.get('integration_percentage', 0)}%")
    print(f"   KingFisher Screenshots Available: {status.get('kingfisher_screenshots_available', 0)}")
    
    # Run integration
    integrator.capture_indicator_screenshots()
    
    # Get updated status
    updated_status = integrator.get_integration_status()
    print(f"\n✅ Updated Status:")
    print(f"   Screenshots Integrated: {updated_status.get('screenshots_integrated', 0)}")
    print(f"   Integration %: {updated_status.get('integration_percentage', 0)}%")
    
    print("\n🎉 KingFisher screenshot integration complete!")

if __name__ == "__main__":
    main()