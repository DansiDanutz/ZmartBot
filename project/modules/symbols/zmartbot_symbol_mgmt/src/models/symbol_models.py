"""
Symbol Management Database Models
Implements the core database models for the ZmartBot Symbol Management Module
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any
import uuid
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property

# Import the db instance from the existing user model
from src.models.user import db

class Symbol(db.Model):
    """Master registry for all futures symbols with comprehensive contract specifications"""
    __tablename__ = 'symbols'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(50), nullable=False, unique=True, index=True)
    root_symbol = Column(String(20), nullable=False)
    base_currency = Column(String(10), nullable=False)
    quote_currency = Column(String(10), nullable=False)
    settle_currency = Column(String(10), nullable=False)
    contract_type = Column(String(20), nullable=False)
    
    # Contract specifications
    lot_size = Column(Numeric(20, 8), nullable=False)
    tick_size = Column(Numeric(20, 8), nullable=False)
    max_order_qty = Column(Integer, nullable=False)
    max_price = Column(Numeric(20, 2), nullable=False)
    multiplier = Column(Numeric(20, 8), nullable=False)
    
    # Margin and risk parameters
    initial_margin = Column(Numeric(10, 6), nullable=False)
    maintain_margin = Column(Numeric(10, 6), nullable=False)
    max_leverage = Column(Integer, nullable=False)
    max_risk_limit = Column(Integer, nullable=False)
    min_risk_limit = Column(Integer, nullable=False)
    risk_step = Column(Integer, nullable=False)
    
    # Fee structure
    maker_fee_rate = Column(Numeric(10, 6), nullable=False)
    taker_fee_rate = Column(Numeric(10, 6), nullable=False)
    
    # Contract lifecycle
    first_open_date = Column(DateTime(timezone=True))
    expire_date = Column(DateTime(timezone=True))
    settle_date = Column(DateTime(timezone=True))
    
    # Trading status and classification
    status = Column(String(20), nullable=False, default='Active', index=True)
    is_inverse = Column(Boolean, nullable=False, default=False)
    is_quanto = Column(Boolean, nullable=False, default=False)
    support_cross = Column(Boolean, nullable=False, default=True)
    
    # Management metadata
    is_eligible_for_management = Column(Boolean, nullable=False, default=True, index=True)
    sector_category = Column(String(50), index=True)
    market_cap_category = Column(String(20))
    volatility_classification = Column(String(20))
    liquidity_tier = Column(String(20))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    portfolio_entries = relationship("PortfolioComposition", back_populates="symbol")
    scores = relationship("SymbolScore", back_populates="symbol")
    signals = relationship("Signal", back_populates="symbol")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert symbol to dictionary representation"""
        return {
            'id': str(self.id),
            'symbol': self.symbol,
            'root_symbol': self.root_symbol,
            'base_currency': self.base_currency,
            'quote_currency': self.quote_currency,
            'settle_currency': self.settle_currency,
            'contract_type': self.contract_type,
            'lot_size': float(self.lot_size),
            'tick_size': float(self.tick_size),
            'max_order_qty': self.max_order_qty,
            'max_price': float(self.max_price),
            'multiplier': float(self.multiplier),
            'initial_margin': float(self.initial_margin),
            'maintain_margin': float(self.maintain_margin),
            'max_leverage': self.max_leverage,
            'status': self.status,
            'is_eligible_for_management': self.is_eligible_for_management,
            'sector_category': self.sector_category,
            'market_cap_category': self.market_cap_category,
            'volatility_classification': self.volatility_classification,
            'liquidity_tier': self.liquidity_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ScoringAlgorithm(db.Model):
    """Configuration and metadata for scoring algorithms"""
    __tablename__ = 'scoring_algorithms'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    algorithm_name = Column(String(100), nullable=False, index=True)
    algorithm_version = Column(String(20), nullable=False)
    algorithm_type = Column(String(50), nullable=False)  # 'TECHNICAL', 'FUNDAMENTAL', 'MARKET_STRUCTURE', 'COMPOSITE'
    
    # Algorithm configuration
    parameters = Column(Text, nullable=False)  # JSON string for SQLite compatibility
    weight_in_composite = Column(Numeric(5, 4), default=1.0)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Performance metadata
    historical_accuracy = Column(Numeric(5, 4))
    last_calibration_date = Column(DateTime(timezone=True))
    calibration_period_days = Column(Integer, default=30)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))
    
    # Relationships
    scores = relationship("SymbolScore", back_populates="algorithm")
    
    __table_args__ = (UniqueConstraint('algorithm_name', 'algorithm_version'),)
    
    @hybrid_property
    def parameters_dict(self) -> Dict[str, Any]:
        """Get parameters as dictionary"""
        try:
            return json.loads(self.parameters) if self.parameters else {}
        except json.JSONDecodeError:
            return {}
    
    @parameters_dict.setter
    def parameters_dict(self, value: Dict[str, Any]):
        """Set parameters from dictionary"""
        self.parameters = json.dumps(value) if value else '{}'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert algorithm to dictionary representation"""
        return {
            'id': str(self.id),
            'algorithm_name': self.algorithm_name,
            'algorithm_version': self.algorithm_version,
            'algorithm_type': self.algorithm_type,
            'parameters': self.parameters_dict,
            'weight_in_composite': float(self.weight_in_composite),
            'is_active': self.is_active,
            'historical_accuracy': float(self.historical_accuracy) if self.historical_accuracy else None,
            'last_calibration_date': self.last_calibration_date.isoformat() if self.last_calibration_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PortfolioComposition(db.Model):
    """Current portfolio composition tracking exactly 10 managed symbols"""
    __tablename__ = 'portfolio_composition'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol_id = Column(UUID(as_uuid=True), ForeignKey('symbols.id'), nullable=False, unique=True, index=True)
    position_rank = Column(Integer, nullable=False, unique=True, index=True)
    inclusion_date = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    inclusion_reason = Column(Text)
    current_score = Column(Numeric(10, 4))
    weight_percentage = Column(Numeric(5, 2))
    
    # Management status
    status = Column(String(20), nullable=False, default='Active', index=True)
    is_replacement_candidate = Column(Boolean, nullable=False, default=False, index=True)
    replacement_priority = Column(Integer)
    
    # Performance tracking
    performance_since_inclusion = Column(Numeric(10, 4))
    max_drawdown_since_inclusion = Column(Numeric(10, 4))
    volatility_since_inclusion = Column(Numeric(10, 4))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    symbol = relationship("Symbol", back_populates="portfolio_entries")
    
    __table_args__ = (
        db.CheckConstraint('position_rank >= 1 AND position_rank <= 10', name='check_position_rank'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio entry to dictionary representation"""
        return {
            'id': str(self.id),
            'symbol_id': str(self.symbol_id),
            'symbol': self.symbol.symbol if self.symbol else None,
            'position_rank': self.position_rank,
            'inclusion_date': self.inclusion_date.isoformat() if self.inclusion_date else None,
            'inclusion_reason': self.inclusion_reason,
            'current_score': float(self.current_score) if self.current_score else None,
            'weight_percentage': float(self.weight_percentage) if self.weight_percentage else None,
            'status': self.status,
            'is_replacement_candidate': self.is_replacement_candidate,
            'replacement_priority': self.replacement_priority,
            'performance_since_inclusion': float(self.performance_since_inclusion) if self.performance_since_inclusion else None,
            'max_drawdown_since_inclusion': float(self.max_drawdown_since_inclusion) if self.max_drawdown_since_inclusion else None,
            'volatility_since_inclusion': float(self.volatility_since_inclusion) if self.volatility_since_inclusion else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PortfolioHistory(db.Model):
    """Complete audit trail of all portfolio changes"""
    __tablename__ = 'portfolio_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol_id = Column(UUID(as_uuid=True), ForeignKey('symbols.id'), nullable=False, index=True)
    action_type = Column(String(20), nullable=False, index=True)  # 'ADD', 'REMOVE', 'REPLACE'
    position_rank = Column(Integer)
    
    # Change context
    trigger_reason = Column(String(100), nullable=False)
    trigger_score = Column(Numeric(10, 4))
    decision_confidence = Column(Numeric(5, 4))
    
    # Replacement details (if applicable)
    replaced_symbol_id = Column(UUID(as_uuid=True), ForeignKey('symbols.id'))
    replacement_score_difference = Column(Numeric(10, 4))
    
    # Performance impact
    expected_performance_impact = Column(Numeric(10, 4))
    actual_performance_impact = Column(Numeric(10, 4))
    
    # Decision metadata
    decision_algorithm_version = Column(String(20))
    agent_consensus_level = Column(Numeric(5, 4))
    manual_override = Column(Boolean, nullable=False, default=False)
    override_reason = Column(Text)
    
    # Audit fields
    action_timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now, index=True)
    action_by = Column(String(100), nullable=False)
    
    # Relationships
    symbol = relationship("Symbol", foreign_keys=[symbol_id])
    replaced_symbol = relationship("Symbol", foreign_keys=[replaced_symbol_id])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio history entry to dictionary representation"""
        return {
            'id': str(self.id),
            'symbol_id': str(self.symbol_id),
            'symbol': self.symbol.symbol if self.symbol else None,
            'action_type': self.action_type,
            'position_rank': self.position_rank,
            'trigger_reason': self.trigger_reason,
            'trigger_score': float(self.trigger_score) if self.trigger_score else None,
            'decision_confidence': float(self.decision_confidence) if self.decision_confidence else None,
            'replaced_symbol_id': str(self.replaced_symbol_id) if self.replaced_symbol_id else None,
            'replaced_symbol': self.replaced_symbol.symbol if self.replaced_symbol else None,
            'replacement_score_difference': float(self.replacement_score_difference) if self.replacement_score_difference else None,
            'expected_performance_impact': float(self.expected_performance_impact) if self.expected_performance_impact else None,
            'actual_performance_impact': float(self.actual_performance_impact) if self.actual_performance_impact else None,
            'decision_algorithm_version': self.decision_algorithm_version,
            'agent_consensus_level': float(self.agent_consensus_level) if self.agent_consensus_level else None,
            'manual_override': self.manual_override,
            'override_reason': self.override_reason,
            'action_timestamp': self.action_timestamp.isoformat() if self.action_timestamp else None,
            'action_by': self.action_by
        }

class SymbolScore(db.Model):
    """Current and historical scores for all symbols"""
    __tablename__ = 'symbol_scores'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol_id = Column(UUID(as_uuid=True), ForeignKey('symbols.id'), nullable=False, index=True)
    algorithm_id = Column(UUID(as_uuid=True), ForeignKey('scoring_algorithms.id'), nullable=False, index=True)
    
    # Score data
    score_value = Column(Numeric(10, 4), nullable=False, index=True)
    confidence_level = Column(Numeric(5, 4), nullable=False)
    score_rank = Column(Integer)
    
    # Score components (for composite scores)
    technical_component = Column(Numeric(10, 4))
    fundamental_component = Column(Numeric(10, 4))
    market_structure_component = Column(Numeric(10, 4))
    risk_component = Column(Numeric(10, 4))
    
    # Calculation metadata
    calculation_timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now, index=True)
    data_freshness_score = Column(Numeric(5, 4))
    calculation_duration_ms = Column(Integer)
    
    # Supporting data references
    input_data_hash = Column(String(64))
    supporting_data = Column(Text)  # JSON string for SQLite compatibility
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    
    # Relationships
    symbol = relationship("Symbol", back_populates="scores")
    algorithm = relationship("ScoringAlgorithm", back_populates="scores")
    
    @hybrid_property
    def supporting_data_dict(self) -> Dict[str, Any]:
        """Get supporting data as dictionary"""
        try:
            return json.loads(self.supporting_data) if self.supporting_data else {}
        except json.JSONDecodeError:
            return {}
    
    @supporting_data_dict.setter
    def supporting_data_dict(self, value: Dict[str, Any]):
        """Set supporting data from dictionary"""
        self.supporting_data = json.dumps(value) if value else '{}'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert score to dictionary representation"""
        return {
            'id': str(self.id),
            'symbol_id': str(self.symbol_id),
            'symbol': self.symbol.symbol if self.symbol else None,
            'algorithm_id': str(self.algorithm_id),
            'algorithm_name': self.algorithm.algorithm_name if self.algorithm else None,
            'score_value': float(self.score_value),
            'confidence_level': float(self.confidence_level),
            'score_rank': self.score_rank,
            'technical_component': float(self.technical_component) if self.technical_component else None,
            'fundamental_component': float(self.fundamental_component) if self.fundamental_component else None,
            'market_structure_component': float(self.market_structure_component) if self.market_structure_component else None,
            'risk_component': float(self.risk_component) if self.risk_component else None,
            'calculation_timestamp': self.calculation_timestamp.isoformat() if self.calculation_timestamp else None,
            'data_freshness_score': float(self.data_freshness_score) if self.data_freshness_score else None,
            'calculation_duration_ms': self.calculation_duration_ms,
            'supporting_data': self.supporting_data_dict,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Signal(db.Model):
    """Incoming trading signals and opportunities"""
    __tablename__ = 'signals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_name = Column(String(100), nullable=False, index=True)
    symbol_id = Column(UUID(as_uuid=True), ForeignKey('symbols.id'), index=True)
    
    # Signal content
    signal_type = Column(String(50), nullable=False)
    signal_strength = Column(Numeric(5, 4), nullable=False)
    confidence_level = Column(Numeric(5, 4), nullable=False)
    signal_direction = Column(String(10))  # 'BUY', 'SELL', 'NEUTRAL'
    
    # Signal metadata
    signal_data = Column(Text)  # JSON string for SQLite compatibility
    expiry_timestamp = Column(DateTime(timezone=True))
    
    # Processing status
    processing_status = Column(String(20), nullable=False, default='PENDING', index=True)
    evaluation_score = Column(Numeric(10, 4))
    agent_consensus = Column(Numeric(5, 4))
    
    # Outcome tracking
    actual_outcome = Column(Numeric(10, 4))
    outcome_timestamp = Column(DateTime(timezone=True))
    
    # Audit fields
    signal_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    received_timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    processed_timestamp = Column(DateTime(timezone=True))
    
    # Relationships
    symbol = relationship("Symbol", back_populates="signals")
    
    @hybrid_property
    def signal_data_dict(self) -> Dict[str, Any]:
        """Get signal data as dictionary"""
        try:
            return json.loads(self.signal_data) if self.signal_data else {}
        except json.JSONDecodeError:
            return {}
    
    @signal_data_dict.setter
    def signal_data_dict(self, value: Dict[str, Any]):
        """Set signal data from dictionary"""
        self.signal_data = json.dumps(value) if value else '{}'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary representation"""
        return {
            'id': str(self.id),
            'source_name': self.source_name,
            'symbol_id': str(self.symbol_id) if self.symbol_id else None,
            'symbol': self.symbol.symbol if self.symbol else None,
            'signal_type': self.signal_type,
            'signal_strength': float(self.signal_strength),
            'confidence_level': float(self.confidence_level),
            'signal_direction': self.signal_direction,
            'signal_data': self.signal_data_dict,
            'expiry_timestamp': self.expiry_timestamp.isoformat() if self.expiry_timestamp else None,
            'processing_status': self.processing_status,
            'evaluation_score': float(self.evaluation_score) if self.evaluation_score else None,
            'agent_consensus': float(self.agent_consensus) if self.agent_consensus else None,
            'actual_outcome': float(self.actual_outcome) if self.actual_outcome else None,
            'outcome_timestamp': self.outcome_timestamp.isoformat() if self.outcome_timestamp else None,
            'signal_timestamp': self.signal_timestamp.isoformat() if self.signal_timestamp else None,
            'received_timestamp': self.received_timestamp.isoformat() if self.received_timestamp else None,
            'processed_timestamp': self.processed_timestamp.isoformat() if self.processed_timestamp else None
        }

class SystemConfiguration(db.Model):
    """Global system settings and configuration"""
    __tablename__ = 'system_configuration'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_key = Column(String(100), nullable=False, unique=True, index=True)
    config_value = Column(Text, nullable=False)  # JSON string for SQLite compatibility
    config_type = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Validation
    is_active = Column(Boolean, nullable=False, default=True)
    validation_schema = Column(Text)  # JSON string for SQLite compatibility
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now)
    updated_by = Column(String(100))
    
    @hybrid_property
    def config_value_parsed(self) -> Any:
        """Get config value parsed according to type"""
        try:
            if self.config_type == 'INTEGER':
                return int(self.config_value)
            elif self.config_type == 'DECIMAL':
                return float(self.config_value)
            elif self.config_type == 'BOOLEAN':
                return self.config_value.lower() in ('true', '1', 'yes')
            elif self.config_type == 'JSON':
                return json.loads(self.config_value)
            else:
                return self.config_value
        except (ValueError, json.JSONDecodeError):
            return self.config_value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation"""
        return {
            'id': str(self.id),
            'config_key': self.config_key,
            'config_value': self.config_value_parsed,
            'config_type': self.config_type,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }

