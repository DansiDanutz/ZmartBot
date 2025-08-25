#!/usr/bin/env python3
"""
Min/Max Calculator - The Core of RiskMetric System
This module determines the critical min (0% risk) and max (100% risk) values
for each symbol using multiple sophisticated approaches
"""

import math
import numpy as np
from scipy import stats, signal
from scipy.optimize import curve_fit
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MinMaxCalculator:
    """
    THE KEY COMPONENT: Calculates accurate min/max values for risk bands
    Uses multiple methods to ensure accuracy:
    1. Logarithmic Regression Bounds
    2. Statistical Distribution Analysis
    3. Support/Resistance Level Detection
    4. Fibonacci Retracement Levels
    5. Historical Cycle Analysis
    """
    
    def __init__(self):
        self.methods_weights = {
            'logarithmic_regression': 0.30,
            'statistical_distribution': 0.20,
            'support_resistance': 0.20,
            'fibonacci_levels': 0.15,
            'cycle_analysis': 0.15
        }
    
    def calculate_min_max(self, symbol: str, price_history: List[Dict]) -> Dict:
        """
        Master function that combines all methods to determine min/max
        This is THE MOST IMPORTANT CALCULATION in the entire system
        """
        if not price_history or len(price_history) < 100:
            logger.error(f"Insufficient data for {symbol}: {len(price_history) if price_history else 0} points")
            return {}  # Return empty dict instead of None
        
        prices = [p['close'] for p in price_history]
        dates = [p['date'] for p in price_history]
        
        logger.info(f"Calculating min/max for {symbol} with {len(prices)} data points")
        
        # Method 1: Logarithmic Regression Bounds
        log_min, log_max = self.logarithmic_regression_bounds(prices, dates)
        
        # Method 2: Statistical Distribution
        stat_min, stat_max = self.statistical_distribution_bounds(prices)
        
        # Method 3: Support/Resistance Levels
        sr_min, sr_max = self.support_resistance_bounds(prices)
        
        # Method 4: Fibonacci Levels
        fib_min, fib_max = self.fibonacci_bounds(prices)
        
        # Method 5: Cycle Analysis
        cycle_min, cycle_max = self.cycle_analysis_bounds(prices, dates)
        
        # Combine all methods with weights
        final_min = (
            log_min * self.methods_weights['logarithmic_regression'] +
            stat_min * self.methods_weights['statistical_distribution'] +
            sr_min * self.methods_weights['support_resistance'] +
            fib_min * self.methods_weights['fibonacci_levels'] +
            cycle_min * self.methods_weights['cycle_analysis']
        )
        
        final_max = (
            log_max * self.methods_weights['logarithmic_regression'] +
            stat_max * self.methods_weights['statistical_distribution'] +
            sr_max * self.methods_weights['support_resistance'] +
            fib_max * self.methods_weights['fibonacci_levels'] +
            cycle_max * self.methods_weights['cycle_analysis']
        )
        
        # Validate and adjust
        current_price = prices[-1]
        final_min, final_max = self.validate_and_adjust(final_min, final_max, current_price, prices)
        
        result = {
            'symbol': symbol,
            'min_price': final_min,
            'max_price': final_max,
            'current_price': current_price,
            'current_risk': self.calculate_risk(current_price, final_min, final_max),
            'methods': {
                'logarithmic_regression': {'min': log_min, 'max': log_max},
                'statistical_distribution': {'min': stat_min, 'max': stat_max},
                'support_resistance': {'min': sr_min, 'max': sr_max},
                'fibonacci_levels': {'min': fib_min, 'max': fib_max},
                'cycle_analysis': {'min': cycle_min, 'max': cycle_max}
            },
            'confidence_score': self.calculate_confidence(prices, final_min, final_max),
            'last_updated': datetime.now()
        }
        
        logger.info(f"{symbol} Min/Max calculated: ${final_min:.2f} - ${final_max:.2f} (Risk: {result['current_risk']:.2%})")
        
        return result
    
    def logarithmic_regression_bounds(self, prices: List[float], dates: List[datetime]) -> Tuple[float, float]:
        """
        Benjamin Cowen's primary method: Logarithmic regression with bands
        This is the foundation of the risk metric system
        """
        # Convert dates to days since start
        start_date = min(dates)
        days = [(d - start_date).days + 1 for d in dates]  # +1 to avoid log(0)
        
        # Filter valid data
        valid_data = [(d, p) for d, p in zip(days, prices) if p > 0 and d > 0]
        if len(valid_data) < 10:
            return min(prices), max(prices)
        
        days_valid, prices_valid = zip(*valid_data)
        
        # Logarithmic transformation
        log_days = np.log(days_valid)
        log_prices = np.log(prices_valid)
        
        # Linear regression on log-transformed data
        result = stats.linregress(log_days, log_prices)
        slope = result.slope  # type: ignore
        intercept = result.intercept  # type: ignore
        r_value = result.rvalue  # type: ignore
        
        # Calculate predicted values
        predicted_log_prices = slope * log_days + intercept
        
        # Calculate residuals (deviation from regression line)
        residuals = log_prices - predicted_log_prices
        
        # Standard deviation of residuals
        std_residual = np.std(residuals)
        
        # Min/Max using 2 standard deviations (95% confidence)
        # This captures the natural volatility range
        current_day = max(days_valid)
        log_current = np.log(current_day)
        
        # Central regression value at current time
        central_log_price = slope * log_current + intercept
        
        # Min is regression - 2*std, Max is regression + 2*std
        min_log_price = central_log_price - 2 * std_residual
        max_log_price = central_log_price + 2 * std_residual
        
        # Convert back from log space
        min_price = np.exp(min_log_price)
        max_price = np.exp(max_log_price)
        
        # Alternative: Use percentile of actual residuals for more accurate bounds
        min_residual_percentile = np.percentile(residuals, 5)  # 5th percentile
        max_residual_percentile = np.percentile(residuals, 95)  # 95th percentile
        
        alt_min_price = np.exp(central_log_price + min_residual_percentile)
        alt_max_price = np.exp(central_log_price + max_residual_percentile)
        
        # Use the tighter bounds for more accurate risk calculation
        final_min = max(min_price, alt_min_price)
        final_max = min(max_price, alt_max_price)
        
        logger.debug(f"Logarithmic regression: R²={r_value**2:.3f}, Min=${final_min:.2f}, Max=${final_max:.2f}")
        
        return final_min, final_max
    
    def statistical_distribution_bounds(self, prices: List[float]) -> Tuple[float, float]:
        """
        Statistical approach using distribution analysis
        Assumes prices follow a log-normal distribution
        """
        # Log transform for normality
        log_prices = np.log(prices)
        
        # Calculate mean and standard deviation
        mean_log = np.mean(log_prices)
        std_log = np.std(log_prices)
        
        # Use 2.5 standard deviations for bounds (99% coverage)
        min_log = mean_log - 2.5 * std_log
        max_log = mean_log + 2.5 * std_log
        
        # Convert back to price space
        min_price = np.exp(min_log)
        max_price = np.exp(max_log)
        
        # Apply Bollinger Band concept for dynamic adjustment
        recent_prices = prices[-20:] if len(prices) > 20 else prices
        recent_mean = np.mean(recent_prices)
        recent_std = np.std(recent_prices)
        
        # Adjust bounds based on recent volatility
        volatility_factor = recent_std / np.std(prices)
        min_price *= (1 - 0.1 * volatility_factor)  # Expand if volatile
        max_price *= (1 + 0.1 * volatility_factor)
        
        return min_price, max_price
    
    def support_resistance_bounds(self, prices: List[float]) -> Tuple[float, float]:
        """
        Identify major support and resistance levels
        These often act as psychological min/max boundaries
        """
        # Find local minima and maxima
        prices_array = np.array(prices)
        
        # Use scipy to find peaks (resistance) and troughs (support)
        peaks, _ = signal.find_peaks(prices_array, distance=20, prominence=np.std(prices_array)*0.5)
        troughs, _ = signal.find_peaks(-prices_array, distance=20, prominence=np.std(prices_array)*0.5)
        
        if len(peaks) > 0 and len(troughs) > 0:
            # Major resistance levels
            resistance_levels = prices_array[peaks]
            major_resistance = np.percentile(resistance_levels, 90)  # Top 10% of peaks
            
            # Major support levels
            support_levels = prices_array[troughs]
            major_support = np.percentile(support_levels, 10)  # Bottom 10% of troughs
            
            # Extend slightly beyond historical levels
            min_price = major_support * 0.95
            max_price = major_resistance * 1.05
        else:
            # Fallback to simple percentiles
            min_price = np.percentile(prices, 5)
            max_price = np.percentile(prices, 95)
        
        return float(min_price), float(max_price)
    
    def fibonacci_bounds(self, prices: List[float]) -> Tuple[float, float]:
        """
        Use Fibonacci retracement levels for natural boundaries
        These are psychologically important levels in trading
        """
        historical_min = min(prices)
        historical_max = max(prices)
        range_size = historical_max - historical_min
        
        # Key Fibonacci levels
        fib_levels = {
            0.0: historical_min,
            0.236: historical_min + range_size * 0.236,
            0.382: historical_min + range_size * 0.382,
            0.5: historical_min + range_size * 0.5,
            0.618: historical_min + range_size * 0.618,
            0.786: historical_min + range_size * 0.786,
            1.0: historical_max,
            1.272: historical_max + range_size * 0.272,  # Extension
            1.618: historical_max + range_size * 0.618   # Golden ratio extension
        }
        
        # Use 0% and 127.2% extension as bounds
        # This gives room for natural price movement beyond historical range
        min_price = fib_levels[0.0] * 0.9  # 10% below historical min
        max_price = fib_levels[1.272]       # 127.2% Fibonacci extension
        
        return min_price, max_price
    
    def cycle_analysis_bounds(self, prices: List[float], dates: List[datetime]) -> Tuple[float, float]:
        """
        Analyze market cycles to predict future bounds
        Based on the idea that markets move in cycles
        """
        # Identify cycle length using autocorrelation
        prices_array = np.array(prices)
        
        # Detrend the data
        x = np.arange(len(prices))
        z = np.polyfit(x, prices_array, 1)
        p = np.poly1d(z)
        detrended = prices_array - p(x)
        
        # Find dominant cycle using FFT
        fft = np.fft.fft(detrended)
        frequencies = np.fft.fftfreq(len(detrended))
        
        # Get dominant frequency (excluding DC component)
        positive_freqs = frequencies[1:len(frequencies)//2]
        fft_magnitude = np.abs(fft[1:len(fft)//2])
        
        if len(fft_magnitude) > 0:
            dominant_freq_idx = np.argmax(fft_magnitude)
            dominant_period = int(1 / positive_freqs[dominant_freq_idx]) if positive_freqs[dominant_freq_idx] != 0 else len(prices)
        else:
            dominant_period = len(prices)
        
        # Analyze cycles
        cycle_mins = []
        cycle_maxs = []
        
        for i in range(0, len(prices) - dominant_period, dominant_period // 2):
            cycle_data = prices[i:i+dominant_period]
            if len(cycle_data) > 0:
                cycle_mins.append(min(cycle_data))
                cycle_maxs.append(max(cycle_data))
        
        if cycle_mins and cycle_maxs:
            # Project next cycle bounds
            avg_cycle_min = np.mean(cycle_mins)
            avg_cycle_max = np.mean(cycle_maxs)
            
            # Add trend adjustment
            if len(prices) > dominant_period:
                recent_trend = (prices[-1] - prices[-dominant_period]) / prices[-dominant_period]
                min_price = avg_cycle_min * (1 + recent_trend * 0.5)
                max_price = avg_cycle_max * (1 + recent_trend * 0.5)
            else:
                min_price = avg_cycle_min
                max_price = avg_cycle_max
        else:
            # Fallback
            min_price = min(prices)
            max_price = max(prices)
        
        return float(min_price), float(max_price)
    
    def validate_and_adjust(self, min_price: float, max_price: float, 
                           current_price: float, prices: List[float]) -> Tuple[float, float]:
        """
        Validate and adjust the calculated min/max values
        Ensures they make sense given current market conditions
        """
        # Ensure min < max
        if min_price >= max_price:
            logger.warning(f"Invalid bounds: min={min_price} >= max={max_price}. Using historical range.")
            min_price = min(prices) * 0.9
            max_price = max(prices) * 1.1
        
        # Ensure current price is within reasonable range
        if current_price < min_price:
            # Current price below min - adjust min but keep some buffer
            logger.info(f"Current price ${current_price:.2f} below min ${min_price:.2f}. Adjusting min.")
            min_price = current_price * 0.95
        
        if current_price > max_price:
            # Current price above max - adjust max but keep some buffer
            logger.info(f"Current price ${current_price:.2f} above max ${max_price:.2f}. Adjusting max.")
            max_price = current_price * 1.05
        
        # Ensure reasonable spread (at least 20% range)
        min_spread = current_price * 0.2
        if (max_price - min_price) < min_spread:
            logger.info(f"Spread too narrow. Expanding to minimum 20% range.")
            center = (min_price + max_price) / 2
            min_price = center * 0.9
            max_price = center * 1.1
        
        # Cap at reasonable multiples of current price
        # Min shouldn't be less than 20% of current
        # Max shouldn't be more than 5x current
        min_price = max(min_price, current_price * 0.2)
        max_price = min(max_price, current_price * 5.0)
        
        return min_price, max_price
    
    def calculate_risk(self, price: float, min_price: float, max_price: float) -> float:
        """
        Calculate risk value (0-1) using logarithmic scale
        This is Benjamin Cowen's formula
        """
        if price <= min_price:
            return 0.0
        elif price >= max_price:
            return 1.0
        else:
            # Logarithmic interpolation
            log_price = math.log(price)
            log_min = math.log(min_price)
            log_max = math.log(max_price)
            
            risk = (log_price - log_min) / (log_max - log_min)
            return max(0.0, min(1.0, risk))
    
    def calculate_confidence(self, prices: List[float], min_price: float, max_price: float) -> float:
        """
        Calculate confidence score for the min/max calculation
        Higher score means more reliable bounds
        """
        confidence_factors = []
        
        # Factor 1: Data sufficiency (more data = higher confidence)
        data_score = min(1.0, len(prices) / 1000)  # Max confidence at 1000+ data points
        confidence_factors.append(data_score)
        
        # Factor 2: How well current price fits within bounds
        current_price = prices[-1]
        current_risk = self.calculate_risk(current_price, min_price, max_price)
        position_score = 1.0 - abs(current_risk - 0.5) * 2  # Best at 50% risk
        confidence_factors.append(position_score)
        
        # Factor 3: Historical coverage (what % of historical prices fall within bounds)
        within_bounds = sum(1 for p in prices if min_price <= p <= max_price)
        coverage_score = within_bounds / len(prices)
        confidence_factors.append(coverage_score)
        
        # Factor 4: Stability of recent calculations (low volatility in bounds)
        recent_prices = prices[-30:] if len(prices) > 30 else prices
        recent_volatility = np.std(recent_prices) / np.mean(recent_prices)
        stability_score = max(0, 1 - recent_volatility * 10)  # Lower volatility = higher confidence
        confidence_factors.append(stability_score)
        
        # Overall confidence is the geometric mean
        confidence = np.prod(confidence_factors) ** (1 / len(confidence_factors))
        
        return float(confidence)
    
    def update_bounds_incrementally(self, symbol: str, current_bounds: Dict, 
                                   new_prices: List[float]) -> Dict:
        """
        Update min/max bounds incrementally with new price data
        This is used for continuous learning without full recalculation
        """
        current_min = current_bounds['min_price']
        current_max = current_bounds['max_price']
        
        # Calculate impact of new prices
        new_min = min(new_prices)
        new_max = max(new_prices)
        
        # Exponential moving average for smooth updates
        alpha = 0.05  # Learning rate
        
        if new_min < current_min:
            # Price broke below min - expand lower bound
            updated_min = new_min * 0.95  # Add 5% buffer
        else:
            # Slowly contract min if prices stay above
            updated_min = current_min * (1 - alpha) + new_min * alpha
        
        if new_max > current_max:
            # Price broke above max - expand upper bound
            updated_max = new_max * 1.05  # Add 5% buffer
        else:
            # Slowly contract max if prices stay below
            updated_max = current_max * (1 - alpha) + new_max * alpha
        
        return {
            'symbol': symbol,
            'min_price': updated_min,
            'max_price': updated_max,
            'last_updated': datetime.now(),
            'update_type': 'incremental'
        }

# Global instance
min_max_calculator = MinMaxCalculator()