"""
complete_coefficient_matrix.py
------------------------------
Generate complete coefficient matrix from 0 to 1 with 0.01 increments.
"""

from dynamic_coefficient_matrix import calculate_dynamic_band_coefficients

def generate_complete_matrix():
    """Generate complete coefficient matrix from 0 to 1 with 0.01 increments."""
    
    # Example risk bands data
    risk_bands_data = {
        "0.0-0.1": {"days": 134, "percentage": 2.45},
        "0.1-0.2": {"days": 721, "percentage": 13.17},
        "0.2-0.3": {"days": 840, "percentage": 15.35},
        "0.3-0.4": {"days": 1131, "percentage": 20.67},
        "0.4-0.5": {"days": 1102, "percentage": 20.14},
        "0.5-0.6": {"days": 943, "percentage": 17.23},
        "0.6-0.7": {"days": 369, "percentage": 6.74},
        "0.7-0.8": {"days": 135, "percentage": 2.47},
        "0.8-0.9": {"days": 79, "percentage": 1.44},
        "0.9-1.0": {"days": 19, "percentage": 0.35}
    }
    
    # Calculate band coefficients
    band_coefficients = calculate_dynamic_band_coefficients(risk_bands_data)
    
    print("=== COMPLETE COEFFICIENT MATRIX (0 to 1 with 0.01 increments) ===")
    print()
    print("Risk | Coefficient | Band | Band Midpoint | Increment")
    print("-" * 65)
    
    complete_matrix = {}
    prev_coefficient = None
    
    for i in range(101):  # 0.00 to 1.00 (101 values)
        risk = i / 100.0
        
        # Determine which band this risk belongs to
        band_index = int(risk * 10)
        if band_index >= 10:  # Handle 1.0 case
            band_index = 9
        band_start = band_index * 0.1
        band_end = band_start + 0.1
        band = f"{band_start:.1f}-{band_end:.1f}"
        
        # Calculate coefficient using linear interpolation
        band_midpoint = band_start + 0.05
        band_coef = band_coefficients[band]
        
        # Calculate increment based on previous band
        if band_index > 0:
            prev_band = f"{(band_index-1)*0.1:.1f}-{band_index*0.1:.1f}"
            prev_band_coef = band_coefficients[prev_band]
            
            # Calculate increment per 0.01 for this band
            increment_per_001 = (band_coef - prev_band_coef) / 10
            
            # Calculate coefficient based on distance from band start
            distance_from_start = (risk - band_start) * 100  # in 0.01 units
            coefficient = prev_band_coef + (distance_from_start * increment_per_001)
        else:
            # For the first band (0.0-0.1), use the band coefficient
            coefficient = band_coef
        
        complete_matrix[risk] = coefficient
        
        # Calculate increment
        increment = ""
        if prev_coefficient is not None:
            increment = f"{coefficient - prev_coefficient:+.3f}"
        
        # Print every 5th value to keep output manageable
        if i % 5 == 0:
            print(f"{risk:.2f} | {coefficient:10.3f} | {band:>8} | {band_start + 0.05:12.2f} | {increment:>8}")
        
        prev_coefficient = coefficient
    
    print()
    print("=== BAND COEFFICIENTS (Midpoints) ===")
    for band, coef in band_coefficients.items():
        print(f"{band}: {coef:.3f}")
    
    print()
    print("=== INCREMENTS BETWEEN BANDS ===")
    for i in range(9):
        current_band = f"{i*0.1:.1f}-{(i+1)*0.1:.1f}"
        next_band = f"{(i+1)*0.1:.1f}-{(i+2)*0.1:.1f}"
        
        current_coef = band_coefficients[current_band]
        next_coef = band_coefficients[next_band]
        difference = next_coef - current_coef
        increment_per_001 = difference / 10
        
        print(f"{current_band} → {next_band}: {increment_per_001:+.3f} per 0.01")
    
    print()
    print("=== SPECIFIC TEST VALUES ===")
    test_values = [0.45, 0.46, 0.47, 0.48, 0.49, 0.50, 0.51, 0.52, 0.53, 0.54, 0.55]
    print("0.4-0.5 to 0.5-0.6 transition:")
    for risk in test_values:
        coef = complete_matrix[risk]
        print(f"Risk {risk:.2f}: {coef:.3f}")
    
    print()
    print("=== 0.5-0.6 BAND DETAILED ===")
    test_values_56 = [0.55, 0.56, 0.57, 0.58, 0.59, 0.60]
    for risk in test_values_56:
        coef = complete_matrix[risk]
        print(f"Risk {risk:.2f}: {coef:.3f}")
    
    print()
    print("=== 0.4-0.5 BAND DETAILED ===")
    test_values_45 = [0.45, 0.46, 0.47, 0.48, 0.49, 0.50]
    for risk in test_values_45:
        coef = complete_matrix[risk]
        print(f"Risk {risk:.2f}: {coef:.3f}")
    
    return complete_matrix

if __name__ == "__main__":
    matrix = generate_complete_matrix()
