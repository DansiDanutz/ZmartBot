"""
correct_coefficient_matrix.py
-----------------------------
Implement the correct coefficient matrix based on Google Sheets methodology.
"""

def calculate_correct_coefficients():
    """Calculate coefficients using the correct methodology from Google Sheets."""
    
    # Band coefficients (from Google Sheets)
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
    
    # Calculate increments between bands (from Google Sheets)
    band_increments = {}
    prev_coef = None
    for band, coef in band_coefficients.items():
        if prev_coef is not None:
            difference = coef - prev_coef
            increment_per_001 = difference / 10
            band_increments[band] = increment_per_001
        prev_coef = coef
    
    print("=== CORRECT COEFFICIENT MATRIX (Based on Google Sheets) ===")
    print()
    print("Band | Coefficient | Difference | Increment/0.01")
    print("-" * 50)
    
    prev_coef = None
    for band, coef in band_coefficients.items():
        if prev_coef is not None:
            diff = coef - prev_coef
            inc = diff / 10
            print(f"{band} | {coef:10.3f} | {diff:10.3f} | {inc:14.4f}")
        else:
            print(f"{band} | {coef:10.3f} | {'START':>10} | {'START':>14}")
        prev_coef = coef
    
    print()
    print("=== DETAILED 0.5-0.6 BAND (From Google Sheets) ===")
    print("Risk | Coefficient | Increment")
    print("-" * 30)
    
    # 0.5-0.6 band: starts at 1.0245, increment 0.0085
    start_coef = 1.0245
    increment = 0.0085
    
    for i in range(11):  # 0.50 to 0.60
        risk = 0.50 + (i * 0.01)
        coef = start_coef + (i * increment)
        if i == 0:
            print(f"{risk:.2f} | {coef:10.4f} | START")
        else:
            print(f"{risk:.2f} | {coef:10.4f} | +{increment:.4f}")
    
    print()
    print("=== DETAILED 0.6-0.7 BAND (From Google Sheets) ===")
    print("Risk | Coefficient | Increment")
    print("-" * 30)
    
    # 0.6-0.7 band: starts at 1.132, increment 0.031
    start_coef = 1.132
    increment = 0.031
    
    for i in range(11):  # 0.60 to 0.70
        risk = 0.60 + (i * 0.01)
        coef = start_coef + (i * increment)
        if i == 0:
            print(f"{risk:.2f} | {coef:10.4f} | START")
        else:
            print(f"{risk:.2f} | {coef:10.4f} | +{increment:.4f}")
    
    print()
    print("=== COMPLETE MATRIX (0.50 to 0.70) ===")
    print("Risk | Coefficient | Band")
    print("-" * 30)
    
    # Generate complete matrix from 0.50 to 0.70
    complete_matrix = {}
    
    # 0.5-0.6 band
    start_coef = 1.0245
    increment = 0.0085
    for i in range(11):
        risk = 0.50 + (i * 0.01)
        coef = start_coef + (i * increment)
        complete_matrix[risk] = coef
        print(f"{risk:.2f} | {coef:10.4f} | 0.5-0.6")
    
    # 0.6-0.7 band
    start_coef = 1.132
    increment = 0.031
    for i in range(11):
        risk = 0.60 + (i * 0.01)
        coef = start_coef + (i * increment)
        complete_matrix[risk] = coef
        print(f"{risk:.2f} | {coef:10.4f} | 0.6-0.7")
    
    return complete_matrix

if __name__ == "__main__":
    matrix = calculate_correct_coefficients()

