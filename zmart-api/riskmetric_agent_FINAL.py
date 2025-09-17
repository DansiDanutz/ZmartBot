#!/usr/bin/env python3
"""
RISKMETRIC AGENT ENHANCED - Complete Autonomous Risk Analysis System with Target Price Feature
Handles all risk calculations, scoring, win rate analysis, and finds optimal entry points
Author: ZmartBot Team
Version: 2.0.0
"""

import asyncio
import asyncpg
import os
from typing import Dict, Tuple, Optional, List
from decimal import Decimal
import aiohttp
from datetime import datetime
import json

class RiskMetricAgentEnhanced:
    """
    Enhanced RISKMETRIC Agent that includes:
    1. All original features (price, risk, band, scoring, signals, win rate)
    2. Target price calculation for better entry points
    3. Finding nearest rare bands for optimal trading
    """

    def __init__(self, db_url: str = None):
        """Initialize the Enhanced RiskMetric Agent with database connection"""
        self.db_url = db_url or os.getenv('SUPABASE_DB_URL')
        self.conn = None

        # Binance symbol mapping
        self.binance_map = {
            'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'SOL': 'SOLUSDT',
            'BNB': 'BNBUSDT', 'XRP': 'XRPUSDT', 'ADA': 'ADAUSDT',
            'AVAX': 'AVAXUSDT', 'DOGE': 'DOGEUSDT', 'DOT': 'DOTUSDT',
            'MATIC': 'MATICUSDT', 'LINK': 'LINKUSDT', 'UNI': 'UNIUSDT',
            'ATOM': 'ATOMUSDT', 'LTC': 'LTCUSDT', 'ETC': 'ETCUSDT',
            'XLM': 'XLMUSDT', 'ALGO': 'ALGOUSDT', 'VET': 'VETUSDT',
            'AAVE': 'AAVEUSDT', 'MKR': 'MKRUSDT', 'HBAR': 'HBARUSDT',
            'XTZ': 'XTZUSDT', 'TRX': 'TRXUSDT', 'SUI': 'SUIUSDT',
            'RENDER': 'RENDERUSDT', 'TON': 'TONUSDT'
        }

    async def connect(self):
        """Establish database connection"""
        if not self.conn:
            self.conn = await asyncpg.connect(self.db_url)

    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def get_current_price(self, symbol: str) -> float:
        """Fetch current price from Binance API"""
        binance_symbol = self.binance_map.get(symbol, f"{symbol}USDT")
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={binance_symbol}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data['price'])
                else:
                    # Fallback to database price
                    return await self.get_db_price(symbol)

    async def get_db_price(self, symbol: str) -> float:
        """Get price from database as fallback"""
        query = "SELECT price_usd FROM cryptoverse_risk_data WHERE symbol = $1"
        result = await self.conn.fetchone(query, symbol)
        return float(result['price_usd']) if result else 0

    async def calculate_risk_at_price(self, symbol: str, price: float) -> float:
        """Calculate risk value from price using linear interpolation"""
        query = """
            SELECT get_risk_at_price($1, $2, 'fiat') as risk
        """
        result = await self.conn.fetchone(query, symbol, price)
        return float(result['risk'])

    async def get_price_at_risk(self, symbol: str, risk: float) -> float:
        """Get price for a specific risk value"""
        query = """
            SELECT get_price_at_risk($1, $2, 'fiat') as price
        """
        result = await self.conn.fetchone(query, symbol, risk)
        return float(result['price']) if result else 0

    async def get_risk_band(self, risk: float) -> str:
        """Determine risk band from risk value"""
        if risk >= 0.0 and risk < 0.1:
            return '0.0-0.1'
        elif risk >= 0.1 and risk < 0.2:
            return '0.1-0.2'
        elif risk >= 0.2 and risk < 0.3:
            return '0.2-0.3'
        elif risk >= 0.3 and risk < 0.4:
            return '0.3-0.4'
        elif risk >= 0.4 and risk < 0.5:
            return '0.4-0.5'
        elif risk >= 0.5 and risk < 0.6:
            return '0.5-0.6'
        elif risk >= 0.6 and risk < 0.7:
            return '0.6-0.7'
        elif risk >= 0.7 and risk < 0.8:
            return '0.7-0.8'
        elif risk >= 0.8 and risk < 0.9:
            return '0.8-0.9'
        elif risk >= 0.9 and risk <= 1.0:
            return '0.9-1.0'
        else:
            return 'UNKNOWN'

    async def get_band_data(self, symbol: str) -> Dict:
        """Get complete band data for symbol"""
        query = """
            SELECT
                total_days,
                band_0_10, band_10_20, band_20_30, band_30_40, band_40_50,
                band_50_60, band_60_70, band_70_80, band_80_90, band_90_100,
                coef_0_10, coef_10_20, coef_20_30, coef_30_40, coef_40_50,
                coef_50_60, coef_60_70, coef_70_80, coef_80_90, coef_90_100
            FROM cryptoverse_risk_time_bands_v2
            WHERE symbol = $1
        """
        result = await self.conn.fetchone(query, symbol)
        return dict(result) if result else {}

    async def calculate_btc_value(self, price_usd: float) -> float:
        """Calculate BTC value for USD price"""
        btc_price = await self.get_current_price('BTC')
        return price_usd / btc_price if btc_price > 0 else 0

    def calculate_base_score(self, risk: float) -> int:
        """Calculate base score from risk value"""
        if 0.00 <= risk <= 0.15:  # Extreme oversold
            return 100
        elif 0.85 <= risk <= 1.00:  # Extreme overbought
            return 100
        elif 0.15 < risk <= 0.25:  # Strong oversold
            return 80
        elif 0.75 <= risk < 0.85:  # Strong overbought
            return 80
        elif 0.25 < risk <= 0.35:  # Moderate oversold
            return 60
        elif 0.65 <= risk < 0.75:  # Moderate overbought
            return 60
        else:  # Neutral zone (0.35-0.65)
            return 50

    def determine_signal(self, risk: float) -> str:
        """Determine trading signal from risk"""
        if risk <= 0.35:
            return 'LONG'
        elif risk >= 0.65:
            return 'SHORT'
        else:
            return 'NEUTRAL'

    def calculate_signal_strength(self, total_score: float) -> str:
        """Determine signal strength from total score"""
        if total_score >= 150:
            return 'STRONGEST'
        elif total_score >= 120:
            return 'STRONG'
        elif total_score >= 90:
            return 'MODERATE'
        else:
            return 'WEAK'

    def calculate_win_rate(self, band_data: Dict, current_band: str, signal: str) -> float:
        """
        Calculate win rate based on days distribution
        Formula: (Most Common Days / Current Days) × 100
        """
        # Map band to days column
        band_to_column = {
            '0.0-0.1': 'band_0_10', '0.1-0.2': 'band_10_20',
            '0.2-0.3': 'band_20_30', '0.3-0.4': 'band_30_40',
            '0.4-0.5': 'band_40_50', '0.5-0.6': 'band_50_60',
            '0.6-0.7': 'band_60_70', '0.7-0.8': 'band_70_80',
            '0.8-0.9': 'band_80_90', '0.9-1.0': 'band_90_100'
        }

        current_days = band_data.get(band_to_column.get(current_band, ''), 0)
        if current_days == 0:
            return 0

        # Find most common band
        band_days = {
            '0.0-0.1': band_data.get('band_0_10', 0),
            '0.1-0.2': band_data.get('band_10_20', 0),
            '0.2-0.3': band_data.get('band_20_30', 0),
            '0.3-0.4': band_data.get('band_30_40', 0),
            '0.4-0.5': band_data.get('band_40_50', 0),
            '0.5-0.6': band_data.get('band_50_60', 0),
            '0.6-0.7': band_data.get('band_60_70', 0),
            '0.7-0.8': band_data.get('band_70_80', 0),
            '0.8-0.9': band_data.get('band_80_90', 0),
            '0.9-1.0': band_data.get('band_90_100', 0)
        }

        most_common_days = max(band_days.values())

        # Calculate win rate based on formula
        win_rate = (most_common_days / current_days) * 100

        # Cap at 95% for realistic representation
        return min(win_rate, 95.0)

    def get_coefficient(self, band_data: Dict, risk_band: str) -> float:
        """Get coefficient for specific risk band"""
        coef_map = {
            '0.0-0.1': 'coef_0_10', '0.1-0.2': 'coef_10_20',
            '0.2-0.3': 'coef_20_30', '0.3-0.4': 'coef_30_40',
            '0.4-0.5': 'coef_40_50', '0.5-0.6': 'coef_50_60',
            '0.6-0.7': 'coef_60_70', '0.7-0.8': 'coef_70_80',
            '0.8-0.9': 'coef_80_90', '0.9-1.0': 'coef_90_100'
        }

        coef_column = coef_map.get(risk_band, 'coef_50_60')
        return float(band_data.get(coef_column, 1.0))

    def get_current_band_days(self, band_data: Dict, risk_band: str) -> int:
        """Get days spent in current band"""
        band_map = {
            '0.0-0.1': 'band_0_10', '0.1-0.2': 'band_10_20',
            '0.2-0.3': 'band_20_30', '0.3-0.4': 'band_30_40',
            '0.4-0.5': 'band_40_50', '0.5-0.6': 'band_50_60',
            '0.6-0.7': 'band_60_70', '0.7-0.8': 'band_70_80',
            '0.8-0.9': 'band_80_90', '0.9-1.0': 'band_90_100'
        }

        band_column = band_map.get(risk_band, 'band_50_60')
        return int(band_data.get(band_column, 0))

    async def find_better_entry_target(self, symbol: str, current_risk: float,
                                      current_band: str, band_data: Dict,
                                      signal: str) -> Optional[Dict]:
        """
        Find the nearest rare band for better entry

        Returns:
            Dict with target_price, target_risk, target_band, target_days,
            target_coefficient, target_score
        """
        # Get all band days
        band_days = [
            ('0.0-0.1', band_data.get('band_0_10', 0), 0.05),
            ('0.1-0.2', band_data.get('band_10_20', 0), 0.15),
            ('0.2-0.3', band_data.get('band_20_30', 0), 0.25),
            ('0.3-0.4', band_data.get('band_30_40', 0), 0.35),
            ('0.4-0.5', band_data.get('band_40_50', 0), 0.45),
            ('0.5-0.6', band_data.get('band_50_60', 0), 0.55),
            ('0.6-0.7', band_data.get('band_60_70', 0), 0.65),
            ('0.7-0.8', band_data.get('band_70_80', 0), 0.75),
            ('0.8-0.9', band_data.get('band_80_90', 0), 0.85),
            ('0.9-1.0', band_data.get('band_90_100', 0), 0.95)
        ]

        current_days = self.get_current_band_days(band_data, current_band)

        # Find target based on signal
        target_band_info = None

        if signal == 'LONG':
            # For LONG, look for rare bands in oversold zone (risk < 0.35)
            oversold_bands = [(b, d, r) for b, d, r in band_days if r <= 0.35 and d < current_days and d > 0]
            if oversold_bands:
                # Get the rarest (least days) band
                target_band_info = min(oversold_bands, key=lambda x: x[1])

        elif signal == 'SHORT':
            # For SHORT, look for rare bands in overbought zone (risk > 0.65)
            overbought_bands = [(b, d, r) for b, d, r in band_days if r >= 0.65 and d < current_days and d > 0]
            if overbought_bands:
                # Get the rarest (least days) band
                target_band_info = min(overbought_bands, key=lambda x: x[1])

        else:  # NEUTRAL
            # Look for extreme zones on either side
            extreme_bands = [(b, d, r) for b, d, r in band_days
                           if (r <= 0.25 or r >= 0.75) and d < current_days and d > 0]
            if extreme_bands:
                target_band_info = min(extreme_bands, key=lambda x: x[1])

        if not target_band_info:
            return None

        target_band, target_days, target_risk = target_band_info

        # Get price at target risk
        target_price = await self.get_price_at_risk(symbol, target_risk)

        # Get coefficient for target band
        target_coefficient = self.get_coefficient(band_data, target_band)

        # Calculate score for target
        target_base_score = self.calculate_base_score(target_risk)
        target_total_score = target_base_score * target_coefficient

        return {
            'target_price': target_price,
            'target_risk': target_risk,
            'target_band': target_band,
            'target_days': target_days,
            'target_coefficient': target_coefficient,
            'target_score': target_total_score,
            'improvement': target_total_score - (self.calculate_base_score(current_risk) *
                                                self.get_coefficient(band_data, current_band))
        }

    async def analyze(self, symbol: str, price: Optional[float] = None) -> Dict:
        """
        Enhanced analysis function with target price calculation

        Args:
            symbol: Cryptocurrency symbol (e.g., 'AVAX')
            price: Optional price override, otherwise fetches current

        Returns:
            Complete analysis dictionary with all metrics including target
        """
        await self.connect()

        try:
            # 1. Get current price
            if price is None:
                price = await self.get_current_price(symbol)

            # 2. Calculate risk value
            risk = await self.calculate_risk_at_price(symbol, price)

            # 3. Get BTC value
            btc_value = await self.calculate_btc_value(price)

            # 4. Get risk band
            risk_band = await self.get_risk_band(risk)

            # 5. Get band data
            band_data = await self.get_band_data(symbol)

            # 6. Get days in current band and total life
            current_band_days = self.get_current_band_days(band_data, risk_band)
            total_days = band_data.get('total_days', 0)

            # 7. Get coefficient
            coefficient = self.get_coefficient(band_data, risk_band)

            # 8. Calculate base score
            base_score = self.calculate_base_score(risk)

            # 9. Calculate total score
            total_score = base_score * coefficient

            # 10. Determine signal
            signal = self.determine_signal(risk)

            # 11. Calculate win rate
            win_rate = self.calculate_win_rate(band_data, risk_band, signal)

            # 12. Determine signal strength
            signal_strength = self.calculate_signal_strength(total_score)

            # 13. Find better entry target (NEW!)
            target_info = await self.find_better_entry_target(
                symbol, risk, risk_band, band_data, signal
            )

            result = {
                'symbol': symbol,
                'price': price,
                'risk_value': risk,
                'btc_value': btc_value,
                'risk_band': risk_band,
                'current_band_days': current_band_days,
                'total_days': total_days,
                'base_score': base_score,
                'coefficient': coefficient,
                'total_score': total_score,
                'signal': signal,
                'signal_strength': signal_strength,
                'win_rate': win_rate
            }

            # Add target info if found
            if target_info:
                result['target'] = target_info

            return result

        finally:
            await self.close()

    def format_output(self, analysis: Dict) -> str:
        """
        Format enhanced analysis output with target price

        Template includes all original fields plus:
        The Target for a better score is: $XXX.XX (Risk: X.XX, Band: X.X-X.X,
        XX days, Coefficient: X.XX, Score: XXX)
        """

        template = f"""Risk value is: {analysis['risk_value']:.3f}

BTC value at this price IS: {analysis['btc_value']:.6f} BTC

{analysis['symbol']} is in the {analysis['risk_band']} risk band for {analysis['current_band_days']} days from his life age of {analysis['total_days']} days.

Based on all this data the base score is: {analysis['base_score']} points, and the coefficient based on our methodology is: {analysis['coefficient']:.3f}

Total score is: {analysis['total_score']:.2f} that means a {analysis['signal']} signal

Based on our history patterns we have a WIN ratio for {analysis['signal']} of: {analysis['win_rate']:.1f}%"""

        # Add target information if available
        if 'target' in analysis and analysis['target']:
            target = analysis['target']
            template += f"""

The Target for a better score is: ${target['target_price']:.2f} (Risk: {target['target_risk']:.2f}, Band: {target['target_band']}, {target['target_days']} days, Coefficient: {target['target_coefficient']:.2f}, Score: {target['target_score']:.0f})"""

            # Add improvement note
            if target['improvement'] > 0:
                template += f"\nThis would improve your score by {target['improvement']:.1f} points!"

        return template


async def main():
    """Example usage of the Enhanced RiskMetric Agent"""

    # Initialize enhanced agent
    agent = RiskMetricAgentEnhanced()

    # Analyze AVAX at specific price
    print("=" * 60)
    print("ENHANCED RISKMETRIC AGENT - ANALYSIS WITH TARGET PRICE")
    print("=" * 60)
    print()

    # Get analysis
    analysis = await agent.analyze('AVAX', price=30.47)

    # Format and print output
    output = agent.format_output(analysis)
    print(output)

    print()
    print("=" * 60)

    # Additional details
    print("\nAdditional Analysis Details:")
    print(f"Signal Strength: {analysis['signal_strength']}")
    print(f"Current Price: ${analysis['price']:.2f}")

    # Enhanced action recommendation with target
    if 'target' in analysis and analysis['target']:
        target = analysis['target']
        if analysis['signal'] == 'LONG':
            action = f"🎯 WAIT FOR TARGET: ${target['target_price']:.2f} for better LONG entry (Score: {target['target_score']:.0f})"
        elif analysis['signal'] == 'SHORT':
            action = f"🎯 WAIT FOR TARGET: ${target['target_price']:.2f} for better SHORT entry (Score: {target['target_score']:.0f})"
        else:
            action = f"⏸️ MONITOR - Target: ${target['target_price']:.2f} for opportunity"
    else:
        if analysis['signal'] == 'LONG' and analysis['signal_strength'] in ['STRONGEST', 'STRONG']:
            action = "🔥 STRONG BUY - Already at optimal entry"
        elif analysis['signal'] == 'SHORT' and analysis['signal_strength'] in ['STRONGEST', 'STRONG']:
            action = "⚠️ STRONG SELL - Already at optimal exit"
        elif analysis['signal'] == 'NEUTRAL':
            action = "⏸️ HOLD - Wait for extreme zones"
        else:
            action = "👀 MONITOR - Weak signal"

    print(f"Recommended Action: {action}")

    # Show target analysis if available
    if 'target' in analysis and analysis['target']:
        print("\n📊 Target Analysis:")
        target = analysis['target']
        print(f"  • Target Price: ${target['target_price']:.2f}")
        print(f"  • Target Risk: {target['target_risk']:.3f}")
        print(f"  • Target Band: {target['target_band']} ({target['target_days']} days)")
        print(f"  • Target Coefficient: {target['target_coefficient']:.2f}")
        print(f"  • Expected Score: {target['target_score']:.0f}")
        print(f"  • Score Improvement: +{target['improvement']:.1f} points")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())