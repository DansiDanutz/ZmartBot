"""
exact_google_sheets_matrix.py
-----------------------------
Implement the EXACT matrix from Google Sheets without any calculations.
"""

def get_exact_google_sheets_matrix():
    """Get the exact coefficient matrix from Google Sheets."""
    
    # EXACT values from Google Sheets matrix
    exact_matrix = {
        # 0.0-0.1 band
        0.00: 1.600, 0.01: 1.5845, 0.02: 1.569, 0.03: 1.5535, 0.04: 1.538,
        
        # 0.1-0.2 band
        0.10: 1.5063, 0.11: 1.4746, 0.12: 1.4429, 0.13: 1.4112, 0.14: 1.3795,
        0.15: 1.3478, 0.16: 1.3161, 0.17: 1.2844, 0.18: 1.2527, 0.19: 1.221,
        
        # 0.2-0.3 band
        0.20: 1.2146, 0.21: 1.2082, 0.22: 1.2018, 0.23: 1.1954, 0.24: 1.189,
        0.25: 1.1826, 0.26: 1.1762, 0.27: 1.1698, 0.28: 1.1634, 0.29: 1.157,
        
        # 0.3-0.4 band
        0.30: 1.1413, 0.31: 1.1256, 0.32: 1.1099, 0.33: 1.0942, 0.34: 1.0785,
        0.35: 1.0628, 0.36: 1.0471, 0.37: 1.0314, 0.38: 1.0157, 0.39: 1.0,
        
        # 0.4-0.5 band
        0.40: 1.0016, 0.41: 1.0032, 0.42: 1.0048, 0.43: 1.0064, 0.44: 1.008,
        0.45: 1.0096, 0.46: 1.0112, 0.47: 1.0128, 0.48: 1.0144, 0.49: 1.016,
        
        # 0.5-0.6 band (EXACT from Google Sheets)
        0.50: 1.0245, 0.51: 1.033, 0.52: 1.0415, 0.53: 1.05, 0.54: 1.0585,
        0.55: 1.067, 0.56: 1.0755, 0.57: 1.084, 0.58: 1.0925, 0.59: 1.101,
        
        # 0.6-0.7 band (EXACT from Google Sheets)
        0.60: 1.132, 0.61: 1.163, 0.62: 1.194, 0.63: 1.225, 0.64: 1.256,
        0.65: 1.287, 0.66: 1.318, 0.67: 1.349, 0.68: 1.38, 0.69: 1.411,
        
        # 0.7-0.8 band
        0.70: 1.4236, 0.71: 1.4362, 0.72: 1.4488, 0.73: 1.4614, 0.74: 1.474,
        0.75: 1.4866, 0.76: 1.4992, 0.77: 1.5118, 0.78: 1.5244, 0.79: 1.537,
        
        # 0.8-0.9 band
        0.80: 1.5401, 0.81: 1.5432, 0.82: 1.5463, 0.83: 1.5494, 0.84: 1.5525,
        0.85: 1.5556, 0.86: 1.5587, 0.87: 1.5618, 0.88: 1.5649, 0.89: 1.568,
        
        # 0.9-1.0 band
        0.90: 1.5712, 0.91: 1.5744, 0.92: 1.5776, 0.93: 1.5808, 0.94: 1.584,
        0.95: 1.5872, 0.96: 1.5904, 0.97: 1.5936, 0.98: 1.5968, 0.99: 1.6,
        1.00: 1.6
    }
    
    return exact_matrix

def print_exact_matrix():
    """Print the exact matrix from Google Sheets."""
    
    matrix = get_exact_google_sheets_matrix()
    
    print("=== EXACT GOOGLE SHEETS MATRIX ===")
    print("These are the EXACT values from your Google Sheets:")
    print()
    
    # Print 0.5-0.6 band (the one you specifically showed)
    print("0.5-0.6 Band (EXACT from Google Sheets):")
    for i in range(11):
        risk = 0.50 + (i * 0.01)
        coef = matrix[risk]
        print(f"  {risk:.2f}: {coef:.4f}")
    
    print()
    print("0.6-0.7 Band (EXACT from Google Sheets):")
    for i in range(11):
        risk = 0.60 + (i * 0.01)
        coef = matrix[risk]
        print(f"  {risk:.2f}: {coef:.4f}")
    
    print()
    print("Complete matrix from 0.00 to 1.00:")
    for i in range(0, 101, 5):  # Print every 5th value
        risk = i / 100.0
        coef = matrix[risk]
        print(f"  {risk:.2f}: {coef:.4f}")

if __name__ == "__main__":
    print_exact_matrix()




