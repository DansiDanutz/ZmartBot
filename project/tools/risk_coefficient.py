"""
risk_coefficient.py
--------------------
Linear interpolation coefficient calculation with exact band midpoint methodology.

Methodology:
- Band average coefficient is at the MIDDLE of the band (0.55 for 0.5-0.6 band)
- Exact linear increments between band midpoints
- 0.31 difference between 0.5-0.6 (1.101) and 0.6-0.7 (1.411) bands
- 0.031 increment per 0.01 risk increase
- FIRST DAY EXCEPTION: When band changes, use band average for first day
- MAX FUNCTION: Compare current and previous band coefficients, take maximum
"""

import math
from datetime import datetime, timedelta
from typing import Optional

def get_coefficient(risk_value: float, previous_risk_band: Optional[str] = None, last_band_change_date: Optional[str] = None) -> float:
    """
    Calculate coefficient using exact band midpoint methodology.
    
    Args:
        risk_value: Current risk value (0.0 - 1.0)
        previous_risk_band: Previous risk band (for detecting changes)
        last_band_change_date: Date when band last changed (YYYY-MM-DD)
    
    Returns:
        Interpolated coefficient value with Max function applied
    """
    
    # Band average coefficients at MIDDLE of each band
    band_midpoints = {
        "0.0-0.1": 1.538,  # Middle at 0.05
        "0.1-0.2": 1.221,  # Middle at 0.15
        "0.2-0.3": 1.157,  # Middle at 0.25
        "0.3-0.4": 1.000,  # Middle at 0.35
        "0.4-0.5": 1.016,  # Middle at 0.45
        "0.5-0.6": 1.101,  # Middle at 0.55
        "0.6-0.7": 1.411,  # Middle at 0.65
        "0.7-0.8": 1.537,  # Middle at 0.75
        "0.8-0.9": 1.568,  # Middle at 0.85
        "0.9-1.0": 1.600   # Middle at 0.95
    }
    
    # Determine current band
    band_start = math.floor(risk_value * 10) / 10
    band_end = band_start + 0.1
    current_band = f"{band_start:.1f}-{band_end:.1f}"
    
    # Check if this is the first day in a new band
    is_first_day_in_band = False
    if previous_risk_band and previous_risk_band != current_band:
        # Band changed - check if this is the first day
        if last_band_change_date:
            try:
                change_date = datetime.strptime(last_band_change_date, "%Y-%m-%d")
                today = datetime.now().date()
                days_since_change = (today - change_date.date()).days
                is_first_day_in_band = days_since_change == 0
            except:
                is_first_day_in_band = True  # Default to first day if date parsing fails
        else:
            is_first_day_in_band = True  # No previous date, assume first day
    
    if is_first_day_in_band:
        # FIRST DAY EXCEPTION: Use band average (middle of band)
        current_band_midpoint = band_midpoints.get(current_band, 1.0)
        current_coef = current_band_midpoint
    else:
        # SECOND DAY+: Dynamic linear interpolation considering both neighboring bands
        
        # Find current band midpoint
        band_midpoint_risk = band_start + 0.05  # Middle of current band
        current_band_midpoint = band_midpoints.get(current_band, 1.0)
        
        # Calculate distance from midpoint
        distance_from_midpoint = risk_value - band_midpoint_risk
        
        # Determine which neighboring band to use for interpolation
        if distance_from_midpoint >= 0:
            # Moving towards higher risk (next band)
            next_band_start = band_end
            next_band_end = next_band_start + 0.1
            next_band = f"{next_band_start:.1f}-{next_band_end:.1f}"
            next_band_midpoint_risk = next_band_start + 0.05
            next_band_midpoint = band_midpoints.get(next_band, current_band_midpoint)
            
            # Calculate interpolation towards next band
            total_difference = next_band_midpoint - current_band_midpoint
            total_risk_distance = next_band_midpoint_risk - band_midpoint_risk
            
            if total_risk_distance != 0:
                increment_per_001 = total_difference / (total_risk_distance * 100)
                current_coef = current_band_midpoint + (distance_from_midpoint * 100 * increment_per_001)
            else:
                current_coef = current_band_midpoint
                
        else:
            # Moving towards lower risk (previous band)
            prev_band_end = band_start
            prev_band_start = prev_band_end - 0.1
            prev_band = f"{prev_band_start:.1f}-{prev_band_end:.1f}"
            prev_band_midpoint_risk = prev_band_start + 0.05
            prev_band_midpoint = band_midpoints.get(prev_band, current_band_midpoint)
            
            # Calculate interpolation towards previous band
            total_difference = current_band_midpoint - prev_band_midpoint
            total_risk_distance = band_midpoint_risk - prev_band_midpoint_risk
            
            if total_risk_distance != 0:
                increment_per_001 = total_difference / (total_risk_distance * 100)
                current_coef = current_band_midpoint + (distance_from_midpoint * 100 * increment_per_001)
            else:
                current_coef = current_band_midpoint
    
    # MAX FUNCTION: Compare current and previous band coefficients
    if previous_risk_band and previous_risk_band != current_band:
        # Get previous band coefficient (use band midpoint for comparison)
        previous_band_midpoint = band_midpoints.get(previous_risk_band, 1.0)
        
        # Take the maximum of current and previous band coefficients
        final_coefficient = max(current_coef, previous_band_midpoint)
        
        return final_coefficient
    else:
        # No previous band or same band - return current coefficient
        return current_coef

# Legacy function for backward compatibility
def get_linear_interpolation_coefficient(risk_value: float, previous_risk_band: Optional[str] = None, last_band_change_date: Optional[str] = None) -> float:
    """Alias for get_coefficient for backward compatibility"""
    return get_coefficient(risk_value, previous_risk_band, last_band_change_date)
