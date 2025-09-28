"""
Advanced Trading Intelligence Service
Provides pattern recognition, market analysis, and intelligent trading insights
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import numpy as np
import pandas as pd
from supabase import create_client, Client
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import talib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class PatternType(Enum):
    BULLISH_FLAG = "bullish_flag"
    BEARISH_FLAG = "bearish_flag"
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIANGLE = "triangle"
    WEDGE = "wedge"
    CHANNEL = "channel"
    SUPPORT_RESISTANCE = "support_resistance"
    BREAKOUT = "breakout"

class SignalStrength(Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class TradingPattern:
    id: str
    symbol: str
    pattern_type: PatternType
    timeframe: str
    confidence: float
    signal_strength: SignalStrength
    entry_price: float
    target_price: float
    stop_loss: float
    risk_reward_ratio: float
    volume_confirmation: bool
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]

@dataclass
class MarketIntelligence:
    symbol: str
    trend_direction: str
    trend_strength: float
    volatility: float
    support_levels: List[float]
    resistance_levels: List[float]
    volume_profile: Dict[str, Any]
    sentiment_score: float
    technical_indicators: Dict[str, Any]
    pattern_signals: List[TradingPattern]
    generated_at: datetime

class AdvancedTradingIntelligence:
    """
    Advanced trading intelligence service with pattern recognition and market analysis
    """
    
    def __init__(self):
        # ZmartBot configuration
        self.bot_url = "https://asjtxrmftmutcsnqgidy.supabase.co"
        self.bot_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzanR4cm1mdG11dGNzbnFnaWR5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk1Nzc4NjgsImV4cCI6MjA2NTE1Mzg2OH0.ScIz31CxgxC2Knya-oHtMw5GQ7QL4QUHky-cEUdqpFM"
        
        # Initialize client
        self.bot_client: Optional[Client] = None
        
        # Pattern recognition models
        self.pattern_models = {}
        self.scaler = StandardScaler()
        
        # Market data cache
        self.market_data_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Configuration
        self.config = {
            "min_pattern_confidence": 0.6,
            "max_patterns_per_symbol": 10,
            "pattern_expiry_hours": 24,
            "volume_threshold": 1.5,  # 1.5x average volume
            "volatility_threshold": 0.02  # 2% volatility
        }
        
        self._initialize_client()
        self._setup_intelligence_tables()
        self._load_pattern_models()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            self.bot_client = create_client(self.bot_url, self.bot_key)
            logger.info("✅ Advanced Trading Intelligence initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    async def _setup_intelligence_tables(self):
        """Set up intelligence tables in ZmartBot"""
        try:
            # Create trading patterns table
            patterns_table_sql = """
            CREATE TABLE IF NOT EXISTS trading_patterns (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                symbol VARCHAR(20) NOT NULL,
                pattern_type VARCHAR(50) NOT NULL,
                timeframe VARCHAR(10) NOT NULL,
                confidence DECIMAL(3,2) NOT NULL,
                signal_strength VARCHAR(20) NOT NULL,
                entry_price DECIMAL(20,8) NOT NULL,
                target_price DECIMAL(20,8) NOT NULL,
                stop_loss DECIMAL(20,8) NOT NULL,
                risk_reward_ratio DECIMAL(5,2) NOT NULL,
                volume_confirmation BOOLEAN DEFAULT FALSE,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                status VARCHAR(20) DEFAULT 'active'
            );
            
            CREATE INDEX IF NOT EXISTS idx_patterns_symbol ON trading_patterns(symbol);
            CREATE INDEX IF NOT EXISTS idx_patterns_type ON trading_patterns(pattern_type);
            CREATE INDEX IF NOT EXISTS idx_patterns_confidence ON trading_patterns(confidence);
            CREATE INDEX IF NOT EXISTS idx_patterns_expires_at ON trading_patterns(expires_at);
            """
            
            # Create market intelligence table
            intelligence_table_sql = """
            CREATE TABLE IF NOT EXISTS market_intelligence (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                symbol VARCHAR(20) NOT NULL,
                trend_direction VARCHAR(20) NOT NULL,
                trend_strength DECIMAL(3,2) NOT NULL,
                volatility DECIMAL(5,4) NOT NULL,
                support_levels DECIMAL(20,8)[] NOT NULL,
                resistance_levels DECIMAL(20,8)[] NOT NULL,
                volume_profile JSONB DEFAULT '{}',
                sentiment_score DECIMAL(3,2) NOT NULL,
                technical_indicators JSONB DEFAULT '{}',
                pattern_signals JSONB DEFAULT '[]',
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_intelligence_symbol ON market_intelligence(symbol);
            CREATE INDEX IF NOT EXISTS idx_intelligence_generated_at ON market_intelligence(generated_at);
            """
            
            # Execute SQL
            self.bot_client.rpc('exec_sql', {'sql': patterns_table_sql}).execute()
            self.bot_client.rpc('exec_sql', {'sql': intelligence_table_sql}).execute()
            
            logger.info("✅ Intelligence tables created")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create intelligence tables: {e}")
    
    def _load_pattern_models(self):
        """Load pre-trained pattern recognition models"""
        try:
            # Load pattern recognition models
            # In a real implementation, these would be loaded from files
            self.pattern_models = {
                'bullish_flag': self._create_bullish_flag_model(),
                'bearish_flag': self._create_bearish_flag_model(),
                'head_and_shoulders': self._create_head_and_shoulders_model(),
                'double_top': self._create_double_top_model(),
                'double_bottom': self._create_double_bottom_model(),
                'triangle': self._create_triangle_model(),
                'wedge': self._create_wedge_model(),
                'channel': self._create_channel_model()
            }
            
            logger.info("✅ Pattern recognition models loaded")
            
        except Exception as e:
            logger.error(f"❌ Failed to load pattern models: {e}")
    
    def _create_bullish_flag_model(self):
        """Create bullish flag pattern model"""
        # Simplified model - in reality, this would be a trained ML model
        return {
            'name': 'Bullish Flag',
            'description': 'Continuation pattern after strong uptrend',
            'min_confidence': 0.7,
            'required_indicators': ['rsi', 'macd', 'volume']
        }
    
    def _create_bearish_flag_model(self):
        """Create bearish flag pattern model"""
        return {
            'name': 'Bearish Flag',
            'description': 'Continuation pattern after strong downtrend',
            'min_confidence': 0.7,
            'required_indicators': ['rsi', 'macd', 'volume']
        }
    
    def _create_head_and_shoulders_model(self):
        """Create head and shoulders pattern model"""
        return {
            'name': 'Head and Shoulders',
            'description': 'Reversal pattern indicating trend change',
            'min_confidence': 0.8,
            'required_indicators': ['rsi', 'macd', 'volume', 'support_resistance']
        }
    
    def _create_double_top_model(self):
        """Create double top pattern model"""
        return {
            'name': 'Double Top',
            'description': 'Bearish reversal pattern',
            'min_confidence': 0.75,
            'required_indicators': ['rsi', 'macd', 'volume', 'support_resistance']
        }
    
    def _create_double_bottom_model(self):
        """Create double bottom pattern model"""
        return {
            'name': 'Double Bottom',
            'description': 'Bullish reversal pattern',
            'min_confidence': 0.75,
            'required_indicators': ['rsi', 'macd', 'volume', 'support_resistance']
        }
    
    def _create_triangle_model(self):
        """Create triangle pattern model"""
        return {
            'name': 'Triangle',
            'description': 'Consolidation pattern before breakout',
            'min_confidence': 0.65,
            'required_indicators': ['rsi', 'macd', 'volume']
        }
    
    def _create_wedge_model(self):
        """Create wedge pattern model"""
        return {
            'name': 'Wedge',
            'description': 'Reversal or continuation pattern',
            'min_confidence': 0.7,
            'required_indicators': ['rsi', 'macd', 'volume']
        }
    
    def _create_channel_model(self):
        """Create channel pattern model"""
        return {
            'name': 'Channel',
            'description': 'Trend continuation pattern',
            'min_confidence': 0.6,
            'required_indicators': ['rsi', 'macd', 'volume']
        }
    
    async def analyze_market_intelligence(self, symbol: str, timeframe: str = "1h") -> MarketIntelligence:
        """
        Generate comprehensive market intelligence for a symbol
        """
        try:
            # Get market data
            market_data = await self._get_market_data(symbol, timeframe)
            if not market_data:
                raise HTTPException(status_code=404, detail=f"No market data found for {symbol}")
            
            # Calculate technical indicators
            technical_indicators = self._calculate_technical_indicators(market_data)
            
            # Identify patterns
            patterns = await self._identify_patterns(symbol, market_data, timeframe)
            
            # Calculate trend analysis
            trend_direction, trend_strength = self._analyze_trend(market_data)
            
            # Calculate volatility
            volatility = self._calculate_volatility(market_data)
            
            # Identify support and resistance levels
            support_levels, resistance_levels = self._identify_support_resistance(market_data)
            
            # Analyze volume profile
            volume_profile = self._analyze_volume_profile(market_data)
            
            # Calculate sentiment score
            sentiment_score = self._calculate_sentiment_score(market_data, patterns)
            
            # Create market intelligence object
            intelligence = MarketIntelligence(
                symbol=symbol,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                volatility=volatility,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                volume_profile=volume_profile,
                sentiment_score=sentiment_score,
                technical_indicators=technical_indicators,
                pattern_signals=patterns,
                generated_at=datetime.now()
            )
            
            # Store in database
            await self._store_market_intelligence(intelligence)
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze market intelligence for {symbol}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_market_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get market data for analysis"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.market_data_cache:
                cached_data, timestamp = self.market_data_cache[cache_key]
                if (datetime.now() - timestamp).seconds < self.cache_ttl:
                    return cached_data
            
            # Get data from Supabase
            response = self.bot_client.table("market_data").select("*").eq("symbol", symbol).order("timestamp", desc=True).limit(1000).execute()
            
            if not response.data:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(response.data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Cache the data
            self.market_data_cache[cache_key] = (df, datetime.now())
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to get market data: {e}")
            return None
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        try:
            # Ensure we have enough data
            if len(df) < 50:
                return {}
            
            # Convert to numpy arrays
            high = df['high'].values
            low = df['low'].values
            close = df['close'].values
            volume = df['volume'].values
            
            # Calculate indicators
            indicators = {
                'rsi': talib.RSI(close, timeperiod=14)[-1] if len(close) >= 14 else None,
                'macd': talib.MACD(close)[0][-1] if len(close) >= 26 else None,
                'macd_signal': talib.MACD(close)[1][-1] if len(close) >= 26 else None,
                'macd_histogram': talib.MACD(close)[2][-1] if len(close) >= 26 else None,
                'bb_upper': talib.BBANDS(close)[0][-1] if len(close) >= 20 else None,
                'bb_middle': talib.BBANDS(close)[1][-1] if len(close) >= 20 else None,
                'bb_lower': talib.BBANDS(close)[2][-1] if len(close) >= 20 else None,
                'stoch_k': talib.STOCH(high, low, close)[0][-1] if len(close) >= 14 else None,
                'stoch_d': talib.STOCH(high, low, close)[1][-1] if len(close) >= 14 else None,
                'atr': talib.ATR(high, low, close, timeperiod=14)[-1] if len(close) >= 14 else None,
                'adx': talib.ADX(high, low, close, timeperiod=14)[-1] if len(close) >= 14 else None,
                'obv': talib.OBV(close, volume)[-1] if len(close) >= 1 else None
            }
            
            # Remove None values
            indicators = {k: v for k, v in indicators.items() if v is not None}
            
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate technical indicators: {e}")
            return {}
    
    async def _identify_patterns(self, symbol: str, df: pd.DataFrame, timeframe: str) -> List[TradingPattern]:
        """Identify trading patterns in the data"""
        try:
            patterns = []
            
            # Check each pattern type
            for pattern_type, model in self.pattern_models.items():
                pattern = await self._detect_pattern(symbol, df, pattern_type, model, timeframe)
                if pattern and pattern.confidence >= self.config["min_pattern_confidence"]:
                    patterns.append(pattern)
            
            # Sort by confidence and limit
            patterns.sort(key=lambda x: x.confidence, reverse=True)
            return patterns[:self.config["max_patterns_per_symbol"]]
            
        except Exception as e:
            logger.error(f"❌ Failed to identify patterns: {e}")
            return []
    
    async def _detect_pattern(self, symbol: str, df: pd.DataFrame, pattern_type: str, model: Dict[str, Any], timeframe: str) -> Optional[TradingPattern]:
        """Detect a specific pattern type"""
        try:
            # Simplified pattern detection - in reality, this would use ML models
            if pattern_type == 'bullish_flag':
                return await self._detect_bullish_flag(symbol, df, timeframe)
            elif pattern_type == 'bearish_flag':
                return await self._detect_bearish_flag(symbol, df, timeframe)
            elif pattern_type == 'head_and_shoulders':
                return await self._detect_head_and_shoulders(symbol, df, timeframe)
            elif pattern_type == 'double_top':
                return await self._detect_double_top(symbol, df, timeframe)
            elif pattern_type == 'double_bottom':
                return await self._detect_double_bottom(symbol, df, timeframe)
            elif pattern_type == 'triangle':
                return await self._detect_triangle(symbol, df, timeframe)
            elif pattern_type == 'wedge':
                return await self._detect_wedge(symbol, df, timeframe)
            elif pattern_type == 'channel':
                return await self._detect_channel(symbol, df, timeframe)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to detect pattern {pattern_type}: {e}")
            return None
    
    async def _detect_bullish_flag(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Optional[TradingPattern]:
        """Detect bullish flag pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Simplified detection logic
            recent_data = df.tail(20)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            closes = recent_data['close'].values
            volumes = recent_data['volume'].values
            
            # Check for flag pattern characteristics
            flag_high = np.max(highs[-10:])
            flag_low = np.min(lows[-10:])
            flag_range = flag_high - flag_low
            
            # Check for consolidation after uptrend
            early_high = np.max(highs[:10])
            late_high = np.max(highs[-10:])
            
            if late_high < early_high and flag_range < np.std(closes) * 2:
                # Calculate confidence based on pattern quality
                confidence = min(0.9, 0.6 + (flag_range / np.std(closes)) * 0.3)
                
                # Calculate entry, target, and stop loss
                entry_price = closes[-1]
                target_price = entry_price + (flag_range * 2)
                stop_loss = entry_price - (flag_range * 0.5)
                risk_reward = (target_price - entry_price) / (entry_price - stop_loss)
                
                # Check volume confirmation
                avg_volume = np.mean(volumes)
                recent_volume = np.mean(volumes[-5:])
                volume_confirmation = recent_volume > avg_volume * self.config["volume_threshold"]
                
                # Determine signal strength
                if confidence > 0.8 and volume_confirmation:
                    signal_strength = SignalStrength.VERY_STRONG
                elif confidence > 0.7:
                    signal_strength = SignalStrength.STRONG
                elif confidence > 0.6:
                    signal_strength = SignalStrength.MODERATE
                else:
                    signal_strength = SignalStrength.WEAK
                
                return TradingPattern(
                    id=f"bullish_flag_{symbol}_{int(datetime.now().timestamp())}",
                    symbol=symbol,
                    pattern_type=PatternType.BULLISH_FLAG,
                    timeframe=timeframe,
                    confidence=confidence,
                    signal_strength=signal_strength,
                    entry_price=entry_price,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    risk_reward_ratio=risk_reward,
                    volume_confirmation=volume_confirmation,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=self.config["pattern_expiry_hours"]),
                    metadata={
                        "flag_range": flag_range,
                        "early_high": early_high,
                        "late_high": late_high,
                        "volume_ratio": recent_volume / avg_volume
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to detect bullish flag: {e}")
            return None
    
    async def _detect_bearish_flag(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Optional[TradingPattern]:
        """Detect bearish flag pattern"""
        try:
            if len(df) < 20:
                return None
            
            # Similar logic to bullish flag but inverted
            recent_data = df.tail(20)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            closes = recent_data['close'].values
            volumes = recent_data['volume'].values
            
            # Check for flag pattern characteristics
            flag_high = np.max(highs[-10:])
            flag_low = np.min(lows[-10:])
            flag_range = flag_high - flag_low
            
            # Check for consolidation after downtrend
            early_low = np.min(lows[:10])
            late_low = np.min(lows[-10:])
            
            if late_low > early_low and flag_range < np.std(closes) * 2:
                confidence = min(0.9, 0.6 + (flag_range / np.std(closes)) * 0.3)
                
                entry_price = closes[-1]
                target_price = entry_price - (flag_range * 2)
                stop_loss = entry_price + (flag_range * 0.5)
                risk_reward = (entry_price - target_price) / (stop_loss - entry_price)
                
                avg_volume = np.mean(volumes)
                recent_volume = np.mean(volumes[-5:])
                volume_confirmation = recent_volume > avg_volume * self.config["volume_threshold"]
                
                if confidence > 0.8 and volume_confirmation:
                    signal_strength = SignalStrength.VERY_STRONG
                elif confidence > 0.7:
                    signal_strength = SignalStrength.STRONG
                elif confidence > 0.6:
                    signal_strength = SignalStrength.MODERATE
                else:
                    signal_strength = SignalStrength.WEAK
                
                return TradingPattern(
                    id=f"bearish_flag_{symbol}_{int(datetime.now().timestamp())}",
                    symbol=symbol,
                    pattern_type=PatternType.BEARISH_FLAG,
                    timeframe=timeframe,
                    confidence=confidence,
                    signal_strength=signal_strength,
                    entry_price=entry_price,
                    target_price=target_price,
                    stop_loss=stop_loss,
                    risk_reward_ratio=risk_reward,
                    volume_confirmation=volume_confirmation,
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=self.config["pattern_expiry_hours"]),
                    metadata={
                        "flag_range": flag_range,
                        "early_low": early_low,
                        "late_low": late_low,
                        "volume_ratio": recent_volume / avg_volume
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to detect bearish flag: {e}")
            return None
    
    async def _detect_head_and_shoulders(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Optional[TradingPattern]:
        """Detect head and shoulders pattern"""
        try:
            if len(df) < 30:
                return None
            
            # Simplified head and shoulders detection
            recent_data = df.tail(30)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            closes = recent_data['close'].values
            
            # Find peaks
            peaks = []
            for i in range(2, len(highs) - 2):
                if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                    peaks.append((i, highs[i]))
            
            if len(peaks) >= 3:
                # Check for head and shoulders formation
                left_shoulder = peaks[-3]
                head = peaks[-2]
                right_shoulder = peaks[-1]
                
                # Head should be higher than shoulders
                if head[1] > left_shoulder[1] and head[1] > right_shoulder[1]:
                    # Shoulders should be roughly equal
                    shoulder_diff = abs(left_shoulder[1] - right_shoulder[1]) / left_shoulder[1]
                    
                    if shoulder_diff < 0.05:  # 5% tolerance
                        confidence = 0.8 - shoulder_diff * 10
                        
                        entry_price = closes[-1]
                        target_price = entry_price - (head[1] - left_shoulder[1])
                        stop_loss = entry_price + (head[1] - left_shoulder[1]) * 0.5
                        risk_reward = (entry_price - target_price) / (stop_loss - entry_price)
                        
                        if confidence > 0.8:
                            signal_strength = SignalStrength.VERY_STRONG
                        elif confidence > 0.7:
                            signal_strength = SignalStrength.STRONG
                        else:
                            signal_strength = SignalStrength.MODERATE
                        
                        return TradingPattern(
                            id=f"head_shoulders_{symbol}_{int(datetime.now().timestamp())}",
                            symbol=symbol,
                            pattern_type=PatternType.HEAD_AND_SHOULDERS,
                            timeframe=timeframe,
                            confidence=confidence,
                            signal_strength=signal_strength,
                            entry_price=entry_price,
                            target_price=target_price,
                            stop_loss=stop_loss,
                            risk_reward_ratio=risk_reward,
                            volume_confirmation=True,  # Assume confirmed for now
                            created_at=datetime.now(),
                            expires_at=datetime.now() + timedelta(hours=self.config["pattern_expiry_hours"]),
                            metadata={
                                "left_shoulder": left_shoulder[1],
                                "head": head[1],
                                "right_shoulder": right_shoulder[1],
                                "shoulder_diff": shoulder_diff
                            }
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to detect head and shoulders: {e}")
            return None
    
    async def _detect_double_top(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Optional[TradingPattern]:
        """Detect double top pattern"""
        # Simplified implementation
        return None
    
    async def _detect_double_bottom(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Optional[TradingPattern]:
        """Detect double bottom pattern"""
        # Simplified implementation
        return None
    
    async def _detect_triangle(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Optional[TradingPattern]:
        """Detect triangle pattern"""
        # Simplified implementation
        return None
    
    async def _detect_wedge(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Optional[TradingPattern]:
        """Detect wedge pattern"""
        # Simplified implementation
        return None
    
    async def _detect_channel(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Optional[TradingPattern]:
        """Detect channel pattern"""
        # Simplified implementation
        return None
    
    def _analyze_trend(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Analyze trend direction and strength"""
        try:
            if len(df) < 20:
                return "neutral", 0.0
            
            # Calculate moving averages
            ma_20 = df['close'].rolling(window=20).mean()
            ma_50 = df['close'].rolling(window=min(50, len(df))).mean()
            
            # Determine trend direction
            if ma_20.iloc[-1] > ma_50.iloc[-1]:
                direction = "bullish"
            elif ma_20.iloc[-1] < ma_50.iloc[-1]:
                direction = "bearish"
            else:
                direction = "neutral"
            
            # Calculate trend strength
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
            strength = min(1.0, abs(price_change) * 10)  # Scale to 0-1
            
            return direction, strength
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze trend: {e}")
            return "neutral", 0.0
    
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate market volatility"""
        try:
            if len(df) < 20:
                return 0.0
            
            # Calculate returns
            returns = df['close'].pct_change().dropna()
            
            # Calculate volatility (standard deviation of returns)
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            return volatility
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate volatility: {e}")
            return 0.0
    
    def _identify_support_resistance(self, df: pd.DataFrame) -> Tuple[List[float], List[float]]:
        """Identify support and resistance levels"""
        try:
            if len(df) < 50:
                return [], []
            
            # Use recent data for level identification
            recent_data = df.tail(50)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            
            # Find support levels (local minima)
            support_levels = []
            for i in range(2, len(lows) - 2):
                if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                    support_levels.append(lows[i])
            
            # Find resistance levels (local maxima)
            resistance_levels = []
            for i in range(2, len(highs) - 2):
                if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                    resistance_levels.append(highs[i])
            
            # Remove duplicates and sort
            support_levels = sorted(list(set(support_levels)))
            resistance_levels = sorted(list(set(resistance_levels)))
            
            return support_levels, resistance_levels
            
        except Exception as e:
            logger.error(f"❌ Failed to identify support/resistance: {e}")
            return [], []
    
    def _analyze_volume_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume profile"""
        try:
            if len(df) < 20:
                return {}
            
            recent_data = df.tail(20)
            volumes = recent_data['volume'].values
            closes = recent_data['close'].values
            
            # Calculate volume metrics
            avg_volume = np.mean(volumes)
            max_volume = np.max(volumes)
            min_volume = np.min(volumes)
            volume_std = np.std(volumes)
            
            # Volume trend
            volume_trend = "increasing" if volumes[-1] > avg_volume else "decreasing"
            
            # Volume-price relationship
            price_change = (closes[-1] - closes[0]) / closes[0]
            volume_change = (volumes[-1] - volumes[0]) / volumes[0]
            
            if price_change > 0 and volume_change > 0:
                volume_price_relationship = "bullish"
            elif price_change < 0 and volume_change > 0:
                volume_price_relationship = "bearish"
            else:
                volume_price_relationship = "neutral"
            
            return {
                "avg_volume": avg_volume,
                "max_volume": max_volume,
                "min_volume": min_volume,
                "volume_std": volume_std,
                "volume_trend": volume_trend,
                "volume_price_relationship": volume_price_relationship,
                "current_volume": volumes[-1],
                "volume_ratio": volumes[-1] / avg_volume
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze volume profile: {e}")
            return {}
    
    def _calculate_sentiment_score(self, df: pd.DataFrame, patterns: List[TradingPattern]) -> float:
        """Calculate market sentiment score"""
        try:
            if len(df) < 20:
                return 0.5
            
            # Base sentiment from price action
            recent_data = df.tail(20)
            price_change = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
            
            # Adjust for patterns
            pattern_sentiment = 0.5
            if patterns:
                bullish_patterns = len([p for p in patterns if p.pattern_type.value in ['bullish_flag', 'double_bottom']])
                bearish_patterns = len([p for p in patterns if p.pattern_type.value in ['bearish_flag', 'double_top', 'head_and_shoulders']])
                
                if bullish_patterns > bearish_patterns:
                    pattern_sentiment = 0.7
                elif bearish_patterns > bullish_patterns:
                    pattern_sentiment = 0.3
                else:
                    pattern_sentiment = 0.5
            
            # Combine price action and pattern sentiment
            sentiment = (price_change * 0.5 + 0.5) * 0.6 + pattern_sentiment * 0.4
            
            # Clamp to 0-1 range
            return max(0.0, min(1.0, sentiment))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate sentiment score: {e}")
            return 0.5
    
    async def _store_market_intelligence(self, intelligence: MarketIntelligence):
        """Store market intelligence in database"""
        try:
            intelligence_data = {
                "symbol": intelligence.symbol,
                "trend_direction": intelligence.trend_direction,
                "trend_strength": intelligence.trend_strength,
                "volatility": intelligence.volatility,
                "support_levels": intelligence.support_levels,
                "resistance_levels": intelligence.resistance_levels,
                "volume_profile": intelligence.volume_profile,
                "sentiment_score": intelligence.sentiment_score,
                "technical_indicators": intelligence.technical_indicators,
                "pattern_signals": [pattern.__dict__ for pattern in intelligence.pattern_signals],
                "generated_at": intelligence.generated_at.isoformat()
            }
            
            response = self.bot_client.table("market_intelligence").insert(intelligence_data).execute()
            
            # Store individual patterns
            for pattern in intelligence.pattern_signals:
                await self._store_trading_pattern(pattern)
            
        except Exception as e:
            logger.error(f"❌ Failed to store market intelligence: {e}")
    
    async def _store_trading_pattern(self, pattern: TradingPattern):
        """Store trading pattern in database"""
        try:
            pattern_data = {
                "id": pattern.id,
                "symbol": pattern.symbol,
                "pattern_type": pattern.pattern_type.value,
                "timeframe": pattern.timeframe,
                "confidence": pattern.confidence,
                "signal_strength": pattern.signal_strength.value,
                "entry_price": pattern.entry_price,
                "target_price": pattern.target_price,
                "stop_loss": pattern.stop_loss,
                "risk_reward_ratio": pattern.risk_reward_ratio,
                "volume_confirmation": pattern.volume_confirmation,
                "metadata": pattern.metadata,
                "created_at": pattern.created_at.isoformat(),
                "expires_at": pattern.expires_at.isoformat()
            }
            
            response = self.bot_client.table("trading_patterns").upsert(pattern_data).execute()
            
        except Exception as e:
            logger.error(f"❌ Failed to store trading pattern: {e}")
    
    async def get_active_patterns(self, symbol: str = None) -> List[TradingPattern]:
        """Get active trading patterns"""
        try:
            query = self.bot_client.table("trading_patterns").select("*").eq("status", "active").gt("expires_at", datetime.now().isoformat())
            
            if symbol:
                query = query.eq("symbol", symbol)
            
            response = query.order("confidence", desc=True).execute()
            
            patterns = []
            for data in response.data:
                pattern = TradingPattern(
                    id=data["id"],
                    symbol=data["symbol"],
                    pattern_type=PatternType(data["pattern_type"]),
                    timeframe=data["timeframe"],
                    confidence=data["confidence"],
                    signal_strength=SignalStrength(data["signal_strength"]),
                    entry_price=data["entry_price"],
                    target_price=data["target_price"],
                    stop_loss=data["stop_loss"],
                    risk_reward_ratio=data["risk_reward_ratio"],
                    volume_confirmation=data["volume_confirmation"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    expires_at=datetime.fromisoformat(data["expires_at"]),
                    metadata=data["metadata"]
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Failed to get active patterns: {e}")
            return []
    
    async def get_market_intelligence(self, symbol: str) -> Optional[MarketIntelligence]:
        """Get latest market intelligence for a symbol"""
        try:
            response = self.bot_client.table("market_intelligence").select("*").eq("symbol", symbol).order("generated_at", desc=True).limit(1).execute()
            
            if not response.data:
                return None
            
            data = response.data[0]
            
            # Reconstruct patterns
            patterns = []
            for pattern_data in data["pattern_signals"]:
                pattern = TradingPattern(
                    id=pattern_data["id"],
                    symbol=pattern_data["symbol"],
                    pattern_type=PatternType(pattern_data["pattern_type"]),
                    timeframe=pattern_data["timeframe"],
                    confidence=pattern_data["confidence"],
                    signal_strength=SignalStrength(pattern_data["signal_strength"]),
                    entry_price=pattern_data["entry_price"],
                    target_price=pattern_data["target_price"],
                    stop_loss=pattern_data["stop_loss"],
                    risk_reward_ratio=pattern_data["risk_reward_ratio"],
                    volume_confirmation=pattern_data["volume_confirmation"],
                    created_at=datetime.fromisoformat(pattern_data["created_at"]),
                    expires_at=datetime.fromisoformat(pattern_data["expires_at"]),
                    metadata=pattern_data["metadata"]
                )
                patterns.append(pattern)
            
            intelligence = MarketIntelligence(
                symbol=data["symbol"],
                trend_direction=data["trend_direction"],
                trend_strength=data["trend_strength"],
                volatility=data["volatility"],
                support_levels=data["support_levels"],
                resistance_levels=data["resistance_levels"],
                volume_profile=data["volume_profile"],
                sentiment_score=data["sentiment_score"],
                technical_indicators=data["technical_indicators"],
                pattern_signals=patterns,
                generated_at=datetime.fromisoformat(data["generated_at"])
            )
            
            return intelligence
            
        except Exception as e:
            logger.error(f"❌ Failed to get market intelligence: {e}")
            return None

# FastAPI integration
app = FastAPI(title="Advanced Trading Intelligence", version="1.0.0")
intelligence_service = AdvancedTradingIntelligence()

@app.get("/intelligence/analyze/{symbol}")
async def analyze_market_intelligence(symbol: str, timeframe: str = "1h"):
    """Analyze market intelligence for a symbol"""
    intelligence = await intelligence_service.analyze_market_intelligence(symbol, timeframe)
    return {
        "symbol": intelligence.symbol,
        "trend_direction": intelligence.trend_direction,
        "trend_strength": intelligence.trend_strength,
        "volatility": intelligence.volatility,
        "support_levels": intelligence.support_levels,
        "resistance_levels": intelligence.resistance_levels,
        "volume_profile": intelligence.volume_profile,
        "sentiment_score": intelligence.sentiment_score,
        "technical_indicators": intelligence.technical_indicators,
        "pattern_signals": [
            {
                "id": p.id,
                "pattern_type": p.pattern_type.value,
                "confidence": p.confidence,
                "signal_strength": p.signal_strength.value,
                "entry_price": p.entry_price,
                "target_price": p.target_price,
                "stop_loss": p.stop_loss,
                "risk_reward_ratio": p.risk_reward_ratio,
                "volume_confirmation": p.volume_confirmation,
                "expires_at": p.expires_at.isoformat()
            }
            for p in intelligence.pattern_signals
        ],
        "generated_at": intelligence.generated_at.isoformat()
    }

@app.get("/intelligence/patterns/{symbol}")
async def get_active_patterns(symbol: str):
    """Get active trading patterns for a symbol"""
    patterns = await intelligence_service.get_active_patterns(symbol)
    return [
        {
            "id": p.id,
            "symbol": p.symbol,
            "pattern_type": p.pattern_type.value,
            "timeframe": p.timeframe,
            "confidence": p.confidence,
            "signal_strength": p.signal_strength.value,
            "entry_price": p.entry_price,
            "target_price": p.target_price,
            "stop_loss": p.stop_loss,
            "risk_reward_ratio": p.risk_reward_ratio,
            "volume_confirmation": p.volume_confirmation,
            "created_at": p.created_at.isoformat(),
            "expires_at": p.expires_at.isoformat(),
            "metadata": p.metadata
        }
        for p in patterns
    ]

@app.get("/intelligence/market/{symbol}")
async def get_market_intelligence(symbol: str):
    """Get latest market intelligence for a symbol"""
    intelligence = await intelligence_service.get_market_intelligence(symbol)
    if not intelligence:
        raise HTTPException(status_code=404, detail="No market intelligence found")
    
    return {
        "symbol": intelligence.symbol,
        "trend_direction": intelligence.trend_direction,
        "trend_strength": intelligence.trend_strength,
        "volatility": intelligence.volatility,
        "support_levels": intelligence.support_levels,
        "resistance_levels": intelligence.resistance_levels,
        "volume_profile": intelligence.volume_profile,
        "sentiment_score": intelligence.sentiment_score,
        "technical_indicators": intelligence.technical_indicators,
        "pattern_signals": [
            {
                "id": p.id,
                "pattern_type": p.pattern_type.value,
                "confidence": p.confidence,
                "signal_strength": p.signal_strength.value,
                "entry_price": p.entry_price,
                "target_price": p.target_price,
                "stop_loss": p.stop_loss,
                "risk_reward_ratio": p.risk_reward_ratio,
                "volume_confirmation": p.volume_confirmation,
                "expires_at": p.expires_at.isoformat()
            }
            for p in intelligence.pattern_signals
        ],
        "generated_at": intelligence.generated_at.isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8904)

