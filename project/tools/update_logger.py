#!/usr/bin/env python3
"""
Update Logger Script
Tracks and logs Life Age and Risk Band updates for frontend alerts
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_logger.log'),
        logging.StreamHandler()
    ]
)

# Database path
DB_PATH = Path(__file__).parent / 'data' / 'update_logs.db'

def create_update_logs_table():
    """Create the update_logs table if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                update_type TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                details TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("✅ Update logs table created")
        
    except Exception as e:
        logging.error(f"❌ Error creating update logs table: {e}")

def log_life_age_update(symbol, old_age, new_age):
    """Log a Life Age update"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO update_logs (symbol, update_type, old_value, new_value, details)
            VALUES (?, 'life_age', ?, ?, ?)
        ''', (symbol, str(old_age), str(new_age), f"Life Age incremented from {old_age} to {new_age} days"))
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ Logged Life Age update for {symbol}: {old_age} → {new_age}")
        
    except Exception as e:
        logging.error(f"❌ Error logging Life Age update: {e}")

def log_risk_band_update(symbol, risk_value, band_key, old_days, new_days):
    """Log a Risk Band update"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO update_logs (symbol, update_type, old_value, new_value, details)
            VALUES (?, 'risk_band', ?, ?, ?)
        ''', (symbol, str(old_days), str(new_days), 
              f"Risk Band {band_key} updated: {old_days} → {new_days} days (Risk Value: {risk_value:.3f})"))
        
        conn.commit()
        conn.close()
        
        logging.info(f"✅ Logged Risk Band update for {symbol}: {band_key} {old_days} → {new_days}")
        
    except Exception as e:
        logging.error(f"❌ Error logging Risk Band update: {e}")

def get_recent_updates(symbol=None, limit=10):
    """Get recent updates for a symbol or all symbols"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute('''
                SELECT * FROM update_logs 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (symbol, limit))
        else:
            cursor.execute('''
                SELECT * FROM update_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        updates = []
        for row in results:
            updates.append({
                'id': row[0],
                'symbol': row[1],
                'update_type': row[2],
                'old_value': row[3],
                'new_value': row[4],
                'details': row[5],
                'timestamp': row[6]
            })
        
        return updates
        
    except Exception as e:
        logging.error(f"❌ Error getting recent updates: {e}")
        return []

def get_update_summary(symbol):
    """Get a summary of recent updates for a symbol"""
    try:
        updates = get_recent_updates(symbol, 5)
        
        if not updates:
            return None
        
        latest_life_age = None
        latest_risk_band = None
        
        for update in updates:
            if update['update_type'] == 'life_age' and not latest_life_age:
                latest_life_age = update
            elif update['update_type'] == 'risk_band' and not latest_risk_band:
                latest_risk_band = update
        
        return {
            'symbol': symbol,
            'latest_life_age': latest_life_age,
            'latest_risk_band': latest_risk_band,
            'total_updates': len(updates)
        }
        
    except Exception as e:
        logging.error(f"❌ Error getting update summary: {e}")
        return None

if __name__ == "__main__":
    create_update_logs_table()
    print("✅ Update Logger initialized")
