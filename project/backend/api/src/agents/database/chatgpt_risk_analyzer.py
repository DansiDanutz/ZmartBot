#!/usr/bin/env python3
"""
ChatGPT Risk Analyzer for RiskMetric Database Agent
==================================================

This module integrates with OpenAI's ChatGPT API to:
1. Find symbol ratios and price data
2. Generate polynomial coefficients
3. Analyze market data for any symbol
4. Provide accurate risk modeling
"""

import openai
import json
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class SymbolAnalysis:
    """Data class for symbol analysis results"""
    symbol: str
    min_price: float
    max_price: float
    polynomial_coeffs: List[float]
    confidence_score: float
    analysis_notes: str

class ChatGPTRiskAnalyzer:
    """ChatGPT API integration for RiskMetric analysis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
    def analyze_symbol_risk_data(self, symbol: str) -> SymbolAnalysis:
        """
        Use ChatGPT to analyze symbol and find risk-based price data
        
        Args:
            symbol: Symbol to analyze (e.g., 'ADA', 'ETH')
            
        Returns:
            SymbolAnalysis with min/max prices and polynomial coefficients
        """
        
        prompt = f"""
        Analyze {symbol} cryptocurrency and provide risk-based price modeling data.
        
        Requirements:
        1. Find realistic min price (Risk 0) and max price (Risk 1) for {symbol}
        2. Generate 41 price points from Risk 0 to Risk 1
        3. Fit a 4th-degree polynomial to the data
        4. Provide polynomial coefficients [c4, c3, c2, c1, c0]
        
        Format your response as JSON:
        {{
            "symbol": "{symbol}",
            "min_price": 0.0,
            "max_price": 0.0,
            "price_points": [
                {{"risk": 0.0, "price": 0.0}},
                {{"risk": 0.025, "price": 0.0}},
                ...
                {{"risk": 1.0, "price": 0.0}}
            ],
            "polynomial_coeffs": [c4, c3, c2, c1, c0],
            "confidence_score": 0.95,
            "analysis_notes": "Brief analysis notes"
        }}
        
        Use realistic market data and ensure the polynomial fits well.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a cryptocurrency risk analyst. Provide accurate, realistic price data and polynomial coefficients."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse ChatGPT response
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("No content received from ChatGPT")
            data = json.loads(content)
            
            # Create SymbolAnalysis object
            analysis = SymbolAnalysis(
                symbol=data["symbol"],
                min_price=data["min_price"],
                max_price=data["max_price"],
                polynomial_coeffs=data["polynomial_coeffs"],
                confidence_score=data["confidence_score"],
                analysis_notes=data["analysis_notes"]
            )
            
            self.logger.info(f"ChatGPT analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"ChatGPT API error for {symbol}: {e}")
            raise
    
    def validate_polynomial_fit(self, risk_values: List[float], 
                               price_values: List[float], 
                               coeffs: List[float]) -> float:
        """
        Validate polynomial fit quality
        
        Args:
            risk_values: List of risk values (0 to 1)
            price_values: List of actual price values
            coeffs: Polynomial coefficients [c4, c3, c2, c1, c0]
            
        Returns:
            R-squared value (0 to 1, higher is better)
        """
        
        # Create polynomial model
        poly = np.poly1d(coeffs[::-1])  # Reverse for np.poly1d order
        
        # Calculate predicted values
        predicted = [poly(risk) for risk in risk_values]
        
        # Calculate R-squared
        ss_res = sum((np.array(price_values) - np.array(predicted)) ** 2)
        ss_tot = sum((np.array(price_values) - np.mean(price_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        return r_squared
    
    def estimate_price_from_risk(self, symbol: str, risk: float, 
                                coeffs: List[float]) -> float:
        """
        Estimate price from risk using polynomial coefficients
        
        Args:
            symbol: Symbol name
            risk: Risk value (0 to 1)
            coeffs: Polynomial coefficients [c4, c3, c2, c1, c0]
            
        Returns:
            Estimated price
        """
        
        if not (0 <= risk <= 1):
            raise ValueError("Risk must be between 0 and 1")
        
        # Create polynomial model
        poly = np.poly1d(coeffs[::-1])  # Reverse for np.poly1d order
        
        # Calculate price
        price = poly(risk)
        
        return max(0, price)  # Ensure non-negative price
    
    def estimate_risk_from_price(self, symbol: str, price: float,
                                min_price: float, max_price: float) -> float:
        """
        Estimate risk from price using linear interpolation
        
        Args:
            symbol: Symbol name
            price: Current price
            min_price: Min price (Risk 0)
            max_price: Max price (Risk 1)
            
        Returns:
            Estimated risk (0 to 1)
        """
        
        if price <= min_price:
            return 0.0
        elif price >= max_price:
            return 1.0
        else:
            return (price - min_price) / (max_price - min_price)

# Example usage
if __name__ == "__main__":
    # Initialize with your OpenAI API key
    api_key = "your-openai-api-key-here"
    analyzer = ChatGPTRiskAnalyzer(api_key)
    
    # Analyze a symbol
    try:
        analysis = analyzer.analyze_symbol_risk_data("ADA")
        print(f"Analysis for {analysis.symbol}:")
        print(f"Min Price: ${analysis.min_price:.4f}")
        print(f"Max Price: ${analysis.max_price:.4f}")
        print(f"Polynomial Coefficients: {analysis.polynomial_coeffs}")
        print(f"Confidence Score: {analysis.confidence_score:.2f}")
        print(f"Notes: {analysis.analysis_notes}")
        
        # Test price estimation
        test_risk = 0.5
        estimated_price = analyzer.estimate_price_from_risk(
            analysis.symbol, test_risk, analysis.polynomial_coeffs
        )
        print(f"Price at Risk {test_risk}: ${estimated_price:.4f}")
        
    except Exception as e:
        print(f"Error: {e}") 