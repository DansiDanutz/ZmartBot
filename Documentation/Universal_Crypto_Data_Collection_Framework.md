# Universal Cryptocurrency Data Collection Framework
## Historical Pattern Analysis & Squeeze Prediction System

**Author:** Manus AI  
**Date:** August 8, 2025  
**Purpose:** Universal data collection system for ANY cryptocurrency symbol  
**Objective:** Pattern recognition, squeeze prediction, and historical validation  

---

## 📊 **CORE DATA COLLECTION TABLES**

### **Table 1: Market Snapshot Data**
```sql
CREATE TABLE market_snapshots (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(18,8) NOT NULL,
    volume_24h BIGINT,
    volume_change_24h DECIMAL(8,2),
    open_interest BIGINT,
    oi_change_24h DECIMAL(8,2),
    market_cap BIGINT,
    data_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table 2: Liquidation Analysis Data**
```sql
CREATE TABLE liquidation_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '1h', '4h', '12h', '24h'
    total_liquidations DECIMAL(15,2),
    long_liquidations DECIMAL(15,2),
    short_liquidations DECIMAL(15,2),
    long_liquidation_pct DECIMAL(5,2),
    short_liquidation_pct DECIMAL(5,2),
    liquidation_dominance VARCHAR(10), -- 'LONG' or 'SHORT'
    dominance_strength DECIMAL(5,2), -- percentage strength
    data_source VARCHAR(50),
    screenshot_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table 3: Technical Indicators**
```sql
CREATE TABLE technical_indicators (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price_position_in_range DECIMAL(5,2), -- 0-100%
    range_low DECIMAL(18,8),
    range_high DECIMAL(18,8),
    fibonacci_23_6 DECIMAL(18,8),
    fibonacci_38_2 DECIMAL(18,8),
    fibonacci_50_0 DECIMAL(18,8),
    fibonacci_61_8 DECIMAL(18,8),
    fibonacci_78_6 DECIMAL(18,8),
    rsi_14 DECIMAL(5,2),
    volume_sma_20 BIGINT,
    volume_vs_sma DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table 4: Win Rate Calculations**
```sql
CREATE TABLE win_rate_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '24h', '7d', '1m'
    long_win_rate DECIMAL(5,2),
    short_win_rate DECIMAL(5,2),
    confidence_level DECIMAL(5,2),
    market_bias VARCHAR(20), -- 'BULLISH', 'BEARISH', 'NEUTRAL'
    bias_strength VARCHAR(20), -- 'WEAK', 'MODERATE', 'STRONG', 'EXTREME'
    calculation_method VARCHAR(100),
    data_quality_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table 5: Squeeze Events Detection**
```sql
CREATE TABLE squeeze_events (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    event_start TIMESTAMP NOT NULL,
    event_end TIMESTAMP,
    event_type VARCHAR(20) NOT NULL, -- 'LONG_SQUEEZE', 'SHORT_SQUEEZE'
    trigger_price DECIMAL(18,8),
    peak_price DECIMAL(18,8),
    price_change_pct DECIMAL(8,2),
    volume_spike_pct DECIMAL(8,2),
    liquidation_volume DECIMAL(15,2),
    duration_minutes INTEGER,
    severity VARCHAR(20), -- 'MINOR', 'MODERATE', 'MAJOR', 'EXTREME'
    pre_event_signals TEXT, -- JSON array of warning signals
    post_event_analysis TEXT, -- JSON analysis results
    screenshot_paths TEXT, -- JSON array of screenshot paths
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table 6: Pattern Recognition**
```sql
CREATE TABLE pattern_library (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(100) NOT NULL,
    pattern_type VARCHAR(50), -- 'LIQUIDATION', 'VOLUME', 'PRICE', 'COMBINED'
    description TEXT,
    success_rate DECIMAL(5,2),
    avg_price_move DECIMAL(8,2),
    avg_duration_hours INTEGER,
    required_conditions TEXT, -- JSON array
    warning_signals TEXT, -- JSON array
    symbols_applicable TEXT, -- JSON array or 'ALL'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table 7: Risk Assessment Data**
```sql
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    liquidation_intensity_score DECIMAL(5,2),
    data_discrepancy_score DECIMAL(5,2),
    volume_volatility_score DECIMAL(5,2),
    market_structure_score DECIMAL(5,2),
    total_risk_score DECIMAL(5,2),
    risk_level VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'
    max_position_size_pct DECIMAL(5,2),
    recommended_stop_loss DECIMAL(18,8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table 8: Cycle Analysis**
```sql
CREATE TABLE cycle_analysis (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    cycle_type VARCHAR(20), -- 'SHORT', 'MEDIUM', 'LONG', '4YEAR'
    current_cycle_position DECIMAL(5,2), -- 0-100%
    cycle_start_price DECIMAL(18,8),
    cycle_low DECIMAL(18,8),
    cycle_high DECIMAL(18,8),
    projected_peak DECIMAL(18,8),
    projected_peak_date DATE,
    confidence_level DECIMAL(5,2),
    supporting_factors TEXT, -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔍 **IMAGE ANALYSIS DATA EXTRACTION**

### **Kingfisher Screenshot Analysis Framework**

#### **Screenshot Type 1: Liquidation Distribution (All Leverage)**
```python
def extract_liquidation_distribution_data(image_path, symbol):
    """Extract data from liquidation distribution screenshots"""
    return {
        'symbol': symbol,
        'long_liquidation_pct': float,  # e.g., 85.7
        'short_liquidation_pct': float, # e.g., 14.3
        'trend_arrows': str,            # e.g., '↓↓', '↑↑', '→'
        'market_sentiment': str,        # 'BEARISH', 'BULLISH', 'NEUTRAL'
        'data_source': 'kingfisher_all_leverage',
        'screenshot_path': image_path
    }
```

#### **Screenshot Type 2: Liquidation Distribution (Optical Opti)**
```python
def extract_optical_opti_data(image_path, symbol):
    """Extract data from optical optimization screenshots"""
    return {
        'symbol': symbol,
        'long_liquidation_pct': float,  # e.g., 56.3
        'short_liquidation_pct': float, # e.g., 43.7
        'sophistication_level': 'PROFESSIONAL',
        'data_source': 'kingfisher_optical_opti',
        'screenshot_path': image_path
    }
```

#### **Screenshot Type 3: Price Chart with Liquidation Heatmap**
```python
def extract_price_chart_data(image_path, symbol):
    """Extract data from price chart screenshots"""
    return {
        'symbol': symbol,
        'current_price': float,
        'price_range_low': float,
        'price_range_high': float,
        'liquidation_clusters': list,   # [{'price': float, 'intensity': str}]
        'volume_profile': dict,         # {'high': float, 'low': float, 'avg': float}
        'timeframe': str,               # '1D', '4H', etc.
        'data_source': 'kingfisher_chart',
        'screenshot_path': image_path
    }
```

#### **Screenshot Type 4: Market Metrics Dashboard**
```python
def extract_market_metrics_data(image_path, symbol):
    """Extract data from market metrics screenshots"""
    return {
        'symbol': symbol,
        'volume_24h': float,
        'volume_change_24h': float,
        'open_interest': float,
        'oi_change_24h': float,
        'funding_rate': float,
        'long_short_ratio': float,
        'data_source': 'kingfisher_metrics',
        'screenshot_path': image_path
    }
```

---

## 🎯 **PATTERN DETECTION ALGORITHMS**

### **Squeeze Detection Algorithm**
```python
def detect_squeeze_pattern(symbol, timeframe='24h'):
    """
    Detect potential squeeze events based on liquidation patterns
    """
    criteria = {
        'liquidation_dominance_threshold': 70,  # % dominance
        'volume_spike_threshold': 50,           # % increase
        'price_acceleration': True,             # Price moving in squeeze direction
        'liquidation_cascade': True,            # Increasing liquidation intensity
        'time_compression': True                # Events happening rapidly
    }
    
    signals = {
        'long_squeeze_signals': [
            'short_liquidation_dominance > 70%',
            'volume_spike > 50%',
            'price_acceleration_upward',
            'decreasing_short_positions',
            'funding_rate_positive_spike'
        ],
        'short_squeeze_signals': [
            'long_liquidation_dominance > 70%',
            'volume_spike > 50%',
            'price_acceleration_downward',
            'decreasing_long_positions',
            'funding_rate_negative_spike'
        ]
    }
    
    return analysis_result
```

### **Win Rate Prediction Model**
```python
def calculate_predictive_win_rates(symbol, historical_data):
    """
    Calculate win rates based on current conditions vs historical patterns
    """
    factors = {
        'liquidation_pattern_similarity': weight_30_percent,
        'volume_pattern_match': weight_25_percent,
        'price_position_similarity': weight_20_percent,
        'market_structure_alignment': weight_15_percent,
        'external_factors': weight_10_percent
    }
    
    return {
        'long_win_rate_24h': float,
        'short_win_rate_24h': float,
        'confidence_level': float,
        'similar_historical_events': list,
        'success_probability': float
    }
```

---

## 📋 **DATA COLLECTION WORKFLOW**

### **Step 1: Image Processing Pipeline**
```python
class UniversalImageProcessor:
    def __init__(self):
        self.supported_symbols = 'ALL'  # Universal support
        self.image_types = [
            'liquidation_distribution_all',
            'liquidation_distribution_opti', 
            'price_chart_heatmap',
            'market_metrics_dashboard'
        ]
    
    def process_image_batch(self, images, symbol):
        """Process multiple images for a symbol"""
        extracted_data = {}
        for image in images:
            image_type = self.classify_image_type(image)
            data = self.extract_data_by_type(image, image_type, symbol)
            extracted_data[image_type] = data
        
        return self.consolidate_data(extracted_data, symbol)
    
    def store_to_database(self, consolidated_data):
        """Store extracted data to appropriate tables"""
        # Insert into market_snapshots
        # Insert into liquidation_data  
        # Insert into technical_indicators
        # Calculate and insert win_rates
        # Detect and insert squeeze_events
        # Update pattern_library
        # Calculate and insert risk_assessment
```

### **Step 2: Real-time Data Integration**
```python
class RealTimeDataCollector:
    def __init__(self):
        self.data_sources = [
            'coinglass',
            'binance',
            'okx', 
            'bybit',
            'bitfinex'
        ]
    
    def collect_market_data(self, symbol):
        """Collect real-time market data"""
        return {
            'price_data': self.get_price_data(symbol),
            'volume_data': self.get_volume_data(symbol),
            'liquidation_data': self.get_liquidation_data(symbol),
            'funding_data': self.get_funding_data(symbol),
            'oi_data': self.get_open_interest_data(symbol)
        }
    
    def sync_with_image_data(self, image_data, real_time_data):
        """Synchronize image analysis with real-time data"""
        return consolidated_dataset
```

### **Step 3: Pattern Recognition Engine**
```python
class PatternRecognitionEngine:
    def __init__(self):
        self.pattern_library = self.load_pattern_library()
        self.ml_models = self.load_trained_models()
    
    def analyze_current_conditions(self, symbol):
        """Analyze current market conditions against historical patterns"""
        current_data = self.get_current_data(symbol)
        similar_patterns = self.find_similar_patterns(current_data)
        
        return {
            'pattern_matches': similar_patterns,
            'squeeze_probability': float,
            'direction_prediction': str,
            'confidence_score': float,
            'recommended_action': str
        }
    
    def update_pattern_library(self, new_event_data):
        """Update pattern library with new validated events"""
        # Validate event outcome
        # Update success rates
        # Add new pattern variations
        # Retrain prediction models
```

---

## 🛠 **IMPLEMENTATION PLAN FOR CURSOR**

### **Phase 1: Database Setup (Week 1)**
```bash
# Create PostgreSQL database
createdb crypto_pattern_analysis

# Run table creation scripts
psql crypto_pattern_analysis < create_tables.sql

# Set up indexes for performance
psql crypto_pattern_analysis < create_indexes.sql
```

### **Phase 2: Image Processing Module (Week 2-3)**
```python
# File: image_processor.py
class ImageProcessor:
    """
    Universal image processing for any cryptocurrency symbol
    Handles Kingfisher screenshots and extracts structured data
    """
    
    def __init__(self):
        # Initialize OCR engines
        # Load image classification models
        # Set up data extraction templates
        pass
    
    def process_liquidation_screenshot(self, image_path, symbol):
        # Extract liquidation percentages
        # Identify trend arrows
        # Determine market sentiment
        # Return structured data
        pass
    
    def process_price_chart(self, image_path, symbol):
        # Extract current price
        # Identify support/resistance levels
        # Map liquidation clusters
        # Calculate technical indicators
        pass
```

### **Phase 3: Data Integration Layer (Week 4)**
```python
# File: data_integrator.py
class DataIntegrator:
    """
    Integrates image analysis with real-time market data
    Handles data validation and consistency checks
    """
    
    def __init__(self):
        # Initialize API connections
        # Set up data validation rules
        # Configure data sources
        pass
    
    def integrate_data_sources(self, symbol, image_data, api_data):
        # Validate data consistency
        # Resolve conflicts between sources
        # Calculate composite metrics
        # Return unified dataset
        pass
```

### **Phase 4: Pattern Recognition System (Week 5-6)**
```python
# File: pattern_engine.py
class PatternEngine:
    """
    Identifies patterns and predicts squeeze events
    Maintains historical pattern library
    """
    
    def __init__(self):
        # Load historical patterns
        # Initialize ML models
        # Set up prediction algorithms
        pass
    
    def detect_squeeze_setup(self, symbol, current_data):
        # Analyze liquidation patterns
        # Check volume confirmations
        # Evaluate price positioning
        # Calculate squeeze probability
        pass
    
    def predict_win_rates(self, symbol, market_conditions):
        # Compare with historical patterns
        # Apply machine learning models
        # Calculate confidence intervals
        # Return probability assessments
        pass
```

### **Phase 5: API and Dashboard (Week 7-8)**
```python
# File: api_server.py
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/analyze/<symbol>', methods=['POST'])
def analyze_symbol(symbol):
    """
    Universal analysis endpoint for any cryptocurrency symbol
    Accepts image uploads and returns comprehensive analysis
    """
    images = request.files.getlist('images')
    
    # Process images
    image_data = process_images(images, symbol)
    
    # Get real-time data
    market_data = get_market_data(symbol)
    
    # Run analysis
    analysis = run_comprehensive_analysis(symbol, image_data, market_data)
    
    return jsonify(analysis)

@app.route('/api/patterns/<symbol>')
def get_patterns(symbol):
    """Get historical patterns for a symbol"""
    patterns = get_historical_patterns(symbol)
    return jsonify(patterns)

@app.route('/api/squeeze-alerts')
def get_squeeze_alerts():
    """Get active squeeze alerts across all symbols"""
    alerts = get_active_squeeze_alerts()
    return jsonify(alerts)
```

---

## 📊 **SAMPLE DATA STRUCTURE**

### **Complete Analysis Output Example**
```json
{
  "symbol": "BTC",
  "timestamp": "2025-08-08T13:00:00Z",
  "market_snapshot": {
    "price": 45234.56,
    "volume_24h": 28500000000,
    "volume_change": 23.4,
    "open_interest": 15600000000,
    "oi_change": 3.8
  },
  "liquidation_analysis": {
    "24h": {
      "total": 156.7,
      "long": 34.2,
      "short": 122.5,
      "dominance": "SHORT",
      "dominance_pct": 78.2
    },
    "pattern_type": "BULLISH_SQUEEZE_SETUP"
  },
  "win_rates": {
    "24h": {"long": 67.3, "short": 32.7},
    "7d": {"long": 62.1, "short": 37.9},
    "1m": {"long": 55.8, "short": 44.2}
  },
  "squeeze_analysis": {
    "probability": 73.5,
    "type": "LONG_SQUEEZE",
    "estimated_trigger": 46500,
    "potential_target": 52000,
    "timeframe": "24-72 hours"
  },
  "risk_assessment": {
    "total_score": 68.4,
    "level": "HIGH",
    "max_position": 2.5,
    "stop_loss": 43800
  },
  "historical_matches": [
    {
      "date": "2024-03-15",
      "similarity": 87.3,
      "outcome": "SUCCESSFUL_SQUEEZE",
      "price_move": 18.7
    }
  ]
}
```

---

## 🎯 **CURSOR IMPLEMENTATION CHECKLIST**

### **Database Setup**
- [ ] Create PostgreSQL database
- [ ] Implement all 8 core tables
- [ ] Set up proper indexes
- [ ] Create data validation triggers
- [ ] Set up backup procedures

### **Image Processing**
- [ ] Implement OCR for text extraction
- [ ] Create image classification system
- [ ] Build data extraction templates
- [ ] Add error handling and validation
- [ ] Test with multiple symbols

### **Data Integration**
- [ ] Connect to CoinGlass API
- [ ] Integrate exchange APIs (Binance, OKX, etc.)
- [ ] Implement data validation logic
- [ ] Create conflict resolution algorithms
- [ ] Add real-time data streaming

### **Pattern Recognition**
- [ ] Build pattern matching algorithms
- [ ] Implement squeeze detection logic
- [ ] Create win rate calculation engine
- [ ] Add machine learning models
- [ ] Build pattern library management

### **API Development**
- [ ] Create RESTful API endpoints
- [ ] Implement file upload handling
- [ ] Add authentication and rate limiting
- [ ] Create comprehensive documentation
- [ ] Build monitoring and logging

### **Testing & Validation**
- [ ] Test with multiple cryptocurrencies
- [ ] Validate against historical events
- [ ] Performance testing with large datasets
- [ ] User acceptance testing
- [ ] Security testing

---

## 📈 **SUCCESS METRICS**

### **Accuracy Targets**
- **Squeeze Prediction Accuracy:** >75%
- **Win Rate Prediction Accuracy:** >70%
- **Pattern Recognition Accuracy:** >80%
- **Data Processing Speed:** <5 seconds per analysis
- **System Uptime:** >99.5%

### **Coverage Goals**
- **Supported Symbols:** All major cryptocurrencies (500+)
- **Data Sources:** 5+ major exchanges
- **Pattern Library:** 100+ validated patterns
- **Historical Data:** 2+ years of squeeze events
- **Real-time Processing:** <1 minute latency

This comprehensive framework provides everything needed to build a universal cryptocurrency analysis system that can predict squeeze events and validate patterns across ANY trading symbol.

