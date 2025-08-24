#!/usr/bin/env python3
"""
Reverse Engineer Benjamin Cowen's EXACT RiskMetric Formula
Using actual data from Google Sheets to find the patterns
"""

import pandas as pd
import numpy as np
import math
from scipy.optimize import curve_fit, minimize
from datetime import datetime
import json

# Google Sheets URLs provided
RISK_VALUES_SHEET = "https://docs.google.com/spreadsheets/d/1F-0_I2zy7MIQ_thTF2g4oaTZNiv1aV4x/edit?gid=1709569802#gid=1709569802"
TIME_SPENT_SHEET = "https://docs.google.com/spreadsheets/d/1fup2CUYxg7Tj3a2BvpoN3OcfGBoSe7EqHIxmp1RRjqg/edit?gid=651319025#gid=651319025"

# Known facts from Benjamin Cowen
BTC_MIN = 30000  # Risk 0 for BTC
BTC_MAX = 299720  # Risk 1 for BTC

def extract_sheet_data_manually():
    """
    Since we can't directly access Google Sheets, I'll use the data 
    that should be extracted from the sheets you provided
    """
    
    # This is sample data structure - you need to input actual values from the sheets
    # Risk values from 0.000 to 1.000 in 0.025 increments (41 values)
    
    # From the first sheet (Risk values and prices)
    # Format: {symbol: [(risk, price), ...]}
    risk_data = {
        'BTC': [
            (0.000, 30000),
            (0.025, None),  # Fill from sheet
            (0.050, None),
            (0.075, None),
            (0.100, None),
            (0.125, None),
            (0.150, None),
            (0.175, None),
            (0.200, None),
            (0.225, None),
            (0.250, None),
            (0.275, None),
            (0.300, None),
            (0.325, None),
            (0.350, None),
            (0.375, None),
            (0.400, None),
            (0.425, None),
            (0.450, None),
            (0.475, None),
            (0.500, None),
            (0.525, None),
            (0.550, None),
            (0.575, None),
            (0.600, None),
            (0.625, None),
            (0.650, None),
            (0.675, None),
            (0.700, None),
            (0.725, None),
            (0.750, None),
            (0.775, None),
            (0.800, None),
            (0.825, None),
            (0.850, None),
            (0.875, None),
            (0.900, None),
            (0.925, None),
            (0.950, None),
            (0.975, None),
            (1.000, 299720),
        ],
        'ETH': [
            # Fill with actual values from sheet
        ],
        'SOL': [
            # Fill with actual values from sheet
        ],
        'ADA': [
            # Fill with actual values from sheet
        ]
    }
    
    # From the second sheet (Time spent in bands)
    # Format: {symbol: {band: days_spent}}
    time_spent_data = {
        'BTC': {
            '0.0-0.1': None,  # Fill from sheet
            '0.1-0.2': None,
            '0.2-0.3': None,
            '0.3-0.4': None,
            '0.4-0.5': None,
            '0.5-0.6': None,
            '0.6-0.7': None,
            '0.7-0.8': None,
            '0.8-0.9': None,
            '0.9-1.0': None,
        },
        # Add other symbols
    }
    
    return risk_data, time_spent_data

def find_logarithmic_parameters(known_points):
    """
    Find the exact logarithmic formula parameters
    Given: risk = (ln(price) - ln(min)) / (ln(max) - ln(min))
    """
    # Filter out None values
    valid_points = [(r, p) for r, p in known_points if p is not None]
    
    if len(valid_points) < 3:
        return None
    
    risks = np.array([r for r, p in valid_points])
    prices = np.array([p for r, p in valid_points])
    
    # We know it's logarithmic, so let's find the exact min and max
    # that make the formula work
    
    def objective(params):
        min_price, max_price = params
        if min_price <= 0 or max_price <= min_price:
            return 1e10
        
        errors = []
        for risk, price in valid_points:
            if price <= 0:
                continue
            
            # Calculate what risk should be with these parameters
            calculated_risk = (math.log(price) - math.log(min_price)) / (math.log(max_price) - math.log(min_price))
            error = (calculated_risk - risk) ** 2
            errors.append(error)
        
        return sum(errors)
    
    # Initial guess based on first and last points
    initial_guess = [valid_points[0][1], valid_points[-1][1]]
    
    # Optimize to find best min and max
    result = minimize(objective, initial_guess, bounds=[(1, 1e6), (1, 1e7)])
    
    min_price, max_price = result.x
    
    return {
        'min_price': min_price,
        'max_price': max_price,
        'error': result.fun
    }

def find_btc_ratio_pattern(btc_data, alt_data):
    """
    Find the Symbol/BTC ratio pattern for min and max values
    """
    # Get BTC min and max
    btc_min = BTC_MIN
    btc_max = BTC_MAX
    
    # Get altcoin min and max (risk 0 and risk 1)
    alt_points = [(r, p) for r, p in alt_data if p is not None]
    if not alt_points:
        return None
    
    alt_min = next((p for r, p in alt_points if r == 0.0), None)
    alt_max = next((p for r, p in alt_points if r == 1.0), None)
    
    if not alt_min or not alt_max:
        return None
    
    # Calculate ratios
    ratio_at_min = alt_min / btc_min  # Symbol/BTC ratio at risk 0
    ratio_at_max = alt_max / btc_max  # Symbol/BTC ratio at risk 1
    
    return {
        'ratio_at_risk_0': ratio_at_min,
        'ratio_at_risk_1': ratio_at_max,
        'ratio_change': (ratio_at_max / ratio_at_min - 1) * 100  # Percentage change
    }

def reverse_engineer_polynomial(risk_values, prices):
    """
    Find polynomial that maps risk to price
    """
    # Remove None values
    valid_indices = [i for i, p in enumerate(prices) if p is not None]
    valid_risks = [risk_values[i] for i in valid_indices]
    valid_prices = [prices[i] for i in valid_indices]
    
    if len(valid_risks) < 3:
        return None
    
    # Try different polynomial degrees
    best_degree = None
    best_r2 = -1
    best_coeffs = None
    
    for degree in range(2, min(8, len(valid_risks))):
        try:
            # Fit polynomial
            coeffs = np.polyfit(valid_risks, valid_prices, degree)
            poly = np.poly1d(coeffs)
            
            # Calculate R-squared
            predicted = [poly(r) for r in valid_risks]
            ss_res = sum((p - pred) ** 2 for p, pred in zip(valid_prices, predicted))
            mean_price = sum(valid_prices) / len(valid_prices)
            ss_tot = sum((p - mean_price) ** 2 for p in valid_prices)
            
            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            if r2 > best_r2:
                best_r2 = r2
                best_degree = degree
                best_coeffs = coeffs.tolist()
        except:
            continue
    
    return {
        'degree': best_degree,
        'coefficients': best_coeffs,
        'r_squared': best_r2
    }

def calculate_time_coefficients(time_spent_dict, total_days):
    """
    Calculate rarity coefficients based on time spent in each band
    """
    coefficients = {}
    
    for band, days in time_spent_dict.items():
        if days is None:
            continue
        
        percentage = (days / total_days * 100) if total_days > 0 else 0
        
        # Rarity-based coefficient (1.0 to 1.6)
        if percentage == 0:
            coeff = 1.6  # Never visited - ultra rare
        elif percentage < 1:
            coeff = 1.6  # Extremely rare
        elif percentage < 2.5:
            coeff = 1.55  # Very rare
        elif percentage < 5:
            coeff = 1.5  # Rare
        elif percentage < 10:
            coeff = 1.4  # Uncommon
        elif percentage < 15:
            coeff = 1.3  # Somewhat uncommon
        elif percentage < 20:
            coeff = 1.2  # Below average
        elif percentage < 30:
            coeff = 1.1  # Near average
        else:
            coeff = 1.0  # Common
        
        coefficients[band] = {
            'days': days,
            'percentage': percentage,
            'coefficient': coeff
        }
    
    return coefficients

def main():
    print("="*80)
    print("BENJAMIN COWEN RISKMETRIC REVERSE ENGINEERING")
    print("="*80)
    
    print(f"\nKnown Facts:")
    print(f"- BTC Min (Risk 0): ${BTC_MIN:,}")
    print(f"- BTC Max (Risk 1): ${BTC_MAX:,}")
    print(f"- Risk increments: 0.025 (41 total values)")
    print(f"- Google Sheets provided for exact values")
    
    # Step 1: Get data from sheets (manual input needed)
    print("\n" + "="*60)
    print("STEP 1: Extract Data from Google Sheets")
    print("="*60)
    print("\n⚠️  Please manually input the values from the Google Sheets:")
    print(f"1. Risk Values Sheet: {RISK_VALUES_SHEET}")
    print(f"2. Time Spent Sheet: {TIME_SPENT_SHEET}")
    
    risk_data, time_spent_data = extract_sheet_data_manually()
    
    # Step 2: Find logarithmic parameters for each symbol
    print("\n" + "="*60)
    print("STEP 2: Find Logarithmic Parameters")
    print("="*60)
    
    log_params = {}
    for symbol, points in risk_data.items():
        params = find_logarithmic_parameters(points)
        if params:
            log_params[symbol] = params
            print(f"\n{symbol}:")
            print(f"  Min Price: ${params['min_price']:,.2f}")
            print(f"  Max Price: ${params['max_price']:,.2f}")
            print(f"  Fit Error: {params['error']:.6f}")
    
    # Step 3: Find BTC ratio patterns
    print("\n" + "="*60)
    print("STEP 3: Find Symbol/BTC Ratio Patterns")
    print("="*60)
    
    if 'BTC' in risk_data:
        for symbol, points in risk_data.items():
            if symbol == 'BTC':
                continue
            
            ratio_pattern = find_btc_ratio_pattern(risk_data['BTC'], points)
            if ratio_pattern:
                print(f"\n{symbol}:")
                print(f"  Ratio at Risk 0: {ratio_pattern['ratio_at_risk_0']:.8f}")
                print(f"  Ratio at Risk 1: {ratio_pattern['ratio_at_risk_1']:.8f}")
                print(f"  Ratio Change: {ratio_pattern['ratio_change']:.1f}%")
    
    # Step 4: Find polynomial approximations
    print("\n" + "="*60)
    print("STEP 4: Find Polynomial Approximations")
    print("="*60)
    
    polynomials = {}
    risk_values = [i * 0.025 for i in range(41)]
    
    for symbol, points in risk_data.items():
        prices = [p for r, p in points]
        poly = reverse_engineer_polynomial(risk_values, prices)
        if poly:
            polynomials[symbol] = poly
            print(f"\n{symbol}:")
            print(f"  Polynomial Degree: {poly['degree']}")
            print(f"  R-squared: {poly['r_squared']:.6f}")
    
    # Step 5: Calculate time-spent coefficients
    print("\n" + "="*60)
    print("STEP 5: Calculate Time-Spent Coefficients")
    print("="*60)
    
    for symbol, bands in time_spent_data.items():
        total_days = sum(d for d in bands.values() if d is not None)
        coeffs = calculate_time_coefficients(bands, total_days)
        
        print(f"\n{symbol} (Total Days: {total_days}):")
        for band, data in sorted(coeffs.items()):
            print(f"  {band}: {data['days']} days ({data['percentage']:.1f}%) - Coeff: {data['coefficient']}")
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'btc_min': BTC_MIN,
        'btc_max': BTC_MAX,
        'logarithmic_parameters': log_params,
        'polynomials': polynomials,
        'methodology': {
            'formula': 'risk = (ln(price) - ln(min)) / (ln(max) - ln(min))',
            'risk_zones': {
                '0.00-0.25': 'BUY ZONE (Bear Market)',
                '0.25-0.40': 'EARLY BULL',
                '0.40-0.60': 'NEUTRAL',
                '0.60-0.75': 'LATE BULL',
                '0.75-1.00': 'SELL ZONE (Bull Market Top)'
            },
            'scoring': {
                'base_score_ranges': {
                    'BUY_ZONE': '70-100 points',
                    'EARLY_BULL': '50-70 points',
                    'NEUTRAL': '30-50 points',
                    'LATE_BULL': '50-70 points',
                    'SELL_ZONE': '70-100 points'
                },
                'coefficient': '1.0-1.6 based on rarity',
                'final_score': 'base_score * coefficient'
            }
        }
    }
    
    with open('cowen_methodology_reverse_engineered.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "="*80)
    print("RESULTS SAVED")
    print("="*80)
    print("\n✅ Results saved to: cowen_methodology_reverse_engineered.json")
    print("\n📊 Next Steps:")
    print("1. Fill in the actual values from Google Sheets")
    print("2. Run the script again with complete data")
    print("3. Validate the formulas against known values")
    print("4. Implement the complete agent system")

if __name__ == "__main__":
    main()