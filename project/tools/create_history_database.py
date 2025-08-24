#!/usr/bin/env python3
"""
Create HistoryMySymbols Database
Creates a comprehensive historical database to store hourly snapshots of all symbol data
for pattern analysis and historical trend analysis.
"""

import sqlite3
import os
from datetime import datetime

def create_history_database():
    """Create the HistoryMySymbols database with all necessary tables"""
    
    db_path = 'HistoryMySymbols.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Removed existing {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🚀 Creating {db_path}...")
    
    # Create historical RSI data table
    cursor.execute("""
        CREATE TABLE historical_rsi_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            rsi_value REAL NOT NULL,
            signal_status TEXT NOT NULL,
            divergence_type TEXT DEFAULT 'none',
            divergence_strength REAL DEFAULT 0.0,
            current_price REAL NOT NULL,
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical EMA data table
    cursor.execute("""
        CREATE TABLE historical_ema_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            ema_9 REAL NOT NULL,
            ema_12 REAL NOT NULL,
            ema_20 REAL NOT NULL,
            ema_21 REAL NOT NULL,
            ema_26 REAL NOT NULL,
            ema_50 REAL NOT NULL,
            cross_signal TEXT NOT NULL,
            cross_strength REAL DEFAULT 0.0,
            golden_cross_detected BOOLEAN DEFAULT 0,
            death_cross_detected BOOLEAN DEFAULT 0,
            short_term_trend TEXT DEFAULT 'neutral',
            long_term_trend TEXT DEFAULT 'neutral',
            current_price REAL NOT NULL,
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical MACD data table
    cursor.execute("""
        CREATE TABLE historical_macd_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            macd_line REAL NOT NULL,
            signal_line REAL NOT NULL,
            histogram REAL NOT NULL,
            signal_status TEXT NOT NULL,
            current_price REAL NOT NULL,
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical Bollinger Bands data table
    cursor.execute("""
        CREATE TABLE historical_bollinger_bands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            sma REAL NOT NULL,
            upper_band REAL NOT NULL,
            lower_band REAL NOT NULL,
            bandwidth REAL NOT NULL,
            position REAL NOT NULL,
            current_price REAL NOT NULL,
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical Volume data table
    cursor.execute("""
        CREATE TABLE historical_volume_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical Support/Resistance data table
    cursor.execute("""
        CREATE TABLE historical_support_resistance_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            support_level_1 REAL NOT NULL,
            support_level_2 REAL NOT NULL,
            support_level_3 REAL NOT NULL,
            resistance_level_1 REAL NOT NULL,
            resistance_level_2 REAL NOT NULL,
            resistance_level_3 REAL NOT NULL,
            current_price REAL NOT NULL,
            price_position TEXT NOT NULL,
            nearest_support REAL NOT NULL,
            nearest_resistance REAL NOT NULL,
            support_distance REAL NOT NULL,
            resistance_distance REAL NOT NULL,
            support_strength REAL DEFAULT 0.0,
            resistance_strength REAL DEFAULT 0.0,
            breakout_potential TEXT DEFAULT 'none',
            breakout_direction TEXT DEFAULT 'neutral',
            breakout_strength REAL DEFAULT 0.0,
            volume_confirmation TEXT DEFAULT 'none',
            volume_strength REAL DEFAULT 0.0,
            trend_alignment TEXT DEFAULT 'neutral',
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical Fibonacci data table
    cursor.execute("""
        CREATE TABLE historical_fibonacci_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            fib_0 REAL NOT NULL,
            fib_236 REAL NOT NULL,
            fib_382 REAL NOT NULL,
            fib_500 REAL NOT NULL,
            fib_618 REAL NOT NULL,
            fib_786 REAL NOT NULL,
            fib_1000 REAL NOT NULL,
            fib_1618 REAL NOT NULL,
            fib_2618 REAL NOT NULL,
            current_price REAL NOT NULL,
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical Stochastic RSI data table
    cursor.execute("""
        CREATE TABLE historical_stoch_rsi_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            stoch_rsi_k REAL NOT NULL,
            stoch_rsi_d REAL NOT NULL,
            signal_status TEXT NOT NULL,
            current_price REAL NOT NULL,
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create historical price data table (for pattern analysis)
    cursor.execute("""
        CREATE TABLE historical_price_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            open_price REAL NOT NULL,
            high_price REAL NOT NULL,
            low_price REAL NOT NULL,
            close_price REAL NOT NULL,
            volume REAL NOT NULL,
            price_change REAL NOT NULL,
            price_change_percent REAL NOT NULL,
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create pattern analysis summary table
    cursor.execute("""
        CREATE TABLE historical_pattern_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timeframe TEXT NOT NULL,
            pattern_type TEXT NOT NULL,
            pattern_strength REAL NOT NULL,
            pattern_direction TEXT NOT NULL,
            pattern_confidence REAL NOT NULL,
            support_level REAL,
            resistance_level REAL,
            target_price REAL,
            stop_loss REAL,
            risk_reward_ratio REAL,
            volume_confirmation BOOLEAN DEFAULT 0,
            trend_alignment TEXT DEFAULT 'neutral',
            snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better query performance
    print("📊 Creating indexes...")
    
    # Indexes for symbol and timeframe queries
    cursor.execute("CREATE INDEX idx_hist_rsi_symbol_timeframe ON historical_rsi_data(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_ema_symbol_timeframe ON historical_ema_data(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_macd_symbol_timeframe ON historical_macd_data(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_bb_symbol_timeframe ON historical_bollinger_bands(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_volume_symbol_timeframe ON historical_volume_data(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_sr_symbol_timeframe ON historical_support_resistance_data(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_fib_symbol_timeframe ON historical_fibonacci_data(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_stoch_symbol_timeframe ON historical_stoch_rsi_data(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_price_symbol_timeframe ON historical_price_data(symbol, timeframe)")
    cursor.execute("CREATE INDEX idx_hist_pattern_symbol_timeframe ON historical_pattern_summary(symbol, timeframe)")
    
    # Indexes for timestamp queries (for time-based analysis)
    cursor.execute("CREATE INDEX idx_hist_rsi_timestamp ON historical_rsi_data(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_ema_timestamp ON historical_ema_data(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_macd_timestamp ON historical_macd_data(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_bb_timestamp ON historical_bollinger_bands(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_volume_timestamp ON historical_volume_data(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_sr_timestamp ON historical_support_resistance_data(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_fib_timestamp ON historical_fibonacci_data(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_stoch_timestamp ON historical_stoch_rsi_data(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_price_timestamp ON historical_price_data(snapshot_timestamp)")
    cursor.execute("CREATE INDEX idx_hist_pattern_timestamp ON historical_pattern_summary(snapshot_timestamp)")
    
    # Indexes for pattern analysis
    cursor.execute("CREATE INDEX idx_hist_pattern_type ON historical_pattern_summary(pattern_type)")
    cursor.execute("CREATE INDEX idx_hist_pattern_strength ON historical_pattern_summary(pattern_strength)")
    cursor.execute("CREATE INDEX idx_hist_pattern_direction ON historical_pattern_summary(pattern_direction)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Successfully created {db_path}")
    print("📊 Database tables created:")
    print("   - historical_rsi_data")
    print("   - historical_ema_data")
    print("   - historical_macd_data")
    print("   - historical_bollinger_bands")
    print("   - historical_volume_data")
    print("   - historical_support_resistance_data")
    print("   - historical_fibonacci_data")
    print("   - historical_stoch_rsi_data")
    print("   - historical_price_data")
    print("   - historical_pattern_summary")
    print("📈 Indexes created for optimal query performance")
    print("🕐 Ready for hourly historical data storage!")

if __name__ == "__main__":
    create_history_database()
