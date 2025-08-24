#!/usr/bin/env python3
"""
Helper script to input Benjamin Cowen's exact data from Google Sheets
and reverse engineer the formulas
"""

import json
import math
import numpy as np
from scipy.optimize import minimize
import pandas as pd

# Known BTC values
BTC_MIN = 30000  # Risk 0
BTC_MAX = 299720  # Risk 1

def logarithmic_formula(price, min_price, max_price):
    """Benjamin Cowen's logarithmic risk formula"""
    if price <= min_price:
        return 0.0
    elif price >= max_price:
        return 1.0
    else:
        log_price = math.log(price)
        log_min = math.log(min_price)
        log_max = math.log(max_price)
        risk = (log_price - log_min) / (log_max - log_min)
        return max(0.0, min(1.0, risk))

def inverse_logarithmic(risk, min_price, max_price):
    """Calculate price from risk"""
    if risk <= 0:
        return min_price
    elif risk >= 1:
        return max_price
    else:
        log_min = math.log(min_price)
        log_max = math.log(max_price)
        log_price = log_min + risk * (log_max - log_min)
        return math.exp(log_price)

def input_risk_table_data():
    """
    Helper to input data from the Risk Values Google Sheet
    """
    print("\n" + "="*80)
    print("INPUT DATA FROM RISK VALUES SHEET")
    print("="*80)
    print("\nPlease input the exact values from:")
    print("https://docs.google.com/spreadsheets/d/1F-0_I2zy7MIQ_thTF2g4oaTZNiv1aV4x/")
    print("\nFormat: For each symbol, provide the price at each risk level")
    print("Risk levels go from 0.000 to 1.000 in 0.025 increments (41 values)")
    
    # For demonstration, I'll create a template you can fill
    # You need to replace these with actual values from the sheet
    
    data = {
        'BTC': {
            0.000: 30000,
            0.025: None,  # <-- Fill this from sheet
            0.050: None,
            0.075: None,
            0.100: None,
            0.125: None,
            0.150: None,
            0.175: None,
            0.200: None,
            0.225: None,
            0.250: None,
            0.275: None,
            0.300: None,
            0.325: None,
            0.350: None,
            0.375: None,
            0.400: None,
            0.425: None,
            0.450: None,
            0.475: None,
            0.500: None,
            0.525: None,
            0.550: None,
            0.575: None,
            0.600: None,
            0.625: None,
            0.650: None,
            0.675: None,
            0.700: None,
            0.725: None,
            0.750: None,
            0.775: None,
            0.800: None,
            0.825: None,
            0.850: None,
            0.875: None,
            0.900: None,
            0.925: None,
            0.950: None,
            0.975: None,
            1.000: 299720,
        },
        'ETH': {
            # Copy the structure and fill with ETH values
            0.000: None,  # ETH price at risk 0
            # ... fill all values
            1.000: None,  # ETH price at risk 1
        },
        'SOL': {
            # Copy the structure and fill with SOL values
            0.000: None,  # SOL price at risk 0
            # ... fill all values
            1.000: None,  # SOL price at risk 1
        },
        'ADA': {
            # Copy the structure and fill with ADA values
            0.000: None,  # ADA price at risk 0
            # ... fill all values
            1.000: None,  # ADA price at risk 1
        }
    }
    
    return data

def input_time_spent_data():
    """
    Helper to input data from the Time Spent Sheet
    """
    print("\n" + "="*80)
    print("INPUT DATA FROM TIME SPENT SHEET")
    print("="*80)
    print("\nPlease input the exact values from:")
    print("https://docs.google.com/spreadsheets/d/1fup2CUYxg7Tj3a2BvpoN3OcfGBoSe7EqHIxmp1RRjqg/")
    print("\nFormat: Days spent in each risk band (0.0-0.1, 0.1-0.2, etc.)")
    
    # Template - fill with actual values
    data = {
        'BTC': {
            '0.0-0.1': None,  # Days spent in 0-10% risk band
            '0.1-0.2': None,  # Days spent in 10-20% risk band
            '0.2-0.3': None,
            '0.3-0.4': None,
            '0.4-0.5': None,
            '0.5-0.6': None,
            '0.6-0.7': None,
            '0.7-0.8': None,
            '0.8-0.9': None,
            '0.9-1.0': None,
            'total_days': None,  # Total life age of BTC
        },
        'ETH': {
            # Same structure for ETH
        },
        'SOL': {
            # Same structure for SOL
        },
        'ADA': {
            # Same structure for ADA
        }
    }
    
    return data

def reverse_engineer_formula(symbol_data, btc_data):
    """
    Reverse engineer the exact formula for a symbol
    """
    # Get valid data points
    valid_points = [(risk, price) for risk, price in symbol_data.items() if price is not None]
    
    if len(valid_points) < 2:
        return None
    
    # Get min and max from data
    min_price = symbol_data.get(0.000)
    max_price = symbol_data.get(1.000)
    
    if not min_price or not max_price:
        return None
    
    # Test if logarithmic formula fits
    errors = []
    for risk, actual_price in valid_points:
        if actual_price is None:
            continue
        
        # Calculate expected price using logarithmic formula
        expected_price = inverse_logarithmic(risk, min_price, max_price)
        error = abs(expected_price - actual_price) / actual_price * 100
        errors.append(error)
    
    avg_error = sum(errors) / len(errors) if errors else 100
    
    # Calculate BTC ratios
    btc_min = btc_data.get(0.000, BTC_MIN)
    btc_max = btc_data.get(1.000, BTC_MAX)
    
    ratio_at_min = min_price / btc_min if btc_min else None
    ratio_at_max = max_price / btc_max if btc_max else None
    
    return {
        'min_price': min_price,
        'max_price': max_price,
        'btc_ratio_at_min': ratio_at_min,
        'btc_ratio_at_max': ratio_at_max,
        'formula_type': 'logarithmic',
        'average_error': avg_error,
        'is_valid': avg_error < 5  # Less than 5% error means formula is correct
    }

def analyze_all_symbols():
    """
    Main analysis function
    """
    print("\n" + "🎯"*30)
    print("BENJAMIN COWEN RISKMETRIC ANALYSIS")
    print("🎯"*30)
    
    # Step 1: Input risk table data
    risk_data = input_risk_table_data()
    
    # Step 2: Input time spent data
    time_data = input_time_spent_data()
    
    # Step 3: Reverse engineer formulas
    print("\n" + "="*60)
    print("REVERSE ENGINEERING FORMULAS")
    print("="*60)
    
    btc_data = risk_data.get('BTC', {})
    results = {}
    
    for symbol, data in risk_data.items():
        formula = reverse_engineer_formula(data, btc_data)
        if formula:
            results[symbol] = formula
            
            print(f"\n{symbol}:")
            print(f"  Min Price: ${formula['min_price']:,.2f}" if formula['min_price'] else "  Min Price: Not set")
            print(f"  Max Price: ${formula['max_price']:,.2f}" if formula['max_price'] else "  Max Price: Not set")
            if formula['btc_ratio_at_min']:
                print(f"  BTC Ratio at Min: {formula['btc_ratio_at_min']:.8f}")
            if formula['btc_ratio_at_max']:
                print(f"  BTC Ratio at Max: {formula['btc_ratio_at_max']:.8f}")
            print(f"  Formula Type: {formula['formula_type']}")
            print(f"  Average Error: {formula['average_error']:.2f}%")
            print(f"  Valid: {'✅' if formula['is_valid'] else '❌'}")
    
    # Step 4: Analyze time coefficients
    print("\n" + "="*60)
    print("TIME SPENT COEFFICIENTS")
    print("="*60)
    
    for symbol, bands in time_data.items():
        total_days = bands.get('total_days', 0)
        if not total_days:
            continue
        
        print(f"\n{symbol} (Total Days: {total_days}):")
        
        for band_range in ['0.0-0.1', '0.1-0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5',
                          '0.5-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']:
            days = bands.get(band_range, 0)
            if days is None:
                continue
            
            percentage = (days / total_days * 100) if total_days else 0
            
            # Calculate coefficient
            if percentage == 0:
                coeff = 1.6
            elif percentage < 1:
                coeff = 1.6
            elif percentage < 2.5:
                coeff = 1.55
            elif percentage < 5:
                coeff = 1.5
            elif percentage < 10:
                coeff = 1.4
            elif percentage < 15:
                coeff = 1.3
            elif percentage < 20:
                coeff = 1.2
            elif percentage < 30:
                coeff = 1.1
            else:
                coeff = 1.0
            
            print(f"  {band_range}: {days:>5} days ({percentage:>5.1f}%) - Coefficient: {coeff}")
    
    # Save results
    output = {
        'btc_reference': {
            'min': BTC_MIN,
            'max': BTC_MAX
        },
        'formulas': results,
        'methodology': {
            'formula': 'risk = (ln(price) - ln(min)) / (ln(max) - ln(min))',
            'inverse': 'price = exp(ln(min) + risk * (ln(max) - ln(min)))',
            'description': 'Logarithmic interpolation between min and max prices'
        },
        'instructions': {
            'step1': 'Fill in the actual values from Google Sheets',
            'step2': 'Run this script to reverse engineer formulas',
            'step3': 'Validate formulas have <5% error',
            'step4': 'Use formulas to generate risk for any price'
        }
    }
    
    with open('cowen_analysis_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\n✅ Results saved to: cowen_analysis_results.json")
    print("\n⚠️  IMPORTANT: You need to fill in the actual values from the Google Sheets!")
    print("Once you have the values, we can:")
    print("1. Find the exact formula Benjamin Cowen uses")
    print("2. Calculate Symbol/BTC ratios")
    print("3. Generate formulas for any new symbol")
    print("4. Build the complete autonomous agent")
    
    return results

if __name__ == "__main__":
    results = analyze_all_symbols()