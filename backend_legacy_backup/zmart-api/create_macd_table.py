#!/usr/bin/env python3
"""
Create MACD Table
Adds the macd_data table to the database for storing MACD indicators
"""

import sqlite3
import os
from datetime import datetime

def create_macd_table():
    """Create the macd_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create macd_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macd_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                macd_line REAL NOT NULL,
                signal_line REAL NOT NULL,
                histogram REAL NOT NULL,
                signal_status TEXT NOT NULL,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_data_symbol 
            ON macd_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_data_timeframe 
            ON macd_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_data_status 
            ON macd_data(signal_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_data_updated 
            ON macd_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ MACD data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating MACD table: {e}")
        return False

if __name__ == "__main__":
    create_macd_table()
