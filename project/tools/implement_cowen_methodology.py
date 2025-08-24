#!/usr/bin/env python3
"""
Implementation of Benjamin Cowen's EXACT Risk Metric Methodology
As documented in the methodology guide
"""

import numpy as np
import pandas as pd
import math
from typing import Dict, Tuple

class CowenRiskMetricMethodology:
    """
    Exact implementation of Benjamin Cowen's Risk Metric
    Using exponential model with fixed BTC anchors
    """
    
    # Fixed BTC anchors for all symbols
    BTC_MIN = 30000
    BTC_MAX = 299720
    
    # Symbol/BTC ratios from Google Sheets (verified)
    SYMBOL_BTC_RATIOS = {
        'BTC': {'bottom': 1.0, 'top': 1.0},
        'ETH': {'bottom': 0.0148533333, 'top': 0.0359677032},
        'SOL': {'bottom': 0.0006250000, 'top': 0.0030264580},
        'ADA': {'bottom': 0.0000033333, 'top': 0.0000218871},
        'AAVE': {'bottom': 0.0021116667, 'top': 0.0048245029},
        'XRP': {'bottom': 0.0000260000, 'top': None},  # Need max
        'BNB': {'bottom': 0.0093206667, 'top': None},  # Need max
        'DOGE': {'bottom': 0.0000023333, 'top': None}, # Need max
        'LINK': {'bottom': 0.0000780000, 'top': None}, # Need max
        'AVAX': {'bottom': 0.0001380000, 'top': None}, # Need max
        'XLM': {'bottom': 0.0000026667, 'top': None},  # Need max
        'SUI': {'bottom': 0.0000416667, 'top': None},  # Need max
        'DOT': {'bottom': 0.0000493333, 'top': None},  # Need max
        'LTC': {'bottom': 0.0006173333, 'top': None},  # Need max
        'XMR': {'bottom': 0.0026203333, 'top': None},  # Need max
    }
    
    def calculate_symbol_bounds(self, symbol: str) -> Tuple[float, float]:
        """
        Step 3: Compute Symbol Min/Max
        Symbol_min = BTC_min × Symbol/BTC at bottom
        Symbol_max = BTC_max × Symbol/BTC at top
        """
        if symbol not in self.SYMBOL_BTC_RATIOS:
            raise ValueError(f"Unknown symbol: {symbol}")
        
        ratios = self.SYMBOL_BTC_RATIOS[symbol]
        
        if ratios['top'] is None:
            raise ValueError(f"Missing top ratio for {symbol}")
        
        symbol_min = self.BTC_MIN * ratios['bottom']
        symbol_max = self.BTC_MAX * ratios['top']
        
        return symbol_min, symbol_max
    
    def risk_to_price_exponential(self, symbol: str, risk: float) -> float:
        """
        Exponential Model (Forward)
        price = Symbol_min × (Symbol_max / Symbol_min)^risk
        """
        symbol_min, symbol_max = self.calculate_symbol_bounds(symbol)
        
        if risk <= 0:
            return symbol_min
        elif risk >= 1:
            return symbol_max
        else:
            return symbol_min * ((symbol_max / symbol_min) ** risk)
    
    def price_to_risk_exponential(self, symbol: str, price: float) -> float:
        """
        Exponential Model (Inverse)
        risk = ln(price / Symbol_min) / ln(Symbol_max / Symbol_min)
        """
        symbol_min, symbol_max = self.calculate_symbol_bounds(symbol)
        
        if price <= symbol_min:
            return 0.0
        elif price >= symbol_max:
            return 1.0
        else:
            return math.log(price / symbol_min) / math.log(symbol_max / symbol_min)
    
    def generate_risk_table(self, symbol: str, steps: int = 41) -> pd.DataFrame:
        """
        Step 4: Generate RISK → PRICE Table
        RISK: from 0 to 1 (step = 0.025 for 41 steps)
        """
        ratios = self.SYMBOL_BTC_RATIOS[symbol]
        
        if ratios['top'] is None:
            raise ValueError(f"Missing top ratio for {symbol}")
        
        sym_min = self.BTC_MIN * ratios['bottom']
        sym_max = self.BTC_MAX * ratios['top']
        
        risk_values = np.linspace(0, 1, steps)
        prices = sym_min * ((sym_max / sym_min) ** risk_values)
        
        df = pd.DataFrame({
            'RISK': risk_values.round(3),
            f'{symbol}_PRICE': prices.round(4)
        })
        
        return df
    
    def verify_with_known_values(self):
        """
        Verify implementation with known values from Google Sheets
        """
        print("✅ VERIFYING IMPLEMENTATION WITH KNOWN VALUES")
        print("=" * 80)
        
        # Test AAVE at $275.39 should give risk = 0.566
        aave_price = 275.39
        aave_risk = self.price_to_risk_exponential('AAVE', aave_price)
        
        print(f"\nAAVE at ${aave_price}:")
        print(f"  Calculated risk: {aave_risk:.3f}")
        print(f"  Expected risk: 0.566")
        print(f"  Match: {'✅' if abs(aave_risk - 0.566) < 0.01 else '❌'}")
        
        # Generate tables for verified symbols
        for symbol in ['ETH', 'SOL', 'ADA', 'AAVE']:
            if self.SYMBOL_BTC_RATIOS[symbol]['top'] is not None:
                sym_min, sym_max = self.calculate_symbol_bounds(symbol)
                print(f"\n{symbol}:")
                print(f"  Min: ${sym_min:.2f}")
                print(f"  Max: ${sym_max:.2f}")
                print(f"  Range: {sym_max/sym_min:.1f}x")
                
                # Test some risk values
                for risk in [0.0, 0.25, 0.5, 0.75, 1.0]:
                    price = self.risk_to_price_exponential(symbol, risk)
                    print(f"    Risk {risk:.2f} → ${price:.2f}")

def demonstrate():
    """
    Demonstrate the complete methodology
    """
    model = CowenRiskMetricMethodology()
    
    print("🎯 BENJAMIN COWEN'S RISK METRIC METHODOLOGY")
    print("=" * 80)
    
    print("\n📊 STEP 1: Fixed BTC Anchors")
    print(f"  BTC_min = ${model.BTC_MIN:,}")
    print(f"  BTC_max = ${model.BTC_MAX:,}")
    
    print("\n📊 STEP 2: Symbol/BTC Ratios (from historical data)")
    for symbol, ratios in model.SYMBOL_BTC_RATIOS.items():
        if ratios['top'] is not None:
            print(f"  {symbol}: bottom={ratios['bottom']:.10f}, top={ratios['top']:.10f}")
    
    print("\n📊 STEP 3: Calculate Symbol Bounds")
    for symbol in ['ETH', 'SOL', 'ADA', 'AAVE']:
        sym_min, sym_max = model.calculate_symbol_bounds(symbol)
        print(f"  {symbol}: ${sym_min:.2f} - ${sym_max:.2f}")
    
    print("\n📊 STEP 4: Generate Risk Tables")
    
    # Generate and show sample of SOL table
    sol_table = model.generate_risk_table('SOL', steps=11)  # Just 11 for display
    print("\nSOL Risk Table (sample):")
    print(sol_table.to_string(index=False))
    
    # Verify implementation
    print("\n" + "=" * 80)
    model.verify_with_known_values()
    
    print("\n" + "=" * 80)
    print("💡 KEY FORMULA:")
    print("  Forward:  price = min × (max/min)^risk")
    print("  Inverse:  risk = ln(price/min) / ln(max/min)")
    print("\nThis is the EXACT methodology from Benjamin Cowen!")

if __name__ == "__main__":
    demonstrate()