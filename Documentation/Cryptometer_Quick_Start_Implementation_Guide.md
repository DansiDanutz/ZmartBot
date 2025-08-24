# Cryptometer API Quick-Start Implementation Guide
## For Cursor AI Self-Learning Trading Agents

**Author:** Manus AI  
**Version:** 1.0  
**Date:** July 30, 2025  
**Purpose:** Rapid implementation guide for Cursor AI development team  

---

## Executive Summary

This quick-start guide provides immediate implementation instructions for building self-learning trading agents using the Cryptometer API. Each agent operates independently per cryptocurrency symbol, continuously learning from trading outcomes to improve pattern recognition and signal generation.

**Key Implementation Points:**
- 18 API endpoints provide comprehensive market data
- 1-second rate limiting required between requests
- Individual learning agents per symbol
- Continuous feedback loops for self-improvement
- Pattern-based signal generation with outcome tracking

---

## Immediate Implementation Steps

### Step 1: API Setup (30 minutes)

```python
# Essential API Configuration
API_KEY = "k77U187e08zGf4I3SLz3sYzTEyM2KNoJ9i1N4xg2"
BASE_URL = "https://api.cryptometer.io"
RATE_LIMIT = 1.0  # seconds between requests

import requests
import time
import json

def make_api_request(endpoint, params=None):
    if params is None:
        params = {}
    params['api_key'] = API_KEY
    
    response = requests.get(f"{BASE_URL}{endpoint}", params=params)
    time.sleep(RATE_LIMIT)  # CRITICAL: Must wait 1 second
    
    return response.json() if response.status_code == 200 else None
```

### Step 2: Core Data Collection (1 hour)

**Priority Endpoints for Immediate Implementation:**

1. **Volume Flow** (`/volume-flow/`) - Primary signal source
2. **LS Ratio** (`/ls-ratio/`) - Sentiment analysis  
3. **Liquidation Data** (`/liquidation-data-v2/`) - Market stress indicators
4. **OHLCV** (`/ohlcv/`) - Price data foundation
5. **Trend Indicator V3** (`/trend-indicator-v3/`) - Trend analysis

```python
def collect_essential_data(symbol="ETH-USDT"):
    data = {}
    
    # Volume Flow - Money flow analysis
    data['volume_flow'] = make_api_request('/volume-flow/', {'timeframe': '1h'})
    
    # LS Ratio - Market sentiment
    data['ls_ratio'] = make_api_request('/ls-ratio/', {
        'e': 'binance_futures', 
        'pair': symbol, 
        'timeframe': '1h'
    })
    
    # Liquidation Data - Market stress
    data['liquidations'] = make_api_request('/liquidation-data-v2/', {
        'symbol': symbol.split('-')[0].lower()
    })
    
    # OHLCV - Price data
    data['ohlcv'] = make_api_request('/ohlcv/', {
        'e': 'binance',
        'pair': symbol,
        'timeframe': '1h'
    })
    
    # Trend Analysis
    data['trend'] = make_api_request('/trend-indicator-v3/')
    
    return data
```

### Step 3: Data Storage Schema (30 minutes)

**Essential Storage Structure:**

```python
# Symbol-specific data storage
class SymbolDataStore:
    def __init__(self, symbol):
        self.symbol = symbol
        self.historical_data = []
        self.patterns = {}
        self.signals = []
        self.outcomes = []
        
    def store_data_point(self, timestamp, endpoint_data):
        data_point = {
            'timestamp': timestamp,
            'symbol': self.symbol,
            'volume_flow': endpoint_data.get('volume_flow'),
            'ls_ratio': endpoint_data.get('ls_ratio'),
            'liquidations': endpoint_data.get('liquidations'),
            'ohlcv': endpoint_data.get('ohlcv'),
            'trend': endpoint_data.get('trend')
        }
        self.historical_data.append(data_point)
        
    def store_signal(self, signal_data):
        self.signals.append(signal_data)
        
    def store_outcome(self, signal_id, outcome_data):
        self.outcomes.append({
            'signal_id': signal_id,
            'outcome': outcome_data,
            'timestamp': time.time()
        })
```

---

## Critical Data Points to Store

### For Each API Call, Store:

**Volume Flow Data:**
- `inflow_volume`: Capital flowing in
- `outflow_volume`: Capital flowing out  
- `net_flow`: Inflow - outflow
- `flow_strength`: Flow intensity indicator

**LS Ratio Data:**
- `ratio`: Long/short position ratio
- `long_percentage`: % of long positions
- `short_percentage`: % of short positions
- `sentiment_extreme`: Flag for extreme positioning

**Liquidation Data:**
- `long_liquidations`: Long position liquidations
- `short_liquidations`: Short position liquidations
- `liquidation_ratio`: Long/short liquidation ratio
- `cascade_indicator`: Liquidation cascade flag

**OHLCV Data:**
- `open`, `high`, `low`, `close`: Price data
- `volume`: Trading volume
- `price_change`: Price change metrics

**Trend Data:**
- `trend_score`: Overall trend strength (0-100)
- `buy_pressure`: Bullish momentum
- `sell_pressure`: Bearish momentum

---

## Pattern Recognition Implementation

### Step 4: Basic Pattern Detection (2 hours)

```python
class PatternDetector:
    def __init__(self, symbol):
        self.symbol = symbol
        self.patterns = {
            'volume_divergence': self.detect_volume_divergence,
            'sentiment_extreme': self.detect_sentiment_extreme,
            'liquidation_cascade': self.detect_liquidation_cascade,
            'trend_reversal': self.detect_trend_reversal
        }
        
    def detect_volume_divergence(self, data_points):
        """Detect when volume flow diverges from price"""
        if len(data_points) < 5:
            return None
            
        recent_flows = [dp['volume_flow']['net_flow'] for dp in data_points[-5:]]
        recent_prices = [dp['ohlcv']['close'] for dp in data_points[-5:]]
        
        # Simple divergence detection
        flow_trend = recent_flows[-1] - recent_flows[0]
        price_trend = recent_prices[-1] - recent_prices[0]
        
        if (flow_trend > 0 and price_trend < 0) or (flow_trend < 0 and price_trend > 0):
            return {
                'pattern': 'volume_divergence',
                'strength': abs(flow_trend) + abs(price_trend),
                'direction': 'bullish' if flow_trend > 0 else 'bearish',
                'confidence': 0.7
            }
        return None
        
    def detect_sentiment_extreme(self, data_points):
        """Detect extreme sentiment positioning"""
        if not data_points:
            return None
            
        latest = data_points[-1]
        ls_data = latest.get('ls_ratio', {})
        
        long_pct = ls_data.get('long_percentage', 50)
        
        if long_pct > 80:  # Extreme long positioning
            return {
                'pattern': 'sentiment_extreme',
                'direction': 'bearish',  # Contrarian signal
                'strength': long_pct - 80,
                'confidence': 0.8
            }
        elif long_pct < 20:  # Extreme short positioning
            return {
                'pattern': 'sentiment_extreme', 
                'direction': 'bullish',  # Contrarian signal
                'strength': 20 - long_pct,
                'confidence': 0.8
            }
        return None
```

### Step 5: Signal Generation (1 hour)

```python
class SignalGenerator:
    def __init__(self, symbol):
        self.symbol = symbol
        self.pattern_detector = PatternDetector(symbol)
        
    def generate_signals(self, data_points):
        signals = []
        
        # Detect all patterns
        for pattern_name, detector in self.pattern_detector.patterns.items():
            pattern = detector(data_points)
            if pattern:
                signal = self.create_signal(pattern, data_points[-1])
                if signal:
                    signals.append(signal)
                    
        return signals
        
    def create_signal(self, pattern, current_data):
        """Convert pattern to trading signal"""
        signal = {
            'signal_id': f"{self.symbol}_{int(time.time())}",
            'symbol': self.symbol,
            'timestamp': time.time(),
            'pattern': pattern,
            'direction': pattern['direction'],
            'strength': pattern['strength'],
            'confidence': pattern['confidence'],
            'current_price': current_data['ohlcv']['close'],
            'market_data': current_data
        }
        
        # Add timeframe-specific targets
        signal['targets'] = {
            '24h': self.calculate_target(signal, '24h'),
            '7d': self.calculate_target(signal, '7d'),
            '30d': self.calculate_target(signal, '30d')
        }
        
        return signal
        
    def calculate_target(self, signal, timeframe):
        """Calculate target based on pattern and timeframe"""
        base_target = signal['strength'] * 0.01  # 1% per strength point
        
        timeframe_multiplier = {
            '24h': 0.5,
            '7d': 1.0, 
            '30d': 2.0
        }
        
        target = base_target * timeframe_multiplier[timeframe]
        
        return {
            'target_return': target,
            'stop_loss': target * -0.5,  # 50% of target as stop loss
            'confidence': signal['confidence']
        }
```

---

## Self-Learning Implementation

### Step 6: Outcome Tracking (1 hour)

```python
class OutcomeTracker:
    def __init__(self, symbol):
        self.symbol = symbol
        
    def track_signal_outcome(self, signal, price_data, timeframe='24h'):
        """Track actual outcome of a signal"""
        entry_price = signal['current_price']
        target = signal['targets'][timeframe]
        
        # Calculate actual performance
        for i, price_point in enumerate(price_data):
            current_price = price_point['close']
            time_elapsed = price_point['timestamp'] - signal['timestamp']
            
            # Calculate return
            if signal['direction'] == 'bullish':
                return_pct = (current_price - entry_price) / entry_price
            else:
                return_pct = (entry_price - current_price) / entry_price
                
            # Check if target reached
            if return_pct >= target['target_return']:
                return {
                    'signal_id': signal['signal_id'],
                    'outcome': 'success',
                    'actual_return': return_pct,
                    'time_to_target': time_elapsed,
                    'max_favorable': self.calculate_max_favorable(signal, price_data[:i+1]),
                    'max_adverse': self.calculate_max_adverse(signal, price_data[:i+1])
                }
                
            # Check if stop loss hit
            if return_pct <= target['stop_loss']:
                return {
                    'signal_id': signal['signal_id'],
                    'outcome': 'failure',
                    'actual_return': return_pct,
                    'time_to_stop': time_elapsed,
                    'max_favorable': self.calculate_max_favorable(signal, price_data[:i+1]),
                    'max_adverse': self.calculate_max_adverse(signal, price_data[:i+1])
                }
        
        # If neither target nor stop reached
        final_price = price_data[-1]['close']
        if signal['direction'] == 'bullish':
            final_return = (final_price - entry_price) / entry_price
        else:
            final_return = (entry_price - final_price) / entry_price
            
        return {
            'signal_id': signal['signal_id'],
            'outcome': 'incomplete',
            'actual_return': final_return,
            'max_favorable': self.calculate_max_favorable(signal, price_data),
            'max_adverse': self.calculate_max_adverse(signal, price_data)
        }
```

### Step 7: Learning Algorithm (2 hours)

```python
class LearningEngine:
    def __init__(self, symbol):
        self.symbol = symbol
        self.pattern_performance = {}
        self.learning_rate = 0.1
        
    def update_pattern_weights(self, outcomes):
        """Update pattern weights based on outcomes"""
        for outcome in outcomes:
            pattern_name = outcome['signal']['pattern']['pattern']
            
            if pattern_name not in self.pattern_performance:
                self.pattern_performance[pattern_name] = {
                    'weight': 1.0,
                    'success_rate': 0.5,
                    'avg_return': 0.0,
                    'total_signals': 0,
                    'successful_signals': 0
                }
            
            perf = self.pattern_performance[pattern_name]
            perf['total_signals'] += 1
            
            if outcome['outcome'] == 'success':
                perf['successful_signals'] += 1
                
            # Update success rate
            perf['success_rate'] = perf['successful_signals'] / perf['total_signals']
            
            # Update average return
            perf['avg_return'] = (perf['avg_return'] * (perf['total_signals'] - 1) + 
                                outcome['actual_return']) / perf['total_signals']
            
            # Update weight based on performance
            target_success_rate = 0.6  # Target 60% success rate
            performance_factor = perf['success_rate'] / target_success_rate
            return_factor = max(0.1, 1 + perf['avg_return'])
            
            new_weight = performance_factor * return_factor
            perf['weight'] = (perf['weight'] * (1 - self.learning_rate) + 
                            new_weight * self.learning_rate)
            
    def get_pattern_weight(self, pattern_name):
        """Get current weight for a pattern"""
        if pattern_name in self.pattern_performance:
            return self.pattern_performance[pattern_name]['weight']
        return 1.0
        
    def should_generate_signal(self, pattern):
        """Decide if pattern should generate signal based on learning"""
        weight = self.get_pattern_weight(pattern['pattern'])
        confidence = pattern['confidence']
        
        # Adjust confidence based on learned weight
        adjusted_confidence = confidence * weight
        
        # Only generate signal if adjusted confidence > threshold
        return adjusted_confidence > 0.5
```

---

## Production Implementation Checklist

### Immediate Requirements (Day 1):

- [ ] API key configured and tested
- [ ] Rate limiting implemented (1 second between requests)
- [ ] Basic data collection for 5 priority endpoints
- [ ] Data storage structure created
- [ ] Basic pattern detection implemented

### Week 1 Goals:

- [ ] All 18 endpoints integrated
- [ ] Pattern detection for all major patterns
- [ ] Signal generation system operational
- [ ] Outcome tracking implemented
- [ ] Basic learning algorithm functional

### Week 2 Goals:

- [ ] Historical backtesting completed
- [ ] Performance optimization implemented
- [ ] Error handling and monitoring added
- [ ] Multi-symbol support added
- [ ] Production deployment ready

---

## Key Success Metrics

**Track These Metrics for Each Symbol:**

1. **Signal Quality:**
   - Success rate (target: >50%)
   - Average return per signal
   - Risk-adjusted return (Sharpe ratio)

2. **Learning Effectiveness:**
   - Pattern weight evolution
   - Performance improvement over time
   - Adaptation to market changes

3. **System Performance:**
   - Data collection reliability (target: >99%)
   - Signal generation latency
   - Learning algorithm efficiency

---

## Critical Implementation Notes

**MUST DO:**
- Implement 1-second rate limiting between API calls
- Store ALL endpoint data for each timestamp
- Track EVERY signal outcome for learning
- Use symbol-specific learning agents
- Implement proper error handling and monitoring

**MUST NOT DO:**
- Make API calls faster than 1 per second
- Use the same learning model across different symbols
- Ignore failed signals in learning process
- Deploy without thorough backtesting
- Skip outcome tracking for any signals

---

**Quick Start Complete!** 

This guide provides the essential foundation for implementing self-learning trading agents. Refer to the comprehensive implementation guide for detailed technical specifications and advanced features.

**Next Steps:** Begin with Step 1 API setup and progress through each step systematically. Each step builds on the previous one to create a complete self-learning trading system.

