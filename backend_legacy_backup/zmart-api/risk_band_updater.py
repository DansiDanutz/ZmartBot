#!/usr/bin/env python3
"""
Risk Band Updater Script
Automatically adds +1 day to the corresponding risk band when Life Age increments
This script is triggered by the Life Age updater
"""

import sqlite3
import logging
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('risk_band_updater.log'),
        logging.StreamHandler()
    ]
)

# Database paths
DB_PATH = Path(__file__).parent / 'data' / 'life_age.db'
RISK_BANDS_DB_PATH = Path(__file__).parent / 'data' / 'risk_bands.db'

# All symbols from the menu
SYMBOLS = [
    'BTC', 'ETH', 'XRP', 'BNB', 'SOL', 'DOGE', 'ADA', 'LINK', 'AVAX', 
    'XLM', 'SUI', 'DOT', 'LTC', 'XMR', 'AAVE', 'VET', 'ATOM', 'RENDER', 
    'HBAR', 'XTZ', 'TON', 'TRX'
]

def create_risk_bands_table():
    """Create the risk_bands table if it doesn't exist"""
    try:
        conn = sqlite3.connect(RISK_BANDS_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_bands (
                symbol TEXT,
                band_key TEXT,
                days INTEGER DEFAULT 0,
                percentage REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, band_key)
            )
        ''')
        
        # Create daily updates tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_band_daily_updates (
                update_date TEXT PRIMARY KEY,
                last_update_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Initialize all symbols with default risk bands
        risk_bands = [
            '0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5',
            '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0'
        ]
        
        for symbol in SYMBOLS:
            for band in risk_bands:
                cursor.execute('''
                    INSERT OR IGNORE INTO risk_bands (symbol, band_key, days, percentage)
                    VALUES (?, ?, 0, 0.0)
                ''', (symbol, band))
        
        conn.commit()
        conn.close()
        logging.info(f"✅ Risk bands table created/initialized with {len(SYMBOLS)} symbols")
        
    except Exception as e:
        logging.error(f"❌ Error creating risk bands table: {e}")

def get_last_risk_value(symbol):
    """Get the last risk value for a symbol from the frontend API"""
    try:
        # Try to get current price and calculate risk value
        response = requests.get(f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT', timeout=10)
        if response.status_code == 200:
            price_data = response.json()
            current_price = float(price_data['price'])
            
            # Calculate risk value using the polynomial formula
            # Risk = −0.380790057100 + 1.718335491963×10⁻⁵⋅P − 1.213364209168×10⁻¹⁰⋅P² + 4.390647720677×10⁻¹⁶⋅P³ − 5.830886880671×10⁻²²⋅P⁴
            a0 = -0.380790057100
            a1 = 1.718335491963e-5
            a2 = -1.213364209168e-10
            a3 = 4.390647720677e-16
            a4 = -5.830886880671e-22
            
            P = current_price
            risk_value = a0 + a1*P + a2*P*P + a3*P*P*P + a4*P*P*P*P
            
            # Clamp to 0-1 range
            risk_value = max(0, min(1, risk_value))
            
            logging.info(f"📊 {symbol} current price: ${current_price:,.2f}, risk value: {risk_value:.3f}")
            return risk_value
        else:
            logging.warning(f"⚠️ Could not get price for {symbol}, using default risk value")
            return 0.5  # Default risk value
            
    except Exception as e:
        logging.error(f"❌ Error getting risk value for {symbol}: {e}")
        return 0.5  # Default risk value

def get_risk_band(risk_value):
    """Get the risk band for a given risk value"""
    if risk_value < 0.1:
        return '0.0-0.1'
    elif risk_value < 0.2:
        return '0.1-0.2'
    elif risk_value < 0.3:
        return '0.2-0.3'
    elif risk_value < 0.4:
        return '0.3-0.4'
    elif risk_value < 0.5:
        return '0.4-0.5'
    elif risk_value < 0.6:
        return '0.5-0.6'
    elif risk_value < 0.7:
        return '0.6-0.7'
    elif risk_value < 0.8:
        return '0.7-0.8'
    elif risk_value < 0.9:
        return '0.8-0.9'
    else:
        return '0.9-1.0'

def update_risk_band(symbol, risk_value):
    """Update the risk band for a symbol based on current risk value"""
    try:
        conn = sqlite3.connect(RISK_BANDS_DB_PATH)
        cursor = conn.cursor()
        
        # Get the risk band for the current risk value
        band_key = get_risk_band(risk_value)
        
        # Get current days for this band
        cursor.execute('SELECT days FROM risk_bands WHERE symbol = ? AND band_key = ?', (symbol, band_key))
        result = cursor.fetchone()
        current_days = result[0] if result else 0
        
        # Increment days by 1
        new_days = current_days + 1
        
        # Update the risk band
        cursor.execute('''
            UPDATE risk_bands 
            SET days = ?, last_updated = CURRENT_TIMESTAMP
            WHERE symbol = ? AND band_key = ?
        ''', (new_days, symbol, band_key))
        
        # Log the Risk Band update
        try:
            import subprocess
            subprocess.run(['python3', '-c', f'from update_logger import log_risk_band_update; log_risk_band_update("{symbol}", {risk_value}, "{band_key}", {current_days}, {new_days})'], 
                          capture_output=True, text=True, cwd=Path(__file__).parent)
        except Exception as e:
            logging.error(f"❌ Error logging Risk Band update for {symbol}: {e}")
        
        # Recalculate percentages for all bands
        cursor.execute('SELECT SUM(days) FROM risk_bands WHERE symbol = ?', (symbol,))
        total_days = cursor.fetchone()[0] or 0
        
        if total_days > 0:
            cursor.execute('SELECT band_key FROM risk_bands WHERE symbol = ?', (symbol,))
            bands = cursor.fetchall()
            
            for (band,) in bands:
                cursor.execute('SELECT days FROM risk_bands WHERE symbol = ? AND band_key = ?', (symbol, band))
                days = cursor.fetchone()[0] or 0
                percentage = (days / total_days) * 100
                
                cursor.execute('''
                    UPDATE risk_bands 
                    SET percentage = ?
                    WHERE symbol = ? AND band_key = ?
                ''', (percentage, symbol, band))
        
        conn.commit()
        conn.close()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"✅ {symbol} risk band updated: {band_key} ({current_days} → {new_days} days) at {current_time}")
        logging.info(f"📊 {symbol} percentages recalculated for all bands based on new total: {total_days} days")
        
        # Trigger coefficient update after risk band and percentage updates
        try:
            from dynamic_coefficient_matrix import generate_daily_coefficient_matrix
            from risk_coefficient import get_coefficient
            from scoring_system import calculate_final_score
            
            # Get current risk value for coefficient calculation
            current_risk_value = get_last_risk_value(symbol)
            
            # Get updated risk bands data
            risk_bands_data = get_risk_bands_data(symbol)
            
            # Generate coefficient matrix
            coefficient_matrix = generate_daily_coefficient_matrix(
                current_risk_value=current_risk_value,
                risk_bands_data=risk_bands_data,
                previous_risk_band=None,  # Will be determined by the system
                last_band_change_date=None  # Will be determined by the system
            )
            
            # Calculate current coefficient using DBI methodology
            current_coefficient = get_coefficient(
                risk_value=current_risk_value,
                previous_risk_band=None,
                last_band_change_date=None
            )
            
            logging.info(f"🎯 {symbol} coefficient updated (DBI): {current_coefficient:.3f} at {current_time}")
            
            # Step 5: Calculate final score (Base Score × Coefficient = Final Score)
            final_score_result = calculate_final_score(symbol, current_risk_value)
            
            logging.info(f"🏆 {symbol} final score updated: {final_score_result['final_score']:.2f} (Base: {final_score_result['base_score']:.2f} × Coef: {final_score_result['coefficient']:.3f}) at {current_time}")
            logging.info(f"📊 {symbol} signal: {final_score_result['signal_strength']}")
            
        except Exception as e:
            logging.error(f"❌ Error updating coefficient/score for {symbol}: {e}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Error updating risk band for {symbol}: {e}")
        return False

def update_all_risk_bands():
    """Update risk bands for all symbols based on current risk values"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"🔄 Starting risk band updates for all symbols at {current_time}...")
    
    # Ensure tables exist
    create_risk_bands_table()
    
    # Get current date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check if we already updated today
    try:
        conn = sqlite3.connect(RISK_BANDS_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT last_update_date FROM risk_band_daily_updates WHERE update_date = ?', (today,))
        already_updated = cursor.fetchone()
        
        if already_updated:
            logging.info(f"✅ Risk bands already updated today ({today}), skipping...")
            conn.close()
            return 0
        
        conn.close()
    except Exception as e:
        logging.error(f"❌ Error checking daily updates: {e}")
    
    updated_count = 0
    for symbol in SYMBOLS:
        try:
            # Get current risk value
            risk_value = get_last_risk_value(symbol)
            
            # Update the corresponding risk band
            if update_risk_band(symbol, risk_value):
                updated_count += 1
                
        except Exception as e:
            logging.error(f"❌ Error processing {symbol}: {e}")
    
    # Mark today as updated if we processed any symbols
    if updated_count > 0:
        try:
            conn = sqlite3.connect(RISK_BANDS_DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO risk_band_daily_updates (update_date, last_update_date)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (today,))
            
            conn.commit()
            conn.close()
            logging.info(f"✅ Marked risk bands as updated for {today} at {current_time}")
        except Exception as e:
            logging.error(f"❌ Error marking daily update: {e}")
    
    logging.info(f"✅ Risk band updates completed: {updated_count}/{len(SYMBOLS)} symbols updated at {current_time}")
    return updated_count

def get_risk_bands_data(symbol):
    """Get risk bands data for a symbol"""
    try:
        conn = sqlite3.connect(RISK_BANDS_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT band_key, days, percentage 
            FROM risk_bands 
            WHERE symbol = ? 
            ORDER BY band_key
        ''', (symbol,))
        
        results = cursor.fetchall()
        conn.close()
        
        risk_bands = {}
        for band_key, days, percentage in results:
            risk_bands[band_key] = {
                'days': days,
                'percentage': percentage
            }
        
        return risk_bands
        
    except Exception as e:
        logging.error(f"❌ Error getting risk bands data for {symbol}: {e}")
        return {}

def main():
    """Main function to run risk band updates"""
    logging.info("🚀 Risk Band Updater starting...")
    
    # Update all risk bands
    success_count = update_all_risk_bands()
    
    if success_count > 0:
        logging.info(f"✅ Successfully updated {success_count} symbols")
    else:
        logging.error("❌ No symbols were updated")
    
    return success_count

if __name__ == "__main__":
    main()
