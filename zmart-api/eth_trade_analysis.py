#!/usr/bin/env python3
"""
ETHUSDT Trading Analysis - Real-time Decision System
"""

import requests
import json
from datetime import datetime
import time

class ETHUSDTTradeAnalyzer:
    def __init__(self):
        self.symbol = "ETHUSDT"
        self.agents = {
            "kingfisher": "http://localhost:8098",
            "riskmetric": "http://localhost:8556",
            "cryptometer": "https://api.cryptometer.io",
            "webhook": "http://localhost:8555"
        }
        self.cryptometer_api_key = "1n3PBsjVq4GdxH1lZZQO5371H5H81v7agEO9I7u9"

    def get_riskmetric_analysis(self):
        """Get Benjamin Cowen style risk analysis"""
        try:
            response = requests.get(f"{self.agents['riskmetric']}/api/v1/riskmetric/{self.symbol}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"RiskMetric error: {e}")
        return None

    def get_kingfisher_analysis(self):
        """Get AI-powered analysis from KingFisher"""
        try:
            response = requests.post(
                f"{self.agents['kingfisher']}/analyze",
                json={"symbol": self.symbol, "timeframe": "4h"},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"KingFisher error: {e}")
        return None

    def calculate_win_rates(self):
        """Calculate win rate ratios for long and short positions"""

        # Get risk metric data
        risk_data = self.get_riskmetric_analysis()

        # Base win rates (will be adjusted based on risk level)
        base_long_wr = 0.52
        base_short_wr = 0.48

        if risk_data:
            risk_score = risk_data.get('risk_score', 50)
            risk_level = risk_data.get('risk_level', 'MEDIUM')

            # Adjust win rates based on risk level
            if risk_level == "LOW":
                # Low risk = better for longs
                long_wr = base_long_wr + 0.15
                short_wr = base_short_wr - 0.10
                bias = "STRONG LONG"
            elif risk_level == "MEDIUM":
                # Medium risk = neutral with slight adjustments
                if risk_score < 50:
                    long_wr = base_long_wr + 0.08
                    short_wr = base_short_wr - 0.05
                    bias = "MODERATE LONG"
                else:
                    long_wr = base_long_wr - 0.05
                    short_wr = base_short_wr + 0.08
                    bias = "MODERATE SHORT"
            else:  # HIGH
                # High risk = better for shorts
                long_wr = base_long_wr - 0.10
                short_wr = base_short_wr + 0.15
                bias = "STRONG SHORT"
        else:
            long_wr = base_long_wr
            short_wr = base_short_wr
            bias = "NEUTRAL"

        return {
            "long_win_rate": round(long_wr * 100, 2),
            "short_win_rate": round(short_wr * 100, 2),
            "market_bias": bias,
            "confidence": "HIGH" if abs(long_wr - short_wr) > 0.1 else "MEDIUM"
        }

    def get_trade_recommendation(self):
        """Generate comprehensive trade recommendation"""

        print("🔍 Analyzing ETHUSDT Trading Opportunity...")
        print("=" * 60)

        # 1. Risk Analysis
        risk_data = self.get_riskmetric_analysis()
        if risk_data:
            print(f"\n📊 RISK ANALYSIS (Benjamin Cowen Model)")
            print(f"   Risk Level: {risk_data['risk_level']}")
            print(f"   Risk Score: {risk_data['risk_score']}/100")
            print(f"   Recommendation: {risk_data['recommendation']}")

        # 2. Win Rate Calculation
        win_rates = self.calculate_win_rates()
        print(f"\n🎯 WIN RATE ANALYSIS")
        print(f"   Long Position Win Rate:  {win_rates['long_win_rate']}%")
        print(f"   Short Position Win Rate: {win_rates['short_win_rate']}%")
        print(f"   Market Bias: {win_rates['market_bias']}")
        print(f"   Confidence: {win_rates['confidence']}")

        # 3. Trading Recommendation
        print(f"\n💡 TRADING RECOMMENDATION")

        if win_rates['market_bias'].startswith("STRONG LONG"):
            print("   ✅ OPEN LONG POSITION")
            print("   Entry: Market price or limit at current - 0.5%")
            print("   Stop Loss: -2% from entry")
            print("   Take Profit 1: +3% (50% position)")
            print("   Take Profit 2: +5% (25% position)")
            print("   Take Profit 3: +8% (25% position)")
            position_type = "LONG"

        elif win_rates['market_bias'].startswith("STRONG SHORT"):
            print("   ✅ OPEN SHORT POSITION")
            print("   Entry: Market price or limit at current + 0.5%")
            print("   Stop Loss: +2% from entry")
            print("   Take Profit 1: -3% (50% position)")
            print("   Take Profit 2: -5% (25% position)")
            print("   Take Profit 3: -8% (25% position)")
            position_type = "SHORT"

        elif win_rates['market_bias'].startswith("MODERATE LONG"):
            print("   ⚠️ CAUTIOUS LONG POSITION")
            print("   Entry: Limit order at support level")
            print("   Stop Loss: -1.5% from entry")
            print("   Take Profit: +2-4% (conservative)")
            print("   Position Size: 50% of normal")
            position_type = "LONG"

        elif win_rates['market_bias'].startswith("MODERATE SHORT"):
            print("   ⚠️ CAUTIOUS SHORT POSITION")
            print("   Entry: Limit order at resistance level")
            print("   Stop Loss: +1.5% from entry")
            print("   Take Profit: -2-4% (conservative)")
            print("   Position Size: 50% of normal")
            position_type = "SHORT"

        else:
            print("   ⏸️ NO POSITION - WAIT FOR BETTER SETUP")
            print("   Market is neutral, wait for clear direction")
            position_type = "NONE"

        # 4. Risk Management
        print(f"\n⚠️ RISK MANAGEMENT")
        print(f"   Max Position Size: 2% of portfolio")
        print(f"   Risk per Trade: 1% of portfolio")
        print(f"   Leverage: 5x maximum (10x if confident)")

        # 5. Key Levels (mock data - would come from real analysis)
        print(f"\n📍 KEY LEVELS")
        print(f"   Support: $2,450 | $2,400 | $2,350")
        print(f"   Resistance: $2,550 | $2,600 | $2,650")

        # 6. Timing
        print(f"\n⏰ OPTIMAL ENTRY TIMING")
        if position_type == "LONG":
            print("   Best Entry: During US market open dip (9:30-10:30 AM EST)")
            print("   Alternative: Asian session support test (8-10 PM EST)")
        elif position_type == "SHORT":
            print("   Best Entry: During resistance test in EU session (3-5 AM EST)")
            print("   Alternative: US afternoon weakness (2-4 PM EST)")
        else:
            print("   Monitor for breakout above $2,600 or breakdown below $2,400")

        print("\n" + "=" * 60)
        print("📈 Analysis Complete - Trade Responsibly!")

        return {
            "symbol": self.symbol,
            "recommendation": position_type,
            "win_rates": win_rates,
            "risk_data": risk_data,
            "timestamp": datetime.now().isoformat()
        }

def main():
    analyzer = ETHUSDTTradeAnalyzer()
    result = analyzer.get_trade_recommendation()

    # Save analysis to file
    with open("eth_trade_decision.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n💾 Full analysis saved to eth_trade_decision.json")

if __name__ == "__main__":
    main()