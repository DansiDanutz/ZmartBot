# Cursor Implementation Guide
## Universal Cryptocurrency Data Collection & Analysis System

**Project Name:** CryptoPatternAnalyzer  
**Target:** Universal pattern recognition for ANY cryptocurrency symbol  
**Technology Stack:** Python, PostgreSQL, Flask, OpenCV, Tesseract OCR  
**Deployment:** Docker containers with REST API  

---

## 🚀 **QUICK START FOR CURSOR**

### **Step 1: Project Setup**
```bash
# Create project directory
mkdir crypto-pattern-analyzer
cd crypto-pattern-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create project structure
mkdir -p {src,tests,data,uploads,screenshots,docs,config}
mkdir -p src/{api,database,image_processing,pattern_recognition,data_collection}
```

### **Step 2: Install Dependencies**
```bash
# Create requirements.txt
cat > requirements.txt << EOF
# Core dependencies
flask==2.3.3
psycopg2-binary==2.9.7
pandas==2.0.3
numpy==1.24.3
aiohttp==3.8.5
asyncio==3.4.3

# Image processing
opencv-python==4.8.0.76
pytesseract==0.3.10
Pillow==10.0.0

# Database
SQLAlchemy==2.0.20
alembic==1.11.3

# API and utilities
requests==2.31.0
python-dotenv==1.0.0
werkzeug==2.3.7
gunicorn==21.2.0

# Data analysis
scipy==1.11.2
scikit-learn==1.3.0
matplotlib==3.7.2

# Testing
pytest==7.4.0
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Development
black==23.7.0
flake8==6.0.0
mypy==1.5.1
EOF

pip install -r requirements.txt
```

### **Step 3: Environment Configuration**
```bash
# Create .env file
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://crypto_user:crypto_pass@localhost:5432/crypto_analysis
POSTGRES_DB=crypto_analysis
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=crypto_pass

# API Keys
COINGLASS_API_KEY=your_coinglass_api_key_here
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,bmp

# Analysis Parameters
LIQUIDATION_DOMINANCE_THRESHOLD=70.0
VOLUME_SPIKE_THRESHOLD=50.0
CONFIDENCE_THRESHOLD=75.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
EOF
```

---

## 📁 **PROJECT STRUCTURE**

```
crypto-pattern-analyzer/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main application entry point
│   ├── config.py              # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # Flask API routes
│   │   ├── models.py          # API data models
│   │   └── validators.py      # Input validation
│   ├── database/
│   │   ├── __init__.py
│   │   ├── manager.py         # Database connection manager
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── migrations/        # Database migrations
│   │   └── schema.sql         # Database schema
│   ├── image_processing/
│   │   ├── __init__.py
│   │   ├── processor.py       # Image processing engine
│   │   ├── ocr_engine.py      # OCR text extraction
│   │   └── classifiers.py     # Image type classification
│   ├── pattern_recognition/
│   │   ├── __init__.py
│   │   ├── engine.py          # Pattern recognition engine
│   │   ├── squeeze_detector.py # Squeeze event detection
│   │   ├── win_rate_calculator.py # Win rate calculations
│   │   └── ml_models.py       # Machine learning models
│   ├── data_collection/
│   │   ├── __init__.py
│   │   ├── collectors.py      # Data collection from APIs
│   │   ├── coinglass.py       # CoinGlass API integration
│   │   ├── exchanges.py       # Exchange API integrations
│   │   └── validators.py      # Data validation
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py         # Utility functions
│       ├── logging.py         # Logging configuration
│       └── exceptions.py      # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_image_processing.py
│   ├── test_pattern_recognition.py
│   └── test_data_collection.py
├── data/
│   ├── patterns/              # Pattern library data
│   ├── historical/            # Historical analysis data
│   └── samples/               # Sample images for testing
├── uploads/                   # Uploaded image storage
├── screenshots/               # Screenshot archive
├── logs/                      # Application logs
├── docs/                      # Documentation
├── config/
│   ├── docker-compose.yml     # Docker configuration
│   ├── Dockerfile            # Docker image definition
│   └── nginx.conf            # Nginx configuration
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── setup.py
```

---

## 🔧 **IMPLEMENTATION STEPS**

### **Phase 1: Core Infrastructure (Week 1)**

#### **1.1 Database Setup**
```python
# src/database/manager.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._connection = None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute query with automatic connection management"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall()
                conn.commit()
                return cursor.rowcount
```

#### **1.2 Configuration Management**
```python
# src/config.py
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    url: str = os.getenv('DATABASE_URL')
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '10'))
    max_overflow: int = int(os.getenv('DB_MAX_OVERFLOW', '20'))

@dataclass
class APIConfig:
    coinglass_key: str = os.getenv('COINGLASS_API_KEY', '')
    binance_key: str = os.getenv('BINANCE_API_KEY', '')
    binance_secret: str = os.getenv('BINANCE_SECRET_KEY', '')
    rate_limit_per_minute: int = int(os.getenv('RATE_LIMIT', '60'))

@dataclass
class ImageProcessingConfig:
    upload_folder: str = os.getenv('UPLOAD_FOLDER', './uploads')
    max_file_size: int = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))
    allowed_extensions: List[str] = os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg').split(',')
    ocr_confidence_threshold: float = float(os.getenv('OCR_CONFIDENCE', '75.0'))

@dataclass
class AnalysisConfig:
    liquidation_threshold: float = float(os.getenv('LIQUIDATION_DOMINANCE_THRESHOLD', '70.0'))
    volume_spike_threshold: float = float(os.getenv('VOLUME_SPIKE_THRESHOLD', '50.0'))
    confidence_threshold: float = float(os.getenv('CONFIDENCE_THRESHOLD', '75.0'))
    max_analysis_time: int = int(os.getenv('MAX_ANALYSIS_TIME', '300'))

class Config:
    database = DatabaseConfig()
    api = APIConfig()
    image_processing = ImageProcessingConfig()
    analysis = AnalysisConfig()
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.database.url:
            errors.append("DATABASE_URL is required")
        
        if not cls.api.coinglass_key:
            errors.append("COINGLASS_API_KEY is recommended")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
```

### **Phase 2: Image Processing Engine (Week 2)**

#### **2.1 OCR Engine**
```python
# src/image_processing/ocr_engine.py
import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self, confidence_threshold: float = 75.0):
        self.confidence_threshold = confidence_threshold
        
        # Configure Tesseract
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.%ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Advanced image preprocessing for better OCR"""
        # Load image
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply adaptive threshold
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_with_confidence(self, image_path: str) -> Dict:
        """Extract text with confidence scores"""
        try:
            processed_image = self.preprocess_image(image_path)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                processed_image, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Filter by confidence
            confident_text = []
            for i, conf in enumerate(data['conf']):
                if int(conf) > self.confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        confident_text.append({
                            'text': text,
                            'confidence': int(conf),
                            'bbox': (data['left'][i], data['top'][i], 
                                   data['width'][i], data['height'][i])
                        })
            
            # Combine all text
            full_text = ' '.join([item['text'] for item in confident_text])
            avg_confidence = np.mean([item['confidence'] for item in confident_text]) if confident_text else 0
            
            return {
                'full_text': full_text,
                'confident_text': confident_text,
                'average_confidence': avg_confidence,
                'extraction_success': len(confident_text) > 0
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                'full_text': '',
                'confident_text': [],
                'average_confidence': 0,
                'extraction_success': False,
                'error': str(e)
            }
```

#### **2.2 Image Classifier**
```python
# src/image_processing/classifiers.py
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ImageClassifier:
    def __init__(self):
        self.classification_rules = {
            'liquidation_distribution_all': [
                r'liquidation.*distribution.*all.*leverage',
                r'long.*short.*liquidation.*distribution',
                r'all_leverage'
            ],
            'liquidation_distribution_opti': [
                r'liquidation.*distribution.*optical.*opti',
                r'optical_opti',
                r'sophisticated.*liquidation'
            ],
            'price_chart_heatmap': [
                r'heatmap.*continuous',
                r'price.*chart.*liquidation',
                r'liq.*heatmap'
            ],
            'market_metrics_dashboard': [
                r'volume.*open.*interest',
                r'market.*metrics',
                r'trading.*dashboard'
            ]
        }
    
    def classify_image_type(self, extracted_text: str) -> Dict:
        """Classify image type based on extracted text"""
        text_lower = extracted_text.lower()
        
        classification_scores = {}
        
        for image_type, patterns in self.classification_rules.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
                    matched_patterns.append(pattern)
            
            if score > 0:
                classification_scores[image_type] = {
                    'score': score,
                    'confidence': min(95.0, score * 30.0),
                    'matched_patterns': matched_patterns
                }
        
        # Determine best classification
        if classification_scores:
            best_type = max(classification_scores.keys(), 
                          key=lambda x: classification_scores[x]['score'])
            return {
                'image_type': best_type,
                'confidence': classification_scores[best_type]['confidence'],
                'all_scores': classification_scores
            }
        else:
            return {
                'image_type': 'unknown',
                'confidence': 0.0,
                'all_scores': {}
            }
```

### **Phase 3: Data Collection System (Week 3)**

#### **3.1 Exchange API Integrations**
```python
# src/data_collection/exchanges.py
import aiohttp
import asyncio
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ExchangeDataCollector:
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_binance_data(self, symbol: str) -> Dict:
        """Get comprehensive data from Binance"""
        try:
            base_url = "https://api.binance.com/api/v3"
            
            # Get 24hr ticker
            ticker_url = f"{base_url}/ticker/24hr"
            params = {'symbol': f"{symbol}USDT"}
            
            async with self.session.get(ticker_url, params=params) as response:
                if response.status == 200:
                    ticker_data = await response.json()
                    
                    return {
                        'symbol': symbol,
                        'price': float(ticker_data['lastPrice']),
                        'volume_24h': float(ticker_data['volume']),
                        'volume_usdt_24h': float(ticker_data['quoteVolume']),
                        'price_change_24h': float(ticker_data['priceChangePercent']),
                        'high_24h': float(ticker_data['highPrice']),
                        'low_24h': float(ticker_data['lowPrice']),
                        'trades_count_24h': int(ticker_data['count']),
                        'timestamp': datetime.utcnow(),
                        'data_source': 'binance'
                    }
                else:
                    logger.error(f"Binance API error: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Binance data collection failed: {e}")
            return {}
    
    async def get_okx_data(self, symbol: str) -> Dict:
        """Get data from OKX"""
        try:
            base_url = "https://www.okx.com/api/v5"
            
            # Get ticker data
            ticker_url = f"{base_url}/market/ticker"
            params = {'instId': f"{symbol}-USDT"}
            
            async with self.session.get(ticker_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['code'] == '0' and data['data']:
                        ticker = data['data'][0]
                        
                        return {
                            'symbol': symbol,
                            'price': float(ticker['last']),
                            'volume_24h': float(ticker['vol24h']),
                            'volume_usdt_24h': float(ticker['volCcy24h']),
                            'price_change_24h': float(ticker['chgUtc']),
                            'high_24h': float(ticker['high24h']),
                            'low_24h': float(ticker['low24h']),
                            'timestamp': datetime.utcnow(),
                            'data_source': 'okx'
                        }
                else:
                    logger.error(f"OKX API error: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"OKX data collection failed: {e}")
            return {}
    
    async def collect_all_exchanges(self, symbol: str) -> Dict:
        """Collect data from all available exchanges"""
        tasks = [
            self.get_binance_data(symbol),
            self.get_okx_data(symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        consolidated = {
            'symbol': symbol,
            'timestamp': datetime.utcnow(),
            'exchanges': {}
        }
        
        exchange_names = ['binance', 'okx']
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result:
                consolidated['exchanges'][exchange_names[i]] = result
        
        # Calculate average price if multiple sources
        prices = [data['price'] for data in consolidated['exchanges'].values() if 'price' in data]
        if prices:
            consolidated['average_price'] = sum(prices) / len(prices)
            consolidated['price_variance'] = max(prices) - min(prices)
        
        return consolidated
```

### **Phase 4: Pattern Recognition Engine (Week 4)**

#### **4.1 Squeeze Detection Algorithm**
```python
# src/pattern_recognition/squeeze_detector.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SqueezeSignal:
    signal_type: str
    strength: float
    description: str
    timestamp: datetime

class SqueezeDetector:
    def __init__(self, dominance_threshold: float = 70.0):
        self.dominance_threshold = dominance_threshold
        
        # Signal weights for squeeze probability calculation
        self.signal_weights = {
            'liquidation_dominance': 0.4,
            'volume_spike': 0.25,
            'price_acceleration': 0.2,
            'funding_rate_extreme': 0.1,
            'open_interest_change': 0.05
        }
    
    def detect_liquidation_dominance(self, liquidation_data: Dict) -> Optional[SqueezeSignal]:
        """Detect liquidation dominance patterns"""
        long_pct = liquidation_data.get('long_liquidation_pct', 50.0)
        short_pct = liquidation_data.get('short_liquidation_pct', 50.0)
        
        dominance_strength = abs(long_pct - short_pct)
        
        if short_pct >= self.dominance_threshold:
            return SqueezeSignal(
                signal_type='short_liquidation_dominance',
                strength=min(100.0, dominance_strength * 1.2),
                description=f"Short liquidations dominate at {short_pct:.1f}%",
                timestamp=datetime.utcnow()
            )
        elif long_pct >= self.dominance_threshold:
            return SqueezeSignal(
                signal_type='long_liquidation_dominance',
                strength=min(100.0, dominance_strength * 1.2),
                description=f"Long liquidations dominate at {long_pct:.1f}%",
                timestamp=datetime.utcnow()
            )
        
        return None
    
    def detect_volume_spike(self, market_data: Dict) -> Optional[SqueezeSignal]:
        """Detect volume spikes that may indicate squeeze conditions"""
        volume_change = market_data.get('volume_change_24h', 0.0)
        
        if volume_change > 50.0:
            spike_strength = min(100.0, volume_change * 1.5)
            return SqueezeSignal(
                signal_type='volume_spike',
                strength=spike_strength,
                description=f"Volume spike of {volume_change:.1f}%",
                timestamp=datetime.utcnow()
            )
        
        return None
    
    def calculate_squeeze_probability(self, signals: List[SqueezeSignal], 
                                    liquidation_data: Dict) -> Dict:
        """Calculate overall squeeze probability based on signals"""
        
        # Base probability calculation
        total_weighted_strength = 0.0
        total_weight = 0.0
        
        signal_summary = {}
        
        for signal in signals:
            weight = self.signal_weights.get(signal.signal_type, 0.1)
            total_weighted_strength += signal.strength * weight
            total_weight += weight
            
            signal_summary[signal.signal_type] = {
                'strength': signal.strength,
                'description': signal.description,
                'weight': weight
            }
        
        # Calculate base probability
        base_probability = (total_weighted_strength / total_weight) if total_weight > 0 else 0.0
        
        # Determine squeeze type
        long_pct = liquidation_data.get('long_liquidation_pct', 50.0)
        short_pct = liquidation_data.get('short_liquidation_pct', 50.0)
        
        if short_pct > long_pct:
            squeeze_type = 'LONG_SQUEEZE'
            direction_confidence = (short_pct - 50.0) * 2  # 0-100 scale
        else:
            squeeze_type = 'SHORT_SQUEEZE'
            direction_confidence = (long_pct - 50.0) * 2  # 0-100 scale
        
        # Adjust probability based on direction confidence
        final_probability = base_probability * (direction_confidence / 100.0)
        
        # Determine severity
        if final_probability >= 80:
            severity = 'EXTREME'
        elif final_probability >= 65:
            severity = 'MAJOR'
        elif final_probability >= 45:
            severity = 'MODERATE'
        else:
            severity = 'MINOR'
        
        return {
            'squeeze_type': squeeze_type,
            'probability': round(final_probability, 1),
            'severity': severity,
            'direction_confidence': round(direction_confidence, 1),
            'signals': signal_summary,
            'signal_count': len(signals),
            'estimated_timeframe': self._estimate_timeframe(final_probability),
            'risk_level': self._assess_risk_level(final_probability, len(signals))
        }
    
    def _estimate_timeframe(self, probability: float) -> str:
        """Estimate timeframe for squeeze occurrence"""
        if probability >= 80:
            return '6-24 hours'
        elif probability >= 65:
            return '24-72 hours'
        elif probability >= 45:
            return '3-7 days'
        else:
            return 'uncertain'
    
    def _assess_risk_level(self, probability: float, signal_count: int) -> str:
        """Assess risk level for trading decisions"""
        if probability >= 75 and signal_count >= 3:
            return 'HIGH_CONFIDENCE'
        elif probability >= 60 and signal_count >= 2:
            return 'MEDIUM_CONFIDENCE'
        elif probability >= 40:
            return 'LOW_CONFIDENCE'
        else:
            return 'INSUFFICIENT_DATA'
    
    def analyze_squeeze_potential(self, symbol: str, liquidation_data: Dict, 
                                market_data: Dict) -> Dict:
        """Main method to analyze squeeze potential"""
        signals = []
        
        # Check for liquidation dominance
        liq_signal = self.detect_liquidation_dominance(liquidation_data)
        if liq_signal:
            signals.append(liq_signal)
        
        # Check for volume spikes
        vol_signal = self.detect_volume_spike(market_data)
        if vol_signal:
            signals.append(vol_signal)
        
        # Calculate squeeze probability
        squeeze_analysis = self.calculate_squeeze_probability(signals, liquidation_data)
        
        # Add metadata
        squeeze_analysis.update({
            'symbol': symbol,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'data_sources': {
                'liquidation_source': liquidation_data.get('data_source', 'unknown'),
                'market_source': market_data.get('data_source', 'unknown')
            }
        })
        
        return squeeze_analysis
```

### **Phase 5: API Development (Week 5)**

#### **5.1 Flask API Routes**
```python
# src/api/routes.py
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import asyncio
from datetime import datetime
import logging

from ..main import CryptoAnalysisEngine
from .validators import validate_symbol, validate_image_files
from .models import AnalysisRequest, AnalysisResponse

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Global analysis engine instance
analysis_engine = None

@api_bp.before_app_first_request
def initialize_engine():
    """Initialize the analysis engine"""
    global analysis_engine
    analysis_engine = CryptoAnalysisEngine()
    
    # Run async initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(analysis_engine.initialize())
    loop.close()

@api_bp.route('/analyze/<symbol>', methods=['POST'])
def analyze_symbol(symbol):
    """
    Universal analysis endpoint for any cryptocurrency symbol
    
    Parameters:
    - symbol: Cryptocurrency symbol (e.g., BTC, ETH, ADA)
    - images: List of screenshot files (multipart/form-data)
    
    Returns:
    - Comprehensive analysis including win rates, squeeze detection, patterns
    """
    try:
        # Validate symbol
        symbol = validate_symbol(symbol)
        
        # Handle file uploads
        uploaded_files = request.files.getlist('images')
        image_paths = validate_image_files(uploaded_files, symbol)
        
        # Get additional parameters
        include_historical = request.form.get('include_historical', 'false').lower() == 'true'
        timeframes = request.form.get('timeframes', '24h,7d,1m').split(',')
        
        # Create analysis request
        analysis_request = AnalysisRequest(
            symbol=symbol,
            image_paths=image_paths,
            include_historical=include_historical,
            timeframes=timeframes,
            timestamp=datetime.utcnow()
        )
        
        # Run analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis_result = loop.run_until_complete(
            analysis_engine.analyze_symbol_comprehensive(analysis_request)
        )
        loop.close()
        
        # Create response
        response = AnalysisResponse(
            success=True,
            data=analysis_result,
            processing_time=analysis_result.get('analysis_duration_seconds', 0),
            timestamp=datetime.utcnow()
        )
        
        return jsonify(response.__dict__)
        
    except ValueError as e:
        logger.warning(f"Validation error for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': 'validation_error',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Analysis failed for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': 'analysis_error',
            'message': 'Internal analysis error occurred'
        }), 500

@api_bp.route('/patterns/<symbol>')
def get_historical_patterns(symbol):
    """Get historical patterns for a specific symbol"""
    try:
        symbol = validate_symbol(symbol)
        
        # Get query parameters
        pattern_type = request.args.get('type')
        limit = int(request.args.get('limit', 50))
        min_success_rate = float(request.args.get('min_success_rate', 0.0))
        
        patterns = analysis_engine.get_historical_patterns(
            symbol=symbol,
            pattern_type=pattern_type,
            limit=limit,
            min_success_rate=min_success_rate
        )
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'patterns': patterns,
                'count': len(patterns)
            }
        })
        
    except Exception as e:
        logger.error(f"Pattern retrieval failed for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/squeeze-alerts')
def get_active_squeeze_alerts():
    """Get active squeeze alerts across all symbols"""
    try:
        # Get query parameters
        severity = request.args.get('severity')  # MINOR, MODERATE, MAJOR, EXTREME
        hours_back = int(request.args.get('hours_back', 24))
        min_probability = float(request.args.get('min_probability', 50.0))
        
        alerts = analysis_engine.get_active_squeeze_alerts(
            severity=severity,
            hours_back=hours_back,
            min_probability=min_probability
        )
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'count': len(alerts),
                'filters': {
                    'severity': severity,
                    'hours_back': hours_back,
                    'min_probability': min_probability
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Squeeze alerts retrieval failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/symbols')
def get_supported_symbols():
    """Get list of supported cryptocurrency symbols"""
    try:
        symbols = analysis_engine.get_supported_symbols()
        
        return jsonify({
            'success': True,
            'data': {
                'symbols': symbols,
                'count': len(symbols),
                'last_updated': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Symbol list retrieval failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = analysis_engine.check_database_health()
        
        # Check external APIs
        api_status = analysis_engine.check_api_health()
        
        overall_status = 'healthy' if db_status and api_status else 'degraded'
        
        return jsonify({
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {
                'database': 'healthy' if db_status else 'unhealthy',
                'external_apis': 'healthy' if api_status else 'degraded'
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'not_found',
        'message': 'Endpoint not found'
    }), 404

@api_bp.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'file_too_large',
        'message': 'Uploaded file is too large'
    }), 413

@api_bp.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'success': False,
        'error': 'rate_limit_exceeded',
        'message': 'Rate limit exceeded. Please try again later.'
    }), 429
```

---

## 🐳 **DOCKER DEPLOYMENT**

### **Docker Configuration**
```dockerfile
# config/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p uploads logs data

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=src.main:app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "src.main:app"]
```

### **Docker Compose**
```yaml
# config/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: crypto_analysis
      POSTGRES_USER: crypto_user
      POSTGRES_PASSWORD: crypto_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./src/database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U crypto_user -d crypto_analysis"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  crypto-analyzer:
    build:
      context: .
      dockerfile: config/Dockerfile
    environment:
      DATABASE_URL: postgresql://crypto_user:crypto_pass@postgres:5432/crypto_analysis
      REDIS_URL: redis://redis:6379/0
      FLASK_ENV: production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./data:/app/data
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - crypto-analyzer
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 🧪 **TESTING FRAMEWORK**

### **Test Configuration**
```python
# tests/conftest.py
import pytest
import asyncio
import tempfile
import os
from src.main import CryptoAnalysisEngine
from src.config import Config

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
async def analysis_engine():
    """Create analysis engine for testing"""
    # Use test database
    Config.database.url = "postgresql://test_user:test_pass@localhost:5432/test_crypto_analysis"
    
    engine = CryptoAnalysisEngine()
    await engine.initialize()
    
    yield engine
    
    await engine.shutdown()

@pytest.fixture
def sample_liquidation_data():
    """Sample liquidation data for testing"""
    return {
        'symbol': 'BTC',
        'long_liquidation_pct': 25.5,
        'short_liquidation_pct': 74.5,
        'extraction_confidence': 95.0,
        'data_source': 'test'
    }

@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return {
        'symbol': 'BTC',
        'price': 45000.0,
        'volume_24h': 28500000000,
        'volume_change_24h': 23.4,
        'data_source': 'test'
    }
```

---

## 📚 **USAGE EXAMPLES**

### **API Usage Examples**
```python
# Example 1: Analyze ETH with screenshots
import requests

url = "http://localhost:5000/api/v1/analyze/ETH"
files = [
    ('images', open('eth_liquidation_1.png', 'rb')),
    ('images', open('eth_liquidation_2.png', 'rb'))
]
data = {
    'include_historical': 'true',
    'timeframes': '24h,7d,1m'
}

response = requests.post(url, files=files, data=data)
analysis = response.json()

print(f"Win Rates: {analysis['data']['win_rates']}")
print(f"Squeeze Analysis: {analysis['data']['squeeze_analysis']}")
```

### **CLI Usage Examples**
```bash
# Analyze single symbol with images
python -m src.main --symbol BTC --images screenshot1.png screenshot2.png

# Run web server
python -m src.main --server --port 5000

# Batch analysis
python -m src.main --batch --symbols BTC,ETH,ADA --data-dir ./screenshots/
```

---

## 🚀 **DEPLOYMENT CHECKLIST**

### **Pre-deployment**
- [ ] Database schema created and tested
- [ ] All environment variables configured
- [ ] API keys obtained and validated
- [ ] Image processing dependencies installed
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Performance tests completed
- [ ] Security scan completed

### **Production Deployment**
- [ ] Docker images built and tested
- [ ] Database migrations applied
- [ ] SSL certificates configured
- [ ] Monitoring and logging set up
- [ ] Backup procedures implemented
- [ ] Rate limiting configured
- [ ] Health checks working
- [ ] Documentation updated

### **Post-deployment**
- [ ] Smoke tests passed
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] User acceptance testing
- [ ] Load testing completed
- [ ] Disaster recovery tested

---

## 📊 **SUCCESS METRICS**

### **Technical Metrics**
- **API Response Time:** <2 seconds for analysis
- **Image Processing Accuracy:** >85% OCR confidence
- **Database Query Performance:** <100ms average
- **System Uptime:** >99.5%
- **Error Rate:** <1%

### **Business Metrics**
- **Squeeze Prediction Accuracy:** >75%
- **Win Rate Prediction Accuracy:** >70%
- **Pattern Recognition Accuracy:** >80%
- **User Adoption:** 100+ active symbols analyzed
- **Data Coverage:** 500+ supported cryptocurrencies

This comprehensive implementation guide provides everything needed to build a production-ready universal cryptocurrency analysis system using Cursor. The modular architecture ensures scalability and maintainability while the extensive testing framework guarantees reliability.

