#!/usr/bin/env python3
"""
Script to store ETH liquidation map analysis in Airtable
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
    
    async def store_eth_liquidation_analysis(self):
        """Store ETH liquidation map analysis in Airtable"""
        
        # Read the analysis content
        with open('ETH_LIQUIDATION_MAP_ANALYSIS.md', 'r') as f:
            analysis_content = f.read()
        
        # Create the record
        record = {
            "fields": {
                "Symbol": "ETHUSDT",
                "Liquidation_Map": analysis_content,
                "LiqRatios_long_term": json.dumps({
                    "analysis_type": "liquidation_map",
                    "market_sentiment": "bullish",
                    "confidence_level": 85,
                    "current_price": 3764.60,
                    "price_range": {
                        "low": 2440.90,
                        "high": 5509.40
                    },
                    "clusters": {
                        "primary": {
                            "location": "2440.90 - 3122.80",
                            "density": "very_high",
                            "sentiment": "bearish_pressure"
                        },
                        "secondary": {
                            "location": "3122.80 - 3804.70",
                            "density": "high",
                            "sentiment": "transition_zone"
                        },
                        "tertiary": {
                            "location": "4145.60 - 5509.40",
                            "density": "moderate_low",
                            "sentiment": "bullish_pressure"
                        }
                    }
                }),
                "LiqRatios_short_term": json.dumps({
                    "overall_sentiment": "bullish",
                    "confidence": 85,
                    "risk_level": "high",
                    "timeframe": "4H-1D",
                    "key_levels": {
                        "support": "2440.90 - 3122.80",
                        "resistance": "4145.60 - 5509.40",
                        "critical": 3804.70
                    }
                }),
                "RSI_Heatmap": json.dumps({
                    "analysis_complete": True,
                    "liquidation_focus": True
                }),
                "Lie_Heatmap": json.dumps({
                    "total_clusters": 3,
                    "cluster_density": "very_high",
                    "market_structure": "bullish_bias",
                    "current_position": "critical_transition"
                }),
                "Result": json.dumps({
                    "trading_recommendation": "BULLISH BIAS with cautious entry timing",
                    "entry_strategy": "Wait for clear breakout above 3804.70",
                    "stop_loss_strategy": "Tight stops due to cluster proximity",
                    "risk_management": "Conservative position sizing"
                }),
                "24h48h": "85%",
                "7days": "85%",
                "1Month": "bullish",
                "Score(24h48h_7Days_1Month)": "3.25"
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
                    print("✅ ETH liquidation analysis stored successfully!")
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
    """Main function to store ETH analysis"""
    print("🚀 Starting ETH Liquidation Analysis Storage...")
    print("=" * 50)
    
    storage = AirtableStorage()
    success = await storage.store_eth_liquidation_analysis()
    
    if success:
        print("\n✅ ETH Liquidation Map Analysis successfully stored in Airtable!")
        print("📊 Analysis includes:")
        print("   - Comprehensive cluster analysis")
        print("   - Market sentiment assessment")
        print("   - Trading recommendations")
        print("   - Risk management guidelines")
        print("\n🎯 Ready for next image analysis!")
    else:
        print("\n❌ Failed to store ETH analysis in Airtable")
        print("Please check the error details above")

if __name__ == "__main__":
    asyncio.run(main()) 