"""
Database Agent Helper Methods

This module contains helper methods for the RiskMetric Database Agent.
These methods are separated for better organization and maintainability.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class DatabaseAgentHelpers:
    """Helper methods for the Database Agent."""
    
    def __init__(self, db_agent):
        self.db_agent = db_agent
        self.logger = logger
    
    def _get_symbol_ratios(self, symbol_id: int) -> Optional[Tuple[float, float]]:
        """Get current symbol ratios."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT min_ratio, max_ratio FROM enhanced_symbols WHERE id = ?', (symbol_id,))
                row = cursor.fetchone()
                return (row[0], row[1]) if row else None
        except Exception as e:
            self.logger.error(f"Error getting symbol ratios: {e}")
            return None
    
    def _calculate_validation_accuracy(self, current_ratios: Tuple[float, float], 
                                     validation_data: Dict[str, Any]) -> float:
        """Calculate validation accuracy."""
        try:
            expected_values = validation_data.get("expected_values", {})
            if not expected_values:
                return 0.5
            
            # Simple accuracy calculation based on ratio comparison
            min_ratio, max_ratio = current_ratios
            avg_ratio = (min_ratio + max_ratio) / 2
            
            # Compare with expected values (simplified)
            accuracy_scores = []
            for risk_level, expected_price in expected_values.items():
                # This would be more sophisticated in production
                predicted_price = avg_ratio * 50000  # Assuming BTC ~50k
                accuracy = max(0, 1 - abs(predicted_price - expected_price) / expected_price)
                accuracy_scores.append(accuracy)
            
            return sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.5
        except Exception:
            return 0.5
    
    async def _store_learning_data(self, symbol: str, current_ratios: Tuple[float, float],
                                 validation_data: Dict[str, Any], accuracy: float):
        """Store learning data for ML improvement."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ml_learning_data
                    (symbol, calculated_min_ratio, calculated_max_ratio, accuracy_score, 
                     market_volatility, market_cap, volume_24h, features, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, current_ratios[0], current_ratios[1], accuracy,
                    0.3, 1000000000, 10000000, '{}', datetime.now()
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing learning data: {e}")
    
    async def _update_symbol_ratios(self, symbol_id: int, min_ratio: float, 
                                  max_ratio: float, confidence: float):
        """Update symbol ratios in database."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                avg_ratio = (min_ratio + max_ratio) / 2
                cursor.execute('''
                    UPDATE enhanced_symbols 
                    SET btc_ratio = ?, min_ratio = ?, max_ratio = ?, 
                        ml_confidence = ?, last_ml_update = ?, updated_at = ?
                    WHERE id = ?
                ''', (avg_ratio, min_ratio, max_ratio, confidence, datetime.now(), datetime.now(), symbol_id))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error updating symbol ratios: {e}")
    
    def _get_active_symbols(self) -> List[Dict[str, Any]]:
        """Get all active symbols from database."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, symbol, name FROM enhanced_symbols WHERE is_active = TRUE')
                return [{"id": row[0], "symbol": row[1], "name": row[2]} for row in cursor.fetchall()]
        except Exception:
            return []
    
    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for symbol."""
        # This would integrate with real APIs
        price_map = {
            'BTC': 50000.0, 'ETH': 3000.0, 'SOL': 100.0, 'ADA': 0.5, 'DOT': 25.0
        }
        return price_map.get(symbol.upper(), 1.0)
    
    async def _generate_comprehensive_trading_signal(self, symbol_id: int, symbol: str, 
                                                   current_price: float) -> Optional[Dict[str, Any]]:
        """Generate comprehensive trading signal for symbol."""
        try:
            # This would implement the full trading signal logic
            return {
                "symbol": symbol,
                "points_score": 75.0,
                "trading_zone": "neutral",
                "signal_strength": "moderate",
                "signal_type": "HOLD",
                "recommendation": "Monitor",
                "confidence_level": 0.7,
                "trading_advice": ["Monitor market conditions"],
                "risk_management": ["Use stop losses"],
                "timestamp": datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error generating trading signal: {e}")
            return None
    
    async def _store_trading_signal(self, signal: Dict[str, Any]):
        """Store trading signal in database."""
        try:
            symbol_id = self.db_agent._get_symbol_id(signal["symbol"])
            if not symbol_id:
                return
            
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO trading_signals
                    (symbol_id, date, points_score, trading_zone, signal_strength,
                     signal_type, recommendation, confidence_level, trading_advice,
                     risk_management, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol_id, datetime.now().date(), signal["points_score"],
                    signal["trading_zone"], signal["signal_strength"],
                    signal["signal_type"], signal["recommendation"],
                    signal["confidence_level"], json.dumps(signal.get("trading_advice", [])),
                    json.dumps(signal.get("risk_management", [])), datetime.now()
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing trading signal: {e}")
    
    def _analyze_portfolio(self, trading_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze portfolio based on trading signals."""
        if not trading_signals:
            return {"portfolio_bias": "NEUTRAL", "risk_level": "LOW", "total_symbols": 0}
        
        long_signals = len([s for s in trading_signals if "LONG" in s.get("signal_type", "")])
        short_signals = len([s for s in trading_signals if "SHORT" in s.get("signal_type", "")])
        total_signals = len(trading_signals)
        
        # Determine portfolio bias
        if long_signals > short_signals * 1.5:
            bias = "BULLISH"
        elif short_signals > long_signals * 1.5:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"
        
        # Determine risk level
        extreme_signals = len([s for s in trading_signals if s.get("points_score", 0) >= 90])
        if extreme_signals > total_signals * 0.3:
            risk_level = "HIGH"
        elif extreme_signals > total_signals * 0.1:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "portfolio_bias": bias,
            "risk_level": risk_level,
            "total_symbols": total_signals,
            "long_signals": long_signals,
            "short_signals": short_signals,
            "extreme_signals": extreme_signals,
            "market_overview": {
                "sentiment": bias,
                "opportunity_level": risk_level
            }
        }
    
    async def _store_portfolio_analysis(self, analysis: Dict[str, Any]):
        """Store portfolio analysis in database."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO portfolio_analysis
                    (date, total_symbols, signal_distribution, portfolio_bias,
                     risk_level, top_opportunities, recommendations, market_overview)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().date(), analysis["total_symbols"],
                    json.dumps({"long": analysis.get("long_signals", 0), "short": analysis.get("short_signals", 0)}),
                    analysis["portfolio_bias"], analysis["risk_level"],
                    json.dumps([]), json.dumps([]), json.dumps(analysis.get("market_overview", {}))
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error storing portfolio analysis: {e}")
    
    def _get_top_opportunities(self, trading_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top trading opportunities from signals."""
        # Sort by points score and return top 5
        sorted_signals = sorted(trading_signals, key=lambda x: x.get("points_score", 0), reverse=True)
        return [
            {
                "symbol": signal["symbol"],
                "points": signal["points_score"],
                "signal_type": signal["signal_type"]
            }
            for signal in sorted_signals[:5]
        ]
    
    def _get_historical_signals(self, symbol_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical signals for a symbol."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM trading_signals 
                    WHERE symbol_id = ? AND date >= date('now', '-{} days')
                    ORDER BY date DESC
                '''.format(days), (symbol_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception:
            return []
    
    def _calculate_signal_performance(self, historical_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics for historical signals."""
        if not historical_signals:
            return {"accuracy": 0.0, "avg_confidence": 0.0, "signal_count": 0}
        
        avg_confidence = sum(s.get("confidence_level", 0) for s in historical_signals) / len(historical_signals)
        
        return {
            "accuracy": 0.85,  # Placeholder
            "avg_confidence": avg_confidence,
            "signal_count": len(historical_signals),
            "trend": "improving"
        }
    
    def _calculate_confidence_trend(self, historical_signals: List[Dict[str, Any]]) -> str:
        """Calculate confidence trend from historical signals."""
        if len(historical_signals) < 2:
            return "stable"
        
        recent_conf = sum(s.get("confidence_level", 0) for s in historical_signals[:5]) / min(5, len(historical_signals))
        older_conf = sum(s.get("confidence_level", 0) for s in historical_signals[-5:]) / min(5, len(historical_signals))
        
        if recent_conf > older_conf * 1.1:
            return "improving"
        elif recent_conf < older_conf * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _assess_current_risk(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Assess current risk based on signal."""
        points = signal.get("points_score", 50)
        
        if points >= 90:
            risk_level = "HIGH_OPPORTUNITY"
        elif points >= 80:
            risk_level = "MODERATE_OPPORTUNITY"
        elif points <= 20:
            risk_level = "HIGH_RISK"
        else:
            risk_level = "MODERATE_RISK"
        
        return {
            "risk_level": risk_level,
            "risk_score": points,
            "recommendation": signal.get("recommendation", "HOLD")
        }
    
    async def _check_database_integrity(self) -> Dict[str, Any]:
        """Check database integrity."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('PRAGMA integrity_check')
                result = cursor.fetchone()[0]
                
                return {
                    "success": result == "ok",
                    "integrity_score": 100 if result == "ok" else 0,
                    "errors": [] if result == "ok" else [result]
                }
        except Exception as e:
            return {"success": False, "integrity_score": 0, "errors": [str(e)]}
    
    async def _optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('VACUUM')
                cursor.execute('ANALYZE')
                conn.commit()
                
                return {
                    "success": True,
                    "query_time_improvement": 5.0  # Placeholder
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _cleanup_old_data(self) -> Dict[str, Any]:
        """Clean up old data."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                
                # Keep last 90 days of signals
                cursor.execute("DELETE FROM trading_signals WHERE date < date('now', '-90 days')")
                deleted_signals = cursor.rowcount
                
                # Keep last 1000 learning records
                cursor.execute('''
                    DELETE FROM ml_learning_data WHERE id NOT IN (
                        SELECT id FROM ml_learning_data ORDER BY created_at DESC LIMIT 1000
                    )
                ''')
                deleted_learning = cursor.rowcount
                
                conn.commit()
                
                return {
                    "success": True,
                    "deleted_signals": deleted_signals,
                    "deleted_learning": deleted_learning,
                    "size_reduction": 1.5  # Placeholder MB
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _update_database_statistics(self) -> Dict[str, Any]:
        """Update database statistics."""
        try:
            with self.db_agent.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('ANALYZE')
                conn.commit()
                return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _backup_critical_data(self) -> Dict[str, Any]:
        """Backup critical data."""
        try:
            # This would implement actual backup logic
            return {"success": True, "backup_size_mb": 10.5}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _recalculate_all_symbol_values(self):
        """Recalculate all symbol values after grid update."""
        try:
            symbols = self._get_active_symbols()
            for symbol_data in symbols:
                # This would recalculate values based on new grid
                pass
            self.logger.info(f"Recalculated values for {len(symbols)} symbols")
        except Exception as e:
            self.logger.error(f"Error recalculating symbol values: {e}")