#!/usr/bin/env python3
"""
Create MACD Histogram Table
Adds the macd_histogram_data table to the database for storing MACD Histogram analysis
"""

import sqlite3
import os
from datetime import datetime

def create_macd_histogram_table():
    """Create the macd_histogram_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create macd_histogram_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macd_histogram_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                macd_line REAL NOT NULL,
                signal_line REAL NOT NULL,
                histogram_value REAL NOT NULL,
                histogram_change REAL DEFAULT 0.0,
                histogram_trend TEXT NOT NULL,
                histogram_strength REAL DEFAULT 0.0,
                zero_line_cross TEXT DEFAULT 'none',
                zero_line_cross_strength REAL DEFAULT 0.0,
                signal_cross TEXT DEFAULT 'none',
                signal_cross_strength REAL DEFAULT 0.0,
                divergence_type TEXT DEFAULT 'none',
                divergence_strength REAL DEFAULT 0.0,
                momentum_shift TEXT DEFAULT 'none',
                momentum_strength REAL DEFAULT 0.0,
                histogram_pattern TEXT DEFAULT 'none',
                pattern_strength REAL DEFAULT 0.0,
                volume_confirmation TEXT DEFAULT 'none',
                volume_strength REAL DEFAULT 0.0,
                current_price REAL NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_histogram_data_symbol 
            ON macd_histogram_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_histogram_data_timeframe 
            ON macd_histogram_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_histogram_data_trend 
            ON macd_histogram_data(histogram_trend)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_histogram_data_cross 
            ON macd_histogram_data(zero_line_cross)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_macd_histogram_data_updated 
            ON macd_histogram_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ MACD Histogram data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating MACD Histogram table: {e}")
        return False

if __name__ == "__main__":
    create_macd_histogram_table()
