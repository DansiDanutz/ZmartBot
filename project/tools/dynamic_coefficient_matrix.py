"""
dynamic_coefficient_matrix.py
------------------------------
Dynamic coefficient matrix generator that updates daily based on current band percentages.

Key Features:
- Generates coefficient matrix once per day
- Focuses on current band and neighboring bands only
- Updates automatically when band percentages change
- Uses current day's band data for accurate calculations
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any

def calculate_dynamic_band_coefficients(risk_bands_data: Dict[str, Dict]) -> Dict[str, float]:
    """
    Calculate dynamic band coefficients based on current day's risk bands data.
    
    Args:
        risk_bands_data: Current day's risk bands data with days and percentages
    
    Returns:
        Dictionary of band coefficients calculated from current data
    """
    
    # Extract days from risk bands data
    days = []
    for i in range(10):
        band_key = f"{i*0.1:.1f}-{(i+1)*0.1:.1f}"
        if band_key in risk_bands_data:
            days.append(risk_bands_data[band_key].get('days', 0))
        else:
            days.append(0)
    
    # Calculate percentages
    total_days = sum(days)
    if total_days == 0:
        return {}
    
    percentages = [d / total_days for d in days]
    
    # Calculate coefficients based on rarity (inverse of percentage)
    # Most common (highest percentage) gets lowest coefficient (1.0)
    # Rarest (lowest percentage) gets highest coefficient (1.6)
    max_percentage = max(percentages)
    min_percentage = min(percentages)
    
    coefficients = {}
    for i, percentage in enumerate(percentages):
        band_key = f"{i*0.1:.1f}-{(i+1)*0.1:.1f}"
        if max_percentage == min_percentage:
            # All bands have same percentage
            coefficient = 1.3  # Midpoint
        else:
            # Linear mapping from percentage to coefficient
            rarity_ratio = (max_percentage - percentage) / (max_percentage - min_percentage)
            coefficient = 1.0 + (rarity_ratio * 0.6)  # 1.0 to 1.6
        
        coefficients[band_key] = round(coefficient, 3)
    
    return coefficients

def generate_daily_coefficient_matrix(
    current_risk_value: float,
    risk_bands_data: Dict[str, Dict],
    previous_risk_band: Optional[str] = None,
    last_band_change_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate daily coefficient matrix for current band and neighboring bands.
    
    Args:
        current_risk_value: Current risk value
        risk_bands_data: Current day's risk bands data
        previous_risk_band: Previous risk band
        last_band_change_date: Date when band last changed
    
    Returns:
        Dictionary containing coefficient matrix and metadata
    """
    
    # Calculate dynamic band coefficients
    band_coefficients = calculate_dynamic_band_coefficients(risk_bands_data)
    
    # Determine current band
    band_start = math.floor(current_risk_value * 10) / 10
    band_end = band_start + 0.1
    current_band = f"{band_start:.1f}-{band_end:.1f}"
    
    # Get neighboring bands
    current_band_num = int(band_start * 10)
    neighboring_bands = []
    
    # Previous band
    if current_band_num > 0:
        prev_band_start = (current_band_num - 1) * 0.1
        prev_band_end = prev_band_start + 0.1
        prev_band = f"{prev_band_start:.1f}-{prev_band_end:.1f}"
        neighboring_bands.append(prev_band)
    
    # Current band
    neighboring_bands.append(current_band)
    
    # Next band
    if current_band_num < 9:
        next_band_start = (current_band_num + 1) * 0.1
        next_band_end = next_band_start + 0.1
        next_band = f"{next_band_start:.1f}-{next_band_end:.1f}"
        neighboring_bands.append(next_band)
    
    # Generate coefficient matrix for neighboring bands
    coefficient_matrix = {}
    
    for band in neighboring_bands:
        band_start_val = float(band.split('-')[0])
        band_end_val = float(band.split('-')[1])
        band_midpoint = band_start_val + 0.05
        
        # Get band coefficient
        band_coef = band_coefficients.get(band, 1.0)
        
        # Generate coefficients for every 0.01 increment in this band
        band_coefficients_list = []
        for i in range(11):  # 0.00 to 0.10 (11 points)
            risk_in_band = band_start_val + (i * 0.01)
            
            # Calculate coefficient using linear interpolation
            if i == 5:  # Middle of band
                coefficient = band_coef
            else:
                # Linear interpolation from band midpoint
                distance_from_midpoint = (i - 5) * 0.01
                
                # Get next band coefficient for interpolation
                next_band_start = band_end_val
                next_band_end = next_band_start + 0.1
                next_band = f"{next_band_start:.1f}-{next_band_end:.1f}"
                next_band_coef = band_coefficients.get(next_band, band_coef)
                
                # Linear interpolation
                total_difference = next_band_coef - band_coef
                coefficient = band_coef + (distance_from_midpoint * 10 * total_difference)
            
            band_coefficients_list.append({
                'risk_value': round(risk_in_band, 2),
                'coefficient': round(coefficient, 3),
                'position': 'START' if i == 0 else 'MIDDLE' if i == 5 else 'END' if i == 10 else 'WITHIN'
            })
        
        coefficient_matrix[band] = {
            'band_midpoint_coefficient': band_coef,
            'coefficients': band_coefficients_list
        }
    
    # Calculate current coefficient
    current_coefficient = calculate_current_coefficient(
        current_risk_value, 
        band_coefficients, 
        previous_risk_band, 
        last_band_change_date
    )
    
    return {
        'generation_date': datetime.now().strftime('%Y-%m-%d'),
        'current_risk_value': current_risk_value,
        'current_band': current_band,
        'current_coefficient': current_coefficient,
        'band_coefficients': band_coefficients,
        'neighboring_bands': neighboring_bands,
        'coefficient_matrix': coefficient_matrix,
        'risk_bands_data': risk_bands_data
    }

def calculate_current_coefficient(
    risk_value: float,
    band_coefficients: Dict[str, float],
    previous_risk_band: Optional[str] = None,
    last_band_change_date: Optional[str] = None
) -> float:
    """
    Calculate current coefficient using dynamic band coefficients.
    """
    
    # Determine current band
    band_start = math.floor(risk_value * 10) / 10
    band_end = band_start + 0.1
    current_band = f"{band_start:.1f}-{band_end:.1f}"
    
    # Check if this is the first day in a new band
    is_first_day_in_band = False
    if previous_risk_band and previous_risk_band != current_band:
        if last_band_change_date:
            try:
                change_date = datetime.strptime(last_band_change_date, "%Y-%m-%d")
                today = datetime.now().date()
                days_since_change = (today - change_date.date()).days
                is_first_day_in_band = days_since_change == 0
            except:
                is_first_day_in_band = True
        else:
            is_first_day_in_band = True
    
    # Get current band coefficient
    current_band_coef = band_coefficients.get(current_band, 1.0)
    
    if is_first_day_in_band:
        # FIRST DAY EXCEPTION: Use band midpoint coefficient
        return current_band_coef
    else:
        # SECOND DAY+: Linear interpolation
        band_midpoint_risk = band_start + 0.05
        next_band_start = band_end
        next_band_end = next_band_start + 0.1
        next_band = f"{next_band_start:.1f}-{next_band_end:.1f}"
        next_band_coef = band_coefficients.get(next_band, current_band_coef)
        
        # Calculate linear interpolation
        distance_from_midpoint = risk_value - band_midpoint_risk
        total_difference = next_band_coef - current_band_coef
        total_risk_distance = 0.1  # Distance between band midpoints
        
        if total_risk_distance != 0:
            slope = total_difference / total_risk_distance
            coefficient = current_band_coef + (distance_from_midpoint * slope)
        else:
            coefficient = current_band_coef
        
        # MAX FUNCTION
        if previous_risk_band and previous_risk_band != current_band:
            previous_band_coef = band_coefficients.get(previous_risk_band, 1.0)
            return max(coefficient, previous_band_coef)
        else:
            return coefficient

def print_daily_coefficient_matrix(matrix_data: Dict[str, Any]):
    """Print the daily coefficient matrix in a readable format."""
    
    print("=== DAILY COEFFICIENT MATRIX ===")
    print(f"Generation Date: {matrix_data['generation_date']}")
    print(f"Current Risk Value: {matrix_data['current_risk_value']:.3f}")
    print(f"Current Band: {matrix_data['current_band']}")
    print(f"Current Coefficient: {matrix_data['current_coefficient']:.3f}")
    print()
    
    print("Dynamic Band Coefficients (Based on Current Day's Data):")
    for band, coef in matrix_data['band_coefficients'].items():
        print(f"  {band}: {coef:.3f}")
    print()
    
    print("Coefficient Matrix (Neighboring Bands Only):")
    for band, data in matrix_data['coefficient_matrix'].items():
        print(f"\n{band} Band (Midpoint Coefficient: {data['band_midpoint_coefficient']:.3f}):")
        print("Risk | Coefficient | Position")
        print("-" * 30)
        
        for coef_data in data['coefficients']:
            print(f"{coef_data['risk_value']:4.2f} | {coef_data['coefficient']:10.3f} | {coef_data['position']}")

# Example usage
if __name__ == "__main__":
    # Example risk bands data (this would come from your database)
    example_risk_bands_data = {
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
    
    # Generate daily coefficient matrix
    matrix_data = generate_daily_coefficient_matrix(
        current_risk_value=0.580,
        risk_bands_data=example_risk_bands_data,
        previous_risk_band="0.5-0.6",
        last_band_change_date="2025-08-12"
    )
    
    print_daily_coefficient_matrix(matrix_data)
