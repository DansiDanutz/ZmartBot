#!/usr/bin/env python3
"""
Create Fibonacci Table
Adds the fibonacci_data table to the database for storing Fibonacci retracement levels
"""

import sqlite3
import os
from datetime import datetime

def create_fibonacci_table():
    """Create the fibonacci_data table in the database"""
    try:
        db_path = 'my_symbols_v2.db'
        
        # Check if database is writable
        if not os.access(db_path, os.W_OK):
            print(f"❌ Database {db_path} is read-only. Cannot create table.")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create fibonacci_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fibonacci_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                swing_high REAL NOT NULL,
                swing_low REAL NOT NULL,
                fib_0 REAL NOT NULL,
                fib_23_6 REAL NOT NULL,
                fib_38_2 REAL NOT NULL,
                fib_50_0 REAL NOT NULL,
                fib_61_8 REAL NOT NULL,
                fib_78_6 REAL NOT NULL,
                fib_100 REAL NOT NULL,
                current_price REAL NOT NULL,
                price_position TEXT NOT NULL,
                nearest_support REAL,
                nearest_resistance REAL,
                support_distance REAL,
                resistance_distance REAL,
                trend_direction TEXT DEFAULT 'neutral',
                swing_strength REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                UNIQUE(symbol, timeframe)
            )
        """)
        
        # Create indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fibonacci_data_symbol 
            ON fibonacci_data(symbol)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fibonacci_data_timeframe 
            ON fibonacci_data(timeframe)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fibonacci_data_position 
            ON fibonacci_data(price_position)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fibonacci_data_updated 
            ON fibonacci_data(last_updated)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Fibonacci data table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Fibonacci table: {e}")
        return False

if __name__ == "__main__":
    create_fibonacci_table()
