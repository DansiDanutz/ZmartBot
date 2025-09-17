#!/usr/bin/env python3
"""
Real-time Risk Metric Calculation using Binance API
Fetches current market prices and calculates risk values for each symbol
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

class BinanceRiskCalculator:
    """Calculate real-time risk metrics using Binance prices"""

    def __init__(self):
        self.binance_base_url = "https://api.binance.com"
        self.symbol_mapping = {
            'BTC': 'BTCUSDT',
            'ETH': 'ETHUSDT',
            'BNB': 'BNBUSDT',
            'SOL': 'SOLUSDT',
            'XRP': 'XRPUSDT',
            'ADA': 'ADAUSDT',
            'AVAX': 'AVAXUSDT',
            'DOGE': 'DOGEUSDT',
            'DOT': 'DOTUSDT',
            'LINK': 'LINKUSDT',
            'LTC': 'LTCUSDT',
            'ATOM': 'ATOMUSDT',
            'XTZ': 'XTZUSDT',
            'AAVE': 'AAVEUSDT',
            'MKR': 'MKRUSDT',
            'XMR': 'XMRUSDT',
            'XLM': 'XLMUSDT',
            'SUI': 'SUIUSDT',
            'HBAR': 'HBARUSDT',
            'RENDER': 'RENDERUSDT',
            'TRX': 'TRXUSDT',
            'VET': 'VETUSDT',
            'ALGO': 'ALGOUSDT',
            'SHIB': 'SHIBUSDT',
            'TON': 'TONUSDT'
        }

        # Initialize Supabase if credentials available
        self.supabase = None
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("✅ Connected to Supabase")
            except Exception as e:
                print(f"⚠️ Supabase connection failed: {e}")

    def get_binance_price(self, symbol: str) -> Optional[float]:
        """
        Get current price from Binance API
        """
        binance_symbol = self.symbol_mapping.get(symbol)
        if not binance_symbol:
            print(f"❌ Symbol {symbol} not mapped to Binance")
            return None

        try:
            url = f"{self.binance_base_url}/api/v3/ticker/price"
            params = {'symbol': binance_symbol}
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                return price
            else:
                print(f"❌ Binance API error for {symbol}: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error fetching {symbol} price: {e}")
            return None

    def get_all_binance_prices(self) -> Dict[str, float]:
        """
        Get all prices in a single API call (more efficient)
        """
        try:
            url = f"{self.binance_base_url}/api/v3/ticker/price"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                all_prices = response.json()

                # Create a lookup dictionary
                price_dict = {item['symbol']: float(item['price']) for item in all_prices}

                # Map to our symbols
                result = {}
                for symbol, binance_symbol in self.symbol_mapping.items():
                    if binance_symbol in price_dict:
                        result[symbol] = price_dict[binance_symbol]

                return result
            else:
                print(f"❌ Binance API error: {response.status_code}")
                return {}

        except Exception as e:
            print(f"❌ Error fetching all prices: {e}")
            return {}

    def calculate_risk_from_price(self, symbol: str, current_price: float) -> Optional[Dict]:
        """
        Calculate risk metric based on current price using Supabase function
        """
        if not self.supabase:
            print("⚠️ Supabase not connected")
            return None

        try:
            # Call Supabase function to get risk at price
            response = self.supabase.rpc('get_risk_at_price', {
                'p_symbol': symbol,
                'p_price': current_price,
                'p_type': 'fiat'
            }).execute()

            if response.data is not None:
                risk_value = response.data

                # Determine risk band
                risk_band = self.get_risk_band(risk_value)

                # Get coefficient for this band
                coef_response = self.supabase.table('cryptoverse_risk_time_bands_v2')\
                    .select('*')\
                    .eq('symbol', symbol)\
                    .single()\
                    .execute()

                coefficient = 1.0
                if coef_response.data:
                    coef_column = f"coef_{risk_band.replace('.', '').replace('-', '_')}"
                    coefficient = coef_response.data.get(coef_column, 1.0)

                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'risk_value': risk_value,
                    'risk_band': risk_band,
                    'coefficient': coefficient,
                    'adjusted_risk': risk_value * coefficient,
                    'trading_signal': self.get_trading_signal(risk_value, coefficient)
                }

        except Exception as e:
            print(f"❌ Error calculating risk for {symbol}: {e}")
            return None

    def get_risk_band(self, risk_value: float) -> str:
        """Convert risk value to band"""
        if risk_value < 0.1: return '0.0-0.1'
        elif risk_value < 0.2: return '0.1-0.2'
        elif risk_value < 0.3: return '0.2-0.3'
        elif risk_value < 0.4: return '0.3-0.4'
        elif risk_value < 0.5: return '0.4-0.5'
        elif risk_value < 0.6: return '0.5-0.6'
        elif risk_value < 0.7: return '0.6-0.7'
        elif risk_value < 0.8: return '0.7-0.8'
        elif risk_value < 0.9: return '0.8-0.9'
        else: return '0.9-1.0'

    def get_trading_signal(self, risk: float, coefficient: float) -> str:
        """Generate trading signal based on risk and coefficient"""
        if coefficient >= 1.5:  # Very rare band
            if risk < 0.2:
                return "🔥🔥 STRONG BUY - Extremely rare low risk"
            elif risk > 0.8:
                return "⚠️⚠️ STRONG SELL - Extremely rare high risk"
            else:
                return "👀 WATCH - Rare zone, high volatility expected"
        elif coefficient >= 1.3:  # Rare band
            if risk < 0.3:
                return "✅ BUY - Rare accumulation zone"
            elif risk > 0.7:
                return "📉 SELL - Rare distribution zone"
            else:
                return "🔍 MONITOR - Uncommon zone"
        else:  # Common band
            if risk < 0.3:
                return "💰 ACCUMULATE - Common accumulation"
            elif risk > 0.7:
                return "💸 TAKE PROFIT - Common distribution"
            else:
                return "⏸️ HOLD - Normal zone"

    def update_supabase_risk_data(self, risk_data: Dict) -> bool:
        """Update Supabase with current risk data"""
        if not self.supabase:
            return False

        try:
            # Update cryptoverse_risk_data table
            response = self.supabase.table('cryptoverse_risk_data')\
                .upsert({
                    'symbol': risk_data['symbol'],
                    'price_usd': risk_data['current_price'],
                    'fiat_risk': risk_data['risk_value'],
                    'last_updated': datetime.now().isoformat()
                })\
                .execute()

            return True
        except Exception as e:
            print(f"❌ Error updating Supabase: {e}")
            return False

    def run_full_update(self) -> List[Dict]:
        """
        Run complete update for all symbols
        """
        print("🔄 Fetching real-time prices from Binance...")
        all_prices = self.get_all_binance_prices()

        if not all_prices:
            print("❌ Failed to fetch prices")
            return []

        results = []
        print(f"\n✅ Got prices for {len(all_prices)} symbols\n")
        print("=" * 70)
        print(f"{'Symbol':<8} {'Price $':<12} {'Risk':<8} {'Band':<10} {'Coef':<8} {'Signal':<30}")
        print("=" * 70)

        for symbol, price in all_prices.items():
            risk_data = self.calculate_risk_from_price(symbol, price)

            if risk_data:
                # Update database
                self.update_supabase_risk_data(risk_data)

                # Display result
                print(f"{risk_data['symbol']:<8} "
                      f"${risk_data['current_price']:<11,.2f} "
                      f"{risk_data['risk_value']:<8.3f} "
                      f"{risk_data['risk_band']:<10} "
                      f"{risk_data['coefficient']:<8.3f} "
                      f"{risk_data['trading_signal']:<30}")

                results.append(risk_data)

        print("=" * 70)
        print(f"\n✅ Updated {len(results)} symbols with real-time risk metrics")

        # Find best opportunities
        self.display_top_opportunities(results)

        return results

    def display_top_opportunities(self, results: List[Dict]):
        """Display top trading opportunities"""
        print("\n" + "=" * 70)
        print("🎯 TOP TRADING OPPORTUNITIES")
        print("=" * 70)

        # Sort by adjusted risk score
        buy_opportunities = [r for r in results if r['risk_value'] < 0.3]
        sell_opportunities = [r for r in results if r['risk_value'] > 0.7]

        if buy_opportunities:
            print("\n💰 BUY OPPORTUNITIES (Low Risk + High Coefficient):")
            buy_opportunities.sort(key=lambda x: x['coefficient'], reverse=True)
            for opp in buy_opportunities[:5]:
                print(f"  {opp['symbol']}: Risk={opp['risk_value']:.3f}, "
                      f"Coef={opp['coefficient']:.3f} → {opp['trading_signal']}")

        if sell_opportunities:
            print("\n💸 SELL OPPORTUNITIES (High Risk + High Coefficient):")
            sell_opportunities.sort(key=lambda x: x['coefficient'], reverse=True)
            for opp in sell_opportunities[:5]:
                print(f"  {opp['symbol']}: Risk={opp['risk_value']:.3f}, "
                      f"Coef={opp['coefficient']:.3f} → {opp['trading_signal']}")

def main():
    """Main function"""
    calculator = BinanceRiskCalculator()

    # Option 1: Get single symbol
    print("\n📊 SINGLE SYMBOL TEST - SOL")
    print("-" * 40)
    sol_price = calculator.get_binance_price('SOL')
    if sol_price:
        print(f"SOL Current Price: ${sol_price:.2f}")
        sol_risk = calculator.calculate_risk_from_price('SOL', sol_price)
        if sol_risk:
            print(f"SOL Risk: {sol_risk['risk_value']:.3f}")
            print(f"SOL Band: {sol_risk['risk_band']}")
            print(f"SOL Signal: {sol_risk['trading_signal']}")

    # Option 2: Update all symbols
    print("\n" + "=" * 70)
    print("📊 FULL SYSTEM UPDATE")
    print("=" * 70)
    calculator.run_full_update()

if __name__ == "__main__":
    main()