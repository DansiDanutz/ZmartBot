"""
Coefficient API Routes
Provides coefficient calculation using the perfected Dynamic Bidirectional Interpolation (DBI) methodology
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging
import sys
import os

# Add the parent directory to the path to import our perfected coefficient system
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from risk_coefficient import get_coefficient
from scoring_system import calculate_final_score, ZmartBotScoringSystem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/coefficient", tags=["coefficient"])

# Initialize the scoring system
scoring_system = ZmartBotScoringSystem()

@router.post("/calculate")
async def calculate_coefficient(
    request: Request,
    symbol: str = Query(..., description="Trading symbol (e.g., BTC, ETH)"),
    risk_value: str = Query("0.5", description="Current risk value (0.0-1.0)"),
    previous_risk_band: Optional[str] = Query(None, description="Previous risk band for band change detection"),
    last_band_change_date: Optional[str] = Query(None, description="Date when band last changed (YYYY-MM-DD)")
):
    """
    Calculate coefficient using the perfected Dynamic Bidirectional Interpolation (DBI) methodology
    
    This endpoint uses the LOCKED and PERFECTED coefficient calculation method
    that considers both previous and next bands based on direction from midpoint.
    
    Returns:
        - coefficient: Calculated coefficient (1.000-1.600)
        - methodology: "Dynamic Bidirectional Interpolation (DBI)"
        - calculation_details: Step-by-step calculation breakdown
        - final_score: Complete score calculation (Base Score × Coefficient)
    """
    try:
        # Handle "null" string from frontend or empty/invalid values
        if risk_value in ["null", "undefined", "NaN", "", None]:
            # Default to 0.5 (midpoint) if no valid risk value provided
            risk_value_float = 0.5
            logger.warning(f"⚠️ Received invalid risk_value '{risk_value}' for {symbol}, defaulting to 0.5")
        else:
            try:
                risk_value_float = float(risk_value)
                # Validate range
                if not 0 <= risk_value_float <= 1:
                    logger.warning(f"⚠️ Risk value {risk_value_float} out of range for {symbol}, clamping to [0,1]")
                    risk_value_float = max(0, min(1, risk_value_float))
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Could not parse risk_value '{risk_value}' for {symbol}, defaulting to 0.5: {e}")
                risk_value_float = 0.5
        
        logger.info(f"🎯 Calculating coefficient for {symbol} at risk {risk_value_float} using DBI methodology")
        
        # Step 1: Calculate coefficient using DBI
        coefficient = get_coefficient(
            risk_value=risk_value_float,
            previous_risk_band=previous_risk_band,
            last_band_change_date=last_band_change_date
        )
        
        # Step 2: Calculate complete final score
        final_score_result = calculate_final_score(symbol, risk_value_float)
        
        # Step 3: Create detailed calculation breakdown
        calculation_details = _create_calculation_breakdown(risk_value_float, coefficient)
        
        # Step 4: Return comprehensive result
        result = {
            "success": True,
            "symbol": symbol.upper(),
            "risk_value": risk_value_float,
            "coefficient": round(coefficient, 3),
            "methodology": "Dynamic Bidirectional Interpolation (DBI)",
            "calculation_details": calculation_details,
            "final_score": final_score_result,
            "timestamp": datetime.now().isoformat(),
            "status": "PERFECT - Using locked DBI methodology"
        }
        
        logger.info(f"✅ Coefficient calculated for {symbol}: {coefficient:.3f} (DBI)")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error calculating coefficient for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating coefficient: {str(e)}")

@router.post("/calculate-batch")
async def calculate_coefficients_batch(
    symbols_data: Dict[str, float]
):
    """
    Calculate coefficients for multiple symbols using DBI methodology
    
    Args:
        symbols_data: Dictionary with symbol as key and risk_value as value
        
    Returns:
        Dictionary with symbol as key and coefficient calculation result as value
    """
    try:
        logger.info(f"🔄 Calculating coefficients for {len(symbols_data)} symbols using DBI")
        
        results = {}
        for symbol, risk_value in symbols_data.items():
            try:
                # Calculate coefficient using DBI
                coefficient = get_coefficient(risk_value=risk_value)
                
                # Calculate final score
                final_score_result = calculate_final_score(symbol, risk_value)
                
                results[symbol] = {
                    "success": True,
                    "symbol": symbol.upper(),
                    "risk_value": risk_value,
                    "coefficient": round(coefficient, 3),
                    "methodology": "Dynamic Bidirectional Interpolation (DBI)",
                    "final_score": final_score_result,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Error calculating coefficient for {symbol}: {e}")
                results[symbol] = {
                    "success": False,
                    "symbol": symbol.upper(),
                    "error": str(e)
                }
        
        logger.info(f"✅ Batch coefficient calculation completed for {len(results)} symbols")
        return {
            "success": True,
            "results": results,
            "total_symbols": len(results),
            "methodology": "Dynamic Bidirectional Interpolation (DBI)",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in batch coefficient calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Error in batch calculation: {str(e)}")

@router.get("/methodology")
async def get_methodology_info():
    """
    Get information about the Dynamic Bidirectional Interpolation (DBI) methodology
    
    Returns:
        Complete methodology documentation and validation results
    """
    try:
        methodology_info = {
            "name": "Dynamic Bidirectional Interpolation (DBI)",
            "status": "PERFECT - LOCKED FOR FUTURE USE",
            "last_updated": "August 14, 2025",
            "description": "Calculate coefficients by dynamically choosing the correct neighboring band based on the direction from the current band's midpoint, ensuring perfect linear interpolation in both directions.",
            
            "calculation_steps": [
                "Step 1: Band Assignment - Determine current risk band",
                "Step 2: Direction Detection - Check if moving towards previous or next band",
                "Step 3: Dynamic Increment Calculation - Use band-specific increments",
                "Step 4: Final Coefficient Calculation - Apply linear interpolation"
            ],
            
            "band_midpoint_coefficients": {
                "0.0-0.1": 1.538, "0.1-0.2": 1.221, "0.2-0.3": 1.157,
                "0.3-0.4": 1.000, "0.4-0.5": 1.016, "0.5-0.6": 1.101,
                "0.6-0.7": 1.411, "0.7-0.8": 1.537, "0.8-0.9": 1.568, "0.9-1.0": 1.600
            },
            
            "validation_results": {
                "BTC at Risk 0.544": "1.096 (Towards Previous - 0.0085 increment) ✅",
                "BTC at Risk 0.556": "1.120 (Towards Next - 0.031 increment) ✅",
                "BTC at Risk 0.550": "1.101 (At Midpoint - no interpolation) ✅"
            },
            
            "key_features": [
                "Dynamic Direction Detection",
                "Band-Specific Increments",
                "Midpoint Anchoring",
                "Linear Precision",
                "Validated Results"
            ],
            
            "integration": {
                "workflow_position": "Step 5 in daily sequence (after risk band updates)",
                "formula": "Final Score = Base Score × Coefficient",
                "files": [
                    "risk_coefficient.py - DBI calculation logic",
                    "scoring_system.py - Final score calculation",
                    "risk_band_updater.py - Workflow integration"
                ]
            }
        }
        
        return {
            "success": True,
            "methodology": methodology_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting methodology info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting methodology info: {str(e)}")

def _create_calculation_breakdown(risk_value: float, coefficient: float) -> Dict[str, Any]:
    """
    Create detailed calculation breakdown for transparency
    """
    # Determine current band
    band_start = int(risk_value * 10) / 10
    band_end = band_start + 0.1
    current_band = f"{band_start:.1f}-{band_end:.1f}"
    
    # Calculate distance from midpoint
    band_midpoint_risk = band_start + 0.05
    distance_from_midpoint = risk_value - band_midpoint_risk
    
    # Determine direction
    direction = "Towards Previous Band" if distance_from_midpoint < 0 else "Towards Next Band" if distance_from_midpoint > 0 else "At Midpoint"
    
    # Band midpoint coefficients
    band_midpoints = {
        "0.0-0.1": 1.538, "0.1-0.2": 1.221, "0.2-0.3": 1.157,
        "0.3-0.4": 1.000, "0.4-0.5": 1.016, "0.5-0.6": 1.101,
        "0.6-0.7": 1.411, "0.7-0.8": 1.537, "0.8-0.9": 1.568, "0.9-1.0": 1.600
    }
    
    current_band_midpoint = band_midpoints.get(current_band, 1.0)
    
    breakdown = {
        "risk_value": risk_value,
        "current_band": current_band,
        "band_midpoint": band_midpoint_risk,
        "band_midpoint_coefficient": current_band_midpoint,
        "distance_from_midpoint": round(distance_from_midpoint, 4),
        "interpolation_direction": direction,
        "final_coefficient": round(coefficient, 3),
        "methodology": "Dynamic Bidirectional Interpolation (DBI)"
    }
    
    return breakdown

@router.get("/health")
async def health_check():
    """Health check for coefficient calculation service"""
    try:
        # Test the DBI calculation
        test_coefficient = get_coefficient(0.544)
        test_score = calculate_final_score("BTC", 0.544)
        
        return {
            "service": "coefficient-calculation",
            "status": "healthy",
            "methodology": "Dynamic Bidirectional Interpolation (DBI)",
            "test_results": {
                "btc_risk_0.544_coefficient": round(test_coefficient, 3),
                "btc_final_score": test_score.get('final_score', 'N/A')
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
