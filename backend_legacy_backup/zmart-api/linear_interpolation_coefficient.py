"""
linear_interpolation_coefficient.py
----------------------------------
Linear interpolation coefficient calculation with first-day exception and Max function.

Methodology:
- Each band has a range of coefficients
- Linear interpolation within each band
- Smooth transition between bands
- FIRST DAY EXCEPTION: When band changes, use band average for first day
- SECOND DAY+: Calculate according to linear interpolation plan
- MAX FUNCTION: Compare current and previous band coefficients, take maximum
"""

import math
from datetime import datetime, timedelta
from typing import Optional

def get_linear_interpolation_coefficient(risk_value: float, previous_risk_band: Optional[str] = None, last_band_change_date: Optional[str] = None) -> float:
    """
    Calculate coefficient using linear interpolation with first-day exception and Max function.
    
    Args:
        risk_value: Current risk value (0.0 - 1.0)
        previous_risk_band: Previous risk band (for detecting changes)
        last_band_change_date: Date when band last changed (YYYY-MM-DD)
    
    Returns:
        Interpolated coefficient value with Max function applied
    """
    
    # Band average coefficients (from our analysis)
    band_averages = {
        "0.0-0.1": 1.538,  # Very Rare
        "0.1-0.2": 1.221,  # Rare
        "0.2-0.3": 1.157,  # Medium
        "0.3-0.4": 1.000,  # Most Common
        "0.4-0.5": 1.016,  # Common
        "0.5-0.6": 1.101,  # Medium (Current BTC)
        "0.6-0.7": 1.411,  # Rare
        "0.7-0.8": 1.537,  # Very Rare
        "0.8-0.9": 1.568,  # Extremely Rare
        "0.9-1.0": 1.600   # Extremely Rare
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
    
    # Calculate current band coefficient
    current_band_avg = band_averages.get(current_band, 1.0)
    
    if is_first_day_in_band:
        # FIRST DAY EXCEPTION: Use band average
        current_coef = current_band_avg
    else:
        # SECOND DAY+: Linear interpolation
        # Get next band average
        next_band_start = band_end
        next_band_end = next_band_start + 0.1
        next_band = f"{next_band_start:.1f}-{next_band_end:.1f}"
        next_band_avg = band_averages.get(next_band, current_band_avg)
        
        # Calculate the difference between bands
        band_difference = next_band_avg - current_band_avg
        
        # Calculate position within current band (0 to 1)
        position_in_band = (risk_value - band_start) / 0.1
        
        # Linear interpolation: distribute the difference evenly within the band
        # First half of band: coefficient decreases from current_band_avg to midpoint
        # Second half of band: coefficient increases from midpoint to next_band_avg
        midpoint = current_band_avg + (band_difference / 2)
        
        if position_in_band <= 0.5:
            # First half: linear decrease from current_band_avg to midpoint
            interpolation_factor = position_in_band / 0.5  # 0 to 1
            current_coef = current_band_avg - (interpolation_factor * (current_band_avg - midpoint))
        else:
            # Second half: linear increase from midpoint to next_band_avg
            interpolation_factor = (position_in_band - 0.5) / 0.5  # 0 to 1
            current_coef = midpoint + (interpolation_factor * (next_band_avg - midpoint))
    
    # MAX FUNCTION: Compare current and previous band coefficients
    if previous_risk_band and previous_risk_band != current_band:
        # Get previous band coefficient (use band average for comparison)
        previous_band_avg = band_averages.get(previous_risk_band, 1.0)
        
        # Take the maximum of current and previous band coefficients
        final_coefficient = max(current_coef, previous_band_avg)
        
        print(f"🔍 MAX FUNCTION ANALYSIS:")
        print(f"   Current Band: {current_band} (Coefficient: {current_coef:.3f})")
        print(f"   Previous Band: {previous_risk_band} (Coefficient: {previous_band_avg:.3f})")
        print(f"   Max Result: {final_coefficient:.3f}")
        
        return final_coefficient
    else:
        # No previous band or same band - return current coefficient
        return current_coef

def test_linear_interpolation_with_max():
    """Test the linear interpolation coefficient calculation with first-day exception and Max function."""
    
    print("=== LINEAR INTERPOLATION WITH FIRST-DAY EXCEPTION AND MAX FUNCTION ===")
    print()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Band Change: 0.4-0.5 → 0.5-0.6 (First Day)",
            "risk_value": 0.579472,
            "previous_band": "0.4-0.5",
            "last_change_date": datetime.now().strftime("%Y-%m-%d"),
            "expected": "Max(1.101, 1.016) = 1.101"
        },
        {
            "name": "Band Change: 0.5-0.6 → 0.6-0.7 (First Day)",
            "risk_value": 0.650,
            "previous_band": "0.5-0.6",
            "last_change_date": datetime.now().strftime("%Y-%m-%d"),
            "expected": "Max(1.411, 1.101) = 1.411"
        },
        {
            "name": "Band Change: 0.6-0.7 → 0.5-0.6 (First Day)",
            "risk_value": 0.579472,
            "previous_band": "0.6-0.7",
            "last_change_date": datetime.now().strftime("%Y-%m-%d"),
            "expected": "Max(1.101, 1.411) = 1.411"
        },
        {
            "name": "Same Band (0.5-0.6) - Second Day",
            "risk_value": 0.579472,
            "previous_band": "0.5-0.6",
            "last_change_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            "expected": "Linear interpolation (1.347) - no Max needed"
        }
    ]
    
    for scenario in scenarios:
        coef = get_linear_interpolation_coefficient(
            scenario["risk_value"],
            scenario["previous_band"],
            scenario["last_change_date"]
        )
        print(f"📊 {scenario['name']}:")
        print(f"   Risk: {scenario['risk_value']:.3f}")
        print(f"   Previous Band: {scenario['previous_band']}")
        print(f"   Last Change: {scenario['last_change_date']}")
        print(f"   Final Coefficient: {coef:.3f}")
        print(f"   Expected: {scenario['expected']}")
        print()
    
    print("=== MAX FUNCTION BENEFITS ===")
    print("✅ Prevents coefficient drops when moving to lower bands")
    print("✅ Maintains signal strength during band transitions")
    print("✅ Provides stability in trading decisions")
    print("✅ Only applies on band changes (first day)")

if __name__ == "__main__":
    test_linear_interpolation_with_max()
