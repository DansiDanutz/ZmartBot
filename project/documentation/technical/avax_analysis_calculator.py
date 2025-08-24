#!/usr/bin/env python3
"""
AVAX USDT Comprehensive Analysis and Win Rate Calculator
Based on collected market data and technical analysis
"""

import json
import numpy as np
from datetime import datetime

class AVAXAnalyzer:
    def __init__(self):
        self.current_price = 23.90
        self.market_cap = 10.09e9  # $10.09B
        self.volume_24h = 671.96e6  # $671.96M
        self.rank = 17
        
        # Technical levels
        self.resistance_levels = [27.0, 36.0]  # Major resistance, breakout target
        self.support_levels = [23.0, 15.0]    # Current support, major support
        
        # Market data
        self.liquidation_data = {
            'total_24h': 3.10e6,
            'long_liquidations': 2.96e6,
            'short_liquidations': 0.146e6,
            'long_ratio': 95.5  # % of liquidations that were longs
        }
        
        self.derivatives_data = {
            'open_interest': 745.49e6,
            'volume': 1.41e9,
            'long_short_ratio': 0.9739,  # Slightly bearish
            'binance_ls_ratio': 2.6536,
            'top_trader_ls_ratio': 2.8285
        }
        
        # Range trading data
        self.trading_range = {
            'high': 27.0,
            'low': 15.0,
            'duration_months': 6,
            'current_position': 'near_support'  # Currently at $23.90, near $23 support
        }
        
    def calculate_technical_score(self):
        """Calculate technical analysis score for AVAX"""
        scores = []
        
        # Range position analysis
        range_size = self.trading_range['high'] - self.trading_range['low']
        current_position_in_range = (self.current_price - self.trading_range['low']) / range_size
        
        # Currently at 74% of range (closer to resistance than support)
        if current_position_in_range > 0.8:
            range_score = 30  # Near resistance, bearish
        elif current_position_in_range < 0.2:
            range_score = 70  # Near support, bullish
        else:
            range_score = 50  # Mid-range, neutral
        
        scores.append(range_score)
        
        # Support/Resistance proximity
        distance_to_support = abs(self.current_price - 23.0) / self.current_price
        distance_to_resistance = abs(27.0 - self.current_price) / self.current_price
        
        if distance_to_support < 0.05:  # Within 5% of support
            proximity_score = 65  # Potential bounce
        elif distance_to_resistance < 0.05:  # Within 5% of resistance
            proximity_score = 35  # Potential rejection
        else:
            proximity_score = 50
        
        scores.append(proximity_score)
        
        # Volume trend (declining = bearish)
        volume_score = 40  # Volume down 31.84% in 7 days
        scores.append(volume_score)
        
        return np.mean(scores)
    
    def calculate_sentiment_score(self):
        """Calculate market sentiment score"""
        scores = []
        
        # Liquidation analysis
        long_liq_dominance = self.liquidation_data['long_ratio']
        if long_liq_dominance > 90:
            liq_score = 65  # Heavy long liquidations = potential oversold
        elif long_liq_dominance < 10:
            liq_score = 35  # Heavy short liquidations = potential overbought
        else:
            liq_score = 50
        
        scores.append(liq_score)
        
        # Long/Short ratio analysis
        ls_ratio = self.derivatives_data['long_short_ratio']
        if ls_ratio < 1.0:  # More shorts than longs
            ls_score = 60  # Contrarian bullish
        else:
            ls_score = 40  # More longs, potential bearish
        
        scores.append(ls_score)
        
        # Top trader positioning
        top_trader_ratio = self.derivatives_data['top_trader_ls_ratio']
        if top_trader_ratio > 2.5:  # Top traders heavily long
            trader_score = 45  # Potentially crowded long trade
        else:
            trader_score = 55
        
        scores.append(trader_score)
        
        return np.mean(scores)
    
    def calculate_momentum_score(self):
        """Calculate momentum and trend score"""
        scores = []
        
        # Price momentum (recent performance)
        price_momentum = 45  # Slight decline, consolidation
        scores.append(price_momentum)
        
        # Volume momentum
        volume_momentum = 35  # Declining volume
        scores.append(volume_momentum)
        
        # Open Interest trend
        oi_momentum = 55  # OI up 4.36%, slight positive
        scores.append(oi_momentum)
        
        # Range breakout potential
        months_in_range = self.trading_range['duration_months']
        if months_in_range >= 6:
            breakout_score = 60  # Long consolidation increases breakout probability
        else:
            breakout_score = 50
        
        scores.append(breakout_score)
        
        return np.mean(scores)
    
    def calculate_composite_scores(self):
        """Calculate composite long and short scores"""
        technical_score = self.calculate_technical_score()
        sentiment_score = self.calculate_sentiment_score()
        momentum_score = self.calculate_momentum_score()
        
        # Weight the components
        weights = {
            'technical': 0.4,
            'sentiment': 0.35,
            'momentum': 0.25
        }
        
        # Long score calculation
        long_score = (technical_score * weights['technical'] + 
                     sentiment_score * weights['sentiment'] + 
                     momentum_score * weights['momentum'])
        
        # Short score (inverse relationship for some factors)
        short_technical = 100 - technical_score + 10  # Slight adjustment for range trading
        short_sentiment = sentiment_score * 0.8  # Sentiment less impactful for shorts
        short_momentum = 100 - momentum_score
        
        short_score = (short_technical * weights['technical'] + 
                      short_sentiment * weights['sentiment'] + 
                      short_momentum * weights['momentum'])
        
        return {
            'long_score': max(25, min(75, long_score)),  # Cap between 25-75
            'short_score': max(25, min(75, short_score)),
            'components': {
                'technical': technical_score,
                'sentiment': sentiment_score,
                'momentum': momentum_score
            }
        }
    
    def calculate_win_rates_by_timeframe(self, long_score, short_score):
        """Calculate win rates for different timeframes"""
        
        def score_to_win_rate(score, timeframe, position):
            """Convert score to win rate with AVAX-specific adjustments"""
            # Base conversion
            base_rate = score * 0.8  # AVAX is range-bound, more predictable
            
            # Timeframe adjustments
            if timeframe == '24-48h':
                volatility_factor = 0.9  # Range-bound = lower volatility
            elif timeframe == '7d':
                volatility_factor = 1.0  # Balanced
            else:  # 1 month
                volatility_factor = 1.1  # Range breakouts more reliable over time
            
            # Position adjustments for AVAX
            if position == 'long':
                if timeframe == '1m':
                    position_factor = 1.15  # Range breakouts favor longs long-term
                else:
                    position_factor = 1.0
            else:  # short
                if timeframe == '24-48h':
                    position_factor = 1.05  # Short-term range trading favors shorts
                else:
                    position_factor = 0.95
            
            # Range position adjustment
            if self.current_price < 25:  # Near support
                if position == 'long':
                    range_factor = 1.1  # Bounce potential
                else:
                    range_factor = 0.9
            else:  # Near resistance
                if position == 'long':
                    range_factor = 0.9
                else:
                    range_factor = 1.1  # Rejection potential
            
            win_rate = base_rate * volatility_factor * position_factor * range_factor
            
            # Cap between 30% and 75% (realistic bounds for AVAX)
            return max(30, min(75, win_rate))
        
        win_rates = {
            '24-48h': {
                'long': score_to_win_rate(long_score, '24-48h', 'long'),
                'short': score_to_win_rate(short_score, '24-48h', 'short')
            },
            '7d': {
                'long': score_to_win_rate(long_score, '7d', 'long'),
                'short': score_to_win_rate(short_score, '7d', 'short')
            },
            '1m': {
                'long': score_to_win_rate(long_score, '1m', 'long'),
                'short': score_to_win_rate(short_score, '1m', 'short')
            }
        }
        
        return win_rates
    
    def generate_market_scenarios(self):
        """Generate market scenarios with probabilities"""
        scenarios = {
            'bullish_breakout': {
                'probability': 35,
                'description': 'Break above $27 resistance, target $36',
                'catalyst': 'Volume increase, institutional buying, range breakout',
                'timeframe': '2-8 weeks',
                'price_target': 36.0,
                'return_potential': 50.6
            },
            'bearish_breakdown': {
                'probability': 25,
                'description': 'Break below $23 support, target $15',
                'catalyst': 'Volume decline, macro headwinds, support failure',
                'timeframe': '2-6 weeks',
                'price_target': 15.0,
                'return_potential': -37.2
            },
            'continued_range': {
                'probability': 40,
                'description': 'Remain in $15-$27 range',
                'catalyst': 'Low volume, institutional indecision, market uncertainty',
                'timeframe': '4-12 weeks',
                'price_target': 21.0,
                'return_potential': -12.1
            }
        }
        
        return scenarios
    
    def analyze_risk_factors(self):
        """Analyze current risk factors"""
        risk_factors = {
            'high_risk': [
                'Heavy long liquidations (95.5% of total)',
                'Declining volume (-31.84% in 7 days)',
                '6-month range consolidation nearing resolution',
                'Current price near critical $23 support'
            ],
            'medium_risk': [
                'Slightly bearish positioning (L/S ratio 0.97)',
                'Top traders heavily long (2.83:1 ratio)',
                'Open interest increasing (+4.36%)',
                'Range-bound market with limited catalysts'
            ],
            'low_risk': [
                'Strong support at $15 (major level)',
                'Clear resistance levels for risk management',
                'Established trading range provides structure',
                'Potential for significant breakout moves'
            ]
        }
        
        return risk_factors
    
    def generate_comprehensive_analysis(self):
        """Generate complete analysis"""
        scores = self.calculate_composite_scores()
        win_rates = self.calculate_win_rates_by_timeframe(scores['long_score'], scores['short_score'])
        scenarios = self.generate_market_scenarios()
        risk_factors = self.analyze_risk_factors()
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'symbol': 'AVAX-USDT',
            'current_price': self.current_price,
            'market_cap': self.market_cap,
            'composite_scores': scores,
            'win_rates_by_timeframe': win_rates,
            'market_scenarios': scenarios,
            'risk_factors': risk_factors,
            'key_levels': {
                'resistance': self.resistance_levels,
                'support': self.support_levels
            },
            'liquidation_analysis': self.liquidation_data,
            'derivatives_analysis': self.derivatives_data
        }
        
        return analysis

def main():
    """Main execution function"""
    print("Starting AVAX USDT Comprehensive Analysis...")
    print("=" * 50)
    
    analyzer = AVAXAnalyzer()
    analysis = analyzer.generate_comprehensive_analysis()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"/home/ubuntu/avax_usdt_analysis_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"Analysis completed! Results saved to: {results_file}")
    
    # Display key results
    print("\n" + "=" * 50)
    print("AVAX USDT ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"\nCOMPOSITE SCORES:")
    print(f"Long Position Score:  {analysis['composite_scores']['long_score']:.1f}/100")
    print(f"Short Position Score: {analysis['composite_scores']['short_score']:.1f}/100")
    
    print(f"\nWIN RATES BY TIMEFRAME:")
    for timeframe, rates in analysis['win_rates_by_timeframe'].items():
        print(f"\n{timeframe.upper()}:")
        print(f"  Long Positions:  {rates['long']:.1f}% win rate")
        print(f"  Short Positions: {rates['short']:.1f}% win rate")
    
    print(f"\nMARKET SCENARIOS:")
    for scenario, data in analysis['market_scenarios'].items():
        print(f"\n{scenario.replace('_', ' ').title()}: {data['probability']}%")
        print(f"  Target: ${data['price_target']:.1f} ({data['return_potential']:+.1f}%)")
    
    print(f"\nCRITICAL LEVELS:")
    print(f"Support: {analysis['key_levels']['support']}")
    print(f"Resistance: {analysis['key_levels']['resistance']}")
    
    return analysis

if __name__ == "__main__":
    results = main()

