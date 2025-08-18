#!/usr/bin/env python3
"""
Cryptometer Data Types and Classes
Provides common data structures for Cryptometer analysis
Replaces removed endpoint analyzer modules
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class EndpointScore:
    """Score for a single endpoint"""
    endpoint_name: str
    score: float
    weight: float
    confidence: float
    data: Dict[str, Any]

@dataclass
class CryptometerAnalysis:
    """Complete Cryptometer analysis result"""
    symbol: str
    timestamp: datetime
    endpoints_analyzed: int
    total_score: float
    signal: str  # LONG, SHORT, NEUTRAL
    confidence: float
    endpoint_scores: List[EndpointScore]
    summary: Dict[str, Any]
    raw_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'endpoints_analyzed': self.endpoints_analyzed,
            'total_score': self.total_score,
            'signal': self.signal,
            'confidence': self.confidence,
            'endpoint_scores': [
                {
                    'endpoint_name': score.endpoint_name,
                    'score': score.score,
                    'weight': score.weight,
                    'confidence': score.confidence
                }
                for score in self.endpoint_scores
            ],
            'summary': self.summary,
            'raw_data': self.raw_data
        }

class CryptometerEndpointAnalyzer:
    """
    Simplified Cryptometer Endpoint Analyzer
    Uses the main cryptometer_service for data collection
    """
    
    def __init__(self):
        self.initialized = True
    
    async def analyze_symbol(self, symbol: str) -> CryptometerAnalysis:
        """
        Analyze a symbol using the main Cryptometer service
        """
        from src.services.cryptometer_service import get_cryptometer_service
        
        # Get the main service
        service = await get_cryptometer_service()
        
        # Collect data from all endpoints
        data = await service.collect_symbol_data(symbol)
        
        # Process endpoint scores
        endpoint_scores = []
        total_weighted_score = 0
        total_weight = 0
        
        for endpoint_name, endpoint_data in data.items():
            if endpoint_name == 'symbol':
                continue
                
            if isinstance(endpoint_data, dict) and endpoint_data.get('success'):
                # Calculate score based on endpoint data
                score = self._calculate_endpoint_score(endpoint_name, endpoint_data.get('data', {}))
                weight = endpoint_data.get('weight', 1.0)
                confidence = 0.8 if endpoint_data.get('success') else 0.3
                
                endpoint_scores.append(EndpointScore(
                    endpoint_name=endpoint_name,
                    score=score,
                    weight=weight,
                    confidence=confidence,
                    data=endpoint_data.get('data', {})
                ))
                
                total_weighted_score += score * weight
                total_weight += weight
        
        # Calculate overall score
        total_score = total_weighted_score / total_weight if total_weight > 0 else 50.0
        
        # Determine signal
        if total_score >= 70:
            signal = 'LONG'
        elif total_score <= 30:
            signal = 'SHORT'
        else:
            signal = 'NEUTRAL'
        
        # Create analysis result
        return CryptometerAnalysis(
            symbol=symbol,
            timestamp=datetime.now(),
            endpoints_analyzed=len(endpoint_scores),
            total_score=total_score,
            signal=signal,
            confidence=min(0.9, len(endpoint_scores) / 10),  # More endpoints = higher confidence
            endpoint_scores=endpoint_scores,
            summary={
                'total_endpoints': len(data) - 1,  # Exclude 'symbol' key
                'successful_endpoints': len(endpoint_scores),
                'average_score': total_score,
                'recommendation': signal
            },
            raw_data=data
        )
    
    def _calculate_endpoint_score(self, endpoint_name: str, data: Dict[str, Any]) -> float:
        """
        Calculate score for a specific endpoint
        Returns a score between 0-100
        """
        # Basic scoring logic - can be enhanced based on endpoint type
        score = 50.0  # Neutral baseline
        
        # Trend indicators
        if 'trend' in str(data).lower():
            if 'bullish' in str(data).lower():
                score = 75.0
            elif 'bearish' in str(data).lower():
                score = 25.0
        
        # Price changes
        if 'change' in data:
            try:
                change = float(data.get('change', 0))
                if change > 5:
                    score = 80.0
                elif change < -5:
                    score = 20.0
                else:
                    score = 50.0 + (change * 6)  # Scale to 0-100
            except:
                pass
        
        # Volume indicators
        if 'volume' in data:
            try:
                volume = float(data.get('volume', 0))
                if volume > 1000000000:  # High volume
                    score = min(100, score + 10)
            except:
                pass
        
        # AI screener results
        if endpoint_name == 'ai_screener' and 'signal' in data:
            signal = data.get('signal', '').upper()
            if signal == 'BUY' or signal == 'LONG':
                score = 85.0
            elif signal == 'SELL' or signal == 'SHORT':
                score = 15.0
        
        return max(0, min(100, score))  # Ensure score is between 0-100

# Backward compatibility aliases
UnifiedCryptometerSystem = CryptometerEndpointAnalyzer
AdvancedCryptometerAnalyzer = CryptometerEndpointAnalyzer
ComprehensiveCryptometerAnalyzer = CryptometerEndpointAnalyzer
CryptometerEndpointAnalyzerV2 = CryptometerEndpointAnalyzer