#!/usr/bin/env python3
"""
CORRECT Trading Strategy Implementation
Position Sizing: 2% → 4% → 8% → 16% → Add Margin up to 50%
Leverage Options: 20X, 10X, 5X, 2X
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List

sys.path.append('/Users/dansidanutz/Desktop/ZmartBot/zmart-api')
sys.path.append('/Users/dansidanutz/Desktop/ZmartBot/zmart-api/src')

from src.services.unified_riskmetric import UnifiedRiskMetric
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class CorrectTradingStrategy:
    """
    The ACTUAL ZmartBot Trading Strategy
    Position Scaling: 2% → 4% → 8% → 16% → Add Margin
    Leverage: 20X, 10X, 5X, 2X (NO 7X!)
    """

    def __init__(self):
        # CORRECT Position Sizing Strategy
        self.position_scaling = {
            'entry_1': 0.02,    # 2% - First entry
            'entry_2': 0.04,    # 4% - Double up
            'entry_3': 0.08,    # 8% - Double up
            'entry_4': 0.16,    # 16% - Double up
            'margin_add': 0.50  # Up to 50% with margin
        }

        # CORRECT Leverage Options
        self.leverage_options = {
            'ultra_high': 20,   # 20X - Maximum leverage
            'high': 10,         # 10X - High leverage
            'medium': 5,        # 5X - Medium leverage
            'low': 2            # 2X - Conservative leverage
        }

        # Strategy timeframes
        self.strategies = {
            'scalp': {
                'duration': '5-15 minutes',
                'target': '0.5-1%',
                'stop': '0.3%',
                'leverage': 20  # Use 20X for scalping
            },
            'intraday': {
                'duration': '1-4 hours',
                'target': '2-3%',
                'stop': '1%',
                'leverage': 10  # Use 10X for intraday
            },
            'swing': {
                'duration': '2-5 days',
                'target': '5-10%',
                'stop': '3%',
                'leverage': 5   # Use 5X for swing
            },
            'position': {
                'duration': '1-4 weeks',
                'target': '15-30%',
                'stop': '5%',
                'leverage': 2   # Use 2X for position trades
            }
        }

        self.riskmetric = UnifiedRiskMetric()

    def determine_leverage_by_risk(self, risk_value: float) -> int:
        """
        Determine leverage based on risk level
        High risk = Lower leverage
        Low risk = Higher leverage
        """
        if risk_value >= 0.8:
            # Extreme high risk - Use lowest leverage
            return self.leverage_options['low']  # 2X
        elif risk_value >= 0.6:
            # High risk - Use medium leverage
            return self.leverage_options['medium']  # 5X
        elif risk_value >= 0.4:
            # Medium risk - Use high leverage
            return self.leverage_options['high']  # 10X
        else:
            # Low risk - Can use ultra high leverage
            return self.leverage_options['ultra_high']  # 20X

    def calculate_position_entries(self, capital: float, risk_level: str) -> Dict[str, Any]:
        """
        Calculate position entry sizes based on doubling strategy
        """
        entries = {}
        total_used = 0

        for entry_name, percentage in self.position_scaling.items():
            if entry_name != 'margin_add':
                entry_size = capital * percentage
                entries[entry_name] = {
                    'percentage': f"{percentage*100:.0f}%",
                    'amount': entry_size,
                    'cumulative': total_used + entry_size
                }
                total_used += entry_size

        # Margin addition (up to 50%)
        margin_available = capital * (self.position_scaling['margin_add'] - total_used/capital)
        entries['margin_addition'] = {
            'percentage': f"Up to 50% total",
            'available': margin_available,
            'note': "Add margin as position moves in favor"
        }

        return entries

    async def generate_complete_strategy(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """
        Generate the COMPLETE and CORRECT trading strategy
        """

        logger.info("\n" + "="*80)
        logger.info(f"📊 CORRECT TRADING STRATEGY FOR {symbol}")
        logger.info("="*80)

        # Get risk assessment
        assessment = await self.riskmetric.assess_risk(symbol, current_price=current_price)

        if not assessment:
            return {'error': 'Unable to get risk assessment'}

        risk_value = assessment.risk_value
        risk_band = assessment.risk_band

        # Determine market bias
        if risk_value >= 0.7:
            market_bias = "SHORT"
            direction = -1
        elif risk_value <= 0.3:
            market_bias = "LONG"
            direction = 1
        else:
            market_bias = "NEUTRAL"
            direction = 0

        logger.info(f"\n📈 MARKET ANALYSIS")
        logger.info(f"  Symbol: {symbol}")
        logger.info(f"  Price: ${current_price:,.2f}")
        logger.info(f"  Risk Value: {risk_value:.3f}")
        logger.info(f"  Risk Band: {risk_band}")
        logger.info(f"  Market Bias: {market_bias}")

        # Determine leverage
        recommended_leverage = self.determine_leverage_by_risk(risk_value)

        logger.info(f"\n⚙️ LEVERAGE SELECTION")
        logger.info(f"  Recommended: {recommended_leverage}X")
        logger.info(f"  Available: 20X, 10X, 5X, 2X")

        # Position sizing
        capital_example = 10000  # Example with $10,000
        entries = self.calculate_position_entries(capital_example, risk_band)

        logger.info(f"\n💰 POSITION SIZING (Doubling Strategy)")
        logger.info(f"  Entry 1: 2% = ${entries['entry_1']['amount']:,.2f}")
        logger.info(f"  Entry 2: 4% = ${entries['entry_2']['amount']:,.2f} (double up)")
        logger.info(f"  Entry 3: 8% = ${entries['entry_3']['amount']:,.2f} (double up)")
        logger.info(f"  Entry 4: 16% = ${entries['entry_4']['amount']:,.2f} (double up)")
        logger.info(f"  Total Base: 30% = ${entries['entry_4']['cumulative']:,.2f}")
        logger.info(f"  Margin Add: Up to 50% = ${entries['margin_addition']['available']:,.2f}")

        # Strategy recommendations
        strategies_recommendation = {}

        for strategy_name, strategy_details in self.strategies.items():
            if market_bias == "LONG":
                win_rate = self.calculate_win_rate(risk_value, strategy_name, 1)
                position = "LONG"
                entry = f"Buy at market or limit at support"
                exit = f"Target: +{strategy_details['target']}, Stop: -{strategy_details['stop']}"
            elif market_bias == "SHORT":
                win_rate = self.calculate_win_rate(risk_value, strategy_name, -1)
                position = "SHORT"
                entry = f"Sell at market or limit at resistance"
                exit = f"Target: -{strategy_details['target']}, Stop: +{strategy_details['stop']}"
            else:
                win_rate = 50
                position = "WAIT"
                entry = "Wait for clearer signal"
                exit = "No position"

            strategies_recommendation[strategy_name] = {
                'position': position,
                'win_rate': f"{win_rate}%",
                'leverage': strategy_details['leverage'],
                'duration': strategy_details['duration'],
                'entry': entry,
                'exit': exit,
                'target': strategy_details['target'],
                'stop': strategy_details['stop']
            }

        logger.info(f"\n📊 STRATEGY RECOMMENDATIONS")
        for name, details in strategies_recommendation.items():
            logger.info(f"\n  {name.upper()}:")
            logger.info(f"    Position: {details['position']}")
            logger.info(f"    Win Rate: {details['win_rate']}")
            logger.info(f"    Leverage: {details['leverage']}X")
            logger.info(f"    Duration: {details['duration']}")

        # Complete strategy package
        complete_strategy = {
            'symbol': symbol,
            'current_price': current_price,
            'risk_assessment': {
                'risk_value': risk_value,
                'risk_band': risk_band,
                'market_bias': market_bias
            },
            'position_sizing': {
                'method': 'Doubling Strategy',
                'entries': entries,
                'rule': '2% → 4% → 8% → 16% → Add Margin to 50%'
            },
            'leverage': {
                'recommended': recommended_leverage,
                'options': self.leverage_options,
                'rule': 'NO 7X! Only 20X, 10X, 5X, 2X'
            },
            'strategies': strategies_recommendation,
            'execution_rules': {
                'entry_method': 'Scale in using doubling strategy',
                'risk_management': 'Never exceed 50% of capital including margin',
                'profit_taking': 'Take partial profits at each target level',
                'stop_loss': 'Always use stops, trail after in profit'
            },
            'timestamp': datetime.now().isoformat()
        }

        return complete_strategy

    def calculate_win_rate(self, risk_value: float, strategy: str, direction: int) -> int:
        """
        Calculate win rate based on risk and strategy
        """
        base_rates = {
            'scalp': {'long': 55, 'short': 55},
            'intraday': {'long': 58, 'short': 58},
            'swing': {'long': 62, 'short': 62},
            'position': {'long': 65, 'short': 65}
        }

        strategy_rate = base_rates.get(strategy, {'long': 50, 'short': 50})

        # Adjust based on risk
        if risk_value < 0.3 and direction == 1:  # Low risk, going long
            return strategy_rate['long'] + 10
        elif risk_value > 0.7 and direction == -1:  # High risk, going short
            return strategy_rate['short'] + 10
        elif risk_value < 0.3 and direction == -1:  # Low risk, going short (against trend)
            return strategy_rate['short'] - 15
        elif risk_value > 0.7 and direction == 1:  # High risk, going long (against trend)
            return strategy_rate['long'] - 15
        else:  # Neutral
            return 50

    def display_execution_example(self, symbol: str, capital: float = 10000) -> None:
        """
        Display a complete execution example
        """
        logger.info(f"\n" + "="*80)
        logger.info(f"💡 EXECUTION EXAMPLE")
        logger.info("="*80)

        logger.info(f"\nStarting Capital: ${capital:,.2f}")
        logger.info(f"Symbol: {symbol}")

        logger.info(f"\n📍 ENTRY SEQUENCE:")
        logger.info(f"1. Entry 1: ${capital * 0.02:,.2f} at market price")
        logger.info(f"   → If price moves against you by 0.5%, add Entry 2")
        logger.info(f"2. Entry 2: ${capital * 0.04:,.2f} (double up)")
        logger.info(f"   → If price moves against you another 0.5%, add Entry 3")
        logger.info(f"3. Entry 3: ${capital * 0.08:,.2f} (double up)")
        logger.info(f"   → If price moves against you another 0.5%, add Entry 4")
        logger.info(f"4. Entry 4: ${capital * 0.16:,.2f} (double up)")
        logger.info(f"   → Total invested: ${capital * 0.30:,.2f} (30%)")

        logger.info(f"\n📈 PROFIT TARGETS:")
        logger.info(f"• Scalp: Exit all at +0.5-1%")
        logger.info(f"• Intraday: Exit 50% at +2%, rest at +3%")
        logger.info(f"• Swing: Exit 33% at +5%, 33% at +7%, rest at +10%")

        logger.info(f"\n⚠️ RISK MANAGEMENT:")
        logger.info(f"• Stop Loss: -3% from average entry")
        logger.info(f"• Max Risk: ${capital * 0.30 * 0.03:,.2f} (3% of position)")
        logger.info(f"• Trail stop after +2% profit")

async def main():
    """Run the correct strategy"""
    strategy = CorrectTradingStrategy()

    # Example for ETH
    symbol = 'ETH'
    current_price = 3500

    # Generate complete strategy
    result = await strategy.generate_complete_strategy(symbol, current_price)

    # Display execution example
    strategy.display_execution_example(symbol, capital=10000)

    # Save strategy
    with open('correct_trading_strategy.json', 'w') as f:
        def clean_for_json(obj):
            if hasattr(obj, '__dict__'):
                return str(obj)
            return obj
        json.dump(result, f, indent=2, default=clean_for_json)

    logger.info(f"\n✅ Strategy saved to correct_trading_strategy.json")
    logger.info(f"\n🎯 REMEMBER: 2% → 4% → 8% → 16% → Add Margin to 50%")
    logger.info(f"🎯 LEVERAGE: 20X, 10X, 5X, 2X only (NO 7X!)")

if __name__ == "__main__":
    asyncio.run(main())