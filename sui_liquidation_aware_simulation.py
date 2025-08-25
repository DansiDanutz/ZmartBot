#!/usr/bin/env python3
"""
SUI/USDT Trading Simulation with PROPER Liquidation Awareness
Implements liquidation clusters and correct doubling triggers
"""

from decimal import Decimal
from datetime import datetime
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LiquidationCluster:
    """Liquidation cluster data"""
    price: Decimal
    side: str  # "above" or "below"
    strength: float  # 0-1 strength indicator
    volume: Decimal

class LiquidationAwareSimulation:
    """Trading simulation with proper liquidation mechanics"""
    
    def __init__(self):
        self.vault_balance = Decimal("10000.00")
        self.symbol = "SUI/USDT"
        
        # Our EXACT strategy from vault_position_manager.py
        self.position_sizing = {
            1: 0.02,   # 2% at 20X
            2: 0.04,   # 4% at 10X  
            3: 0.08,   # 8% at 5X
            4: 0.16,   # 16% at 2X
            5: 0.15    # 15% margin (no leverage)
        }
        
        self.leverage_stages = {
            1: 20,
            2: 10,
            3: 5,
            4: 2,
            5: 0  # Just margin injection
        }
        
        self.tp_percentage = Decimal("1.75")  # 175% of margin
        self.partial_close_ratio = 0.5
        self.trailing_stop_percentage = Decimal("0.02")
    
    def calculate_liquidation_price(self, entry_price: Decimal, leverage: int, 
                                   is_long: bool = True) -> Decimal:
        """Calculate exact liquidation price for leveraged position"""
        if leverage == 0:
            return Decimal("0")  # No liquidation with no leverage
        
        # Liquidation occurs when loss equals margin (minus maintenance margin)
        # With 20X leverage, 5% drop = 100% loss
        # Formula: liquidation_distance = 1 / leverage * 0.95 (accounting for maintenance)
        liquidation_percentage = Decimal("1") / Decimal(str(leverage)) * Decimal("0.95")
        
        if is_long:
            liquidation_price = entry_price * (Decimal("1") - liquidation_percentage)
        else:
            liquidation_price = entry_price * (Decimal("1") + liquidation_percentage)
        
        return liquidation_price
    
    def find_liquidation_clusters(self, current_price: Decimal) -> Tuple[List[LiquidationCluster], List[LiquidationCluster]]:
        """Find liquidation clusters around current price"""
        clusters_above = []
        clusters_below = []
        
        # Simulate liquidation clusters based on common leverage levels
        # Above current price (shorts get liquidated)
        for i, (percentage, strength) in enumerate([(0.05, 0.8), (0.10, 0.6)]):
            cluster_price = current_price * (Decimal("1") + Decimal(str(percentage)))
            clusters_above.append(LiquidationCluster(
                price=cluster_price,
                side="above",
                strength=strength,
                volume=Decimal("1000000") * (2 - i)
            ))
        
        # Below current price (longs get liquidated)
        for i, (percentage, strength) in enumerate([(0.05, 0.9), (0.10, 0.7)]):
            cluster_price = current_price * (Decimal("1") - Decimal(str(percentage)))
            clusters_below.append(LiquidationCluster(
                price=cluster_price,
                side="below",
                strength=strength,
                volume=Decimal("1500000") * (2 - i)
            ))
        
        return clusters_above, clusters_below
    
    def check_doubling_trigger(self, entry_price: Decimal, current_price: Decimal,
                              position_liquidation: Decimal, 
                              clusters_below: List[LiquidationCluster],
                              current_margin: Decimal) -> Tuple[bool, str]:
        """Check if we should double position based on liquidation proximity"""
        # Calculate current loss percentage
        loss_percentage = (entry_price - current_price) / entry_price
        margin_loss_percentage = loss_percentage * self.leverage_stages[1]  # Assuming initial leverage
        
        # Trigger 1: Position liquidation is at 80% of margin
        if margin_loss_percentage >= Decimal("0.80"):
            return True, "80% margin loss reached"
        
        # Trigger 2: Price hits first liquidation cluster below
        if clusters_below:
            first_cluster = clusters_below[0]
            if current_price <= first_cluster.price:
                # Check if our position liquidation is between clusters
                if len(clusters_below) >= 2:
                    second_cluster = clusters_below[1]
                    if position_liquidation < first_cluster.price and position_liquidation > second_cluster.price:
                        return True, f"First cluster hit at {first_cluster.price}, position liquidation between clusters"
        
        return False, ""
    
    def simulate_with_liquidation_awareness(self):
        """Run complete simulation with liquidation awareness"""
        print("\n" + "="*80)
        print("🚀 LIQUIDATION-AWARE SUI/USDT SIMULATION")
        print("="*80)
        print(f"Vault Balance: ${self.vault_balance}")
        print("Strategy: NO STOP LOSS - Liquidation cluster based doubling")
        print("="*80)
        
        # Scenario 1: Position with liquidation risk
        self.simulate_liquidation_scenario()
        
        # Scenario 2: Doubling at liquidation clusters
        self.simulate_cluster_doubling()
        
        # Scenario 3: Margin injection scenario
        self.simulate_margin_injection()
    
    def simulate_liquidation_scenario(self):
        """Simulate position approaching liquidation"""
        print("\n" + "="*80)
        print("SCENARIO: LIQUIDATION RISK WITH 20X LEVERAGE")
        print("="*80)
        
        entry_price = Decimal("3.50")
        margin = self.vault_balance * Decimal(str(self.position_sizing[1]))
        leverage = self.leverage_stages[1]
        position_size = margin * leverage
        quantity = position_size / entry_price
        
        print(f"\n📍 INITIAL POSITION:")
        print(f"   Entry Price: ${entry_price}")
        print(f"   Margin: ${margin} (2% of balance)")
        print(f"   Leverage: {leverage}X")
        print(f"   Position Size: ${position_size}")
        print(f"   Quantity: {quantity:.2f} SUI")
        
        # Calculate liquidation
        liquidation_price = self.calculate_liquidation_price(entry_price, leverage)
        drop_to_liquidation = (entry_price - liquidation_price) / entry_price * 100
        
        print(f"\n⚠️ LIQUIDATION ANALYSIS:")
        print(f"   Liquidation Price: ${liquidation_price:.4f}")
        print(f"   Distance to Liquidation: {drop_to_liquidation:.2f}%")
        print(f"   With 20X leverage, a {drop_to_liquidation:.2f}% drop = LIQUIDATION")
        
        # Show what happens at different price drops
        print(f"\n📊 PRICE DROP SCENARIOS:")
        for drop_pct in [3, 4.5, 4.8, 5]:
            test_price = entry_price * (Decimal("1") - Decimal(str(drop_pct/100)))
            margin_loss = (entry_price - test_price) / entry_price * leverage * margin
            margin_loss_pct = margin_loss / margin * 100
            
            if test_price > liquidation_price:
                print(f"   -{drop_pct}% to ${test_price:.4f}: Loss = ${margin_loss:.2f} ({margin_loss_pct:.1f}% of margin)")
            else:
                print(f"   -{drop_pct}% to ${test_price:.4f}: ❌ LIQUIDATED - Total loss of ${margin}")
        
        # Find liquidation clusters
        clusters_above, clusters_below = self.find_liquidation_clusters(entry_price)
        
        print(f"\n🎯 LIQUIDATION CLUSTERS DETECTED:")
        print(f"   Above (Shorts liquidating):")
        for cluster in clusters_above:
            print(f"      ${cluster.price:.4f} - Strength: {cluster.strength}")
        print(f"   Below (Longs liquidating):")
        for cluster in clusters_below:
            print(f"      ${cluster.price:.4f} - Strength: {cluster.strength}")
        
        # Check doubling triggers
        test_price = entry_price * Decimal("0.96")  # 4% drop
        should_double, reason = self.check_doubling_trigger(
            entry_price, test_price, liquidation_price, clusters_below, margin
        )
        
        print(f"\n🔄 DOUBLING CHECK at ${test_price:.4f}:")
        if should_double:
            print(f"   ✅ DOUBLE POSITION: {reason}")
        else:
            print(f"   ⏸️ Hold position, doubling triggers not met")
    
    def simulate_cluster_doubling(self):
        """Simulate doubling at liquidation clusters"""
        print("\n" + "="*80)
        print("SCENARIO: DOUBLING AT LIQUIDATION CLUSTERS")
        print("="*80)
        
        entry_price_1 = Decimal("3.50")
        clusters_above, clusters_below = self.find_liquidation_clusters(entry_price_1)
        
        print(f"\n📍 STAGE 1:")
        margin_1 = self.vault_balance * Decimal(str(self.position_sizing[1]))
        leverage_1 = self.leverage_stages[1]
        liquidation_1 = self.calculate_liquidation_price(entry_price_1, leverage_1)
        print(f"   Entry: ${entry_price_1}")
        print(f"   Margin: ${margin_1}")
        print(f"   Leverage: {leverage_1}X")
        print(f"   Position Liquidation: ${liquidation_1:.4f}")
        
        # Price drops to first cluster
        first_cluster = clusters_below[0]
        print(f"\n📉 PRICE DROPS TO FIRST CLUSTER:")
        print(f"   Current Price: ${first_cluster.price:.4f}")
        print(f"   First Cluster: ${first_cluster.price:.4f}")
        print(f"   Position Liquidation: ${liquidation_1:.4f}")
        
        if liquidation_1 < first_cluster.price and len(clusters_below) > 1:
            second_cluster = clusters_below[1]
            if liquidation_1 > second_cluster.price:
                print(f"   ✅ DOUBLE TRIGGER: Liquidation between clusters!")
                print(f"      Position liquidation ({liquidation_1:.4f}) is between:")
                print(f"      - First cluster: ${first_cluster.price:.4f}")
                print(f"      - Second cluster: ${second_cluster.price:.4f}")
                
                # Execute doubling
                margin_2 = self.vault_balance * Decimal(str(self.position_sizing[2]))
                leverage_2 = self.leverage_stages[2]
                entry_price_2 = first_cluster.price
                
                print(f"\n📍 STAGE 2 DOUBLE:")
                print(f"   Entry: ${entry_price_2:.4f}")
                print(f"   Additional Margin: ${margin_2}")
                print(f"   New Leverage: {leverage_2}X")
                
                # Calculate new weighted average
                position_1 = margin_1 * leverage_1
                position_2 = margin_2 * leverage_2
                total_cost = position_1 * entry_price_1 / entry_price_1 + position_2 * entry_price_2 / entry_price_2
                total_quantity = position_1 / entry_price_1 + position_2 / entry_price_2
                avg_entry = (entry_price_1 * position_1 / entry_price_1 + entry_price_2 * position_2 / entry_price_2) / total_quantity
                
                print(f"\n📊 COMBINED POSITION:")
                print(f"   Total Margin: ${margin_1 + margin_2}")
                print(f"   Average Entry: ${avg_entry:.4f}")
                print(f"   Effective Leverage: {(position_1 + position_2)/(margin_1 + margin_2):.1f}X")
                
                # New liquidation with combined position
                effective_leverage = (position_1 + position_2) / (margin_1 + margin_2)
                new_liquidation = self.calculate_liquidation_price(avg_entry, int(effective_leverage))
                print(f"   New Liquidation: ${new_liquidation:.4f}")
                print(f"   🛡️ Liquidation moved from ${liquidation_1:.4f} to ${new_liquidation:.4f}")
                
                # Reset targets
                total_margin = margin_1 + margin_2
                tp_target = total_margin * self.tp_percentage
                print(f"\n🎯 TARGETS RESET:")
                print(f"   New TP Target: 175% of ${total_margin} = ${tp_target}")
                print(f"   All previous targets cancelled and reset")
    
    def simulate_margin_injection(self):
        """Simulate margin injection as last resort"""
        print("\n" + "="*80)
        print("SCENARIO: MARGIN INJECTION (15% BALANCE)")
        print("="*80)
        
        # After all doublings
        total_margin_used = sum(self.vault_balance * Decimal(str(self.position_sizing[i])) 
                               for i in range(1, 5))
        
        print(f"\n📊 POSITION AFTER ALL DOUBLINGS:")
        print(f"   Stages 1-4 Margin: ${total_margin_used}")
        print(f"   Percentage of Balance: {total_margin_used/self.vault_balance*100:.1f}%")
        
        # Calculate effective leverage
        position_sizes = [
            self.vault_balance * Decimal(str(self.position_sizing[i])) * self.leverage_stages[i]
            for i in range(1, 5) if self.leverage_stages[i] > 0
        ]
        total_position = sum(position_sizes)
        effective_leverage = total_position / total_margin_used
        
        print(f"   Total Position Size: ${total_position}")
        print(f"   Effective Leverage: {effective_leverage:.1f}X")
        
        # Price approaching liquidation
        avg_entry = Decimal("2.80")  # Assumed average after doublings
        current_liquidation = self.calculate_liquidation_price(avg_entry, int(effective_leverage))
        
        print(f"\n⚠️ APPROACHING LIQUIDATION:")
        print(f"   Average Entry: ${avg_entry}")
        print(f"   Current Liquidation: ${current_liquidation:.4f}")
        
        critical_price = current_liquidation * Decimal("1.01")  # 1% above liquidation
        print(f"   Price drops to: ${critical_price:.4f}")
        print(f"   Distance to liquidation: 1%")
        
        # Inject margin
        margin_injection = self.vault_balance * Decimal(str(self.position_sizing[5]))
        print(f"\n💉 MARGIN INJECTION TRIGGERED:")
        print(f"   Injection Amount: ${margin_injection} (15% of balance)")
        print(f"   No leverage on injection (pure margin)")
        
        # New liquidation after injection
        new_total_margin = total_margin_used + margin_injection
        new_effective_leverage = total_position / new_total_margin
        new_liquidation = self.calculate_liquidation_price(avg_entry, max(1, int(new_effective_leverage)))
        
        print(f"\n✅ AFTER MARGIN INJECTION:")
        print(f"   Total Margin: ${new_total_margin}")
        print(f"   New Effective Leverage: {new_effective_leverage:.1f}X")
        print(f"   New Liquidation: ${new_liquidation:.4f}")
        print(f"   🛡️ Liquidation moved from ${current_liquidation:.4f} to ${new_liquidation:.4f}")
        
        # Maximum risk
        print(f"\n📊 MAXIMUM RISK SUMMARY:")
        print(f"   Total Margin Committed: ${new_total_margin}")
        print(f"   Percentage of Vault: {new_total_margin/self.vault_balance*100:.1f}%")
        print(f"   Maximum Loss (if liquidated): ${new_total_margin}")
        print(f"   Remaining Balance: ${self.vault_balance - new_total_margin}")
    
    def run_complete_simulation(self):
        """Run all simulations"""
        print("\n" + "="*80)
        print("🚀 COMPLETE LIQUIDATION-AWARE TRADING SIMULATION")
        print(f"💰 Vault Balance: ${self.vault_balance}")
        print("📋 Strategy: Liquidation Cluster Based Doubling")
        print("="*80)
        
        self.simulate_with_liquidation_awareness()
        
        print("\n" + "="*80)
        print("📊 KEY STRATEGY RULES WITH LIQUIDATION AWARENESS")
        print("="*80)
        
        print("\n✅ LIQUIDATION MANAGEMENT:")
        print("   1. Monitor liquidation clusters (2 above, 2 below)")
        print("   2. Double when:")
        print("      - Position at 80% margin loss")
        print("      - Price hits first cluster AND liquidation between clusters")
        print("   3. Reset ALL targets when doubling")
        print("   4. Inject 15% margin when within 1% of liquidation")
        print("   5. NEVER close at loss - manage liquidation risk instead")
        
        print("\n⚠️ LEVERAGE & LIQUIDATION:")
        print("   • 20X leverage = liquidation at 4.75% drop")
        print("   • 10X leverage = liquidation at 9.5% drop")
        print("   • 5X leverage = liquidation at 19% drop")
        print("   • 2X leverage = liquidation at 47.5% drop")
        print("   • 0X (margin) = no liquidation possible")
        
        print("\n🎯 PROFIT TARGETS:")
        print("   • Always 175% of TOTAL margin invested")
        print("   • Targets RESET completely on each double")
        print("   • Close 50% at TP, trail the rest")
        
        print("\n" + "="*80)
        print("✅ SIMULATION COMPLETE - LIQUIDATION LOGIC IMPLEMENTED")
        print("="*80)

# Run the simulation
if __name__ == "__main__":
    simulator = LiquidationAwareSimulation()
    simulator.run_complete_simulation()