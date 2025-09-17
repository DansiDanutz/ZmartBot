#!/usr/bin/env python3
"""
Strategy-Based Trade Analyzer
Displays win rates using our actual trading strategies
"""

import requests
import json
from datetime import datetime
from tabulate import tabulate

class StrategyTradeAnalyzer:
    def __init__(self):
        self.riskmetric_url = "http://localhost:8556"
        self.trading_agent_url = "http://localhost:8200"  # Trading Orchestration Agent

    def analyze_symbol(self, symbol: str):
        """Analyze a symbol using our trading strategies"""

        print(f"\n{'='*80}")
        print(f"📊 STRATEGY-BASED ANALYSIS FOR {symbol}")
        print(f"{'='*80}")

        try:
            # Get strategy-based risk metric data
            response = requests.get(f"{self.riskmetric_url}/api/v1/riskmetric/{symbol}")

            if response.status_code == 200:
                data = response.json()

                # Display risk overview
                print(f"\n🎯 RISK ANALYSIS")
                print(f"   Risk Level: {data['risk_level']}")
                print(f"   Risk Score: {data['risk_score']}/100")
                print(f"   Recommendation: {data['recommendation']}")

                # Prepare strategy data for table
                strategy_data = []

                for strat_key, strat_data in data['strategies'].items():
                    win_rates = strat_data['win_rates']
                    strategy_data.append([
                        strat_data['name'],
                        strat_data['duration'],
                        f"{win_rates['long']}%",
                        f"{win_rates['short']}%",
                        strat_data['market_bias'],
                        strat_data['confidence'],
                        strat_data['recommended_position']
                    ])

                # Display win rates table
                print(f"\n📈 TRADING STRATEGY WIN RATES")
                headers = ["Strategy", "Duration", "Long WR", "Short WR", "Bias", "Confidence", "Position"]
                print(tabulate(strategy_data, headers=headers, tablefmt="grid"))

                # Trading plan
                plan = data['trading_plan']
                print(f"\n💡 TRADING PLAN")
                print(f"   Action: {plan['primary_action']}")
                print(f"   Best Strategy: {plan['best_strategy'].upper()}")
                print(f"   Position Size: {plan['position_sizing']}")
                print(f"   Risk per Trade: {plan['risk_per_trade']}")
                print(f"   Max Leverage: {plan['max_leverage']}")
                print(f"   Strategy Alignment: {plan['strategy_alignment']}")
                print(f"   Execution: {plan['execution_plan']}")

                # Detailed strategy recommendations
                print(f"\n📋 STRATEGY-SPECIFIC EXECUTION")

                for strat_key, strat_data in data['strategies'].items():
                    print(f"\n   {strat_data['name']} ({strat_data['duration']}):")
                    print(f"   • Position: {strat_data['recommended_position']}")
                    print(f"   • Entry: {strat_data['entry']}")
                    print(f"   • Exit: {strat_data['exit']}")
                    print(f"   • Win Rate: Long {strat_data['win_rates']['long']}% vs Short {strat_data['win_rates']['short']}%")

                # Best opportunity
                self.identify_best_opportunity(data['strategies'])

                # Trading Agent integration check
                self.check_trading_agent_status()

                return data

            else:
                print(f"❌ Failed to get data: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def identify_best_opportunity(self, strategies):
        """Identify the best trading opportunity across strategies"""

        print(f"\n⭐ BEST OPPORTUNITY")

        # Find highest confidence trade
        best_strat = None
        best_score = 0

        for strat_key, strat_data in strategies.items():
            win_rates = strat_data['win_rates']
            # Calculate opportunity score
            wr_diff = abs(win_rates['long'] - win_rates['short'])
            confidence_multiplier = {"HIGH": 1.0, "MEDIUM": 0.7, "LOW": 0.4}[strat_data['confidence']]

            # Weight by strategy type (scalp = quick profit, swing = larger profit)
            strategy_weight = {"Scalp Strategy": 0.8, "Intraday Strategy": 1.0, "Swing Strategy": 1.2}
            weight = strategy_weight.get(strat_data['name'], 1.0)

            score = wr_diff * confidence_multiplier * weight

            if score > best_score and strat_data['recommended_position'] != "NEUTRAL":
                best_score = score
                best_strat = (strat_key, strat_data)

        if best_strat:
            strat_key, strat_data = best_strat
            win_rates = strat_data['win_rates']

            print(f"   Strategy: {strat_data['name']}")
            print(f"   Duration: {strat_data['duration']}")
            print(f"   Position: {strat_data['recommended_position']}")

            if strat_data['recommended_position'] == "LONG":
                print(f"   Win Rate: {win_rates['long']}% (vs {win_rates['short']}% short)")
            else:
                print(f"   Win Rate: {win_rates['short']}% (vs {win_rates['long']}% long)")

            print(f"   Target: {strat_data['target']}")
            print(f"   Stop Loss: {strat_data['stop_loss']}")
            print(f"   Confidence: {strat_data['confidence']}")
            print(f"   Score: {best_score:.2f}")

    def check_trading_agent_status(self):
        """Check if Trading Orchestration Agent is available"""
        print(f"\n🤖 TRADING AGENT STATUS")
        try:
            response = requests.get(f"{self.trading_agent_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"   ✅ Trading Orchestration Agent: ONLINE (port 8200)")
            else:
                print(f"   ⚠️ Trading Orchestration Agent: OFFLINE")
        except:
            print(f"   ❌ Trading Orchestration Agent: NOT RESPONDING")

    def compare_symbols(self, symbols: list):
        """Compare multiple symbols to find best opportunity"""

        print(f"\n{'='*80}")
        print(f"📊 SYMBOL COMPARISON - STRATEGY BASED")
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
                f"{result['scalp']['long']}% / {result['scalp']['short']}%",
                f"{result['intraday']['long']}% / {result['intraday']['short']}%",
                f"{result['swing']['long']}% / {result['swing']['short']}%",
                result['best_strategy'].upper()
            ])

        headers = ["Symbol", "Scalp (L/S)", "Intraday (L/S)", "Swing (L/S)", "Best Strategy"]
        print(tabulate(comparison_data, headers=headers, tablefmt="grid"))

def main():
    analyzer = StrategyTradeAnalyzer()

    print("🤖 Strategy-Based Trade Analyzer")
    print("Using our actual trading strategies:")
    print("• Scalp: 5-15 minutes, 0.5-1% target")
    print("• Intraday: 1-4 hours, 2-3% target")
    print("• Swing: 2-5 days, 5-10% target")
    print("\n1. Analyze single symbol")
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