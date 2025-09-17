#!/usr/bin/env python3
"""
Multi-Timeframe Trade Analyzer
Provides win rates and trading recommendations for 24h, 7d, and 1 month
"""

import requests
import json
from datetime import datetime
from tabulate import tabulate

class MultiTimeframeTradeAnalyzer:
    def __init__(self):
        self.riskmetric_url = "http://localhost:8556"

    def analyze_symbol(self, symbol: str):
        """Analyze a symbol with multi-timeframe win rates"""

        print(f"\n{'='*80}")
        print(f"📊 MULTI-TIMEFRAME ANALYSIS FOR {symbol}")
        print(f"{'='*80}")

        try:
            # Get enhanced risk metric data
            response = requests.get(f"{self.riskmetric_url}/api/v1/riskmetric/{symbol}")

            if response.status_code == 200:
                data = response.json()

                # Display risk overview
                print(f"\n🎯 RISK OVERVIEW")
                print(f"   Risk Level: {data['risk_level']}")
                print(f"   Risk Score: {data['risk_score']}/100")
                print(f"   Recommendation: {data['recommendation']}")

                # Prepare timeframe data for table
                timeframe_data = []

                for tf_name, tf_data in data['timeframes'].items():
                    win_rates = tf_data['win_rates']
                    timeframe_data.append([
                        tf_name.upper(),
                        f"{win_rates['long']}%",
                        f"{win_rates['short']}%",
                        tf_data['market_bias'],
                        tf_data['confidence'],
                        tf_data['recommended_position']
                    ])

                # Display win rates table
                print(f"\n📈 WIN RATE ANALYSIS")
                headers = ["Timeframe", "Long WR", "Short WR", "Market Bias", "Confidence", "Position"]
                print(tabulate(timeframe_data, headers=headers, tablefmt="grid"))

                # Trading strategy
                strategy = data['trading_strategy']
                print(f"\n💡 TRADING STRATEGY")
                print(f"   Action: {strategy['recommended_action']}")
                print(f"   Entry: {strategy['entry_strategy']}")
                print(f"   Exit: {strategy['exit_strategy']}")
                print(f"   Position Size: {strategy['position_sizing']}")
                print(f"   Stop Loss: {strategy['stop_loss']}")
                print(f"   Alignment: {strategy['timeframe_alignment']}")

                # Detailed recommendations per timeframe
                print(f"\n📋 DETAILED TIMEFRAME RECOMMENDATIONS")

                for tf_name, tf_data in data['timeframes'].items():
                    win_rates = tf_data['win_rates']
                    print(f"\n   {tf_name.upper()} Timeframe:")

                    if tf_name == "24h":
                        if tf_data['recommended_position'] == "LONG":
                            print(f"   • Quick LONG scalp opportunity")
                            print(f"   • Entry: Market or limit -0.2%")
                            print(f"   • Target: +1-2% quick profit")
                            print(f"   • Stop: -0.5% tight stop")
                        elif tf_data['recommended_position'] == "SHORT":
                            print(f"   • Quick SHORT scalp opportunity")
                            print(f"   • Entry: Market or limit +0.2%")
                            print(f"   • Target: -1-2% quick profit")
                            print(f"   • Stop: +0.5% tight stop")
                        else:
                            print(f"   • No clear direction - avoid")

                    elif tf_name == "7d":
                        if tf_data['recommended_position'] == "LONG":
                            print(f"   • Swing LONG position")
                            print(f"   • Entry: Accumulate on dips")
                            print(f"   • Target: +5-8% swing target")
                            print(f"   • Stop: -2% below support")
                        elif tf_data['recommended_position'] == "SHORT":
                            print(f"   • Swing SHORT position")
                            print(f"   • Entry: Short on rallies")
                            print(f"   • Target: -5-8% swing target")
                            print(f"   • Stop: +2% above resistance")
                        else:
                            print(f"   • Range-bound - trade the range")

                    else:  # 1month
                        if tf_data['recommended_position'] == "LONG":
                            print(f"   • Position LONG trade")
                            print(f"   • Entry: DCA over several days")
                            print(f"   • Target: +10-20% position target")
                            print(f"   • Stop: -5% major support break")
                        elif tf_data['recommended_position'] == "SHORT":
                            print(f"   • Position SHORT trade")
                            print(f"   • Entry: Scale in on strength")
                            print(f"   • Target: -10-20% position target")
                            print(f"   • Stop: +5% major resistance break")
                        else:
                            print(f"   • Accumulation phase - patient entries")

                # Best opportunity
                self.identify_best_opportunity(data['timeframes'])

                return data

            else:
                print(f"❌ Failed to get data: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def identify_best_opportunity(self, timeframes):
        """Identify the best trading opportunity across timeframes"""

        print(f"\n⭐ BEST OPPORTUNITY")

        # Find highest confidence trade
        best_tf = None
        best_score = 0

        for tf_name, tf_data in timeframes.items():
            win_rates = tf_data['win_rates']
            # Calculate opportunity score
            wr_diff = abs(win_rates['long'] - win_rates['short'])
            confidence_multiplier = {"HIGH": 1.0, "MEDIUM": 0.7, "LOW": 0.4}[tf_data['confidence']]
            score = wr_diff * confidence_multiplier

            if score > best_score and tf_data['recommended_position'] != "NEUTRAL":
                best_score = score
                best_tf = (tf_name, tf_data)

        if best_tf:
            tf_name, tf_data = best_tf
            win_rates = tf_data['win_rates']

            print(f"   Timeframe: {tf_name.upper()}")
            print(f"   Position: {tf_data['recommended_position']}")

            if tf_data['recommended_position'] == "LONG":
                print(f"   Win Rate: {win_rates['long']}% (vs {win_rates['short']}% short)")
            else:
                print(f"   Win Rate: {win_rates['short']}% (vs {win_rates['long']}% long)")

            print(f"   Confidence: {tf_data['confidence']}")
            print(f"   Score: {best_score:.2f}")

    def compare_symbols(self, symbols: list):
        """Compare multiple symbols to find best opportunity"""

        print(f"\n{'='*80}")
        print(f"📊 SYMBOL COMPARISON")
        print(f"{'='*80}")

        results = []

        for symbol in symbols:
            response = requests.get(f"{self.riskmetric_url}/api/v1/winrates/{symbol}")
            if response.status_code == 200:
                data = response.json()
                results.append(data)

        # Create comparison table
        comparison_data = []

        for result in results:
            comparison_data.append([
                result['symbol'],
                f"{result['24h']['long']}% / {result['24h']['short']}%",
                f"{result['7d']['long']}% / {result['7d']['short']}%",
                f"{result['1month']['long']}% / {result['1month']['short']}%",
                result['best_timeframe'].upper()
            ])

        headers = ["Symbol", "24h (L/S)", "7d (L/S)", "1month (L/S)", "Best TF"]
        print(tabulate(comparison_data, headers=headers, tablefmt="grid"))

def main():
    analyzer = MultiTimeframeTradeAnalyzer()

    print("🤖 Multi-Timeframe Trade Analyzer")
    print("1. Analyze single symbol")
    print("2. Compare multiple symbols")
    print("3. Quick ETHUSDT analysis")

    choice = input("\nChoice (1-3): ").strip()

    if choice == "1":
        symbol = input("Enter symbol (e.g., BTCUSDT): ").strip().upper()
        analyzer.analyze_symbol(symbol)

    elif choice == "2":
        symbols = input("Enter symbols comma-separated (e.g., BTCUSDT,ETHUSDT,SOLUSDT): ").strip().upper().split(",")
        analyzer.compare_symbols(symbols)

    elif choice == "3":
        analyzer.analyze_symbol("ETHUSDT")

    else:
        # Default to ETHUSDT
        analyzer.analyze_symbol("ETHUSDT")

if __name__ == "__main__":
    main()