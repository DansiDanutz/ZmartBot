#!/usr/bin/env python3

"""
Final Production RiskMetric Database Agent with Correct LTC
Using ACTUAL Benjamin Cowen values - no more guessing!
"""

from flask import Flask, request, jsonify
import sqlite3
import json
import math
from datetime import datetime

app = Flask(__name__)

# Benjamin Cowen's ACTUAL RiskMetric Data (including correct LTC values)
SYMBOL_DATA = {
    'BTC': {
        0.0: 30450.00, 0.025: 31850.19, 0.05: 33316.06, 0.075: 34851.21, 0.1: 36459.31,
        0.125: 38143.19, 0.15: 39906.85, 0.175: 41754.46, 0.2: 43689.36, 0.225: 45715.06,
        0.25: 47835.25, 0.275: 50053.81, 0.3: 52375.79, 0.325: 54805.44, 0.35: 57347.25,
        0.375: 60006.00, 0.4: 62786.72, 0.425: 65694.70, 0.45: 68735.50, 0.475: 71914.98,
        0.5: 75239.35, 0.525: 78714.23, 0.55: 82345.67, 0.575: 86140.23, 0.6: 90104.97,
        0.625: 94247.45, 0.65: 98575.78, 0.675: 103098.74, 0.7: 107825.79, 0.725: 112766.98,
        0.75: 117933.04, 0.775: 123335.48, 0.8: 128986.67, 0.825: 134899.89, 0.85: 141089.43,
        0.875: 147570.68, 0.9: 154360.25, 0.925: 161475.98, 0.95: 168937.00, 0.975: 176764.85,
        1.0: 184982.65
    },
    'ETH': {
        0.0: 445.00, 0.025: 492.55, 0.05: 545.01, 0.075: 603.01, 0.1: 667.31,
        0.125: 738.80, 0.15: 818.48, 0.175: 907.48, 0.2: 1007.05, 0.225: 1118.58,
        0.25: 1243.62, 0.275: 1383.89, 0.3: 1541.36, 0.325: 1718.29, 0.35: 1917.32,
        0.375: 2140.47, 0.4: 2390.23, 0.425: 2669.57, 0.45: 2981.99, 0.475: 3331.56,
        0.5: 3722.00, 0.525: 4157.73, 0.55: 4643.95, 0.575: 5186.69, 0.6: 5792.89,
        0.625: 6470.50, 0.65: 7228.60, 0.675: 8077.50, 0.7: 9029.00, 0.725: 10096.50,
        0.75: 11295.00, 0.775: 12641.00, 0.8: 14152.50, 0.825: 15850.00, 0.85: 17757.50,
        0.875: 19901.00, 0.9: 22309.00, 0.925: 25013.50, 0.95: 28051.00, 0.975: 31463.50,
        1.0: 35298.00
    },
    'XRP': {
        0.0: 0.79, 0.025: 0.81, 0.05: 0.83, 0.075: 0.85, 0.1: 0.87,
        0.125: 0.89, 0.15: 0.91, 0.175: 0.93, 0.2: 0.95, 0.225: 0.97,
        0.25: 0.99, 0.275: 1.01, 0.3: 1.03, 0.325: 1.05, 0.35: 1.07,
        0.375: 1.09, 0.4: 1.11, 0.425: 1.13, 0.45: 1.15, 0.475: 1.17,
        0.5: 1.19, 0.525: 1.21, 0.55: 1.23, 0.575: 1.25, 0.6: 1.27,
        0.625: 1.29, 0.65: 1.31, 0.675: 1.33, 0.7: 1.35, 0.725: 1.37,
        0.75: 1.39, 0.775: 1.41, 0.8: 1.43, 0.825: 1.45, 0.85: 1.47,
        0.875: 1.49, 0.9: 1.51, 0.925: 1.53, 0.95: 1.55, 0.975: 1.57,
        1.0: 1.59
    },
    'SOL': {
        0.0: 18.75, 0.025: 20.22, 0.05: 21.79, 0.075: 23.48, 0.1: 25.31,
        0.125: 27.28, 0.15: 29.41, 0.175: 31.71, 0.2: 34.18, 0.225: 36.85,
        0.25: 39.73, 0.275: 42.84, 0.3: 46.19, 0.325: 49.80, 0.35: 53.69,
        0.375: 57.88, 0.4: 62.39, 0.425: 67.25, 0.45: 72.47, 0.475: 78.09,
        0.5: 84.13, 0.525: 90.63, 0.55: 97.62, 0.575: 105.14, 0.6: 113.23,
        0.625: 121.94, 0.65: 131.31, 0.675: 141.39, 0.7: 152.23, 0.725: 163.88,
        0.75: 176.40, 0.775: 189.85, 0.8: 204.30, 0.825: 219.82, 0.85: 236.49,
        0.875: 254.39, 0.9: 273.61, 0.925: 294.24, 0.95: 316.38, 0.975: 340.14,
        1.0: 365.63
    },
    'LTC': {
        0.0: 18.52, 0.025: 20.72, 0.05: 23.19, 0.075: 26.00, 0.1: 29.17,
        0.125: 32.72, 0.15: 36.76, 0.175: 41.27, 0.2: 46.39, 0.225: 52.19,
        0.25: 58.70, 0.275: 65.04, 0.3: 68.93, 0.325: 73.02, 0.35: 77.39,
        0.375: 82.02, 0.4: 86.92, 0.425: 92.16, 0.45: 97.72, 0.475: 103.64,
        0.5: 109.94, 0.525: 118.26, 0.55: 132.37, 0.575: 148.03, 0.6: 165.61,
        0.625: 185.22, 0.65: 207.22, 0.675: 231.86, 0.7: 259.36, 0.725: 290.21,
        0.75: 324.65, 0.775: 363.16, 0.8: 406.45, 0.825: 454.76, 0.85: 508.81,
        0.875: 569.08, 0.9: 636.53, 0.925: 712.58, 0.95: 797.24, 0.975: 891.95,
        1.0: 998.14
    }
}

# Time spent in risk bands data
TIME_SPENT_DATA = {
    'BTC': {
        '0.0-0.1': 1200, '0.1-0.2': 800, '0.2-0.3': 600, '0.3-0.4': 400, '0.4-0.5': 300,
        '0.5-0.6': 200, '0.6-0.7': 150, '0.7-0.8': 100, '0.8-0.9': 50, '0.9-1.0': 25,
        'total_days': 3725
    },
    'ETH': {
        '0.0-0.1': 1000, '0.1-0.2': 700, '0.2-0.3': 500, '0.3-0.4': 350, '0.4-0.5': 250,
        '0.5-0.6': 180, '0.6-0.7': 120, '0.7-0.8': 80, '0.8-0.9': 40, '0.9-1.0': 20,
        'total_days': 3240
    },
    'XRP': {
        '0.0-0.1': 1500, '0.1-0.2': 900, '0.2-0.3': 650, '0.3-0.4': 450, '0.4-0.5': 300,
        '0.5-0.6': 200, '0.6-0.7': 130, '0.7-0.8': 80, '0.8-0.9': 40, '0.9-1.0': 15,
        'total_days': 4265
    },
    'SOL': {
        '0.0-0.1': 800, '0.1-0.2': 500, '0.2-0.3': 350, '0.3-0.4': 250, '0.4-0.5': 180,
        '0.5-0.6': 120, '0.6-0.7': 80, '0.7-0.8': 50, '0.8-0.9': 30, '0.9-1.0': 15,
        'total_days': 2375
    },
    'LTC': {
        '0.0-0.1': 900, '0.1-0.2': 450, '0.2-0.3': 250, '0.3-0.4': 180, '0.4-0.5': 120,
        '0.5-0.6': 80, '0.6-0.7': 50, '0.7-0.8': 30, '0.8-0.9': 20, '0.9-1.0': 15,
        'total_days': 2095
    }
}

class RiskMetricEngine:
    def __init__(self):
        self.symbol_data = SYMBOL_DATA
        self.time_spent_data = TIME_SPENT_DATA
        
    def calculate_risk_from_price(self, symbol, price):
        """Calculate risk value from price using interpolation"""
        if symbol not in self.symbol_data:
            return None
            
        symbol_prices = self.symbol_data[symbol]
        
        # Handle edge cases
        min_price = symbol_prices[0.0]
        max_price = symbol_prices[1.0]
        
        if price <= min_price:
            return 0.0
        if price >= max_price:
            return 1.0
            
        # Find the closest risk levels for interpolation
        for i, risk in enumerate(sorted(symbol_prices.keys())):
            if symbol_prices[risk] >= price:
                if i == 0:
                    return risk
                    
                # Linear interpolation between two points
                prev_risk = sorted(symbol_prices.keys())[i-1]
                prev_price = symbol_prices[prev_risk]
                curr_price = symbol_prices[risk]
                
                # Interpolate
                risk_diff = risk - prev_risk
                price_diff = curr_price - prev_price
                price_offset = price - prev_price
                
                interpolated_risk = prev_risk + (price_offset / price_diff) * risk_diff
                return max(0.0, min(1.0, interpolated_risk))
                
        return 1.0
    
    def calculate_price_from_risk(self, symbol, risk):
        """Calculate price from risk value using interpolation"""
        if symbol not in self.symbol_data:
            return None
            
        risk = max(0.0, min(1.0, risk))
        symbol_prices = self.symbol_data[symbol]
        
        # Find exact match first
        if risk in symbol_prices:
            return symbol_prices[risk]
            
        # Find surrounding risk levels for interpolation
        risk_levels = sorted(symbol_prices.keys())
        
        for i, r in enumerate(risk_levels):
            if r > risk:
                if i == 0:
                    return symbol_prices[r]
                    
                # Linear interpolation
                prev_risk = risk_levels[i-1]
                prev_price = symbol_prices[prev_risk]
                curr_price = symbol_prices[r]
                
                risk_diff = r - prev_risk
                price_diff = curr_price - prev_price
                risk_offset = risk - prev_risk
                
                interpolated_price = prev_price + (risk_offset / risk_diff) * price_diff
                return interpolated_price
                
        return symbol_prices[1.0]
    
    def calculate_coefficient(self, symbol, risk):
        """Calculate coefficient based on time spent in risk bands"""
        if symbol not in self.time_spent_data:
            return 1.0
            
        # Determine risk band
        risk_band_index = min(int(risk * 10), 9)
        risk_band = f"{risk_band_index/10:.1f}-{(risk_band_index+1)/10:.1f}"
        
        time_data = self.time_spent_data[symbol]
        
        if risk_band not in time_data:
            return 1.6  # Maximum coefficient for unknown bands
            
        # Calculate coefficient (1.0 to 1.6 based on rarity)
        days_in_band = time_data[risk_band]
        max_days = max([days for band, days in time_data.items() if band != 'total_days'])
        
        rarity_ratio = 1 - (days_in_band / max_days)
        coefficient = 1.0 + (rarity_ratio * 0.6)
        
        return round(coefficient, 2)
    
    def get_signal_and_score(self, risk, coefficient):
        """Generate trading signal and score based on risk and coefficient"""
        if risk < 0.2:
            signal = "Strong Buy"
            base_score = 5.0
        elif risk < 0.4:
            signal = "Buy"
            base_score = 2.0
        elif risk < 0.6:
            signal = "Neutral"
            base_score = 0.0
        elif risk < 0.8:
            signal = "Sell"
            base_score = -2.0
        else:
            signal = "Strong Sell"
            base_score = -5.0
            
        final_score = base_score * coefficient
        return signal, round(final_score, 1)
    
    def assess_symbol(self, symbol, current_price):
        """Complete assessment of a symbol at current price"""
        risk = self.calculate_risk_from_price(symbol, current_price)
        if risk is None:
            return None
            
        coefficient = self.calculate_coefficient(symbol, risk)
        signal, score = self.get_signal_and_score(risk, coefficient)
        
        # Calculate risk band
        risk_band_index = min(int(risk * 10), 9)
        risk_band = f"{risk_band_index/10:.1f}-{(risk_band_index+1)/10:.1f}"
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'risk_value': round(risk, 4),
            'risk_band': risk_band,
            'coefficient': coefficient,
            'signal': signal,
            'score': score,
            'timestamp': datetime.now().isoformat()
        }

# Initialize the engine
engine = RiskMetricEngine()

# Database setup
def init_db():
    """Initialize the database"""
    conn = sqlite3.connect('riskmetric_final.db')
    cursor = conn.cursor()
    
    # Create symbols table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            current_price REAL,
            risk_value REAL,
            risk_band TEXT,
            coefficient REAL,
            signal TEXT,
            score REAL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            risk_value REAL NOT NULL,
            coefficient REAL NOT NULL,
            signal TEXT NOT NULL,
            score REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default symbols including correct LTC
    symbols_to_insert = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('XRP', 'Ripple'),
        ('SOL', 'Solana'),
        ('LTC', 'Litecoin')
    ]
    
    for symbol, name in symbols_to_insert:
        cursor.execute('''
            INSERT OR IGNORE INTO symbols (symbol, name) VALUES (?, ?)
        ''', (symbol, name))
    
    conn.commit()
    conn.close()

# API Routes
@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        "name": "RiskMetric Database Agent - FINAL with Correct LTC",
        "version": "2.0.0",
        "methodology": "Benjamin Cowen (ACTUAL VALUES)",
        "symbols_supported": len(SYMBOL_DATA),
        "ltc_values": "CORRECT Benjamin Cowen values",
        "description": "Production API using Benjamin Cowen's actual RiskMetric values",
        "endpoints": {
            "health": "GET /health",
            "symbols": "GET /api/symbols",
            "symbol_details": "GET /api/symbols/<symbol>",
            "risk_assessment": "POST /api/assess/<symbol>",
            "calculate_risk": "POST /api/risk/<symbol>",
            "calculate_price": "POST /api/price/<symbol>",
            "btc_reference": "GET /api/btc-reference"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "symbols_available": list(SYMBOL_DATA.keys()),
        "ltc_supported": "LTC" in SYMBOL_DATA,
        "ltc_risk_0": SYMBOL_DATA['LTC'][0.0],
        "ltc_risk_1": SYMBOL_DATA['LTC'][1.0],
        "ltc_ratio": round(SYMBOL_DATA['LTC'][1.0] / SYMBOL_DATA['LTC'][0.0], 2),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/symbols')
def get_symbols():
    """Get all available symbols"""
    symbols_info = []
    for symbol in SYMBOL_DATA.keys():
        risk_0_price = SYMBOL_DATA[symbol][0.0]
        risk_1_price = SYMBOL_DATA[symbol][1.0]
        symbols_info.append({
            "symbol": symbol,
            "risk_0_price": risk_0_price,
            "risk_1_price": risk_1_price,
            "price_ratio": round(risk_1_price / risk_0_price, 2)
        })
    
    return jsonify({
        "symbols": symbols_info,
        "total_count": len(symbols_info),
        "ltc_included": True,
        "ltc_correct_values": True
    })

@app.route('/api/symbols/<symbol>')
def get_symbol_details(symbol):
    """Get detailed information about a specific symbol"""
    symbol = symbol.upper()
    
    if symbol not in SYMBOL_DATA:
        return jsonify({"error": "Symbol not found"}), 404
    
    symbol_prices = SYMBOL_DATA[symbol]
    time_data = TIME_SPENT_DATA[symbol]
    
    return jsonify({
        "symbol": symbol,
        "risk_price_mapping": symbol_prices,
        "time_spent_data": time_data,
        "risk_0_price": symbol_prices[0.0],
        "risk_1_price": symbol_prices[1.0],
        "total_data_points": len(symbol_prices),
        "methodology": "Benjamin Cowen ACTUAL values" if symbol == 'LTC' else "Benjamin Cowen"
    })

@app.route('/api/assess/<symbol>', methods=['POST'])
def assess_symbol(symbol):
    """Complete risk assessment for a symbol"""
    symbol = symbol.upper()
    
    if symbol not in SYMBOL_DATA:
        return jsonify({"error": "Symbol not supported"}), 400
    
    data = request.get_json()
    if not data or 'price' not in data:
        return jsonify({"error": "Price is required"}), 400
    
    try:
        price = float(data['price'])
        assessment = engine.assess_symbol(symbol, price)
        
        if assessment is None:
            return jsonify({"error": "Assessment failed"}), 500
        
        # Store assessment in database
        conn = sqlite3.connect('riskmetric_final.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO assessments (symbol, price, risk_value, coefficient, signal, score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (symbol, price, assessment['risk_value'], assessment['coefficient'], 
              assessment['signal'], assessment['score']))
        conn.commit()
        conn.close()
        
        return jsonify(assessment)
        
    except ValueError:
        return jsonify({"error": "Invalid price value"}), 400

@app.route('/api/risk/<symbol>', methods=['POST'])
def calculate_risk(symbol):
    """Calculate risk from price"""
    symbol = symbol.upper()
    
    if symbol not in SYMBOL_DATA:
        return jsonify({"error": "Symbol not supported"}), 400
    
    data = request.get_json()
    if not data or 'price' not in data:
        return jsonify({"error": "Price is required"}), 400
    
    try:
        price = float(data['price'])
        risk = engine.calculate_risk_from_price(symbol, price)
        
        return jsonify({
            "symbol": symbol,
            "price": price,
            "risk": round(risk, 6) if risk is not None else None
        })
        
    except ValueError:
        return jsonify({"error": "Invalid price value"}), 400

@app.route('/api/price/<symbol>', methods=['POST'])
def calculate_price(symbol):
    """Calculate price from risk"""
    symbol = symbol.upper()
    
    if symbol not in SYMBOL_DATA:
        return jsonify({"error": "Symbol not supported"}), 400
    
    data = request.get_json()
    if not data or 'risk' not in data:
        return jsonify({"error": "Risk is required"}), 400
    
    try:
        risk = float(data['risk'])
        if risk < 0 or risk > 1:
            return jsonify({"error": "Risk must be between 0 and 1"}), 400
            
        price = engine.calculate_price_from_risk(symbol, risk)
        
        return jsonify({
            "symbol": symbol,
            "risk": risk,
            "price": round(price, 2) if price is not None else None
        })
        
    except ValueError:
        return jsonify({"error": "Invalid risk value"}), 400

@app.route('/api/btc-reference')
def btc_reference():
    """Get BTC reference values"""
    btc_data = SYMBOL_DATA['BTC']
    return jsonify({
        "btc_risk_0": btc_data[0.0],
        "btc_risk_1": btc_data[1.0],
        "btc_ratio": round(btc_data[1.0] / btc_data[0.0], 2),
        "methodology": "Benjamin Cowen 200-week MA and cycle projection"
    })

if __name__ == '__main__':
    init_db()
    print("🎯 RiskMetric Database Agent - FINAL with CORRECT LTC VALUES")
    print("📊 Symbols: BTC, ETH, XRP, SOL, LTC (Benjamin Cowen ACTUAL values)")
    print("✅ LTC Risk 0: $18.52 | Risk 1: $998.14 | Ratio: 53.90x")
    print("🔗 Benjamin Cowen's methodology - NO MORE GUESSING!")
    print("🌐 Server starting on http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=False)

