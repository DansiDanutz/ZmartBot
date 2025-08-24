#!/usr/bin/env python3
"""
Create Ichimoku Table
Adds the ichimoku_data table to the database for storing Ichimoku Cloud indicators
"""

import sqlite3
import os
from datetime import datetime

def create_ichimoku_table():
    """Create the ichimoku_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create ichimoku_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ichimoku_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                tenkan_sen REAL NOT NULL,
                kijun_sen REAL NOT NULL,
                senkou_span_a REAL NOT NULL,
                senkou_span_b REAL NOT NULL,
                chikou_span REAL NOT NULL,
                current_price REAL NOT NULL,
                cloud_color TEXT NOT NULL,
                cloud_trend TEXT NOT NULL,
                price_position TEXT NOT NULL,
                tenkan_kijun_signal TEXT NOT NULL,
                tenkan_kijun_strength REAL DEFAULT 0.0,
                cloud_support REAL,
                cloud_resistance REAL,
                support_distance REAL,
                resistance_distance REAL,
                momentum_signal TEXT DEFAULT 'neutral',
                trend_strength REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ichimoku_data_symbol 
            ON ichimoku_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ichimoku_data_timeframe 
            ON ichimoku_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ichimoku_data_cloud_color 
            ON ichimoku_data(cloud_color)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ichimoku_data_signal 
            ON ichimoku_data(tenkan_kijun_signal)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ichimoku_data_updated 
            ON ichimoku_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Ichimoku data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Ichimoku table: {e}")
        return False

if __name__ == "__main__":
    create_ichimoku_table()
