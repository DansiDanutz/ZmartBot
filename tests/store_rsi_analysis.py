#!/usr/bin/env python3
"""
Script to store RSI heatmap analysis in Airtable
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
    
    async def store_rsi_heatmap_analysis(self):
        """Store RSI heatmap analysis in Airtable"""
        
        # Read the analysis content
        with open('RSI_HEATMAP_ANALYSIS.md', 'r') as f:
            analysis_content = f.read()
        
        # Create the record
        record = {
            "fields": {
                "Symbol": "RSI_HEATMAP",
                "RSI_Heatmap": analysis_content,
                "LiqRatios_long_term": json.dumps({
                    "analysis_type": "rsi_heatmap",
                    "market_sentiment": "neutral_to_slightly_bullish",
                    "confidence_level": 70,
                    "total_assets_analyzed": 40,
                    "rsi_regions": {
                        "overbought": {
                            "count": 1,
                            "assets": ["ASR"],
                            "avg_rsi": 75
                        },
                        "strong": {
                            "count": 4,
                            "assets": ["VINE", "OMNI", "TRX", "ZORA"],
                            "avg_rsi": 63
                        },
                        "neutral": {
                            "count": 25,
                            "assets": ["ETH", "BNB", "HYPERGOD", "LINK", "UNI"],
                            "avg_rsi": 50
                        },
                        "weak": {
                            "count": 8,
                            "assets": ["XRP", "DOGE", "1000PEPE", "AAVE"],
                            "avg_rsi": 35
                        },
                        "oversold": {
                            "count": 1,
                            "assets": ["TREE"],
                            "avg_rsi": 5
                        }
                    }
                }),
                "LiqRatios_short_term": json.dumps({
                    "overall_sentiment": "neutral_to_slightly_bullish",
                    "confidence": 70,
                    "risk_level": "medium",
                    "timeframe": "4H-1D",
                    "key_observations": {
                        "market_balance": "Most assets in neutral region",
                        "selective_strength": "Limited strong momentum assets",
                        "controlled_extremes": "Minimal overbought/oversold",
                        "premium_warning": "SR600CAT marked as premium"
                    }
                }),
                "Liquidation_Map": json.dumps({
                    "analysis_complete": True,
                    "rsi_focus": True
                }),
                "Lie_Heatmap": json.dumps({
                    "total_assets": 40,
                    "region_distribution": {
                        "overbought": 1,
                        "strong": 4,
                        "neutral": 25,
                        "weak": 8,
                        "oversold": 1
                    },
                    "market_structure": "balanced_consolidation",
                    "momentum_profile": "selective_strength"
                }),
                "Result": json.dumps({
                    "trading_recommendation": "NEUTRAL TO SLIGHTLY BULLISH with selective positioning",
                    "entry_strategy": "Focus on neutral-to-strong transitions",
                    "stop_loss_strategy": "Tight stops for overbought, wider for oversold",
                    "risk_management": "Conservative position sizing due to mixed signals"
                }),
                "24h48h": "70%",
                "7days": "70%",
                "1Month": "neutral_to_slightly_bullish",
                "Score(24h48h_7Days_1Month)": "2.80"
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
                    print("✅ RSI heatmap analysis stored successfully!")
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
    """Main function to store RSI analysis"""
    print("🚀 Starting RSI Heatmap Analysis Storage...")
    print("=" * 50)
    
    storage = AirtableStorage()
    success = await storage.store_rsi_heatmap_analysis()
    
    if success:
        print("\n✅ RSI Heatmap Analysis successfully stored in Airtable!")
        print("📊 Analysis includes:")
        print("   - Comprehensive RSI region analysis")
        print("   - Market sentiment assessment")
        print("   - Asset-specific momentum analysis")
        print("   - Trading recommendations")
        print("\n🎯 Ready for next image analysis!")
    else:
        print("\n❌ Failed to store RSI analysis in Airtable")
        print("Please check the error details above")

if __name__ == "__main__":
    asyncio.run(main()) 