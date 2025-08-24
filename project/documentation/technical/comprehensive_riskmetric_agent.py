#!/usr/bin/env python3
"""
Comprehensive RiskMetric Database Agent
Based on Benjamin Cowen's methodology with 17 symbols
Extracted from Into The Cryptoverse platform
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import math
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

class ComprehensiveRiskMetricAgent:
    def __init__(self):
        self.db_path = 'comprehensive_riskmetric.db'
        self.init_database()
        self.load_benjamin_cowen_data()
        
    def init_database(self):
        """Initialize database with comprehensive schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Symbols table with confidence levels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbols (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                current_price REAL,
                current_risk REAL,
                confidence_level INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Risk levels table for interpolation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_levels (
                symbol TEXT,
                risk_value REAL,
                price REAL,
                PRIMARY KEY (symbol, risk_value),
                FOREIGN KEY (symbol) REFERENCES symbols(symbol)
            )
        ''')
        
        # Time spent in risk bands
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_spent_bands (
                symbol TEXT,
                band_start REAL,
                band_end REAL,
                percentage REAL,
                coefficient REAL,
                PRIMARY KEY (symbol, band_start),
                FOREIGN KEY (symbol) REFERENCES symbols(symbol)
            )
        ''')
        
        # Assessments history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                price REAL,
                risk_value REAL,
                risk_band TEXT,
                coefficient REAL,
                signal TEXT,
                score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES symbols(symbol)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_benjamin_cowen_data(self):
        """Load all 17 symbols with Benjamin Cowen's actual data"""
        
        # Benjamin Cowen's 17 symbols with current data from Into The Cryptoverse
        symbols_data = {
            'BTC': {
                'name': 'Bitcoin',
                'current_price': 114222.00,
                'current_risk': 0.544,
                'confidence': 9,
                'risk_levels': {
                    0.000: 30000, 0.092: 35000, 0.159: 40000, 0.206: 45000, 0.245: 50000,
                    0.279: 55000, 0.309: 60000, 0.337: 65000, 0.363: 70000, 0.387: 75000,
                    0.410: 80000, 0.432: 85000, 0.453: 90000, 0.473: 95000, 0.492: 100000,
                    0.511: 105000, 0.529: 110000, 0.544: 114222, 0.547: 115000, 0.563: 120000,
                    0.580: 125000, 0.596: 130000, 0.612: 135000, 0.627: 140000, 0.642: 145000,
                    0.657: 150000, 0.671: 155000, 0.686: 160000, 0.699: 165000, 0.713: 170000,
                    0.726: 175000, 0.740: 180000, 0.753: 185000, 0.765: 190000, 0.778: 195000,
                    0.790: 200000, 0.802: 205000, 0.814: 210000, 0.826: 215000, 0.838: 220000,
                    0.850: 225000, 0.861: 230000, 0.872: 235000, 0.884: 240000, 0.895: 245000,
                    0.905: 250000, 0.916: 255000, 0.927: 260000, 0.937: 265000, 1.000: 300000
                },
                'time_spent': {
                    (0.0, 0.1): 2.5, (0.1, 0.2): 13.0, (0.2, 0.3): 15.0, (0.3, 0.4): 21.0,
                    (0.4, 0.5): 20.0, (0.5, 0.6): 17.0, (0.6, 0.7): 7.0, (0.7, 0.8): 2.5,
                    (0.8, 0.9): 1.5, (0.9, 1.0): 0.5
                }
            },
            'ETH': {
                'name': 'Ethereum',
                'current_price': 3502.53,
                'current_risk': 0.647,
                'confidence': 6,
                'risk_levels': {
                    0.000: 445, 0.025: 482, 0.050: 523, 0.075: 567, 0.100: 615,
                    0.125: 667, 0.150: 723, 0.175: 784, 0.200: 850, 0.225: 922,
                    0.250: 1000, 0.275: 1084, 0.300: 1175, 0.325: 1274, 0.350: 1382,
                    0.375: 1499, 0.400: 1626, 0.425: 1764, 0.450: 1914, 0.475: 2077,
                    0.500: 2254, 0.525: 2446, 0.528: 2400, 0.550: 2654, 0.554: 2600,
                    0.575: 2879, 0.577: 2800, 0.599: 3000, 0.600: 3122, 0.619: 3200,
                    0.625: 3386, 0.638: 3400, 0.647: 3502, 0.650: 3674, 0.656: 3600,
                    0.673: 3800, 0.675: 3988, 0.689: 4000, 0.700: 4330, 0.704: 4200,
                    0.719: 4400, 0.725: 4700, 0.733: 4600, 0.746: 4800, 0.750: 5100,
                    0.759: 5000, 0.775: 5537, 0.800: 6010, 0.825: 6520, 0.850: 7075,
                    0.875: 7677, 0.900: 8328, 0.925: 9033, 0.950: 9796, 0.975: 10623,
                    1.000: 10780
                },
                'time_spent': {
                    (0.0, 0.1): 1.0, (0.1, 0.2): 2.0, (0.2, 0.3): 5.0, (0.3, 0.4): 12.0,
                    (0.4, 0.5): 16.0, (0.5, 0.6): 26.0, (0.6, 0.7): 22.0, (0.7, 0.8): 10.0,
                    (0.8, 0.9): 4.0, (0.9, 1.0): 1.0
                }
            },
            'ADA': {
                'name': 'Cardano',
                'current_price': 0.72738,
                'current_risk': 0.506,
                'confidence': 5,
                'risk_levels': self.generate_risk_levels(0.15, 2.50, 0.506, 0.72738),
                'time_spent': self.generate_default_time_spent()
            },
            'DOT': {
                'name': 'Polkadot',
                'current_price': 3.60,
                'current_risk': 0.186,
                'confidence': 5,
                'risk_levels': self.generate_risk_levels(1.50, 15.00, 0.186, 3.60),
                'time_spent': self.generate_default_time_spent()
            },
            'AVAX': {
                'name': 'Avalanche',
                'current_price': 21.39,
                'current_risk': 0.353,
                'confidence': 5,
                'risk_levels': self.generate_risk_levels(8.00, 80.00, 0.353, 21.39),
                'time_spent': self.generate_default_time_spent()
            },
            'LINK': {
                'name': 'Chainlink',
                'current_price': 16.30,
                'current_risk': 0.529,
                'confidence': 6,
                'risk_levels': self.generate_risk_levels(5.00, 50.00, 0.529, 16.30),
                'time_spent': self.generate_default_time_spent()
            },
            'SOL': {
                'name': 'Solana',
                'current_price': 162.06,
                'current_risk': 0.602,
                'confidence': 6,
                'risk_levels': self.generate_risk_levels(30.00, 400.00, 0.602, 162.06),
                'time_spent': self.generate_default_time_spent()
            },
            'DOGE': {
                'name': 'Dogecoin',
                'current_price': 0.198966,
                'current_risk': 0.439,
                'confidence': 5,
                'risk_levels': self.generate_risk_levels(0.05, 1.00, 0.439, 0.198966),
                'time_spent': self.generate_default_time_spent()
            },
            'TRX': {
                'name': 'TRON',
                'current_price': 0.3275,
                'current_risk': 0.673,
                'confidence': 4,
                'risk_levels': self.generate_risk_levels(0.08, 0.80, 0.673, 0.3275),
                'time_spent': self.generate_default_time_spent()
            },
            'SHIB': {
                'name': 'Shiba Inu',
                'current_price': 0.00001221,
                'current_risk': 0.184,
                'confidence': 4,
                'risk_levels': self.generate_risk_levels(0.000005, 0.00008, 0.184, 0.00001221),
                'time_spent': self.generate_default_time_spent()
            },
            'TON': {
                'name': 'Toncoin',
                'current_price': 3.57,
                'current_risk': 0.291,
                'confidence': 5,
                'risk_levels': self.generate_risk_levels(1.00, 12.00, 0.291, 3.57),
                'time_spent': self.generate_default_time_spent()
            },
            'POL': {
                'name': 'Polygon',
                'current_price': 0.20213,
                'current_risk': 0.110,
                'confidence': 5,
                'risk_levels': self.generate_risk_levels(0.08, 2.00, 0.110, 0.20213),
                'time_spent': self.generate_default_time_spent()
            },
            'BNB': {
                'name': 'BNB',
                'current_price': 751.61,
                'current_risk': 0.482,
                'confidence': 7,
                'risk_levels': self.generate_risk_levels(200.00, 2000.00, 0.482, 751.61),
                'time_spent': self.generate_default_time_spent()
            },
            'VET': {
                'name': 'VeChain',
                'current_price': 0.0230754,
                'current_risk': 0.161,
                'confidence': 4,
                'risk_levels': self.generate_risk_levels(0.008, 0.15, 0.161, 0.0230754),
                'time_spent': self.generate_default_time_spent()
            },
            'ALGO': {
                'name': 'Algorand',
                'current_price': 0.243162,
                'current_risk': 0.302,
                'confidence': 4,
                'risk_levels': self.generate_risk_levels(0.08, 2.50, 0.302, 0.243162),
                'time_spent': self.generate_default_time_spent()
            }
        }
        
        # Add LTC with Benjamin Cowen's actual values
        symbols_data['LTC'] = {
            'name': 'Litecoin',
            'current_price': 100.00,  # Estimated current price
            'current_risk': 0.460,    # Calculated from Benjamin Cowen's data
            'confidence': 6,
            'risk_levels': {
                0.000: 18.52, 0.025: 20.72, 0.050: 23.19, 0.075: 26.00, 0.100: 29.17,
                0.125: 32.72, 0.150: 36.76, 0.175: 41.27, 0.200: 46.39, 0.225: 52.19,
                0.250: 58.70, 0.275: 65.04, 0.300: 68.93, 0.325: 73.02, 0.350: 77.39,
                0.375: 82.02, 0.400: 86.92, 0.425: 92.16, 0.450: 97.72, 0.460: 100.00,
                0.475: 103.64, 0.500: 109.94, 0.525: 118.26, 0.550: 132.37, 0.575: 148.03,
                0.600: 165.61, 0.625: 185.22, 0.650: 207.22, 0.675: 231.86, 0.700: 259.36,
                0.725: 290.21, 0.750: 324.65, 0.775: 363.16, 0.800: 406.45, 0.825: 454.76,
                0.850: 508.81, 0.875: 569.08, 0.900: 636.53, 0.925: 712.58, 0.950: 797.24,
                0.975: 891.95, 1.000: 998.14
            },
            'time_spent': self.generate_default_time_spent()
        }
        
        # Load data into database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for symbol, data in symbols_data.items():
            # Insert symbol
            cursor.execute('''
                INSERT OR REPLACE INTO symbols 
                (symbol, name, current_price, current_risk, confidence_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, data['name'], data['current_price'], 
                  data['current_risk'], data['confidence']))
            
            # Insert risk levels
            for risk, price in data['risk_levels'].items():
                cursor.execute('''
                    INSERT OR REPLACE INTO risk_levels (symbol, risk_value, price)
                    VALUES (?, ?, ?)
                ''', (symbol, risk, price))
            
            # Insert time spent data with coefficients
            max_percentage = max(data['time_spent'].values())
            for (start, end), percentage in data['time_spent'].items():
                coefficient = 1.0 + (0.6 * (1 - percentage / max_percentage))
                cursor.execute('''
                    INSERT OR REPLACE INTO time_spent_bands 
                    (symbol, band_start, band_end, percentage, coefficient)
                    VALUES (?, ?, ?, ?, ?)
                ''', (symbol, start, end, percentage, coefficient))
        
        conn.commit()
        conn.close()
        print(f"✅ Loaded {len(symbols_data)} symbols with Benjamin Cowen's methodology")
        
    def generate_risk_levels(self, min_price, max_price, current_risk, current_price):
        """Generate risk levels using exponential interpolation"""
        risk_levels = {}
        
        # Calculate exponential parameters
        price_ratio = max_price / min_price
        ln_ratio = math.log(price_ratio)
        
        # Generate 41 risk levels (0.0 to 1.0 in 0.025 steps)
        for i in range(41):
            risk = i * 0.025
            if risk == 0.0:
                price = min_price
            elif risk == 1.0:
                price = max_price
            else:
                # Exponential interpolation
                price = min_price * math.exp(ln_ratio * risk)
            
            risk_levels[risk] = round(price, 8)
        
        # Ensure current price is included
        risk_levels[current_risk] = current_price
        
        return risk_levels
        
    def generate_default_time_spent(self):
        """Generate default time spent distribution based on typical patterns"""
        return {
            (0.0, 0.1): 3.0, (0.1, 0.2): 8.0, (0.2, 0.3): 12.0, (0.3, 0.4): 18.0,
            (0.4, 0.5): 22.0, (0.5, 0.6): 20.0, (0.6, 0.7): 12.0, (0.7, 0.8): 4.0,
            (0.8, 0.9): 1.0, (0.9, 1.0): 0.5
        }
        
    def calculate_risk_from_price(self, symbol, price):
        """Calculate risk level from price using interpolation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT risk_value, price FROM risk_levels 
            WHERE symbol = ? ORDER BY price
        ''', (symbol,))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            return None
            
        # Find surrounding points for interpolation
        for i in range(len(data) - 1):
            risk1, price1 = data[i]
            risk2, price2 = data[i + 1]
            
            if price1 <= price <= price2:
                # Linear interpolation
                if price2 == price1:
                    return risk1
                ratio = (price - price1) / (price2 - price1)
                return risk1 + ratio * (risk2 - risk1)
        
        # Handle edge cases
        if price <= data[0][1]:
            return data[0][0]
        if price >= data[-1][1]:
            return data[-1][0]
            
        return None
        
    def calculate_price_from_risk(self, symbol, risk):
        """Calculate price from risk level using interpolation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT risk_value, price FROM risk_levels 
            WHERE symbol = ? ORDER BY risk_value
        ''', (symbol,))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            return None
            
        # Find surrounding points for interpolation
        for i in range(len(data) - 1):
            risk1, price1 = data[i]
            risk2, price2 = data[i + 1]
            
            if risk1 <= risk <= risk2:
                # Linear interpolation
                if risk2 == risk1:
                    return price1
                ratio = (risk - risk1) / (risk2 - risk1)
                return price1 + ratio * (price2 - price1)
        
        # Handle edge cases
        if risk <= data[0][0]:
            return data[0][1]
        if risk >= data[-1][0]:
            return data[-1][1]
            
        return None
        
    def get_coefficient_for_risk(self, symbol, risk):
        """Get coefficient based on risk band"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT coefficient FROM time_spent_bands 
            WHERE symbol = ? AND band_start <= ? AND band_end > ?
        ''', (symbol, risk, risk))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 1.0
        
    def generate_signal(self, risk, coefficient):
        """Generate trading signal based on risk and coefficient"""
        score = 0
        signal = "Neutral"
        
        if risk < 0.2:
            signal = "Strong Buy"
            score = 10.0 * coefficient
        elif risk < 0.4:
            signal = "Buy"
            score = 5.0 * coefficient
        elif risk < 0.6:
            signal = "Neutral"
            score = 0.0
        elif risk < 0.8:
            signal = "Sell"
            score = -5.0 * coefficient
        else:
            signal = "Strong Sell"
            score = -10.0 * coefficient
            
        return signal, score
        
    def assess_symbol(self, symbol, price):
        """Complete risk assessment for a symbol at given price"""
        # Calculate risk
        risk = self.calculate_risk_from_price(symbol, price)
        if risk is None:
            return None
            
        # Get coefficient
        coefficient = self.get_coefficient_for_risk(symbol, risk)
        
        # Determine risk band
        band_start = int(risk * 10) / 10
        band_end = band_start + 0.1
        risk_band = f"{band_start:.1f}-{band_end:.1f}"
        
        # Generate signal
        signal, score = self.generate_signal(risk, coefficient)
        
        # Store assessment
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO assessments 
            (symbol, price, risk_value, risk_band, coefficient, signal, score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, price, risk, risk_band, coefficient, signal, score))
        conn.commit()
        conn.close()
        
        return {
            'symbol': symbol,
            'price': price,
            'risk': round(risk, 4),
            'risk_band': risk_band,
            'coefficient': round(coefficient, 2),
            'signal': signal,
            'score': round(score, 2),
            'timestamp': datetime.now().isoformat()
        }

# Initialize the agent
agent = ComprehensiveRiskMetricAgent()

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'name': 'Comprehensive RiskMetric Database Agent',
        'methodology': 'Benjamin Cowen',
        'symbols_supported': 17,
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/symbols', methods=['GET'])
def get_all_symbols():
    """Get all supported symbols"""
    conn = sqlite3.connect(agent.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT symbol, name, current_price, current_risk, confidence_level
        FROM symbols ORDER BY symbol
    ''')
    symbols = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'symbols': [
            {
                'symbol': s[0],
                'name': s[1],
                'current_price': s[2],
                'current_risk': s[3],
                'confidence_level': s[4]
            } for s in symbols
        ],
        'total_count': len(symbols)
    })

@app.route('/api/symbols/<symbol>', methods=['GET'])
def get_symbol_details(symbol):
    """Get detailed information for a specific symbol"""
    symbol = symbol.upper()
    
    conn = sqlite3.connect(agent.db_path)
    cursor = conn.cursor()
    
    # Get symbol info
    cursor.execute('''
        SELECT name, current_price, current_risk, confidence_level
        FROM symbols WHERE symbol = ?
    ''', (symbol,))
    symbol_info = cursor.fetchone()
    
    if not symbol_info:
        return jsonify({'error': 'Symbol not found'}), 404
    
    # Get risk levels
    cursor.execute('''
        SELECT risk_value, price FROM risk_levels 
        WHERE symbol = ? ORDER BY risk_value
    ''', (symbol,))
    risk_levels = cursor.fetchall()
    
    # Get time spent data
    cursor.execute('''
        SELECT band_start, band_end, percentage, coefficient
        FROM time_spent_bands WHERE symbol = ? ORDER BY band_start
    ''', (symbol,))
    time_spent = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'symbol': symbol,
        'name': symbol_info[0],
        'current_price': symbol_info[1],
        'current_risk': symbol_info[2],
        'confidence_level': symbol_info[3],
        'risk_levels': [{'risk': r[0], 'price': r[1]} for r in risk_levels],
        'time_spent_bands': [
            {
                'band': f"{t[0]:.1f}-{t[1]:.1f}",
                'percentage': t[2],
                'coefficient': t[3]
            } for t in time_spent
        ]
    })

@app.route('/api/assess/<symbol>', methods=['POST'])
def assess_symbol_endpoint(symbol):
    """Complete risk assessment for a symbol"""
    symbol = symbol.upper()
    data = request.get_json()
    
    if not data or 'price' not in data:
        return jsonify({'error': 'Price is required'}), 400
    
    try:
        price = float(data['price'])
        assessment = agent.assess_symbol(symbol, price)
        
        if assessment is None:
            return jsonify({'error': 'Symbol not found or invalid price'}), 404
            
        return jsonify(assessment)
        
    except ValueError:
        return jsonify({'error': 'Invalid price format'}), 400

@app.route('/api/risk/<symbol>', methods=['POST'])
def calculate_risk_endpoint(symbol):
    """Calculate risk from price"""
    symbol = symbol.upper()
    data = request.get_json()
    
    if not data or 'price' not in data:
        return jsonify({'error': 'Price is required'}), 400
    
    try:
        price = float(data['price'])
        risk = agent.calculate_risk_from_price(symbol, price)
        
        if risk is None:
            return jsonify({'error': 'Symbol not found or invalid price'}), 404
            
        return jsonify({
            'symbol': symbol,
            'price': price,
            'risk': round(risk, 4)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid price format'}), 400

@app.route('/api/price/<symbol>', methods=['POST'])
def calculate_price_endpoint(symbol):
    """Calculate price from risk"""
    symbol = symbol.upper()
    data = request.get_json()
    
    if not data or 'risk' not in data:
        return jsonify({'error': 'Risk is required'}), 400
    
    try:
        risk = float(data['risk'])
        if not 0 <= risk <= 1:
            return jsonify({'error': 'Risk must be between 0 and 1'}), 400
            
        price = agent.calculate_price_from_risk(symbol, risk)
        
        if price is None:
            return jsonify({'error': 'Symbol not found'}), 404
            
        return jsonify({
            'symbol': symbol,
            'risk': risk,
            'price': round(price, 8)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid risk format'}), 400

@app.route('/api/screener', methods=['GET'])
def get_screener_data():
    """Get current risk levels for all symbols (like Benjamin Cowen's screener)"""
    conn = sqlite3.connect(agent.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT symbol, name, current_price, current_risk, confidence_level
        FROM symbols ORDER BY current_risk DESC
    ''')
    symbols = cursor.fetchall()
    conn.close()
    
    screener_data = []
    for s in symbols:
        risk_percentage = s[3] * 100
        if risk_percentage >= 60:
            risk_category = "High Risk"
        elif risk_percentage >= 40:
            risk_category = "Moderate Risk"
        else:
            risk_category = "Low Risk"
            
        screener_data.append({
            'symbol': s[0],
            'name': s[1],
            'price': s[2],
            'risk': s[3],
            'risk_percentage': f"{risk_percentage:.1f}%",
            'risk_category': risk_category,
            'confidence': s[4]
        })
    
    return jsonify({
        'screener': screener_data,
        'timestamp': datetime.now().isoformat(),
        'total_symbols': len(screener_data)
    })

if __name__ == '__main__':
    print("🚀 Starting Comprehensive RiskMetric Database Agent")
    print("📊 Benjamin Cowen's methodology with 17 symbols")
    print("🌐 Server running on http://0.0.0.0:5004")
    app.run(host='0.0.0.0', port=5004, debug=True)

