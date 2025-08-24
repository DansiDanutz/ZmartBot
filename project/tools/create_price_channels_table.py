#!/usr/bin/env python3
"""
Create Price Channels (Donchian Channels) Table
Adds the price_channels_data table to the database for storing Donchian Channels analysis
"""

import sqlite3
import os
from datetime import datetime

def create_price_channels_table():
    """Create the price_channels_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create price_channels_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_channels_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                upper_channel REAL NOT NULL,
                middle_channel REAL NOT NULL,
                lower_channel REAL NOT NULL,
                channel_width REAL NOT NULL,
                channel_position REAL NOT NULL,
                breakout_direction TEXT DEFAULT 'none',
                breakout_strength REAL DEFAULT 0.0,
                channel_trend TEXT NOT NULL,
                trend_strength REAL DEFAULT 0.0,
                volatility_status TEXT NOT NULL,
                volatility_strength REAL DEFAULT 0.0,
                momentum_status TEXT DEFAULT 'neutral',
                momentum_strength REAL DEFAULT 0.0,
                support_resistance_levels TEXT,
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
            CREATE INDEX IF NOT EXISTS idx_price_channels_data_symbol 
            ON price_channels_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_channels_data_timeframe 
            ON price_channels_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_channels_data_breakout 
            ON price_channels_data(breakout_direction)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_channels_data_trend 
            ON price_channels_data(channel_trend)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_channels_data_volatility 
            ON price_channels_data(volatility_status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_channels_data_updated 
            ON price_channels_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Price Channels (Donchian Channels) data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Price Channels table: {e}")
        return False

if __name__ == "__main__":
    create_price_channels_table()
