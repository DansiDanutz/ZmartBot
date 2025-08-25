#!/usr/bin/env python3
"""
EXACT Implementation of Benjamin Cowen's Risk Metric Calculation Methodology
Following the guide provided by ChatGPT - NO GUESSING, ONLY WHAT'S WRITTEN
"""

import numpy as np
import pandas as pd
import math

class ExactCowenMethodology:
    """
    Exact implementation following the methodology guide
    """
    
    # Step 1: Define BTC Min/Max (Fixed for All Symbols)
    BTC_MIN = 30000
    BTC_MAX = 299720
    
    def calculate_symbol_bounds(self, ratio_bottom: float, ratio_top: float) -> tuple:
        """
        Step 3: Compute Symbol Min/Max
        Symbol_min = BTC_min × Symbol/BTC at bottom
        Symbol_max = BTC_max × Symbol/BTC at top
        """
        symbol_min = self.BTC_MIN * ratio_bottom
        symbol_max = self.BTC_MAX * ratio_top
        return symbol_min, symbol_max
    
    def risk_to_price_exponential(self, symbol_min: float, symbol_max: float, risk: float) -> float:
        """
        Exponential Model (Forward)
        price = Symbol_min × (Symbol_max / Symbol_min)^risk
        """
        if risk <= 0:
            return symbol_min
        elif risk >= 1:
            return symbol_max
        else:
            return symbol_min * ((symbol_max / symbol_min) ** risk)
    
    def price_to_risk_exponential(self, symbol_min: float, symbol_max: float, price: float) -> float:
        """
        Exponential Model (Inverse)
        risk = ln(price / Symbol_min) / ln(Symbol_max / Symbol_min)
        """
        if price <= symbol_min:
            return 0.0
        elif price >= symbol_max:
            return 1.0
        else:
            return math.log(price / symbol_min) / math.log(symbol_max / symbol_min)
    
    def generate_risk_table(self, symbol: str, ratio_bottom: float, ratio_top: float, steps: int = 41) -> pd.DataFrame:
        """
        Step 4: Generate RISK → PRICE Table
        RISK: from 0 to 1 (step = 0.025 for 41 steps)
        """
        sym_min = self.BTC_MIN * ratio_bottom
        sym_max = self.BTC_MAX * ratio_top
        
        risk_values = np.linspace(0, 1, steps)
        prices = sym_min * ((sym_max / sym_min) ** risk_values)
        
        df = pd.DataFrame({
            'RISK': risk_values.round(3),
            f'{symbol}_PRICE': prices.round(4)
        })
        
        return df
    
    def risk_to_price_polynomial(self, symbol_min: float, symbol_max: float, risk: float, 
                                 a: float = None, b: float = None, c: float = None, 
                                 d: float = None, e: float = None) -> float:
        """
        Polynomial Formula (4th Degree)
        price = a + b·risk + c·risk² + d·risk³ + e·risk⁴
        
        If coefficients not provided, fit to min/max bounds
        """
        if a is None:
            # Default polynomial that maps 0->min, 1->max
            # This is a simple linear interpolation as placeholder
            # In practice, you'd fit this to actual data
            return symbol_min + (symbol_max - symbol_min) * risk
        else:
            return a + b*risk + c*risk**2 + d*risk**3 + e*risk**4


def demonstrate_exact_methodology():
    """
    Demonstrate the EXACT methodology as provided
    """
    model = ExactCowenMethodology()
    
    print("🧠 CRYPTOCURRENCY RISK METRIC CALCULATION METHODOLOGY")
    print("=" * 80)
    
    print("\n✅ Step 1: Define BTC Min/Max (Fixed for All Symbols)")
    print(f"BTC_min = {model.BTC_MIN:,}")
    print(f"BTC_max = {model.BTC_MAX:,}")
    
    print("\n✅ Step 2: Estimate Symbol/BTC Ratios")
    print("Symbol/BTC at bottom = Symbol_min / BTC_min")
    print("Symbol/BTC at top    = Symbol_max / BTC_max")
    
    # Example: SOL (from the guide)
    print("\n🎯 Example: SOL")
    print("-" * 40)
    sol_ratio_bottom = 0.000625
    sol_ratio_top = 0.003027
    
    print(f"SOL/BTC bottom = {sol_ratio_bottom}")
    print(f"SOL/BTC top    = {sol_ratio_top}")
    
    sol_min, sol_max = model.calculate_symbol_bounds(sol_ratio_bottom, sol_ratio_top)
    print(f"\nSOL_min = {model.BTC_MIN:,} × {sol_ratio_bottom} = {sol_min:.2f}")
    print(f"SOL_max = {model.BTC_MAX:,} × {sol_ratio_top} = {sol_max:.2f}")
    
    # Example: LTC (from the guide)
    print("\n🎯 Example: LTC")
    print("-" * 40)
    ltc_ratio_bottom = 0.0006177
    ltc_ratio_top = 0.004225
    
    print(f"LTC/BTC bottom = {ltc_ratio_bottom}")
    print(f"LTC/BTC top    = {ltc_ratio_top}")
    
    ltc_min, ltc_max = model.calculate_symbol_bounds(ltc_ratio_bottom, ltc_ratio_top)
    print(f"\nLTC_min = {model.BTC_MIN:,} × {ltc_ratio_bottom} ≈ {ltc_min:.2f}")
    print(f"LTC_max = {model.BTC_MAX:,} × {ltc_ratio_top} ≈ {ltc_max:.2f}")
    
    # Generate risk tables
    print("\n✅ Step 4: Generate RISK → PRICE Table")
    print("-" * 40)
    
    sol_table = model.generate_risk_table("SOL", sol_ratio_bottom, sol_ratio_top, steps=11)
    print("\nSOL Risk Table (sample):")
    print(sol_table.to_string(index=False))
    
    # Test exponential model
    print("\n🔁 Exponential Model Tests")
    print("-" * 40)
    
    # Forward: Risk to Price
    test_risks = [0.0, 0.25, 0.5, 0.75, 1.0]
    print("\nSOL - Risk to Price:")
    for risk in test_risks:
        price = model.risk_to_price_exponential(sol_min, sol_max, risk)
        print(f"  Risk {risk:.2f} → ${price:.2f}")
    
    # Inverse: Price to Risk
    test_prices = [18.75, 100, 250, 500, 907.09]
    print("\nSOL - Price to Risk:")
    for price in test_prices:
        risk = model.price_to_risk_exponential(sol_min, sol_max, price)
        print(f"  ${price:.2f} → Risk {risk:.3f}")
    
    print("\n" + "=" * 80)
    print("✅ SUMMARY TABLE")
    print("-" * 80)
    print("| Component    | Formula                                          |")
    print("|--------------|--------------------------------------------------|")
    print("| SYMBOL_min   | BTC_min × SYMBOL/BTC at BTC bottom              |")
    print("| SYMBOL_max   | BTC_max × SYMBOL/BTC at BTC top                 |")
    print("| RISK → Price | Exponential: min × (max/min)^risk               |")
    print("| Price → RISK | Exponential: ln(price/min) / ln(max/min)        |")
    print("-" * 80)
    
    # Test with known values from Google Sheets
    print("\n🧪 Testing with Known Values")
    print("-" * 40)
    
    # Known ratios from Google Sheets
    known_ratios = {
        'ETH': {'bottom': 0.0148533333, 'top': 0.0359677032},
        'SOL': {'bottom': 0.0006250000, 'top': 0.0030264580},
        'ADA': {'bottom': 0.0000033333, 'top': 0.0000218871},
        'AAVE': {'bottom': 0.0021116667, 'top': 0.0048245029},
    }
    
    for symbol, ratios in known_ratios.items():
        sym_min, sym_max = model.calculate_symbol_bounds(ratios['bottom'], ratios['top'])
        print(f"\n{symbol}:")
        print(f"  Min: ${sym_min:.2f}")
        print(f"  Max: ${sym_max:.2f}")
        print(f"  Range: {sym_max/sym_min:.1f}x")
        
        # Test mid-point
        mid_price = model.risk_to_price_exponential(sym_min, sym_max, 0.5)
        print(f"  Risk 0.5 → ${mid_price:.2f}")


if __name__ == "__main__":
    demonstrate_exact_methodology()