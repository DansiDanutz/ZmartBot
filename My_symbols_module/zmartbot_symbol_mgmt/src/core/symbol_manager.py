"""
Symbol Manager - Core orchestrator for symbol management operations
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
import uuid

from sqlalchemy import desc, asc
from sqlalchemy.orm import sessionmaker
from src.models.user import db
from src.models.symbol_models import (
    Symbol, PortfolioComposition, PortfolioHistory, 
    SymbolScore, ScoringAlgorithm, Signal, SystemConfiguration
)

logger = logging.getLogger(__name__)

class SymbolManager:
    """
    Main orchestrator for symbol management operations.
    Coordinates portfolio management, scoring, and replacement decisions.
    """
    
    def __init__(self):
        self.max_portfolio_size = 10
        self.replacement_candidates_count = 2
        self.min_consensus_score = Decimal('0.7')
        self._load_configuration()
    
    def _load_configuration(self):
        """Load system configuration from database"""
        try:
            from flask import current_app
            if current_app:
                configs = SystemConfiguration.query.filter_by(is_active=True).all()
                for config in configs:
                    if config.config_key == 'max_portfolio_symbols':
                        self.max_portfolio_size = config.config_value_parsed
                    elif config.config_key == 'replacement_candidates':
                        self.replacement_candidates_count = config.config_value_parsed
                    elif config.config_key == 'min_consensus_score':
                        self.min_consensus_score = Decimal(str(config.config_value_parsed))
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
    
    def get_current_portfolio(self) -> List[Dict[str, Any]]:
        """
        Get the current portfolio composition with symbol details and scores.
        
        Returns:
            List of portfolio entries with symbol and score information
        """
        try:
            portfolio_entries = (
                db.session.query(PortfolioComposition)
                .join(Symbol)
                .filter(PortfolioComposition.status == 'Active')
                .order_by(PortfolioComposition.position_rank)
                .all()
            )
            
            result = []
            for entry in portfolio_entries:
                entry_dict = entry.to_dict()
                
                # Add latest composite score
                latest_score = self._get_latest_composite_score(entry.symbol_id)
                entry_dict['latest_composite_score'] = latest_score
                
                # Add symbol details
                if entry.symbol:
                    entry_dict['symbol_details'] = entry.symbol.to_dict()
                
                result.append(entry_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting current portfolio: {e}")
            return []
    
    def get_replacement_candidates(self) -> List[Dict[str, Any]]:
        """
        Get symbols that are candidates for replacement (lowest scoring symbols).
        
        Returns:
            List of replacement candidate entries
        """
        try:
            candidates = (
                db.session.query(PortfolioComposition)
                .join(Symbol)
                .filter(
                    PortfolioComposition.status == 'Active',
                    PortfolioComposition.is_replacement_candidate == True
                )
                .order_by(PortfolioComposition.current_score.asc())
                .limit(self.replacement_candidates_count)
                .all()
            )
            
            result = []
            for candidate in candidates:
                candidate_dict = candidate.to_dict()
                if candidate.symbol:
                    candidate_dict['symbol_details'] = candidate.symbol.to_dict()
                result.append(candidate_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting replacement candidates: {e}")
            return []
    
    def get_eligible_symbols(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get symbols eligible for management with their latest scores.
        
        Args:
            limit: Maximum number of symbols to return
            
        Returns:
            List of eligible symbols with scores
        """
        try:
            symbols = (
                db.session.query(Symbol)
                .filter(
                    Symbol.is_eligible_for_management == True,
                    Symbol.status == 'Active'
                )
                .order_by(Symbol.symbol)
                .limit(limit)
                .all()
            )
            
            result = []
            for symbol in symbols:
                symbol_dict = symbol.to_dict()
                
                # Add latest composite score
                latest_score = self._get_latest_composite_score(symbol.id)
                symbol_dict['latest_composite_score'] = latest_score
                
                # Check if already in portfolio
                in_portfolio = (
                    db.session.query(PortfolioComposition)
                    .filter(
                        PortfolioComposition.symbol_id == symbol.id,
                        PortfolioComposition.status == 'Active'
                    )
                    .first() is not None
                )
                symbol_dict['in_portfolio'] = in_portfolio
                
                result.append(symbol_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting eligible symbols: {e}")
            return []
    
    def add_symbol_to_portfolio(
        self, 
        symbol_id: str, 
        reason: str = "Manual addition",
        user: str = "system"
    ) -> Dict[str, Any]:
        """
        Add a symbol to the portfolio.
        
        Args:
            symbol_id: UUID of the symbol to add
            reason: Reason for addition
            user: User performing the action
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Validate symbol exists and is eligible
            symbol = Symbol.query.filter_by(
                id=uuid.UUID(symbol_id),
                is_eligible_for_management=True,
                status='Active'
            ).first()
            
            if not symbol:
                return {
                    'success': False,
                    'error': 'Symbol not found or not eligible for management'
                }
            
            # Check if symbol is already in portfolio
            existing_entry = PortfolioComposition.query.filter_by(
                symbol_id=symbol.id,
                status='Active'
            ).first()
            
            if existing_entry:
                return {
                    'success': False,
                    'error': 'Symbol is already in portfolio'
                }
            
            # Check portfolio size
            current_size = PortfolioComposition.query.filter_by(status='Active').count()
            if current_size >= self.max_portfolio_size:
                return {
                    'success': False,
                    'error': f'Portfolio is full (max {self.max_portfolio_size} symbols)'
                }
            
            # Find next available position rank
            occupied_ranks = [
                entry.position_rank for entry in 
                PortfolioComposition.query.filter_by(status='Active').all()
            ]
            next_rank = 1
            while next_rank in occupied_ranks and next_rank <= self.max_portfolio_size:
                next_rank += 1
            
            if next_rank > self.max_portfolio_size:
                return {
                    'success': False,
                    'error': 'No available position ranks'
                }
            
            # Get latest score for the symbol
            latest_score = self._get_latest_composite_score(symbol.id)
            
            # Create portfolio entry
            portfolio_entry = PortfolioComposition(
                symbol_id=symbol.id,
                position_rank=next_rank,
                inclusion_reason=reason,
                current_score=latest_score,
                weight_percentage=Decimal('10.0'),  # Equal weight initially
                status='Active'
            )
            
            db.session.add(portfolio_entry)
            
            # Create history entry
            history_entry = PortfolioHistory(
                symbol_id=symbol.id,
                action_type='ADD',
                position_rank=next_rank,
                trigger_reason=reason,
                trigger_score=latest_score,
                decision_confidence=Decimal('1.0'),  # Manual addition has full confidence
                manual_override=True,
                action_by=user
            )
            
            db.session.add(history_entry)
            db.session.commit()
            
            # Update replacement candidates
            self._update_replacement_candidates()
            
            logger.info(f"Added symbol {symbol.symbol} to portfolio at rank {next_rank}")
            
            return {
                'success': True,
                'portfolio_entry': portfolio_entry.to_dict(),
                'message': f'Symbol {symbol.symbol} added to portfolio successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding symbol to portfolio: {e}")
            return {
                'success': False,
                'error': f'Failed to add symbol: {str(e)}'
            }
    
    def remove_symbol_from_portfolio(
        self, 
        symbol_id: str, 
        reason: str = "Manual removal",
        user: str = "system"
    ) -> Dict[str, Any]:
        """
        Remove a symbol from the portfolio.
        
        Args:
            symbol_id: UUID of the symbol to remove
            reason: Reason for removal
            user: User performing the action
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Find portfolio entry
            portfolio_entry = PortfolioComposition.query.filter_by(
                symbol_id=uuid.UUID(symbol_id),
                status='Active'
            ).first()
            
            if not portfolio_entry:
                return {
                    'success': False,
                    'error': 'Symbol not found in portfolio'
                }
            
            # Update portfolio entry status
            portfolio_entry.status = 'Removed'
            
            # Create history entry
            history_entry = PortfolioHistory(
                symbol_id=portfolio_entry.symbol_id,
                action_type='REMOVE',
                position_rank=portfolio_entry.position_rank,
                trigger_reason=reason,
                trigger_score=portfolio_entry.current_score,
                decision_confidence=Decimal('1.0'),  # Manual removal has full confidence
                manual_override=True,
                action_by=user
            )
            
            db.session.add(history_entry)
            db.session.commit()
            
            # Update replacement candidates
            self._update_replacement_candidates()
            
            logger.info(f"Removed symbol {portfolio_entry.symbol.symbol} from portfolio")
            
            return {
                'success': True,
                'message': f'Symbol {portfolio_entry.symbol.symbol} removed from portfolio successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing symbol from portfolio: {e}")
            return {
                'success': False,
                'error': f'Failed to remove symbol: {str(e)}'
            }
    
    def replace_symbol(
        self, 
        old_symbol_id: str, 
        new_symbol_id: str, 
        reason: str = "Automatic replacement",
        user: str = "system"
    ) -> Dict[str, Any]:
        """
        Replace one symbol with another in the portfolio.
        
        Args:
            old_symbol_id: UUID of the symbol to replace
            new_symbol_id: UUID of the new symbol
            reason: Reason for replacement
            user: User performing the action
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Validate old symbol is in portfolio
            old_entry = PortfolioComposition.query.filter_by(
                symbol_id=uuid.UUID(old_symbol_id),
                status='Active'
            ).first()
            
            if not old_entry:
                return {
                    'success': False,
                    'error': 'Old symbol not found in portfolio'
                }
            
            # Validate new symbol exists and is eligible
            new_symbol = Symbol.query.filter_by(
                id=uuid.UUID(new_symbol_id),
                is_eligible_for_management=True,
                status='Active'
            ).first()
            
            if not new_symbol:
                return {
                    'success': False,
                    'error': 'New symbol not found or not eligible for management'
                }
            
            # Check if new symbol is already in portfolio
            existing_new_entry = PortfolioComposition.query.filter_by(
                symbol_id=new_symbol.id,
                status='Active'
            ).first()
            
            if existing_new_entry:
                return {
                    'success': False,
                    'error': 'New symbol is already in portfolio'
                }
            
            # Get scores for comparison
            old_score = old_entry.current_score or Decimal('0')
            new_score = self._get_latest_composite_score(new_symbol.id)
            score_difference = new_score - old_score if new_score and old_score else None
            
            # Update old entry status
            old_entry.status = 'Replaced'
            
            # Create new portfolio entry
            new_entry = PortfolioComposition(
                symbol_id=new_symbol.id,
                position_rank=old_entry.position_rank,
                inclusion_reason=f"Replacement for {old_entry.symbol.symbol}",
                current_score=new_score,
                weight_percentage=old_entry.weight_percentage,
                status='Active'
            )
            
            db.session.add(new_entry)
            
            # Create history entry
            history_entry = PortfolioHistory(
                symbol_id=new_symbol.id,
                action_type='REPLACE',
                position_rank=old_entry.position_rank,
                trigger_reason=reason,
                trigger_score=new_score,
                decision_confidence=Decimal('0.8'),  # Replacement has high confidence
                replaced_symbol_id=old_entry.symbol_id,
                replacement_score_difference=score_difference,
                action_by=user
            )
            
            db.session.add(history_entry)
            db.session.commit()
            
            # Update replacement candidates
            self._update_replacement_candidates()
            
            logger.info(f"Replaced symbol {old_entry.symbol.symbol} with {new_symbol.symbol}")
            
            return {
                'success': True,
                'old_symbol': old_entry.symbol.symbol,
                'new_symbol': new_symbol.symbol,
                'score_difference': float(score_difference) if score_difference else None,
                'message': f'Successfully replaced {old_entry.symbol.symbol} with {new_symbol.symbol}'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error replacing symbol: {e}")
            return {
                'success': False,
                'error': f'Failed to replace symbol: {str(e)}'
            }
    
    def get_portfolio_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive portfolio statistics and metrics.
        
        Returns:
            Dictionary with portfolio statistics
        """
        try:
            portfolio = self.get_current_portfolio()
            
            if not portfolio:
                return {
                    'total_symbols': 0,
                    'replacement_candidates': 0,
                    'average_score': None,
                    'score_range': None,
                    'sector_distribution': {},
                    'performance_metrics': {}
                }
            
            # Basic statistics
            total_symbols = len(portfolio)
            replacement_candidates = sum(1 for entry in portfolio if entry['is_replacement_candidate'])
            
            # Score statistics
            scores = [entry['latest_composite_score'] for entry in portfolio if entry['latest_composite_score']]
            avg_score = sum(scores) / len(scores) if scores else None
            score_range = (min(scores), max(scores)) if scores else None
            
            # Sector distribution
            sector_distribution = {}
            for entry in portfolio:
                if entry.get('symbol_details', {}).get('sector_category'):
                    sector = entry['symbol_details']['sector_category']
                    sector_distribution[sector] = sector_distribution.get(sector, 0) + 1
            
            # Performance metrics
            performance_metrics = {
                'avg_performance_since_inclusion': None,
                'avg_max_drawdown': None,
                'avg_volatility': None
            }
            
            performance_values = [entry['performance_since_inclusion'] for entry in portfolio if entry['performance_since_inclusion']]
            if performance_values:
                performance_metrics['avg_performance_since_inclusion'] = sum(performance_values) / len(performance_values)
            
            drawdown_values = [entry['max_drawdown_since_inclusion'] for entry in portfolio if entry['max_drawdown_since_inclusion']]
            if drawdown_values:
                performance_metrics['avg_max_drawdown'] = sum(drawdown_values) / len(drawdown_values)
            
            volatility_values = [entry['volatility_since_inclusion'] for entry in portfolio if entry['volatility_since_inclusion']]
            if volatility_values:
                performance_metrics['avg_volatility'] = sum(volatility_values) / len(volatility_values)
            
            return {
                'total_symbols': total_symbols,
                'max_portfolio_size': self.max_portfolio_size,
                'replacement_candidates': replacement_candidates,
                'average_score': avg_score,
                'score_range': score_range,
                'sector_distribution': sector_distribution,
                'performance_metrics': performance_metrics,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio statistics: {e}")
            return {'error': str(e)}
    
    def _get_latest_composite_score(self, symbol_id: uuid.UUID) -> Optional[Decimal]:
        """Get the latest composite score for a symbol"""
        try:
            # Get the composite algorithm
            composite_algorithm = ScoringAlgorithm.query.filter_by(
                algorithm_type='COMPOSITE',
                is_active=True
            ).first()
            
            if not composite_algorithm:
                return None
            
            # Get latest score
            latest_score = (
                SymbolScore.query
                .filter_by(symbol_id=symbol_id, algorithm_id=composite_algorithm.id)
                .order_by(desc(SymbolScore.calculation_timestamp))
                .first()
            )
            
            return latest_score.score_value if latest_score else None
            
        except Exception as e:
            logger.error(f"Error getting latest composite score: {e}")
            return None
    
    def _update_replacement_candidates(self):
        """Update which symbols are marked as replacement candidates"""
        try:
            # Reset all replacement candidate flags
            PortfolioComposition.query.filter_by(status='Active').update({
                'is_replacement_candidate': False,
                'replacement_priority': None
            })
            
            # Get portfolio entries sorted by score (ascending - lowest first)
            portfolio_entries = (
                PortfolioComposition.query
                .filter_by(status='Active')
                .order_by(PortfolioComposition.current_score.asc())
                .limit(self.replacement_candidates_count)
                .all()
            )
            
            # Mark lowest scoring symbols as replacement candidates
            for i, entry in enumerate(portfolio_entries):
                entry.is_replacement_candidate = True
                entry.replacement_priority = i + 1
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating replacement candidates: {e}")
            db.session.rollback()
    
    def get_portfolio_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get portfolio change history.
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of portfolio history entries
        """
        try:
            history_entries = (
                PortfolioHistory.query
                .order_by(desc(PortfolioHistory.action_timestamp))
                .limit(limit)
                .all()
            )
            
            return [entry.to_dict() for entry in history_entries]
            
        except Exception as e:
            logger.error(f"Error getting portfolio history: {e}")
            return []

