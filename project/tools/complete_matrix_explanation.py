"""
complete_matrix_explanation.py
------------------------------
Generate and explain the complete coefficient matrix from 0 to 1 with 0.01 increments.
"""

def generate_complete_matrix():
    """Generate complete coefficient matrix with detailed explanation."""
    
    # Band coefficients (midpoints) from current data
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
    
    # Starting coefficients from Google Sheets matrix
    starting_coefficients = {
        "0.0-0.1": 1.600,   # 0.00-0.01
        "0.1-0.2": 1.5063,  # 0.10-0.11
        "0.2-0.3": 1.2146,  # 0.20-0.21
        "0.3-0.4": 1.1413,  # 0.30-0.31
        "0.4-0.5": 1.0016,  # 0.40-0.41
        "0.5-0.6": 1.0245,  # 0.50-0.51
        "0.6-0.7": 1.132,   # 0.60-0.61
        "0.7-0.8": 1.4236,  # 0.70-0.71
        "0.8-0.9": 1.5401,  # 0.80-0.81
        "0.9-1.0": 1.5712   # 0.90-0.91
    }
    
    # Calculate increments between bands
    band_increments = {}
    prev_coef = None
    for i in range(10):
        band_key = f"{i*0.1:.1f}-{(i+1)*0.1:.1f}"
        current_coef = band_coefficients[band_key]
        
        if prev_coef is not None:
            difference = current_coef - prev_coef
            increment_per_001 = difference / 10
            band_increments[band_key] = round(increment_per_001, 4)
        else:
            band_increments[band_key] = 0.0
        
        prev_coef = current_coef
    
    print("=== COMPLETE COEFFICIENT MATRIX EXPLANATION ===")
    print()
    print("STEP 1: BAND COEFFICIENTS (Midpoints)")
    print("These are calculated based on rarity from current day's data:")
    for band, coef in band_coefficients.items():
        print(f"  {band}: {coef:.3f}")
    
    print()
    print("STEP 2: STARTING COEFFICIENTS")
    print("These are the exact values from Google Sheets matrix:")
    for band, start_coef in starting_coefficients.items():
        print(f"  {band}: {start_coef:.4f}")
    
    print()
    print("STEP 3: INCREMENTS BETWEEN BANDS")
    print("Formula: (Current Band Coef - Previous Band Coef) ÷ 10")
    prev_coef = None
    for i in range(10):
        band_key = f"{i*0.1:.1f}-{(i+1)*0.1:.1f}"
        current_coef = band_coefficients[band_key]
        
        if prev_coef is not None:
            difference = current_coef - prev_coef
            increment = difference / 10
            direction = "ADD" if increment > 0 else "SUBTRACT" if increment < 0 else "NO CHANGE"
            print(f"  {band_key}: {increment:+.4f} per 0.01 ({direction})")
        else:
            print(f"  {band_key}: {0.0000:+.4f} per 0.01 (FIRST BAND)")
        
        prev_coef = current_coef
    
    print()
    print("STEP 4: COMPLETE MATRIX (0 to 1 with 0.01 increments)")
    print("Formula: Starting Coef + (Position × Increment)")
    print()
    print("Risk | Coefficient | Band | Starting Coef | Increment | Calculation")
    print("-" * 80)
    
    complete_matrix = {}
    
    for i in range(101):  # 0.00 to 1.00 (101 values)
        risk = i / 100.0
        
        # Determine which band this risk belongs to
        band_index = int(risk * 10)
        if band_index >= 10:
            band_index = 9
        
        band_start = band_index * 0.1
        band_end = band_start + 0.1
        band = f"{band_start:.1f}-{band_end:.1f}"
        
        # Get starting coefficient and increment for this band
        start_coef = starting_coefficients[band]
        increment = band_increments[band]
        
        # Calculate position within the band (0-10)
        position_in_band = int((risk - band_start) * 100)
        
        # Calculate coefficient
        coefficient = start_coef + (position_in_band * increment)
        complete_matrix[risk] = coefficient
        
        # Show calculation for key points
        if i % 10 == 0 or (i % 5 == 0 and i < 50) or (i % 5 == 0 and i > 50):
            calculation = f"{start_coef:.4f} + ({position_in_band} × {increment:+.4f})"
            print(f"{risk:.2f} | {coefficient:10.4f} | {band:>8} | {start_coef:12.4f} | {increment:9.4f} | {calculation}")
    
    print()
    print("STEP 5: KEY EXAMPLES EXPLAINED")
    print()
    print("Example 1: 0.5-0.6 Band")
    print("  Starting coefficient: 1.0245")
    print("  Increment per 0.01: +0.0085")
    print("  Values:")
    for i in range(11):
        risk = 0.50 + (i * 0.01)
        coef = 1.0245 + (i * 0.0085)
        print(f"    {risk:.2f}: {coef:.4f}")
    
    print()
    print("Example 2: 0.6-0.7 Band")
    print("  Starting coefficient: 1.132")
    print("  Increment per 0.01: +0.031")
    print("  Values:")
    for i in range(11):
        risk = 0.60 + (i * 0.01)
        coef = 1.132 + (i * 0.031)
        print(f"    {risk:.2f}: {coef:.4f}")
    
    return complete_matrix

if __name__ == "__main__":
    matrix = generate_complete_matrix()




