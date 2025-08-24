#!/usr/bin/env python3
import asyncio
import aiohttp
import sys
import sqlite3
from datetime import datetime, timedelta, timezone

sys.path.append('src')
from src.services.ultimate_riskmetric_database import UltimateRiskMetricDatabase

print('🔄 CORRECTED COMPLETE DATABASE UPDATE')
print('=' * 60)
print('Fixing the previous incomplete update')
print('')

# Configuration
BINANCE_SYMBOLS = {
    'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'SOL': 'SOLUSDT', 'XRP': 'XRPUSDT',
    'ADA': 'ADAUSDT', 'AVAX': 'AVAXUSDT', 'DOT': 'DOTUSDT', 'LINK': 'LINKUSDT',
    'LTC': 'LTCUSDT', 'DOGE': 'DOGEUSDT', 'BNB': 'BNBUSDT', 'TRX': 'TRXUSDT',
    'ATOM': 'ATOMUSDT', 'XLM': 'XLMUSDT', 'VET': 'VETUSDT', 'HBAR': 'HBARUSDT',
    'AAVE': 'AAVEUSDT', 'SUI': 'SUIUSDT', 'TON': 'TONUSDT'
}

COINGECKO_SYMBOLS = {'RENDER': 'render-token', 'XMR': 'monero'}

def determine_risk_band(price, min_price, max_price):
    if max_price <= min_price:
        return '0.5-0.6'
    risk_value = (price - min_price) / (max_price - min_price)
    risk_value = max(0.0, min(1.0, risk_value))
    bands = ['0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5', 
             '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']
    return bands[min(int(risk_value * 10), 9)]

async def fetch_prices(date, session):
    date_str = date.strftime('%Y-%m-%d')
    day_start = int(date.replace(hour=0, minute=0, second=0).timestamp() * 1000)
    day_end = int(date.replace(hour=23, minute=59, second=59).timestamp() * 1000)
    prices = {}
    
    # Binance
    for symbol, pair in BINANCE_SYMBOLS.items():
        try:
            params = {'symbol': pair, 'interval': '1d', 'startTime': day_start, 'endTime': day_end, 'limit': 1}
            async with session.get('https://api.binance.com/api/v3/klines', params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data:
                        prices[symbol] = float(data[0][4])
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f'    ❌ {symbol}: {e}')
    
    # CoinGecko
    for symbol, coin_id in COINGECKO_SYMBOLS.items():
        try:
            cg_date = date.strftime('%d-%m-%Y')
            params = {'date': cg_date, 'localization': 'false'}
            async with session.get(f'https://api.coingecko.com/api/v3/coins/{coin_id}/history', params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'market_data' in data and 'current_price' in data['market_data']:
                        price = data['market_data']['current_price'].get('usd')
                        if price:
                            prices[symbol] = price
            await asyncio.sleep(1.1)
        except Exception as e:
            print(f'    ❌ {symbol}: {e}')
    
    return date_str, prices

def update_database_day(date_str, prices, db):
    """Update database with proper error handling and verification"""
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    updates = 0
    
    try:
        for symbol, price in prices.items():
            try:
                # Get symbol info
                cursor.execute('SELECT id, min_price, max_price FROM symbols WHERE symbol = ?', (symbol,))
                result = cursor.fetchone()
                if not result:
                    print(f'    ⚠️  {symbol}: Not found in symbols table')
                    continue
                
                symbol_id, min_price, max_price = result
                target_band = determine_risk_band(price, min_price, max_price)
                
                # Get previous day data
                cursor.execute('''
                    SELECT risk_band, days_in_band, total_days 
                    FROM time_in_bands 
                    WHERE symbol_id = ? AND last_updated = (
                        SELECT MAX(last_updated) FROM time_in_bands WHERE symbol_id = ?
                    )
                ''', (symbol_id, symbol_id))
                
                current_bands = {}
                current_total = 0
                for row in cursor.fetchall():
                    band, days, total = row
                    current_bands[band] = days
                    current_total = total
                
                if not current_bands:
                    print(f'    ⚠️  {symbol}: No previous data found')
                    continue
                
                # Calculate new values
                new_days = current_bands.get(target_band, 0) + 1
                new_total = current_total + 1
                
                # Delete existing data for this date (if any)
                cursor.execute('DELETE FROM time_in_bands WHERE symbol_id = ? AND last_updated = ?', (symbol_id, date_str))
                
                # Insert all bands with updated data
                for band in ['0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5', 
                             '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']:
                    days = current_bands.get(band, 0)
                    if band == target_band:
                        days = new_days
                    
                    cursor.execute('''
                        INSERT INTO time_in_bands 
                        (symbol_id, risk_band, days_in_band, total_days, percentage, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (symbol_id, band, days, new_total, (days/new_total)*100, date_str))
                
                updates += 1
                print(f'    ✅ {symbol}: ${price:,.4f} → {target_band} (total: {new_total})')
                
            except Exception as e:
                print(f'    ❌ Error updating {symbol}: {e}')
        
        # Update symbols table
        cursor.execute('UPDATE symbols SET last_update_date = ?', (date_str,))
        
        # Commit changes
        conn.commit()
        
        # Verify the data was saved
        cursor.execute('SELECT COUNT(*) FROM time_in_bands WHERE last_updated = ?', (date_str,))
        saved_records = cursor.fetchone()[0]
        print(f'    📊 Verified: {saved_records} records saved for {date_str}')
        
    except Exception as e:
        print(f'    ❌ Database error for {date_str}: {e}')
        conn.rollback()
    finally:
        conn.close()
    
    return updates

async def main():
    # Generate ALL dates from July 11 to August 1
    start_date = datetime(2025, 7, 11, tzinfo=timezone.utc)
    end_date = datetime(2025, 8, 1, tzinfo=timezone.utc)
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    
    print(f'📅 Processing {len(dates)} days: {dates[0].strftime("%Y-%m-%d")} → {dates[-1].strftime("%Y-%m-%d")}')
    print('')
    
    db = UltimateRiskMetricDatabase()
    total_updates = 0
    successful_days = 0
    
    async with aiohttp.ClientSession() as session:
        for i, date in enumerate(dates):
            print(f'📈 Day {i+1}/{len(dates)}: {date.strftime("%Y-%m-%d")}')
            
            try:
                date_str, prices = await fetch_prices(date, session)
                if prices:
                    updates = update_database_day(date_str, prices, db)
                    total_updates += updates
                    successful_days += 1
                    print(f'    ✅ Completed: {updates} symbols updated')
                else:
                    print(f'    ❌ No prices fetched')
            except Exception as e:
                print(f'    ❌ Error: {e}')
            
            print('')  # Space between days
            await asyncio.sleep(1)  # Rate limiting
    
    print('🎉 CORRECTED UPDATE COMPLETE!')
    print('=' * 50)
    print(f'✅ Days processed: {successful_days}/{len(dates)}')
    print(f'✅ Symbol updates: {total_updates}')
    
    # Final verification
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT last_updated) FROM time_in_bands WHERE last_updated >= "2025-07-11"')
    final_dates = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM time_in_bands WHERE last_updated >= "2025-07-11"')
    final_records = cursor.fetchone()[0]
    conn.close()
    
    print(f'✅ Final verification: {final_dates} dates, {final_records} records')

if __name__ == "__main__":
    asyncio.run(main())
