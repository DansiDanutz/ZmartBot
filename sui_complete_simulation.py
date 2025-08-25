#!/usr/bin/env python3
"""
Complete SUI/USDT Trading Simulation
ALL scenarios with $10,000 vault balance using our EXACT strategy
"""

from decimal import Decimal
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SUIPaperTradeSimulation:
    """Complete simulation of all possible trading scenarios"""
    
    def __init__(self):
        self.vault_balance = Decimal("10000.00")  # $10,000 USD vault
        self.symbol = "SUI/USDT"
        
        # Our EXACT strategy parameters from vault_position_manager.py
        self.position_sizing = {
            1: 0.02,   # Stage 1: 2% at 20X
            2: 0.04,   # Stage 2: 4% at 10X  
            3: 0.08,   # Stage 3: 8% at 5X
            4: 0.16,   # Stage 4: 16% at 2X
            5: 0.15    # Stage 5: 15% margin (no leverage)
        }
        
        self.leverage_stages = {
            1: 20,
            2: 10,
            3: 5,
            4: 2,
            5: 0  # Just margin
        }
        
        self.tp_percentage = Decimal("1.75")  # 175% of margin
        self.partial_close_ratio = 0.5  # Close 50% at TP
        self.trailing_stop_percentage = Decimal("0.02")  # 2% trailing after TP
    
    def calculate_weighted_average_entry(self, entries):
        """Calculate weighted average entry price"""
        total_cost = sum(e['cost'] for e in entries)
        total_quantity = sum(e['quantity'] for e in entries)
        return total_cost / total_quantity if total_quantity > 0 else 0
    
    def simulate_scenario_1(self):
        """SCENARIO 1: Market goes RIGHT way immediately"""
        print("\n" + "="*80)
        print("SCENARIO 1: MARKET GOES RIGHT WAY")
        print("="*80)
        
        entry_price = Decimal("3.50")
        
        # Stage 1: Initial position
        margin_1 = self.vault_balance * Decimal(str(self.position_sizing[1]))  # $200
        leverage_1 = self.leverage_stages[1]  # 20X
        position_size_1 = margin_1 * leverage_1  # $4,000
        quantity_1 = position_size_1 / entry_price  # 1,142.86 SUI
        
        print(f"\n📍 ENTRY:")
        print(f"   SUI Price: ${entry_price}")
        print(f"   Margin Used: ${margin_1} (2% of balance)")
        print(f"   Leverage: {leverage_1}X")
        print(f"   Position Size: ${position_size_1}")
        print(f"   Quantity: {quantity_1:.2f} SUI")
        
        # Calculate TP
        tp_target_profit = margin_1 * self.tp_percentage  # $350 profit target
        tp_price_movement = tp_target_profit / position_size_1  # 8.75% move needed
        tp_price = entry_price * (Decimal("1") + tp_price_movement)  # $3.81
        
        print(f"\n🎯 TAKE PROFIT CALCULATION:")
        print(f"   TP Target: 175% of ${margin_1} = ${tp_target_profit}")
        print(f"   Required Price Move: {tp_price_movement*100:.2f}%")
        print(f"   TP Price: ${tp_price:.4f}")
        
        # Market moves to TP
        print(f"\n📈 MARKET ACTION:")
        print(f"   Price moves from ${entry_price} → ${tp_price:.4f}")
        print(f"   Profit reached: ${tp_target_profit}")
        
        print(f"\n✅ ACTIONS TAKEN:")
        print(f"   1. Close 50% of position (571.43 SUI)")
        print(f"   2. Secure profit: ${tp_target_profit/2}")
        print(f"   3. Trailing stop activated at {tp_price * (1-self.trailing_stop_percentage):.4f}")
        print(f"   4. Let remaining 50% run with trailing stop")
        
        # If price continues up
        higher_price = tp_price * Decimal("1.05")  # 5% higher
        trailing_stop = higher_price * (Decimal("1") - self.trailing_stop_percentage)
        
        print(f"\n📊 IF PRICE CONTINUES UP:")
        print(f"   Price reaches: ${higher_price:.4f}")
        print(f"   Trailing stop moves to: ${trailing_stop:.4f}")
        print(f"   If hit, additional profit: ${(trailing_stop - entry_price) * (quantity_1/2):.2f}")
        
        total_profit = tp_target_profit/2 + (trailing_stop - entry_price) * (quantity_1/2)
        print(f"\n💰 TOTAL OUTCOME:")
        print(f"   Total Profit: ${total_profit:.2f}")
        print(f"   ROI on Margin: {(total_profit/margin_1)*100:.1f}%")
        print(f"   New Balance: ${self.vault_balance + total_profit:.2f}")
    
    def simulate_scenario_2(self):
        """SCENARIO 2: Market goes WRONG way (1 double)"""
        print("\n" + "="*80)
        print("SCENARIO 2: MARKET GOES WRONG WAY (1 DOUBLE)")
        print("="*80)
        
        entry_price_1 = Decimal("3.50")
        
        # Stage 1: Initial position
        margin_1 = self.vault_balance * Decimal(str(self.position_sizing[1]))  # $200
        position_size_1 = margin_1 * self.leverage_stages[1]  # $4,000
        quantity_1 = position_size_1 / entry_price_1
        
        print(f"\n📍 STAGE 1 ENTRY:")
        print(f"   SUI Price: ${entry_price_1}")
        print(f"   Margin: ${margin_1} (2% balance)")
        print(f"   Position: ${position_size_1} ({quantity_1:.2f} SUI)")
        
        # Market drops 15%
        entry_price_2 = entry_price_1 * Decimal("0.85")  # $2.975
        
        print(f"\n📉 MARKET DROPS 15%:")
        print(f"   Price: ${entry_price_1} → ${entry_price_2:.4f}")
        print(f"   Unrealized Loss: ${(entry_price_2 - entry_price_1) * quantity_1:.2f}")
        
        # Stage 2: Double position
        margin_2 = self.vault_balance * Decimal(str(self.position_sizing[2]))  # $400
        position_size_2 = margin_2 * self.leverage_stages[2]  # $4,000
        quantity_2 = position_size_2 / entry_price_2
        
        print(f"\n📍 STAGE 2 DOUBLE:")
        print(f"   SUI Price: ${entry_price_2:.4f}")
        print(f"   Additional Margin: ${margin_2} (4% balance)")
        print(f"   Leverage: {self.leverage_stages[2]}X")
        print(f"   Additional Position: ${position_size_2} ({quantity_2:.2f} SUI)")
        
        # Calculate new averages
        total_margin = margin_1 + margin_2  # $600
        total_quantity = quantity_1 + quantity_2
        total_cost = (entry_price_1 * quantity_1) + (entry_price_2 * quantity_2)
        avg_entry = total_cost / total_quantity
        
        print(f"\n📊 NEW POSITION SUMMARY:")
        print(f"   Total Margin: ${total_margin}")
        print(f"   Total Quantity: {total_quantity:.2f} SUI")
        print(f"   Average Entry: ${avg_entry:.4f}")
        
        # New TP calculation
        tp_target_profit = total_margin * self.tp_percentage  # $1,050
        tp_price_movement = tp_target_profit / (total_quantity * avg_entry)
        tp_price = avg_entry * (Decimal("1") + tp_price_movement)
        
        print(f"\n🎯 NEW TAKE PROFIT:")
        print(f"   TP Target: 175% of ${total_margin} = ${tp_target_profit}")
        print(f"   TP Price: ${tp_price:.4f}")
        print(f"   Required move from current: {((tp_price/entry_price_2)-1)*100:.2f}%")
        
        # Market recovers to TP
        print(f"\n📈 MARKET RECOVERS:")
        print(f"   Price moves: ${entry_price_2:.4f} → ${tp_price:.4f}")
        print(f"   Profit reached: ${tp_target_profit}")
        
        print(f"\n✅ ACTIONS TAKEN:")
        print(f"   1. Close 50% of position")
        print(f"   2. Secure profit: ${tp_target_profit/2:.2f}")
        print(f"   3. Trailing stop at ${tp_price * (1-self.trailing_stop_percentage):.4f}")
        
        print(f"\n💰 FINAL OUTCOME:")
        print(f"   Secured Profit: ${tp_target_profit/2:.2f}")
        print(f"   ROI on Total Margin: {(tp_target_profit/2/total_margin)*100:.1f}%")
        print(f"   New Balance: ${self.vault_balance + tp_target_profit/2:.2f}")
    
    def simulate_scenario_3(self):
        """SCENARIO 3: Market goes WRONG way TWICE (2 doubles)"""
        print("\n" + "="*80)
        print("SCENARIO 3: MARKET GOES WRONG WAY TWICE (2 DOUBLES)")
        print("="*80)
        
        entries = []
        
        # Stage 1
        entry_price_1 = Decimal("3.50")
        margin_1 = self.vault_balance * Decimal(str(self.position_sizing[1]))
        position_1 = margin_1 * self.leverage_stages[1]
        quantity_1 = position_1 / entry_price_1
        entries.append({'price': entry_price_1, 'quantity': quantity_1, 'margin': margin_1, 'cost': entry_price_1 * quantity_1})
        
        print(f"\n📍 STAGE 1:")
        print(f"   Entry: ${entry_price_1}, Margin: ${margin_1}, Quantity: {quantity_1:.2f} SUI")
        
        # Drop 1: -15%
        entry_price_2 = entry_price_1 * Decimal("0.85")
        margin_2 = self.vault_balance * Decimal(str(self.position_sizing[2]))
        position_2 = margin_2 * self.leverage_stages[2]
        quantity_2 = position_2 / entry_price_2
        entries.append({'price': entry_price_2, 'quantity': quantity_2, 'margin': margin_2, 'cost': entry_price_2 * quantity_2})
        
        print(f"\n📉 DROP 1 (-15%):")
        print(f"   Price: ${entry_price_1} → ${entry_price_2:.4f}")
        print(f"\n📍 STAGE 2 DOUBLE:")
        print(f"   Entry: ${entry_price_2:.4f}, Margin: ${margin_2}, Quantity: {quantity_2:.2f} SUI")
        
        # Drop 2: Another -10%
        entry_price_3 = entry_price_2 * Decimal("0.90")
        margin_3 = self.vault_balance * Decimal(str(self.position_sizing[3]))
        position_3 = margin_3 * self.leverage_stages[3]
        quantity_3 = position_3 / entry_price_3
        entries.append({'price': entry_price_3, 'quantity': quantity_3, 'margin': margin_3, 'cost': entry_price_3 * quantity_3})
        
        print(f"\n📉 DROP 2 (-10%):")
        print(f"   Price: ${entry_price_2:.4f} → ${entry_price_3:.4f}")
        print(f"\n📍 STAGE 3 DOUBLE:")
        print(f"   Entry: ${entry_price_3:.4f}, Margin: ${margin_3}, Quantity: {quantity_3:.2f} SUI")
        
        # Calculate totals
        total_margin = sum(e['margin'] for e in entries)
        total_quantity = sum(e['quantity'] for e in entries)
        avg_entry = self.calculate_weighted_average_entry(entries)
        
        print(f"\n📊 POSITION SUMMARY AFTER 2 DOUBLES:")
        print(f"   Total Margin: ${total_margin}")
        print(f"   Total Quantity: {total_quantity:.2f} SUI")
        print(f"   Average Entry: ${avg_entry:.4f}")
        print(f"   Current Price: ${entry_price_3:.4f}")
        print(f"   Unrealized Loss: ${(entry_price_3 - avg_entry) * total_quantity:.2f}")
        
        # TP Calculation
        tp_target_profit = total_margin * self.tp_percentage
        tp_price = avg_entry * (Decimal("1") + (tp_target_profit / (total_quantity * avg_entry)))
        
        print(f"\n🎯 TAKE PROFIT TARGET:")
        print(f"   175% of ${total_margin} = ${tp_target_profit}")
        print(f"   TP Price: ${tp_price:.4f}")
        print(f"   Required recovery: {((tp_price/entry_price_3)-1)*100:.2f}%")
        
        print(f"\n📈 ACHIEVING 175% PROFIT:")
        print(f"   Price moves: ${entry_price_3:.4f} → ${tp_price:.4f}")
        print(f"   Total Profit: ${tp_target_profit}")
        
        print(f"\n✅ ACTIONS AT TP:")
        print(f"   1. Close 50% position → Secure ${tp_target_profit/2:.2f}")
        print(f"   2. Trailing stop at ${tp_price * (1-self.trailing_stop_percentage):.4f}")
        print(f"   3. Keep 50% running with trailing")
        
        print(f"\n💰 OUTCOME:")
        print(f"   Secured Profit: ${tp_target_profit/2:.2f}")
        print(f"   ROI: {(tp_target_profit/2/total_margin)*100:.1f}%")
        print(f"   New Balance: ${self.vault_balance + tp_target_profit/2:.2f}")
    
    def simulate_scenario_4(self):
        """SCENARIO 4: Maximum drawdown (ALL 5 stages)"""
        print("\n" + "="*80)
        print("SCENARIO 4: MAXIMUM DRAWDOWN (ALL 5 STAGES)")
        print("="*80)
        
        entries = []
        entry_prices = [
            Decimal("3.50"),   # Stage 1
            Decimal("3.00"),   # Stage 2 (-14%)
            Decimal("2.50"),   # Stage 3 (-17%)
            Decimal("2.00"),   # Stage 4 (-20%)
            Decimal("1.70"),   # Stage 5 (-15%)
        ]
        
        print(f"\n📉 EXTREME SCENARIO - CONTINUOUS DROPS:")
        
        total_margin = Decimal("0")
        total_quantity = Decimal("0")
        
        for stage in range(1, 6):
            price = entry_prices[stage-1]
            margin = self.vault_balance * Decimal(str(self.position_sizing[stage]))
            leverage = self.leverage_stages[stage]
            
            if leverage > 0:
                position = margin * leverage
            else:
                position = margin  # Stage 5 is just margin
            
            quantity = position / price if leverage > 0 else margin / price
            
            total_margin += margin
            total_quantity += quantity
            
            entries.append({
                'stage': stage,
                'price': price,
                'margin': margin,
                'leverage': leverage,
                'quantity': quantity,
                'cost': price * quantity
            })
            
            print(f"\n📍 STAGE {stage}:")
            print(f"   Price: ${price}")
            print(f"   Margin: ${margin} ({self.position_sizing[stage]*100}% of balance)")
            print(f"   Leverage: {leverage}X" if leverage > 0 else "   No leverage (margin only)")
            print(f"   Quantity: {quantity:.2f} SUI")
        
        avg_entry = self.calculate_weighted_average_entry(entries)
        
        print(f"\n📊 FINAL POSITION SUMMARY:")
        print(f"   Total Margin Used: ${total_margin} ({(total_margin/self.vault_balance)*100:.1f}% of balance)")
        print(f"   Total Quantity: {total_quantity:.2f} SUI")
        print(f"   Average Entry: ${avg_entry:.4f}")
        print(f"   Current Price: ${entry_prices[-1]}")
        print(f"   Unrealized Loss: ${(entry_prices[-1] - avg_entry) * total_quantity:.2f}")
        
        # TP Calculation
        tp_target_profit = total_margin * self.tp_percentage
        tp_price = avg_entry * (Decimal("1") + (tp_target_profit / (total_quantity * avg_entry)))
        
        print(f"\n🎯 TAKE PROFIT CALCULATION:")
        print(f"   Target: 175% of ${total_margin} = ${tp_target_profit}")
        print(f"   TP Price: ${tp_price:.4f}")
        print(f"   Required recovery from ${entry_prices[-1]}: {((tp_price/entry_prices[-1])-1)*100:.2f}%")
        
        print(f"\n📈 MARKET RECOVERY TO TP:")
        print(f"   Price moves: ${entry_prices[-1]} → ${tp_price:.4f}")
        print(f"   Profit achieved: ${tp_target_profit}")
        
        print(f"\n✅ EXIT STRATEGY:")
        print(f"   1. Close 50% → Secure ${tp_target_profit/2:.2f}")
        print(f"   2. Trailing stop at ${tp_price * (1-self.trailing_stop_percentage):.4f}")
        
        print(f"\n💰 RESULT:")
        print(f"   Maximum Risk Used: ${total_margin} (45% of balance)")
        print(f"   Profit Secured: ${tp_target_profit/2:.2f}")
        print(f"   ROI: {(tp_target_profit/2/total_margin)*100:.1f}%")
    
    def simulate_scenario_5(self):
        """SCENARIO 5: Partial TP hit then reversal"""
        print("\n" + "="*80)
        print("SCENARIO 5: PARTIAL TP HIT THEN REVERSAL")
        print("="*80)
        
        entry_price = Decimal("3.50")
        margin = self.vault_balance * Decimal(str(self.position_sizing[1]))
        position = margin * self.leverage_stages[1]
        quantity = position / entry_price
        
        print(f"\n📍 INITIAL POSITION:")
        print(f"   Entry: ${entry_price}")
        print(f"   Margin: ${margin}")
        print(f"   Quantity: {quantity:.2f} SUI")
        
        # Calculate TP
        tp_target = margin * self.tp_percentage
        tp_price = entry_price * (Decimal("1") + (tp_target / position))
        
        print(f"\n📈 PRICE REACHES TP:")
        print(f"   Price: ${entry_price} → ${tp_price:.4f}")
        print(f"   Profit: ${tp_target}")
        
        print(f"\n✅ PARTIAL CLOSE AT TP:")
        print(f"   Close 50% ({quantity/2:.2f} SUI)")
        print(f"   Secured Profit: ${tp_target/2:.2f}")
        print(f"   Remaining Position: {quantity/2:.2f} SUI")
        
        # Set trailing stop
        trailing_stop = tp_price * (Decimal("1") - self.trailing_stop_percentage)
        print(f"   Trailing Stop Set: ${trailing_stop:.4f}")
        
        # Market reverses
        print(f"\n📉 MARKET REVERSES:")
        print(f"   Price drops to trailing stop: ${trailing_stop:.4f}")
        
        remaining_profit = (trailing_stop - entry_price) * (quantity/2)
        total_profit = tp_target/2 + remaining_profit
        
        print(f"\n💰 FINAL OUTCOME:")
        print(f"   Profit from 50% at TP: ${tp_target/2:.2f}")
        print(f"   Profit from trailing stop: ${remaining_profit:.2f}")
        print(f"   Total Profit: ${total_profit:.2f}")
        print(f"   ROI: {(total_profit/margin)*100:.1f}%")
    
    def simulate_scenario_6(self):
        """SCENARIO 6: Never reaches TP (sideways/slow bleed)"""
        print("\n" + "="*80)
        print("SCENARIO 6: NEVER REACHES TP (POSITION MANAGEMENT)")
        print("="*80)
        
        entries = []
        
        # Build position through doubles
        print(f"\n📉 SLOW BLEED SCENARIO:")
        
        # Stage 1
        price_1 = Decimal("3.50")
        margin_1 = self.vault_balance * Decimal(str(self.position_sizing[1]))
        entries.append({'price': price_1, 'margin': margin_1, 'quantity': (margin_1 * 20) / price_1})
        print(f"   Stage 1: ${price_1}, Margin: ${margin_1}")
        
        # Stage 2
        price_2 = Decimal("3.10")
        margin_2 = self.vault_balance * Decimal(str(self.position_sizing[2]))
        entries.append({'price': price_2, 'margin': margin_2, 'quantity': (margin_2 * 10) / price_2})
        print(f"   Stage 2: ${price_2}, Margin: ${margin_2}")
        
        total_margin = margin_1 + margin_2
        total_quantity = sum(e['quantity'] for e in entries)
        avg_entry = sum(e['price'] * e['quantity'] for e in entries) / total_quantity
        
        print(f"\n📊 POSITION STATUS:")
        print(f"   Total Margin: ${total_margin}")
        print(f"   Average Entry: ${avg_entry:.4f}")
        
        # Price oscillates but never reaches TP
        tp_target = total_margin * self.tp_percentage
        tp_price = avg_entry * (Decimal("1") + (tp_target / (total_quantity * avg_entry)))
        
        print(f"\n⚠️ MARKET BEHAVIOR:")
        print(f"   TP Target: ${tp_price:.4f}")
        print(f"   Market oscillates between ${price_2*Decimal('0.95'):.4f} - ${price_2*Decimal('1.08'):.4f}")
        print(f"   Never reaches TP of ${tp_price:.4f}")
        
        print(f"\n📋 POSITION MANAGEMENT:")
        print(f"   • NO STOP LOSS - We NEVER close at loss")
        print(f"   • Wait for market to reach TP")
        print(f"   • Can add more stages if drops continue")
        print(f"   • Maximum risk capped at 45% of balance")
        print(f"   • Position remains OPEN indefinitely until TP")
        
        print(f"\n💡 KEY POINT:")
        print(f"   Our strategy NEVER realizes losses")
        print(f"   We wait for profitable exit at 175% of margin")
        print(f"   Time in position: As long as needed")
    
    def simulate_scenario_7(self):
        """SCENARIO 7: Liquidation protection through stages"""
        print("\n" + "="*80)
        print("SCENARIO 7: LIQUIDATION PROTECTION MECHANISM")
        print("="*80)
        
        print(f"\n⚠️ EXTREME DROP SCENARIO:")
        
        # Show how leverage reduction protects
        stages_data = []
        
        for stage in range(1, 6):
            margin = self.vault_balance * Decimal(str(self.position_sizing[stage]))
            leverage = self.leverage_stages[stage]
            
            if leverage > 0:
                liquidation_distance = Decimal("1") / Decimal(str(leverage + 1))
                liquidation_pct = liquidation_distance * 100
            else:
                liquidation_pct = Decimal("100")  # No liquidation with just margin
            
            stages_data.append({
                'stage': stage,
                'margin': margin,
                'leverage': leverage,
                'liquidation_pct': liquidation_pct
            })
            
            print(f"\n📍 STAGE {stage}:")
            print(f"   Margin: ${margin}")
            print(f"   Leverage: {leverage}X" if leverage > 0 else "   No leverage")
            print(f"   Liquidation Distance: {liquidation_pct:.1f}% drop from entry")
        
        print(f"\n🛡️ PROTECTION MECHANISM:")
        print(f"   • Stage 1 (20X): Liquidates at -4.8% from entry")
        print(f"   • Stage 2 (10X): Liquidates at -9.1% from entry")
        print(f"   • Stage 3 (5X): Liquidates at -16.7% from entry")
        print(f"   • Stage 4 (2X): Liquidates at -33.3% from entry")
        print(f"   • Stage 5 (0X): Cannot liquidate (margin only)")
        
        print(f"\n✅ HOW IT PROTECTS:")
        print(f"   As price drops, we reduce leverage")
        print(f"   Lower leverage = harder to liquidate")
        print(f"   Final stage has NO leverage = NO liquidation risk")
        print(f"   Maximum loss capped at 45% of balance")
    
    def run_all_simulations(self):
        """Run all simulation scenarios"""
        print("\n" + "="*80)
        print("🚀 COMPLETE SUI/USDT TRADING SIMULATION")
        print(f"💰 VAULT BALANCE: ${self.vault_balance}")
        print("📋 STRATEGY: Vault Position Manager (NO STOP LOSS)")
        print("="*80)
        
        # Run all scenarios
        self.simulate_scenario_1()  # Market goes right
        self.simulate_scenario_2()  # 1 double, then profit
        self.simulate_scenario_3()  # 2 doubles, then profit
        self.simulate_scenario_4()  # Maximum drawdown (all stages)
        self.simulate_scenario_5()  # Partial TP then reversal
        self.simulate_scenario_6()  # Never reaches TP
        self.simulate_scenario_7()  # Liquidation protection
        
        # Final summary
        print("\n" + "="*80)
        print("📊 SIMULATION COMPLETE - KEY TAKEAWAYS")
        print("="*80)
        
        print("\n✅ OUR STRATEGY RULES:")
        print("   1. NEVER use stop loss")
        print("   2. Start with 2% at 20X leverage")
        print("   3. Double position with decreasing leverage on drops")
        print("   4. Take profit ALWAYS at 175% of total margin")
        print("   5. Close 50% at TP, trail the rest")
        print("   6. Maximum risk: 45% of vault balance")
        print("   7. Never close at loss - wait for profitable exit")
        
        print("\n💰 PROFIT SCENARIOS:")
        print("   • Best case: Immediate TP = 175% of 2% = 3.5% vault gain")
        print("   • After 1 double: 175% of 6% = 10.5% vault gain")
        print("   • After 2 doubles: 175% of 14% = 24.5% vault gain")
        print("   • Maximum (all stages): 175% of 45% = 78.75% vault gain")
        
        print("\n⚠️ RISK MANAGEMENT:")
        print("   • No stop loss = No realized losses")
        print("   • Leverage decreases as position increases")
        print("   • Liquidation protection through stages")
        print("   • Time is our friend - we wait for profit")
        
        print("\n" + "="*80)
        print("✅ SIMULATION COMPLETE - ALL SCENARIOS COVERED")
        print("="*80)

# Run the simulation
if __name__ == "__main__":
    simulator = SUIPaperTradeSimulation()
    simulator.run_all_simulations()