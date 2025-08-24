#!/usr/bin/env python3
"""
Technical Indicators Engine
Implements all 10 key technical indicators for pattern detection
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

try:
    import talib  # type: ignore
    TALIB_AVAILABLE = True
except ImportError:
    talib = None
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not installed. Some technical indicators will use fallback implementations.")

logger = logging.getLogger(__name__)

class TechnicalIndicatorsEngine:
    """
    Comprehensive technical indicators calculator
    Implements all 10 key indicators for crypto pattern analysis
    """
    
    def __init__(self):
        self.indicator_weights = {
            'ema_cross': 0.15,
            'rsi': 0.12,
            'macd': 0.12,
            'volume_profile': 0.10,
            'bollinger_bands': 0.10,
            'fibonacci': 0.08,
            'ichimoku': 0.10,
            'stochastic_rsi': 0.08,
            'divergence': 0.10,
            'support_resistance': 0.05
        }
        
        logger.info("Technical Indicators Engine initialized")
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all 10 technical indicators
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            Dictionary with all indicator values and signals
        """
        
        indicators = {}
        
        try:
            # 1. EMA Crossovers
            indicators['ema'] = self.calculate_ema_crossovers(df)
            
            # 2. RSI
            indicators['rsi'] = self.calculate_rsi(df)
            
            # 3. MACD
            indicators['macd'] = self.calculate_macd(df)
            
            # 4. Volume Profile / OBV
            indicators['volume'] = self.calculate_volume_indicators(df)
            
            # 5. Bollinger Bands
            indicators['bollinger'] = self.calculate_bollinger_bands(df)
            
            # 6. Fibonacci Retracement
            indicators['fibonacci'] = self.calculate_fibonacci_levels(df)
            
            # 7. Ichimoku Cloud
            indicators['ichimoku'] = self.calculate_ichimoku(df)
            
            # 8. Stochastic RSI
            indicators['stoch_rsi'] = self.calculate_stochastic_rsi(df)
            
            # 9. Divergence Analysis
            indicators['divergence'] = self.calculate_divergences(df, indicators)
            
            # 10. Support/Resistance
            indicators['support_resistance'] = self.calculate_support_resistance(df)
            
            # Combination patterns
            indicators['combinations'] = self.detect_combination_patterns(indicators)
            
            # Overall scores
            indicators['overall'] = self.calculate_overall_scores(indicators)
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
        
        return indicators
    
    def calculate_ema_crossovers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        1. EMA Crossovers (Golden Cross / Death Cross)
        """
        
        result = {}
        
        try:
            # Calculate EMAs
            if TALIB_AVAILABLE and talib is not None:
                result['ema_9'] = talib.EMA(df['close'], timeperiod=9)  # type: ignore
                result['ema_21'] = talib.EMA(df['close'], timeperiod=21)  # type: ignore
                result['ema_20'] = talib.EMA(df['close'], timeperiod=20)  # type: ignore
                result['ema_50'] = talib.EMA(df['close'], timeperiod=50)  # type: ignore
                result['ema_200'] = talib.EMA(df['close'], timeperiod=200)  # type: ignore
            else:
                # Fallback to pandas EWM
                result['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
                result['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
                result['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
                result['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
                result['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
            
            # Detect crossovers
            current_9 = result['ema_9'].iloc[-1]
            current_21 = result['ema_21'].iloc[-1]
            current_50 = result['ema_50'].iloc[-1]
            current_200 = result['ema_200'].iloc[-1] if len(df) >= 200 else None
            
            prev_9 = result['ema_9'].iloc[-2]
            prev_21 = result['ema_21'].iloc[-2]
            prev_50 = result['ema_50'].iloc[-2]
            
            # Golden Cross / Death Cross (50/200)
            if current_200:
                if current_50 > current_200 and prev_50 <= result['ema_200'].iloc[-2]:
                    result['signal'] = 'golden_cross'
                    result['signal_strength'] = 'strong'
                elif current_50 < current_200 and prev_50 >= result['ema_200'].iloc[-2]:
                    result['signal'] = 'death_cross'
                    result['signal_strength'] = 'strong'
            
            # Short-term crosses (9/21)
            if current_9 > current_21 and prev_9 <= prev_21:
                result['short_signal'] = 'bullish_cross'
                result['short_strength'] = 'moderate'
            elif current_9 < current_21 and prev_9 >= prev_21:
                result['short_signal'] = 'bearish_cross'
                result['short_strength'] = 'moderate'
            
            # Trend direction
            if current_9 > current_21 > current_50:
                result['trend'] = 'strong_uptrend'
            elif current_9 < current_21 < current_50:
                result['trend'] = 'strong_downtrend'
            else:
                result['trend'] = 'neutral'
            
            result['values'] = {
                'ema_9': current_9,
                'ema_21': current_21,
                'ema_50': current_50,
                'ema_200': current_200
            }
            
        except Exception as e:
            logger.error(f"Error calculating EMA crossovers: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_rsi(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        2. RSI - Relative Strength Index
        """
        
        result = {}
        
        try:
            # Calculate RSI
            if TALIB_AVAILABLE and talib is not None:
                result['rsi'] = talib.RSI(df['close'], timeperiod=14)  # type: ignore
            else:
                # Fallback RSI calculation
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()  # type: ignore
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()  # type: ignore
                rs = gain / loss
                result['rsi'] = 100 - (100 / (1 + rs))
            result['rsi_current'] = result['rsi'].iloc[-1]
            
            # Overbought/Oversold
            if result['rsi_current'] >= 70:
                result['signal'] = 'overbought'
                result['action'] = 'consider_sell'
            elif result['rsi_current'] <= 30:
                result['signal'] = 'oversold'
                result['action'] = 'consider_buy'
            else:
                result['signal'] = 'neutral'
                result['action'] = 'hold'
            
            # RSI Divergence
            price_trend = 'up' if df['close'].iloc[-1] > df['close'].iloc[-14] else 'down'
            rsi_trend = 'up' if result['rsi_current'] > result['rsi'].iloc[-14] else 'down'
            
            if price_trend == 'up' and rsi_trend == 'down':
                result['divergence'] = 'bearish_divergence'
                result['divergence_strength'] = 'strong'
            elif price_trend == 'down' and rsi_trend == 'up':
                result['divergence'] = 'bullish_divergence'
                result['divergence_strength'] = 'strong'
            else:
                result['divergence'] = 'none'
            
            # RSI momentum
            rsi_change = result['rsi_current'] - result['rsi'].iloc[-5]
            if abs(rsi_change) > 10:
                result['momentum'] = 'strong'
            elif abs(rsi_change) > 5:
                result['momentum'] = 'moderate'
            else:
                result['momentum'] = 'weak'
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_macd(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        3. MACD - Moving Average Convergence Divergence
        """
        
        result = {}
        
        try:
            # Calculate MACD
            if TALIB_AVAILABLE and talib is not None:
                macd, signal, histogram = talib.MACD(df['close'],   # type: ignore
                                                     fastperiod=12, 
                                                     slowperiod=26, 
                                                     signalperiod=9)
            else:
                # Fallback MACD calculation
                exp1 = df['close'].ewm(span=12, adjust=False).mean()
                exp2 = df['close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                histogram = macd - signal
            
            result['macd'] = macd
            result['signal'] = signal
            result['histogram'] = histogram
            
            current_macd = macd.iloc[-1]
            current_signal = signal.iloc[-1]
            current_hist = histogram.iloc[-1]
            
            prev_macd = macd.iloc[-2]
            prev_signal = signal.iloc[-2]
            prev_hist = histogram.iloc[-2]
            
            # MACD Cross signals
            if current_macd > current_signal and prev_macd <= prev_signal:
                result['cross_signal'] = 'bullish_cross'
                result['action'] = 'buy'
            elif current_macd < current_signal and prev_macd >= prev_signal:
                result['cross_signal'] = 'bearish_cross'
                result['action'] = 'sell'
            else:
                result['cross_signal'] = 'none'
                result['action'] = 'hold'
            
            # Zero line cross
            if current_macd > 0 and prev_macd <= 0:
                result['zero_cross'] = 'bullish'
            elif current_macd < 0 and prev_macd >= 0:
                result['zero_cross'] = 'bearish'
            else:
                result['zero_cross'] = 'none'
            
            # Histogram momentum
            if current_hist > prev_hist:
                result['momentum'] = 'increasing'
            else:
                result['momentum'] = 'decreasing'
            
            result['values'] = {
                'macd': current_macd,
                'signal': current_signal,
                'histogram': current_hist
            }
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        4. Volume Profile / OBV (On-Balance Volume)
        """
        
        result = {}
        
        try:
            # Calculate OBV
            if TALIB_AVAILABLE and talib is not None:
                result['obv'] = talib.OBV(df['close'], df['volume'])  # type: ignore
            else:
                # Fallback OBV calculation
                obv = (df['volume'] * ((df['close'] - df['close'].shift(1)) > 0).astype(int) - 
                       df['volume'] * ((df['close'] - df['close'].shift(1)) < 0).astype(int)).cumsum()
                result['obv'] = obv
            current_obv = result['obv'].iloc[-1]
            
            # Volume SMA
            result['volume_sma'] = df['volume'].rolling(window=20).mean()
            current_vol_sma = result['volume_sma'].iloc[-1]
            current_volume = df['volume'].iloc[-1]
            
            # Volume spike detection
            volume_ratio = current_volume / current_vol_sma
            if volume_ratio > 2:
                result['volume_spike'] = True
                result['spike_strength'] = 'very_strong'
            elif volume_ratio > 1.5:
                result['volume_spike'] = True
                result['spike_strength'] = 'strong'
            else:
                result['volume_spike'] = False
                result['spike_strength'] = 'normal'
            
            # OBV trend
            obv_sma = result['obv'].rolling(window=10).mean()
            if current_obv > obv_sma.iloc[-1]:
                result['obv_trend'] = 'bullish'
            else:
                result['obv_trend'] = 'bearish'
            
            # Volume-Price divergence
            price_trend = 'up' if df['close'].iloc[-1] > df['close'].iloc[-10] else 'down'
            obv_trend = 'up' if current_obv > result['obv'].iloc[-10] else 'down'
            
            if price_trend != obv_trend:
                result['divergence'] = f"{obv_trend}_volume_{price_trend}_price"
                result['divergence_warning'] = True
            else:
                result['divergence'] = 'none'
                result['divergence_warning'] = False
            
            result['values'] = {
                'obv': current_obv,
                'volume': current_volume,
                'volume_sma': current_vol_sma,
                'volume_ratio': volume_ratio
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        5. Bollinger Bands
        """
        
        result = {}
        
        try:
            # Calculate Bollinger Bands
            if TALIB_AVAILABLE and talib is not None:
                upper, middle, lower = talib.BBANDS(df['close'],   # type: ignore
                                                   timeperiod=20, 
                                                   nbdevup=2, 
                                                   nbdevdn=2)
            else:
                # Fallback Bollinger Bands calculation
                middle = df['close'].rolling(window=20).mean()
                std = df['close'].rolling(window=20).std()
                upper = middle + (std * 2)
                lower = middle - (std * 2)
            
            result['upper'] = upper
            result['middle'] = middle
            result['lower'] = lower
            
            current_price = df['close'].iloc[-1]
            current_upper = upper.iloc[-1]
            current_middle = middle.iloc[-1]
            current_lower = lower.iloc[-1]
            
            # Band width (volatility)
            band_width = (current_upper - current_lower) / current_middle
            result['band_width'] = band_width
            
            # Squeeze detection
            recent_widths = [(upper.iloc[i] - lower.iloc[i]) / middle.iloc[i] 
                           for i in range(-20, 0)]
            avg_width = np.mean(recent_widths)
            
            if band_width < avg_width * 0.7:
                result['squeeze'] = True
                result['squeeze_strength'] = 'tight'
            elif band_width < avg_width * 0.85:
                result['squeeze'] = True
                result['squeeze_strength'] = 'moderate'
            else:
                result['squeeze'] = False
            
            # Band position
            position_in_band = (current_price - current_lower) / (current_upper - current_lower)
            
            if position_in_band > 1:
                result['signal'] = 'above_upper'
                result['action'] = 'overbought'
            elif position_in_band < 0:
                result['signal'] = 'below_lower'
                result['action'] = 'oversold'
            elif position_in_band > 0.8:
                result['signal'] = 'near_upper'
                result['action'] = 'watch_reversal'
            elif position_in_band < 0.2:
                result['signal'] = 'near_lower'
                result['action'] = 'watch_bounce'
            else:
                result['signal'] = 'middle_band'
                result['action'] = 'neutral'
            
            result['values'] = {
                'upper': current_upper,
                'middle': current_middle,
                'lower': current_lower,
                'price': current_price,
                'position_in_band': position_in_band
            }
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_fibonacci_levels(self, df: pd.DataFrame, lookback: int = 50) -> Dict[str, Any]:
        """
        6. Fibonacci Retracement / Extensions
        """
        
        result = {}
        
        try:
            # Find recent high and low
            recent_data = df.tail(lookback)
            high_price = recent_data['high'].max()
            low_price = recent_data['low'].min()
            
            # Calculate Fibonacci levels
            diff = high_price - low_price
            
            levels = {
                '0.0': high_price,
                '0.236': high_price - diff * 0.236,
                '0.382': high_price - diff * 0.382,
                '0.500': high_price - diff * 0.500,
                '0.618': high_price - diff * 0.618,
                '0.786': high_price - diff * 0.786,
                '1.000': low_price,
                # Extensions
                '1.618': low_price - diff * 0.618,
                '2.618': low_price - diff * 1.618
            }
            
            result['levels'] = levels
            
            current_price = df['close'].iloc[-1]
            
            # Find nearest Fibonacci level
            nearest_level = None
            min_distance = float('inf')
            
            for level_name, level_price in levels.items():
                distance = abs(current_price - level_price)
                if distance < min_distance:
                    min_distance = distance
                    nearest_level = level_name
            
            result['nearest_level'] = nearest_level
            result['distance_to_level'] = min_distance
            
            # Determine if at key level
            key_levels = ['0.382', '0.500', '0.618']
            if nearest_level in key_levels and min_distance < diff * 0.02:
                result['at_key_level'] = True
                result['signal'] = f'at_fib_{nearest_level}'
                
                # Determine bounce or break
                if current_price > levels[nearest_level]:
                    result['action'] = 'watch_resistance'
                else:
                    result['action'] = 'watch_support'
            else:
                result['at_key_level'] = False
                result['signal'] = 'between_levels'
            
            # Trend direction relative to Fibonacci
            if current_price > levels['0.618']:
                result['trend'] = 'bullish'
            elif current_price < levels['0.382']:
                result['trend'] = 'bearish'
            else:
                result['trend'] = 'neutral'
            
        except Exception as e:
            logger.error(f"Error calculating Fibonacci levels: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_ichimoku(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        7. Ichimoku Cloud
        """
        
        result = {}
        
        try:
            # Calculate Ichimoku components
            high_9 = df['high'].rolling(window=9).max()
            low_9 = df['low'].rolling(window=9).min()
            tenkan_sen = (high_9 + low_9) / 2  # Conversion Line
            
            high_26 = df['high'].rolling(window=26).max()
            low_26 = df['low'].rolling(window=26).min()
            kijun_sen = (high_26 + low_26) / 2  # Base Line
            
            # Leading Span A (Senkou Span A)
            senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
            
            # Leading Span B (Senkou Span B)
            high_52 = df['high'].rolling(window=52).max()
            low_52 = df['low'].rolling(window=52).min()
            senkou_span_b = ((high_52 + low_52) / 2).shift(26)
            
            # Lagging Span (Chikou Span)
            chikou_span = df['close'].shift(-26)
            
            result['tenkan_sen'] = tenkan_sen
            result['kijun_sen'] = kijun_sen
            result['senkou_span_a'] = senkou_span_a
            result['senkou_span_b'] = senkou_span_b
            result['chikou_span'] = chikou_span
            
            # Current values
            current_price = df['close'].iloc[-1]
            current_tenkan = tenkan_sen.iloc[-1]
            current_kijun = kijun_sen.iloc[-1]
            current_span_a = senkou_span_a.iloc[-1] if not pd.isna(senkou_span_a.iloc[-1]) else 0
            current_span_b = senkou_span_b.iloc[-1] if not pd.isna(senkou_span_b.iloc[-1]) else 0
            
            # TK Cross
            if current_tenkan > current_kijun and tenkan_sen.iloc[-2] <= kijun_sen.iloc[-2]:
                result['tk_cross'] = 'bullish'
            elif current_tenkan < current_kijun and tenkan_sen.iloc[-2] >= kijun_sen.iloc[-2]:
                result['tk_cross'] = 'bearish'
            else:
                result['tk_cross'] = 'none'
            
            # Kumo (Cloud) analysis
            cloud_top = max(current_span_a, current_span_b)
            cloud_bottom = min(current_span_a, current_span_b)
            
            if current_price > cloud_top:
                result['kumo_breakout'] = 'above_cloud'
                result['signal'] = 'bullish'
            elif current_price < cloud_bottom:
                result['kumo_breakout'] = 'below_cloud'
                result['signal'] = 'bearish'
            else:
                result['kumo_breakout'] = 'inside_cloud'
                result['signal'] = 'neutral'
            
            # Cloud thickness (volatility indicator)
            cloud_thickness = cloud_top - cloud_bottom
            result['cloud_thickness'] = cloud_thickness
            
            # Future cloud (26 periods ahead)
            future_span_a = senkou_span_a.iloc[-26] if len(senkou_span_a) >= 26 else None
            future_span_b = senkou_span_b.iloc[-26] if len(senkou_span_b) >= 26 else None
            
            if future_span_a and future_span_b:
                if future_span_a > future_span_b:
                    result['future_cloud'] = 'bullish'
                else:
                    result['future_cloud'] = 'bearish'
            
            result['values'] = {
                'price': current_price,
                'tenkan': current_tenkan,
                'kijun': current_kijun,
                'span_a': current_span_a,
                'span_b': current_span_b
            }
            
        except Exception as e:
            logger.error(f"Error calculating Ichimoku: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_stochastic_rsi(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        8. Stochastic RSI
        """
        
        result = {}
        
        try:
            # Calculate RSI first
            if TALIB_AVAILABLE and talib is not None:
                rsi = talib.RSI(df['close'], timeperiod=14)  # type: ignore
            else:
                # Fallback RSI calculation
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()  # type: ignore
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()  # type: ignore
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
            
            # Calculate Stochastic RSI
            stoch_rsi = (rsi - rsi.rolling(window=14).min()) / (rsi.rolling(window=14).max() - rsi.rolling(window=14).min())
            
            # K line (3-period SMA of Stoch RSI)
            k_line = stoch_rsi.rolling(window=3).mean() * 100
            
            # D line (3-period SMA of K)
            d_line = k_line.rolling(window=3).mean()
            
            result['k'] = k_line
            result['d'] = d_line
            
            current_k = k_line.iloc[-1]
            current_d = d_line.iloc[-1]
            prev_k = k_line.iloc[-2]
            prev_d = d_line.iloc[-2]
            
            # Overbought/Oversold
            if current_k >= 80:
                result['signal'] = 'overbought'
                result['action'] = 'consider_sell'
            elif current_k <= 20:
                result['signal'] = 'oversold'
                result['action'] = 'consider_buy'
            else:
                result['signal'] = 'neutral'
            
            # Crossover signals
            if current_k > current_d and prev_k <= prev_d:
                result['crossover'] = 'bullish'
                if current_k < 20:
                    result['crossover_strength'] = 'strong'
                else:
                    result['crossover_strength'] = 'moderate'
            elif current_k < current_d and prev_k >= prev_d:
                result['crossover'] = 'bearish'
                if current_k > 80:
                    result['crossover_strength'] = 'strong'
                else:
                    result['crossover_strength'] = 'moderate'
            else:
                result['crossover'] = 'none'
            
            result['values'] = {
                'k': current_k,
                'd': current_d
            }
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic RSI: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_divergences(self, df: pd.DataFrame, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """
        9. Divergence Analysis (Price vs Oscillators)
        """
        
        result = {}
        
        try:
            # Price trend
            lookback = 14
            current_price = df['close'].iloc[-1]
            past_price = df['close'].iloc[-lookback]
            price_trend = 'up' if current_price > past_price else 'down'
            
            divergences = []
            
            # RSI Divergence
            if 'rsi' in indicators and 'rsi' in indicators['rsi']:
                current_rsi = indicators['rsi']['rsi_current']
                past_rsi = indicators['rsi']['rsi'].iloc[-lookback]
                rsi_trend = 'up' if current_rsi > past_rsi else 'down'
                
                if price_trend == 'up' and rsi_trend == 'down':
                    divergences.append({
                        'type': 'bearish_divergence',
                        'indicator': 'RSI',
                        'strength': 'strong'
                    })
                elif price_trend == 'down' and rsi_trend == 'up':
                    divergences.append({
                        'type': 'bullish_divergence',
                        'indicator': 'RSI',
                        'strength': 'strong'
                    })
            
            # MACD Divergence
            if 'macd' in indicators and 'histogram' in indicators['macd']:
                current_hist = indicators['macd']['histogram'].iloc[-1]
                past_hist = indicators['macd']['histogram'].iloc[-lookback]
                macd_trend = 'up' if current_hist > past_hist else 'down'
                
                if price_trend == 'up' and macd_trend == 'down':
                    divergences.append({
                        'type': 'bearish_divergence',
                        'indicator': 'MACD',
                        'strength': 'moderate'
                    })
                elif price_trend == 'down' and macd_trend == 'up':
                    divergences.append({
                        'type': 'bullish_divergence',
                        'indicator': 'MACD',
                        'strength': 'moderate'
                    })
            
            # OBV Divergence
            if 'volume' in indicators and 'obv' in indicators['volume']:
                current_obv = indicators['volume']['obv'].iloc[-1]
                past_obv = indicators['volume']['obv'].iloc[-lookback]
                obv_trend = 'up' if current_obv > past_obv else 'down'
                
                if price_trend == 'up' and obv_trend == 'down':
                    divergences.append({
                        'type': 'bearish_divergence',
                        'indicator': 'OBV',
                        'strength': 'strong'
                    })
                elif price_trend == 'down' and obv_trend == 'up':
                    divergences.append({
                        'type': 'bullish_divergence',
                        'indicator': 'OBV',
                        'strength': 'strong'
                    })
            
            result['divergences'] = divergences
            result['price_trend'] = price_trend
            
            # Overall divergence signal
            if divergences:
                bullish_count = sum(1 for d in divergences if 'bullish' in d['type'])
                bearish_count = sum(1 for d in divergences if 'bearish' in d['type'])
                
                if bullish_count > bearish_count:
                    result['overall_signal'] = 'bullish_divergence'
                    result['confidence'] = bullish_count / len(divergences)
                elif bearish_count > bullish_count:
                    result['overall_signal'] = 'bearish_divergence'
                    result['confidence'] = bearish_count / len(divergences)
                else:
                    result['overall_signal'] = 'mixed'
                    result['confidence'] = 0.5
            else:
                result['overall_signal'] = 'no_divergence'
                result['confidence'] = 0
            
        except Exception as e:
            logger.error(f"Error calculating divergences: {e}")
            result['error'] = str(e)
        
        return result
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict[str, Any]:
        """
        10. Support/Resistance Levels with Candle Patterns
        """
        
        result = {}
        
        try:
            # Find support and resistance levels using pivot points
            highs = df['high'].rolling(window=window).max()
            lows = df['low'].rolling(window=window).min()
            
            # Identify local maxima and minima
            resistance_levels = []
            support_levels = []
            
            for i in range(window, len(df) - window):
                # Resistance (local high)
                if df['high'].iloc[i] == highs.iloc[i]:
                    resistance_levels.append(df['high'].iloc[i])
                
                # Support (local low)
                if df['low'].iloc[i] == lows.iloc[i]:
                    support_levels.append(df['low'].iloc[i])
            
            # Remove duplicates and sort
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]
            support_levels = sorted(list(set(support_levels)))[:5]
            
            result['resistance_levels'] = resistance_levels
            result['support_levels'] = support_levels
            
            current_price = df['close'].iloc[-1]
            
            # Find nearest support and resistance
            nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price)) if resistance_levels else None
            nearest_support = min(support_levels, key=lambda x: abs(x - current_price)) if support_levels else None
            
            result['nearest_resistance'] = nearest_resistance
            result['nearest_support'] = nearest_support
            
            # Check for breakouts
            prev_close = df['close'].iloc[-2]
            
            if nearest_resistance and current_price > nearest_resistance and prev_close <= nearest_resistance:
                result['breakout'] = 'resistance_break'
                result['signal'] = 'bullish'
            elif nearest_support and current_price < nearest_support and prev_close >= nearest_support:
                result['breakout'] = 'support_break'
                result['signal'] = 'bearish'
            else:
                result['breakout'] = 'none'
                result['signal'] = 'neutral'
            
            # Detect candle patterns
            candle_patterns = self._detect_candle_patterns(df)
            result['candle_patterns'] = candle_patterns
            
            # Combine S/R with candle patterns
            if candle_patterns and nearest_resistance:
                for pattern in candle_patterns:
                    if 'bearish' in pattern['type'] and abs(current_price - nearest_resistance) < nearest_resistance * 0.01:
                        result['combined_signal'] = 'bearish_reversal_at_resistance'
                        result['confidence'] = 'high'
                        break
            
            if candle_patterns and nearest_support:
                for pattern in candle_patterns:
                    if 'bullish' in pattern['type'] and abs(current_price - nearest_support) < nearest_support * 0.01:
                        result['combined_signal'] = 'bullish_reversal_at_support'
                        result['confidence'] = 'high'
                        break
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            result['error'] = str(e)
        
        return result
    
    def _detect_candle_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect candlestick patterns"""
        
        patterns = []
        
        try:
            # Use TA-Lib candle pattern functions if available
            if TALIB_AVAILABLE and talib is not None:
                # Engulfing patterns
                engulfing = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])  # type: ignore
                if engulfing.iloc[-1] > 0:
                    patterns.append({'type': 'bullish_engulfing', 'strength': 'strong'})
                elif engulfing.iloc[-1] < 0:
                    patterns.append({'type': 'bearish_engulfing', 'strength': 'strong'})
                
                # Hammer/Shooting Star
                hammer = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])  # type: ignore
                if hammer.iloc[-1] > 0:
                    patterns.append({'type': 'hammer', 'strength': 'moderate'})
                
                shooting_star = talib.CDLSHOOTINGSTAR(df['open'], df['high'], df['low'], df['close'])  # type: ignore
                if shooting_star.iloc[-1] > 0:
                    patterns.append({'type': 'shooting_star', 'strength': 'moderate'})
                
                # Doji
                doji = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])  # type: ignore
                if doji.iloc[-1] > 0:
                    patterns.append({'type': 'doji', 'strength': 'weak'})
            else:
                # Fallback pattern detection with simple calculations
                # Engulfing detection
                if len(df) >= 2:
                    prev_body = abs(df['close'].iloc[-2] - df['open'].iloc[-2])
                    curr_body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
                    
                    # Bullish engulfing
                    if (df['close'].iloc[-2] < df['open'].iloc[-2] and  # Previous was bearish
                        df['close'].iloc[-1] > df['open'].iloc[-1] and  # Current is bullish
                        df['open'].iloc[-1] < df['close'].iloc[-2] and  # Opens below prev close
                        df['close'].iloc[-1] > df['open'].iloc[-2]):    # Closes above prev open
                        patterns.append({'type': 'bullish_engulfing', 'strength': 'strong'})
                    
                    # Bearish engulfing
                    elif (df['close'].iloc[-2] > df['open'].iloc[-2] and  # Previous was bullish
                          df['close'].iloc[-1] < df['open'].iloc[-1] and  # Current is bearish
                          df['open'].iloc[-1] > df['close'].iloc[-2] and  # Opens above prev close
                          df['close'].iloc[-1] < df['open'].iloc[-2]):    # Closes below prev open
                        patterns.append({'type': 'bearish_engulfing', 'strength': 'strong'})
                    
                    # Doji detection (body is very small compared to range)
                    range_val = df['high'].iloc[-1] - df['low'].iloc[-1]
                    body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
                    if range_val > 0 and body / range_val < 0.1:
                        patterns.append({'type': 'doji', 'strength': 'weak'})
            
            # Pin Bar (custom detection)
            body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
            upper_wick = df['high'].iloc[-1] - max(df['close'].iloc[-1], df['open'].iloc[-1])
            lower_wick = min(df['close'].iloc[-1], df['open'].iloc[-1]) - df['low'].iloc[-1]
            
            if upper_wick > body * 2:
                patterns.append({'type': 'bearish_pin_bar', 'strength': 'strong'})
            elif lower_wick > body * 2:
                patterns.append({'type': 'bullish_pin_bar', 'strength': 'strong'})
            
        except Exception as e:
            logger.error(f"Error detecting candle patterns: {e}")
        
        return patterns
    
    def detect_combination_patterns(self, indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect combination patterns for stronger signals
        """
        
        combinations = []
        
        try:
            # EMA Cross + RSI Divergence
            if ('ema' in indicators and 'short_signal' in indicators['ema'] and 
                'rsi' in indicators and 'divergence' in indicators['rsi']):
                
                if (indicators['ema']['short_signal'] == 'bullish_cross' and 
                    indicators['rsi']['divergence'] == 'bullish_divergence'):
                    combinations.append({
                        'name': 'EMA Cross + RSI Divergence',
                        'signal': 'strong_buy',
                        'confidence': 0.85,
                        'description': 'Reliable reversal signal - Bullish EMA cross with RSI divergence'
                    })
                elif (indicators['ema']['short_signal'] == 'bearish_cross' and 
                      indicators['rsi']['divergence'] == 'bearish_divergence'):
                    combinations.append({
                        'name': 'EMA Cross + RSI Divergence',
                        'signal': 'strong_sell',
                        'confidence': 0.85,
                        'description': 'Reliable reversal signal - Bearish EMA cross with RSI divergence'
                    })
            
            # Bollinger Band Squeeze + MACD Cross
            if ('bollinger' in indicators and indicators['bollinger'].get('squeeze') and 
                'macd' in indicators and indicators['macd'].get('cross_signal') != 'none'):
                
                combinations.append({
                    'name': 'Bollinger Squeeze + MACD Cross',
                    'signal': 'breakout_imminent',
                    'confidence': 0.80,
                    'description': f"Strong breakout signal - BB squeeze with {indicators['macd']['cross_signal']}"
                })
            
            # Ichimoku Cloud Breakout + Volume Spike
            if ('ichimoku' in indicators and indicators['ichimoku'].get('kumo_breakout') != 'inside_cloud' and 
                'volume' in indicators and indicators['volume'].get('volume_spike')):
                
                signal = 'strong_buy' if indicators['ichimoku']['kumo_breakout'] == 'above_cloud' else 'strong_sell'
                combinations.append({
                    'name': 'Ichimoku Breakout + Volume Spike',
                    'signal': signal,
                    'confidence': 0.90,
                    'description': f"Trend confirmation - Ichimoku {indicators['ichimoku']['kumo_breakout']} with volume spike"
                })
            
            # Stochastic RSI Overbought + Bearish Engulfing on Resistance
            if ('stoch_rsi' in indicators and indicators['stoch_rsi'].get('signal') == 'overbought' and 
                'support_resistance' in indicators and 'candle_patterns' in indicators['support_resistance']):
                
                for pattern in indicators['support_resistance']['candle_patterns']:
                    if pattern['type'] == 'bearish_engulfing':
                        combinations.append({
                            'name': 'Stoch RSI OB + Bearish Engulfing',
                            'signal': 'strong_sell',
                            'confidence': 0.88,
                            'description': 'High-probability short entry - Stochastic RSI overbought with bearish engulfing'
                        })
                        break
            
        except Exception as e:
            logger.error(f"Error detecting combination patterns: {e}")
        
        return combinations
    
    def calculate_overall_scores(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall bullish/bearish scores"""
        
        bullish_score = 0
        bearish_score = 0
        total_weight = 0
        
        signals = []
        
        try:
            # Score each indicator
            for indicator_name, weight in self.indicator_weights.items():
                if indicator_name == 'ema_cross' and 'ema' in indicators:
                    if indicators['ema'].get('signal') == 'golden_cross':
                        bullish_score += weight * 100
                        signals.append('Golden Cross')
                    elif indicators['ema'].get('signal') == 'death_cross':
                        bearish_score += weight * 100
                        signals.append('Death Cross')
                    elif indicators['ema'].get('trend') == 'strong_uptrend':
                        bullish_score += weight * 70
                        signals.append('Strong Uptrend')
                    elif indicators['ema'].get('trend') == 'strong_downtrend':
                        bearish_score += weight * 70
                        signals.append('Strong Downtrend')
                
                elif indicator_name == 'rsi' and 'rsi' in indicators:
                    if indicators['rsi'].get('signal') == 'oversold':
                        bullish_score += weight * 80
                        signals.append('RSI Oversold')
                    elif indicators['rsi'].get('signal') == 'overbought':
                        bearish_score += weight * 80
                        signals.append('RSI Overbought')
                
                elif indicator_name == 'macd' and 'macd' in indicators:
                    if indicators['macd'].get('cross_signal') == 'bullish_cross':
                        bullish_score += weight * 85
                        signals.append('MACD Bullish Cross')
                    elif indicators['macd'].get('cross_signal') == 'bearish_cross':
                        bearish_score += weight * 85
                        signals.append('MACD Bearish Cross')
                
                total_weight += weight
            
            # Normalize scores
            if total_weight > 0:
                bullish_score = bullish_score / total_weight
                bearish_score = bearish_score / total_weight
            
            # Determine overall signal
            if bullish_score > bearish_score + 20:
                overall_signal = 'STRONG_BUY'
            elif bullish_score > bearish_score + 10:
                overall_signal = 'BUY'
            elif bearish_score > bullish_score + 20:
                overall_signal = 'STRONG_SELL'
            elif bearish_score > bullish_score + 10:
                overall_signal = 'SELL'
            else:
                overall_signal = 'NEUTRAL'
            
            return {
                'bullish_score': round(bullish_score, 2),
                'bearish_score': round(bearish_score, 2),
                'overall_signal': overall_signal,
                'active_signals': signals,
                'confidence': abs(bullish_score - bearish_score) / 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall scores: {e}")
            return {
                'bullish_score': 50,
                'bearish_score': 50,
                'overall_signal': 'ERROR',
                'active_signals': [],
                'confidence': 0
            }

# Global instance
technical_indicators_engine = TechnicalIndicatorsEngine()