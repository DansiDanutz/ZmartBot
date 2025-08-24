#!/usr/bin/env python3
"""
Universal Cryptocurrency Data Collection and Analysis System
Template for Cursor Implementation

Author: Manus AI
Date: August 8, 2025
Purpose: Universal pattern recognition and squeeze prediction for ANY cryptocurrency symbol
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from decimal import Decimal
import asyncio
import aiohttp
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import numpy as np
from PIL import Image
import pytesseract
import cv2
import requests
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    """Configuration settings for the application"""
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/crypto_analysis')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    
    # API Keys
    COINGLASS_API_KEY = os.getenv('COINGLASS_API_KEY', '')
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
    
    # Analysis Parameters
    LIQUIDATION_DOMINANCE_THRESHOLD = 70.0  # % for squeeze detection
    VOLUME_SPIKE_THRESHOLD = 50.0  # % for volume spike detection
    CONFIDENCE_THRESHOLD = 75.0  # % minimum confidence for predictions

# Data Models
@dataclass
class MarketSnapshot:
    """Market snapshot data model"""
    symbol: str
    timestamp: datetime
    price: Decimal
    volume_24h: Optional[int] = None
    volume_change_24h: Optional[Decimal] = None
    open_interest: Optional[int] = None
    oi_change_24h: Optional[Decimal] = None
    market_cap: Optional[int] = None
    data_source: str = 'unknown'
    data_quality_score: Decimal = Decimal('100.0')

@dataclass
class LiquidationData:
    """Liquidation analysis data model"""
    symbol: str
    timestamp: datetime
    timeframe: str
    total_liquidations: Decimal
    long_liquidations: Decimal
    short_liquidations: Decimal
    long_liquidation_pct: Decimal
    short_liquidation_pct: Decimal
    liquidation_dominance: str
    dominance_strength: Decimal
    liquidation_intensity: str
    cascade_potential: Decimal
    data_source: str
    screenshot_path: Optional[str] = None
    extraction_confidence: Decimal = Decimal('100.0')

@dataclass
class SqueezeEvent:
    """Squeeze event data model"""
    symbol: str
    event_start: datetime
    event_type: str  # 'LONG_SQUEEZE' or 'SHORT_SQUEEZE'
    event_status: str = 'DETECTED'
    trigger_price: Optional[Decimal] = None
    peak_price: Optional[Decimal] = None
    severity: str = 'MODERATE'
    pre_event_signals: List[str] = None
    prediction_accuracy: Optional[Decimal] = None

@dataclass
class WinRateAnalysis:
    """Win rate analysis data model"""
    symbol: str
    timestamp: datetime
    timeframe: str
    long_win_rate: Decimal
    short_win_rate: Decimal
    confidence_level: Decimal
    market_bias: str
    bias_strength: str
    calculation_method: str
    data_quality_score: Decimal

# Database Manager
class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a query and return results"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall()
                return []
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
            raise
    
    def insert_market_snapshot(self, snapshot: MarketSnapshot) -> str:
        """Insert market snapshot data"""
        query = """
        INSERT INTO market_snapshots 
        (symbol, timestamp, price, volume_24h, volume_change_24h, 
         open_interest, oi_change_24h, market_cap, data_source, data_quality_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        params = (
            snapshot.symbol, snapshot.timestamp, snapshot.price,
            snapshot.volume_24h, snapshot.volume_change_24h,
            snapshot.open_interest, snapshot.oi_change_24h,
            snapshot.market_cap, snapshot.data_source, snapshot.data_quality_score
        )
        
        result = self.execute_query(query, params)
        self.connection.commit()
        return result[0]['id'] if result else None
    
    def insert_liquidation_data(self, liquidation: LiquidationData) -> str:
        """Insert liquidation analysis data"""
        query = """
        INSERT INTO liquidation_data 
        (symbol, timestamp, timeframe, total_liquidations, long_liquidations, 
         short_liquidations, long_liquidation_pct, short_liquidation_pct,
         liquidation_dominance, dominance_strength, liquidation_intensity,
         cascade_potential, data_source, screenshot_path, extraction_confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        params = (
            liquidation.symbol, liquidation.timestamp, liquidation.timeframe,
            liquidation.total_liquidations, liquidation.long_liquidations,
            liquidation.short_liquidations, liquidation.long_liquidation_pct,
            liquidation.short_liquidation_pct, liquidation.liquidation_dominance,
            liquidation.dominance_strength, liquidation.liquidation_intensity,
            liquidation.cascade_potential, liquidation.data_source,
            liquidation.screenshot_path, liquidation.extraction_confidence
        )
        
        result = self.execute_query(query, params)
        self.connection.commit()
        return result[0]['id'] if result else None
    
    def get_historical_patterns(self, symbol: str, pattern_type: str = None) -> List[Dict]:
        """Get historical patterns for a symbol"""
        query = """
        SELECT * FROM pattern_library 
        WHERE symbols_applicable = 'ALL' OR symbols_applicable LIKE %s
        """
        params = [f'%{symbol}%']
        
        if pattern_type:
            query += " AND pattern_type = %s"
            params.append(pattern_type)
        
        query += " ORDER BY success_rate DESC"
        
        return self.execute_query(query, tuple(params))

# Image Processing Engine
class ImageProcessor:
    """Handles image analysis and data extraction"""
    
    def __init__(self):
        self.supported_formats = Config.ALLOWED_EXTENSIONS
        
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.supported_formats
    
    def calculate_image_hash(self, image_path: str) -> str:
        """Calculate hash for duplicate detection"""
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for OCR"""
        # Load image
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply noise reduction
        denoised = cv2.medianBlur(gray, 3)
        
        # Apply threshold
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            processed_image = self.preprocess_image(image_path)
            text = pytesseract.image_to_string(processed_image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def classify_image_type(self, image_path: str) -> str:
        """Classify the type of screenshot"""
        text = self.extract_text_from_image(image_path)
        text_lower = text.lower()
        
        if 'liquidation' in text_lower and 'distribution' in text_lower:
            if 'optical' in text_lower or 'opti' in text_lower:
                return 'liquidation_distribution_opti'
            else:
                return 'liquidation_distribution_all'
        elif 'heatmap' in text_lower or 'chart' in text_lower:
            return 'price_chart_heatmap'
        elif 'volume' in text_lower or 'metrics' in text_lower:
            return 'market_metrics_dashboard'
        else:
            return 'unknown'
    
    def extract_liquidation_percentages(self, image_path: str, symbol: str) -> Dict:
        """Extract liquidation percentages from screenshot"""
        text = self.extract_text_from_image(image_path)
        
        # Initialize result
        result = {
            'symbol': symbol,
            'long_liquidation_pct': None,
            'short_liquidation_pct': None,
            'extraction_confidence': 0.0,
            'raw_text': text
        }
        
        try:
            # Look for percentage patterns
            import re
            
            # Find symbol-specific line
            lines = text.split('\n')
            symbol_line = None
            
            for line in lines:
                if symbol.upper() in line.upper():
                    symbol_line = line
                    break
            
            if symbol_line:
                # Extract percentages using regex
                percentages = re.findall(r'(\d+\.?\d*)%', symbol_line)
                
                if len(percentages) >= 2:
                    # Assume first percentage is long, second is short
                    result['long_liquidation_pct'] = float(percentages[0])
                    result['short_liquidation_pct'] = float(percentages[1])
                    result['extraction_confidence'] = 85.0
                    
                    # Validate percentages sum to approximately 100
                    total = result['long_liquidation_pct'] + result['short_liquidation_pct']
                    if 95 <= total <= 105:
                        result['extraction_confidence'] = 95.0
                    
        except Exception as e:
            logger.error(f"Percentage extraction failed: {e}")
            result['extraction_confidence'] = 0.0
        
        return result
    
    def process_image_batch(self, image_paths: List[str], symbol: str) -> Dict:
        """Process multiple images for a symbol"""
        results = {}
        
        for image_path in image_paths:
            try:
                image_type = self.classify_image_type(image_path)
                image_hash = self.calculate_image_hash(image_path)
                
                if image_type.startswith('liquidation_distribution'):
                    data = self.extract_liquidation_percentages(image_path, symbol)
                    data['image_type'] = image_type
                    data['image_hash'] = image_hash
                    data['screenshot_path'] = image_path
                    results[image_type] = data
                
            except Exception as e:
                logger.error(f"Failed to process image {image_path}: {e}")
        
        return results

# Market Data Collector
class MarketDataCollector:
    """Collects real-time market data from various sources"""
    
    def __init__(self):
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.close()
    
    async def get_coinglass_data(self, symbol: str) -> Dict:
        """Get data from CoinGlass API"""
        try:
            url = f"https://open-api.coinglass.com/public/v2/liquidation"
            params = {
                'symbol': symbol,
                'time_type': '24h'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"CoinGlass API error: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"CoinGlass data collection failed: {e}")
            return {}
    
    async def get_binance_data(self, symbol: str) -> Dict:
        """Get data from Binance API"""
        try:
            # 24hr ticker statistics
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {'symbol': f"{symbol}USDT"}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'price': float(data['lastPrice']),
                        'volume_24h': float(data['volume']),
                        'price_change_24h': float(data['priceChangePercent']),
                        'data_source': 'binance'
                    }
                else:
                    logger.error(f"Binance API error: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Binance data collection failed: {e}")
            return {}
    
    async def collect_comprehensive_data(self, symbol: str) -> Dict:
        """Collect data from all available sources"""
        tasks = [
            self.get_coinglass_data(symbol),
            self.get_binance_data(symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Consolidate results
        consolidated = {
            'symbol': symbol,
            'timestamp': datetime.utcnow(),
            'sources': {}
        }
        
        source_names = ['coinglass', 'binance']
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result:
                consolidated['sources'][source_names[i]] = result
        
        return consolidated

# Pattern Recognition Engine
class PatternRecognitionEngine:
    """Identifies patterns and predicts squeeze events"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.patterns = self.load_pattern_library()
    
    def load_pattern_library(self) -> List[Dict]:
        """Load pattern library from database"""
        try:
            return self.db.get_historical_patterns('ALL')
        except Exception as e:
            logger.error(f"Failed to load pattern library: {e}")
            return []
    
    def calculate_win_rates(self, symbol: str, liquidation_data: Dict, 
                          market_data: Dict) -> Dict:
        """Calculate win rates based on current conditions"""
        
        # Extract key metrics
        long_liq_pct = liquidation_data.get('long_liquidation_pct', 50.0)
        short_liq_pct = liquidation_data.get('short_liquidation_pct', 50.0)
        dominance_strength = abs(long_liq_pct - short_liq_pct)
        
        # Base win rates (neutral market)
        base_long_rate = 50.0
        base_short_rate = 50.0
        
        # Adjust based on liquidation dominance
        if short_liq_pct > long_liq_pct:
            # Short liquidation dominance = bullish for longs
            adjustment = min(dominance_strength * 0.3, 25.0)
            base_long_rate += adjustment
            base_short_rate -= adjustment
        else:
            # Long liquidation dominance = bearish for longs
            adjustment = min(dominance_strength * 0.3, 25.0)
            base_long_rate -= adjustment
            base_short_rate += adjustment
        
        # Calculate confidence based on data quality and dominance strength
        confidence = min(90.0, 50.0 + dominance_strength * 0.5)
        
        # Determine market bias
        if base_long_rate > 55:
            bias = 'BULLISH'
            if base_long_rate > 65:
                bias_strength = 'STRONG'
            elif base_long_rate > 60:
                bias_strength = 'MODERATE'
            else:
                bias_strength = 'WEAK'
        elif base_short_rate > 55:
            bias = 'BEARISH'
            if base_short_rate > 65:
                bias_strength = 'STRONG'
            elif base_short_rate > 60:
                bias_strength = 'MODERATE'
            else:
                bias_strength = 'WEAK'
        else:
            bias = 'NEUTRAL'
            bias_strength = 'WEAK'
        
        return {
            '24h': {
                'long_win_rate': round(base_long_rate, 1),
                'short_win_rate': round(base_short_rate, 1),
                'confidence_level': round(confidence, 1),
                'market_bias': bias,
                'bias_strength': bias_strength
            },
            '7d': {
                'long_win_rate': round(base_long_rate * 0.9, 1),  # Moderate toward neutral
                'short_win_rate': round(base_short_rate * 0.9 + 5, 1),
                'confidence_level': round(confidence * 0.8, 1),
                'market_bias': bias if bias_strength == 'STRONG' else 'NEUTRAL',
                'bias_strength': 'WEAK' if bias_strength != 'STRONG' else 'MODERATE'
            },
            '1m': {
                'long_win_rate': round(50 + (base_long_rate - 50) * 0.3, 1),  # Strong reversion
                'short_win_rate': round(50 + (base_short_rate - 50) * 0.3, 1),
                'confidence_level': round(confidence * 0.6, 1),
                'market_bias': 'NEUTRAL',
                'bias_strength': 'WEAK'
            }
        }
    
    def detect_squeeze_potential(self, symbol: str, liquidation_data: Dict, 
                               market_data: Dict) -> Dict:
        """Detect potential squeeze events"""
        
        long_liq_pct = liquidation_data.get('long_liquidation_pct', 50.0)
        short_liq_pct = liquidation_data.get('short_liquidation_pct', 50.0)
        dominance_strength = abs(long_liq_pct - short_liq_pct)
        
        # Determine squeeze type and probability
        if short_liq_pct >= Config.LIQUIDATION_DOMINANCE_THRESHOLD:
            squeeze_type = 'LONG_SQUEEZE'
            probability = min(95.0, 30.0 + dominance_strength * 0.8)
        elif long_liq_pct >= Config.LIQUIDATION_DOMINANCE_THRESHOLD:
            squeeze_type = 'SHORT_SQUEEZE'
            probability = min(95.0, 30.0 + dominance_strength * 0.8)
        else:
            squeeze_type = 'NONE'
            probability = 0.0
        
        # Determine severity
        if dominance_strength >= 80:
            severity = 'EXTREME'
        elif dominance_strength >= 70:
            severity = 'MAJOR'
        elif dominance_strength >= 60:
            severity = 'MODERATE'
        else:
            severity = 'MINOR'
        
        # Generate signals
        signals = []
        if dominance_strength > 70:
            signals.append(f"{squeeze_type.split('_')[0].lower()}_liquidation_dominance")
        if dominance_strength > 80:
            signals.append("extreme_imbalance")
        
        return {
            'squeeze_type': squeeze_type,
            'probability': round(probability, 1),
            'severity': severity,
            'dominance_strength': round(dominance_strength, 1),
            'signals': signals,
            'estimated_timeframe': '24-72 hours' if probability > 60 else 'uncertain'
        }

# Main Analysis Engine
class CryptoAnalysisEngine:
    """Main engine that coordinates all analysis components"""
    
    def __init__(self):
        self.db = DatabaseManager(Config.DATABASE_URL)
        self.image_processor = ImageProcessor()
        self.market_collector = MarketDataCollector()
        self.pattern_engine = None  # Initialize after DB connection
        
    async def initialize(self):
        """Initialize the analysis engine"""
        self.db.connect()
        self.pattern_engine = PatternRecognitionEngine(self.db)
        logger.info("Analysis engine initialized")
    
    async def shutdown(self):
        """Shutdown the analysis engine"""
        await self.market_collector.close()
        self.db.disconnect()
        logger.info("Analysis engine shutdown")
    
    async def analyze_symbol(self, symbol: str, image_paths: List[str] = None) -> Dict:
        """Perform comprehensive analysis for a symbol"""
        try:
            analysis_start = datetime.utcnow()
            
            # Collect market data
            market_data = await self.market_collector.collect_comprehensive_data(symbol)
            
            # Process images if provided
            image_data = {}
            if image_paths:
                image_data = self.image_processor.process_image_batch(image_paths, symbol)
            
            # Extract liquidation data
            liquidation_data = {}
            if 'liquidation_distribution_all' in image_data:
                liquidation_data = image_data['liquidation_distribution_all']
            
            # Calculate win rates
            win_rates = {}
            if liquidation_data:
                win_rates = self.pattern_engine.calculate_win_rates(
                    symbol, liquidation_data, market_data
                )
            
            # Detect squeeze potential
            squeeze_analysis = {}
            if liquidation_data:
                squeeze_analysis = self.pattern_engine.detect_squeeze_potential(
                    symbol, liquidation_data, market_data
                )
            
            # Store data in database
            if market_data.get('sources', {}).get('binance'):
                binance_data = market_data['sources']['binance']
                snapshot = MarketSnapshot(
                    symbol=symbol,
                    timestamp=analysis_start,
                    price=Decimal(str(binance_data['price'])),
                    volume_24h=int(binance_data['volume_24h']),
                    data_source='binance'
                )
                self.db.insert_market_snapshot(snapshot)
            
            if liquidation_data:
                liq_data = LiquidationData(
                    symbol=symbol,
                    timestamp=analysis_start,
                    timeframe='24h',
                    total_liquidations=Decimal('0'),  # Would be calculated from API
                    long_liquidations=Decimal('0'),
                    short_liquidations=Decimal('0'),
                    long_liquidation_pct=Decimal(str(liquidation_data['long_liquidation_pct'])),
                    short_liquidation_pct=Decimal(str(liquidation_data['short_liquidation_pct'])),
                    liquidation_dominance='SHORT' if liquidation_data['short_liquidation_pct'] > 50 else 'LONG',
                    dominance_strength=Decimal(str(abs(liquidation_data['long_liquidation_pct'] - liquidation_data['short_liquidation_pct']))),
                    liquidation_intensity='HIGH',
                    cascade_potential=Decimal('75.0'),
                    data_source='kingfisher_screenshot',
                    screenshot_path=liquidation_data.get('screenshot_path'),
                    extraction_confidence=Decimal(str(liquidation_data['extraction_confidence']))
                )
                self.db.insert_liquidation_data(liq_data)
            
            # Compile final analysis
            analysis_result = {
                'symbol': symbol,
                'timestamp': analysis_start.isoformat(),
                'market_data': market_data,
                'liquidation_analysis': liquidation_data,
                'win_rates': win_rates,
                'squeeze_analysis': squeeze_analysis,
                'image_processing_results': image_data,
                'analysis_duration_seconds': (datetime.utcnow() - analysis_start).total_seconds()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            raise

# Flask API Application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Global analysis engine
analysis_engine = None

@app.before_first_request
async def initialize_app():
    """Initialize the application"""
    global analysis_engine
    analysis_engine = CryptoAnalysisEngine()
    await analysis_engine.initialize()

@app.teardown_appcontext
async def shutdown_app(exception):
    """Shutdown the application"""
    global analysis_engine
    if analysis_engine:
        await analysis_engine.shutdown()

@app.route('/api/analyze/<symbol>', methods=['POST'])
def analyze_symbol_endpoint(symbol):
    """
    Universal analysis endpoint for any cryptocurrency symbol
    Accepts image uploads and returns comprehensive analysis
    """
    try:
        # Validate symbol
        symbol = symbol.upper()
        
        # Handle file uploads
        uploaded_files = request.files.getlist('images')
        image_paths = []
        
        for file in uploaded_files:
            if file and analysis_engine.image_processor.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 
                                      f"{symbol}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}")
                file.save(filepath)
                image_paths.append(filepath)
        
        # Run analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis_result = loop.run_until_complete(
            analysis_engine.analyze_symbol(symbol, image_paths)
        )
        loop.close()
        
        return jsonify({
            'success': True,
            'data': analysis_result
        })
        
    except Exception as e:
        logger.error(f"API analysis failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/patterns/<symbol>')
def get_patterns_endpoint(symbol):
    """Get historical patterns for a symbol"""
    try:
        patterns = analysis_engine.db.get_historical_patterns(symbol.upper())
        return jsonify({
            'success': True,
            'data': patterns
        })
    except Exception as e:
        logger.error(f"Pattern retrieval failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/squeeze-alerts')
def get_squeeze_alerts_endpoint():
    """Get active squeeze alerts across all symbols"""
    try:
        query = """
        SELECT symbol, event_type, event_start, trigger_price, 
               severity, prediction_accuracy, pre_event_signals
        FROM squeeze_events 
        WHERE event_status IN ('DETECTED', 'CONFIRMED') 
            AND event_start > NOW() - INTERVAL '24 hours'
        ORDER BY event_start DESC
        """
        alerts = analysis_engine.db.execute_query(query)
        
        return jsonify({
            'success': True,
            'data': alerts
        })
    except Exception as e:
        logger.error(f"Squeeze alerts retrieval failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# CLI Interface for testing
def main():
    """Main function for CLI testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crypto Analysis Engine')
    parser.add_argument('--symbol', required=True, help='Cryptocurrency symbol (e.g., BTC, ETH)')
    parser.add_argument('--images', nargs='+', help='Paths to screenshot images')
    parser.add_argument('--server', action='store_true', help='Run as web server')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    
    args = parser.parse_args()
    
    if args.server:
        # Run Flask server
        app.run(host='0.0.0.0', port=args.port, debug=True)
    else:
        # Run CLI analysis
        async def run_analysis():
            engine = CryptoAnalysisEngine()
            await engine.initialize()
            
            try:
                result = await engine.analyze_symbol(args.symbol, args.images or [])
                print(json.dumps(result, indent=2, default=str))
            finally:
                await engine.shutdown()
        
        asyncio.run(run_analysis())

if __name__ == '__main__':
    main()

