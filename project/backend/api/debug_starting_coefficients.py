"""
debug_starting_coefficients.py
------------------------------
Debug script to understand the correct starting coefficients from Google Sheets.
"""

def debug_starting_coefficients():
    """Debug the starting coefficient calculation."""
    
    # From Google Sheets - band coefficients (midpoints)
    band_coefficients = {
        "0.0-0.1": 1.538,
        "0.1-0.2": 1.221,
        "0.2-0.3": 1.157,
        "0.3-0.4": 1.000,
        "0.4-0.5": 1.016,
        "0.5-0.6": 1.101,
        "0.6-0.7": 1.411,
        "0.7-0.8": 1.537,
        "0.8-0.9": 1.568,
        "0.9-1.0": 1.600
    }
    
    print("=== DEBUG STARTING COEFFICIENTS ===")
    print()
    print("Band | Midpoint Coef | Previous Coef | Difference | Increment/0.01 | Starting Coef")
    print("-" * 80)
    
    prev_coef = None
    starting_coefficients = {}
    
    for i in range(10):
        band_key = f"{i*0.1:.1f}-{(i+1)*0.1:.1f}"
        current_coef = band_coefficients[band_key]
        
        if prev_coef is not None:
            difference = current_coef - prev_coef
            increment_per_001 = difference / 10
            starting_coef = prev_coef + (5 * increment_per_001)
            print(f"{band_key} | {current_coef:12.3f} | {prev_coef:12.3f} | {difference:10.3f} | {increment_per_001:14.4f} | {starting_coef:13.4f}")
        else:
            starting_coef = current_coef
            print(f"{band_key} | {current_coef:12.3f} | {'START':>12} | {'START':>10} | {'START':>14} | {starting_coef:13.4f}")
        
        starting_coefficients[band_key] = starting_coef
        prev_coef = current_coef
    
    print()
    print("=== COMPARISON WITH GOOGLE SHEETS ===")
    print()
    print("0.5-0.6 Band:")
    print("Google Sheets: 0.50 = 1.0245, 0.55 = 1.0670, 0.60 = 1.1095")
    print("My calculation: 0.50 = 1.0585, 0.55 = 1.1010, 0.60 = 1.1435")
    print()
    print("The issue is that I'm calculating starting coefficients wrong!")
    print("I need to find the correct starting values from the Google Sheets.")

if __name__ == "__main__":
    debug_starting_coefficients()

