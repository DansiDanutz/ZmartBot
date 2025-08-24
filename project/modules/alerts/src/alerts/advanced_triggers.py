"""Advanced trigger system based on ChatGPT analysis and Zmart implementation."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass, field

from ..core.models import MarketData, TechnicalIndicators, AlertTrigger, TimeFrame

logger = logging.getLogger(__name__)


@dataclass
class TriggerState:
    """State tracking for advanced triggers."""
    symbol: str
    last_update: datetime = field(default_factory=datetime.now)
    price_history: List[float] = field(default_factory=list)
    volume_history: List[float] = field(default_factory=list)
    
    # Technical indicators cache
    indicators_cache: Dict[TimeFrame, Dict[str, float]] = field(default_factory=dict)
    
    # Event tracking
    recent_events: List[Dict[str, Any]] = field(default_factory=list)
    cooldown_tracker: Dict[str, datetime] = field(default_factory=dict)
    
    # Multi-timeframe alignment
    tf_scores: Dict[str, int] = field(default_factory=dict)
    
    # Orderbook microstructure (if available)
    book_tilt_history: List[float] = field(default_factory=list)
    depth_changes: List[float] = field(default_factory=list)
    
    # Derivatives data (futures)
    funding_rate_history: List[float] = field(default_factory=list)
    oi_history: List[float] = field(default_factory=list)
    basis_history: List[float] = field(default_factory=list)


class AdvancedTriggerEngine:
    """Advanced trigger engine with multi-timeframe analysis and LLM gating."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.states: Dict[str, TriggerState] = {}
        self.llm_client = None  # Optional LLM integration
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration based on ChatGPT analysis."""
        return {
            "lookbacks": {
                "sma": 50,
                "sma_long": 200,
                "ema_fast": 9,
                "ema_slow": 21,
                "rsi": 14,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "atr": 14,
                "donchian": 20,
                "vol_window": 60
            },
            "thresholds": {
                "breakout_atr_factor": 0.5,
                "volume_z": 2.0,
                "atr_z": 2.0,
                "basis_bps": 15,
                "oi_pct_1h": 2.5,
                "oi_purge_pct": -3.0,
                "funding_extreme": 0.0005,
                "rsi_reentry_long": 45,
                "rsi_reentry_short": 55,
                "rsi_extreme_hi": 75,
                "rsi_extreme_lo": 25,
                "book_tilt_up": 1.8,
                "book_tilt_dn": 0.55,
                "tilt_persist_sec": 120,
                "spoof_wall_factor": 5.0,
                "spoof_persist_sec": 60
            },
            "cooldowns_minutes": {
                "ema_cross": 30,
                "sma_cross": 30,
                "ma_breakout": 60,
                "structure_break": 60,
                "range_escape": 60,
                "rsi_reentry": 30,
                "rsi_exhaust": 30,
                "macd_cross": 30,
                "macd_inflect": 30,
                "atr_shift": 60,
                "volume_spike": 30,
                "derivatives": 60,
                "book_tilt": 15,
                "spoof": 30,
                "pre_signal": 30
            },
            "pre_signal": {
                "alignment_needed": 8,
                "fresh_events_needed": 2
            },
            "suppressors": {
                "stale_after_minutes": 5,
                "rsi_extremes_block": True
            },
            "features": {
                "enable_orderbook": True,
                "enable_derivatives": True,
                "enable_llm_gating": False
            }
        }
    
    def get_or_create_state(self, symbol: str) -> TriggerState:
        """Get or create trigger state for symbol."""
        if symbol not in self.states:
            self.states[symbol] = TriggerState(symbol=symbol)
        return self.states[symbol]
    
    async def process_market_data(self, market_data: MarketData, 
                                technical_data: Dict[TimeFrame, TechnicalIndicators]) -> List[Dict[str, Any]]:
        """Process market data and detect advanced triggers."""
        state = self.get_or_create_state(market_data.symbol)
        
        # Update state
        self._update_state(state, market_data, technical_data)
        
        # Detect events across timeframes
        events = []
        
        # Technical analysis events
        ta_events = self._detect_ta_events(state, technical_data)
        events.extend(ta_events)
        
        # Volume and volatility events
        vol_events = self._detect_volume_events(state, market_data)
        events.extend(vol_events)
        
        # Multi-timeframe alignment
        alignment_events = self._detect_alignment_events(state, technical_data)
        events.extend(alignment_events)
        
        # Orderbook microstructure (if enabled)
        if self.config["features"]["enable_orderbook"]:
            book_events = self._detect_orderbook_events(state, market_data)
            events.extend(book_events)
        
        # Derivatives events (if enabled)
        if self.config["features"]["enable_derivatives"]:
            deriv_events = self._detect_derivatives_events(state, market_data)
            events.extend(deriv_events)
        
        # Apply cooldowns and filters
        filtered_events = self._apply_filters(state, events)
        
        # LLM gating for pre-signals
        if self.config["features"]["enable_llm_gating"] and filtered_events:
            gated_events = await self._apply_llm_gating(state, technical_data, filtered_events)
            filtered_events = gated_events
        
        # Update recent events
        state.recent_events.extend(filtered_events)
        state.recent_events = state.recent_events[-50:]  # Keep last 50 events
        
        return filtered_events
    
    def _update_state(self, state: TriggerState, market_data: MarketData, 
                     technical_data: Dict[TimeFrame, TechnicalIndicators]):
        """Update trigger state with new data."""
        state.last_update = datetime.now()
        
        # Update price and volume history
        state.price_history.append(market_data.price)
        state.volume_history.append(market_data.volume)
        
        # Keep rolling windows
        max_history = 500
        if len(state.price_history) > max_history:
            state.price_history = state.price_history[-max_history:]
        if len(state.volume_history) > max_history:
            state.volume_history = state.volume_history[-max_history:]
        
        # Update indicators cache
        for timeframe, indicators in technical_data.items():
            if indicators:
                state.indicators_cache[timeframe] = {
                    'rsi': indicators.rsi,
                    'macd': indicators.macd,
                    'macd_signal': indicators.macd_signal,
                    'macd_histogram': indicators.macd_histogram,
                    'bb_upper': indicators.bb_upper,
                    'bb_middle': indicators.bb_middle,
                    'bb_lower': indicators.bb_lower,
                    'sma_20': indicators.sma_20,
                    'sma_50': indicators.sma_50,
                    'ema_12': indicators.ema_12,
                    'ema_26': indicators.ema_26,
                    'price': market_data.price
                }
    
    def _detect_ta_events(self, state: TriggerState, 
                         technical_data: Dict[TimeFrame, TechnicalIndicators]) -> List[Dict[str, Any]]:
        """Detect technical analysis events."""
        events = []
        
        for timeframe, indicators in technical_data.items():
            if not indicators:
                continue
            
            # Get previous indicators for cross detection
            prev_indicators = state.indicators_cache.get(timeframe, {})
            
            # EMA crossovers
            if (indicators.ema_12 and indicators.ema_26 and 
                prev_indicators.get('ema_12') and prev_indicators.get('ema_26')):
                
                prev_rel = prev_indicators['ema_12'] - prev_indicators['ema_26']
                curr_rel = indicators.ema_12 - indicators.ema_26
                
                if prev_rel <= 0 and curr_rel > 0:
                    events.append({
                        'type': 'ema_cross',
                        'direction': 'bullish',
                        'timeframe': timeframe.value,
                        'strength': abs(curr_rel / indicators.ema_26) * 100,
                        'labels': ['bull_ema_cross']
                    })
                elif prev_rel >= 0 and curr_rel < 0:
                    events.append({
                        'type': 'ema_cross',
                        'direction': 'bearish',
                        'timeframe': timeframe.value,
                        'strength': abs(curr_rel / indicators.ema_26) * 100,
                        'labels': ['bear_ema_cross']
                    })
            
            # MACD signal crossovers
            if (indicators.macd and indicators.macd_signal and 
                prev_indicators.get('macd') and prev_indicators.get('macd_signal')):
                
                prev_rel = prev_indicators['macd'] - prev_indicators['macd_signal']
                curr_rel = indicators.macd - indicators.macd_signal
                
                if prev_rel <= 0 and curr_rel > 0:
                    events.append({
                        'type': 'macd_cross',
                        'direction': 'bullish',
                        'timeframe': timeframe.value,
                        'strength': abs(curr_rel),
                        'labels': ['bull_macd_cross']
                    })
                elif prev_rel >= 0 and curr_rel < 0:
                    events.append({
                        'type': 'macd_cross',
                        'direction': 'bearish',
                        'timeframe': timeframe.value,
                        'strength': abs(curr_rel),
                        'labels': ['bear_macd_cross']
                    })
            
            # MACD histogram inflection
            if (indicators.macd_histogram and prev_indicators.get('macd_histogram')):
                if prev_indicators['macd_histogram'] <= 0 < indicators.macd_histogram:
                    events.append({
                        'type': 'macd_hist_inflect',
                        'direction': 'bullish',
                        'timeframe': timeframe.value,
                        'labels': ['bull_macd_hist_inflect']
                    })
                elif prev_indicators['macd_histogram'] >= 0 > indicators.macd_histogram:
                    events.append({
                        'type': 'macd_hist_inflect',
                        'direction': 'bearish',
                        'timeframe': timeframe.value,
                        'labels': ['bear_macd_hist_inflect']
                    })
            
            # RSI reentry and exhaustion
            if indicators.rsi:
                rsi = indicators.rsi
                prev_rsi = prev_indicators.get('rsi')
                
                if prev_rsi:
                    # RSI reentry zones
                    if prev_rsi < 45 <= rsi:
                        events.append({
                            'type': 'rsi_reentry',
                            'direction': 'bullish',
                            'timeframe': timeframe.value,
                            'rsi_value': rsi,
                            'labels': ['bull_rsi_reentry']
                        })
                    elif prev_rsi > 55 >= rsi:
                        events.append({
                            'type': 'rsi_reentry',
                            'direction': 'bearish',
                            'timeframe': timeframe.value,
                            'rsi_value': rsi,
                            'labels': ['bear_rsi_reentry']
                        })
                
                # RSI exhaustion zones
                if rsi >= 75:
                    events.append({
                        'type': 'rsi_exhaust',
                        'direction': 'bearish',
                        'timeframe': timeframe.value,
                        'rsi_value': rsi,
                        'labels': ['overbought']
                    })
                elif rsi <= 25:
                    events.append({
                        'type': 'rsi_exhaust',
                        'direction': 'bullish',
                        'timeframe': timeframe.value,
                        'rsi_value': rsi,
                        'labels': ['oversold']
                    })
            
            # Bollinger Band breakouts
            current_price = state.price_history[-1] if state.price_history else 0
            if indicators.bb_upper and indicators.bb_lower and current_price:
                if current_price > indicators.bb_upper:
                    events.append({
                        'type': 'bb_breakout',
                        'direction': 'bullish',
                        'timeframe': timeframe.value,
                        'price': current_price,
                        'bb_upper': indicators.bb_upper,
                        'labels': ['bull_bb_breakout']
                    })
                elif current_price < indicators.bb_lower:
                    events.append({
                        'type': 'bb_breakout',
                        'direction': 'bearish',
                        'timeframe': timeframe.value,
                        'price': current_price,
                        'bb_lower': indicators.bb_lower,
                        'labels': ['bear_bb_breakout']
                    })
        
        return events
    
    def _detect_volume_events(self, state: TriggerState, market_data: MarketData) -> List[Dict[str, Any]]:
        """Detect volume and volatility events."""
        events = []
        
        if len(state.volume_history) < 20:
            return events
        
        # Volume spike detection
        recent_volumes = state.volume_history[-20:]
        avg_volume = np.mean(recent_volumes[:-1])
        current_volume = market_data.volume
        
        volume_z = (current_volume - avg_volume) / np.std(recent_volumes) if np.std(recent_volumes) > 0 else 0
        
        if volume_z >= self.config["thresholds"]["volume_z"]:
            events.append({
                'type': 'volume_spike',
                'direction': 'neutral',
                'volume_z_score': volume_z,
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'labels': ['volume_spike']
            })
        
        # Price volatility (using price history)
        if len(state.price_history) >= 20:
            recent_prices = state.price_history[-20:]
            price_changes = [abs(recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] 
                           for i in range(1, len(recent_prices))]
            
            if price_changes:
                avg_change = np.mean(price_changes)
                current_change = abs(market_data.price - state.price_history[-2]) / state.price_history[-2]
                
                if current_change > avg_change * 2:
                    events.append({
                        'type': 'volatility_spike',
                        'direction': 'neutral',
                        'price_change_pct': current_change * 100,
                        'avg_change_pct': avg_change * 100,
                        'labels': ['volatility_spike']
                    })
        
        return events
    
    def _detect_alignment_events(self, state: TriggerState, 
                               technical_data: Dict[TimeFrame, TechnicalIndicators]) -> List[Dict[str, Any]]:
        """Detect multi-timeframe alignment events."""
        events = []
        
        # Calculate timeframe scores
        long_score = 0
        short_score = 0
        
        for timeframe, indicators in technical_data.items():
            if not indicators:
                continue
            
            tf_long = 0
            tf_short = 0
            
            # EMA alignment
            if indicators.ema_12 and indicators.ema_26:
                if indicators.ema_12 > indicators.ema_26:
                    tf_long += 1
                else:
                    tf_short += 1
            
            # MACD histogram
            if indicators.macd_histogram:
                if indicators.macd_histogram > 0:
                    tf_long += 1
                else:
                    tf_short += 1
            
            # Price vs SMA
            current_price = state.price_history[-1] if state.price_history else 0
            if indicators.sma_50 and current_price:
                if current_price > indicators.sma_50:
                    tf_long += 1
                else:
                    tf_short += 1
            
            state.tf_scores[f"{timeframe.value}_long"] = tf_long
            state.tf_scores[f"{timeframe.value}_short"] = tf_short
            
            long_score += tf_long
            short_score += tf_short
        
        # Check for strong alignment
        alignment_needed = self.config["pre_signal"]["alignment_needed"]
        
        if long_score >= alignment_needed:
            events.append({
                'type': 'multi_tf_alignment',
                'direction': 'bullish',
                'score': long_score,
                'max_score': len(technical_data) * 3,
                'labels': ['bull_alignment']
            })
        elif short_score >= alignment_needed:
            events.append({
                'type': 'multi_tf_alignment',
                'direction': 'bearish',
                'score': short_score,
                'max_score': len(technical_data) * 3,
                'labels': ['bear_alignment']
            })
        
        return events
    
    def _detect_orderbook_events(self, state: TriggerState, market_data: MarketData) -> List[Dict[str, Any]]:
        """Detect orderbook microstructure events (placeholder for future implementation)."""
        events = []
        
        # This would require orderbook data which isn't available in basic MarketData
        # Implementation would include:
        # - Book tilt detection
        # - Spoof wall detection
        # - Absorption patterns
        # - Liquidity imbalances
        
        return events
    
    def _detect_derivatives_events(self, state: TriggerState, market_data: MarketData) -> List[Dict[str, Any]]:
        """Detect derivatives-specific events (placeholder for futures data)."""
        events = []
        
        # This would require futures-specific data:
        # - Funding rate extremes/flips
        # - Open interest surges/purges
        # - Basis dislocations
        # - Perpetual vs spot divergence
        
        return events
    
    def _apply_filters(self, state: TriggerState, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply cooldowns and other filters to events."""
        filtered_events = []
        now = datetime.now()
        
        for event in events:
            event_type = event['type']
            cooldown_minutes = self.config["cooldowns_minutes"].get(event_type, 30)
            
            # Check cooldown
            last_trigger = state.cooldown_tracker.get(event_type)
            if last_trigger and now - last_trigger < timedelta(minutes=cooldown_minutes):
                continue
            
            # Apply RSI extremes suppression
            if self.config["suppressors"]["rsi_extremes_block"]:
                # Check if RSI is in extreme zones and should block certain signals
                for timeframe, indicators_dict in state.indicators_cache.items():
                    rsi = indicators_dict.get('rsi')
                    if rsi and (rsi >= 75 or rsi <= 25):
                        # Block trend-following signals in extreme RSI zones
                        if event_type in ['ema_cross', 'macd_cross'] and event['direction'] == ('bullish' if rsi <= 25 else 'bearish'):
                            continue
            
            # Event passed filters
            filtered_events.append(event)
            state.cooldown_tracker[event_type] = now
        
        return filtered_events
    
    async def _apply_llm_gating(self, state: TriggerState, 
                              technical_data: Dict[TimeFrame, TechnicalIndicators],
                              events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply LLM gating for pre-signal validation."""
        if not self.llm_client:
            return events
        
        # Check if conditions are met for LLM call
        should_call, reason = self._should_call_llm(state, technical_data, events)
        
        if not should_call:
            logger.debug(f"LLM gating blocked: {reason}")
            return []
        
        # Prepare context for LLM
        context = self._prepare_llm_context(state, technical_data, events)
        
        try:
            # Call LLM for signal validation
            llm_response = await self.llm_client.validate_signal(context)
            
            if llm_response.get('valid', False):
                # Add LLM confidence to events
                for event in events:
                    event['llm_confidence'] = llm_response.get('confidence', 0.5)
                    event['llm_reasoning'] = llm_response.get('reasoning', '')
                return events
            else:
                logger.info(f"LLM rejected signal: {llm_response.get('reasoning', 'No reason provided')}")
                return []
                
        except Exception as e:
            logger.error(f"LLM gating error: {e}")
            # Return events without LLM validation on error
            return events
    
    def _should_call_llm(self, state: TriggerState, 
                        technical_data: Dict[TimeFrame, TechnicalIndicators],
                        events: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Determine if LLM should be called based on gating conditions."""
        # Check data staleness
        stale_minutes = (datetime.now() - state.last_update).total_seconds() / 60
        if stale_minutes > self.config["suppressors"]["stale_after_minutes"]:
            return False, "data.stale"
        
        # Calculate alignment scores
        long_score = sum(state.tf_scores.get(f"{tf.value}_long", 0) for tf in technical_data.keys())
        short_score = sum(state.tf_scores.get(f"{tf.value}_short", 0) for tf in technical_data.keys())
        
        alignment_needed = self.config["pre_signal"]["alignment_needed"]
        fresh_events_needed = self.config["pre_signal"]["fresh_events_needed"]
        
        # Count fresh events
        fresh_events = len([e for e in events if any(label in ['bull', 'bear'] for label in e.get('labels', []))])
        
        # Strong alignment check
        if long_score >= alignment_needed and fresh_events >= fresh_events_needed:
            return True, "pre_signal.long.strong"
        if short_score >= alignment_needed and fresh_events >= fresh_events_needed:
            return True, "pre_signal.short.strong"
        
        # Pullback setup check (higher timeframe trend + lower timeframe reentry)
        h1_data = technical_data.get(TimeFrame.H1)
        m15_data = technical_data.get(TimeFrame.M15)
        
        if h1_data and m15_data:
            h1_indicators = state.indicators_cache.get(TimeFrame.H1, {})
            m15_indicators = state.indicators_cache.get(TimeFrame.M15, {})
            
            # Bullish pullback setup
            if (h1_indicators.get('ema_12', 0) > h1_indicators.get('ema_26', 1) and
                35 <= m15_indicators.get('rsi', 50) <= 45 and
                h1_indicators.get('price', 0) > h1_indicators.get('sma_50', float('inf'))):
                return True, "pre_signal.long.pullback"
            
            # Bearish pullback setup
            if (h1_indicators.get('ema_12', 1) < h1_indicators.get('ema_26', 0) and
                55 <= m15_indicators.get('rsi', 50) <= 65 and
                h1_indicators.get('price', float('inf')) < h1_indicators.get('sma_50', 0)):
                return True, "pre_signal.short.pullback"
        
        return False, "no_setup"
    
    def _prepare_llm_context(self, state: TriggerState, 
                           technical_data: Dict[TimeFrame, TechnicalIndicators],
                           events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare context for LLM analysis."""
        return {
            'symbol': state.symbol,
            'current_price': state.price_history[-1] if state.price_history else 0,
            'technical_indicators': {
                tf.value: {
                    'rsi': indicators.rsi,
                    'macd': indicators.macd,
                    'macd_signal': indicators.macd_signal,
                    'ema_12': indicators.ema_12,
                    'ema_26': indicators.ema_26,
                    'sma_50': indicators.sma_50
                } for tf, indicators in technical_data.items() if indicators
            },
            'recent_events': events,
            'tf_scores': state.tf_scores,
            'volume_trend': 'increasing' if len(state.volume_history) >= 2 and 
                          state.volume_history[-1] > state.volume_history[-2] else 'decreasing'
        }

