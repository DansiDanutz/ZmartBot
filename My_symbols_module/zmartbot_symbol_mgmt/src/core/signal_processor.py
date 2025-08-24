"""
Signal Processor - Handles trading signals and multi-agent evaluation
"""

import logging
import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import uuid
import random

from sqlalchemy import desc, asc
from src.models.user import db
from src.models.symbol_models import Signal, Symbol

logger = logging.getLogger(__name__)

class SignalProcessor:
    """
    Processes trading signals and coordinates multi-agent evaluation.
    """
    
    def __init__(self):
        self.min_signal_strength = Decimal('0.5')
        self.min_confidence = Decimal('0.6')
        self.signal_timeout_hours = 24
    
    def process_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming trading signal.
        
        Args:
            signal_data: Dictionary containing signal information
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Validate signal data
            validation_result = self._validate_signal_data(signal_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error']
                }
            
            # Create signal record
            signal = Signal(
                source_name=signal_data['source_name'],
                symbol_id=uuid.UUID(signal_data['symbol_id']) if signal_data.get('symbol_id') else None,
                signal_type=signal_data['signal_type'],
                signal_strength=Decimal(str(signal_data['signal_strength'])),
                confidence_level=Decimal(str(signal_data['confidence_level'])),
                signal_direction=signal_data.get('signal_direction'),
                signal_data=json.dumps(signal_data.get('signal_data', {})),
                expiry_timestamp=self._parse_expiry_timestamp(signal_data.get('expiry_timestamp')),
                signal_timestamp=self._parse_signal_timestamp(signal_data.get('signal_timestamp')),
                processing_status='PENDING'
            )
            
            db.session.add(signal)
            db.session.commit()
            
            # Start processing pipeline
            processing_result = self._start_signal_processing(signal)
            
            return {
                'success': True,
                'signal_id': str(signal.id),
                'processing_status': signal.processing_status,
                'processing_result': processing_result
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing signal: {e}")
            return {
                'success': False,
                'error': f'Failed to process signal: {str(e)}'
            }
    
    def _validate_signal_data(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate incoming signal data"""
        required_fields = ['source_name', 'signal_type', 'signal_strength', 'confidence_level']
        
        for field in required_fields:
            if field not in signal_data:
                return {
                    'valid': False,
                    'error': f'Missing required field: {field}'
                }
        
        # Validate signal strength
        try:
            strength = Decimal(str(signal_data['signal_strength']))
            if strength < 0 or strength > 1:
                return {
                    'valid': False,
                    'error': 'Signal strength must be between 0 and 1'
                }
        except (ValueError, TypeError):
            return {
                'valid': False,
                'error': 'Invalid signal strength format'
            }
        
        # Validate confidence level
        try:
            confidence = Decimal(str(signal_data['confidence_level']))
            if confidence < 0 or confidence > 1:
                return {
                    'valid': False,
                    'error': 'Confidence level must be between 0 and 1'
                }
        except (ValueError, TypeError):
            return {
                'valid': False,
                'error': 'Invalid confidence level format'
            }
        
        # Validate symbol if provided
        if signal_data.get('symbol_id'):
            try:
                symbol_id = uuid.UUID(signal_data['symbol_id'])
                symbol = Symbol.query.filter_by(id=symbol_id).first()
                if not symbol:
                    return {
                        'valid': False,
                        'error': 'Symbol not found'
                    }
            except ValueError:
                return {
                    'valid': False,
                    'error': 'Invalid symbol ID format'
                }
        
        return {'valid': True}
    
    def _parse_expiry_timestamp(self, expiry_str: Optional[str]) -> Optional[datetime]:
        """Parse expiry timestamp string"""
        if not expiry_str:
            # Default to 24 hours from now
            return datetime.now(timezone.utc) + timedelta(hours=self.signal_timeout_hours)
        
        try:
            return datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
        except ValueError:
            logger.warning(f"Invalid expiry timestamp format: {expiry_str}")
            return datetime.now(timezone.utc) + timedelta(hours=self.signal_timeout_hours)
    
    def _parse_signal_timestamp(self, signal_str: Optional[str]) -> datetime:
        """Parse signal timestamp string"""
        if not signal_str:
            return datetime.now(timezone.utc)
        
        try:
            return datetime.fromisoformat(signal_str.replace('Z', '+00:00'))
        except ValueError:
            logger.warning(f"Invalid signal timestamp format: {signal_str}")
            return datetime.now(timezone.utc)
    
    def _start_signal_processing(self, signal: Signal) -> Dict[str, Any]:
        """Start the signal processing pipeline"""
        try:
            # Update status
            signal.processing_status = 'PROCESSING'
            db.session.commit()
            
            # Simulate multi-agent evaluation
            evaluation_result = self._simulate_multi_agent_evaluation(signal)
            
            # Update signal with evaluation results
            signal.evaluation_score = evaluation_result['evaluation_score']
            signal.agent_consensus = evaluation_result['agent_consensus']
            signal.processing_status = 'COMPLETED'
            signal.processed_timestamp = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return evaluation_result
            
        except Exception as e:
            signal.processing_status = 'FAILED'
            db.session.commit()
            logger.error(f"Error in signal processing pipeline: {e}")
            return {
                'error': str(e),
                'evaluation_score': None,
                'agent_consensus': None
            }
    
    def _simulate_multi_agent_evaluation(self, signal: Signal) -> Dict[str, Any]:
        """Simulate multi-agent evaluation process"""
        # In production, this would coordinate actual agent evaluations
        
        # Simulate agent evaluations
        agents = ['technical_agent', 'fundamental_agent', 'risk_agent', 'market_structure_agent']
        agent_scores = {}
        agent_recommendations = {}
        
        for agent in agents:
            # Simulate agent evaluation
            score = random.uniform(0.3, 0.9)
            recommendation = random.choice(['APPROVE', 'REJECT', 'CONDITIONAL'])
            
            # Bias based on signal strength and confidence
            signal_quality = (float(signal.signal_strength) + float(signal.confidence_level)) / 2
            if signal_quality > 0.7:
                score = max(score, 0.6)  # Higher minimum for good signals
                if random.random() < 0.7:  # 70% chance of approval for good signals
                    recommendation = 'APPROVE'
            
            agent_scores[agent] = score
            agent_recommendations[agent] = recommendation
        
        # Calculate consensus
        avg_score = sum(agent_scores.values()) / len(agent_scores)
        approval_count = sum(1 for rec in agent_recommendations.values() if rec == 'APPROVE')
        consensus_level = approval_count / len(agents)
        
        # Determine final evaluation
        if consensus_level >= 0.75 and avg_score >= 0.7:
            final_evaluation = 'STRONG_APPROVE'
        elif consensus_level >= 0.5 and avg_score >= 0.6:
            final_evaluation = 'APPROVE'
        elif consensus_level >= 0.25 or avg_score >= 0.5:
            final_evaluation = 'CONDITIONAL'
        else:
            final_evaluation = 'REJECT'
        
        return {
            'evaluation_score': Decimal(str(round(avg_score, 4))),
            'agent_consensus': Decimal(str(round(consensus_level, 4))),
            'final_evaluation': final_evaluation,
            'agent_scores': agent_scores,
            'agent_recommendations': agent_recommendations,
            'evaluation_details': {
                'total_agents': len(agents),
                'approval_count': approval_count,
                'average_score': avg_score,
                'consensus_threshold_met': consensus_level >= 0.5
            }
        }
    
    def get_pending_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get pending signals awaiting processing"""
        try:
            signals = (
                Signal.query
                .filter_by(processing_status='PENDING')
                .order_by(Signal.signal_timestamp)
                .limit(limit)
                .all()
            )
            
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logger.error(f"Error getting pending signals: {e}")
            return []
    
    def get_processed_signals(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recently processed signals"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            signals = (
                Signal.query
                .filter(
                    Signal.processing_status.in_(['COMPLETED', 'FAILED']),
                    Signal.processed_timestamp >= cutoff_time
                )
                .order_by(desc(Signal.processed_timestamp))
                .limit(limit)
                .all()
            )
            
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logger.error(f"Error getting processed signals: {e}")
            return []
    
    def get_signal_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get signal processing statistics"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Total signals
            total_signals = Signal.query.filter(
                Signal.signal_timestamp >= cutoff_time
            ).count()
            
            # Status breakdown
            status_counts = {}
            for status in ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED']:
                count = Signal.query.filter(
                    Signal.processing_status == status,
                    Signal.signal_timestamp >= cutoff_time
                ).count()
                status_counts[status] = count
            
            # Source breakdown
            source_stats = (
                db.session.query(Signal.source_name, db.func.count(Signal.id))
                .filter(Signal.signal_timestamp >= cutoff_time)
                .group_by(Signal.source_name)
                .all()
            )
            
            source_counts = {source: count for source, count in source_stats}
            
            # Evaluation statistics
            completed_signals = Signal.query.filter(
                Signal.processing_status == 'COMPLETED',
                Signal.signal_timestamp >= cutoff_time,
                Signal.evaluation_score.isnot(None)
            ).all()
            
            evaluation_stats = {}
            if completed_signals:
                scores = [float(signal.evaluation_score) for signal in completed_signals]
                consensus_levels = [float(signal.agent_consensus) for signal in completed_signals if signal.agent_consensus]
                
                evaluation_stats = {
                    'average_score': sum(scores) / len(scores),
                    'min_score': min(scores),
                    'max_score': max(scores),
                    'average_consensus': sum(consensus_levels) / len(consensus_levels) if consensus_levels else 0,
                    'high_quality_signals': sum(1 for score in scores if score >= 0.7),
                    'approved_signals': sum(1 for score in scores if score >= 0.6)
                }
            
            return {
                'analysis_period_days': days,
                'total_signals': total_signals,
                'status_breakdown': status_counts,
                'source_breakdown': source_counts,
                'evaluation_statistics': evaluation_stats,
                'processing_rate': status_counts.get('COMPLETED', 0) / max(total_signals, 1),
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting signal statistics: {e}")
            return {'error': str(e)}
    
    def cleanup_expired_signals(self) -> Dict[str, Any]:
        """Clean up expired signals"""
        try:
            current_time = datetime.now(timezone.utc)
            
            # Find expired signals
            expired_signals = Signal.query.filter(
                Signal.expiry_timestamp < current_time,
                Signal.processing_status.in_(['PENDING', 'PROCESSING'])
            ).all()
            
            # Update status
            for signal in expired_signals:
                signal.processing_status = 'EXPIRED'
                signal.processed_timestamp = current_time
            
            db.session.commit()
            
            return {
                'success': True,
                'expired_signals_count': len(expired_signals),
                'cleanup_timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cleaning up expired signals: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def reprocess_failed_signals(self, max_retries: int = 3) -> Dict[str, Any]:
        """Reprocess failed signals"""
        try:
            # Find failed signals that haven't exceeded retry limit
            failed_signals = Signal.query.filter(
                Signal.processing_status == 'FAILED'
            ).limit(10).all()  # Limit to prevent overwhelming
            
            reprocessed_count = 0
            errors = []
            
            for signal in failed_signals:
                try:
                    # Reset status and reprocess
                    signal.processing_status = 'PENDING'
                    signal.processed_timestamp = None
                    
                    processing_result = self._start_signal_processing(signal)
                    
                    if 'error' not in processing_result:
                        reprocessed_count += 1
                    else:
                        errors.append(f"Signal {signal.id}: {processing_result['error']}")
                        
                except Exception as e:
                    errors.append(f"Signal {signal.id}: {str(e)}")
            
            db.session.commit()
            
            return {
                'success': True,
                'reprocessed_count': reprocessed_count,
                'total_failed_signals': len(failed_signals),
                'errors': errors,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reprocessing failed signals: {e}")
            return {
                'success': False,
                'error': str(e)
            }

