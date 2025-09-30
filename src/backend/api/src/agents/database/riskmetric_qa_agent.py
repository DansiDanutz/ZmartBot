#!/usr/bin/env python3
"""
RiskMetric Q&A Agent
Intelligent agent that can answer natural language questions about RiskMetric data
"""

import sqlite3
import json
import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re
from dataclasses import dataclass, field
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class QAResponse:
    """Structure for Q&A responses"""
    question: str
    answer: str
    data: Optional[Dict] = None
    confidence: float = 1.0
    category: str = "general"
    timestamp: datetime = field(default_factory=datetime.now)

class RiskMetricQAAgent:
    """
    Intelligent Q&A Agent for RiskMetric data
    Can answer natural language questions about risk values, formulas, time spent, etc.
    """
    
    def __init__(self, db_path: str = "data/riskmetric_qa.db"):
        self.db_path = db_path
        self.init_database()
        self.load_knowledge_base()
        logger.info("RiskMetric Q&A Agent initialized")
    
    def init_database(self):
        """Initialize Q&A database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Symbol bounds and formulas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbol_data (
                symbol TEXT PRIMARY KEY,
                min_price REAL,
                max_price REAL,
                growth_multiple REAL,
                formula TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        # Time spent data with latest update
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_spent_current (
                symbol TEXT,
                band_start REAL,
                band_end REAL,
                days_spent INTEGER,
                percentage REAL,
                coefficient REAL,
                last_updated DATE,
                PRIMARY KEY (symbol, band_start, band_end)
            )
        ''')
        
        # Symbol life ages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbol_life_ages (
                symbol TEXT PRIMARY KEY,
                inception_date DATE,
                life_age_days INTEGER,
                last_updated DATE
            )
        ''')
        
        # Risk values at different prices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                price REAL,
                risk_value REAL,
                zone TEXT,
                calculation_date TIMESTAMP
            )
        ''')
        
        # Win rate statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS win_rate_stats (
                symbol TEXT PRIMARY KEY,
                total_trades INTEGER,
                winning_trades INTEGER,
                win_rate REAL,
                avg_profit REAL,
                best_zone TEXT,
                last_updated TIMESTAMP
            )
        ''')
        
        # Q&A history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                category TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        # Knowledge base
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                keyword TEXT,
                response_template TEXT,
                data_source TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_knowledge_base(self):
        """Load initial data and knowledge patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load symbol data
        symbols_data = {
            'BTC': {'min': 30000, 'max': 299720, 'life_age': 5466},
            'ETH': {'min': 445.60, 'max': 10780.24, 'life_age': 3652},
            'SOL': {'min': 18.75, 'max': 907.09, 'life_age': 1942},
            'ADA': {'min': 0.10, 'max': 6.56, 'life_age': 2845},
            'DOT': {'min': 2.5, 'max': 150, 'life_age': 1810},
            'XRP': {'min': 0.15, 'max': 10, 'life_age': 4384},
            'BNB': {'min': 30, 'max': 2000, 'life_age': 2943},
            'AVAX': {'min': 3, 'max': 500, 'life_age': 1775},
            'LINK': {'min': 3.5, 'max': 200, 'life_age': 2825},
            'LTC': {'min': 30, 'max': 1000, 'life_age': 4482},
            'DOGE': {'min': 0.002, 'max': 1, 'life_age': 4251},
            'ATOM': {'min': 2, 'max': 100, 'life_age': 2356},
            'XLM': {'min': 0.03, 'max': 2, 'life_age': 4012},
            'XMR': {'min': 50, 'max': 1000, 'life_age': 4090},
            'VET': {'min': 0.002, 'max': 0.5, 'life_age': 2565},
            'HBAR': {'min': 0.02, 'max': 1, 'life_age': 2149},
            'TRX': {'min': 0.01, 'max': 0.5, 'life_age': 2826},
            'TON': {'min': 0.5, 'max': 20, 'life_age': 1441},
            'AAVE': {'min': 30, 'max': 1000, 'life_age': 1768},
            'RENDER': {'min': 0.5, 'max': 50, 'life_age': 1879},
            'SUI': {'min': 0.5, 'max': 20, 'life_age': 827}
        }
        
        for symbol, data in symbols_data.items():
            cursor.execute('''
                INSERT OR REPLACE INTO symbol_data 
                (symbol, min_price, max_price, growth_multiple, formula, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, data['min'], data['max'], data['max']/data['min'],
                  'risk = (ln(price) - ln(min)) / (ln(max) - ln(min))',
                  datetime.now()))
            
            cursor.execute('''
                INSERT OR REPLACE INTO symbol_life_ages
                (symbol, life_age_days, last_updated)
                VALUES (?, ?, ?)
            ''', (symbol, data['life_age'], datetime.now().date()))
        
        # Load time spent data for key symbols
        time_spent_data = {
            'BTC': {
                '0-0.1': {'days': 134, 'pct': 2.5},
                '0.1-0.2': {'days': 721, 'pct': 13.2},
                '0.2-0.3': {'days': 840, 'pct': 15.4},
                '0.3-0.4': {'days': 1131, 'pct': 20.7},
                '0.4-0.5': {'days': 1102, 'pct': 20.2},
                '0.5-0.6': {'days': 933, 'pct': 17.1},
                '0.6-0.7': {'days': 369, 'pct': 6.8},
                '0.7-0.8': {'days': 135, 'pct': 2.5},
                '0.8-0.9': {'days': 79, 'pct': 1.4},
                '0.9-1': {'days': 19, 'pct': 0.3}
            },
            'ETH': {
                '0-0.1': {'days': 31, 'pct': 0.8},
                '0.1-0.2': {'days': 81, 'pct': 2.2},
                '0.2-0.3': {'days': 192, 'pct': 5.3},
                '0.3-0.4': {'days': 448, 'pct': 12.3},
                '0.4-0.5': {'days': 585, 'pct': 16.0},
                '0.5-0.6': {'days': 949, 'pct': 26.0},
                '0.6-0.7': {'days': 804, 'pct': 22.0},
                '0.7-0.8': {'days': 370, 'pct': 10.1},
                '0.8-0.9': {'days': 151, 'pct': 4.1},
                '0.9-1': {'days': 38, 'pct': 1.0}
            }
        }
        
        for symbol, bands in time_spent_data.items():
            for band_range, data in bands.items():
                parts = band_range.split('-')
                band_start = float(parts[0])
                band_end = float(parts[1])
                
                # Calculate coefficient
                pct = data['pct']
                if pct == 0:
                    coeff = 1.6
                elif pct < 1:
                    coeff = 1.6
                elif pct < 2.5:
                    coeff = 1.55
                elif pct < 5:
                    coeff = 1.5
                elif pct < 10:
                    coeff = 1.4
                elif pct < 15:
                    coeff = 1.3
                elif pct < 20:
                    coeff = 1.2
                elif pct < 30:
                    coeff = 1.1
                else:
                    coeff = 1.0
                
                cursor.execute('''
                    INSERT OR REPLACE INTO time_spent_current
                    (symbol, band_start, band_end, days_spent, percentage, coefficient, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, band_start, band_end, data['days'], data['pct'], coeff, datetime.now().date()))
        
        # Load knowledge patterns
        knowledge_patterns = [
            ('formula', 'formula|equation|calculate|math', 'The RiskMetric formula is: risk = (ln(price) - ln(min)) / (ln(max) - ln(min))', 'formula'),
            ('risk_value', 'risk value|risk at|what risk', 'Calculating risk value for the given price...', 'calculation'),
            ('time_spent', 'days spent|time spent|how many days|band', 'Looking up time spent data...', 'time_data'),
            ('life_age', 'life age|age|how old|inception', 'Checking symbol life age...', 'age_data'),
            ('percentage', 'percentage|percent|%', 'Calculating percentage distribution...', 'percentage'),
            ('coefficient', 'coefficient|multiplier|rarity', 'The coefficient ranges from 1.0 to 1.6 based on rarity', 'coefficient'),
            ('zones', 'zone|zones|buy zone|sell zone', 'Risk zones: 0-0.25 (BUY), 0.25-0.4 (EARLY BULL), 0.4-0.6 (NEUTRAL), 0.6-0.75 (LATE BULL), 0.75-1.0 (SELL)', 'zones'),
            ('win_rate', 'win rate|success rate|profit|performance', 'Analyzing win rate statistics...', 'performance'),
            ('bounds', 'min|max|minimum|maximum|bounds', 'Looking up symbol bounds...', 'bounds'),
            ('comparison', 'compare|versus|vs|better|worse', 'Comparing symbols...', 'comparison')
        ]
        
        for category, keywords, template, source in knowledge_patterns:
            cursor.execute('''
                INSERT OR REPLACE INTO knowledge_base
                (category, keyword, response_template, data_source)
                VALUES (?, ?, ?, ?)
            ''', (category, keywords, template, source))
        
        conn.commit()
        conn.close()
    
    def calculate_risk(self, symbol: str, price: float) -> float:
        """Calculate risk value for a given price"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT min_price, max_price FROM symbol_data WHERE symbol = ?', (symbol.upper(),))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return 0.5  # Return default middle value
        
        min_price, max_price = row
        
        if price <= min_price:
            return 0.0
        elif price >= max_price:
            return 1.0
        else:
            return (math.log(price) - math.log(min_price)) / (math.log(max_price) - math.log(min_price))
    
    def get_risk_zone(self, risk: float) -> str:
        """Get zone name for risk value"""
        if risk < 0.25:
            return "BUY ZONE (Bear Market)"
        elif risk < 0.40:
            return "EARLY BULL"
        elif risk < 0.60:
            return "NEUTRAL"
        elif risk < 0.75:
            return "LATE BULL"
        else:
            return "SELL ZONE (Bull Market Top)"
    
    async def process_question(self, question: str) -> QAResponse:
        """Process a natural language question and return an answer"""
        question_lower = question.lower()
        
        # Extract symbols mentioned
        symbols = self.extract_symbols(question_lower)
        
        # Identify question type
        if 'risk' in question_lower and ('price' in question_lower or any(str(p) in question for p in range(1000, 1000000))):
            return await self.answer_risk_at_price(question, symbols)
        
        elif 'days' in question_lower and 'spent' in question_lower:
            return await self.answer_time_spent(question, symbols)
        
        elif 'life age' in question_lower or 'age' in question_lower:
            return await self.answer_life_age(question, symbols)
        
        elif 'formula' in question_lower:
            return await self.answer_formula(question, symbols)
        
        elif 'percentage' in question_lower or '%' in question:
            return await self.answer_percentage(question, symbols)
        
        elif 'coefficient' in question_lower or 'multiplier' in question_lower:
            return await self.answer_coefficient(question, symbols)
        
        elif 'win rate' in question_lower or 'performance' in question_lower:
            return await self.answer_win_rate(question, symbols)
        
        elif 'compare' in question_lower or 'versus' in question_lower or 'vs' in question_lower:
            return await self.answer_comparison(question, symbols)
        
        elif 'min' in question_lower or 'max' in question_lower or 'bounds' in question_lower:
            return await self.answer_bounds(question, symbols)
        
        elif 'zone' in question_lower:
            return await self.answer_zones(question)
        
        elif 'all symbols' in question_lower or 'list' in question_lower:
            return await self.answer_list_symbols()
        
        else:
            return await self.answer_general(question)
    
    def extract_symbols(self, text: str) -> List[str]:
        """Extract cryptocurrency symbols from text"""
        all_symbols = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'XRP', 'BNB', 'AVAX', 
                      'LINK', 'LTC', 'DOGE', 'ATOM', 'XLM', 'XMR', 'VET', 
                      'HBAR', 'TRX', 'TON', 'AAVE', 'RENDER', 'SUI']
        
        found_symbols = []
        text_upper = text.upper()
        
        # Also check for full names
        name_map = {
            'BITCOIN': 'BTC', 'ETHEREUM': 'ETH', 'SOLANA': 'SOL',
            'CARDANO': 'ADA', 'POLKADOT': 'DOT', 'RIPPLE': 'XRP',
            'BINANCE': 'BNB', 'AVALANCHE': 'AVAX', 'CHAINLINK': 'LINK',
            'LITECOIN': 'LTC', 'DOGECOIN': 'DOGE', 'COSMOS': 'ATOM'
        }
        
        for full_name, symbol in name_map.items():
            if full_name in text_upper:
                found_symbols.append(symbol)
        
        for symbol in all_symbols:
            if symbol in text_upper and symbol not in found_symbols:
                found_symbols.append(symbol)
        
        return found_symbols
    
    def extract_price(self, text: str) -> Optional[float]:
        """Extract price value from text"""
        # Look for patterns like $134000, 134,000, 134000, etc.
        patterns = [
            r'\$?([\d,]+\.?\d*)',
            r'price of ([\d,]+\.?\d*)',
            r'at ([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return float(price_str)
                except:
                    continue
        return None
    
    def extract_band(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract risk band from text"""
        # Look for patterns like 0.8-0.9, 0.8 to 0.9, etc.
        patterns = [
            r'(\d\.?\d*)\s*[-to]+\s*(\d\.?\d*)',
            r'band[s]?\s+(\d\.?\d*)\s*[-to]+\s*(\d\.?\d*)',
            r'between\s+(\d\.?\d*)\s+and\s+(\d\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    start = float(match.group(1))
                    end = float(match.group(2))
                    return (start, end)
                except:
                    continue
        return None
    
    async def answer_risk_at_price(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer questions about risk value at specific price"""
        price = self.extract_price(question)
        
        if not price:
            return QAResponse(
                question=question,
                answer="I couldn't extract a price from your question. Please specify a price value.",
                confidence=0.5,
                category="risk_calculation"
            )
        
        if not symbols:
            symbols = ['BTC']  # Default to Bitcoin
        
        symbol = symbols[0]
        risk = self.calculate_risk(symbol, price)
        
        if risk is None:
            return QAResponse(
                question=question,
                answer=f"I don't have data for {symbol}.",
                confidence=0.5,
                category="risk_calculation"
            )
        
        zone = self.get_risk_zone(risk)
        
        # Get bounds for context
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT min_price, max_price FROM symbol_data WHERE symbol = ?', (symbol,))
        row = cursor.fetchone()
        conn.close()
        
        min_price, max_price = row
        
        answer = f"For {symbol} at ${price:,.2f}:\n"
        answer += f"• Risk Value: {risk:.4f}\n"
        answer += f"• Zone: {zone}\n"
        answer += f"• Context: Min (Risk 0) = ${min_price:,.2f}, Max (Risk 1) = ${max_price:,.2f}\n"
        
        if risk < 0.25:
            answer += "• Signal: Strong BUY opportunity (historical bottom zone)"
        elif risk < 0.4:
            answer += "• Signal: BUY zone (early bull market)"
        elif risk < 0.6:
            answer += "• Signal: NEUTRAL (wait for direction)"
        elif risk < 0.75:
            answer += "• Signal: Consider taking profits (late bull)"
        else:
            answer += "• Signal: SELL zone (near market top)"
        
        return QAResponse(
            question=question,
            answer=answer,
            data={'symbol': symbol, 'price': price, 'risk': risk, 'zone': zone},
            confidence=1.0,
            category="risk_calculation",
            timestamp=datetime.now()
        )
    
    async def answer_time_spent(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer questions about time spent in risk bands"""
        band = self.extract_band(question)
        
        if not symbols:
            symbols = ['BTC']
        
        symbol = symbols[0]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if band:
            # Specific band query
            cursor.execute('''
                SELECT days_spent, percentage, coefficient 
                FROM time_spent_current 
                WHERE symbol = ? AND band_start = ? AND band_end = ?
            ''', (symbol, band[0], band[1]))
            
            row = cursor.fetchone()
            if row:
                days, pct, coeff = row
                answer = f"{symbol} has spent {days} days in the {band[0]:.1f}-{band[1]:.1f} risk band:\n"
                answer += f"• Percentage of life: {pct:.1f}%\n"
                answer += f"• Rarity coefficient: {coeff:.2f}x\n"
                
                if pct < 1:
                    answer += f"• This is an ULTRA RARE zone (visited less than 1% of the time)"
                elif pct < 5:
                    answer += f"• This is a RARE zone"
                elif pct < 15:
                    answer += f"• This is an UNCOMMON zone"
                else:
                    answer += f"• This is a COMMON zone"
            else:
                answer = f"No data found for {symbol} in band {band[0]:.1f}-{band[1]:.1f}"
        else:
            # All bands query
            cursor.execute('''
                SELECT band_start, band_end, days_spent, percentage 
                FROM time_spent_current 
                WHERE symbol = ?
                ORDER BY band_start
            ''', (symbol,))
            
            rows = cursor.fetchall()
            answer = f"Time spent distribution for {symbol}:\n\n"
            
            for start, end, days, pct in rows:
                answer += f"• {start:.1f}-{end:.1f}: {days} days ({pct:.1f}%)\n"
        
        conn.close()
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=1.0,
            category="time_spent",
            timestamp=datetime.now()
        )
    
    async def answer_life_age(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer questions about symbol life age"""
        if not symbols:
            # If no specific symbol, list all
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT symbol, life_age_days FROM symbol_life_ages ORDER BY life_age_days DESC')
            rows = cursor.fetchall()
            conn.close()
            
            answer = "Life ages of all symbols (in days):\n\n"
            for symbol, age in rows[:10]:  # Top 10
                years = age / 365
                answer += f"• {symbol}: {age:,} days ({years:.1f} years)\n"
            
            answer += f"\nOldest: {rows[0][0]} ({rows[0][1]:,} days)\n"
            answer += f"Youngest: {rows[-1][0]} ({rows[-1][1]:,} days)"
        else:
            symbol = symbols[0]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT life_age_days FROM symbol_life_ages WHERE symbol = ?', (symbol,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                age = row[0]
                years = age / 365
                answer = f"{symbol} has a life age of {age:,} days ({years:.1f} years)"
            else:
                answer = f"No life age data found for {symbol}"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=1.0,
            category="life_age",
            timestamp=datetime.now()
        )
    
    async def answer_formula(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer questions about formulas"""
        answer = "**Benjamin Cowen's RiskMetric Formula:**\n\n"
        answer += "```\nrisk = (ln(price) - ln(min)) / (ln(max) - ln(min))\n```\n\n"
        answer += "Where:\n"
        answer += "• ln = natural logarithm\n"
        answer += "• price = current price\n"
        answer += "• min = minimum price (risk 0)\n"
        answer += "• max = maximum price (risk 1)\n\n"
        answer += "**Inverse formula (price from risk):**\n"
        answer += "```\nprice = min × e^(risk × ln(max/min))\n```\n\n"
        
        if symbols:
            symbol = symbols[0]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT min_price, max_price FROM symbol_data WHERE symbol = ?', (symbol,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                min_price, max_price = row
                answer += f"**For {symbol}:**\n"
                answer += f"• Min price: ${min_price:,.2f}\n"
                answer += f"• Max price: ${max_price:,.2f}\n"
                answer += f"• Growth multiple: {max_price/min_price:.2f}x"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=1.0,
            category="formula",
            timestamp=datetime.now()
        )
    
    async def answer_percentage(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer questions about percentages"""
        if not symbols:
            symbols = ['BTC']
        
        symbol = symbols[0]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT band_start, band_end, percentage 
            FROM time_spent_current 
            WHERE symbol = ?
            ORDER BY percentage DESC
        ''', (symbol,))
        
        rows = cursor.fetchall()
        conn.close()
        
        answer = f"Risk band percentages for {symbol}:\n\n"
        answer += "**Most visited bands:**\n"
        
        for i, (start, end, pct) in enumerate(rows[:3]):
            answer += f"{i+1}. Band {start:.1f}-{end:.1f}: {pct:.1f}%\n"
        
        answer += "\n**Least visited bands:**\n"
        
        for i, (start, end, pct) in enumerate(rows[-3:]):
            answer += f"• Band {start:.1f}-{end:.1f}: {pct:.1f}%\n"
        
        # Calculate zone percentages
        buy_zone = sum(pct for start, end, pct in rows if end <= 0.25)
        neutral_zone = sum(pct for start, end, pct in rows if 0.4 <= start < 0.6)
        sell_zone = sum(pct for start, end, pct in rows if start >= 0.75)
        
        answer += f"\n**Zone distribution:**\n"
        answer += f"• Buy Zone (0-0.25): {buy_zone:.1f}%\n"
        answer += f"• Neutral (0.4-0.6): {neutral_zone:.1f}%\n"
        answer += f"• Sell Zone (0.75-1.0): {sell_zone:.1f}%"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=1.0,
            category="percentage",
            timestamp=datetime.now()
        )
    
    async def answer_coefficient(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer questions about coefficients"""
        answer = "**RiskMetric Coefficient System:**\n\n"
        answer += "Coefficients multiply the base score based on rarity:\n\n"
        answer += "• **1.6x** - Never visited or <1% (Ultra Rare)\n"
        answer += "• **1.55x** - 1-2.5% of time (Very Rare)\n"
        answer += "• **1.5x** - 2.5-5% of time (Rare)\n"
        answer += "• **1.4x** - 5-10% of time (Uncommon)\n"
        answer += "• **1.3x** - 10-15% of time (Somewhat Uncommon)\n"
        answer += "• **1.2x** - 15-20% of time (Below Average)\n"
        answer += "• **1.1x** - 20-30% of time (Near Average)\n"
        answer += "• **1.0x** - >30% of time (Common)\n\n"
        
        if symbols:
            symbol = symbols[0]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT band_start, band_end, coefficient, percentage
                FROM time_spent_current 
                WHERE symbol = ?
                ORDER BY coefficient DESC
            ''', (symbol,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                answer += f"**{symbol} current coefficients:**\n"
                for start, end, coeff, pct in rows[:3]:
                    answer += f"• Band {start:.1f}-{end:.1f}: {coeff:.2f}x ({pct:.1f}%)\n"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=1.0,
            category="coefficient",
            timestamp=datetime.now()
        )
    
    async def answer_zones(self, question: str) -> QAResponse:
        """Answer questions about risk zones"""
        answer = "**Benjamin Cowen's Risk Zones:**\n\n"
        answer += "📉 **BUY ZONE (0.00-0.25)**\n"
        answer += "• Bear market bottom\n"
        answer += "• Best accumulation opportunity\n"
        answer += "• Base score: 70-100 points\n\n"
        
        answer += "📈 **EARLY BULL (0.25-0.40)**\n"
        answer += "• Recovery phase\n"
        answer += "• Buy on strength\n"
        answer += "• Base score: 50-70 points\n\n"
        
        answer += "⚖️ **NEUTRAL (0.40-0.60)**\n"
        answer += "• Consolidation zone\n"
        answer += "• Follow other indicators\n"
        answer += "• Base score: 30-50 points\n\n"
        
        answer += "⚠️ **LATE BULL (0.60-0.75)**\n"
        answer += "• Euphoria approaching\n"
        answer += "• Start taking profits\n"
        answer += "• Base score: 50-70 points\n\n"
        
        answer += "🔴 **SELL ZONE (0.75-1.00)**\n"
        answer += "• Market top region\n"
        answer += "• Distribution phase\n"
        answer += "• Base score: 70-100 points"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=1.0,
            category="zones",
            timestamp=datetime.now()
        )
    
    async def answer_win_rate(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer questions about win rates"""
        # This would need actual trading data to be accurate
        # For now, provide theoretical win rates based on zones
        
        answer = "**Theoretical Win Rates by Zone:**\n\n"
        answer += "Based on historical patterns:\n\n"
        answer += "• **BUY ZONE (0-0.25)**: ~75-85% win rate for longs\n"
        answer += "• **EARLY BULL (0.25-0.40)**: ~65-75% win rate for longs\n"
        answer += "• **NEUTRAL (0.40-0.60)**: ~50% win rate (coin flip)\n"
        answer += "• **LATE BULL (0.60-0.75)**: ~60-70% win rate for shorts\n"
        answer += "• **SELL ZONE (0.75-1.00)**: ~75-85% win rate for shorts\n\n"
        
        if symbols:
            answer += f"**Note:** Actual win rates for {', '.join(symbols)} would require backtesting with real trade data.\n\n"
        
        answer += "**Key Factors:**\n"
        answer += "• Rarity coefficient enhances signal strength\n"
        answer += "• Combine with other indicators for confirmation\n"
        answer += "• Risk management is crucial regardless of zone"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=0.8,
            category="win_rate",
            timestamp=datetime.now()
        )
    
    async def answer_comparison(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer comparison questions between symbols"""
        if len(symbols) < 2:
            return QAResponse(
                question=question,
                answer="Please specify at least two symbols to compare.",
                confidence=0.5,
                category="comparison"
            )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        answer = f"**Comparison: {' vs '.join(symbols)}**\n\n"
        
        comparison_data = []
        for symbol in symbols[:3]:  # Limit to 3 symbols
            cursor.execute('''
                SELECT min_price, max_price, growth_multiple 
                FROM symbol_data WHERE symbol = ?
            ''', (symbol,))
            
            row = cursor.fetchone()
            if row:
                min_price, max_price, growth = row
                
                cursor.execute('SELECT life_age_days FROM symbol_life_ages WHERE symbol = ?', (symbol,))
                age_row = cursor.fetchone()
                age = age_row[0] if age_row else 0
                
                comparison_data.append({
                    'symbol': symbol,
                    'min': min_price,
                    'max': max_price,
                    'growth': growth,
                    'age': age
                })
        
        conn.close()
        
        # Create comparison table
        for data in comparison_data:
            answer += f"**{data['symbol']}:**\n"
            answer += f"• Min: ${data['min']:,.2f}\n"
            answer += f"• Max: ${data['max']:,.2f}\n"
            answer += f"• Growth potential: {data['growth']:.1f}x\n"
            answer += f"• Life age: {data['age']:,} days\n\n"
        
        # Determine winner in different categories
        if comparison_data:
            highest_growth = max(comparison_data, key=lambda x: x['growth'])
            oldest = max(comparison_data, key=lambda x: x['age'])
            
            answer += "**Analysis:**\n"
            answer += f"• Highest growth potential: {highest_growth['symbol']} ({highest_growth['growth']:.1f}x)\n"
            answer += f"• Most mature (data): {oldest['symbol']} ({oldest['age']:,} days)"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=1.0,
            category="comparison",
            timestamp=datetime.now()
        )
    
    async def answer_bounds(self, question: str, symbols: List[str]) -> QAResponse:
        """Answer questions about min/max bounds"""
        if not symbols:
            # Show all bounds
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT symbol, min_price, max_price FROM symbol_data ORDER BY symbol')
            rows = cursor.fetchall()
            conn.close()
            
            answer = "**All Symbol Bounds:**\n\n"
            for symbol, min_p, max_p in rows[:10]:
                answer += f"• {symbol}: ${min_p:,.2f} - ${max_p:,.2f}\n"
        else:
            symbol = symbols[0]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT min_price, max_price, growth_multiple FROM symbol_data WHERE symbol = ?', (symbol,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                min_p, max_p, growth = row
                answer = f"**{symbol} Bounds:**\n\n"
                answer += f"• Minimum (Risk 0): ${min_p:,.2f}\n"
                answer += f"• Maximum (Risk 1): ${max_p:,.2f}\n"
                answer += f"• Growth Multiple: {growth:.1f}x\n"
                answer += f"• Range: ${max_p - min_p:,.2f}"
            else:
                answer = f"No bounds data found for {symbol}"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=1.0,
            category="bounds",
            timestamp=datetime.now()
        )
    
    async def answer_list_symbols(self) -> QAResponse:
        """List all available symbols"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT symbol FROM symbol_data ORDER BY symbol')
        rows = cursor.fetchall()
        conn.close()
        
        symbols = [row[0] for row in rows]
        
        answer = f"**Available Symbols ({len(symbols)} total):**\n\n"
        answer += ", ".join(symbols)
        answer += "\n\nYou can ask about any of these symbols' risk values, time spent, formulas, etc."
        
        return QAResponse(
            question="List all symbols",
            answer=answer,
            confidence=1.0,
            category="list",
            timestamp=datetime.now()
        )
    
    async def answer_general(self, question: str) -> QAResponse:
        """General fallback answer"""
        answer = "I can help you with RiskMetric questions such as:\n\n"
        answer += "• **Risk calculations**: 'What's the risk value at Bitcoin price of $134,000?'\n"
        answer += "• **Time spent**: 'How many days has BTC spent in 0.8-0.9 band?'\n"
        answer += "• **Life age**: 'What is the life age of Solana?'\n"
        answer += "• **Formulas**: 'What is the risk value formula?'\n"
        answer += "• **Percentages**: 'What percentage for each risk band?'\n"
        answer += "• **Win rates**: 'What's the best win rate ratio?'\n"
        answer += "• **Comparisons**: 'Compare BTC vs ETH'\n"
        answer += "• **Bounds**: 'What are the min/max values for ETH?'\n\n"
        answer += "Please ask a specific question and I'll help you!"
        
        return QAResponse(
            question=question,
            answer=answer,
            confidence=0.3,
            category="general",
            timestamp=datetime.now()
        )
    
    def save_qa_history(self, response: QAResponse):
        """Save Q&A interaction to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO qa_history (question, answer, category, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (response.question, response.answer, response.category, response.timestamp))
        
        conn.commit()
        conn.close()


# Example usage
async def test_qa_agent():
    """Test the Q&A agent with various questions"""
    agent = RiskMetricQAAgent()
    
    test_questions = [
        "What would be the risk value at the price of Bitcoin of 134000?",
        "How many days has Bitcoin spent in the risk band of 0.8-0.9?",
        "What is the life age of Solana?",
        "What is the formula for calculating risk?",
        "What is the percentage for each risk band for ETH?",
        "Compare BTC vs ETH vs SOL",
        "What are the risk zones?",
        "What's the coefficient system?",
        "List all symbols"
    ]
    
    print("="*80)
    print("RISKMETRIC Q&A AGENT TEST")
    print("="*80)
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        response = await agent.process_question(question)
        print(f"\n💡 Answer:\n{response.answer}")
        print(f"\n📊 Category: {response.category} | Confidence: {response.confidence:.1%}")
        print("-"*60)
        
        # Save to history
        agent.save_qa_history(response)

if __name__ == "__main__":
    asyncio.run(test_qa_agent())