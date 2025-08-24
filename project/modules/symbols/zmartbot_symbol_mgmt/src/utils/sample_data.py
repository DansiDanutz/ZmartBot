"""
Sample Data Initialization for ZmartBot Symbol Management Module
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
import uuid

from src.models.user import db
from src.models.symbol_models import (
    Symbol, ScoringAlgorithm, SystemConfiguration
)

def initialize_sample_data():
    """Initialize sample data for testing and demonstration"""
    try:
        # Initialize scoring algorithms
        _create_scoring_algorithms()
        
        # Initialize system configuration
        _create_system_configuration()
        
        # Initialize sample symbols
        _create_sample_symbols()
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Sample data initialized successfully',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Failed to initialize sample data: {str(e)}'
        }

def _create_scoring_algorithms():
    """Create default scoring algorithms"""
    algorithms = [
        {
            'algorithm_name': 'Technical Momentum',
            'algorithm_version': '1.0',
            'algorithm_type': 'TECHNICAL',
            'parameters': {
                'indicators': ['RSI', 'MACD', 'BB'],
                'timeframes': ['1h', '4h', '1d'],
                'weights': {
                    'rsi': 0.3,
                    'macd': 0.3,
                    'bollinger': 0.2,
                    'volume': 0.2
                }
            },
            'weight_in_composite': Decimal('0.25')
        },
        {
            'algorithm_name': 'Fundamental Analysis',
            'algorithm_version': '1.0',
            'algorithm_type': 'FUNDAMENTAL',
            'parameters': {
                'factors': ['volume', 'open_interest', 'funding_rate'],
                'weights': {
                    'volume': 0.4,
                    'open_interest': 0.3,
                    'funding': 0.2,
                    'market_cap': 0.1
                }
            },
            'weight_in_composite': Decimal('0.25')
        },
        {
            'algorithm_name': 'Market Structure',
            'algorithm_version': '1.0',
            'algorithm_type': 'MARKET_STRUCTURE',
            'parameters': {
                'metrics': ['spread', 'depth', 'efficiency'],
                'weights': {
                    'spread': 0.3,
                    'depth': 0.3,
                    'impact': 0.2,
                    'efficiency': 0.2
                }
            },
            'weight_in_composite': Decimal('0.25')
        },
        {
            'algorithm_name': 'Risk Assessment',
            'algorithm_version': '1.0',
            'algorithm_type': 'RISK',
            'parameters': {
                'measures': ['volatility', 'correlation', 'drawdown'],
                'weights': {
                    'volatility': 0.3,
                    'drawdown': 0.3,
                    'correlation': 0.2,
                    'liquidity': 0.2
                }
            },
            'weight_in_composite': Decimal('0.25')
        },
        {
            'algorithm_name': 'Composite Score',
            'algorithm_version': '1.0',
            'algorithm_type': 'COMPOSITE',
            'parameters': {
                'weights': {
                    'TECHNICAL': 0.25,
                    'FUNDAMENTAL': 0.25,
                    'MARKET_STRUCTURE': 0.25,
                    'RISK': 0.25
                }
            },
            'weight_in_composite': Decimal('1.0')
        }
    ]
    
    for algo_data in algorithms:
        # Check if algorithm already exists
        existing = ScoringAlgorithm.query.filter_by(
            algorithm_name=algo_data['algorithm_name'],
            algorithm_version=algo_data['algorithm_version']
        ).first()
        
        if not existing:
            algorithm = ScoringAlgorithm(
                algorithm_name=algo_data['algorithm_name'],
                algorithm_version=algo_data['algorithm_version'],
                algorithm_type=algo_data['algorithm_type'],
                parameters=json.dumps(algo_data['parameters']),
                weight_in_composite=algo_data['weight_in_composite'],
                is_active=True,
                created_by='sample_data_init'
            )
            db.session.add(algorithm)

def _create_system_configuration():
    """Create default system configuration"""
    configs = [
        {
            'config_key': 'max_portfolio_symbols',
            'config_value': '10',
            'config_type': 'INTEGER',
            'description': 'Maximum number of symbols in managed portfolio'
        },
        {
            'config_key': 'replacement_candidates',
            'config_value': '2',
            'config_type': 'INTEGER',
            'description': 'Number of lowest-scoring symbols eligible for replacement'
        },
        {
            'config_key': 'min_consensus_score',
            'config_value': '0.7',
            'config_type': 'DECIMAL',
            'description': 'Minimum consensus score required for symbol addition'
        },
        {
            'config_key': 'scoring_update_frequency',
            'config_value': '300',
            'config_type': 'INTEGER',
            'description': 'Scoring update frequency in seconds'
        },
        {
            'config_key': 'signal_processing_timeout',
            'config_value': '30',
            'config_type': 'INTEGER',
            'description': 'Signal processing timeout in seconds'
        },
        {
            'config_key': 'agent_evaluation_timeout',
            'config_value': '60',
            'config_type': 'INTEGER',
            'description': 'Agent evaluation timeout in seconds'
        }
    ]
    
    for config_data in configs:
        # Check if config already exists
        existing = SystemConfiguration.query.filter_by(
            config_key=config_data['config_key']
        ).first()
        
        if not existing:
            config = SystemConfiguration(
                config_key=config_data['config_key'],
                config_value=config_data['config_value'],
                config_type=config_data['config_type'],
                description=config_data['description'],
                is_active=True,
                updated_by='sample_data_init'
            )
            db.session.add(config)

def _create_sample_symbols():
    """Create sample cryptocurrency futures symbols"""
    symbols_data = [
        {
            'symbol': 'BTCUSDTM',
            'root_symbol': 'BTC',
            'base_currency': 'BTC',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Layer 1',
            'market_cap_category': 'Large',
            'volatility_classification': 'Medium',
            'liquidity_tier': 'Tier 1'
        },
        {
            'symbol': 'ETHUSDTM',
            'root_symbol': 'ETH',
            'base_currency': 'ETH',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Layer 1',
            'market_cap_category': 'Large',
            'volatility_classification': 'Medium',
            'liquidity_tier': 'Tier 1'
        },
        {
            'symbol': 'ADAUSDTM',
            'root_symbol': 'ADA',
            'base_currency': 'ADA',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Layer 1',
            'market_cap_category': 'Medium',
            'volatility_classification': 'High',
            'liquidity_tier': 'Tier 2'
        },
        {
            'symbol': 'SOLUSDTM',
            'root_symbol': 'SOL',
            'base_currency': 'SOL',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Layer 1',
            'market_cap_category': 'Medium',
            'volatility_classification': 'High',
            'liquidity_tier': 'Tier 2'
        },
        {
            'symbol': 'LINKUSDTM',
            'root_symbol': 'LINK',
            'base_currency': 'LINK',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Oracle',
            'market_cap_category': 'Medium',
            'volatility_classification': 'High',
            'liquidity_tier': 'Tier 2'
        },
        {
            'symbol': 'DOTUSDTM',
            'root_symbol': 'DOT',
            'base_currency': 'DOT',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Layer 0',
            'market_cap_category': 'Medium',
            'volatility_classification': 'High',
            'liquidity_tier': 'Tier 2'
        },
        {
            'symbol': 'AVAXUSDTM',
            'root_symbol': 'AVAX',
            'base_currency': 'AVAX',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Layer 1',
            'market_cap_category': 'Medium',
            'volatility_classification': 'High',
            'liquidity_tier': 'Tier 2'
        },
        {
            'symbol': 'UNIUSDTM',
            'root_symbol': 'UNI',
            'base_currency': 'UNI',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'DeFi',
            'market_cap_category': 'Medium',
            'volatility_classification': 'High',
            'liquidity_tier': 'Tier 3'
        },
        {
            'symbol': 'AAVEUSDTM',
            'root_symbol': 'AAVE',
            'base_currency': 'AAVE',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'DeFi',
            'market_cap_category': 'Medium',
            'volatility_classification': 'High',
            'liquidity_tier': 'Tier 3'
        },
        {
            'symbol': 'ATOMUSDTM',
            'root_symbol': 'ATOM',
            'base_currency': 'ATOM',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Layer 0',
            'market_cap_category': 'Medium',
            'volatility_classification': 'High',
            'liquidity_tier': 'Tier 3'
        },
        {
            'symbol': 'FTMUSDTM',
            'root_symbol': 'FTM',
            'base_currency': 'FTM',
            'quote_currency': 'USDT',
            'settle_currency': 'USDT',
            'contract_type': 'FFWCSX',
            'sector_category': 'Layer 1',
            'market_cap_category': 'Small',
            'volatility_classification': 'Very High',
            'liquidity_tier': 'Tier 3'
        }
    ]
    
    for symbol_data in symbols_data:
        # Check if symbol already exists
        existing = Symbol.query.filter_by(symbol=symbol_data['symbol']).first()
        
        if not existing:
            symbol = Symbol(
                symbol=symbol_data['symbol'],
                root_symbol=symbol_data['root_symbol'],
                base_currency=symbol_data['base_currency'],
                quote_currency=symbol_data['quote_currency'],
                settle_currency=symbol_data['settle_currency'],
                contract_type=symbol_data['contract_type'],
                
                # Default contract specifications
                lot_size=Decimal('1'),
                tick_size=Decimal('0.1'),
                max_order_qty=1000000,
                max_price=Decimal('1000000'),
                multiplier=Decimal('1'),
                
                # Default margin and risk parameters
                initial_margin=Decimal('0.01'),
                maintain_margin=Decimal('0.005'),
                max_leverage=100,
                max_risk_limit=1000000,
                min_risk_limit=1000,
                risk_step=1000,
                
                # Default fee structure
                maker_fee_rate=Decimal('0.0002'),
                taker_fee_rate=Decimal('0.0006'),
                
                # Trading status
                status='Active',
                is_eligible_for_management=True,
                
                # Classification
                sector_category=symbol_data['sector_category'],
                market_cap_category=symbol_data['market_cap_category'],
                volatility_classification=symbol_data['volatility_classification'],
                liquidity_tier=symbol_data['liquidity_tier'],
                
                created_by='sample_data_init'
            )
            db.session.add(symbol)

