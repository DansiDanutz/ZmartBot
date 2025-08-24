#!/usr/bin/env python3
"""
STEP 6 ENHANCED: Generate Professional Trading Reports with Win Rate Analysis
Advanced version with better win rate extraction and continuous monitoring
"""

import os
import sys
import json
import re
import time
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from dotenv import load_dotenv
import aiohttp
import pytz

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID', 'appAs9sZH7OmtYaTJ')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'KingFisher')

# Paths
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / 'downloads'
MD_REPORTS_DIR = DOWNLOADS_DIR / 'MD Reports'
HISTORY_DIR = BASE_DIR / 'HistoryData'

# Ensure directories exist
MD_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

class EnhancedReportGenerator:
    def __init__(self):
        self.openai_key = OPENAI_API_KEY
        self.airtable_key = AIRTABLE_API_KEY
        self.airtable_base = AIRTABLE_BASE_ID
        self.airtable_table = AIRTABLE_TABLE_NAME
        self.processed_symbols = set()
        
    async def fetch_all_symbol_data(self) -> List[Dict[str, Any]]:
        """Fetch all symbols with their complete data from Airtable"""
        url = f"https://api.airtable.com/v0/{self.airtable_base}/{self.airtable_table}"
        headers = {
            "Authorization": f"Bearer {self.airtable_key}",
            "Content-Type": "application/json"
        }
        
        all_records = []
        offset = None
        
        async with aiohttp.ClientSession() as session:
            while True:
                params = {}
                if offset:
                    params['offset'] = offset
                
                try:
                    async with session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            all_records.extend(data['records'])
                            
                            # Check if there are more records
                            offset = data.get('offset')
                            if not offset:
                                break
                        else:
                            print(f"Error fetching data: {response.status}")
                            break
                except Exception as e:
                    print(f"Error: {e}")
                    break
        
        return all_records
    
    def create_reference_prompt(self) -> str:
        """Create the reference prompt for Manus-style reports"""
        return """
        You are Manus AI, a professional cryptocurrency trading analyst. Create a comprehensive professional trading report 
        following this EXACT structure and style:
        
        # Final [SYMBOL]/USDT Trading Report: Market Analysis
        ## [Current Date] - Strategic Implications and Win Rate Analysis
        
        **Author:** Manus AI  
        **Date:** [Current Date]  
        **Analysis Period:** [Date Range]  
        **Report Version:** 1.0  
        
        ## Executive Summary
        [Provide comprehensive market overview focusing on liquidation patterns and win rates. Include current price context and major trend direction]
        
        ## Methodology and Data Sources
        ### Data Collection Framework
        - **Kingfisher Liquidation Maps**: Real-time liquidation clustering analysis
        - **Liquidation Heatmaps**: Visual representation of leverage distribution
        - **Ratio Analysis**: Short-term (OPTI) and Long-term leverage ratios
        - **Support/Resistance Levels**: Key technical price levels
        
        ### Win Rate Calculation Methodology
        CRITICAL: Calculate win rates based on liquidation dominance:
        - If short liquidations > long liquidations: Long positions have higher win rate
        - Win rate percentage = (Dominant liquidations / Total liquidations) × 100
        - Apply this for 24h, 7d, and 1m timeframes
        
        ## Current Win Rate Analysis
        ### 24-Hour Analysis
        - **Long Position Win Rate**: [X]%
        - **Short Position Win Rate**: [Y]%
        - **Dominant Direction**: [Long/Short]
        - **Confidence Level**: [High/Medium/Low]
        [Detailed explanation of current market dynamics and liquidation patterns]
        
        ### 7-Day Projection
        - **Long Position Win Rate**: [X]%
        - **Short Position Win Rate**: [Y]%
        - **Expected Volatility**: [High/Medium/Low]
        - **Trend Strength**: [Strong/Moderate/Weak]
        [Weighted analysis incorporating current and historical data with trend continuation probability]
        
        ### 1-Month Outlook
        - **Long Position Win Rate**: [X]%
        - **Short Position Win Rate**: [Y]%
        - **Market Cycle Phase**: [Accumulation/Markup/Distribution/Markdown]
        - **Risk Profile**: [Conservative/Moderate/Aggressive]
        [Balanced perspective with trend analysis and cycle positioning]
        
        ## Cycle Target Analysis
        ### Fibonacci Extension Levels
        Based on current price and liquidation clusters:
        - **0.618 Target**: $[Price] ([X]% from current)
        - **1.000 Target**: $[Price] ([X]% from current)
        - **1.618 Target**: $[Price] ([X]% from current)
        - **2.618 Target**: $[Price] ([X]% from current)
        
        ### Critical Price Levels
        **Support Zones:**
        - Primary: $[Price] (Cluster -1)
        - Secondary: $[Price] (Cluster -2)
        
        **Resistance Zones:**
        - Primary: $[Price] (Cluster +1)
        - Secondary: $[Price] (Cluster +2)
        
        ## Strategic Trading Recommendations
        ### Long Position Strategy
        **Entry Zones:**
        - Aggressive: $[Price Range]
        - Conservative: $[Price Range]
        
        **Target Levels:**
        1. First Target: $[Price] ([X]% gain)
        2. Second Target: $[Price] ([X]% gain)
        3. Final Target: $[Price] ([X]% gain)
        
        **Stop Loss:** $[Price] ([X]% risk)
        **Risk/Reward Ratio:** [X:Y]
        
        ### Short Position Strategy
        **Entry Zones:**
        - Aggressive: $[Price Range]
        - Conservative: $[Price Range]
        
        **Target Levels:**
        1. First Target: $[Price] ([X]% gain)
        2. Second Target: $[Price] ([X]% gain)
        3. Final Target: $[Price] ([X]% gain)
        
        **Stop Loss:** $[Price] ([X]% risk)
        **Risk/Reward Ratio:** [X:Y]
        
        ## Risk Assessment and Market Outlook
        ### Current Risk Factors
        - **Liquidation Cascade Risk**: [High/Medium/Low]
        - **Volatility Assessment**: [Extreme/High/Moderate/Low]
        - **Market Sentiment**: [Extreme Greed/Greed/Neutral/Fear/Extreme Fear]
        
        ### Market Structure Analysis
        - **Trend Direction**: [Bullish/Bearish/Neutral]
        - **Momentum**: [Strong/Moderate/Weak/Diverging]
        - **Volume Profile**: [Increasing/Stable/Decreasing]
        
        ## Win Rate Summary Table
        | Timeframe | Long Win Rate | Short Win Rate | Market Sentiment | Risk Level | Recommended Position |
        |-----------|---------------|----------------|------------------|------------|---------------------|
        | 24 Hours  | X%           | Y%             | [Sentiment]      | [Level]    | [Long/Short/Neutral]|
        | 7 Days    | X%           | Y%             | [Sentiment]      | [Level]    | [Long/Short/Neutral]|
        | 1 Month   | X%           | Y%             | [Sentiment]      | [Level]    | [Long/Short/Neutral]|
        
        ## Key Takeaways
        • [Most important insight about current market condition]
        • [Key win rate observation and its implications]
        • [Critical support/resistance level to watch]
        • [Risk management recommendation]
        • [Optimal position sizing suggestion based on win rates]
        """
    
    async def generate_professional_report(
        self, record: Dict[str, Any]
    ) -> Tuple[Optional[str], Dict[str, Dict[str, float]]]:
        """Generate a Manus-style professional report"""
        fields = record['fields']
        symbol = fields.get('Symbol', 'UNKNOWN')
        
        # Prepare comprehensive context
        context = f"""
        Symbol: {symbol}
        Current Price: ${fields.get('CurrentPrice', 'N/A')}
        Last Updated: {fields.get('LastUpdated', 'N/A')}
        
        LIQUIDATION MAP ANALYSIS:
        {fields.get('LiquidationMap', 'No data available')}
        
        LIQUIDATION HEATMAP ANALYSIS:
        {fields.get('LiquidationHeatmap', 'No data available')}
        
        SHORT-TERM RATIO (OPTICAL/OPTI):
        {fields.get('ShortTermRatio', 'No data available')}
        
        LONG-TERM RATIO (ALL LEVERAGE):
        {fields.get('LongTermRatio', 'No data available')}
        
        LIQUIDATION CLUSTERS:
        - Cluster -2 (Below): ${fields.get('Liqcluster-2', 'N/A')}
        - Cluster -1 (Below): ${fields.get('Liqcluster-1', 'N/A')}
        - Cluster +1 (Above): ${fields.get('Liqcluster+1', 'N/A')}
        - Cluster +2 (Above): ${fields.get('Liqcluster+2', 'N/A')}
        
        ADDITIONAL METRICS:
        - Support Levels: {fields.get('SupportLevels', 'N/A')}
        - Resistance Levels: {fields.get('ResistanceLevels', 'N/A')}
        """
        
        reference_prompt = self.create_reference_prompt()
        
        prompt = f"""
        {reference_prompt}
        
        Based on the following data, create a comprehensive professional report:
        
        {context}
        
        CRITICAL ANALYSIS REQUIREMENTS:
        
        1. WIN RATE CALCULATION (MOST IMPORTANT):
           - Analyze the liquidation data to determine dominance
           - If more shorts are liquidated → Longs have advantage (higher win rate)
           - If more longs are liquidated → Shorts have advantage (higher win rate)
           - Calculate precise percentages for 24h, 7d, and 1m timeframes
           - Example: If 70% of liquidations are shorts, then Long win rate = 70%, Short win rate = 30%
        
        2. CYCLE TARGET ANALYSIS:
           - Use the liquidation cluster prices to calculate Fibonacci extensions
           - Project targets based on current price relative to clusters
           - Include percentage distances from current price
           - Consider both bullish and bearish scenarios
        
        3. STRATEGIC RECOMMENDATIONS:
           - Provide specific entry zones based on support/resistance
           - Calculate risk/reward ratios for each strategy
           - Include stop loss levels based on liquidation clusters
           - Suggest position sizing based on win rate confidence
        
        4. MARKET STRUCTURE:
           - Analyze the overall trend using liquidation patterns
           - Assess momentum and volume implications
           - Determine market cycle phase
           - Evaluate risk levels based on liquidation cascade potential
        
        5. PROFESSIONAL QUALITY:
           - Write in the style of an institutional research report
           - Use precise financial terminology
           - Include specific price levels and percentages
           - Provide actionable insights, not generic advice
           - Ensure the report is comprehensive (4000+ tokens)
        
        6. DATA INTERPRETATION GUIDE:
           - Liquidation clusters indicate key support/resistance levels
           - Higher leverage ratios suggest increased volatility
           - OPTI ratio shows short-term sentiment
           - Heatmap density indicates concentration of positions
        
        FORMATTING REQUIREMENTS:
        - Use the exact structure provided in the template
        - Include all sections with detailed content
        - Format numbers consistently (e.g., "86.6%" not "86.58%")
        - Use bullet points for key takeaways
        - Include the comprehensive table with all columns
        
        TONE AND STYLE:
        - Professional and authoritative
        - Data-driven and objective
        - Clear and actionable
        - Confident in analysis while acknowledging risks
        
        Generate the complete professional report now, ensuring every section is thoroughly detailed:
        """
        
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system", 
                    "content": "You are Manus AI, creating institutional-grade cryptocurrency trading reports with precise win rate calculations."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        report = result['choices'][0]['message']['content']
                        
                        # Extract win rates
                        win_rates = self.extract_win_rates_advanced(report)
                        
                        return report, win_rates
                    else:
                        error_text = await response.text()
                        print(f"OpenAI API error {response.status}: {error_text}")
                        return None, self._empty_win_rates()
            except asyncio.TimeoutError:
                print(f"Timeout generating report for {symbol}")
                return None, self._empty_win_rates()
            except Exception as e:
                print(f"Error generating report: {e}")
                return None, self._empty_win_rates()
    
    def extract_win_rates_advanced(self, report: str) -> Dict[str, Dict[str, float]]:
        """Advanced win rate extraction with multiple pattern matching"""
        win_rates = {
            "24h": {"long": 0.0, "short": 0.0},
            "7d": {"long": 0.0, "short": 0.0},
            "1m": {"long": 0.0, "short": 0.0}
        }
        
        # Convert to lowercase for matching
        report_lower = report.lower()
        
        # Multiple pattern strategies
        patterns = {
            "24h": [
                r"24[\s-]?hour.*?long.*?win.*?rate.*?(\d+\.?\d*)%",
                r"24[\s-]?hour.*?long.*?(\d+\.?\d*)%",
                r"long.*?position.*?win.*?rate.*?24.*?hour.*?(\d+\.?\d*)%",
                r"24h.*?long.*?(\d+\.?\d*)%",
                r"\|\s*24\s*hour[s]?\s*\|\s*(\d+\.?\d*)%",
            ],
            "24h_short": [
                r"24[\s-]?hour.*?short.*?win.*?rate.*?(\d+\.?\d*)%",
                r"24[\s-]?hour.*?short.*?(\d+\.?\d*)%",
                r"short.*?position.*?win.*?rate.*?24.*?hour.*?(\d+\.?\d*)%",
                r"24h.*?short.*?(\d+\.?\d*)%",
            ],
            "7d": [
                r"7[\s-]?day.*?long.*?win.*?rate.*?(\d+\.?\d*)%",
                r"7[\s-]?day.*?long.*?(\d+\.?\d*)%",
                r"long.*?position.*?win.*?rate.*?7.*?day.*?(\d+\.?\d*)%",
                r"7d.*?long.*?(\d+\.?\d*)%",
                r"\|\s*7\s*day[s]?\s*\|\s*(\d+\.?\d*)%",
            ],
            "7d_short": [
                r"7[\s-]?day.*?short.*?win.*?rate.*?(\d+\.?\d*)%",
                r"7[\s-]?day.*?short.*?(\d+\.?\d*)%",
                r"short.*?position.*?win.*?rate.*?7.*?day.*?(\d+\.?\d*)%",
                r"7d.*?short.*?(\d+\.?\d*)%",
            ],
            "1m": [
                r"1[\s-]?month.*?long.*?win.*?rate.*?(\d+\.?\d*)%",
                r"1[\s-]?month.*?long.*?(\d+\.?\d*)%",
                r"long.*?position.*?win.*?rate.*?1.*?month.*?(\d+\.?\d*)%",
                r"1m.*?long.*?(\d+\.?\d*)%",
                r"\|\s*1\s*month\s*\|\s*(\d+\.?\d*)%",
            ],
            "1m_short": [
                r"1[\s-]?month.*?short.*?win.*?rate.*?(\d+\.?\d*)%",
                r"1[\s-]?month.*?short.*?(\d+\.?\d*)%",
                r"short.*?position.*?win.*?rate.*?1.*?month.*?(\d+\.?\d*)%",
                r"1m.*?short.*?(\d+\.?\d*)%",
            ]
        }
        
        # Extract rates for each timeframe
        for timeframe_key, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, report_lower)
                if matches:
                    value = float(matches[0])
                    if "24h" in timeframe_key:
                        if "short" in timeframe_key:
                            win_rates["24h"]["short"] = value
                        else:
                            win_rates["24h"]["long"] = value
                    elif "7d" in timeframe_key:
                        if "short" in timeframe_key:
                            win_rates["7d"]["short"] = value
                        else:
                            win_rates["7d"]["long"] = value
                    elif "1m" in timeframe_key:
                        if "short" in timeframe_key:
                            win_rates["1m"]["short"] = value
                        else:
                            win_rates["1m"]["long"] = value
                    break
        
        # Try to extract from table format
        table_pattern = r"\|\s*([^|]+)\s*\|\s*(\d+\.?\d*)%?\s*\|\s*(\d+\.?\d*)%?"
        for match in re.finditer(table_pattern, report):
            timeframe = match.group(1).lower().strip()
            try:
                long_rate = float(match.group(2))
                short_rate = float(match.group(3)) if match.group(3) else 100 - long_rate
                
                if "24" in timeframe or "hour" in timeframe:
                    win_rates["24h"]["long"] = long_rate
                    win_rates["24h"]["short"] = short_rate
                elif "7" in timeframe or ("day" in timeframe and "1" not in timeframe):
                    win_rates["7d"]["long"] = long_rate
                    win_rates["7d"]["short"] = short_rate
                elif "1" in timeframe or "month" in timeframe:
                    win_rates["1m"]["long"] = long_rate
                    win_rates["1m"]["short"] = short_rate
            except (ValueError, IndexError):
                continue
        
        # Ensure complementary rates (if one is found, calculate the other)
        for timeframe in ["24h", "7d", "1m"]:
            if win_rates[timeframe]["long"] > 0 and win_rates[timeframe]["short"] == 0:
                win_rates[timeframe]["short"] = 100 - win_rates[timeframe]["long"]
            elif win_rates[timeframe]["short"] > 0 and win_rates[timeframe]["long"] == 0:
                win_rates[timeframe]["long"] = 100 - win_rates[timeframe]["short"]
        
        return win_rates
    
    def _empty_win_rates(self) -> Dict[str, Dict[str, float]]:
        """Return a typed empty/default win rates structure."""
        return {
            "24h": {"long": 0.0, "short": 0.0},
            "7d": {"long": 0.0, "short": 0.0},
            "1m": {"long": 0.0, "short": 0.0},
        }
    
    async def update_airtable_with_rates(self, record_id: str, symbol: str, win_rates: Dict, report: str) -> bool:
        """Update Airtable with win rates and report status"""
        url = f"https://api.airtable.com/v0/{self.airtable_base}/{self.airtable_table}/{record_id}"
        headers = {
            "Authorization": f"Bearer {self.airtable_key}",
            "Content-Type": "application/json"
        }
        
        # Calculate SCORE as max(long_24h, short_24h)
        score = max(win_rates['24h']['long'], win_rates['24h']['short'])
        
        # Truncate report if it's too long for Airtable (max 100,000 chars for Long Text field)
        truncated_report = report[:95000] + "\n\n[Report truncated due to size limits...]" if len(report) > 95000 else report
        
        # Format win rates as "X% Long/Y% Short"
        update_data = {
            "fields": {
                "WinRate_24h": f"{win_rates['24h']['long']:.0f}% Long/{win_rates['24h']['short']:.0f}% Short",
                "WinRate_7d": f"{win_rates['7d']['long']:.0f}% Long/{win_rates['7d']['short']:.0f}% Short",
                "WinRate_1m": f"{win_rates['1m']['long']:.0f}% Long/{win_rates['1m']['short']:.0f}% Short",
                "Score": score,  # Add the calculated score
                "Report": truncated_report,  # Add the comprehensive report
                "ReportGenerated": datetime.now().isoformat(),
                "ReportStatus": "Complete"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(url, headers=headers, json=update_data) as response:
                    if response.status == 200:
                        print(f"  ✅ Updated Airtable for {symbol}")
                        return True
                    else:
                        error = await response.text()
                        print(f"  ❌ Failed to update Airtable: {error}")
                        return False
            except Exception as e:
                print(f"  ❌ Error updating Airtable: {e}")
                return False
    
    def save_report_with_structure(self, symbol: str, report: str, win_rates: Dict) -> str:
        """Save report with organized folder structure"""
        # Create date-based folder structure
        now = datetime.now()
        date_folder = now.strftime("%Y-%m-%d")
        day_path = MD_REPORTS_DIR / date_folder
        day_path.mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"report_{symbol}_{timestamp}.md"
        filepath = day_path / filename
        
        # Calculate score
        score = max(win_rates['24h']['long'], win_rates['24h']['short'])
        
        # Add win rate summary at the top of the report
        win_rate_summary = f"""
# WIN RATE SUMMARY - {symbol}
**Generated:** {now.strftime('%Y-%m-%d %H:%M:%S')}
**SCORE: {score:.0f}**

| Timeframe | Long Win Rate | Short Win Rate |
|-----------|---------------|----------------|
| 24 Hours  | {win_rates['24h']['long']:.1f}% | {win_rates['24h']['short']:.1f}% |
| 7 Days    | {win_rates['7d']['long']:.1f}% | {win_rates['7d']['short']:.1f}% |
| 1 Month   | {win_rates['1m']['long']:.1f}% | {win_rates['1m']['short']:.1f}% |

---

"""
        
        # Save the complete report
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(win_rate_summary + report)
        
        print(f"  📁 Report saved: {filepath}")
        
        # Also save a copy in history
        history_path = HISTORY_DIR / date_folder
        history_path.mkdir(parents=True, exist_ok=True)
        history_file = history_path / filename
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write(win_rate_summary + report)
        
        return str(filepath)
    
    async def process_all_symbols(self):
        """Process all symbols from Airtable"""
        print("\n" + "="*60)
        print(" STEP 6: PROFESSIONAL REPORT GENERATION")
        print("="*60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Fetch all records
        print("\n📥 Fetching all symbols from Airtable...")
        records = await self.fetch_all_symbol_data()
        
        if not records:
            print("❌ No records found in Airtable")
            return
        
        print(f"✅ Found {len(records)} symbols to process")
        
        # Process each symbol
        success_count = 0
        for i, record in enumerate(records, 1):
            fields = record.get('fields', {})
            symbol = fields.get('Symbol', 'UNKNOWN')
            record_id = record['id']
            
            print(f"\n[{i}/{len(records)}] Processing {symbol}...")
            
            # Check if report needs generation
            if fields.get('LiquidationMap') or fields.get('LiquidationHeatmap'):
                # Generate report
                report, win_rates = await self.generate_professional_report(record)
                
                if report and win_rates:
                    # Save report
                    filepath = self.save_report_with_structure(symbol, report, win_rates)
                    
                    # Update Airtable with win rates and full report
                    success = await self.update_airtable_with_rates(record_id, symbol, win_rates, report)
                    
                    if success:
                        success_count += 1
                        score = max(win_rates['24h']['long'], win_rates['24h']['short'])
                        print(f"  ✅ {symbol} complete - Score: {score:.0f} - Win Rates: 24h L:{win_rates['24h']['long']:.1f}%/S:{win_rates['24h']['short']:.1f}%")
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                else:
                    print(f"  ⚠️ Failed to generate report for {symbol}")
            else:
                print(f"  ⏭️ Skipping {symbol} - No liquidation data")
        
        print("\n" + "="*60)
        print(f" COMPLETED: {success_count}/{len(records)} symbols processed")
        print("="*60)
    
    async def run_continuous(self):
        """Run continuously every 30 minutes"""
        while True:
            try:
                await self.process_all_symbols()
                print(f"\n⏰ Next run in 30 minutes...")
                await asyncio.sleep(1800)  # 30 minutes
            except KeyboardInterrupt:
                print("\n👋 Stopping continuous monitoring...")
                break
            except Exception as e:
                print(f"\n❌ Error in continuous run: {e}")
                print("Retrying in 5 minutes...")
                await asyncio.sleep(300)

async def main():
    """Main entry point"""
    generator = EnhancedReportGenerator()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            print("🔄 Starting continuous monitoring mode...")
            await generator.run_continuous()
        else:
            # Process specific symbol
            symbol = sys.argv[1]
            print(f"Processing single symbol: {symbol}")
            # Would need to implement single symbol processing
    else:
        # Run once for all symbols
        await generator.process_all_symbols()

if __name__ == "__main__":
    asyncio.run(main())