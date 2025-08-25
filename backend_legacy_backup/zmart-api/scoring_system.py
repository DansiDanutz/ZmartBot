"""
scoring_system.py
-----------------
ZmartBot Final Scoring System using Dynamic Bidirectional Interpolation (DBI)

Calculates final scores using: Base Score × Coefficient = Final Score
Integrated into the complete daily workflow after coefficient updates.
"""

import math
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from risk_coefficient import get_coefficient

logger = logging.getLogger(__name__)

class ZmartBotScoringSystem:
    """
    Final Scoring System that combines base scores with DBI coefficients
    """
    
    def __init__(self):
        self.scoring_components = {
            'cryptometer': 0.50,  # 50% weight
            'kingfisher': 0.30,   # 30% weight  
            'riskmetric': 0.20    # 20% weight
        }
    
    def calculate_base_score(self, symbol: str, risk_value: float) -> float:
        """
        Calculate base score from risk value (0-100 scale)
        
        Args:
            symbol: Trading symbol
            risk_value: Current risk value (0.0-1.0)
            
        Returns:
            Base score (0-100)
        """
        try:
            # Base score calculation: Higher risk = Lower score
            # Risk 0% = Score 100, Risk 100% = Score 0
            base_score = 100 * (1 - risk_value)
            
            logger.info(f"📊 {symbol} base score calculated: {base_score:.2f} (risk: {risk_value:.3f})")
            return base_score
            
        except Exception as e:
            logger.error(f"❌ Error calculating base score for {symbol}: {e}")
            return 50.0  # Default neutral score
    
    def get_current_coefficient(self, symbol: str, risk_value: float) -> float:
        """
        Get current coefficient using DBI methodology
        
        Args:
            symbol: Trading symbol
            risk_value: Current risk value
            
        Returns:
            Coefficient value (1.000-1.600)
        """
        try:
            coefficient = get_coefficient(risk_value)
            logger.info(f"🎯 {symbol} coefficient (DBI): {coefficient:.3f}")
            return coefficient
            
        except Exception as e:
            logger.error(f"❌ Error getting coefficient for {symbol}: {e}")
            return 1.0  # Default neutral coefficient
    
    def calculate_final_score(self, symbol: str, risk_value: float) -> Dict[str, Any]:
        """
        Calculate final score using: Base Score × Coefficient = Final Score
        
        Args:
            symbol: Trading symbol
            risk_value: Current risk value (0.0-1.0)
            
        Returns:
            Dictionary with all scoring components
        """
        try:
            # Step 1: Calculate base score
            base_score = self.calculate_base_score(symbol, risk_value)
            
            # Step 2: Get coefficient using DBI
            coefficient = self.get_current_coefficient(symbol, risk_value)
            
            # Step 3: Calculate final score
            final_score = base_score * coefficient
            
            # Step 4: Determine signal strength
            signal_strength = self._determine_signal_strength(final_score)
            
            # Step 5: Create comprehensive result
            result = {
                'symbol': symbol,
                'risk_value': risk_value,
                'base_score': round(base_score, 2),
                'coefficient': round(coefficient, 3),
                'final_score': round(final_score, 2),
                'signal_strength': signal_strength,
                'calculation_time': datetime.now().isoformat(),
                'methodology': 'Dynamic Bidirectional Interpolation (DBI)'
            }
            
            logger.info(f"🏆 {symbol} final score: {final_score:.2f} (Base: {base_score:.2f} × Coef: {coefficient:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating final score for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'final_score': 0.0
            }
    
    def _determine_signal_strength(self, final_score: float) -> str:
        """
        Determine signal strength based on final score
        
        Args:
            final_score: Final calculated score
            
        Returns:
            Signal strength description
        """
        if final_score >= 80:
            return "STRONG BUY"
        elif final_score >= 60:
            return "BUY"
        elif final_score >= 40:
            return "NEUTRAL"
        elif final_score >= 20:
            return "SELL"
        else:
            return "STRONG SELL"
    
    def update_all_symbols_scores(self, symbols_data: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """
        Update final scores for all symbols
        
        Args:
            symbols_data: Dictionary of {symbol: risk_value}
            
        Returns:
            Dictionary of all symbol results
        """
        logger.info(f"🔄 Starting final score updates for {len(symbols_data)} symbols")
        
        results = {}
        for symbol, risk_value in symbols_data.items():
            try:
                result = self.calculate_final_score(symbol, risk_value)
                results[symbol] = result
                
            except Exception as e:
                logger.error(f"❌ Error updating score for {symbol}: {e}")
                results[symbol] = {
                    'symbol': symbol,
                    'error': str(e),
                    'final_score': 0.0
                }
        
        logger.info(f"✅ Final score updates completed for {len(results)} symbols")
        return results

# Global instance for easy access
scoring_system = ZmartBotScoringSystem()

def calculate_final_score(symbol: str, risk_value: float) -> Dict[str, Any]:
    """
    Convenience function to calculate final score for a single symbol
    """
    return scoring_system.calculate_final_score(symbol, risk_value)

def update_all_scores(symbols_data: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to update all symbol scores
    """
    return scoring_system.update_all_symbols_scores(symbols_data)

if __name__ == "__main__":
    # Test the scoring system
    test_symbols = {
        'BTC': 0.544,
        'ETH': 0.647,
        'SOL': 0.723
    }
    
    print("🧪 Testing ZmartBot Scoring System")
    print("=" * 50)
    
    for symbol, risk in test_symbols.items():
        result = calculate_final_score(symbol, risk)
        print(f"\n{symbol}:")
        print(f"  Risk: {result['risk_value']:.3f}")
        print(f"  Base Score: {result['base_score']:.2f}")
        print(f"  Coefficient: {result['coefficient']:.3f}")
        print(f"  Final Score: {result['final_score']:.2f}")
        print(f"  Signal: {result['signal_strength']}")
