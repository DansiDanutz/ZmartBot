"""
Trade Strategy Module - Position Scaler Service
===============================================

Advanced position scaling service with correct profit calculation logic.
Calculates profit thresholds based on TOTAL POSITION VALUE, not initial position.

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
    PositionScaleCreate, PositionStatus, ScaleStage
)


class ScalingTrigger(str, Enum):
    """Position scaling trigger types."""
    BETTER_SCORE = "better_score"
    LIQUIDATION_PROXIMITY = "liquidation_proximity"
    MANUAL = "manual"
    EMERGENCY = "emergency"


class ProfitTakeStage(str, Enum):
    """Profit taking stages."""
    FIRST_TAKE = "first_take"      # 30% at 75% total profit
    SECOND_TAKE = "second_take"    # 25% at trailing stop
    FINAL_TAKE = "final_take"      # Remaining 45%


@dataclass
class PositionScaleConfig:
    """Configuration for a single scaling stage."""
    stage: int
    bankroll_percentage: Decimal
    leverage: Decimal
    description: str


@dataclass
class PositionCalculation:
    """Complete position calculation results."""
    # Investment amounts
    total_invested: Decimal
    current_stage_investment: Decimal
    
    # Position values
    total_position_value: Decimal
    current_margin: Decimal
    
    # Profit calculations (CORRECTED LOGIC)
    profit_threshold_75pct: Decimal  # 75% of total invested
    first_take_profit_trigger: Decimal  # total_invested + profit_threshold_75pct
    
    # Liquidation calculations
    liquidation_price: Decimal
    liquidation_distance_pct: Decimal
    
    # Profit taking levels
    first_take_amount: Decimal      # 30% of position
    second_take_amount: Decimal     # 25% of position  
    final_take_amount: Decimal      # Remaining 45%
    
    # Trailing stop levels
    trailing_stop_1_pct: Decimal    # Initial trailing stop
    trailing_stop_2_pct: Decimal    # Final trailing stop (3%)
    
    # Risk metrics
    risk_reward_ratio: Decimal
    max_loss_amount: Decimal
    break_even_price: Decimal


@dataclass
class ScalingDecision:
    """Position scaling decision result."""
    should_scale: bool
    trigger_reason: ScalingTrigger
    recommended_stage: int
    confidence_score: Decimal
    risk_assessment: str
    calculation: Optional[PositionCalculation]


class PositionScaler:
    """
    Advanced position scaling service with CORRECTED profit calculations.
    
    Key Correction: Profit thresholds are calculated based on TOTAL POSITION VALUE,
    not just the initial position value.
    
    Example:
    - Initial: 100 USDT → Total invested: 100 USDT
    - Double 1: +200 USDT → Total invested: 300 USDT  
    - Double 2: +400 USDT → Total invested: 700 USDT
    - Double 3: +800 USDT → Total invested: 1500 USDT
    
    75% profit = 75% of 1500 = 1125 USDT
    First take profit trigger = 1500 + 1125 = 2625 USDT margin
    """
    
    def __init__(self, session: Session, redis_client: Redis):
        self.session = session
        self.redis_client = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Initialize repositories
        self.position_repo = BaseRepository(Position, session)
        self.scale_repo = BaseRepository(PositionScale, session)
        
        # Position scaling configuration (CORRECTED)
        self.scaling_stages = [
            PositionScaleConfig(
                stage=1,
                bankroll_percentage=Decimal('0.01'),  # 1%
                leverage=Decimal('20.0'),             # 20X
                description="Initial entry"
            ),
            PositionScaleConfig(
                stage=2, 
                bankroll_percentage=Decimal('0.02'),  # 2%
                leverage=Decimal('10.0'),             # 10X
                description="First double-up"
            ),
            PositionScaleConfig(
                stage=3,
                bankroll_percentage=Decimal('0.04'),  # 4% 
                leverage=Decimal('5.0'),              # 5X
                description="Second double-up"
            ),
            PositionScaleConfig(
                stage=4,
                bankroll_percentage=Decimal('0.08'),  # 8%
                leverage=Decimal('2.0'),              # 2X
                description="Final double-up"
            )
        ]
        
        # Profit taking configuration
        self.profit_threshold_pct = Decimal('0.75')      # 75% profit threshold
        self.first_take_pct = Decimal('0.30')            # 30% position close
        self.second_take_pct = Decimal('0.25')           # 25% position close
        self.final_take_pct = Decimal('0.45')            # 45% remaining
        self.trailing_stop_1 = Decimal('0.30')           # 30% trailing stop
        self.trailing_stop_2 = Decimal('0.03')           # 3% final trailing stop
        
        # Risk management
        self.max_positions_per_vault = 2
        self.liquidation_buffer_pct = Decimal('0.05')    # 5% buffer from liquidation
        self.emergency_scale_threshold = Decimal('0.10') # 10% from liquidation
    
    async def calculate_position_metrics(
        self, 
        position: Position,
        current_price: Decimal,
        vault_bankroll: Decimal
    ) -> PositionCalculation:
        """
        Calculate complete position metrics with CORRECTED profit logic.
        
        Key Correction: Profit calculations are based on total invested amount
        across all scaling stages, not just the initial investment.
        """
        
        # Get all scaling stages for this position
        scales = self.session.query(PositionScale).filter(
            PositionScale.position_id == position.id
        ).order_by(PositionScale.stage).all()
        
        if not scales:
            raise ValueError(f"No scaling stages found for position {position.id}")
        
        # Calculate total invested amount across ALL stages
        total_invested = Decimal('0')
        total_position_value = Decimal('0')
        
        for scale in scales:
            # Investment amount for this stage
            stage_investment = scale.investment_amount
            total_invested += stage_investment
            
            # Position value for this stage (investment * leverage)
            stage_position_value = stage_investment * scale.leverage
            total_position_value += stage_position_value
        
        # CORRECTED PROFIT CALCULATION
        # 75% profit is calculated on TOTAL INVESTED, not initial investment
        profit_threshold_75pct = total_invested * self.profit_threshold_pct
        
        # First take profit trigger = total invested + 75% profit
        first_take_profit_trigger = total_invested + profit_threshold_75pct
        
        # Current margin calculation
        if position.direction == "long":
            current_margin = total_position_value * (current_price - position.average_entry_price) / position.average_entry_price
        else:  # short
            current_margin = total_position_value * (position.average_entry_price - current_price) / position.average_entry_price
        
        # Add the invested amount to get total margin
        current_margin += total_invested
        
        # Liquidation price calculation (weighted average across all scales)
        liquidation_price = self._calculate_weighted_liquidation_price(scales, position)
        
        # Liquidation distance
        if position.direction == "long":
            liquidation_distance_pct = (current_price - liquidation_price) / current_price
        else:
            liquidation_distance_pct = (liquidation_price - current_price) / current_price
        
        # Profit taking amounts (based on total position value)
        first_take_amount = total_position_value * self.first_take_pct
        second_take_amount = total_position_value * self.second_take_pct
        final_take_amount = total_position_value * self.final_take_pct
        
        # Risk metrics
        max_loss_amount = total_invested  # Maximum loss is total invested
        
        # Break-even price (where margin equals total invested)
        if position.direction == "long":
            break_even_price = position.average_entry_price
        else:
            break_even_price = position.average_entry_price
        
        # Risk-reward ratio
        potential_profit = profit_threshold_75pct
        risk_reward_ratio = potential_profit / max_loss_amount if max_loss_amount > 0 else Decimal('0')
        
        return PositionCalculation(
            total_invested=total_invested,
            current_stage_investment=scales[-1].investment_amount,
            total_position_value=total_position_value,
            current_margin=current_margin,
            profit_threshold_75pct=profit_threshold_75pct,
            first_take_profit_trigger=first_take_profit_trigger,
            liquidation_price=liquidation_price,
            liquidation_distance_pct=liquidation_distance_pct,
            first_take_amount=first_take_amount,
            second_take_amount=second_take_amount,
            final_take_amount=final_take_amount,
            trailing_stop_1_pct=self.trailing_stop_1,
            trailing_stop_2_pct=self.trailing_stop_2,
            risk_reward_ratio=risk_reward_ratio,
            max_loss_amount=max_loss_amount,
            break_even_price=break_even_price
        )
    
    def _calculate_weighted_liquidation_price(
        self, 
        scales: List[PositionScale], 
        position: Position
    ) -> Decimal:
        """Calculate weighted average liquidation price across all scaling stages."""
        
        total_weight = Decimal('0')
        weighted_liquidation = Decimal('0')
        
        for scale in scales:
            # Weight by position value (investment * leverage)
            weight = scale.investment_amount * scale.leverage
            total_weight += weight
            
            # Calculate liquidation price for this scale
            if position.direction == "long":
                # Long liquidation: entry_price * (1 - 1/leverage)
                scale_liquidation = scale.entry_price * (Decimal('1') - Decimal('1') / scale.leverage)
            else:
                # Short liquidation: entry_price * (1 + 1/leverage)  
                scale_liquidation = scale.entry_price * (Decimal('1') + Decimal('1') / scale.leverage)
            
            weighted_liquidation += scale_liquidation * weight
        
        return weighted_liquidation / total_weight if total_weight > 0 else Decimal('0')
    
    async def evaluate_scaling_opportunity(
        self,
        position: Position,
        current_price: Decimal,
        current_signal_score: Decimal,
        vault_bankroll: Decimal
    ) -> ScalingDecision:
        """Evaluate whether position should be scaled up."""
        
        try:
            # Get current position metrics
            calculation = await self.calculate_position_metrics(
                position, current_price, vault_bankroll
            )
            
            # Get current scaling stage
            current_stage = len(self.session.query(PositionScale).filter(
                PositionScale.position_id == position.id
            ).all())
            
            # Check if we can scale further
            if current_stage >= len(self.scaling_stages):
                return ScalingDecision(
                    should_scale=False,
                    trigger_reason=ScalingTrigger.MANUAL,
                    recommended_stage=current_stage,
                    confidence_score=Decimal('0'),
                    risk_assessment="Maximum scaling stages reached",
                    calculation=calculation
                )
            
            # Check liquidation proximity
            liquidation_proximity = calculation.liquidation_distance_pct
            
            # Scaling decision logic
            should_scale = False
            trigger_reason = ScalingTrigger.MANUAL
            confidence_score = Decimal('0')
            risk_assessment = "No scaling recommended"
            
            # 1. Check for better signal score
            if current_signal_score > position.initial_signal_score * Decimal('1.2'):  # 20% better
                should_scale = True
                trigger_reason = ScalingTrigger.BETTER_SCORE
                confidence_score = Decimal('0.8')
                risk_assessment = "Better signal score detected"
            
            # 2. Check for liquidation proximity (higher priority)
            elif liquidation_proximity < self.liquidation_buffer_pct:
                should_scale = True
                trigger_reason = ScalingTrigger.LIQUIDATION_PROXIMITY
                confidence_score = Decimal('0.9')
                risk_assessment = "Close to liquidation - defensive scaling"
            
            # 3. Emergency scaling (very close to liquidation)
            elif liquidation_proximity < self.emergency_scale_threshold:
                should_scale = True
                trigger_reason = ScalingTrigger.EMERGENCY
                confidence_score = Decimal('1.0')
                risk_assessment = "Emergency scaling to prevent liquidation"
            
            return ScalingDecision(
                should_scale=should_scale,
                trigger_reason=trigger_reason,
                recommended_stage=current_stage + 1,
                confidence_score=confidence_score,
                risk_assessment=risk_assessment,
                calculation=calculation
            )
            
        except Exception as e:
            self.logger.error(f"Error evaluating scaling opportunity: {str(e)}")
            return ScalingDecision(
                should_scale=False,
                trigger_reason=ScalingTrigger.MANUAL,
                recommended_stage=1,
                confidence_score=Decimal('0'),
                risk_assessment=f"Error in evaluation: {str(e)}",
                calculation=None
            )
    
    async def execute_position_scaling(
        self,
        position: Position,
        scaling_decision: ScalingDecision,
        current_price: Decimal,
        vault_bankroll: Decimal,
        signal_score: Decimal
    ) -> Tuple[bool, str, Optional[PositionScale]]:
        """Execute position scaling based on decision."""
        
        try:
            if not scaling_decision.should_scale:
                return False, "Scaling not recommended", None
            
            stage = scaling_decision.recommended_stage
            if stage > len(self.scaling_stages):
                return False, "Invalid scaling stage", None
            
            stage_config = self.scaling_stages[stage - 1]
            
            # Calculate investment amount for this stage
            investment_amount = vault_bankroll * stage_config.bankroll_percentage
            
            # Validate vault has sufficient funds
            if investment_amount > vault_bankroll * Decimal('0.5'):  # Max 50% of bankroll per scale
                return False, "Insufficient vault funds for scaling", None
            
            # Create new scaling stage
            scale_data = PositionScaleCreate(
                position_id=position.id,
                stage=stage,
                investment_amount=investment_amount,
                leverage=stage_config.leverage,
                entry_price=current_price,
                signal_score=signal_score,
                trigger_reason=scaling_decision.trigger_reason.value,
                scaling_metadata={
                    "trigger_confidence": float(scaling_decision.confidence_score),
                    "risk_assessment": scaling_decision.risk_assessment,
                    "liquidation_distance_pct": float(scaling_decision.calculation.liquidation_distance_pct) if scaling_decision.calculation else None,
                    "vault_bankroll_at_scaling": float(vault_bankroll),
                    "scaling_timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            
            new_scale = self.scale_repo.create(scale_data)
            
            # Update position with new average entry price and total investment
            await self._update_position_after_scaling(position, new_scale, current_price)
            
            # Log scaling event
            self.logger.info(
                f"Position {position.id} scaled to stage {stage} "
                f"with {investment_amount} USDT at {current_price} "
                f"(trigger: {scaling_decision.trigger_reason.value})"
            )
            
            return True, f"Successfully scaled to stage {stage}", new_scale
            
        except Exception as e:
            self.logger.error(f"Error executing position scaling: {str(e)}")
            return False, str(e), None
    
    async def _update_position_after_scaling(
        self,
        position: Position,
        new_scale: PositionScale,
        current_price: Decimal
    ) -> None:
        """Update position metrics after adding new scaling stage."""
        
        # Get all scales for this position
        all_scales = self.session.query(PositionScale).filter(
            PositionScale.position_id == position.id
        ).all()
        
        # Calculate new weighted average entry price
        total_position_value = Decimal('0')
        weighted_entry_sum = Decimal('0')
        total_investment = Decimal('0')
        
        for scale in all_scales:
            position_value = scale.investment_amount * scale.leverage
            total_position_value += position_value
            weighted_entry_sum += scale.entry_price * position_value
            total_investment += scale.investment_amount
        
        new_average_entry = weighted_entry_sum / total_position_value if total_position_value > 0 else position.average_entry_price
        
        # Update position
        position.average_entry_price = new_average_entry
        position.total_investment = total_investment
        position.total_position_size = total_position_value
        position.current_stage = new_scale.stage
        position.last_scaled_at = datetime.now(timezone.utc)
        position.updated_at = datetime.now(timezone.utc)
        
        self.session.commit()
    
    async def check_profit_taking_triggers(
        self,
        position: Position,
        current_price: Decimal,
        vault_bankroll: Decimal
    ) -> Dict[str, Any]:
        """
        Check if position has reached profit taking triggers.
        
        CORRECTED LOGIC: Uses total invested amount for profit calculations.
        """
        
        try:
            calculation = await self.calculate_position_metrics(
                position, current_price, vault_bankroll
            )
            
            triggers = {
                "first_take_profit": False,
                "trailing_stop_1": False,
                "trailing_stop_2": False,
                "final_take": False,
                "current_margin": calculation.current_margin,
                "profit_threshold": calculation.first_take_profit_trigger,
                "profit_amount": calculation.current_margin - calculation.total_invested,
                "profit_percentage": ((calculation.current_margin - calculation.total_invested) / calculation.total_invested * 100) if calculation.total_invested > 0 else Decimal('0')
            }
            
            # Check first take profit trigger (75% of total invested)
            if calculation.current_margin >= calculation.first_take_profit_trigger:
                triggers["first_take_profit"] = True
                triggers["take_amount"] = calculation.first_take_amount
                triggers["remaining_position"] = calculation.total_position_value - calculation.first_take_amount
                
                # Calculate trailing stop price for remaining position
                if position.direction == "long":
                    trailing_stop_price = current_price * (Decimal('1') - calculation.trailing_stop_1_pct)
                else:
                    trailing_stop_price = current_price * (Decimal('1') + calculation.trailing_stop_1_pct)
                
                triggers["trailing_stop_price"] = trailing_stop_price
            
            # Check if position has already taken first profit and is at trailing stop
            if position.profit_take_stage == ProfitTakeStage.FIRST_TAKE.value:
                # Check trailing stop conditions
                if position.direction == "long":
                    if current_price <= position.trailing_stop_price:
                        triggers["trailing_stop_1"] = True
                        triggers["take_amount"] = calculation.second_take_amount
                else:
                    if current_price >= position.trailing_stop_price:
                        triggers["trailing_stop_1"] = True
                        triggers["take_amount"] = calculation.second_take_amount
            
            # Check final trailing stop (3%)
            if position.profit_take_stage == ProfitTakeStage.SECOND_TAKE.value:
                if position.direction == "long":
                    if current_price <= position.trailing_stop_price:
                        triggers["final_take"] = True
                        triggers["take_amount"] = calculation.final_take_amount
                else:
                    if current_price >= position.trailing_stop_price:
                        triggers["final_take"] = True
                        triggers["take_amount"] = calculation.final_take_amount
            
            return triggers
            
        except Exception as e:
            self.logger.error(f"Error checking profit taking triggers: {str(e)}")
            return {"error": str(e)}
    
    async def execute_profit_taking(
        self,
        position: Position,
        profit_stage: ProfitTakeStage,
        current_price: Decimal,
        take_amount: Decimal
    ) -> Tuple[bool, str, Decimal]:
        """Execute profit taking at specified stage."""
        
        try:
            # Calculate profit realized
            if position.direction == "long":
                profit_per_unit = current_price - position.average_entry_price
            else:
                profit_per_unit = position.average_entry_price - current_price
            
            units_to_close = take_amount / current_price
            profit_realized = profit_per_unit * units_to_close
            
            # Update position
            position.total_position_size -= take_amount
            position.profit_take_stage = profit_stage.value
            position.total_profit_realized += profit_realized
            position.last_profit_take_at = datetime.now(timezone.utc)
            
            # Set new trailing stop if not final take
            if profit_stage == ProfitTakeStage.FIRST_TAKE:
                if position.direction == "long":
                    position.trailing_stop_price = current_price * (Decimal('1') - self.trailing_stop_1)
                else:
                    position.trailing_stop_price = current_price * (Decimal('1') + self.trailing_stop_1)
            
            elif profit_stage == ProfitTakeStage.SECOND_TAKE:
                if position.direction == "long":
                    position.trailing_stop_price = current_price * (Decimal('1') - self.trailing_stop_2)
                else:
                    position.trailing_stop_price = current_price * (Decimal('1') + self.trailing_stop_2)
            
            elif profit_stage == ProfitTakeStage.FINAL_TAKE:
                # Close entire position
                position.status = PositionStatus.CLOSED.value
                position.closed_at = datetime.now(timezone.utc)
                position.close_price = current_price
            
            self.session.commit()
            
            self.logger.info(
                f"Profit taking executed for position {position.id}: "
                f"Stage {profit_stage.value}, Amount {take_amount}, Profit {profit_realized}"
            )
            
            return True, f"Profit taking successful: {profit_stage.value}", profit_realized
            
        except Exception as e:
            self.logger.error(f"Error executing profit taking: {str(e)}")
            return False, str(e), Decimal('0')
    
    async def add_margin_to_prevent_liquidation(
        self,
        position: Position,
        current_price: Decimal,
        vault_bankroll: Decimal
    ) -> Tuple[bool, str, Decimal]:
        """Add margin to prevent liquidation when all scaling stages are exhausted."""
        
        try:
            calculation = await self.calculate_position_metrics(
                position, current_price, vault_bankroll
            )
            
            # Check if we're close to liquidation
            if calculation.liquidation_distance_pct > self.emergency_scale_threshold:
                return False, "Not close enough to liquidation to add margin", Decimal('0')
            
            # Calculate required margin to move liquidation price to safe distance
            required_margin = calculation.total_invested  # Add total invested amount as margin
            
            # Check if vault has sufficient funds
            if required_margin > vault_bankroll * Decimal('0.3'):  # Max 30% of bankroll for margin
                required_margin = vault_bankroll * Decimal('0.3')
            
            # Update position with additional margin
            position.additional_margin += required_margin
            position.margin_added_at = datetime.now(timezone.utc)
            position.margin_add_reason = "Liquidation prevention"
            
            self.session.commit()
            
            self.logger.info(
                f"Added {required_margin} USDT margin to position {position.id} "
                f"to prevent liquidation"
            )
            
            return True, f"Added {required_margin} USDT margin successfully", required_margin
            
        except Exception as e:
            self.logger.error(f"Error adding margin: {str(e)}")
            return False, str(e), Decimal('0')
    
    def get_position_summary(self, position: Position) -> Dict[str, Any]:
        """Get comprehensive position summary with corrected calculations."""
        
        scales = self.session.query(PositionScale).filter(
            PositionScale.position_id == position.id
        ).order_by(PositionScale.stage).all()
        
        # Calculate totals
        total_invested = sum(scale.investment_amount for scale in scales)
        total_position_value = sum(scale.investment_amount * scale.leverage for scale in scales)
        
        # CORRECTED: 75% profit based on total invested
        profit_threshold = total_invested * self.profit_threshold_pct
        first_take_trigger = total_invested + profit_threshold
        
        return {
            "position_id": str(position.id),
            "symbol": position.symbol,
            "direction": position.direction,
            "status": position.status,
            "current_stage": position.current_stage,
            "total_invested": float(total_invested),
            "total_position_value": float(total_position_value),
            "profit_threshold_75pct": float(profit_threshold),
            "first_take_profit_trigger": float(first_take_trigger),
            "average_entry_price": float(position.average_entry_price),
            "liquidation_price": float(position.liquidation_price) if position.liquidation_price else None,
            "scaling_stages": [
                {
                    "stage": scale.stage,
                    "investment": float(scale.investment_amount),
                    "leverage": float(scale.leverage),
                    "entry_price": float(scale.entry_price),
                    "position_value": float(scale.investment_amount * scale.leverage)
                }
                for scale in scales
            ],
            "profit_take_stage": position.profit_take_stage,
            "total_profit_realized": float(position.total_profit_realized) if position.total_profit_realized else 0,
            "additional_margin": float(position.additional_margin) if position.additional_margin else 0
        }


# Export main class
__all__ = [
    'PositionScaler',
    'PositionCalculation', 
    'ScalingDecision',
    'ScalingTrigger',
    'ProfitTakeStage',
    'PositionScaleConfig'
]

