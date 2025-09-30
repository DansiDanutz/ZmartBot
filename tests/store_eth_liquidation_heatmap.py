#!/usr/bin/env python3
"""
Script to store ETH Liquidation Heatmap analysis in Airtable
"""

import asyncio
import json
import httpx
from datetime import datetime

class AirtableStorage:
    def __init__(self):
        self.api_key = "patcE6fQFEu7sDjmd.3f556799e233829b3aef09d9387bc3ada86c8eb7eb74616076d90f7f11b70835"
        self.base_id = "appAs9sZH7OmtYaTJ"
        self.table_name = "KingFisher"
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def store_eth_liquidation_heatmap_analysis(self):
        """Store ETH Liquidation Heatmap analysis in Airtable"""
        
        # Read the analysis content
        with open('ETH_LIQUIDATION_HEATMAP_ANALYSIS.md', 'r') as f:
            analysis_content = f.read()
        
        # Create the record
        record = {
            "fields": {
                "Symbol": "ETHUSDT",
                "Liq_Heatmap": analysis_content,
                "LiqRatios_long_term": json.dumps({
                    "analysis_type": "liquidation_heatmap",
                    "market_sentiment": "neutral_to_slightly_bullish",
                    "confidence_level": 75,
                    "price_range": {
                        "low": 2700,
                        "high": 4300,
                        "current": 3700
                    },
                    "liquidation_zones": {
                        "lower_range": {
                            "price_range": "2700-3300",
                            "density": "very_high",
                            "type": "short_liquidation_cluster",
                            "risk_level": "high"
                        },
                        "mid_range": {
                            "price_range": "3300-3700",
                            "density": "high_to_moderate",
                            "type": "mixed_liquidation_pressure",
                            "risk_level": "medium_high"
                        },
                        "upper_range": {
                            "price_range": "3700-4300",
                            "density": "moderate_to_low",
                            "type": "long_liquidation_accumulation",
                            "risk_level": "medium"
                        }
                    },
                    "critical_levels": {
                        "major_support": "2900-3000",
                        "current_level": "3700",
                        "major_resistance": "3800-3900",
                        "upper_resistance": "4100-4300"
                    }
                }),
                "LiqRatios_short_term": json.dumps({
                    "overall_sentiment": "neutral_to_slightly_bullish",
                    "confidence": 75,
                    "risk_level": "high",
                    "timeframe": "4H-1D",
                    "key_levels": {
                        "support": "3700",
                        "resistance": "3800",
                        "major_support": "2900-3000",
                        "major_resistance": "4100-4300"
                    },
                    "liquidation_pressure": {
                        "short_pressure": "high_below_3300",
                        "long_pressure": "building_above_3800",
                        "current_status": "mixed_signals"
                    }
                }),
                "Liquidation_Map": json.dumps({
                    "analysis_complete": True,
                    "heatmap_focus": True
                }),
                "RSI_Heatmap": json.dumps({
                    "analysis_complete": True,
                    "liquidation_focus": True
                }),
                "Result": json.dumps({
                    "trading_recommendation": "NEUTRAL TO SLIGHTLY BULLISH with cautious positioning",
                    "entry_strategy": "Wait for clear breakout above 3800",
                    "stop_loss_strategy": "Tight stops due to high liquidation density",
                    "risk_management": "Conservative position sizing"
                }),
                "24h48h": "75%",
                "7days": "75%",
                "1Month": "neutral_to_slightly_bullish",
                "Score(24h48h_7Days_1Month)": "3.00"
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=record
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ ETH Liquidation Heatmap analysis stored successfully!")
                    print(f"📝 Record ID: {result.get('id')}")
                    print(f"🕒 Timestamp: {datetime.now().isoformat()}")
                    return True
                else:
                    print(f"❌ Failed to store analysis: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error storing analysis: {str(e)}")
            return False

async def main():
    """Main function to store ETH Liquidation Heatmap analysis"""
    print("🚀 Starting ETH Liquidation Heatmap Analysis Storage...")
    print("=" * 50)
    
    storage = AirtableStorage()
    success = await storage.store_eth_liquidation_heatmap_analysis()
    
    if success:
        print("\n✅ ETH Liquidation Heatmap Analysis successfully stored in Airtable!")
        print("📊 Analysis includes:")
        print("   - Comprehensive liquidation heatmap analysis")
        print("   - Price action and market structure analysis")
        print("   - Critical liquidation levels identification")
        print("   - Trading recommendations and risk management")
        print("\n🎯 Ready for next image analysis!")
    else:
        print("\n❌ Failed to store ETH Liquidation Heatmap analysis in Airtable")
        print("Please check the error details above")

if __name__ == "__main__":
    asyncio.run(main()) 