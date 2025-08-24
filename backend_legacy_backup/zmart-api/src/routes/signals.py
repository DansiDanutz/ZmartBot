"""
Zmart Trading Bot Platform - Signals Routes
Signal generation, processing, and management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.routes.auth import get_current_active_user, require_role
from src.utils.locking import signal_lock
from src.utils.metrics import record_signal_metrics
from src.utils.event_bus import emit_signal_event

router = APIRouter()

# Pydantic models
class Signal(BaseModel):
    signal_id: str
    symbol: str
    signal_type: str  # "buy", "sell", "hold"
    confidence: float
    source: str
    data: Dict[str, Any]
    timestamp: datetime
    status: str  # "active", "expired", "executed", "rejected"

class SignalRequest(BaseModel):
    symbol: str
    signal_type: str
    confidence: float
    source: str
    data: Dict[str, Any]

class SignalFilter(BaseModel):
    symbol: Optional[str] = None
    signal_type: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    min_confidence: Optional[float] = None
    max_confidence: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

# Mock data (replace with database)
MOCK_SIGNALS = []

@router.post("/generate", response_model=Signal)
async def generate_signal(
    signal_request: SignalRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Generate a new trading signal"""
    async with signal_lock(signal_request.symbol, current_user["username"]):
        try:
            # Validate signal request
            if signal_request.signal_type not in ["buy", "sell", "hold"]:
                raise HTTPException(status_code=400, detail="Invalid signal type")
            
            if not 0 <= signal_request.confidence <= 1:
                raise HTTPException(status_code=400, detail="Confidence must be between 0 and 1")
            
            # Create signal
            signal_id = f"signal_{len(MOCK_SIGNALS) + 1}_{datetime.utcnow().timestamp()}"
            signal = {
                "signal_id": signal_id,
                "symbol": signal_request.symbol,
                "signal_type": signal_request.signal_type,
                "confidence": signal_request.confidence,
                "source": signal_request.source,
                "data": signal_request.data,
                "timestamp": datetime.utcnow(),
                "status": "active",
                "user_id": current_user["id"]
            }
            
            MOCK_SIGNALS.append(signal)
            
            # Record metrics
            record_signal_metrics(
                source=signal_request.source,
                confidence=signal_request.confidence,
                status="generated"
            )
            
            # Emit signal event
            await emit_signal_event(
                source=signal_request.source,
                symbol=signal_request.symbol,
                confidence=signal_request.confidence,
                data=signal_request.data
            )
            
            return Signal(**signal)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Signal generation failed: {str(e)}")

@router.get("/signals", response_model=List[Signal])
async def get_signals(
    symbol: Optional[str] = None,
    signal_type: Optional[str] = None,
    source: Optional[str] = None,
    status: Optional[str] = None,
    min_confidence: Optional[float] = None,
    max_confidence: Optional[float] = None,
    limit: int = 100,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get signals with optional filtering"""
    signals = [signal for signal in MOCK_SIGNALS if signal["user_id"] == current_user["id"]]
    
    # Apply filters
    if symbol:
        signals = [signal for signal in signals if signal["symbol"] == symbol]
    
    if signal_type:
        signals = [signal for signal in signals if signal["signal_type"] == signal_type]
    
    if source:
        signals = [signal for signal in signals if signal["source"] == source]
    
    if status:
        signals = [signal for signal in signals if signal["status"] == status]
    
    if min_confidence is not None:
        signals = [signal for signal in signals if signal["confidence"] >= min_confidence]
    
    if max_confidence is not None:
        signals = [signal for signal in signals if signal["confidence"] <= max_confidence]
    
    # Sort by timestamp (newest first) and limit
    signals.sort(key=lambda x: x["timestamp"], reverse=True)
    signals = signals[:limit]
    
    return [Signal(**signal) for signal in signals]

@router.get("/signals/{signal_id}", response_model=Signal)
async def get_signal(
    signal_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific signal by ID"""
    signal = next((s for s in MOCK_SIGNALS if s["signal_id"] == signal_id and s["user_id"] == current_user["id"]), None)
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return Signal(**signal)

@router.put("/signals/{signal_id}/status")
async def update_signal_status(
    signal_id: str,
    status: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update signal status"""
    signal = next((s for s in MOCK_SIGNALS if s["signal_id"] == signal_id and s["user_id"] == current_user["id"]), None)
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    if status not in ["active", "expired", "executed", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    signal["status"] = status
    
    # Record metrics
    record_signal_metrics(
        source=signal["source"],
        confidence=signal["confidence"],
        status=status
    )
    
    return {"message": f"Signal {signal_id} status updated to {status}"}

@router.delete("/signals/{signal_id}")
async def delete_signal(
    signal_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a signal"""
    signal = next((s for s in MOCK_SIGNALS if s["signal_id"] == signal_id and s["user_id"] == current_user["id"]), None)
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    MOCK_SIGNALS.remove(signal)
    
    return {"message": f"Signal {signal_id} deleted"}

@router.get("/signals/active")
async def get_active_signals(
    symbol: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get active signals"""
    signals = [signal for signal in MOCK_SIGNALS 
               if signal["user_id"] == current_user["id"] and signal["status"] == "active"]
    
    if symbol:
        signals = [signal for signal in signals if signal["symbol"] == symbol]
    
    return [Signal(**signal) for signal in signals]

@router.get("/signals/confidence-heatmap")
async def get_confidence_heatmap(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get signal confidence heatmap data"""
    # Mock heatmap data (replace with real calculation)
    heatmap_data = {
        "BTCUSDT": {
            "buy": 0.8,
            "sell": 0.3,
            "hold": 0.5
        },
        "ETHUSDT": {
            "buy": 0.6,
            "sell": 0.7,
            "hold": 0.4
        }
    }
    
    return {
        "heatmap": heatmap_data,
        "timestamp": datetime.utcnow()
    }

@router.get("/signals/sources")
async def get_signal_sources(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get available signal sources"""
    # Get unique sources from user's signals
    sources = list(set(signal["source"] for signal in MOCK_SIGNALS if signal["user_id"] == current_user["id"]))
    
    return {
        "sources": sources,
        "total_sources": len(sources)
    }

@router.get("/signals/statistics")
async def get_signal_statistics(
    symbol: Optional[str] = None,
    time_range: str = "24h",
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get signal statistics"""
    user_signals = [signal for signal in MOCK_SIGNALS if signal["user_id"] == current_user["id"]]
    
    if symbol:
        user_signals = [signal for signal in user_signals if signal["symbol"] == symbol]
    
    # Calculate statistics
    total_signals = len(user_signals)
    active_signals = len([s for s in user_signals if s["status"] == "active"])
    executed_signals = len([s for s in user_signals if s["status"] == "executed"])
    rejected_signals = len([s for s in user_signals if s["status"] == "rejected"])
    
    avg_confidence = sum(s["confidence"] for s in user_signals) / total_signals if total_signals > 0 else 0
    
    signal_types = {}
    for signal in user_signals:
        signal_type = signal["signal_type"]
        if signal_type not in signal_types:
            signal_types[signal_type] = 0
        signal_types[signal_type] += 1
    
    return {
        "total_signals": total_signals,
        "active_signals": active_signals,
        "executed_signals": executed_signals,
        "rejected_signals": rejected_signals,
        "average_confidence": avg_confidence,
        "signal_types": signal_types,
        "time_range": time_range
    }

@router.post("/signals/bulk")
async def create_bulk_signals(
    signals: List[SignalRequest],
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create multiple signals at once"""
    created_signals = []
    
    for signal_request in signals:
        try:
            signal = await generate_signal(signal_request, current_user)
            created_signals.append(signal)
        except Exception as e:
            # Continue with other signals even if one fails
            continue
    
    return {
        "created_signals": len(created_signals),
        "total_requested": len(signals),
        "signals": created_signals
    }

@router.get("/signals/recent")
async def get_recent_signals(
    hours: int = 24,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get recent signals from the last N hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    recent_signals = [
        signal for signal in MOCK_SIGNALS 
        if signal["user_id"] == current_user["id"] and signal["timestamp"] >= cutoff_time
    ]
    
    # Sort by timestamp (newest first)
    recent_signals.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return [Signal(**signal) for signal in recent_signals]

@router.post("/signals/validate")
async def validate_signal(
    signal_request: SignalRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Validate a signal without creating it"""
    try:
        # Validate signal request
        if signal_request.signal_type not in ["buy", "sell", "hold"]:
            raise HTTPException(status_code=400, detail="Invalid signal type")
        
        if not 0 <= signal_request.confidence <= 1:
            raise HTTPException(status_code=400, detail="Confidence must be between 0 and 1")
        
        # Mock validation logic (replace with actual validation)
        validation_result = {
            "valid": True,
            "confidence_score": signal_request.confidence,
            "risk_level": "low" if signal_request.confidence < 0.5 else "medium" if signal_request.confidence < 0.8 else "high",
            "recommendations": []
        }
        
        if signal_request.confidence < 0.3:
            validation_result["recommendations"].append("Consider increasing confidence threshold")
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signal validation failed: {str(e)}") 