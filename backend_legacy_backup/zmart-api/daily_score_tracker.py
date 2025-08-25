#!/usr/bin/env python3
"""
Daily Score Tracker
Automatically records Base Score and Total Score for all tracked symbols
Runs daily to build comprehensive score history database
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.score_tracking_service import ScoreTrackingService
from src.utils.database import get_postgres_connection, postgres_transaction
from src.agents.database.cowen_riskmetric_production_agent import CowenRiskMetricAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_score_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyScoreTracker:
    """
    Daily Score Tracker for recording Base Score and Total Score
    """
    
    def __init__(self):
        self.score_tracking_service = ScoreTrackingService()
        self.riskmetric_agent = CowenRiskMetricAgent()
        self.logger = logging.getLogger(__name__)
    
    async def get_all_symbols(self) -> List[str]:
        """Get all symbols that need score tracking"""
        try:
            # For now, use a predefined list of major symbols
            # In the future, this could be fetched from a database
            symbols = [
                'BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'AVAX', 'DOT', 'MATIC',
                'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'XLM', 'BCH', 'FIL',
                'TRX', 'NEAR', 'ALGO', 'VET', 'ICP', 'FTM'
            ]
            
            self.logger.info(f"Retrieved {len(symbols)} symbols for score tracking")
            return symbols
            
        except Exception as e:
            self.logger.error(f"Error getting symbols: {e}")
            return []
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol from Binance API"""
        try:
            import aiohttp
            
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data['price'])
                    else:
                        self.logger.warning(f"Failed to get price for {symbol}: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    async def calculate_risk_value(self, symbol: str, price: float) -> Optional[float]:
        """Calculate risk value using the polynomial formula"""
        try:
            # Use the same formula as in the frontend
            a0 = -0.380790057100
            a1 = 1.718335491963e-5
            a2 = -1.213364209168e-10
            a3 = 4.390647720677e-16
            a4 = -5.830886880671e-22
            
            P = price
            risk_value = a0 + a1*P + a2*P*P + a3*P*P*P + a4*P*P*P*P
            
            # Ensure the result is between 0 and 1
            risk_value = max(0, min(1, risk_value))
            
            return round(risk_value, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating risk value for {symbol}: {e}")
            return None
    
    def get_risk_band(self, risk_value: float) -> str:
        """Get risk band for a risk value"""
        if risk_value < 0.1: return '0.0-0.1'
        if risk_value < 0.2: return '0.1-0.2'
        if risk_value < 0.3: return '0.2-0.3'
        if risk_value < 0.4: return '0.3-0.4'
        if risk_value < 0.5: return '0.4-0.5'
        if risk_value < 0.6: return '0.5-0.6'
        if risk_value < 0.7: return '0.6-0.7'
        if risk_value < 0.8: return '0.7-0.8'
        if risk_value < 0.9: return '0.8-0.9'
        return '0.9-1.0'
    
    async def get_risk_bands_data(self, symbol: str) -> Dict[str, Any]:
        """Get risk bands data for a symbol"""
        try:
            # This would fetch from the database in a real implementation
            # For now, return a placeholder structure
            return {
                '0.0-0.1': {'days': 19, 'percentage': 0.35},
                '0.1-0.2': {'days': 79, 'percentage': 1.44},
                '0.2-0.3': {'days': 135, 'percentage': 2.47},
                '0.3-0.4': {'days': 369, 'percentage': 6.74},
                '0.4-0.5': {'days': 943, 'percentage': 17.23},
                '0.5-0.6': {'days': 1102, 'percentage': 20.14},
                '0.6-0.7': {'days': 1131, 'percentage': 20.67},
                '0.7-0.8': {'days': 840, 'percentage': 15.35},
                '0.8-0.9': {'days': 721, 'percentage': 13.17},
                '0.9-1.0': {'days': 134, 'percentage': 2.45}
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk bands data for {symbol}: {e}")
            return {}
    
    async def get_life_age(self, symbol: str) -> int:
        """Get life age in days for a symbol"""
        try:
            # This would fetch from the database in a real implementation
            # For now, return a placeholder value
            return 5472  # ~15 years
            
        except Exception as e:
            self.logger.error(f"Error getting life age for {symbol}: {e}")
            return 365
    
    def calculate_base_score(self, risk_value: float, risk_bands_data: Dict[str, Any]) -> float:
        """Calculate base score with rarity-based adjustments"""
        try:
            # Base score ranges as specified
            if risk_value >= 0 and risk_value <= 0.25:
                # 0-0.25: 70 to 100 points
                baseMin = 70
                baseMax = 100
            elif risk_value >= 0.25 and risk_value <= 0.40:
                # 0.25-0.40: 60 to 70 points
                baseMin = 60
                baseMax = 70
            elif risk_value >= 0.40 and risk_value <= 0.60:
                # 0.40-0.60: 40 to 60 points (neutral zone)
                baseMin = 40
                baseMax = 60
            elif risk_value >= 0.60 and risk_value <= 0.75:
                # 0.60-0.75: 60 to 70 points
                baseMin = 60
                baseMax = 70
            elif risk_value >= 0.75 and risk_value <= 1.0:
                # 0.75-1.0: 70 to 100 points
                baseMin = 70
                baseMax = 100
            else:
                return 50  # Default neutral score
            
            # Calculate base proportion within the risk band
            if risk_value >= 0 and risk_value <= 0.25:
                proportion = risk_value / 0.25
            elif risk_value >= 0.25 and risk_value <= 0.40:
                proportion = (risk_value - 0.25) / (0.40 - 0.25)
            elif risk_value >= 0.40 and risk_value <= 0.60:
                proportion = (risk_value - 0.40) / (0.60 - 0.40)
            elif risk_value >= 0.60 and risk_value <= 0.75:
                proportion = (risk_value - 0.60) / (0.75 - 0.60)
            elif risk_value >= 0.75 and risk_value <= 1.0:
                proportion = (risk_value - 0.75) / (1.0 - 0.75)
            else:
                proportion = 0.5  # Default to middle
            
            # Calculate base score
            baseScore = baseMin + (proportion * (baseMax - baseMin))
            
            # Apply rarity-based adjustments if risk bands data is available
            if risk_bands_data and len(risk_bands_data) > 0:
                currentBand = self.get_risk_band(risk_value)
                currentBandData = risk_bands_data.get(currentBand, {})
                
                if currentBandData:
                    currentDays = currentBandData.get('days', 0)
                    currentPercentage = currentBandData.get('percentage', 0)
                    
                    # Convert risk bands data to array for analysis
                    bandsArray = [
                        {'band': band, 'days': data.get('days', 0), 'percentage': data.get('percentage', 0)}
                        for band, data in risk_bands_data.items()
                        if data and data.get('days') is not None
                    ]
                    
                    bandsArray.sort(key=lambda x: x['days'])  # Sort by rarity
                    
                    if len(bandsArray) > 0:
                        # Find current band rank (1 = rarest, 10 = most common)
                        currentBandRank = next((i + 1 for i, band_info in enumerate(bandsArray) if band_info['band'] == currentBand), None)
                        
                        if currentBandRank:
                            totalBands = len(bandsArray)
                            
                            # Calculate rarity factor (0 = most common, 1 = rarest)
                            rarityFactor = 1 - (currentBandRank - 1) / (totalBands - 1) if totalBands > 1 else 0.5
                            
                            # Calculate proximity to neighboring bands
                            currentBandIndex = next((i for i, b in enumerate(bandsArray) if b['band'] == currentBand), None)
                            
                            proximityBonus = 0
                            if currentBandIndex is not None:
                                lowerNeighbor = bandsArray[currentBandIndex - 1] if currentBandIndex > 0 else None
                                upperNeighbor = bandsArray[currentBandIndex + 1] if currentBandIndex < len(bandsArray) - 1 else None
                                
                                if lowerNeighbor and upperNeighbor:
                                    # Check if current band is sandwiched between rarer bands
                                    lowerRarer = lowerNeighbor['days'] < currentDays
                                    upperRarer = upperNeighbor['days'] < currentDays
                                    
                                    if lowerRarer and upperRarer:
                                        # High opportunity: sandwiched between rarer bands
                                        proximityBonus = 15
                                    elif lowerRarer or upperRarer:
                                        # Medium opportunity: adjacent to rarer band
                                        rarerNeighbor = lowerNeighbor if lowerRarer else upperNeighbor
                                        rarityRatio = currentDays / rarerNeighbor['days']
                                        proximityBonus = min(10, rarityRatio * 5)
                            
                            # Apply rarity and proximity adjustments
                            rarityBonus = rarityFactor * 20  # 0-20 points based on rarity
                            totalBonus = rarityBonus + proximityBonus
                            
                            # Apply bonus to base score
                            baseScore = min(100, baseScore + totalBonus)
            
            return round(baseScore)
            
        except Exception as e:
            self.logger.error(f"Error calculating base score: {e}")
            return 50
    
    async def calculate_coefficient(self, symbol: str, risk_bands_data: Dict[str, Any], life_age: int) -> float:
        """Calculate coefficient using the ChatGPT system"""
        try:
            # This would call the ChatGPT coefficient calculation
            # For now, return a placeholder value
            return 1.16
            
        except Exception as e:
            self.logger.error(f"Error calculating coefficient for {symbol}: {e}")
            return 1.0
    
    async def track_symbol_score(self, symbol: str) -> bool:
        """Track daily score for a single symbol"""
        try:
            self.logger.info(f"Tracking score for {symbol}")
            
            # Get current price
            price = await self.get_current_price(symbol)
            if price is None:
                self.logger.warning(f"Could not get price for {symbol}, skipping")
                return False
            
            # Calculate risk value
            risk_value = await self.calculate_risk_value(symbol, price)
            if risk_value is None:
                self.logger.warning(f"Could not calculate risk value for {symbol}, skipping")
                return False
            
            # Get risk band
            risk_band = self.get_risk_band(risk_value)
            
            # Get risk bands data
            risk_bands_data = await self.get_risk_bands_data(symbol)
            
            # Get life age
            life_age = await self.get_life_age(symbol)
            
            # Calculate base score
            base_score = self.calculate_base_score(risk_value, risk_bands_data)
            
            # Calculate coefficient
            coefficient_value = await self.calculate_coefficient(symbol, risk_bands_data, life_age)
            
            # Calculate total score
            total_score = min(100, base_score * coefficient_value)
            
            # Record the score
            success = await self.score_tracking_service.record_daily_score(
                symbol=symbol,
                current_price=price,
                risk_value=risk_value,
                risk_band=risk_band,
                base_score=base_score,
                coefficient_value=coefficient_value,
                total_score=total_score,
                risk_bands_data=risk_bands_data,
                life_age_days=life_age
            )
            
            if success:
                self.logger.info(f"Successfully tracked score for {symbol}: Base={base_score}, Total={total_score}")
            else:
                self.logger.error(f"Failed to record score for {symbol}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error tracking score for {symbol}: {e}")
            return False
    
    async def run_daily_tracking(self):
        """Run daily score tracking for all symbols"""
        try:
            self.logger.info("Starting daily score tracking")
            
            # Initialize database connections
            from src.utils.database import init_database
            await init_database()
            self.logger.info("Database connections initialized")
            
            # Get all symbols
            symbols = await self.get_all_symbols()
            
            if not symbols:
                self.logger.error("No symbols found for tracking")
                return
            
            # Track scores for each symbol
            results = []
            for symbol in symbols:
                success = await self.track_symbol_score(symbol)
                results.append((symbol, success))
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
            
            # Log summary
            successful = sum(1 for _, success in results if success)
            failed = len(results) - successful
            
            self.logger.info(f"Daily score tracking completed: {successful} successful, {failed} failed")
            
            # Log failed symbols
            failed_symbols = [symbol for symbol, success in results if not success]
            if failed_symbols:
                self.logger.warning(f"Failed symbols: {', '.join(failed_symbols)}")
            
        except Exception as e:
            self.logger.error(f"Error in daily score tracking: {e}")

async def main():
    """Main function"""
    tracker = DailyScoreTracker()
    await tracker.run_daily_tracking()

if __name__ == "__main__":
    asyncio.run(main())
