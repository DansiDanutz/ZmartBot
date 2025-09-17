#!/usr/bin/env python3
"""
RISKMETRIC AGENT V2 - With Target Price Calculation
Enhanced version that finds optimal entry points
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

class RiskMetricAgentV2:
    """
    Enhanced RISKMETRIC Agent with target price calculation
    Finds the nearest rare band for better entry points
    """

    def __init__(self, db_url: str = None):
        """Initialize the RiskMetric Agent V2"""
        self.db_url = db_url or os.getenv('SUPABASE_DB_URL')
        self.conn = None

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
                    return await self.get_db_price(symbol)

    async def get_db_price(self, symbol: str) -> float:
        """Get price from database as fallback"""
        query = "SELECT price_usd FROM cryptoverse_risk_data WHERE symbol = $1"
        result = await self.conn.fetchone(query, symbol)
        return float(result['price_usd']) if result else 0

    async def calculate_risk_at_price(self, symbol: str, price: float) -> float:
        """Calculate risk value from price"""
        query = "SELECT get_risk_at_price($1, $2, 'fiat') as risk"
        result = await self.conn.fetchone(query, symbol, price)
        return float(result['risk'])

    async def get_price_at_risk(self, symbol: str, risk: float) -> float:
        """Calculate price from risk value"""
        query = "SELECT get_price_at_risk($1, $2, 'fiat') as price"
        result = await self.conn.fetchone(query, symbol, risk)
        return float(result['price'])

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
        else:  # Neutral zone
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
        """Calculate win rate based on days distribution"""
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

        if signal == 'LONG' and float(current_band.split('-')[0]) <= 0.3:
            target_days = band_days['0.4-0.5'] + band_days['0.5-0.6']
            win_rate = (target_days / current_days) * 100
        elif signal == 'SHORT' and float(current_band.split('-')[1]) >= 0.7:
            target_days = band_days['0.4-0.5'] + band_days['0.5-0.6']
            win_rate = (target_days / current_days) * 100
        else:
            win_rate = (most_common_days / current_days) * 100

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
                                       current_band: str, band_data: Dict) -> Optional[Dict]:
        """
        Find the nearest rare band for better entry
        Returns target price and details
        """
        current_days = self.get_current_band_days(band_data, current_band)

        # Band configurations with risk centers
        band_configs = {
            '0.0-0.1': {'center': 0.05, 'days_key': 'band_0_10', 'coef_key': 'coef_0_10', 'score': 100},
            '0.1-0.2': {'center': 0.15, 'days_key': 'band_10_20', 'coef_key': 'coef_10_20', 'score': 100},
            '0.2-0.3': {'center': 0.25, 'days_key': 'band_20_30', 'coef_key': 'coef_20_30', 'score': 80},
            '0.3-0.4': {'center': 0.35, 'days_key': 'band_30_40', 'coef_key': 'coef_30_40', 'score': 60},
            '0.7-0.8': {'center': 0.75, 'days_key': 'band_70_80', 'coef_key': 'coef_70_80', 'score': 80},
            '0.8-0.9': {'center': 0.85, 'days_key': 'band_80_90', 'coef_key': 'coef_80_90', 'score': 100},
            '0.9-1.0': {'center': 0.95, 'days_key': 'band_90_100', 'coef_key': 'coef_90_100', 'score': 100}
        }

        best_target = None
        best_score = 0

        # Look for LONG targets if not in oversold
        if current_risk > 0.35:
            for band in ['0.2-0.3', '0.1-0.2', '0.0-0.1']:
                config = band_configs[band]
                days = band_data.get(config['days_key'], 0)

                if days > 0 and days < current_days:
                    coef = band_data.get(config['coef_key'], 1.0)
                    total_score = config['score'] * coef

                    if total_score > best_score:
                        target_price = await self.get_price_at_risk(symbol, config['center'])
                        best_target = {
                            'band': band,
                            'risk': config['center'],
                            'price': target_price,
                            'days': days,
                            'coefficient': coef,
                            'base_score': config['score'],
                            'total_score': total_score,
                            'type': 'LONG'
                        }
                        best_score = total_score

        # Look for SHORT targets if not in overbought
        elif current_risk < 0.65:
            for band in ['0.7-0.8', '0.8-0.9', '0.9-1.0']:
                config = band_configs[band]
                days = band_data.get(config['days_key'], 0)

                if days > 0 and days < current_days:
                    coef = band_data.get(config['coef_key'], 1.0)
                    total_score = config['score'] * coef

                    if total_score > best_score:
                        target_price = await self.get_price_at_risk(symbol, config['center'])
                        best_target = {
                            'band': band,
                            'risk': config['center'],
                            'price': target_price,
                            'days': days,
                            'coefficient': coef,
                            'base_score': config['score'],
                            'total_score': total_score,
                            'type': 'SHORT'
                        }
                        best_score = total_score

        return best_target

    async def analyze_v2(self, symbol: str, price: Optional[float] = None) -> Dict:
        """
        Enhanced analysis with target price calculation

        Returns complete analysis including optimal entry targets
        """
        await self.connect()

        try:
            # Get basic analysis
            if price is None:
                price = await self.get_current_price(symbol)

            risk = await self.calculate_risk_at_price(symbol, price)
            btc_value = await self.calculate_btc_value(price)
            risk_band = await self.get_risk_band(risk)
            band_data = await self.get_band_data(symbol)

            current_band_days = self.get_current_band_days(band_data, risk_band)
            total_days = band_data.get('total_days', 0)
            coefficient = self.get_coefficient(band_data, risk_band)
            base_score = self.calculate_base_score(risk)
            total_score = base_score * coefficient
            signal = self.determine_signal(risk)
            win_rate = self.calculate_win_rate(band_data, risk_band, signal)
            signal_strength = self.calculate_signal_strength(total_score)

            # Find better entry target
            target = await self.find_better_entry_target(symbol, risk, risk_band, band_data)

            return {
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
                'win_rate': win_rate,
                'target': target
            }

        finally:
            await self.close()

    def format_output_v2(self, analysis: Dict) -> str:
        """
        Format analysis output with target price information
        """
        # Basic template
        template = f"""Risk value is: {analysis['risk_value']:.3f}

BTC value at this price IS: {analysis['btc_value']:.6f} BTC

{analysis['symbol']} is in the {analysis['risk_band']} risk band for {analysis['current_band_days']} days from his life age of {analysis['total_days']} days.

Based on all this data the base score is: {analysis['base_score']} points, and the coefficient based on our methodology is: {analysis['coefficient']:.3f}

Total score is: {analysis['total_score']:.2f} that means a {analysis['signal']} signal

Based on our history patterns we have a WIN ratio for {analysis['signal']} of: {analysis['win_rate']:.1f}%"""

        # Add target information
        if analysis.get('target'):
            target = analysis['target']
            template += f"""

The Target for a better score is: ${target['price']:.2f} (Risk: {target['risk']:.2f}, Band: {target['band']}, {target['days']} days, Coefficient: {target['coefficient']:.2f}, Score: {target['total_score']:.0f})"""
        else:
            if analysis['signal_strength'] in ['STRONGEST', 'STRONG']:
                template += "\n\nThe Target for a better score is: Already in optimal position!"
            else:
                template += "\n\nThe Target for a better score is: Wait for extreme zones"

        return template


async def main():
    """Example usage of RiskMetric Agent V2"""

    # Initialize agent
    agent = RiskMetricAgentV2()

    # Analyze AVAX
    print("=" * 60)
    print("RISKMETRIC AGENT V2 - WITH TARGET PRICES")
    print("=" * 60)
    print()

    # Get analysis
    analysis = await agent.analyze_v2('AVAX', price=30.47)

    # Format and print output
    output = agent.format_output_v2(analysis)
    print(output)

    print()
    print("=" * 60)

    # Show target details if available
    if analysis.get('target'):
        target = analysis['target']
        print("\n📎 Target Details:")
        print(f"  Type: {target['type']}")
        print(f"  Target Band: {target['band']}")
        print(f"  Target Price: ${target['price']:.2f}")
        print(f"  Days in Target: {target['days']}")
        print(f"  Target Score: {target['total_score']:.0f}")
        print(f"  Price Movement Needed: {((target['price'] - analysis['price']) / analysis['price'] * 100):.1f}%")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())