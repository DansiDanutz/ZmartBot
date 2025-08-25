#!/usr/bin/env python3
"""
Analyze polynomial patterns for all symbols from Cowen's exact data
"""

import numpy as np
import pandas as pd
import math

def analyze_all_symbols():
    """Analyze polynomial adjustment patterns for all symbols"""
    
    # Cowen's exact data
    risks = np.array([0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 
                      0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.475, 0.5, 0.525, 0.55, 0.575, 0.6, 
                      0.625, 0.65, 0.675, 0.7, 0.725, 0.75, 0.775, 0.8, 0.825, 0.85, 0.875, 0.9, 
                      0.925, 0.95, 0.975, 1.0])
    
    symbol_data = {
        'BTC': [30000, 31352, 32704, 34055, 35567, 37452, 39336, 41718, 44371, 47457, 50778, 54471, 
                58519, 62865, 67523, 72497, 77786, 83385, 89289, 95509, 102054, 108886, 116028, 123479,
                131227, 139275, 147635, 156284, 165228, 174480, 184029, 193872, 204009, 214439, 225163,
                236186, 247499, 259099, 272006, 286003, 299720],
        
        'ETH': [445.60, 482.55, 522.56, 565.88, 612.80, 663.60, 718.62, 778.20, 842.72, 912.59, 988.25,
                1070.19, 1158.92, 1255.00, 1359.05, 1471.73, 1593.75, 1725.89, 1868.98, 2023.93, 2191.74,
                2373.45, 2570.23, 2783.33, 3014.09, 3263.99, 3534.60, 3827.65, 4145.00, 4488.66, 4860.81,
                5263.81, 5700.23, 6172.83, 6684.62, 7238.83, 7839.00, 8488.92, 9192.73, 9954.89, 10780.24],
        
        'SOL': [18.75, 21.09, 23.69, 26.64, 29.92, 33.64, 37.81, 42.50, 47.76, 53.73, 60.40, 68.04,
                76.82, 82.68, 87.78, 93.25, 99.00, 105.18, 111.74, 118.74, 126.22, 134.13, 142.65, 151.70,
                161.35, 171.66, 182.61, 197.79, 222.41, 249.95, 280.96, 315.88, 354.92, 399.16, 448.61,
                504.57, 567.03, 637.73, 717.11, 806.46, 907.09],
        
        'ADA': [0.10, 0.11, 0.12, 0.14, 0.15, 0.17, 0.19, 0.22, 0.24, 0.27, 0.31, 0.35, 0.39, 0.45,
                0.50, 0.53, 0.56, 0.60, 0.63, 0.67, 0.72, 0.76, 0.81, 0.88, 0.99, 1.12, 1.26, 1.41,
                1.59, 1.79, 2.01, 2.27, 2.55, 2.87, 3.23, 3.64, 4.09, 4.60, 5.18, 5.83, 6.56],
        
        'DOT': [1.48, 1.67, 1.89, 2.13, 2.40, 2.70, 3.05, 3.44, 3.81, 4.05, 4.31, 4.58, 4.86, 5.17,
                5.50, 5.84, 6.21, 6.60, 7.02, 7.46, 7.94, 8.44, 8.97, 9.54, 10.15, 10.80, 11.48, 12.33,
                14.03, 15.98, 18.22, 20.78, 23.69, 27.02, 30.70, 34.89, 39.69, 45.20, 51.47, 58.70, 67.02],
        
        'LTC': [18.52, 20.72, 23.19, 26.00, 29.17, 32.72, 36.76, 41.27, 46.39, 52.19, 58.70, 65.04,
                68.93, 73.02, 77.39, 82.02, 86.92, 92.16, 97.72, 103.64, 109.94, 118.26, 132.37, 148.03,
                165.61, 185.22, 207.22, 231.86, 259.36, 290.21, 324.65, 363.16, 406.45, 454.76, 508.81,
                569.08, 636.53, 712.58, 797.24, 891.95, 998.14],
        
        'AAVE': [63.35, 70.10, 77.57, 85.89, 95.00, 105.22, 116.53, 125.90, 132.40, 139.27, 146.49, 154.13,
                 162.15, 170.59, 179.49, 188.86, 198.82, 209.20, 220.18, 231.82, 243.98, 256.89, 270.48,
                 284.83, 299.85, 319.94, 353.70, 391.18, 432.37, 477.95, 528.59, 584.30, 646.08, 714.28,
                 789.91, 873.64, 966.15, 1068.78, 1181.55, 1307.14, 1446.24],
    }
    
    print("🔬 ANALYZING POLYNOMIAL PATTERNS FOR ALL SYMBOLS")
    print("=" * 100)
    
    # Store results
    polynomial_coefficients = {}
    
    for symbol, prices in symbol_data.items():
        prices = np.array(prices)
        min_price = prices[0]
        max_price = prices[-1]
        
        # Calculate pure exponential prices
        pure_exp_prices = min_price * ((max_price / min_price) ** risks)
        
        # Calculate adjustment ratios
        ratios = prices / pure_exp_prices
        
        # Fit polynomial (degree 4 seems to work best)
        coeffs = np.polyfit(risks, ratios, 4)
        polynomial_coefficients[symbol] = coeffs
        
        # Calculate fitted values
        fitted_ratios = np.polyval(coeffs, risks)
        fitted_prices = pure_exp_prices * fitted_ratios
        
        # Calculate error metrics
        mse = np.mean((fitted_prices - prices) ** 2)
        rmse = np.sqrt(mse)
        mean_abs_error = np.mean(np.abs(fitted_prices - prices))
        mean_pct_error = np.mean(np.abs((fitted_prices - prices) / prices)) * 100
        
        print(f"\n{'='*60}")
        print(f"📊 {symbol}")
        print(f"{'='*60}")
        print(f"Min: ${min_price:.2f}, Max: ${max_price:.2f}, Growth: {max_price/min_price:.1f}x")
        print(f"\nPolynomial Coefficients (degree 4):")
        for i, coeff in enumerate(coeffs):
            print(f"  x^{4-i}: {coeff:>10.6f}")
        
        print(f"\nError Metrics:")
        print(f"  RMSE: ${rmse:.2f}")
        print(f"  Mean Absolute Error: ${mean_abs_error:.2f}")
        print(f"  Mean Percentage Error: {mean_pct_error:.2f}%")
        
        # Show adjustment factors at key points
        print(f"\nAdjustment Factors:")
        key_risks = [0.0, 0.25, 0.5, 0.75, 1.0]
        for risk in key_risks:
            adj = np.polyval(coeffs, risk)
            print(f"  Risk {risk:.2f}: {adj:.4f}x")
    
    # Generate Python code for implementation
    print("\n" + "=" * 100)
    print("📝 PYTHON IMPLEMENTATION CODE")
    print("=" * 100)
    
    print("\n# Polynomial coefficients for each symbol (degree 4)")
    print("POLYNOMIAL_COEFFICIENTS = {")
    for symbol, coeffs in polynomial_coefficients.items():
        coeffs_str = ", ".join([f"{c:.6f}" for c in coeffs])
        print(f"    '{symbol}': np.array([{coeffs_str}]),")
    print("}")
    
    print("\n# Symbol bounds from Cowen's data")
    print("COWEN_BOUNDS = {")
    for symbol, prices in symbol_data.items():
        print(f"    '{symbol}': {{'min': {prices[0]:.2f}, 'max': {prices[-1]:.2f}}},")
    print("}")
    
    # Test implementation
    print("\n" + "=" * 100)
    print("✅ VERIFICATION TEST")
    print("=" * 100)
    
    # Test a few symbols at specific risk levels
    test_cases = [
        ('ETH', 0.5, 2191.74),
        ('SOL', 0.4, 99.00),
        ('ADA', 0.6, 0.99),
        ('AAVE', 0.5, 243.98),
    ]
    
    print(f"\n{'Symbol':<8} {'Risk':<8} {'Expected':<12} {'Calculated':<12} {'Error':<10} {'Match':<8}")
    print("-" * 70)
    
    for symbol, risk, expected in test_cases:
        min_p = symbol_data[symbol][0]
        max_p = symbol_data[symbol][-1]
        coeffs = polynomial_coefficients[symbol]
        
        # Calculate with polynomial adjustment
        pure_price = min_p * ((max_p / min_p) ** risk)
        adjustment = np.polyval(coeffs, risk)
        calculated = pure_price * adjustment
        
        error = abs(calculated - expected)
        match = "✅" if error < 1 else "❌"
        
        print(f"{symbol:<8} {risk:<8.2f} ${expected:<11.2f} ${calculated:<11.2f} ${error:<9.2f} {match:<8}")
    
    return polynomial_coefficients

if __name__ == "__main__":
    coefficients = analyze_all_symbols()