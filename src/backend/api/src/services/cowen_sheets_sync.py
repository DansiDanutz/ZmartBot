#!/usr/bin/env python3
"""
Benjamin Cowen's Risk Band Data Synchronization
Automatically pulls and updates risk band data from Google Sheets daily
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import sqlite3
import math

logger = logging.getLogger(__name__)

class CowenSheetsSync:
    """
    Synchronizes Benjamin Cowen's risk band data from Google Sheets
    Updates the RiskMetric database with real, current data
    """
    
    def __init__(self, credentials_path: str = "credentials/google_service_account.json"):
        """
        Initialize Google Sheets sync service
        
        Args:
            credentials_path: Path to Google service account credentials JSON
        """
        self.credentials_path = credentials_path
        self.db_path = "data/comprehensive_riskmetric.db"
        
        # Google Sheets IDs from your URLs
        self.sheets_config = {
            'risk_bands': {
                'spreadsheet_id': '1F-0_I2zy7MIQ_thTF2g4oaTZNiv1aV4x',
                'sheet_name': 'Risk Bands',  # Adjust based on actual sheet name
                'range': 'A1:Z1000'  # Adjust based on data range
            },
            'time_spent': {
                'spreadsheet_id': '1fup2CUYxg7Tj3a2BvpoN3OcfGBoSe7EqHIxmp1RRjqg',
                'sheet_name': 'Time Spent Analysis',  # Adjust based on actual sheet name
                'range': 'A1:Z1000'
            }
        }
        
        self.service = None
        self.last_sync = None
        
        logger.info("Cowen Sheets Sync initialized")
    
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Use service account credentials
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            
            self.service = build('sheets', 'v4', credentials=creds)
            logger.info("Successfully authenticated with Google Sheets API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {e}")
            return False
    
    async def fetch_risk_bands_data(self) -> Dict[str, Any]:
        """
        Fetch risk band data from Benjamin Cowen's sheet
        
        Expected columns:
        - Symbol
        - Risk 0%, Risk 10%, Risk 20%, ... Risk 100% (price levels)
        - Current Price
        - Current Risk
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return {}
            
            if self.service:
                sheet = self.service.spreadsheets()
            else:
                return {}
            result = sheet.values().get(
                spreadsheetId=self.sheets_config['risk_bands']['spreadsheet_id'],
                range=self.sheets_config['risk_bands']['range']
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in risk bands sheet")
                return {}
            
            # Parse the data
            headers = values[0]
            data = {}
            
            for row in values[1:]:
                if len(row) < 2:
                    continue
                
                symbol = row[0].upper()
                risk_data = {
                    'symbol': symbol,
                    'risk_levels': {},
                    'current_price': None,
                    'current_risk': None,
                    'last_updated': datetime.now()
                }
                
                # Parse risk level columns (0%, 10%, 20%, etc.)
                for i, header in enumerate(headers):
                    if i >= len(row):
                        break
                        
                    value = row[i]
                    
                    # Check for risk percentage columns
                    if 'risk' in header.lower() and '%' in header:
                        try:
                            # Extract percentage value
                            risk_pct = float(header.replace('Risk', '').replace('%', '').strip()) / 100
                            price = float(value.replace('$', '').replace(',', ''))
                            risk_data['risk_levels'][risk_pct] = price
                        except:
                            pass
                    
                    # Check for current price
                    elif 'current price' in header.lower():
                        try:
                            risk_data['current_price'] = float(value.replace('$', '').replace(',', ''))
                        except:
                            pass
                    
                    # Check for current risk
                    elif 'current risk' in header.lower():
                        try:
                            risk_data['current_risk'] = float(value.replace('%', '')) / 100
                        except:
                            pass
                
                data[symbol] = risk_data
            
            logger.info(f"Fetched risk band data for {len(data)} symbols")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching risk bands data: {e}")
            return {}
    
    async def fetch_time_spent_data(self) -> Dict[str, Any]:
        """
        Fetch time spent in bands data from Benjamin Cowen's sheet
        
        Expected columns:
        - Symbol
        - Band (0-10%, 10-20%, etc.)
        - Days Spent
        - Percentage
        - Coefficient
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return {}
            
            if self.service:
                sheet = self.service.spreadsheets()
            else:
                return {}
            result = sheet.values().get(
                spreadsheetId=self.sheets_config['time_spent']['spreadsheet_id'],
                range=self.sheets_config['time_spent']['range']
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in time spent sheet")
                return {}
            
            # Parse the data
            headers = values[0]
            data = {}
            
            for row in values[1:]:
                if len(row) < 3:
                    continue
                
                # Parse based on expected structure
                symbol = row[0].upper()
                
                if symbol not in data:
                    data[symbol] = {
                        'symbol': symbol,
                        'bands': {},
                        'total_days': 0,
                        'inception_date': None
                    }
                
                # Try to parse band data
                try:
                    band = row[1]  # e.g., "0-10%"
                    days_spent = int(row[2]) if len(row) > 2 else 0
                    percentage = float(row[3].replace('%', '')) if len(row) > 3 else 0
                    coefficient = float(row[4]) if len(row) > 4 else 1.0
                    
                    # Parse band range
                    band_parts = band.replace('%', '').split('-')
                    if len(band_parts) == 2:
                        band_start = float(band_parts[0]) / 100
                        band_end = float(band_parts[1]) / 100
                        
                        data[symbol]['bands'][band] = {
                            'band_start': band_start,
                            'band_end': band_end,
                            'days_spent': days_spent,
                            'percentage': percentage,
                            'coefficient': coefficient
                        }
                        
                        data[symbol]['total_days'] += days_spent
                        
                except Exception as e:
                    logger.debug(f"Error parsing row for {symbol}: {e}")
                    continue
            
            logger.info(f"Fetched time spent data for {len(data)} symbols")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching time spent data: {e}")
            return {}
    
    async def calculate_dynamic_coefficients(self, time_spent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate dynamic coefficients based on actual time spent
        Following Benjamin Cowen's methodology
        """
        for symbol, data in time_spent_data.items():
            for band_key, band_data in data['bands'].items():
                percentage = band_data['percentage']
                
                # Calculate coefficient based on rarity
                if percentage == 0:
                    coefficient = 1.6  # Never visited - maximum coefficient
                elif percentage < 1:
                    coefficient = 1.6  # Extremely rare
                elif percentage < 2.5:
                    coefficient = 1.55  # Very rare
                elif percentage < 5:
                    coefficient = 1.5  # Rare
                elif percentage < 10:
                    coefficient = 1.4  # Uncommon
                elif percentage < 15:
                    coefficient = 1.3  # Below average
                elif percentage < 20:
                    coefficient = 1.2  # Slightly below average
                elif percentage < 30:
                    coefficient = 1.1  # Near average
                elif percentage < 40:
                    coefficient = 1.0  # Average
                else:
                    coefficient = 0.95  # Common (slight penalty)
                
                # Update coefficient
                band_data['coefficient'] = coefficient
                band_data['rarity_score'] = math.exp(-percentage / 10) if percentage > 0 else 1.0
        
        return time_spent_data
    
    async def update_database(self, risk_bands_data: Dict[str, Any], time_spent_data: Dict[str, Any]):
        """Update the RiskMetric database with fetched data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Update risk levels
            for symbol, risk_data in risk_bands_data.items():
                # Update symbols table
                cursor.execute('''
                    INSERT OR REPLACE INTO symbols 
                    (symbol, name, current_price, current_risk, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    symbol,  # Use symbol as name if not provided
                    risk_data.get('current_price'),
                    risk_data.get('current_risk'),
                    datetime.now()
                ))
                
                # Update risk levels
                for risk_value, price in risk_data['risk_levels'].items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO risk_levels
                        (symbol, risk_value, price, calculated_date)
                        VALUES (?, ?, ?, ?)
                    ''', (symbol, risk_value, price, datetime.now().date()))
            
            # Update time spent bands
            for symbol, spent_data in time_spent_data.items():
                total_days = spent_data['total_days']
                
                for band_key, band_data in spent_data['bands'].items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO time_spent_bands
                        (symbol, band_start, band_end, days_spent, percentage, 
                         coefficient, total_days, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol,
                        band_data['band_start'],
                        band_data['band_end'],
                        band_data['days_spent'],
                        band_data['percentage'],
                        band_data['coefficient'],
                        total_days,
                        datetime.now().date()
                    ))
            
            # Log the sync
            cursor.execute('''
                INSERT INTO manual_overrides
                (symbol, override_type, override_value, override_reason, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'SYSTEM',
                'google_sheets_sync',
                datetime.now().isoformat(),
                f'Synced data for {len(risk_bands_data)} symbols',
                'CowenSheetsSync'
            ))
            
            conn.commit()
            logger.info(f"Updated database with {len(risk_bands_data)} symbols")
            
        except Exception as e:
            logger.error(f"Error updating database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    async def sync_all_data(self):
        """Perform complete sync of all data from Google Sheets"""
        logger.info("Starting full data sync from Benjamin Cowen's sheets...")
        
        # Fetch risk bands
        risk_bands_data = await self.fetch_risk_bands_data()
        if not risk_bands_data:
            logger.error("Failed to fetch risk bands data")
            return False
        
        # Fetch time spent data
        time_spent_data = await self.fetch_time_spent_data()
        if not time_spent_data:
            logger.error("Failed to fetch time spent data")
            return False
        
        # Calculate dynamic coefficients
        time_spent_data = await self.calculate_dynamic_coefficients(time_spent_data)
        
        # Update database
        await self.update_database(risk_bands_data, time_spent_data)
        
        self.last_sync = datetime.now()
        logger.info(f"Full sync completed at {self.last_sync}")
        return True
    
    async def start_daily_sync(self, sync_hour: int = 2):
        """
        Start daily synchronization at specified hour (UTC)
        
        Args:
            sync_hour: Hour of day to sync (0-23, default 2 AM UTC)
        """
        logger.info(f"Starting daily sync scheduler (sync at {sync_hour:02d}:00 UTC)")
        
        while True:
            try:
                now = datetime.now()
                
                # Calculate next sync time
                next_sync = now.replace(hour=sync_hour, minute=0, second=0, microsecond=0)
                if now >= next_sync:
                    # If we've passed today's sync time, schedule for tomorrow
                    next_sync += timedelta(days=1)
                
                # Wait until sync time
                wait_seconds = (next_sync - now).total_seconds()
                logger.info(f"Next sync scheduled for {next_sync} ({wait_seconds/3600:.1f} hours from now)")
                
                await asyncio.sleep(wait_seconds)
                
                # Perform sync
                logger.info("Starting scheduled daily sync...")
                success = await self.sync_all_data()
                
                if success:
                    logger.info("Daily sync completed successfully")
                    
                    # Send Telegram notification if configured
                    try:
                        from src.services.telegram_notifications import get_telegram_service, AlertLevel
                        telegram = get_telegram_service()
                        if telegram.enabled:
                            await telegram.send_message(
                                f"✅ RiskMetric data sync completed\n"
                                f"Updated data from Benjamin Cowen's sheets\n"
                                f"Next sync: {next_sync + timedelta(days=1)}",
                                level=AlertLevel.SUCCESS
                            )
                    except:
                        pass
                else:
                    logger.error("Daily sync failed")
                    
            except Exception as e:
                logger.error(f"Error in daily sync scheduler: {e}")
                # Wait 1 hour before retrying
                await asyncio.sleep(3600)

# Manual sync function
async def manual_sync():
    """Manually trigger a sync from Google Sheets"""
    sync_service = CowenSheetsSync()
    success = await sync_service.sync_all_data()
    
    if success:
        print("✅ Manual sync completed successfully")
        
        # Show summary
        conn = sqlite3.connect(sync_service.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM risk_levels")
        symbol_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM time_spent_bands")
        time_spent_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  - Risk levels updated for {symbol_count} symbols")
        print(f"  - Time spent data updated for {time_spent_count} symbols")
    else:
        print("❌ Manual sync failed")

# Example usage
if __name__ == "__main__":
    # Run manual sync
    asyncio.run(manual_sync())