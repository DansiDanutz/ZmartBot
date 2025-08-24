#!/usr/bin/env python3
"""
Discover the Symbol/BTC ratio pattern from Benjamin Cowen's data
"""

import math
import numpy as np
import json

# EXACT DATA FROM BENJAMIN COWEN
BTC_MIN = 30000    # Risk 0
BTC_MAX = 299720   # Risk 1

SYMBOL_DATA = {
    'BTC': {
        'min': 30000,
        'max': 299720,
    },
    'ETH': {
        'min': 445.60,
        'max': 10780.24,
    },
    'SOL': {
        'min': 18.75,
        'max': 907.09,
    },
    'ADA': {
        'min': 0.10,
        'max': 6.56,
    }
}

def analyze_ratios():
    """Analyze Symbol/BTC ratios to find the pattern"""
    print("="*80)
    print("SYMBOL/BTC RATIO ANALYSIS")
    print("="*80)
    
    print(f"\nBTC Reference:")
    print(f"  Min (Risk 0): ${BTC_MIN:,}")
    print(f"  Max (Risk 1): ${BTC_MAX:,}")
    print(f"  Max/Min Ratio: {BTC_MAX/BTC_MIN:.4f}x")
    
    print("\n" + "-"*80)
    print(f"{'Symbol':<10} {'Min Price':<15} {'Max Price':<15} {'Min/BTC Ratio':<20} {'Max/BTC Ratio':<20} {'Ratio Change'}")
    print("-"*80)
    
    ratios = {}
    for symbol, data in SYMBOL_DATA.items():
        if symbol == 'BTC':
            min_btc_ratio = 1.0
            max_btc_ratio = 1.0
            ratio_change = 0
        else:
            min_btc_ratio = data['min'] / BTC_MIN
            max_btc_ratio = data['max'] / BTC_MAX
            ratio_change = (max_btc_ratio / min_btc_ratio - 1) * 100
        
        ratios[symbol] = {
            'min_price': data['min'],
            'max_price': data['max'],
            'min_btc_ratio': min_btc_ratio,
            'max_btc_ratio': max_btc_ratio,
            'ratio_change_percent': ratio_change,
            'price_multiplier': data['max'] / data['min']
        }
        
        print(f"{symbol:<10} ${data['min']:<14.2f} ${data['max']:<14.2f} {min_btc_ratio:<20.8f} {max_btc_ratio:<20.8f} {ratio_change:>10.2f}%")
    
    return ratios

def find_ratio_formula():
    """Find the formula for calculating min/max based on BTC ratios"""
    print("\n" + "="*80)
    print("RATIO FORMULA DISCOVERY")
    print("="*80)
    
    # Analyze the pattern
    eth_min_ratio = 445.60 / 30000  # 0.01485333
    eth_max_ratio = 10780.24 / 299720  # 0.03597920
    
    sol_min_ratio = 18.75 / 30000  # 0.000625
    sol_max_ratio = 907.09 / 299720  # 0.00302716
    
    ada_min_ratio = 0.10 / 30000  # 0.00000333
    ada_max_ratio = 6.56 / 299720  # 0.00002189
    
    print("\nRatio Analysis:")
    print(f"ETH: Min Ratio = {eth_min_ratio:.8f}, Max Ratio = {eth_max_ratio:.8f}")
    print(f"     Ratio increased by {(eth_max_ratio/eth_min_ratio - 1)*100:.2f}%")
    
    print(f"SOL: Min Ratio = {sol_min_ratio:.8f}, Max Ratio = {sol_max_ratio:.8f}")
    print(f"     Ratio increased by {(sol_max_ratio/sol_min_ratio - 1)*100:.2f}%")
    
    print(f"ADA: Min Ratio = {ada_min_ratio:.8f}, Max Ratio = {ada_max_ratio:.8f}")
    print(f"     Ratio increased by {(ada_max_ratio/ada_min_ratio - 1)*100:.2f}%")
    
    # Key insight: The ratios CHANGE during the cycle
    # This means altcoins grow at different rates than BTC
    
    print("\n" + "="*60)
    print("KEY DISCOVERY")
    print("="*60)
    print("""
    The Symbol/BTC ratio is NOT constant!
    - Altcoins have different growth multipliers than BTC
    - Each symbol has its own min and max that creates a unique risk curve
    - The formula appears to be:
      
      Symbol_Min = Fixed value (bear market low)
      Symbol_Max = Fixed value (bull market high)
      
      Risk = (ln(price) - ln(Symbol_Min)) / (ln(Symbol_Max) - ln(Symbol_Min))
    """)
    
    return {
        'ETH': {'min_ratio': eth_min_ratio, 'max_ratio': eth_max_ratio},
        'SOL': {'min_ratio': sol_min_ratio, 'max_ratio': sol_max_ratio},
        'ADA': {'min_ratio': ada_min_ratio, 'max_ratio': ada_max_ratio}
    }

def generate_risk_formula(symbol, min_price, max_price):
    """Generate the complete risk formula for a symbol"""
    print(f"\n" + "="*60)
    print(f"{symbol} RISK FORMULA")
    print("="*60)
    
    print(f"\nParameters:")
    print(f"  Min Price (Risk 0): ${min_price:.2f}")
    print(f"  Max Price (Risk 1): ${max_price:.2f}")
    print(f"  Growth Multiple: {max_price/min_price:.2f}x")
    
    print(f"\nFormulas:")
    print(f"  Risk from Price: risk = (ln(price) - ln({min_price:.2f})) / ln({max_price/min_price:.2f})")
    print(f"  Price from Risk: price = {min_price:.2f} * ({max_price/min_price:.2f})^risk")
    
    # Generate risk table
    print(f"\nRisk Table (Sample):")
    print("-"*40)
    print(f"{'Risk':<10} {'Price':<15}")
    print("-"*40)
    
    for risk in [0, 0.1, 0.25, 0.5, 0.75, 1.0]:
        if risk == 0:
            price = min_price
        elif risk == 1:
            price = max_price
        else:
            # Logarithmic interpolation
            log_price = math.log(min_price) + risk * (math.log(max_price) - math.log(min_price))
            price = math.exp(log_price)
        
        print(f"{risk:<10.2f} ${price:<14,.2f}")
    
    return {
        'min': min_price,
        'max': max_price,
        'formula_type': 'logarithmic',
        'growth_multiple': max_price / min_price
    }

def test_price_to_risk():
    """Test calculating risk from current prices"""
    print("\n" + "="*80)
    print("TEST: CURRENT PRICES TO RISK VALUES")
    print("="*80)
    
    # Test prices
    test_prices = {
        'BTC': 95000,
        'ETH': 3800,
        'SOL': 185,
        'ADA': 0.65
    }
    
    print(f"\n{'Symbol':<10} {'Current Price':<15} {'Risk Value':<15} {'Market Phase'}")
    print("-"*70)
    
    for symbol, price in test_prices.items():
        if symbol in SYMBOL_DATA:
            min_price = SYMBOL_DATA[symbol]['min']
            max_price = SYMBOL_DATA[symbol]['max']
            
            if price <= min_price:
                risk = 0.0
            elif price >= max_price:
                risk = 1.0
            else:
                risk = (math.log(price) - math.log(min_price)) / (math.log(max_price) - math.log(min_price))
            
            # Determine market phase
            if risk < 0.25:
                phase = "BUY ZONE (Bear)"
            elif risk < 0.40:
                phase = "EARLY BULL"
            elif risk < 0.60:
                phase = "NEUTRAL"
            elif risk < 0.75:
                phase = "LATE BULL"
            else:
                phase = "SELL ZONE (Top)"
            
            print(f"{symbol:<10} ${price:<14,.2f} {risk:<15.4f} {phase}")

def create_implementation():
    """Create the complete implementation"""
    print("\n" + "="*80)
    print("COMPLETE IMPLEMENTATION")
    print("="*80)
    
    code = '''
class CowenRiskMetric:
    """Benjamin Cowen's Complete RiskMetric Implementation"""
    
    # Exact min/max values for each symbol
    SYMBOL_BOUNDS = {
        'BTC': {'min': 30000, 'max': 299720},
        'ETH': {'min': 445.60, 'max': 10780.24},
        'SOL': {'min': 18.75, 'max': 907.09},
        'ADA': {'min': 0.10, 'max': 6.56},
        # Add more symbols as needed
    }
    
    @staticmethod
    def calculate_risk(symbol: str, price: float) -> float:
        """Calculate risk (0-1) from price"""
        if symbol not in CowenRiskMetric.SYMBOL_BOUNDS:
            raise ValueError(f"Symbol {symbol} not configured")
        
        bounds = CowenRiskMetric.SYMBOL_BOUNDS[symbol]
        min_price = bounds['min']
        max_price = bounds['max']
        
        if price <= min_price:
            return 0.0
        elif price >= max_price:
            return 1.0
        else:
            return (math.log(price) - math.log(min_price)) / (math.log(max_price) - math.log(min_price))
    
    @staticmethod
    def calculate_price(symbol: str, risk: float) -> float:
        """Calculate price from risk (0-1)"""
        if symbol not in CowenRiskMetric.SYMBOL_BOUNDS:
            raise ValueError(f"Symbol {symbol} not configured")
        
        bounds = CowenRiskMetric.SYMBOL_BOUNDS[symbol]
        min_price = bounds['min']
        max_price = bounds['max']
        
        if risk <= 0:
            return min_price
        elif risk >= 1:
            return max_price
        else:
            return min_price * math.exp(risk * math.log(max_price / min_price))
    '''
    
    print(code)

def main():
    print("\n" + "🎯"*40)
    print("BENJAMIN COWEN COMPLETE METHODOLOGY DISCOVERY")
    print("🎯"*40)
    
    # Step 1: Analyze ratios
    ratios = analyze_ratios()
    
    # Step 2: Find ratio formula
    ratio_formulas = find_ratio_formula()
    
    # Step 3: Generate formulas for each symbol
    for symbol in ['ETH', 'SOL', 'ADA']:
        data = SYMBOL_DATA[symbol]
        generate_risk_formula(symbol, data['min'], data['max'])
    
    # Step 4: Test current prices
    test_price_to_risk()
    
    # Step 5: Create implementation
    create_implementation()
    
    # Save complete methodology
    methodology = {
        'discovery': 'Each symbol has FIXED min/max values, not derived from BTC ratios',
        'formula': 'risk = (ln(price) - ln(min)) / (ln(max) - ln(min))',
        'symbols': SYMBOL_DATA,
        'ratios': ratios,
        'key_insights': [
            'Min/max are fixed per symbol based on historical bear/bull extremes',
            'The logarithmic formula applies to ALL symbols',
            'Symbol/BTC ratios CHANGE throughout the cycle',
            'Altcoins have higher growth multiples than BTC'
        ],
        'implementation': {
            'step1': 'Define min/max for each symbol',
            'step2': 'Use logarithmic formula for risk calculation',
            'step3': 'Apply time-spent coefficients for scoring',
            'step4': 'Generate signals based on risk zones'
        }
    }
    
    with open('cowen_complete_methodology.json', 'w') as f:
        json.dump(methodology, f, indent=2)
    
    print("\n" + "="*80)
    print("METHODOLOGY COMPLETE")
    print("="*80)
    print("\n✅ Complete methodology discovered and saved!")
    print("\nKEY FINDINGS:")
    print("1. Each symbol has FIXED min/max values (not calculated from BTC)")
    print("2. All symbols use the SAME logarithmic formula")
    print("3. The formula is: risk = (ln(price) - ln(min)) / (ln(max) - ln(min))")
    print("4. To add new symbols, we need their historical bear/bull extremes")
    print("\n📊 Next: Build the complete RiskMetric agent with this methodology")

if __name__ == "__main__":
    main()