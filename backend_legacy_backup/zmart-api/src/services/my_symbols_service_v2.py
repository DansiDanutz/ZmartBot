#!/usr/bin/env python3
"""
My Symbols Service V2 - FIXED VERSION
Manages a portfolio of up to 10 KuCoin futures symbols with REAL data and validation
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid
import json
import sqlite3
from decimal import Decimal
import numpy as np
import pandas as pd
from src.utils.symbol_converter import to_kucoin, to_standard, to_binance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SymbolData:
    """Symbol data structure for My Symbols management"""
    symbol: str
    root_symbol: str
    base_currency: str
    quote_currency: str
    settle_currency: str
    contract_type: str
    lot_size: float
    tick_size: float
    max_order_qty: int
    max_price: float
    multiplier: float
    initial_margin: float
    maintain_margin: float
    max_leverage: int
    status: str
    is_eligible_for_management: bool = True
    is_kucoin_tradeable: bool = False  # NEW: Track KuCoin availability
    is_binance_available: bool = False  # NEW: Track Binance availability
    sector_category: Optional[str] = None
    market_cap_category: Optional[str] = None
    volatility_classification: Optional[str] = None
    liquidity_tier: Optional[str] = None

@dataclass
class SymbolScore:
    """Symbol scoring data"""
    symbol: str
    technical_score: float
    fundamental_score: float
    market_structure_score: float
    risk_score: float
    composite_score: float
    confidence_level: float
    rank: int
    calculation_timestamp: datetime
    supporting_data: Dict[str, Any]
    data_source: str = "real"  # NEW: Track if using real or mock data

@dataclass
class PortfolioEntry:
    """Portfolio composition entry"""
    symbol: str
    position_rank: int
    inclusion_date: datetime
    current_score: float
    weight_percentage: float
    status: str
    is_replacement_candidate: bool
    replacement_priority: Optional[int]
    performance_since_inclusion: Optional[float]
    max_drawdown_since_inclusion: Optional[float]
    volatility_since_inclusion: Optional[float]
    is_tradeable: bool = True  # NEW: Can we trade this right now

class MySymbolsServiceV2:
    """My Symbols management service V2 with REAL data"""
    
    def __init__(self, db_path: str = "my_symbols_v2.db"):
        """Initialize the My Symbols service V2"""
        self.db_path = db_path
        
        # Portfolio configuration
        self.max_portfolio_size = 10
        self.min_score_threshold = 0.6
        self.replacement_candidates = 2
        
        # NEW: Safety limits
        self.max_position_weight = 20.0  # Max 20% per symbol
        self.min_position_weight = 5.0   # Min 5% per symbol
        self.min_score_for_trading = 0.6  # Don't trade low scores
        self.require_binance_availability = False  # Prefer but don't require
        
        # Initialize database
        self._init_database()
        
        # Load initial data with CORRECT symbols
        self._load_initial_data()
    
    def _init_database(self):
        """Initialize SQLite database for My Symbols management"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create symbols table with new fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS symbols (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL UNIQUE,
                    root_symbol TEXT NOT NULL,
                    base_currency TEXT NOT NULL,
                    quote_currency TEXT NOT NULL,
                    settle_currency TEXT NOT NULL,
                    contract_type TEXT NOT NULL,
                    lot_size REAL NOT NULL,
                    tick_size REAL NOT NULL,
                    max_order_qty INTEGER NOT NULL,
                    max_price REAL NOT NULL,
                    multiplier REAL NOT NULL,
                    initial_margin REAL NOT NULL,
                    maintain_margin REAL NOT NULL,
                    max_leverage INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Active',
                    is_eligible_for_management BOOLEAN NOT NULL DEFAULT 1,
                    is_kucoin_tradeable BOOLEAN NOT NULL DEFAULT 0,
                    is_binance_available BOOLEAN NOT NULL DEFAULT 0,
                    sector_category TEXT,
                    market_cap_category TEXT,
                    volatility_classification TEXT,
                    liquidity_tier TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create portfolio composition table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_composition (
                    id TEXT PRIMARY KEY,
                    symbol_id TEXT NOT NULL,
                    position_rank INTEGER NOT NULL UNIQUE,
                    inclusion_date TIMESTAMP NOT NULL,
                    inclusion_reason TEXT,
                    current_score REAL,
                    weight_percentage REAL,
                    status TEXT NOT NULL DEFAULT 'Active',
                    is_replacement_candidate BOOLEAN NOT NULL DEFAULT 0,
                    replacement_priority INTEGER,
                    performance_since_inclusion REAL,
                    max_drawdown_since_inclusion REAL,
                    volatility_since_inclusion REAL,
                    is_tradeable BOOLEAN NOT NULL DEFAULT 1,
                    last_validation TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
                )
            ''')
            
            # Create symbol scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS symbol_scores (
                    id TEXT PRIMARY KEY,
                    symbol_id TEXT NOT NULL,
                    technical_score REAL,
                    fundamental_score REAL,
                    market_structure_score REAL,
                    risk_score REAL,
                    composite_score REAL NOT NULL,
                    confidence_level REAL NOT NULL,
                    rank INTEGER,
                    calculation_timestamp TIMESTAMP NOT NULL,
                    supporting_data TEXT,
                    data_source TEXT DEFAULT 'real',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (symbol_id) REFERENCES symbols (id)
                )
            ''')
            
            # Other tables remain the same...
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_history (
                    id TEXT PRIMARY KEY,
                    symbol_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    position_rank INTEGER,
                    trigger_reason TEXT NOT NULL,
                    trigger_score REAL,
                    decision_confidence REAL,
                    replaced_symbol_id TEXT,
                    replacement_score_difference REAL,
                    expected_performance_impact REAL,
                    actual_performance_impact REAL,
                    decision_algorithm_version TEXT,
                    agent_consensus_level REAL,
                    manual_override BOOLEAN NOT NULL DEFAULT 0,
                    override_reason TEXT,
                    action_timestamp TIMESTAMP NOT NULL,
                    action_by TEXT NOT NULL,
                    FOREIGN KEY (symbol_id) REFERENCES symbols (id),
                    FOREIGN KEY (replaced_symbol_id) REFERENCES symbols (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ My Symbols V2 database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def _load_initial_data(self):
        """Load initial symbols with CORRECT format"""
        try:
            # Load default symbols with validation - run in background
            import threading
            import asyncio
            
            def run_async_load():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._load_and_validate_default_symbols())
                finally:
                    loop.close()
            
            # Start in background thread
            thread = threading.Thread(target=run_async_load, daemon=True)
            thread.start()
            
            logger.info("✅ Initial data loading started in background")
            
        except Exception as e:
            logger.error(f"❌ Failed to load initial data: {e}")
    
    async def _load_and_validate_default_symbols(self):
        """Load and validate default symbols"""
        try:
            from src.services.futures_symbol_validator import get_futures_validator
            
            # CORRECTED symbols format (standard format, not KuCoin format)
            default_symbols = [
                {"symbol": "BTCUSDT", "name": "Bitcoin", "base": "BTC", "quote": "USDT"},
                {"symbol": "ETHUSDT", "name": "Ethereum", "base": "ETH", "quote": "USDT"},
                {"symbol": "SOLUSDT", "name": "Solana", "base": "SOL", "quote": "USDT"},
                {"symbol": "BNBUSDT", "name": "Binance Coin", "base": "BNB", "quote": "USDT"},
                {"symbol": "XRPUSDT", "name": "Ripple", "base": "XRP", "quote": "USDT"},
                {"symbol": "ADAUSDT", "name": "Cardano", "base": "ADA", "quote": "USDT"},
                {"symbol": "AVAXUSDT", "name": "Avalanche", "base": "AVAX", "quote": "USDT"},
                {"symbol": "DOGEUSDT", "name": "Dogecoin", "base": "DOGE", "quote": "USDT"},
                {"symbol": "DOTUSDT", "name": "Polkadot", "base": "DOT", "quote": "USDT"}
            ]
            
            # Get validator
            validator = await get_futures_validator()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            valid_symbols = []
            for symbol_data in default_symbols:
                symbol = symbol_data['symbol']
                
                # Check if symbol already exists
                cursor.execute("SELECT id FROM symbols WHERE symbol = ?", (symbol,))
                if cursor.fetchone():
                    continue
                
                # VALIDATE with KuCoin
                is_kucoin_tradeable = await validator.is_tradeable_on_kucoin(symbol)
                is_binance_available = symbol in validator.binance_symbols
                
                if not is_kucoin_tradeable:
                    logger.warning(f"⚠️ {symbol} not tradeable on KuCoin - SKIPPING")
                    continue
                
                # Get symbol info from validator
                symbol_info = await validator.get_symbol_info(symbol)
                
                # Insert validated symbol
                symbol_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO symbols (
                        id, symbol, root_symbol, base_currency, quote_currency, settle_currency,
                        contract_type, lot_size, tick_size, max_order_qty, max_price, multiplier,
                        initial_margin, maintain_margin, max_leverage, status,
                        is_kucoin_tradeable, is_binance_available
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol_id,
                    symbol,
                    symbol_data['base'],
                    symbol_data['base'],
                    symbol_data['quote'],
                    symbol_data['quote'],
                    symbol_info.contract_type if symbol_info else 'perpetual',
                    symbol_info.min_qty if symbol_info else 0.001,
                    symbol_info.tick_size if symbol_info else 0.01,
                    int(symbol_info.max_qty) if symbol_info else 1000000,
                    1000000.0,
                    1.0,
                    symbol_info.maintainance_margin if symbol_info else 0.01,
                    symbol_info.maintainance_margin if symbol_info else 0.005,
                    symbol_info.max_leverage if symbol_info else 100,
                    'Active',
                    is_kucoin_tradeable,
                    is_binance_available
                ))
                
                valid_symbols.append(symbol)
                logger.info(f"✅ Added {symbol} - KuCoin: {'✓' if is_kucoin_tradeable else '✗'}, Binance: {'✓' if is_binance_available else '✗'}")
            
            conn.commit()
            
            # Check if portfolio already has active entries - only initialize if empty
            cursor.execute("SELECT COUNT(*) FROM portfolio_composition WHERE status = 'Active'")
            active_count = cursor.fetchone()[0]
            
            if active_count == 0:
                # Initialize portfolio with validated symbols only if no active entries exist
                await self._initialize_portfolio_with_validated_symbols(valid_symbols[:self.max_portfolio_size])
                logger.info(f"✅ Portfolio initialized with {min(len(valid_symbols), self.max_portfolio_size)} validated symbols")
            else:
                logger.info(f"✅ Portfolio already has {active_count} active entries, skipping initialization")
            
            conn.close()
            logger.info(f"✅ Loaded {len(valid_symbols)} validated symbols")
            
        except Exception as e:
            logger.error(f"❌ Failed to load and validate symbols: {e}")
    
    async def _initialize_portfolio_with_validated_symbols(self, symbols: List[str]):
        """Initialize portfolio with validated symbols only"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for i, symbol in enumerate(symbols):
                symbol_id = self._get_symbol_id(symbol)
                if not symbol_id:
                    continue
                
                # Check if already in portfolio
                cursor.execute(
                    "SELECT id FROM portfolio_composition WHERE symbol_id = ? AND status = 'Active'", 
                    (symbol_id,)
                )
                if cursor.fetchone():
                    continue
                
                # Add to portfolio
                portfolio_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO portfolio_composition (
                        id, symbol_id, position_rank, inclusion_date, inclusion_reason,
                        current_score, weight_percentage, status, is_tradeable, last_validation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    portfolio_id,
                    symbol_id,
                    i + 1,
                    datetime.now().isoformat(),
                    'Initial validated portfolio',
                    0.7,  # Default good score
                    10.0,  # Equal weight initially
                    'Active',
                    True,
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Portfolio initialized with {len(symbols)} validated symbols")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize portfolio: {e}")
    
    def _get_symbol_id(self, symbol: str) -> Optional[str]:
        """Get symbol ID from symbol name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM symbols WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    async def add_symbol(self, symbol: str) -> Tuple[bool, str]:
        """Add a symbol to the database with validation"""
        try:
            from src.services.futures_symbol_validator import get_futures_validator
            
            # CRITICAL: Validate with KuCoin first
            validator = await get_futures_validator()
            if not await validator.is_tradeable_on_kucoin(symbol):
                return False, f"❌ {symbol} not tradeable on KuCoin futures"
            
            # Check if already exists
            if self._get_symbol_id(symbol):
                return False, f"Symbol {symbol} already exists"
            
            # Get symbol info
            symbol_info = await validator.get_symbol_info(symbol)
            if not symbol_info:
                return False, f"Could not get symbol info for {symbol}"
            
            # Add to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            symbol_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO symbols (
                    id, symbol, root_symbol, base_currency, quote_currency, settle_currency,
                    contract_type, lot_size, tick_size, max_order_qty, max_price, multiplier,
                    initial_margin, maintain_margin, max_leverage, status,
                    is_kucoin_tradeable, is_binance_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol_id,
                symbol,
                symbol_info.base_asset,
                symbol_info.base_asset,
                symbol_info.quote_asset,
                symbol_info.quote_asset,
                symbol_info.contract_type,
                symbol_info.min_qty,
                symbol_info.tick_size,
                int(symbol_info.max_qty),
                1000000.0,
                1.0,
                symbol_info.maintainance_margin,
                symbol_info.maintainance_margin,
                symbol_info.max_leverage,
                'Active',
                True,  # We validated it's on KuCoin
                symbol in validator.binance_symbols
            ))
            
            conn.commit()
            conn.close()
            
            return True, f"✅ Successfully added {symbol}"
            
        except Exception as e:
            logger.error(f"❌ Failed to add symbol {symbol}: {e}")
            return False, str(e)

    async def clear_portfolio(self):
        """Clear all symbols from the portfolio"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Set all portfolio entries to 'Removed' status
            cursor.execute('''
                UPDATE portfolio_composition 
                SET status = 'Removed', 
                    updated_at = CURRENT_TIMESTAMP
                WHERE status = 'Active'
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Portfolio cleared successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to clear portfolio: {e}")
            raise

    async def add_symbol_to_portfolio(self, symbol: str, position_rank: int) -> bool:
        """Add a symbol to portfolio at specific position"""
        try:
            logger.info(f"🔍 Adding {symbol} to portfolio at position {position_rank}")
            
            # First try to find the symbol as-is
            symbol_id = self._get_symbol_id(symbol)
            logger.info(f"🔍 Symbol {symbol} as-is: symbol_id = {symbol_id}")
            
            # If not found, try to convert to KuCoin format
            if not symbol_id:
                kucoin_symbol = to_kucoin(symbol)
                symbol_id = self._get_symbol_id(kucoin_symbol)
                logger.info(f"🔍 Symbol {symbol} as {kucoin_symbol}: symbol_id = {symbol_id}")
                if symbol_id:
                    logger.info(f"✅ Found {symbol} as {kucoin_symbol} in database")
                else:
                    logger.error(f"❌ Symbol {symbol} (and {kucoin_symbol}) not found in database")
                    return False
            
            # Check if this exact symbol is already in the portfolio (prevent duplicates)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT position_rank FROM portfolio_composition pc
                JOIN symbols s ON pc.symbol_id = s.id
                WHERE s.symbol = ? AND pc.status = 'Active'
            ''', (symbol,))
            
            existing_position = cursor.fetchone()
            if existing_position:
                logger.warning(f"⚠️ Symbol {symbol} already exists at position {existing_position[0]}, skipping")
                conn.close()
                return False
            
            # Check if the same underlying asset (different exchange) is already in portfolio
            # For example, if XBTUSDTM is already there, don't add BTCUSDT
            standard_symbol = to_standard(symbol)
            kucoin_symbol = to_kucoin(symbol)
            
            # Check if any existing symbol maps to the same standard symbol
            cursor.execute('''
                SELECT pc.position_rank, s.symbol FROM portfolio_composition pc
                JOIN symbols s ON pc.symbol_id = s.id
                WHERE pc.status = 'Active'
            ''')
            
            existing_symbols = cursor.fetchall()
            for existing_pos, existing_sym in existing_symbols:
                existing_standard = to_standard(existing_sym)
                if existing_standard == standard_symbol:
                    logger.warning(f"⚠️ Same underlying asset {standard_symbol} already exists as {existing_sym} at position {existing_pos}, skipping {symbol}")
                    conn.close()
                    return False
            
            # Check if position_rank already exists and remove it first (any status)
            cursor.execute('''
                DELETE FROM portfolio_composition 
                WHERE position_rank = ?
            ''', (position_rank,))
            
            portfolio_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO portfolio_composition (
                    id, symbol_id, position_rank, inclusion_date, inclusion_reason,
                    current_score, weight_percentage, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
                portfolio_id,
                symbol_id,
                position_rank,
                datetime.now().isoformat(),
                'Added via API',
                0.5,  # Default score
                10.0,  # Equal weight
                'Active'
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Added {symbol} to portfolio at position {position_rank} with symbol_id {symbol_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add {symbol} to portfolio: {e}")
            return False

    async def remove_symbol_from_portfolio(self, symbol: str) -> bool:
        """Remove a symbol from portfolio"""
        try:
            logger.info(f"🔍 Removing {symbol} from portfolio")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find the symbol in portfolio and mark as removed
            cursor.execute('''
                UPDATE portfolio_composition 
                SET status = 'Removed', 
                    updated_at = CURRENT_TIMESTAMP
                WHERE symbol_id IN (
                    SELECT id FROM symbols WHERE symbol = ?
                ) AND status = 'Active'
            ''', (symbol,))
            
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_affected > 0:
                logger.info(f"✅ Removed {symbol} from portfolio")
                return True
            else:
                logger.warning(f"⚠️ Symbol {symbol} not found in active portfolio")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to remove {symbol} from portfolio: {e}")
            return False
    
    async def calculate_symbol_scores(self) -> Dict[str, float]:
        """Calculate scores using REAL market data"""
        try:
            from src.services.real_time_price_service import get_real_time_price_service
            
            # Get all eligible symbols
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT symbol FROM symbols WHERE is_eligible_for_management = 1 AND is_kucoin_tradeable = 1"
            )
            symbols = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Get real-time price service
            price_service = await get_real_time_price_service()
            
            scores = {}
            for symbol in symbols:
                try:
                    # Calculate scores using REAL data
                    technical_score = await self._calculate_technical_score_real(symbol, price_service)
                    fundamental_score = await self._calculate_fundamental_score_real(symbol, price_service)
                    market_structure_score = await self._calculate_market_structure_score_real(symbol, price_service)
                    risk_score = await self._calculate_risk_score_real(symbol, price_service)
                    
                    # Calculate composite score
                    composite_score = (
                        technical_score * 0.35 +      # Technical most important
                        fundamental_score * 0.25 +    # Volume/liquidity important
                        market_structure_score * 0.20 + # Market structure
                        risk_score * 0.20              # Risk management
                    )
                    
                    scores[symbol] = composite_score
                    
                    # Save score to database
                    await self._save_symbol_score(
                        symbol, technical_score, fundamental_score, 
                        market_structure_score, risk_score, composite_score,
                        data_source="real"
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Failed to calculate score for {symbol}: {e}")
                    scores[symbol] = 0.5  # Default neutral score
            
            return scores
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate symbol scores: {e}")
            return {}
    
    async def _calculate_technical_score_real(self, symbol: str, price_service) -> float:
        """Calculate technical score using REAL data"""
        try:
            # Get real technical data
            tech_data = await price_service.get_technical_data(symbol)
            if not tech_data:
                logger.warning(f"No technical data for {symbol}, using default")
                return 0.5
            
            # RSI Score (30-70 is normal, <30 oversold, >70 overbought)
            rsi = tech_data.rsi
            if rsi < 30:
                rsi_score = 0.8  # Oversold = potential buy
            elif rsi > 70:
                rsi_score = 0.2  # Overbought = potential sell
            else:
                rsi_score = 0.5 + (50 - rsi) / 100  # Neutral zone
            
            # Trend Score
            trend_score = {
                "bullish": 0.8,
                "neutral": 0.5,
                "bearish": 0.2
            }.get(tech_data.trend, 0.5)
            
            # Signal Strength Score
            signal_score = tech_data.signal_strength / 100
            
            # Combine scores
            technical_score = (
                rsi_score * 0.4 +
                trend_score * 0.4 +
                signal_score * 0.2
            )
            
            return min(1.0, max(0.0, technical_score))
            
        except Exception as e:
            logger.error(f"Error calculating technical score for {symbol}: {e}")
            return 0.5
    
    async def _calculate_fundamental_score_real(self, symbol: str, price_service) -> float:
        """Calculate fundamental score using REAL data"""
        try:
            # Get real price data
            price_data = await price_service.get_real_time_price(symbol)
            if not price_data:
                return 0.5
            
            # Volume Score (higher volume = better liquidity)
            volume = price_data.volume_24h
            if volume > 1000000000:  # > $1B
                volume_score = 1.0
            elif volume > 100000000:  # > $100M
                volume_score = 0.8
            elif volume > 10000000:   # > $10M
                volume_score = 0.6
            else:
                volume_score = max(0.2, volume / 10000000)
            
            # Price change momentum
            change = price_data.change_24h
            if -5 <= change <= 5:  # Stable
                momentum_score = 0.7
            elif 5 < change <= 10:  # Good momentum
                momentum_score = 0.8
            elif change > 10:  # Very strong momentum (but risky)
                momentum_score = 0.6
            else:  # Negative momentum
                momentum_score = max(0.2, (change + 20) / 20)
            
            # Verification bonus (multiple sources agree)
            verification_score = 1.0 if price_data.is_verified else 0.8
            
            fundamental_score = (
                volume_score * 0.5 +
                momentum_score * 0.3 +
                verification_score * 0.2
            )
            
            return min(1.0, max(0.0, fundamental_score))
            
        except Exception as e:
            logger.error(f"Error calculating fundamental score for {symbol}: {e}")
            return 0.5
    
    async def _calculate_market_structure_score_real(self, symbol: str, price_service) -> float:
        """Calculate market structure score using REAL data"""
        try:
            # Get technical data for support/resistance
            tech_data = await price_service.get_technical_data(symbol)
            if not tech_data:
                return 0.5
            
            # Get current price
            price_data = await price_service.get_real_time_price(symbol)
            if not price_data:
                return 0.5
            
            current_price = price_data.price
            
            # Check position relative to support/resistance
            position_score = 0.5
            if tech_data.support_levels and tech_data.resistance_levels:
                nearest_support = min(tech_data.support_levels, key=lambda x: abs(x - current_price))
                nearest_resistance = min(tech_data.resistance_levels, key=lambda x: abs(x - current_price))
                
                # Calculate position in range
                if nearest_resistance > nearest_support:
                    position_in_range = (current_price - nearest_support) / (nearest_resistance - nearest_support)
                    # Better score if closer to support (potential upside)
                    position_score = 1.0 - (position_in_range * 0.5)
            
            # MACD analysis
            macd_score = 0.5
            if tech_data.macd:
                histogram = tech_data.macd.get('histogram', 0)
                if histogram > 0:
                    macd_score = min(0.8, 0.5 + abs(histogram) / 100)
                else:
                    macd_score = max(0.2, 0.5 - abs(histogram) / 100)
            
            market_structure_score = (
                position_score * 0.6 +
                macd_score * 0.4
            )
            
            return min(1.0, max(0.0, market_structure_score))
            
        except Exception as e:
            logger.error(f"Error calculating market structure score for {symbol}: {e}")
            return 0.5
    
    async def _calculate_risk_score_real(self, symbol: str, price_service) -> float:
        """Calculate risk score using REAL data"""
        try:
            # Get historical prices for volatility calculation
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            historical = await price_service.get_historical_prices(symbol, start_date, end_date)
            
            if historical and len(historical) > 1:
                # Calculate volatility from real price movements
                prices = [h.close for h in historical]
                returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                
                if returns:
                    import numpy as np
                    volatility = np.std(returns)
                    
                    # Lower volatility = higher risk score (safer)
                    if volatility < 0.02:  # < 2% daily volatility
                        risk_score = 0.9
                    elif volatility < 0.05:  # < 5% daily volatility
                        risk_score = 0.7
                    elif volatility < 0.10:  # < 10% daily volatility
                        risk_score = 0.5
                    else:  # High volatility
                        risk_score = max(0.2, 1.0 - (volatility * 5))
                else:
                    risk_score = 0.5
            else:
                # No historical data, use current price change as proxy
                price_data = await price_service.get_real_time_price(symbol)
                if price_data:
                    change = abs(price_data.change_24h)
                    risk_score = max(0.2, 1.0 - (change / 20))  # 20% change = 0 score
                else:
                    risk_score = 0.5
            
            return float(min(1.0, max(0.0, risk_score)))
            
        except Exception as e:
            logger.error(f"Error calculating risk score for {symbol}: {e}")
            return 0.5
    
    async def _save_symbol_score(self, symbol: str, technical_score: float, fundamental_score: float,
                                market_structure_score: float, risk_score: float, composite_score: float,
                                data_source: str = "real"):
        """Save symbol score to database"""
        try:
            symbol_id = self._get_symbol_id(symbol)
            if not symbol_id:
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old scores for this symbol
            cursor.execute("DELETE FROM symbol_scores WHERE symbol_id = ?", (symbol_id,))
            
            # Insert new score
            score_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO symbol_scores (
                    id, symbol_id, technical_score, fundamental_score, market_structure_score,
                    risk_score, composite_score, confidence_level, rank, calculation_timestamp,
                    supporting_data, data_source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                score_id,
                symbol_id,
                technical_score,
                fundamental_score,
                market_structure_score,
                risk_score,
                composite_score,
                0.8 if data_source == "real" else 0.3,  # Higher confidence for real data
                0,    # Will be updated later
                datetime.now().isoformat(),
                json.dumps({
                    'technical_score': technical_score,
                    'fundamental_score': fundamental_score,
                    'market_structure_score': market_structure_score,
                    'risk_score': risk_score,
                    'composite_score': composite_score,
                    'data_source': data_source
                }),
                data_source
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to save symbol score for {symbol}: {e}")
    
    async def calculate_dynamic_weights(self) -> Dict[str, float]:
        """Calculate dynamic portfolio weights based on scores"""
        try:
            portfolio = await self.get_portfolio()
            scores = await self.calculate_symbol_scores()
            
            # Filter out symbols below minimum score
            valid_symbols = {
                symbol: score 
                for symbol, score in scores.items() 
                if score >= self.min_score_for_trading and 
                   symbol in [e.symbol for e in portfolio]
            }
            
            if not valid_symbols:
                # Equal weight if no valid scores
                return {entry.symbol: 10.0 for entry in portfolio}
            
            # Calculate weights proportional to scores
            total_score = sum(valid_symbols.values())
            
            weights = {}
            for symbol, score in valid_symbols.items():
                # Base weight proportional to score
                base_weight = (score / total_score) * 100
                
                # Apply min/max limits
                weight = max(self.min_position_weight, min(self.max_position_weight, base_weight))
                weights[symbol] = weight
            
            # Normalize to 100%
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: (v / total_weight) * 100 for k, v in weights.items()}
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for symbol, weight in weights.items():
                symbol_id = self._get_symbol_id(symbol)
                if symbol_id:
                    cursor.execute('''
                        UPDATE portfolio_composition 
                        SET weight_percentage = ?, updated_at = ?
                        WHERE symbol_id = ? AND status = 'Active'
                    ''', (weight, datetime.now().isoformat(), symbol_id))
            
            conn.commit()
            conn.close()
            
            return weights
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate dynamic weights: {e}")
            return {}
    
    async def validate_portfolio_safety(self) -> Dict[str, Any]:
        """Validate portfolio meets all safety requirements"""
        try:
            from src.services.futures_symbol_validator import get_futures_validator
            
            portfolio = await self.get_portfolio()
            validator = await get_futures_validator()
            
            issues = []
            warnings = []
            valid_symbols = []
            
            for entry in portfolio:
                # Check KuCoin availability
                if not await validator.is_tradeable_on_kucoin(entry.symbol):
                    issues.append(f"❌ {entry.symbol} NOT tradeable on KuCoin")
                else:
                    valid_symbols.append(entry.symbol)
                
                # Check score threshold
                if entry.current_score < self.min_score_for_trading:
                    warnings.append(f"⚠️ {entry.symbol} score below threshold: {entry.current_score:.3f}")
                
                # Check if marked for replacement
                if entry.is_replacement_candidate:
                    warnings.append(f"⚠️ {entry.symbol} marked for replacement")
            
            # Check portfolio size
            if len(portfolio) > self.max_portfolio_size:
                issues.append(f"❌ Portfolio size {len(portfolio)} exceeds maximum {self.max_portfolio_size}")
            
            return {
                "is_safe": len(issues) == 0,
                "has_warnings": len(warnings) > 0,
                "issues": issues,
                "warnings": warnings,
                "valid_symbols": valid_symbols,
                "total_symbols": len(portfolio),
                "tradeable_symbols": len(valid_symbols),
                "validation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to validate portfolio safety: {e}")
            return {
                "is_safe": False,
                "error": str(e)
            }
    
    async def get_tradeable_symbols(self) -> List[str]:
        """Get only symbols that can be traded right now"""
        try:
            from src.services.futures_symbol_validator import get_futures_validator
            
            portfolio = await self.get_portfolio()
            validator = await get_futures_validator()
            
            tradeable = []
            for entry in portfolio:
                # Must pass ALL checks
                if entry.current_score >= self.min_score_for_trading:
                    if await validator.is_tradeable_on_kucoin(entry.symbol):
                        if not entry.is_replacement_candidate:
                            tradeable.append(entry.symbol)
            
            return tradeable
            
        except Exception as e:
            logger.error(f"❌ Failed to get tradeable symbols: {e}")
            return []
    
    async def should_trade_symbol(self, symbol: str) -> Tuple[bool, str]:
        """Check if a symbol should be traded with detailed reason"""
        try:
            from src.services.futures_symbol_validator import get_futures_validator
            
            portfolio = await self.get_portfolio()
            entry = next((e for e in portfolio if e.symbol == symbol), None)
            
            if not entry:
                return False, "Not in portfolio"
            
            # Check KuCoin availability
            validator = await get_futures_validator()
            if not await validator.is_tradeable_on_kucoin(symbol):
                return False, "Not tradeable on KuCoin"
            
            # Check score
            if entry.current_score < self.min_score_for_trading:
                return False, f"Score too low: {entry.current_score:.3f} < {self.min_score_for_trading}"
            
            # Check replacement status
            if entry.is_replacement_candidate:
                return False, "Marked for replacement"
            
            # Check weight
            if entry.weight_percentage < self.min_position_weight:
                return False, f"Weight too low: {entry.weight_percentage:.1f}%"
            
            return True, f"OK to trade (score: {entry.current_score:.3f}, weight: {entry.weight_percentage:.1f}%)"
            
        except Exception as e:
            logger.error(f"❌ Failed to check if should trade {symbol}: {e}")
            return False, str(e)
    
    async def get_portfolio(self) -> List[PortfolioEntry]:
        """Get current portfolio composition"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    s.symbol,
                    pc.position_rank,
                    pc.inclusion_date,
                    pc.current_score,
                    pc.weight_percentage,
                    pc.status,
                    pc.is_replacement_candidate,
                    pc.replacement_priority,
                    pc.performance_since_inclusion,
                    pc.max_drawdown_since_inclusion,
                    pc.volatility_since_inclusion,
                    pc.is_tradeable
                FROM portfolio_composition pc
                JOIN symbols s ON pc.symbol_id = s.id
                WHERE pc.status = 'Active'
                ORDER BY pc.position_rank
            ''')
            
            portfolio = []
            for row in cursor.fetchall():
                entry = PortfolioEntry(
                    symbol=row[0],
                    position_rank=row[1],
                    inclusion_date=datetime.fromisoformat(row[2]),
                    current_score=row[3] or 0.0,
                    weight_percentage=row[4] or 10.0,
                    status=row[5],
                    is_replacement_candidate=bool(row[6]),
                    replacement_priority=row[7],
                    performance_since_inclusion=row[8],
                    max_drawdown_since_inclusion=row[9],
                    volatility_since_inclusion=row[10],
                    is_tradeable=bool(row[11])
                )
                portfolio.append(entry)
            
            conn.close()
            return portfolio
            
        except Exception as e:
            logger.error(f"❌ Failed to get portfolio: {e}")
            return []
    
    async def get_symbol_scores(self, limit: int = 50) -> List[SymbolScore]:
        """Get top scored symbols from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    s.symbol,
                    ss.technical_score,
                    ss.fundamental_score,
                    ss.market_structure_score,
                    ss.risk_score,
                    ss.composite_score,
                    ss.confidence_level,
                    ss.rank,
                    ss.calculation_timestamp,
                    ss.supporting_data
                FROM symbol_scores ss
                JOIN symbols s ON ss.symbol_id = s.id
                ORDER BY ss.composite_score DESC
                LIMIT ?
            ''', (limit,))
            
            scores = []
            for row in cursor.fetchall():
                scores.append(SymbolScore(
                    symbol=row[0],
                    technical_score=row[1] or 0.0,
                    fundamental_score=row[2] or 0.0,
                    market_structure_score=row[3] or 0.0,
                    risk_score=row[4] or 0.0,
                    composite_score=row[5] or 0.0,
                    confidence_level=row[6] or 0.0,
                    rank=row[7] or 0,
                    calculation_timestamp=datetime.fromisoformat(row[8]) if row[8] else datetime.now(),
                    supporting_data=json.loads(row[9]) if row[9] else {},
                    data_source="real"
                ))
            
            conn.close()
            return scores
            
        except Exception as e:
            logger.error(f"❌ Failed to get symbol scores: {e}")
            return []
    
    async def evaluate_portfolio_replacement(self) -> List[Dict[str, Any]]:
        """Evaluate portfolio and recommend replacements"""
        try:
            portfolio = await self.get_portfolio()
            all_scores = await self.calculate_symbol_scores()
            
            # Find lowest scoring portfolio symbols
            portfolio_scores = [
                (entry.symbol, entry.current_score) 
                for entry in portfolio
            ]
            portfolio_scores.sort(key=lambda x: x[1])
            
            # Find highest scoring non-portfolio symbols
            portfolio_symbols = {entry.symbol for entry in portfolio}
            candidate_scores = [
                (symbol, score) 
                for symbol, score in all_scores.items() 
                if symbol not in portfolio_symbols
            ]
            candidate_scores.sort(key=lambda x: x[1], reverse=True)
            
            recommendations = []
            
            # Recommend replacements for bottom performers
            for i in range(min(self.replacement_candidates, len(portfolio_scores))):
                replace_symbol, replace_score = portfolio_scores[i]
                
                if replace_score < self.min_score_threshold and candidate_scores:
                    candidate_symbol, candidate_score = candidate_scores[0]
                    
                    if candidate_score > replace_score * 1.2:  # 20% improvement threshold
                        recommendations.append({
                            'replace_symbol': replace_symbol,
                            'replace_score': replace_score,
                            'candidate_symbol': candidate_symbol,
                            'candidate_score': candidate_score,
                            'score_improvement': candidate_score - replace_score,
                            'recommendation_strength': min(1.0, (candidate_score - replace_score) / replace_score)
                        })
                        
                        # Remove used candidate
                        candidate_scores.pop(0)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate portfolio replacement: {e}")
            return []
    
    async def execute_portfolio_replacement(self, old_symbol: str, new_symbol: str) -> bool:
        """Execute a portfolio replacement"""
        try:
            from src.services.futures_symbol_validator import get_futures_validator
            
            # Validate new symbol
            validator = await get_futures_validator()
            if not await validator.is_tradeable_on_kucoin(new_symbol):
                logger.error(f"❌ {new_symbol} not tradeable on KuCoin")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get old and new symbol IDs
            old_symbol_id = self._get_symbol_id(old_symbol)
            new_symbol_id = self._get_symbol_id(new_symbol)
            
            if not old_symbol_id or not new_symbol_id:
                logger.error(f"❌ Symbol IDs not found")
                conn.close()
                return False
            
            # Get position rank of old symbol
            cursor.execute(
                "SELECT position_rank FROM portfolio_composition WHERE symbol_id = ? AND status = 'Active'",
                (old_symbol_id,)
            )
            result = cursor.fetchone()
            if not result:
                logger.error(f"❌ {old_symbol} not in active portfolio")
                conn.close()
                return False
            
            position_rank = result[0]
            
            # Deactivate old symbol
            cursor.execute(
                "UPDATE portfolio_composition SET status = 'Replaced', updated_at = ? WHERE symbol_id = ?",
                (datetime.now().isoformat(), old_symbol_id)
            )
            
            # Add new symbol with same rank
            portfolio_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO portfolio_composition (
                    id, symbol_id, position_rank, inclusion_date, inclusion_reason,
                    current_score, weight_percentage, status, is_tradeable, last_validation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                portfolio_id,
                new_symbol_id,
                position_rank,
                datetime.now().isoformat(),
                f'Replaced {old_symbol} due to better score',
                0.7,  # Will be updated on next calculation
                10.0,  # Will be updated on next calculation
                'Active',
                True,
                datetime.now().isoformat()
            ))
            
            # Log replacement in history
            history_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO portfolio_history (
                    id, symbol_id, action_type, position_rank, trigger_reason,
                    replaced_symbol_id, action_timestamp, action_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                history_id,
                new_symbol_id,
                'replacement',
                position_rank,
                'Score-based replacement',
                old_symbol_id,
                datetime.now().isoformat(),
                'system'
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Successfully replaced {old_symbol} with {new_symbol}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to execute replacement: {e}")
            return False
    
    async def get_portfolio_analytics(self) -> Dict[str, Any]:
        """Get comprehensive portfolio analytics"""
        try:
            portfolio = await self.get_portfolio()
            scores = await self.calculate_symbol_scores()
            
            if not portfolio:
                return {
                    'portfolio_size': 0,
                    'average_score': 0.0,
                    'total_score': 0.0,
                    'average_performance': 0.0,
                    'max_drawdown': 0.0,
                    'average_volatility': 0.0,
                    'replacement_candidates': 0,
                    'top_performers': [],
                    'lowest_scorers': [],
                    'last_updated': datetime.now().isoformat()
                }
            
            # Calculate metrics
            portfolio_scores = [entry.current_score for entry in portfolio]
            average_score = sum(portfolio_scores) / len(portfolio_scores) if portfolio_scores else 0
            
            performances = [entry.performance_since_inclusion for entry in portfolio if entry.performance_since_inclusion]
            average_performance = sum(performances) / len(performances) if performances else 0
            
            drawdowns = [entry.max_drawdown_since_inclusion for entry in portfolio if entry.max_drawdown_since_inclusion]
            max_drawdown = max(drawdowns) if drawdowns else 0
            
            volatilities = [entry.volatility_since_inclusion for entry in portfolio if entry.volatility_since_inclusion]
            average_volatility = sum(volatilities) / len(volatilities) if volatilities else 0
            
            replacement_candidates = sum(1 for entry in portfolio if entry.is_replacement_candidate)
            
            # Sort portfolio by score
            sorted_portfolio = sorted(portfolio, key=lambda x: x.current_score, reverse=True)
            
            return {
                'portfolio_size': len(portfolio),
                'average_score': average_score,
                'total_score': sum(portfolio_scores),
                'average_performance': average_performance,
                'max_drawdown': max_drawdown,
                'average_volatility': average_volatility,
                'replacement_candidates': replacement_candidates,
                'top_performers': sorted_portfolio[:3],
                'lowest_scorers': sorted_portfolio[-3:],
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get portfolio analytics: {e}")
            return {}
    
    async def get_position_size_for_symbol(self, symbol: str, account_balance: float) -> float:
        """Calculate position size based on weight and account balance"""
        try:
            # Convert symbol to standard format
            standard_symbol = to_standard(symbol)
            
            portfolio = await self.get_portfolio()
            entry = next((e for e in portfolio if e.symbol == standard_symbol), None)
            
            if not entry:
                logger.warning(f"Symbol {standard_symbol} not in portfolio")
                return 0.0
            
            # Check if should trade
            can_trade, reason = await self.should_trade_symbol(standard_symbol)
            if not can_trade:
                logger.warning(f"Should not trade {standard_symbol}: {reason}")
                return 0.0
            
            # Position size = account_balance * weight_percentage / 100
            position_size = account_balance * entry.weight_percentage / 100
            
            # Apply risk limits
            max_position = account_balance * self.max_position_weight / 100
            min_position = account_balance * self.min_position_weight / 100
            
            # Ensure within limits
            position_size = max(min_position, min(position_size, max_position))
            
            logger.info(f"Position size for {standard_symbol}: ${position_size:.2f} ({entry.weight_percentage:.1f}% of ${account_balance:.2f})")
            return position_size
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate position size for {symbol}: {e}")
            return 0.0
    
    async def check_portfolio_correlation(self) -> Dict[str, Any]:
        """Check correlation between portfolio symbols"""
        try:
            from src.services.real_time_price_service import get_real_time_price_service
            
            portfolio = await self.get_portfolio()
            if len(portfolio) < 2:
                return {'correlations': {}, 'warnings': []}
            
            price_service = await get_real_time_price_service()
            
            # Get historical prices for correlation calculation
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            price_data = {}
            for entry in portfolio:
                historical = await price_service.get_historical_prices(
                    entry.symbol, start_date, end_date
                )
                if historical:
                    price_data[entry.symbol] = [h.close for h in historical]
            
            if len(price_data) < 2:
                return {'correlations': {}, 'warnings': ['Insufficient price data for correlation']}
            
            # Create DataFrame for correlation calculation
            df = pd.DataFrame(price_data)
            
            # Calculate returns
            returns = df.pct_change().dropna()
            
            # Calculate correlation matrix
            correlation_matrix = returns.corr()
            
            correlations = {}
            warnings = []
            
            # Extract correlations and check for high correlation
            for i, symbol1 in enumerate(correlation_matrix.columns):
                for j, symbol2 in enumerate(correlation_matrix.columns):
                    if i < j:  # Upper triangle only
                        # Use values array to get native Python types
                        corr_float = float(correlation_matrix.values[i, j])
                        pair = f"{symbol1}-{symbol2}"
                        correlations[pair] = round(corr_float, 3)
                        
                        if abs(corr_float) > 0.8:
                            warnings.append(
                                f"⚠️ High correlation ({corr_float:.2f}) between {symbol1} and {symbol2}"
                            )
            
            return {
                'correlations': correlations,
                'warnings': warnings,
                'average_correlation': round(correlation_matrix.values[correlation_matrix.values != 1].mean(), 3),
                'max_correlation': round(correlation_matrix.values[correlation_matrix.values != 1].max(), 3),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to check portfolio correlation: {e}")
            return {'correlations': {}, 'warnings': [str(e)]}
    
    async def rebalance_portfolio(self) -> Dict[str, Any]:
        """Rebalance portfolio weights based on current scores"""
        try:
            # Recalculate weights
            new_weights = await self.calculate_dynamic_weights()
            
            if not new_weights:
                return {'changes': {}, 'message': 'No rebalancing needed'}
            
            # Get current portfolio
            portfolio = await self.get_portfolio()
            
            changes = {}
            for entry in portfolio:
                old_weight = entry.weight_percentage
                new_weight = new_weights.get(entry.symbol, 0)
                
                # Only record significant changes (> 1%)
                if abs(new_weight - old_weight) > 1.0:
                    changes[entry.symbol] = {
                        'old': round(old_weight, 2),
                        'new': round(new_weight, 2),
                        'change': round(new_weight - old_weight, 2),
                        'action': 'increase' if new_weight > old_weight else 'decrease'
                    }
            
            # Apply changes if any
            if changes:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                for symbol, change_data in changes.items():
                    symbol_id = self._get_symbol_id(symbol)
                    if symbol_id:
                        cursor.execute(
                            "UPDATE portfolio_composition SET weight_percentage = ?, updated_at = ? WHERE symbol_id = ? AND status = 'Active'",
                            (change_data['new'], datetime.now().isoformat(), symbol_id)
                        )
                
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Rebalanced portfolio: {len(changes)} changes")
            
            return {
                'changes': changes,
                'total_changes': len(changes),
                'message': f"Rebalanced {len(changes)} positions" if changes else "No rebalancing needed",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to rebalance portfolio: {e}")
            return {'changes': {}, 'error': str(e)}
    
    async def update_performance_metrics(self, symbol: str, pnl: float, current_price: Optional[float] = None):
        """Update actual performance metrics for a symbol"""
        try:
            standard_symbol = to_standard(symbol)
            symbol_id = self._get_symbol_id(standard_symbol)
            
            if not symbol_id:
                logger.error(f"Symbol {standard_symbol} not found")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current metrics
            cursor.execute(
                "SELECT performance_since_inclusion, max_drawdown_since_inclusion FROM portfolio_composition WHERE symbol_id = ? AND status = 'Active'",
                (symbol_id,)
            )
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
            
            current_performance = result[0] or 0.0
            current_max_drawdown = result[1] or 0.0
            
            # Update performance
            new_performance = current_performance + pnl
            
            # Update max drawdown if necessary
            if pnl < 0:
                new_drawdown = abs(pnl)
                if new_drawdown > current_max_drawdown:
                    current_max_drawdown = new_drawdown
            
            # Calculate volatility (simplified - would need more data points in production)
            # For now, just use a placeholder
            volatility = abs(pnl) * 0.1  # Simplified volatility estimate
            
            # Update database
            cursor.execute('''
                UPDATE portfolio_composition 
                SET performance_since_inclusion = ?,
                    max_drawdown_since_inclusion = ?,
                    volatility_since_inclusion = ?,
                    updated_at = ?
                WHERE symbol_id = ? AND status = 'Active'
            ''', (
                new_performance,
                current_max_drawdown,
                volatility,
                datetime.now().isoformat(),
                symbol_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Updated performance for {standard_symbol}: P&L={pnl:.2f}, Total={new_performance:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update performance metrics for {symbol}: {e}")
            return False
    
    async def check_portfolio_alerts(self) -> List[Dict[str, Any]]:
        """Check for portfolio issues that need attention"""
        try:
            from src.services.futures_symbol_validator import get_futures_validator
            
            alerts = []
            portfolio = await self.get_portfolio()
            validator = await get_futures_validator()
            
            for entry in portfolio:
                # Check using standard format (validator handles conversion)
                
                # Check KuCoin availability
                if not await validator.is_tradeable_on_kucoin(entry.symbol):
                    alerts.append({
                        'type': 'critical',
                        'symbol': entry.symbol,
                        'message': f'{entry.symbol} no longer tradeable on KuCoin',
                        'action': 'replace_immediately'
                    })
                
                # Check low scores
                if entry.current_score < self.min_score_for_trading:
                    alerts.append({
                        'type': 'warning',
                        'symbol': entry.symbol,
                        'message': f'{entry.symbol} score below threshold: {entry.current_score:.3f}',
                        'action': 'consider_replacement'
                    })
                
                # Check poor performance
                if entry.performance_since_inclusion and entry.performance_since_inclusion < -10:
                    alerts.append({
                        'type': 'warning',
                        'symbol': entry.symbol,
                        'message': f'{entry.symbol} significant losses: {entry.performance_since_inclusion:.2f}%',
                        'action': 'review_position'
                    })
                
                # Check high drawdown
                if entry.max_drawdown_since_inclusion and entry.max_drawdown_since_inclusion > 15:
                    alerts.append({
                        'type': 'warning',
                        'symbol': entry.symbol,
                        'message': f'{entry.symbol} high drawdown: {entry.max_drawdown_since_inclusion:.2f}%',
                        'action': 'reduce_position'
                    })
            
            # Check correlation
            correlation_data = await self.check_portfolio_correlation()
            if correlation_data.get('warnings'):
                for warning in correlation_data['warnings']:
                    alerts.append({
                        'type': 'info',
                        'symbol': 'portfolio',
                        'message': warning,
                        'action': 'diversify'
                    })
            
            # Check portfolio size
            if len(portfolio) < self.max_portfolio_size:
                alerts.append({
                    'type': 'info',
                    'symbol': 'portfolio',
                    'message': f'Portfolio has {len(portfolio)}/{self.max_portfolio_size} positions',
                    'action': 'consider_adding_symbols'
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Failed to check portfolio alerts: {e}")
            return [{
                'type': 'error',
                'symbol': 'system',
                'message': f'Alert system error: {str(e)}',
                'action': 'check_logs'
            }]

# Global instance
_my_symbols_service_v2 = None

def get_my_symbols_service() -> MySymbolsServiceV2:
    """Get or create My Symbols service V2 instance"""
    global _my_symbols_service_v2
    if _my_symbols_service_v2 is None:
        from src.config.database_config import DATABASE_PATH
        _my_symbols_service_v2 = MySymbolsServiceV2(DATABASE_PATH)
    return _my_symbols_service_v2