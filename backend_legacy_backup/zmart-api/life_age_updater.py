#!/usr/bin/env python3
"""
Life Age Updater Script
Automatically increments Life Age for all symbols by +1 every day at 1 AM
"""

import sqlite3
import schedule
import time
import logging
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('life_age_updater.log'),
        logging.StreamHandler()
    ]
)

# Database path
DB_PATH = Path(__file__).parent / 'data' / 'life_age.db'

# All symbols from the menu
SYMBOLS = [
    'BTC', 'ETH', 'XRP', 'BNB', 'SOL', 'DOGE', 'ADA', 'LINK', 'AVAX', 
    'XLM', 'SUI', 'DOT', 'LTC', 'XMR', 'AAVE', 'VET', 'ATOM', 'RENDER', 
    'HBAR', 'XTZ', 'TON', 'TRX'
]

def create_life_age_table():
    """Create the life_age table if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS life_age (
                symbol TEXT PRIMARY KEY,
                age_days INTEGER DEFAULT 365,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create daily updates tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_updates (
                update_date TEXT PRIMARY KEY,
                last_update_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize all symbols with default age of 365 days
        for symbol in SYMBOLS:
            cursor.execute('''
                INSERT OR IGNORE INTO life_age (symbol, age_days)
                VALUES (?, 365)
            ''', (symbol,))
        
        conn.commit()
        conn.close()
        logging.info(f"✅ Life age table created/initialized with {len(SYMBOLS)} symbols")
        
    except Exception as e:
        logging.error(f"❌ Error creating life age table: {e}")

def increment_life_age():
    """Increment life age for all symbols by +1 (only once per day)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if we already updated today
        cursor.execute('SELECT last_update_date FROM daily_updates WHERE update_date = ?', (today,))
        already_updated = cursor.fetchone()
        
        if already_updated:
            logging.info(f"✅ Life age already updated today ({today}), skipping...")
            return True
        
        # Get current ages
        cursor.execute('SELECT symbol, age_days FROM life_age')
        current_ages = dict(cursor.fetchall())
        
        # Increment all symbols by +1
        updated_count = 0
        for symbol in SYMBOLS:
            current_age = current_ages.get(symbol, 365)
            new_age = current_age + 1
            
            cursor.execute('''
                UPDATE life_age 
                SET age_days = ?, last_updated = CURRENT_TIMESTAMP
                WHERE symbol = ?
            ''', (new_age, symbol))
            
            # Log the Life Age update
            try:
                import subprocess
                subprocess.run(['python3', '-c', f'from update_logger import log_life_age_update; log_life_age_update("{symbol}", {current_age}, {new_age})'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
            except Exception as e:
                logging.error(f"❌ Error logging Life Age update for {symbol}: {e}")
            
            updated_count += 1
            logging.info(f"📈 {symbol}: {current_age} → {new_age} days")
        
        # Mark today as updated
        cursor.execute('''
            INSERT OR REPLACE INTO daily_updates (update_date, last_update_date)
            VALUES (?, CURRENT_TIMESTAMP)
        ''', (today,))
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ Successfully incremented life age for {updated_count} symbols on {today}")
        
        # Trigger risk band updates after life age increment
        if updated_count > 0:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"🔄 Triggering risk band updates at {current_time}...")
            try:
                import subprocess
                result = subprocess.run(['python3', 'risk_band_updater.py'], 
                                      capture_output=True, text=True, cwd=Path(__file__).parent)
                if result.returncode == 0:
                    logging.info(f"✅ Risk band updates completed successfully at {current_time}")
                else:
                    logging.error(f"❌ Risk band updates failed: {result.stderr}")
            except Exception as e:
                logging.error(f"❌ Error updating risk bands: {e}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Error incrementing life age: {e}")
        return False

def get_life_age(symbol):
    """Get current life age for a specific symbol"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT age_days FROM life_age WHERE symbol = ?', (symbol,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return result[0]
        else:
            return 365  # Default age
            
    except Exception as e:
        logging.error(f"❌ Error getting life age for {symbol}: {e}")
        return 365

def set_life_age(symbol, age_days):
    """Set life age for a specific symbol"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO life_age (symbol, age_days, last_updated)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (symbol, age_days))
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ Set {symbol} life age to {age_days} days")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error setting life age for {symbol}: {e}")
        return False

def get_all_life_ages():
    """Get life ages for all symbols"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT symbol, age_days, last_updated FROM life_age ORDER BY symbol')
        results = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                'symbol': row[0],
                'age_days': row[1],
                'last_updated': row[2]
            }
            for row in results
        ]
        
    except Exception as e:
        logging.error(f"❌ Error getting all life ages: {e}")
        return []

def run_daily_update():
    """Main function to run the daily update"""
    logging.info("🕐 Starting daily life age update...")
    
    # Ensure database exists
    create_life_age_table()
    
    # Increment all life ages
    success = increment_life_age()
    
    if success:
        logging.info("✅ Daily life age update completed successfully")
    else:
        logging.error("❌ Daily life age update failed")
    
    return success

def main():
    """Main function to run the scheduler"""
    logging.info("🚀 Life Age Updater starting...")
    
    # Ensure database exists
    create_life_age_table()
    
    # Schedule daily update at 1 AM
    schedule.every().day.at("01:00").do(run_daily_update)
    
    logging.info("⏰ Scheduled daily life age update at 1:00 AM")
    logging.info("📊 Monitoring {len(SYMBOLS)} symbols: {', '.join(SYMBOLS)}")
    
    # Run initial update if it's the first time
    logging.info("🔄 Running initial update...")
    run_daily_update()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
