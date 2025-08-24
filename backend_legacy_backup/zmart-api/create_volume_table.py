#!/usr/bin/env python3
"""
Create Volume Table
Adds the volume_data table to the database for storing volume analysis indicators
"""

import sqlite3
import os
from datetime import datetime

def create_volume_table():
    """Create the volume_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create volume_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS volume_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                current_volume REAL NOT NULL,
                volume_sma_20 REAL NOT NULL,
                volume_ratio REAL NOT NULL,
                obv REAL NOT NULL,
                obv_sma REAL NOT NULL,
                volume_spike_detected BOOLEAN DEFAULT 0,
                volume_spike_ratio REAL DEFAULT 0.0,
                volume_trend TEXT DEFAULT 'neutral',
                volume_divergence_type TEXT DEFAULT 'none',
                volume_divergence_strength REAL DEFAULT 0.0,
                price_volume_correlation REAL DEFAULT 0.0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_volume_data_symbol 
            ON volume_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_volume_data_timeframe 
            ON volume_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_volume_data_spike 
            ON volume_data(volume_spike_detected)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_volume_data_updated 
            ON volume_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Volume data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Volume table: {e}")
        return False

if __name__ == "__main__":
    create_volume_table()
