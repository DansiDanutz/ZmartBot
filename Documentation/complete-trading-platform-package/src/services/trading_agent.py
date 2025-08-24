"""
Trade Strategy Module - Trading Agent Service
============================================

Advanced trading agent with CORRECTED profit calculation logic.
Makes intelligent trading decisions based on signal analysis and position management.

Author: Manus AI
Version: 1.0 Professional Edition - CORRECTED PROFIT CALCULATIONS
Compatibility: Mac Mini 2025 M2 Pro Integration
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from redis import Redis

from ..core.config import settings, config_manager
from ..models.base import BaseRepository
from ..models.positions import (
    Position, PositionScale, PositionCreate, PositionUpdate,
    PositionStatus, ScaleStage
)
from ..models.signals import ProcessedSignal, SignalQuality
from ..models.vaults import Vault, VaultStatus
from .signal_center import SignalCenterService
from .position_scaler import PositionScaler, ScalingDecision, ProfitTakeStage
from .vault_manager import VaultManagerService


class TradingDecision(str, Enum):
    """Trading decision types."""
    OPEN_POSITION = "open_position"
    SCALE_POSITION = "scale_position"
    TAKE_PROFIT = "take_profit"
    CLOSE_POSITION = "close_position"
    HOLD = "hold"
    REJECT = "reject"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class TradingRecommendation:
    """Trading recommendation with corrected profit calculations."""
    decision: TradingDecision
    symbol: str
    direction: str
    confidence: Decimal
    risk_level: RiskLevel
    
    # Position sizing (CORRECTED)
    recommended_investment: Decimal
    leverage: Decimal
    position_value: Decimal
    
    # Profit calculations (CORRECTED - based on total invested)
    total_invested_if_executed: Decimal  # Total invested after this action
    profit_threshold_75pct: Decimal      # 75% of total invested
    take_profit_trigger: Decimal         # total_invested + profit_threshold
    
    # Risk metrics
    liquidation_price: Decimal
    max_loss: Decimal
    risk_reward_ratio: Decimal
    
    # Metadata
    signal_scores: List[Decimal]
    reasoning: str
    vault_id: str
    created_at: datetime


class TradingAgent:
    """
    Advanced trading agent with CORRECTED profit calculation logic.
    
    Key Correction: All profit calculations are based on TOTAL INVESTED AMOUNT
    across all scaling stages, not just the initial investment.
    
    Example:
    - Initial: 100 USDT → Total invested: 100 USDT, Profit target: 75 USDT
    - After scaling: 1500 USDT → Total invested: 1500 USDT, Profit target: 1125 USDT
    """
    
    def __init__(self, session: Session, redis_client: Redis):
        self.session = session
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.signal_center = SignalCenterService(session, redis_client)
        self.position_scaler = PositionScaler(session, redis_client)
        self.vault_manager = VaultManagerService(session, redis_client)
        
        # Initialize repositories
        self.position_repo = BaseRepository(Position, session)
        self.signal_repo = BaseRepository(ProcessedSignal, session)
        self.vault_repo = BaseRepository(Vault, session)
        
        # Trading configuration
        self.min_signal_confidence = Decimal('0.65')
        self.min_consensus_signals = 3
        self.max_positions_per_vault = 2
        
        # CORRECTED: Profit thresholds based on total invested
        self.profit_threshold_pct = Decimal('0.75')  # 75% of TOTAL invested
        self.min_profit_threshold = Decimal('0.75')  # Minimum 75% profit required
        
        # Risk management
        self.max_risk_per_trade = Decimal('0.05')    # 5% of vault per trade
        self.liquidation_buffer = Decimal('0.10')    # 10% buffer from liquidation
        self.correlation_threshold = Decimal('0.70')  # Max correlation between positions
    
    async def analyze_trading_opportunity(
        self,
        symbol: str,
        timeframe: str = "1h"
    ) -> Optional[TradingRecommendation]:
        """
        Analyze trading opportunity with CORRECTED profit calculations.
        """
        
        try:
            # Get signal consensus for symbol
            consensus = await self.signal_center.get_signal_consensus(symbol, timeframe)
            
            if not consensus or len(consensus.get('signals', [])) < self.min_consensus_signals:
                return None
            
            # Check if we have available vaults
            available_vaults = await self.vault_manager.get_available_vaults()
            if not available_vaults:
                self.logger.warning("No available vaults for trading")
                return None
            
            # Select best vault for this trade
            selected_vault = await self._select_optimal_vault(available_vaults, symbol)
            if not selected_vault:
                return None
            
            # Analyze signals and determine direction
            signal_analysis = self._analyze_signal_quality(consensus)
            if signal_analysis['confidence'] < self.min_signal_confidence:
                return None
            
            # Check for existing positions in this symbol
            existing_position = await self._get_existing_position(selected_vault.id, symbol)
            
            if existing_position:
                # Evaluate scaling opportunity
                return await self._evaluate_scaling_opportunity(
                    existing_position, consensus, selected_vault
                )
            else:
                # Evaluate new position opportunity
                return await self._evaluate_new_position_opportunity(
                    symbol, signal_analysis, selected_vault, consensus
                )
                
        except Exception as e:
            self.logger.error(f"Error analyzing trading opportunity for {symbol}: {str(e)}")
            return None
    
    async def _evaluate_new_position_opportunity(
        self,
        symbol: str,
        signal_analysis: Dict[str, Any],
        vault: Vault,
        consensus: Dict[str, Any]
    ) -> Optional[TradingRecommendation]:
        """Evaluate opportunity for opening new position with CORRECTED calculations."""
        
        try:
            # Calculate position sizing
            vault_bankroll = vault.current_balance
            investment_amount = vault_bankroll * Decimal('0.01')  # 1% initial investment
            leverage = Decimal('20.0')  # Initial 20X leverage
            position_value = investment_amount * leverage
            
            # CORRECTED: Profit calculations for new position
            total_invested_if_executed = investment_amount  # Just this investment for new position
            profit_threshold_75pct = total_invested_if_executed * self.profit_threshold_pct
            take_profit_trigger = total_invested_if_executed + profit_threshold_75pct
            
            # Risk calculations
            entry_price = Decimal(str(consensus.get('average_price', 0)))
            direction = signal_analysis['direction']
            
            # Calculate liquidation price for 20X leverage
            if direction == "long":
                liquidation_price = entry_price * (Decimal('1') - Decimal('1') / leverage)
            else:
                liquidation_price = entry_price * (Decimal('1') + Decimal('1') / leverage)
            
            max_loss = investment_amount  # Maximum loss is the investment
            potential_profit = profit_threshold_75pct
            risk_reward_ratio = potential_profit / max_loss if max_loss > 0 else Decimal('0')
            
            # Risk assessment
            risk_level = self._assess_risk_level(
                signal_analysis['confidence'],
                risk_reward_ratio,
                vault_bankroll,
                investment_amount
            )
            
            return TradingRecommendation(
                decision=TradingDecision.OPEN_POSITION,
                symbol=symbol,
                direction=direction,
                confidence=signal_analysis['confidence'],
                risk_level=risk_level,
                recommended_investment=investment_amount,
                leverage=leverage,
                position_value=position_value,
                total_invested_if_executed=total_invested_if_executed,
                profit_threshold_75pct=profit_threshold_75pct,
                take_profit_trigger=take_profit_trigger,
                liquidation_price=liquidation_price,
                max_loss=max_loss,
                risk_reward_ratio=risk_reward_ratio,
                signal_scores=[Decimal(str(s.get('strength', 0))) for s in consensus.get('signals', [])],
                reasoning=f"New position opportunity: {signal_analysis['reasoning']}",
                vault_id=str(vault.id),
                created_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating new position opportunity: {str(e)}")
            return None
    
    async def _evaluate_scaling_opportunity(
        self,
        position: Position,
        consensus: Dict[str, Any],
        vault: Vault
    ) -> Optional[TradingRecommendation]:
        """Evaluate position scaling opportunity with CORRECTED calculations."""
        
        try:
            current_price = Decimal(str(consensus.get('average_price', 0)))
            current_signal_score = Decimal(str(consensus.get('consensus_strength', 0)))
            
            # Check if position should be scaled
            scaling_decision = await self.position_scaler.evaluate_scaling_opportunity(
                position, current_price, current_signal_score, vault.current_balance
            )
            
            if not scaling_decision.should_scale:
                # Check for profit taking opportunity
                return await self._evaluate_profit_taking_opportunity(
                    position, current_price, vault
                )
            
            # Calculate scaling investment
            stage = scaling_decision.recommended_stage
            stage_configs = self.position_scaler.scaling_stages
            
            if stage > len(stage_configs):
                return None
            
            stage_config = stage_configs[stage - 1]
            investment_amount = vault.current_balance * stage_config.bankroll_percentage
            leverage = stage_config.leverage
            position_value = investment_amount * leverage
            
            # CORRECTED: Calculate total invested after this scaling
            current_scales = self.session.query(PositionScale).filter(
                PositionScale.position_id == position.id
            ).all()
            
            current_total_invested = sum(scale.investment_amount for scale in current_scales)
            total_invested_if_executed = current_total_invested + investment_amount
            
            # CORRECTED: Profit calculations based on total invested after scaling
            profit_threshold_75pct = total_invested_if_executed * self.profit_threshold_pct
            take_profit_trigger = total_invested_if_executed + profit_threshold_75pct
            
            # Risk calculations
            max_loss = total_invested_if_executed
            potential_profit = profit_threshold_75pct
            risk_reward_ratio = potential_profit / max_loss if max_loss > 0 else Decimal('0')
            
            return TradingRecommendation(
                decision=TradingDecision.SCALE_POSITION,
                symbol=position.symbol,
                direction=position.direction,
                confidence=scaling_decision.confidence_score,
                risk_level=self._assess_scaling_risk_level(scaling_decision),
                recommended_investment=investment_amount,
                leverage=leverage,
                position_value=position_value,
                total_invested_if_executed=total_invested_if_executed,
                profit_threshold_75pct=profit_threshold_75pct,
                take_profit_trigger=take_profit_trigger,
                liquidation_price=scaling_decision.calculation.liquidation_price if scaling_decision.calculation else Decimal('0'),
                max_loss=max_loss,
                risk_reward_ratio=risk_reward_ratio,
                signal_scores=[current_signal_score],
                reasoning=f"Scaling opportunity: {scaling_decision.risk_assessment}",
                vault_id=str(vault.id),
                created_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating scaling opportunity: {str(e)}")
            return None
    
    async def _evaluate_profit_taking_opportunity(
        self,
        position: Position,
        current_price: Decimal,
        vault: Vault
    ) -> Optional[TradingRecommendation]:
        """Evaluate profit taking opportunity with CORRECTED calculations."""
        
        try:
            # Check profit taking triggers
            triggers = await self.position_scaler.check_profit_taking_triggers(
                position, current_price, vault.current_balance
            )
            
            if triggers.get("error"):
                return None
            
            # Determine profit taking stage
            profit_stage = None
            take_amount = Decimal('0')
            
            if triggers.get("first_take_profit"):
                profit_stage = ProfitTakeStage.FIRST_TAKE
                take_amount = triggers.get("take_amount", Decimal('0'))
            elif triggers.get("trailing_stop_1"):
                profit_stage = ProfitTakeStage.SECOND_TAKE
                take_amount = triggers.get("take_amount", Decimal('0'))
            elif triggers.get("final_take"):
                profit_stage = ProfitTakeStage.FINAL_TAKE
                take_amount = triggers.get("take_amount", Decimal('0'))
            
            if not profit_stage:
                return None
            
            # Calculate profit metrics
            profit_amount = triggers.get("profit_amount", Decimal('0'))
            profit_percentage = triggers.get("profit_percentage", Decimal('0'))
            
            # Get current total invested (CORRECTED)
            current_scales = self.session.query(PositionScale).filter(
                PositionScale.position_id == position.id
            ).all()
            total_invested = sum(scale.investment_amount for scale in current_scales)
            
            return TradingRecommendation(
                decision=TradingDecision.TAKE_PROFIT,
                symbol=position.symbol,
                direction=position.direction,
                confidence=Decimal('0.95'),  # High confidence for profit taking
                risk_level=RiskLevel.LOW,
                recommended_investment=Decimal('0'),  # No new investment
                leverage=Decimal('1'),
                position_value=take_amount,
                total_invested_if_executed=total_invested,  # No change in invested amount
                profit_threshold_75pct=total_invested * self.profit_threshold_pct,
                take_profit_trigger=triggers.get("profit_threshold", Decimal('0')),
                liquidation_price=position.liquidation_price or Decimal('0'),
                max_loss=Decimal('0'),  # No loss when taking profit
                risk_reward_ratio=Decimal('999'),  # Very high when taking profit
                signal_scores=[],
                reasoning=f"Profit taking: {profit_stage.value} - {profit_percentage:.2f}% profit",
                vault_id=str(vault.id),
                created_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating profit taking opportunity: {str(e)}")
            return None
    
    async def execute_trading_recommendation(
        self,
        recommendation: TradingRecommendation
    ) -> Tuple[bool, str, Optional[Position]]:
        """Execute trading recommendation with proper error handling."""
        
        try:
            if recommendation.decision == TradingDecision.OPEN_POSITION:
                return await self._execute_new_position(recommendation)
            
            elif recommendation.decision == TradingDecision.SCALE_POSITION:
                return await self._execute_position_scaling(recommendation)
            
            elif recommendation.decision == TradingDecision.TAKE_PROFIT:
                return await self._execute_profit_taking(recommendation)
            
            elif recommendation.decision == TradingDecision.CLOSE_POSITION:
                return await self._execute_position_closure(recommendation)
            
            else:
                return False, f"Unsupported decision: {recommendation.decision}", None
                
        except Exception as e:
            self.logger.error(f"Error executing trading recommendation: {str(e)}")
            return False, str(e), None
    
    async def _execute_new_position(
        self,
        recommendation: TradingRecommendation
    ) -> Tuple[bool, str, Optional[Position]]:
        """Execute new position opening."""
        
        try:
            # Create position
            position_data = PositionCreate(
                vault_id=recommendation.vault_id,
                symbol=recommendation.symbol,
                direction=recommendation.direction,
                average_entry_price=recommendation.liquidation_price,  # Will be updated
                total_investment=recommendation.recommended_investment,
                total_position_size=recommendation.position_value,
                current_stage=1,
                initial_signal_score=recommendation.confidence,
                liquidation_price=recommendation.liquidation_price,
                status=PositionStatus.OPEN.value,
                position_metadata={
                    "signal_scores": [float(s) for s in recommendation.signal_scores],
                    "reasoning": recommendation.reasoning,
                    "risk_level": recommendation.risk_level.value,
                    "total_invested_projected": float(recommendation.total_invested_if_executed),
                    "profit_threshold_75pct": float(recommendation.profit_threshold_75pct),
                    "take_profit_trigger": float(recommendation.take_profit_trigger)
                }
            )
            
            new_position = self.position_repo.create(position_data)
            
            # Create initial scaling stage
            from ..models.positions import PositionScaleCreate
            scale_data = PositionScaleCreate(
                position_id=new_position.id,
                stage=1,
                investment_amount=recommendation.recommended_investment,
                leverage=recommendation.leverage,
                entry_price=recommendation.liquidation_price,  # Will be updated with actual entry
                signal_score=recommendation.confidence,
                trigger_reason="initial_entry"
            )
            
            self.position_scaler.scale_repo.create(scale_data)
            
            # Update vault balance
            vault = self.vault_repo.get(recommendation.vault_id)
            vault.current_balance -= recommendation.recommended_investment
            vault.positions_count += 1
            self.session.commit()
            
            self.logger.info(
                f"New position opened: {recommendation.symbol} {recommendation.direction} "
                f"with {recommendation.recommended_investment} USDT"
            )
            
            return True, "Position opened successfully", new_position
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error executing new position: {str(e)}")
            return False, str(e), None
    
    async def _execute_position_scaling(
        self,
        recommendation: TradingRecommendation
    ) -> Tuple[bool, str, Optional[Position]]:
        """Execute position scaling."""
        
        try:
            # Find the position to scale
            position = self.session.query(Position).filter(
                and_(
                    Position.vault_id == recommendation.vault_id,
                    Position.symbol == recommendation.symbol,
                    Position.status == PositionStatus.OPEN.value
                )
            ).first()
            
            if not position:
                return False, "Position not found for scaling", None
            
            # Create scaling decision
            from .position_scaler import ScalingDecision, ScalingTrigger
            scaling_decision = ScalingDecision(
                should_scale=True,
                trigger_reason=ScalingTrigger.BETTER_SCORE,  # Default
                recommended_stage=position.current_stage + 1,
                confidence_score=recommendation.confidence,
                risk_assessment=recommendation.reasoning,
                calculation=None
            )
            
            # Execute scaling
            success, message, new_scale = await self.position_scaler.execute_position_scaling(
                position,
                scaling_decision,
                recommendation.liquidation_price,  # Current price
                Decimal(str(recommendation.vault_id)),  # Vault bankroll
                recommendation.confidence
            )
            
            if success:
                # Update vault balance
                vault = self.vault_repo.get(recommendation.vault_id)
                vault.current_balance -= recommendation.recommended_investment
                self.session.commit()
                
                self.logger.info(
                    f"Position scaled: {recommendation.symbol} stage {scaling_decision.recommended_stage} "
                    f"with {recommendation.recommended_investment} USDT"
                )
            
            return success, message, position
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error executing position scaling: {str(e)}")
            return False, str(e), None
    
    async def _execute_profit_taking(
        self,
        recommendation: TradingRecommendation
    ) -> Tuple[bool, str, Optional[Position]]:
        """Execute profit taking."""
        
        try:
            # Find the position
            position = self.session.query(Position).filter(
                and_(
                    Position.vault_id == recommendation.vault_id,
                    Position.symbol == recommendation.symbol,
                    Position.status == PositionStatus.OPEN.value
                )
            ).first()
            
            if not position:
                return False, "Position not found for profit taking", None
            
            # Determine profit stage from reasoning
            if "first_take" in recommendation.reasoning.lower():
                profit_stage = ProfitTakeStage.FIRST_TAKE
            elif "second_take" in recommendation.reasoning.lower():
                profit_stage = ProfitTakeStage.SECOND_TAKE
            else:
                profit_stage = ProfitTakeStage.FINAL_TAKE
            
            # Execute profit taking
            success, message, profit_realized = await self.position_scaler.execute_profit_taking(
                position,
                profit_stage,
                recommendation.liquidation_price,  # Current price
                recommendation.position_value  # Take amount
            )
            
            if success:
                # Update vault balance with profit
                vault = self.vault_repo.get(recommendation.vault_id)
                vault.current_balance += profit_realized
                
                # If position is closed, update vault positions count
                if profit_stage == ProfitTakeStage.FINAL_TAKE:
                    vault.positions_count -= 1
                
                self.session.commit()
                
                self.logger.info(
                    f"Profit taken: {recommendation.symbol} {profit_stage.value} "
                    f"realized {profit_realized} USDT"
                )
            
            return success, message, position
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error executing profit taking: {str(e)}")
            return False, str(e), None
    
    async def _execute_position_closure(
        self,
        recommendation: TradingRecommendation
    ) -> Tuple[bool, str, Optional[Position]]:
        """Execute position closure."""
        
        try:
            # Find and close position
            position = self.session.query(Position).filter(
                and_(
                    Position.vault_id == recommendation.vault_id,
                    Position.symbol == recommendation.symbol,
                    Position.status == PositionStatus.OPEN.value
                )
            ).first()
            
            if not position:
                return False, "Position not found for closure", None
            
            # Close position
            position.status = PositionStatus.CLOSED.value
            position.closed_at = datetime.now(timezone.utc)
            position.close_price = recommendation.liquidation_price
            
            # Update vault
            vault = self.vault_repo.get(recommendation.vault_id)
            vault.positions_count -= 1
            
            self.session.commit()
            
            self.logger.info(f"Position closed: {recommendation.symbol}")
            
            return True, "Position closed successfully", position
            
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error executing position closure: {str(e)}")
            return False, str(e), None
    
    def _analyze_signal_quality(self, consensus: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze signal quality and determine trading direction."""
        
        signals = consensus.get('signals', [])
        if not signals:
            return {'confidence': Decimal('0'), 'direction': 'hold', 'reasoning': 'No signals'}
        
        # Calculate signal metrics
        buy_signals = [s for s in signals if s.get('signal_type') == 'buy']
        sell_signals = [s for s in signals if s.get('signal_type') == 'sell']
        
        buy_strength = sum(s.get('strength', 0) for s in buy_signals)
        sell_strength = sum(s.get('strength', 0) for s in sell_signals)
        
        total_strength = buy_strength + sell_strength
        if total_strength == 0:
            return {'confidence': Decimal('0'), 'direction': 'hold', 'reasoning': 'No signal strength'}
        
        # Determine direction and confidence
        if buy_strength > sell_strength:
            direction = 'long'
            confidence = Decimal(str(buy_strength / total_strength))
            reasoning = f"Bullish consensus: {len(buy_signals)} buy vs {len(sell_signals)} sell signals"
        else:
            direction = 'short'
            confidence = Decimal(str(sell_strength / total_strength))
            reasoning = f"Bearish consensus: {len(sell_signals)} sell vs {len(buy_signals)} buy signals"
        
        return {
            'confidence': confidence,
            'direction': direction,
            'reasoning': reasoning,
            'signal_count': len(signals),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals)
        }
    
    def _assess_risk_level(
        self,
        confidence: Decimal,
        risk_reward_ratio: Decimal,
        vault_balance: Decimal,
        investment_amount: Decimal
    ) -> RiskLevel:
        """Assess risk level for trading decision."""
        
        # Risk factors
        confidence_risk = 1 - confidence  # Lower confidence = higher risk
        size_risk = investment_amount / vault_balance  # Larger position = higher risk
        reward_risk = 1 / (risk_reward_ratio + 1)  # Lower reward = higher risk
        
        # Combined risk score
        risk_score = (confidence_risk + size_risk + reward_risk) / 3
        
        if risk_score < 0.25:
            return RiskLevel.LOW
        elif risk_score < 0.50:
            return RiskLevel.MEDIUM
        elif risk_score < 0.75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.EXTREME
    
    def _assess_scaling_risk_level(self, scaling_decision) -> RiskLevel:
        """Assess risk level for scaling decision."""
        
        if scaling_decision.trigger_reason.value == "emergency":
            return RiskLevel.EXTREME
        elif scaling_decision.trigger_reason.value == "liquidation_proximity":
            return RiskLevel.HIGH
        elif scaling_decision.trigger_reason.value == "better_score":
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def _select_optimal_vault(
        self,
        available_vaults: List[Vault],
        symbol: str
    ) -> Optional[Vault]:
        """Select optimal vault for trading."""
        
        if not available_vaults:
            return None
        
        # Score vaults based on various factors
        vault_scores = []
        
        for vault in available_vaults:
            score = 0
            
            # Balance factor (higher balance = better)
            score += float(vault.current_balance) / 10000  # Normalize to 10k
            
            # Position count factor (fewer positions = better)
            score += (self.max_positions_per_vault - vault.positions_count) * 0.5
            
            # Performance factor (if available)
            if hasattr(vault, 'performance_score'):
                score += float(vault.performance_score or 0) * 0.3
            
            vault_scores.append((vault, score))
        
        # Return vault with highest score
        vault_scores.sort(key=lambda x: x[1], reverse=True)
        return vault_scores[0][0]
    
    async def _get_existing_position(
        self,
        vault_id: str,
        symbol: str
    ) -> Optional[Position]:
        """Get existing position for symbol in vault."""
        
        return self.session.query(Position).filter(
            and_(
                Position.vault_id == vault_id,
                Position.symbol == symbol,
                Position.status == PositionStatus.OPEN.value
            )
        ).first()
    
    async def get_trading_summary(self) -> Dict[str, Any]:
        """Get comprehensive trading summary with corrected metrics."""
        
        try:
            # Get all active positions
            active_positions = self.session.query(Position).filter(
                Position.status == PositionStatus.OPEN.value
            ).all()
            
            # Calculate summary metrics
            total_positions = len(active_positions)
            total_invested = Decimal('0')
            total_profit_targets = Decimal('0')
            
            position_summaries = []
            
            for position in active_positions:
                # Get position scales
                scales = self.session.query(PositionScale).filter(
                    PositionScale.position_id == position.id
                ).all()
                
                # CORRECTED: Calculate total invested for this position
                position_total_invested = sum(scale.investment_amount for scale in scales)
                position_profit_threshold = position_total_invested * self.profit_threshold_pct
                position_take_profit_trigger = position_total_invested + position_profit_threshold
                
                total_invested += position_total_invested
                total_profit_targets += position_profit_threshold
                
                position_summaries.append({
                    "symbol": position.symbol,
                    "direction": position.direction,
                    "stage": position.current_stage,
                    "total_invested": float(position_total_invested),
                    "profit_threshold": float(position_profit_threshold),
                    "take_profit_trigger": float(position_take_profit_trigger),
                    "liquidation_price": float(position.liquidation_price) if position.liquidation_price else None
                })
            
            return {
                "total_positions": total_positions,
                "total_invested": float(total_invested),
                "total_profit_targets": float(total_profit_targets),
                "average_profit_threshold_pct": float(self.profit_threshold_pct * 100),
                "positions": position_summaries,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting trading summary: {str(e)}")
            return {"error": str(e)}


# Export main class
__all__ = [
    'TradingAgent',
    'TradingRecommendation',
    'TradingDecision',
    'RiskLevel'
]

