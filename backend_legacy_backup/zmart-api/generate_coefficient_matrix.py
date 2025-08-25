"""
generate_coefficient_matrix.py
------------------------------
Generate complete coefficient matrix from 0 to 1 for all bands.

This matrix shows the exact coefficient values for every risk level,
demonstrating the band midpoint methodology and linear interpolation.
"""

from risk_coefficient import get_coefficient

def generate_coefficient_matrix():
    """Generate complete coefficient matrix from 0 to 1."""
    
    print("=== COMPLETE COEFFICIENT MATRIX (0.00 to 1.00) ===")
    print()
    print("Risk Value | Coefficient | Band | Description")
    print("-" * 60)
    
    # Generate matrix for every 0.01 increment from 0.00 to 1.00
    for i in range(0, 101):  # 0 to 100
        risk_value = i / 100.0
        
        # Determine band
        band_start = (i // 10) * 0.1
        band_end = band_start + 0.1
        current_band = f"{band_start:.1f}-{band_end:.1f}"
        
        # Calculate coefficient (assuming second day in same band)
        coefficient = get_coefficient(risk_value, current_band, "2025-08-12")
        
        # Add description
        if i % 10 == 5:  # Middle of each band
            description = f"MIDDLE of {current_band} band"
        elif i % 10 == 0:  # Start of band
            description = f"START of {current_band} band"
        elif i % 10 == 9:  # End of band
            description = f"END of {current_band} band"
        else:
            description = f"Within {current_band} band"
        
        print(f"{risk_value:8.2f} | {coefficient:10.3f} | {current_band:8} | {description}")
        
        # Add separator between bands
        if i % 10 == 9 and i < 99:
            print("-" * 60)
    
    print()
    print("=== BAND MIDPOINT SUMMARY ===")
    print()
    
    # Show band midpoints
    band_midpoints = [
        (0.05, "0.0-0.1", 1.538),
        (0.15, "0.1-0.2", 1.221),
        (0.25, "0.2-0.3", 1.157),
        (0.35, "0.3-0.4", 1.000),
        (0.45, "0.4-0.5", 1.016),
        (0.55, "0.5-0.6", 1.101),
        (0.65, "0.6-0.7", 1.411),
        (0.75, "0.7-0.8", 1.537),
        (0.85, "0.8-0.9", 1.568),
        (0.95, "0.9-1.0", 1.600)
    ]
    
    print("Band Midpoints (Fixed Daily Values):")
    for risk, band, expected in band_midpoints:
        coef = get_coefficient(risk, band, "2025-08-12")
        print(f"Risk {risk:.2f} ({band}): {coef:.3f} (expected: {expected:.3f}) {'✅' if abs(coef - expected) < 0.001 else '❌'}")
    
    print()
    print("=== LINEAR INTERPOLATION EXAMPLES ===")
    print()
    
    # Show specific examples of linear interpolation
    examples = [
        (0.56, "0.5-0.6", "0.55 (1.101) + 0.01 increment"),
        (0.57, "0.5-0.6", "0.55 (1.101) + 0.02 increment"),
        (0.58, "0.5-0.6", "0.55 (1.101) + 0.03 increment"),
        (0.59, "0.5-0.6", "0.55 (1.101) + 0.04 increment"),
        (0.60, "0.5-0.6", "0.55 (1.101) + 0.05 increment"),
        (0.61, "0.6-0.7", "0.65 (1.411) - 0.04 increment"),
        (0.62, "0.6-0.7", "0.65 (1.411) - 0.03 increment"),
        (0.63, "0.6-0.7", "0.65 (1.411) - 0.02 increment"),
        (0.64, "0.6-0.7", "0.65 (1.411) - 0.01 increment"),
    ]
    
    print("Linear Interpolation Examples:")
    for risk, band, description in examples:
        coef = get_coefficient(risk, band, "2025-08-12")
        print(f"Risk {risk:.2f} ({band}): {coef:.3f} - {description}")

def generate_compact_matrix():
    """Generate compact coefficient matrix showing key points."""
    
    print("=== COMPACT COEFFICIENT MATRIX ===")
    print()
    print("Risk | Coefficient | Band | Type")
    print("-" * 40)
    
    # Show key points: start, middle, end of each band
    for band_num in range(10):
        band_start = band_num * 0.1
        band_end = band_start + 0.1
        band = f"{band_start:.1f}-{band_end:.1f}"
        
        # Start of band
        start_risk = band_start
        start_coef = get_coefficient(start_risk, band, "2025-08-12")
        print(f"{start_risk:.2f} | {start_coef:10.3f} | {band:8} | START")
        
        # Middle of band
        middle_risk = band_start + 0.05
        middle_coef = get_coefficient(middle_risk, band, "2025-08-12")
        print(f"{middle_risk:.2f} | {middle_coef:10.3f} | {band:8} | MIDDLE")
        
        # End of band
        end_risk = band_end
        end_coef = get_coefficient(end_risk, band, "2025-08-12")
        print(f"{end_risk:.2f} | {end_coef:10.3f} | {band:8} | END")
        
        if band_num < 9:  # Don't print separator after last band
            print("-" * 40)

if __name__ == "__main__":
    print("Choose matrix type:")
    print("1. Complete matrix (0.00 to 1.00)")
    print("2. Compact matrix (key points only)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        generate_coefficient_matrix()
    elif choice == "2":
        generate_compact_matrix()
    else:
        print("Invalid choice. Generating compact matrix...")
        generate_compact_matrix()
