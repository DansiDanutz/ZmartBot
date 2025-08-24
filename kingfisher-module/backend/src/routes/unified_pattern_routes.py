#!/usr/bin/env python3
"""
🎯 Unified Pattern Recognition Routes
API endpoints for the Unified Pattern Agent
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
import json

# Import the unified pattern agent
from src.agents.unified_pattern_agent import (
    UnifiedPatternAgent,
    analyze_symbol_patterns,
    PatternLearningModule
)

# Import data fetching services
from src.services.airtable_service import AirtableService
from src.services.kingfisher_service import KingfisherService

logger = logging.getLogger(__name__)

# Create Blueprint
unified_pattern_bp = Blueprint('unified_pattern', __name__)

# Initialize services
pattern_agent = UnifiedPatternAgent()
learning_module = PatternLearningModule()
airtable_service = AirtableService()
kingfisher_service = KingfisherService()

# ==================== Main Analysis Endpoint ====================

@unified_pattern_bp.route('/analyze/<symbol>', methods=['GET', 'POST'])
def analyze_pattern(symbol: str):
    """
    Analyze patterns for a symbol using all data sources
    
    GET: Uses latest available data
    POST: Uses provided data in request body
    """
    try:
        # Get data from request or fetch latest
        if request.method == 'POST':
            data = request.json or {}
            riskmetric_data = data.get('riskmetric')
            cryptometer_data = data.get('cryptometer')
            kingfisher_data = data.get('kingfisher')
        else:
            # Fetch latest data from services
            riskmetric_data = _fetch_riskmetric_data(symbol)
            cryptometer_data = _fetch_cryptometer_data(symbol)
            kingfisher_data = _fetch_kingfisher_data(symbol)
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            analyze_symbol_patterns(
                symbol,
                riskmetric_data,
                cryptometer_data,
                kingfisher_data
            )
        )
        
        return jsonify({
            "success": True,
            "symbol": symbol,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error analyzing patterns for {symbol}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "symbol": symbol
        }), 500

# ==================== Pattern Detection Endpoints ====================

@unified_pattern_bp.route('/patterns/detect', methods=['POST'])
def detect_patterns():
    """
    Detect patterns from provided data
    
    Request body:
    {
        "symbol": "BTC-USDT",
        "data": {
            "riskmetric": {...},
            "cryptometer": {...},
            "kingfisher": {...}
        }
    }
    """
    try:
        data = request.json
        symbol = data.get('symbol', 'UNKNOWN')
        source_data = data.get('data', {})
        
        # Run pattern detection
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        analysis = loop.run_until_complete(
            pattern_agent.analyze_symbol(symbol, source_data)
        )
        
        # Extract just the patterns
        patterns = {
            "detected_patterns": [
                {
                    "type": p.pattern_type.value,
                    "strength": p.strength.name,
                    "confidence": p.confidence,
                    "direction": p.direction,
                    "timeframe": p.timeframe,
                    "source": p.source.value,
                    "notes": p.notes
                }
                for p in analysis.detected_patterns
            ],
            "integrated_patterns": [
                {
                    "id": ip.pattern_id,
                    "confluence_score": ip.confluence_score,
                    "combined_strength": ip.combined_strength.name,
                    "win_rates": ip.win_rate_estimate,
                    "recommendations": ip.recommendations
                }
                for ip in analysis.integrated_patterns
            ],
            "pattern_score": analysis.pattern_score,
            "signal_strength": analysis.signal_strength,
            "confidence": analysis.confidence_level
        }
        
        return jsonify({
            "success": True,
            "symbol": symbol,
            "patterns": patterns,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error detecting patterns: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== Win Rate Endpoints ====================

@unified_pattern_bp.route('/winrate/<symbol>', methods=['GET'])
def get_win_rates(symbol: str):
    """Get win rate predictions for a symbol"""
    try:
        # Fetch latest data
        riskmetric_data = _fetch_riskmetric_data(symbol)
        cryptometer_data = _fetch_cryptometer_data(symbol)
        kingfisher_data = _fetch_kingfisher_data(symbol)
        
        # Run analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            analyze_symbol_patterns(
                symbol,
                riskmetric_data,
                cryptometer_data,
                kingfisher_data
            )
        )
        
        win_rates = result.get('win_rates', {})
        
        return jsonify({
            "success": True,
            "symbol": symbol,
            "win_rates": win_rates,
            "confidence": result.get('confidence_level', 0),
            "market_phase": result.get('market_phase', 'unknown'),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting win rates for {symbol}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "symbol": symbol
        }), 500

# ==================== Pattern Statistics Endpoints ====================

@unified_pattern_bp.route('/statistics/<symbol>', methods=['GET'])
def get_pattern_statistics(symbol: str):
    """Get historical pattern statistics for a symbol"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        stats = loop.run_until_complete(
            pattern_agent.get_pattern_statistics(symbol)
        )
        
        return jsonify({
            "success": True,
            "symbol": symbol,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting statistics for {symbol}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "symbol": symbol
        }), 500

# ==================== Learning Endpoints ====================

@unified_pattern_bp.route('/learn/outcome', methods=['POST'])
def update_pattern_outcome():
    """
    Update pattern outcome for learning
    
    Request body:
    {
        "symbol": "BTC-USDT",
        "pattern_id": "pattern_123",
        "outcome": {
            "success": true,
            "actual_direction": "long",
            "profit_loss": 5.2,
            "duration_hours": 12
        }
    }
    """
    try:
        data = request.json
        symbol = data.get('symbol')
        pattern_id = data.get('pattern_id')
        outcome = data.get('outcome')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            pattern_agent.update_pattern_performance(symbol, pattern_id, outcome)
        )
        
        return jsonify({
            "success": True,
            "message": "Pattern outcome updated successfully",
            "symbol": symbol,
            "pattern_id": pattern_id
        })
    
    except Exception as e:
        logger.error(f"Error updating pattern outcome: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== Comprehensive Report Endpoint ====================

@unified_pattern_bp.route('/report/<symbol>', methods=['GET'])
def generate_pattern_report(symbol: str):
    """Generate comprehensive pattern analysis report"""
    try:
        # Fetch all data
        riskmetric_data = _fetch_riskmetric_data(symbol)
        cryptometer_data = _fetch_cryptometer_data(symbol)
        kingfisher_data = _fetch_kingfisher_data(symbol)
        
        # Run full analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        analysis = loop.run_until_complete(
            analyze_symbol_patterns(
                symbol,
                riskmetric_data,
                cryptometer_data,
                kingfisher_data
            )
        )
        
        # Format comprehensive report
        report = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "executive_summary": analysis.get('executive_summary', ''),
            "technical_analysis": analysis.get('technical_analysis', ''),
            "pattern_narrative": analysis.get('pattern_narrative', ''),
            "patterns": {
                "detected": len(analysis.get('detected_patterns', [])),
                "integrated": len(analysis.get('integrated_patterns', [])),
                "score": analysis.get('pattern_score', 0),
                "signal": analysis.get('signal_strength', 'neutral'),
                "confidence": analysis.get('confidence_level', 0)
            },
            "win_rates": analysis.get('win_rates', {}),
            "risk_metrics": {
                "risk_score": analysis.get('risk_score', 0),
                "liquidation_risk": analysis.get('liquidation_risk', 0),
                "volatility_regime": analysis.get('volatility_regime', 'normal')
            },
            "recommendations": {
                "entry_zones": analysis.get('entry_zones', []),
                "exit_targets": analysis.get('exit_targets', []),
                "position_size": analysis.get('position_sizing', 0.02),
                "risk_management": analysis.get('risk_management', {})
            }
        }
        
        return jsonify({
            "success": True,
            "report": report
        })
    
    except Exception as e:
        logger.error(f"Error generating report for {symbol}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "symbol": symbol
        }), 500

# ==================== Batch Analysis Endpoint ====================

@unified_pattern_bp.route('/batch/analyze', methods=['POST'])
def batch_analyze():
    """
    Analyze multiple symbols in batch
    
    Request body:
    {
        "symbols": ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
    }
    """
    try:
        data = request.json
        symbols = data.get('symbols', [])
        
        results = {}
        for symbol in symbols:
            try:
                # Fetch data for each symbol
                riskmetric_data = _fetch_riskmetric_data(symbol)
                cryptometer_data = _fetch_cryptometer_data(symbol)
                kingfisher_data = _fetch_kingfisher_data(symbol)
                
                # Run analysis
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                analysis = loop.run_until_complete(
                    analyze_symbol_patterns(
                        symbol,
                        riskmetric_data,
                        cryptometer_data,
                        kingfisher_data
                    )
                )
                
                results[symbol] = {
                    "success": True,
                    "pattern_score": analysis.get('pattern_score', 0),
                    "signal": analysis.get('signal_strength', 'neutral'),
                    "confidence": analysis.get('confidence_level', 0),
                    "win_rates": analysis.get('win_rates', {})
                }
                
            except Exception as e:
                results[symbol] = {
                    "success": False,
                    "error": str(e)
                }
        
        return jsonify({
            "success": True,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== Real-time Monitoring Endpoint ====================

@unified_pattern_bp.route('/monitor/<symbol>/start', methods=['POST'])
def start_monitoring(symbol: str):
    """Start real-time pattern monitoring for a symbol"""
    try:
        # TODO: Implement WebSocket or SSE for real-time updates
        return jsonify({
            "success": True,
            "message": f"Started monitoring {symbol}",
            "symbol": symbol,
            "status": "monitoring"
        })
    
    except Exception as e:
        logger.error(f"Error starting monitoring for {symbol}: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "symbol": symbol
        }), 500

# ==================== Helper Functions ====================

def _fetch_riskmetric_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch RiskMetric data for a symbol"""
    try:
        # TODO: Implement actual RiskMetric data fetching
        # This is a placeholder
        return {
            "risk_metric": 0.45,
            "current_price": 50000,
            "lower_band": 45000,
            "upper_band": 55000,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching RiskMetric data: {e}")
        return None

def _fetch_cryptometer_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch Cryptometer data for a symbol"""
    try:
        # TODO: Implement actual Cryptometer data fetching
        # This is a placeholder
        return {
            "fear_greed_index": 55,
            "funding_rate": 0.01,
            "open_interest_change": 10,
            "volume_24h_change": 25,
            "volatility_24h": 3.2,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching Cryptometer data: {e}")
        return None

def _fetch_kingfisher_data(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch Kingfisher data for a symbol"""
    try:
        # Fetch from Airtable
        record = airtable_service.get_symbol_data(symbol)
        
        if record:
            fields = record.get('fields', {})
            
            # Parse liquidation data
            liquidation_map = fields.get('LiquidationMap', '')
            liquidation_heatmap = fields.get('LiquidationHeatmap', '')
            
            # Extract liquidation values (simplified parsing)
            long_liq = 0
            short_liq = 0
            
            # Parse from reports (this would need actual parsing logic)
            if 'long' in liquidation_map.lower():
                # Extract long liquidation value
                pass
            if 'short' in liquidation_map.lower():
                # Extract short liquidation value
                pass
            
            return {
                "long_liquidations": long_liq,
                "short_liquidations": short_liq,
                "total_liquidations": long_liq + short_liq,
                "liquidation_map": liquidation_map,
                "liquidation_heatmap": liquidation_heatmap,
                "win_rate_24h": fields.get('WinRate_24h', ''),
                "score": fields.get('Score', 0),
                "timestamp": fields.get('LastUpdated', datetime.now().isoformat())
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching Kingfisher data: {e}")
        return None

# ==================== Status Endpoint ====================

@unified_pattern_bp.route('/status', methods=['GET'])
def get_status():
    """Get status of the Unified Pattern Agent"""
    return jsonify({
        "success": True,
        "status": "operational",
        "version": "1.0.0",
        "capabilities": [
            "pattern_detection",
            "win_rate_prediction",
            "risk_assessment",
            "multi_source_analysis",
            "real_time_monitoring"
        ],
        "data_sources": [
            "riskmetric",
            "cryptometer",
            "kingfisher"
        ],
        "timestamp": datetime.now().isoformat()
    })

# ==================== Health Check ====================

@unified_pattern_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "unified_pattern_agent",
        "timestamp": datetime.now().isoformat()
    })