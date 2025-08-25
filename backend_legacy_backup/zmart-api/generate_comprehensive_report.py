#!/usr/bin/env python3
"""
Generate Comprehensive Symbol Report
Creates a detailed report including all symbol data, alerts, and Bollinger Bands analysis
"""

import sqlite3
import os
from datetime import datetime

def generate_comprehensive_report():
    """Generate a comprehensive report of all symbol data"""
    try:
        db_path = 'my_symbols_v2.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all active symbols with their data
        cursor.execute("""
            SELECT 
                s.symbol,
                s.root_symbol,
                pc.weight_percentage,
                pc.status,
                pc.updated_at,
                (SELECT COUNT(*) FROM symbol_alerts sa WHERE sa.symbol = s.symbol AND sa.is_active = 1) as alert_count,
                (SELECT COUNT(*) FROM bollinger_bands bb WHERE bb.symbol = s.symbol) as bb_count
            FROM symbols s
            JOIN portfolio_composition pc ON s.id = pc.symbol_id
            WHERE pc.status = 'Active'
            ORDER BY s.symbol
        """)
        
        symbols_data = cursor.fetchall()
        
        if not symbols_data:
            print("📊 No active symbols found in database")
            return
        
        print("\n" + "="*100)
        print("📊 ZMARTBOT COMPREHENSIVE SYMBOL REPORT")
        print("="*100)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)
        
        # Summary statistics
        total_symbols = len(symbols_data)
        total_alerts = sum(row[5] for row in symbols_data)
        total_bb_data = sum(row[6] for row in symbols_data)
        
        print(f"\n📈 SUMMARY STATISTICS:")
        print(f"   • Total Active Symbols: {total_symbols}")
        print(f"   • Total Active Alerts: {total_alerts}")
        print(f"   • Total Bollinger Bands Data Points: {total_bb_data}")
        print(f"   • Average Alerts per Symbol: {total_alerts/total_symbols:.1f}")
        print(f"   • Average BB Data Points per Symbol: {total_bb_data/total_symbols:.1f}")
        
        print("\n" + "="*100)
        print("🔸 DETAILED SYMBOL ANALYSIS")
        print("="*100)
        
        for row in symbols_data:
            symbol, root_symbol, weight, status, last_updated, alert_count, bb_count = row
            
            print(f"\n🔸 {symbol} ({root_symbol})")
            print("-" * 60)
            print(f"   📊 Weight: {weight}% | Status: {status}")
            print(f"   📊 Alerts: {alert_count} active | BB Data: {bb_count} timeframes")
            print(f"   📊 Last Updated: {last_updated}")
            
            # Get alerts for this symbol
            cursor.execute("""
                SELECT timeframe, condition, threshold, last_triggered
                FROM symbol_alerts 
                WHERE symbol = ? AND is_active = 1
                ORDER BY timeframe, condition
            """, (symbol,))
            
            alerts = cursor.fetchall()
            if alerts:
                print(f"   🚨 Active Alerts:")
                for alert in alerts:
                    timeframe, condition, threshold, last_triggered = alert
                    print(f"      • {timeframe} {condition} ${threshold:,.2f}")
                    if last_triggered:
                        print(f"        Last triggered: {last_triggered}")
            
            # Get Bollinger Bands data for this symbol
            cursor.execute("""
                SELECT timeframe, sma, upper_band, lower_band, bandwidth, position, current_price
                FROM bollinger_bands 
                WHERE symbol = ?
                ORDER BY timeframe
            """, (symbol,))
            
            bb_data = cursor.fetchall()
            if bb_data:
                print(f"   📊 Bollinger Bands Analysis:")
                for bb in bb_data:
                    timeframe, sma, upper_band, lower_band, bandwidth, position, current_price = bb
                    
                    # Determine position status
                    if position <= 20:
                        position_status = "🟢 Near Support"
                    elif position >= 80:
                        position_status = "🔴 Near Resistance"
                    else:
                        position_status = "⚪ Middle Range"
                    
                    # Determine bandwidth status
                    if bandwidth > 5:
                        bandwidth_status = "🟠 High Volatility"
                    elif bandwidth < 1:
                        bandwidth_status = "🔵 Low Volatility"
                    else:
                        bandwidth_status = "⚪ Normal Volatility"
                    
                    print(f"      • {timeframe}: Position {position:.1f}% ({position_status}) | Bandwidth {bandwidth:.2f}% ({bandwidth_status})")
                    print(f"        SMA: ${sma:,.2f} | Upper: ${upper_band:,.2f} | Lower: ${lower_band:,.2f}")
        
        print("\n" + "="*100)
        print("🚨 ALERT SUMMARY BY TIMEFRAME")
        print("="*100)
        
        # Get alert summary by timeframe
        cursor.execute("""
            SELECT timeframe, COUNT(*) as count
            FROM symbol_alerts 
            WHERE is_active = 1
            GROUP BY timeframe
            ORDER BY timeframe
        """)
        
        timeframe_alerts = cursor.fetchall()
        for timeframe, count in timeframe_alerts:
            print(f"   • {timeframe}: {count} alerts")
        
        print("\n" + "="*100)
        print("📊 BOLLINGER BANDS VOLATILITY ANALYSIS")
        print("="*100)
        
        # Get volatility analysis
        cursor.execute("""
            SELECT 
                symbol,
                timeframe,
                bandwidth,
                position,
                CASE 
                    WHEN bandwidth > 5 THEN 'High'
                    WHEN bandwidth < 1 THEN 'Low'
                    ELSE 'Normal'
                END as volatility_level,
                CASE 
                    WHEN position <= 20 THEN 'Support'
                    WHEN position >= 80 THEN 'Resistance'
                    ELSE 'Middle'
                END as position_level
            FROM bollinger_bands
            ORDER BY symbol, timeframe
        """)
        
        volatility_data = cursor.fetchall()
        
        # Group by volatility level
        high_volatility = [row for row in volatility_data if row[4] == 'High']
        low_volatility = [row for row in volatility_data if row[4] == 'Low']
        normal_volatility = [row for row in volatility_data if row[4] == 'Normal']
        
        print(f"   🟠 High Volatility ({len(high_volatility)} instances):")
        for row in high_volatility:
            symbol, timeframe, bandwidth, position, vol_level, pos_level = row
            print(f"      • {symbol} {timeframe}: {bandwidth:.2f}% bandwidth, {position:.1f}% position ({pos_level})")
        
        print(f"\n   🔵 Low Volatility ({len(low_volatility)} instances):")
        for row in low_volatility:
            symbol, timeframe, bandwidth, position, vol_level, pos_level = row
            print(f"      • {symbol} {timeframe}: {bandwidth:.2f}% bandwidth, {position:.1f}% position ({pos_level})")
        
        print(f"\n   ⚪ Normal Volatility ({len(normal_volatility)} instances):")
        for row in normal_volatility:
            symbol, timeframe, bandwidth, position, vol_level, pos_level = row
            print(f"      • {symbol} {timeframe}: {bandwidth:.2f}% bandwidth, {position:.1f}% position ({pos_level})")
        
        print("\n" + "="*100)
        print("🎯 TRADING OPPORTUNITIES")
        print("="*100)
        
        # Find potential trading opportunities
        cursor.execute("""
            SELECT symbol, timeframe, position, bandwidth
            FROM bollinger_bands
            WHERE position <= 15 OR position >= 85
            ORDER BY symbol, timeframe
        """)
        
        opportunities = cursor.fetchall()
        
        if opportunities:
            print("   🚨 Potential Breakout Signals:")
            for opp in opportunities:
                symbol, timeframe, position, bandwidth = opp
                if position <= 15:
                    signal_type = "🟢 BUY (Near Support)"
                else:
                    signal_type = "🔴 SELL (Near Resistance)"
                print(f"      • {symbol} {timeframe}: {signal_type} - Position {position:.1f}%")
        else:
            print("   ✅ No immediate breakout signals detected")
        
        # Find high volatility opportunities
        cursor.execute("""
            SELECT symbol, timeframe, bandwidth
            FROM bollinger_bands
            WHERE bandwidth > 10
            ORDER BY bandwidth DESC
        """)
        
        high_vol_opps = cursor.fetchall()
        
        if high_vol_opps:
            print(f"\n   🟠 High Volatility Opportunities (Bandwidth > 10%):")
            for opp in high_vol_opps:
                symbol, timeframe, bandwidth = opp
                print(f"      • {symbol} {timeframe}: {bandwidth:.2f}% bandwidth")
        
        conn.close()
        
        print("\n" + "="*100)
        print("✅ Report generation completed successfully!")
        print("="*100)
        
    except Exception as e:
        print(f"❌ Error generating comprehensive report: {e}")

if __name__ == "__main__":
    generate_comprehensive_report()
